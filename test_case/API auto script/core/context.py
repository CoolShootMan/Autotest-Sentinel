"""变量上下文。

一个 dict 语义的对象，承载「全局 → 环境 → 运行期令牌 → 用例私有」四层合并后的变量。

之所以实现成 ``MutableMapping`` 而不是普通 dict：

* 既有 146 条用例里有大量手写逻辑直接操作 ``vars['x'] = ...`` / ``vars.get('x')``，
  实现为 Mapping 后这些代码**无需改动**即可继续工作；
* 同时提供 ``render`` / ``extract`` / ``save_runtime`` 等框架能力。

用例内通过 conftest 提供的 ``ctx`` fixture 获取，并约定 ``vars = ctx`` 别名以兼容旧写法。
"""
from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any, Iterator

from config import env_loader
from core import jsonpath, templating


class Context(MutableMapping):
    """分层变量上下文。"""

    def __init__(self, base_url: str, variables: dict | None = None,
                 *, env_name: str = "", case_vars_file: str = ""):
        self.base_url = base_url
        self.env_name = env_name
        self.case_vars_file = case_vars_file
        self._vars: dict = dict(variables or {})
        # 记录本用例新增/覆盖的键，便于报告与调试
        self._initial_keys = set(self._vars)

    # --- MutableMapping 协议 -------------------------------------------
    def __getitem__(self, key: str) -> Any:
        return self._vars[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._vars[key] = value

    def __delitem__(self, key: str) -> None:
        del self._vars[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._vars)

    def __len__(self) -> int:
        return len(self._vars)

    def __contains__(self, key: object) -> bool:
        return key in self._vars

    def __repr__(self) -> str:
        return f"Context(env={self.env_name!r}, vars={len(self._vars)}, base_url={self.base_url!r})"

    # --- 框架能力 -------------------------------------------------------
    def render(self, value: Any) -> Any:
        """渲染 ``{{变量}}`` 占位符（递归）。"""
        return templating.render(value, self._vars)

    def render_text(self, template: str) -> str:
        return templating.render_text(template, self._vars)

    def missing(self, value: Any) -> list[str]:
        """返回模板引用但上下文缺失的变量名。"""
        return templating.missing_variables(value, self._vars)

    def extract(self, name: str, response, expr: str, default: Any = None) -> Any:
        """从响应中提取变量并写回上下文。

        Args:
            name:     变量名
            response: ApiResponse
            expr:     JSONPath 表达式（支持 ``..`` 递归）
            default: 未命中时的取值（默认 ``None``）
        """
        value = response.path(expr, default)
        self._vars[name] = value
        return value

    def extract_many(self, mapping: dict, response) -> dict:
        """批量提取：``{"token": "$.data.token", ...}``。"""
        return {k: self.extract(k, response, expr) for k, expr in mapping.items()}

    def run_db(self, connection_id: int, sql: str, extractors=None) -> list:
        """执行 Apifox ``database`` 步骤并把结果绑定回上下文。

        迁移器丢弃了 ``type="database"`` 处理器，导致断言基准（如
        ``order_count0``、``total_revenue``）恒为空串。本方法还原该行为。

        Args:
            connection_id: Apifox 连接 id（如 ``112809``）。
            sql:           原生 SQL。
            extractors:    ``[("变量名", "$[0].列名"), ...]``。

        Returns:
            查询结果行列表。
        """
        from core import db as _db

        # SQL 里同样可以引用 {{变量}}（Apifox 在执行前渲染），例如
        # ``WHERE promoter_id = '{{merchant_id}}'``。
        rendered_sql = self.render_text(sql)
        rows = _db.query(connection_id, rendered_sql, self._vars)
        for name, expr in (extractors or []):
            self._vars[name] = _db.extract(rows, expr)
        return rows

    def set(self, name: str, value: Any) -> None:
        self._vars[name] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._vars.get(key, default)

    def setdefault(self, key: str, default: Any = None) -> Any:
        return self._vars.setdefault(key, default)

    # --- 运行期令牌 -----------------------------------------------------
    def save_runtime(self, keys: list[str] | None = None) -> dict:
        """把变量持久化到运行期令牌文件，供后续用例读取。

        Args:
            keys: 需要持久化的键；``None`` 表示本用例新增的全部键。
        """
        if keys is None:
            keys = [k for k in self._vars if k not in self._initial_keys]
        payload = {k: self._vars[k] for k in keys if self._vars.get(k) is not None}
        if payload:
            env_loader.save_runtime_tokens(payload)
        return payload

    # --- 调试 -----------------------------------------------------------
    def snapshot(self) -> dict:
        return dict(self._vars)

    def new_keys(self) -> list[str]:
        return [k for k in self._vars if k not in self._initial_keys]

    def overridden_keys(self) -> list[str]:
        """被本用例覆盖的初始键（用于发现用例间变量污染）。"""
        return [k for k in self._vars if k in self._initial_keys and self._vars[k] is None]
