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

from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t2601_verify_the_resale_posts_need_to_inherit_the_parent_post_quantity_limit(ctx: "Context"):
    """Apifox case #7898399: Linda_T2601_Verify_the_resale_posts_need_to_inherit_the_parent_post_quantity_lim"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: c60da6cd-574c-4d28-a8f7-09ece9ae6907
    _resp1 = ctx.api.posts.curator_504d5e2a_d2e9_4782_9333_536a696b9669(body={
    'id': '504d5e2a-d2e9-4782-9333-536a696b9669',
    'announcements': [],
    'createFromEventId': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
    'title': 'API Test T2601',
    'subTitle': '',
    'links': [],
    'allowPromotersResell': True,
    'financeModeForPromoters': 'FINANCE_MODE_COMMISSION',
    'financeMode': 'FINANCE_MODE_COMMISSION',
    'status': 'ACTIVE',
    'allowPromotersHideProducts': True,
    'allowPromotersCustomizeMedia': True,
    'allowPromotersCreateCoupon': True,
    'promotions': [],
    'isPurchaseQuantityLimited': True,
    'purchaseQuantityLimit': 5,
    'isAccessRestricted': False,
    'allowPromotersAccess': False,
    'styleSettings': {
        'recentUsedColors': [
            '#B7E2E0FF',
            '#FFEEBEFF',
            '#E91E63FF',
            '#757575FF',
            '#0B99FFFF',
            '#F2F2F6FF',
            '#FFFFFF',
        ],
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'dividerColor': '#CFCFCF',
        'secondaryTextColor': '#E0E0E0FF',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontSize': 24,
            'fontFamily': 'Inter',
            'fontWeight': 700,
        },
        'columnTitle': {
            'color': '#FFFFFF',
            'fontSize': 20,
            'fontFamily': 'Inter',
            'fontWeight': 700,
        },
        'subtitle': {
            'color': '#FFFFFF',
            'fontSize': 20,
            'fontFamily': 'Inter',
            'fontWeight': 400,
        },
        'button': {
            'color': '#000000',
            'fontSize': 16,
            'boxShadow': 'none',
            'fontWeight': 400,
            'borderColor': '#0000',
            'borderRadius': 0,
            'backgroundColor': '#F6CA7C',
        },
        'secondaryButton': {
            'color': '#FFFFFF',
            'fontSize': 16,
            'boxShadow': 'none',
            'fontWeight': 400,
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
        },
        'textButton': {
            'color': '#FFFFFF',
            'fontSize': 16,
            'fontWeight': 700,
        },
        'selectButton': {
            'borderColor': '#000000',
        },
        'relatedLink': {
            'color': '#000000 ',
            'borderColor': '#0000',
            'borderRadius': 0,
            'backgroundColor': '#FFFFFF80',
        },
        'featuredProducts': {
            'color': '#FFFFFF',
            'title': {
                'color': '#FFFFFF',
                'fontSize': 14,
                'fontFamily': 'Inter',
                'fontWeight': 400,
            },
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'secondaryTextColor': '#E0E0E0FF',
        },
        'product': {
            'color': '#FFFFFF',
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'secondaryTextColor': '#E0E0E0FF',
        },
        'discount': {
            'color': '#FFFFFF',
            'priceColor': '#FFFFFF',
            'backgroundColor': '#D32A09',
        },
        'freeShipping': {
            'color': '#268E46',
            'backgroundColor': '#EBF5EF',
        },
        'starRatingColor': '#FAAF03',
        'layoutFeatureCard': {
            'color': '#FFFFFF',
            'title': {
                'color': '#FFFFFF',
                'fontSize': 16,
                'fontFamily': 'Inter',
                'fontWeight': 700,
            },
            'button': {
                'color': '#000000',
                'backgroundColor': '#F6CA7C',
            },
            'secondaryTextColor': '#E0E0E0FF',
        },
        'lineupBanner': {
            'titleText': '#FFFFFF',
            'descriptionText': '#F6CA7C',
        },
        'eventInfoBanner': {
            'text': '#FFFFFF',
            'secondaryText': '#ABABAB',
        },
        'eventDescription': {
            'text': '#E0E0E0FF',
            'title': '#FFFFFF',
        },
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'height': 'MEDIUM',
                'displayText': 'SHOP_NAME',
            },
            'productBanner': {
                'display': 'HIDE',
                'ctaButton': 'VIEW_PRODUCT',
            },
        },
        'template': 'ClearSky',
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
    },
    'hideInStore': False,
    'recommendationSectionTitle': '',
    'coverImages': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp',
            'width': 2100,
            'height': 2700,
            'mediaSrc': None,
            'position': 1,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'checkoutInPost': True,
    'allowAffiliateSharingOnly': False,
    'abTestingSettings': [],
    'enableAbTesting': False,
    'isOrderConfirmationNoteEnabled': False,
    'hideCouponBox': False,
    'allowCustomizeDisplayPrices': True,
    'customizeDisplayPrices': {
        'price': '1930 Pacific Ave | Thu, Oct 01 (CDT)',
        'priceColor': '#FFFFFF',
        'titleColor': '#FFFFFF',
        'discountPercent': 'Get Tickets',
        'discountPercentColor': '#D32A08',
    },
    'canSetPrice': False,
    'downlineNoteBodyHtml': None,
    'downlineNoteBodyJson': None,
    'featuredSectionTitle': '',
    'enableRedirectUrl': False,
    'redirectUrl': '',
    'redirectDestinationName': '',
    'event': {
        'id': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
        'status': 'UPCOMING',
        'title': 'API Test T4259 ',
        'venue': '1930 Pacific Ave',
        'location': '1930 Pacific Ave, Dallas, TX 75201, USA',
        'startDateDisplay': '2026-10-01',
        'endDateDisplay': None,
        'timezone': {
            'dstOffset': 3600,
            'rawOffset': -21600,
            'timeZoneId': 'America/Chicago',
            'timeZoneName': 'Central Daylight Time',
        },
        'poster': {
            'src': 'https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp',
            'width': 2100,
            'height': 2700,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    },
    'additionalContentPosition': 'aboveTickets',
    'bodyHtml': '<div class="lexical-root"><div class="katana-paragraph"><div class="event-info-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-node-id="f49b1646-20c6-4335-8297-6a68ba7c732b">Event Info</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="c8fcc487-9b3a-46cd-b4e6-c73e477c349f" data-node-id="4921e2ce-636b-4d28-9ba3-0e5ea8a1a619">Buy Ticket</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="c49e0e20-543b-4e1e-9197-4c7bb8f02b34" data-node-id="14e45003-0185-4da0-ae1e-2951581906d2">Buy Ticket</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="2a6aed2e-bc40-4384-b193-4583fdb75bad" data-node-id="91c66f83-f112-467f-9430-4ac4d1aea29c">Buy Ticket</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="2888dfc8-66e9-445e-aad3-28df194ce424" data-node-id="283cb42e-21d4-40fd-87ca-c621e7632f3e">Buy Ticket</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="5589beae-d2ca-40fc-b361-03122952beb2" data-node-id="b604d5e7-bfe2-4680-8e14-60452e10f090">Buy Ticket</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="f0a91cf5-c585-45d9-8b08-f59a6941e6d8" data-node-id="64d10706-7dd7-490b-98dc-23b89082626a">Buy Ticket</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7" data-node-id="3fa37e58-8229-4171-91b9-b5d3a343b3ae">Buy Ticket</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="a963f25a-44a3-439f-ae37-1817621f8c11" data-node-id="0de00a38-0efe-4f85-81a6-fa1e95b9c02b">Buy Ticket</div></div><div class="katana-paragraph"><hr /></div><div class="katana-paragraph"><br></div><div class="katana-paragraph"><hr /></div><div class="katana-paragraph"><div class="lineup-info-banner" data-node-id="6f5829a7-340c-4b6c-a190-0f2fb1eccaa2">Lineup</div></div></div>',
    'currentDate': '2026-03-26T08:03:29.102Z',
    'relatedProducts': [
        {
            'type': 'PRODUCT',
            'merchantProductId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'isVisible': True,
            'isPurchaseQuantityLimited': True,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 51,
                    'price': 56.67,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '4640fcee-a802-4410-a90d-2fdd4227c777',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            'isVisible': True,
            'isPurchaseQuantityLimited': True,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 2,
            'variants': [
                {
                    'wholesalePriceForPromoters': 151,
                    'price': 167.78,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '935e3c20-64b2-4e1a-95ff-34e68bbf55f4',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': 'a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 372.59,
                    'price': 413.99,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': 'fe01f82b-267c-4dfe-bdaa-714633d1e355',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': 'a963f25a-44a3-439f-ae37-1817621f8c11',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 930.14,
                    'price': 1033.49,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '2b8ff662-991e-4909-ae80-c80b1412a6a5',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': 'c8fcc487-9b3a-46cd-b4e6-c73e477c349f',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 11,
                    'price': 12.22,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '23d86ea9-6706-4ce9-a881-91917ec3584f',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': 'c49e0e20-543b-4e1e-9197-4c7bb8f02b34',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 11,
                    'price': 12.22,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '353117e2-0677-431d-a7a8-7fcde0032b82',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': '2a6aed2e-bc40-4384-b193-4583fdb75bad',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 11,
                    'price': 12.22,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '2c194312-39cd-4a64-98b1-14b1cb504174',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': '2888dfc8-66e9-445e-aad3-28df194ce424',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 11,
                    'price': 12.22,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': 'f5065f6b-819b-40a8-8386-33b0bcf5d7cc',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
    ],
    'accessSpecificUser': [],
    'featuredSectionEnable': False,
    'tab': {
        'value': 'Commerce',
        'label': 'Commerce',
        'mappingControl': [],
    },
    'timeKey': 1774512209102,
    'originEnablePaymentRestriction': False,
    'syncEnabled': False,
    'postType': 'EVENT',
    'bodyJson': '{"root":{"type":"root","children":[{"type":"katana-paragraph","children":[{"type":"event-info-banner","id":"f49b1646-20c6-4335-8297-6a68ba7c732b","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"id":"d74eebea-b473-4308-b3ea-34f0c65ac7a1","type":"additional-content","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"4921e2ce-636b-4d28-9ba3-0e5ea8a1a619","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"c8fcc487-9b3a-46cd-b4e6-c73e477c349f","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"14e45003-0185-4da0-ae1e-2951581906d2","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"c49e0e20-543b-4e1e-9197-4c7bb8f02b34","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"91c66f83-f112-467f-9430-4ac4d1aea29c","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"2a6aed2e-bc40-4384-b193-4583fdb75bad","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"283cb42e-21d4-40fd-87ca-c621e7632f3e","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"2888dfc8-66e9-445e-aad3-28df194ce424","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"b604d5e7-bfe2-4680-8e14-60452e10f090","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"5589beae-d2ca-40fc-b361-03122952beb2","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"64d10706-7dd7-490b-98dc-23b89082626a","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"f0a91cf5-c585-45d9-8b08-f59a6941e6d8","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"3fa37e58-8229-4171-91b9-b5d3a343b3ae","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"0de00a38-0efe-4f85-81a6-fa1e95b9c02b","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"a963f25a-44a3-439f-ae37-1817621f8c11","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"horizontalrule","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"post-event-description","id":"2c94284d-2104-4c47-9853-36e91971a941","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","width":"100%","version":2}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"horizontalrule","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"lineup-info-banner","id":"6f5829a7-340c-4b6c-a190-0f2fb1eccaa2","lineupItems":[{"id":"f06062ef-f975-4e4f-aa07-58022b234af3","order":0,"eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","isHeadliner":true}],"width":"100%","layout":"WITH_HEADLINER","photoShape":"RECTANGLE","textAlignment":"CENTER","headliner":{"width":"100%"},"headlinerTitle":"Headliner","otherSectionTitle":"Talent","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1}],"direction":"ltr","format":"","indent":0,"version":1},"containerClassName":"","editorClassName":""}',
    'needRefreshHTML': True,
    'additionalContent': '{}',
    'showAdditionalContent': False,
    'media': [
        {
            'id': '5cef587a-3e0b-4dab-bd74-2ce5929fe9e4',
            'src': 'https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp',
            'selected': True,
            'type': 'IMAGE',
            'height': 2700,
            'width': 2100,
            'mediaDuration': 0,
            'mediaSrc': None,
            'mediaType': 'IMAGE',
            'inherited': True,
            'position': 1,
            'referenceId': None,
            'source': None,
            'setThumbnail': False,
        },
    ],
    'othersCanCopy': False,
    'enableDownlineNote': False,
    'expiredAt': None,
    'urlAlias': 'api-test-t2601',
    'headline': 'API Test T2601',
    'isPaymentRestrictionEnabled': False,
}, token='linda05_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # step 2: guest get token
    _resp2 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    })
    vars['access_token'] = (_resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 3: Guest visit and check the product purchase exist limit
    _resp3 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t2601'})
    # step 4: 5bd8287b-5f33-4544-8b58-f350221a0d55
    _resp4 = ctx.api.posts.curator_edit_ac273ab5_3f9a_4f89_8e07_72d19c463b18(body=None, token='linda06_token')
    # step 5: Guest visit and check the product purchase exist limit
    _resp5 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'qvur6nnf7n', 'urlAlias': 'api-test-t2601'})
