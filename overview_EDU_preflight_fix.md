# EDU 预检修复：`tools/dismiss_edu.py` 重写（含用户 6 项反馈）+ U3 路径残留清查

> 状态：**已改完并本地验证通过，按用户要求「先别提」——尚未 commit / PR。**
> 触发问题：GitHub 每日 CI 连续两次报告里，**第一个用例**倒在"被 EDU 遮挡"。

---

## 1. 问题定位：第一个用例就是 T1742

`test_case/UI/main.py` 按序跑 YAML，`All_YAML/Post/Post_setting.yaml` 排第一，其首例是 `testT1742`。

CI 原始证据：

```
Exception: smart_click: element not found: Batch set commission for all products
<locator …> … "<p class="…">Done</p> from <div aria-hidden="true" role="presentation"
   class="MuiPopover-root MuiModal-root …"> … subtree intercepts pointer events
```

## 2. 根因：EDU 是"按账号"的 onboarding，旧脚本从未走到它面前

resale onboarding tour 是 **三步**，入口是"把转售开关打开"：

| 步 | 文案 | 按钮 |
|---|---|---|
| 1 | Set resale earnings | [Start Customizing]（旁有 `Do not show this again`） |
| 2 | Choose a resale model | [Done] |
| 3 | Set per-product values | [Done] |

**只有走完第 3 步**，`Batch set commission for all products` 才可点 —— 正是 T1742 找不到的元素。

旧脚本四处致命：

1. **从没导航过去** —— `Customize` 的点击被注释掉；它找的 `Selling` tab 在**店面**上不存在。
2. **从不开启转售** —— 于是 `+998` / `+997` 这两个没有 event post 的账号**永远不会触发这个 tour**。
   开关是 `input[name=allowPromotersResell]`（`opacity: 0`），可见的 "Off"/"On" 是开关**内部**的
   `<span>`，所以它的可访问名就是字面量 "Off" ——
   `get_by_role("checkbox", name="allowPromotersResell")` **永远不可能匹配**。
3. **勾选 opt-out 靠点文本** —— 在 "Set resale earnings" 弹窗里那段文字是**惰性兄弟 `<p>`**，
   点了没反应，代码却报"已勾选"，于是下次跑弹窗依旧。
4. **异常全吞 + `main()` 无返回值** —— returncode 恒 0，`main.py` 的中止分支从未触发。

### 2.1 两个把上面全部掩盖掉的"隐形墙"（本次新挖出）

**A. MUI modal 让 `get_by_role` 全盲**

`get_by_role(...)` **会跳过 `aria-hidden` 子树**。只要有一个 MUI modal 打开，它背后的整个编辑器就被
标记 `aria-hidden="true"`，于是——页面截图完全正常、`innerText` 里甚至能看到 "Select" 字样，
**但所有 role 定位器返回 0**：

```
get_by_role("button", name="Select", exact=True).count()  ->  0   # 弹窗在
get_by_role("button", name="Select", exact=True).count()  ->  1   # 弹窗没了
```

这里的 modal 就是 **"We found an unsaved version of this post … [Discard]"**，它在 `/post/create`
加载后 **约 2–3 秒异步弹出**（recovery snapshot 是首帧之后才去取的）。上一版只在 +2s 检查一次，
输掉了这场竞速 → `_add_first_product` 超时 → 没有商品 → 转售开关不渲染 → tour 不触发，
而日志只留下一句人畜无害的 `product=no`。

**B. Playwright Python 绑定：正则里带 `/` 会炸掉它自己的选择器**

```
page.get_by_role("button", name=re.compile(r"Add \d+/\d+ product"))
-> InvalidSelectorError: Error while parsing selector
   `button[name=/Add \d+/\d+ product/]` - unexpected symbol "\" at position 21
```

Python 绑定把 `name=<pattern>` 序列化成自己的选择器字符串时会**转义斜杠**，然后自己的解析器又拒绝
这个转义。**这个定位器在任何环境都不可能匹配** —— 不是 flake、不是时序，是彻底坏的。
JS 绑定传的是真 RegExp 对象，不受影响，所以只有 Python 跑会踩。

用本机解释器实测：

```
get_by_role("button", name=re.compile(r"Add \d+"))        -> OK   count=1
get_by_role("button", name=re.compile(r"Add \d+/\d+"))     -> FAIL InvalidSelectorError
locator("div").filter(has_text=re.compile(r"a/b"))         -> OK   count=1
locator("button", has_text="product(s)")                   -> OK   count=1
```

## 3. 用户 6 项反馈 → 逐条落实

| # | 反馈 | 落实 |
|---|---|---|
| 1 | +999 不该遍历所有 event post；第一个 post 里点完 EDU 就该停 | `handle_post_selling_edu` 在**第一个成功打开抽屉的行**停止（`decisive` 早退）。`DISMISS_EDU_FULL_SWEEP=1` 可恢复全量 |
| 2 | +997 / +998 漏了"开启转售"，导致 EDU 没触发 | 新增 `_enable_resale()`：`input[name=allowPromotersResell]` 显式打开并**验证**（`checked` 或"抽屉自动打开"副作用），三级升级含 JS `.click()` |
| 3 | 必须先勾 "Do not show this again" 再点 Start Customizing | `_set_opt_out()` **解析到真正的 `<input>`**（label 或兄弟节点都处理），点击后**回读 `input.checked`** 才认；`dismiss_edu_tour` 保证**先勾再点** |
| 4 | +998 是 co-seller，没有 `/events` 路由，别跳 | `ACCOUNTS` 加 `has_events` 门控；+998 = `False`，打印 `no /events route for this role -- skipping the event sweep`（实测该角色 `/events` 返回 HTTP 404） |
| 5 | "未保存草稿"弹窗要预备着点 Discard | 新增 `_discard_unsaved_draft()`（**轮询等待**，不再单次检查）+ 入口循环清理 + 退出时 `_leave_editor_without_saving()` 可靠收尾 |
| 6 | 加一步：跳 `/account` 点它的 EDU | 新增 `handle_account_edu()`：`/account` → "Manage multiple accounts" → `Got it`（一次性，实测不再复现） |

补充修复（同源）：

- `_close_topmost_edu_popup` 加 EDU 门控 —— `[data-testid=CloseIcon]` 也会匹配**编辑器自己的 X**，
  误点会把编辑器关掉。
- `_add_first_product` 后置条件**真验证**（转售开关出现），不再"点了没抛异常就算成功"；
  且改用 CSS/`hasText` 定位（不受 aria-hidden 影响）。
- 每次失败都打印 `[EDU-WARN] <异常类型>: <首行>`；`DISMISS_EDU_DEBUG=1` 会把截图 + 页面文本落到
  `data/_edu_debug/`。**无头预检静默失败，比大声失败更糟**。
- 草稿计数拆成 `entry` / `exit`：`entry` 必须为 0，否则说明上一轮留了残留、脚本在自我喂养。

## 4. 证据（自证，非推断）

调试环路：`API 预制重置 → get_all_cookies.py → dismiss_edu.py → 浏览器断言/pytest`。

### 4.1 全环境重置后三账号全绿

```
[main (+999)]            post-create: product=yes · resale=on by click · tour=finished · opt-out=verified
[co-seller (+998)]       post-create: product=yes · resale=on by click · tour=finished · opt-out=verified
                         no /events route for this role -- skipping the event sweep
[partner co-seller(+997)] post-create: product=yes · resale=on by click · tour=finished · opt-out=verified

[main (+999)]             OK · events=1 · tours_finished=1 · resale=on · opt_out=verified · leftovers=0
[co-seller (+998)]        OK · events=0 · tours_finished=1 · resale=on · opt_out=verified · leftovers=0
[partner co-seller(+997)] OK · events=0 · tours_finished=1 · resale=on · opt_out=verified · leftovers=0
=== All accounts processed, no onboarding layer left ===   EXITCODE=0
```

### 4.2 幂等（紧接再跑一次，只跑 +999）

```
post-create: product=yes · resale=on by click · tour=skipped · opt-out=n/a · drafts=1(entry=0, exit=1)
```
- `tour=skipped` = EDU 已一次性消费，不再复现 ✅
- `opt-out=n/a` = 屏幕上没有可勾的东西（不是"勾不上"）✅
- **`entry=0`** = 脚本没给自己留残留；`exit=1` 是关编辑器时的正常确认 ✅

### 4.3 定位器 A/B（MCP 浏览器实测）

| 阶段 | 现象 |
|---|---|
| 修复前 | `selectCount=0`、`dlgCount=1`（草稿弹窗）→ 编辑器可视但 role 定位全盲 |
| 清掉弹窗后 | `selectCount=1 / cssSelect=1`，点击正常，`resale:1`，"great start" 弹出 |
| 含 `/` 正则 | `InvalidSelectorError`（见 §2.1-B），改 `hasText` 字符串后通过 |

截图：`data/_t1742/recon_postcreate_01..05*.png`、`data/_edu_debug/`（失败自证）。

### 4.4 T1742 本地冒烟全绿

```
py -3.9 -m pytest -k testT1742 --yaml=All_YAML/Post/Post_setting.yaml
→ 1 passed, 31 deselected in 190.32s     EXITCODE=0
  TEST_STATUS: T1742 - passed
```

CI 挂掉的那一步 `Clicked 'Batch set commission for all products'` 顺利通过。

## 5. 顺带查出的问题

### 5.1 U3 扁平化残留（已修）

三个工具把 UI 根写成 `test_case/UI/UI`（**翻倍段，目录不存在**）：

| 文件 | 症状 | 证据 |
|---|---|---|
| `tools/locator_lint.py` `DEFAULT_ROOTS` | **铁律 12 的首诊工具变成空扫描、恒报 OK** | 修复前 `0 files scanned / OK - no findings`；修复后 `10 files scanned` |
| `tools/parse_allure_status.py` `yaml_dir` | 每次 lookup 都 miss → 用例状态从不更新 | 同型 |
| `tools/ui_snapshot.py` `cookie_dir` | `_resolve_cookie_path()` **恒返回 None** | 修复后返回 `test_case/UI/cookie_release.json` ✔ |

### 5.2 `tools/step_capture.py`：SVG 的 `className` 让整个 DOM 提取静默失败（**已修**）

跑 T1742 冒烟时日志里反复出现：

```
tools.step_capture:step_end:196 - step_capture: DOM extract failed:
Page.evaluate: TypeError: (el.className || "").substring is not a function
```

`el.className` 在 **SVG 元素**上是 `SVGAnimatedString`（对象，不是字符串）→ `.substring` 抛异常 →
**整次提取作废**，该步骤的 DOM 快照全丢。而 `step_end` 只按 DEBUG 记录，看起来人畜无害 ——
正是你 Post-Step Forward Validation 最怕的那种"静默降级"。

根因修复（1 行）：改用 `el.getAttribute('class')`，HTML/SVG 通用且直接返回字符串。

实测（本机解释器）：

```
修复前: EXTRACT FAIL  Page.evaluate: TypeError: (el.className || "").substring is not a function
修复后: EXTRACT OK  rows=3  nameAttr=contactEmail ✔   SVG className='MuiSvgIcon-root jss123' ✔
```

（`nameAttr: contactEmail` 命中符合铁律 29 的自查要求。）

### 5.3 ⚠️ `test_case/UI/actions/product.py:129` 是同类正则地雷（**未动**）

```python
page.get_by_role("button", name=re.compile(target_name)).wait_for(state="visible", timeout=10000)
```

`target_name` 来自 YAML 的标题。**一旦标题里含 `/`，就会抛 `InvalidSelectorError`**（§2.1-B）。
属 framework 层，按用户"别动已封装方法"的要求**只报告不擅改**。建议改成
`locator("button").filter(has_text=target_name)`（已实测该路径安全）。

同族但影响更小的一处：`test_case/UI/actions/base.py:1218` 的 `el.className.split(' ')[0]`
（收集可滚动元素时）——同样会在遇到 SVG 时抛错。通常滚动容器都是 `div`，风险低，仅记录。

（`product.py` 153/175/184–187 行用的是 `filter(has_text=re.compile(...))`，走的是安全路径，不受影响。）

## 6. ⚠️ 待你拍板的 cookie 凭据问题（**未动**）

- `test_case/UI/Test_Katana/cookie_release.json` **含真 token** 且**被 git 跟踪**。
  历史：`674dbec` 已删并 ignore → 队友 **Lury Dian** `3ea0543`(09-22) **复活**，经 `be87d57 Merge branch 'linda'` 进来。
- **根因不是手滑**：队友新用例 `All_YAML/Events/Event settings/fee_breakdown.yaml:635` 写的是
  `cookie_file: "test_case/UI/Test_Katana/cookie_{ENV}.json"`（旧路径），她必须把文件放回旧路径才跑得通。
- `.gitignore:153` 的 `/test_case/UI/*cookie*.json` **目录锚定**，不跨 `/` → 覆盖不到 `Test_Katana/` 子目录。
- 建议：① YAML 路径改 `test_case/UI/cookie_{ENV}.json`；② ignore 放宽为 `test_case/UI/**/*cookie*.json`；
  ③ `git rm --cached` 该文件。**会动到队友用例，先问。**

## 7. 其他观察

- T1742 的 3 个 `smart_click_optional_{start_customizing,done_1,done_2}` 现在**必然空转**
  （每个撞 4 个 popover scope × 5s ≈ 20s，共约 60s）—— 因为 preflight 已把 tour 清干净。可考虑降 timeout，属独立优化。
- `run_suite.py`（API 预制）仍硬编码 macOS 个人路径 `/Users/a123456/...` 且 <3.10 直接硬退 ——
  重置环境时用管理版 venv 直接单跑模块绕过：
  `C:/Users/tester/.workbuddy/binaries/python/envs/default/Scripts/python.exe -m pytest "tests/00_UI Prefill/test_ui_prefill_data_configuration.py" -q --capture=tee-sys`

## 8. 改动文件

```
tools/dismiss_edu.py          | 主交付（重写）
tools/locator_lint.py         |   5 +-
tools/parse_allure_status.py  |   4 +-
tools/ui_snapshot.py          |   4 +-
tools/step_capture.py         |   1 +-  ← SVG className 静默失败（§5.2）
```

未入库（`.gitignore` 覆盖）：`data/_*`（调试落盘与截图）、`data/_edu_debug/`。

## 9. 环境开关速查

| 变量 | 作用 |
|---|---|
| `DISMISS_EDU_STRICT=1` | 有残留时退出码 4（默认只报 `[EDU-LEFT]`，不 fail） |
| `DISMISS_EDU_FULL_SWEEP=1` | 恢复"遍历所有 event post"（默认首个成功打开抽屉即停） |
| `DISMISS_EDU_DEBUG=1` | 失败时把截图 + 页面文本落到 `data/_edu_debug/` |
| `DISMISS_EDU_ONLY=<子串>` | 只跑名字匹配的账号（调试用，如 `999`） |

退出码：`0` 正常 / `2` cookie 文件缺失（指向步骤 2）/ `3` 会话或页面打不开 / `4` strict 模式有残留。
