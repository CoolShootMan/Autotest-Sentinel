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

import re

#: 被测系统的应用级凭据头（值经上下文渲染，不硬编码密钥）
APP_HEADERS = {
    "Pear-AutoTesting": "{{Pear-AutoTesting}}",
    "Pear-Client-Id": "{{pear_client_id}}",
    "Pear-Client-Secret": "{{pear_client_secret}}",
}

#: 测试期静默通知头：避免回归跑批给真实用户发邮件/短信
SKIP_NOTIFICATIONS_HEADERS = {"X-Skip-Notifications": "email,sms"}

_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _pv(*pairs, extra: dict | None = None) -> dict | None:
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

    def __init__(self, client, ctx):
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
    def _resolve_path_vars(self, path_vars: dict | None) -> dict | None:
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

    def _call(self, method: str, path: str, *, body=None, params=None,
              token: str | None = None, headers: dict | None = None,
              app_headers: bool = False, skip_notifications: bool = False,
              path_vars: dict | None = None, timeout: int | None = None,
              allow_redirects: bool = True):
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
        hdrs: dict = {}
        if app_headers:
            hdrs.update(APP_HEADERS)
        if skip_notifications:
            hdrs.update(SKIP_NOTIFICATIONS_HEADERS)
        if token:
            hdrs["Authorization"] = self.bearer(token)
        if headers:
            hdrs.update(headers)

        # --- 未配置角色 token 时的安全 fallback ---
        # 迁移后大量用例引用 linda01_token / admin_token / merchant_token 等角色 token，
        # 但环境文件里只有通用 token 有值；发送 ``Bearer {{linda01_token}}`` 会被 WAF 直接 403。
        # 此处对未解析/为空的 Authorization 做一次性 fallback 到 ``token``，并打 warn 日志，
        # 保证框架能先跑起来；后续应把各角色真实 token 补进环境文件。
        auth = hdrs.get("Authorization")
        if auth and self.ctx is not None:
            rendered = self.ctx.render(auth)
            if "{{" in rendered or rendered.strip() == "Bearer" or rendered.strip() == "":
                fallback = self.ctx.render(self.bearer("token"))
                if fallback and "{{" not in fallback and fallback.strip() not in ("Bearer", ""):
                    import logging
                    logging.getLogger("api.framework").warning(
                        "角色 token '%s' 未定义或为空，已 fallback 到通用 token；"
                        "建议将真实 token 补进 config/environments/<ENV>.yaml。",
                        token,
                    )
                    hdrs["Authorization"] = fallback
        # --------------------------------------------

        path_vars = self._resolve_path_vars(path_vars)

        return self.client.request(
            method, path,
            headers=hdrs,
            params=params,
            body=body,
            path_vars=path_vars,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

    # --- 调试 -----------------------------------------------------------
    def __repr__(self) -> str:
        return f"<{type(self).__name__} domain={self.domain!r}>"
