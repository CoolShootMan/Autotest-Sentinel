"""Auto-generated from Apifox case #6111855. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 6111855
# Folder: 
# Case: (Linda)T2810 Verify curator can set compared at price for my item when creating post
# Priority: P1
# Created: 2025-03-06T08:10:58.000Z
# Updated: 2026-08-25T07:43:58.000Z


CASE_ID = 6111855
ENV_NAME = "Release"

# --- step 1: Get Partner linda01 token ---
# pre: pm.environment.set("account_email_merchant","dian.yuhong.ext@1m.app");
# pre: pm.environment.set("password_merchant","178Ad6e0aF0Ec22Ab948d8c0c69Ae072");
# post[customScript]:     if(pm.response.to.have.status(201)){
# post:         var res = JSON.parse(responseBody);
# post:         pm.environment.set("merchant_access_token",res['data']['token']);
# post:     }
# post[extractor]: {"variableName": "linda01_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: update post related product's "compare at price" ---
# pre: 
# pre: 
# pre: // 生成一个 100 到 999 之间的随机整数
# pre: var CompareAtPrice = Math.floor(100 + Math.random() * 900);
# pre: 
# pre: // 设置环境变量
# pre: pm.environment.set("CompareAtPrice", CompareAtPrice);
# pre: 
# pre: // 打印变量值
# pre: console.log("CompareAtPrice is", CompareAtPrice);
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: Check the compare at price display correct ---
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{CompareAtPrice}}", "path": "$.data.relatedProducts[0].priceDisplayAnchor", "multipleValue": [], "extractSettings": {"expression": "$.data.relatedProducts[0].priceDisplayAnchor", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





from core.assertions import expect

def test__6111855__Linda_T2810_Verify_curator_can_set_compared_at_price_for_my_item_when_creating_post(ctx):
    """Apifox case #6111855: Linda_T2810_Verify_curator_can_set_compared_at_price_for_my_item_when_creating_p"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['account_email_merchant'] = 'dian.yuhong.ext@1m.app'
    vars['password_merchant'] = '178Ad6e0aF0Ec22Ab948d8c0c69Ae072'
    # step 1: Get Partner linda01 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+01@1m.app"\n}')
    ctx.extract('merchant_access_token', _resp1, '$.data.token')
    # extractor: linda01_token = $.data.token
    ctx.extract('linda01_token', _resp1, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    vars['postid'] = 'eb9c09da-7e3b-4c11-a735-00bc9d414275'
    import random as _random
    vars['CompareAtPrice'] = _random.randint(100, 999)
    # step 2: update post related product's "compare at price"
    _resp2 = ctx.api.posts.curator_by_post_id(body='{\r\n  "id": "{{postid}}",\r\n  "announcements": [],\r\n  "createFromEventId": "79a0ae94-a4dc-4bf8-bc24-7951d78f4237",\r\n  "title": "automation-t2810",\r\n  "subTitle": "",\r\n  "links": [],\r\n  "allowPromotersResell": false,\r\n  "financeModeForPromoters": "FINANCE_MODE_COMMISSION",\r\n  "financeMode": "FINANCE_MODE_WHOLESALE",\r\n  "status": "ACTIVE",\r\n  "allowPromotersHideProducts": false,\r\n  "allowPromotersCustomizeMedia": false,\r\n  "allowPromotersCreateCoupon": false,\r\n  "allowVisitorCreateAffiliateLink": false,\r\n  "promotions": [],\r\n  "isPurchaseQuantityLimited": false,\r\n  "purchaseQuantityLimit": 0,\r\n  "isAccessRestricted": false,\r\n  "allowPromotersAccess": false,\r\n  "styleSettings": {\r\n    "recentUsedColors": [\r\n      "#110921FF",\r\n      "#ECA416FF",\r\n      "#B7E2E0FF",\r\n      "#BA68C8FF",\r\n      "#CB135BFF",\r\n      "#F1BBFFFF",\r\n      "#E91E63FF",\r\n      "#0B99FFFF",\r\n      "#FFFFFFFF",\r\n      "#000000FF",\r\n      "#FFE0B2FF",\r\n      "#FACA4EFF",\r\n      "#EEEEEE",\r\n      "#3F51B5",\r\n      "#7132F4",\r\n      "#8BC34A",\r\n      "#000000"\r\n    ],\r\n    "fontFamily": "Replica Mono LL",\r\n    "color": "#FFFFFF",\r\n    "backgroundColor": "#000000",\r\n    "borderColor": "#000000",\r\n    "secondaryTextColor": "#ABABAB",\r\n    "announcementCarousel": {\r\n      "color": "#000000",\r\n      "backgroundColor": "#F6CA7C"\r\n    },\r\n    "title": {\r\n      "color": "#F6CA7C",\r\n      "fontSize": 30,\r\n      "fontFamily": "Inter",\r\n      "fontWeight": 700\r\n    },\r\n    "columnTitle": {\r\n      "color": "#FFFFFF",\r\n      "fontSize": 20,\r\n      "fontFamily": "Inter",\r\n      "fontWeight": 700\r\n    },\r\n    "subtitle": {\r\n      "color": "#FFFFFF",\r\n      "fontSize": 20,\r\n      "fontFamily": "Replica Mono LL",\r\n      "fontWeight": 400\r\n    },\r\n    "button": {\r\n      "color": "#000000",\r\n      "fontSize": 16,\r\n      "boxShadow": "none",\r\n      "fontWeight": 400,\r\n      "borderColor": "#0000",\r\n      "borderRadius": 0,\r\n      "backgroundColor": "#F6CA7C"\r\n    },\r\n    "secondaryButton": {\r\n      "color": "#FFFFFF",\r\n      "fontSize": 16,\r\n      "boxShadow": "none",\r\n      "fontWeight": 400,\r\n      "borderColor": "#F6CA7C",\r\n      "borderRadius": 0\r\n    },\r\n    "textButton": {\r\n      "color": "#FFFFFF",\r\n      "fontSize": 16,\r\n      "fontWeight": 700\r\n    },\r\n    "selectButton": {\r\n      "borderColor": "#000000"\r\n    },\r\n    "relatedLink": {\r\n      "color": "#000000 ",\r\n      "borderColor": "#0000",\r\n      "borderRadius": 0,\r\n      "backgroundColor": "#FFFFFF80"\r\n    },\r\n    "featuredProducts": {\r\n      "color": "#FFFFFF",\r\n      "title": {\r\n        "color": "#FFFFFF",\r\n        "fontSize": 14,\r\n        "fontFamily": "Replica Mono LL",\r\n        "fontWeight": 400\r\n      },\r\n      "borderRadius": 0,\r\n      "backgroundColor": "#000000",\r\n      "secondaryTextColor": "#ABABAB"\r\n    },\r\n    "product": {\r\n      "color": "#FFFFFF",\r\n      "borderRadius": 0,\r\n      "backgroundColor": "#000000",\r\n      "secondaryTextColor": "#ABABAB"\r\n    },\r\n    "discount": {\r\n      "color": "#FFFFFF",\r\n      "priceColor": "#FFFFFF",\r\n      "backgroundColor": "#D32A09"\r\n    },\r\n    "freeShipping": {\r\n      "color": "#268E46",\r\n      "backgroundColor": "#EBF5EF"\r\n    },\r\n    "starRatingColor": "#FAAF03",\r\n    "layoutFeatureCard": {\r\n      "color": "#FFFFFF",\r\n      "title": {\r\n        "color": "#FFFFFF",\r\n        "fontSize": 16,\r\n        "fontFamily": "Inter",\r\n        "fontWeight": 700\r\n      },\r\n      "button": {\r\n        "color": "#000000",\r\n        "backgroundColor": "#F6CA7C"\r\n      },\r\n      "secondaryTextColor": "#ABABAB"\r\n    },\r\n    "lineupBanner": {\r\n      "titleText": "#FFFFFF",\r\n      "descriptionText": "#F6CA7C"\r\n    },\r\n    "eventInfoBanner": {\r\n      "text": "#FFFFFF"\r\n    },\r\n    "eventDescription": {\r\n      "text": "#9E9E9E",\r\n      "title": "#FFFFFF"\r\n    },\r\n    "layout": {\r\n      "pageHeader": {\r\n        "style": "DEDICATED_HEADER_BAR",\r\n        "height": "MEDIUM",\r\n        "displayText": "SHOP_NAME"\r\n      },\r\n      "productBanner": {\r\n        "display": "HIDE",\r\n        "ctaButton": "VIEW_PRODUCT"\r\n      }\r\n    },\r\n    "template": "ShadowFocus",\r\n    "featuredProduct": {\r\n      "cover": {\r\n        "borderRadius": 0\r\n      }\r\n    }\r\n  },\r\n  "hideInStore": false,\r\n  "recommendationSectionTitle": "",\r\n  "coverImages": [\r\n    {\r\n      "id": "5b31fd19-d72d-42e9-91e8-e4d3c6df62b9",\r\n      "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n      "selected": true,\r\n      "type": "IMAGE",\r\n      "height": 2048,\r\n      "width": 3072,\r\n      "mediaDuration": 0,\r\n      "mediaSrc": null,\r\n      "mediaType": "IMAGE",\r\n      "inherited": false,\r\n      "position": 1,\r\n      "referenceId": null,\r\n      "source": null,\r\n      "setThumbnail": true\r\n    }\r\n  ],\r\n  "checkoutInPost": true,\r\n  "allowAffiliateSharingOnly": false,\r\n  "abTestingSettings": [],\r\n  "enableAbTesting": false,\r\n  "isOrderConfirmationNoteEnabled": false,\r\n  "hideCouponBox": false,\r\n  "allowCustomizeDisplayPrices": true,\r\n  "customizeDisplayPrices": {\r\n    "price": "Instagram Live, Zoom, In-person | Fri, Dec 05, 2025 12:00 AM - Sat, Dec 13, 2025 12:00 AM (CST)",\r\n    "priceColor": "#F6CA7C",\r\n    "discountPercent": "Get Tickets",\r\n    "discountPercentColor": "#D32A08"\r\n  },\r\n  "canSetPrice": true,\r\n  "downlineNoteBodyHtml": null,\r\n  "downlineNoteBodyJson": null,\r\n  "featuredSectionTitle": "Featured products",\r\n  "bodyHtml": "<p class=\\"katana__paragraph--align-left\\"><span data-id=\\"fc25524a-0380-4d63-885e-4b553fb0d602\\" data-type=\\"event-info-banner\\" data-event-id=\\"79a0ae94-a4dc-4bf8-bc24-7951d78f4237\\"></span></p><p class=\\"katana__paragraph--align-left\\"><span data-id=\\"143dd2b7-6c55-4664-958b-0b9988963d4a\\" data-width=\\"100%\\" data-height=\\"\\" data-product-id=\\"5eed9a05-008f-40ab-a984-403cb2217e07\\" data-available-purchase-types=\\"ONE_TIME\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\"></span></p>",\r\n  "currentDate": "2025-12-10T06:28:58.631Z",\r\n  "relatedProducts": [\r\n    {\r\n      "type": "PRODUCT",\r\n      "merchantProductId": "5eed9a05-008f-40ab-a984-403cb2217e07",\r\n      "isVisible": true,\r\n      "isPurchaseQuantityLimited": false,\r\n      "isRecommendation": false,\r\n      "hasDependentProducts": false,\r\n      "dependentProductIds": [],\r\n      "isFreeShipping": false,\r\n      "isDefaultToSubscription": false,\r\n      "toReplaceMerchantProductId": null,\r\n      "syncWithCatalogPrice": false,\r\n      "purchaseQuantityLimit": 1,\r\n      "variants": [\r\n        {\r\n          "wholesalePriceForPromoters": 10,\r\n          "price": 10,\r\n          "costPrice": 0,\r\n          "isExcluded": false,\r\n          "isDefault": false,\r\n          "priceAnchor": {{CompareAtPrice}},\r\n          "merchantProductVariantId": "c3f9aa79-fd7b-44cd-a450-5658e780b623",\r\n          "commissionRateForPromoters": 0\r\n        }\r\n      ]\r\n    }\r\n  ],\r\n  "accessSpecificUser": [],\r\n  "featuredSectionEnable": true,\r\n  "tab": {\r\n    "value": "Commerce",\r\n    "label": "Commerce",\r\n    "mappingControl": []\r\n  },\r\n  "timeKey": 1765348138631,\r\n  "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[{\\"id\\":\\"fc25524a-0380-4d63-885e-4b553fb0d602\\",\\"eventId\\":\\"79a0ae94-a4dc-4bf8-bc24-7951d78f4237\\",\\"type\\":\\"event-info-banner\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\"},{\\"children\\":[{\\"id\\":\\"143dd2b7-6c55-4664-958b-0b9988963d4a\\",\\"productId\\":\\"5eed9a05-008f-40ab-a984-403cb2217e07\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"event\\",\\"type\\":\\"show-product-banner\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\"}],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\r\n  "media": [\r\n    {\r\n      "id": "5b31fd19-d72d-42e9-91e8-e4d3c6df62b9",\r\n      "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n      "selected": true,\r\n      "type": "IMAGE",\r\n      "height": 2048,\r\n      "width": 3072,\r\n      "mediaDuration": 0,\r\n      "mediaSrc": null,\r\n      "mediaType": "IMAGE",\r\n      "inherited": false,\r\n      "position": 1,\r\n      "referenceId": null,\r\n      "source": null,\r\n      "setThumbnail": true\r\n    }\r\n  ],\r\n  "othersCanCopy": false,\r\n  "enableDownlineNote": false,\r\n  "expiredAt": "2029-12-27T09:00:00.000Z",\r\n  "urlAlias": "automation-t2810",\r\n  "headline": "automation-t2810"\r\n}', app_headers=False, token='linda01_token', path_vars={'postId': '{{postid}}'})
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: Check the compare at price display correct
    _resp3 = ctx.api.posts.consumer_detail(params={'vanityUrl': 'lindazhoucurator', 'urlAlias': 'automation-t2810'}, app_headers=False, token='linda01_token')
    # assertion 3.assertion: responseJson equal {{CompareAtPrice}}
    expect(_resp3).json('$.data.relatedProducts[0].priceDisplayAnchor').equals(ctx.render_text('{{CompareAtPrice}}'))
