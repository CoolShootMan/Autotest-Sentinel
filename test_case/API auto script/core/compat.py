"""迁移期兼容垫片。

为什么需要它
------------
146 条用例从 Apifox 迁移过来时，除自动生成的样板外还夹着**人工补丁**——
裸 ``assert``、for/if 分支、中间变量等。实测这些补丁里有 63 处调用旧辅助函数
``_get_path``、5 处 ``_render``、3 处 ``_url`` / ``client.session().request(...)``。

重构的目标是「用例层只写业务意图」，但这些人工补丁承载的是**真实校验逻辑**，
一旦改写就有引入语义偏差的风险。因此本模块按**原样复刻**原则提供等价实现，
让补丁代码零改动继续运行，同时把 ``apifox_client`` 这个迁移平台依赖从用例里摘掉。

======================  ==================================================================
名称                     说明
======================  ==================================================================
``get_path``            ``apifox_client._get_path`` 的逐字复刻（含 ``"items[0]"`` 段语义）
``get_path_recursive``  ``apifox_client._get_path_recursive`` 的逐字复刻（``..`` 递归）
``legacy_render``       等价于旧 ``_render(tmpl, vars)``
``legacy_url``          等价于旧 ``_url(base, path, vars)``
``LegacyClient``        ``client.session().request(method, url, **kw)`` 旧调用形态
======================  ==================================================================

.. warning::
   ``get_path`` 曾是 ``apifox_client._get_path`` 的**逐字复刻**，包括其缺陷：
   拿到 ``"data.token"`` 这类字符串时会逐字符迭代，**恒返回 ``None``**。
   2026-09 全量核查后已按预期语义修正（见 :func:`get_path` 的 versionchanged），
   列表入参行为不变。需要完整 JSONPath（过滤器/通配符）请用 :mod:`core.jsonpath`。
"""
from __future__ import annotations

from typing import Any

from core import templating

__all__ = [
    "LegacyClient",
    "get_path",
    "get_path_recursive",
    "legacy_render",
    "legacy_url",
]


# --- JSONPath 取值（apifox_client 复刻 + 字符串路径语义修正）-------------
def _split_str_path(path: str) -> list:
    """把 ``"$.data.token"`` / ``"data.token"`` / ``"code"`` 拆成段列表。

    ``"data.items[0].id"`` → ``['data', 'items[0]', 'id']``：下标仍由段内的
    ``[...]`` 语法承载，交回 :func:`get_path` 原逻辑处理。
    """
    p = path.strip()
    if p.startswith("$"):
        p = p[1:]
    while p.startswith("."):
        p = p[1:]
    return [seg for seg in p.split(".") if seg]


def get_path(obj: Any, path) -> Any:
    """沿路径逐级取值，失败返回 ``None``。

    ``path`` 支持两种形态：

    * **列表**（推荐）：``['data', 'token']``、``['data', 'items', 0, 'id']``
    * **字符串**：``'data.token'``、``'$.data.items[0].id'``、``'code'``

    .. note::
       段元素既可以是 dict 键（str）也可以是列表下标（int）；字符串段也接受
       ``"items[0]"`` 这种自带下标的写法。

    .. versionchanged:: 2026-09
       字符串 ``path`` 原先会被 ``for p in path`` **按字符**迭代
       （``"code"`` → ``'c' / 'o' / 'd' / 'e'``），从而**恒返回 ``None``**——
       这是 ``apifox_client._get_path`` 的迁移遗留缺陷。全量核查结论：146 条
       用例中依赖该 ``None`` 结果的反向断言（``assert ... is None``）共 **0** 处，
       而 6 处受影响调用点全部是正向提取/断言（必然失败），故按预期语义修正为
       按 ``"."`` 拆分。**列表入参行为完全不变。**
    """
    if isinstance(path, str):
        path = _split_str_path(path)
    cur = obj
    for p in path:
        if cur is None:
            return None
        if isinstance(cur, list):
            try:
                idx = int(p)
            except (TypeError, ValueError):
                return None
            cur = cur[idx] if 0 <= idx < len(cur) else None
        elif isinstance(cur, dict):
            if isinstance(p, str) and "[" in p and p.endswith("]"):
                key, _, rest = p.partition("[")
                sub = cur.get(key)
                try:
                    idx = int(rest.rstrip("]"))
                except (TypeError, ValueError):
                    cur = None
                else:
                    cur = sub[idx] if isinstance(sub, list) and 0 <= idx < len(sub) else None
            else:
                cur = cur.get(p)
        else:
            return None
    return cur


def get_path_recursive(obj: Any, segments: list) -> list:
    """递归路径取值（``$.data..status`` 语义），返回全部命中值（保序）。

    ``segments`` 传字符串时按 ``"."`` 拆分（与 :func:`get_path` 一致），
    避免 ``for seg in "$.a..b"`` 按字符迭代的同类缺陷。
    """
    if isinstance(segments, str):
        segments = _split_str_path(segments)
    def find_keys(cur, key):
        if cur is None:
            return
        if isinstance(cur, dict):
            for k, v in cur.items():
                if k == key:
                    yield v
                yield from find_keys(v, key)
        elif isinstance(cur, list):
            for v in cur:
                yield from find_keys(v, key)

    if not segments:
        return [obj] if obj is not None else []
    if isinstance(obj, dict) and segments[0] in obj:
        pool = [obj[segments[0]]]
    else:
        pool = [None]
    for seg in segments[1:]:
        pool = [v for cur in pool for v in find_keys(cur, seg)]
    return pool


# --- 旧辅助函数的等价实现 ----------------------------------------------
def legacy_render(ctx):
    """返回等价于旧 ``_render(tmpl, vars)`` 的函数。

    旧签名的第二个参数 ``vars`` 在既有补丁里恒等于用例上下文，故此处忽略它，
    统一用 ``ctx`` 渲染，避免调用方把上下文传错。
    """
    def _render(tmpl, vars=None):  # noqa: ARG001 - 保留旧签名
        if not isinstance(tmpl, str):
            return tmpl
        return templating.render_text(tmpl, ctx)

    return _render


def legacy_url(ctx):
    """返回等价于旧 ``_url(base, path, vars)`` 的函数。

    语义（与迁移前两版 ``_url`` 合并后的正确版本一致）：

    1. 路径渲染后已是绝对 URL（含 ``://``）→ 直接使用
    2. 其余 → ``base`` 渲染后拼接
    """
    def _url(base, path, vars=None):  # noqa: ARG001 - 保留旧签名
        p = templating.render_text(path, ctx) if isinstance(path, str) else path
        if isinstance(p, str) and p.startswith(("http://", "https://")):
            return p
        b = templating.render_text(base, ctx) if isinstance(base, str) else base
        return str(b) + str(p)

    return _url


class _LegacySession:
    """旧 ``requests.Session`` 的替代：把 ``.request()`` 转交给框架客户端。"""

    def __init__(self, ctx):
        self._ctx = ctx

    def request(self, method: str, url: str, headers=None, params=None,
                data=None, **kw) -> Any:
        return self._ctx.client.request(
            method, url, headers=headers, params=params, body=data
        )


class LegacyClient:
    """旧 ``ApifoxClient`` 的替代，只保留 ``.session()`` 调用形态。

    既有补丁的写法是 ``client.session().request('GET', _url(...), headers=..., data=None)``，
    其中 URL / 请求头 / 请求体都已渲染完毕，因此这里直接透传给
    :meth:`core.http_client.ApiClient.request`（绝对 URL 会被原样使用，
    重复渲染是幂等的）。
    """

    def __init__(self, ctx):
        self._ctx = ctx

    def session(self) -> _LegacySession:
        return _LegacySession(self._ctx)

    def request(self, method: str, url: str, **kw) -> Any:
        return self._ctx.client.request(method, url, **kw)
