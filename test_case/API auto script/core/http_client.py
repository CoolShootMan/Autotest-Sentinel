"""统一 HTTP 客户端。

这是整套框架的唯一出口：所有用例的请求都必须经过 ``ApiClient``，从而把
超时、重试、鉴权、日志、URL 解析、模板渲染集中在一处。

与迁移前的关键差异
------------------
============  ============================================================
迁移前                                          迁移后
============  ============================================================
``ApifoxClient.session()`` 每个用例各建一次会话，   单例会话 + 连接池复用，
且携带 ``x-project-id`` / ``Cookie`` 等 **Apifox     只携带被测系统需要的请求头
平台凭据**（凭据被误送到被测系统）
1203 处裸调用，超时/重试/日志无统一入口            全部收敛到 ``request()``
``_url`` 有两个版本（19 个文件用新版、127 个用旧版）  统一为新版语义（含域名启发式）
============  ============================================================

URL 解析规则（合并两版 ``_url`` 并取正确语义）::

    1. 渲染后含 ``://``            -> 直接使用（绝对 URL）
    2. 首段含 ``.`` 且非 ``{{`` 开头 -> 补 ``https://``（裸域名，如 release.katana-api.1m.app/x）
    3. 其余                        -> ``base_url`` + 路径
"""
from __future__ import annotations

import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter

try:  # urllib3 v2 与 v1 的 Retry 位置不同
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover
    from requests.packages.urllib3.util.retry import Retry  # type: ignore

from config import settings
from core import logging_util, templating
from core.errors import RequestError
from core.response import ApiResponse

# 默认请求头：只放与被测系统交互真正需要的通用头。
# 注意：绝不携带任何迁移平台（Apifox）的凭据。
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US",
}


def _has_header(headers: dict, name: str) -> bool:
    """大小写不敏感地判断请求头是否存在。"""
    low = name.lower()
    return any(k.lower() == low for k in headers)


def _dedupe_bearer(value: str) -> str:
    """折叠重复的 ``Bearer`` 前缀（``Bearer Bearer x`` -> ``Bearer x``）。

    迁移前的环境文件里个别 token 变量自带 ``Bearer `` 前缀，而调用处又拼了一次，
    会产生 ``Bearer Bearer eyJ...``。此处统一收敛，避免逐个用例去改。
    """
    if not isinstance(value, str):
        return value
    parts = value.split()
    if len(parts) >= 2 and parts[0].lower() == "bearer" and parts[1].lower() == "bearer":
        return "Bearer " + " ".join(parts[2:])
    return value


class ApiClient:
    """被测系统 HTTP 客户端。

    Args:
        base_url: 环境根地址（由 config/environments/<ENV>.yaml 提供）
        ctx:      变量上下文，用于渲染 URL / 请求头 / 请求体中的 ``{{变量}}``
        timeout:  单请求超时（秒）
        retries:  瞬时故障重试次数
        verify:   是否校验 TLS 证书
    """

    def __init__(self, base_url: str, ctx=None, *, timeout: int | None = None,
                 retries: int | None = None, verify: bool = True,
                 default_headers: dict | None = None):
        if not base_url:
            raise RequestError("base_url 为空，请检查环境配置文件")
        self.base_url = base_url
        self.ctx = ctx
        self.timeout = timeout if timeout is not None else settings.TIMEOUT
        self.retries = retries if retries is not None else settings.RETRIES
        self.verify = verify
        self.default_headers = {**DEFAULT_HEADERS, **(default_headers or {})}
        self._session = self._build_session()
        self.log = logging_util.get_logger()

    # --- 会话 -----------------------------------------------------------
    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=self.retries,
            connect=self.retries,
            read=self.retries,
            status=self.retries,
            backoff_factor=settings.RETRY_BACKOFF_FACTOR,
            status_forcelist=list(settings.RETRY_STATUS_FORCELIST),
            allowed_methods=None,   # POST/PUT/DELETE 等瞬时故障同样重试
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=32, pool_maxsize=32)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update(self.default_headers)
        return session

    @property
    def session(self) -> requests.Session:
        """底层会话（仅用于需要直接控制 requests 的场景）。"""
        return self._session

    def close(self) -> None:
        try:
            self._session.close()
        except Exception:
            pass

    # --- URL / 渲染 -----------------------------------------------------
    def _mapping(self, path_vars: dict | None = None):
        """构造渲染用的变量映射；``path_vars`` 会临时覆盖上下文取值。"""
        if not path_vars or self.ctx is None:
            return self.ctx
        merged = dict(self.ctx)
        merged.update(path_vars)
        return merged

    def _render(self, value: Any, path_vars: dict | None = None) -> Any:
        mapping = self._mapping(path_vars)
        if mapping is None:
            return value
        return templating.render(value, mapping)

    def resolve_url(self, path: str, path_vars: dict | None = None) -> str:
        """把路径解析成完整 URL（规则见模块文档）。"""
        rendered = str(self._render(path, path_vars))
        if "://" in rendered:
            return rendered
        head = rendered.split("/", 1)[0]
        if head and "." in head and not head.startswith("{{"):
            return "https://" + rendered
        return str(self._render(self.base_url, path_vars)) + rendered

    def _normalize_headers(self, headers: dict) -> dict:
        """请求头规范化（当前仅收敛重复的 ``Bearer`` 前缀）。"""
        out = {}
        for k, v in headers.items():
            if k.lower() == "authorization":
                v = _dedupe_bearer(v)
            out[k] = v
        return out

    # --- 请求 -----------------------------------------------------------
    def request(self, method: str, path: str, *, headers: dict | None = None,
                params: dict | None = None, body: Any = None,
                path_vars: dict | None = None,
                timeout: int | None = None, allow_redirects: bool = True) -> ApiResponse:
        """发送请求并返回 :class:`ApiResponse`。

        Args:
            method:  HTTP 方法
            path:    路径或完整 URL，支持 ``{{变量}}``
            headers: 请求头（在默认头之上合并），值支持 ``{{变量}}``
            params:  查询参数，值支持 ``{{变量}}``
            body:    请求体。``str`` 视为模板（渲染后原样发送，与迁移前一致）；
                     ``dict``/``list`` 直接以 JSON 发送；``None`` 表示无请求体
            path_vars: 仅本次请求生效的变量覆盖（用于路径参数）
            timeout: 覆盖默认超时
        """
        method = method.upper()
        url = self.resolve_url(path, path_vars)

        merged_headers = dict(self.default_headers)
        merged_headers.update(self._render(headers or {}, path_vars))
        merged_headers = self._normalize_headers(merged_headers)

        rendered_params = self._render(params, path_vars) if params else None

        data: Any = None
        json_body: Any = None
        if isinstance(body, (dict, list)):
            json_body = self._render(body, path_vars)
        elif isinstance(body, str):
            rendered = str(self._render(body, path_vars))
            if rendered.strip():
                data = rendered
        elif body is not None:
            data = body

        # Content-Type 推导：有 JSON 请求体但调用方未指定时自动补 application/json。
        # 迁移前由 659 处手写请求头承担，现收敛为一条规则（调用方显式指定者优先）。
        if (json_body is not None or data is not None) and not _has_header(merged_headers, "Content-Type"):
            merged_headers["Content-Type"] = "application/json"

        logging_util.log_request(method, url, merged_headers, json_body if json_body is not None else data)

        start = time.perf_counter()
        try:
            raw = self._session.request(
                method, url,
                headers=merged_headers,
                params=rendered_params,
                data=data,
                json=json_body,
                timeout=timeout if timeout is not None else self.timeout,
                verify=self.verify,
                allow_redirects=allow_redirects,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            raise RequestError(
                f"请求失败（已重试 {self.retries} 次）: {method} {url}\n  {type(exc).__name__}: {exc}"
            ) from exc

        elapsed_ms = (time.perf_counter() - start) * 1000
        response = ApiResponse(
            raw, method=method, url=url,
            request_headers=merged_headers,
            request_body=json_body if json_body is not None else data,
            elapsed_ms=elapsed_ms,
        )

        logging_util.log_response(response.status_code, elapsed_ms, response.body_preview(300))
        logging_util.append_http_log({
            "method": method, "url": url,
            "headers": logging_util.mask_headers(merged_headers),
            "body": json_body if json_body is not None else data,
            "status": response.status_code,
            "elapsed_ms": round(elapsed_ms, 1),
            "response": response.body_preview(1000),
        })
        logging_util.attach(f"{method} {url}", response.curl() + "\n\n--- response ---\n" + response.body_preview(2000))
        return response

    # --- 便捷方法 -------------------------------------------------------
    def get(self, path: str, **kw) -> ApiResponse:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw) -> ApiResponse:
        return self.request("POST", path, **kw)

    def put(self, path: str, **kw) -> ApiResponse:
        return self.request("PUT", path, **kw)

    def patch(self, path: str, **kw) -> ApiResponse:
        return self.request("PATCH", path, **kw)

    def delete(self, path: str, **kw) -> ApiResponse:
        return self.request("DELETE", path, **kw)

    # --- 上下文切换 -----------------------------------------------------
    def bind(self, ctx) -> "ApiClient":
        """绑定/替换变量上下文（返回自身，便于链式使用）。"""
        self.ctx = ctx
        return self

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
