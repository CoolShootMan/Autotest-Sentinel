# KAT-12117 — 实测操作路径（path_map）

> 环境：release（`https://release.pear.us`，API `https://release.katana-api.1m.app`）
> 执行时间：2026-09-18 15:53–16:12 (GMT+8)

## 被测对象

| 角色 | 账号 | 店铺 | Post id | alias |
|---|---|---|---|---|
| owner（父/原创贴） | `yuxiao.zhu.ext+999@1m.app` | `autotestshop` | `0916aead-3496-4773-90fb-1f04adcdaba0` | `auto-test-post-setting-t1742` |
| co-seller（转售贴） | `yuxiao.zhu.ext+998@1m.app` | `autotest-coseller` | `7af9d810-1ed7-429c-a532-ea2f760e49e6` | 同上（子贴沿用父贴 alias） |

父贴 event：`1a8c503f-1d2c-4b4b-9fe2-5dcd0e155857`（Auto-Test-post-setting）

## 登录态注入（cookie 文件）

```bash
py -3.9 tools/inject_cookie.py --cookie-file test_case/UI/Test_Katana/cookie_release.json \
    --url "https://release.pear.us/events" --out tools/_inject_cookie.js --vanity /autotestshop
# 再用 MCP browser_run_code_unsafe filename=tools/_inject_cookie.js 执行
```

- owner 闸门：URL 停在目标页（不跳 `/login`）、`context.cookies()` 无 `_web_auth_token_guest`、页面无 `Log in`。
- ⚠️ **co-seller / owner 都能通过"无 Log in + 有 auth_token"**（非 owner 不显示 `Copy link`/`Manage event`），要区分视角必须看 `release_katana_vanity_url` cookie 或接口里的 `promoter.email`。

## 进入 Post settings

```
/events → event 卡片 → Post settings 入口二选一：
  A) 编辑器工具栏：button[data-testid="enhance-button"][aria-label="Settings"]
  B) 深链直达：/post/<POST_ID>/settings
→ 页面标题 "Post settings"（整页，不是 Drawer）
```

## Post settings 面板上的控件（实测）

| 控件 | 定位器 | 说明 |
|---|---|---|
| 联系邮箱开关 | `input[name="contactEmail"]`（`span.MuiSwitch-switchBase:has(input[name=contactEmail])`） | MUI Switch，`checked` 即 On/Off |
| 齿轮图标 | `button[data-testid="manage-button"]` | **仅开关为 On 时存在**；Off 时 DOM 中消失 |
| 说明 tooltip | `button.MuiIconButton-root[aria-label="Use a different contact email"]`（class 含 `tooltip-control-button-icon`） | ⚠️ **不要**用它当齿轮，它只弹 tooltip |
| 邮箱弹窗 | `.MuiDialog-root`（**不是** `div[role=dialog]`） | 标题 `Use a different contact email`；`input[type=email]`；`Update` |
| 保存 | `button.MuiLoadingButton:has-text("Save")` / `getByRole('button', {name:'Save', exact:true})` | 成功 toast：`Post settings updated` |
| 失败提示 | `.MuiFormHelperText-root` | 例：`contactEmail must be an email` |

## 前台底部联系邮箱

```
{shop}/{vanity}/post/auto-test-post-setting-t1742
→ 底部文本："Need help? Contact us at\n<email>"
```

## 创建转售贴（co-seller）

```
co-seller 打开 https://release.pear.us/autotestshop/post/<父alias>
→ button:has-text('Add to shop')
→ 直接跳到 /post/<新POST_ID>/view?source=sell（无中间弹窗）
→ 弹窗 "This post has been added to your shop. You now have your own version." → 点 Save
→ 落到 co-seller 店铺编辑器 /autotest-coseller
```

- 参考 YAML：`test_case/UI/Test_Katana/All_YAML/Post/Post_setting.yaml` → `testT3686_CosellerResell`
- 子贴的 Post settings 深链：`/post/7af9d810-1ed7-429c-a532-ea2f760e49e6/settings`
- **转售贴开关为 Off 时，点开关会自动弹出邮箱弹窗**（因为 `contactEmail` 为 null），填完 Update 后开关才变 On。

## 接口事实（用于断言，避免只看 UI）

| 接口 | 用途 |
|---|---|
| `GET /posts/curator/preview/<POST_ID>` | 取 `post.contactEmail` / `post.parentPostId` / `post.originalPostId` / `promoter.supportEmail` |
| `GET /posts/consumer/detail?vanityUrl=<shop>&urlAlias=<alias>` | 消费者视角的 `contactEmail`、`creator.supportEmail` |
| `PATCH /posts/curator/<POST_ID>/advanced` | 保存 Post settings（含 contactEmail） |

## 坑

1. 设置页/编辑器上可能有**残留弹窗**盖住开关（`elementFromPoint` 返回 `.MuiDialog-container`）→ 先关弹窗再点，否则点击静默失效。
2. MUI Switch 用 `.check()` 会报 "did not change its state"；用 `boundingBox()` + `page.mouse.click()` 真实鼠标点击 switchBase 中心可靠。
3. `browser_network_request` 的 `filename` 落盘不生效，别指望把大响应写文件；要在 JS 侧用 `page.waitForResponse` 取 body 再只回传需要的字段。
