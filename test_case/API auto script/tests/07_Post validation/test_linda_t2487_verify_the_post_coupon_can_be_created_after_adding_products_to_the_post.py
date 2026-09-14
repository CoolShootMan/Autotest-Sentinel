"""Migrated from Apifox case #8014988. Source folder: Post validation."""
# Apifox Case ID: 8014988  (traceability only — not needed to run)
NAME = "Verify the post coupon can be created after adding products to the post"
TAGS = ["p2", "post_validation", "suite:linda"]
PRIORITY = 2


CASE_ID = 8014988
ENV_NAME = "Release"

# --- step 1: Get Partner linda05 token ---
# post[extractor]: {"variableName": "linda05_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: bd8f74c7-a340-487a-92c7-b47ac97fe7d7 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: guest get token ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 4: 5a7c7672-3428-4e58-9521-f17a335f20bf ---
# post[customScript]: // 1. Parse the response body
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: 
# post: /**
# post:  * 2. Strict Validation for totalToPay
# post:  * Validates that the payment amount is exactly 113.34
# post:  */
# post: pm.test("Verify totalToPay is 113.34", () => {
# post:     // Using eql to check the numeric value strictly
# post:     pm.expect(data.totalToPay, `Expected 113.34 but received ${data.totalToPay}`).to.eql(113.34);
# post: });
# post: 
# post: /**
# post:  * 3. Extract orderId and orderNumber
# post:  * These values are saved as environment variables for use in subsequent requests
# post:  */
# post: if (data.orderId && data.orderNumber) {
# post:     pm.environment.set("orderId", data.orderId);
# post:     pm.environment.set("orderNumber", data.orderNumber);
# post:     
# post:     // Log the results for visibility in the console
# post:     console.log("✅ Extraction Successful:");
# post:     console.log(`   - orderId: ${data.orderId}`);
# post:     console.log(`   - orderNumber: ${data.orderNumber}`);
# post: } else {
# post:     console.error("❌ Extraction Failed: orderId or orderNumber missing in response.");
# post: }
# post: 
# post: /**
# post:  * 4. General Integrity Check
# post:  */
# post: pm.test("Response contains required order metadata", () => {
# post:     pm.expect(data).to.have.property('orderId');
# post:     pm.expect(data).to.have.property('orderNumber');
# post: });
# --- step 5: dc8ea801-3fd0-4d34-86bd-59b5f0b311eb ---
# post[customScript]: // 1. Parse the response body
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: 
# post: /**
# post:  * 2. Main Financial Fields Validation
# post:  * Validates the subtotal, discounts, and final payment amounts.
# post:  */
# post: pm.test("Verify Main Financial Summary", () => {
# post:     pm.expect(data.productSubtotal, "productSubtotal mismatch").to.eql(113.34);
# post:     pm.expect(data.totalLineItemPrice, "totalLineItemPrice mismatch").to.eql(113.34);
# post:     pm.expect(data.totalLineItemCouponDiscount, "totalLineItemCouponDiscount mismatch").to.eql(11.33);
# post:     pm.expect(data.totalLineItemSampleDiscount, "totalLineItemSampleDiscount mismatch").to.eql(0);
# post:     pm.expect(data.totalLineItemSubscriptionDiscount, "totalLineItemSubscriptionDiscount mismatch").to.eql(0);
# post:     pm.expect(data.totalLineItemDiscount, "totalLineItemDiscount mismatch").to.eql(0);
# post:     pm.expect(data.totalLineItemSubtotal, "totalLineItemSubtotal mismatch").to.eql(102.01);
# post:     pm.expect(data.totalToPay, "totalToPay mismatch").to.eql(102.01);
# post: });
# post: 
# post: /**
# post:  * 3. Coupon Application Validation (appliedPromotions)
# post:  * Specifically checks for the code "ygzaz9jm" and its associated values.
# post:  */
# post: pm.test("Verify Coupon 'ygzaz9jm' Application Details", () => {
# post:     const promotions = data.appliedPromotions || [];
# post:     
# post:     // Ensure at least one promotion is applied
# post:     pm.expect(promotions, "No promotions were applied").to.be.an('array').that.is.not.empty;
# post: 
# post:     // Find the specific coupon in the list
# post:     const targetCoupon = promotions.find(p => p.appliedCode === "ygzaz9jm");
# post:     
# post:     pm.expect(targetCoupon, "Coupon 'ygzaz9jm' not found in appliedPromotions").to.not.be.undefined;
# post:     
# post:     // Detailed field validation for the coupon
# post:     pm.expect(targetCoupon.autoApplied, "autoApplied should be false").to.eql(false);
# post:     pm.expect(targetCoupon.applicableCode, "applicableCode mismatch").to.eql("ygzaz9jm");
# post:     pm.expect(targetCoupon.subtotalDiscount, "subtotalDiscount mismatch").to.eql(11.33);
# post:     
# post:     // Verify Payment Contract
# post:     pm.expect(targetCoupon.paymentContract.subsidizedPercentage, "subsidizedPercentage mismatch").to.eql(100);
# post: });
# post: 
# post: /**
# post:  * 4. Extraction for next steps (Optional)
# post:  */
# post: if (data.orderId) {
# post:     pm.environment.set("currentOrderId", data.orderId);
# post:     console.log(`✅ Order ${data.orderNumber} validated and Coupon ygzaz9jm applied successfully.`);
# post: }
# --- step 6: c2514d17-9d6e-47e8-8ff6-47ad80335e43 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "1", "path": "$.data.items[0].quantity", "multipleValue": [], "extractSettings": {"expression": "$.data.items[0].quantity", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "56.67", "path": "$.data.items[0].subtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.items[0].subtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: b4248f82-3498-44d0-9218-9cef1b7eb0c3 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "56.67", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "neworderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: 80bfe5e9-3436-4ffb-b5a4-0f2ca5b8e1ba ---
# post[customScript]: // Parse the response body to JSON
# post: const response = pm.response.json();
# post: 
# post: // 1. Assert: totalToPay should be equal to 56.67
# post: pm.test("Check if 'totalToPay' is 56.67", () => {
# post:     pm.expect(response.data.totalToPay).to.eql(56.67);
# post: });
# post: 
# post: // 2. Assert: appliedPromotions should be an empty array
# post: pm.test("Check if 'appliedPromotions' is an empty array", () => {
# post:     pm.expect(response.data.appliedPromotions).to.be.an('array').that.is.empty;
# post: });
# post: 
# post: // 3. Assert: Check for specific promotion error in 'errorPromotionMsg' array
# post: pm.test("Verify 'errorPromotionMsg' contains specific promotion error", () => {
# post:     const errorMsgs = response.data.errorPromotionMsg;
# post:     
# post:     // Check if the array exists and is not empty
# post:     pm.expect(errorMsgs).to.be.an('array').that.is.not.empty;
# post: 
# post:     // Find the specific error object in the array
# post:     const targetError = errorMsgs.find(msg => 
# post:         msg.promotionCode === "ygzaz9jm" && 
# post:         msg.errorType === "INVALID_BY_THRESHOLD"
# post:     );
# post: 
# post:     // Assert the target error was found
# post:     pm.expect(targetError).to.not.be.undefined;
# post:     
# post:     // Optional: Log the result for debugging
# post:     if (targetError) {
# post:         console.log("Found expected promotion error:", targetError);
# post:     }
# post: });




import json

from core.assertions import expect

def test_linda_t2487_verify_the_post_coupon_can_be_created_after_adding_products_to_the_post(ctx):
    """Apifox case #8014988: Linda_T2487_Verify_the_post_coupon_can_be_created_after_adding_products_to_the_p"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body={
        "email": "linda.zhou.ext+05@1m.app",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: bd8f74c7-a340-487a-92c7-b47ac97fe7d7
    _resp2 = ctx.api.posts.curator_24232e2c_b3af_4517_be24_4dfddb1ca79f(body={
        "id": "24232e2c-b3af-4517-be24-4dfddb1ca79f",
        "announcements": [],
        "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",
        "title": "API Test T2487 ",
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
                "amountThresholdDiscounts": [
                    {
                        "amountThreshold": 100,
                        "discountPercentage": 10,
                    },
                ],
                "applicableCode": "ygzaz9jm",
                "codeAliases": None,
                "title": "",
                "description": "",
                "autoApplied": False,
                "oneTimeUsePerCustomer": False,
                "isExtend": False,
                "startTime": "2026-03-12T09:12:48.935Z",
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
                "setThumbnail": True,
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
            "price": "1930 Pacific Ave | Thu, Oct 01 (CDT)",
            "discountPercent": "Get Tickets",
            "titleColor": "#FFFFFF",
            "priceColor": "#FFFFFF",
            "discountPercentColor": "#D32A08",
        },
        "canSetPrice": False,
        "downlineNoteBodyHtml": None,
        "downlineNoteBodyJson": None,
        "featuredSectionTitle": "",
        "enableRedirectUrl": False,
        "redirectUrl": "",
        "redirectDestinationName": "",
        "cardCustomizeCoverImages": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",
                "width": 2100,
                "height": 2700,
                "mediaSrc": None,
                "position": 1,
                "mediaType": "IMAGE",
                "mediaDuration": 0,
                "setThumbnail": True,
            },
        ],
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
        "bodyHtml": "<div data-id=\"7e9b1b84-b3b3-4298-a720-5b73610a7812\" data-type=\"event-info-banner\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-width=\"100%\"></div><div data-id=\"890482c4-1a37-4069-82e8-2c5fa6ea7342\" data-type=\"additional-content\"></div><div data-id=\"87cf79be-1c28-481b-9346-fab65fa06bd1\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"5589beae-d2ca-40fc-b361-03122952beb2\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"15db9920-2096-460b-ac66-0bf41c4907f9\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"ab3c87b9-b7ec-483f-8855-506aa9d6f7d4\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"9b1034fb-41bf-41c3-8a0b-127297ae6f9a\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"a963f25a-44a3-439f-ae37-1817621f8c11\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><hr><div data-id=\"61325d70-2348-4022-9fa4-1b152231069f\" data-type=\"post-event-description\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-width=\"100%\"></div>",
        "currentDate": "2026-03-12T09:12:26.839Z",
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
        "timeKey": 1773306746839,
        "originEnablePaymentRestriction": False,
        "syncEnabled": False,
        "postType": "EVENT",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"7e9b1b84-b3b3-4298-a720-5b73610a7812\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"type\":\"event-info-banner\",\"version\":2},{\"id\":\"890482c4-1a37-4069-82e8-2c5fa6ea7342\",\"type\":\"additional-content\",\"version\":1},{\"id\":\"87cf79be-1c28-481b-9346-fab65fa06bd1\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"5589beae-d2ca-40fc-b361-03122952beb2\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"15db9920-2096-460b-ac66-0bf41c4907f9\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"ab3c87b9-b7ec-483f-8855-506aa9d6f7d4\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"9b1034fb-41bf-41c3-8a0b-127297ae6f9a\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"a963f25a-44a3-439f-ae37-1817621f8c11\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"type\":\"horizontalrule\",\"version\":1},{\"id\":\"61325d70-2348-4022-9fa4-1b152231069f\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"type\":\"post-event-description\",\"version\":2}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
        "needRefreshHTML": True,
        "additionalContent": "{}",
        "showAdditionalContent": False,
        "media": [
            {
                "id": "08f2a795-18a6-4232-98c6-37595c43f617",
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
        "urlAlias": "api-test-t2487",
        "headline": "API Test T2487",
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
    # --- 人工补丁：先清空 guest 购物车 ---
    # 该 guest consumer（bc9a5b70…）的购物车在服务端是持久化的。历史运行如果没走到
    # checkout 后的收尾，就会残留购物车行；本次 buy-now(qty=2) 与残留行叠加后，
    # step7 的 `items[0].quantity/subtotal` 断言仍能通过（只校验首行），但 checkout 会把
    # 两行都算进去 → totalToPay=113.34 而非期望的 56.67。
    # 套件里其余 81 个用例都会先 DELETE /cart，唯独这条漏了；补上以保证可重复执行。
    ctx.api.cart.delete(body={}, app_headers=True, token='access_token')
    # step 4: 5a7c7672-3428-4e58-9521-f17a335f20bf
    _resp4 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "24232e2c-b3af-4517-be24-4dfddb1ca79f",
        "updateCartItems": [
            {
                "quantity": 2,
                "promoterProductVariantId": "b50e488e-575c-4e8c-81a4-881c9708fd6d",
                "price": 56.67,
                "postId": "24232e2c-b3af-4517-be24-4dfddb1ca79f",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "ba8bd15d-e654-4150-9f83-3a4627ee3641",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1773391988545.970780213906643546",
            "externalId": "73d2a9f5-6635-45b7-97a7-d84d1b66377c",
            "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2487",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 2,
                "id": "b50e488e-575c-4e8c-81a4-881c9708fd6d",
                "postId": "24232e2c-b3af-4517-be24-4dfddb1ca79f",
                "price": 113.34,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='access_token')
    ctx.extract('orderId', _resp4, '$.data.orderId')
    ctx.extract('orderNumber', _resp4, '$.data.orderNumber')
    # step 5: dc8ea801-3fd0-4d34-86bd-59b5f0b311eb
    _resp5 = ctx.api.orders.update_promotions(body={
        "postIdForFilter": "24232e2c-b3af-4517-be24-4dfddb1ca79f",
        "orderId": "{{orderId}}",
        "shippingAddress": {
            "line1": "",
            "city": "",
            "zipcode": "",
            "state": "",
        },
        "applicableCode": "ygzaz9jm",
    }, app_headers=True, token='access_token')
    ctx.extract('currentOrderId', _resp5, '$.data.orderId')
    # step 6: c2514d17-9d6e-47e8-8ff6-47ad80335e43
    _resp6 = ctx.api.cart.update(body={
        "items": [
            {
                "id": "{{orderId}}",
                "quantity": -1,
                "promoterProductVariantId": "b50e488e-575c-4e8c-81a4-881c9708fd6d",
                "price": 56.67,
                "postId": "24232e2c-b3af-4517-be24-4dfddb1ca79f",
                "selected": True,
            },
        ],
        "lite": False,
    }, app_headers=True, token='access_token')
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # assertion 6.assertion: responseJson equal 1
    expect(_resp6).json('$.data.items[0].quantity').equals('1')
    # assertion 6.assertion: responseJson equal 56.67
    expect(_resp6).json('$.data.items[0].subtotal').equals('56.67')
    # step 7: b4248f82-3498-44d0-9218-9cef1b7eb0c3
    _resp7 = ctx.api.orders.checkout(body={}, app_headers=True, token='access_token')
    # assertion 7.assertion: responseJson equal 56.67
    expect(_resp7).json('$.data.totalToPay').equals('56.67')
    # extractor: neworderId = $.data.orderId
    ctx.extract('neworderId', _resp7, '$.data.orderId')
    # step 8: 80bfe5e9-3436-4ffb-b5a4-0f2ca5b8e1ba
    _resp8 = ctx.api.orders.update_promotions(body={
        "orderId": "{{neworderId}}",
        "shippingAddress": {
            "line1": "",
            "city": "",
            "zipcode": "",
            "state": "",
        },
        "applicableCode": "ygzaz9jm",
    }, app_headers=True, token='access_token')
