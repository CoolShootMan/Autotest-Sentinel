"""统一日志。

* 控制台输出保持单行、可 grep，格式：``[API] POST /auth/sign-in -> 200 (312ms)``
* 可选把请求/响应原文写入 HTTP 日志，便于失败复盘。落盘路径由 ``run_archive``
  在会话开始时切换为 ``results/runs/<run_id>/http.log``（按运行切分）；
  未启用归档时回退到 ``results/http.log``。
* 若安装了 ``allure-pytest``，自动把请求/响应附加到 Allure 报告（缺失时静默跳过）
"""
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

from config import settings

_LOGGER_NAME = "api.framework"
_configured = False
_lock = threading.Lock()

# 需要脱敏的请求头（不写入日志）
_SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "pear-client-secret",
                      "pear-autotesting", "x-api-key"}


def get_logger() -> logging.Logger:
    global _configured
    if not _configured:
        with _lock:
            if not _configured:
                _configure()
                _configured = True
    return logging.getLogger(_LOGGER_NAME)


def _configure() -> None:
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False


def mask_headers(headers: dict) -> dict:
    """对敏感请求头做脱敏。"""
    out = {}
    for k, v in (headers or {}).items():
        out[k] = "***" if k.lower() in _SENSITIVE_HEADERS else v
    return out


def truncate(text: Any, limit: int = 800) -> str:
    s = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False, default=str)
    return s if len(s) <= limit else s[:limit] + f"...(+{len(s) - limit})"


def log_request(method: str, url: str, headers: dict | None = None, body: Any = None) -> None:
    logger = get_logger()
    logger.info(f"[API] --> {method.upper()} {url}")
    if settings.LOG_BODY:
        if headers:
            logger.info(f"      headers: {truncate(mask_headers(headers), 400)}")
        if body not in (None, ""):
            logger.info(f"      body   : {truncate(body)}")


def log_response(status: int, elapsed_ms: float, body: Any = None) -> None:
    logger = get_logger()
    logger.info(f"[API] <-- {status} ({elapsed_ms:.0f}ms)")
    if settings.LOG_BODY and body not in (None, ""):
        logger.info(f"      body   : {truncate(body)}")


def log_warning(message: str) -> None:
    get_logger().warning(f"[API] !! {message}")


# --- Allure（可选） ------------------------------------------------------
def attach(name: str, content: Any, content_type: str = "text/plain") -> None:
    """把内容附加到 Allure 报告；未安装 allure 时静默跳过。"""
    try:
        import allure  # type: ignore
    except Exception:
        return
    try:
        text = content if isinstance(content, str) else json.dumps(
            content, ensure_ascii=False, indent=2, default=str)
        allure.attach(text, name=name, attachment_type=getattr(
            allure.attachment_type, "TEXT", "text/plain"))
    except Exception:
        pass


# --- 落盘 ---------------------------------------------------------------
#: 当前运行的 HTTP 日志路径；由 ``core.run_archive.begin()`` 设置，None 时用默认路径
_current_http_log: Path | None = None


def set_http_log_path(path: Path | None) -> None:
    """把 HTTP 报文日志切到指定文件（按运行归档时调用）。"""
    global _current_http_log
    _current_http_log = Path(path) if path else None


def http_log_path() -> Path:
    """当前 HTTP 日志文件（未启用归档时为 ``results/http.log``）。"""
    if _current_http_log is not None:
        return _current_http_log
    return settings.RESULTS_DIR / "http.log"


def append_http_log(record: dict) -> None:
    """把一条请求/响应记录追加到当前 HTTP 日志。"""
    try:
        path = http_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass
