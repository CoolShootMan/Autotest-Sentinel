"""JSONPath 取值。

支持 Apifox 用例中用到的三种表达式：

1. 普通路径      ``$.data.items[0].id``   —— 逐级下钻，数组用 ``[n]``
2. 过滤路径      ``$.data.modules[?(@.title=="Upcoming Events")].id``
                  —— 在数组里按字段值定位**首个**命中元素，再继续下钻
3. 递归路径      ``$.data..ticketRedemptions..status``
                  ``..`` 表示「在任意后代层级查找该键」，返回所有命中值

设计要点
--------
* 数组下标既可写在段内（``items[0]``），也可作为独立段（``0``）——两者都支持
* 过滤谓词支持 ``@.field == "value"`` / ``== 123`` / ``!= ...``，字段可嵌套（``@.a.b``）
* 取值失败一律返回 ``None`` / 空列表，不抛异常（与旧实现一致，便于断言给出可读的失败信息）
"""
from __future__ import annotations

import re
from typing import Any

_RECURSIVE_SPLIT = re.compile(r"\.\.")


def _split_dots(e: str) -> list[str]:
    """按 ``.`` 拆段，但**不拆**方括号内部（过滤谓词里含 ``@.field``）。

    >>> _split_dots('data.items[0].id')
    ['data', 'items[0]', 'id']
    >>> _split_dots('data.modules[?(@.title=="Events")].id')
    ['data', 'modules[?(@.title=="Events")]', 'id']
    """
    out: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in e:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        if ch == "." and depth == 0:
            if buf:
                out.append("".join(buf))
                buf = []
            continue
        buf.append(ch)
    if buf:
        out.append("".join(buf))
    return [s for s in out if s]


def _has_top_level_double_dot(e: str) -> bool:
    """``..`` 只在中括号之外才算递归标记。"""
    depth = 0
    for i, ch in enumerate(e):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif ch == "." and depth == 0 and i + 1 < len(e) and e[i + 1] == ".":
            return True
    return False


def parse(expr: str) -> tuple[list[str], bool]:
    """把表达式拆成段列表，并标记是否为递归路径。

    >>> parse("$.data.items[0].id")
    (['data', 'items[0]', 'id'], False)
    >>> parse("$.data..units..status")
    (['data', 'units', 'status'], True)
    >>> parse('$.data.modules[?(@.title=="E")].id')
    (['data', 'modules[?(@.title=="E")]', 'id'], False)
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
    recursive = _has_top_level_double_dot(e)
    if recursive:
        segments: list[str] = []
        for chunk in _RECURSIVE_SPLIT.split(e):
            segments.extend(_split_dots(chunk))
    else:
        segments = _split_dots(e)
    return [s for s in segments if s], recursive


def _step(cur: Any, key: Any) -> Any:
    """沿单个段下钻一层。"""
    if cur is None:
        return None
    if key == "length" and isinstance(cur, (list, tuple, str, dict)):
        # 支持 ``$.data.items.length``：Apifox 用例常用它做数量断言
        return len(cur)
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
            rest = rest[:-1]  # 去掉收尾的 ']'
            if rest.startswith("?"):
                return _filter_first(sub, rest[1:])
            try:
                idx = int(rest)
            except (TypeError, ValueError):
                return None
            return sub[idx] if isinstance(sub, list) and 0 <= idx < len(sub) else None
        return cur.get(key)
    return None


#: ``?(...)`` 过滤谓词：``@.field == "value"`` / ``@.field == 123`` / ``@.a.b == 1``
_FILTER_RE = re.compile(
    r"^\(?\s*@\.(?P<field>[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*)\s*"
    r"(?P<op>==|!=)\s*(?P<val>.+?)\s*\)?$"
)


def _literal(raw: str) -> Any:
    """把过滤谓词右侧的字面量还原成 Python 值。"""
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "none"):
        return None
    try:
        return int(s)
    except (TypeError, ValueError):
        pass
    try:
        return float(s)
    except (TypeError, ValueError):
        return s


def _filter_first(sub: Any, predicate: str) -> Any:
    """在数组 ``sub`` 中按谓词匹配，返回**第一个**命中的元素。

    Apifox 用例里形如 ``$.data.shopModules[?(@.title=="Upcoming Events")].id``
    的取值很常见：先在数组里按字段值定位元素，再继续下钻。这里只实现
    「首个命中」语义；未命中返回 ``None``（与 :func:`get` 的失败语义一致）。
    """
    if not isinstance(sub, list):
        return None
    m = _FILTER_RE.match(predicate.strip())
    if not m:
        return None
    field, op = m.group("field"), m.group("op")
    want = _literal(m.group("val"))
    for item in sub:
        if not isinstance(item, dict):
            continue
        got: Any = item
        for seg in field.split("."):
            got = got.get(seg) if isinstance(got, dict) else None
            if got is None:
                break
        if (got == want) if op == "==" else (got != want):
            return item
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
