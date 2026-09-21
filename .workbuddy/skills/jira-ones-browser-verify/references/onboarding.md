# 同事上手：把「Jira + Figma + ONES → 浏览器验收」跑起来

> 目标：**clone 下来、照着做完，不问人就能跑第一条用例。**
> 全程 Windows + `py -3.9`（本机验证环境）。

---

## 0. 一句话流程

```
clone ──► 装依赖 ──► 配 backend/.env ──► 刷 cookie 文件 ──► 自检 4 条 ──► 开跑
```

---

## 1. Python：**必须用 `py -3.9`**

```bash
cd <repo>          # 例如 d:/monster_test/Autotest-monster
py -3.9 -V
```

- 本机**唯一**装齐 playwright / faiss / sentence-transformers 的解释器就是 **系统 Python 3.9**，所有脚本都用 `py -3.9` 调用。
- ⚠️ **不要**用 `~/.workbuddy/binaries/python/envs/default` —— 那个 venv 是空壳（只有 `Lib`，没有 `Scripts\*.exe`），`python.exe` 都不存在。
- 如果你在别的机器上，先确认 `py -0p` 能列出 3.9，否则整套工具跑不起来。

---

## 2. 装依赖

```bash
# ① 主依赖（pytest / playwright / allure / jira / openpyxl ...）
py -3.9 -m pip install -r venv_requirements.txt

# ② Playwright 浏览器内核（新机器必做）
py -3.9 -m playwright install chromium

# ③ 【可选】DOM 知识库依赖 —— 要跑 autotest-kb-refresh 才需要
py -3.9 -m pip install -r requirements-kb.txt
```

> ⚠️ ③ 会拉 **torch（约 2GB）**。不碰知识库就别装。
> ⚠️ 首次查询还会自动下载嵌入模型 `all-MiniLM-L6-v2`（~80MB）到 `.models/`（已 gitignore）。

---

## 3. 配凭证：`backend/.env`

```bash
cp backend/.env.example backend/.env      # Windows: copy backend\.env.example backend\.env
```

然后填**你自己的**个人凭证（`JIRA_API_TOKEN` / `ONES_EMAIL` / `ONES_PASSWORD` / `FIGMA_TOKEN`）。
**团队常量**（URL、各种 UUID）已经写好，照抄不用改。

```bash
py -3.9 tools/ones_writer.py refresh-token     # 自动换 ONES_AUTH_TOKEN（约 1h 过期）
```

- `backend/.env` 已被 gitignore（规则 `.env`）。**永远不要把真实 token 提交上来。**
- 个人凭证**不要互相借用** —— ONES/Jira 的操作会记到 key 的所有者头上。

---

## 4. 登录态：刷 cookie 文件

```bash
py -3.9 tools/switch_env.py                    # 确认/切换环境（staging / release / prod）
py -3.9 tools/get_all_cookies.py               # 约 40s，登录 3 个账号并落盘
```

产出 `test_case/UI/Test_Katana/` 下三个 Playwright `storage_state`：

| 文件 | 账号 | 视角 |
|------|------|------|
| `cookie_release.json` | `+999` | **owner / 商家** |
| `cookie_release_co_seller.json` | `+998` | co-seller |
| `cookie_release_partner_coseller.json` | `+997` | partner co-seller |

> 时序不用焦虑：**refresh cookie 才是承载身份的那个**，它长期有效。
> 「必须 2 分钟内开工」的旧说法已被实测推翻，详见 `references/browser-runtime.md` §2.1。

---

## 5. 自检：跑通这 4 条就说明环境 OK

```bash
# ① Jira 取数
py -3.9 tools/jira_reader.py KAT-12069 --format text

# ② ONES 取数（模块列表）
py -3.9 tools/ones_reader.py --list-modules

# ③ 知识库检索（没装 ③ 依赖的跳过）
py -3.9 tools/dom_kb.py query --name "Edit footer" --url "{BASE_URL}/autotestshop" --top_k 1
#    期望：Result 1 的 Text 就是 Edit footer

# ④ 登录态（在 Playwright MCP 里，按 references/browser-runtime.md §2.0 注入 cookie）
#    期望：owner=true, guestToken=false
```

四条都过 → 可以按 `SKILL.md` 的 Phase 0 → 5 开跑。

---

## 6. 常见卡点

| 症状 | 真因 | 处理 |
|------|------|------|
| `TypeError: unsupported operand type(s) for \|: 'type' and 'NoneType'` | 该脚本用了 PEP 604 `X \| None`（需 ≥3.10），但你在 3.9 跑 | 在**该脚本顶部**加一行 `from __future__ import annotations`（`ones_writer.py` 已加好） |
| ONES 报 401 | `ONES_AUTH_TOKEN` 约 1h 过期 | `py -3.9 tools/ones_writer.py refresh-token` |
| MCP 里 `require is not defined` / `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING` | MCP 的 `run_code` 沙箱**没有文件系统** | 先用 Python 把文件内容读出，再**内联**进代码字符串 |
| `dom_kb.py query` 返回一堆无关元素 | 索引过期（`meta.pkl` 的 `timestamp` 太旧） | 重建索引 → skill `autotest-kb-refresh` |
| 页面上出现 `Log in` | 你现在是**访客态** | 重新注入 cookie（别去"等 2 分钟"） |
| 页面卡住/不跳转 | **不是** token 过期 | 查交互/时序 → `references/browser-pitfalls.md` |
| 用例莫名其妙 FAIL，预期里的元素页面没有 | 可能拿的是**旧用例快照** | 先 `ones_reader.py` 拉线上最新 + `ones_case_diff.py` 比对 |

---

## 7. 第一次跑一条真实用例的顺序

严格按 `SKILL.md` 的「合格 QA 的开工前准备」四件套来：

```
票（含评论）→ 设计稿 Figma → 用例（线上实时拉）→ 对齐审查
        → 探路（写 path_map.md）→ 执行（MCP）→ 报告（report.md）
```

**别跳设计稿**：没看过设计，你就没有判断"页面缺元素"是 bug 还是用例写错的独立依据。

---

## 8. 什么东西不要提交

仓库已用 `.gitignore` 挡掉大部分，**新增文件前先确认**：

| 路径 | 为什么不能提交 |
|------|----------------|
| `backend/.env` | 个人凭证（规则 `.env`） |
| `dom_kb/`、`.models/` | 本机构建产物 / 80MB 模型缓存 |
| `ui_snapshots/` | DOM 快照，`ui_snapshot.py snapshot` 随时可重建 |
| `.playwright-mcp/`、`.playwright-cli/` | 浏览器工具运行时产物（`page-*.yml` / console log 会刷屏） |
| `data/verify/**/*.png` | 单票可到 16MB；截图证据请贴到 Jira 票里 |
| `tools/_*.py`、`/_*.py` | 一次性临时脚本 |

**要提交的**：`data/verify/<KEY>/` 下的 `report.md` / `path_map.md` / `ones_cases*.json` / `case_diff.*` —— 这是团队的验收历史。

---

## 9. 还需要什么 → 看哪份文档

| 想知道 | 看 |
|--------|-----|
| 完整工作流、各 Phase 的判定纪律 | `SKILL.md` |
| 工具怎么选、登录态怎么搞、踩过的坑 | `references/browser-runtime.md` |
| Jira/ONES 接口、脚本参数 | `references/jira-ones-api.md` |
| pear.us 业务侧的坑（MUI 定位、时序、视角差异） | `references/browser-pitfalls.md` |
| 报告该写什么 | `assets/verify-report-template.md` |
| 知识库刷新 | skill `autotest-kb-refresh` |
| 把用例录进 ONES / 建计划 | skill `jira-ones-testflow` |
