#!/usr/bin/env python3
r"""生成 CI 的「完整测试结果」汇总（GitHub Actions Job Summary + 运行页注解）。

设计目标（对应需求）：
  1. **一眼可见** —— 通过率与失败用例名放在 Job Summary 最顶部（H1 + 速览表），
     并用 workflow command 发 notice/error 注解，让 run 页面顶部的 Annotations
     区块直接列出失败用例名，**不需要展开任何日志**。
  2. **如实记录** —— 每个用例的真实状态（passed / failed / broken / skipped）
     与失败原因逐条列出，失败排最前，不隐藏、不美化。
  3. **不中断执行** —— 本脚本只做「读结果 + 汇总」，任何一步读不到（缺文件 /
     缺目录）都降级成一句说明，绝不抛异常影响 CI 后续步骤。

数据来源与优先级：
  - UI 用例：首选 ``allure-results/<时间戳>/*-result.json``（能拿到逐条用例名）；
    退化到 ``run.log`` 里 pytest 的汇总行（``4 failed, 16 passed in 1234.56s``），
    此时只有计数、没有用例名。
  - API 预制：``results/runs/<run_id>_ui-automation-prefill/`` 下的
    ``meta.json``（计数）+ ``failures.json``（失败清单）+ ``summary.md``（人读）。

用法（CI 内）::

    # 1) 写 Job Summary（run 页面的 Summary 区块）
    python3 tools/ci_summary.py \
        --prefill-root "test_case/API auto script/results/runs" \
        --allure-root allure-results \
        --run-log log \          # 传目录：取最新的 log/<日期>.log（run.log 几乎为空）
        --event-name workflow_dispatch --sha abc1234 --outcome failure \
        --report-dir "report/html/20260920_031254" >> "$GITHUB_STEP_SUMMARY"

    # 2) 发运行页注解（run 页面顶部 Annotations 区块）+ 导出步骤输出
    python3 tools/ci_summary.py --github-annotations --outputs "$GITHUB_OUTPUT"

退出码恒为 0：这是只读汇总脚本，不允许它把 CI 拖红。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

STATUS_ICON = {"passed": "✅", "failed": "❌", "broken": "💥", "skipped": "⏭"}
STATUS_ORDER = {"failed": 0, "broken": 1, "passed": 2, "skipped": 3}
# 计入「通过率」分母的状态（skipped 不算失败，也不进分母）。
RATE_STATES = ("passed", "failed", "broken")
# GitHub 单个 step 最多接受 10 条 error 注解，超出会被静默丢弃。
ANNOTATION_MAX = 10


# ── 通用小工具 ──────────────────────────────────────────────────────────────

def _resolve_run_log(path: str) -> str:
    """允许 ``--run-log`` 传目录：取其中最新修改的 ``*.log``。

    main.py 把框架日志写到 ``log/<日期>.log``，而 ``run.log``（workflow 里
    ``python main.py 2>&1 | tee run.log``）只留下最后一行报告路径 —— 日志尾部、
    预制内 DB 行、pytest 汇总行其实都在 ``log/`` 下。传目录即可自动定位。
    """
    if not path or not os.path.isdir(path):
        return path
    candidates = glob.glob(os.path.join(path, "*.log"))
    if not candidates:
        return path
    return max(candidates, key=os.path.getmtime)

def _md_escape(text: str, limit: int = 300) -> str:
    """转义会破坏 Markdown 表格/单行的字符，并按需截断。"""
    s = (text or "").replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()
    return s[:limit] + ("…" if len(s) > limit else "")


def _cmd_escape(text: str, limit: int = 300) -> str:
    """转义 workflow command（``::error::``）的消息体与属性值。"""
    s = (text or "").replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    s = s.replace("\\", "\\\\").strip()
    return s[:limit] + ("…" if len(s) > limit else "")


def _newest(paths: list[str]) -> str | None:
    """按 mtime 取最新一项；无候选返回 None。"""
    cands = [p for p in paths if os.path.exists(p)]
    if not cands:
        return None
    return max(cands, key=os.path.getmtime)


def _first_line(detail: dict | None) -> str:
    """取 statusDetails 的首个有信息量的行（失败原因）。"""
    detail = detail or {}
    for key in ("message", "trace"):
        raw = (detail.get(key) or "").strip()
        if not raw:
            continue
        for line in raw.splitlines():
            line = line.strip()
            # 跳过 pytest 的定位噪音行（"self = ..." / 文件路径:行号）
            if not line or line.startswith(("self =", "E   ", "File \"")):
                continue
            return _md_escape(line)
    return ""


def _read_json(path: str):
    """读 JSON，失败返回 None（汇总脚本不允许因坏文件抛错）。"""
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return None


# ── 结果采集：UI 用例 ───────────────────────────────────────────────────────

def collect_ui_results(allure_root: str) -> tuple[str | None, list[dict], dict]:
    """解析 allure-results 下最新一次运行的每个用例结果。

    Returns:
        (结果目录, 用例列表, 状态计数)。目录缺失时返回 (None, [], {})。
    """
    dirs = sorted(glob.glob(os.path.join(allure_root, "*/")))
    if not dirs:
        return None, [], {}
    latest = max(dirs, key=os.path.getmtime)

    rows: list[dict] = []
    counts: dict[str, int] = {}
    for fp in glob.glob(os.path.join(latest, "*-result.json")):
        data = _read_json(fp)
        if not isinstance(data, dict):
            continue
        status = data.get("status") or "unknown"
        counts[status] = counts.get(status, 0) + 1
        start, stop = data.get("start"), data.get("stop")
        duration = f"{(stop - start) / 1000:.1f}s" if start and stop else ""
        rows.append({
            "name": _md_escape(data.get("name") or "(未命名用例)", 160),
            "status": status,
            "duration": duration,
            "reason": _first_line(data.get("statusDetails")),
        })
    rows.sort(key=lambda r: (STATUS_ORDER.get(r["status"], 9), r["name"]))
    return latest, rows, counts


# ── 结果采集：API 预制 ──────────────────────────────────────────────────────

def collect_prefill(prefill_root: str) -> dict:
    """取最新一次预制的目录 / summary.md / meta.json / 失败清单。"""
    out: dict = {"dir": None, "md": None, "meta": None, "failures": []}
    latest = _newest(glob.glob(os.path.join(prefill_root, "*ui-automation-prefill*")))
    if not latest:
        return out
    out["dir"] = latest

    md_path = os.path.join(latest, "summary.md")
    if os.path.exists(md_path):
        try:
            with open(md_path, encoding="utf-8", errors="replace") as fh:
                out["md"] = fh.read().strip()
        except Exception:  # noqa: BLE001
            out["md"] = None

    meta = _read_json(os.path.join(latest, "meta.json"))
    out["meta"] = meta if isinstance(meta, dict) else None

    fails = _read_json(os.path.join(latest, "failures.json"))
    if isinstance(fails, list):
        out["failures"] = [x for x in fails if isinstance(x, dict)]
    return out


def _prefill_meta_counts(meta: dict | None) -> dict:
    """把预制的 meta.json 计数映射成与 UI 侧一致的状态名。"""
    if not meta:
        return {}
    raw = meta.get("counts") or {}
    counts: dict[str, int] = {}
    for key, val in raw.items():
        key = {"error": "broken"}.get(key, key)
        if key in RATING_KEYS and isinstance(val, int):
            counts[key] = counts.get(key, 0) + val
    return counts


RATING_KEYS = ("passed", "failed", "broken", "skipped")


# ── 结果采集：日志 ──────────────────────────────────────────────────────────

def collect_db_lines(run_log: str, limit: int = 25) -> list[str]:
    """从 run.log 里捞出预制阶段的 DB 步骤日志（如 step 76 的别名写入）。"""
    if not os.path.exists(run_log):
        return []
    hits: list[str] = []
    with open(run_log, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "[db]" in line:
                hits.append(line.rstrip())
    return hits[-limit:]


def collect_log_tail(run_log: str, lines: int = 40) -> list[str]:
    if not os.path.exists(run_log):
        return []
    with open(run_log, encoding="utf-8", errors="replace") as fh:
        return [ln.rstrip() for ln in fh.readlines()[-lines:]]


# ── pytest 汇总行兜底解析 ───────────────────────────────────────────────────

# pytest 的收尾行形如 ``============ 4 failed, 16 passed in 1234.56s ============``，
# 尾部的 ``=`` 装饰不能把匹配卡死，所以不用 $ 锚定，只要求 ``in <秒>s`` 出现。
_SUMMARY_TIME_RE = re.compile(r"\bin\s+[\d.]+s\b")
_COUNT_RE = re.compile(
    r"(\d+)\s+(passed|failed|errors?|skipped|xfailed|xpassed|deselected|warnings?|rerun)\b"
)
_COUNT_KEY = {
    "error": "broken", "errors": "broken",
    "xpassed": "passed", "xfailed": "failed",
    "warning": "warnings", "warnings": "warnings",
}


def parse_pytest_summary(run_log: str) -> dict | None:
    """从 run.log 里取最后一行 pytest 汇总（如 ``4 failed, 16 passed in 123s``）。

    必须排除预制阶段那行 —— ``main.py`` 会把预制的 stdout 记进同一个 run.log
    （``Prefill stdout: 1 passed in 61.90s``），若把它当成 UI 结果，会在
    「UI 根本没跑」时误报 100% 通过。这里按「不含 prefill 字样 + 取最后一行」过滤：
    UI 的 pytest 汇总行永远排在预制之后。
    """
    if not os.path.exists(run_log):
        return None
    last: str | None = None
    with open(run_log, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if "prefill" in s.lower():
                continue
            if _SUMMARY_TIME_RE.search(s) and _COUNT_RE.search(s):
                last = s
    if not last:
        return None
    counts: dict[str, int] = {}
    for num, word in _COUNT_RE.findall(last):
        if not isinstance(word, str):
            continue
        key = _COUNT_KEY.get(word, word)
        counts[key] = counts.get(key, 0) + int(num)
    return {"line": last, "counts": counts}


# ── 指标计算 ────────────────────────────────────────────────────────────────

def _pass_rate(counts: dict) -> tuple[float | None, int]:
    """通过率 = passed / (passed + failed + broken)；skipped 不进分母。"""
    executed = sum(counts.get(k, 0) for k in RATE_STATES)
    if not executed:
        return None, 0
    return counts.get("passed", 0) / executed * 100.0, executed


def _bar(rate: float | None, width: int = 12) -> str:
    if rate is None:
        return ""
    filled = max(0, min(width, round(rate / 100 * width)))
    return "`" + "█" * filled + "░" * (width - filled) + "`"


def _counts_phrase(counts: dict) -> str:
    parts = []
    for key, label in (("passed", "通过"), ("failed", "失败"),
                       ("broken", "异常"), ("skipped", "跳过")):
        if counts.get(key):
            parts.append(f"{counts[key]} {label}")
    return " · ".join(parts) or "无用例结果"


# ── 汇总数据装配（Job Summary / 注解 / 输出 共用）───────────────────────────

# main.py 在跑 UI 用例【之前】就可能中止（前置/环境问题）。这些是「未跑用例」，
# 不是「用例失败」——必须在 summary 顶部与注解里区分开，否则会被误读成 20 条全挂。
_INFRA_ABORTS = (
    ("Login/EDU preflight FAILED", "登录态预检失败（dismiss EDU 走不通）"),
    ("Auth cookie preflight FAILED", "登录态预检失败（cookie 已不是登录态）"),
    ("API prefill FAILED", "API 预制失败"),
)


def detect_infra_abort(run_log: str) -> str | None:
    """识别 main.py 的「预检中止」，返回可读原因；没有则返回 None。"""
    if not run_log or not os.path.exists(run_log):
        return None
    try:
        with open(run_log, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except Exception:  # noqa: BLE001
        return None
    for needle, label in _INFRA_ABORTS:
        if needle in text:
            return label
    return None


def gather(args: argparse.Namespace) -> dict:
    """把三路来源装配成一份统一的结果快照。任何一步失败都降级，不抛错。"""
    allure_dir, rows, allure_counts = collect_ui_results(args.allure_root)
    prefill = collect_prefill(args.prefill_root)
    pytest_sum = parse_pytest_summary(args.run_log)

    ui_failed = [r for r in rows if r["status"] in ("failed", "broken")]
    if rows:
        ui_counts = allure_counts
        ui_source = f"allure-results 逐条结果（`{allure_dir}`）"
        ui_total = len(rows)
    elif pytest_sum:
        ui_counts = pytest_sum["counts"]
        ui_source = "run.log 的 pytest 汇总行（**未拿到逐条用例名**）"
        ui_total = sum(v for k, v in ui_counts.items() if k in RATING_KEYS)
    else:
        ui_counts, ui_source, ui_total = {}, "无", 0

    prefill_counts = _prefill_meta_counts(prefill["meta"])
    prefill_failed = list(prefill["failures"])
    prefill_ok = None
    if prefill_counts:
        prefill_ok = not (prefill_counts.get("failed") or prefill_counts.get("broken"))
    elif prefill["meta"] is not None:
        prefill_ok = not prefill["meta"].get("failures")

    return {
        "allure_dir": allure_dir,
        "rows": rows,
        "ui_failed": ui_failed,
        "ui_counts": ui_counts,
        "ui_source": ui_source,
        "ui_total": ui_total,
        "prefill": prefill,
        "prefill_counts": prefill_counts,
        "prefill_failed": prefill_failed,
        "prefill_ok": prefill_ok,
        "pytest_sum": pytest_sum,
        "infra_abort": detect_infra_abort(getattr(args, "run_log", "")),
    }


def _prefill_fail_row(item: dict) -> tuple[str, str]:
    """把 failures.json 的一条记录转成 (用例名, 原因)。"""
    name = (item.get("name") or item.get("case_id")
            or item.get("nodeid") or "(未命名预制用例)")
    reason = item.get("message") or ""
    if not reason and item.get("longrepr"):
        reason = str(item["longrepr"]).strip().splitlines()[0] if str(item["longrepr"]).strip() else ""
    return _md_escape(str(name), 160), _md_escape(str(reason), 300)


# ── 汇总（Job Summary）──────────────────────────────────────────────────────

def build_report(args: argparse.Namespace) -> str:
    out: list[str] = []
    d = gather(args)

    rows, ui_failed = d["rows"], d["ui_failed"]
    ui_counts, ui_total = d["ui_counts"], d["ui_total"]
    prefill = d["prefill"]
    prefill_failed = d["prefill_failed"]
    pytest_sum = d["pytest_sum"]

    rate, executed = _pass_rate(ui_counts)
    counts_failed = ui_counts.get("failed", 0) + ui_counts.get("broken", 0)
    # 有逐条结果时以逐条为准（更权威）；拿不到逐条结果时退化用计数。
    fail_total = (len(ui_failed) if rows else counts_failed) + len(prefill_failed)
    report_url = (getattr(args, "report_url", "") or "").strip()

    # ── 0) 顶部 Allure 在线报告（最先看到，一键跳转详细结果）─────────────
    if report_url:
        out.append(f"📊 **Allure 详细测试报告**：[点击查看完整测试结果]({report_url})"
                   "（每个用例的步骤 / 截图 / 失败日志）")
        out.append("")

    # ── 1) 顶部结论：通过率 + 失败用例名（一眼可见）──────────────────────
    if ui_total or ui_counts:
        icon = "✅" if not fail_total else "❌"
        if rate is not None:
            out.append(f"# {icon} UI Automation：通过率 {rate:.1f}%"
                       f"（{ui_counts.get('passed', 0)}/{executed} 通过）")
            out.append("")
            out.append(f"{_bar(rate)} 共 {ui_total} 条 UI 用例 · {_counts_phrase(ui_counts)}")
        else:
            out.append(f"# {icon} UI Automation：{_counts_phrase(ui_counts)}")
            out.append("")
            out.append(f"共 {ui_total} 条 UI 用例")
    else:
        infra = d.get("infra_abort")
        if infra:
            out.append("# 🚧 UI Automation：未跑用例（预检中止）")
            out.append("")
            out.append(f"main.py 在跑 UI 用例**之前**就中止了：**{infra}**。")
            out.append("")
            out.append("这类中断是环境 / 前置条件问题（例如账号登录态失效、预制失败），"
                       "**不代表任何用例失败** —— 修好前置后重跑即可。详见下方日志尾部。")
        else:
            out.append("# ⚠️ UI Automation：未取到用例结果")
            out.append("")
            out.append("`allure-results/` 与运行日志里的 pytest 汇总行都不可用 —— "
                       "UI 阶段可能未执行，详情见下方日志尾部。")

    if ui_failed or prefill_failed:
        out.append("")
        out.append("**失败清单：** " + "、".join(
            [f"`{r['name']}`" for r in ui_failed]
            + [f"`预制/{n}`" for n, _ in (_prefill_fail_row(x) for x in prefill_failed)]
        ))

    out.append("")
    meta = [f"触发 `{args.event_name}`" if args.event_name else "",
            f"提交 `{args.sha[:7]}`" if args.sha else "",
            f"job `{args.outcome}`" if args.outcome else "",
            f"报告目录 `{args.report_dir}`" if args.report_dir else ""]
    meta = [m for m in meta if m]
    if meta:
        out.append(" · ".join(meta))
    out.append("")
    out.append(f"UI 数据来源：{d['ui_source']}")
    out.append("")

    # ── 2) 失败用例速览（最重要，紧跟结论）──────────────────────────────
    if ui_failed or prefill_failed or counts_failed:
        out.append(f"## ❌ 失败用例（{fail_total}）")
    elif rows or ui_counts:
        out.append("## ✅ 失败用例（0）")
    else:
        out.append("## ❓ 失败用例（未知）")
    out.append("")
    if ui_failed or prefill_failed:
        out.append("| 阶段 | 用例 | 状态 | 耗时 | 失败原因 |")
        out.append("| --- | --- | --- | --- | --- |")
        for r in ui_failed:
            out.append(f"| UI | **{r['name']}** | `{r['status']}` | {r['duration']} | "
                       f"{r['reason'] or '—'} |")
        for item in prefill_failed:
            name, reason = _prefill_fail_row(item)
            dur = item.get("duration_s")
            out.append(f"| 预制 | **{name}** | `failed` | "
                       f"{f'{dur}s' if dur else '—'} | {reason or '—'} |")
    elif counts_failed:
        out.append(f"未拿到逐条用例名（`allure-results` 缺失），只能从 `run.log` 的 "
                   f"pytest 汇总行得知计数：{_counts_phrase(ui_counts)}。")
    elif rows:
        out.append("全部 UI 用例通过。")
    elif ui_counts:
        out.append(f"计数：{_counts_phrase(ui_counts)}。")
    else:
        out.append("（本次没有 UI 结果可判定）")
    out.append("")

    # ── 3) 全量逐条结果 ─────────────────────────────────────────────────
    out.append("## 全量 UI 用例结果")
    out.append("")
    if rows:
        out.append("| 结果 | 用例 | 状态 | 耗时 | 失败原因 |")
        out.append("| --- | --- | --- | --- | --- |")
        for r in rows:
            icon = STATUS_ICON.get(r["status"], "❔")
            out.append(f"| {icon} | {r['name']} | `{r['status']}` | "
                       f"{r['duration']} | {r['reason'] or '—'} |")
    else:
        out.append("未找到 `allure-results`，无法列出逐条结果。")
    out.append("")

    # ── 4) API 预制 ─────────────────────────────────────────────────────
    out.append("## API 预制（UI Automation Data Pre-configuration）")
    out.append("")
    if prefill["meta"] is not None or prefill["md"]:
        verdict = {True: "✅ 通过", False: "❌ 有失败", None: "⚠️ 结果未知"}[d["prefill_ok"]]
        cnt = d["prefill_counts"]
        detail = f"（{_counts_phrase(cnt)}）" if cnt else ""
        out.append(f"报告目录：`{prefill['dir']}` · 结果：{verdict}{detail}")
        out.append("")
        if prefill["md"]:
            out.append(prefill["md"])
    elif prefill["dir"]:
        out.append(f"找到预制目录 `{prefill['dir']}`，但缺少 `summary.md` / `meta.json`。")
    else:
        out.append("未产出预制报告 —— 预制未执行，或 `main.py` 在预制阶段即中止"
                   "（此时 UI 用例不会被执行，见下方日志尾部）。")
    out.append("")
    db_lines = collect_db_lines(args.run_log)
    if db_lines:
        out.append("<details><summary>预制内的 DB 步骤日志（如 step 76 别名写入）</summary>")
        out.append("")
        out.append("```")
        out.extend(db_lines)
        out.append("```")
        out.append("</details>")
        out.append("")

    # ── 5) 产物与日志 ───────────────────────────────────────────────────
    out.append("## 产物与日志")
    out.append("")
    run_no = os.environ.get("GITHUB_RUN_NUMBER", "")
    suffix = f"-{run_no}" if run_no else ""
    out.append(f"- 完整运行日志：Artifacts `run-logs{suffix}`（`run.log` + `log/` + 预制 run 目录）")
    if report_url:
        out.append(f"- Allure 报告：[在线查看]({report_url}) · 下载备用：Artifacts `allure-report{suffix}`")
    else:
        out.append(f"- Allure 报告：Artifacts `allure-report{suffix}`（Pages 未开启时仅可下载）")
    out.append(f"- 失败录屏：Artifacts `videos{suffix}`（仅失败时上传）")
    if pytest_sum:
        out.append("")
        out.append(f"- pytest 汇总行：`{_md_escape(pytest_sum['line'], 200)}`")
    out.append("")
    tail = collect_log_tail(args.run_log, args.tail)
    if tail:
        out.append(f"<details><summary>run.log 末尾 {len(tail)} 行</summary>")
        out.append("")
        out.append("```")
        out.extend(tail)
        out.append("```")
        out.append("</details>")

    return "\n".join(out)


# ── 运行页注解（Annotations）────────────────────────────────────────────────

def build_annotations(args: argparse.Namespace) -> list[str]:
    """生成 workflow command 注解，让通过率与失败用例名出现在 run 页面顶部。

    通过率用一条汇总注解；失败用例各一条 error（上限 10 条，含汇总那条）。
    Allure 在线报告作为第一条 notice 注解，运行页顶部即可点击跳转。
    """
    d = gather(args)
    ui_counts, ui_failed = d["ui_counts"], d["ui_failed"]
    prefill_failed = d["prefill_failed"]
    failed_names = [r["name"] for r in ui_failed] + [
        f"预制/{n}" for n, _ in (_prefill_fail_row(x) for x in prefill_failed)
    ]

    out: list[str] = []
    report_url = (getattr(args, "report_url", "") or "").strip()
    if report_url:
        out.append(f"::notice title=📊 Allure 详细测试报告::点击查看完整测试结果：{report_url}")

    if not ui_counts and not failed_names:
        infra = d.get("infra_abort")
        if infra:
            out.append(f"::error title=🚧 未跑用例（{_cmd_escape(infra, 60)}）::"
                       f"main.py 在跑 UI 用例前中止 —— 环境/前置问题，非用例失败。"
                       f"详见 Job Summary。")
        else:
            out.append("::warning title=⚠️ UI Automation 未取到结果::"
                       "allure-results 与运行日志的 pytest 汇总行都不可用，"
                       "UI 阶段可能未执行。详见 Job Summary。")
        return out

    rate, executed = _pass_rate(ui_counts)
    rate_txt = f"{rate:.1f}%" if rate is not None else "N/A"
    summary_line = (f"{ui_counts.get('passed', 0)}/{executed} 通过 · "
                    f"失败 {ui_counts.get('failed', 0)} · "
                    f"异常 {ui_counts.get('broken', 0)} · "
                    f"跳过 {ui_counts.get('skipped', 0)}")

    if failed_names:
        out.append(f"::error title=❌ UI Automation 通过率 {rate_txt}"
                   f"（{len(failed_names)} 条失败）::{_cmd_escape(summary_line)}")
        for name in failed_names[:ANNOTATION_MAX - 1]:
            out.append(f"::error title=失败用例：{_cmd_escape(name, 120)}::"
                       f"详情见 Job Summary 的「失败用例」表")
        hidden = len(failed_names) - (ANNOTATION_MAX - 1)
        if hidden > 0:
            out.append(f"::warning title=另有 {hidden} 条失败用例未在注解中展开::"
                       f"完整清单见 Job Summary")
    elif ui_counts.get("failed") or ui_counts.get("broken"):
        out.append(f"::error title=❌ UI Automation 通过率 {rate_txt}"
                   f"（{ui_counts.get('failed', 0)} 条失败）::{_cmd_escape(summary_line)}")
        out.append("::warning title=未拿到逐条用例名::"
                   "allure-results 缺失，失败用例名见 Job Summary 的 run.log 末尾。")
    else:
        out.append(f"::notice title=✅ UI Automation 通过率 {rate_txt}::"
                   f"{_cmd_escape(summary_line)}")
    return out


def build_outputs(args: argparse.Namespace) -> list[str]:
    """生成 ``$GITHUB_OUTPUT`` 内容（供后续步骤引用通过率/失败用例名）。"""
    d = gather(args)
    ui_counts = d["ui_counts"]
    names = ([r["name"] for r in d["ui_failed"]]
             + [f"预制/{n}" for n, _ in (_prefill_fail_row(x) for x in d["prefill_failed"])])
    rate, executed = _pass_rate(ui_counts)
    result_dir = os.path.basename((d["allure_dir"] or "").rstrip("/"))
    pytest_sum = d["pytest_sum"]
    return [
        f"pass_rate={'' if rate is None else f'{rate:.1f}'}",
        f"executed={executed}",
        f"passed={ui_counts.get('passed', 0)}",
        f"failed={ui_counts.get('failed', 0)}",
        f"broken={ui_counts.get('broken', 0)}",
        f"skipped={ui_counts.get('skipped', 0)}",
        f"failed_count={len(names)}",
        f"failed_names={','.join(names)[:900]}",
        f"prefill_failed={len(d['prefill_failed'])}",
        f"pytest_summary={'' if not pytest_sum else pytest_sum['line'][:200]}",
        f"ui_result_dir={result_dir}",
    ]


# ── 入口 ────────────────────────────────────────────────────────────────────

def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prefill-root",
                        default=os.path.join("test_case", "API auto script", "results", "runs"),
                        help="预制报告根目录（results/runs）")
    parser.add_argument("--allure-root", default="allure-results",
                        help="Allure 原始结果根目录")
    parser.add_argument("--run-log", default="run.log", help="main.py 的运行日志")
    parser.add_argument("--tail", type=int, default=60, help="run.log 末尾展示行数")
    parser.add_argument("--event-name", default="", help="触发方式（写入元信息行）")
    parser.add_argument("--sha", default="", help="提交号（写入元信息行）")
    parser.add_argument("--outcome", default="", help="main.py 步骤结果（写入元信息行）")
    parser.add_argument("--report-dir", default="", help="Allure 报告目录（写入元信息行）")
    parser.add_argument("--report-url", default="",
                        help="Allure 报告在线链接（GitHub Pages），写进 Summary/Annotations 顶部")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the CI job summary (markdown).")
    _add_common_args(parser)
    parser.add_argument("--github-annotations", action="store_true",
                        help="只输出 workflow command 注解（写 run 页面 Annotations 区块）")
    parser.add_argument("--outputs", default="",
                        help="把通过率/失败清单追加写入该文件（通常传 $GITHUB_OUTPUT）")
    parser.add_argument("-o", "--output", default="",
                        help="Job Summary 输出文件（默认 stdout；'-' 也是 stdout）")
    args = parser.parse_args(argv)

    # main.py 真正的日志写在 log/<日期>.log（run.log 里只有最后一行报告路径），
    # 所以 --run-log 允许传目录，这里解析成「最新那个日志文件」。
    args.run_log = _resolve_run_log(args.run_log)

    # 注解模式与其他输出互斥，避免 workflow command 混进 Job Summary。
    if args.github_annotations:
        for line in build_annotations(args):
            sys.stdout.write(line + "\n")
    else:
        report = build_report(args)
        if args.output and args.output != "-":
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(report + "\n")
        else:
            sys.stdout.write(report + "\n")

    if args.outputs:
        with open(args.outputs, "a", encoding="utf-8") as fh:
            fh.write("\n".join(build_outputs(args)) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
