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
    _resp1 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+05@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}', app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: bd8f74c7-a340-487a-92c7-b47ac97fe7d7
    _resp2 = ctx.api.posts.curator_24232e2c_b3af_4517_be24_4dfddb1ca79f(body='{\r\n    "id": "24232e2c-b3af-4517-be24-4dfddb1ca79f",\r\n    "announcements": [],\r\n    "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n    "title": "API Test T2487 ",\r\n    "subTitle": "",\r\n    "links": [],\r\n    "allowPromotersResell": true,\r\n    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",\r\n    "financeMode": "FINANCE_MODE_COMMISSION",\r\n    "status": "ACTIVE",\r\n    "allowPromotersHideProducts": true,\r\n    "allowPromotersCustomizeMedia": true,\r\n    "allowPromotersCreateCoupon": true,\r\n    "promotions": [\r\n        {\r\n            "amountThresholdDiscounts": [\r\n                {\r\n                    "amountThreshold": 100,\r\n                    "discountPercentage": 10\r\n                }\r\n            ],\r\n            "applicableCode": "ygzaz9jm",\r\n            "codeAliases": null,\r\n            "title": "",\r\n            "description": "",\r\n            "autoApplied": false,\r\n            "oneTimeUsePerCustomer": false,\r\n            "isExtend": false,\r\n            "startTime": "2026-03-12T09:12:48.935Z"\r\n        }\r\n    ],\r\n    "isPurchaseQuantityLimited": false,\r\n    "purchaseQuantityLimit": 0,\r\n    "isAccessRestricted": false,\r\n    "allowPromotersAccess": false,\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#FFEEBEFF",\r\n            "#E91E63FF",\r\n            "#757575FF",\r\n            "#0B99FFFF",\r\n            "#F2F2F6FF",\r\n            "#FFFFFF"\r\n        ],\r\n        "fontFamily": "Inter",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "secondaryTextColor": "#E0E0E0FF",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontSize": 24,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "subtitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 400\r\n        },\r\n        "button": {\r\n            "color": "#000000",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "secondaryButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 0\r\n        },\r\n        "textButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "fontWeight": 700\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "color": "#000000 ",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 14,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 400\r\n            },\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "product": {\r\n            "color": "#FFFFFF",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "discount": {\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF",\r\n            "backgroundColor": "#D32A09"\r\n        },\r\n        "freeShipping": {\r\n            "color": "#268E46",\r\n            "backgroundColor": "#EBF5EF"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 16,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 700\r\n            },\r\n            "button": {\r\n                "color": "#000000",\r\n                "backgroundColor": "#F6CA7C"\r\n            },\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF",\r\n            "secondaryText": "#ABABAB"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#E0E0E0FF",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "height": "MEDIUM",\r\n                "displayText": "SHOP_NAME"\r\n            },\r\n            "productBanner": {\r\n                "display": "HIDE",\r\n                "ctaButton": "VIEW_PRODUCT"\r\n            }\r\n        },\r\n        "template": "ClearSky",\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 0\r\n            }\r\n        }\r\n    },\r\n    "hideInStore": false,\r\n    "recommendationSectionTitle": "",\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "setThumbnail": true\r\n        }\r\n    ],\r\n    "checkoutInPost": true,\r\n    "allowAffiliateSharingOnly": false,\r\n    "abTestingSettings": [],\r\n    "enableAbTesting": false,\r\n    "isOrderConfirmationNoteEnabled": false,\r\n    "hideCouponBox": false,\r\n    "allowCustomizeDisplayPrices": true,\r\n    "customizeDisplayPrices": {\r\n        "price": "1930 Pacific Ave | Thu, Oct 01 (CDT)",\r\n        "discountPercent": "Get Tickets",\r\n        "titleColor": "#FFFFFF",\r\n        "priceColor": "#FFFFFF",\r\n        "discountPercentColor": "#D32A08"\r\n    },\r\n    "canSetPrice": false,\r\n    "downlineNoteBodyHtml": null,\r\n    "downlineNoteBodyJson": null,\r\n    "featuredSectionTitle": "",\r\n    "enableRedirectUrl": false,\r\n    "redirectUrl": "",\r\n    "redirectDestinationName": "",\r\n    "cardCustomizeCoverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "setThumbnail": true\r\n        }\r\n    ],\r\n    "event": {\r\n        "id": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n        "status": "UPCOMING",\r\n        "title": "API Test T4259 ",\r\n        "venue": "1930 Pacific Ave",\r\n        "location": "1930 Pacific Ave, Dallas, TX 75201, USA",\r\n        "startDateDisplay": "2026-10-01",\r\n        "endDateDisplay": null,\r\n        "timezone": {\r\n            "dstOffset": 3600,\r\n            "rawOffset": -21600,\r\n            "timeZoneId": "America/Chicago",\r\n            "timeZoneName": "Central Daylight Time"\r\n        },\r\n        "poster": {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "position": 0,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    },\r\n    "additionalContentPosition": "aboveTickets",\r\n    "bodyHtml": "<div data-id=\\"7e9b1b84-b3b3-4298-a720-5b73610a7812\\" data-type=\\"event-info-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-width=\\"100%\\"></div><div data-id=\\"890482c4-1a37-4069-82e8-2c5fa6ea7342\\" data-type=\\"additional-content\\"></div><div data-id=\\"87cf79be-1c28-481b-9346-fab65fa06bd1\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"5589beae-d2ca-40fc-b361-03122952beb2\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"15db9920-2096-460b-ac66-0bf41c4907f9\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"ab3c87b9-b7ec-483f-8855-506aa9d6f7d4\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"9b1034fb-41bf-41c3-8a0b-127297ae6f9a\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a963f25a-44a3-439f-ae37-1817621f8c11\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><hr><div data-id=\\"61325d70-2348-4022-9fa4-1b152231069f\\" data-type=\\"post-event-description\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-width=\\"100%\\"></div>",\r\n    "currentDate": "2026-03-12T09:12:26.839Z",\r\n    "relatedProducts": [\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "5589beae-d2ca-40fc-b361-03122952beb2",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 51,\r\n                    "price": 56.67,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "f0a91cf5-c585-45d9-8b08-f59a6941e6d8",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 151,\r\n                    "price": 167.78,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "935e3c20-64b2-4e1a-95ff-34e68bbf55f4",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 372.59,\r\n                    "price": 413.99,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "fe01f82b-267c-4dfe-bdaa-714633d1e355",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a963f25a-44a3-439f-ae37-1817621f8c11",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 930.14,\r\n                    "price": 1033.49,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "2b8ff662-991e-4909-ae80-c80b1412a6a5",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "accessSpecificUser": [],\r\n    "featuredSectionEnable": false,\r\n    "tab": {\r\n        "value": "Commerce",\r\n        "label": "Commerce",\r\n        "mappingControl": []\r\n    },\r\n    "timeKey": 1773306746839,\r\n    "originEnablePaymentRestriction": false,\r\n    "syncEnabled": false,\r\n    "postType": "EVENT",\r\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"id\\":\\"7e9b1b84-b3b3-4298-a720-5b73610a7812\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"type\\":\\"event-info-banner\\",\\"version\\":2},{\\"id\\":\\"890482c4-1a37-4069-82e8-2c5fa6ea7342\\",\\"type\\":\\"additional-content\\",\\"version\\":1},{\\"id\\":\\"87cf79be-1c28-481b-9346-fab65fa06bd1\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"5589beae-d2ca-40fc-b361-03122952beb2\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"15db9920-2096-460b-ac66-0bf41c4907f9\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"ab3c87b9-b7ec-483f-8855-506aa9d6f7d4\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"9b1034fb-41bf-41c3-8a0b-127297ae6f9a\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a963f25a-44a3-439f-ae37-1817621f8c11\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"type\\":\\"horizontalrule\\",\\"version\\":1},{\\"id\\":\\"61325d70-2348-4022-9fa4-1b152231069f\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"type\\":\\"post-event-description\\",\\"version\\":2}],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1},\\"containerClassName\\":\\"\\",\\"editorClassName\\":\\"\\"}",\r\n    "needRefreshHTML": true,\r\n    "additionalContent": "{}",\r\n    "showAdditionalContent": false,\r\n    "media": [\r\n        {\r\n            "id": "08f2a795-18a6-4232-98c6-37595c43f617",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "selected": true,\r\n            "type": "IMAGE",\r\n            "height": 2700,\r\n            "width": 2100,\r\n            "mediaDuration": 0,\r\n            "mediaSrc": null,\r\n            "mediaType": "IMAGE",\r\n            "inherited": false,\r\n            "position": 1,\r\n            "referenceId": null,\r\n            "source": null,\r\n            "setThumbnail": false\r\n        }\r\n    ],\r\n    "othersCanCopy": false,\r\n    "enableDownlineNote": false,\r\n    "expiredAt": null,\r\n    "urlAlias": "api-test-t2487",\r\n    "headline": "API Test T2487",\r\n    "isPaymentRestrictionEnabled": false\r\n}', token='linda05_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: guest get token
    _resp3 = ctx.api.auth.guest_login(body='{\n    "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda"\n}')
    vars['access_token'] = (_resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # --- 人工补丁：先清空 guest 购物车 ---
    # 该 guest consumer（bc9a5b70…）的购物车在服务端是持久化的。历史运行如果没走到
    # checkout 后的收尾，就会残留购物车行；本次 buy-now(qty=2) 与残留行叠加后，
    # step7 的 `items[0].quantity/subtotal` 断言仍能通过（只校验首行），但 checkout 会把
    # 两行都算进去 → totalToPay=113.34 而非期望的 56.67。
    # 套件里其余 81 个用例都会先 DELETE /cart，唯独这条漏了；补上以保证可重复执行。
    ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # step 4: 5a7c7672-3428-4e58-9521-f17a335f20bf
    _resp4 = ctx.api.orders.buy_now(body='{\r\n    "postIdForFilter": "24232e2c-b3af-4517-be24-4dfddb1ca79f",\r\n    "updateCartItems": [\r\n        {\r\n            "quantity": 2,\r\n            "promoterProductVariantId": "b50e488e-575c-4e8c-81a4-881c9708fd6d",\r\n            "price": 56.67,\r\n            "postId": "24232e2c-b3af-4517-be24-4dfddb1ca79f",\r\n            "selected": true,\r\n            "customFields": []\r\n        }\r\n    ],\r\n    "fbAdParams": {\r\n        "eventID": "ba8bd15d-e654-4150-9f83-3a4627ee3641",\r\n        "pixelId": [\r\n            "268933192948110"\r\n        ],\r\n        "fbBrowserId": "fb.1.1773391988545.970780213906643546",\r\n        "externalId": "73d2a9f5-6635-45b7-97a7-d84d1b66377c",\r\n        "eventSourceUrl": "https://release.pear.us/resident/post/api-test-t2487"\r\n    },\r\n    "currentUpdateCartItems": [\r\n        {\r\n            "quantity": 2,\r\n            "id": "b50e488e-575c-4e8c-81a4-881c9708fd6d",\r\n            "postId": "24232e2c-b3af-4517-be24-4dfddb1ca79f",\r\n            "price": 113.34,\r\n            "customFields": []\r\n        }\r\n    ]\r\n}', app_headers=True, token='access_token')
    ctx.extract('orderId', _resp4, '$.data.orderId')
    ctx.extract('orderNumber', _resp4, '$.data.orderNumber')
    # step 5: dc8ea801-3fd0-4d34-86bd-59b5f0b311eb
    _resp5 = ctx.api.orders.update_promotions(body='{\r\n    "postIdForFilter": "24232e2c-b3af-4517-be24-4dfddb1ca79f",\r\n    "orderId": "{{orderId}}",\r\n    "shippingAddress": {\r\n        "line1": "",\r\n        "city": "",\r\n        "zipcode": "",\r\n        "state": ""\r\n    },\r\n    "applicableCode": "ygzaz9jm"\r\n}', app_headers=True, token='access_token')
    ctx.extract('currentOrderId', _resp5, '$.data.orderId')
    # step 6: c2514d17-9d6e-47e8-8ff6-47ad80335e43
    _resp6 = ctx.api.cart.update(body='{\r\n    "items": [\r\n        {\r\n            "id": "{{orderId}}",\r\n            "quantity": -1,\r\n            "promoterProductVariantId": "b50e488e-575c-4e8c-81a4-881c9708fd6d",\r\n            "price": 56.67,\r\n            "postId": "24232e2c-b3af-4517-be24-4dfddb1ca79f",\r\n            "selected": true\r\n        }\r\n    ],\r\n    "lite": false\r\n}', app_headers=True, token='access_token')
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # assertion 6.assertion: responseJson equal 1
    expect(_resp6).json('$.data.items[0].quantity').equals('1')
    # assertion 6.assertion: responseJson equal 56.67
    expect(_resp6).json('$.data.items[0].subtotal').equals('56.67')
    # step 7: b4248f82-3498-44d0-9218-9cef1b7eb0c3
    _resp7 = ctx.api.orders.checkout(body='{}', app_headers=True, token='access_token')
    # assertion 7.assertion: responseJson equal 56.67
    expect(_resp7).json('$.data.totalToPay').equals('56.67')
    # extractor: neworderId = $.data.orderId
    ctx.extract('neworderId', _resp7, '$.data.orderId')
    # step 8: 80bfe5e9-3436-4ffb-b5a4-0f2ca5b8e1ba
    _resp8 = ctx.api.orders.update_promotions(body='{\r\n    "orderId": "{{neworderId}}",\r\n    "shippingAddress": {\r\n        "line1": "",\r\n        "city": "",\r\n        "zipcode": "",\r\n        "state": ""\r\n    },\r\n    "applicableCode": "ygzaz9jm"\r\n}', app_headers=True, token='access_token')
