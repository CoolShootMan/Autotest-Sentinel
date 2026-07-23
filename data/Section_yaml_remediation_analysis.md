# Section.yaml 剩余用例修复分析（2026-07-23）

> 目标：在动手改下一个用例之前，先把剩余用例理清楚——哪些**能一起修**（共享根因），哪些存在**因果/数据依赖**（不能孤立跑）。
> 重构背景：storefront module 上周重构为 section，旧 DOM 结构失效，导致全文件 module/section 用例大面积挂。

## 0. 总览

- 文件共 **28 个顶层用例**（含组合用例如 `testT4600_4602`、`testT5210_5211_5212`）
- 已修复 **5 个**：`testT3554`(加) / `testT3556`(改) / `testT3577`(排序) 由用户修；`testT4903`(隐藏badge) / `testT4622`(折叠展开) 由我修
- **剩余 23 个全部需要重构复核**，其中：
  - **4 个标 `[PASSED 2026-05-06]`**：`testT3555`、`testAddNewUpdateSection`、`testT4556`、`testT4853` —— 是**重构前过的 stale-pass**，现在几乎必然也挂了，不能当"已通过"
  - **1 个标 `[FAILED 2026-05-06]`**：`testT4603`
  - **18 个标 `[BROKEN 2026-05-06]`**

---

## 1. 能一起修的（共享同一根因 / 同一 locator 模式）

### Group A — `verify_child_element_count` 的 `child_locator` 脆性（最大的一块，6 个用例）

这 6 个用例全部用同一个断言模式数 section 内卡片数量：
```yaml
verify_child_element_count: { container: 'X', parent_locator: '..', child_locator: '+div>div>div:nth-child(2)>div', expected: N }
```
重构后 section body 的 DOM 结构变了，`+div>div>div:nth-child(2)>div` 这个相对路径定位不到 → 全部超时或计数错。

| 用例 | expected | 备注 |
|------|----------|------|
| `testAddNewPost` | 1 / 2 | 两处断言 |
| `testT3788` | 3 | partner 产品 section |
| `testT3886_long` | 1 | YouTube 视频 |
| `testT3886_short` | 1 | Tiktok 短视频 |
| `testT4852` | 9 | 混合内容 |
| `testT4605` | 2 | 帖子去重 |

**修法**：只要摸清楚重构后"section 内容卡片列表"的真实 DOM，改这一个 `child_locator` 就能一把修 6 个（可能各用例路径微差，但根因相同，可批量对照）。`verify_child_element_count` 是 `module.py:716` 单点实现，无需改代码。

### Group B — `verify_element_style` / `verify_element_contains_text` 的 `container_filter: '../..'`（CSS/文本断言脆性）

与 T4903 老问题同源：靠相对祖先路径 + CSS 属性找元素，重构后易失效。建议优先改成"文字/结构断言"而非 CSS 属性。

| 用例 | 断言 | 风险 |
|------|------|------|
| `testT5210_5211_5212` | 3× `verify_element_style` 查 `.link_title` 的 `textAlign` | 与 T4903 同源，CSS 属性最脆 |
| `testT4264` | `verify_element_contains_text` `../..` | 文本断言，稍稳 |
| `testT4908` | `verify_element_contains_text` `../..` | 文本断言 |
| `testT5105` / `testT4853` | `verify_element_contains_text` `../..` | 文本断言 |

### Group C — Music section 新增流（2 个用例）

`testT4660`（加 track + 删）与 `testT4816`（加 streaming 链接）都走 `Add storefront section → Music 类型 → 填 track/service`。两条可对照修，公共段一次验证通。

### Group D — Link 卡片类型组（General Link / Product / Image / Video / Ticket-Event）

都走 `Add section → 选 link 子类型 → 加卡片`。"加 section + 选类型"前半段几乎一致，可先把公共创建段验证通，再逐个看卡片填表逻辑：

- **General Link**：`testT3843`(加链接) / `testT4600_4602`(carousel 导航) / `testT5210_5211_5212`(对齐)
- **Product link**：`testT3842`
- **Image link**：`testT4264`
- **Video**：`testT3886_long`(YouTube) / `testT3886_short`(Tiktok)
- **Ticket/Event**：`testT3841` (+ 依赖用例 `testT4908`)

---

## 2. 因果关系 / 数据依赖（不能孤立跑）

### 2.1 硬依赖（下游用例不建数据，直接吃上游用例产出的 section / 数据）

1. **`testT3789` → `testT3788`**
   - `testT3789` 直接购买 "Section-products" section（含 2 个 product），**自己不建 section**。
   - `testT3788` 不过 / 数据没留下 → `testT3789` 必挂。
   - 必须配对跑：`testT3788` 先成功并保留数据，再跑 `testT3789`。

2. **`testT4908` → `testT3841`**
   - 文件内注释明确写 *"This use case relies on T3841"*。
   - `testT4908` 验证 "Test Ticket Event section"（T3841 建的）里的日期时区，**自己不建 section**。
   - 必须 `testT3841` 先成功并保留该 section，再跑 `testT4908`。

3. **`testT4853` → `testAddNewUpdateSection`**（软依赖）
   - `testT4853` 创建事件 post 时选 "new section use in archiving test cases"（由 `testAddNewUpdateSection` 建的）作为归档目标。

4. **`testT4559` → `testAddNewUpdateSection`**（软依赖）
   - `testT4559` 断言事件 post **不在** "new section use in archiving test cases"。

### 2.2 共享种子数据依赖（多个用例吃同一份预置数据，预置缺失则一起挂）

| 预置数据 | 被依赖用例 | 说明 |
|----------|-----------|------|
| 帖子 **"auto test T3788"** | `testT3788`、`testT4852` | 两用例都从 "Add from my posts" 选它，必须预置在账号里 |
| 产品 **"test_general_products"** / **"autotest product title - do not delete"** | `testT3788` | 断言可见，需预置 |
| **"Upcoming Events"** section + post **"verify-co-seller-auto-archive"** | `testT5105` | 直接引用，需预置（非本文件用例产出） |

### 2.3 共享全局状态依赖（操作同一个全局开关，顺序会互相干扰）

- **auto-archive 开关**（`events/settings` 的 `autoArchive`）：`testT4556` / `testT4853` / `testT4559` / `testT5105` 都操作同一个 toggle（且都是点两次翻转）。
- 并发或多用例连跑会互相覆盖状态 → 这组建议**串行跑**，且每个用例自己保证开关终态正确（或加 reset 步骤）。

### 2.4 自清理、无外部依赖（可独立跑，风险最低）

| 用例 | 自清理方式 |
|------|-----------|
| `testT4600_4602` | 自建 'test nav buttons' + `teardown_step` 删除 ✓ |
| `testT4660` | 自建 Music section + 自己删除 ✓ |
| `testT4605` | 自建 'post duplicate section' + `teardown_step` 删除 ✓ |
| `testT3555` | 建 post + 删 section，但**不清理 post**（会在 shop 留垃圾，不过不依赖别的用例） |

---

## 3. 建议修复顺序

1. **先打通公共删除段**：用 `testT3555`（delete）把"加 section → 删 section"生命周期跑通。delete 通了，所有"自建+自删"用例（T4600_4602 / T4660 / T4605）的删除段就稳了。
2. **Group A 一把修**：摸清新 section body DOM，改 `child_locator` → 一次修 6 个 count 断言。
3. **Link 卡片组（Group D）逐个类型过**：从 General Link（`testT3843`）起，不带 count 断言、最简单；再 Product / Image / Video / Ticket-Event。
4. **硬依赖链配对跑**：`testT3788`→`testT3789`、`testT3841`→`testT4908`，必须上游成功并保留数据。
5. **Archiving 组（共享开关）最后**：串行 + 注意 `autoArchive` 开关终态。

---

## 4. 待确认事项（修之前）

- [ ] `testT3555` 现在的失败点具体在哪一步？（你之前说"接下来修 T3555"，但它本身标的是 stale-PASSED，需先复跑定位）
- [ ] Group A 的新 `child_locator` 需一次 DOM 摸排（哪个元素承载 section 卡片列表）
- [ ] 种子数据是否还在：`auto test T3788` 帖子、`test_general_products` 产品、`Upcoming Events` section
- [ ] `module` → `section` 关键字：文件/文件夹层已改，代码层 `module_name` / `click_module_*` / `module.py` 保持原样（框架已注册 `click_section_*` 别名兼容），**本次分析不涉及改名**
