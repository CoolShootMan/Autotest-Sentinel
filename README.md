## Auto Test 框架 v4.0

> pytest + playwright + allure + Gemini AI 实现 UI 自动化测试 + AI 自愈

简体中文 | [English](./README.en.md)

## 实现功能

- **关键字驱动**: YAML 定义测试用例，无需编码即可编写 UI 自动化测试
- **Action Registry 模式**: 模块化动作注册表，支持多人协作开发
- **AI 自愈 (Self-Healing)**: 当传统定位器失效时，基于 Gemini Vision 的 AI 自动识别并修复元素定位
- **RAG 知识库增强**: 使用 FAISS + SentenceTransformers 构建领域知识库，为 AI 提供业务上下文
- **执行历史追踪**: 自动记录已成功执行的步骤，为 AI 提供当前测试流程状态
- **多环境支持**: 通过 `--env` 参数切换 staging/release 环境
- **动态多断言**: 支持多种断言类型（文本可见性、元素存在性等）
- **测试完成自动生成 Allure 测试报告**
- **跨平台支持**: 支持 Windows、macOS、Linux 系统

## 架构概览

```
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

## 目录结构

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
│       │  ├─module.py     # 模块相关动作
│       │  ├─product.py    # 产品相关动作
│       │  ├─form.py       # 表单相关动作
│       │  └─layout.py     # 布局验证动作
│       ├─utils/           # [NEW v4.0] AI 自愈工具集
│       │  ├─ai_vision.py  # Gemini Vision AI 服务 (SOM + 多 API Key 轮换)
│       │  ├─rag_knowledge.py  # RAG 知识库 (FAISS + SentenceTransformers)
│       │  └─Knowledge_Base.md # 领域知识库文档
│       ├─conftest.py      # Pytest fixtures (多环境 + 认证)
│       ├─test_ui.py       # 核心测试执行引擎 (含执行历史追踪)
│       └─Katana_curator_smoke_release.yaml  # Release 环境用例
├─tools                    # 工具包
│  ├─__init__.py           # Allure 集成等
│  └─get_cookie.py         # Cookie 获取
├─requirements.txt         # 项目依赖
├─setup_env.sh            # macOS/Linux 环境设置脚本
├─setup_env.bat           # Windows 环境设置脚本
└─main.py                  # 主启动文件
```

## 快速开始

### 1. 环境设置（推荐）

根据您的操作系统，运行相应的设置脚本：

**macOS/Linux:**

```bash
./setup_env.sh
```

**Windows:**

```bash
setup_env.bat
```

这个脚本会自动：

- 检测并创建适合当前操作系统的虚拟环境
- 安装所有 Python 依赖
- 安装 Playwright 浏览器

### 2. 手动安装（可选）

如果您想手动设置环境：

```bash
# 创建虚拟环境
python3 -m venv venv          # macOS/Linux
python -m venv venv            # Windows

# 激活虚拟环境
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate.bat      # Windows CMD

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install
```

### 3. 环境配置

在项目**根目录**下创建 `.env` 文件，配置 Gemini API Keys（支持多个 Key 轮换以避免频率限制）：

```env
# 必填：Gemini API Key (推荐使用复数形式配置多个)
GEMINI_API_KEYS=key1,key2,key3

# 或者配置单个 Key (兼容旧版本)
GEMINI_API_KEY=your_single_key_here
```

### 4. 运行测试

```bash
# 运行特定用例 (headed 模式)
pytest test_case/UI/Test_Katana/test_ui.py \
    -k "testT3554" \
    --headed \
    -v \
    --env release \
    --storage-state test_case/UI/Test_Katana/cookie_release.json

# 运行全部用例并生成报告
python main.py
```

### 5. 查看报告

运行完成后 Allure 报告会自动打开。

## 常用命令

### 激活/退出虚拟环境

**macOS/Linux:**

```bash
source venv/bin/activate    # 激活
deactivate                  # 退出
```

**Windows:**

```bash
venv\Scripts\activate.bat   # 激活
deactivate                  # 退出
```

### 运行测试

```bash
# 测试特定用例
pytest test_case/UI/Test_Katana/test_ui.py -k testT3554 --headed -v --env release --storage-state test_case/UI/Test_Katana/cookie_release.json

# 测试多个用例
pytest test_case/UI/Test_Katana/test_ui.py -k "testT3554 or testT4660" --headed -v

# 运行所有测试
pytest test_case/UI/Test_Katana/test_ui.py --headed -v

# 显示详细输出
pytest -vv -s test_case/UI/Test_Katana/test_ui.py

# 生成 Allure 报告
pytest --alluredir=allure-results test_case/UI/Test_Katana/test_ui.py
allure serve allure-results
```

### 环境管理

```bash
# 重建环境（遇到问题时使用）
rm -rf venv && ./setup_env.sh          # macOS/Linux
rmdir /s venv && setup_env.bat         # Windows

# 更新依赖
pip install --upgrade -r requirements.txt

# 安装新依赖
pip install package_name
pip freeze > requirements.txt
```

## 测试参数说明

| 参数              | 说明            | 示例                          |
| ----------------- | --------------- | ----------------------------- |
| `-k`              | 按名称过滤测试  | `-k testT3554`                |
| `-v`              | 详细输出        | `-v`                          |
| `-vv`             | 更详细输出      | `-vv`                         |
| `-s`              | 显示 print 输出 | `-s`                          |
| `--headed`        | 显示浏览器窗口  | `--headed`                    |
| `--headless`      | 无头模式        | `--headless`                  |
| `--storage-state` | 使用保存的会话  | `--storage-state cookie.json` |
| `--env`           | 指定环境        | `--env release`               |
| `--yaml`          | 指定配置文件    | `--yaml config.yaml`          |

## V4.0 AI 自愈架构

### 核心流程

1. `smart_click` 先尝试传统 Playwright 定位 (role/name/text)
2. 如果 5s 内超时，触发 Legacy Fallback (15s)
3. 如果仍然失败，触发 **AI Self-Healing**：
   - 对当前页面截图并注入 SOM (Set-of-Mark) 标注
   - 查询 RAG 知识库获取相关业务上下文
   - 将截图 + 目标描述 + 执行历史 + RAG 知识 发送至 Gemini Vision
   - AI 返回诊断结果和目标元素 ID
   - 根据 AI 指引点击目标元素

### RAG 知识库

`utils/Knowledge_Base.md` 存储了系统的业务规则和 UI 导航模式，包括：

- 系统架构和模块概述
- 常见导航模式（FAB 按钮、事件管理等）
- UI 元素特征和定位策略
- 已知的自动化陷阱和解决方案

### 如何补充知识库

当 AI 自愈出现误判时，在 `Knowledge_Base.md` 中添加对应的业务规则，AI 下次会自动检索并参考。

## 多环境支持

```bash
# Staging 环境
pytest --env staging ...

# Release 环境
pytest --env release ...
```

## 跨平台支持

本项目支持在 Windows、macOS 和 Linux 上运行。自动设置脚本会：

1. **自动检测操作系统类型**
2. **创建适合该系统的虚拟环境**
3. **安装对应的依赖和浏览器**

### 虚拟环境兼容性

- **Windows**: 使用 `venv/Scripts/` 目录，包含 `.exe` 可执行文件
- **macOS/Linux**: 使用 `venv/bin/` 目录，包含无扩展名可执行文件

### 解决跨平台问题

如果您在不同操作系统之间切换工作，遇到虚拟环境不兼容的问题：

```bash
# 删除旧环境，重新创建
rm -rf venv          # macOS/Linux
rmdir /s venv        # Windows

# 运行设置脚本
./setup_env.sh       # macOS/Linux
setup_env.bat        # Windows
```

## 故障排除

| 问题                    | 解决方案                                     |
| ----------------------- | -------------------------------------------- |
| 虚拟环境无法激活        | 重新运行 `./setup_env.sh` 或 `setup_env.bat` |
| Playwright 浏览器未找到 | 激活环境后运行 `playwright install`          |
| 测试超时                | 增加 `--timeout` 参数或检查网络连接          |
| 元素未找到              | 检查选择器，使用 `--headed` 模式调试         |
| 导入错误                | 确认虚拟环境已激活，重新安装依赖             |
| 权限错误 (macOS/Linux)  | 运行 `chmod +x setup_env.sh`                 |

## 系统要求

- **Python:** 3.9+ (推荐 3.10+)
- **操作系统:** Windows 10+, macOS 11+, 或主流 Linux 发行版
- **浏览器:** Chromium (由 Playwright 自动安装)
- **内存:** 建议 8GB+ RAM
- **磁盘空间:** 至少 2GB 可用空间

## 最佳实践

1. **每次使用前激活虚拟环境**
2. **测试失败时使用 `--headed` 模式调试**
3. **定期更新依赖并测试兼容性**
4. **提交代码前确保所有测试通过**
5. **遇到 AI 误判时及时更新 RAG 知识库**

## 依赖说明

主要依赖包括：

- `pytest` - 测试框架
- `playwright` - 浏览器自动化
- `allure-pytest` - 测试报告
- `pandas` - 数据处理
- `sentence-transformers` - AI/ML 功能
- `faiss-cpu` - 向量搜索
- `google-generativeai` - Gemini Vision AI

查看完整依赖列表请参考 `requirements.txt`。

## 技术支持

如遇问题，请检查：

1. Python 版本是否符合要求（`python --version`）
2. 虚拟环境是否正确激活
3. 依赖包是否完整安装
4. Playwright 浏览器是否已安装
5. `.env` 文件中的 API Key 是否正确配置

## Page-level Search — 零 Token 全页扫描兜底

**背景**: 当目标按钮/元素处于 Modal 弹窗域之外（例如 Drawer 抽屉、Post 编辑器面板），而框架已将搜索域锁定在弹窗内时，传统定位会失败。

**机制**: `smart_click` 在传统 Playwright 定位失败后，若目标具有 `role='button'` 属性，会自动触发全页面按钮扫描：

```python
# YAML 用法无需任何改动，框架自动兜底：
R_click_save: { role: 'button', name: 'Save' }
```

**优势**: 相比 AI 自愈，Page-level Search **无需截图、无需调用 Gemini API、零 Token 消耗、零额外延迟**，精准度反而更高（因为页面按钮枚举是精确匹配，AI 视觉是概率性的）。

### MUI Controlled-Input 自愈 — 应对 React 受控组件拦截

**背景**: Material-UI 的 Switch/Checkbox 使用受控组件模式，原生 `<input>` 被视觉 Wrapper 覆盖。Playwright 的 `set_checked()` 有时会抛出：
```
Locator.set_checked: Clicking the checkbox did not change its state
<div class="MuiStack-root ..."> intercepts pointer events
```

**机制**: `smart_check` 检测到此错误后，自动执行三步降级：
1. 通过 JS `node.checked` 读取真实状态，避免无谓的重复切换
2. 定位父级包裹节点（React onClick handler 真正绑定处）
3. `force=True` 穿透遮罩层直接点击父节点

### test_id 原生支持

`smart_click` 现已支持 `test_id` 参数，作为**最高优先级定位策略**（优于 role/name/locator）：

```yaml
# 支持在任何 clickable 步骤中使用 test_id
click_cta: { test_id: 'enhance-button-cta' }
click_confirm: { test_id: 'confirm-button' }
```

### smart_check 弹窗域感知

`smart_check` 现已与 `smart_click` 同步，自动检测当前激活的 Modal/Dialog/Drawer，将 checkbox 搜索域限制在弹窗内，避免勾选到背景页面中的同名元素。

---

**版本:** v4.0  
**最后更新:** 2026-04-15  
**维护者:** Autotest-monster Team

```
