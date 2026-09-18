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

from typing import Any, TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t2917_verify_the_checked_for_recommendation_and_recommended_products_response_logic_correct(ctx: "Context"):
    """Apifox case #8038584: Linda_T2917_Verify_the_checked_For_recommendation_and_Recommended_products_respo"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 1ed004ca-9615-47c9-9d46-6e774aa66402
    _resp1 = ctx.api.posts.curator_update(post_id='{{T2917_post_id}}', body={
    'id': '{{T2917_post_id}}',
    'announcements': [],
    'createFromEventId': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
    'title': 'API Test T2917',
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
    'isPurchaseQuantityLimited': False,
    'purchaseQuantityLimit': 0,
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
        'dividerColor': '#FFFFFF',
        'secondaryTextColor': '#E0E0E0FF',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontSize': 40,
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
            'borderRadius': 12,
            'backgroundColor': '#F6CA7C',
        },
        'secondaryButton': {
            'color': '#FFFFFF',
            'fontSize': 16,
            'boxShadow': 'none',
            'fontWeight': 400,
            'borderColor': '#F6CA7C',
            'borderRadius': 12,
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
            'borderRadius': 99,
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
            'borderRadius': 16,
            'backgroundColor': '#000000',
            'secondaryTextColor': '#E0E0E0FF',
        },
        'product': {
            'color': '#FFFFFF',
            'borderRadius': 8,
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
        'header': {
            'backgroundColor': '#FFFFFF',
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
        'template': 'ShadowFocus',
        'detailTextColor': '#110921',
        'featuredProduct': {
            'cover': {
                'borderRadius': 8,
            },
        },
    },
    'hideInStore': False,
    'recommendationSectionTitle': 'You may also like',
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
    'featuredSectionTitle': 'Featured products',
    'enableRedirectUrl': False,
    'redirectUrl': '',
    'redirectDestinationName': '',
    'cardCustomizeCoverImages': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp',
            'width': 2100,
            'height': 2700,
            'mediaSrc': None,
            'inherited': False,
            'mediaType': 'IMAGE',
            'setThumbnail': True,
            'mediaDuration': 0,
        },
    ],
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
    'bodyHtml': '<div data-id="cdbd0eeb-4525-4495-8d4a-be7335f41c15" data-type="event-info-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-width="100%"></div><div data-id="0ab44132-49a9-4e77-b6af-67518473766c" data-width="100%" data-height="" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="5589beae-d2ca-40fc-b361-03122952beb2" data-cta-label="Buy Ticket" data-primary-action="buy-now" data-layout="vertical" data-thumbnail-display="showThumbnail" data-event-notes-display="showEventNotes"></div><div data-id="fcd61831-2587-4f92-a372-9e6baa41de22" data-width="100%" data-height="" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="f0a91cf5-c585-45d9-8b08-f59a6941e6d8" data-cta-label="Buy Ticket" data-primary-action="buy-now" data-layout="vertical" data-thumbnail-display="showThumbnail" data-event-notes-display="showEventNotes"></div><div data-id="0b56cb27-2c09-4677-8873-f8eaae4ecdd6" data-width="100%" data-height="" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7" data-cta-label="Buy Ticket" data-primary-action="buy-now" data-layout="vertical" data-thumbnail-display="showThumbnail" data-event-notes-display="showEventNotes"></div><div data-id="06450775-aeed-4432-b7a3-c161e7098261" data-width="100%" data-height="" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="a963f25a-44a3-439f-ae37-1817621f8c11" data-cta-label="Buy Ticket" data-primary-action="buy-now" data-layout="vertical" data-thumbnail-display="showThumbnail" data-event-notes-display="showEventNotes"></div><hr><div data-id="5b22b73d-bd68-4b10-b323-4c7cfaf196b5" data-type="post-event-description" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-width="100%"></div><hr><div data-id="ec8ba8ab-f6bd-404e-b938-f85125badf0f" data-type="lineup-info-banner" data-lineup-items="[{&quot;id&quot;:&quot;f06062ef-f975-4e4f-aa07-58022b234af3&quot;,&quot;order&quot;:0,&quot;eventId&quot;:&quot;0fe6623e-a3ba-40fb-815d-3d6f444775c3&quot;,&quot;isHeadliner&quot;:true}]" data-width="100%" data-layout="WITH_HEADLINER" data-photo-shape="RECTANGLE" data-text-alignment="CENTER" data-headliner="{&quot;width&quot;:&quot;100%&quot;}"></div><p class="katana__paragraph katana__paragraph--align-left"><br></p><p class="katana__paragraph katana__paragraph--align-left"><br></p><p class="katana__paragraph katana__paragraph--align-left"><br></p>',
    'currentDate': '2026-03-17T07:32:37.736Z',
    'relatedProducts': [
        {
            'type': 'PRODUCT',
            'merchantProductId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': True,
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
            'isPurchaseQuantityLimited': False,
            'isRecommendation': True,
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
    ],
    'accessSpecificUser': [],
    'featuredSectionEnable': True,
    'tab': {
        'value': 'Commerce',
        'label': 'Commerce',
        'mappingControl': [],
    },
    'timeKey': 1773732757736,
    'originEnablePaymentRestriction': False,
    'syncEnabled': False,
    'postType': 'EVENT',
    'bodyJson': '{"root":{"children":[{"id":"cdbd0eeb-4525-4495-8d4a-be7335f41c15","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","width":"100%","type":"event-info-banner","version":2},{"id":"0ab44132-49a9-4e77-b6af-67518473766c","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"5589beae-d2ca-40fc-b361-03122952beb2","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","thumbnailDisplay":"showThumbnail","eventNotesDisplay":"showEventNotes","type":"ticket-banner","version":1},{"id":"fcd61831-2587-4f92-a372-9e6baa41de22","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"f0a91cf5-c585-45d9-8b08-f59a6941e6d8","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","thumbnailDisplay":"showThumbnail","eventNotesDisplay":"showEventNotes","type":"ticket-banner","version":1},{"id":"0b56cb27-2c09-4677-8873-f8eaae4ecdd6","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","thumbnailDisplay":"showThumbnail","eventNotesDisplay":"showEventNotes","type":"ticket-banner","version":1},{"id":"06450775-aeed-4432-b7a3-c161e7098261","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"a963f25a-44a3-439f-ae37-1817621f8c11","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","thumbnailDisplay":"showThumbnail","eventNotesDisplay":"showEventNotes","type":"ticket-banner","version":1},{"type":"horizontalrule","version":1,"width":"100%"},{"id":"5b22b73d-bd68-4b10-b323-4c7cfaf196b5","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","width":"100%","type":"post-event-description","version":2},{"type":"horizontalrule","version":1,"width":"100%"},{"id":"ec8ba8ab-f6bd-404e-b938-f85125badf0f","lineupItems":[{"id":"f06062ef-f975-4e4f-aa07-58022b234af3","order":0,"eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","isHeadliner":true}],"width":"100%","height":"","layout":"WITH_HEADLINER","photoShape":"RECTANGLE","textAlignment":"CENTER","headliner":{"width":"100%"},"headlinerTitle":"Headliner","otherSectionTitle":"Talent","type":"lineup-info-banner","version":2},{"children":[],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""},{"children":[],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""},{"children":[],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":"ltr","format":"","indent":0,"type":"root","version":1},"containerClassName":"","editorClassName":""}',
    'needRefreshHTML': True,
    'additionalContent': '{}',
    'showAdditionalContent': False,
    'media': [
        {
            'id': '2e0713e3-15a0-43a6-b736-7614a99ec4bf',
            'src': 'https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp',
            'selected': True,
            'type': 'IMAGE',
            'height': 2700,
            'width': 2100,
            'mediaDuration': 0,
            'mediaSrc': None,
            'mediaType': 'IMAGE',
            'inherited': False,
            'position': 1,
            'referenceId': None,
            'source': None,
            'setThumbnail': False,
        },
    ],
    'othersCanCopy': False,
    'enableDownlineNote': False,
    'expiredAt': None,
    'urlAlias': 'api-test-t2917',
    'headline': 'API Test T2917',
    'isPaymentRestrictionEnabled': False,
}, token='linda05_token')
    # step 2: guest get token
    _resp2 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    }, app_headers=False)
    # === 断言/提取（由Apifox customScript翻译）===
    assert _resp2.status_code == 201, f"step2 status != 201, got {_resp2.status_code}"
    _j2: dict[str, Any] = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    _guestTok = _j2.get('data')
    assert _guestTok, "step2 guest-login 未返回 access_token (data)"
    vars['access_token'] = _guestTok
    # step 3: Guest visit and check the post product recommendation response
    _resp3 = ctx.api.posts.consumer_detail(app_headers=False, token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t2917'})
    # === 断言（由Apifox customScript翻译）===
    _j3: dict[str, Any] = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
    _d3: dict[str, Any] = _j3.get('data') or {}
    assert _d3.get('recommendationSectionTitle') == 'You may also like', f"step3 recommendationSectionTitle 不匹配: {_d3.get('recommendationSectionTitle')}"
    _prods3: list[Any] = _d3.get('relatedProducts') or []
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
    _j4: dict[str, Any] = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
    _d4: dict[str, Any] = _j4.get('data') or {}
    assert _d4.get('recommendationSectionTitle') == 'You may also like', f"step4 recommendationSectionTitle 不匹配: {_d4.get('recommendationSectionTitle')}"
    _prods4: list[Any] = _d4.get('relatedProducts') or []
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
