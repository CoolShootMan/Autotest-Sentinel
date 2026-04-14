# Auto Test 框架 v4.0

> pytest + playwright + allure + Gemini AI 实现 UI 自动化测试 + AI 自愈

简体中文 | [English](./README.en.md)

---

## ✨ 核心特性

- **关键字驱动**: YAML 定义测试用例，无需编码即可编写 UI 自动化测试。
- **Action Registry 模式**: 模块化动作注册表，支持多人协作开发。
- **AI 自愈 (Self-Healing)**: 当传统定位器失效时，基于 Gemini Vision 的 AI 自动识别并修复元素定位。
- **RAG 知识库增强**: 使用 FAISS + SentenceTransformers 构建领域知识库，为 AI 提供业务上下文。
- **执行历史追踪**: 自动记录已成功执行的步骤，为 AI 提供当前测试流程状态。
- **多环境支持**: 通过 `--env` 参数无缝切换 staging/release 环境。
- **动态多断言**: 支持多种断言类型（文本可见性、元素存在性等）。
- **跨平台支持**: 完美兼容并支持 Windows、macOS、Linux 系统。

---

## 💻 系统要求

- **Python:** 3.9+ (推荐 3.10+)
- **操作系统:** Windows 10+, macOS 11+, 或主流 Linux 发行版
- **浏览器:** Chromium (由 Playwright 自动安装)
- **内存:** 建议 8GB+ RAM
- **磁盘空间:** 至少 2GB 可用空间

---

## 🚀 快速开始

### 1. 环境准备 (自动化配置)

本项目支持跨平台一键部署。脚本会自动检测操作系统、创建适合的虚拟环境并安装所有依赖（包含 Playwright 浏览器）。

**macOS/Linux:**
```bash
./setup_env.sh
```

**Windows:**
```bash
setup_env.bat
```
*(注：如果您想手动配置环境，请参考[环境管理](#环境管理)部分)*

### 2. API Key 配置

在项目**根目录**下创建 `.env` 文件，配置 Gemini API Keys（支持配置多个 Key 自动轮换以避免频率限制）：

```env
# 必填：Gemini API Key (推荐使用复数形式配置多个，逗号分隔)
GEMINI_API_KEYS=key1,key2,key3

# 或者配置单个 Key (兼容旧版本)
GEMINI_API_KEY=your_single_key_here
```

### 3. 一键运行测试

推荐使用 `run.py` 智能启动脚本进行测试执行：

```bash
# 交互式执行：终端弹出层级菜单，支持逐层进入目录、选择具体 YAML 或一键执行某个目录下的所有测试！
python run.py
```

### 4. 查看测试报告

测试完成后，系统会自动生成并打开 Allure 测试报告。

---

## 📖 详细使用指南

### 测试执行与常用命令

除了交互式的 `run.py`，您也可以通过命令行传递参数或直接使用 pytest 命令。

**使用 `run.py` 快捷指令：**
```bash
# 运行单个测试用例 (默认带上 --headed -v)
python run.py testT4718

# 运行多个测试用例 (默认使用 or 逻辑匹配)
python run.py testT4718 testT4718_guest

# 传递额外的 pytest 参数 (如无头模式、指定环境等)
python run.py testT4718 --headless --env release
```
> **💡 提示：** 当执行整个文件或目录下所有的测试时，`run.py` 会自动解析 YAML 提取出每一个单独的 `testTxxxx` 测试用例，并**逐一拆分执行**。如果某一个用例失败，不会中断其他用例的执行。

**使用原生 `pytest` 命令：**
```bash
# 测试特定用例
pytest test_case/UI/Test_Katana/test_ui.py -k testT3554 --yaml All_YAML/Module/Module.yaml --headed -v --env release

# 测试多个用例
pytest test_case/UI/Test_Katana/test_ui.py -k "testT3554 or testT4660" --yaml All_YAML/Module/Module.yaml --headed -v

# 生成 Allure 报告
pytest --alluredir=allure-results test_case/UI/Test_Katana/test_ui.py
allure serve allure-results
```

### 测试参数说明

| 参数              | 说明            | 示例                          |
| ----------------- | --------------- | ----------------------------- |
| `-k`              | 按名称过滤测试  | `-k testT3554`                |
| `-v` / `-vv`      | 详细/更详细输出 | `-vv`                         |
| `-s`              | 显示 print 输出 | `-s`                          |
| `--headed`        | 显示浏览器窗口  | `--headed`                    |
| `--headless`      | 无头模式        | `--headless`                  |
| `--storage-state` | 使用保存的会话  | `--storage-state cookie.json` |
| `--env`           | 指定运行环境    | `--env release` 或 `staging`  |
| `--yaml`          | 指定配置文件    | `--yaml config.yaml`          |

### 环境管理

若需要手动干预、重建环境或跨平台迁移：

```bash
# 1. 激活/退出虚拟环境
source venv/bin/activate    # macOS/Linux 激活
venv\Scripts\activate.bat   # Windows 激活
deactivate                  # 退出环境

# 2. 重建环境 (遇到跨平台切换或环境损坏时使用)
rm -rf venv && ./setup_env.sh          # macOS/Linux
rmdir /s venv && setup_env.bat         # Windows

# 3. 手动安装依赖与浏览器 (不使用 setup 脚本时)
python3 -m venv venv                   # 创建虚拟环境
pip install -r requirements.txt        # 安装依赖
playwright install                     # 安装浏览器
```

---

## 🧠 架构与底层机制

### 整体架构概览

```text
YAML 测试定义
    ↓
test_ui.py (步骤分发器 + 执行历史追踪)
    ↓
actions/ (Action Registry 动作注册表)
    ├── base.py → smart_click / smart_fill (含 AI Fallback)
    ├── module.py / product.py / form.py ...
    ↓
┌─ 传统 Playwright 定位 (role/text/locator)
│   成功 → 继续执行
│   失败 ↓
└─ AI 自愈引擎 (utils/ai_vision.py)
       ├── 截图 + SOM 标注
       ├── RAG 知识库检索 (utils/rag_knowledge.py)
       ├── 执行历史上下文注入
       └── Gemini Vision 分析 → 输出目标元素 ID
              ↓
         修复后继续执行
              ↓
         Allure 报告 + 截图/录屏
```

### V4.0 AI 自愈深度解析

1. **执行策略**: `smart_click` 优先尝试传统 Playwright 定位 (role/name/text)。
2. **降级机制**: 若 5s 内超时，触发 Legacy Fallback (15s 宽限期)。
3. **AI 介入**: 若仍失败，触发 **AI Self-Healing**：
   - 对当前页面截图并注入 **SOM (Set-of-Mark)** 标注。
   - 查询 **RAG 知识库** (`utils/Knowledge_Base.md`) 获取系统业务规则与导航模式。
   - 将截图、目标描述、执行历史及 RAG 知识一并发送至 Gemini Vision。
   - AI 返回诊断结果与目标元素 ID，框架根据指引完成操作。
4. **知识库演进**: 当 AI 出现误判时，测试人员可在 `Knowledge_Base.md` 中补充业务规则，AI 下次运行将自动检索并学习规避。

---

## 📂 目录结构

```shell
├─config
│  └─config.yaml          # 配置文件
├─page
│  └─home.py              # UI 层基础封装
├─recordings              # playwright codegen 录制脚本
├─test_case
│  └─UI
│    └─Test_Katana
│       ├─actions/         # Action Registry (动作注册表)
│       │  ├─__init__.py   # 注册表入口
│       │  ├─base.py       # 基础动作 (smart_click, smart_fill, AI Fallback)
│       │  └─...           # 各业务线动作模块
│       ├─utils/           # [NEW v4.0] AI 自愈工具集
│       │  ├─ai_vision.py  # Gemini Vision AI 服务 (SOM + 多 API Key 轮换)
│       │  ├─rag_knowledge.py  # RAG 知识库 (FAISS + SentenceTransformers)
│       │  └─Knowledge_Base.md # 领域知识库文档
│       ├─conftest.py      # Pytest fixtures (多环境 + 认证)
│       ├─test_ui.py       # 核心测试执行引擎 (含执行历史追踪)
│       └─*.yaml           # 测试用例定义
├─tools                    # 工具包
├─requirements.txt         # 项目核心依赖 (pytest, playwright, allure, FAISS, Gemini 等)
├─setup_env.sh / .bat      # 跨平台环境一键设置脚本
└─main.py                  # 主启动文件
```

---

## 💡 最佳实践

1. **隔离环境**: 每次执行测试或开发前，请确保已激活虚拟环境。
2. **调试利器**: 测试失败或编写新用例时，善用 `--headed` 模式进行可视化调试。
3. **持续集成**: 提交代码前确保所有冒烟测试通过。
4. **知识沉淀**: 遇到 AI 定位不准或特殊业务组件时，及时更新 `Knowledge_Base.md`，实现真正的“自愈进化”。
5. **依赖更新**: 定期更新依赖并测试兼容性 (`pip install --upgrade -r requirements.txt`)。

---

## 🔧 故障排除与技术支持

### 常见问题排查

| 问题                    | 解决方案                                     |
| ----------------------- | -------------------------------------------- |
| 虚拟环境无法激活        | 重新运行 `./setup_env.sh` 或 `setup_env.bat` |
| Playwright 浏览器未找到 | 激活环境后手动运行 `playwright install`      |
| 测试超时                | 增加 `--timeout` 参数或检查测试网络连接      |
| 元素未找到              | 检查选择器，使用 `--headed` 模式辅助排查     |
| 模块导入错误            | 确认虚拟环境已激活，重新安装依赖包           |
| 权限错误 (macOS/Linux)  | 运行 `chmod +x setup_env.sh` 赋予执行权限    |

### 寻求技术支持

如遇框架或配置上的复杂问题，请依次检查：
1. Python 版本是否符合 3.9+ 要求 (`python --version`)
2. `.env` 文件中的 Gemini API Key 是否正确配置并未欠费/超限
3. 控制台输出的 AI 诊断日志，以定位问题根因

---

**版本:** v4.0 | **最后更新:** 2026-04-14 | **维护者:** Autotest-monster Team
