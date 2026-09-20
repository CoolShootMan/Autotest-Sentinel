#!/usr/bin/env python3
"""生成 CI 的「完整测试结果」汇总（写入 GitHub Actions Job Summary）。

设计目标（对应需求）：
  1. 如实记录 —— 每个 UI 用例的真实状态（passed / failed / broken / skipped）
     与失败原因都逐条列出，失败用例排在最前，不隐藏、不美化。
  2. 不中断执行 —— 本脚本只做「读结果 + 汇总」，任何一步读不到（缺文件 /
     缺目录）都降级成一句说明，绝不抛异常影响 CI 后续步骤。
  3. 完整汇总 —— 预制结果（[1/4]）、UI 逐条结果（[2/4]）、失败清单（[3/4]）、
     产物位置（[4/4]）四段齐全，即使整轮跑红也能看懂"谁红了、为什么红"。

用法（CI 内）::

    python3 tools/ci_summary.py \
        --prefill-root "test_case/API auto script/results/runs" \
        --allure-root allure-results \
        --run-log run.log >> "$GITHUB_STEP_SUMMARY"
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

STATUS_ICON = {"passed": "✅", "failed": "❌", "broken": "💥", "skipped": "⏭"}
STATUS_ORDER = {"failed": 0, "broken": 1, "passed": 2, "skipped": 3}


def _md_escape(text: str, limit: int = 200) -> str:
    """转义会破坏 Markdown 表格/单行的字符，并按需截断。"""
    s = (text or "").replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()
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
        try:
            with open(fp, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:  # noqa: BLE001 - 单个结果文件坏掉不应影响整体汇总
            continue
        status = data.get("status") or "unknown"
        counts[status] = counts.get(status, 0) + 1
        start, stop = data.get("start"), data.get("stop")
        duration = f"{(stop - start) / 1000:.1f}s" if start and stop else ""
        rows.append({
            "name": _md_escape(data.get("name") or "(未命名用例)", 120),
            "status": status,
            "duration": duration,
            "reason": _first_line(data.get("statusDetails")),
        })
    rows.sort(key=lambda r: (STATUS_ORDER.get(r["status"], 9), r["name"]))
    return latest, rows, counts


def collect_prefill(prefill_root: str) -> tuple[str | None, str | None]:
    """取最新一次预制的目录与 summary.md 内容。"""
    cands = glob.glob(os.path.join(prefill_root, "*ui-automation-prefill*"))
    latest = _newest(cands)
    if not latest:
        return None, None
    summary = os.path.join(latest, "summary.md")
    if os.path.exists(summary):
        with open(summary, encoding="utf-8", errors="replace") as fh:
            return latest, fh.read().strip()
    return latest, None


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


def build_report(args: argparse.Namespace) -> str:
    out: list[str] = []

    prefill_dir, prefill_md = collect_prefill(args.prefill_root)
    allure_dir, rows, counts = collect_ui_results(args.allure_root)
    db_lines = collect_db_lines(args.run_log)

    failed = [r for r in rows if r["status"] in ("failed", "broken")]
    total = len(rows)

    # ── 总览 ────────────────────────────────────────────────────────────
    out.append("## 测试结果总览")
    out.append("")
    out.append("| 阶段 | 结果 |")
    out.append("| --- | --- |")
    out.append(f"| [1/4] API 预制 | {'✅ 有报告' if prefill_md else '⚠️ 未产出报告'} |")
    if total:
        mark = "✅" if not failed else f"❌ {len(failed)} 条失败"
        out.append(f"| [2/4] UI 用例 | {mark}（共 {total} 条："
                   f"passed {counts.get('passed', 0)} · failed {counts.get('failed', 0)} · "
                   f"broken {counts.get('broken', 0)} · skipped {counts.get('skipped', 0)}） |")
    else:
        out.append("| [2/4] UI 用例 | ⚠️ 未收集到结果（UI 阶段可能未执行） |")
    out.append("")

    # ── [1/4] 预制 ─────────────────────────────────────────────────────
    out.append("## [1/4] API 预制（UI Automation Data Pre-configuration）")
    out.append("")
    if prefill_md:
        out.append(f"报告目录：`{prefill_dir}`")
        out.append("")
        out.append(prefill_md)
    elif prefill_dir:
        out.append(f"找到预制目录 `{prefill_dir}`，但缺少 `summary.md`。")
    else:
        out.append("未产出预制报告 —— 预制未执行，或 `main.py` 在预制阶段即中止"
                   "（此时 UI 用例不会被执行，见下方日志尾部）。")
    out.append("")
    if db_lines:
        out.append("<details><summary>预制内的 DB 步骤日志（如 step 76 别名写入）</summary>")
        out.append("")
        out.append("```")
        out.extend(db_lines)
        out.append("```")
        out.append("</details>")
        out.append("")

    # ── [2/4] 逐条结果 ─────────────────────────────────────────────────
    out.append("## [2/4] UI 用例逐条结果（真实状态）")
    out.append("")
    if not rows:
        out.append("未找到 `allure-results`，无法列出逐条结果。")
    else:
        out.append(f"结果目录：`{allure_dir}`")
        out.append("")
        out.append("| 结果 | 用例 | 状态 | 耗时 | 失败原因 |")
        out.append("| --- | --- | --- | --- | --- |")
        for r in rows:
            icon = STATUS_ICON.get(r["status"], "❔")
            out.append(f"| {icon} | {r['name']} | `{r['status']}` | "
                       f"{r['duration']} | {r['reason'] or '—'} |")
    out.append("")

    # ── [3/4] 失败清单 ─────────────────────────────────────────────────
    out.append("## [3/4] 失败用例清单")
    out.append("")
    if failed:
        for r in failed:
            out.append(f"- {STATUS_ICON.get(r['status'], '❔')} **{r['name']}** "
                       f"— `{r['status']}`" + (f" · {r['reason']}" if r["reason"] else ""))
    else:
        out.append("无失败用例。" if rows else "（本次没有 UI 结果可判定）")
    out.append("")

    # ── [4/4] 产物 ─────────────────────────────────────────────────────
    out.append("## [4/4] 日志与报告")
    out.append("")
    run_no = os.environ.get("GITHUB_RUN_NUMBER", "")
    suffix = f"-{run_no}" if run_no else ""
    out.append(f"- 完整运行日志：Artifacts `run-logs{suffix}`（`run.log` + `log/`）")
    out.append(f"- Allure 报告：Artifacts `allure-report{suffix}`")
    out.append(f"- 失败录屏：Artifacts `videos{suffix}`（仅失败时上传）")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the CI job summary (markdown).")
    parser.add_argument("--prefill-root",
                        default=os.path.join("test_case", "API auto script", "results", "runs"),
                        help="预制报告根目录（results/runs）")
    parser.add_argument("--allure-root", default="allure-results",
                        help="Allure 原始结果根目录")
    parser.add_argument("--run-log", default="run.log", help="main.py 的运行日志")
    parser.add_argument("--tail", type=int, default=40, help="run.log 末尾展示行数")
    parser.add_argument("-o", "--output", default="-", help="输出文件（默认 stdout）")
    args = parser.parse_args(argv)

    report = build_report(args)
    if args.output == "-":
        sys.stdout.write(report + "\n")
    else:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
