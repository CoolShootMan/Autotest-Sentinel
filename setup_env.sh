#!/bin/bash
# 跨平台虚拟环境设置脚本
# 支持 Windows (Git Bash), macOS 和 Linux

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取操作系统类型
OS_TYPE="$(uname -s)"
VENV_DIR="venv"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  跨平台虚拟环境设置脚本${NC}"
echo -e "${GREEN}======================================${NC}"
echo -e "检测到操作系统: ${OS_TYPE}"

# 检查 Python 命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}错误: 未找到 Python。请先安装 Python 3.9+${NC}"
    exit 1
fi

echo -e "使用 Python: ${PYTHON_CMD}"
${PYTHON_CMD} --version

# 删除旧的虚拟环境（如果存在）
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}检测到已存在的虚拟环境目录${NC}"
    read -p "是否删除并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}正在删除旧的虚拟环境...${NC}"
        rm -rf "$VENV_DIR"
    else
        echo -e "${YELLOW}保留现有虚拟环境${NC}"
        if [ -f "$VENV_DIR/bin/activate" ] || [ -f "$VENV_DIR/Scripts/activate" ]; then
            echo -e "${GREEN}虚拟环境已存在，跳过创建${NC}"
        else
            echo -e "${RED}现有虚拟环境不完整，请删除后重试${NC}"
            exit 1
        fi
    fi
fi

# 创建新的虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${GREEN}创建虚拟环境...${NC}"
    ${PYTHON_CMD} -m venv "$VENV_DIR"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
    else
        echo -e "${RED}✗ 虚拟环境创建失败${NC}"
        exit 1
    fi
fi

# 激活虚拟环境
echo -e "${GREEN}激活虚拟环境...${NC}"
if [ -f "$VENV_DIR/bin/activate" ]; then
    # Linux/macOS
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    # Windows (Git Bash)
    source "$VENV_DIR/Scripts/activate"
else
    echo -e "${RED}错误: 无法找到激活脚本${NC}"
    exit 1
fi

# 升级 pip
echo -e "${GREEN}升级 pip...${NC}"
python -m pip install --upgrade pip

# 安装依赖
echo -e "${GREEN}安装项目依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "venv_requirements.txt" ]; then
    pip install -r venv_requirements.txt
else
    echo -e "${YELLOW}警告: 未找到 requirements.txt 或 venv_requirements.txt${NC}"
fi

# 安装 Playwright 浏览器
echo -e "${GREEN}安装 Playwright 浏览器...${NC}"
playwright install

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  ✓ 设置完成！${NC}"
echo -e "${GREEN}======================================${NC}"
echo -e ""
echo -e "使用说明:"
echo -e "  1. 激活虚拟环境:"
echo -e "     - Linux/macOS:  ${YELLOW}source venv/bin/activate${NC}"
echo -e "     - Windows:      ${YELLOW}venv\\Scripts\\activate${NC}"
echo -e ""
echo -e "  2. 运行测试:"
echo -e "     ${YELLOW}pytest test_case/UI/Test_Katana/test_ui.py -k testT5106${NC}"
echo -e ""
echo -e "  3. 退出虚拟环境:"
echo -e "     ${YELLOW}deactivate${NC}"
echo -e ""
