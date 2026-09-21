# KAT-12069 操作路径表（实测，2026-09-17）

票：Growth: allow partners to create their own storefront footnote
环境：**release**（`https://release.pear.us/autotestshop`）
视角：owner = `cookie_release.json`（`yuxiao.zhu.ext+999@1m.app`）

## 0. 起手式（**必须连成一条链：冷启动窗口 ~2 分钟**）

> 实测模型（2026-09-17）：`release_katana_web_auth_token` 的 `expires` ≈ 登录后 +115 秒；过期后 Playwright 新建 context 会**丢弃**它 → 站点补 `..._web_auth_token_guest` → 访客视角。
> **但已以 owner 启动过的会话不会掉线**（内存态），且 **reload 会自动补发新 token**。
> ⇒ 要防的只有"**带 `--state` 新建会话时的冷启动**"。

```bash
cd d:/monster_test/Autotest-monster
py -3.9 tools/get_all_cookies.py > /dev/null 2>&1 \
  && cd data/verify/KAT-12069/preflight \
  && AB="C:/Users/tester/.workbuddy/binaries/node/versions/22.22.2-3/agent-browser.cmd" \
  && "$AB" --json --session k12069 --headed \
       --state d:/monster_test/Autotest-monster/test_case/UI/Test_Katana/cookie_release.json \
       batch "open https://release.pear.us/autotestshop" "wait 4000" \
             "open https://release.pear.us/autotestshop" "wait 6000" "get title" ...
```

- **`open` 要开两次**：首次常撞 `net::ERR_TOO_MANY_REDIRECTS`（重定向竞态），第二次稳。判据 `get title` == `Auto_Test_shop`。
- 登录态判据：`cookies get` 有 `release_katana_web_auth_token`，**且没有** `release_katana_web_auth_token_guest`。

## 1. 主流程（T5724 happy path）— 已逐段实测

| 步骤 | 动作 | 实测结果 |
|------|------|----------|
| 1 | `open /autotestshop` → `scroll down 300000` → 截图 | 底部出现 **`Add footer`**（owner 专属 CTA）✅ |
| 2 | `find text "Add footer" click` | 弹出 **`Storefront footer`** 模态编辑器 ✅ |
| 3 | 编辑器内容区 `textbox "Storefront footer"` 为空，placeholder = `Edit your footer` | ✅ |
| 4 | 工具栏 | `Undo` `Redo` `Bold` `Underlined` `Insert link` `Center`；**无颜色/字号/间距** ✅ |
| 5 | 模态内另有 `Insert copyright template` 链接、`Close`(X)、主按钮 **`Add`** | ✅ |

**`/autotestshop` 视角特征元素（用于 Phase 0.5 断言）**

- owner：**无** `Log in`；产品卡有 `Copy link` / `Manage event`；底部有 `Add footer`
- 访客：有 `button "Log in"` + `link "Cookie preferences"`；无任何管理控件

## 2. 用例 ↔ 实现 的偏差（执行前已发现）

| 用例 | 用例写法 | 实际实现 | 处理 |
|------|----------|----------|------|
| T5724 步骤 4 / T5734 步骤 2 | 点 **"Save"** | 主按钮是 **"Add"** | 以实现为准执行，报告里标"用例措辞与实现不一致" |
| T5725 步骤 2 / T5734 步骤 4 | `Add footer` / `Edit footer` 两个 CTA | 未配置时是 `Add footer`；配置后是否变 `Edit footer` **待验证** | T5724 保存后再回来确认 |
| T5727 步骤 1 | 模板文案 "Contact Us \| Privacy Policy \| Terms & Conditions" + "(c) 2026 ..." | **未验证**（点了才知道） | T5727 执行时取真实文案 |

## 3. 已知坑（本票实测）

1. **冷启动窗口 ~2 分钟**：access token 的 `expires` ≈ +115 秒，过期后新建 context 会被丢弃 → 应用补 `_guest` → 静默变访客。刷新与开会话必须连链。**已启动的会话不受影响**（实测 +334 秒仍是 owner，reload 还会补发新 token）。
2. **`scroll down 300000` 后 `snapshot -i -c` 只剩轮播的 `Next`**，`Add footer` 不在快照里 → footer 类控件**以截图为准**，点击用 `find text "..." click`，别用 `@eN`。
3. **`open` 首次 `net::ERR_TOO_MANY_REDIRECTS`** → 开两次。
4. **`wait 150000` 级别的长等待会让 agent-browser daemon 死掉**（之后 `cookies get` 返回 0、快照空、exit 1）→ 别在 batch 里塞超长 wait；需要长时间停留就拆成多次短 wait，或分段重开会话（重开记得**先重抓 cookie**）。
5. **refresh token 从不轮换**（168 字符，两次保存逐字节相同）——所以"文件里的 refresh token 还有效"**不代表**能自举登录态，别据此判断登录可用。

## 4. 2026-09-18 补测：关键控件与选择器（实测）

> 12 条已跑完，结论见同目录 `report.md`。以下为本票补充的**可复用操作要点**。

| 目标 | 正确做法 / 选择器 | 备注 |
|------|------------------|------|
| footnote 编辑器（弹层） | 作用域用 `:is(div[class*=MuiDialog-root], div.MuiDrawer-root)` —— **宽视口是 `MuiDialog`、窄视口/移动端是 `MuiDrawer`**，别写死；且**没有** `div[role=dialog]` | 编辑器内容区统一 `.katana-wysiwyg`（Lexical contenteditable） |
| 抽屉主按钮 | 动态：空内容 = **`Add`**、有内容 = **`Save`** | 用例统一写作 "Save"，以实现为准 |
| Style → Color 的"目标"下拉 | 点该行**右缘的 `ArrowDropDownIcon`** 才弹 `MuiPopover`；**无 `role=combobox`** | 选项分组 `Storefront/Buttons/Top bar button/Post cards/Links, Forms & Products`；**多列 ⇒ DOM 顺序 ≠ 视觉顺序**，按 `getBoundingClientRect` 坐标点 |
| Style → Font | 三连下拉：`[元素: Store name/Subtitle/Tab header/Section title/**Other texts**] [字体] [粗细] [字号]` | footnote 字体跟 **Other texts** 走 |
| footnote 结构 | `span`(无 inline style) → `p.katana__paragraph--align-center` → `div.katana-wysiwyg` → 外层 `katana-lc5jup`(`border-top`+`padding-top:16px`) | 分隔线就在 `katana-lc5jup` 上 |
| footnote 所在容器 | `katana-l7wkrt`（**独立于** sections 容器 `katana-cjsq01`） | ⇒ 不参与 Rearrange 排序 |
| 移动端访客查 footnote | 先 `Accept` 掉 Cookie 同意条 → 循环 `scrollTo(bottom)` 6 次 × 700ms → 再读 | 一次 `scrollTo` + 未关同意条会误判 `footnote:null` |
| 保存 → 访客前台 | 有 **~<1 分钟**传播延迟；owner 即时 | 验证访客时加 `?cb=<ts>` 或稍等，别当 Bug |

### 已确认的产品 Bug（本票）
- **T5730**：Insert link 无 URL 校验，`abc` → `https://abc` 静默插入。
- **T5726**：编辑 footnote 无实时预览。
- **T5727**：空编辑器点 `Insert copyright template` 只插入版权行，缺链接行。

### 阻塞项
- **T5732 步骤 2**：dnd-kit 排序鼠标拖 + 键盘 `Space→ArrowUp→Space` **均无效** ⇒ BLOCKED（用容器结构证据替代"仍置底"结论）。

## 5. 2026-09-18 复测：需求澄清与用例定性修订

> 用户当面纠正了口径 —— **失败的用例不一定是产品 Bug**，要先分辨三类。

| 用例 | 首轮定性 | 修订后 | 依据 |
|------|----------|--------|------|
| **T5726** | ❌ FAIL（"无实时预览"） | ✅ **PASS** | 需求本意是「**保存后** shop 底部**立刻**更新、**无需刷新**」，**不是**逐字实时预览。原用例描述写错（用户此前**跳过**了这条）→ **已改写 ONES 用例**（uuid `4WBTxGGR`，改名/描述/前置/3 步；`assign`/P1/类型/模块不动；备份 `data/KAT-12069_case_backup_4WBTxGGR.json`） |
| **T5727** | ⚠️ FAIL(部分) | ✅ **PASS** | 首次判"用例预期待修正"是**我用了 09-17 旧快照**所致 —— 用户已在 09-17 亲手把期望改成"只输出版权行"。**实时拉取线上用例后改判 PASS**（见 §6） |
| **T5730** | ❌ FAIL | ❌ FAIL 但标 **历史 bug** | 用户确认 Insert link 组件**在本特性之前就有**该问题，非 KAT-12069 引入 |

**复测 T5726 的判定方式**：编辑 footnote（含加粗）→ 点保存 → **不做任何 `page.reload()`** → 直接滚到底部读 DOM，确认底部**立即**出现新内容且 `footnote` 为 `<strong class="katana__textBold">`；再 reload 确认持久。证据 `T5726r_s2_editor_bold.png` / `T5726r_s3_no_reload.png` / `T5726r_s4_reload_persist.png`。

**工具层顺带修复**：`ones_writer.py` 用了 `X | None`（PEP 604，需 ≥3.10），而本机唯一装了 playwright 的是 `py -3.9` ⇒ **整个写入流程本机跑不起来**。已在文件顶部加 `from __future__ import annotations`（一行，3.9/3.10+ 通吃）修复。

---

## 6. 2026-09-18 复测：**实时拉取用例 + 快照 diff**（用户第二次纠偏）

> 用户："你能不能实时对比下最新的用例？我发现你跑的时候就是照着旧的用例步骤来，T5727 在我昨天测试的时候就已经被我更新过了。"
> 根因：**我复用了上一次跑留下的 09-17 本地快照**，而用例在快照之后被改过。

**标准动作**（已写进 skill `jira-ones-browser-verify` Phase 2）：

```bash
# 1) 拉线上最新副本
py -3.9 tools/ones_reader.py "<ONES_LINK>" --out data/verify/KAT-12069/ones_cases_live.json
# 2) 与本地镜像逐条 diff（字段级 + 步骤级）
py -3.9 tools/ones_case_diff.py data/verify/KAT-12069/ones_cases.json \
                                data/verify/KAT-12069/ones_cases_live.json
#    → case_diff.md / case_diff.json；"没有任何用例发生变化" 才可复用当前快照
# 3) 刷新本地镜像
py -3.9 tools/ones_reader.py "<ONES_LINK>" --out data/verify/KAT-12069/ones_cases.json --markdown
```

**本次结果**：线上 12 条 vs 旧快照 → **2 条有差异**：

| 用例 | 漂移 | 说明 |
|------|------|------|
| T5727 | 真·外部漂移 | 步骤 1 期望从"链接行 + 版权行"改为**仅**版权行（用户 09-17 改的）→ 改判 **PASS** |
| T5726 | 我自己改的 | 非漂移，是上一轮我同步 ONES 用例所致 |

⇒ 结论：**T5727 是 PASS**；报告计数 **PASS 10 · FAIL 1(历史) · PASS+BLOCKED 1**。
⚠️ `data/verify/` 不在 git 里，旧快照被覆盖后不可恢复 → 漂移明细留档在 `report.md` 的「C-留档 / I-留档」段。

