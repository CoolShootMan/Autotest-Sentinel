"""Migrated from Apifox case #7898399. Source folder: Post validation."""
# Apifox Case ID: 7898399  (traceability only — not needed to run)
NAME = "Verify the resale posts need to inherit the parent post quantity limit"
TAGS = ["p1", "post_validation", "suite:linda"]
PRIORITY = 1


CASE_ID = 7898399
ENV_NAME = "Release"

# --- step 1: c60da6cd-574c-4d28-a8f7-09ece9ae6907 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: guest get token ---
# pre: 
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 3: Guest visit and check the product purchase exist limit ---
# post[customScript]: // 1. Parse the response body
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: const relatedProducts = data.relatedProducts || [];
# post: 
# post: /**
# post:  * 2. Global Level Validation (Root Data)
# post:  * Verify the overall purchase limit for the main product
# post:  */
# post: pm.test("Verify Global Purchase Quantity Limits", () => {
# post:     pm.expect(data.isPurchaseQuantityLimited, "Global isPurchaseQuantityLimited mismatch").to.eql(true);
# post:     pm.expect(data.purchaseQuantityLimit, "Global purchaseQuantityLimit mismatch").to.eql(5);
# post: });
# post: 
# post: /**
# post:  * 3. Specific Product Mapping (PromoterProductId)
# post:  * Defines the strict expectations for each related product
# post:  */
# post: const purchaseExpectations = {
# post:     "e580e57e-7ca4-4f5a-ae3d-fd7f9b932a61": {
# post:         isPurchaseQuantityLimited: true,
# post:         purchaseQuantityLimit: 1
# post:     },
# post:     "64594457-03ca-4049-911f-3862ef9bc156": {
# post:         isPurchaseQuantityLimited: true,
# post:         purchaseQuantityLimit: 2
# post:     },
# post:     "c289fd5c-8a12-4cd0-b175-628af6fe1300": {
# post:         isPurchaseQuantityLimited: false,
# post:         purchaseQuantityLimit: 0
# post:     },
# post:     "65b5c286-7ddf-474f-97cd-f0aff5550b34": {
# post:         isPurchaseQuantityLimited: false,
# post:         purchaseQuantityLimit: 0
# post:     }
# post: };
# post: 
# post: // 4. Iterate and validate each product based on promoterProductId
# post: relatedProducts.forEach((product) => {
# post:     const pId = product.promoterProductId;
# post:     const expected = purchaseExpectations[pId];
# post: 
# post:     if (expected) {
# post:         // Test: isPurchaseQuantityLimited
# post:         pm.test(`[ID: ${pId}] Verify isPurchaseQuantityLimited (Exp: ${expected.isPurchaseQuantityLimited})`, () => {
# post:             pm.expect(product.isPurchaseQuantityLimited, `Mismatch for isPurchaseQuantityLimited at ${pId}`)
# post:               .to.eql(expected.isPurchaseQuantityLimited);
# post:         });
# post: 
# post:         // Test: purchaseQuantityLimit
# post:         pm.test(`[ID: ${pId}] Verify purchaseQuantityLimit (Exp: ${expected.purchaseQuantityLimit})`, () => {
# post:             pm.expect(product.purchaseQuantityLimit, `Mismatch for purchaseQuantityLimit at ${pId}`)
# post:               .to.eql(expected.purchaseQuantityLimit);
# post:         });
# post:     }
# post: });
# --- step 4: 5bd8287b-5f33-4544-8b58-f350221a0d55 ---
# post[customScript]: // 1. Parse the response body
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: const relatedProducts = data.relatedProducts || [];
# post: 
# post: /**
# post:  * 2. Global Level Validation (Root Data)
# post:  * Verify the overall purchase limit for the main product
# post:  */
# post: pm.test("Verify Global Purchase Quantity Limits", () => {
# post:     pm.expect(data.isPurchaseQuantityLimited, "Global isPurchaseQuantityLimited mismatch").to.eql(true);
# post:     pm.expect(data.purchaseQuantityLimit, "Global purchaseQuantityLimit mismatch").to.eql(5);
# post: });
# post: 
# post: /**
# post:  * 3. Specific Product Mapping (PromoterProductId)
# post:  * Defines the strict expectations for each related product
# post:  */
# post: const purchaseExpectations = {
# post:     "6073386a-ec24-4066-b04d-f51f0976d5be": {
# post:         isPurchaseQuantityLimited: true,
# post:         purchaseQuantityLimit: 1
# post:     },
# post:     "af6c5ba1-f0cc-4a4e-b3d6-52d528b21e17": {
# post:         isPurchaseQuantityLimited: true,
# post:         purchaseQuantityLimit: 2
# post:     },
# post:     "2946a170-f0f7-41c2-9b14-f0929cc18165": {
# post:         isPurchaseQuantityLimited: false,
# post:         // purchaseQuantityLimit: 0
# post:     },
# post:     "57124ed2-16b7-41b1-a964-b9071109f9e2": {
# post:         isPurchaseQuantityLimited: false,
# post:         // purchaseQuantityLimit: 0
# post:     }
# post: };
# post: 
# post: ;
# --- step 5: Guest visit and check the product purchase exist limit ---
# post[customScript]: // 1. Parse the response body
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: const relatedProducts = data.relatedProducts || [];
# post: 
# post: /**
# post:  * 2. Global Level Validation (Root Data)
# post:  * Verify the overall purchase limit for the main product
# post:  */
# post: pm.test("Verify Global Purchase Quantity Limits", () => {
# post:     pm.expect(data.isPurchaseQuantityLimited, "Global isPurchaseQuantityLimited mismatch").to.eql(true);
# post:     pm.expect(data.purchaseQuantityLimit, "Global purchaseQuantityLimit mismatch").to.eql(5);
# post: });
# post: 
# post: /**
# post:  * 3. Specific Product Mapping (PromoterProductId)
# post:  * Defines the strict expectations for each related product
# post:  */
# post: const purchaseExpectations = {
# post:     "e580e57e-7ca4-4f5a-ae3d-fd7f9b932a61": {
# post:         isPurchaseQuantityLimited: true,
# post:         purchaseQuantityLimit: 1
# post:     },
# post:     "64594457-03ca-4049-911f-3862ef9bc156": {
# post:         isPurchaseQuantityLimited: true,
# post:         purchaseQuantityLimit: 2
# post:     },
# post:     "c289fd5c-8a12-4cd0-b175-628af6fe1300": {
# post:         isPurchaseQuantityLimited: false,
# post:         purchaseQuantityLimit: 0
# post:     },
# post:     "65b5c286-7ddf-474f-97cd-f0aff5550b34": {
# post:         isPurchaseQuantityLimited: false,
# post:         purchaseQuantityLimit: 0
# post:     }
# post: };
# post: 
# post: // 4. Iterate and validate each product based on promoterProductId
# post: relatedProducts.forEach((product) => {
# post:     const pId = product.promoterProductId;
# post:     const expected = purchaseExpectations[pId];
# post: 
# post:     if (expected) {
# post:         // Test: isPurchaseQuantityLimited
# post:         pm.test(`[ID: ${pId}] Verify isPurchaseQuantityLimited (Exp: ${expected.isPurchaseQuantityLimited})`, () => {
# post:             pm.expect(product.isPurchaseQuantityLimited, `Mismatch for isPurchaseQuantityLimited at ${pId}`)
# post:               .to.eql(expected.isPurchaseQuantityLimited);
# post:         });
# post: 
# post:         // Test: purchaseQuantityLimit
# post:         pm.test(`[ID: ${pId}] Verify purchaseQuantityLimit (Exp: ${expected.purchaseQuantityLimit})`, () => {
# post:             pm.expect(product.purchaseQuantityLimit, `Mismatch for purchaseQuantityLimit at ${pId}`)
# post:               .to.eql(expected.purchaseQuantityLimit);
# post:         });
# post:     }
# post: });




import json

from core.assertions import expect

def test_linda_t2601_verify_the_resale_posts_need_to_inherit_the_parent_post_quantity_limit(ctx):
    """Apifox case #7898399: Linda_T2601_Verify_the_resale_posts_need_to_inherit_the_parent_post_quantity_lim"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: c60da6cd-574c-4d28-a8f7-09ece9ae6907
    _resp1 = ctx.api.posts.curator_504d5e2a_d2e9_4782_9333_536a696b9669(body='{\r\n    "id": "504d5e2a-d2e9-4782-9333-536a696b9669",\r\n    "announcements": [],\r\n    "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n    "title": "API Test T2601",\r\n    "subTitle": "",\r\n    "links": [],\r\n    "allowPromotersResell": true,\r\n    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",\r\n    "financeMode": "FINANCE_MODE_COMMISSION",\r\n    "status": "ACTIVE",\r\n    "allowPromotersHideProducts": true,\r\n    "allowPromotersCustomizeMedia": true,\r\n    "allowPromotersCreateCoupon": true,\r\n    "promotions": [],\r\n    "isPurchaseQuantityLimited": true,\r\n    "purchaseQuantityLimit": 5,\r\n    "isAccessRestricted": false,\r\n    "allowPromotersAccess": false,\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#FFEEBEFF",\r\n            "#E91E63FF",\r\n            "#757575FF",\r\n            "#0B99FFFF",\r\n            "#F2F2F6FF",\r\n            "#FFFFFF"\r\n        ],\r\n        "fontFamily": "Inter",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "dividerColor": "#CFCFCF",\r\n        "secondaryTextColor": "#E0E0E0FF",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontSize": 24,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "subtitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 400\r\n        },\r\n        "button": {\r\n            "color": "#000000",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "secondaryButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 0\r\n        },\r\n        "textButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "fontWeight": 700\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "color": "#000000 ",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 14,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 400\r\n            },\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "product": {\r\n            "color": "#FFFFFF",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "discount": {\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF",\r\n            "backgroundColor": "#D32A09"\r\n        },\r\n        "freeShipping": {\r\n            "color": "#268E46",\r\n            "backgroundColor": "#EBF5EF"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 16,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 700\r\n            },\r\n            "button": {\r\n                "color": "#000000",\r\n                "backgroundColor": "#F6CA7C"\r\n            },\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF",\r\n            "secondaryText": "#ABABAB"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#E0E0E0FF",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "height": "MEDIUM",\r\n                "displayText": "SHOP_NAME"\r\n            },\r\n            "productBanner": {\r\n                "display": "HIDE",\r\n                "ctaButton": "VIEW_PRODUCT"\r\n            }\r\n        },\r\n        "template": "ClearSky",\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 0\r\n            }\r\n        }\r\n    },\r\n    "hideInStore": false,\r\n    "recommendationSectionTitle": "",\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    ],\r\n    "checkoutInPost": true,\r\n    "allowAffiliateSharingOnly": false,\r\n    "abTestingSettings": [],\r\n    "enableAbTesting": false,\r\n    "isOrderConfirmationNoteEnabled": false,\r\n    "hideCouponBox": false,\r\n    "allowCustomizeDisplayPrices": true,\r\n    "customizeDisplayPrices": {\r\n        "price": "1930 Pacific Ave | Thu, Oct 01 (CDT)",\r\n        "priceColor": "#FFFFFF",\r\n        "titleColor": "#FFFFFF",\r\n        "discountPercent": "Get Tickets",\r\n        "discountPercentColor": "#D32A08"\r\n    },\r\n    "canSetPrice": false,\r\n    "downlineNoteBodyHtml": null,\r\n    "downlineNoteBodyJson": null,\r\n    "featuredSectionTitle": "",\r\n    "enableRedirectUrl": false,\r\n    "redirectUrl": "",\r\n    "redirectDestinationName": "",\r\n    "event": {\r\n        "id": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n        "status": "UPCOMING",\r\n        "title": "API Test T4259 ",\r\n        "venue": "1930 Pacific Ave",\r\n        "location": "1930 Pacific Ave, Dallas, TX 75201, USA",\r\n        "startDateDisplay": "2026-10-01",\r\n        "endDateDisplay": null,\r\n        "timezone": {\r\n            "dstOffset": 3600,\r\n            "rawOffset": -21600,\r\n            "timeZoneId": "America/Chicago",\r\n            "timeZoneName": "Central Daylight Time"\r\n        },\r\n        "poster": {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "position": 0,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    },\r\n    "additionalContentPosition": "aboveTickets",\r\n    "bodyHtml": "<div class=\\"lexical-root\\"><div class=\\"katana-paragraph\\"><div class=\\"event-info-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-node-id=\\"f49b1646-20c6-4335-8297-6a68ba7c732b\\">Event Info</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"c8fcc487-9b3a-46cd-b4e6-c73e477c349f\\" data-node-id=\\"4921e2ce-636b-4d28-9ba3-0e5ea8a1a619\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"c49e0e20-543b-4e1e-9197-4c7bb8f02b34\\" data-node-id=\\"14e45003-0185-4da0-ae1e-2951581906d2\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"2a6aed2e-bc40-4384-b193-4583fdb75bad\\" data-node-id=\\"91c66f83-f112-467f-9430-4ac4d1aea29c\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"2888dfc8-66e9-445e-aad3-28df194ce424\\" data-node-id=\\"283cb42e-21d4-40fd-87ca-c621e7632f3e\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"5589beae-d2ca-40fc-b361-03122952beb2\\" data-node-id=\\"b604d5e7-bfe2-4680-8e14-60452e10f090\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\" data-node-id=\\"64d10706-7dd7-490b-98dc-23b89082626a\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\" data-node-id=\\"3fa37e58-8229-4171-91b9-b5d3a343b3ae\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><div class=\\"ticket-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a963f25a-44a3-439f-ae37-1817621f8c11\\" data-node-id=\\"0de00a38-0efe-4f85-81a6-fa1e95b9c02b\\">Buy Ticket</div></div><div class=\\"katana-paragraph\\"><hr /></div><div class=\\"katana-paragraph\\"><br></div><div class=\\"katana-paragraph\\"><hr /></div><div class=\\"katana-paragraph\\"><div class=\\"lineup-info-banner\\" data-node-id=\\"6f5829a7-340c-4b6c-a190-0f2fb1eccaa2\\">Lineup</div></div></div>",\r\n    "currentDate": "2026-03-26T08:03:29.102Z",\r\n    "relatedProducts": [\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "5589beae-d2ca-40fc-b361-03122952beb2",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": true,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 51,\r\n                    "price": 56.67,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "f0a91cf5-c585-45d9-8b08-f59a6941e6d8",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": true,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 2,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 151,\r\n                    "price": 167.78,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "935e3c20-64b2-4e1a-95ff-34e68bbf55f4",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 372.59,\r\n                    "price": 413.99,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "fe01f82b-267c-4dfe-bdaa-714633d1e355",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a963f25a-44a3-439f-ae37-1817621f8c11",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 930.14,\r\n                    "price": 1033.49,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "2b8ff662-991e-4909-ae80-c80b1412a6a5",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "c8fcc487-9b3a-46cd-b4e6-c73e477c349f",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 11,\r\n                    "price": 12.22,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "23d86ea9-6706-4ce9-a881-91917ec3584f",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "c49e0e20-543b-4e1e-9197-4c7bb8f02b34",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 11,\r\n                    "price": 12.22,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "353117e2-0677-431d-a7a8-7fcde0032b82",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "2a6aed2e-bc40-4384-b193-4583fdb75bad",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 11,\r\n                    "price": 12.22,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "2c194312-39cd-4a64-98b1-14b1cb504174",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "2888dfc8-66e9-445e-aad3-28df194ce424",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 11,\r\n                    "price": 12.22,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "f5065f6b-819b-40a8-8386-33b0bcf5d7cc",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "accessSpecificUser": [],\r\n    "featuredSectionEnable": false,\r\n    "tab": {\r\n        "value": "Commerce",\r\n        "label": "Commerce",\r\n        "mappingControl": []\r\n    },\r\n    "timeKey": 1774512209102,\r\n    "originEnablePaymentRestriction": false,\r\n    "syncEnabled": false,\r\n    "postType": "EVENT",\r\n    "bodyJson": "{\\"root\\":{\\"type\\":\\"root\\",\\"children\\":[{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"event-info-banner\\",\\"id\\":\\"f49b1646-20c6-4335-8297-6a68ba7c732b\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"id\\":\\"d74eebea-b473-4308-b3ea-34f0c65ac7a1\\",\\"type\\":\\"additional-content\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"4921e2ce-636b-4d28-9ba3-0e5ea8a1a619\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"c8fcc487-9b3a-46cd-b4e6-c73e477c349f\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"14e45003-0185-4da0-ae1e-2951581906d2\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"c49e0e20-543b-4e1e-9197-4c7bb8f02b34\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"91c66f83-f112-467f-9430-4ac4d1aea29c\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"2a6aed2e-bc40-4384-b193-4583fdb75bad\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"283cb42e-21d4-40fd-87ca-c621e7632f3e\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"2888dfc8-66e9-445e-aad3-28df194ce424\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"b604d5e7-bfe2-4680-8e14-60452e10f090\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"5589beae-d2ca-40fc-b361-03122952beb2\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"64d10706-7dd7-490b-98dc-23b89082626a\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"3fa37e58-8229-4171-91b9-b5d3a343b3ae\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"ticket-banner\\",\\"id\\":\\"0de00a38-0efe-4f85-81a6-fa1e95b9c02b\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a963f25a-44a3-439f-ae37-1817621f8c11\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"horizontalrule\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"post-event-description\\",\\"id\\":\\"2c94284d-2104-4c47-9853-36e91971a941\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"width\\":\\"100%\\",\\"version\\":2}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"horizontalrule\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1},{\\"type\\":\\"katana-paragraph\\",\\"children\\":[{\\"type\\":\\"lineup-info-banner\\",\\"id\\":\\"6f5829a7-340c-4b6c-a190-0f2fb1eccaa2\\",\\"lineupItems\\":[{\\"id\\":\\"f06062ef-f975-4e4f-aa07-58022b234af3\\",\\"order\\":0,\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"isHeadliner\\":true}],\\"width\\":\\"100%\\",\\"layout\\":\\"WITH_HEADLINER\\",\\"photoShape\\":\\"RECTANGLE\\",\\"textAlignment\\":\\"CENTER\\",\\"headliner\\":{\\"width\\":\\"100%\\"},\\"headlinerTitle\\":\\"Headliner\\",\\"otherSectionTitle\\":\\"Talent\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"version\\":1}],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"version\\":1},\\"containerClassName\\":\\"\\",\\"editorClassName\\":\\"\\"}",\r\n    "needRefreshHTML": true,\r\n    "additionalContent": "{}",\r\n    "showAdditionalContent": false,\r\n    "media": [\r\n        {\r\n            "id": "5cef587a-3e0b-4dab-bd74-2ce5929fe9e4",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "selected": true,\r\n            "type": "IMAGE",\r\n            "height": 2700,\r\n            "width": 2100,\r\n            "mediaDuration": 0,\r\n            "mediaSrc": null,\r\n            "mediaType": "IMAGE",\r\n            "inherited": true,\r\n            "position": 1,\r\n            "referenceId": null,\r\n            "source": null,\r\n            "setThumbnail": false\r\n        }\r\n    ],\r\n    "othersCanCopy": false,\r\n    "enableDownlineNote": false,\r\n    "expiredAt": null,\r\n    "urlAlias": "api-test-t2601",\r\n    "headline": "API Test T2601",\r\n    "isPaymentRestrictionEnabled": false\r\n}', token='linda05_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # step 2: guest get token
    _resp2 = ctx.api.auth.guest_login(body='{\n    "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda"\n}')
    vars['access_token'] = (_resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 3: Guest visit and check the product purchase exist limit
    _resp3 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t2601'})
    # step 4: 5bd8287b-5f33-4544-8b58-f350221a0d55
    _resp4 = ctx.api.posts.curator_edit_ac273ab5_3f9a_4f89_8e07_72d19c463b18(body=None, token='linda06_token')
    # step 5: Guest visit and check the product purchase exist limit
    _resp5 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'qvur6nnf7n', 'urlAlias': 'api-test-t2601'})
