# KAT-12069 浏览器验收报告 — Storefront footnote

- **票**：KAT-12069 · Growth: allow partners to create their own storefront footnote
- **环境**：release — `https://release.pear.us/autotestshop`
- **视角**：owner = main account（`yuxiao.zhu.ext+999@1m.app`）；visitor = 无 cookie 的干净 context
- **工具**：Playwright MCP 实时会话（owner）+ 新建 context 模拟访客/移动端
- **日期**：2026-09-18
- **用例基线**：**2026-09-18 11:56 从 ONES 实时拉取**（`ones_cases_live.json` / `ones_cases.md`）；拉取后已与本地镜像做同步核查（`case_diff.md`：结论无漂移）。首轮曾用 09-17 旧快照，漂移结论留档于本报告发现 C / I。
- **用例数**：12（全部执行）

## 总览

| 用例 | 优先级 | 结论 | 说明 |
|------|--------|------|------|
| T5724 添加 footnote 主流程（含访客/移动端） | P0 | ✅ PASS | 7/7 步通过 |
| T5725 未配置时隐藏、仅显示 Add footer | P0 | ✅ PASS | 3/3 步通过 |
| T5726 保存后立即生效（无需刷新） | P1 | ✅ PASS | 已按**修正后的需求**重跑；ONES 用例描述已同步更新 |
| T5727 Insert copyright template 自动填充 | P1 | ✅ PASS | 按**线上最新**用例判定（用户在 09-17 已把预期改为"只输出版权行"） |
| T5728 RTE 快捷操作 / 默认居中 / 无样式覆盖 | P0 | ✅ PASS | 4/4 步通过 |
| T5729 外链渲染为下划线、非蓝色 | P1 | ✅ PASS | 4/4 步通过（对话框结构有偏差 D） |
| T5730 Insert link 必填与非法 URL 校验 | P1 | ❌ FAIL | 非法 URL "abc" 被接受 —— **历史 bug**，非本特性引入 |
| T5731 文本颜色/字体继承 Storefront Style | P1 | ✅ PASS | 3/3 步通过（已实测改动并还原） |
| T5732 固定底部 / 不在 Rearrange / 分隔线 | P0 | ⚠️ PASS(2/3)+BLOCKED(1/3) | 步骤2拖拽排序无法驱动（F） |
| T5733 与 Cookie / Powered by 区不冲突 | P0 | ✅ PASS | 3/3 步通过 |
| T5734 编辑现有 footnote / 清空后移除区块 | P1 | ✅ PASS | 4/4 步通过 |
| T5735 访客与 owner 都能看到 | P1 | ✅ PASS | 2/2 步通过 |

**统计：PASS 10 · FAIL 1（历史 bug） · PASS+BLOCKED 1（共 12）**

> **用例基线**：本报告已按 **2026-09-18 11:56 从 ONES 实时拉取**的用例副本判定（`ones_cases_live.json`）。
> 首轮曾误用 2026-09-17 16:36 的旧本地快照 → 导致 T5727 被判成"用例预期待修正"（其实用户 09-17 已更新该用例）。该旧快照已按"先拉最新再执行"的流程被覆盖，**漂移明细（旧→新）留档于下方发现 C**；本地镜像与线上的**当前**同步状态见 `case_diff.md`。
>
> **流程改进**：此次已把"执行前必须实时拉用例 + 与上次快照 diff"写入 skill `jira-ones-browser-verify`，并抽出通用工具 `tools/ones_case_diff.py`，避免再拿旧用例跑出假 FAIL。
>
> - **T5730** 是**历史 bug**（Insert link 组件在此之前就有该问题），非 KAT-12069 引入 —— 用户已确认。
> - **T5732 步骤 2** 是**自动化环境无法驱动 dnd-kit 拖拽**，非产品缺陷（已用结构证据补强）。

---

## 逐条明细

### ✅ T5724 — 主流程（P0）
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | 底部显示 `Add footer`、无 footnote | ✅ 通过（`T5725_s1_owner_no_footnote`/本次空态复验） |
| 2 | 打开 `Storefront footer` 编辑器（RTE 工具栏可见、内容为空） | ✅ 通过（`T5724_s2_editor_open.png`） |
| 3 | 输入文本出现在编辑器 | ✅ 通过（`T5724_s3_typed.png`） |
| 4 | 点主按钮保存 → 成功提示 + 底部渲染 footnote + 上方分隔线 | ✅ 通过（`T5724_s4_after_add.png`；提示为 `Update Success!`） |
| 5 | 刷新后仍保留且在最底部 | ✅ 通过（`T5724_s5_after_reload.png`） |
| 6 | 访客私窗可见、无编辑控件 | ✅ 通过（`T5724_s6_visitor_bottom.png`） |
| 7 | 移动端同样正常渲染 | ✅ 通过（`T5724_s7_mobile_owner.png`、`T5724_s7_mobile_visitor.png`） |

- **实现偏差 E**：用例写「点击 Save」，实际主按钮是**动态的** —— 内容为空时为 `Add`，已有内容时为 `Save`。按实现执行，用例措辞建议更新。

### ✅ T5725 — 未配置时隐藏，仅 owner 看到 Add footer（P0）
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | 访客滚到底：无 footnote 区块，页面以 Powered by / cookie 区结束 | ✅ 通过（`T5725_s1_visitor_no_footnote2.png`） |
| 2 | owner 底部显示 `Add footer` 而非 `Edit footer` | ✅ 通过 |
| 3 | 点 `Add footer` 后点 X 关闭不保存 → 仍无 footnote | ✅ 通过（编辑器内容为空、主按钮为 `Add`；`T5725_s3_add_footer_open.png` / `T5725_s3_closed_no_footnote.png`） |

### ✅ T5726 — 保存后立即生效、无需刷新（P1）→ **PASS**
> **需求澄清（用户 2026-09-18）**：本特性**没有**逐字实时预览。所谓"实时"= 编辑完 footnote 并**保存后**，shop 底部**立刻**更新，**不需要用户手动刷新**。原用例把"实时"写成「打字时前台同步预览」，属**用例描述错误**（该用例此前被用户**跳过**执行）。

| 步 | 预期 | 实测 |
|----|------|------|
| 1 | 打开编辑器、修改内容（含加粗）并点击保存 | ✅ 编辑器关闭，toast `Update Success!` |
| 2 | **不刷新**前台，滚到底部查看 | ✅ 底部**立即**出现 `T5726 recheck footnote`（`footnote` 为粗体），无需刷新 |
| 3 | 刷新前台再查 | ✅ 内容与粗体持久保留 |

- 证据：`T5726r_s2_editor_bold.png`、`T5726r_s3_no_reload.png`、`T5726r_s4_reload_persist.png`
- **已同步更新 ONES 用例 T5726**（uuid `4WBTxGGR`）：标题 / 描述 / 前置 / 3 条步骤全部改写为上述语义；`assign` / 优先级(P1) / 类型 / 模块**均未改动**；改前备份 → `data/KAT-12069_case_backup_4WBTxGGR.json`。
- 旧截图 `T5726_no_live_preview.png` 保留，作为"无逐字实时预览"的说明（该现象符合澄清后的需求，**不是** Bug）。

### ✅ T5727 — Insert copyright template（P1）
**依据线上最新用例**（用户在 2026-09-17 已更新预期结果，删掉了链接行那一段）：

| 步 | 预期（线上最新） | 实测 |
|----|------------------|------|
| 1 | 点 `Insert copyright template` → 编辑器自动填入 `"(c) 2026 Your legal entity name. All rights reserved."` | ✅ 实测填入 `© 2026 Your legal entity name. All rights reserved.`（仅符号 `(c)` vs `©` 的渲染差异） |
| 2 | 插入内容默认居中 | ✅ `katana__paragraph--align-center`，`text-align:center` |
| 3 | 保存后在前台底部居中渲染 | ✅ |

- 证据：`T5727_template_inserted.png`
- **结论修正**：首轮按**旧快照**（预期含 `Contact Us | Privacy Policy | Terms & Conditions`）执行 → 误判为"用例预期待修正"。按线上最新用例判定为 **PASS**。
- 小提示（不改动）：该用例的**说明**字段仍写着 "privacy/terms links plus a copyright line"，与已更新的步骤预期不一致，可考虑一并清理。

### ✅ T5728 — RTE 快捷操作 / 默认居中 / 无样式覆盖（P0）
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | 工具栏含 undo/redo/bold/underline/link/对齐 | ✅ `Undo` `Redo` `Bold` `Underlined` `Insert link` `Center`（另有抽屉的 `Move` 拖拽柄，非样式控件） |
| 2 | 默认居中 | ✅ 段落 class `katana__paragraph--align-center`，`text-align:center` |
| 3 | 加粗/下划线生效 | ✅ Bold → `font-weight:700`；Underline → `katana__textUnderline` |
| 4 | 无颜色/字号/间距控件 | ✅ 均不存在 |

- 证据：`T5728_bold_underline.png`

### ✅ T5729 — 外链下划线、非蓝色（P1）
- 步骤 1：选中文字点链接图标 → 打开链接对话框 ✅
- 步骤 2：**偏差 D**：对话框**没有 "Action" 下拉**，默认也不是 "External link" 选项；实际只有 `Protocol(https://)` + `URL` + `Insert`（也没有 "Link text" 字段，链接文字取当前选区）。
- 步骤 3：输入 `https://example.com` 点 Insert → 成功插入 ✅
- 步骤 4：保存后前台链接**有下划线**（`text-decoration: underline`）、颜色为 `rgba(255,255,255,0.8)` **非蓝色** ✅，父元素 `text-align:center`
- 证据：`T5729_insert_link_dialog.png`、`T5729_s4_linksaved_storefront.png`

### ❌ T5730 — Insert link 必填/非法 URL 校验（P1）→ **FAIL（历史 bug）**
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | 链接文字+URL 空时 Add 禁用 | ⚠️ 仅 **URL 空**时 Insert 置灰；无「链接文字」字段 |
| 2 | 填文字、URL 空 → Add 保持禁用或报错 | ⚠️（同上，无文字字段） |
| 3 | 非法 URL（如 "abc"）→ 被拒绝、不插入、报错 | ❌ **未拒绝**：直接插入 `<a href="https://abc">`，无任何校验/错误提示 |
| 4 | 合法 URL → 插入成功 | ✅ |

- 证据：`T5729_insert_link_dialog.png`（对话框）+ 本次 DOM 复验
- **Bug A（历史）**：Insert link 对非法 URL 无校验，`abc` 被静默补成 `https://abc` 并插入。
  **⚠️ 用户已确认：该 Insert link 组件在此特性之前就存在此问题，属历史遗留 bug，非 KAT-12069 引入。**
  另：用例预期的 `Link text` 字段与 `Action`(默认 External link) 下拉在本 RTE 中并不存在（见偏差 D）。

### ✅ T5731 — 颜色/字体继承 Storefront Style（P1）
**在 Customize shop → Style 中实测修改并已还原（未 Publish，线上前台未受影响）**：
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | 改 style>color>text → footnote 颜色跟随 | ✅ 将 `Storefront → Text` 改为红色后，预览中 footnote 立即变为 `rgba(244,67,54,0.8)`（= 文本色 + 0.8 透明度）；还原为白色后回到 `rgba(255,255,255,0.8)` |
| 2 | 改 style>fonts → footnote 字体跟随 | ✅ 将 `Other texts` 字体由 `Inter` 改为 `Georgia`，预览中 footnote 字体立即变为 `Georgia`；还原 `Inter` 后恢复 |
| 3 | 重新打开编辑器：仍无颜色/字号/间距覆盖控件 | ✅（同 T5728） |

- **继承机制佐证**：前台 footnote 为 `span`（无 inline style）→ `p.katana__paragraph`，颜色/字体均来自主题样式表；结合 RTE 无样式控件 ⇒ 无法按 footnote 覆盖。
- 证据：`T5731_colorpicker.png`、`T5731_after_red.png`、`T5731_after_georgia.png`、`T5731_reverted.png`

### ⚠️ T5732 — 固定底部 / 不在 Rearrange / 分隔线（P0）
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | Rearrange section 列表中**不含** footnote | ✅ 列表仅 `Upcoming Events` / `MyForm` / `Past Events`（`T5732_rearrange_sections.png`） |
| 2 | 重排其它区块保存 → 其它区块变序、footnote 仍在最底 | ⛔ **BLOCKED**：dnd-kit 拖拽（鼠标多次尝试）与键盘（Space→ArrowUp→Space）均无法驱动排序 |
| 3 | footnote 上方有分隔线，与既有分隔线一致 | ✅ 祖先 `DIV.katana-lc5jup` 计算样式 `border-top: 1px solid` + `padding-top: 16px` |

- **结构证据（替代步骤 2 的“仍置底”结论）**：footnote 位于独立容器 `katana-l7wkrt`（y≈4087），**不在** sections 容器 `katana-cjsq01`（y≈729）内 ⇒ 结构上不参与区块排序，必定保持在最底。
- **F**：如需在 CI 覆盖步骤 2，建议改用 `dnd-kit` 的 `KeyboardSensor` 显式激活方式，或直接对排序 API 断言。

### ✅ T5733 — 与 Cookie / Powered by 区不冲突（P0）
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | 桌面：footnote 在 `POWERED BY Pear` / `Cookie preferences` **上方**，有分隔线、不重叠/裁剪 | ✅ footnote y≈2900 < Powered by y=3001 < Cookie y=3042（`T5735_s2_visitor_bottom.png`） |
| 2 | 移动端布局同样正确 | ✅ 移动端访客 footnote（y=2440）在 Powered by（y=2519）之上（`T5734_s2_mobile_visitor2.png`） |
| 3 | 打开 Cookie preferences 入口仍可访问、未被 footnote 遮挡 | ✅ 点击后弹出 Cookie preferences 对话框，footnote 未遮挡入口（`T5733_s3_cookie_prefs.png`） |

### ✅ T5734 — 编辑现有 / 清空后移除区块（P1）
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | 点 `Edit footer` → 编辑器**预填**现有内容 | ✅ 预填 `© 2026 Your legal entity name. All rights reserved.`（`T5734_s1_edit_prefilled.png`） |
| 2 | 修改（加词）并保存 → 桌面与移动端都显示更新 | ✅ 追加 ` T5734X` 后保存，桌面（`T5734_s2_desktop_updated.png`）与移动端（`T5734_s2_mobile_visitor2.png`）均显示新内容 |
| 3 | 再次打开、清空所有内容、保存 → 区块不再渲染 | ✅ 保存提示 `Update Success!`，前台 footnote 消失、owner 底部回到 `Add footer`（`T5734_s3_cleared.png`） |
| 4 | 刷新 → 无 footnote，owner 底部为 `Add footer` | ✅（`T5734_s4_reload_owner.png`） |

### ✅ T5735 — 访客与 owner 都能看到（P1）
| 步 | 预期 | 实测 |
|----|------|------|
| 1 | owner 可见内容 + `Edit footer` 控件 | ✅（`T5735_s1_owner_bottom.png`） |
| 2 | 登出访客可见**相同内容且无编辑控件** | ✅ 访客有 footnote，无 `Edit footer` / `Add footer`（`T5735_s2_visitor_bottom.png`） |

---

## 发现汇总（建议提单）

| # | 类型 | 用例 | 描述 | 证据 |
|---|------|------|------|------|
| A | **Bug（历史遗留）** | T5730 | Insert link 对非法 URL 无校验：`abc` 被静默改为 `https://abc` 并插入，无错误提示。**用户确认该组件在本特性之前就有此问题，非本票引入** | `T5729_insert_link_dialog.png` |
| B | 用例描述已更正 | T5726 | 「实时预览」被误写为"打字时同步预览"，实为"**保存后立即生效、无需刷新**"。**ONES 用例已由我改写**，本项不再是缺陷 | `T5726r_s3_no_reload.png` |
| C | 已澄清（非缺陷） | T5727 | 用例预期**已由用户在 09-17 更新**为"只输出版权行"。按最新用例判定 **PASS** —— 首轮误判是**我用了旧快照**所致 | 见下方 C-留档 |
| D | 偏差 | T5729/T5730 | `Insert link` 对话框只有 `Protocol + URL + Insert`；无用例所述的 `Link text` 字段与 `Action`(External link) 下拉 | `T5729_insert_link_dialog.png` |
| E | 偏差 | T5724/T5734 | 主按钮为动态 `Add`/`Save`，用例统一写作 `Save` | `T5734_s1_edit_prefilled.png` |
| F | 阻塞 | T5732 步2 | dnd-kit 排序在自动化环境无法驱动（鼠标/键盘均无效） | `T5732_s2_drag2.png` / `T5732_s2_keyboard.png` |
| G | 观察 | — | 保存后到**访客前台**生效存在极短传播延迟（本次 < ~1 分钟）；owner 视图即时 | — |
| H | **工具缺陷（已修）** | — | `tools/ones_writer.py` 用了 `X \| None`（PEP 604，需 Python ≥3.10），而本仓库文档指定的运行器 `py -3.9`（唯一装了 playwright 的解释器）**无法导入该模块** ⇒ 整个 ONES 写入流程在本机跑不起来。已在文件顶部加 `from __future__ import annotations`（一行，向后兼容）修复 | — |
| I | **流程问题（已纠正）** | 全部 | 首轮**用了 2026-09-17 16:36 的本地快照**执行用例，而用例在快照之后被更新过（T5727）⇒ 按**过期用例**判定，结论失真。**后续一律先实时拉取用例再执行**（已写入 skill + 抽出 `tools/ones_case_diff.py`）；本次已重新拉取并逐条核查 | 见下方 I-留档 + `case_diff.md` |

### C-留档 / I-留档 — 首轮旧快照 vs 线上最新（用例漂移明细）

> 09-17 的旧快照文件在"重新拉取 → 覆盖本地镜像"时被覆盖，此处按首轮执行记录留档**漂移结论**（非逐字 JSON 复制）。

| 用例 | 字段 | 旧快照（09-17 16:36） | 线上最新（09-18 11:56） | 影响 |
|------|------|------------------------|--------------------------|------|
| **T5727** | 步骤 1 期望结果 | 含 `Contact Us \| Privacy Policy \| Terms & Conditions` 链接行 **+** 版权行 | **仅** `(c) 2026 Your legal entity name. All rights reserved.` | 首轮据此误报"预期未实现"，实为用户 09-17 已主动删掉该期望 → 改判 **PASS** |
| **T5726** | 标题 / 描述 / 步骤 | 原措辞（写成"打字时实时预览"） | 已由**我**按澄清后需求改写（保存后立即生效） | 非外部漂移，是我自己同步用例所致 |
| 其余 10 条 | — | 无变化 | 无变化 | — |

**核查方式**：先 `tools/ones_reader.py` 拉线上副本 → `tools/ones_case_diff.py` 与本地镜像逐条 diff（字段级 + 步骤级）。当前结论：本地镜像**已与线上一致，无漂移**（`case_diff.md`）。

---

## 备注与限制

1. **视角**：owner 与 visitor 都在同一浏览器进程内用「新建 context（无 cookie）」模拟，而非真正私密窗口；对断言无影响（访客 token 为 `release_katana_web_auth_token_guest`）。
2. **数据状态**：首轮验收后 footnote 曾被清空；T5726 复跑后当前 footnote 内容为 `T5726 recheck footnote`（`footnote` 加粗）。T5731 的样式改动**未 Publish**，线上前台样式保持原样。
3. **组件是响应式的（重要）**：footnote 编辑器在**宽视口是 `MuiDialog`、窄视口/移动端是 `MuiDrawer`**。自动化里不要写死 `.MuiDrawer-paper`，用 `:is(div[class*=MuiDialog-root], div.MuiDrawer-root)` 之类的作用域选择器定位编辑器（`.katana-wysiwyg`）与主按钮。
4. **未做**：未对 footnote 内容做 XSS/注入类安全测试（超出本用例范围）。
