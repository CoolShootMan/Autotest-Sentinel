#!/usr/bin/env python3
"""多套件 CI 报告：把各套件的结果汇总成 Job Summary，并推送到 Slack。

数据来源
--------
``results/runs/<run_id>/`` 下由 ``conftest`` 的 run_archive 自动落盘的
``meta.json``（机器可读计数）/ ``summary.md``（人读报告）/ ``failures.json``。
本脚本只做「读取 + 合并 + 展示」，不解析 pytest 的 stdout，也不重新跑用例，
因此 CI 里可以随便重复执行、失败也不影响测试结论。

与 ``tools/notify_slack.py`` 的分工
-----------------------------------
* ``notify_slack.py`` —— 单套件、本地调试用（``--run-id linda``）。
* ``ci_report.py``     —— 多套件合并视图，CI 的 Job Summary 与 Slack 都用它。

用法
----
  python tools/ci_report.py --step-summary          # 写 $GITHUB_STEP_SUMMARY + results/summary.md
  python tools/ci_report.py --slack --dry-run       # 打印将发送的 Slack 文本（不发送）
  python tools/ci_report.py --slack                 # 推送到 Slack（需 SLACK_WEBHOOK_URL）
  python tools/ci_report.py --print                 # 打印合并后的 Markdown
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                   # test_case/API auto script
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.notify_slack import (                      # noqa: E402
    _first_error_line,
    _human_duration,
    _short_name,
    post,
)

RUNS_DIR = ROOT / "results" / "runs"
COMBINED_MD = ROOT / "results" / "summary.md"

# 展示顺序（先出现的套件排在前面；未列出的按名字排在后面）
SUITE_ORDER = ["linda", "lury"]
SUITE_TITLE = {"linda": "linda 套", "lury": "lury 套"}

MAX_SLACK_FAILURES = 12          # Slack 里最多列多少条失败
MAX_SLACK_CHARS = 2900           # Slack text 上限 3000，留余量


# --- 数据读取 -----------------------------------------------------------
def _counts_of(meta: dict) -> dict:
    """从 meta.json 抽计数，并补出 executed / rate（口径与 run_archive 的
    summary.md 完全一致：有效用例 = passed + failed + error）。"""
    c = meta.get("counts") or {}

    def n(k: str) -> int:
        try:
            return int(c.get(k) or 0)
        except (TypeError, ValueError):
            return 0

    passed, failed, error = n("passed"), n("failed"), n("error")
    skipped, xfailed, xpassed = n("skipped"), n("xfailed"), n("xpassed")
    total = meta.get("total") or (passed + failed + error + skipped + xfailed + xpassed)
    executed = passed + failed + error
    return {
        "passed": passed, "failed": failed, "error": error,
        "skipped": skipped, "xfailed": xfailed, "xpassed": xpassed,
        "total": total, "executed": executed,
        "rate": (passed / executed * 100) if executed else None,
    }


def _suite_of(run_dir: Path, meta: dict) -> str:
    label = str(meta.get("label") or "").strip().lower()
    if label:
        return label
    # run_id 形如 20260921_043325_linda，取最后一段
    name = str(meta.get("run_id") or run_dir.name)
    return name.rsplit("_", 1)[-1].lower()


def discover(runs_dir: Path = RUNS_DIR) -> "dict[str, dict]":
    """每个套件取最新一次运行，返回有序 dict（按 SUITE_ORDER 优先）。"""
    found: dict[str, dict] = {}
    if not runs_dir.exists():
        return found
    for d in sorted(runs_dir.iterdir(), key=lambda p: (p.stat().st_mtime, p.name)):
        meta_file = d / "meta.json"
        if not d.is_dir() or not meta_file.exists():
            continue
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:                                  # 坏文件跳过，不阻断 CI
            continue
        failures_file = d / "failures.json"
        try:
            failures = (json.loads(failures_file.read_text(encoding="utf-8"))
                        if failures_file.exists() else [])
        except Exception:
            failures = []
        found[_suite_of(d, meta)] = {"dir": d, "meta": meta, "failures": failures}

    ordered: dict[str, dict] = {}
    for s in SUITE_ORDER:
        if s in found:
            ordered[s] = found.pop(s)
    for s in sorted(found):
        ordered[s] = found[s]
    return ordered


def _title(suite: str) -> str:
    return SUITE_TITLE.get(suite, f"{suite} 套")


def _totals(suites: dict) -> dict:
    agg = {"passed": 0, "failed": 0, "error": 0, "skipped": 0,
           "xfailed": 0, "xpassed": 0, "total": 0, "duration": 0.0}
    for info in suites.values():
        s = _counts_of(info["meta"])
        for k in ("passed", "failed", "error", "skipped", "xfailed", "xpassed", "total"):
            agg[k] += s[k]
        agg["duration"] += float(info["meta"].get("duration_s") or 0)
    agg["executed"] = agg["passed"] + agg["failed"] + agg["error"]
    agg["rate"] = (agg["passed"] / agg["executed"] * 100) if agg["executed"] else None
    return agg


def _rate_str(rate: float | None) -> str:
    return f"{rate:.1f}%" if rate is not None else "-"


def _verdict(failed: int, error: int) -> str:
    return "✅ 全部通过" if (failed + error) == 0 else f"❌ {failed + error} 条失败"


# --- Job Summary --------------------------------------------------------
def build_step_summary(suites: dict, env: str, run_url: str = "",
                       run_number: str = "") -> str:
    agg = _totals(suites)
    L: list[str] = [f"# API Automation 每日执行结果（{env}）", ""]

    if not suites:
        L += ["⚠️ 没有找到任何运行结果（`results/runs/*/meta.json` 不存在），"
              "可能两套 suite 都在启动阶段就失败了。", ""]
        return "\n".join(L)

    # 概览表
    L += ["| 套件 | 通过 | 失败 | 错误 | 跳过 | 共 | 通过率 | 结果 |",
          "|---|---:|---:|---:|---:|---:|---:|:--:|"]
    for suite, info in suites.items():
        s = _counts_of(info["meta"])
        ok = (s["failed"] + s["error"]) == 0
        L.append(f"| {_title(suite)} | {s['passed']} | {s['failed']} | {s['error']} | "
                 f"{s['skipped']} | {s['total']} | {_rate_str(s['rate'])} | "
                 f"{'✅' if ok else '❌'} |")
    ok_all = (agg["failed"] + agg["error"]) == 0
    L.append(f"| **合计** | **{agg['passed']}** | **{agg['failed']}** | **{agg['error']}** | "
             f"**{agg['skipped']}** | **{agg['total']}** | "
             f"**{_rate_str(agg['rate'])}** | {'✅' if ok_all else '❌'} |")
    L += ["", f"**{_verdict(agg['failed'], agg['error'])}** · 共 {agg['total']} 条用例 · "
              f"总耗时 {_human_duration(agg['duration'])}"]

    if run_url:
        L += ["", f"运行详情：{run_url}"]
    if run_number:
        L += ["", f"完整日志与原始产物：本次 run 的 Artifacts `api-run-logs-{run_number}`"
                  "（`results/` 内含各套件 summary.md / junit.xml / http.log）。"]

    # 失败用例清单（一眼可见，不用展开）
    if agg["failed"] + agg["error"] > 0:
        L += ["", f"## 失败用例清单（{agg['failed'] + agg['error']}）", ""]
        for suite, info in suites.items():
            failures = info["failures"]
            if not failures:
                continue
            s = _counts_of(info["meta"])
            L += [f"### {_title(suite)}（{len(failures)} 条）", ""]
            for i, f in enumerate(failures, 1):
                kind = "ERR" if f.get("kind") == "error" else "FAIL"
                cid = f.get("t_id")
                cid_s = f"`[{cid}]` " if cid else ""
                detail = _first_error_line(f.get("message") or "")
                line = f"{i}. `{kind}` {cid_s}{_short_name(f.get('name') or '', 110)}"
                if detail:
                    line += f" — {detail}"
                L.append(line)
            L.append("")

    # 各套件完整报告（summary.md 原文，折叠展示）
    L += ["", "## 各套件完整报告（点击展开）", ""]
    for suite, info in suites.items():
        s = _counts_of(info["meta"])
        summary = info["dir"] / "summary.md"
        body = ""
        if summary.exists():
            try:
                body = summary.read_text(encoding="utf-8").strip()
            except Exception as e:                          # noqa: BLE001
                body = f"(读取 summary.md 失败: {e})"
        else:
            body = "(无 summary.md)"
        L += [f"<details>",
              f"<summary><b>{_title(suite)} 完整报告</b>"
              f"（✅ {s['passed']} / ❌ {s['failed']} · 通过率 {_rate_str(s['rate'])}）</summary>",
              "", body, "", "</details>", ""]

    L += ["---", "",
          "机器可读产物：每套件 `results/runs/<run_id>/` 下的 "
          "`meta.json` / `failures.json` / `junit.xml` / `http.log`。", ""]
    return "\n".join(L)


# --- Slack --------------------------------------------------------------
def build_slack_text(suites: dict, env: str, run_url: str = "",
                     run_number: str = "") -> str:
    agg = _totals(suites)
    ok_all = (agg["failed"] + agg["error"]) == 0
    head = ":white_check_mark: *PASS*" if ok_all else ":warning: *FAIL*"

    lines = [f"{head} · *API Automation 每日报告（{env}）*"]
    if not suites:
        lines.append("> ⚠️ 没有找到任何运行结果（两套 suite 可能都在启动阶段失败）")
    else:
        for suite, info in suites.items():
            s = _counts_of(info["meta"])
            mark = ":white_check_mark:" if (s["failed"] + s["error"]) == 0 else ":x:"
            lines.append(
                f"> {mark} *{_title(suite)}*：✅ {s['passed']} 通过 / ❌ {s['failed']} 失败 / "
                f"⚠️ {s['error']} 错误 / ⏭ {s['skipped']} 跳过 · "
                f"共 {s['total']} 条 · 通过率 *{_rate_str(s['rate'])}*"
            )
        lines.append(
            f"> *合计*：✅ *{agg['passed']} 通过* / ❌ *{agg['failed']} 失败* / "
            f"⚠️ {agg['error']} 错误 / ⏭ {agg['skipped']} 跳过 · "
            f"共 {agg['total']} 条 · 通过率 *{_rate_str(agg['rate'])}*"
        )

    # 失败明细
    all_failures: list[dict] = []
    for info in suites.values():
        all_failures += info["failures"]
    if all_failures:
        lines += ["", f"*失败明细（前 {min(len(all_failures), MAX_SLACK_FAILURES)} 条，"
                      f"共 {len(all_failures)} 条）*"]
        for i, f in enumerate(all_failures[:MAX_SLACK_FAILURES], 1):
            kind = "ERR " if f.get("kind") == "error" else "FAIL"
            cid = f.get("t_id")
            cid_s = f"{cid} " if cid else ""
            lines.append(f"{i}. `{kind}` {cid_s}{_short_name(f.get('name') or '')}")
            detail = _first_error_line(f.get("message") or "")
            if detail:
                lines.append(f"    ↳ {detail}")
        if len(all_failures) > MAX_SLACK_FAILURES:
            lines.append(f"… 其余 {len(all_failures) - MAX_SLACK_FAILURES} 条见运行页 Summary")

    if run_url:
        lines += ["", f"<{run_url}|🔗 运行详情与日志（含 Job Summary 完整报告）>"]
    if run_number:
        lines.append(f":package: Artifacts：`api-run-logs-{run_number}`")

    text = "\n".join(lines)
    if len(text) > MAX_SLACK_CHARS:
        text = text[: MAX_SLACK_CHARS - 24] + "\n…（已截断，详见运行页）"
    return text


# --- CLI ----------------------------------------------------------------
def _run_url_from_env() -> str:
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    rid = os.environ.get("GITHUB_RUN_ID", "")
    if repo and rid:
        return f"{server}/{repo}/actions/runs/{rid}"
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="多套件 CI 报告（Job Summary + Slack）")
    ap.add_argument("--step-summary", action="store_true",
                    help="把汇总 Markdown 追加到 $GITHUB_STEP_SUMMARY，并落盘 results/summary.md")
    ap.add_argument("--slack", action="store_true", help="推送汇总消息到 Slack")
    ap.add_argument("--print", dest="print_md", action="store_true", help="打印汇总 Markdown")
    ap.add_argument("--dry-run", action="store_true", help="只打印将发送的 Slack 文本，不发送")
    ap.add_argument("--runs-dir", default=str(RUNS_DIR), help="结果根目录（默认 results/runs）")
    ap.add_argument("--env", default=os.environ.get("API_ENV", "Release"), help="环境名（展示用）")
    ap.add_argument("--run-url", default=None, help="运行页链接（默认由 GITHUB_* 环境变量拼出）")
    ap.add_argument("--run-number", default=os.environ.get("GITHUB_RUN_NUMBER", ""),
                    help="run number（用于 Artifacts 名）")
    args = ap.parse_args()

    suites = discover(Path(args.runs_dir))
    run_url = args.run_url if args.run_url is not None else _run_url_from_env()

    names = ", ".join(f"{k}({info['dir'].name})" for k, info in suites.items()) or "无"
    print(f"[ci_report] 发现 {len(suites)} 个套件结果: {names}")

    if args.print_md or args.step_summary:
        md = build_step_summary(suites, args.env, run_url, args.run_number)
        if args.print_md:
            print("-" * 70)
            print(md)
            print("-" * 70)
        if args.step_summary:
            COMBINED_MD.parent.mkdir(parents=True, exist_ok=True)
            COMBINED_MD.write_text(md, encoding="utf-8")
            dest = os.environ.get("GITHUB_STEP_SUMMARY")
            if dest:
                with open(dest, "a", encoding="utf-8") as fh:
                    fh.write(md + "\n")
                print(f"[ci_report] 已写入 Job Summary: {dest}")
            else:
                print(f"[ci_report] 未设置 $GITHUB_STEP_SUMMARY，仅落盘 {COMBINED_MD}")

    if args.slack:
        text = build_slack_text(suites, args.env, run_url, args.run_number)
        if args.dry_run:
            print("-" * 70)
            print(text)
            print("-" * 70)
            print("[ci_report] --dry-run：未发送")
            return 0
        url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
        if not url:
            print("[ci_report] 没有 SLACK_WEBHOOK_URL，跳过发送", file=sys.stderr)
            return 0
        ok, info = post(url, {"text": text})
        print(f"[ci_report] Slack {'已发送' if ok else '发送失败'}：{info}")
        return 0 if ok else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
