"""Migrated from Apifox case #8038584. Source folder: Post validation."""
# Apifox Case ID: 8038584  (traceability only — not needed to run)
NAME = "Verify the checked \"For recommendation\" and \"Recommended products\" response logic correct"
TAGS = ["p1", "post_validation", "suite:linda"]
PRIORITY = 1


CASE_ID = 8038584
ENV_NAME = "Release"

# --- step 1: 1ed004ca-9615-47c9-9d46-6e774aa66402 ---
# --- step 2: guest get token ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 3: Guest visit and check the post product recommendation response ---
# post[customScript]: /**
# post:  * Strict validation for Recommendation logic and Product IDs
# post:  */
# post: 
# post: const responseData = pm.response.json();
# post: const data = responseData.data;
# post: 
# post: // 1. Validate the Recommendation Section Title
# post: pm.test("Confirm recommendationSectionTitle is exactly 'You may also like'", function () {
# post:     pm.expect(data.recommendationSectionTitle).to.eql("You may also like");
# post: });
# post: 
# post: // 2. Strict validation for Product IDs and their isRecommendation status
# post: pm.test("Strictly verify isRecommendation status for specific Product IDs", function () {
# post:     const products = data.relatedProducts;
# post: 
# post:     // Define the expectation mapping
# post:     const expectedStatus = {
# post:         // Expected True
# post:         "e580e57e-7ca4-4f5a-ae3d-fd7f9b932a61": true,
# post:         "64594457-03ca-4049-911f-3862ef9bc156": true,
# post:         // Expected False
# post:         "c289fd5c-8a12-4cd0-b175-628af6fe1300": false,
# post:         "65b5c286-7ddf-474f-97cd-f0aff5550b34": false
# post:     };
# post: 
# post:     products.forEach(product => {
# post:         const pId = product.promoterProductId;
# post:         
# post:         // If the product ID is in our checklist, verify its status
# post:         if (expectedStatus.hasOwnProperty(pId)) {
# post:             const expectedValue = expectedStatus[pId];
# post:             pm.test(`Product ${pId} should have isRecommendation: ${expectedValue}`, function() {
# post:                 pm.expect(product.isRecommendation).to.equal(expectedValue);
# post:             });
# post:         }
# post:     });
# post: });
# post: 
# post: // 3. Verify that all 4 required products actually exist in the response
# post: pm.test("Ensure all 4 target Product IDs are present in the response", function () {
# post:     const requiredIds = [
# post:         "e580e57e-7ca4-4f5a-ae3d-fd7f9b932a61",
# post:         "64594457-03ca-4049-911f-3862ef9bc156",
# post:         "c289fd5c-8a12-4cd0-b175-628af6fe1300",
# post:         "65b5c286-7ddf-474f-97cd-f0aff5550b34"
# post:     ];
# post:     
# post:     const actualIds = data.relatedProducts.map(p => p.promoterProductId);
# post:     
# post:     requiredIds.forEach(id => {
# post:         pm.expect(actualIds).to.include(id, `Required Product ID ${id} is missing from the response!`);
# post:     });
# post: });
# --- step 4: Consumer visit and check the post product recommendation response ---
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
# post[customScript]: /**
# post:  * Strict validation for Recommendation logic and Product IDs
# post:  */
# post: 
# post: const responseData = pm.response.json();
# post: const data = responseData.data;
# post: 
# post: // 1. Validate the Recommendation Section Title
# post: pm.test("Confirm recommendationSectionTitle is exactly 'You may also like'", function () {
# post:     pm.expect(data.recommendationSectionTitle).to.eql("You may also like");
# post: });
# post: 
# post: // 2. Strict validation for Product IDs and their isRecommendation status
# post: pm.test("Strictly verify isRecommendation status for specific Product IDs", function () {
# post:     const products = data.relatedProducts;
# post: 
# post:     // Define the expectation mapping
# post:     const expectedStatus = {
# post:         // Expected True
# post:         "e580e57e-7ca4-4f5a-ae3d-fd7f9b932a61": true,
# post:         "64594457-03ca-4049-911f-3862ef9bc156": true,
# post:         // Expected False
# post:         "c289fd5c-8a12-4cd0-b175-628af6fe1300": false,
# post:         "65b5c286-7ddf-474f-97cd-f0aff5550b34": false
# post:     };
# post: 
# post:     products.forEach(product => {
# post:         const pId = product.promoterProductId;
# post:         
# post:         // If the product ID is in our checklist, verify its status
# post:         if (expectedStatus.hasOwnProperty(pId)) {
# post:             const expectedValue = expectedStatus[pId];
# post:             pm.test(`Product ${pId} should have isRecommendation: ${expectedValue}`, function() {
# post:                 pm.expect(product.isRecommendation).to.equal(expectedValue);
# post:             });
# post:         }
# post:     });
# post: });
# post: 
# post: // 3. Verify that all 4 required products actually exist in the response
# post: pm.test("Ensure all 4 target Product IDs are present in the response", function () {
# post:     const requiredIds = [
# post:         "e580e57e-7ca4-4f5a-ae3d-fd7f9b932a61",
# post:         "64594457-03ca-4049-911f-3862ef9bc156",
# post:         "c289fd5c-8a12-4cd0-b175-628af6fe1300",
# post:         "65b5c286-7ddf-474f-97cd-f0aff5550b34"
# post:     ];
# post:     
# post:     const actualIds = data.relatedProducts.map(p => p.promoterProductId);
# post:     
# post:     requiredIds.forEach(id => {
# post:         pm.expect(actualIds).to.include(id, `Required Product ID ${id} is missing from the response!`);
# post:     });
# post: });




import json

from core.assertions import expect

def test_linda_t2917_verify_the_checked_for_recommendation_and_recommended_products_response_logic_correct(ctx):
    """Apifox case #8038584: Linda_T2917_Verify_the_checked_For_recommendation_and_Recommended_products_respo"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 1ed004ca-9615-47c9-9d46-6e774aa66402
    _resp1 = ctx.api.posts.curator_ff9274b0_b4b1_442c_b9ea_afcaf67912ae(body='{\r\n    "id": "ff9274b0-b4b1-442c-b9ea-afcaf67912ae",\r\n    "announcements": [],\r\n    "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n    "title": "API Test T2917",\r\n    "subTitle": "",\r\n    "links": [],\r\n    "allowPromotersResell": true,\r\n    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",\r\n    "financeMode": "FINANCE_MODE_COMMISSION",\r\n    "status": "ACTIVE",\r\n    "allowPromotersHideProducts": true,\r\n    "allowPromotersCustomizeMedia": true,\r\n    "allowPromotersCreateCoupon": true,\r\n    "promotions": [],\r\n    "isPurchaseQuantityLimited": false,\r\n    "purchaseQuantityLimit": 0,\r\n    "isAccessRestricted": false,\r\n    "allowPromotersAccess": false,\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#FFEEBEFF",\r\n            "#E91E63FF",\r\n            "#757575FF",\r\n            "#0B99FFFF",\r\n            "#F2F2F6FF",\r\n            "#FFFFFF"\r\n        ],\r\n        "fontFamily": "Inter",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "dividerColor": "#FFFFFF",\r\n        "secondaryTextColor": "#E0E0E0FF",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontSize": 40,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "subtitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 400\r\n        },\r\n        "button": {\r\n            "color": "#000000",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#0000",\r\n            "borderRadius": 12,\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "secondaryButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 12\r\n        },\r\n        "textButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "fontWeight": 700\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "color": "#000000 ",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 99,\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 14,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 400\r\n            },\r\n            "borderRadius": 16,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "product": {\r\n            "color": "#FFFFFF",\r\n            "borderRadius": 8,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "discount": {\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF",\r\n            "backgroundColor": "#D32A09"\r\n        },\r\n        "freeShipping": {\r\n            "color": "#268E46",\r\n            "backgroundColor": "#EBF5EF"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 16,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 700\r\n            },\r\n            "button": {\r\n                "color": "#000000",\r\n                "backgroundColor": "#F6CA7C"\r\n            },\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF",\r\n            "secondaryText": "#ABABAB"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#E0E0E0FF",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "header": {\r\n            "backgroundColor": "#FFFFFF"\r\n        },\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "height": "MEDIUM",\r\n                "displayText": "SHOP_NAME"\r\n            },\r\n            "productBanner": {\r\n                "display": "HIDE",\r\n                "ctaButton": "VIEW_PRODUCT"\r\n            }\r\n        },\r\n        "template": "ShadowFocus",\r\n        "detailTextColor": "#110921",\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 8\r\n            }\r\n        }\r\n    },\r\n    "hideInStore": false,\r\n    "recommendationSectionTitle": "You may also like",\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    ],\r\n    "checkoutInPost": true,\r\n    "allowAffiliateSharingOnly": false,\r\n    "abTestingSettings": [],\r\n    "enableAbTesting": false,\r\n    "isOrderConfirmationNoteEnabled": false,\r\n    "hideCouponBox": false,\r\n    "allowCustomizeDisplayPrices": true,\r\n    "customizeDisplayPrices": {\r\n        "price": "1930 Pacific Ave | Thu, Oct 01 (CDT)",\r\n        "priceColor": "#FFFFFF",\r\n        "titleColor": "#FFFFFF",\r\n        "discountPercent": "Get Tickets",\r\n        "discountPercentColor": "#D32A08"\r\n    },\r\n    "canSetPrice": false,\r\n    "downlineNoteBodyHtml": null,\r\n    "downlineNoteBodyJson": null,\r\n    "featuredSectionTitle": "Featured products",\r\n    "enableRedirectUrl": false,\r\n    "redirectUrl": "",\r\n    "redirectDestinationName": "",\r\n    "cardCustomizeCoverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "mediaSrc": null,\r\n            "inherited": false,\r\n            "mediaType": "IMAGE",\r\n            "setThumbnail": true,\r\n            "mediaDuration": 0\r\n        }\r\n    ],\r\n    "event": {\r\n        "id": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n        "status": "UPCOMING",\r\n        "title": "API Test T4259 ",\r\n        "venue": "1930 Pacific Ave",\r\n        "location": "1930 Pacific Ave, Dallas, TX 75201, USA",\r\n        "startDateDisplay": "2026-10-01",\r\n        "endDateDisplay": null,\r\n        "timezone": {\r\n            "dstOffset": 3600,\r\n            "rawOffset": -21600,\r\n            "timeZoneId": "America/Chicago",\r\n            "timeZoneName": "Central Daylight Time"\r\n        },\r\n        "poster": {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "position": 0,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    },\r\n    "additionalContentPosition": "aboveTickets",\r\n    "bodyHtml": "<div data-id=\\"cdbd0eeb-4525-4495-8d4a-be7335f41c15\\" data-type=\\"event-info-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-width=\\"100%\\"></div><div data-id=\\"0ab44132-49a9-4e77-b6af-67518473766c\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"5589beae-d2ca-40fc-b361-03122952beb2\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"fcd61831-2587-4f92-a372-9e6baa41de22\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"0b56cb27-2c09-4677-8873-f8eaae4ecdd6\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"06450775-aeed-4432-b7a3-c161e7098261\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a963f25a-44a3-439f-ae37-1817621f8c11\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><hr><div data-id=\\"5b22b73d-bd68-4b10-b323-4c7cfaf196b5\\" data-type=\\"post-event-description\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-width=\\"100%\\"></div><hr><div data-id=\\"ec8ba8ab-f6bd-404e-b938-f85125badf0f\\" data-type=\\"lineup-info-banner\\" data-lineup-items=\\"[{&quot;id&quot;:&quot;f06062ef-f975-4e4f-aa07-58022b234af3&quot;,&quot;order&quot;:0,&quot;eventId&quot;:&quot;0fe6623e-a3ba-40fb-815d-3d6f444775c3&quot;,&quot;isHeadliner&quot;:true}]\\" data-width=\\"100%\\" data-layout=\\"WITH_HEADLINER\\" data-photo-shape=\\"RECTANGLE\\" data-text-alignment=\\"CENTER\\" data-headliner=\\"{&quot;width&quot;:&quot;100%&quot;}\\"></div><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p>",\r\n    "currentDate": "2026-03-17T07:32:37.736Z",\r\n    "relatedProducts": [\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "5589beae-d2ca-40fc-b361-03122952beb2",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": true,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 51,\r\n                    "price": 56.67,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "f0a91cf5-c585-45d9-8b08-f59a6941e6d8",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": true,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 151,\r\n                    "price": 167.78,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "935e3c20-64b2-4e1a-95ff-34e68bbf55f4",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 372.59,\r\n                    "price": 413.99,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "fe01f82b-267c-4dfe-bdaa-714633d1e355",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a963f25a-44a3-439f-ae37-1817621f8c11",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 930.14,\r\n                    "price": 1033.49,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "2b8ff662-991e-4909-ae80-c80b1412a6a5",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "accessSpecificUser": [],\r\n    "featuredSectionEnable": true,\r\n    "tab": {\r\n        "value": "Commerce",\r\n        "label": "Commerce",\r\n        "mappingControl": []\r\n    },\r\n    "timeKey": 1773732757736,\r\n    "originEnablePaymentRestriction": false,\r\n    "syncEnabled": false,\r\n    "postType": "EVENT",\r\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"id\\":\\"cdbd0eeb-4525-4495-8d4a-be7335f41c15\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"width\\":\\"100%\\",\\"type\\":\\"event-info-banner\\",\\"version\\":2},{\\"id\\":\\"0ab44132-49a9-4e77-b6af-67518473766c\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"5589beae-d2ca-40fc-b361-03122952beb2\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"thumbnailDisplay\\":\\"showThumbnail\\",\\"eventNotesDisplay\\":\\"showEventNotes\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"fcd61831-2587-4f92-a372-9e6baa41de22\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"thumbnailDisplay\\":\\"showThumbnail\\",\\"eventNotesDisplay\\":\\"showEventNotes\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"0b56cb27-2c09-4677-8873-f8eaae4ecdd6\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"thumbnailDisplay\\":\\"showThumbnail\\",\\"eventNotesDisplay\\":\\"showEventNotes\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"06450775-aeed-4432-b7a3-c161e7098261\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a963f25a-44a3-439f-ae37-1817621f8c11\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"thumbnailDisplay\\":\\"showThumbnail\\",\\"eventNotesDisplay\\":\\"showEventNotes\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"type\\":\\"horizontalrule\\",\\"version\\":1,\\"width\\":\\"100%\\"},{\\"id\\":\\"5b22b73d-bd68-4b10-b323-4c7cfaf196b5\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"width\\":\\"100%\\",\\"type\\":\\"post-event-description\\",\\"version\\":2},{\\"type\\":\\"horizontalrule\\",\\"version\\":1,\\"width\\":\\"100%\\"},{\\"id\\":\\"ec8ba8ab-f6bd-404e-b938-f85125badf0f\\",\\"lineupItems\\":[{\\"id\\":\\"f06062ef-f975-4e4f-aa07-58022b234af3\\",\\"order\\":0,\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"isHeadliner\\":true}],\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"layout\\":\\"WITH_HEADLINER\\",\\"photoShape\\":\\"RECTANGLE\\",\\"textAlignment\\":\\"CENTER\\",\\"headliner\\":{\\"width\\":\\"100%\\"},\\"headlinerTitle\\":\\"Headliner\\",\\"otherSectionTitle\\":\\"Talent\\",\\"type\\":\\"lineup-info-banner\\",\\"version\\":2},{\\"children\\":[],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"},{\\"children\\":[],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"},{\\"children\\":[],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1},\\"containerClassName\\":\\"\\",\\"editorClassName\\":\\"\\"}",\r\n    "needRefreshHTML": true,\r\n    "additionalContent": "{}",\r\n    "showAdditionalContent": false,\r\n    "media": [\r\n        {\r\n            "id": "2e0713e3-15a0-43a6-b736-7614a99ec4bf",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "selected": true,\r\n            "type": "IMAGE",\r\n            "height": 2700,\r\n            "width": 2100,\r\n            "mediaDuration": 0,\r\n            "mediaSrc": null,\r\n            "mediaType": "IMAGE",\r\n            "inherited": false,\r\n            "position": 1,\r\n            "referenceId": null,\r\n            "source": null,\r\n            "setThumbnail": false\r\n        }\r\n    ],\r\n    "othersCanCopy": false,\r\n    "enableDownlineNote": false,\r\n    "expiredAt": null,\r\n    "urlAlias": "api-test-t2917",\r\n    "headline": "API Test T2917",\r\n    "isPaymentRestrictionEnabled": false\r\n}', token='linda05_token')
    # step 2: guest get token
    _resp2 = ctx.api.auth.guest_login(body='{\n    "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda"\n}', app_headers=False)
    # === 断言/提取（由Apifox customScript翻译）===
    assert _resp2.status_code == 201, f"step2 status != 201, got {_resp2.status_code}"
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    _guestTok = _j2.get('data')
    assert _guestTok, "step2 guest-login 未返回 access_token (data)"
    vars['access_token'] = _guestTok
    # step 3: Guest visit and check the post product recommendation response
    _resp3 = ctx.api.posts.consumer_detail(app_headers=False, token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t2917'})
    # === 断言（由Apifox customScript翻译）===
    _j3 = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
    _d3 = _j3.get('data') or {}
    assert _d3.get('recommendationSectionTitle') == 'You may also like', f"step3 recommendationSectionTitle 不匹配: {_d3.get('recommendationSectionTitle')}"
    _prods3 = _d3.get('relatedProducts') or []
    _expected3 = {
        "e580e57e-7ca4-4f5a-ae3d-fd7f9b932a61": True,
        "64594457-03ca-4049-911f-3862ef9bc156": True,
        "c289fd5c-8a12-4cd0-b175-628af6fe1300": False,
        "65b5c286-7ddf-474f-97cd-f0aff5550b34": False,
    }
    _byId3 = {p.get('promoterProductId'): p.get('isRecommendation') for p in _prods3}
    for _pid, _exp in _expected3.items():
        assert _pid in _byId3, f"step3 缺少产品 {_pid}"
        assert _byId3[_pid] is _exp, f"step3 产品 {_pid} isRecommendation 期望{_exp} 实际{_byId3[_pid]}"
    # step 4: Consumer visit and check the post product recommendation response
    _resp4 = ctx.api.posts.consumer_detail(app_headers=False, token='linda05_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t2917'})
    # === 断言（由Apifox customScript翻译）===
    _j4 = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
    _d4 = _j4.get('data') or {}
    assert _d4.get('recommendationSectionTitle') == 'You may also like', f"step4 recommendationSectionTitle 不匹配: {_d4.get('recommendationSectionTitle')}"
    _prods4 = _d4.get('relatedProducts') or []
    _expected4 = {
        "e580e57e-7ca4-4f5a-ae3d-fd7f9b932a61": True,
        "64594457-03ca-4049-911f-3862ef9bc156": True,
        "c289fd5c-8a12-4cd0-b175-628af6fe1300": False,
        "65b5c286-7ddf-474f-97cd-f0aff5550b34": False,
    }
    _byId4 = {p.get('promoterProductId'): p.get('isRecommendation') for p in _prods4}
    for _pid, _exp in _expected4.items():
        assert _pid in _byId4, f"step4 缺少产品 {_pid}"
        assert _byId4[_pid] is _exp, f"step4 产品 {_pid} isRecommendation 期望{_exp} 实际{_byId4[_pid]}"
