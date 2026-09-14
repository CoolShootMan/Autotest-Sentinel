"""框架内核（与被测系统无关）。

分层职责
--------
``templating``    ``{{变量}}`` 渲染
``jsonpath``      JSONPath 取值（含 ``..`` 递归）
``context``       分层变量上下文（dict 语义，兼容既有手写逻辑）
``http_client``   统一 HTTP 出口（超时/重试/日志/鉴权）
``response``      响应包装（JSONPath 取值、curl 复现）
``assertions``    断言 DSL（``expect(resp).json(...).equals(...)``）
``logging_util``  日志 / Allure 附件 / 落盘
``errors``        异常类型
``case_audit``    harness 静态审计引擎（harness 自带；轻依赖）

业务用例只依赖本包 + ``api`` 包，不直接使用 ``requests``。

Import 容错
-----------
顶层 import 采用 best-effort：核心 API（``expect``/``Context``/``ApiClient``
等）若缺失依赖（典型：harness 工具在精简 Python 环境里跑）则在
``__getattr__`` 层兜底返回 ``None``，避免拉起 ``case_audit`` / 评分器时
整个 core 包炸掉。这与"用例必须装齐依赖才能跑"是两件事——harness 的
静态分析不需要真正的 HTTP 客户端。
"""
from __future__ import annotations

# 这些名字通过 ``core.X`` 取时若顶层 import 失败，会再尝试懒加载；
# 都失败则返回 ``None``，由调用方决定如何降级。
_LAZY_NAMES = (
    "expect", "Context", "ApiClient", "ApiResponse",
    "ApiFrameworkError", "AssertionFailed", "ConfigError",
    "ExtractionError", "RequestError", "TemplateError",
)


def __getattr__(name: str):
    if name in ("case_audit",):
        # 本模块：避免循环
        import importlib
        return importlib.import_module("core.case_audit")
    if name not in _LAZY_NAMES:
        raise AttributeError(name)
    module_map = {
        "expect":                  "core.assertions",
        "Context":                 "core.context",
        "ApiClient":               "core.http_client",
        "ApiResponse":             "core.response",
        "ApiFrameworkError":       "core.errors",
        "AssertionFailed":         "core.errors",
        "ConfigError":             "core.errors",
        "ExtractionError":         "core.errors",
        "RequestError":            "core.errors",
        "TemplateError":           "core.errors",
    }
    import importlib
    try:
        mod = importlib.import_module(module_map[name])
        return getattr(mod, name)
    except Exception:
        return None


# eager exports for "happy path" (full env) so existing usage ``core.expect``
# still works without the __getattr__ dance.
try:
    from core.assertions import expect  # noqa: F401
    from core.context import Context     # noqa: F401
    from core.http_client import ApiClient  # noqa: F401
    from core.response import ApiResponse  # noqa: F401
    from core.errors import (  # noqa: F401
        ApiFrameworkError,
        AssertionFailed,
        ConfigError,
        ExtractionError,
        RequestError,
        TemplateError,
    )
except Exception:
    pass


__all__ = [
    "ApiClient",
    "ApiResponse",
    "ApiFrameworkError",
    "AssertionFailed",
    "ConfigError",
    "Context",
    "ExtractionError",
    "RequestError",
    "TemplateError",
    "expect",
]
