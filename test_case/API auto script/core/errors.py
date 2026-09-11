"""框架异常类型。

设计原则：异常信息必须能独立定位问题——带上表达式、期望值、实际值与响应摘要。
"""
from __future__ import annotations


class ApiFrameworkError(Exception):
    """框架层异常基类。"""


class ConfigError(ApiFrameworkError):
    """配置缺失或非法（如环境文件不存在、base_url 未定义）。"""


class TemplateError(ApiFrameworkError):
    """模板渲染失败（占位符无法解析）。"""


class RequestError(ApiFrameworkError):
    """请求发送失败（网络层，重试耗尽）。"""


class AssertionFailed(ApiFrameworkError):
    """断言失败。

    独立于 ``AssertionError`` 以便框架统一格式化输出，再转换为 pytest 失败。
    """

    def __init__(self, message: str, *, expr: str = "", expected=None, actual=None,
                 response=None):
        self.expr = expr
        self.expected = expected
        self.actual = actual
        self.response = response
        super().__init__(message)


class ExtractionError(ApiFrameworkError):
    """变量提取失败（表达式求值出错）。"""
