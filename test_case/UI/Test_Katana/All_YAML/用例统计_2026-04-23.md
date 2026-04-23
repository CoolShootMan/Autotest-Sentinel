# 测试用例统计报告

**生成时间**: 2026-04-23
**统计范围**: `test_case/UI/Test_Katana/All_YAML/`

---

## 总览

| 文件夹 | 文件 | 用例数 |
|--------|------|--------|
| Events | Scanner.yaml | 1 (含3子用例) |
| Events | Sync_event_post.yaml | 1 (含2子用例) |
| Form | Storefront_form.yaml | 4 |
| Form | Storefront_product_with_form.yaml | 19 |
| Module | Module.yaml | 28 |
| Post | Post_setting.yaml | 16 |

**总计: 69 个测试用例编号** (展开后)

---

## Post/Post_setting.yaml (16个)

| 序号 | 测试用例 | 测试函数 | 说明 |
|------|----------|----------|------|
| 1 | T1742 | testT1742_BatchSetCommissionRate | Post commission Batch set to 10% |
| 2 | T2069 | testT2069_ScrollAnnouncement | 滚动公告(banners > 3) |
| 3 | T2705 | testT2705_HideVariant | Partner hides variant & sets default |
| 4 | T2830 | testT2830_HidePost | Partner hides a post on storefront |
| 5 | T2834 | testT2834_VerifyPartner/Guest | Verify partner hides post (partner+guest) |
| 6 | T3683 | testT3683_VerifyPartner | 订单确认备注 - Partner编辑 |
| 7 | T3684 | testT3683_VerifyGuest | 订单确认备注 - Guest验证 |
| 8 | T3686 | testT3686_CosellerInherited | Coseller继承非编辑订单备注 |
| 9 | T3963 | testT3963_ShippingFeeLogic | 运费逻辑(Catalog_Fulfillment) |
| 10 | T4038 | testT4038_EditAnnouncement | 编辑公告 |
| 11 | T4735 | testT4735_VerifyPartner/Guest | Redirect URL启用 |
| 12 | T4735_YesPlease | testT4735_VerifyGuest_YesPlease | Redirect弹窗 - Yes please |
| 13 | T4735_NoThanks | testT4735_VerifyGuest_NoThanks | Redirect弹窗 - No thanks |
| 14 | T2515 | testT2515_SetLimit_WithVariant | 限购5件(variants商品) |
| 15 | T2874 | testT2874_EnableDependentProducts | Must be bought with another item |
| 16 | T5033 | testT5033_5034_VerifyPartner | Choose CTA type - View options |
| 17 | T5034 | (同函数) | Choose CTA type - Add to cart/View Product |
| 18 | T4955 | testT4955_Partner_SetPaymentRestriction | Payment Restriction设置access code |

**展开合并用例后: 16个独立编号**

---

## Events/Scanner.yaml (1个，含3子用例)

| 序号 | 测试用例 | 测试函数 | 说明 |
|------|----------|----------|------|
| 1 | T3981 | testT3981_Verified | QR Scanner - 已签到 |
| 2 | (T3981) | testT3981_Already | QR Scanner - 已签到(重复) |
| 3 | (T3981) | testT3981_NotRecognized | QR Scanner - 无法识别 |

---

## Events/Sync_event_post.yaml (1个，含2子用例)

| 序号 | 测试用例 | 测试函数 | 说明 |
|------|----------|----------|------|
| 1 | T4984 | testT4984_partner | 通过enhance按钮添加产品 |
| 2 | (T4984) | testT4984_guest | Guest验证产品添加 |

---

## Module/Module.yaml (28个)

| 序号 | 测试用例 | 测试函数 | 说明 |
|------|----------|----------|------|
| 1 | T3554 | testT3554 | Module相关 |
| 2 | T3555 | testT3555 | Module相关 |
| 3 | T3556 | testT3556 | Module相关 |
| 4 | T3577 | testT3577 | Module相关 |
| 5 | T3788 | testT3788 | Module相关 |
| 6 | T3789 | testT3789 | Module相关 |
| 7 | T3841 | testT3841 | Module相关 |
| 8 | T3842 | testT3842 | Module相关 |
| 9 | T3843 | testT3843 | Module相关 |
| 10 | T3886 | testT3886_long | Module相关(长文本) |
| 11 | (T3886) | testT3886_short | Module相关(短文本) |
| 12 | T4264 | testT4264 | Module相关 |
| 13 | T4556 | testT4556 | Module相关 |
| 14 | T4559 | testT4559 | Module相关 |
| 15 | T4602 | testT4602 | Module相关 |
| 16 | T4603 | testT4603 | Module相关 |
| 17 | T4605 | testT4605 | Module相关 |
| 18 | T4622 | testT4622 | Module相关 |
| 19 | T4660 | testT4660 | Module相关 |
| 20 | T4816 | testT4816 | Module相关 |
| 21 | T4852 | testT4852 | Module相关 |
| 22 | T4853 | testT4853 | Module相关 |
| 23 | T4903 | testT4903 | Module相关 |
| 24 | T4908 | testT4908 | Module相关 |
| 25 | T5105 | testT5105 | Module相关 |
| 26 | T5210 | testT5210_5211_5212 | Module相关(合并编号) |
| 27 | T5211 | (同函数) | Module相关(合并编号) |
| 28 | T5212 | (同函数) | Module相关(合并编号) |
| 29 | addNewPost | testAddNewPost | Module新增Post |
| 30 | addNewUpdateModule | testAddNewUpdateModule | Module新增更新 |

**展开合并用例后: 28个独立编号**

---

## Form/Storefront_form.yaml (4个)

| 序号 | 测试用例 | 测试函数 | 说明 |
|------|----------|----------|------|
| 1 | - | testPartner_create_form | Partner创建form |
| 2 | - | test_guest_submission_1 | Guest提交(submission 1) |
| 3 | - | test_guest_submission_2 | Guest提交(submission 2) |
| 4 | - | testPartner_verify_commission | Partner验证commission |

---

## Form/Storefront_product_with_form.yaml (19个)

| 序号 | 测试用例 | 测试函数 | 说明 |
|------|----------|----------|------|
| 1 | T3690 | testT3690 | Storefront product with form |
| 2 | T3695 | testT3695_config_form | Curator form配置 |
| 3 | T3695 | testT3695_curator | Curator form |
| 4 | T3695 | testT3695_guest | Guest验证form |
| 5 | T3794 | testT3794 | Storefront相关 |
| 6 | T4276 | testT4276 | Storefront product相关 |
| 7 | T4281 | testT4281 | Storefront product相关 |
| 8 | T4539 | testT4539 | Storefront product相关 |
| 9 | T4540 | testT4540 | Storefront product相关 |
| 10 | T4790 | testT4790 | Storefront product相关 |
| 11 | T4847 | testT4847 | Storefront product相关 |
| 12 | T4847 | testT4847_view | Storefront product相关 |
| 13 | T4847 | testT4847_destroy | Storefront product相关 |
| 14 | T4860 | testT4860 | Storefront product相关 |
| 15 | T4866 | testT4866 | Storefront product相关 |
| 16 | T4867 | testT4867 | Storefront product相关 |
| 17 | T4955 | testT4955 | Storefront product相关 |
| 18 | T4970 | testT4970 | Storefront product相关 |
| 19 | T5006 | testT5006_curator | Storefront product相关 |
| 20 | T5007 | testT5007 | Storefront product相关 |

---

## 合并用例展开规则

当 YAML 中出现以下格式时，需要拆分为独立用例编号：

| YAML格式 | 展开为 |
|----------|--------|
| `T5033_5034` | T5033, T5034 |
| `T3683 & T3684` | T3683, T3684 |
| `T5210_5211_5212` | T5210, T5211, T5212 |
| `T4735_YesPlease` | 视为T4735的变体，编号同T4735 |
| `T3981_Already` | 视为T3981的变体，编号同T3981 |

---

## 统计总结

```
Events:        2  个用例文件
Form:          2  个用例文件
Module:        1  个用例文件
Post:          1  个用例文件
─────────────────────────────
总计:          6  个YAML文件

Post:          16 个独立测试用例编号
Events:         1 个测试用例编号 (T3981, T4984)
Module:        28 个独立测试用例编号
Form:          23 个独立测试用例编号 (含4个无编号函数)

总计:          69 个用例条目
  - 有编号:    45 个
  - 无编号:     4 个 (Storefront_form.yaml)
  - 变体函数:  20 个 (同编号的partner/guest变体)
```
