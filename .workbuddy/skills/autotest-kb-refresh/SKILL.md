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

## 两段式刷新

```
① 抓快照   ui_snapshot.py snapshot   →  ui_snapshots/baseline__<env>__<ts>.json
② 建索引   dom_kb.py build           →  dom_kb/faiss.index + meta.pkl
③ 验证     dom_kb.py query           →  必须能查回本票涉及的新控件
```

### 前置条件

- **`py -3.9`**（本机唯一装了 playwright / faiss / sentence_transformers 的解释器）。
- **依赖**：`py -3.9 -m pip install -r requirements-kb.txt`（`faiss-cpu` / `sentence-transformers` / `numpy` / `scikit-learn`）。
  ⚠️ `sentence-transformers` 会拉 **torch（约 2GB）**，所以它是**独立于主依赖**的可选文件。
- **新鲜的 cookie 文件**：先跑 `py -3.9 tools/get_all_cookies.py`。
  ⚠️ 没有 cookie 会**以访客视角抓 DOM**（拿不到 owner 专属控件）= 垃圾进垃圾出。
- 新机器整体上手（含 `.env`、自检）见 `jira-ones-browser-verify/references/onboarding.md`。

### ① 抓快照（约 40 秒）

```bash
cd d:/monster_test/Autotest-monster
py -3.9 tools/get_all_cookies.py
py -3.9 tools/ui_snapshot.py snapshot --env release --account main --label baseline
```

- 一个 Playwright 会话连访 `MONITORED_URLS`（`tools/ui_snapshot.py` L38-48）里的 **9 个静态页面**。
- ⚠️ **只覆盖静态 URL**：需要点击才能到达的页面（弹窗、二级配置页、编辑器内部）**不在范围内**。要加页面就往 `MONITORED_URLS` + `WAIT_SELECTORS` 里加（两边要成对加，否则等不到 `role=main`）。
- `--account main` = owner。partner/co-seller 视角才有的控件不会入库。

### ② 建索引（约 20 秒）

```bash
py -3.9 tools/dom_kb.py build --env release --account main --label baseline
```

- 自动取**最新**的该 label 快照（`load_latest_snapshot`）。
- 首次运行会下载 `all-MiniLM-L6-v2`（~80MB）到 `.models/`，之后走本地缓存。

### ③ 验证（**必做，别省**）

```bash
# 用本次变更里的关键控件名查一次
py -3.9 tools/dom_kb.py query --name "<本次新增/改名的控件>" --url "{BASE_URL}/autotestshop" --top_k 5

# 看索引年龄与规模
py -3.9 -c "import pickle;m=pickle.load(open('dom_kb/meta.pkl','rb'));print(m['timestamp'], m['env'], len(m['elements']), 'elements')"
```

**通过标准**：Result 1 就是你要找的那个控件（文案对得上），且 `meta.pkl` 的 `timestamp` **晚于**你关心的那次 UI 变更。

## 🔴 已知坑

1. **去重键绝不能用 `data-testid` 单字段**（2026-09-18 修的缺陷）。
   旧实现按 `url_template||testid` 去重，而这套 App 的 testid **大量复用**：`enhance-button` 在 `/autotestshop` 出现 **62 次**，`mui-box` 覆盖该页所有 MUI box 按钮。
   后果：**402 个元素被压成 66 个**，`Add footer` / `Edit footer`（testid 都是 `mui-box`）被压没了 → query 返回一堆无关 tab，知识库等于废掉。
   修法：改用 `element_signature()` 完整签名（`tag|role|testid|ariaLabel|name|text|placeholder|type`）→ 保留 **160** 个。
   ⇒ **任何改动 `dom_kb.py` 去重逻辑的动作，都必须用同一个控件名做 build 前后的 query 对比。**
2. **`dom_kb/` 与 `.models/` 已 gitignore** ⇒ 索引是本机产物，不会随仓库分发，队友要用得自己 build。
   改的是**逻辑**（`tools/dom_kb.py`）就提交代码；**不要**试图提交索引。
3. **`ui_snapshots/*.json` 是被 git 跟踪的** ⇒ 每次 build 都会多一个快照文件。别把历史快照全部提交（仓库会膨胀），只提交有意义的基线，或考虑加 gitignore 规则。
4. **MCP 的 `browser_run_code_unsafe` 没有文件系统**（`require('fs')` → `ReferenceError`；`await import('node:fs')` → `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`）⇒ 不要想在 MCP 里读索引；读索引只走 `py -3.9 tools/dom_kb.py query`。
5. **索引有"年龄"陷阱**：`meta.pkl` 的 `timestamp` 早于本票的开发时间时，**新功能的控件大概率不在里面**。此时**不要**推断"KB 里没有 ⇒ 线上没有" —— 去浏览器探索，或先重建索引。
6. **`--url` 必须与 `url_map` 的 key 完全一致**（如 `{BASE_URL}/autotestshop`，含花括号）。给了 `--url` 就只返回该页元素；查不到时先去掉 `--url`，看是不是模板字符串写错了。
7. 相似度阈值 **0.3**、过采 `top_k*3` 后再按 URL 过滤（见 `query()`）。所以"查不到"可能是真的没有，也可能是阈值/过滤把结果切掉了 —— 先放开 `--url` 与 `top_k` 再判断。
8. **没有 `search` 子命令**（旧 docstring 写过，从未实现）→ 只有 `build` / `query`。

## 何时刷新

| 触发 | 动作 |
|------|------|
| 本票涉及 **UI 结构变化**（新增/改名控件、新页面、布局调整） | 测完就刷（`jira-ones-browser-verify` Phase 5 第 3 条） |
| 距上次 build **超过 ~2 周**，且要依赖 KB 做定位器修复 | 刷 |
| `query` 的结果与浏览器所见不一致 | **先刷**，再怀疑 KB 逻辑 |
| **不是**每次测试都刷 | 只读、便宜的查询不需要重建；刷新只因为**页面变了** |

## 变更记录

- **2026-09-18**：修掉去重缺陷（新增 `element_signature()`）；端到端实测通过（快照 40s / 建索引 20s / 402 原始 → 160 元素 / `Edit footer` 可被 query 查回）；修正 docstring 里不存在的 `search` 子命令。
