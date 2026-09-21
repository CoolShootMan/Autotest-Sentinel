# T3690 卡在 checkout email —— 根因与修复

**文件**：`test_case/UI/Test_Katana/All_YAML/Form/Storefront_product_with_form.yaml`
**结论**：不是页面漂移，是 **YAML 同名 key 被 `yaml.safe_load` 折叠**，把 checkout 的定位器提前到了产品页执行。

---

## 1. 根因（100% 实证）

T3690 的 `test_step` 里有两组**同名 key**：

| 同名 key | 第一次出现（产品表单段） | 第二次出现（checkout 段） |
|---|---|---|
| `fill_email` | line 715 `placeholder: "Enter your email address"` | line 756 `locator: input[name="contact.email"]` |
| `fill_phone` | line 720 `placeholder: "Phone number"` | line 762 `role: textbox, name: Phone number` |

`yaml.safe_load` 的语义是：**值取最后一个，键的位置停在第一次出现处**（Python dict 语义）。于是实际执行序变成：

```
fill_form → fill_email( = checkout 的 input[name="contact.email"] !) → ...
```

即 **checkout 的 email 定位器被提前约 20 秒，在产品页上执行** → `Locator.fill: Timeout 10000ms exceeded`。日志里那句 `Filling field 'input[name="contact.email"]' with value 'xx@qq.com' (frame: None)` 正是这样来的。

**双重取证**

1. `yaml.safe_load` 后打印键序 → index 5 就是 `fill_email: {"locator": "input[name=\"contact.email\"]"}`。
2. 用户留下的 `step_captures/testT3690/manifest.json`：
   - step 3 `fill_form` **passed**（产品页表单弹窗已打开，DOM 有 4 个表单 input）
   - step 4 `fill_email(contact.email)` **failed**，且该步 **`url` 仍是 `/autotestshop/p/bxasz9`** ← 决定性证据

## 2. 修复（最小作用域，只改坏的两处）

只重命名**产品表单段**的两个 key，checkout 段保留规范名（与 Post_setting / Section 等文件一致）：

```diff
-    fill_email:
+    fill_form_email:
       placeholder: "Enter your email address"
       value: "cooperation.business@gmail.com"

-    fill_phone:
+    fill_form_phone:
       placeholder: "Phone number"
       value: "13105558976"
```

改后 T3690 共 33 键、**全唯一**，执行顺序 = 文本顺序。

## 3. 顺带发现的依赖（很重要）

**`testT3690` / `testT5007` 依赖 `testT3695_config_form` 先跑。**

T3695（owner 身份）负责在产品 `/catalog` → Advanced 页**开关 `isProductFormEnabled`** 并配置字段。只跑 `-k T3690` 时产品表单未启用 → 点 Add to cart **不弹表单** → `fill_form` 超时（这是修复后暴露出来的下一个拦路点，不是新 bug）。

main.py 按文件顺序执行（T3695 在 T3690 之前），所以正常跑没问题；**单用例调试时必须 `-k "T3695 or T3690"`**。

## 4. 顺带加固

`wait_for_place_order_button2` timeout **5000 → 15000**。

实测偶发失败：`/cart → /checkout` 跳转慢于 5s，而 `smart_wait` **只 WARN 不 fail**，导致下一个 `R_click_enhance_2` 仍在 `/cart` 上点击，展开态丢失 → `verify_form_data_confirm` 找不到 `just place some text`。

## 5. 线上核对（release 真浏览器）—— 结论：其余定位器全对，无需改

`/checkout` 页可见 input 的真实 `name` 属性：

| name | 说明 |
|---|---|
| `contact.email` | ✅ YAML 用法正确 |
| `address.firstName` / `address.lastName` | ✅ |
| `address.line1` | ph=`e.g. 123 Main St, Austin, TX` ✅ |
| `address.line2` | ✅ |
| `address.city` / `address.state` / `address.zipcode` | ✅ |
| `address.phoneNumber` | ph=`Phone number` ✅ |

- 点 `/checkout` 的 `enhance-button` index 0（**"View required info"**）确实能展开出 Name / Phone / Email / short 全部表单数据。
- 产品表单弹窗内的 input 是 **UUID `name`**（`cf20c387-…` 等），只能用 `placeholder` 定位 —— 与 YAML 现有写法一致。

## 6. 验证（连续 3 轮全绿）

```
py -3.9 tools/get_all_cookies.py          # access token 当时已过期，先刷新
CI=true py -3.9 -m pytest test_case/UI/Test_Katana/test_ui.py \
  --yaml=All_YAML/Form/Storefront_product_with_form.yaml -k "T3695 or T3690" ...
```

- 修复前：`1 failed`（卡 `fill_form`，因缺 T3695 前置）
- 修复后：`1 passed 1 failed`（偶发 verify_form_data_confirm）→ 加 timeout 余量 → **`2 passed` × 3 轮**

## 7. 遗留 / 待办

- **未推送**：按惯例攒一波再推。
- 全仓重复键扫描结果：动作型重复键共 5 处 —— T3690 的 `fill_email`/`fill_phone`（**已修**）；`Post_content.yaml` 与 `Post_setting_for_venue_map.yaml` 各 1 处 `expect_result`、`Post_setting.yaml` testT2515 1 处 `swipe`（**未动**，跨文件、且 Post_setting.yaml 有并发协作，建议确认后再改）。
- sleep/wait 型重复键 **1003 处**（会静默丢等待）。**不建议批量重命名**：恢复了会让总时长暴涨，可能撑爆 CI。
