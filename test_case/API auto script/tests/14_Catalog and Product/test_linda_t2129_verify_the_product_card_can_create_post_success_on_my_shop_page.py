"""Migrated from Apifox case #7674680. Source folder: Catalog and Product."""
# Apifox Case ID: 7674680  (traceability only — not needed to run)
NAME = "Verify the Product card can create post success on my shop page"
TAGS = ["p0", "catalog_and_product", "suite:linda"]
PRIORITY = 0


CASE_ID = 7674680
ENV_NAME = "Release"

# --- step 1: 20e3754a-3578-4b57-90b9-60d5e67b8853 ---
# pre: try {
# pre:   // 原脚本所有逻辑
# pre:   const timestamp = Date.now().toString().slice(-7);
# pre:   const postTitleValue = `Automation test T2129 ${timestamp}`;
# pre:   pm.environment.set('posttitle', postTitleValue);
# pre: 
# pre:   function getRandomChars(len, type = 'letters') {
# pre:     const chars = type === 'letters' ? 'abcdefghijklmnopqrstuvwxyz' : '0123456789';
# pre:     let result = '';
# pre:     for (let i = 0; i < len; i++) {
# pre:       result += chars[Math.floor(Math.random() * chars.length)];
# pre:     }
# pre:     return result;
# pre:   }
# pre: 
# pre:   const urlAlias = `${getRandomChars(6)}${getRandomChars(6, 'nums')}`;
# pre:   pm.environment.set('urlAlias', urlAlias);
# pre: 
# pre:   console.log(`生成posttitle：${postTitleValue}`);
# pre:   console.log(`生成urlAlias：${urlAlias}`);
# pre: } catch (error) {
# pre:   console.error('脚本执行失败：', error.message);
# pre:   throw new Error(`前置脚本执行异常：${error.message}`); // 中断请求，便于定位
# pre: }
# post[customScript]: // 1. 引入assert模块（解决assert未定义问题）
# post: const assert = require('assert');
# post: 
# post: // 2. 正确获取JSON格式的接口响应体
# post: const responseBody = pm.response.json();
# post: 
# post: try {
# post:   // 3. 校验核心返回值
# post:   // 校验code是否为200
# post:   assert.equal(responseBody.code, 200, `接口返回code错误，预期200，实际${responseBody.code}`);
# post:   // 校验message是否为success
# post:   assert.equal(responseBody.message, "success", `接口返回message错误，预期success，实际${responseBody.message}`);
# post:   // 校验data存在且status为ACTIVE
# post:   assert.ok(responseBody.data, "接口返回data字段不存在");
# post:   assert.equal(responseBody.data.status, "ACTIVE", `data.status错误，预期ACTIVE，实际${responseBody.data.status}`);
# post: 
# post:   // 4. 提取data.id并存入环境变量
# post:   const postId = responseBody.data.id;
# post:   pm.environment.set("post_id", postId); 
# post: 
# post:   // 5. 日志提示
# post:   console.log("接口校验通过！");
# post:   console.log(`提取的post_id：${postId}，已存入环境变量`);
# post: 
# post: } catch (error) {
# post:   // 6. 校验失败抛出异常
# post:   console.error("接口校验失败：", error.message);
# post:   throw new Error(`后置脚本校验失败：${error.message}`);
# post: }
# --- step 2: db3ae71c-5ae8-4737-b52a-d305261dc6cc ---
# post[customScript]: // ========== 步骤1：解析删除接口响应，提取post_id ==========
# post: try {
# post:     const deleteResponse = pm.response.json();
# post:     
# post:     pm.test("删除接口响应格式正确", () => {
# post:         pm.expect(deleteResponse.code).to.equal(200);
# post:         pm.expect(deleteResponse.data.id).to.not.be.empty;
# post:     });
# post:     
# post:     const postId = deleteResponse.data.id;
# post:     console.log("待验证的post_id：", postId);
# post: 
# post:     // ========== 步骤2：获取创建post时的实际urlAlias（必须从环境变量取，无默认值） ==========
# post:     const urlAlias = pm.environment.get("urlAlias");
# post:     if (!urlAlias) {
# post:         throw new Error("请先在【创建post接口】的后置脚本中，将实际urlAlias存入created_post_urlAlias环境变量");
# post:     }
# post:     console.log("创建post时的实际urlAlias：", urlAlias);
# post: 
# post:     // ========== 步骤3：构造查询接口URL（完全用实际参数） ==========
# post:     const baseUrl = "https://release.katana-api.1m.app";
# post:     const vanityUrl = pm.environment.get("created_post_vanityUrl") || "lindazhoucurator"; // 同理同步创建时的vanityUrl
# post:     const affiliateCode = "";
# post: 
# post:     // 拼接URL（用创建时的实际urlAlias）
# post:     const queryPostUrl = `${baseUrl}/posts/consumer/detail?vanityUrl=${vanityUrl}&urlAlias=${urlAlias}&affiliateCode=${affiliateCode}`;
# post:     console.log("最终查询URL（匹配创建参数）：", queryPostUrl);
# post: 
# post:     // ========== 步骤4：验证删除 ==========
# post:     pm.sendRequest({
# post:         url: queryPostUrl,
# post:         method: "GET",
# post:         header: { "Content-Type": "application/json" }
# post:     }, (err, res) => {
# post:         pm.test("查询接口请求正常", () => pm.expect(err).to.be.null);
# post:         
# post:         pm.test("验证post已删除", () => {
# post:             const queryRes = res.json();
# post:             pm.expect(queryRes.code).to.not.equal(200);
# post:             pm.expect(queryRes.message).to.include("Requested resource not found");
# post:         });
# post:     });
# post: 
# post: } catch (e) {
# post:     pm.test("脚本异常", () => pm.expect.fail(e.message));
# post:     console.error("错误：", e);
# post: }




import json

from core.assertions import expect

from core.compat import LegacyClient, legacy_render, legacy_url

def test_linda_t2129_verify_the_product_card_can_create_post_success_on_my_shop_page(ctx):
    """Apifox case #7674680: Linda_T2129_Verify_the_Product_card_can_create_post_success_on_my_shop_page"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    base_url = ctx.base_url
    client = LegacyClient(ctx)
    _render = legacy_render(ctx)
    _url = legacy_url(ctx)
    # === Steps ===
    # step 1: 20e3754a-3578-4b57-90b9-60d5e67b8853
    _resp1 = ctx.api.posts.curator(body='{\r\n    "title": "{{posttitle}}",\r\n    "links": [],\r\n    "allowPromotersResell": true,\r\n    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",\r\n    "status": "ACTIVE",\r\n    "allowPromotersHideProducts": true,\r\n    "allowPromotersCustomizeMedia": true,\r\n    "isPurchaseQuantityLimited": false,\r\n    "purchaseQuantityLimit": 1,\r\n    "styleSettings": {\r\n        "template": "ShadowFocus",\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "displayText": "SHOP_NAME",\r\n                "height": "MEDIUM"\r\n            },\r\n            "productBanner": {\r\n                "ctaButton": "VIEW_PRODUCT",\r\n                "display": "HIDE"\r\n            }\r\n        },\r\n        "fontFamily": "Replica Mono LL",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "secondaryTextColor": "#ABABAB",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontFamily": "Inter",\r\n            "fontSize": 30,\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "fontFamily": "Inter",\r\n            "fontSize": 20,\r\n            "fontWeight": 700,\r\n            "color": "#FFFFFF"\r\n        },\r\n        "subtitle": {\r\n            "fontFamily": "Replica Mono LL",\r\n            "fontSize": 20,\r\n            "fontWeight": 400,\r\n            "color": "#FFFFFF"\r\n        },\r\n        "button": {\r\n            "backgroundColor": "#F6CA7C",\r\n            "color": "#000000",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "boxShadow": "none",\r\n            "fontSize": 16,\r\n            "fontWeight": 400\r\n        },\r\n        "secondaryButton": {\r\n            "fontSize": 16,\r\n            "fontWeight": 400,\r\n            "color": "#FFFFFF",\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 0,\r\n            "boxShadow": "none"\r\n        },\r\n        "textButton": {\r\n            "fontSize": 16,\r\n            "fontWeight": 700,\r\n            "color": "#FFFFFF"\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "borderRadius": 0,\r\n            "color": "#000000 ",\r\n            "borderColor": "#0000",\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "color": "#FFFFFF",\r\n            "secondaryTextColor": "#ABABAB",\r\n            "title": {\r\n                "fontFamily": "Replica Mono LL",\r\n                "fontSize": 14,\r\n                "fontWeight": 400,\r\n                "color": "#FFFFFF"\r\n            }\r\n        },\r\n        "product": {\r\n            "backgroundColor": "#000000",\r\n            "borderRadius": 0,\r\n            "color": "#FFFFFF",\r\n            "secondaryTextColor": "#ABABAB"\r\n        },\r\n        "discount": {\r\n            "backgroundColor": "#D32A09",\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF"\r\n        },\r\n        "freeShipping": {\r\n            "backgroundColor": "#EBF5EF",\r\n            "color": "#268E46"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "title": {\r\n                "fontFamily": "Inter",\r\n                "fontSize": 16,\r\n                "fontWeight": 700,\r\n                "color": "#FFFFFF"\r\n            },\r\n            "color": "#FFFFFF",\r\n            "secondaryTextColor": "#ABABAB",\r\n            "button": {\r\n                "backgroundColor": "#F6CA7C",\r\n                "color": "#000000"\r\n            }\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#9E9E9E",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 0\r\n            }\r\n        },\r\n        "recentUsedColors": [\r\n            "#7132F4FF",\r\n            "#616161FF",\r\n            "#B7E2E0FF",\r\n            "#0B99FFFF",\r\n            "#E0E0E0FF",\r\n            "#F1BBFFFF",\r\n            "#F44336FF",\r\n            "#4A148CFF",\r\n            "#C5CAE9FF",\r\n            "#3F51B5FF",\r\n            "#ECA416FF",\r\n            "#110921FF",\r\n            "#303F9FFF",\r\n            "#8BC34AFF",\r\n            "#7986CBFF",\r\n            "#BA68C8FF",\r\n            "#CB135BFF",\r\n            "#E91E63FF"\r\n        ]\r\n    },\r\n    "variantSelectorType": "FULL_PAGE",\r\n    "abTestingSettings": [],\r\n    "enableAbTesting": false,\r\n    "featuredSectionTitle": "Featured products",\r\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\"><span data-id=\\"6155979f-16e8-4461-adf7-11741f58f66d\\" data-type=\\"event-info-banner\\" data-event-id=\\"f07e07c5-8146-43fb-9516-01f56a8593ba\\"></span></p><span data-id=\\"9259371b-7fa2-4d73-933d-41515df64875\\" data-type=\\"additional-content\\"></span><p class=\\"katana__paragraph katana__paragraph--align-left\\"><span data-id=\\"5c2bf0a7-353b-435b-8fe8-c40dbb098327\\" data-width=\\"100%\\" data-height=\\"\\" data-product-id=\\"21fc1b6e-2be1-4d66-9f70-b3c23fd5826d\\" data-available-purchase-types=\\"ONE_TIME\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\"></span></p><hr><p class=\\"katana__paragraph katana__paragraph--align-left\\"><span data-id=\\"7a27be5c-579a-41f4-afe9-2416e7d14ecc\\" data-type=\\"post-event-description\\" data-event-id=\\"f07e07c5-8146-43fb-9516-01f56a8593ba\\"></span></p>",\r\n    "currentDate": "2025-12-19T07:25:11.463Z",\r\n    "relatedProducts": [\r\n        {\r\n            "merchantProductId": "21fc1b6e-2be1-4d66-9f70-b3c23fd5826d",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "isDefaultToSubscription": false,\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 51,\r\n                    "price": 56.67,\r\n                    "costPrice": 0,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "6a8a3ae1-afca-4aa9-968a-5353affa3ae9",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "promotions": [],\r\n    "accessSpecificUser": [],\r\n    "allowPromotersCreateCoupon": true,\r\n    "featuredSectionEnable": true,\r\n    "allowAffiliateSharingOnly": false,\r\n    "hideCouponBox": false,\r\n    "checkoutInPost": true,\r\n    "tab": {\r\n        "value": "Commerce",\r\n        "label": "Commerce",\r\n        "mappingControl": []\r\n    },\r\n    "timeKey": 1766129113643,\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n            "width": 3072,\r\n            "height": 2048,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "eventFill": true,\r\n            "setThumbnail": true\r\n        }\r\n    ],\r\n    "customizeDisplayPrices": {\r\n        "price": "Liberty Island, New York, NY 10004 | Fri, Dec 19 (CST)",\r\n        "discountPercent": "Get Tickets",\r\n        "priceColor": "#F6CA7C",\r\n        "discountPercentColor": "#D32A08"\r\n    },\r\n    "redirectUrl": "",\r\n    "redirectDestinationName": "",\r\n    "syncEnabled": false,\r\n    "postType": "EVENT",\r\n    "canSetPrice": false,\r\n    "allowCustomizeDisplayPrices": true,\r\n    "createFromEventId": "f07e07c5-8146-43fb-9516-01f56a8593ba",\r\n    "recommendationSectionTitle": "",\r\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[{\\"id\\":\\"6155979f-16e8-4461-adf7-11741f58f66d\\",\\"eventId\\":\\"f07e07c5-8146-43fb-9516-01f56a8593ba\\",\\"type\\":\\"event-info-banner\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\"},{\\"id\\":\\"9259371b-7fa2-4d73-933d-41515df64875\\",\\"type\\":\\"additional-content\\",\\"version\\":1},{\\"children\\":[{\\"id\\":\\"5c2bf0a7-353b-435b-8fe8-c40dbb098327\\",\\"productId\\":\\"21fc1b6e-2be1-4d66-9f70-b3c23fd5826d\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"availablePurchaseTypes\\":[\\"ONE_TIME\\"],\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"event\\",\\"type\\":\\"show-product-banner\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\"},{\\"type\\":\\"horizontalrule\\",\\"version\\":1},{\\"children\\":[{\\"id\\":\\"7a27be5c-579a-41f4-afe9-2416e7d14ecc\\",\\"eventId\\":\\"f07e07c5-8146-43fb-9516-01f56a8593ba\\",\\"type\\":\\"post-event-description\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\r\n    "media": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n            "width": 3072,\r\n            "height": 2048,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "eventFill": true,\r\n            "setThumbnail": true\r\n        }\r\n    ],\r\n    "othersCanCopy": false,\r\n    "enableDownlineNote": false,\r\n    "expiredAt": null,\r\n    "urlAlias": "{{urlAlias}}",\r\n    "headline": "{{posttitle}}"\r\n}', token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    assert _j1.get('code') == 200, f"接口返回code错误，预期200，实际={_j1.get('code')!r}"
    assert _j1.get('message') == 'success', f"接口返回message错误，预期success，实际={_j1.get('message')!r}"
    _d1 = _j1.get('data')
    assert _d1, "接口返回data字段不存在"
    assert _d1.get('status') == 'ACTIVE', f"data.status错误，预期ACTIVE，实际={_d1.get('status')!r}"
    vars['post_id'] = _d1.get('id')
    # step 2: db3ae71c-5ae8-4737-b52a-d305261dc6cc
    _resp2 = ctx.api.posts.curator_by_post_id_2(body=None, token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"删除接口响应code错误，期望200，实际={_j2.get('code')!r}"
    assert _j2.get('data', {}).get('id'), f"删除接口data.id为空，实际={_j2.get('data')!r}"
    # 二次查询验证 post 已删除（原 customScript 逻辑：查询详情断言 code != 200 且 message 含 Requested resource not found）
    _ua = _render('{{urlAlias}}', vars)
    if _ua:
        _q = client.session().request(
            'GET',
            _url(base_url, f'/posts/consumer/detail?vanityUrl=lindazhoucurator&urlAlias={_ua}&affiliateCode=', vars),
            headers={k:_render(v, vars) for k, v in [('Authorization', 'Bearer {{linda01_token}}'), ('Content-Type', 'application/json')]},
            data=_render(None, vars) if False else None,
        )
        _qj = _q.json() if _q.headers.get('content-type', '').startswith('application/json') else {}
        assert _qj.get('code') != 200, f"验证post已删除失败：code应为非200，实际={_qj.get('code')!r}"
        assert 'Requested resource not found' in (_qj.get('message') or ''), f"删除验证message未包含预期文本，实际={_qj.get('message')!r}"
