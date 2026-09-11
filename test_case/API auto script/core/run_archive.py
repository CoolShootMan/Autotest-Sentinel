"""每次运行的归档器（由 ``conftest`` 的 pytest 钩子驱动）。

设计目标
--------
1. **按运行切分** —— 每次 ``pytest`` 独占 ``results/runs/<run_id>/``，
   原先跨天跨次混写的 ``results/http.log`` 被拆开，复盘不再串台。
2. **零参数** —— ``python -m pytest`` / ``python run_suite.py`` 直接就有归档，
   不必再记 ``--junitxml=`` / ``--html=`` 这类参数。
3. **可回退** —— ``--no-archive`` 一键关掉，行为回到旧的全局 ``results/http.log``。
4. **永不阻断** —— 归档失败只打印告警，绝不影响用例结果与退出码。

产物布局::

    results/
      http.log                      ← 恒指向最近一次运行（符号链接，旧习惯可用）
      RUNS.md                       ← 运行历史索引（一次运行一行）
      latest -> runs/<run_id>       ← 最近一次运行的目录
      runs/<run_id>/
        meta.json      运行元信息（环境 / 入参 / 计数 / 耗时）
        summary.md     人读汇总（统计 + 失败明细 + 最慢用例）
        failures.json  机读失败清单（含失败前最后一个 HTTP 记录）
        junit.xml      JUnit 报告（Jenkins / CI 可直接消费）
        http.log       本次运行的 HTTP 报文（JSONL）
      _legacy/http_<ts>.log         ← 改造前的全局 http.log，仅归档一次

``<run_id>`` 形如 ``20260910_141530_linda``（时间戳 + 可选标签）。
"""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import pytest

from config import settings
from core import logging_util

RESULTS_DIR = settings.RESULTS_DIR
RUNS_DIR = RESULTS_DIR / "runs"
LEGACY_DIR = RESULTS_DIR / "_legacy"
GLOBAL_HTTP_LOG = RESULTS_DIR / "http.log"
HISTORY_FILE = RESULTS_DIR / "RUNS.md"
LATEST_LINK = RESULTS_DIR / "latest"

_state: dict[str, Any] = {}

# nodeid -> http.log byte size at the moment the test finished.
#
# Failure dicts are only built at session end (see ``_finish``), when http.log
# already contains every later request. Reading the file tail at that point
# blames the wrong request -- with 4 failures they all reported the *last*
# test's request. Snapshotting the size per test keeps attribution exact.
_END_OFFSETS: dict[str, int] = {}


def mark_test_end(nodeid: str) -> None:
    """Remember how far http.log had grown when ``nodeid`` finished."""
    path = logging_util.http_log_path()
    if path is None:
        return
    try:
        _END_OFFSETS[nodeid] = path.stat().st_size
    except OSError:
        pass


# --- 生命周期 -----------------------------------------------------------
def _slug(text: str) -> str:
    s = re.sub(r"[^0-9A-Za-z]+", "-", (text or "").strip()).strip("-").lower()
    return s[:32]


def new_run_id(label: str | None = None) -> str:
    """``20260910_141530`` 或 ``20260910_141530_linda``。"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slug(label or "")
    return f"{ts}_{slug}" if slug else ts


def begin(label: str | None = None, args: list[str] | None = None) -> Path:
    """建立本次运行目录，并把 HTTP 日志切到运行目录内。返回运行目录。"""
    run_dir = RUNS_DIR / new_run_id(label)
    run_dir.mkdir(parents=True, exist_ok=True)

    # 改造前的全局 http.log（真实文件）只归档一次；之后的 results/http.log 是符号链接
    if GLOBAL_HTTP_LOG.exists() and not GLOBAL_HTTP_LOG.is_symlink():
        LEGACY_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.fromtimestamp(
            GLOBAL_HTTP_LOG.stat().st_mtime).strftime("%Y%m%d_%H%M%S")
        target = LEGACY_DIR / f"http_{stamp}.log"
        i = 1
        while target.exists():
            target = LEGACY_DIR / f"http_{stamp}_{i}.log"
            i += 1
        shutil.move(str(GLOBAL_HTTP_LOG), str(target))

    log_path = run_dir / "http.log"
    log_path.touch()
    logging_util.set_http_log_path(log_path)
    _link_latest(run_dir)
    _link_global_log(log_path)

    _END_OFFSETS.clear()
    _state.clear()
    _state.update({
        "run_id": run_dir.name,
        "dir": run_dir,
        "log": log_path,
        "start": time.time(),
        "started_at": datetime.now(),
        "args": list(args if args is not None else sys.argv),
        "result": None,
    })
    return run_dir


def active() -> bool:
    return bool(_state)


def detach() -> None:
    """``--no-archive``：断开与最近一次运行的链接，回到全局 ``results/http.log``。

    否则软链会让本次的报文追加进上一次运行的文件里。
    """
    logging_util.set_http_log_path(None)
    try:
        if os.path.islink(GLOBAL_HTTP_LOG):
            GLOBAL_HTTP_LOG.unlink()
    except OSError:
        pass


def run_dir() -> Path | None:
    return _state.get("dir")


def junit_path() -> Path | None:
    d = _state.get("dir")
    return (d / "junit.xml") if d else None


# --- 归档收尾 -----------------------------------------------------------
def finish(config: Any, session: Any, terminalreporter: Any,
           entry_lookup: Callable[[str], dict] | None = None) -> Path | None:
    """写 summary.md / failures.json / meta.json，追加 RUNS.md。返回运行目录。"""
    if not _state:
        return None
    try:
        return _finish(config, session, terminalreporter, entry_lookup)
    except Exception as exc:                      # 归档失败不影响测试结果
        _state["error"] = f"{type(exc).__name__}: {exc}"
        print(f"\n[archive] 归档失败（不影响用例结果）: {type(exc).__name__}: {exc}")
        return None


def _finish(config: Any, session: Any, terminalreporter: Any,
            entry_lookup: Callable[[str], dict] | None) -> Path:
    stats = getattr(terminalreporter, "stats", None) or {}
    counts = _counts(stats)
    run_dir: Path = _state["dir"]
    log_path: Path = _state["log"]
    duration = time.time() - _state["start"]
    started: datetime = _state["started_at"]

    failures = [_failure(r, "failed", entry_lookup, log_path)
                for r in stats.get("failed", [])]
    failures += [_failure(r, "error", entry_lookup, log_path)
                 for r in stats.get("error", [])]

    slowest = sorted(
        ((_label_of(r, entry_lookup), round(getattr(r, "duration", 0.0), 2))
         for r in stats.get("passed", []) + stats.get("failed", [])
         if getattr(r, "when", "") == "call"),
        key=lambda x: -x[1],
    )[:10]

    label = config.getoption("--run-label", None) or ""
    meta = {
        "run_id": _state["run_id"],
        "label": label,
        "env": settings.ENV_NAME,
        "started_at": started.isoformat(timespec="seconds"),
        "duration_s": round(duration, 2),
        "exit_status": int(getattr(session, "exitstatus", 0) or 0),
        "counts": counts,
        "total": sum(counts[k] for k in
                     ("passed", "failed", "error", "skipped", "xfailed", "xpassed")),
        "args": _state["args"],
        "rootdir": str(getattr(config, "rootpath", getattr(config, "rootdir", ""))),
        "python": platform.python_version(),
        "pytest": pytest.__version__,
        "platform": f"{platform.system()}-{platform.release()} {platform.machine()}",
        "http_records": _count_lines(log_path),
        "failures": len(failures),
    }

    (run_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "failures.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "summary.md").write_text(
        _summary_md(meta, failures, slowest, log_path), encoding="utf-8")
    _append_history(meta)

    _state["result"] = meta
    return run_dir


def summary_line() -> str:
    """给终端汇总用的一行提示（未归档时返回空串）。"""
    meta = _state.get("result") if _state else None
    if not meta:
        return ""
    d: Path = _state["dir"]
    try:
        rel = d.relative_to(settings.ROOT)
    except ValueError:
        rel = d
    c = meta["counts"]
    return (f"{rel}   →   "
            f"{c['passed']} passed / {c['failed']} failed / {c['error']} error / "
            f"{c['skipped']} skipped   ·   {meta['http_records']} HTTP records\n"
            f"{' ' * 2}summary.md · failures.json · junit.xml · http.log")


# --- 内部工具 -----------------------------------------------------------
def _counts(stats: dict) -> dict:
    def n(key: str, when: str | None = None) -> int:
        return sum(1 for r in stats.get(key, [])
                   if when is None or getattr(r, "when", "") == when)
    return {
        "passed": n("passed", "call"),
        "failed": n("failed"),
        "error": n("error"),
        "skipped": n("skipped"),
        "xfailed": n("xfailed", "call"),
        "xpassed": n("xpassed", "call"),
        "deselected": n("deselected"),
    }


def _label_of(report: Any, entry_lookup: Callable[[str], dict] | None) -> str:
    nodeid = getattr(report, "nodeid", "")
    entry = (entry_lookup(nodeid) if entry_lookup else None) or {}
    name = entry.get("name") or nodeid.split("::")[-1]
    cid = entry.get("case_id")
    return f"[{cid}] {name}" if cid else name


def _failure(report: Any, kind: str, entry_lookup: Callable[[str], dict] | None,
             log_path: Path) -> dict:
    nodeid = getattr(report, "nodeid", "")
    # ``None`` means "no snapshot" -> fall back to reading to EOF.
    upto = _END_OFFSETS.get(nodeid)
    entry = (entry_lookup(nodeid) if entry_lookup else None) or {}
    text = (getattr(report, "longreprtext", "") or "").strip()
    return {
        "kind": kind,
        "case_id": entry.get("case_id"),
        "name": entry.get("name") or nodeid.split("::")[-1],
        "folder": entry.get("folder"),
        "tags": entry.get("tags", []),
        "nodeid": nodeid,
        "phase": getattr(report, "when", ""),
        "duration_s": round(getattr(report, "duration", 0.0), 2),
        "message": _first_error_line(text),
        "longrepr": text[:3000],
        "last_request": _tail_record(log_path, upto=upto),
    }


def _first_error_line(text: str) -> str:
    """取 ``--tb=short`` 输出里第一条 ``E ...`` 作为错误摘要。"""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("E "):
            return s[2:].strip()
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _tail_record(path: Path, upto: int | None = None) -> dict | None:
    """读取 JSONL 最后一条（失败前最近一次 HTTP 交互）。

    ``upto`` 是用例结束时的文件字节数：只看该位置之前的内容，避免把后续
    用例的请求算到这条失败上。为 None 时读到文件末尾。
    """
    try:
        with path.open("rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            end = size if upto is None else max(0, min(upto, size))
            if end == 0:
                return None
            block = min(end, 65536)
            fh.seek(end - block)
            lines = [ln for ln in fh.read(block).decode("utf-8", "replace").splitlines()
                     if ln.strip() and ln.lstrip().startswith("{")]
        return json.loads(lines[-1]) if lines else None
    except Exception:
        return None


def _count_lines(path: Path) -> int:
    try:
        with path.open("rb") as fh:
            return sum(1 for _ in fh)
    except Exception:
        return 0


def _link_latest(target: Path) -> None:
    _replace_symlink(LATEST_LINK, Path("runs") / target.name, is_dir=True)


def _link_global_log(log_path: Path) -> None:
    """``results/http.log`` 恒指向当次运行，保留旧的使用习惯（tail -f 等）。"""
    _replace_symlink(GLOBAL_HTTP_LOG,
                     Path("runs") / log_path.parent.name / "http.log", is_dir=False)


def _replace_symlink(link: Path, target: Path, is_dir: bool) -> None:
    try:
        if os.path.islink(link) or link.exists():
            if link.is_dir() and not link.is_symlink():
                shutil.rmtree(link)
            else:
                link.unlink()
        link.symlink_to(target, target_is_directory=is_dir)
    except OSError:
        pass                                       # 文件系统不支持符号链接时跳过


def _append_history(meta: dict) -> None:
    header = ("| Run ID | 环境 | 结果 | 耗时 | 报告 |\n"
              "|---|---|---|---|---|\n")
    row = (f"| `{meta['run_id']}` | {meta['env']} | "
           f"✅ {meta['counts']['passed']} / ❌ {meta['counts']['failed']}"
           f" / ⚠️ {meta['counts']['error']} | {_fmt_dur(meta['duration_s'])} | "
           f"[summary](runs/{meta['run_id']}/summary.md) |\n")
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("# 运行历史\n\n" + header + row, encoding="utf-8")
        return
    with HISTORY_FILE.open("a", encoding="utf-8") as fh:
        fh.write(row)


def _fmt_dur(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


def _summary_md(meta: dict, failures: list[dict], slowest: list[tuple[str, float]],
                log_path: Path) -> str:
    c = meta["counts"]
    executed = c["passed"] + c["failed"] + c["error"]
    rate = f"{c['passed'] / executed * 100:.1f}%" if executed else "-"
    verdict = "✅ 全部通过" if not (c["failed"] or c["error"]) else \
              f"❌ {c['failed'] + c['error']} 条失败"
    cmd = " ".join(meta["args"])

    L = [
        f"# 运行报告 · {meta['label'] or meta['run_id']}",
        "",
        f"**{verdict}**",
        "",
        "| 项 | 值 |",
        "|---|---|",
        f"| Run ID | `{meta['run_id']}` |",
        f"| 环境 | {meta['env']} |",
        f"| 开始时间 | {meta['started_at']} |",
        f"| 耗时 | {_fmt_dur(meta['duration_s'])} |",
        f"| 执行结果 | ✅ {c['passed']} passed · ❌ {c['failed']} failed · "
        f"⚠️ {c['error']} error · ⏭ {c['skipped']} skipped "
        f"（xfail {c['xfailed']} / xpass {c['xpassed']}） |",
        f"| 有效用例通过率 | {rate} |",
        f"| HTTP 记录 | {meta['http_records']} 条（`http.log`） |",
        f"| 机器 | {meta['platform']} · Python {meta['python']} · "
        f"pytest {meta['pytest']} |",
        f"| 命令 | `{cmd}` |",
        "",
    ]

    if failures:
        L += [f"## 失败明细（{len(failures)}）", ""]
        for i, f in enumerate(failures, 1):
            icon = "⚠️" if f["kind"] == "error" else "❌"
            L.append(f"### {i}. {icon} {f['name']}")
            L.append("")
            L.append(f"- **用例 ID**: {f['case_id'] or '-'}　**阶段**: "
                     f"{f['phase']}　**耗时**: {f['duration_s']}s")
            L.append(f"- **目录**: {f['folder'] or '-'}")
            L.append(f"- **节点**: `{f['nodeid']}`")
            if f["message"]:
                L.append(f"- **错误**: `{f['message']}`")
            lr = f.get("last_request")
            if lr:
                L.append(f"- **失败前最后一个请求**: `{lr.get('method', '')} "
                         f"{lr.get('url', '')}` → **{lr.get('status')}** "
                         f"({lr.get('elapsed_ms')}ms)")
                body = str(lr.get("response") or "")[:300]
                if body:
                    L.append(f"  ```\n  {body}\n  ```")
            L += ["", "<details><summary>完整 traceback</summary>", "",
                  "```", f["longrepr"] or "(empty)", "```", "", "</details>", ""]
    else:
        L += ["## 失败明细", "", "无 —— 本次运行没有失败用例。", ""]

    if slowest:
        L += ["## 最慢用例（Top 10）", "", "| 用例 | 耗时(s) |", "|---|---|"]
        L += [f"| {n} | {d} |" for n, d in slowest]
        L.append("")

    L += ["---", "",
          f"机器可读产物：`failures.json`（失败清单）、`meta.json`（元信息）、"
          f"`junit.xml`（CI 报告）、`http.log`（本次 {meta['http_records']} 条报文）。", ""]
    return "\n".join(L)
