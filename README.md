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

推荐使用 `runner.py` 智能启动脚本进行测试执行：

```bash
# 交互式执行：终端弹出层级菜单，支持逐层进入目录、选择具体 YAML 或一键执行某个目录下的所有测试！
python runner.py
```

### 4. 录制测试脚本 (Codegen)

本项目提供了 `codegen.py` 和 `codegen.sh` 脚本，用于快速启动 Playwright 录制工具，并自动根据角色和环境加载对应的登录 Cookie，避免每次录制都需要重新登录。

**使用方式：**
```bash
# 使用 Python 脚本 (推荐)
./codegen.py

# 或使用 Shell 脚本
./codegen.sh
```

**交互式录制流程：**
1. **选择角色**: 支持 `partner`, `guest`, `co-seller`。选择 `guest` 时不会加载任何 Cookie。
2. **选择环境**: 支持 `staging`, `release`, `prod`。工具会自动寻找类似 `cookie_release.json` 或 `cookie_coseller_prod.json` 的文件并加载。
3. **输入 URL**: 输入你想直接跳转录制的页面链接（直接回车可跳过，开启空白页）。
*(注：在任意提示环节输入 `q` 或按 `Ctrl+C` 即可安全退出)*

### 5. 查看测试报告

测试完成后，系统会自动生成并打开 Allure 测试报告。

---

## 📖 详细使用指南

### 测试执行与常用命令

除了交互式的 `runner.py`，您也可以通过命令行传递参数或直接使用 pytest 命令。

**使用 `runner.py` 快捷指令：**
```bash
# 运行单个测试用例 (默认带上 --headed -v)
python runner.py testT4718

# 运行多个测试用例 (默认使用 or 逻辑匹配)
python runner.py testT4718 testT4718_guest

# 传递额外的 pytest 参数 (如无头模式、指定环境等)
python runner.py testT4718 --headless --env release
```
> **💡 提示：** 当执行整个文件或目录下所有的测试时，`runner.py` 会自动解析 YAML 提取出每一个单独的 `testTxxxx` 测试用例，并**逐一拆分执行**。如果某一个用例失败，不会中断其他用例的执行。

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
如遇问题，请检查：

1. Python 版本是否符合要求（`python --version`）
2. 虚拟环境是否正确激活
3. 依赖包是否完整安装
4. Playwright 浏览器是否已安装
5. `.env` 文件中的 API Key 是否正确配置

## Page-level Search — 按需启用，避免无差别降级拖慢用例

**背景**: Page-level Search 在弹窗嵌套、多层 Drawer 等场景下非常有效，但若不加区分地默认触发，会让所有用例（即使不涉及弹窗的普通用例）都多走一轮全页面枚举，导致整体执行时间大幅增加。

**v4.1 变更 — Page-level Search 改为按需启用**:

`smart_click` 默认行为已优化为**快速精准定位**，不再默认触发 Page-level Search。只有显式声明 `fallback_scan: true` 时才进入完整兜底链路。

```yaml
# ✅ 普通用例（推荐，默认快速，不触发页面枚举）
R_click_save: { name: 'Save' }
click_submit: { role: 'button', name: 'Submit' }

# ✅ 困难场景（显式开启 Page-level Search + AI 自愈兜底）
R_click_save_hard: { name: 'Save', fallback_scan: true }
R_click_scan: { name: 'Get Tickets' }   # 始终启用完整兜底

# ✅ 显式 action 名称（推荐用于复杂场景）
R_click_scan_save: { name: 'Save' }     # 等效于 fallback_scan: true
```

**性能收益**: 根据用例步骤数量，无差别 Page-level Search 可能导致每步额外等待 0.5–2 秒。改为按需启用后，普通用例预计提速 **30–50%**。

**优势**: 相比 AI 自愈，Page-level Search **无需截图、无需调用 Gemini API、零 Token 消耗**，精准度反而更高（页面按钮枚举是精确匹配，AI 视觉是概率性的）。

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

#### `smart_check` 典型使用场景示例：

*   **场景 1：标准 MUI Switch (受控组件)**
    ```yaml
    # 无需担心 Playwright 报错 "Clicking... did not change state"
    check_allow_copy: { name: "Allow others to copy", checked: true }
    ```

*   **场景 2：弹窗与背景“撞衫” (智能域感知)**
    ```yaml
    # 自动锁定最新弹窗视口，避免误点背景中的同名元素
    check_modal_default: { role: 'checkbox', index: 0 } 
    ```

*   **场景 3：打破沙箱 (手动跨域)**
    ```yaml
    # 若需在弹窗/抽屉开启时勾选底层页面元素，使用 no_modal_scope
    check_background_sync: { role: 'checkbox', name: 'Sync now', no_modal_scope: true }
    ```

*   **场景 4：最高稳定定位 (`test_id` + `check`)**
    ```yaml
    # 结合最稳的 test_id 定位与最聪明的 check 动作
    check_publish_toggle: { test_id: 'publish-switch-input', checked: true }
    ```

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

## v4.2 新增功能 (2026-04-23)

### verify_no_sibling_text — 验证元素/文本不存在

**适用场景**: 验证"某个文本在指定区域内**不存在**"，例如验证 CTA 选项未展开时 "Choose call-to-action type" 不可见。

**实现位置**: `actions/base.py` → `verify_no_sibling_text()`

**两种用法**:

```yaml
# Pattern 1: 锚定元素，检查其兄弟节点不包含指定文本
verify_no_sibling_add_new:
    locator: '[data-testid="base-more-horiz-icon-cta"]'
    index: -1
    text: 'Add new'

# Pattern 2: 直接验证文本在指定容器区域内不可见（推荐）
verify_cta_type_4:
    text: 'Choose call-to-action type'
    container: 'test_general_products'
```

**参数说明**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `locator` | string | - | 锚定元素选择器（与 container 二选一） |
| `index` | int | -1 | 元素索引，支持负数（如 -1 为最后一个） |
| `text` | string | 必填 | 要验证**不存在**的文本 |
| `container` | string | - | 搜索范围容器文本（与 locator 二选一） |
| `timeout` | int | 5000 | 超时(ms) |

### execute_js — 执行 JavaScript

**适用场景**: 直接在浏览器上下文中执行 JavaScript，适用于自定义操作、读取 DOM 数据、触发特殊事件等。

**实现位置**: `actions/base.py` → `execute_js()`

```yaml
# 1. 内联脚本（自动包装为箭头函数）
execute_js: { script: "document.title" }

# 2. 脚本带参数
execute_js:
    script: "(selector) => document.querySelector(selector).innerText"
    args: "h1"

# 3. 多参数
execute_js:
    script: "(a, b) => a + b"
    args: [1, 2]

# 4. 外部 JS 文件
execute_js: { file: "scripts/scroll_to_top.js" }

# 5. 断言返回值
execute_js:
    script: "() => document.querySelectorAll('.item').length"
    assert_equals: 5

# 6. 保存返回值到 workflow context
execute_js:
    script: "() => document.querySelector('.price').textContent"
    save_as: "price_text"
```

### Allure HTTP Server — 局域网共享测试报告

**背景**: CI/CD 环境下运行 `allure open` 会阻塞主进程，且机器可能有多块虚拟网卡导致 IP 随机，不便于局域网同事访问报告。

**解决方案**: `http_server.py` 独立子进程 HTTP 服务器，自动检测局域网 IP（排除 VirtualBox/VMware/Hyper-V 虚拟网卡）。

**使用方法**:

```bash
# 启动（独立窗口，不阻塞 pytest 主进程）
python http_server.py <report_dir> <port>

# 示例
python http_server.py report/html/2026-04-23_11-00 8080
```

**启动后自动打印**:

```
Allure 报告服务已启动!
====================================
同事访问: http://192.168.50.92:8080
本机 Allure: 自动已打开
====================================
按 Ctrl+C 停止服务
```

**main.py 集成**: `main.py` 已在测试完成后自动启动 HTTP Server 并打印局域网访问地址。

---

**版本:** v4.2 | **最后更新:** 2026-04-23 | **维护者:** Autotest-monster Team
