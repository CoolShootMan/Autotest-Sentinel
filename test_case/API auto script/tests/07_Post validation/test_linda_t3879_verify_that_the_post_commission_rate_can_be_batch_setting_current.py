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




from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t3879_verify_that_the_post_commission_rate_can_be_batch_setting_current(ctx: "Context"):
    """Apifox case #8008202: Linda_T3879_Verify_that_the_Post_commission_rate_can_be_Batch_setting_Current"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body={
        "email": "linda.zhou.ext+05@1m.app",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: 4ac8cb7c-3f22-43fe-bae2-56f753138fe9
    _resp2 = ctx.api.posts.curator_update(post_id='{{T3879_post_id}}', body={
        "id": "{{T3879_post_id}}",
        "announcements": [],
        "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",
        "title": "API Test T3879",
        "subTitle": "",
        "links": [],
        "allowPromotersResell": True,
        "financeModeForPromoters": "FINANCE_MODE_COMMISSION",
        "financeMode": "FINANCE_MODE_COMMISSION",
        "status": "ACTIVE",
        "allowPromotersHideProducts": True,
        "allowPromotersCustomizeMedia": True,
        "allowPromotersCreateCoupon": True,
        "promotions": [],
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
        "bodyHtml": "<div data-id=\"7676cdf8-4754-455e-874a-e2fa9711f381\" data-type=\"event-info-banner\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-width=\"100%\"></div><div data-id=\"2a01b102-5176-431b-9c75-6b19820510cf\" data-type=\"additional-content\"></div><div data-id=\"588dd2c2-20db-4441-90a7-02264b5cf566\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"5589beae-d2ca-40fc-b361-03122952beb2\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"43d5a0e7-c782-4d1b-bc59-c886b04e11f5\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"3c94ffbb-f331-4d10-bf28-50a4f156234f\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"9e272d81-ebd7-4053-b0c5-9da34d126177\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"a963f25a-44a3-439f-ae37-1817621f8c11\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><hr><div data-id=\"f930dc3e-f9d1-4ca5-bca4-152a4b99c80a\" data-type=\"post-event-description\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-width=\"100%\"></div>",
        "currentDate": "2026-03-11T08:37:18.589Z",
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
                        "wholesalePriceForPromoters": 52.14,
                        "price": 56.67,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "4640fcee-a802-4410-a90d-2fdd4227c777",
                        "commissionRateForPromoters": 13,
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
                        "wholesalePriceForPromoters": 152.68,
                        "price": 167.78,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "935e3c20-64b2-4e1a-95ff-34e68bbf55f4",
                        "commissionRateForPromoters": 14,
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
                        "commissionRateForPromoters": 15,
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
                        "wholesalePriceForPromoters": 919.81,
                        "price": 1033.49,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "2b8ff662-991e-4909-ae80-c80b1412a6a5",
                        "commissionRateForPromoters": 16,
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
        "timeKey": 1773218238589,
        "originEnablePaymentRestriction": False,
        "syncEnabled": False,
        "postType": "EVENT",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"7676cdf8-4754-455e-874a-e2fa9711f381\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"type\":\"event-info-banner\",\"version\":2},{\"id\":\"2a01b102-5176-431b-9c75-6b19820510cf\",\"type\":\"additional-content\",\"version\":1},{\"id\":\"588dd2c2-20db-4441-90a7-02264b5cf566\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"5589beae-d2ca-40fc-b361-03122952beb2\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"43d5a0e7-c782-4d1b-bc59-c886b04e11f5\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"3c94ffbb-f331-4d10-bf28-50a4f156234f\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"9e272d81-ebd7-4053-b0c5-9da34d126177\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"a963f25a-44a3-439f-ae37-1817621f8c11\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"type\":\"horizontalrule\",\"version\":1},{\"id\":\"f930dc3e-f9d1-4ca5-bca4-152a4b99c80a\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"type\":\"post-event-description\",\"version\":2}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
        "needRefreshHTML": True,
        "additionalContent": "{}",
        "showAdditionalContent": False,
        "media": [
            {
                "id": "9e0ed94d-7828-45f8-b1b1-d927f0eaafaa",
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
        "urlAlias": "api-test-t3879",
        "headline": "API Test T3879",
        "isPaymentRestrictionEnabled": False,
    }, token='linda05_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: 72e3ee6a-b5d2-4f9c-88f8-6d39ef1ff13a
    _resp3 = ctx.api.posts.curator_event_posts(event_id='{{T4259_event_id}}', body=None, token='linda05_token')
    # step 4: 2b075276-5c14-4779-93e0-cc9133de7091
    _resp4 = ctx.api.posts.promoter_detail(body=None, params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t3879'}, token='linda06_token')
