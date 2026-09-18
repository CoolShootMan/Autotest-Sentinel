---
name: jira-ones-browser-verify
description: 用 Jira 票 + Figma 设计稿 + ONES 用例驱动浏览器功能测试与验收（Playwright MCP 执行，cookie 文件注入登录态）。当用户给出 Jira 链接/票号（如 KAT-11397）与 ONES 用例链接（计划/模块/单条），要求"读票了解需求 → 看 Figma 设计 → 读 ONES 用例 → 去浏览器按用例跑功能测试/验收/复测"时使用；也用于单票回归验证与发布前人工验收。触发词：jira 链接、图/设计稿/Figma、ONES 用例、按用例测、浏览器验收、功能测试、跑一遍用例、复测、verify ticket。
agent_created: true
---

# Jira + Figma + ONES 驱动的浏览器功能测试

## 用途

把"一张 Jira 票 + 一份设计稿 + 一份 ONES 用例"变成一次可复现、有证据、有结论的浏览器功能测试：

```
Jira 链接 ──► 需求/范围/验收口径 ──┐
Figma 链接 ─► 设计/文案/状态 ──────┼──► 浏览器逐条执行 ──► 证据(截图/URL) ──► 结论报告
ONES 链接 ──► 用例+步骤+预期 ─────┘
```

核心原则：**结论必须自证**。每个 PASS/FAIL 都对应一条可观测事实（页面元素、URL、网络响应、截图），不靠推理、不靠"看起来应该没问题"。拿不准就写 BLOCKED，宁缺毋滥。

## 与相邻 skill 的分工

| skill | 方向 | 什么时候用 |
|-------|------|-----------|
| `jira-ones-testflow` | **录入**：Jira + Figma → 生成用例 → 写进 ONES → 建计划 → 回填 Jira | 要把用例录进 ONES / 建测试计划 |
| **本 skill** | **执行**：Jira + Figma + ONES → 浏览器按用例跑 → 出验证报告 | 用例已经在 ONES 里，要去测/验收/复测 |
| `autotest-kb-refresh` | **知识库**：刷新 `dom_kb`（DOM 向量索引） | 页面结构变了 / 查询结果过期 |

三者共用 `backend/.env` 的凭证与 `tools/` 下的脚本。本 skill **默认只读 ONES 用例库**；只有在用户明确要求时才改写用例（走 `jira-ones-testflow` 的"修改既有用例"配方）。

## 触发场景

- "按这个票和 ONES 用例去浏览器测一遍" / "验收一下 KAT-11397"
- "这张票的功能测了吗？照着用例跑"
- 发布前按计划做一轮人工验收
- 修正后对失败用例复测

## 前置条件

> 🚀 **第一次在新机器上用？先读 `references/onboarding.md`** —— clone 后装依赖、配 `backend/.env`、刷 cookie、跑 4 条自检，照做即可跑起来。

1. **工作目录**：`Autotest-Sentinel` 仓库根目录（本机 `d:\monster_test\Autotest-monster`）——脚本依赖仓库内 `tools/` 与 `backend/.env`。
2. **Python**：`py -3.9`（系统 `D:\Program Files\python.exe`，已装 playwright，`jira_reader`/`ones_reader`/Playwright 全部用它跑通）。
   ⚠️ 不要用 `~/.workbuddy/binaries/python/envs/default`——该 venv 当前不存在 `Scripts\*.exe`，是空壳。
3. **凭证**：`backend/.env` 内 `JIRA_EMAIL/JIRA_API_TOKEN/JIRA_BASE_URL`、`ONES_AUTH_TOKEN/ONES_URL/ONES_TEAM_UUID/ONES_LIBRARY_UUID/ONES_EMAIL/ONES_PASSWORD`。
4. **执行工具**：**只用 Playwright MCP 实时会话**（`browser_navigate` / `browser_snapshot` → `browser_click target=<ref>`）。浏览器跨调用常驻，**不写定位器**。agent-browser 降级为**可选取证工具**（WebM/HAR/视觉 diff），**不要用它驱动用例**。
5. **登录态**：**首选 cookie 文件注入**（`py -3.9 tools/get_all_cookies.py` → 把 cookies 内联进 `browser_run_code_unsafe` → 导航 → 断言 owner 标记）。这也让**切视角只需换文件**（owner / co-seller / partner co-seller）。表单登录是备选。完整配方与实测事实见 `references/browser-runtime.md` §2。

```bash
cd d:/monster_test/Autotest-monster
py -3.9 tools/get_all_cookies.py          # 刷新 3 个账号的 storage_state（每次开跑前）
py -3.9 tools/switch_env.py               # 确认/切换环境（staging / release / prod）
```

## 合格 QA 的开工前准备（**这四样缺一不可**）

跑用例只是最后一步；结论的可信度取决于开工前的准备。缺任何一项，你都会在"判 PASS 还是 FAIL"时失去依据。

| # | 准备项 | 产出 | 不做会怎样 |
|---|--------|------|-----------|
| 1 | **需求**：Jira 票 + **评论** | 一句话需求 / 范围外项 / 业务规则 / 验收口径 | 把已被砍掉的需求当必测项，白跑 |
| 2 | **设计**：Figma（常在评论里） | 确切文案、控件清单与顺序、各状态、显示规则 | "页面上没有这个按钮"无法定性（bug？偏差？用例写错？） |
| 3 | **用例**：ONES **实时**拉取 + 与本地 diff | 执行清单 + 用例↔票↔设计的一致性结论 | 拿旧用例跑 → **假 FAIL**（KAT-12069/T5727） |
| 4 | **环境**：cookie 注入 + owner 标记断言 + 已跑通的操作路径 | preflight 证据 + `path_map.md` | 视角不对 / 路径靠猜 → 大量假 FAIL |

> 顺序：**票 → 设计 → 用例 → 对齐审查 →（发现问题先问人）→ 探路 → 开跑**。
> 对齐审查发现"用例与票/设计冲突"时，**先按 Phase 2 的规则定性，拿不准先问**，不要闷头跑完 12 条再说。

## 工作流

### Phase 0 — 解析输入，锁定任务边界

- Jira：`/browse/([A-Z][A-Z0-9]+-\d+)` → 票号
- ONES：`/testcase/team/<team>/plan/<plan>/library` | `/library/<lib>/module/<module>` | `/case/<case_uuid>`

开始前确认三件事，缺哪项就按默认值走并写进报告：

1. **环境**：默认 `release`；涉及生产数据/支付时必须问。
2. **视角**：owner（商家）还是 partner/co-seller（协作者）？**同功能两种视角可见性不同**（partner 常看不到 owner 创建的对象），选错身份会得到假 FAIL。
3. **范围**：全量跑，还是只跑与本次改动相关的用例。

### Phase 0.5 — 登录态闸门（**不通过不许开跑**）

**做法**：按 `references/browser-runtime.md` §2.0 注入 cookie 文件 → 导航 → **实测断言**。

> 🔴 **2026-09-18 定稿，替换旧版"115 秒冷启动窗口"那套**（旧结论已实测推翻）：
> - **真正承载身份的是 `..._web_auth_token_refresh`（refresh cookie），不是那个 115 秒的 access token。** 只注入 refresh cookie 就能自举出新的 access token；用 **295 秒前**生成的文件 `new_context(storage_state=)` 依然是 owner。
> - 所以**不存在"必须在 2 分钟内开工"的倒计时**。旧观察（+171s 掉访客）已无法复现。
> - **判据从"数秒表"改成"断言 owner 标记"**：页面上没有 `Log in`、有 owner 专属元素、`context.cookies()` 里没有 `_guest` 令牌。
> - 真掉访客的原因通常是：**在访客会话里操作** / **根本没注入 cookie** / 注入了别的账号的文件 —— 而不是"token 过期"。

| # | 检查 | 通过标准 | 不过怎么办 |
|---|------|----------|-----------|
| 1 | owner 标记 | 页面上**没有** `Log in`，且有 owner 专属元素（`/autotestshop`：产品卡 `Copy link`/`Manage event`、底部 `Edit footer`（已配）或 `Add footer`（未配）） | 重新按 §2.0 注入 cookie |
| 2 | 没有降级令牌 | `context.cookies()` **没有** `..._web_auth_token_guest` | 说明当前是访客态 → 重新注入 |
| 3 | 视角与用例匹配 | 用例要求 partner/co-seller 视角时，注入的是**对应账号的文件** | 换文件重注入（**不要**用 owner 跑 partner 用例 → 必然假 FAIL） |
| 4 | 会话保持 | 同一 MCP 会话内连续操作，**不要**为每条用例重建会话 | 需要换视角时，重新注入并**再断言一次** |

**闸门规则**

- 任一条不过 → **不许开跑**；先解决账号/视角，把阻塞原因写进报告。
- 执行阶段**每条用例开始前**再断言一次 owner 特征元素，确认没漂移再测。
- ⚠️ 别把"页面上一步没跳转/卡住"甩给"token 过期"：**已启动的会话不因 token 过期掉线**。卡住要往交互/时序上查（见 `references/browser-pitfalls.md`）。

### Phase 1 — 读票：还原需求与验收口径

```bash
py -3.9 tools/jira_reader.py <KEY> --format text        # 摘要/描述/评论/关联票/附件
py -3.9 tools/jira_reader.py <KEY> --comments-only --format text
```

提炼成四件套，写进报告头部：

- **一句话需求**：用户能看到什么变化。
- **范围外项**：票里明确不测的（历史上大量"重复功能/已有功能"被写进评论澄清）。
- **业务规则**：配置项、触发方式、约束（例："点击按钮才跳转，不是自动跳转"）。
- **验收口径 checklist**：每条都能被页面观测。

**关键**：设计澄清与范围裁剪通常只出现在 **comments**；只看 description 会把已砍掉的需求当成必测项。两者冲突时**以更晚的评论为准**并标注。

### Phase 1.5 — 读设计稿：Figma 是**必做**，不是可选

> 一个合格的 QA 在动手前必须看过设计稿。**只看票 + 用例就去点页面，等于放弃了"预期"的独立来源** —— 你会无法判断"页面上没有这个按钮"到底是 bug、是实现偏差、还是用例写错。

**Figma 链接通常不在 description，而在 comments 里** → 先扫评论，别急着下结论说"没有 Figma"：

```bash
py -3.9 tools/jira_reader.py <KEY> --comments-only --format text    # 扫 figma.com/design/... 或 figma.com/file/...
py -3.9 tools/figma_api_reader.py --url "<FIGMA_URL>" --output data/figma_<KEY> --analyze
py -3.9 tools/figma_reader.py <FIGMA_URL>          # 截图式取证的轻量替代
```

`figma_api_reader.py` 会：抓整棵节点树与全部文案、批量下载关键屏 PNG、输出 `analysis.md`（用户流程 / 关键屏 / 建议的用例分类）。
需要 `backend/.env` 里的 `FIGMA_TOKEN`（权限只需 `file_content:read` + `file_metadata:read`）。API 不可用时，**请用户截图**关键屏（每个场景一张）并描述。

**看设计稿要提取什么**（直接决定后续能不能判 FAIL）：

| 提取项 | 用途 |
|--------|------|
| 按钮/字段的**确切文案** | 用例写的 `Save` 可能实际是动态的 `Add`/`Save`（KAT-12069 偏差 E） |
| **控件清单与顺序** | 用例写有 `Link text` 字段 + `Action` 下拉，设计里根本没有（偏差 D） |
| **状态**：空态 / 有值态 / 禁用态 / 错误态 | 空态模板文案与追加时不同（KAT-12069 T5727） |
| **显示/隐藏规则、跳转方式** | "点按钮才跳转" vs "自动跳转" 这类口径差异 |
| 多端差异（桌面 / 移动） | 响应式组件在不同视口可能是**不同组件**（footnote 编辑器：宽视口 `MuiDialog`、窄视口 `MuiDrawer`） |

**设计 ↔ 用例对齐审查**（产出写进报告的"与设计的偏差"段）：

- 设计里有、用例**没覆盖**的 → 记入"未覆盖与风险"。
- 用例里写了、**设计里没有**的 → 高度怀疑是**用例过时/写错**，先别当 FAIL 记，按 Phase 2 的对齐审查处理。
- 设计与实现不一致 → 这才是要提的偏差/bug，附设计图与实测截图**对照**。

### Phase 1.6 — 读设计稿能对上的历史知识（知识库）

见 Phase 2.5 的"来源优先级"第 4 条：`dom_kb` 里已有**当前线上各页的真实控件清单**，可用来快速回答"这个按钮现在叫什么、在哪个页面"。开工前查一次，比在浏览器里瞎点快。

### Phase 2 — 读用例：把 ONES 用例变成执行清单

```bash
# 计划级 / 模块级 / 单条都能吃，链接直接粘
py -3.9 tools/ones_reader.py "<ONES_LINK>" --out data/verify/<KEY>/ones_cases.json --markdown

# 用例多的模块先收敛
py -3.9 tools/ones_reader.py "<ONES_LINK>" --grep "form" --limit 20

# 找不到模块 uuid 时
py -3.9 tools/ones_reader.py --list-modules

# ★ 每次开跑前：拉一份线上下载副本，并与本地镜像 diff（判断手上用例是否最新）
py -3.9 tools/ones_reader.py "<ONES_LINK>" --out data/verify/<KEY>/ones_cases_live.json
py -3.9 tools/ones_case_diff.py data/verify/<KEY>/ones_cases.json data/verify/<KEY>/ones_cases_live.json
#   → 输出 case_diff.md / case_diff.json；"没有任何用例发生变化" 才可安心复用当前快照
#   → 若有变化：以线上为准，并把旧→新差异写进报告（避免"过期用例 → 假 FAIL"）
```

产出 JSON 含 `id / name / module / priority / condition(前置) / steps[{desc, result}]`；Markdown 版直接当执行清单。读取全程只读（GraphQL 按模块过滤 + 批量取步骤，共 2 次请求）。

> 🔴 **每次开跑前必须重新拉一次（`--out` 覆盖或另存 `*_live.json`），禁止复用上一次跑留下的本地快照。**
> 用例维护者（有时就是用户本人）会**随时改** ONES 用例——改步骤、改期望结果、甚至整条重写。
> 用旧快照执行 = 按**已废弃的步骤/期望**跑，得出"预期未实现"的**假 FAIL**（KAT-12069/T5727 实测：开发者前一日已把期望结果里的 `Contact Us | Privacy Policy | Terms & Conditions` 删掉，我拿 09-17 的旧快照跑，误判成待修复项）。
> 拉完后与上次快照**对一下 diff**（改了哪些用例、改了哪一步），diff 有变动才说明拿的是最新版；把 diff 结论写进报告。这样"用例是否过期"不再靠猜。

拿到清单后**先做用例与票的对齐审查**（60 秒省下半小时白跑）：

- 票里的验收点，哪些**没有用例**覆盖？→ 记入"未覆盖与风险"。
- 用例是否**过期**（票已澄清范围，用例还按旧范围写）？冲突时**以票为准**，该用例标 `SKIP(用例过时)` 并写依据。
- ⚠️ **用例"期望结果"写的是理想态还是已实现态？** 若期望里含某元素而页面上没有，先确认那是**待实现的需求**还是**已被删掉的旧期望**——分不清就别急着报 FAIL，去 diff 历史用例或问开发者。
- 前置条件是否具备（数据、账号、配置）？不满足直接 `BLOCKED`，不要硬跑。
- ⚠️ ONES token 约 **1 小时**过期，长流程中途遇到 401 就 `py -3.9 tools/ones_writer.py refresh-token` 再继续。

### Phase 2.5 — 操作路径探明（**跑批量之前必须做**）

ONES 用例（尤其 AI 生成的）给的是**意图级**步骤，通常**没有定位器、没有入口路径、没有数据准备说明**。直接开跑 = 让 agent 猜着点 → 大量假 FAIL。所以先探路：

**操作知识的来源优先级（按顺序找，别凭感觉）**

1. **同模块已跑通的 YAML 用例** —— `test_case/UI/Test_Katana/All_YAML/`。里面有真实入口路径 + 已验证的定位器写法，是最值钱的参考。
2. **Jira 票 + 评论 + Figma**（Phase 1 / 1.5）—— 入口在哪、按钮文案、显示/隐藏规则、边界行为。
3. **DOM 知识库 `dom_kb/`**（**先查它，再开浏览器**）—— 已经从线上抓好的**真实控件清单**（含 `role`/`testid`/`aria-label`/可见文本 + 所属页面）。用它把"用例里写的按钮名"先翻译成"线上真实的控件名与所在页面"，能省掉大量试错：
   ```bash
   py -3.9 tools/dom_kb.py query --name "Edit footer" --url "{BASE_URL}/autotestshop" --top_k 5
   py -3.9 tools/dom_kb.py query --role button --name "Save"
   ```
   维护（何时重建、怎么读结果、已知坑）见 skill **`autotest-kb-refresh`**。
   - ⚠️ **索引有"年龄"**：`dom_kb/meta.pkl` 里的 `timestamp` 就是抓取时间。若它早于本票的开发时间，**新功能的控件大概率还不在里面** —— 那就老老实实去浏览器探索，或先重建索引。
4. **浏览器实时探索** —— MCP `browser_snapshot` 拿界面树与 `ref`，按 role/name 点击；用 `browser_evaluate` 核对页面事实。
5. **框架工具** —— `tools/ui_snapshot.py`（DOM 快照 + diff）、`tools/locator_lint.py`（定位器静态校验）、`tools/hunt_forms.py`。

**探路做法**

- 挑**最长/最完整的一条用例**（通常是主流程那条）先走通，边做边把真实路径写成 `data/verify/<KEY>/path_map.md`：
  ```
  用例 Txxxx → URL 序列 → 点击序列（role/name 或 @ref 语义） → 前置数据（谁建的、什么状态） → 关键断言点
  ```
- 后续用例复用这份 path_map，速度与稳定性都会好一个量级。
- 探路阶段用**有头**浏览器，你能看着、能随时喊停。

**判定纪律**

- `FAIL` = 路径摸清了、操作都做对了，但**页面事实与用例预期不符**（真 bug 或需求变更）。
- `BLOCKED` = 路径没摸清 / 数据不够 / 视角不对 / 环境不满足 —— **绝不许记成 FAIL**。
- 用例与设计冲突（用例过时）→ `SKIP(用例过时)`，写清依据。

### Phase 3 — 浏览器执行

**默认用 Playwright MCP 实时会话**（`browser_navigate` → `browser_snapshot` 拿带 `ref` 的界面树 → `browser_click target=<ref>`）。**不要**用 CLI 批处理模式逐条跑——那等于每条动作重开浏览器+重登，慢到不可用。工具裁决、登录方式、有头/无头、命令模板与已知坑 → `references/browser-runtime.md`。

- 探路：`--headed`；批量回归：默认 headless + `record`/`trace` 取证。
- 每条用例独立 `--session <name>`；`close` 只在整任务结束时调。

单条用例的执行循环：

```
1. 前置：按 condition 准备环境/数据，报告里写**实际状态**（不写"应已配置"）
2. 步骤：逐条驱动浏览器执行，每条步骤留一张截图
        data/verify/<KEY>/<case_id>_step<N>.png
3. 断言：逐条比对预期，记录"实际观测到什么"
4. 判定：PASS / FAIL / BLOCKED / SKIP + 一句证据（截图名 / URL / 元素文本）
```

**断言纪律（最容易出错的地方）**

- 断言落在**可观测事实**上：元素存在与文本、URL、页面标题、网络响应、跳转落地页。不要写"操作成功"。
- **页面漂移是头号假 PASS 来源**：上一步没真正跳转成功，后续步骤会在**错误页面**继续跑到"通过"。每个跳转后显式验证一次目标页标志元素。
- 拿不准 → `BLOCKED`，写清缺什么。绝不用 PASS 掩盖不确定性。

**定位器优先级**：`data-testid` > `role + name` > 可见文本 > CSS。已知坑：MUI combobox 可访问名常为空，别用 `get_by_role('combobox', name=...)`，改用 `[aria-haspopup='listbox']:has-text('<值>')` 或按 label 的 id 锚定。

### Phase 4 — 报告与收口

写 `data/verify/<KEY>/report.md`（模板见 `assets/verify-report-template.md`），必须包含：

- **精确计数**：总数 / 已执行 / PASS / FAIL / BLOCKED / SKIP / 未执行。数字要能对上明细行数。
- **逐条明细表**：用例 ID、名称、结论、证据路径、备注。
- **失败详情**：复现步骤、实际 vs 预期、截图、初步归属（前端 / 后端 / 环境 / 用例过时 / 需求变更）。
- **与票的偏差**：用例过时项、实现与需求不一致项。
- **与设计的偏差（Phase 1.5 的产出）**：设计里有用例没覆盖的、用例写了设计里没有的、实现与设计不符的（附**设计图 vs 实测截图**对照）。
- **未覆盖与风险**：票里有验收点但无用例覆盖的部分。

需要自动化收口时，把稳定用例转成 YAML 方案用例（`test_case/UI/Test_Katana/All_YAML/`）用 pytest 复跑取证（pytest 才是最终收口证据）：

```bash
py -3.9 -m pytest test_case/UI/Test_Katana/test_ui.py -k testT<number> --alluredir=allure-results
```

可选回写（**先确认再动手，不默认执行**）：ONES 用例步骤带 `execute_result / actual_result` 字段，可承载执行结论，但**写入路径未验证**；Jira 侧回写已有先例 `tools/jira_backfill_test_link.py`（回填 `customfield_10090`）。

### Phase 5 — 沉淀（**测试的价值在于这一阶段**）

一次测试跑完，除了报告，还要把"下次能省时间"的东西留下来：

1. **项目记忆** → `.workbuddy/memory/YYYY-MM-DD.md`（append）：本票的入口路径、真实控件名、踩到的坑与对策。
2. **稳定定位器 / 配置路径 / 业务规则** → `.workbuddy/memory/` 或 `overview_<KEY>_*.md`，同类票直接复用。
3. **DOM 知识库** → 若本票涉及**页面结构变化**（新控件、改名、新页面、改布局），跑 skill **`autotest-kb-refresh`** 把 `dom_kb` 刷新一遍。否则下次别人（或未来的你）在 KB 里查到的是**过期控件名**。
4. **skill 本身的修正** → 发现本 skill 的结论被实测推翻（如 2026-09-18 的"refresh cookie 能自举"）、或文档里的坑已修复，**当场改掉**，别让它继续误导下一个人。
5. **真实 bug** → 另出一段"给开发的复现说明"（环境 + 账号视角 + 步骤 + 证据），可直接贴票。

## 红线

1. **不写探针脚本去 mutate 被测数据**。浏览器里点、看、截图；反复改同一对象会让数据脏掉、结论失效。
2. **不在生产环境跑会改数据的用例**（保存配置、发券、退款、发布），除非用户明确要求；默认 `release`/`staging`。
3. **不做没有证据的结论**。没有截图/URL/响应，就不能写 PASS 或 FAIL。
4. **不改 ONES 用例库来让测试通过**。用例与实现不一致时先判谁错，结论写进报告由人确认。
5. **不跳过前置审查**：用例过时、前置不满足、视角不对，必须在执行前说明，而不是执行后解释。
6. **不跳过设计稿**：没看过设计（或确认票里/评论里确实没有设计稿）就开始跑用例 = 放弃了判 FAIL 的独立依据。
7. **不把"结论被推翻"当没事**：实测推翻了文档/skill/记忆里的结论，必须**当场回写**，否则错误会被反复继承。

## 参考

- **`references/onboarding.md`** — **新机器上手清单**：依赖、`.env`、cookie、4 条自检、常见卡点、不要提交什么。
- `references/jira-ones-api.md` — Jira/ONES 取数接口、链接格式、脚本参数、token 处理（2026-09-17 实测）。
- `references/browser-runtime.md` — **工具裁决（MCP 唯一执行）、登录态首选 cookie 注入（含实测事实与推翻的旧结论）**、有头/无头、agent-browser 取证模板与实测坑。
- `references/browser-pitfalls.md` — pear.us 业务侧的坑与对策（登录态、发布/跳转时序、MUI 定位、视角差异、用例定性四类）。
- `assets/verify-report-template.md` — 验证报告模板。
- 相邻 skill：`jira-ones-testflow`（录入用例 / 用 Figma 生成用例）、**`autotest-kb-refresh`**（刷新 DOM 知识库）。

## 变更记录

- **2026-09-18**：执行工具收敛为 **Playwright MCP 唯一**（agent-browser 降为可选取证）；登录态改为**首选 cookie 文件注入**，并实测推翻"115 秒冷启动窗口 / refresh 不能自举"的旧结论；新增 **Phase 1.5 设计稿对齐**（Figma 必做）与"开工前准备"四件套；接入 **`dom_kb` 知识库**（Phase 1.6 / 2.5 来源优先级）；Phase 5 增加"回写知识库与 skill"。
