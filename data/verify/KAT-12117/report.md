# KAT-12117 允许每条 Post 自定义联系邮箱 — 浏览器功能验证报告

## 1. 信息

| 项 | 值 |
|----|----|
| Jira | [KAT-12117](https://pearshop.atlassian.net/browse/KAT-12117) — Operation: allow every post to customize the contact email（Subtask / 进行中 / QA: Yuxiao Zhu / due Sep 18, 2026） |
| 关联票 | [KAT-12124](https://pearshop.atlassian.net/browse/KAT-12124) — 缺陷票「关闭开关后 Save 报 `contactEmail must be an email`」（提单：Yuxiao Zhu）= C3 的失败；[KAT-12123](https://pearshop.atlassian.net/browse/KAT-12123) — 缺陷票「转售贴应继承 Use a different contact email」（待办 / Assignee: Jiaqi Yu）= C4 的失败 |
| ONES 用例来源 | 计划 [`UjmD4hzp`](https://ones.cn/project/#/testcase/team/T7u1zXum/plan/UjmD4hzp/library)（新建模块 `Contact email` = `RyKqbvvV`，共 5 条） |
| ONES 执行状态 | **已回写**：计划 `UjmD4hzp` = `passed=3 / failed=2`（不再显示「未执行」）；回写工具 `tools/ones_plan_result.py`，数据 `data/verify/KAT-12117/ones_results.json` |
| 环境 | release — `https://release.pear.us`（API `release.katana-api.1m.app`） |
| 执行视角 | owner（`+999` / autotestshop）＋ co-seller（`+998` / autotest-coseller）＋ 访客 |
| 需求依据 | Jira description（To do 两条）+ 评论 [2026-09-17 Yizhen Xin] 的 Figma 链接 |
| 设计依据 | Figma `mB8sz3XLgI3BgJHh1U3198` node `29241-13120` → `data/figma_KAT-12117/analysis.md` + 21 张截图 |
| 执行时间 | 2026-09-18 15:53–16:12 (GMT+8) |
| 操作路径 | `data/verify/KAT-12117/path_map.md` |
| 证据说明 | 本目录下的 `C*_s*.png` 为**当前有效**证据；`superseded/` 内 4 张是早期口径作废的截图（保留以便追溯，不要引用） |

## 2. 需求口径（从票提炼）

- **一句话需求**：Post 的 Settings 里新增一个 advanced setting，可把 post 底部展示的联系邮箱改成自定义邮箱（默认跟 Business settings 的 customer support email）。
- **业务规则**：
  1. 开关项 `Use a different contact email`，默认 Off；开启后齿轮图标出现，可在弹窗里填邮箱。
  2. 邮箱格式必须是合法邮箱。
  3. Co-selling post 从父 post **derive（继承）**该设置；但 co-selling post **可以单独自定义**联系邮箱。
- **范围外（本轮未覆盖）**：真实收信验证链路（收信 → 点链接 → `I've verified`）依赖真实邮箱，自动化无法闭环。
- **验收口径 checklist**：
  1. ✅ 开关可开启、可配置合法邮箱并保存，前台底部显示该自定义邮箱
  2. ✅ 非法格式被拒（Update 不可用）
  3. ❌ 关闭开关可保存并回退到 Business settings 邮箱
  4. ❌ 转售贴继承父贴的 contactEmail
  5. ✅ co-seller 可独立改转售贴邮箱且不影响父贴

## 3. 结论摘要

| 指标 | 数量 |
|------|------|
| 用例总数 | 5 |
| 已执行 | 5 |
| PASS | 3 |
| FAIL | 2 |
| BLOCKED | 0 |
| SKIP（用例过时 / 不适用） | 0 |
| 未执行 | 0 |

> 3 + 2 = 5，与下方明细行数一致。

**一句话结论**：owner 侧「开启 + 配置 + 前台展示」主流程可用；但**关闭开关无法保存**（已提 [KAT-12124](https://pearshop.atlassian.net/browse/KAT-12124)），且**转售贴不继承父贴设置**（= 已提的 KAT-12123，同一根因：co-sell 接口未带主贴 advanced settings）。

## 4. 用例明细

| 用例 ID | 用例名 | 结论 | 证据 | 备注 |
|---------|--------|------|------|------|
| `Ds8QUXpQ` | Verify organizer can set a custom contact email for a post and customers see it at the post bottom | **PASS** | `C1_s1_post_settings_panel.png` / `C1_s3_email_dialog.png` / `C1_s4_post_bottom_custom_email.png` / `C1_s5_guest_bottom_custom_email.png` | 设 `kat12117-owner@1m.app`，owner 与访客前台底部均显示该值（Business 默认是 `test@pear.us`，两者不同 → 对比有效） |
| `JPioSgHX` | Verify an invalid email format is rejected in the 'Use a different contact email' dialog | **PASS** | `C2_s1_invalid_abc_update_disabled.png` / `C2_s3_invalid_space_update_disabled.png` / `C2_s4_valid_update_enabled.png` | `abc` / `abc@` / `a b@c.com` 三种非法值 `Update` 均 `disabled`；合法值恢复可用 |
| `7UdpmKjo` | Verify turning the contact email switch off restores the Business settings customer support email | **FAIL** | `C3_s1_switch_off_gear_gone.png` / `C3_s2_save_error_contactEmail_must_be_an_email.png` | 见 §5.1，**新 bug** |
| `4ZmiXCrP` | Verify a co-seller resale post inherits the 'Use a different contact email' setting from the original post | **FAIL** | `C4_s2_added_to_shop_dialog.png` / `C4_s3_resale_post_settings_contactEmail_off.png` | 见 §5.2，**= KAT-12123** |
| `5wZH1Hhx` | Verify a co-seller can customize the contact email on the resale post without affecting the original post | **PASS** | `C5_s1_resale_email_dialog.png` / `C5_s2_resale_switch_on_after_update.png` / `C5_s3_resale_post_bottom_email.png` | ⚠️ **带前置偏差**：因 C4 bug，转售贴起始为 Off（非继承的 X），co-seller 自行开启并设 `kat12117-coseller@1m.app`，保存成功、前台显示正确、父贴未被改动 → 业务规则本身成立 |

## 5. 失败详情

### 5.1 `7UdpmKjo` — 关闭开关后无法保存（**已提票 KAT-12124**）

- **复现步骤**（环境 release / 账号 owner `yuxiao.zhu.ext+999@1m.app`）：
  1. 打开 `/autoshop` 父贴 → Post settings（`/post/0916aead-3496-4773-90fb-1f04adcdaba0/settings`）
  2. `Use a different contact email` 开关置 **Off**（齿轮图标随之消失 —— 这一步 UI 正常）
  3. 点 `Save`
- **实际观测**：
  - 出现表单错误 ``contactEmail must be an email``（`.MuiFormHelperText-root`），**没有** `Post settings updated` toast；
  - 页面重载后开关**又变回 On**（`input[name=contactEmail].checked === true`），且**未发出** `PATCH /posts/curator/<id>/advanced`；
  - 前台 post 底部仍显示自定义邮箱 —— 即"关掉自定义邮箱"这个操作**永远无法生效**。
- **预期结果**：保存成功（toast `Post settings updated`），前台底部回退为 Business settings 的 `test@pear.us`。
- **初步归属**：**后端 + 前端契约**。开关为 Off 时前端把 `contactEmail` 作为**空字符串**提交，后端按"邮箱格式"校验拒绝；Off 语义应是 `null` 或不下发该字段。对比：开关为 On 且已填合法邮箱时保存成功（PATCH 200）。
- **归属状态**：**已提单** → [KAT-12124](https://pearshop.atlassian.net/browse/KAT-12124)「After turning it to "Off", the "Save" function reports that "contactEmail must be an email"」（Reporter: Yuxiao Zhu）。
- **原始复现说明（提单时使用）**：
  > 环境：release，账号 owner（yuxiao.zhu.ext+999@1m.app），post `0916aead-3496-4773-90fb-1f04adcdaba0`（/autotestshop/post/auto-test-post-setting-t1742）
  > 步骤：Post settings → 把 `Use a different contact email` 关到 Off → Save
  > 实际：提示 `contactEmail must be an email`，保存失败；重载后开关回到 On，值仍是自定义邮箱
  > 预期：保存成功并回退到 Business settings 的 support email（test@pear.us）
  > 证据：`C3_s2_save_error_contactEmail_must_be_an_email.png`；该 PATCH 未发出
  > 推测：Off 时前端提交 `contactEmail: ""`，后端把空串当非法邮箱拒绝，应改为 `null`/省略

### 5.2 `4ZmiXCrP` — 转售贴不继承父贴设置（**= KAT-12123，票面描述已补全**）

- **复现步骤**：
  1. owner 在父贴开启 `Use a different contact email` 并配置自定义邮箱（父贴 `contactEmail` 有值）
  2. 切 co-seller（`+998`）打开父贴 → 点 `Add to shop` → 在 "This post has been added to your shop." 弹窗点 `Save`
  3. 打开转售贴的 Post settings（`/post/7af9d810-1ed7-429c-a532-ea2f760e49e6/settings`）
- **实际观测**：
  - 转售贴 `input[name=contactEmail].checked === false`（**Off**），齿轮图标不存在；
  - 接口 `GET /posts/curator/preview/7af9d810-…` 返回 **`contactEmail: null`**，而 `parentPostId = 0916aead-…`（确认是子贴）；
  - 父贴同一时刻 `contactEmail` 为自定义邮箱 → **未继承**。
- **预期结果**：转售贴 `contactEmail` 应等于父贴的值，开关为 On。
- **根因**（**后端 / 接口**）：co-sell（`Add to shop`）**接口没有把主贴的 advanced settings 带过来**。转售贴是按"转售创建那一刻的设置快照"建的，而这份快照里**没有这个字段的数据** → `contactEmail = null`。
  → 因此**同一个根因**同时导致两个可观测现象：
  1. 转售贴自己的 Post settings 开关为 Off、前台底部回退到 Business settings 的 support email；
  2. **co-seller 登录态下看到该 post 底部也是 Business settings 的值**，而不是帖子配置的自定义邮箱（见 §7 —— 这一条已不再列为"未解释的发现"，它就是本 bug）。
- **票面已更新**：KAT-12123 的描述已补全 `Environment` / `Preconditions` / 完整 Reproduce Step / `Actual Result` / `Root cause` / `Impact`（原描述只有 2 步 + 空 Actual Result + 一张截图，截图已保留）。
- **给开发的复现说明**：
  > 环境：release，owner `+999`（autotestshop）/ co-seller `+998`（autotest-coseller）
  > 父贴：`0916aead-3496-4773-90fb-1f04adcdaba0`，contactEmail 已设为自定义值
  > 步骤：co-seller 打开 /autotestshop/post/auto-test-post-setting-t1742 → Add to shop → 弹窗 Save
  > 实际：子贴 `7af9d810-1ed7-429c-a532-ea2f760e49e6`（parentPostId=0916aead-…）的 `contactEmail = null`，开关 Off，后台底部回退为 test@pear.us
  > 预期：子贴继承父贴的 contactEmail（开关 On）
  > 证据：`C4_s3_resale_post_settings_contactEmail_off.png`；`/posts/curator/preview/7af9d810-…` 响应 `contactEmail: null`

## 6. 与票 / 设计的偏差

| 类型 | 对象 | 说明 | 处理 |
|------|------|------|------|
| 实现与需求不一致 | C3（关闭开关） | 需求未显式写关闭路径，但开关存在即隐含可关；实测**关不掉** | **已提 bug**：[KAT-12124](https://pearshop.atlassian.net/browse/KAT-12124)（§5.1） |
| 实现与需求不一致 | C4（继承） | 票面写 "Co-selling post should derive this setting from the parent post"；根因 = co-sell 接口未把主贴设置带过来 | **= KAT-12123**，票面描述已补全（§5.2） |
| ~~实现与设计不一致~~ → **已确认为范围外** | C1 step4 | 设计稿画了 `Verify your new email` 校验弹窗（`We've sent a verification email…` + `Resend in 59s` + `I've verified`）；实测点 `Update` 后弹窗直接关闭、无校验弹窗 | **不是偏差，不提票**。Jira 评论已明确该验证步骤**超出本期需求范围**，本期不做 |
| 未覆盖（设计有、用例无） | — | 设计稿移动端 375 宽；实测的是桌面视口 | 见 §7 |

## 7. 未覆盖与风险

- **真实邮箱验证链路（本期范围外，非缺陷）**：设计稿画了 `Verify your new email` 弹窗，但 Jira 评论已明确**超出本期需求范围**，本期不实现 → 不计为偏差、不提票。因此"无法真实收信并点 `I've verified`"不构成未覆盖项。
- **前台邮箱随"浏览者身份"变化 → 已归因，并入 KAT-12123，不再是"未解释的发现"**：同一个父贴，
  - owner 视角：显示 owner 设的自定义值 ✅
  - 访客（清 cookie）视角：显示 owner 设的自定义值 ✅
  - **co-seller 登录态视角：显示 `test@pear.us`（Business settings 默认），不是 owner 设的自定义值** ❌
  证据：`C1_s5_guest_bottom_custom_email.png`（访客）vs `C4_s1_coseller_view_original_footer.png`（co-seller）。
  **归因**：与 C4（§5.2）**同一根因** —— co-sell 接口未把主贴的 advanced settings 带到转售侧，转售侧渲染时拿不到该字段 → 回退到 Business settings 的 support email。
  （补充说明：`test@pear.us` 恰好同时等于父贴创建者与 co-seller 自己的 Business support email，就"具体回退到了谁的值"这一点无法从数据上区分；但"co-seller 看到的是 Business 默认而非帖子配置值"与 KAT-12123 的根因一致。）
- **移动端视口未测**：设计稿为 375 宽，本轮只跑桌面视口。
- **⚠️ 数据漂移（并发改动）**：执行期间父贴被**外部**改动 —— `updatedAt 2026-09-18T08:04:06Z`，`contactEmail` 从 `kat12117-owner@1m.app` 变成 `kat12117-new@1m.app`（非本次操作）。C5「父贴未被改动」的结论按"父贴值 ≠ co-seller 设的 Y"判定仍成立，但父贴最终值以实时数据为准。
- **未回归的相邻流程**：含 post 的邮件通知/订单确认邮件是否与 contactEmail 联动，未测。

## 8. 后续

- [x] **回写 ONES 执行结果**：已完成 —— 计划 `UjmD4hzp` 现为 `passed=3 / failed=2`（不再有「未执行」）；备注见各用例 note，工具 `tools/ones_plan_result.py`，数据 `ones_results.json`
- [x] **C3 提新 bug**：已完成 → [KAT-12124](https://pearshop.atlassian.net/browse/KAT-12124)（Reporter: Yuxiao Zhu）
- [x] **补全 KAT-12123 描述**：已完成 —— 补齐 Environment / Preconditions / Reproduce Step / Actual Result / Root cause / Impact，原截图保留；工具 `tools/jira_writer.py`，内容 `data/verify/KAT-12117/KAT-12123_description.md`
- [ ] 转 YAML 自动化（`test_case/UI/Test_Katana/All_YAML/Post/Post_setting.yaml`）：C1 / C2 / C3（C4/C5 依赖 KAT-12123 修复后再补）
- [ ] 清理测试数据：co-seller 转售贴 `7af9d810-1ed7-429c-a532-ea2f760e49e6`（已加入 autotest-coseller 店铺）
