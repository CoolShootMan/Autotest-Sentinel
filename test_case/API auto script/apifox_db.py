"""Database connection helpers for migrated Apifox tests.

Connection definitions are read from `_apifox_export/data/database_connections.json`.
Only the connection referenced by a scenario step is instantiated lazily.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_FILE = ROOT / "_apifox_export" / "data" / "database_connections.json"


def load_connections():
    data = json.load(open(DB_FILE, encoding="utf-8"))
    return {c["name"]: c for c in data.get("data", [])}


class ApifoxDB:
    def __init__(self):
        self._connections = load_connections()
        self._pools = {}

    def get_config(self, name):
        conn = self._connections.get(name)
        if not conn:
            raise ValueError(f"Database connection {name!r} not found")
        return conn

    def execute(self, name, sql, params=None):
        """Execute SQL on the named connection.

        Uses SQLAlchemy if available; falls back to the raw driver.
        """
        config = self.get_config(name)
        ctype = config.get("type", "postgresql")
        cfg = config.get("configs", {}).get("default", {})
        if ctype == "postgresql":
            return self._execute_pg(cfg, sql, params)
        if ctype == "mysql":
            return self._execute_mysql(cfg, sql, params)
        raise NotImplementedError(f"DB type {ctype!r} not supported yet")

    def _execute_pg(self, cfg, sql, params):
        try:
            from sqlalchemy import create_engine, text
        except ImportError as e:
            raise ImportError("SQLAlchemy is required for DB steps: pip install sqlalchemy psycopg2-binary") from e
        url = (
            f"postgresql+psycopg2://{cfg.get('username')}:{cfg.get('password')}"
            f"@{cfg.get('host')}:{cfg.get('port', 5432)}/{cfg.get('database')}"
        )
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            return [dict(row._mapping) for row in result]

    def _execute_mysql(self, cfg, sql, params):
        try:
            from sqlalchemy import create_engine, text
        except ImportError as e:
            raise ImportError("SQLAlchemy is required for DB steps: pip install sqlalchemy pymysql") from e
        url = (
            f"mysql+pymysql://{cfg.get('username')}:{cfg.get('password')}"
            f"@{cfg.get('host')}:{cfg.get('port', 3306)}/{cfg.get('database')}"
        )
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            return [dict(row._mapping) for row in result]
