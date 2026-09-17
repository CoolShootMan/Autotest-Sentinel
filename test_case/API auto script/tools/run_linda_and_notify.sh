#!/usr/bin/env bash
# 跑 Linda API 回归套件，并把结果推到 Slack #qae-team。
# 定时任务（每天 09:00）直接调用本脚本即可。
#
#   bash tools/run_linda_and_notify.sh              # 正常跑
#   bash tools/run_linda_and_notify.sh --dry-run    # 只跑 suite 的挑选，不发 Slack
#
# Slack 凭据：config/slack.json 里的 webhook_url（或环境变量 SLACK_WEBHOOK_URL）。
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

PY=/Users/a123456/.workbuddy/binaries/python/envs/default/bin/python
[ -x "$PY" ] || PY=python3

LOG_DIR="$ROOT/results/automation_logs"
mkdir -p "$LOG_DIR"

DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

RUN_LOG="$LOG_DIR/run_$(date +%Y%m%d_%H%M%S).log"
echo "[$(date '+%F %T')] ===== 开始跑 suites/linda.yaml =====" | tee -a "$RUN_LOG"

if [ "$DRY" = "1" ]; then
  "$PY" run_suite.py suites/linda.yaml --dry-run 2>&1 | tee -a "$RUN_LOG"
  exit 0
fi

"$PY" run_suite.py suites/linda.yaml 2>&1 | tee -a "$RUN_LOG"
PYTEST_EXIT=${PIPESTATUS[0]}
echo "[$(date '+%F %T')] pytest 退出码 = $PYTEST_EXIT" | tee -a "$RUN_LOG"

# 报告已由 conftest 落到 results/runs/<ts>_linda/
"$PY" tools/notify_slack.py --channel qae-team --run-id linda 2>&1 | tee -a "$RUN_LOG"
NOTIFY_EXIT=${PIPESTATUS[0]:-0}

# 注意：变量紧邻中文/全角字符时必须写成 ${VAR}，
# 否则 bash 会把全角字符的首字节并进变量名（NOTIFY_EXIT<乱码>: unbound variable）。
echo "[$(date '+%F %T')] ===== 结束（pytest=${PYTEST_EXIT:-0}, slack=${NOTIFY_EXIT:-0}）=====" | tee -a "$RUN_LOG"
exit 0
