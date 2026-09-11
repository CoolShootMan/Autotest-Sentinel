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

业务用例只依赖本包 + ``api`` 包，不直接使用 ``requests``。
"""
from core.assertions import expect
from core.context import Context
from core.errors import (
    ApiFrameworkError,
    AssertionFailed,
    ConfigError,
    ExtractionError,
    RequestError,
    TemplateError,
)
from core.http_client import ApiClient
from core.response import ApiResponse

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
