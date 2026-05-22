# Auto Test Framework v4.3 - 技术指南

## 目录
- [1. 项目架构](#1-项目架构)
- [2. 测试执行流程](#2-测试执行流程)
- [3. AI 自愈系统](#3-ai-自愈系统)
- [4. Action Registry 动作注册表](#4-action-registry-动作注册表)
- [5. 添加新测试用例](#5-添加新测试用例)
- [6. RAG 知识库维护](#6-rag-知识库维护)
- [7. 调试技巧](#7-调试技巧)
- [8. 常见问题](#8-常见问题)
- [9. v4.1 智能兜底机制 (Smart Fallback)](#9-v41-智能兜底机制-smart-fallback)
- [10. 可选点击与稳定重试机制](#10-可选点击与稳定重试机制)
- [11. verify_no_sibling_text — 验证元素/文本不存在](#11-verify_no_sibling_text--验证元素文本不存在)
- [12. execute_js — 执行 JavaScript](#12-execute_js--执行-javascript)
- [13. Allure HTTP Server — 局域网共享报告](#13-allure-http-server--局域网共享报告)
- [14. 失败用例诊断工具 (diagnose_failed.py)](#14-失败用例诊断工具-diagnose_failedpy)
- [15. AI Vision 按需加载 (ENABLE_AI_VISION)](#15-ai-vision-按需加载-enable_ai_vision)
- [16. 辅助工具生态](#16-辅助工具生态)

---

## 1. 项目架构

### 1.1 核心组件

```
autotest-monster/
├── test_case/UI/Test_Katana/
│   ├── actions/                # Action Registry (动作注册表)
│   │   ├── __init__.py         # 注册表入口 + get_action()
│   │   ├── base.py             # 基础动作 (smart_click, smart_fill)
│   │   ├── module.py           # 模块相关动作
│   │   ├── product.py          # 产品相关动作
│   │   ├── form.py             # 表单相关动作
│   │   └── layout.py           # 布局验证动作
│   ├── utils/                  # [v4.0] AI 自愈工具集
│   │   ├── ai_vision.py        # Gemini Vision AI 服务
│   │   ├── rag_knowledge.py    # RAG 知识库引擎
│   │   └── Knowledge_Base.md   # 领域知识库文档
├── conftest.py                         # 【根级】全局配置：YAML 加载、storage-state、
│                                       #          browser_context_args、guest 模式 cookie 隔离
│   └── test_case/UI/Test_Katana/
│       ├── conftest.py                 # 【包级】Test_Katana 专属配置：video/screenshot
│       │                              #          自动附加到 Allure、摄像头伪装参数、
│       │                              #          is_guest cookie 拦截（以包级为准覆盖根级）
│   ├── test_ui.py              # 核心测试执行引擎
│   └── Katana_curator_smoke_release.yaml  # 测试用例定义
├── page/
│   └── home.py                 # Playwright UI 操作封装
├── tools/
│   ├── __init__.py             # Allure 集成
│   ├── diagnose_failed.py      # [v4.3] 失败用例诊断报告工具
│   ├── ui_snapshot.py          # DOM 快照 + diff 检测
│   ├── locator_updater.py      # YAML 定位器批量更新
│   └── get_cookie.py           # Cookie 获取
└── main.py                     # 主启动入口
```

### 1.2 数据流

```
YAML 测试定义
    ↓
conftest.py (pytest fixtures: 浏览器/环境/认证)
    ↓
test_ui.py (步骤解析 → Action Registry 分发 + 执行历史追踪)
    ↓
actions/base.py → smart_click (传统定位 → Legacy Fallback → AI 自愈)
    ↓                                                    ↓
page/home.py (Playwright 操作)              utils/ai_vision.py (Gemini Vision)
    ↓                                            ↓
浏览器自动化                              utils/rag_knowledge.py (RAG 检索)
    ↓
Allure 报告 + 截图/录屏
    ↓
[失败用例] → tools/diagnose_failed.py → 重放 + 截图 + DOM + 多策略探查 → HTML 诊断报告
```

---

## 2. 测试执行流程

### 2.1 完整流程

```bash
python main.py
```

**执行步骤:**
1. `main.py` 配置 logger、Allure 路径
2. 调用 `pytest` 执行 `test_ui.py`
3. `conftest.py` 创建 browser/context fixtures (加载 cookie)
4. `test_ui.py` 的 `test_case` 函数被参数化执行
5. 每个步骤通过 `get_action(key)` 分发到对应的处理函数
6. 成功的步骤被记录到 `_execution_history` 列表
7. 生成 Allure HTML 报告

### 2.2 单个测试用例执行

```bash
# 运行特定用例
pytest test_case\UI\Test_Katana\test_ui.py -k "test_guest_submission_2" --storage-state "test_case\UI\Test_Katana\cookie_release_demi.json" --env release --yaml Partner_create_form.yaml --headed -v 
```

### 2.3 多环境支持

通过 `--env` 参数切换：
- `--env staging` → 加载 `_staging.yaml`
- `--env release` → 加载 `_release.yaml`

---

## 3. AI 自愈系统

### 3.1 触发机制

`smart_click` (在 `actions/base.py` 中) 实现了三级容错：

```
Level 1: 标准 Playwright 定位 (test_id → role+name → locator → text)
    ↓ 失败（若 fallback_scan=True 进入 Level 2；否则直接抛异常）
Level 2a: Page-level Search (fallback_scan=True 时触发，零 Token)
    ↓ 失败
Level 2b: MUI Controlled-Input Fallback (仅 smart_check)
    ↓ 失败
Level 3: AI Self-Healing (fallback_scan=True 且 disable_ai=False 且 ENABLE_AI_VISION=1)
```

> **v4.3 重要变更**: AI 自愈 (Level 3) 默认关闭。需在 `.env` 设置 `ENABLE_AI_VISION=1` 才会加载 Gemini Vision + RAG 知识库。详见 [第 15 节](#15-ai-vision-按需加载-enable_ai_vision)。

### 3.2 AI Vision 服务 (`utils/ai_vision.py`)

**AIVisionService 类功能：**
- **多 API Key 轮换**: 支持多个 Gemini API Key，自动在 Rate Limit 时切换
- **SOM 标注**: 在截图上注入 Set-of-Mark 标签，帮助 AI 精确定位元素
- **结构化输出**: AI 返回 JSON 格式的诊断结果，包含：
  - `consciousness_diagnosis`: 当前页面状态诊断
  - `thought_process`: 推理过程
  - `suggested_action`: 建议操作 (GOAL_CLICK / NAVIGATE_BACK 等)
  - `label_id`: 目标元素的 SOM 标签 ID

**Prompt 包含的上下文信息：**
1. 业务背景描述 (Pear 系统概述)
2. 当前步骤的目标描述
3. 已成功执行的步骤列表 (`_execution_history`)
4. RAG 知识库检索结果
5. 测试用例的整体描述

### 3.3 RAG 知识库 (`utils/rag_knowledge.py`)

**技术栈：**
- **FAISS** (faiss-cpu): 向量相似度搜索
- **SentenceTransformers** (all-MiniLM-L6-v2): 文本嵌入模型

**工作流程：**
1. 启动时加载 `Knowledge_Base.md`，按 `##` 标题分块
2. 使用 SentenceTransformers 对每个块进行向量编码
3. 建立 FAISS 索引
4. AI 自愈触发时，根据当前目标 + 执行历史检索 Top-3 相关知识
5. 将检索到的知识注入 AI Prompt

### 3.4 执行历史追踪

`test_ui.py` 在 `page` 对象上维护 `_execution_history` 列表：

```python
page._execution_history = []

# 每步成功后追加
page._execution_history.append(f"Step '{k}': completed successfully")
```

这让 AI 知道"我已经完成了哪些步骤"，避免重复操作或误判当前位置。

---

## 4. Action Registry 动作注册表

### 4.1 架构

`actions/__init__.py` 维护关键字到函数的映射：

```python
ACTIONS = {
    "open": open_url,
    "R_click": smart_click,
    "fill": smart_fill,
    "wait_for_url": wait_for_url,
    # ...
}
```

`test_ui.py` 通过前缀匹配分发：
```python
action_fn = get_action(k)  # 根据键名前缀查找处理函数
action_fn(page, v)          # 执行
```

### 4.2 如何新增测试步骤

1. 在 `actions/` 下找到或新建模块文件
2. 编写处理函数：`def my_action(page: Page, v: dict): ...`
3. 在 `actions/__init__.py` 的 `ACTIONS` 字典中注册
4. 在 YAML 中使用对应的 key

---

## 5. 添加新测试用例

### 5.1 YAML 用例格式

```yaml
testT{编号}:
    description: "用例描述"
    test_step:
        open: "https://release.pear.us/events"
        wait_for_url: { url: "**/events" }
        sleep_after_open: 3000
        R_click_button: { role: 'button', name: 'Submit' }
        sleep_after_click: 2000
    expect_result:
        description: "验证结果"
        assertions:
            - { assertion_type: "element_visible_by_text", text: "Success" }
```

### 5.2 常用步骤速查

| 操作 | YAML 示例 | 说明 |
|------|----------|------|
| 打开页面 | `open: "https://..."` | 导航到 URL |
| 等待 URL | `wait_for_url: { url: "**/events" }` | 等待 URL 匹配 |
| 等待 | `sleep_after_open: 2000` | 毫秒 |
| 点击 (role) | `R_click_btn: { role: "button", name: "Submit" }` | 语义定位 |
| 点击 (text) | `R_click_item: { text: "Link text", exact: false }` | 文本定位 |
| 强制点击 | `R_click_item: { role: "paragraph", name: "...", force: true }` | 穿透遮罩层 |
| 填充 | `fill_email: { role: "textbox", name: "Email", value: "test@test.com" }` | |
| 上传 | `upload_file: { text: "Upload", file_path: "data/img.jpg" }` | |
| 勾选 | `check_agree: { role: "checkbox", name: "I agree" }` | |
| 执行 JS | `execute_js: { script: "document.title" }` | 浏览器上下文执行 JS |
| 验证文本不存在 | `verify_no_sibling_text: { text: "xxx", container: "yyy" }` | 验证文本在容器内不可见 |

### 5.3 断言类型

```yaml
assertions:
    - { assertion_type: "element_visible_by_text", text: "Success" }
    - { assertion_type: "element_text", role: "heading", value: "Title" }
    - { assertion_type: "element_visible", role: "button", visible: true }
```

---

## 6. RAG 知识库维护

### 6.1 文件位置
`test_case/UI/Test_Katana/utils/Knowledge_Base.md`

### 6.2 内容结构
使用 `##` 二级标题分块，每个块是一个独立的知识条目：

```markdown
## 1. System Overview
* 系统架构描述...

## 2. Common Navigation Patterns
* FAB 按钮使用规则...

## 3. UI Element Characteristics
* 定位策略和技巧...

## 4. Known Bugs
* 已知的自动化问题...

## 5. Standard Test Flows
* 标准测试流程模板...
```

### 6.3 何时更新知识库
- AI 自愈频繁误判同类元素时
- 发现新的 UI 模式或导航路径时
- 遇到 MUI 组件的特殊行为时

### 6.4 更新后生效
知识库在测试启动时自动重新索引，无需额外操作。

---

## 7. 调试技巧

### 7.1 查看 AI 自愈日志

AI 每次自愈都会在日志中输出：
```
🧠 AI SOM Thoughts: [AI的推理过程]
✨ AI 'Junior QA' Found Target ID: [元素ID]
🧠 Diagnosis: [页面状态诊断]
🚀 Suggested Action: [建议操作]
```

### 7.2 Headed 模式运行

```bash
pytest test_case/UI/Test_Katana/test_ui.py -k "testT4777" --headed -v
```

### 7.3 查看执行历史

日志中搜索 `>>> Current Step:` 可追踪完整执行路径。

---

## 8. 常见问题

### 8.1 AI 自愈误判

**原因**: 知识库中缺少对应的业务规则
**解决**: 在 `Knowledge_Base.md` 中补充相关知识条目

### 8.2 元素定位超时

**原因**: MUI 组件渲染延迟或遮罩层
**解决**: 使用 `force: true` 穿透遮罩，或增加 `sleep` 等待时间

### 8.3 Session 过期

**原因**: Cookie 文件中的 token 已过期
**解决**: 重新执行 `playwright codegen` 获取新的 cookie

### 8.4 Guest 模式

在 YAML 中添加 `guest: true` 使测试在未登录状态下运行：
```yaml
testT4279:
    guest: true
    description: "访客模式测试"
```

---

## 9. V4.1 智能兜底机制 (Smart Fallback)

### 9.1 架构升级：三层容错（v4.1）

```
Level 1: 标准 Playwright 定位 (test_id → role+name → locator → text)
    ↓ 失败（fallback_scan=False 时直接抛出异常）
    ↓
Level 2: Page-level Search + AI 自愈（仅 fallback_scan=True 时触发）
    ├── Page-level Search: 零 Token 全页扫描
    │   遍历页面所有匹配元素 → 点击第一个可见者
    │   └── is_visible 超时优化：500ms（v4.1 原为 2000ms）
    └── AI Self-Healing: Gemini Vision + SOM + RAG（当 Page-level Search 也失败时）
```

> ⚠️ **v4.1 重大变更**: Page-level Search **不再默认触发**。
> 改为 `fallback_scan=True` 按需启用，避免无差别降级拖慢所有用例。
> 默认行为已恢复为纯快速精准定位。

### 9.2 Page-level Search

**触发条件**: `fallback_scan=True` 且 Level 1 精准定位失败。

**实现位置**: `actions/base.py` → `_smart_click_with_fallback()`。

**工作原理**:
```python
# 调用 page.get_by_role(...).all() 不限制 Modal 域
all_matches = page.get_by_role(target_role, name=target_name, exact=False).all()
for idx, candidate in enumerate(all_matches):
    # 优化：超时 500ms（v4.0 原为 2000ms），减少等待
    if candidate.is_visible(timeout=500):
        candidate.click(force=True)   # 点击第一个可见者
        return
    else:
        # 最终降级：JS 直接 dispatch click event
        page.evaluate("(el) => el.click()", candidate.element_handle())
        return
```

**关键优势**:
| 对比项 | Page-level Search | AI Self-Healing |
|--------|------------------|-----------------|
| Token 消耗 | **0** | 约 500-1500 tokens/次 |
| 延迟 | **< 200ms** | 3-10 秒 |
| 精准度 | **精确字符串匹配** | 视觉概率估算 |
| 依赖 | 无 | Gemini API + 网络 |

**YAML 使用** — 推荐用法：

```yaml
# ✅ 普通用例（快速，默认不触发 Page-level Search）
R_click_save: { name: 'Save' }

# ✅ 困难场景（显式开启完整兜底）
R_click_save_hard: { name: 'Save', fallback_scan: true }

# ✅ 显式 action（R_click_scan 等效于 fallback_scan=True）
R_click_scan_save: { name: 'Save' }
```

### 9.3 MUI Controlled-Input Fallback (`smart_check` 专属)

**触发条件**: `set_checked()` 抛出 `"Clicking the checkbox did not change its state"` 或 `"intercepts pointer events"`。

**实现位置**: `actions/base.py` → `smart_check()` → except 块。

**分步流程**:
```python
# Step 1: 重新定位元素
el = root.get_by_role(target_role, ...).nth(index)

# Step 2: 读取 JS 真实状态，防止重复切换
is_currently_checked = el.evaluate("node => node.checked")
if bool(is_currently_checked) == bool(checked):
    return  # 状态已正确，无需操作

# Step 3: 强制穿透点击父级包裹
el.locator("..").click(force=True)
page.wait_for_timeout(500)
```

**适用场景**: Material-UI Switch、Checkbox、Toggle 等 React 受控组件。

### 9.4 test_id 原生支持

`smart_click` 最高优先级定位策略，在所有其他定位方式之前尝试：

```yaml
# YAML 中直接传入 test_id 参数
click_cta_btn: { test_id: 'enhance-button-cta' }
click_confirm:  { test_id: 'confirm-button' }
```

```python
# 内部实现（base.py）
if target_test_id:
    el = root.get_by_test_id(target_test_id).nth(target_index)
    if el.is_visible(timeout=5000):
        el.click(force=force)
        return
```

### 9.5 smart_check 弹窗域感知

与 `smart_click` 保持一致，自动检测激活弹窗并将搜索域限制在其中：

```python
modals = page.locator("[role='dialog'], [role='alertdialog'], .MuiDialog-root, .MuiModal-root, .MuiDrawer-root").all()
active_modal = next((m for m in reversed(modals) if m.is_visible()), None)
root = active_modal if active_modal else page
```

**避免的问题**: 防止 `check_xxx_checkbox: { role: 'checkbox', index: 0 }` 在弹窗打开时误匹配到背景页面的同名 checkbox。

---

## 10. 可选点击与稳定重试机制

### 10.1 概述

为了解决不同场景下的元素点击稳定性问题，新增了两个专用动作方法：

| 方法 | 适用场景 | 找不到元素时 | 点击失败时 |
|------|----------|--------------|------------|
| `smart_click_optional` | 元素**可能不存在**（弹框可省略） | 静默跳过 | 不重试 |
| `smart_click_retry` | 元素**一定存在**，但点击不稳定 | 重试多次后报错 | 自动重试 |

### 10.2 smart_click_optional — 可选点击

**实现位置**: `actions/base.py` → `smart_click_optional()`

**设计目的**: 用于处理"可能出现也可能不出现"的弹框/提示。元素不存在时静默跳过，不报错。

**YAML 用法**:
```yaml
# 点击 "Start Customizing" 按钮，如果出现弹框则点击 Done
smart_click_optional_start_customizing: { role: 'button', name: 'Start Customizing' }
smart_click_optional_done: { role: 'button', name: 'Done' }
```

**与 `smart_click + optional: true` 的区别**:
- `smart_click` 的 `optional: true` **只在 `target_locator` 路径生效**
- `smart_click_optional` 在**所有定位策略**上都支持 optional 跳过

**实现逻辑**:
```python
def smart_click_optional(page: Page, v: dict):
    """可选点击 — 元素不存在时静默跳过，不报错。"""
    # 1. 尝试多种定位策略（test_id → locator → role+name → text）
    # 2. 所有策略都包裹 try/except，找不到元素不会抛异常
    # 3. 最终日志: "smart_click_optional: element not found 'xxx', skipping."
```

**支持的参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `role` | string | - | ARIA 角色 |
| `name` / `text` | string | - | 元素文本 |
| `test_id` | string | - | data-testid 属性 |
| `locator` | string | - | CSS/XPath 选择器 |
| `index` | int | 0 | 匹配多个时选择第几个 |
| `timeout` | int | 5000 | 查找超时(ms) |
| `exact` | bool | false | 文本精确匹配 |

### 10.3 smart_click_retry — 稳定重试点击

**实现位置**: `actions/base.py` → `smart_click_retry()`

**设计目的**: 用于处理"元素一定存在，但点击不稳定"的场景。常见原因：
- 元素被 loading 遮罩短暂遮挡
- 元素动画过渡中（未完全可点击）
- 元素刚出现在 DOM 但未渲染完成

**YAML 用法**:
```yaml
# Publish 按钮一定存在，但点击可能不稳定
smart_click_retry_publish: { role: 'button', name: 'Publish', retry: 3, delay: 500 }

# 弹框中的确认按钮
smart_click_retry_confirm: { role: 'button', name: 'Confirm', retry: 3, delay: 800, timeout: 8000 }
```

**实现逻辑**:
```python
def smart_click_retry(page: Page, v: dict):
    """带重试的稳定点击 — 元素一定存在但点击不稳定时使用。"""
    for attempt in range(1, retry_count + 1):
        # 1. 尝试多种定位策略查找元素
        el = _find_element()
        
        # 2. 元素未找到 → 等待后重试
        if el is None:
            page.wait_for_timeout(delay_ms)
            continue
        
        # 3. 等待动画完成（200ms）
        page.wait_for_timeout(200)
        
        # 4. 执行点击
        el.click(force=force, timeout=timeout)
        return
    
    # 5. 所有重试都失败 → 抛出异常
    raise Exception(f"Element not found: {desc}")
```

**新增参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `retry` | int | 3 | 重试次数上限 |
| `delay` | int | 500 | 每次重试间隔(ms) |

**支持的参数**（同 `smart_click_optional`）:
| 参数 | 说明 |
|------|------|
| `role` | ARIA 角色 |
| `name` / `text` | 元素文本 |
| `test_id` | data-testid 属性 |
| `locator` | CSS/XPath 选择器 |
| `index` | 匹配多个时选择第几个 |
| `timeout` | 查找超时(ms) |
| `exact` | 文本精确匹配 |

### 10.4 注册与使用

两个方法已注册到 `actions/__init__.py`:

```python
# 导入
from .base import smart_click_optional, smart_click_retry

# ACTIONS 注册表
ACTIONS = {
    "smart_click_optional": smart_click_optional,
    "smart_click_retry": smart_click_retry,
}

# 前缀匹配规则
if name.startswith("smart_click_optional"):
    return smart_click_optional
if name.startswith("smart_click_retry"):
    return smart_click_retry
```

**命名规范**: YAML 中的 step key 需要以方法名开头：
- `smart_click_optional_xxx` → 调用 `smart_click_optional`
- `smart_click_retry_xxx` → 调用 `smart_click_retry`

### 10.5 场景选择指南

```
元素可能不存在？
├── 是 → smart_click_optional（弹框可省略）
└── 否 → 元素一定存在
        ├── 点击不稳定（动画/遮罩）→ smart_click_retry
        └── 点击稳定 → smart_click 或 R_click
```

---

## 11. verify_no_sibling_text — 验证元素/文本不存在

### 11.1 适用场景

验证"某个文本在指定区域内**不存在**"，常用于：
- 验证 CTA 选项折叠状态下，相关文案不可见
- 验证表单未填写时，错误提示不显示
- 验证弹框关闭后，内容消失

### 11.2 实现位置

`actions/base.py` → `verify_no_sibling_text()`，已注册到 `actions/__init__.py`。

### 11.3 两种用法

**Pattern 1: 锚定元素，检查兄弟节点**

```yaml
verify_no_sibling_add_new:
    locator: '[data-testid="base-more-horiz-icon-cta"]'
    index: -1
    text: 'Add new'
```

**Pattern 2: 直接验证文本在容器区域内不可见（推荐）**

```yaml
# 验证 "Choose call-to-action type" 在 test_general_products 容器内不可见
verify_cta_type_4:
    text: 'Choose call-to-action type'
    container: 'test_general_products'
```

### 11.4 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `locator` | string | - | 锚定元素选择器（与 container 二选一） |
| `index` | int | -1 | 元素索引，支持负数（如 -1 为最后一个） |
| `text` | string | 必填 | 要验证**不存在**的文本 |
| `container` | string | - | 搜索范围容器文本（与 locator 二选一，推荐） |
| `timeout` | int | 5000 | 超时(ms) |

### 11.5 注意事项

- `locator` 和 `container` 互斥，必须提供其中一个
- Pattern 2（container）更稳定，不依赖可能不存在的锚点元素
- 文本不可见时直接通过，不抛异常；文本可见时截图并抛 AssertionError

---

## 12. execute_js — 执行 JavaScript

### 12.1 适用场景

- 读取 DOM 数据（如元素文本、属性、计算后的样式）
- 触发 Playwright 不直接支持的事件
- 执行自定义业务逻辑
- 调用外部 JS 脚本文件

### 12.2 实现位置

`actions/base.py` → `execute_js()`，已注册到 `actions/__init__.py`。

### 12.3 用法示例

```yaml
# 1. 读取页面标题
execute_js: { script: "document.title" }

# 2. 读取元素文本
execute_js:
    script: "(sel) => document.querySelector(sel).textContent"
    args: ".price"

# 3. 断言返回值
execute_js:
    script: "() => document.querySelectorAll('.item').length"
    assert_equals: 5

# 4. 保存到上下文供后续使用
execute_js:
    script: "() => document.querySelector('.price').textContent"
    save_as: "price_text"

# 5. 外部 JS 文件
execute_js: { file: "scripts/scroll_to_top.js" }
```

### 12.4 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `script` | string | JS 代码（自动包装为 `() => (...)`） |
| `file` | string | 外部 JS 文件路径（与 script 二选一） |
| `args` | string/list | 传给脚本的参数 |
| `assert_equals` | any | 断言返回值等于指定值 |
| `assert_contains` | string | 断言返回值包含指定字符串 |
| `save_as` | string | 将返回值保存到 `page._workflow_context[key]` |

---

## 13. Allure HTTP Server — 局域网共享报告

### 13.1 背景问题

1. **阻塞问题**: `allure open` 阻塞主进程，HTTP 线程随进程退出被强制终止
2. **IP 问题**: 机器有多块虚拟网卡时，`socket.gethostbyname` 随机返回虚拟网卡 IP（如 `192.168.56.1`），同事无法访问

### 13.2 解决方案

`http_server.py` 独立子进程 HTTP 服务器：

```python
# 自动检测局域网 IP（排除 VirtualBox/VMware/Hyper-V 虚拟网卡）
# 监听 0.0.0.0:port，不阻塞 pytest 主进程
# 静默日志，减少干扰
```

### 13.3 使用方法

```bash
# 手动启动
python http_server.py <report_dir> <port>

# 示例：共享 2026-04-23 的报告
python http_server.py report/html/2026-04-23_11-00 8080
```

### 13.4 main.py 集成

`main.py` 在测试完成后自动：
1. 启动 `http_server.py` 独立子进程（`CREATE_NEW_CONSOLE`）
2. 打印局域网访问地址供同事查看

```python
subprocess.Popen(http_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
logger.info(f"局域网报告地址: http://{lan_ip}:{http_port}")
```

### 13.5 文件清单

| 文件 | 说明 |
|------|------|
| `http_server.py` | 独立 HTTP 服务器脚本 |
| `main.py` | 集成启动逻辑（子进程 + 局域网 IP 检测） |

---

## 14. 失败用例诊断工具 (diagnose_failed.py)

### 14.1 概述

`tools/diagnose_failed.py` 是 v4.3 新增的失败用例自动诊断工具。它从 Allure 报告中提取失败用例，在真实浏览器中逐步重放，记录每步的截图 + DOM 快照，在失败步骤执行多策略探查，最终生成独立的 HTML 诊断报告。

### 14.2 工作流程

```
Phase 1: Allure 解析
    扫描 *-result.json → 提取 failed/broken 用例 → 解析 YAML 参数
    ↓
Phase 2: 浏览器重放
    启动 Chromium → 注入 Cookie (storage_state) → 执行 pre_condition → 逐步执行 test_step
    每步记录: before_screenshot + before_dom + after_screenshot + after_dom
    ↓
Phase 3: 失败探查 (仅在失败步骤)
    6 种探查策略并行:
    ├── 文本搜索: 查找页面中包含目标文本的元素
    ├── 角色搜索: 查找匹配 role 的所有元素
    ├── Test ID 搜索: 查找包含 testid 的元素
    ├── Locator 直接检查: 统计 locator 匹配数
    ├── 弹窗检测: 检查是否有遮挡的 dialog/popover
    └── aria-label 搜索: 查找匹配 aria-label 的元素
    ↓
Phase 4: HTML 报告生成
    生成独立 HTML 文件 (截图 base64 内嵌) → report/Error_Test_Case_Diagnosis_Report_*.html
```

### 14.3 使用方法

```bash
# 诊断最近一次运行的所有失败用例
python tools/diagnose_failed.py

# 指定 Allure 结果子目录
python tools/diagnose_failed.py --allure-dir 20260521_144342

# 诊断单个用例
python tools/diagnose_failed.py --case testT1928

# 有头模式（观察浏览器操作过程）
python tools/diagnose_failed.py --case testT1928 --headed

# 指定环境
python tools/diagnose_failed.py --env staging
```

### 14.4 关键设计决策

| 决策 | 方案 | 原因 |
|------|------|------|
| Cookie 注入 | `storage_state` (与 conftest.py 一致) | `add_cookies()` 无法正确恢复 localStorage/sessionStorage |
| `{ENV}` 占位符 | 保持原样，运行时从 cookie 文件名反推环境 | 避免 YAML 中的动态变量被破坏 |
| Pre-condition | 全量执行，走 `_execute_step` + `get_action()` | 用户要求"完完整整跑完" |
| 自定义 Action | Fallback 到项目 `get_action()` registry | 支持 `delete_coseller_if_exists` 等 104 个注册 action |
| Optional 步骤 | 步骤名含 "optional" → SKIPPED | 不中断重放流程 |
| AI 模块 | `sys.modules` mock + `ENABLE_AI_VISION` 开关 | 避免每次诊断等待 20s 模型加载 |

### 14.5 报告结构

生成的 HTML 报告包含以下部分：

- **Summary Dashboard**: 失败用例表格、复现率统计
- **Case Detail**: 每个用例的逐步重放记录
  - 每步: 状态(PASSED/FAILED/SKIPPED) + 配置 + 前后截图 + DOM 快照
  - 失败步: 错误信息 + 6 种探查策略的结果
- **Flaky Notice**: 重放通过的用例标记为可能不稳定

### 14.6 注意事项

- 报告文件名为 `Error_Test_Case_Diagnosis_Report_*.html`，存放在 `report/` 目录
- HTML 文件完全独立（截图 base64 内嵌），可直接通过邮件/IM 发送
- 诊断工具不依赖 pytest，直接使用 Playwright API
- 大量失败用例时，重放可能需要较长时间

---

## 15. AI Vision 按需加载 (ENABLE_AI_VISION)

### 15.1 背景

`utils/rag_knowledge.py` 在模块级别导入 `SentenceTransformer`，导致每次运行 pytest/python 都会加载模型（~20s）。日常调试时完全不需要 AI 自愈，白白浪费时间。

### 15.2 实现方案

在 `base.py` 和 `rag_knowledge.py` 中添加环境变量开关：

```python
# base.py
if os.getenv("ENABLE_AI_VISION", "").lower() in ("1", "true", "yes"):
    from ..utils.ai_vision import ai_vision
else:
    ai_vision = None

# rag_knowledge.py
_ENABLE_RAG = os.getenv("ENABLE_AI_VISION", "").lower() in ("1", "true", "yes")

class RAGKnowledgeBase:
    def __init__(self):
        if _ENABLE_RAG:
            from sentence_transformers import SentenceTransformer  # 延迟导入
            self._load_and_index()
        else:
            logger.debug("RAG disabled")
```

### 15.3 使用方式

```bash
# 日常调试（默认，快速启动）
python runner.py testT4718

# 需要 AI 自愈时
ENABLE_AI_VISION=1 python runner.py testT4718     # macOS/Linux
set ENABLE_AI_VISION=1 && python runner.py testT4718  # Windows CMD
```

或在 `.env` 文件中永久设置：
```env
ENABLE_AI_VISION=1
```

### 15.4 影响范围

**所有** python/pytest 命令：
- `python main.py`
- `python runner.py`
- `pytest ...`
- `python tools/diagnose_failed.py`

### 15.5 关闭状态下的行为

- `smart_click` 在 Level 1/2 失败后直接抛出异常（跳过 AI 自愈）
- RAG 知识库不加载（`SentenceTransformer` 不导入）
- `ai_vision` 变量为 `None`，在 `_smart_click_with_fallback` 末尾检查：
  ```python
  if ai_vision is None:
      raise Exception(f"Element not found (AI healing disabled): {target_name}")
  ```

---

## 16. 辅助工具生态

### 16.1 工具总览

| 工具 | 用途 | 典型场景 |
|------|------|---------|
| `diagnose_failed.py` | 失败用例诊断报告 | 测试失败后自动定位根因 |
| `ui_snapshot.py` | DOM 快照 + diff | UI 改版前后对比、检测元素变动 |
| `locator_updater.py` | YAML 定位器批量更新 | UI 文案/组件变更后批量修复 |
| `allure_summary.py` | Allure 报告摘要 | 快速查看测试通过率 |
| `translate_yaml_comments.py` | YAML 注释翻译 | 多语言团队协作 |
| `codegen.py` | Playwright 录制 | 快速录制新用例的交互流程 |
| `http_server.py` | 局域网报告共享 | CI/CD 环境下共享 Allure 报告 |

### 16.2 典型工作流

**UI 改版后的处理流程**:

```
1. 运行测试 → 发现失败
   python main.py

2. 生成诊断报告 → 定位失败原因
   python tools/diagnose_failed.py

3. 如果是定位器变更 → 批量搜索受影响步骤
   python tools/locator_updater.py search --role button --name "旧文案"

4. 预览修改 → 确认后写入
   python tools/locator_updater.py update --role button --name "旧文案" --new-name "新文案" --dry-run
   python tools/locator_updater.py update --role button --name "旧文案" --new-name "新文案"

5. 重新运行验证
   python main.py
```

**预防性 DOM 监控**:

```
1. 建立基线快照
   python tools/ui_snapshot.py snapshot --env release --account main --label baseline

2. 定期或改版后保存新快照
   python tools/ui_snapshot.py snapshot --env release --account main --label current

3. 对比差异
   python tools/ui_snapshot.py check --env release --account main --label current --base baseline
```

---

## 附录: 安全注意事项

以下文件包含敏感信息，已在 `.gitignore` 中排除，**禁止提交到 Git**：
- `cookie_*.json` — 包含真实的认证 Token
- `.env` — 包含 Gemini API Keys
- `ai_healing_screenshots/` — 包含系统截图（可能暴露业务数据）

