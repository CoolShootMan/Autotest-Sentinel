"""``{{变量}}`` 模板渲染。

行为与迁移前保持一致（逐变量 ``str.replace``），以保证 146 条既有用例语义不变：

* 只替换形如 ``{{key}}`` 的占位符（花括号内允许空格：``{{ key }}``）
* 变量值统一按 ``str()`` 注入——与旧生成器一致，避免数字/布尔类型漂移
* 未定义的占位符原样保留，同时记录到 ``unresolved``，便于排查拼写错误

``render`` 支持 str / list / tuple / dict 递归；非字符串类型原样返回。
"""
from __future__ import annotations

import re
from typing import Any, Iterable

# 匹配 {{ key }} / {{key}}；不支持嵌套表达式
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


def render_text(template: str, variables: dict) -> str:
    """渲染单个字符串。"""
    if not isinstance(template, str) or "{{" not in template:
        return template
    out = template
    for key, value in variables.items():
        if value is None:
            continue
        # 两种书写形式都支持：{{key}} 与 {{ key }}
        out = out.replace("{{" + str(key) + "}}", str(value))
        out = out.replace("{{ " + str(key) + " }}", str(value))
    return out


def render(value: Any, variables: dict) -> Any:
    """递归渲染任意结构。"""
    if isinstance(value, str):
        return render_text(value, variables)
    if isinstance(value, dict):
        return {k: render(v, variables) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(render(v, variables) for v in value)
    return value


def unresolved(value: Any, variables: dict) -> list[str]:
    """返回渲染后仍然残留的占位符名（用于校验数据是否配齐）。"""
    found: list[str] = []

    def _walk(v):
        if isinstance(v, str):
            found.extend(m.group(1).strip() for m in _PLACEHOLDER_RE.finditer(v))
        elif isinstance(v, dict):
            for x in v.values():
                _walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                _walk(x)

    _walk(value)
    # 去掉仍能在 variables 里找到的（说明是被替换后残留的假阳性）
    return sorted({k for k in found if k not in variables})


def collect_placeholders(value: Any) -> list[str]:
    """收集模板中出现的所有占位符名（去重、保序）。"""
    out: list[str] = []

    def _walk(v):
        if isinstance(v, str):
            out.extend(m.group(1).strip() for m in _PLACEHOLDER_RE.finditer(v))
        elif isinstance(v, dict):
            for x in v.values():
                _walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                _walk(x)

    _walk(value)
    seen: set[str] = set()
    return [k for k in out if not (k in seen or seen.add(k))]


def missing_variables(value: Any, variables: Iterable[str]) -> list[str]:
    """返回模板引用但上下文中不存在的变量名。"""
    known = set(variables)
    return [k for k in collect_placeholders(value) if k not in known]
