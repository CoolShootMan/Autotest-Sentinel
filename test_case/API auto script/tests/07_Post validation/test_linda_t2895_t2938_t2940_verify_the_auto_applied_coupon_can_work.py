"""Migrated from Apifox case #8037415. Source folder: Post validation."""
# Apifox Case ID: 8037415  (traceability only — not needed to run)
NAME = "&T2938&t2940 Verify the auto-applied coupon can work"
TAGS = ["p0", "post_validation", "suite:linda"]
PRIORITY = 0


CASE_ID = 8037415
ENV_NAME = "Release"

# --- step 1: Get Partner linda05 token ---
# post[extractor]: {"variableName": "linda05_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 39c21944-7359-485c-9c3d-5c9d033ef018 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: guest get token ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 4: Guest visit and check the auto coupon banner response ---
# post[customScript]: /**
# post:  * Post-processor Script:
# post:  * Validates the promotion details within the related products array.
# post:  */
# post: 
# post: // Parse the JSON response
# post: const response = pm.response.json();
# post: 
# post: // 1. Basic Status Check
# post: pm.test("Status code is 200", () => {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: // 2. Validate Promotion Info in relatedProducts
# post: pm.test("Verify promotionInfo details in relatedProducts", () => {
# post:     const products = response.data.relatedProducts;
# post:     
# post:     // Ensure relatedProducts exists and is not empty
# post:     pm.expect(products).to.be.an('array').that.is.not.empty;
# post: 
# post:     // We will check the first product's promotionInfo as per your snippet
# post:     const promo = products[0].promotionInfo;
# post: 
# post:     // Validate top-level promo fields
# post:     pm.expect(promo.promotionId).to.eql("1862");
# post:     pm.expect(promo.title).to.contain("auto coupon 10%");
# post:     pm.expect(promo.description).to.eql("auto coupon T2895&T2938&t2940");
# post: 
# post:     // Validate discountConfig nested structure
# post:     const config = promo.discountConfig;
# post:     pm.expect(config.type).to.eql("AMOUNT_THRESHOLD");
# post:     
# post:     // Validate the specific discount threshold and percentage
# post:     const thresholdData = config.amountThresholdDiscounts[0];
# post:     pm.expect(thresholdData.amountThreshold).to.eql(100);
# post:     pm.expect(thresholdData.discountPercentage).to.eql(10);
# post: });
# post: 
# post: /**
# post:  * Optional: If you want to verify that EVERY product in the list 
# post:  * has this specific promotion, you can use a loop:
# post:  */
# post: /*
# post: pm.test("Verify all products have the correct promotion ID", () => {
# post:     response.data.relatedProducts.forEach((product, index) => {
# post:         pm.expect(product.promotionInfo.promotionId, `Product at index ${index} promo ID error`).to.eql("1862");
# post:     });
# post: });
# post: */
# --- step 5: edeed7a3-ef3f-400a-9ab1-11699ed19d3a ---
# post[customScript]: /**
# post:  * Post-processor Script:
# post:  * 1. Validates the total payment amount.
# post:  * 2. Extracts order metadata for subsequent requests.
# post:  * 3. Ensures data integrity via schema assertions.
# post:  */
# post: 
# post: // Parse the JSON response body
# post: const response = pm.response.json();
# post: 
# post: // Assertion 1: Verify the specific payment total
# post: pm.test("Verify 'totalToPay' is 56.67", () => {
# post:     // Using eql for numeric value comparison
# post:     pm.expect(response.data.totalToPay).to.eql(56.67);
# post: });
# post: 
# post: // Assertion 2: Verify that essential order fields are present and not empty
# post: pm.test("Validate Order ID and Number presence", () => {
# post:     pm.expect(response.data.orderId).to.be.a('string').and.not.empty;
# post:     pm.expect(response.data.orderNumber).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // Variable Extraction Logic
# post: if (response.code === 200 && response.data) {
# post:     // Extract and store 'orderId' into the environment scope
# post:     const orderId = response.data.orderId;
# post:     pm.environment.set("orderId", orderId);
# post:     
# post:     // Extract and store 'orderNumber' into the environment scope
# post:     const orderNumber = response.data.orderNumber;
# post:     pm.environment.set("orderNumber", orderNumber);
# post:     
# post:     // Debugging logs for visibility in the console
# post:     console.log(`[Variable Saved] orderId: ${orderId}`);
# post:     console.log(`[Variable Saved] orderNumber: ${orderNumber}`);
# post: } else {
# post:     // Log an error if the response format is unexpected
# post:     console.error("Failed to extract variables: Invalid response status or missing data.");
# post: }
# --- step 6: 90703ec6-7eb4-4e02-8a1c-6ac5cd9f1299 ---
# post[customScript]: /**
# post:  * Post-processor Script:
# post:  * 1. Validates the total payment amount.
# post:  * 2. Extracts order metadata for subsequent requests.
# post:  * 3. Ensures data integrity via schema assertions.
# post:  */
# post: 
# post: // Parse the JSON response body
# post: const response = pm.response.json();
# post: 
# post: // Assertion 1: Verify the specific payment total
# post: pm.test("Verify 'totalToPay' is 56.67", () => {
# post:     // Using eql for numeric value comparison
# post:     pm.expect(response.data.totalToPay).to.eql(56.67);
# post: });
# post: 
# post: // Assertion 2: Verify that essential order fields are present and not empty
# post: pm.test("Validate Order ID and Number presence", () => {
# post:     pm.expect(response.data.orderId).to.be.a('string').and.not.empty;
# post:     pm.expect(response.data.orderNumber).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // Variable Extraction Logic
# post: if (response.code === 200 && response.data) {
# post:     // Extract and store 'orderId' into the environment scope
# post:     const orderId = response.data.orderId;
# post:     pm.environment.set("orderId", orderId);
# post:     
# post:     // Extract and store 'orderNumber' into the environment scope
# post:     const orderNumber = response.data.orderNumber;
# post:     pm.environment.set("orderNumber", orderNumber);
# post:     
# post:     // Debugging logs for visibility in the console
# post:     console.log(`[Variable Saved] orderId: ${orderId}`);
# post:     console.log(`[Variable Saved] orderNumber: ${orderNumber}`);
# post: } else {
# post:     // Log an error if the response format is unexpected
# post:     console.error("Failed to extract variables: Invalid response status or missing data.");
# post: }
# --- step 7: Get consumer linda10 token ---
# post[extractor]: {"variableName": "linda10_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: 14495694-f158-4275-861d-91faf01549b5 ---
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
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: 3e59ea11-8837-471e-938e-7151823ca597 ---
# post[customScript]: /**
# post:  * Post-processor Script:
# post:  * 1. Validates the total payment amount.
# post:  * 2. Extracts order metadata for subsequent requests.
# post:  * 3. Ensures data integrity via schema assertions.
# post:  */
# post: 
# post: // Parse the JSON response body
# post: const response = pm.response.json();
# post: 
# post: // Assertion 1: Verify the specific payment total
# post: pm.test("Verify 'totalToPay' is 56.67", () => {
# post:     // Using eql for numeric value comparison
# post:     pm.expect(response.data.totalToPay).to.eql(56.67);
# post: });
# post: 
# post: // Assertion 2: Verify that essential order fields are present and not empty
# post: pm.test("Validate Order ID and Number presence", () => {
# post:     pm.expect(response.data.orderId).to.be.a('string').and.not.empty;
# post:     pm.expect(response.data.orderNumber).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // Variable Extraction Logic
# post: if (response.code === 200 && response.data) {
# post:     // Extract and store 'orderId' into the environment scope
# post:     const orderId = response.data.orderId;
# post:     pm.environment.set("orderId", orderId);
# post:     
# post:     // Extract and store 'orderNumber' into the environment scope
# post:     const orderNumber = response.data.orderNumber;
# post:     pm.environment.set("orderNumber", orderNumber);
# post:     
# post:     // Debugging logs for visibility in the console
# post:     console.log(`[Variable Saved] orderId: ${orderId}`);
# post:     console.log(`[Variable Saved] orderNumber: ${orderNumber}`);
# post: } else {
# post:     // Log an error if the response format is unexpected
# post:     console.error("Failed to extract variables: Invalid response status or missing data.");
# post: }
# --- step 10: 948e658d-e739-4485-8f70-e1c15096f756 ---
# post[customScript]: /**
# post:  * Post-processor Script:
# post:  * 1. Validates the total payment amount.
# post:  * 2. Extracts order metadata for subsequent requests.
# post:  * 3. Ensures data integrity via schema assertions.
# post:  */
# post: 
# post: // Parse the JSON response body
# post: const response = pm.response.json();
# post: 
# post: // Assertion 1: Verify the specific payment total
# post: pm.test("Verify 'totalToPay' is 56.67", () => {
# post:     // Using eql for numeric value comparison
# post:     pm.expect(response.data.totalToPay).to.eql(56.67);
# post: });
# post: 
# post: // Assertion 2: Verify that essential order fields are present and not empty
# post: pm.test("Validate Order ID and Number presence", () => {
# post:     pm.expect(response.data.orderId).to.be.a('string').and.not.empty;
# post:     pm.expect(response.data.orderNumber).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // Variable Extraction Logic
# post: if (response.code === 200 && response.data) {
# post:     // Extract and store 'orderId' into the environment scope
# post:     const orderId = response.data.orderId;
# post:     pm.environment.set("orderId", orderId);
# post:     
# post:     // Extract and store 'orderNumber' into the environment scope
# post:     const orderNumber = response.data.orderNumber;
# post:     pm.environment.set("orderNumber", orderNumber);
# post:     
# post:     // Debugging logs for visibility in the console
# post:     console.log(`[Variable Saved] orderId: ${orderId}`);
# post:     console.log(`[Variable Saved] orderNumber: ${orderNumber}`);
# post: } else {
# post:     // Log an error if the response format is unexpected
# post:     console.error("Failed to extract variables: Invalid response status or missing data.");
# post: }




import json

from core.assertions import expect

def test_linda_t2895_t2938_t2940_verify_the_auto_applied_coupon_can_work(ctx):
    """Apifox case #8037415: Linda_T2895_T2938_t2940_Verify_the_auto_applied_coupon_can_work"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+05@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}', app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: 39c21944-7359-485c-9c3d-5c9d033ef018
    _resp2 = ctx.api.posts.curator_907f5bec_0233_4778_8f46_7820e8b2eb7c(body='{\r\n    "id": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n    "announcements": [],\r\n    "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n    "title": "API Test T2895",\r\n    "subTitle": "",\r\n    "links": [],\r\n    "allowPromotersResell": true,\r\n    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",\r\n    "financeMode": "FINANCE_MODE_COMMISSION",\r\n    "status": "ACTIVE",\r\n    "allowPromotersHideProducts": true,\r\n    "allowPromotersCustomizeMedia": true,\r\n    "allowPromotersCreateCoupon": true,\r\n    "promotions": [\r\n        {\r\n            "promotionId": "1862",\r\n            "codeAliases": [],\r\n            "oneTimeUsePerCustomer": false,\r\n            "autoApplied": true,\r\n            "isExtend": false,\r\n            "startTime": 1773726368984,\r\n            "title": "auto coupon 10% percantage",\r\n            "description": "auto coupon T2895&T2938&t2940",\r\n            "amountThresholdDiscounts": [\r\n                {\r\n                    "amountThreshold": 100,\r\n                    "discountPercentage": 10\r\n                }\r\n            ],\r\n            "productIdsFilter": []\r\n        }\r\n    ],\r\n    "isPurchaseQuantityLimited": false,\r\n    "purchaseQuantityLimit": 0,\r\n    "isAccessRestricted": false,\r\n    "allowPromotersAccess": false,\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#FFEEBEFF",\r\n            "#E91E63FF",\r\n            "#757575FF",\r\n            "#0B99FFFF",\r\n            "#F2F2F6FF",\r\n            "#FFFFFF"\r\n        ],\r\n        "fontFamily": "Inter",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "dividerColor": "#FFFFFF",\r\n        "secondaryTextColor": "#E0E0E0FF",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontSize": 24,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "subtitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 400\r\n        },\r\n        "button": {\r\n            "color": "#000000",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "secondaryButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 0\r\n        },\r\n        "textButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "fontWeight": 700\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "color": "#000000 ",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 14,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 400\r\n            },\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "product": {\r\n            "color": "#FFFFFF",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "discount": {\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF",\r\n            "backgroundColor": "#D32A09"\r\n        },\r\n        "freeShipping": {\r\n            "color": "#268E46",\r\n            "backgroundColor": "#EBF5EF"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 16,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 700\r\n            },\r\n            "button": {\r\n                "color": "#000000",\r\n                "backgroundColor": "#F6CA7C"\r\n            },\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF",\r\n            "secondaryText": "#ABABAB"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#E0E0E0FF",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "height": "MEDIUM",\r\n                "displayText": "SHOP_NAME"\r\n            },\r\n            "productBanner": {\r\n                "display": "HIDE",\r\n                "ctaButton": "VIEW_PRODUCT"\r\n            }\r\n        },\r\n        "template": "ClearSky",\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 0\r\n            }\r\n        }\r\n    },\r\n    "hideInStore": false,\r\n    "recommendationSectionTitle": "",\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    ],\r\n    "checkoutInPost": true,\r\n    "allowAffiliateSharingOnly": false,\r\n    "abTestingSettings": [],\r\n    "enableAbTesting": false,\r\n    "isOrderConfirmationNoteEnabled": false,\r\n    "hideCouponBox": true,\r\n    "allowCustomizeDisplayPrices": true,\r\n    "customizeDisplayPrices": {\r\n        "price": "1930 Pacific Ave | Thu, Oct 01 (CDT)",\r\n        "priceColor": "#FFFFFF",\r\n        "titleColor": "#FFFFFF",\r\n        "discountPercent": "Get Tickets",\r\n        "discountPercentColor": "#D32A08"\r\n    },\r\n    "canSetPrice": false,\r\n    "downlineNoteBodyHtml": null,\r\n    "downlineNoteBodyJson": null,\r\n    "featuredSectionTitle": "",\r\n    "enableRedirectUrl": false,\r\n    "redirectUrl": "",\r\n    "redirectDestinationName": "",\r\n    "event": {\r\n        "id": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n        "status": "UPCOMING",\r\n        "title": "API Test T4259 ",\r\n        "venue": "1930 Pacific Ave",\r\n        "location": "1930 Pacific Ave, Dallas, TX 75201, USA",\r\n        "startDateDisplay": "2026-10-01",\r\n        "endDateDisplay": null,\r\n        "timezone": {\r\n            "dstOffset": 3600,\r\n            "rawOffset": -21600,\r\n            "timeZoneId": "America/Chicago",\r\n            "timeZoneName": "Central Daylight Time"\r\n        },\r\n        "poster": {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "position": 0,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    },\r\n    "additionalContentPosition": "aboveTickets",\r\n    "bodyHtml": "<div data-id=\\"140998d8-3047-4438-9b37-546c86e2ca22\\" data-type=\\"event-info-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-width=\\"100%\\"></div><div data-id=\\"328c7a03-7a8a-4fa8-8ed3-7edb7d772739\\" data-type=\\"additional-content\\"></div><div data-id=\\"607ab37b-8976-48f0-aafe-02c4f80e9c8a\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"5589beae-d2ca-40fc-b361-03122952beb2\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"ec43104d-b471-421d-b809-a1eadbdf3ff4\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"eaee3e83-4535-4ba6-8e81-6e995092aa01\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"b75b10d5-9e17-40a0-89a5-79cc5c91023a\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a963f25a-44a3-439f-ae37-1817621f8c11\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><hr><div data-id=\\"f416cde0-ced8-4f36-a141-c446496ed8bc\\" data-type=\\"post-event-description\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-width=\\"100%\\"></div><hr><div data-id=\\"fde17b4d-12e3-4b08-83cd-8fc15cf9ea9a\\" data-type=\\"lineup-info-banner\\" data-lineup-items=\\"[{&quot;id&quot;:&quot;f06062ef-f975-4e4f-aa07-58022b234af3&quot;,&quot;order&quot;:0,&quot;eventId&quot;:&quot;0fe6623e-a3ba-40fb-815d-3d6f444775c3&quot;,&quot;isHeadliner&quot;:true}]\\" data-width=\\"100%\\" data-layout=\\"WITH_HEADLINER\\" data-photo-shape=\\"RECTANGLE\\" data-text-alignment=\\"CENTER\\" data-headliner=\\"{&quot;width&quot;:&quot;100%&quot;}\\"></div>",\r\n    "currentDate": "2026-03-17T05:51:17.251Z",\r\n    "relatedProducts": [\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "5589beae-d2ca-40fc-b361-03122952beb2",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 51,\r\n                    "price": 56.67,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "f0a91cf5-c585-45d9-8b08-f59a6941e6d8",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 151,\r\n                    "price": 167.78,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "935e3c20-64b2-4e1a-95ff-34e68bbf55f4",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 372.59,\r\n                    "price": 413.99,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "fe01f82b-267c-4dfe-bdaa-714633d1e355",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a963f25a-44a3-439f-ae37-1817621f8c11",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 930.14,\r\n                    "price": 1033.49,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "2b8ff662-991e-4909-ae80-c80b1412a6a5",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "accessSpecificUser": [],\r\n    "featuredSectionEnable": false,\r\n    "tab": {\r\n        "value": "Commerce",\r\n        "label": "Commerce",\r\n        "mappingControl": []\r\n    },\r\n    "timeKey": 1773726677251,\r\n    "originEnablePaymentRestriction": false,\r\n    "syncEnabled": false,\r\n    "postType": "EVENT",\r\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"id\\":\\"140998d8-3047-4438-9b37-546c86e2ca22\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"type\\":\\"event-info-banner\\",\\"version\\":2},{\\"id\\":\\"328c7a03-7a8a-4fa8-8ed3-7edb7d772739\\",\\"type\\":\\"additional-content\\",\\"version\\":1},{\\"id\\":\\"607ab37b-8976-48f0-aafe-02c4f80e9c8a\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"5589beae-d2ca-40fc-b361-03122952beb2\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"ec43104d-b471-421d-b809-a1eadbdf3ff4\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"eaee3e83-4535-4ba6-8e81-6e995092aa01\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"b75b10d5-9e17-40a0-89a5-79cc5c91023a\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a963f25a-44a3-439f-ae37-1817621f8c11\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"type\\":\\"horizontalrule\\",\\"version\\":1},{\\"id\\":\\"f416cde0-ced8-4f36-a141-c446496ed8bc\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"type\\":\\"post-event-description\\",\\"version\\":2},{\\"type\\":\\"horizontalrule\\",\\"version\\":1},{\\"id\\":\\"fde17b4d-12e3-4b08-83cd-8fc15cf9ea9a\\",\\"lineupItems\\":[{\\"id\\":\\"f06062ef-f975-4e4f-aa07-58022b234af3\\",\\"order\\":0,\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"isHeadliner\\":true}],\\"width\\":\\"100%\\",\\"layout\\":\\"WITH_HEADLINER\\",\\"photoShape\\":\\"RECTANGLE\\",\\"textAlignment\\":\\"CENTER\\",\\"headlinerTitle\\":\\"Headliner\\",\\"otherSectionTitle\\":\\"Talent\\",\\"headliner\\":{\\"width\\":\\"100%\\"},\\"type\\":\\"lineup-info-banner\\",\\"version\\":2}],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1},\\"containerClassName\\":\\"\\",\\"editorClassName\\":\\"\\"}",\r\n    "needRefreshHTML": true,\r\n    "additionalContent": "{}",\r\n    "showAdditionalContent": false,\r\n    "media": [\r\n        {\r\n            "id": "7b06c8a6-ecc3-49c5-89bf-ab4b15bc4e7a",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "selected": true,\r\n            "type": "IMAGE",\r\n            "height": 2700,\r\n            "width": 2100,\r\n            "mediaDuration": 0,\r\n            "mediaSrc": null,\r\n            "mediaType": "IMAGE",\r\n            "inherited": false,\r\n            "position": 1,\r\n            "referenceId": null,\r\n            "source": null,\r\n            "setThumbnail": false\r\n        }\r\n    ],\r\n    "othersCanCopy": false,\r\n    "enableDownlineNote": false,\r\n    "expiredAt": null,\r\n    "urlAlias": "api-test-t2895",\r\n    "headline": "API Test T2895 ",\r\n    "isPaymentRestrictionEnabled": false\r\n}', token='linda05_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: guest get token
    _resp3 = ctx.api.auth.guest_login(body='{\n    "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda"\n}')
    vars['access_token'] = (_resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 4: Guest visit and check the auto coupon banner response
    _resp4 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t2895'})
    # step 5: edeed7a3-ef3f-400a-9ab1-11699ed19d3a
    _resp5 = ctx.api.orders.buy_now(body='{\r\n    "postIdForFilter": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n    "updateCartItems": [\r\n        {\r\n            "quantity": 1,\r\n            "promoterProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n            "price": 56.67,\r\n            "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n            "selected": true,\r\n            "customFields": []\r\n        }\r\n    ],\r\n    "fbAdParams": {\r\n        "eventID": "1336a11f-b5f7-4305-aae4-6c26146b1ee7",\r\n        "pixelId": [\r\n            "268933192948110"\r\n        ],\r\n        "fbBrowserId": "fb.1.1773714303427.697551905492792340",\r\n        "externalId": "742c624f-79e2-4ace-96dd-a96b5dd8fbfa",\r\n        "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2895"\r\n    },\r\n    "currentUpdateCartItems": [\r\n        {\r\n            "quantity": 1,\r\n            "id": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n            "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n            "price": 56.67,\r\n            "customFields": []\r\n        }\r\n    ]\r\n}', app_headers=True, token='access_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp5, 'orderId')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp5, 'orderNumber')
    # step 6: 90703ec6-7eb4-4e02-8a1c-6ac5cd9f1299
    _resp6 = ctx.api.orders.buy_now(body='{\r\n    "postIdForFilter": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n    "updateCartItems": [\r\n        {\r\n            "quantity": 1,\r\n            "promoterProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n            "price": 56.67,\r\n            "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n            "selected": true,\r\n            "customFields": []\r\n        }\r\n    ],\r\n    "fbAdParams": {\r\n        "eventID": "a078d702-0da1-42bb-83c2-8c071f13dc71",\r\n        "pixelId": [\r\n            "268933192948110"\r\n        ],\r\n        "fbBrowserId": "fb.1.1773714303427.697551905492792340",\r\n        "externalId": "742c624f-79e2-4ace-96dd-a96b5dd8fbfa",\r\n        "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2895"\r\n    },\r\n    "currentUpdateCartItems": [\r\n        {\r\n            "quantity": 1,\r\n            "id": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n            "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n            "price": 56.67,\r\n            "customFields": []\r\n        }\r\n    ]\r\n}', app_headers=True, token='access_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp6, 'orderId')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp6, 'orderNumber')
    # step 7: Get consumer linda10 token
    _resp7 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+10@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}', app_headers=True)
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp7, '$.data.token')
    # step 8: 14495694-f158-4275-861d-91faf01549b5
    _resp8 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 8.assertion: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # assertion 8.assertion: responseJson equal success
    expect(_resp8).json('$.message').equals('success')
    # step 9: 3e59ea11-8837-471e-938e-7151823ca597
    _resp9 = ctx.api.orders.buy_now(body='{\r\n    "postIdForFilter": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n    "updateCartItems": [\r\n        {\r\n            "quantity": 1,\r\n            "promoterProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n            "price": 56.67,\r\n            "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n            "selected": true,\r\n            "customFields": []\r\n        }\r\n    ],\r\n    "fbAdParams": {\r\n        "eventID": "1336a11f-b5f7-4305-aae4-6c26146b1ee7",\r\n        "pixelId": [\r\n            "268933192948110"\r\n        ],\r\n        "fbBrowserId": "fb.1.1773714303427.697551905492792340",\r\n        "externalId": "742c624f-79e2-4ace-96dd-a96b5dd8fbfa",\r\n        "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2895"\r\n    },\r\n    "currentUpdateCartItems": [\r\n        {\r\n            "quantity": 1,\r\n            "id": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n            "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n            "price": 56.67,\r\n            "customFields": []\r\n        }\r\n    ]\r\n}', app_headers=True, token='linda10_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp9, 'orderId')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp9, 'orderNumber')
    # step 10: 948e658d-e739-4485-8f70-e1c15096f756
    _resp10 = ctx.api.orders.buy_now(body='{\r\n    "postIdForFilter": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n    "updateCartItems": [\r\n        {\r\n            "quantity": 1,\r\n            "promoterProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n            "price": 56.67,\r\n            "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n            "selected": true,\r\n            "customFields": []\r\n        }\r\n    ],\r\n    "fbAdParams": {\r\n        "eventID": "a078d702-0da1-42bb-83c2-8c071f13dc71",\r\n        "pixelId": [\r\n            "268933192948110"\r\n        ],\r\n        "fbBrowserId": "fb.1.1773714303427.697551905492792340",\r\n        "externalId": "742c624f-79e2-4ace-96dd-a96b5dd8fbfa",\r\n        "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2895"\r\n    },\r\n    "currentUpdateCartItems": [\r\n        {\r\n            "quantity": 1,\r\n            "id": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n            "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",\r\n            "price": 56.67,\r\n            "customFields": []\r\n        }\r\n    ]\r\n}', app_headers=True, token='linda10_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp10, 'orderId')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp10, 'orderNumber')
