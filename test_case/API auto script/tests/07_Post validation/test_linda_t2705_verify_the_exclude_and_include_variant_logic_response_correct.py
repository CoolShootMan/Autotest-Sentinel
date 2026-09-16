"""Migrated from Apifox case #8038375. Source folder: Post validation."""
# Apifox Case ID: 8038375  (traceability only — not needed to run)
NAME = "Verify the \"Exclude\"  and \u201cInclude\u201c variant logic response correct"
TAGS = ["p1", "post_validation", "suite:linda"]
PRIORITY = 1


CASE_ID = 8038375
ENV_NAME = "Release"

# --- step 1: 7bac97ce-2d5b-4b26-9ea3-b6c2303e1ab7 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: guest get token ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 3: Guest visit and check the varaint exclude and include response ---
# post[customScript]: // 解析响应体
# post: const responseData = pm.response.json();
# post: const relatedProduct = responseData.data.relatedProducts[0];
# post: const variants = relatedProduct.variants;
# post: 
# post: // 1. 断言特定变体的属性 (isExcluded 和 title)
# post: pm.test("校验特定 Variant 的 title 和 isExcluded 状态", function () {
# post:     variants.forEach(variant => {
# post:         if (variant.merchantProductVariantId === "8a77a74a-9b7e-47fa-9527-b4ffc34e7d06") {
# post:             pm.expect(variant.title).to.eql("18:00 AM");
# post:             pm.expect(variant.isExcluded).to.be.false;
# post:         }
# post:         
# post:         if (variant.merchantProductVariantId === "59b0c824-dd2d-450b-b858-3a6423432ebc") {
# post:             pm.expect(variant.title).to.eql("20:00 PM");
# post:             pm.expect(variant.isExcluded).to.be.false;
# post:         }
# post:     });
# post: });
# post: 
# post: // 2. 断言 displayVariantId 是否符合预期
# post: pm.test("校验 displayVariantId 为 07eb325b-e2f6-419c-96db-a5fd8fb7994c", function () {
# post:     pm.expect(relatedProduct.displayVariantId).to.eql("07eb325b-e2f6-419c-96db-a5fd8fb7994c");
# post: });
# post: 
# post: // 3. 断言不存在指定的 merchantProductVariantId
# post: pm.test("校验不存在特定的 merchantProductVariantId 列表", function () {
# post:     const excludedIds = [
# post:         "dbd67afc-4bab-45c2-b6a5-69ac1d23805b", 
# post:         "6b4dba36-9e0e-4123-ab7c-e95dd9e86d13"
# post:     ];
# post:     
# post:     // 获取当前响应中所有的 variantId
# post:     const currentVariantIds = variants.map(v => v.merchantProductVariantId);
# post:     
# post:     excludedIds.forEach(id => {
# post:         pm.expect(currentVariantIds).to.not.include(id, `不应该包含 ID: ${id}`);
# post:     });
# post: });
# --- step 4: Consumer visit and check the varaint exclude and include response ---
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
# post[customScript]: // 解析响应体
# post: const responseData = pm.response.json();
# post: const relatedProduct = responseData.data.relatedProducts[0];
# post: const variants = relatedProduct.variants;
# post: 
# post: // 1. 断言特定变体的属性 (isExcluded 和 title)
# post: pm.test("校验特定 Variant 的 title 和 isExcluded 状态", function () {
# post:     variants.forEach(variant => {
# post:         if (variant.merchantProductVariantId === "8a77a74a-9b7e-47fa-9527-b4ffc34e7d06") {
# post:             pm.expect(variant.title).to.eql("18:00 AM");
# post:             pm.expect(variant.isExcluded).to.be.false;
# post:         }
# post:         
# post:         if (variant.merchantProductVariantId === "59b0c824-dd2d-450b-b858-3a6423432ebc") {
# post:             pm.expect(variant.title).to.eql("20:00 PM");
# post:             pm.expect(variant.isExcluded).to.be.false;
# post:         }
# post:     });
# post: });
# post: 
# post: // 2. 断言 displayVariantId 是否符合预期
# post: pm.test("校验 displayVariantId 为 07eb325b-e2f6-419c-96db-a5fd8fb7994c", function () {
# post:     pm.expect(relatedProduct.displayVariantId).to.eql("07eb325b-e2f6-419c-96db-a5fd8fb7994c");
# post: });
# post: 
# post: // 3. 断言不存在指定的 merchantProductVariantId
# post: pm.test("校验不存在特定的 merchantProductVariantId 列表", function () {
# post:     const excludedIds = [
# post:         "dbd67afc-4bab-45c2-b6a5-69ac1d23805b", 
# post:         "6b4dba36-9e0e-4123-ab7c-e95dd9e86d13"
# post:     ];
# post:     
# post:     // 获取当前响应中所有的 variantId
# post:     const currentVariantIds = variants.map(v => v.merchantProductVariantId);
# post:     
# post:     excludedIds.forEach(id => {
# post:         pm.expect(currentVariantIds).to.not.include(id, `不应该包含 ID: ${id}`);
# post:     });
# post: });




import json

from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t2705_verify_the_exclude_and_include_variant_logic_response_correct(ctx: "Context"):
    """Apifox case #8038375: Linda_T2705_Verify_the_Exclude_and_Include_variant_logic_response_correct"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 7bac97ce-2d5b-4b26-9ea3-b6c2303e1ab7
    _resp1 = ctx.api.posts.curator_de6f0abd_c8f8_41e5_b2d1_1eb2ba05f839(body={
    'id': 'de6f0abd-c8f8-41e5-b2d1-1eb2ba05f839',
    'announcements': None,
    'createFromEventId': '8c911bb6-78ec-4af4-a78c-479a0416349d',
    'title': 'API TEST T2705',
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
        'fontFamily': 'Replica Mono LL',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'dividerColor': '#CFCFCF',
        'secondaryTextColor': '#ABABAB',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontSize': 30,
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
            'fontFamily': 'Replica Mono LL',
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
            'color': '#000000',
            'borderColor': '#0000',
            'borderRadius': 0,
            'backgroundColor': '#FFFFFF80',
        },
        'featuredProducts': {
            'color': '#FFFFFF',
            'title': {
                'color': '#FFFFFF',
                'fontSize': 14,
                'fontFamily': 'Replica Mono LL',
                'fontWeight': 400,
            },
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'secondaryTextColor': '#ABABAB',
        },
        'product': {
            'color': '#FFFFFF',
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'secondaryTextColor': '#ABABAB',
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
            'secondaryTextColor': '#ABABAB',
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
            'text': '#9E9E9E',
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
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1773383669/uploaded_images/jlpay15cvcj9upgdlzw8.webp',
            'width': 2560,
            'height': 3413,
            'mediaSrc': None,
            'position': 1,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
            'setThumbnail': True,
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
        'price': 'Instagram Live, Zoom, In-person | Sat, Mar 14 (CDT)',
        'discountPercent': 'Get Tickets',
        'titleColor': '#FFFFFF',
        'priceColor': '#FFFFFF',
        'discountPercentColor': '#D32A08',
    },
    'canSetPrice': False,
    'downlineNoteBodyHtml': None,
    'downlineNoteBodyJson': None,
    'featuredSectionTitle': '',
    'enableRedirectUrl': False,
    'redirectUrl': '',
    'redirectDestinationName': '',
    'cardCustomizeCoverImages': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1773383669/uploaded_images/jlpay15cvcj9upgdlzw8.webp',
            'width': 2560,
            'height': 3413,
            'mediaSrc': None,
            'position': 1,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
            'setThumbnail': True,
        },
    ],
    'event': {
        'id': '8c911bb6-78ec-4af4-a78c-479a0416349d',
        'status': 'UPCOMING',
        'title': 'API Test for multiple variants',
        'venue': 'Instagram Live, Zoom, In-person',
        'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
        'startDateDisplay': '2026-03-20 01:37',
        'endDateDisplay': '2032-03-20',
        'timezone': {
            'dstOffset': 3600,
            'rawOffset': -21600,
            'timeZoneId': 'America/Chicago',
            'timeZoneName': 'Central Daylight Time',
        },
        'poster': {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1773383669/uploaded_images/jlpay15cvcj9upgdlzw8.webp',
            'width': 2560,
            'height': 3413,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    },
    'additionalContentPosition': 'aboveTickets',
    'bodyHtml': '<div class="lexical-root"><div class="katana-paragraph"><div class="event-info-banner" data-event-id="8c911bb6-78ec-4af4-a78c-479a0416349d" data-node-id="71fa0b33-d07e-4490-a518-eb61a49b5129">Event Info</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="8c911bb6-78ec-4af4-a78c-479a0416349d" data-product-id="06099c59-48d6-494b-be00-74ee20e78f75" data-node-id="3e045651-f7f1-49f6-88df-1c836e5baf07">Buy Ticket</div></div><div class="katana-paragraph"><hr /></div><div class="katana-paragraph"><span style="font-size: 20px;"><strong>Missed our last event?  everything is ok.</strong></span></div><div class="katana-paragraph">Everything is well. Here\'s a lil recap of our last event👇</div><div class="katana-paragraph"><br></div><div class="katana-paragraph"><img src="https://res.cloudinary.com/dr9io1zjv/v1773383675/uploaded_images/zmqf8vdwsuza5qqkqc70.webp" alt="placeholder image" style="width: 100%; height: 100%;" /></div><div class="katana-paragraph"><img src="https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/t0lafz3hk5sfnvv70jpc.webp" alt="placeholder image" style="width: 100%; height: 100%;" /></div><div class="katana-paragraph"><img src="https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/lecifjjuftkjxjmizgg9.webp" alt="placeholder image" style="width: 100%; height: 100%;" /></div><div class="katana-paragraph"><hr /></div><div class="katana-paragraph"><div class="lineup-info-banner" data-node-id="daa924b4-684e-4881-ae35-d23ad2ed8879">Lineup</div></div></div>',
    'currentDate': '2026-03-17T06:42:42.734Z',
    'relatedProducts': [
        {
            'type': 'PRODUCT',
            'merchantProductId': '06099c59-48d6-494b-be00-74ee20e78f75',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': [],
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 21,
                    'price': 23.33,
                    'costPrice': 0,
                    'isExcluded': True,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': 'dbd67afc-4bab-45c2-b6a5-69ac1d23805b',
                    'commissionRateForPromoters': 10,
                },
                {
                    'wholesalePriceForPromoters': 31,
                    'price': 34.44,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '8a77a74a-9b7e-47fa-9527-b4ffc34e7d06',
                    'commissionRateForPromoters': 10,
                },
                {
                    'wholesalePriceForPromoters': 41,
                    'price': 45.56,
                    'costPrice': 0,
                    'isExcluded': True,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '6b4dba36-9e0e-4123-ab7c-e95dd9e86d13',
                    'commissionRateForPromoters': 10,
                },
                {
                    'wholesalePriceForPromoters': 51,
                    'price': 56.67,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '59b0c824-dd2d-450b-b858-3a6423432ebc',
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
    'timeKey': 1773729762734,
    'originEnablePaymentRestriction': False,
    'syncEnabled': True,
    'postType': 'EVENT',
    'bodyJson': '{"root":{"type":"root","children":[{"type":"katana-paragraph","children":[{"type":"event-info-banner","id":"71fa0b33-d07e-4490-a518-eb61a49b5129","eventId":"8c911bb6-78ec-4af4-a78c-479a0416349d","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"id":"6f7693fa-1ff2-49aa-8cb0-209fe5118a56","type":"additional-content","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"3e045651-f7f1-49f6-88df-1c836e5baf07","eventId":"8c911bb6-78ec-4af4-a78c-479a0416349d","productId":"06099c59-48d6-494b-be00-74ee20e78f75","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"horizontalrule","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"extended-text","text":"Missed our last event?  everything is ok.","format":1,"version":1,"style":"font-size: 20px;"}],"direction":"ltr","format":"left","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"extended-text","text":"Everything is well. Here\'s a lil recap of our last event👇","format":0,"version":1}],"direction":"ltr","format":"left","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[],"direction":"ltr","format":"center","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"media","src":"https://res.cloudinary.com/dr9io1zjv/v1773383675/uploaded_images/zmqf8vdwsuza5qqkqc70.webp","imageSrc":"https://res.cloudinary.com/dr9io1zjv/v1773383675/uploaded_images/zmqf8vdwsuza5qqkqc70.webp","srcId":"16c31e48-e469-4604-9f94-d399ee519551","mediaType":"IMAGE","width":"100%","height":"100%","baseWidth":474,"baseHeight":265,"unit":"PERCENT","altText":"placeholder image","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"media","src":"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/t0lafz3hk5sfnvv70jpc.webp","imageSrc":"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/t0lafz3hk5sfnvv70jpc.webp","srcId":"344557a6-647c-40e5-b4ab-f9d5eba10f0a","mediaType":"IMAGE","width":"100%","height":"100%","baseWidth":1440,"baseHeight":1152,"unit":"PERCENT","altText":"placeholder image","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"media","src":"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/lecifjjuftkjxjmizgg9.webp","imageSrc":"https://res.cloudinary.com/dr9io1zjv/v1773383674/uploaded_images/lecifjjuftkjxjmizgg9.webp","srcId":"8d90c52a-b95c-4ddb-970d-8c90e07b5c71","mediaType":"IMAGE","width":"100%","height":"100%","baseWidth":1192,"baseHeight":710,"unit":"PERCENT","altText":"placeholder image","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"horizontalrule","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"lineup-info-banner","id":"daa924b4-684e-4881-ae35-d23ad2ed8879","lineupItems":[{"id":"47f88972-05aa-4668-83ef-095472aa8f18","order":0,"eventId":"8c911bb6-78ec-4af4-a78c-479a0416349d","isHeadliner":false}],"width":"100%","layout":"WITHOUT_HEADLINER","photoShape":"RECTANGLE","textAlignment":"CENTER","headliner":{"width":"100%"},"headlinerTitle":"Headliner","otherSectionTitle":"Talent","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1}],"direction":"ltr","format":"","indent":0,"version":1},"containerClassName":"","editorClassName":""}',
    'needRefreshHTML': True,
    'additionalContent': '{}',
    'showAdditionalContent': False,
    'media': [
        {
            'id': 'c1849e1b-dfb7-4553-94de-00e5d5c29719',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1773383669/uploaded_images/jlpay15cvcj9upgdlzw8.webp',
            'selected': True,
            'type': 'IMAGE',
            'height': 3413,
            'width': 2560,
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
    'urlAlias': 'api-test-2705',
    'headline': 'API TEST T2705',
    'isPaymentRestrictionEnabled': False,
}, token='linda05_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # assertion 1.assertion: responseJson equal ACTIVE
    expect(_resp1).json('$.data.status').equals('ACTIVE')
    # step 2: guest get token
    _resp2 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    })
    vars['access_token'] = (_resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 3: Guest visit and check the varaint exclude and include response
    _resp3 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-2705'})
    # step 4: Consumer visit and check the varaint exclude and include response
    _resp4 = ctx.api.posts.consumer_detail(token='linda10_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-2705'})
