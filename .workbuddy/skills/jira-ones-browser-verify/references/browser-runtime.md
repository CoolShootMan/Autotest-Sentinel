# 浏览器运行时：工具、登录态、有头/无头

> 2026-09-17 初测，**2026-09-18 定稿**（本机 Win11 + release 环境）。执行前先读这份，能省掉大量试错。

## 1. 工具裁决（默认用哪个）

> **2026-09-18 定稿**：跑用例的**执行工具只有一个 —— Playwright MCP 实时会话**。此前用 agent-browser CLI 的 `batch` 模式逐条跑，被用户当面否掉（**每次调用 = 新开浏览器 + 重新登录，且拿不到实时画面**，只能靠 snapshot 文本猜选择器，一个动作一轮往返）。agent-browser **降级为"可选的取证工具"**，不再承担执行职责。

| 工具 | 定位 | 说明 |
|------|------|------|
| **Playwright MCP**（`mcp__playwright__browser_*`） | **唯一执行工具** | 浏览器跨调用常驻：`browser_navigate` → `browser_snapshot`（带 `ref=eNN` 的界面树，可 `boxes:true` 拿坐标）→ `browser_click target=<ref>`。**不写定位器**；`browser_take_screenshot` 出图留证；登录态用 §2.0 的 cookie 注入建立 |
| **Playwright CLI 脚本**（`py -3.9`） | 确定性/CI/`pytest` 收口 | 原生 `storage_state=`；要循环、重试、断言脚本化时用。`pytest` 仍是最终收口证据 |
| **agent-browser**（v0.27.0） | **可选**：截图/trace/视频/HAR/`diff screenshot` 视觉回归 | **session 不跨调用存活**、"每次 `--state` 都是冷启动" ⇒ **不要用它驱动用例**；只在需要 WebM/HAR/视觉 diff 这类 MCP 给不了的东西时用 |

**一条用例固定用一个工具跑完**，中途换工具会丢上下文、制造"找不到元素"的假象。

**MCP 用法要点（省掉 90% 无效往返）**

- `snapshot` 是"看得见 + 点得到"的界面树，**优先用它而不是自己写定位器**；ref 陈旧（元素重挂载）就再取一次快照，代价很低。
- 快照太大/太杂时用 `target="[role=dialog]"` 只取某个子树，ref 更短更稳。
- 点击目标有歧义（如页面上有两个 `Add`）时：`snapshot target=<子树>` 拿子树内的 ref，别猜。
- 需要坐标（视觉点击/画布/拖拽）时 `snapshot boxes:true` 拿 `[box=x,y,w,h]`。
- ⚠️ **`browser_run_code_unsafe` 的沙箱没有文件系统**：`require('fs')` → `ReferenceError: require is not defined`；`await import('node:fs')` → `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`。**需要文件内容时必须先由 Bash/Python 读出、再内联进代码字符串**（§2.0 的 cookie 注入就是这么做的）。
- ⚠️ **MCP 的 context 是长寿命的**：一旦它以 owner 启动过，单靠 `clearCookies()` 之后导航也可能自愈回 owner。要做**干净的访客对照**，见 §2.2。

## 2. 登录态：**首选 cookie 文件注入**（2026-09-18 实测定型）

### 2.0 首选：cookie 文件 → 注入 MCP 会话

```bash
# ① 刷新 cookie 文件（每次开跑前；约 40s，登录 3 个账号）
py -3.9 tools/get_all_cookies.py
#    → test_case/UI/Test_Katana/cookie_release.json            (owner / main)
#      test_case/UI/Test_Katana/cookie_release_co_seller.json  (co-seller)
#      test_case/UI/Test_Katana/cookie_release_partner_coseller.json (partner co-seller)

# ② 取出 cookies 数组（紧凑单行，便于内联）
py -3.9 -c "import json;print(json.dumps(json.load(open('test_case/UI/Test_Katana/cookie_release.json',encoding='utf-8'))['cookies'],separators=(',',':')))"
```

把 ② 的输出粘进 `browser_run_code_unsafe`（**一次调用完成"注入 → 导航 → 断言"**）：

```js
async (page) => {
  const cookies = [ /* 粘贴 ② 的输出 */ ];
  await page.context().clearCookies();
  await page.context().addCookies(cookies);
  await page.goto('https://release.pear.us/autotestshop', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);
  const t = await page.evaluate(() => document.body.innerText);
  const cs = await page.context().cookies();
  return JSON.stringify({
    owner:      !t.includes('Log in'),
    editFooter: t.includes('Edit footer'),
    guestToken: cs.some(c => c.name === 'release_katana_web_auth_token_guest'),
  });
}
```

**为什么首选它（而不是表单登录）**

1. 一次拿到**确定的身份**，绕开表单登录的 `Tab`/`onBlur` 时序坑。
2. **切视角只要换文件** —— owner / co-seller / partner co-seller 三个文件直接换，不用登出再登录。这正是 Phase 0 要求的"视角"最省事的实现（partner 视角看不到 owner 创建的对象，用错身份 = 假 FAIL）。
3. 与 `pytest`/框架走**同一条鉴权路径**（`storage_state`），验证过的东西可迁移。

### 2.1 实测事实（2026-09-18，**推翻旧结论**）

| 事实 | 实测值 |
|------|--------|
| `release_katana_web_auth_token`（access token）的 `expires` | 约 **+110~115 秒** |
| `..._web_auth_token_refresh` | 长期有效（2027+），**从不轮换** |
| 注入**已过期**的 access token | Playwright/Chromium **直接丢弃**（`context.cookies()` 里查不到），不报错 |
| **只注入 refresh cookie**（先清空所有 cookie + `localStorage` + `sessionStorage`） | **能自举出新的 access token → OWNER** ✅ |
| `new_context(storage_state=)` 用 **295 秒前**生成的 cookie 文件 | **仍是 OWNER** ✅（access token 被补发，无 guest token） |
| 冷启动后采样（每 500ms） | `domcontentloaded` 后第一个采样点（4.8s）**已经是 owner**，没有"先访客后切换"的中间态 |
| MCP 会话一旦以 owner 启动 | **长期保持**：access token 过期后导航时自动补发 |

> 🔴 **纠正（旧文档已错，勿再沿用）**
> 旧版写过：「冷启动没有 access token 时站点补 `..._web_auth_token_guest`，**不会用 refresh cookie 自举**」，并据此把 **115 秒**当成"冷启动必须趁热"的硬窗口。
> **2026-09-18 两次独立实测推翻**：① MCP 里只注入 refresh cookie → OWNER；② 用 **295 秒前**的文件 `new_context(storage_state=)` → 仍是 OWNER。
> **⇒ 真正承载身份的是 refresh cookie，不是那个 115 秒的 access token。** 115 秒只是 access token 的属性，它过期会被站点用 refresh 换新，**不是"必须 2 分钟内开工"的倒计时**。
> 旧观察（+171s 掉访客）现在**无法复现**；不要再拿"token 过期"解释页面卡住/掉访客（见 §5 第 7 条）。

### 2.2 访客视角（MCP）

```js
// 清掉全部 cookie 且不注入任何 cookie 文件 → 访客
async (page) => {
  await page.context().clearCookies();
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.goto('https://release.pear.us/autotestshop', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);
  const t = await page.evaluate(() => document.body.innerText);
  const cs = await page.context().cookies();
  return JSON.stringify({
    guest: t.includes('Log in'),
    guestToken: cs.some(c => c.name === 'release_katana_web_auth_token_guest'),
  });
}
```

⚠️ **访客对照必须在"没注入过 owner cookie 的会话"里做**：MCP 的 context 长寿命，一旦当过 owner，后续操作可能自愈。若同一 context 既要测 owner 又要测访客，**先测访客、再注入 owner cookie**，并每次都实测断言（不要靠"我以为清了"）。

### 2.3 备选：表单登录（cookie 文件不可用时兜底）

`release` 账号密码在 `tools/get_all_cookies.py` 的 `ACCOUNTS`：

| 账号 | 邮箱 | 密码 | 视角 |
|------|------|------|------|
| main | `yuxiao.zhu.ext+999@1m.app` | `Happy123` | **owner / 商家** |
| co-seller | `yuxiao.zhu.ext+998@1m.app` | `Happy123` | co-seller |
| partner co-seller | `yuxiao.zhu.ext+997@1m.app` | `Happy123` | partner co-seller |

```
browser_navigate https://release.pear.us/login
snapshot → 邮箱 textbox / 密码 textbox / "Log in" 按钮的 ref
browser_fill_form 填两个字段
browser_press_key Tab        ← 触发 onBlur 校验（必需，否则点击是静默空操作）
browser_click <Log in ref>
```

### 2.4 判据：**断言 owner 标记，不要数秒表**

| # | 检查 | 通过 |
|---|------|------|
| 1 | 页面上**没有** `Log in`，但有 owner 专属元素 | ✓ |
| 2 | `context.cookies()` **没有** `..._web_auth_token_guest` | ✓ |
| 3 | 若出现 `_guest` 或 `Log in` | 停 → 按 §2.0 重新注入（不是"等 2 分钟"） |

**`/autotestshop` 上的 owner 特征元素**（实测截图确认）：

- owner：页头**没有** `Log in`；产品卡有 `Copy link` / `Manage event`；**店铺底部有 `Edit footer`（已配 footenote）或 `Add footer`（未配）**
- 访客：页头有 `button "Log in"`、`link "Cookie preferences"`；无任何管理控件

> 纠错记录：曾误判为"`/autotestshop` 不体现视角"（当时两侧快照 15 元素逐字相同）。**真实原因是那次确实在访客态**。趁热启动时 owner 与访客**明显不同**。

## 3. 有头 / 无头

- **MCP 实时会话**：浏览器窗口由 MCP 自己管理，**执行阶段默认可见**（人能看、能随时打断，MUI 时序更真实）。这是执行主力，不需要额外开关。
- `get_all_cookies.py`：headless（只取 cookie，不需要看）。
- 本地 `pytest`：由 `conftest.py` 的 `pytest_configure` 钩子强制 headed（框架约定，与工具默认无关）。
- agent-browser（仅当用作取证工具时）：默认 headless，`--headed` 才显示窗口；要 WebM/HAR 时用 `record start/stop`、`trace start/stop`。

## 4. agent-browser 命令模板（**可选，仅用于取证**）

> ⚠️ 不要用它驱动用例（见 §1 裁决）。下面模板只在需要 **WebM 录屏 / HAR / 视觉 diff** 这类 MCP 给不了的能力时用。

```bash
agent-browser --session kat12069 --headed \
  --state test_case/UI/Test_Katana/cookie_release.json \
  --screenshot-dir data/verify/KAT-12069 \
  open "https://release.pear.us/autotestshop"
agent-browser --session kat12069 snapshot -i -c -d 4     # 拿 @eN ref，别猜 CSS
agent-browser --session kat12069 find role button click --name "Save"
agent-browser --session kat12069 screenshot "T5512_step3.png"
agent-browser --session kat12069 get url                 # 断言当前 URL
agent-browser --session kat12069 close                   # 整个任务结束时才 close

# 录屏取证（MCP 给不了 WebM）
agent-browser --session batch1 --state <cookie_file> open <url>
agent-browser --session batch1 record start data/verify/KAT-12069/T5512.webm
agent-browser --session batch1 record stop
```

要点：

- 一个 session 内登录态与页面状态贯穿（**同一进程内**）；`close` 只在整任务结束时调。
- ⚠️ **daemon 不跨工具调用存活**：分多次调用跑时，后续调用会连到新 daemon（页面空白 / cookie 丢失 / 竞态 404）。→ 把「open → 等待 → 操作 → 截图 → 断言」写成**一次 `agent-browser batch` 调用**，并且**每次调用都带 `--state`**。
- **用 `--json`**：输出结构化（`{"command":[...],"result":{...},"success":true}`），可直接解析；默认文本输出经 PowerShell 重定向会变 UTF-16。
- **`--screenshot-dir` 在 batch 模式下不生效**（截图落在进程 cwd）→ 先 `cd` 到目标目录再跑，或跑完把 png 移走。
- 每个用例用独立 `--session <name>`，避免串台（也可并行）。
- `--json` 便于程序化解析；`--annotate` 出带编号标注的截图。
- 建议加护栏：`--allowed-domains "release.pear.us"`、`--confirm-actions` 只放行必要动作类别。
- 其他可用能力：`cookies get/set`、`storage local/session`、`network requests`、`har start/stop`、`console`、`errors`、`diff screenshot --baseline`（视觉回归）、`get vitals`（Core Web Vitals）。

## 5. 实测踩到的坑

1. **直接开根域名 `https://release.pear.us/` 会偶发 `net::ERR_TOO_MANY_REDIRECTS`** → 开具体路径（如 `/autotestshop`）。
2. **PowerShell 里跑 agent-browser**：其 shim 往 stderr 打噪声，PowerShell 会当成终止错误 → **同一次调用里后续命令不再执行**。对策：每条 agent-browser 命令单独发一次调用，或 `try/catch` 包住。**更省事的是改用 bash**（见下条）。
3. **bash 里跑 agent-browser 是可行的**（2026-09-17 实测 `agent-browser 0.27.0` 正常）：用全路径即可 —— `AB="C:/Users/tester/.workbuddy/binaries/node/versions/22.22.2-3/agent-browser.cmd"`，且**输出重定向为 UTF-8**（比 PowerShell 的 UTF-16 好处理）。唯一注意：该 bash 环境**缺 coreutils**（`dirname`/`ls`/`head`/`tail` 全没有），所以**别在命令里拼 `| head` / `ls`**，需要看输出就用 `py -3.9 -c "print(open(...).read())"`。
   - shim 仍会往 stderr 打一条 `dirname: command not found` 噪声，**无害，可忽略**。
4. PowerShell 重定向写出的中文是 **UTF-16**，`Read`/`grep` 会当二进制 → 用 python 解码后再看。
5. agent-browser 自带技能文档（版本对齐，比 flag 文档更全）：
   ```bash
   agent-browser skills list
   agent-browser skills get core --full     # 核心用法
   agent-browser skills get dogfood         # 系统性探索/找 bug 的流程（与本 skill 最接近）
   ```
6. **跨调用状态不保**（实测）：`snapshot` 在另一次调用里返回 `(no interactive elements)`、同 URL 偶发 `This page could not be found.` —— 都是连到新 daemon / 页面未就绪所致，**不是被测系统的 bug**。判定前先确认「cookie 是否已加载」（`cookies get --json` 应能看到 `..._web_auth_token`，**且没有 `..._web_auth_token_guest`**）与「页面是否真的加载完」（`get title` 有值）。
7. **`Log in` 是有效的降级信号，别忽略**：owner 态下 `/autotestshop` 页头**没有** `Log in`；一旦看到 `Log in`，基本可以断定你在访客视角 —— 按 §2.0 **重新注入 cookie**（并确认 `context.cookies()` 里没有 `..._web_auth_token_guest`），**不要**当成"公开页正常现象"放过去。
   - 🔴 但**不要**再把它归因成"token 过期 / 115 秒窗口过了"：2026-09-18 实测 refresh cookie 能自举（§2.1），295 秒前的文件照样是 owner。掉访客真实原因通常是**你在访客会话里操作**或**根本没注入 cookie**。
   - 同理，**页面卡住/不跳转 ≠ token 过期**（已启动的会话不会因 token 过期掉线）。往交互/时序上查（见本文件与 `browser-pitfalls.md`）。
8. **`snapshot -i -c` 会漏掉店铺底部的 `Add footer`**（KAT-12069 实测：滚到底后快照只剩轮播的 `Next`，而截图里 `Add footer` 清清楚楚）。**footer/footnote 这类小文本控件以截图为准**；要点击它，用 `find text "Add footer" click` 或 `click "text=Add footer"`，别依赖 `@eN` ref。
9. **滚动到底要滚足够远**：`scroll down 300000` 之后快照可能只反映视口附近；想验证"页面最底部"，先 `scroll down` 再 `wait 2500` 再截图，别只信快照。
