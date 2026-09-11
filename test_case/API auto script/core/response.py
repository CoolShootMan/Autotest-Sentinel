"""响应对象。

把 ``requests.Response`` 包一层，提供业务断言真正需要的能力：

* ``status_code`` / ``text`` / ``headers`` —— 透传
* ``json_safe()``  —— 仅在 ``Content-Type`` 为 JSON 时解析，否则返回 ``{}``
                     （复刻旧生成器的判断，保证既有用例行为不变）
* ``path("$.data.token")`` —— JSONPath 取值，支持 ``..`` 递归
* ``paths("$.data..status")`` —— 取全部命中值
* ``curl()`` —— 生成可复现的 curl 命令，失败时直接贴进终端排查
"""
from __future__ import annotations

import json
from typing import Any

from core import jsonpath, logging_util

_MAX_BODY_PREVIEW = 600


class CaseInsensitiveHeaders(dict):
    """大小写无关的响应头映射。

    迁移前用例跑在 Apifox 里，``pm.response.headers.get('content-type')`` 是
    **大小写无关**的；转成 Python 后 ``dict(headers)`` 变成了普通 dict，而服务端
    下发的是 ``Content-Type``，于是 ``headers.get('content-type')`` 恒为 ``""``，
    连带 ``.startswith('application/json')`` 守卫全部判假 —— 断言拿到空 ``{}``、
    报 ``code=None``。

    这里做一个仍是 ``dict`` 的子类（保持迭代顺序与原键名大小写），只把
    ``get`` / ``__getitem__`` / ``__contains__`` 改为大小写无关查找，
    从而在不改动任何既有用例的前提下恢复 Apifox 语义。
    """

    __slots__ = ("_lower_map",)

    def __init__(self, data=None, **kwargs):
        super().__init__(data or {}, **kwargs)
        self._lower_map = {str(k).lower(): k for k in self.keys()}

    def _real_key(self, key):
        return self._lower_map.get(str(key).lower(), key)

    def get(self, key, default=None):
        return super().get(self._real_key(key), default)

    def __getitem__(self, key):
        return super().__getitem__(self._real_key(key))

    def __contains__(self, key):
        return super().__contains__(self._real_key(key))

    def pop(self, key, *args):
        return super().pop(self._real_key(key), *args)

    def setdefault(self, key, default=None):
        return super().setdefault(self._real_key(key), default)


class ApiResponse:
    """被测系统响应的统一视图。"""

    __slots__ = ("_raw", "method", "url", "request_headers", "request_body",
                 "elapsed_ms", "_json_cache", "_json_parsed")

    def __init__(self, raw, *, method: str = "", url: str = "",
                 request_headers: dict | None = None, request_body: Any = None,
                 elapsed_ms: float = 0.0):
        self._raw = raw
        self.method = method.upper()
        self.url = url
        self.request_headers = request_headers or {}
        self.request_body = request_body
        self.elapsed_ms = elapsed_ms
        self._json_cache: Any = None
        self._json_parsed = False

    # --- 基础透传 -------------------------------------------------------
    @property
    def status_code(self) -> int:
        return getattr(self._raw, "status_code", 0)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    @property
    def text(self) -> str:
        try:
            return self._raw.text
        except Exception:
            return ""

    @property
    def headers(self) -> CaseInsensitiveHeaders:
        """响应头；键名大小写无关（对齐 Apifox ``pm.response.headers.get``）。"""
        try:
            return CaseInsensitiveHeaders(self._raw.headers)
        except Exception:
            return CaseInsensitiveHeaders()

    @property
    def content_type(self) -> str:
        """``Content-Type`` 头，大小写不敏感。"""
        return self.headers.get("Content-Type") or ""

    @property
    def elapsed(self) -> float:
        """响应耗时（秒）。"""
        return self.elapsed_ms / 1000.0

    @property
    def raw(self):
        """原始 ``requests.Response``，逃生舱口。"""
        return self._raw

    # --- JSON -----------------------------------------------------------
    def json(self) -> Any:
        """严格解析 JSON；非 JSON 或解析失败抛 ``ValueError``。"""
        if not self._json_parsed:
            self._json_cache = json.loads(self.text)
            self._json_parsed = True
        return self._json_cache

    def json_safe(self) -> Any:
        """宽松解析：仅在 Content-Type 为 JSON 时解析，否则返回 ``{}``。

        与旧生成器 ``_a.json() if headers['content-type'].startswith('application/json') else {}``
        完全等价，是断言/提取的默认取值入口。
        """
        if self._json_parsed:
            return self._json_cache
        self._json_parsed = True
        if not self.content_type.lower().startswith("application/json"):
            self._json_cache = {}
            return self._json_cache
        try:
            self._json_cache = self._raw.json()
        except Exception:
            self._json_cache = {}
        return self._json_cache

    def as_dict(self) -> Any:
        """返回可 JSON 序列化的响应体（失败时返回原始文本）。"""
        data = self.json_safe()
        return data if data else self.text

    # --- JSONPath -------------------------------------------------------
    def path(self, expr: str, default: Any = None) -> Any:
        """按 JSONPath 取单个值；未命中返回 ``default``。"""
        hits = jsonpath.query(self.json_safe(), expr)
        return hits[0] if hits else default

    def paths(self, expr: str) -> list:
        """按 JSONPath 取全部命中值（``..`` 递归语义）。"""
        return jsonpath.query(self.json_safe(), expr)

    def has(self, expr: str) -> bool:
        """路径是否存在（值非 ``None``）。"""
        return bool(jsonpath.query(self.json_safe(), expr))

    # --- 调试 -----------------------------------------------------------
    def body_preview(self, limit: int = _MAX_BODY_PREVIEW) -> str:
        return logging_util.truncate(self.text, limit)

    def describe(self, limit: int = _MAX_BODY_PREVIEW) -> str:
        """单行摘要，用于断言失败信息。"""
        return f"{self.method} {self.url} -> {self.status_code} ({self.elapsed_ms:.0f}ms) {self.body_preview(limit)}"

    def curl(self) -> str:
        """生成等价的 curl 命令，便于人工复现。"""
        parts = [f"curl -X {self.method} '{self.url}'"]
        for k, v in self.request_headers.items():
            if k.lower() == "content-length":
                continue
            parts.append(f"  -H '{k}: {v}'")
        if self.request_body not in (None, ""):
            body = self.request_body if isinstance(self.request_body, str) else json.dumps(
                self.request_body, ensure_ascii=False)
            parts.append(f"  --data-raw '{body}'")
        return " \\\n".join(parts)

    def __repr__(self) -> str:
        return f"<ApiResponse {self.method} {self.url} -> {self.status_code}>"
