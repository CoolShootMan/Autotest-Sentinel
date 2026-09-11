"""断言 DSL。

把旧生成器里「每条断言 8~9 行 try/except」压缩成一行，并统一失败信息。

用法::

    expect(resp).json("$.code").equals(200)
    expect(resp).json("$.data.token").exists()
    expect(resp).json("$.data..status").includes("REFUNDED")
    expect(resp).json("$.data.items").is_empty()
    expect(resp).status().is_(200)
    expect(resp).status().is_ok()

语义对齐 Apifox（并修复旧生成器的偏差）：

===========  ==========================================  ==========================
comparison   Apifox 语义                                  旧生成器实现
===========  ==========================================  ==========================
equal        实际值 == 期望值（字符串化比较）              ✅ 一致
exists       路径存在（值非 None）                        ❌ 被生成为 ``== ''``，永远失败
include      递归路径命中的任一值 == 期望值                ✅ 一致
isEmpty      值为空（None / 空串 / 空容器 / 0 为真值）      ✅ 一致
===========  ==========================================  ==========================

断言失败统一抛 ``AssertionFailed``，由 conftest 的 hook 转成 pytest 失败并附响应摘要。
"""
from __future__ import annotations

from typing import Any

from core.errors import AssertionFailed
from core.response import ApiResponse


def _to_str(value: Any) -> str:
    """字符串化比较——语义对齐 Apifox（即 JS ``String(x)``），而非 Python ``str(x)``。

    .. important::
       两者在两处**不同**，且都会把本应通过的断言判成失败：

       ==============  ==================  ==================
       值              Python ``str()``    JS ``String()``
       ==============  ==================  ==================
       ``True``        ``'True'``          ``'true'``
       ``False``       ``'False'``         ``'false'``
       ``None``        ``'None'``          ``'null'``
       ==============  ==================  ==================

       数值不受影响（``str(25) == String(25) == '25'``）。146 条用例中
       期望值为 ``'true'`` / ``'false'`` 的断言共 5 处，期望 ``'None'`` /
       ``'null'`` 的为 0 处，故改为 JS 语义不会反转任何既有结论，
       只会把 5 处「布尔误判」修回正确。
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def _is_empty(value: Any) -> bool:
    """空值判定：None / '' / [] / {} 视为空；0 与 False 视为非空（有值）。"""
    if value is None:
        return True
    if isinstance(value, str):
        return value == ""
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) == 0
    return False


class _JsonAssertion:
    """针对某个 JSONPath 的断言集合。"""

    def __init__(self, response: ApiResponse, expr: str):
        self.response = response
        self.expr = expr

    # --- 取值 -----------------------------------------------------------
    @property
    def _hits(self) -> list:
        return self.response.paths(self.expr)

    @property
    def actual(self) -> Any:
        hits = self._hits
        return hits[0] if hits else None

    def _fail(self, expected: Any, hint: str = "") -> None:
        msg = (
            f"断言失败: {self.expr} {hint}\n"
            f"  期望: {expected!r}\n"
            f"  实际: {self.actual!r}\n"
            f"  响应: {self.response.describe()}"
        )
        raise AssertionFailed(msg, expr=self.expr, expected=expected,
                              actual=self.actual, response=self.response)

    # --- 断言 -----------------------------------------------------------
    def equals(self, expected: Any) -> "_JsonAssertion":
        """相等断言（字符串化比较，与 Apifox / 旧实现一致）。"""
        actual = self.actual
        if _to_str(actual) != _to_str(expected):
            self._fail(expected, "相等")
        return self

    def not_equals(self, expected: Any) -> "_JsonAssertion":
        if _to_str(self.actual) == _to_str(expected):
            self._fail(expected, "不相等")
        return self

    def exists(self) -> "_JsonAssertion":
        """路径存在（值非 ``None``）。"""
        if self.actual is None:
            self._fail("(存在)", "存在")
        return self

    def not_exists(self) -> "_JsonAssertion":
        if self.actual is not None:
            self._fail("(不存在)", "不存在")
        return self

    def includes(self, expected: Any) -> "_JsonAssertion":
        """递归命中的任一值等于期望值。"""
        hits = self._hits
        if not any(_to_str(v) == _to_str(expected) for v in hits):
            self._fail(expected, "包含")
        return self

    def not_includes(self, expected: Any) -> "_JsonAssertion":
        hits = self._hits
        if any(_to_str(v) == _to_str(expected) for v in hits):
            self._fail(expected, "不包含")
        return self

    def is_empty(self) -> "_JsonAssertion":
        if not _is_empty(self.actual):
            self._fail("(空)", "为空")
        return self

    def is_not_empty(self) -> "_JsonAssertion":
        if _is_empty(self.actual):
            self._fail("(非空)", "非空")
        return self

    def greater_than(self, expected: Any) -> "_JsonAssertion":
        try:
            if not float(self.actual) > float(expected):
                self._fail(expected, "大于")
        except (TypeError, ValueError):
            self._fail(expected, "大于(不可比较)")
        return self

    def less_than(self, expected: Any) -> "_JsonAssertion":
        try:
            if not float(self.actual) < float(expected):
                self._fail(expected, "小于")
        except (TypeError, ValueError):
            self._fail(expected, "小于(不可比较)")
        return self

    def contains(self, substring: Any) -> "_JsonAssertion":
        """字符串包含。"""
        if _to_str(substring) not in _to_str(self.actual):
            self._fail(substring, "字符串包含")
        return self

    def length(self, expected: int) -> "_JsonAssertion":
        actual = self.actual
        n = len(actual) if hasattr(actual, "__len__") else -1
        if n != expected:
            self._fail(expected, f"长度(实际 {n})")
        return self

    def matches(self, pattern: str) -> "_JsonAssertion":
        """正则匹配。"""
        import re
        if not re.search(pattern, _to_str(self.actual)):
            self._fail(pattern, "正则匹配")
        return self


class _StatusAssertion:
    """针对 HTTP 状态码的断言。"""

    def __init__(self, response: ApiResponse):
        self.response = response

    def _fail(self, expected: Any, hint: str = "") -> None:
        msg = (f"HTTP 状态断言失败 {hint}\n"
               f"  期望: {expected!r}\n"
               f"  实际: {self.response.status_code}\n"
               f"  响应: {self.response.describe()}")
        raise AssertionFailed(msg, expr="<status>", expected=expected,
                              actual=self.response.status_code, response=self.response)

    def is_(self, expected: int) -> "_StatusAssertion":
        if self.response.status_code != int(expected):
            self._fail(expected)
        return self

    def is_ok(self) -> "_StatusAssertion":
        """2xx / 3xx 视为成功。"""
        if not self.response.ok:
            self._fail("2xx/3xx")
        return self

    def is_less_than(self, expected: int) -> "_StatusAssertion":
        if not self.response.status_code < int(expected):
            self._fail(f"< {expected}")
        return self

    def is_json(self) -> "_StatusAssertion":
        if "application/json" not in self.response.content_type.lower():
            self._fail("Content-Type: application/json")
        return self


class _BodyAssertion:
    """针对原始响应体的断言。"""

    def __init__(self, response: ApiResponse):
        self.response = response

    def contains(self, text: str) -> "_BodyAssertion":
        if text not in self.response.text:
            raise AssertionFailed(
                f"响应体不包含 {text!r}\n  响应: {self.response.describe()}",
                expr="<body>", expected=text, actual=None, response=self.response)
        return self


class _Expect:
    """``expect(resp)`` 的入口。"""

    def __init__(self, response: ApiResponse):
        self.response = response

    def json(self, expr: str) -> _JsonAssertion:
        return _JsonAssertion(self.response, expr)

    def status(self) -> _StatusAssertion:
        return _StatusAssertion(self.response)

    def body(self) -> _BodyAssertion:
        return _BodyAssertion(self.response)


def expect(response: ApiResponse) -> _Expect:
    """断言入口。"""
    if not isinstance(response, ApiResponse):
        raise TypeError(
            f"expect() 需要 ApiResponse，实际收到 {type(response).__name__}；"
            "请确认被测方法通过 api 层调用"
        )
    return _Expect(response)
