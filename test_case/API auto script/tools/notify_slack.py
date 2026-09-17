#!/usr/bin/env python3
"""
把一次测试运行的结果推送到 Slack。

数据来源：results/runs/<run_id>/ 下的 summary.md / meta.json / failures.json
（由 conftest.py 的 run_archive 自动生成，无需额外解析 pytest 输出）。

凭据来源（按优先级）：
  1) --webhook 参数
  2) 环境变量 SLACK_WEBHOOK_URL
  3) config/slack.json  ->  {"webhook_url": "https://hooks.slack.com/services/...",
                             "channel": "qae-team"}

用法：
  python tools/notify_slack.py --dry-run                 # 只看会发什么，不发
  python tools/notify_slack.py                           # 发最新一次运行
  python tools/notify_slack.py --run-id 20260916_090012_linda
  python tools/notify_slack.py --write-only              # 同时把消息落盘到 results/slack/
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "results" / "runs"
CONFIG_FILE = ROOT / "config" / "slack.json"
OUT_DIR = ROOT / "results" / "slack"

MAX_FAILURES = 12          # Slack 单条消息里最多列多少条失败
MAX_MSG_CHARS = 2900       # Slack text 字段上限 3000，留点余量


def _load_webhook(args) -> str:
    if args.webhook:
        return args.webhook
    env = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if env:
        return env
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return (cfg.get("webhook_url") or "").strip()
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] 读取 {CONFIG_FILE} 失败: {e}", file=sys.stderr)
    return ""


def _latest_run_dir() -> Path | None:
    if not RUNS_DIR.exists():
        return None
    cands = [d for d in RUNS_DIR.iterdir() if d.is_dir() and (d / "meta.json").exists()]
    if not cands:
        return None
    return max(cands, key=lambda d: d.stat().st_mtime)


def _resolve_run(run_id: str | None) -> Path | None:
    if not run_id:
        return _latest_run_dir()
    p = RUNS_DIR / run_id
    if p.is_dir():
        return p
    # 允许只给前缀 / label，例如 "linda"
    matches = sorted([d for d in RUNS_DIR.glob(f"*{run_id}*") if d.is_dir()],
                     key=lambda d: d.stat().st_mtime)
    return matches[-1] if matches else None


def _human_duration(sec: float) -> str:
    if sec < 60:
        return f"{sec:.1f}s"
    m, s = divmod(int(sec), 60)
    if m < 60:
        return f"{m}m{s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m"


def _short_name(name: str, limit: int = 90) -> str:
    name = " ".join((name or "").split())
    return name if len(name) <= limit else name[: limit - 1] + "…"


def _first_error_line(msg: str, limit: int = 110) -> str:
    msg = " ".join((msg or "").split())
    # 只取最后一段（通常是真正的断言信息），去掉前缀堆栈
    if ": " in msg:
        msg = msg.rsplit(": ", 1)[-1]
    return _short_name(msg, limit)


def build_message(run_dir: Path, channel: str | None, report_url: str | None) -> dict:
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    failures_file = run_dir / "failures.json"
    failures = json.loads(failures_file.read_text(encoding="utf-8")) if failures_file.exists() else []

    c = meta.get("counts", {})
    passed = c.get("passed", 0) + c.get("xpassed", 0)
    failed = c.get("failed", 0)
    error = c.get("error", 0)
    skipped = c.get("skipped", 0)
    total = meta.get("total") or (passed + failed + error + skipped)
    effective = passed + failed + error
    rate = (passed / effective * 100) if effective else 0.0

    ok = (failed + error) == 0
    head = "✅ PASS" if ok else "❌ FAIL"

    run_id = meta.get("run_id") or run_dir.name
    label = meta.get("label") or ""
    title = f"{head} · Linda API Suite" + (f"（{label}）" if label else "")

    lines = [
        f"*{title}*",
        f"Run `{run_id}` · 环境 *{meta.get('env','?')}* · 耗时 *{_human_duration(float(meta.get('duration_s') or 0))}*",
        f"*通过 {passed} / 失败 {failed} / 错误 {error} / 跳过 {skipped}* · 共 {total} 条 · 通过率 *{rate:.1f}%*",
    ]
    if meta.get("started_at"):
        lines.append(f"开始时间：{meta['started_at']}")

    if failures:
        lines.append("")
        lines.append(f"*失败明细（前 {min(len(failures), MAX_FAILURES)} 条，共 {len(failures)} 条）*")
        for i, f in enumerate(failures[:MAX_FAILURES], 1):
            kind = "ERR " if f.get("kind") == "error" else "FAIL"
            cid = f.get("case_id")
            cid_s = f"T{cid} " if cid else ""
            lines.append(f"{i}. `{kind}` {cid_s}{_short_name(f.get('name',''))}")
            detail = _first_error_line(f.get("message") or "")
            if detail:
                lines.append(f"    ↳ {detail}")
        if len(failures) > MAX_FAILURES:
            lines.append(f"… 其余 {len(failures) - MAX_FAILURES} 条见报告")

    if report_url:
        lines.append("")
        lines.append(f"<{report_url}|📄 查看完整报告>")

    text = "\n".join(lines)
    if len(text) > MAX_MSG_CHARS:
        text = text[: MAX_MSG_CHARS - 20] + "\n…（已截断）"

    payload: dict = {"text": text}
    if channel:
        payload["channel"] = channel
    return payload


def post(url: str, payload: dict, timeout: int = 20) -> tuple[bool, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.status == 200 and body.strip() == "ok", f"HTTP {resp.status} {body.strip()}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code} {e.read().decode('utf-8', 'replace')[:200]}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def main() -> int:
    ap = argparse.ArgumentParser(description="把测试结果推送到 Slack")
    ap.add_argument("--run-id", help="results/runs 下的运行 id（前缀即可），默认取最新一次")
    ap.add_argument("--channel", default=None, help="频道名覆盖，如 qae-team（多数 webhook 会忽略）")
    ap.add_argument("--webhook", default=None, help="Slack Incoming Webhook URL（覆盖配置文件）")
    ap.add_argument("--report-url", default=None, help="报告链接，会作为按钮附在消息里")
    ap.add_argument("--dry-run", action="store_true", help="只打印 payload，不发送")
    ap.add_argument("--write-only", action="store_true", help="只落盘消息文本，不发送")
    args = ap.parse_args()

    run_dir = _resolve_run(args.run_id)
    if not run_dir:
        print(f"[ERROR] 在 {RUNS_DIR} 下找不到运行结果目录", file=sys.stderr)
        return 2

    channel = args.channel
    if channel is None and CONFIG_FILE.exists():
        try:
            channel = (json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get("channel") or "").strip() or None
        except Exception:  # noqa: BLE001
            pass

    payload = build_message(run_dir, channel, args.report_url)
    text = payload["text"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = OUT_DIR / f"{stamp}_{run_dir.name}.txt"
    out_file.write_text(text + "\n", encoding="utf-8")

    print(f"Run     : {run_dir.name}")
    print(f"Message : {out_file}")
    print("-" * 60)
    print(text)
    print("-" * 60)

    if args.dry_run or args.write_only:
        print("[SKIP] 未发送（--dry-run/--write-only）")
        return 0

    url = _load_webhook(args)
    if not url:
        print(
            "[ERROR] 没有可用的 Slack 凭据。请任选其一：\n"
            "  1) 把 Incoming Webhook URL 写进 config/slack.json "
            '{"webhook_url": "https://hooks.slack.com/services/...", "channel": "qae-team"}\n'
            "  2) 设置环境变量 SLACK_WEBHOOK_URL\n"
            "  3) 运行本脚本时加 --webhook <url>",
            file=sys.stderr,
        )
        return 3

    ok, info = post(url, payload)
    print(f"[{'OK' if ok else 'FAIL'}] Slack 推送：{info}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
