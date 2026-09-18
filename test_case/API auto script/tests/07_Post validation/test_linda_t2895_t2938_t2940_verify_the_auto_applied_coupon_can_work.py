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

from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t2895_t2938_t2940_verify_the_auto_applied_coupon_can_work(ctx: "Context"):
    """Apifox case #8037415: Linda_T2895_T2938_t2940_Verify_the_auto_applied_coupon_can_work"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body={
        "email": "linda.zhou.ext+05@1m.app",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: 39c21944-7359-485c-9c3d-5c9d033ef018
    _resp2 = ctx.api.posts.curator_update(post_id='{{T2895_post_id}}', body={
        "id": "{{T2895_post_id}}",
        "announcements": [],
        "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",
        "title": "API Test T2895",
        "subTitle": "",
        "links": [],
        "allowPromotersResell": True,
        "financeModeForPromoters": "FINANCE_MODE_COMMISSION",
        "financeMode": "FINANCE_MODE_COMMISSION",
        "status": "ACTIVE",
        "allowPromotersHideProducts": True,
        "allowPromotersCustomizeMedia": True,
        "allowPromotersCreateCoupon": True,
        "promotions": [
            {
                "promotionId": "1862",
                "codeAliases": [],
                "oneTimeUsePerCustomer": False,
                "autoApplied": True,
                "isExtend": False,
                "startTime": 1773726368984,
                "title": "auto coupon 10% percantage",
                "description": "auto coupon T2895&T2938&t2940",
                "amountThresholdDiscounts": [
                    {
                        "amountThreshold": 100,
                        "discountPercentage": 10,
                    },
                ],
                "productIdsFilter": [],
            },
        ],
        "isPurchaseQuantityLimited": False,
        "purchaseQuantityLimit": 0,
        "isAccessRestricted": False,
        "allowPromotersAccess": False,
        "styleSettings": {
            "recentUsedColors": [
                "#B7E2E0FF",
                "#FFEEBEFF",
                "#E91E63FF",
                "#757575FF",
                "#0B99FFFF",
                "#F2F2F6FF",
                "#FFFFFF",
            ],
            "fontFamily": "Inter",
            "color": "#FFFFFF",
            "backgroundColor": "#000000",
            "borderColor": "#000000",
            "dividerColor": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0FF",
            "announcementCarousel": {
                "color": "#000000",
                "backgroundColor": "#F6CA7C",
            },
            "title": {
                "color": "#F6CA7C",
                "fontSize": 24,
                "fontFamily": "Inter",
                "fontWeight": 700,
            },
            "columnTitle": {
                "color": "#FFFFFF",
                "fontSize": 20,
                "fontFamily": "Inter",
                "fontWeight": 700,
            },
            "subtitle": {
                "color": "#FFFFFF",
                "fontSize": 20,
                "fontFamily": "Inter",
                "fontWeight": 400,
            },
            "button": {
                "color": "#000000",
                "fontSize": 16,
                "boxShadow": "none",
                "fontWeight": 400,
                "borderColor": "#0000",
                "borderRadius": 0,
                "backgroundColor": "#F6CA7C",
            },
            "secondaryButton": {
                "color": "#FFFFFF",
                "fontSize": 16,
                "boxShadow": "none",
                "fontWeight": 400,
                "borderColor": "#F6CA7C",
                "borderRadius": 0,
            },
            "textButton": {
                "color": "#FFFFFF",
                "fontSize": 16,
                "fontWeight": 700,
            },
            "selectButton": {
                "borderColor": "#000000",
            },
            "relatedLink": {
                "color": "#000000 ",
                "borderColor": "#0000",
                "borderRadius": 0,
                "backgroundColor": "#FFFFFF80",
            },
            "featuredProducts": {
                "color": "#FFFFFF",
                "title": {
                    "color": "#FFFFFF",
                    "fontSize": 14,
                    "fontFamily": "Inter",
                    "fontWeight": 400,
                },
                "borderRadius": 0,
                "backgroundColor": "#000000",
                "secondaryTextColor": "#E0E0E0FF",
            },
            "product": {
                "color": "#FFFFFF",
                "borderRadius": 0,
                "backgroundColor": "#000000",
                "secondaryTextColor": "#E0E0E0FF",
            },
            "discount": {
                "color": "#FFFFFF",
                "priceColor": "#FFFFFF",
                "backgroundColor": "#D32A09",
            },
            "freeShipping": {
                "color": "#268E46",
                "backgroundColor": "#EBF5EF",
            },
            "starRatingColor": "#FAAF03",
            "layoutFeatureCard": {
                "color": "#FFFFFF",
                "title": {
                    "color": "#FFFFFF",
                    "fontSize": 16,
                    "fontFamily": "Inter",
                    "fontWeight": 700,
                },
                "button": {
                    "color": "#000000",
                    "backgroundColor": "#F6CA7C",
                },
                "secondaryTextColor": "#E0E0E0FF",
            },
            "lineupBanner": {
                "titleText": "#FFFFFF",
                "descriptionText": "#F6CA7C",
            },
            "eventInfoBanner": {
                "text": "#FFFFFF",
                "secondaryText": "#ABABAB",
            },
            "eventDescription": {
                "text": "#E0E0E0FF",
                "title": "#FFFFFF",
            },
            "layout": {
                "pageHeader": {
                    "style": "DEDICATED_HEADER_BAR",
                    "height": "MEDIUM",
                    "displayText": "SHOP_NAME",
                },
                "productBanner": {
                    "display": "HIDE",
                    "ctaButton": "VIEW_PRODUCT",
                },
            },
            "template": "ClearSky",
            "featuredProduct": {
                "cover": {
                    "borderRadius": 0,
                },
            },
        },
        "hideInStore": False,
        "recommendationSectionTitle": "",
        "coverImages": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",
                "width": 2100,
                "height": 2700,
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
        "hideCouponBox": True,
        "allowCustomizeDisplayPrices": True,
        "customizeDisplayPrices": {
            "price": "1930 Pacific Ave | Thu, Oct 01 (CDT)",
            "priceColor": "#FFFFFF",
            "titleColor": "#FFFFFF",
            "discountPercent": "Get Tickets",
            "discountPercentColor": "#D32A08",
        },
        "canSetPrice": False,
        "downlineNoteBodyHtml": None,
        "downlineNoteBodyJson": None,
        "featuredSectionTitle": "",
        "enableRedirectUrl": False,
        "redirectUrl": "",
        "redirectDestinationName": "",
        "event": {
            "id": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",
            "status": "UPCOMING",
            "title": "API Test T4259 ",
            "venue": "1930 Pacific Ave",
            "location": "1930 Pacific Ave, Dallas, TX 75201, USA",
            "startDateDisplay": "2026-10-01",
            "endDateDisplay": None,
            "timezone": {
                "dstOffset": 3600,
                "rawOffset": -21600,
                "timeZoneId": "America/Chicago",
                "timeZoneName": "Central Daylight Time",
            },
            "poster": {
                "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",
                "width": 2100,
                "height": 2700,
                "position": 0,
                "mediaType": "IMAGE",
                "mediaDuration": 0,
            },
        },
        "additionalContentPosition": "aboveTickets",
        "bodyHtml": "<div data-id=\"140998d8-3047-4438-9b37-546c86e2ca22\" data-type=\"event-info-banner\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-width=\"100%\"></div><div data-id=\"328c7a03-7a8a-4fa8-8ed3-7edb7d772739\" data-type=\"additional-content\"></div><div data-id=\"607ab37b-8976-48f0-aafe-02c4f80e9c8a\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"5589beae-d2ca-40fc-b361-03122952beb2\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"ec43104d-b471-421d-b809-a1eadbdf3ff4\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"eaee3e83-4535-4ba6-8e81-6e995092aa01\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"b75b10d5-9e17-40a0-89a5-79cc5c91023a\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"a963f25a-44a3-439f-ae37-1817621f8c11\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><hr><div data-id=\"f416cde0-ced8-4f36-a141-c446496ed8bc\" data-type=\"post-event-description\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-width=\"100%\"></div><hr><div data-id=\"fde17b4d-12e3-4b08-83cd-8fc15cf9ea9a\" data-type=\"lineup-info-banner\" data-lineup-items=\"[{&quot;id&quot;:&quot;f06062ef-f975-4e4f-aa07-58022b234af3&quot;,&quot;order&quot;:0,&quot;eventId&quot;:&quot;0fe6623e-a3ba-40fb-815d-3d6f444775c3&quot;,&quot;isHeadliner&quot;:true}]\" data-width=\"100%\" data-layout=\"WITH_HEADLINER\" data-photo-shape=\"RECTANGLE\" data-text-alignment=\"CENTER\" data-headliner=\"{&quot;width&quot;:&quot;100%&quot;}\"></div>",
        "currentDate": "2026-03-17T05:51:17.251Z",
        "relatedProducts": [
            {
                "type": "PRODUCT",
                "merchantProductId": "5589beae-d2ca-40fc-b361-03122952beb2",
                "isVisible": True,
                "isPurchaseQuantityLimited": False,
                "isRecommendation": False,
                "hasDependentProducts": False,
                "dependentProductIds": [],
                "isFreeShipping": False,
                "isDefaultToSubscription": False,
                "toReplaceMerchantProductIds": None,
                "isCtaCustomized": False,
                "ctaConfig": {
                    "type": "BUY_NOW",
                },
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 51,
                        "price": 56.67,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
            {
                "type": "PRODUCT",
                "merchantProductId": "f0a91cf5-c585-45d9-8b08-f59a6941e6d8",
                "isVisible": True,
                "isPurchaseQuantityLimited": False,
                "isRecommendation": False,
                "hasDependentProducts": False,
                "dependentProductIds": [],
                "isFreeShipping": False,
                "isDefaultToSubscription": False,
                "toReplaceMerchantProductIds": None,
                "isCtaCustomized": False,
                "ctaConfig": {
                    "type": "BUY_NOW",
                },
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 151,
                        "price": 167.78,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "935e3c20-64b2-4e1a-95ff-34e68bbf55f4",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
            {
                "type": "PRODUCT",
                "merchantProductId": "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7",
                "isVisible": True,
                "isPurchaseQuantityLimited": False,
                "isRecommendation": False,
                "hasDependentProducts": False,
                "dependentProductIds": [],
                "isFreeShipping": False,
                "isDefaultToSubscription": False,
                "toReplaceMerchantProductIds": None,
                "isCtaCustomized": False,
                "ctaConfig": {
                    "type": "BUY_NOW",
                },
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 372.59,
                        "price": 413.99,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "fe01f82b-267c-4dfe-bdaa-714633d1e355",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
            {
                "type": "PRODUCT",
                "merchantProductId": "a963f25a-44a3-439f-ae37-1817621f8c11",
                "isVisible": True,
                "isPurchaseQuantityLimited": False,
                "isRecommendation": False,
                "hasDependentProducts": False,
                "dependentProductIds": [],
                "isFreeShipping": False,
                "isDefaultToSubscription": False,
                "toReplaceMerchantProductIds": None,
                "isCtaCustomized": False,
                "ctaConfig": {
                    "type": "BUY_NOW",
                },
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 930.14,
                        "price": 1033.49,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "2b8ff662-991e-4909-ae80-c80b1412a6a5",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
        ],
        "accessSpecificUser": [],
        "featuredSectionEnable": False,
        "tab": {
            "value": "Commerce",
            "label": "Commerce",
            "mappingControl": [],
        },
        "timeKey": 1773726677251,
        "originEnablePaymentRestriction": False,
        "syncEnabled": False,
        "postType": "EVENT",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"140998d8-3047-4438-9b37-546c86e2ca22\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"type\":\"event-info-banner\",\"version\":2},{\"id\":\"328c7a03-7a8a-4fa8-8ed3-7edb7d772739\",\"type\":\"additional-content\",\"version\":1},{\"id\":\"607ab37b-8976-48f0-aafe-02c4f80e9c8a\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"5589beae-d2ca-40fc-b361-03122952beb2\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"ec43104d-b471-421d-b809-a1eadbdf3ff4\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"eaee3e83-4535-4ba6-8e81-6e995092aa01\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"b75b10d5-9e17-40a0-89a5-79cc5c91023a\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"a963f25a-44a3-439f-ae37-1817621f8c11\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"type\":\"horizontalrule\",\"version\":1},{\"id\":\"f416cde0-ced8-4f36-a141-c446496ed8bc\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"type\":\"post-event-description\",\"version\":2},{\"type\":\"horizontalrule\",\"version\":1},{\"id\":\"fde17b4d-12e3-4b08-83cd-8fc15cf9ea9a\",\"lineupItems\":[{\"id\":\"f06062ef-f975-4e4f-aa07-58022b234af3\",\"order\":0,\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"isHeadliner\":true}],\"width\":\"100%\",\"layout\":\"WITH_HEADLINER\",\"photoShape\":\"RECTANGLE\",\"textAlignment\":\"CENTER\",\"headlinerTitle\":\"Headliner\",\"otherSectionTitle\":\"Talent\",\"headliner\":{\"width\":\"100%\"},\"type\":\"lineup-info-banner\",\"version\":2}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
        "needRefreshHTML": True,
        "additionalContent": "{}",
        "showAdditionalContent": False,
        "media": [
            {
                "id": "7b06c8a6-ecc3-49c5-89bf-ab4b15bc4e7a",
                "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",
                "selected": True,
                "type": "IMAGE",
                "height": 2700,
                "width": 2100,
                "mediaDuration": 0,
                "mediaSrc": None,
                "mediaType": "IMAGE",
                "inherited": False,
                "position": 1,
                "referenceId": None,
                "source": None,
                "setThumbnail": False,
            },
        ],
        "othersCanCopy": False,
        "enableDownlineNote": False,
        "expiredAt": None,
        "urlAlias": "api-test-t2895",
        "headline": "API Test T2895 ",
        "isPaymentRestrictionEnabled": False,
    }, token='linda05_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: guest get token
    _resp3 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    })
    vars['access_token'] = (_resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 4: Guest visit and check the auto coupon banner response
    _resp4 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t2895'})
    # step 5: edeed7a3-ef3f-400a-9ab1-11699ed19d3a
    _resp5 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",
                "price": 56.67,
                "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "1336a11f-b5f7-4305-aae4-6c26146b1ee7",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1773714303427.697551905492792340",
            "externalId": "742c624f-79e2-4ace-96dd-a96b5dd8fbfa",
            "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2895",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "4640fcee-a802-4410-a90d-2fdd4227c777",
                "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
                "price": 56.67,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='access_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp5, 'orderId')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp5, 'orderNumber')
    # step 6: 90703ec6-7eb4-4e02-8a1c-6ac5cd9f1299
    _resp6 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",
                "price": 56.67,
                "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "a078d702-0da1-42bb-83c2-8c071f13dc71",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1773714303427.697551905492792340",
            "externalId": "742c624f-79e2-4ace-96dd-a96b5dd8fbfa",
            "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2895",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "4640fcee-a802-4410-a90d-2fdd4227c777",
                "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
                "price": 56.67,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='access_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp6, 'orderId')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp6, 'orderNumber')
    # step 7: Get consumer linda10 token
    _resp7 = ctx.api.auth.sign_in(body={
        "email": "linda.zhou.ext+10@1m.app",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp7, '$.data.token')
    # step 8: 14495694-f158-4275-861d-91faf01549b5
    _resp8 = ctx.api.cart.delete(body={}, app_headers=True, token='linda10_token')
    # assertion 8.assertion: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # assertion 8.assertion: responseJson equal success
    expect(_resp8).json('$.message').equals('success')
    # step 9: 3e59ea11-8837-471e-938e-7151823ca597
    _resp9 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",
                "price": 56.67,
                "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "1336a11f-b5f7-4305-aae4-6c26146b1ee7",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1773714303427.697551905492792340",
            "externalId": "742c624f-79e2-4ace-96dd-a96b5dd8fbfa",
            "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2895",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "4640fcee-a802-4410-a90d-2fdd4227c777",
                "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
                "price": 56.67,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='linda10_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp9, 'orderId')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp9, 'orderNumber')
    # step 10: 948e658d-e739-4485-8f70-e1c15096f756
    _resp10 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",
                "price": 56.67,
                "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "a078d702-0da1-42bb-83c2-8c071f13dc71",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1773714303427.697551905492792340",
            "externalId": "742c624f-79e2-4ace-96dd-a96b5dd8fbfa",
            "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2895",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "4640fcee-a802-4410-a90d-2fdd4227c777",
                "postId": "907f5bec-0233-4778-8f46-7820e8b2eb7c",
                "price": 56.67,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='linda10_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp10, 'orderId')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp10, 'orderNumber')
