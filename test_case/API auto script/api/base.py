"""业务服务层基类。

分层职责
--------
``api/`` 层是**被测系统的业务语义层**：它知道「哪个接口叫什么、需要什么鉴权、
属于哪个业务域」，但不知道「哪个用例在什么场景下调它」。

用例层只表达业务意图::

    resp = ctx.api.auth.sign_in(body='{"email": "{{account_email_curator}}", ...}')
    expect(resp).json("$.code").equals(200)

而「POST /auth/sign-in、路径参数叫什么、默认带不带 app 头」这些**接口事实**
全部沉淀在 ``api/auth.py`` 里。

请求头的归属判定
----------------
实测 203 个接口中 **178 个的请求头形态是稳定的**，因此请求头被认定为
**接口属性**而非调用属性，按以下规则拆解：

======================  ==========================================  ====================
请求头                   归属                                        理由
======================  ==========================================  ====================
``Content-Type``        由 :class:`~core.http_client.ApiClient` 自动补   有 JSON body 即有它（659 处）
``Pear-AutoTesting``    接口级开关 ``app_headers``                   与鉴权强相关（P=0.79）但非必然
``Pear-Client-Id``      同上                                        ——
``Pear-Client-Secret``  同上                                        ——
``X-Skip-Notifications`` 接口级开关 ``skip_notifications``           恒为 ``email,sms``
``Authorization``       调用级参数 ``token``                         变量名随角色变化（linda05/10/merchant…）
其它                     ``headers=`` 逃生口                          极少数个案
======================  ==========================================  ====================

``app_headers`` / ``skip_notifications`` 的**默认值直接写在各接口方法的签名里**，
因此「这个接口默认带不带 app 头」在代码里一眼可见，调用方只在偏离默认时才需要显式传参。
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 仅类型检查期导入：避免 api ↔ core 运行期循环依赖
    from core.context import Context
    from core.http_client import ApiClient
    from core.response import ApiResponse

#: 被测系统的应用级凭据头（值经上下文渲染，不硬编码密钥）
APP_HEADERS = {
    "Pear-AutoTesting": "{{Pear-AutoTesting}}",
    "Pear-Client-Id": "{{pear_client_id}}",
    "Pear-Client-Secret": "{{pear_client_secret}}",
}

#: 测试期静默通知头：避免回归跑批给真实用户发邮件/短信
SKIP_NOTIFICATIONS_HEADERS = {"X-Skip-Notifications": "email,sms"}

_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

_log = logging.getLogger("api.framework")


def _pv(*pairs, extra: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """组装路径参数覆盖表。

    接口方法把路径参数声明成可选关键字参数（默认 ``None``）：
    不传时路径保留 ``{{变量}}`` 模板、由上下文渲染（与迁移前行为一致）；
    传了才覆盖。全部为空时返回 ``None``，不产生额外开销。

    Args:
        *pairs: ``(参数名, 取值)`` 序列，取值为 ``None`` 的项被跳过
        extra:  调用方直接传入的 ``path_vars``，优先级最高
    """
    out = {k: v for k, v in pairs if v is not None}
    if extra:
        out.update(extra)
    return out or None


class BaseApi:
    """所有业务服务模块的基类。

    Args:
        client: :class:`~core.http_client.ApiClient` 实例
        ctx:    :class:`~core.context.Context` 变量上下文
    """

    #: 该业务域的名称（子类覆盖），用于日志与错误信息
    domain = "base"

    def __init__(self, client: "ApiClient", ctx: "Context | None" = None) -> None:
        self.client = client
        self.ctx = ctx

    # --- 鉴权 -----------------------------------------------------------
    @staticmethod
    def bearer(token: str) -> str:
        """把 token 参数规整成 ``Authorization`` 头的值。

        Args:
            token: 变量名（如 ``"linda10_token"``）或直接的值/模板。

        Returns:
            形如 ``Bearer {{linda10_token}}`` 的模板。

        Notes:
            ``Bearer`` 前缀是**幂等**的：环境里个别 token 变量本身已含
            ``Bearer ``（Apifox 迁移遗留），客户端会再收敛一次，不会叠加成
            ``Bearer Bearer``。
        """
        if not token:
            return ""
        if _IDENT_RE.match(token):
            return "Bearer {{" + token + "}}"
        if token.lower().startswith("bearer "):
            return token
        return "Bearer " + token

    # --- 请求出口 -------------------------------------------------------
    def _resolve_path_vars(self, path_vars: dict[str, Any] | None) -> dict[str, Any] | None:
        """把 ``path_vars`` 里的模板值先按上下文解析一次。

        路径参数的**变量名在不同用例里并不统一**（同一个接口既可能写
        ``{{merchantId}}`` 也可能写 ``{{P1_merchantIDa}}``）。接口方法签名里的
        形参名取自多数派，因此调用方在变量名不一致时需要覆盖取值。允许直接写
        模板，可以让「用哪个变量」这件事在用例里一眼可见::

            ctx.api.orders.merchant_detail_by_order_number(
                path_vars={"merchantId": "{{P1_merchantIDa}}"},
            )

        未定义的占位符按 :mod:`core.templating` 的既有语义**原样保留**，
        与迁移前「变量缺失时把 ``{{x}}`` 字面量发出去」的行为一致，不抛 KeyError。
        """
        if not path_vars or self.ctx is None:
            return path_vars
        return {
            k: (self.ctx.render(v) if isinstance(v, str) and "{{" in v else v)
            for k, v in path_vars.items()
        }

    def _call(self, method: str, path: str, *, body: Any = None,
              params: dict[str, Any] | None = None,
              token: str | None = None, headers: dict[str, Any] | None = None,
              app_headers: bool = False, skip_notifications: bool = False,
              path_vars: dict[str, Any] | None = None, timeout: int | None = None,
              allow_redirects: bool = True) -> "ApiResponse":
        """本层唯一的请求出口：把「接口事实 + 调用参数」组装成一次 HTTP 请求。

        Args:
            method:            HTTP 方法
            path:              路径模板（可含 ``{{变量}}``）
            body:              请求体模板字符串；``None`` 表示无请求体
            params:            查询参数
            token:             鉴权变量名；``None`` 表示匿名请求
            headers:           额外请求头（逃生口）
            app_headers:       是否携带应用级凭据头
            skip_notifications: 是否静默通知
            path_vars:         覆盖路径中 ``{{变量}}`` 的临时取值；值可以是模板
                               （如 ``"{{P1_merchantIDa}}"``），先按上下文解析
            timeout:           覆盖默认超时
            allow_redirects:   是否跟随重定向
        """
        hdrs: dict[str, str] = {}
        if app_headers:
            hdrs.update(APP_HEADERS)
        if skip_notifications:
            hdrs.update(SKIP_NOTIFICATIONS_HEADERS)
        if token:
            hdrs["Authorization"] = self.bearer(token)
        if headers:
            hdrs.update(headers)

        # --- 角色 token 即时续期 ---
        # 在发请求前，先检查 token 是否即将过期（< 30s）或已过期/为空。
        # 如果是，立即刷新对应角色的 token，避免 403 后再重试的往返开销。
        self._try_refresh_token_if_needed(token)

        path_vars = self._resolve_path_vars(path_vars)

        resp = self.client.request(
            method, path,
            headers=hdrs,
            params=params,
            body=body,
            path_vars=path_vars,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

        # --- 401/403 token 过期自动续期 + 重试 ---
        # 后端 JWT 过期 → 403 "please log in again"；
        # JWT 缺失/无效 → 401 "Unauthorized"（JwtAuthGuard 直接拒绝）。
        # 两种情况都自动刷新对应角色 token 并重试一次。
        if token and self._is_token_expired_response(resp):
            try:
                from core import token_refresh
                known = set(token_refresh.RECIPES) | set(token_refresh.ALIASES)
            except ImportError:
                known = set()
            if token in known:
                _log.info("[token] 请求 %s %s 收到 %d，尝试续期 %s 后重试",
                          method, path, resp.status_code, token)
                new_token = self._refresh_token_by_name(token)
                if new_token:
                    # 重新构建 headers（token 已更新到 ctx，重新渲染即可）
                    hdrs2 = dict(hdrs)
                    if token:
                        hdrs2["Authorization"] = self.bearer(token)
                    resp = self.client.request(
                        method, path,
                        headers=hdrs2,
                        params=params,
                        body=body,
                        path_vars=path_vars,
                        timeout=timeout,
                        allow_redirects=allow_redirects,
                    )
        return resp

    # --- 调试 -----------------------------------------------------------
    def __repr__(self) -> str:
        return f"<{type(self).__name__} domain={self.domain!r}>"

    # --- token 即时续期辅助 ---------------------------------------------
    def _try_refresh_token_if_needed(self, token: str | None) -> None:
        """在发请求前检查 token 是否即将过期，如果是则立即刷新。

        阈值 30 秒：剩余寿命 < 30s 或已过期/为空时触发刷新。
        这是对 ``conftest._ensure_runtime_tokens``（用例级续期）的补充，
        覆盖「同一条用例内多步请求耗时 > token 寿命」的场景。
        """
        if not token or not _IDENT_RE.match(token) or self.ctx is None:
            return
        try:
            from core import token_refresh
        except ImportError:
            return
        # 只处理框架已知的角色 token（RECIPES / ALIASES 里的）
        known = set(token_refresh.RECIPES) | set(token_refresh.ALIASES)
        if token not in known:
            return
        current = self.ctx.get(token)
        if not current or not isinstance(current, str):
            # token 为空，尝试刷新
            self._refresh_token_by_name(token)
            return
        left = token_refresh.seconds_left(current)
        if left is not None and left < 30:
            _log.debug("[token] %s 剩余 %ds < 30s，发请求前即时续期", token, int(left))
            self._refresh_token_by_name(token)

    def _refresh_token_by_name(self, token: str) -> str | None:
        """按名称刷新角色 token，写入 ctx 和 runtime 文件。"""
        if not token or self.ctx is None:
            return None
        try:
            from core import token_refresh
        except ImportError:
            return None
        return token_refresh.refresh_by_name(self.ctx, token)

    @staticmethod
    def _is_token_expired_response(resp) -> bool:
        """判断响应是否为 JWT 过期/无效的 401 或 403。"""
        try:
            from core import token_refresh
            return token_refresh.is_token_expired_response(
                resp.status_code, resp.body_preview(500)
            )
        except Exception:
            return False
