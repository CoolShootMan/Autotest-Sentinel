"""全局运行配置。

所有可调项集中在这里，环境变量优先（便于 CI 覆盖），其次是默认值。
业务用例不应直接读环境变量，统一通过本模块或 ``ctx`` 取值。

环境变量
--------
``API_ENV``           运行环境名，对应 config/environments/<name>.yaml（默认 Release）
``API_TIMEOUT``       单请求超时秒数（默认 45）
``API_RETRIES``       瞬时故障重试次数（默认 3）
``API_LOG_LEVEL``     日志级别（默认 INFO）
``API_LOG_BODY``      是否打印请求/响应体，1/true 开启（默认关闭）
"""
from __future__ import annotations

import os
from pathlib import Path

# --- 路径 ---------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent          # 工程根目录
CONFIG_DIR = ROOT / "config"
ENV_DIR = CONFIG_DIR / "environments"
TESTS_DIR = ROOT / "tests"
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

# 运行期令牌文件：由前置用例（如 T0000）写入，供后续用例读取
RUNTIME_TOKENS_FILE = ENV_DIR / "_runtime_tokens.yaml"


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "") or default)
    except ValueError:
        return default


def _bool_env(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


# --- 运行参数 -----------------------------------------------------------
ENV_NAME: str = os.environ.get("API_ENV", "Release")
TIMEOUT: int = _int_env("API_TIMEOUT", 45)
RETRIES: int = _int_env("API_RETRIES", 3)
LOG_LEVEL: str = os.environ.get("API_LOG_LEVEL", "INFO").upper()
LOG_BODY: bool = _bool_env("API_LOG_BODY", False)

# 重试策略：仅对瞬时故障重试，不重试 4xx 业务错误
RETRY_STATUS_FORCELIST = (429, 500, 502, 503, 504)
RETRY_BACKOFF_FACTOR = 0.5

# 触发重试的瞬时异常
RETRY_EXCEPTIONS = (
    "ConnectionError",
    "ConnectTimeout",
    "ReadTimeout",
    "Timeout",
    "ChunkedEncodingError",
    "ProtocolError",
    "SSLError",
)
