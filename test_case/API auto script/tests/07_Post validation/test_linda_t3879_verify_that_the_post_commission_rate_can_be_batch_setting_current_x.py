"""Migrated from Apifox case #8008209. Source folder: Post validation."""
# Apifox Case ID: 8008209  (traceability only — not needed to run)
NAME = "Verify that the Post commission rate can be Batch setting Current X"
TAGS = ["p1", "post_validation", "suite:linda"]
PRIORITY = 1


CASE_ID = 8008209
ENV_NAME = "Release"

# --- step 1: c00988c0-aa6d-43df-a32a-bc4e5f335d77 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 00164776-19b0-4877-a7f0-24a3f8b4cb55 ---
# post[customScript]: // Parse the response JSON data
# post: const response = pm.response.json();
# post: const items = response.data.items || [];
# post: 
# post: /**
# post:  * Validation: Verify commissionRateForPromotersMax for a specific Item ID
# post:  * Target ID: ed73ae71-ad44-4391-8b69-02e5a21982e9
# post:  * Expected Value: 12
# post:  */
# post: pm.test("Validate commissionRateForPromotersMax is 20 for specific item ID", function () {
# post:     const targetId = "ed73ae71-ad44-4391-8b69-02e5a21982e9";
# post:     const expectedRate = 20;
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
# --- step 3: Get Co-seller linda06 token ---
# post[extractor]: {"variableName": "linda06_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 2f36ee54-6f19-4f3b-8039-fad4ca8f808a ---
# post[customScript]: // Parse the response body
# post: const response = pm.response.json();
# post: const relatedProducts = response.data.relatedProducts || [];
# post: 
# post: /**
# post:  * Expected data map for validation
# post:  * Key: merchantProductId
# post:  * Value: Object containing expected financial metrics
# post:  */
# post: const expectedDataMap = {
# post:     "5589beae-d2ca-40fc-b361-03122952beb2": { price: "56.67", costPrice: 45.34, fees: 6.67, priceDisplayCost: 45.34 },
# post:     "f0a91cf5-c585-45d9-8b08-f59a6941e6d8": { price: "167.77", costPrice: 134.22, fees: 17.77, priceDisplayCost: 134.22 },
# post:     "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7": { price: "413.99", costPrice: 331.19, fees: 42.4, priceDisplayCost: 331.19 },
# post:     "a963f25a-44a3-439f-ae37-1817621f8c11": { price: "1033.49", costPrice: 826.79, fees: 104.35, priceDisplayCost: 826.79 }
# post: };
# post: 
# post: /**
# post:  * Iterate through all related products to create individual test assertions.
# post:  * This ensures that if one field fails, others are still checked.
# post:  */
# post: relatedProducts.forEach((product) => {
# post:     const mId = product.merchantProductId;
# post:     const variant = product.variants[0]; // Assuming we validate the first variant
# post:     const expected = expectedDataMap[mId];
# post: 
# post:     // --- Validation: Commission Rates ---
# post:     pm.test(`[${product.title || mId}] CommissionRateForMe should be 20`, () => {
# post:         pm.expect(variant.commissionRateForMe, `Expected 20, but got ${variant.commissionRateForMe}`).to.eql(20);
# post:     });
# post: 
# post:     pm.test(`[${product.title || mId}] CommissionRateForPromoters should be 20`, () => {
# post:         pm.expect(variant.commissionRateForPromoters, `Expected 20, but got ${variant.commissionRateForPromoters}`).to.eql(20);
# post:     });
# post: 
# post:     // --- Validation: Financial Fields (Only if in mapping) ---
# post:     if (expected) {
# post:         Object.keys(expected).forEach(field => {
# post:             pm.test(`[${product.title || mId}] Field [${field}] validation`, () => {
# post:                 const actualValue = String(variant[field]);
# post:                 const expectedValue = String(expected[field]);
# post:                 
# post:                 pm.expect(actualValue, `For ${field}: Expected ${expectedValue}, but got ${actualValue}`)
# post:                   .to.eql(expectedValue);
# post:             });
# post:         });
# post:     }
# post: });




from core.assertions import expect

def test_linda_t3879_verify_that_the_post_commission_rate_can_be_batch_setting_current_x(ctx):
    """Apifox case #8008209: Linda_T3879_Verify_that_the_Post_commission_rate_can_be_Batch_setting_Current_X"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: c00988c0-aa6d-43df-a32a-bc4e5f335d77
    _resp1 = ctx.api.posts.curator_ed73ae71_ad44_4391_8b69_02e5a21982e9(body={
        "id": "ed73ae71-ad44-4391-8b69-02e5a21982e9",
        "announcements": [],
        "createFromEventId": "0fe6623e-a3ba-40fb-815d-3d6f444775c3",
        "title": "API Test T3879 commission multiply ",
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
        "bodyHtml": "<div data-id=\"987e974d-10b5-4ab2-b674-11b680b3d26b\" data-type=\"event-info-banner\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-width=\"100%\"></div><div data-id=\"d8b5d008-f1c9-4b86-9696-6d418828cc5a\" data-type=\"additional-content\"></div><div data-id=\"3a4cbd8b-8102-4761-a15a-b39fe486e2e0\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"5589beae-d2ca-40fc-b361-03122952beb2\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"4ca2deed-59f2-491c-a26d-65423edfe37d\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"5d5587cf-4282-4b1d-91fd-06bca59d54b2\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"26ec6f01-279b-4a15-97f9-adde280390ab\" data-width=\"100%\" data-height=\"\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-product-id=\"a963f25a-44a3-439f-ae37-1817621f8c11\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><hr><div data-id=\"814ccec3-676d-4622-a428-54e3abe877f3\" data-type=\"post-event-description\" data-event-id=\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\" data-width=\"100%\"></div>",
        "currentDate": "2026-03-12T02:59:05.069Z",
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
                        "commissionRateForPromoters": 20,
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
                        "commissionRateForPromoters": 20,
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
                        "commissionRateForPromoters": 20,
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
                        "commissionRateForPromoters": 20,
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
        "timeKey": 1773284345069,
        "originEnablePaymentRestriction": False,
        "syncEnabled": False,
        "postType": "EVENT",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"987e974d-10b5-4ab2-b674-11b680b3d26b\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"type\":\"event-info-banner\",\"version\":2},{\"id\":\"d8b5d008-f1c9-4b86-9696-6d418828cc5a\",\"type\":\"additional-content\",\"version\":1},{\"id\":\"3a4cbd8b-8102-4761-a15a-b39fe486e2e0\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"5589beae-d2ca-40fc-b361-03122952beb2\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"4ca2deed-59f2-491c-a26d-65423edfe37d\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"f0a91cf5-c585-45d9-8b08-f59a6941e6d8\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"5d5587cf-4282-4b1d-91fd-06bca59d54b2\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"26ec6f01-279b-4a15-97f9-adde280390ab\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"productId\":\"a963f25a-44a3-439f-ae37-1817621f8c11\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"type\":\"horizontalrule\",\"version\":1},{\"id\":\"814ccec3-676d-4622-a428-54e3abe877f3\",\"eventId\":\"0fe6623e-a3ba-40fb-815d-3d6f444775c3\",\"type\":\"post-event-description\",\"version\":2}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
        "needRefreshHTML": True,
        "additionalContent": "{}",
        "showAdditionalContent": False,
        "media": [
            {
                "id": "c4146c4d-0c0e-404b-868f-e362b217d7db",
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
        "urlAlias": "api-test-t3879-commission-multiply",
        "headline": "API Test T3879 commission multiply ",
        "isPaymentRestrictionEnabled": False,
    }, token='linda05_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # assertion 1.assertion: responseJson equal ACTIVE
    expect(_resp1).json('$.data.status').equals('ACTIVE')
    # step 2: 00164776-19b0-4877-a7f0-24a3f8b4cb55
    _resp2 = ctx.api.posts.curator_event_0fe6623e_a3ba_40fb_815d_3d6f444775c3_posts(body=None, token='linda05_token')
    # step 3: Get Co-seller linda06 token
    _resp3 = ctx.api.auth.sign_in(body={
        "email": "linda.zhou.ext+06@1m.app",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: linda06_token = $.data.token
    ctx.extract('linda06_token', _resp3, '$.data.token')
    # step 4: 2f36ee54-6f19-4f3b-8039-fad4ca8f808a
    _resp4 = ctx.api.posts.promoter_detail(body=None, params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t3879-commission-multiply'}, token='linda06_token')
