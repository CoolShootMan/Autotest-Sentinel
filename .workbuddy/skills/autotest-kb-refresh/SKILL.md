---
name: autotest-kb-refresh
description: 刷新 pear.us 的 DOM 知识库（dom_kb，FAISS 向量索引），供 UI 定位器自愈与"用例里的控件到底叫什么"查询使用。当页面结构变化后（新增/改名控件、新页面、布局调整）、dom_kb 查询结果与浏览器不一致、距离上次构建超过两周、或用户要求"更新/刷新知识库"时使用。触发词：更新知识库、刷新知识库、知识库过期、重建索引、dom_kb、DOM 知识库、kb refresh。
agent_created: true
---

# DOM 知识库刷新（dom_kb）

## 这是什么

`dom_kb/` 是**本机**的 DOM 向量知识库（**`dom_kb/` 与 `.models/` 都在 `.gitignore` 里，不入库**；每台机器各自构建）：

| 文件 | 内容 |
|------|------|
| `dom_kb/faiss.index` | FAISS `IndexFlatIP`，384 维（`all-MiniLM-L6-v2`），向量已归一化 ⇒ 内积 = 余弦相似度 |
| `dom_kb/meta.pkl` | 与索引顺序对齐的元素元数据 + `url_map` + `env` + **`timestamp`**（索引年龄就看它） |

**它能回答什么**：给定一个"失败的定位器"或一句"用例里写的控件名"，检索出线上**真实存在**的控件 —— `tag` / `role` / `data-testid` / `aria-label` / 可见文本 / 所属页面。

**谁在用它**：
- `jira-ones-browser-verify`（Phase 2.5 来源优先级第 3 条：开工前先查控件真名）
- `tools/diagnose_failed.py` / `tools/step_analyzer.py` → `dom_kb.query_for_failed_step()`（RAG 定位器自愈）
- `tools/diagnose_failed.py` → `dom_kb.add_elements()`（跑测试时**增量补录**当前页面 DOM）

## 三条补库路径（**不是只有静态快照**）

```
① 静态页面    ui_snapshot.py snapshot  →  ui_snapshots/baseline__<env>__<ts>.json
② 点击路径    kb_capture_flow.py       →  ui_snapshots/flows__<env>__<name>.json   ← 弹窗/配置页靠这条
③ 建索引      dom_kb.py build          →  dom_kb/faiss.index + meta.pkl  （①+② 自动合并）
④ 验证        dom_kb.py query          →  必须能查回本票涉及的新控件
```

**为什么要第 ② 条**：`MONITORED_URLS` 只有静态 URL。**真实业务控件大量藏在点击路径后面**
——Post settings 面板、各种 MUI 弹窗、二级配置页、编辑器内部。只跑 ①，新功能的控件永远进不了库
（KAT-12117 的 `input[name=contactEmail]` / `button[data-testid=manage-button]` 就是这样漏掉的）。

**⚠️ 顺序不能反**：`dom_kb.build_index()` 是**整体重建**（新建 `IndexFlatIP` 后覆盖）。
`build_from_snapshot()` 现在会额外合并 `ui_snapshots/flows__<env>__*.json`，所以 ② 的内容能跨重建存活；
但如果你绕过快照、只用 `add_elements()` 增量，**下一次 build 就全没了**。规则：
> 想让知识**跨重建存活**，就必须落到快照文件（①或②），不能只 `add_elements`。

### 前置条件

- **`py -3.9`**（本机唯一装了 playwright / faiss / sentence_transformers 的解释器）。
- **依赖**：`py -3.9 -m pip install -r requirements-kb.txt`（`faiss-cpu` / `sentence-transformers` / `numpy` / `scikit-learn`）。
  ⚠️ `sentence-transformers` 会拉 **torch（约 2GB）**，所以它是**独立于主依赖**的可选文件。
- **新鲜的 cookie 文件**：先跑 `py -3.9 tools/get_all_cookies.py`。
  ⚠️ 没有 cookie 会**以访客视角抓 DOM**（拿不到 owner 专属控件）= 垃圾进垃圾出。
- 新机器整体上手（含 `.env`、自检）见 `jira-ones-browser-verify/references/onboarding.md`。

### ① 抓静态快照（约 3 分钟 / 11 个页面）

```bash
cd d:/monster_test/Autotest-monster
py -3.9 tools/get_all_cookies.py
py -3.9 tools/ui_snapshot.py snapshot --env release --account main --label baseline
```

- 一个 Playwright 会话连访 `MONITORED_URLS`（`tools/ui_snapshot.py` L38-的 11 个页面）。
- **等待策略（2026-09-18 修）**：旧写法 `wait_until="networkidle"` + `wait_for_selector("body")` 对 SPA 太弱
  —— `/post/create`、`/events/create`、`/events/settings`、`/collabs` 实测**只抓到 2 个元素**（还没 hydrate 完就抓了）。
  现在改为 `domcontentloaded` + **轮询元素数直到稳定**（`settle()`），并且加了**两道守卫**：
  - 落到 `/login` → 跳过（访客 DOM 是垃圾，owner 控件全丢）
  - 正文含 `could not be found` → 404 页，跳过（别把 404 页的链接灌进索引）
- `--account main` = owner。partner/co-seller 视角才有的控件不会入库。

### ② 抓点击路径（新功能**必做**）

```bash
py -3.9 tools/kb_capture_flow.py --flow data/kb_flows/<name>.json --dry-run
py -3.9 tools/kb_capture_flow.py --flow data/kb_flows/<name>.json
```

flow 文件（放 `data/kb_flows/`）：
```json
{
  "name": "post_contact_email",
  "url_template": "{BASE_URL}/post/<post_id>/settings",
  "stages": [
    {"label": "post_settings_panel",
     "url": "{BASE_URL}/post/<post_id>/settings",
     "wait_for": "input[name=\"contactEmail\"]",
     "actions": [{"wait": 2500}]},
    {"label": "contact_email_dialog",
     "actions": [{"click": "button[data-testid=\"manage-button\"]"}, {"wait": 1500}]}
  ]
}
```

- 每个 stage 可自带 `url_template`（跨页面时各归各的 key）；不给则沿用 flow 级的。
- 动作：`click` / `wait` / `wait_for` / `goto` / `press`。**单个 action 失败只告警不中断**
  （很多控件要前置条件才出现，点不到 ≠ 这一页没价值）。
- 产出 `ui_snapshots/flows__<env>__<name>.json`（**同名覆盖、无时间戳**，所以不会像 baseline 那样膨胀仓库）。
- **采集脚本只能"看"，不能"改"**：只允许点开弹窗/切 tab 这类只读动作。
  ⚠️ **绝不要在 flow 里点会被保存的开关/表单** —— 那是 mutate 被测数据。

### ③ 建索引（约 30 秒）

```bash
py -3.9 tools/dom_kb.py build --env release --account main --label baseline
```

- 自动取**最新**的该 label 快照 + 合并所有 `flows__<env>__*.json`。
- 首次运行会下载 `all-MiniLM-L6-v2`（~80MB）到 `.models/`，之后走本地缓存。

### ④ 验证（**必做，别省**）

```bash
# 用本次变更里的关键控件名查一次
py -3.9 tools/dom_kb.py query --name "<本次新增/改名的控件>" --url "{BASE_URL}/<页面>" --top_k 5

# 看索引年龄与规模 / 每个 URL 有多少元素
py -3.9 -c "import pickle;m=pickle.load(open('dom_kb/meta.pkl','rb'));print(m['timestamp'], m['env'], len(m['elements']),'elements');print(list(m['url_map']))"
```

**通过标准**：Result 1 就是你要找的那个控件（文案对得上），且 `meta.pkl` 的 `timestamp` **晚于**你关心的那次 UI 变更。
**KAT-12117 实测基线（2026-09-18 全绿一次）**：静态 11 页 **660 raw** + flow **112** = **772 raw → 328 元素**
（修「可见性漏掉 MUI 开关」之前是 549 raw → 268）。**低于这个数量级就要怀疑页面没抓到**。
更硬的判据不是总数，而是**能不能查回本票的控件**：`grep '"nameAttr": "contactEmail"'` 必须命中。

## 🔴 已知坑

1. **去重键绝不能用 `data-testid` 单字段**（2026-09-18 修的缺陷）。
   旧实现按 `url_template||testid` 去重，而这套 App 的 testid **大量复用**：`enhance-button` 在 `/autotestshop` 出现 **62 次**，`mui-box` 覆盖该页所有 MUI box 按钮。
   后果：**402 个元素被压成 66 个**，`Add footer` / `Edit footer`（testid 都是 `mui-box`）被压没了 → query 返回一堆无关 tab，知识库等于废掉。
   修法：改用 `element_signature()` 完整签名（`tag|role|testid|ariaLabel|name|text|placeholder|type|nameAttr`）→ 保留 **160** 个。
   ⇒ **任何改动 `dom_kb.py` 去重逻辑的动作，都必须用同一个控件名做 build 前后的 query 对比。**
   （2026-09-18 晚些时候把页面覆盖修对、并加上 `nameAttr` 后：549 raw → **239**；再修掉可见性判据后是
   **660 raw（静态）+ 112（flow）→ 328**。"元素数变少"不代表变差，
   要看**能不能查回目标控件**，以及**每个 URL 的元素分布**是否合理。）
2. **`dom_kb/` 与 `.models/` 已 gitignore** ⇒ 索引是本机产物，不会随仓库分发，队友要用得自己 build。
   改的是**逻辑**（`tools/dom_kb.py`）就提交代码；**不要**试图提交索引。
3. **`ui_snapshots/` 整个目录已 gitignore**（2026-09-18 核实：`git check-ignore` 命中 `.gitignore:240`，`git ls-files ui_snapshots/` 为空）⇒
   快照（含 baseline 与 `flows__*`）**是纯本机产物，不入库**。`dom_kb/` 同理。
   后果：**流知识不会随仓库分发** —— 队友要用得自己 build；改的是**逻辑**（`tools/*.py`）才提交代码。
   本机则要注意快照会堆积（每次 build 多一个 `baseline__<ts>.json`），定期清理旧 baseline（build 只取最新）。
4. **MCP 的 `browser_run_code_unsafe` 没有文件系统**（`require('fs')` → `ReferenceError`；`await import('node:fs')` → `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`）⇒ 不要想在 MCP 里读索引；读索引只走 `py -3.9 tools/dom_kb.py query`。
5. **索引有"年龄"陷阱**：`meta.pkl` 的 `timestamp` 早于本票的开发时间时，**新功能的控件大概率不在里面**。此时**不要**推断"KB 里没有 ⇒ 线上没有" —— 去浏览器探索，或先重建索引。
6. **`--url` 必须与 `url_map` 的 key 完全一致**（如 `{BASE_URL}/autotestshop`，含花括号）。给了 `--url` 就只返回该页元素；查不到时先去掉 `--url`，看是不是模板字符串写错了。
7. 相似度阈值 **0.3**、过采 `top_k*3` 后再按 URL 过滤（见 `query()`）。所以"查不到"可能是真的没有，也可能是阈值/过滤把结果切掉了 —— 先放开 `--url` 与 `top_k` 再判断。
8. **没有 `search` 子命令**（旧 docstring 写过，从未实现）→ 只有 `build` / `query`。
9. **`build` 会整体重建** ⇒ 只 `add_elements()` 的增量活不过下一次 build。要"越攒越多"就必须落到快照文件
   （静态进 baseline 快照，点击路径进 `flows__*` 快照）。见开头「三条补库路径」。
10. **`MONITORED_URLS` 里的路由会死**。2026-09-18 实测：`/dashboard`、`/shop`、`/settings`、`/profile`、
    `/analytics`、`/orders` 全部已是 `This page could not be found`。
    死路由不会报错，只会把 **404 页的两个链接**当成"页面控件"灌进索引（静默污染）。
    ⇒ 现在 `snapshot` 有 404 守卫会跳过并告警；**新增/改路由后要补一次健康探测**：
    ```bash
    py -3.9 tools/probe_routes.py                 # 探内置候选集（含历史死路由，回归用）
    py -3.9 tools/probe_routes.py --from-monitored # 只探当前 MONITORED_URLS（发版前体检）
    ```
    输出 `OK / 404 / LOG(掉登录态) / ERR` 四档；`LOG` 说明 cookie 失效，先重跑 `get_all_cookies.py`。
11. **提取器必须采集 HTML `name` 属性**（2026-09-18 补 `nameAttr`）。本套 App 的表单控件主要靠
    `input[name="contactEmail"]` 这类选择器定位；旧提取器只取 `aria-label`/`innerText`，导致这类控件
    在 KB 里**完全无名**、查不回来。`ui_snapshot.py` / `step_capture.py` / `diagnose_failed.py` 三处
    `JS_EXTRACT*` 已同步补上；`element_signature` / `element_to_text` 也纳入该字段。
12. **新增静态页面要成对改两处**：`MONITORED_URLS`（列表）与 `WAIT_SELECTORS`（可选锚点）。
    本套页面**没有 `<main>` / `role=main`**，旧的 `role=main` 锚点是空转的（白等 8s），已清空。
    主等待策略是 `settle()`，`WAIT_SELECTORS` 只是可选加速项。
13. **可见性判据必须与 Playwright 对齐**（2026-09-18 实测发现的**大坑**）。
    旧 `isVisible` 有 `parseFloat(style.opacity) === 0 → false` 和 `!el.offsetParent` 两条，
    而 **MUI `<Switch>` 把原生 `<input type="checkbox">` 设成 `opacity:0`**（可见部分是外层
    track/thumb 的 span）；**Playwright 认为 `opacity:0` 仍可见**，所以 YAML 里
    `input[name="contactEmail"]` 能点、flow 的 `wait_for` 也成功 —— 但提取器把它整批滤掉了
    ⇒ **知识库恰好丢掉 YAML 最依赖的那批设置开关**（`contactEmail` / `checkoutInPost` /
    `isPurchaseApprovalRequired` … 全丢）。修法：改成「`display:none` / `visibility:hidden` /
    零尺寸」才算不可见（见 `ui_snapshot.py` / `step_capture.py` / `diagnose_failed.py` 三处
    `JS_EXTRACT*` 的 `isVisible`）。
    ⚠️ **自查方法**：`py -3.9 tools/ui_snapshot.py snapshot` 后，直接 grep 快照里有没有
    `"nameAttr": "contactEmail"`；没有就说明开关又被滤掉了。

## 何时刷新

| 触发 | 动作 |
|------|------|
| 本票涉及 **UI 结构变化**（新增/改名控件、新页面、布局调整） | 测完就刷（`jira-ones-browser-verify` Phase 5 第 3 条） |
| **本票是新功能** | 除了 ① 静态快照，**必须补 ② `kb_capture_flow.py`** —— 新控件基本都在点击路径后面 |
| 距上次 build **超过 ~2 周**，且要依赖 KB 做定位器修复 | 刷 |
| `query` 的结果与浏览器所见不一致 | **先刷**，再怀疑 KB 逻辑 |
| 发现 `MONITORED_URLS` 里某页返回 404 / 元素数异常少 | 修 URL 列表或等待策略，再刷 |
| **不是**每次测试都刷 | 只读、便宜的查询不需要重建；刷新只因为**页面变了** |

## 变更记录

- **2026-09-18（晚·二）**：修掉**可见性判据漏掉 MUI 开关**的大坑（见已知坑 #13）——`isVisible`
  去掉 `opacity===0` / `!offsetParent`，改为与 Playwright 对齐（零尺寸才算不可见）；三处
  `JS_EXTRACT*` 同步。核实 `ui_snapshots/` 整个目录已 gitignore（修正旧坑 #3 的错误描述）。
  新增 `tools/probe_routes.py`（死路由健康探测，替代一次性探针）。
- **2026-09-18（晚）**：新增 `tools/kb_capture_flow.py`（点击路径补录）+ `build_from_snapshot()` 合并 `flows__*` 快照（解决"build 会抹掉增量"）；
  修 SPA 等待策略（`settle()` 轮询）并加 404/登录页守卫；`MONITORED_URLS` 去掉已死的 `/dashboard`、`/shop`，补
  `explore` / `customers` / `account` / `storefront-modules`；三个提取器补 `nameAttr`。
  实测：静态 549 raw → 239 元素；KAT-12117 flow 补入 85 元素 → 索引 268+。
- **2026-09-18（早）**：修掉去重缺陷（新增 `element_signature()`）；端到端实测通过（快照 40s / 建索引 20s / 402 原始 → 160 元素 / `Edit footer` 可被 query 查回）；修正 docstring 里不存在的 `search` 子命令。
