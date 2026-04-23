# Autotest-monster Actions 模块文档

本文档基于 `__init__.py` 文件提取，详细说明了测试框架中支持的所有动作指令及其匹配机制。

## 1. 核心路由机制 (`get_action`)

框架在解析 YAML 用例时，会通过 `get_action(name)` 函数来寻找对应的底层执行方法。该函数采用了 **双层匹配策略**：

1. **精确匹配 (Exact Match)**：首先在 `ACTIONS` 字典中查找完全一致的键名。如果匹配成功，直接返回对应的处理函数。
2. **前缀匹配 (Prefix Mapping)**：如果精确匹配失败，会按照定义好的前缀规则（`name.startswith(...)`）进行模糊匹配。这使得类似于 `click_login_button` 或 `verify_user_name` 这样的动态命名能够自动路由到 `smart_click` 或 `verify_text_visible` 等通用方法上。

---

## 2. 基础交互动作 (Base Interactions)

这些动作涵盖了最常见的浏览器交互，通过前缀映射或精确名称调用：

| 动作前缀/名称 | 绑定的底层方法 | 说明 |
| :--- | :--- | :--- |
| `open` | `open_url` | 打开指定的 URL |
| `click`, `R_click`, `l_click` | `smart_click` | 智能点击，支持快速定位，不触发页面级全量扫描 |
| `fill` | `smart_fill` | 智能文本输入 |
| `fill_numeric` | `fill_numeric` | 专门用于数字类型的输入 |
| `check`, `uncheck` | `smart_check` | 勾选或取消勾选复选框/单选框 |
| `swipe`, `scroll` | `smart_swipe` | 页面滑动或元素内滚动 |
| `press` | `smart_press` | 键盘按键操作 (如 Enter, Escape) |
| `sleep` | `smart_sleep` | 显式等待（强制休眠） |
| `upload`, `wait_for_upload` | `smart_upload` | 文件上传操作 |
| `screenshot` | `smart_screenshot` | 智能截图 |
| `if_` | `smart_if` | **YAML 条件执行分支**，支持根据条件判断执行不同的动作流 |

---

## 3. 验证与断言动作 (Verifications)

所有以 `verify_` 开头的操作，主要用于测试用例的结果检查：

| 动作前缀/名称 | 绑定的底层方法 | 说明 |
| :--- | :--- | :--- |
| `verify` (通用前缀) | `verify_text_visible` | 验证指定文本或元素是否可见 |
| `verify_hidden` | `verify_text_hidden` | 验证指定文本或元素是否被隐藏 |
| `verify_value` | `verify_value` | 验证元素的特定值 |
| `verify_toast` | `verify_toast_message` | 验证全局提示框（Toast）的文本内容 |
| `verify_no_sibling` | `verify_no_sibling_text` | 验证不存在特定的兄弟节点文本 |
| `verify_element_style` | `verify_element_style` | 验证元素的 CSS 样式 |
| `verify_child_element_count`| `verify_child_element_count` | 验证子元素的数量 |

---

## 4. 进阶与系统控制 (Advanced & System)

涉及会话管理、弹窗处理以及页面状态等待的操作：

| 动作前缀/名称 | 绑定的底层方法 | 说明 |
| :--- | :--- | :--- |
| `create_session`, `session_`| `create_session` | 创建新的浏览器会话上下文 |
| `switch_session` | `switch_session` | 在多个会话之间切换 |
| `close_session` | `close_session` | 关闭当前会话 |
| `handle_modal` | `handle_modal` | 手动处理特定的弹窗 |
| `auto_handle_modals` | `auto_handle_modals` | 自动处理页面上的常见弹窗 |
| `wait_for_selector` | `wait_for_selector` | 等待特定的 DOM 元素出现 |
| `wait_for_url`, `verify_navigation`| `wait_for_url` | 等待页面导航至特定 URL |
| `wait_` (通用前缀) | `smart_wait` | 智能等待 |

---

## 5. 特色机制：智能扫描点击 (`smart_click_scan`)

- **触发关键字**: `R_click_scan`, `click_scan`
- **绑定的方法**: `smart_click_scan(page, v)`
- **核心说明**: 
  这是 `smart_click` 的完整兜底版本，内部强制启用了 `fallback_scan=True`。它会触发 **Page-level Search（页面级扫描）和 AI 兜底定位**。
- **推荐场景**: 
  适用于传统的基于选择器难以定位的复杂场景，如：弹窗嵌套、多层 Drawer、元素被外层容器严重遮盖等。普通情况建议直接使用 `click` 以保证执行速度。

---

## 6. 业务专属动作 (Business Domain Actions)

框架中针对特定的业务模块（Product, Form, Layout 等）封装了大量专属方法：

### 模块/组件操作 (Module)
- `click_module_edit_button`: 点击模块编辑按钮
- `click_add_new_product`: 点击添加新产品
- `click_module_collapse` / `expand`: 折叠或展开模块
- `drag_element` / `drag_and_drop_by_coordinates`: 元素拖拽操作

### 产品与社交操作 (Product & Social)
- `click_product_image`: 点击产品图片
- `verify_post_exists`: 验证动态是否存在
- `R_click_follow`: 智能关注操作
- `select_replacement_product`: 选择替换产品 (映射了 `select_a_for_b` 等语法)

### 表单与布局操作 (Form & Layout)
- `verify_submission_details`: 验证表单提交详情
- `download_submission_csv` / `verify_csv_data`: CSV 报表下载与数据验证
- `goto_storefront`: 跳转到 Storefront (包含 waterfall 等特定布局后缀)
- `publish_button_click`: 点击发布按钮并处理相关流转
