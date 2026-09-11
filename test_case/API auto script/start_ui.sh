#!/bin/bash
# 启动 测试套可视化 UI（局域网可访问，且完全脱离 Apifox 运行时）
# 数据来自 case_index.scan_tests()（扫描 tests/），不再依赖 runable_scenarios.json
# 用法: bash start_ui.sh
cd "/Users/a123456/Desktop/UI Automation/test_case/API auto script"
PY=/Users/a123456/.workbuddy/binaries/python/envs/default/bin/python
LOG=/tmp/apifox_ui.log
PORT=8765
HOST=0.0.0.0

# 关闭已存在的实例
P=$(lsof -ti tcp:$PORT 2>/dev/null)
if [ -n "$P" ]; then kill $P 2>/dev/null; sleep 1; fi

# nohup + & + disown：macOS 下脱离终端，关闭终端后继续运行
nohup "$PY" server.py --host "$HOST" --port "$PORT" >> "$LOG" 2>&1 < /dev/null &
disown 2>/dev/null || true

sleep 2
echo "started -> http://0.0.0.0:$PORT  (LAN: http://$(ipconfig getifaddr en0 2>/dev/null):$PORT)"
echo "log: $LOG"
