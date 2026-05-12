# Test Case Statistics Report

**Generated:** 2026-04-23
**Scope:** `test_case/UI/Test_Katana/All_YAML/`

---

## Overview

| Folder | File | Test Cases |
|--------|------|-----------|
| Events | Scanner.yaml | 1 (with 3 sub-cases) |
| Events | Sync_event_post.yaml | 1 (with 2 sub-cases) |
| Form | Storefront_form.yaml | 4 |
| Form | Storefront_product_with_form.yaml | 19 |
| Module | Module.yaml | 28 |
| Post | Post_setting.yaml | 16 |

**Total: 69 test case entries** (after expansion)

---

## Post/Post_setting.yaml (16 cases)

| # | Test Case | Test Function | Description |
|---|-----------|---------------|-------------|
| 1 | T1742 | testT1742_BatchSetCommissionRate | Post commission batch set to 10% |
| 2 | T2069 | testT2069_ScrollAnnouncement | Scroll announcement (banners > 3) |
| 3 | T2705 | testT2705_HideVariant | Partner hides variant & sets default |
| 4 | T2830 | testT2830_HidePost | Partner hides a post on storefront |
| 5 | T2834 | testT2834_VerifyPartner/Guest | Verify partner hides post (partner + guest) |
| 6 | T3683 | testT3683_VerifyPartner | Order confirmation note — Partner edit |
| 7 | T3684 | testT3683_VerifyGuest | Order confirmation note — Guest verification |
| 8 | T3686 | testT3686_CosellerInherited | Coseller inherits non-edit order notes |
| 9 | T3963 | testT3963_ShippingFeeLogic | Shipping fee logic (Catalog_Fulfillment) |
| 10 | T4038 | testT4038_EditAnnouncement | Edit announcement |
| 11 | T4735 | testT4735_VerifyPartner/Guest | Redirect URL enabled |
| 12 | T4735_YesPlease | testT4735_VerifyGuest_YesPlease | Redirect modal — Yes please |
| 13 | T4735_NoThanks | testT4735_VerifyGuest_NoThanks | Redirect modal — No thanks |
| 14 | T2515 | testT2515_SetLimit_WithVariant | Purchase limit 5 units (variants product) |
| 15 | T2874 | testT2874_EnableDependentProducts | Must be bought with another item |
| 16 | T5033 | testT5033_5034_VerifyPartner | Choose CTA type — View options |
| 17 | T5034 | (same function) | Choose CTA type — Add to cart / View Product |
| 18 | T4955 | testT4955_Partner_SetPaymentRestriction | Payment Restriction — set access code |

**After expansion of merged cases: 16 independent IDs**

---

## Events/Scanner.yaml (1 case, with 3 sub-cases)

| # | Test Case | Test Function | Description |
|---|-----------|---------------|-------------|
| 1 | T3981 | testT3981_Verified | QR Scanner — checked in |
| 2 | (T3981) | testT3981_Already | QR Scanner — duplicate check-in |
| 3 | (T3981) | testT3981_NotRecognized | QR Scanner — unrecognized |

---

## Events/Sync_event_post.yaml (1 case, with 2 sub-cases)

| # | Test Case | Test Function | Description |
|---|-----------|---------------|-------------|
| 1 | T4984 | testT4984_partner | Add product via enhance button |
| 2 | (T4984) | testT4984_guest | Guest verifies product addition |

---

## Module/Module.yaml (28 cases)

| # | Test Case | Test Function | Description |
|---|-----------|---------------|-------------|
| 1 | T3554 | testT3554 | Module-related |
| 2 | T3555 | testT3555 | Module-related |
| 3 | T3556 | testT3556 | Module-related |
| 4 | T3577 | testT3577 | Module-related |
| 5 | T3788 | testT3788 | Module-related |
| 6 | T3789 | testT3789 | Module-related |
| 7 | T3841 | testT3841 | Module-related |
| 8 | T3842 | testT3842 | Module-related |
| 9 | T3843 | testT3843 | Module-related |
| 10 | T3886 | testT3886_long | Module-related (long text) |
| 11 | (T3886) | testT3886_short | Module-related (short text) |
| 12 | T4264 | testT4264 | Module-related |
| 13 | T4556 | testT4556 | Module-related |
| 14 | T4559 | testT4559 | Module-related |
| 15 | T4602 | testT4602 | Module-related |
| 16 | T4603 | testT4603 | Module-related |
| 17 | T4605 | testT4605 | Module-related |
| 18 | T4622 | testT4622 | Module-related |
| 19 | T4660 | testT4660 | Module-related |
| 20 | T4816 | testT4816 | Module-related |
| 21 | T4852 | testT4852 | Module-related |
| 22 | T4853 | testT4853 | Module-related |
| 23 | T4903 | testT4903 | Module-related |
| 24 | T4908 | testT4908 | Module-related |
| 25 | T5105 | testT5105 | Module-related |
| 26 | T5210 | testT5210_5211_5212 | Module-related (merged IDs) |
| 27 | T5211 | (same function) | Module-related (merged IDs) |
| 28 | T5212 | (same function) | Module-related (merged IDs) |
| 29 | addNewPost | testAddNewPost | Module — add new Post |
| 30 | addNewUpdateModule | testAddNewUpdateModule | Module — add and update |

**After expansion of merged cases: 28 independent IDs**

---

## Form/Storefront_form.yaml (4 cases)

| # | Test Case | Test Function | Description |
|---|-----------|---------------|-------------|
| 1 | — | testPartner_create_form | Partner creates form |
| 2 | — | test_guest_submission_1 | Guest submission (submission 1) |
| 3 | — | test_guest_submission_2 | Guest submission (submission 2) |
| 4 | — | testPartner_verify_commission | Partner verifies commission |

---

## Form/Storefront_product_with_form.yaml (19 cases)

| # | Test Case | Test Function | Description |
|---|-----------|---------------|-------------|
| 1 | T3690 | testT3690 | Storefront product with form |
| 2 | T3695 | testT3695_config_form | Curator form config |
| 3 | T3695 | testT3695_curator | Curator form |
| 4 | T3695 | testT3695_guest | Guest verifies form |
| 5 | T3794 | testT3794 | Storefront-related |
| 6 | T4276 | testT4276 | Storefront product-related |
| 7 | T4281 | testT4281 | Storefront product-related |
| 8 | T4539 | testT4539 | Storefront product-related |
| 9 | T4540 | testT4540 | Storefront product-related |
| 10 | T4790 | testT4790 | Storefront product-related |
| 11 | T4847 | testT4847 | Storefront product-related |
| 12 | T4847 | testT4847_view | Storefront product-related |
| 13 | T4847 | testT4847_destroy | Storefront product-related |
| 14 | T4860 | testT4860 | Storefront product-related |
| 15 | T4866 | testT4866 | Storefront product-related |
| 16 | T4867 | testT4867 | Storefront product-related |
| 17 | T4955 | testT4955 | Storefront product-related |
| 18 | T4970 | testT4970 | Storefront product-related |
| 19 | T5006 | testT5006_curator | Storefront product-related |
| 20 | T5007 | testT5007 | Storefront product-related |

---

## Merged Case Expansion Rules

When the following YAML patterns appear, they need to be split into independent case IDs:

| YAML Pattern | Expands To |
|-------------|-----------|
| `T5033_5034` | T5033, T5034 |
| `T3683 & T3684` | T3683, T3684 |
| `T5210_5211_5212` | T5210, T5211, T5212 |
| `T4735_YesPlease` | Variant of T4735, same ID |
| `T3981_Already` | Variant of T3981, same ID |

---

## Statistics Summary

```
Events:        2  test case files
Form:          2  test case files
Module:        1  test case file
Post:          1  test case file
─────────────────────────────
Total:         6  YAML files

Post:          16 independent test case IDs
Events:         2 test case IDs (T3981, T4984)
Module:        28 independent test case IDs
Form:          23 independent test case IDs (incl. 4 unnumbered functions)

Total:         69 test case entries
  - Numbered:     45
  - Unnumbered:    4 (Storefront_form.yaml)
  - Variants:    20 (partner/guest variants of same IDs)
```
