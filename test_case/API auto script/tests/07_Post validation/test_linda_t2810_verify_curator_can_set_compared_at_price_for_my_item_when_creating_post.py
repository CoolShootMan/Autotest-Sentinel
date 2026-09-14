"""Auto-generated from Apifox case #6111855. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 6111855
# Folder: 
# Case: (Linda)T2810 Verify curator can set compared at price for my item when creating post
# Priority: P1
# Created: 2025-03-06T08:10:58.000Z
# Updated: 2026-08-25T07:43:58.000Z


CASE_ID = 6111855
ENV_NAME = "Release"

# --- step 1: Get Partner linda01 token ---
# pre: pm.environment.set("account_email_merchant","dian.yuhong.ext@1m.app");
# pre: pm.environment.set("password_merchant","178Ad6e0aF0Ec22Ab948d8c0c69Ae072");
# post[customScript]:     if(pm.response.to.have.status(201)){
# post:         var res = JSON.parse(responseBody);
# post:         pm.environment.set("merchant_access_token",res['data']['token']);
# post:     }
# post[extractor]: {"variableName": "linda01_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: update post related product's "compare at price" ---
# pre: 
# pre: 
# pre: // 生成一个 100 到 999 之间的随机整数
# pre: var CompareAtPrice = Math.floor(100 + Math.random() * 900);
# pre: 
# pre: // 设置环境变量
# pre: pm.environment.set("CompareAtPrice", CompareAtPrice);
# pre: 
# pre: // 打印变量值
# pre: console.log("CompareAtPrice is", CompareAtPrice);
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: Check the compare at price display correct ---
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{CompareAtPrice}}", "path": "$.data.relatedProducts[0].priceDisplayAnchor", "multipleValue": [], "extractSettings": {"expression": "$.data.relatedProducts[0].priceDisplayAnchor", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





from core.assertions import expect

def test__6111855__Linda_T2810_Verify_curator_can_set_compared_at_price_for_my_item_when_creating_post(ctx):
    """Apifox case #6111855: Linda_T2810_Verify_curator_can_set_compared_at_price_for_my_item_when_creating_p"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['account_email_merchant'] = 'dian.yuhong.ext@1m.app'
    vars['password_merchant'] = '178Ad6e0aF0Ec22Ab948d8c0c69Ae072'
    # step 1: Get Partner linda01 token
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
        "email": "linda.zhou.ext+01@1m.app",
    })
    ctx.extract('merchant_access_token', _resp1, '$.data.token')
    # extractor: linda01_token = $.data.token
    ctx.extract('linda01_token', _resp1, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    vars['postid'] = 'eb9c09da-7e3b-4c11-a735-00bc9d414275'
    import random as _random
    vars['CompareAtPrice'] = _random.randint(100, 999)
    # step 2: update post related product's "compare at price"
    _resp2 = ctx.api.posts.curator_by_post_id(body={
    'id': '{{postid}}',
    'announcements': [],
    'createFromEventId': '79a0ae94-a4dc-4bf8-bc24-7951d78f4237',
    'title': 'automation-t2810',
    'subTitle': '',
    'links': [],
    'allowPromotersResell': False,
    'financeModeForPromoters': 'FINANCE_MODE_COMMISSION',
    'financeMode': 'FINANCE_MODE_WHOLESALE',
    'status': 'ACTIVE',
    'allowPromotersHideProducts': False,
    'allowPromotersCustomizeMedia': False,
    'allowPromotersCreateCoupon': False,
    'allowVisitorCreateAffiliateLink': False,
    'promotions': [],
    'isPurchaseQuantityLimited': False,
    'purchaseQuantityLimit': 0,
    'isAccessRestricted': False,
    'allowPromotersAccess': False,
    'styleSettings': {
        'recentUsedColors': [
            '#110921FF',
            '#ECA416FF',
            '#B7E2E0FF',
            '#BA68C8FF',
            '#CB135BFF',
            '#F1BBFFFF',
            '#E91E63FF',
            '#0B99FFFF',
            '#FFFFFFFF',
            '#000000FF',
            '#FFE0B2FF',
            '#FACA4EFF',
            '#EEEEEE',
            '#3F51B5',
            '#7132F4',
            '#8BC34A',
            '#000000',
        ],
        'fontFamily': 'Replica Mono LL',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
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
        'template': 'ShadowFocus',
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
            'id': '5b31fd19-d72d-42e9-91e8-e4d3c6df62b9',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'selected': True,
            'type': 'IMAGE',
            'height': 2048,
            'width': 3072,
            'mediaDuration': 0,
            'mediaSrc': None,
            'mediaType': 'IMAGE',
            'inherited': False,
            'position': 1,
            'referenceId': None,
            'source': None,
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
        'price': 'Instagram Live, Zoom, In-person | Fri, Dec 05, 2025 12:00 AM - Sat, Dec 13, 2025 12:00 AM (CST)',
        'priceColor': '#F6CA7C',
        'discountPercent': 'Get Tickets',
        'discountPercentColor': '#D32A08',
    },
    'canSetPrice': True,
    'downlineNoteBodyHtml': None,
    'downlineNoteBodyJson': None,
    'featuredSectionTitle': 'Featured products',
    'bodyHtml': '<p class="katana__paragraph--align-left"><span data-id="fc25524a-0380-4d63-885e-4b553fb0d602" data-type="event-info-banner" data-event-id="79a0ae94-a4dc-4bf8-bc24-7951d78f4237"></span></p><p class="katana__paragraph--align-left"><span data-id="143dd2b7-6c55-4664-958b-0b9988963d4a" data-width="100%" data-height="" data-product-id="5eed9a05-008f-40ab-a984-403cb2217e07" data-available-purchase-types="ONE_TIME" data-cta-label="Buy Ticket" data-primary-action="buy-now"></span></p>',
    'currentDate': '2025-12-10T06:28:58.631Z',
    'relatedProducts': [
        {
            'type': 'PRODUCT',
            'merchantProductId': '5eed9a05-008f-40ab-a984-403cb2217e07',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductId': None,
            'syncWithCatalogPrice': False,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 10,
                    'price': 10,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': '{{CompareAtPrice}}',
                    'merchantProductVariantId': 'c3f9aa79-fd7b-44cd-a450-5658e780b623',
                    'commissionRateForPromoters': 0,
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
    'timeKey': 1765348138631,
    'bodyJson': '{"root":{"children":[{"children":[{"id":"fc25524a-0380-4d63-885e-4b553fb0d602","eventId":"79a0ae94-a4dc-4bf8-bc24-7951d78f4237","type":"event-info-banner","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""},{"children":[{"id":"143dd2b7-6c55-4664-958b-0b9988963d4a","productId":"5eed9a05-008f-40ab-a984-403cb2217e07","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"event","type":"show-product-banner","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":"ltr","format":"","indent":0,"type":"root","version":1}}',
    'media': [
        {
            'id': '5b31fd19-d72d-42e9-91e8-e4d3c6df62b9',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'selected': True,
            'type': 'IMAGE',
            'height': 2048,
            'width': 3072,
            'mediaDuration': 0,
            'mediaSrc': None,
            'mediaType': 'IMAGE',
            'inherited': False,
            'position': 1,
            'referenceId': None,
            'source': None,
            'setThumbnail': True,
        },
    ],
    'othersCanCopy': False,
    'enableDownlineNote': False,
    'expiredAt': '2029-12-27T09:00:00.000Z',
    'urlAlias': 'automation-t2810',
    'headline': 'automation-t2810',
}, app_headers=False, token='linda01_token', path_vars={'postId': '{{postid}}'})
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: Check the compare at price display correct
    _resp3 = ctx.api.posts.consumer_detail(params={'vanityUrl': 'lindazhoucurator', 'urlAlias': 'automation-t2810'}, app_headers=False, token='linda01_token')
    # assertion 3.assertion: responseJson equal {{CompareAtPrice}}
    expect(_resp3).json('$.data.relatedProducts[0].priceDisplayAnchor').equals(ctx.render_text('{{CompareAtPrice}}'))
