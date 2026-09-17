# T4866 修复 Overview — net::ERR_ABORTED（broken） + 顺带修掉的清理泄漏

## 结论（一句话）
T4866 的 broken 根因是"发布动作触发的客户端重定向与紧接着的 `page.goto` 抢跑"，用框架自带的 `open_until_ready` 重试即可消除；验证过程中又发现 T4866 第 4 段"删除按钮"从未真正发布（post 残留按钮），一并修掉。三个 form CTA 用例（T4860/T4867/T4866）现已实跑通过，且共享 post 回到干净状态。

---

## 1. 报障现象
- 用户全量跑测：90% 通过，两个失败。T3690 已自行修复；T4866 是 **broken**（异常中断，非断言失败）。
- 现场：`step_captures/testT4866/manifest.json`（用户 11:45 那次）
  - step 27 `open_storefront` → `failed`
  - `error_msg: Page.goto: net::ERR_ABORTED at https://release.pear.us/autotestshop/post/event-for-rte-insert-form`
  - 失败瞬间页面 URL **仍停在 admin 页** `/events/b4773b4f-.../view#tab=POSTS,eventTab=TicketsMerch`

## 2. 根因
- T4866 第 2 段以"发布（Update）"结束，编辑器带 `?redirect=%2Fevents%2F...%2Fview` → **发布成功后应用做了一次客户端重定向回事件页**。
- 紧接着的 `open_storefront`（= `page.goto`）与这次客户端导航**抢跑**，`goto` 被浏览器 `net::ERR_ABORTED` 中断 → 步骤抛异常 → 用例 broken。
- 排除项：非登录态/租户问题（匿名与 owner 单独打开均正常）、非 404（同一 URL HTTP 200）、非缓存（curl 加 cache-buster 结果一致）。属**发布后时序竞态**，与具体用例内容无关。

## 3. 修复

### 3.1 竞态：`open_storefront` → `open_until_ready`
`actions/base.py` 的 `open_until_ready` 正是为"刚发布后 storefront 短暂不就绪"设计（先例：`Post_setting.yaml:729`）。三处**同一根因**一次性改掉：

| 用例 | 行 | ready 锚点 | 说明 |
|---|---|---|---|
| testT4860 | CTA 按钮验证 | `button[data-testid="button"]:has-text("test form")` | 紧跟其后的点击必须是这个按钮 |
| testT4867 | 删除后验证 | `text="event-for-rte-insert-form"` | 按钮已被删，改用**post 标题**（SSR 即可见、404 壳没有）当锚点 |
| testT4866 | Part 3 验证 | `button[data-testid="button"]:has-text("test form test1")` | 与随后断言的目标文本一致 |

参数：`retries: 6 / timeout: 8000 / retry_delay: 3000`；`sleep_after_open_storefront` 3000 → 1000（重试已等到内容，固定 sleep 冗余）。T4866 保留其原有 `auto_handle_modals: false`。

### 3.2 顺带修掉：T4866 第 4 段"删除按钮"从未发布（清理泄漏）
验证时用真实浏览器查 DOM，发现 post 上**残留一个 CTA 按钮 `test form test1`**。定位过程（`--step-capture on` 全量抓取）：
- step 33 `R_click_cta_btn_delete`：编辑器里 CTA 已选中（浮动栏出现 Move/Edit/Delete）。
- step 34 `R_click_delete_btn`：CTA 及浮动栏**消失 → 删除本身有效**。
- step 35 `R_click_update_5`：出现确认态（Close/Cancel）。
- step 36 `R_click_update_6`：**确认态仍在、URL 未离开编辑器 → 发布没发生**。
- 对比 Part 1/Part 2 与 testT4867：它们都是**两次 Update 背靠背**点击，能发布成功；只有 Part 4 在两次 Update 之间插了 `sleep_after_update_3: 3000`，长间隔让确认步骤失效 → 删除停在草稿、没发布到 storefront。

修复：把 Part 4 的两次 Update 改为背靠背（对齐 Part 1/Part 2/T4867），并**补一条发布断言** `verify_deleted_published: { text: 'Post published!' }`（T4867 早有此断言，Part 4 缺失 → 失败被静默吞掉）。另补 `wait_cta_button_p4`（对齐 Part 2/T4867 的 Lexical 装饰器水合等待，降低选择抖动）。

## 4. 验证（均为实跑，非推断）
| 用例 | 结果 | 备注 |
|---|---|---|
| testT4866 | **PASSED** ×3（137–140s） | 含新增发布断言 |
| testT4860 | PASSED | 修复前一次即通过 |
| testT4867 | PASSED ×3 | 同时承担把共享 post 清干净 |

- 共享 post 终态：浏览器实测 `button[data-testid="button"]` 中 **无 `test form`**，`total` 由 4 → 3 → **干净**。
- 运行顺序说明：T4860/T4867/T4866 共用同一 post（`/autotestshop/post/event-for-rte-insert-form`）。全量套件顺序为 T4860→T4867→T4866；单人验证时按 T4867(清理)→T4866→T4860 的顺序跑可保持状态一致。

## 5. 改动文件
- `test_case/UI/Test_Katana/All_YAML/Form/Storefront_product_with_form.yaml`
  - T4860 / T4867 / T4866 三处 `open_storefront` → `open_until_ready`
  - T4866 Part 4：两次 Update 背靠背 + `verify_deleted_published` + `wait_cta_button_p4`
  - （含工作区里你今天的 T5007 `fill_form_field` 值修改，未动）

## 6. 备注 / 后续建议
- **T4866 存在同名 sleep 键重复**（`sleep_step3`/`sleep_step4`/`sleep_step5` 各出现两次；`sleep_add` 等属同名不同位置）。按字典折叠语义，值是"最后一个"、位置停在"第一次出现处"，导致实际等待与字面不符（如 `sleep_step3` 实际 500 而非 1000）。**本次未动**（避免改 timing 引入新 flake）；建议单独排期去重。
- `step_captures/<case>/manifest.json` 默认 `--step-capture on-failure`：**通过的用例不会写/覆盖**它，所以它可能停在更早的失败现场。要按步取证需显式 `--step-capture on`。
- storefront post 页的**标题是可见文本**（`<span class="... MuiTypography-h1">event-for-rte-insert-form</span>`），可作为"已到达正确 post 页"的通用锚点（404 壳不含）。
