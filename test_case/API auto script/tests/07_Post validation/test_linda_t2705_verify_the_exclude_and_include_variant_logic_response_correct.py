"""Migrated from Apifox case #8038375. Source folder: Post validation."""
# Apifox Case ID: 8038375  (traceability only — not needed to run)
NAME = "Verify the \"Exclude\"  and \u201cInclude\u201c variant logic response correct"
TAGS = ["p1", "post_validation", "suite:linda"]
PRIORITY = 1


CASE_ID = 8038375
ENV_NAME = "Release"

# --- step 1: 7bac97ce-2d5b-4b26-9ea3-b6c2303e1ab7 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: guest get token ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 3: Guest visit and check the varaint exclude and include response ---
# post[customScript]: // 解析响应体
# post: const responseData = pm.response.json();
# post: const relatedProduct = responseData.data.relatedProducts[0];
# post: const variants = relatedProduct.variants;
# post: 
# post: // 1. 断言特定变体的属性 (isExcluded 和 title)
# post: pm.test("校验特定 Variant 的 title 和 isExcluded 状态", function () {
# post:     variants.forEach(variant => {
# post:         if (variant.merchantProductVariantId === "8a77a74a-9b7e-47fa-9527-b4ffc34e7d06") {
# post:             pm.expect(variant.title).to.eql("18:00 AM");
# post:             pm.expect(variant.isExcluded).to.be.false;
# post:         }
# post:         
# post:         if (variant.merchantProductVariantId === "59b0c824-dd2d-450b-b858-3a6423432ebc") {
# post:             pm.expect(variant.title).to.eql("20:00 PM");
# post:             pm.expect(variant.isExcluded).to.be.false;
# post:         }
# post:     });
# post: });
# post: 
# post: // 2. 断言 displayVariantId 是否符合预期
# post: pm.test("校验 displayVariantId 为 07eb325b-e2f6-419c-96db-a5fd8fb7994c", function () {
# post:     pm.expect(relatedProduct.displayVariantId).to.eql("07eb325b-e2f6-419c-96db-a5fd8fb7994c");
# post: });
# post: 
# post: // 3. 断言不存在指定的 merchantProductVariantId
# post: pm.test("校验不存在特定的 merchantProductVariantId 列表", function () {
# post:     const excludedIds = [
# post:         "dbd67afc-4bab-45c2-b6a5-69ac1d23805b", 
# post:         "6b4dba36-9e0e-4123-ab7c-e95dd9e86d13"
# post:     ];
# post:     
# post:     // 获取当前响应中所有的 variantId
# post:     const currentVariantIds = variants.map(v => v.merchantProductVariantId);
# post:     
# post:     excludedIds.forEach(id => {
# post:         pm.expect(currentVariantIds).to.not.include(id, `不应该包含 ID: ${id}`);
# post:     });
# post: });
# --- step 4: Consumer visit and check the varaint exclude and include response ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 0;
# pre:     item_percentage_fee = 0.085;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: var order_level_transaction_fee = Number((4.99 * 0.085).toFixed(2));
# pre: var transaction_fee_item_level = Number((get_transaction_fee_item_level_general(1.33,1)).toFixed(2));
# pre: var p1_transaction_fee = Math.round(((0.16/1.33 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee = Math.round(((0.17/1.33 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - merchant_transaction_fee + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# pre: 
# post[customScript]: // 解析响应体
# post: const responseData = pm.response.json();
# post: const relatedProduct = responseData.data.relatedProducts[0];
# post: const variants = relatedProduct.variants;
# post: 
# post: // 1. 断言特定变体的属性 (isExcluded 和 title)
# post: pm.test("校验特定 Variant 的 title 和 isExcluded 状态", function () {
# post:     variants.forEach(variant => {
# post:         if (variant.merchantProductVariantId === "8a77a74a-9b7e-47fa-9527-b4ffc34e7d06") {
# post:             pm.expect(variant.title).to.eql("18:00 AM");
# post:             pm.expect(variant.isExcluded).to.be.false;
# post:         }
# post:         
# post:         if (variant.merchantProductVariantId === "59b0c824-dd2d-450b-b858-3a6423432ebc") {
# post:             pm.expect(variant.title).to.eql("20:00 PM");
# post:             pm.expect(variant.isExcluded).to.be.false;
# post:         }
# post:     });
# post: });
# post: 
# post: // 2. 断言 displayVariantId 是否符合预期
# post: pm.test("校验 displayVariantId 为 07eb325b-e2f6-419c-96db-a5fd8fb7994c", function () {
# post:     pm.expect(relatedProduct.displayVariantId).to.eql("07eb325b-e2f6-419c-96db-a5fd8fb7994c");
# post: });
# post: 
# post: // 3. 断言不存在指定的 merchantProductVariantId
# post: pm.test("校验不存在特定的 merchantProductVariantId 列表", function () {
# post:     const excludedIds = [
# post:         "dbd67afc-4bab-45c2-b6a5-69ac1d23805b", 
# post:         "6b4dba36-9e0e-4123-ab7c-e95dd9e86d13"
# post:     ];
# post:     
# post:     // 获取当前响应中所有的 variantId
# post:     const currentVariantIds = variants.map(v => v.merchantProductVariantId);
# post:     
# post:     excludedIds.forEach(id => {
# post:         pm.expect(currentVariantIds).to.not.include(id, `不应该包含 ID: ${id}`);
# post:     });
# post: });




import json

from core.assertions import expect

def test_linda_t2705_verify_the_exclude_and_include_variant_logic_response_correct(ctx):
    """Apifox case #8038375: Linda_T2705_Verify_the_Exclude_and_Include_variant_logic_response_correct"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 7bac97ce-2d5b-4b26-9ea3-b6c2303e1ab7
    _resp1 = ctx.api.posts.curator_de6f0abd_c8f8_41e5_b2d1_1eb2ba05f839(body='{\r\n    "id": "de6f0abd-c8f8-41e5-b2d1-1eb2ba05f839",\r\n    "announcements": null,\r\n    "createFromEventId": "8c911bb6-78ec-4af4-a78c-479a0416349d",\r\n    "title": "API TEST T2705",\r\n    "subTitle": "",\r\n    "links": [],\r\n    "allowPromotersResell": true,\r\n    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",\r\n    "financeMode": "FINANCE_MODE_COMMISSION",\r\n    "status": "ACTIVE",\r\n    "allowPromotersHideProducts": true,\r\n    "allowPromotersCustomizeMedia": true,\r\n    "allowPromotersCreateCoupon": true,\r\n    "promotions": [],\r\n    "isPurchaseQuantityLimited": false,\r\n    "purchaseQuantityLimit": 0,\r\n    "isAccessRestricted": false,\r\n    "allowPromotersAccess": false,\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#FFEEBEFF",\r\n            "#E91E63FF",\r\n            "#757575FF",\r\n            "#0B99FFFF",\r\n            "#F2F2F6FF",\r\n            "#FFFFFF"\r\n        ],\r\n        "fontFamily": "Replica Mono LL",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "dividerColor": "#CFCFCF",\r\n        "secondaryTextColor": "#ABABAB",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontSize": 30,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "subtitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Replica Mono LL",\r\n            "fontWeight": 400\r\n        },\r\n        "button": {\r\n            "color": "#000000",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "secondaryButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 0\r\n        },\r\n        "textButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "fontWeight": 700\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "color": "#000000",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 14,\r\n                "fontFamily": "Replica Mono LL",\r\n                "fontWeight": 400\r\n            },\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#ABABAB"\r\n        },\r\n        "product": {\r\n            "color": "#FFFFFF",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#ABABAB"\r\n        },\r\n        "discount": {\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF",\r\n            "backgroundColor": "#D32A09"\r\n        },\r\n        "freeShipping": {\r\n            "color": "#268E46",\r\n            "backgroundColor": "#EBF5EF"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 16,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 700\r\n            },\r\n            "button": {\r\n                "color": "#000000",\r\n                "backgroundColor": "#F6CA7C"\r\n            },\r\n            "secondaryTextColor": "#ABABAB"\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF",\r\n            "secondaryText": "#ABABAB"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#9E9E9E",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "height": "MEDIUM",\r\n                "displayText": "SHOP_NAME"\r\n            },\r\n            "productBanner": {\r\n                "display": "HIDE",\r\n                "ctaButton": "VIEW_PRODUCT"\r\n            }\r\n        },\r\n        "template": "ClearSky",\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 0\r\n            }\r\n        }\r\n    },\r\n    "hideInStore": false,\r\n    "recommendationSectionTitle": "",\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1773383669/uploaded_images/jlpay15cvcj9upgdlzw8.webp",\r\n            "width": 2560,\r\n            "height": 3413,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "setThumbnail": true\r\n        }\r\n    ],\r\n    "checkoutInPost": true,\r\n    "allowAffiliateSharingOnly": false,\r\n    "abTestingSettings": [],\r\n    "enableAbTesting": false,\r\n    "isOrderConfirmationNoteEnabled": false,\r\n    "hideCouponBox": false,\r\n    "allowCustomizeDisplayPrices": true,\r\n    "customizeDisplayPrices": {\r\n        "price": "Instagram Live, Zoom, In-person | Sat, Mar 14 (CDT)",\r\n        "discountPercent": "Get Tickets",\r\n        "titleColor": "#FFFFFF",\r\n        "priceColor": "#FFFFFF",\r\n        "discountPercentColor": "#D32A08"\r\n    },\r\n    "canSetPrice": false,\r\n    "downlineNoteBodyHtml": null,\r\n    "downlineNoteBodyJson": null,\r\n    "featuredSectionTitle": "",\r\n    "enableRedirectUrl": false,\r\n    "redirectUrl": "",\r\n    "redirectDestinationName": "",\r\n    "cardCustomizeCoverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1773383669/uploaded_images/jlpay15cvcj9upgdlzw8.webp",\r\n            "width": 2560,\r\n            "height": 3413,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "setThumbnail": true\r\n        }\r\n    ],\r\n    "event": {\r\n        "id": "8c911bb6-78ec-4af4-a78c-479a0416349d",\r\n        "status": "UPCOMING",\r\n        "title": "API Test for multiple variants",\r\n        "venue": "Instagram Live, Zoom, In-person",\r\n        "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",\r\n        "startDateDisplay": "2026-03-20 01:37",\r\n        "endDateDisplay": "2032-03-20",\r\n        "timezone": {\r\n            "dstOffset": 3600,\r\n            "rawOffset": -21600,\r\n            "timeZoneId": "America/Chicago",\r\n            "timeZoneName": "Central Daylight Time"\r\n        },\r\n        "poster": {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1773383669/uploaded_images/jlpay15cvcj9upgdlzw8.webp",\r\n            "width": 2560,\r\n            "height": 3413,\r\n            "position": 0,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    },\r\n    "additionalContentPosition": "aboveTickets",\r\n    "bodyHtml": "<div class=\\"lexical-root\\"><div class=\\"katana-paragraph\\"><div class=\\"event-info-banner\\" data-event-id=\\"8c911bb6-78ec-4af4-a78c-479a0416349d\\" data-node-id=\\"71fa0b33-d07e-4490-a518-eb61a49b5129\\">Event Info</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"8c911bb6-78ec-4af4-a78c-479a0416349d\\" data-product-id=\\"06099c59-48d6-494b-be00-74ee20e78f75\\" data-node-id=\\"3e045651-f7f1-49f6-88df-1c836e5baf07\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><hr /></div><div class=\\"katana-paragraph\\"><span style=\\"font-size: 20px;\\"><strong>Missed our last event?  everything is ok.</strong></span></div><div class=\\"katana-paragraph\\">Everything is well. Here\'s a lil recap of our last event👇</div><div class=\\"katana-paragraph\\"><br></div><div class=\\"katana-paragraph\\"><img src=\\"https://res.cloudinary.com/dr9io1zjv/v1773383675/uploaded_images/zmqf8vdwsuza5qqkqc70.webp\\" alt=\\"placeholder image\\" style=\\"width: 100%; height: 100%;\\" /></div><div class=\\"katana-paragraph\\"><img src=\\"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/t0lafz3hk5sfnvv70jpc.webp\\" alt=\\"placeholder image\\" style=\\"width: 100%; height: 100%;\\" /></div><div class=\\"katana-paragraph\\"><img src=\\"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/lecifjjuftkjxjmizgg9.webp\\" alt=\\"placeholder image\\" style=\\"width: 100%; height: 100%;\\" /></div><div class=\\"katana-paragraph\\"><hr /></div><div class=\\"katana-paragraph\\"><div class=\\"lineup-info-banner\\" data-node-id=\\"daa924b4-684e-4881-ae35-d23ad2ed8879\\">Lineup</div></div></div>",\r\n    "currentDate": "2026-03-17T06:42:42.734Z",\r\n    "relatedProducts": [\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "06099c59-48d6-494b-be00-74ee20e78f75",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": [],\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 21,\r\n                    "price": 23.33,\r\n                    "costPrice": 0,\r\n                    "isExcluded": true,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "dbd67afc-4bab-45c2-b6a5-69ac1d23805b",\r\n                    "commissionRateForPromoters": 10\r\n                },\r\n                {\r\n                    "wholesalePriceForPromoters": 31,\r\n                    "price": 34.44,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "8a77a74a-9b7e-47fa-9527-b4ffc34e7d06",\r\n                    "commissionRateForPromoters": 10\r\n                },\r\n                {\r\n                    "wholesalePriceForPromoters": 41,\r\n                    "price": 45.56,\r\n                    "costPrice": 0,\r\n                    "isExcluded": true,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "6b4dba36-9e0e-4123-ab7c-e95dd9e86d13",\r\n                    "commissionRateForPromoters": 10\r\n                },\r\n                {\r\n                    "wholesalePriceForPromoters": 51,\r\n                    "price": 56.67,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "59b0c824-dd2d-450b-b858-3a6423432ebc",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "accessSpecificUser": [],\r\n    "featuredSectionEnable": false,\r\n    "tab": {\r\n        "value": "Commerce",\r\n        "label": "Commerce",\r\n        "mappingControl": []\r\n    },\r\n    "timeKey": 1773729762734,\r\n    "originEnablePaymentRestriction": false,\r\n    "syncEnabled": true,\r\n    "postType": "EVENT",\r\n    "bodyJson": "{\\"root\\":{\\"type\\":\\"root\\",\\"children\\":[{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"event-info-banner\\",\\"id\\":\\"71fa0b33-d07e-4490-a518-eb61a49b5129\\",\\"eventId\\":\\"8c911bb6-78ec-4af4-a78c-479a0416349d\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"id\\":\\"6f7693fa-1ff2-49aa-8cb0-209fe5118a56\\",\\"type\\":\\"additional-content\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"3e045651-f7f1-49f6-88df-1c836e5baf07\\",\\"eventId\\":\\"8c911bb6-78ec-4af4-a78c-479a0416349d\\",\\"productId\\":\\"06099c59-48d6-494b-be00-74ee20e78f75\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"horizontalrule\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"extended-text\\",\\"text\\":\\"Missed our last event?  everything is ok.\\",\\"format\\":1,\\"version\\":1,\\"style\\":\\"font-size: 20px;\\"}],\\"direction\\":\\"ltr\\",\\"format\\":\\"left\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"extended-text\\",\\"text\\":\\"Everything is well. Here\'s a lil recap of our last event👇\\",\\"format\\":0,\\"version\\":1}],\\"direction\\":\\"ltr\\",\\"format\\":\\"left\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"center\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"media\\",\\"src\\":\\"https://res.cloudinary.com/dr9io1zjv/v1773383675/uploaded_images/zmqf8vdwsuza5qqkqc70.webp\\",\\"imageSrc\\":\\"https://res.cloudinary.com/dr9io1zjv/v1773383675/uploaded_images/zmqf8vdwsuza5qqkqc70.webp\\",\\"srcId\\":\\"16c31e48-e469-4604-9f94-d399ee519551\\",\\"mediaType\\":\\"IMAGE\\",\\"width\\":\\"100%\\",\\"height\\":\\"100%\\",\\"baseWidth\\":474,\\"baseHeight\\":265,\\"unit\\":\\"PERCENT\\",\\"altText\\":\\"placeholder image\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"media\\",\\"src\\":\\"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/t0lafz3hk5sfnvv70jpc.webp\\",\\"imageSrc\\":\\"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/t0lafz3hk5sfnvv70jpc.webp\\",\\"srcId\\":\\"344557a6-647c-40e5-b4ab-f9d5eba10f0a\\",\\"mediaType\\":\\"IMAGE\\",\\"width\\":\\"100%\\",\\"height\\":\\"100%\\",\\"baseWidth\\":1440,\\"baseHeight\\":1152,\\"unit\\":\\"PERCENT\\",\\"altText\\":\\"placeholder image\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"media\\",\\"src\\":\\"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/lecifjjuftkjxjmizgg9.webp\\",\\"imageSrc\\":\\"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/lecifjjuftkjxjmizgg9.webp\\",\\"srcId\\":\\"8d90c52a-b95c-4ddb-970d-8c90e07b5c71\\",\\"mediaType\\":\\"IMAGE\\",\\"width\\":\\"100%\\",\\"height\\":\\"100%\\",\\"baseWidth\\":1192,\\"baseHeight\\":710,\\"unit\\":\\"PERCENT\\",\\"altText\\":\\"placeholder image\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"horizontalrule\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"lineup-info-banner\\",\\"id\\":\\"daa924b4-684e-4881-ae35-d23ad2ed8879\\",\\"lineupItems\\":[{\\"id\\":\\"47f88972-05aa-4668-83ef-095472aa8f18\\",\\"order\\":0,\\"eventId\\":\\"8c911bb6-78ec-4af4-a78c-479a0416349d\\",\\"isHeadliner\\":false}],\\"width\\":\\"100%\\",\\"layout\\":\\"WITHOUT_HEADLINER\\",\\"photoShape\\":\\"RECTANGLE\\",\\"textAlignment\\":\\"CENTER\\",\\"headliner\\":{\\"width\\":\\"100%\\"},\\"headlinerTitle\\":\\"Headliner\\",\\"otherSectionTitle\\":\\"Talent\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1}],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"version\\":1},\\"containerClassName\\":\\"\\",\\"editorClassName\\":\\"\\"}",\r\n    "needRefreshHTML": true,\r\n    "additionalContent": "{}",\r\n    "showAdditionalContent": false,\r\n    "media": [\r\n        {\r\n            "id": "c1849e1b-dfb7-4553-94de-00e5d5c29719",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1773383669/uploaded_images/jlpay15cvcj9upgdlzw8.webp",\r\n            "selected": true,\r\n            "type": "IMAGE",\r\n            "height": 3413,\r\n            "width": 2560,\r\n            "mediaDuration": 0,\r\n            "mediaSrc": null,\r\n            "mediaType": "IMAGE",\r\n            "inherited": true,\r\n            "position": 1,\r\n            "referenceId": null,\r\n            "source": null,\r\n            "setThumbnail": false\r\n        }\r\n    ],\r\n    "othersCanCopy": false,\r\n    "enableDownlineNote": false,\r\n    "expiredAt": null,\r\n    "urlAlias": "api-test-2705",\r\n    "headline": "API TEST T2705",\r\n    "isPaymentRestrictionEnabled": false\r\n}', token='linda05_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # assertion 1.assertion: responseJson equal ACTIVE
    expect(_resp1).json('$.data.status').equals('ACTIVE')
    # step 2: guest get token
    _resp2 = ctx.api.auth.guest_login(body='{\n    "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda"\n}')
    vars['access_token'] = (_resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 3: Guest visit and check the varaint exclude and include response
    _resp3 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-2705'})
    # step 4: Consumer visit and check the varaint exclude and include response
    _resp4 = ctx.api.posts.consumer_detail(token='linda10_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-2705'})
