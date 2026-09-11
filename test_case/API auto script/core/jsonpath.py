"""JSONPath 取值。

支持 Apifox 用例中用到的两种表达式：

1. 普通路径      ``$.data.items[0].id``   —— 逐级下钻，数组用 ``[n]``
2. 递归路径      ``$.data..ticketRedemptions..status``
                  ``..`` 表示「在任意后代层级查找该键」，返回所有命中值

设计要点
--------
* 数组下标既可写在段内（``items[0]``），也可作为独立段（``0``）——两者都支持
* 取值失败一律返回 ``None`` / 空列表，不抛异常（与旧实现一致，便于断言给出可读的失败信息）
"""
from __future__ import annotations

import re
from typing import Any

_RECURSIVE_SPLIT = re.compile(r"\.\.")


def parse(expr: str) -> tuple[list[str], bool]:
    """把表达式拆成段列表，并标记是否为递归路径。

    >>> parse("$.data.items[0].id")
    (['data', 'items[0]', 'id'], False)
    >>> parse("$.data..units..status")
    (['data', 'units', 'status'], True)
    """
    if not isinstance(expr, str):
        return [], False
    e = expr.strip()
    if e.startswith("$"):
        e = e[1:]
    if e.startswith("."):
        e = e[1:]
    if not e:
        return [], False
    recursive = ".." in e
    if recursive:
        segments = [s for s in _RECURSIVE_SPLIT.split(e) if s]
    else:
        segments = [s for s in e.split(".") if s]
    return segments, recursive


def _step(cur: Any, key: Any) -> Any:
    """沿单个段下钻一层。"""
    if cur is None:
        return None
    if isinstance(cur, list):
        try:
            idx = int(key)
        except (TypeError, ValueError):
            return None
        return cur[idx] if 0 <= idx < len(cur) else None
    if isinstance(cur, dict):
        if isinstance(key, str) and key.endswith("]") and "[" in key:
            name, _, rest = key.partition("[")
            sub = cur.get(name)
            try:
                idx = int(rest.rstrip("]"))
            except (TypeError, ValueError):
                return None
            return sub[idx] if isinstance(sub, list) and 0 <= idx < len(sub) else None
        return cur.get(key)
    return None


def get(obj: Any, segments: list) -> Any:
    """按段列表逐级取值，失败返回 ``None``。"""
    cur = obj
    for seg in segments:
        cur = _step(cur, seg)
        if cur is None:
            return None
    return cur


def _find_all(cur: Any, key: str):
    """在任意后代层级查找 ``key``，产出所有命中值（保序）。"""
    if cur is None:
        return
    if isinstance(cur, dict):
        for k, v in cur.items():
            if k == key:
                yield v
            yield from _find_all(v, key)
    elif isinstance(cur, list):
        for v in cur:
            yield from _find_all(v, key)


def get_recursive(obj: Any, segments: list) -> list:
    """递归路径取值：首段按普通键解析，其后每段在任意后代层级匹配。"""
    if not segments:
        return [obj] if obj is not None else []
    if isinstance(obj, dict) and segments[0] in obj:
        pool: list = [obj[segments[0]]]
    else:
        pool = [None]
    for seg in segments[1:]:
        pool = [v for cur in pool for v in _find_all(cur, seg)]
    return pool


def query(obj: Any, expr: str) -> list:
    """统一入口：返回所有命中值的列表（非递归路径返回 0 或 1 个元素）。"""
    segments, recursive = parse(expr)
    if not segments:
        return [obj] if obj is not None else []
    if recursive:
        return get_recursive(obj, segments)
    val = get(obj, segments)
    return [] if val is None else [val]


def query_one(obj: Any, expr: str, default: Any = None) -> Any:
    """返回首个命中值，未命中返回 ``default``。"""
    hits = query(obj, expr)
    return hits[0] if hits else default
