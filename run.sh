#!/bin/bash
# macOS 启动脚本 — UI Automation
# 用法: bash run.sh 或 chmod +x run.sh && ./run.sh

cd "$(dirname "$0")"

# 检查虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

python3 main.py