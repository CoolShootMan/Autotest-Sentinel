# pear.us 浏览器执行坑与对策

> 来源：Autotest-Sentinel 项目长期失败复盘。每一条都造成过假失败或假通过。

## 一、登录态与视角

| 坑 | 表现 | 对策 |
|----|------|------|
| cookie 当天过期 | 报错看着像"locator 找不到"，容易误判成 UI 改了 | 每天开跑前 `py -3.9 tools/get_all_cookies.py` |
| 视角错 | partner/co-seller 看不到 owner 创建的对象（事件、合作邀请、店铺模块） | 先确认用例是 owner 还是 partner 视角，用对应账号；结论里写明身份 |
| 多端差异 | 手机端 / 桌面端 DOM 与可见性不同 | 按用例要求设 viewport，截图里带上 viewport 事实 |
| 环境混淆 | staging/release/prod 数据不通 | `py -3.9 tools/switch_env.py` 确认；报告里写清环境 |

## 二、时序类（假通过的重灾区）

1. **发布后立刻 `open` 会 `net::ERR_ABORTED`** → 用"打开并等到就绪"的语义（框架里是 `open_until_ready`），中途不要插长 sleep。
2. **编辑器发布 = 两次 Update 背靠背**（首次写入、二次生效），中间别插长 sleep，发完补一次发布态校验。
3. **`wait_for_*` 超时只 WARN 不 fail** → 页面漂移不会被拦住，后续步骤会在**错页面**继续跑到"通过"。每个跳转后显式断言目标页标志元素。
4. **动画/抽屉/弹层**：MUI 动画未结束就点击 → 点在遮罩上。等目标元素 visible 且 stable 再点。
5. **提交后的成功页**：先等成功态文案出现，再找下一步按钮，不要用固定 sleep 赌。

## 三、定位器

- 优先级：`data-testid` > `role + name` > 可见文本 > CSS。写进报告的定位器要用稳定那一种。
- **MUI combobox 可访问名常为空**：`get_by_role('combobox', name=...)` 会失败。改用 `[aria-haspopup='listbox']:has-text('<值>')`，或按 label 的 `id` 锚定。
- **同名项/同名按钮**：DOM 里重复项容易点错；多候选时先用容器收敛（`section:has-text(...)` 之内再找）。
- 下拉/抽屉常渲染在 `body` 末尾（portal），不要限定在表单容器内查找。
- 脆弱定位器（`div > div:nth-child(3)`）不要写进结论，先换语义化锚点。

## 四、数据与环境准备

- 用例的 `condition` 要**真的准备好**再跑，报告里写**实际状态**（例："已存在店铺 X 的 form，字段 Name/Email"），不写"应该已配置"。
- 一批用例可能共享同一前置对象（同一表单/同一帖子），**顺序会影响结果**；有依赖先排序并在报告注明。
- 发券/建事件/建合作邀请类用例会产生遗留数据；在 release 跑要记下创建物，便于清理。
- **禁止**用脚本或反复 mutate 同一对象"试出"结果——数据会被改脏，结论不可信。

## 五、取证

- 每条用例的每条步骤留一张截图：`data/verify/<KEY>/<case_id>_step<N>.png`，命名对得上用例 ID。
- 关键跳转额外记录：当前 URL、页面标题、目标元素文本。
- 需要抓网络请求或可回放证据（trace/video）时用 Playwright（MCP 或 CLI），不要用截图猜接口行为。
- 结论证据只认"截图 + URL + 元素文本"三类；单独的 DOM dump 不能作为结论依据。

## 六、实测新增（KAT-12069 踩到，2026-09）

1. **同一弹层会随视口切换组件类型（MUI Drawer ↔ Dialog）**：Storefront footer 编辑器在**窄视口/移动端**是 `MuiDrawer`（`.MuiDrawer-paper`），**宽视口**却是 `MuiDialog`（`.MuiDialog-root` / `.MuiDialog-container`）。**别写死其中一种** —— 用作用域选择器，例如 `:is(div[class*=MuiDialog-root], div.MuiDrawer-root) .katana-wysiwyg`。另外这些弹层**都没有** `div[role=dialog]`，用 `[role=dialog]` 查会恒为 null、误判"没弹出来"。编辑器内容区统一是 `.katana-wysiwyg`（Lexical contenteditable）。
2. **自定义下拉不是原生 combobox**：`role=combobox` 找不到（Style → Color 的"颜色目标"下拉就是）。它是个 `div` + 右缘 `ArrowDropDownIcon`，**必须点箭头**才弹 `MuiPopover`。
3. **多列 Popover 的 DOM 顺序 ≠ 视觉顺序**：同一组选项会横向分列，`querySelectorAll` 的先后和肉眼顺序对不上 → **按 `getBoundingClientRect()` 的坐标点**，不要按 DOM 索引点。
4. **移动端访客查元素先关 Cookie 同意条**：首次进入时同意条是 `position:fixed` 覆盖底部，且一次 `scrollTo(bottom)` 到不了底 → 会**误判元素不存在**。流程：`Accept` → 循环滚动 6 次 × 700ms → 再读。
5. **保存 → 访客前台有 ~<1 分钟传播延迟**：owner reload 即时生效，同一刻新建的访客 context 可能仍见旧内容。**别把瞬时不一致当 Bug**；加 `?cb=<ts>` 或稍等再验。
6. **dnd-kit 拖拽排序无法驱动**：鼠标多步 `move` 与键盘 `focus + Space→ArrowUp→Space` 都无效。这种情况记 **BLOCKED，不是 FAIL**；并用**容器结构证据**替代（例：目标元素在独立容器内、不在 sections 容器内 ⇒ 结构上不参与排序）。
7. **改「设置类」用例要可逆**：改颜色/字体后**必须还原且不 Publish**（改值 → 验证 → 改回 → 选 "Leave without saving"），否则污染线上前台样式。验证"是否真的还原"要读回计算样式，不要只看 UI 标签。
8. **用例「失败」≠ 产品 Bug —— 先分辨三类**（KAT-12069 T5726 教训，2026-09-18）
   （第 4 类来源见 #9：你手上的用例快照本身过期了）：
   - **用例描述写错了**（最常见）：需求本意与步骤写法不一致。例：T5726 把"保存后立即生效、无需刷新"写成了"打字时前台实时预览" → 实测"无实时预览"其实**符合需求**，差点误报 Bug。
   - **历史遗留缺陷**：失败发生在**本票之前就存在**的公共组件上（如 RTE 的 Insert link 不校验非法 URL）→ 照实记为 FAIL，但**注明"非本票引入"**，不要算到本特性头上。
   - **真正的本票缺陷**：才是要提单的。
   → 拿不准时**先问用户/设计**确认需求，再定性；确认是用例写错后，**同步改写 ONES 用例**（见 `jira-ones-testflow` 的"修改既有用例"）。
   → 用户**跳过（skipped）**某条用例时，往往就是"用例写法有问题"的信号 —— 值得先去核对需求而不是硬跑。
9. 🔴 **别拿旧用例跑 —— 第 4 类"失败"来源：手上的用例快照已过期**（KAT-12069 T5727 教训，2026-09-18）：
   - 表现：按步骤执行"期望结果"里的某个元素，页面上**确实没有** → 你判"产品没实现" → **假 FAIL**。真相是用例维护者（常常就是提需求的人自己）**已经把这个期望删掉了**，你只是拿的是改动之前的快照。
   - 铁律：**每次开跑前重新拉一次用例**（`ones_reader.py --out <dir>/ones_cases_live.json`），并用 `tools/ones_case_diff.py <dir>/ones_cases.json <dir>/ones_cases_live.json` 与本地镜像 diff；`changed=0` 才可复用。
   - 有差异时：**以线上为准**，把"旧→新"明细写进报告；**不要**只留一份会被下一次 diff 覆盖的文件当证据（`data/verify/<KEY>/` 不在 git 里，覆盖后无法恢复）。
   - 判别口诀：期望元素缺失时，先问"这是**待实现的需求**，还是**已被删掉的旧期望**？"分不清就别急着报 FAIL。

## 七、实测新增（KAT-12117 踩到，2026-09-18）

1. **Post settings 是整页**：`/post/<POST_ID>/settings`（不是 Drawer/侧栏）。入口两条：编辑器工具栏 `button[data-testid="enhance-button"][aria-label="Settings"]`，或深链直达。
2. **齿轮 ≠ 那个 tooltip 按钮**（最容易点错，点了只弹 tooltip、看不到弹窗还以为功能没做）：
   - 齿轮（真正打开配置弹窗）＝ `button[data-testid="manage-button"]`，**仅当该开关为 On 时才存在于 DOM**；
   - 开关旁边 `aria-label="Use a different contact email"` 的按钮 class 含 `tooltip-control-button-icon` —— 它只负责 tooltip。
3. **MUI 弹窗选择器**：用 `.MuiDialog-root` —— **不是** `div[role="dialog"]`（按 `role=dialog` 查会得到"没弹窗"的错误结论）。
4. **MUI Switch 怎么点**：`.check()` 会报 `Clicking the checkbox did not change its state`（透明遮罩）。可靠做法：`boundingBox()` 取中心 → `page.mouse.click(cx, cy)`。
5. 🔴 **残留弹窗会静默吃掉点击**：MUI 弹窗（onboarding、"This post has been added to your shop." 确认框等）盖在上层时，`page.mouse.click` / `browser_click` **看起来成功但元素状态根本不变**。点关键控件前先 `document.elementFromPoint(cx, cy)` 看顶层是谁；若是 `.MuiDialog-container` 就先关弹窗。
6. **大响应别灌进上下文**：`browser_network_request` 的 `filename` 参数**落盘不生效**（文件不会出现）。要取大 JSON 里的几个字段，用 `browser_run_code_unsafe` + `page.waitForResponse(<url 片段>)` 拿 `resp.json()`，**只 return 需要的字段**。注意 SPA 里 `page.reload()` 可能走缓存**不重新发请求** → 改从别的页面 `goto` 过来触发。
7. **同一个 Post 的前台邮箱会随"浏览者身份"变化**：KAT-12117 实测 owner 与访客都看到帖子自定义邮箱，而 **co-seller 登录态看到的是 Business 默认邮箱**。⇒ 断言"前台显示 X"必须写清**用的哪个身份**，否则同一功能会得出互相矛盾的结论。（桌面视口 + 移动视口同理。）
8. **并发数据漂移**：执行期间别人（常常就是提单/提需求的人自己）会同时改同一条数据。关键断言前后都读一次接口的 `updatedAt` 与字段值；报告里注明"被测数据在 <时间> 被外部改动"。**不要**把"值和我上次设的不一样"直接当产品 bug 报。
9. **开关为 Off 且字段为 null 时，点开关会自动弹配置弹窗**：转售贴 `contactEmail=null` 时点开关 → 直接弹出邮箱弹窗，**填完 Update 开关才变 On**。别误判成"开关点不动"。
10. **别把 token 灌进 `browser_run_code_unsafe`**：该工具会**回显整段 code**，内联的 access token / 密码就进了对话日志。优先改成"本地脚本读 .env 生成 snippet 文件 → `filename=` 调用"（见 `tools/inject_cookie.py`）。
