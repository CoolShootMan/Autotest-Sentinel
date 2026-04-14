#!/bin/bash
# 自动加载 cookie 启动 Playwright Codegen，支持交互式输入角色、环境和 URL

# 捕获 Ctrl+C (SIGINT) 信号
trap 'echo -e "\n👋 收到取消指令 (Ctrl+C)，已退出启动程序。"; exit 0' SIGINT

echo "========================================="
echo "🚀 欢迎使用 Playwright Codegen 快捷启动工具"
echo "========================================="

# 1. 交互式选择角色
read -p "👤 请选择角色 (1: partner, 2: guest, 3: co-seller, q: 退出) [默认: 1]: " role_choice

# 退出逻辑
if [ "$role_choice" = "q" ] || [ "$role_choice" = "Q" ] || [ "$role_choice" = "quit" ]; then
    echo "👋 已退出启动程序。"
    exit 0
fi

case "$role_choice" in
    2) ROLE="guest" ;;
    3) ROLE="co-seller" ;;
    *) ROLE="partner" ;; # 默认 partner
esac

# 2. 交互式选择环境（如果是 guest 则跳过）
ENV="release" # 默认值
if [ "$ROLE" != "guest" ]; then
    read -p "🌍 请选择环境 (1: staging, 2: release, 3: prod, q: 退出) [默认: 2]: " env_choice
    
    # 退出逻辑
    if [ "$env_choice" = "q" ] || [ "$env_choice" = "Q" ] || [ "$env_choice" = "quit" ]; then
        echo "👋 已退出启动程序。"
        exit 0
    fi
    
    case "$env_choice" in
        1) ENV="staging" ;;
        3) ENV="prod" ;;
        *) ENV="release" ;; # 默认 release
    esac
fi

# 3. 交互式提示输入 URL
read -p "🔗 请输入要录制的网址 (直接回车可跳过, q: 退出): " URL

# 退出逻辑
if [ "$URL" = "q" ] || [ "$URL" = "Q" ] || [ "$URL" = "quit" ]; then
    echo "👋 已退出启动程序。"
    exit 0
fi

# 恢复 Ctrl+C 的默认行为，防止启动 Playwright 后 Ctrl+C 异常
trap - SIGINT

# 构建基础命令
CMD="playwright codegen"

if [ -n "$URL" ]; then
    CMD="$CMD \"$URL\""
fi

# 拼接传入的其它参数
if [ $# -gt 0 ]; then
    CMD="$CMD $@"
fi

# 处理 Cookie 逻辑
if [ "$ROLE" != "guest" ]; then
    if [ "$ROLE" = "partner" ]; then
        COOKIE_FILE="./test_case/UI/Test_Katana/cookie_${ENV}.json"
    else
        # 对于 co-seller 角色
        COOKIE_FILE="./test_case/UI/Test_Katana/cookie_coseller_${ENV}.json"
    fi
    
    if [ ! -f "$COOKIE_FILE" ]; then
        echo "⚠️ 警告: Cookie 文件 $COOKIE_FILE 不存在，可能导致无法正常加载登录状态。"
    fi
    
    CMD="$CMD --load-storage=$COOKIE_FILE"
    echo -e "\n🚀 正在启动 Playwright Codegen (角色: $ROLE, 环境: $ENV) 并加载 Cookie..."
else
    echo -e "\n🚀 正在启动 Playwright Codegen (角色: guest)，不加载 Cookie..."
fi

echo "💻 执行命令: $CMD"

# 执行命令
eval "$CMD"
