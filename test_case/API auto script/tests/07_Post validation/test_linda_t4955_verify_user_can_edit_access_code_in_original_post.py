"""Auto-generated from Apifox case #7886135. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7886135
# Folder: 
# Case: (Linda) T4955 Verify user can edit access code in original post
# Priority: P0
# Created: 2026-02-02T04:05:24.000Z
# Updated: 2026-08-11T06:51:09.000Z


CASE_ID = 7886135
ENV_NAME = "Release"

# --- step 1: d916bc6e-0d14-4a34-b4bb-515119343dbd ---
# pre: //post url:  https://release.pear.us/lindanewcurator/post/t4955bylinda
# pre: pm.environment.set("postId", "e6aa0dd3-3d87-4d64-bb8c-78be838908f7");
# pre: 
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 36bb23eb-ac93-4856-abb6-33c32b362795 ---
# pre: // 1. 生成标准 UUID
# pre: var standardUuid = pm.variables.replaceIn('{{$guid}}');
# pre: 
# pre: // 2. 存入环境（给后面的接口用）
# pre: pm.environment.set("guest_session_id", standardUuid);
# pre: 
# pre: // 3. 【关键】直接修改本次请求的 Body，不给它读取旧值的机会
# pre: var body = JSON.parse(pm.request.body.raw);
# pre: body.consumerId = standardUuid;
# pre: pm.request.body.raw = JSON.stringify(body);
# pre: 
# pre: console.log("⚡ 强行注入本次请求的 ID: " + standardUuid);
# post[customScript]: var jsonData = pm.response.json();
# post: if (jsonData.data) {
# post:     pm.environment.set("guest_token", jsonData.data);
# post:     console.log("✅ Token 已保存");
# post: }
# --- step 3: 83a2f2e6-81a0-42a0-ad6a-1630ef59bb6b ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderId", "multipleValue": [], "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumber", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumber", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 58b469eb-74d3-4a63-8cde-5f08e36dced4 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: d59ea706-fb0b-41a8-bc18-97ba17c0e4fa ---
# pre: //post url:  https://release.pear.us/lindanewcurator/post/t4955bylinda
# pre: pm.environment.set("postId", "e6aa0dd3-3d87-4d64-bb8c-78be838908f7");
# pre: pm.environment.set("postId", "e6aa0dd3-3d87-4d64-bb8c-78be838908f7");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: 4f75abe3-9434-447c-aa35-f27e1d70d0a4 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





import uuid as _uuid

from core.assertions import expect

def test__7886135__Linda_T4955_Verify_user_can_edit_access_code_in_original_post(ctx):
    """Apifox case #7886135: Linda_T4955_Verify_user_can_edit_access_code_in_original_post"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['postId'] = 'e6aa0dd3-3d87-4d64-bb8c-78be838908f7'
    # step 1: d916bc6e-0d14-4a34-b4bb-515119343dbd
    # === pre-script（由 Apifox customScript 翻译）===
    # post url:  https://release.pear.us/lindanewcurator/post/t4955bylinda
    vars['postId'] = "e6aa0dd3-3d87-4d64-bb8c-78be838908f7"

    _resp1 = ctx.api.posts.curator_by_post_id(body={
        "id": "e6aa0dd3-3d87-4d64-bb8c-78be838908f7",
        "announcements": [],
        "createFromEventId": None,
        "title": "Auto test T4955 by linda",
        "subTitle": "Auto test T4955 by linda subtitle",
        "links": [],
        "allowPromotersResell": False,
        "financeModeForPromoters": "FINANCE_MODE_COMMISSION",
        "financeMode": "FINANCE_MODE_COMMISSION",
        "status": "ACTIVE",
        "allowPromotersHideProducts": True,
        "allowPromotersCustomizeMedia": True,
        "allowPromotersCreateCoupon": True,
        "promotions": [],
        "isPurchaseQuantityLimited": False,
        "purchaseQuantityLimit": 1,
        "isAccessRestricted": False,
        "allowPromotersAccess": False,
        "hideInStore": False,
        "recommendationSectionTitle": "",
        "coverImages": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1769417658/uploaded_images/ndowianynlljjmj56ffo.webp",
                "width": 1500,
                "height": 1443,
                "mediaSrc": None,
                "position": 1,
                "mediaType": "IMAGE",
                "mediaDuration": 0,
            },
        ],
        "checkoutInPost": True,
        "allowAffiliateSharingOnly": False,
        "abTestingSettings": [],
        "enableAbTesting": False,
        "isOrderConfirmationNoteEnabled": False,
        "hideCouponBox": False,
        "allowCustomizeDisplayPrices": True,
        "customizeDisplayPrices": {
            "price": "$23.33",
            "priceColor": "#FFFFFF",
            "titleColor": "#FFFFFF",
            "discountPercent": "",
            "discountPercentColor": "#D32A08",
        },
        "canSetPrice": False,
        "downlineNoteBodyHtml": None,
        "downlineNoteBodyJson": None,
        "featuredSectionTitle": "Featured products",
        "enableRedirectUrl": False,
        "redirectUrl": "",
        "redirectDestinationName": "",
        "cardCustomizeCoverImages": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1769417658/uploaded_images/ndowianynlljjmj56ffo.webp",
                "width": 1500,
                "height": 1443,
                "mediaSrc": None,
                "inherited": False,
                "mediaType": "IMAGE",
                "setThumbnail": True,
                "mediaDuration": 0,
            },
        ],
        "additionalContentPosition": "aboveTickets",
        "bodyHtml": "",
        "currentDate": "2026-02-10T09:17:46.467Z",
        "relatedProducts": [
            {
                "type": "PRODUCT",
                "merchantProductId": "000c24b6-801d-40ab-9113-59fd6e23b75f",
                "isVisible": True,
                "isPurchaseQuantityLimited": False,
                "isRecommendation": False,
                "hasDependentProducts": False,
                "dependentProductIds": [],
                "isFreeShipping": False,
                "isDefaultToSubscription": False,
                "toReplaceMerchantProductIds": None,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 50,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 200,
                        "merchantProductVariantId": "a7cd0054-e9fe-44ca-a630-bbcee6a5d8e0",
                        "commissionRateForPromoters": 0,
                    },
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 50,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 200,
                        "merchantProductVariantId": "4510bba0-2f2f-4bdd-a660-08df7403cb45",
                        "commissionRateForPromoters": 0,
                    },
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 50,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 200,
                        "merchantProductVariantId": "3d02e259-664e-4d43-a7b4-7b2725c8aac6",
                        "commissionRateForPromoters": 0,
                    },
                ],
            },
            {
                "type": "PRODUCT",
                "merchantProductId": "4d0e57b7-0759-4b21-a4a6-5e27bd7e129b",
                "isVisible": True,
                "isPurchaseQuantityLimited": False,
                "isRecommendation": False,
                "hasDependentProducts": False,
                "dependentProductIds": [],
                "isFreeShipping": False,
                "isDefaultToSubscription": False,
                "toReplaceMerchantProductIds": None,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 0,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "2ac3b1d5-545c-4a7c-9bed-5b62a8b15cdf",
                        "commissionRateForPromoters": 0,
                    },
                ],
            },
        ],
        "accessSpecificUser": [],
        "featuredSectionEnable": True,
        "tab": {
            "value": "Commerce",
            "label": "Commerce",
            "mappingControl": [],
        },
        "timeKey": 1770715066467,
        "originEnablePaymentRestriction": False,
        "syncEnabled": False,
        "postType": "STANDARD",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"05d0d278-7922-449d-b1e3-721435544ad0\",\"lineupItems\":[{\"id\":\"1c3e22c0-d1c6-4d10-8880-b27f1c12f68f\",\"eventId\":\"e3ca1e2a-8d00-437e-a89a-9e14f2ec69eb\",\"order\":0,\"isHeadliner\":true},{\"id\":\"153b167b-2840-4dee-8246-7b9a8becc644\",\"eventId\":\"e3ca1e2a-8d00-437e-a89a-9e14f2ec69eb\",\"order\":1,\"isHeadliner\":false}],\"width\":\"100%\",\"height\":\"\",\"layout\":\"WITH_HEADLINER\",\"photoShape\":\"RECTANGLE\",\"textAlignment\":\"CENTER\",\"headliner\":{\"width\":\"100%\"},\"headlinerTitle\":\"Headliner\",\"otherSectionTitle\":\"Talent\",\"type\":\"lineup-info-banner\",\"version\":2},{\"id\":\"e9da9c24-ace5-4f16-b440-f7cd3154e532\",\"lineupItems\":[{\"id\":\"1c3e22c0-d1c6-4d10-8880-b27f1c12f68f\",\"eventId\":\"e3ca1e2a-8d00-437e-a89a-9e14f2ec69eb\",\"order\":0,\"isHeadliner\":true},{\"id\":\"153b167b-2840-4dee-8246-7b9a8becc644\",\"eventId\":\"e3ca1e2a-8d00-437e-a89a-9e14f2ec69eb\",\"order\":1,\"isHeadliner\":false}],\"width\":\"100%\",\"height\":\"\",\"layout\":\"WITH_HEADLINER\",\"photoShape\":\"RECTANGLE\",\"textAlignment\":\"CENTER\",\"headliner\":{\"width\":\"100%\"},\"headlinerTitle\":\"Headliner\",\"otherSectionTitle\":\"Talent\",\"type\":\"lineup-info-banner\",\"version\":2}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
        "additionalContent": "{}",
        "showAdditionalContent": False,
        "media": [
            {
                "id": "e8e9070d-acad-4ab7-ad25-0324a9748dcb",
                "src": "https://res.cloudinary.com/dr9io1zjv/v1769417658/uploaded_images/ndowianynlljjmj56ffo.webp",
                "selected": True,
                "type": "IMAGE",
                "height": 1443,
                "width": 1500,
                "mediaDuration": 0,
                "mediaSrc": None,
                "mediaType": "IMAGE",
                "inherited": True,
                "position": 1,
                "referenceId": None,
                "source": "UPLOAD",
                "setThumbnail": True,
            },
            {
                "id": "8031c5e7-1af3-465b-ae71-701593c12dd3",
                "src": "https://res.cloudinary.com/dr9io1zjv/v1769417666/uploaded_images/gapsiejdt4cxs1hkyun4.webp",
                "selected": True,
                "type": "IMAGE",
                "height": 802,
                "width": 600,
                "mediaDuration": 0,
                "mediaSrc": None,
                "mediaType": "IMAGE",
                "inherited": True,
                "position": 2,
                "referenceId": None,
                "source": "UPLOAD",
                "setThumbnail": False,
            },
        ],
        "othersCanCopy": False,
        "enableDownlineNote": False,
        "allowVisitorCreateAffiliateLink": False,
        "expiredAt": None,
        "urlAlias": "t4955bylinda",
        "headline": "Auto test T4955 by linda",
        "isPaymentRestrictionEnabled": True,
        "paymentRestriction": {
            "accessCodes": [
                "123456",
                "654321",
            ],
            "paymentVendors": [
                "BANK_CARD",
            ],
            "reason": "reason by linda automation test",
            "cardBrands": [
                "cash_app_card",
                "visa",
                "mastercard",
            ],
            "howToGetAccessCode": "This product requires access code. Please make sure you have the access code from the seller.",
        },
    }, token='linda05_token')
    # assertion 1.assertion: responseJson equal ACTIVE
    expect(_resp1).json('$.data.status').equals('ACTIVE')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # Apifox: var standardUuid = pm.variables.replaceIn('{{$guid}}')
    vars['guest_session_id'] = str(_uuid.uuid4())
    # step 2: 36bb23eb-ac93-4856-abb6-33c32b362795
    _resp2 = ctx.api.auth.guest_login(body={
        "consumerId": "{{guest_session_id}}",
    })
    # extractor: guest_token = $.data
    ctx.extract('guest_token', _resp2, '$.data')
    # step 3: 83a2f2e6-81a0-42a0-ad6a-1630ef59bb6b
    _resp3 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "{{postId}}",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "a242e8f4-46aa-43e1-92db-80b004ab1f84",
                "price": 0,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
                "accessCode": "123456",
            },
        ],
        "fbAdParams": {
            "eventID": "f8227ec3-2c1a-4de7-aa6e-6a5db01c2c2e",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1770012485749.217500641978621954",
            "externalId": "7bf1fe2f-66d3-41e6-aff2-bb9bc4b62d6b",
            "eventSourceUrl": "https://release.pear.us/lindanewcurator/post/t4955bylinda",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "a242e8f4-46aa-43e1-92db-80b004ab1f84",
                "postId": "{{postId}}",
                "price": 0,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='guest_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # assertion 3.assertion: responseJson exists 
    expect(_resp3).json('$.data.orderId').exists()
    # assertion 3.assertion: responseJson exists 
    expect(_resp3).json('$.data.orderNumber').exists()
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp3, '$.data.orderId')
    # step 4: 58b469eb-74d3-4a63-8cde-5f08e36dced4
    _resp4 = ctx.api.orders.create(body={
        "id": "{{orderId}}",
        "contact": {
            "email": "linda.zhou.ext+10@1m.app",
            "firstName": "linda",
            "lastName": "zhou10",
            "phoneNumber": "+16502396646",
        },
        "fbAdParams": {
            "eventID": "8454717a-93fd-45d2-a2f6-ce424cd414e7",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1770012485749.217500641978621954",
            "externalId": "7bf1fe2f-66d3-41e6-aff2-bb9bc4b62d6b",
            "eventSourceUrl": "https://release.pear.us/lindanewcurator/post/t4955bylinda",
        },
    }, app_headers=True, token='guest_token')
    # assertion 4.assertion: responseJson equal 200
    expect(_resp4).json('$.code').equals('200')
    # assertion 4.assertion: responseJson equal success
    expect(_resp4).json('$.message').equals('success')
    vars['postId'] = 'e6aa0dd3-3d87-4d64-bb8c-78be838908f7'
    vars['postId'] = 'e6aa0dd3-3d87-4d64-bb8c-78be838908f7'
    # step 5: d59ea706-fb0b-41a8-bc18-97ba17c0e4fa
    # === pre-script（由 Apifox customScript 翻译）===
    # post url:  https://release.pear.us/lindanewcurator/post/t4955bylinda
    vars['postId'] = "e6aa0dd3-3d87-4d64-bb8c-78be838908f7"
    vars['postId'] = "e6aa0dd3-3d87-4d64-bb8c-78be838908f7"

    _resp5 = ctx.api.posts.curator_by_post_id(body={
        "id": "e6aa0dd3-3d87-4d64-bb8c-78be838908f7",
        "announcements": [],
        "createFromEventId": None,
        "title": "Auto test T4955 by linda",
        "subTitle": "Auto test T4955 by linda subtitle",
        "links": [],
        "allowPromotersResell": False,
        "financeModeForPromoters": "FINANCE_MODE_COMMISSION",
        "financeMode": "FINANCE_MODE_COMMISSION",
        "status": "ACTIVE",
        "allowPromotersHideProducts": True,
        "allowPromotersCustomizeMedia": True,
        "allowPromotersCreateCoupon": True,
        "promotions": [],
        "isPurchaseQuantityLimited": False,
        "purchaseQuantityLimit": 1,
        "isAccessRestricted": False,
        "allowPromotersAccess": False,
        "hideInStore": False,
        "recommendationSectionTitle": "",
        "coverImages": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1769417658/uploaded_images/ndowianynlljjmj56ffo.webp",
                "width": 1500,
                "height": 1443,
                "mediaSrc": None,
                "position": 1,
                "mediaType": "IMAGE",
                "mediaDuration": 0,
            },
        ],
        "checkoutInPost": True,
        "allowAffiliateSharingOnly": False,
        "abTestingSettings": [],
        "enableAbTesting": False,
        "isOrderConfirmationNoteEnabled": False,
        "hideCouponBox": False,
        "allowCustomizeDisplayPrices": True,
        "customizeDisplayPrices": {
            "price": "$23.33",
            "priceColor": "#FFFFFF",
            "titleColor": "#FFFFFF",
            "discountPercent": "",
            "discountPercentColor": "#D32A08",
        },
        "canSetPrice": False,
        "downlineNoteBodyHtml": None,
        "downlineNoteBodyJson": None,
        "featuredSectionTitle": "Featured products",
        "enableRedirectUrl": False,
        "redirectUrl": "",
        "redirectDestinationName": "",
        "cardCustomizeCoverImages": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1769417658/uploaded_images/ndowianynlljjmj56ffo.webp",
                "width": 1500,
                "height": 1443,
                "mediaSrc": None,
                "inherited": False,
                "mediaType": "IMAGE",
                "setThumbnail": True,
                "mediaDuration": 0,
            },
        ],
        "additionalContentPosition": "aboveTickets",
        "bodyHtml": "",
        "currentDate": "2026-02-10T09:17:46.467Z",
        "relatedProducts": [
            {
                "type": "PRODUCT",
                "merchantProductId": "000c24b6-801d-40ab-9113-59fd6e23b75f",
                "isVisible": True,
                "isPurchaseQuantityLimited": False,
                "isRecommendation": False,
                "hasDependentProducts": False,
                "dependentProductIds": [],
                "isFreeShipping": False,
                "isDefaultToSubscription": False,
                "toReplaceMerchantProductIds": None,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 50,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 200,
                        "merchantProductVariantId": "a7cd0054-e9fe-44ca-a630-bbcee6a5d8e0",
                        "commissionRateForPromoters": 0,
                    },
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 50,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 200,
                        "merchantProductVariantId": "4510bba0-2f2f-4bdd-a660-08df7403cb45",
                        "commissionRateForPromoters": 0,
                    },
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 50,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 200,
                        "merchantProductVariantId": "3d02e259-664e-4d43-a7b4-7b2725c8aac6",
                        "commissionRateForPromoters": 0,
                    },
                ],
            },
            {
                "type": "PRODUCT",
                "merchantProductId": "4d0e57b7-0759-4b21-a4a6-5e27bd7e129b",
                "isVisible": True,
                "isPurchaseQuantityLimited": False,
                "isRecommendation": False,
                "hasDependentProducts": False,
                "dependentProductIds": [],
                "isFreeShipping": False,
                "isDefaultToSubscription": False,
                "toReplaceMerchantProductIds": None,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 0,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "2ac3b1d5-545c-4a7c-9bed-5b62a8b15cdf",
                        "commissionRateForPromoters": 0,
                    },
                ],
            },
        ],
        "accessSpecificUser": [],
        "featuredSectionEnable": True,
        "tab": {
            "value": "Commerce",
            "label": "Commerce",
            "mappingControl": [],
        },
        "timeKey": 1770715066467,
        "originEnablePaymentRestriction": False,
        "syncEnabled": False,
        "postType": "STANDARD",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"05d0d278-7922-449d-b1e3-721435544ad0\",\"lineupItems\":[{\"id\":\"1c3e22c0-d1c6-4d10-8880-b27f1c12f68f\",\"eventId\":\"e3ca1e2a-8d00-437e-a89a-9e14f2ec69eb\",\"order\":0,\"isHeadliner\":true},{\"id\":\"153b167b-2840-4dee-8246-7b9a8becc644\",\"eventId\":\"e3ca1e2a-8d00-437e-a89a-9e14f2ec69eb\",\"order\":1,\"isHeadliner\":false}],\"width\":\"100%\",\"height\":\"\",\"layout\":\"WITH_HEADLINER\",\"photoShape\":\"RECTANGLE\",\"textAlignment\":\"CENTER\",\"headliner\":{\"width\":\"100%\"},\"headlinerTitle\":\"Headliner\",\"otherSectionTitle\":\"Talent\",\"type\":\"lineup-info-banner\",\"version\":2},{\"id\":\"e9da9c24-ace5-4f16-b440-f7cd3154e532\",\"lineupItems\":[{\"id\":\"1c3e22c0-d1c6-4d10-8880-b27f1c12f68f\",\"eventId\":\"e3ca1e2a-8d00-437e-a89a-9e14f2ec69eb\",\"order\":0,\"isHeadliner\":true},{\"id\":\"153b167b-2840-4dee-8246-7b9a8becc644\",\"eventId\":\"e3ca1e2a-8d00-437e-a89a-9e14f2ec69eb\",\"order\":1,\"isHeadliner\":false}],\"width\":\"100%\",\"height\":\"\",\"layout\":\"WITH_HEADLINER\",\"photoShape\":\"RECTANGLE\",\"textAlignment\":\"CENTER\",\"headliner\":{\"width\":\"100%\"},\"headlinerTitle\":\"Headliner\",\"otherSectionTitle\":\"Talent\",\"type\":\"lineup-info-banner\",\"version\":2}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
        "additionalContent": "{}",
        "showAdditionalContent": False,
        "media": [
            {
                "id": "e8e9070d-acad-4ab7-ad25-0324a9748dcb",
                "src": "https://res.cloudinary.com/dr9io1zjv/v1769417658/uploaded_images/ndowianynlljjmj56ffo.webp",
                "selected": True,
                "type": "IMAGE",
                "height": 1443,
                "width": 1500,
                "mediaDuration": 0,
                "mediaSrc": None,
                "mediaType": "IMAGE",
                "inherited": True,
                "position": 1,
                "referenceId": None,
                "source": "UPLOAD",
                "setThumbnail": True,
            },
            {
                "id": "8031c5e7-1af3-465b-ae71-701593c12dd3",
                "src": "https://res.cloudinary.com/dr9io1zjv/v1769417666/uploaded_images/gapsiejdt4cxs1hkyun4.webp",
                "selected": True,
                "type": "IMAGE",
                "height": 802,
                "width": 600,
                "mediaDuration": 0,
                "mediaSrc": None,
                "mediaType": "IMAGE",
                "inherited": True,
                "position": 2,
                "referenceId": None,
                "source": "UPLOAD",
                "setThumbnail": False,
            },
        ],
        "othersCanCopy": False,
        "enableDownlineNote": False,
        "allowVisitorCreateAffiliateLink": False,
        "expiredAt": None,
        "urlAlias": "t4955bylinda",
        "headline": "Auto test T4955 by linda",
        "isPaymentRestrictionEnabled": False,
        "paymentRestriction": {
            "accessCodes": [
                "123456",
                "654321",
            ],
            "paymentVendors": [
                "BANK_CARD",
            ],
            "reason": "reason by linda automation test",
            "cardBrands": [
                "cash_app_card",
                "visa",
                "mastercard",
            ],
            "howToGetAccessCode": "This product requires access code. Please make sure you have the access code from the seller.",
        },
    }, token='linda05_token')
    # assertion 5.assertion: responseJson equal ACTIVE
    expect(_resp5).json('$.data.status').equals('ACTIVE')
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson equal success
    expect(_resp5).json('$.message').equals('success')
    # step 6: 4f75abe3-9434-447c-aa35-f27e1d70d0a4
    _resp6 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "{{postId}}",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "a242e8f4-46aa-43e1-92db-80b004ab1f84",
                "price": 0,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "f8227ec3-2c1a-4de7-aa6e-6a5db01c2c2e",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1770012485749.217500641978621954",
            "externalId": "7bf1fe2f-66d3-41e6-aff2-bb9bc4b62d6b",
            "eventSourceUrl": "https://release.pear.us/lindanewcurator/post/t4955bylinda",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "a242e8f4-46aa-43e1-92db-80b004ab1f84",
                "postId": "{{postId}}",
                "price": 0,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='guest_token')
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # assertion 6.assertion: responseJson equal 0
    expect(_resp6).json('$.data.totalToPay').equals('0')
