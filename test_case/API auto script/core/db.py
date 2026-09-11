"""执行 Apifox ``database`` 处理器（迁移后丢失的能力）。

背景
----
Apifox 的 step 可以是 ``type="database"``：直接对配置好的连接跑原生 SQL，
再用 ``jsonPath``（形如 ``$[0].order_count``）把结果列绑定为环境变量。
例如 T3100/T3130 的断言基准 ``order_count0`` / ``total_revenue`` 就是 SQL 查出来的。

迁移器**完全忽略了这类处理器**，于是这些基准值变成空串，断言拿
``期望: ''`` 去比真实数据，必然失败。本模块把这项能力补回来。

连接定义来自 ``_apifox_export/data/database_connections.json``，其中 host /
username / password / database 是 ``{{release_sql_*}}`` 模板，用当前环境变量渲染。

用法::

    ctx.run_db(112809, "SELECT COUNT(*) AS c FROM ...", [("today_count", "$[0].c")])
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONNECTIONS_FILE = ROOT / "_apifox_export" / "data" / "database_connections.json"

_TEMPLATE = re.compile(r"\{\{(\w+)\}\}")
# Apifox 的 jsonPath 有两种写法：``$[0].count`` 和 ``$.[0].count``（多一个点）
_INDEX_THEN_KEY = re.compile(r"^\$\.?\[(\d+)\](?:\.(.+))?$")
_KEY_ONLY = re.compile(r"^\$\.?(.+)$")

# 连接名 -> 已建 engine，避免每条用例都重新握手
_ENGINES: dict = {}


class DatabaseError(RuntimeError):
    """数据库步骤执行失败。"""


@lru_cache(maxsize=1)
def _connections() -> dict:
    """``connection_id -> connection dict``。"""
    if not CONNECTIONS_FILE.exists():
        raise DatabaseError(f"连接定义文件不存在: {CONNECTIONS_FILE}")
    data = json.loads(CONNECTIONS_FILE.read_text(encoding="utf-8"))
    return {c["id"]: c for c in data.get("data", [])}


def _render(value, env_vars: dict) -> str:
    """把 ``{{var}}`` 用环境变量渲染；未定义的变量保持原样。"""
    return _TEMPLATE.sub(lambda m: str(env_vars.get(m.group(1), m.group(0))), str(value))


def connection_config(connection_id: int, env_vars: dict | None = None) -> dict:
    """解析某个连接的最终参数（host/port/username/password/database）。"""
    env_vars = env_vars or {}
    conn = _connections().get(connection_id)
    if conn is None:
        raise DatabaseError(f"未找到 connectionId={connection_id} 的连接定义")
    raw = dict((conn.get("configs") or {}).get("default") or {})
    cfg = {k: _render(v, env_vars) for k, v in raw.items()}
    cfg["type"] = conn.get("type", "postgresql")
    return cfg


def _engine(connection_id: int, env_vars: dict):
    key = (connection_id, tuple(sorted((k, str(v)) for k, v in env_vars.items()
                                      if k.startswith("release_sql"))))
    if key in _ENGINES:
        return _ENGINES[key]
    try:
        from sqlalchemy import create_engine
    except ImportError as exc:  # pragma: no cover - 环境未装驱动时给出可读提示
        raise DatabaseError(
            "需要 sqlalchemy + 驱动才能执行数据库步骤："
            "pip install sqlalchemy psycopg2-binary"
        ) from exc

    cfg = connection_config(connection_id, env_vars)
    ctype = cfg["type"]
    auth = f"{cfg.get('username', '')}:{cfg.get('password', '')}"
    host = cfg.get("host", "")
    db = cfg.get("database", "")
    if ctype == "mysql":
        url = f"mysql+pymysql://{auth}@{host}:{cfg.get('port', 3306)}/{db}"
    else:
        url = f"postgresql+psycopg2://{auth}@{host}:{cfg.get('port', 5432)}/{db}"
    engine = create_engine(url, connect_args={"connect_timeout": 15}, pool_pre_ping=True)
    _ENGINES[key] = engine
    return engine


def query(connection_id: int, sql: str, env_vars: dict | None = None) -> list:
    """执行 SQL，返回 ``[ {列名: 值}, ... ]``。"""
    from sqlalchemy import text

    engine = _engine(connection_id, env_vars or {})
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            return [dict(row._mapping) for row in result]
    except Exception as exc:  # noqa: BLE001 - 统一包成可读的领域异常
        raise DatabaseError(f"SQL 执行失败 (connectionId={connection_id}): {exc}") from exc


def extract(rows: list, expr: str):
    """按 Apifox 风格的 jsonPath 取值。

    支持 ``$[0].field`` / ``$[0].a.b`` / ``$.field``（取第一行）。
    """
    if not rows:
        return None
    e = (expr or "").strip()
    m = _INDEX_THEN_KEY.match(e)
    if m:
        idx = int(m.group(1))
        if idx >= len(rows):
            return None
        row = rows[idx]
        tail = m.group(2)
        return _dig(row, tail) if tail else row
    m = _KEY_ONLY.match(e)
    if m:
        return _dig(rows[0], m.group(1))
    # 无 jsonPath：直接返回首行（extractFirstRecord 语义）
    return rows[0]


def _dig(row: dict, path: str):
    cur = row
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur
