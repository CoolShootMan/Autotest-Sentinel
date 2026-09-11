"""Migrated from Apifox case #8008202. Source folder: Post validation."""
# Apifox Case ID: 8008202  (traceability only — not needed to run)
NAME = "Verify that the Post commission rate can be Batch setting Current +"
TAGS = ["p1", "post_validation", "suite:linda"]
PRIORITY = 1


CASE_ID = 8008202
ENV_NAME = "Release"

# --- step 1: Get Partner linda05 token ---
# post[extractor]: {"variableName": "linda05_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 4ac8cb7c-3f22-43fe-bae2-56f753138fe9 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 72e3ee6a-b5d2-4f9c-88f8-6d39ef1ff13a ---
# post[customScript]: // Parse the response JSON data
# post: const response = pm.response.json();
# post: const items = response.data.items || [];
# post: 
# post: /**
# post:  * Validation: Verify commissionRateForPromotersMax for a specific Item ID
# post:  * Target ID: 1a6bf2bd-f228-40f2-ba24-e0128b88bccd
# post:  * Expected Value: 16
# post:  */
# post: pm.test("Validate commissionRateForPromotersMax is 16 for specific item ID", function () {
# post:     const targetId = "1a6bf2bd-f228-40f2-ba24-e0128b88bccd";
# post:     const expectedRate = 16;
# post: 
# post:     // Locate the specific item in the array
# post:     const targetItem = items.find(item => item.id === targetId);
# post: 
# post:     // Assertion 1: Ensure the item exists
# post:     pm.expect(targetItem, `Item with ID "${targetId}" not found in the response`).to.not.be.undefined;
# post: 
# post:     // Assertion 2: Verify the specific field value
# post:     const actualRate = targetItem.commissionRateForPromotersMax;
# post:     pm.expect(actualRate).to.eql(expectedRate);
# post:     
# post:     // Log details for debugging if needed
# post:     console.log(`Verified ID: ${targetId} | Commission Rate: ${actualRate}`);
# post: });
# --- step 4: 2b075276-5c14-4779-93e0-cc9133de7091 ---
# post[customScript]: // Parse the response body
# post: const response = pm.response.json();
# post: const relatedProducts = response.data.relatedProducts || [];
# post: 
# post: /**
# post:  * Expected Configuration Map for strict validation
# post:  * Mapping IDs to their specific commission rates (13, 14, 15, 16) and financial metrics
# post:  */
# post: const strictExpectations = {
# post:     "5589beae-d2ca-40fc-b361-03122952beb2": {
# post:         commissionRateForMe: 13,
# post:         commissionRateForPromoters: 13,
# post:         price: "56.67",
# post:         costPrice: 49.3,
# post:         priceDisplayCost: 49.3,
# post:         fees: 6.67,
# post:         discountPercent: 0
# post:     },
# post:     "f0a91cf5-c585-45d9-8b08-f59a6941e6d8": {
# post:         commissionRateForMe: 14,
# post:         commissionRateForPromoters: 14,
# post:         price: "167.77",
# post:         costPrice: 144.28,
# post:         priceDisplayCost: 144.28,
# post:         fees: 17.77,
# post:         discountPercent: 0
# post:     },
# post:     "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7": {
# post:         commissionRateForMe: 15,
# post:         commissionRateForPromoters: 15,
# post:         price: "413.99",
# post:         costPrice: 351.89,
# post:         priceDisplayCost: 351.89,
# post:         fees: 42.4,
# post:         discountPercent: 0
# post:     },
# post:     "a963f25a-44a3-439f-ae37-1817621f8c11": {
# post:         commissionRateForMe: 16,
# post:         commissionRateForPromoters: 16,
# post:         price: "1033.49",
# post:         costPrice: 868.13,
# post:         priceDisplayCost: 868.13,
# post:         fees: 104.35,
# post:         discountPercent: 0
# post:     }
# post: };
# post: 
# post: // Execute strict validation for each product found in the mapping
# post: relatedProducts.forEach((product) => {
# post:     const mId = product.merchantProductId;
# post:     const expected = strictExpectations[mId];
# post:     
# post:     // Validate if the product exists in our strict expectation map
# post:     if (expected && product.variants && product.variants.length > 0) {
# post:         const variant = product.variants[0]; // Primary variant validation
# post: 
# post:         // Dynamically loop through all defined expectations for this product
# post:         Object.keys(expected).forEach(key => {
# post:             pm.test(`[Product: ${mId}] Verify field: ${key} (Expected: ${expected[key]})`, () => {
# post:                 const actualValue = variant[key];
# post:                 const expectedValue = expected[key];
# post:                 
# post:                 // Assert strict equality
# post:                 pm.expect(actualValue, `Field [${key}] mismatch for ID ${mId}. Expected ${expectedValue}, but got ${actualValue}`)
# post:                   .to.eql(expectedValue);
# post:             });
# post:         });
# post:     } else if (expected) {
# post:         pm.test(`[Product: ${mId}] Check variants exist`, () => {
# post:             pm.expect(product.variants, `Variants are missing for ID ${mId}`).to.not.be.empty;
# post:         });
# post:     }
# post: });




from core.assertions import expect

def test_linda_t3879_verify_that_the_post_commission_rate_can_be_batch_setting_current(ctx):
    """Apifox case #8008202: Linda_T3879_Verify_that_the_Post_commission_rate_can_be_Batch_setting_Current"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+05@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}', app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: 4ac8cb7c-3f22-43fe-bae2-56f753138fe9
    _resp2 = ctx.api.posts.curator_1a6bf2bd_f228_40f2_ba24_e0128b88bccd(body='{\r\n    "id": "1a6bf2bd-f228-40f2-ba24-e0128b88bccd",\r\n    "announcements": [],\r\n    "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n    "title": "API Test T3879",\r\n    "subTitle": "",\r\n    "links": [],\r\n    "allowPromotersResell": true,\r\n    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",\r\n    "financeMode": "FINANCE_MODE_COMMISSION",\r\n    "status": "ACTIVE",\r\n    "allowPromotersHideProducts": true,\r\n    "allowPromotersCustomizeMedia": true,\r\n    "allowPromotersCreateCoupon": true,\r\n    "promotions": [],\r\n    "isPurchaseQuantityLimited": false,\r\n    "purchaseQuantityLimit": 0,\r\n    "isAccessRestricted": false,\r\n    "allowPromotersAccess": false,\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#FFEEBEFF",\r\n            "#E91E63FF",\r\n            "#757575FF",\r\n            "#0B99FFFF",\r\n            "#F2F2F6FF",\r\n            "#FFFFFF"\r\n        ],\r\n        "fontFamily": "Inter",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "secondaryTextColor": "#E0E0E0FF",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontSize": 24,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "subtitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 400\r\n        },\r\n        "button": {\r\n            "color": "#000000",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "secondaryButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 0\r\n        },\r\n        "textButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "fontWeight": 700\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "color": "#000000 ",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 14,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 400\r\n            },\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "product": {\r\n            "color": "#FFFFFF",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "discount": {\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF",\r\n            "backgroundColor": "#D32A09"\r\n        },\r\n        "freeShipping": {\r\n            "color": "#268E46",\r\n            "backgroundColor": "#EBF5EF"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 16,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 700\r\n            },\r\n            "button": {\r\n                "color": "#000000",\r\n                "backgroundColor": "#F6CA7C"\r\n            },\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF",\r\n            "secondaryText": "#ABABAB"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#E0E0E0FF",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "height": "MEDIUM",\r\n                "displayText": "SHOP_NAME"\r\n            },\r\n            "productBanner": {\r\n                "display": "HIDE",\r\n                "ctaButton": "VIEW_PRODUCT"\r\n            }\r\n        },\r\n        "template": "ClearSky",\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 0\r\n            }\r\n        }\r\n    },\r\n    "hideInStore": false,\r\n    "recommendationSectionTitle": "",\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    ],\r\n    "checkoutInPost": true,\r\n    "allowAffiliateSharingOnly": false,\r\n    "abTestingSettings": [],\r\n    "enableAbTesting": false,\r\n    "isOrderConfirmationNoteEnabled": false,\r\n    "hideCouponBox": false,\r\n    "allowCustomizeDisplayPrices": true,\r\n    "customizeDisplayPrices": {\r\n        "price": "1930 Pacific Ave | Thu, Oct 01 (CDT)",\r\n        "priceColor": "#FFFFFF",\r\n        "titleColor": "#FFFFFF",\r\n        "discountPercent": "Get Tickets",\r\n        "discountPercentColor": "#D32A08"\r\n    },\r\n    "canSetPrice": false,\r\n    "downlineNoteBodyHtml": null,\r\n    "downlineNoteBodyJson": null,\r\n    "featuredSectionTitle": "",\r\n    "enableRedirectUrl": false,\r\n    "redirectUrl": "",\r\n    "redirectDestinationName": "",\r\n    "event": {\r\n        "id": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",\r\n        "status": "UPCOMING",\r\n        "title": "API Test T4259 ",\r\n        "venue": "1930 Pacific Ave",\r\n        "location": "1930 Pacific Ave, Dallas, TX 75201, USA",\r\n        "startDateDisplay": "2026-10-01",\r\n        "endDateDisplay": null,\r\n        "timezone": {\r\n            "dstOffset": 3600,\r\n            "rawOffset": -21600,\r\n            "timeZoneId": "America/Chicago",\r\n            "timeZoneName": "Central Daylight Time"\r\n        },\r\n        "poster": {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "width": 2100,\r\n            "height": 2700,\r\n            "position": 0,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0\r\n        }\r\n    },\r\n    "additionalContentPosition": "aboveTickets",\r\n    "bodyHtml": "<div data-id=\\"7676cdf8-4754-455e-874a-e2fa9711f381\\" data-type=\\"event-info-banner\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-width=\\"100%\\"></div><div data-id=\\"2a01b102-5176-431b-9c75-6b19820510cf\\" data-type=\\"additional-content\\"></div><div data-id=\\"588dd2c2-20db-4441-90a7-02264b5cf566\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"5589beae-d2ca-40fc-b361-03122952beb2\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"43d5a0e7-c782-4d1b-bc59-c886b04e11f5\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"3c94ffbb-f331-4d10-bf28-50a4f156234f\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"9e272d81-ebd7-4053-b0c5-9da34d126177\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-product-id=\\"a963f25a-44a3-439f-ae37-1817621f8c11\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><hr><div data-id=\\"f930dc3e-f9d1-4ca5-bca4-152a4b99c80a\\" data-type=\\"post-event-description\\" data-event-id=\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\" data-width=\\"100%\\"></div>",\r\n    "currentDate": "2026-03-11T08:37:18.589Z",\r\n    "relatedProducts": [\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "5589beae-d2ca-40fc-b361-03122952beb2",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 52.14,\r\n                    "price": 56.67,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",\r\n                    "commissionRateForPromoters": 13\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "f0a91cf5-c585-45d9-8b08-f59a6941e6d8",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 152.68,\r\n                    "price": 167.78,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "935e3c20-64b2-4e1a-95ff-34e68bbf55f4",\r\n                    "commissionRateForPromoters": 14\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 372.59,\r\n                    "price": 413.99,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "fe01f82b-267c-4dfe-bdaa-714633d1e355",\r\n                    "commissionRateForPromoters": 15\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "type": "PRODUCT",\r\n            "merchantProductId": "a963f25a-44a3-439f-ae37-1817621f8c11",\r\n            "isVisible": true,\r\n            "isPurchaseQuantityLimited": false,\r\n            "isRecommendation": false,\r\n            "hasDependentProducts": false,\r\n            "dependentProductIds": [],\r\n            "isFreeShipping": false,\r\n            "isDefaultToSubscription": false,\r\n            "toReplaceMerchantProductIds": null,\r\n            "isCtaCustomized": false,\r\n            "ctaConfig": {\r\n                "type": "BUY_NOW"\r\n            },\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 919.81,\r\n                    "price": 1033.49,\r\n                    "costPrice": 0,\r\n                    "isExcluded": false,\r\n                    "isDefault": false,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "2b8ff662-991e-4909-ae80-c80b1412a6a5",\r\n                    "commissionRateForPromoters": 16\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "accessSpecificUser": [],\r\n    "featuredSectionEnable": false,\r\n    "tab": {\r\n        "value": "Commerce",\r\n        "label": "Commerce",\r\n        "mappingControl": []\r\n    },\r\n    "timeKey": 1773218238589,\r\n    "originEnablePaymentRestriction": false,\r\n    "syncEnabled": false,\r\n    "postType": "EVENT",\r\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"id\\":\\"7676cdf8-4754-455e-874a-e2fa9711f381\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"type\\":\\"event-info-banner\\",\\"version\\":2},{\\"id\\":\\"2a01b102-5176-431b-9c75-6b19820510cf\\",\\"type\\":\\"additional-content\\",\\"version\\":1},{\\"id\\":\\"588dd2c2-20db-4441-90a7-02264b5cf566\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"5589beae-d2ca-40fc-b361-03122952beb2\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"43d5a0e7-c782-4d1b-bc59-c886b04e11f5\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"3c94ffbb-f331-4d10-bf28-50a4f156234f\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"9e272d81-ebd7-4053-b0c5-9da34d126177\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"productId\\":\\"a963f25a-44a3-439f-ae37-1817621f8c11\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"type\\":\\"horizontalrule\\",\\"version\\":1},{\\"id\\":\\"f930dc3e-f9d1-4ca5-bca4-152a4b99c80a\\",\\"eventId\\":\\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\\",\\"type\\":\\"post-event-description\\",\\"version\\":2}],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1},\\"containerClassName\\":\\"\\",\\"editorClassName\\":\\"\\"}",\r\n    "needRefreshHTML": true,\r\n    "additionalContent": "{}",\r\n    "showAdditionalContent": false,\r\n    "media": [\r\n        {\r\n            "id": "9e0ed94d-7828-45f8-b1b1-d927f0eaafaa",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp",\r\n            "selected": true,\r\n            "type": "IMAGE",\r\n            "height": 2700,\r\n            "width": 2100,\r\n            "mediaDuration": 0,\r\n            "mediaSrc": null,\r\n            "mediaType": "IMAGE",\r\n            "inherited": false,\r\n            "position": 1,\r\n            "referenceId": null,\r\n            "source": null,\r\n            "setThumbnail": false\r\n        }\r\n    ],\r\n    "othersCanCopy": false,\r\n    "enableDownlineNote": false,\r\n    "expiredAt": null,\r\n    "urlAlias": "api-test-t3879",\r\n    "headline": "API Test T3879",\r\n    "isPaymentRestrictionEnabled": false\r\n}', token='linda05_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: 72e3ee6a-b5d2-4f9c-88f8-6d39ef1ff13a
    _resp3 = ctx.api.posts.curator_event_0fe6623e_a3ba_40fb_815d_3d6f444775c3_posts(body=None, token='linda05_token')
    # step 4: 2b075276-5c14-4779-93e0-cc9133de7091
    _resp4 = ctx.api.posts.promoter_detail(body=None, params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t3879'}, token='linda06_token')
