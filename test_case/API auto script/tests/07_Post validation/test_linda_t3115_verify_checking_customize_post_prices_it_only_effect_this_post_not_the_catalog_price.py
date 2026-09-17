"""Migrated from Apifox case #8003958. Source folder: Post validation."""
# Apifox Case ID: 8003958  (traceability only — not needed to run)
NAME = "Verify checking \"Customize post prices\", it only effect this post, not the catalog price."
TAGS = ["p1", "post_validation", "suite:linda"]
PRIORITY = 1


CASE_ID = 8003958
ENV_NAME = "Release"

# --- step 1: e21e9f86-97f2-41a2-b8c3-8ddc653a00c4 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: f2156443-185c-4ff8-bdf2-4603370d1c98 ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: 
# post: // 2. 检查路径是否正确：variants 现在位于 response.data.variants
# post: if (response.data && response.data.variants && response.data.variants.length > 0) {
# post:     const variant = response.data.variants[0];
# post:     
# post:     // 3. 存入环境变量
# post:     pm.environment.set("catalog_price", variant.price);
# post:     pm.environment.set("compare_price", variant.priceAnchor);
# post:     
# post:     console.log("提取成功 -> catalog_price: " + variant.price + ", compare_price: " + variant.priceAnchor);
# post: } else {
# post:     console.error("未在 response.data.variants 中找到数据，响应结构为: ", JSON.stringify(response));
# post: }
# --- step 3: guest get token ---
# pre: 
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 4: Guest visit the post and check the price is the different from the catalog price ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: 
# post: // 2. 获取 Post 关联的第一个相关产品数据
# post: // 注意：根据 JSON 结构，数据位于 data.relatedProducts[0]
# post: const product = response.data.relatedProducts[0];
# post: 
# post: // 3. 从环境变量获取之前存储的目录原始价格
# post: const originalPrice = pm.environment.get("catalog_price"); // 假设之前存的是 "150"
# post: const originalComparePrice = pm.environment.get("compare_price"); // 假设之前存的是 230
# post: 
# post: // 4. 断言验证
# post: pm.test("验证自定义价格已更新且不同于原始目录价格", function () {
# post:     // 验证当前值
# post:     pm.expect(product.priceDisplay).to.eql(200);
# post:     pm.expect(product.priceDisplayAnchor).to.eql(300);
# post:     
# post:     // 验证当前价格不等于目录原始价格 (逻辑隔离)
# post:     pm.expect(product.priceDisplay.toString()).to.not.eql(originalPrice);
# post:     pm.expect(product.priceDisplayAnchor).to.not.eql(originalComparePrice);
# post: });
# post: 
# post: console.log("自定义价格已验证: " + product.priceDisplay + " (原价: " + originalPrice + ")");




import json

from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t3115_verify_checking_customize_post_prices_it_only_effect_this_post_not_the_catalog_price(ctx: "Context"):
    """Apifox case #8003958: Linda_T3115_Verify_checking_Customize_post_prices_it_only_effect_this_post_not_t"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: e21e9f86-97f2-41a2-b8c3-8ddc653a00c4
    _resp1 = ctx.api.posts.curator_397367e3_1140_4a14_9ba1_26f92bd7f24a(body={
        "id": "397367e3-1140-4a14-9ba1-26f92bd7f24a",
        "announcements": [],
        "createFromEventId": None,
        "title": "API Test T3115",
        "subTitle": "",
        "links": [],
        "allowPromotersResell": False,
        "financeModeForPromoters": "FINANCE_MODE_COMMISSION",
        "financeMode": "FINANCE_MODE_WHOLESALE",
        "status": "ACTIVE",
        "allowPromotersHideProducts": True,
        "allowPromotersCustomizeMedia": True,
        "allowPromotersCreateCoupon": True,
        "promotions": [],
        "isPurchaseQuantityLimited": False,
        "purchaseQuantityLimit": 1,
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
            "color": "#000000",
            "backgroundColor": "#FFFFFF",
            "borderColor": "#CFCFCF",
            "secondaryTextColor": "#5D5D5D",
            "announcementCarousel": {
                "color": "#FFFFFF",
                "backgroundColor": "#0D0D14",
            },
            "title": {
                "color": "#000000",
                "fontSize": 24,
                "fontFamily": "Inter",
                "fontWeight": 800,
            },
            "columnTitle": {
                "color": "#000000",
                "fontSize": 20,
                "fontFamily": "Inter",
                "fontWeight": 700,
            },
            "subtitle": {
                "color": "#000000",
                "fontSize": 20,
                "fontFamily": "Inter",
                "fontWeight": 700,
            },
            "button": {
                "color": "#FFFFFF",
                "fontSize": 16,
                "boxShadow": "none",
                "fontWeight": 700,
                "borderColor": "#0000",
                "borderRadius": 0,
                "backgroundColor": "#0D0D14",
            },
            "secondaryButton": {
                "color": "#0D0D14",
                "fontSize": 16,
                "boxShadow": "none",
                "fontWeight": 700,
                "borderColor": "#0D0D14",
                "borderRadius": 0,
            },
            "textButton": {
                "color": "#0D0D14",
                "fontSize": 16,
                "fontWeight": 700,
            },
            "selectButton": {
                "borderColor": "#2D2D3340",
            },
            "relatedLink": {
                "color": "#2D2D33",
                "borderColor": "#0000",
                "borderRadius": 0,
                "backgroundColor": "#F2F2F6",
            },
            "featuredProducts": {
                "color": "#000000",
                "title": {
                    "color": "#000000",
                    "fontSize": 14,
                    "fontFamily": "Inter",
                    "fontWeight": 400,
                },
                "borderRadius": 0,
                "backgroundColor": "#F2F2F6",
                "secondaryTextColor": "#5D5D5D",
            },
            "product": {
                "color": "#000000",
                "borderRadius": 0,
                "backgroundColor": "#FFFFFF",
                "secondaryTextColor": "#5D5D5D",
            },
            "discount": {
                "color": "#FFFFFF",
                "priceColor": "#D32A08",
                "backgroundColor": "#D32A08",
            },
            "freeShipping": {
                "color": "#268E46",
                "backgroundColor": "#EBF5EF",
            },
            "starRatingColor": "#FAAF00",
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
                    "backgroundColor": "#FFFFFF",
                },
                "secondaryTextColor": "#5D5D5D",
            },
            "lineupBanner": {
                "titleText": "#000000",
                "descriptionText": "#000000",
            },
            "eventInfoBanner": {
                "text": "#000000",
                "secondaryText": "#5D5D5D",
            },
            "eventDescription": {
                "text": "#000000",
                "title": "#000000",
            },
            "layout": {
                "pageHeader": {
                    "style": "DEDICATED_HEADER_BAR",
                    "height": "MEDIUM",
                    "displayText": "NOTHING",
                },
                "productBanner": {
                    "display": "SHRINK",
                    "ctaButton": "VIEW_PRODUCT",
                },
            },
            "template": "TwilightChic",
        },
        "hideInStore": False,
        "recommendationSectionTitle": "",
        "coverImages": [],
        "checkoutInPost": True,
        "allowAffiliateSharingOnly": False,
        "abTestingSettings": [],
        "enableAbTesting": False,
        "isOrderConfirmationNoteEnabled": False,
        "hideCouponBox": False,
        "allowCustomizeDisplayPrices": True,
        "customizeDisplayPrices": None,
        "canSetPrice": True,
        "downlineNoteBodyHtml": None,
        "downlineNoteBodyJson": None,
        "featuredSectionTitle": "Featured products",
        "enableRedirectUrl": False,
        "redirectUrl": "",
        "redirectDestinationName": "",
        "additionalContentPosition": "aboveTickets",
        "bodyHtml": "<div data-id=\"5dab57ec-42da-47bb-9ffb-1be231368874\" data-width=\"100%\" data-height=\"\" data-product-id=\"50cfb015-c43d-463e-8357-4556d592bf26\" data-available-purchase-types=\"ONE_TIME\" data-cta-label=\"Buy now\" data-primary-action=\"buy-now\"></div>",
        "currentDate": "2026-03-10T08:34:49.859Z",
        "relatedProducts": [
            {
                "type": "PRODUCT",
                "merchantProductId": "50cfb015-c43d-463e-8357-4556d592bf26",
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
                "syncWithCatalogPrice": False,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 150,
                        "price": 200,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 300,
                        "merchantProductVariantId": "d4493a35-6b62-47cb-b531-86bcd591af87",
                        "commissionRateForPromoters": 25,
                    },
                ],
            },
        ],
        "accessSpecificUser": [],
        "featuredSectionEnable": True,
        "tab": {
            "value": "Commerce",
            "label": "Commerce",
            "mappingControl": [],
        },
        "timeKey": 1773131689859,
        "originEnablePaymentRestriction": False,
        "syncEnabled": False,
        "postType": "STANDARD",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"5dab57ec-42da-47bb-9ffb-1be231368874\",\"productId\":\"50cfb015-c43d-463e-8357-4556d592bf26\",\"width\":\"100%\",\"height\":\"\",\"availablePurchaseTypes\":[\"ONE_TIME\"],\"ctaLabel\":\"Buy now\",\"action\":\"buy-now\",\"layout\":\"text-focus\",\"type\":\"show-product-banner\",\"version\":3}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
        "needRefreshHTML": True,
        "additionalContent": "{}",
        "showAdditionalContent": False,
        "media": [],
        "othersCanCopy": False,
        "enableDownlineNote": False,
        "allowVisitorCreateAffiliateLink": False,
        "expiredAt": None,
        "urlAlias": "s1o6x7",
        "headline": "API Test T3115",
        "isPaymentRestrictionEnabled": False,
    }, token='linda05_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # assertion 1.assertion: responseJson equal ACTIVE
    expect(_resp1).json('$.data.status').equals('ACTIVE')
    # step 2: f2156443-185c-4ff8-bdf2-4603370d1c98
    _resp2 = ctx.api.products.v_50cfb015_c43d_463e_8357_4556d592bf26(body={
    'id': '50cfb015-c43d-463e-8357-4556d592bf26',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-03-10T07:29:06.728Z',
    'updatedAt': '2026-03-10T08:43:19.758Z',
    'merchantId': '2ff36ba8-8a95-4b65-ae4b-39045e4fe28b',
    'title': 'API Test T3115',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'isBodyHtmlOverridden': False,
    'bodyText': '\n',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-03-10T07:29:06.724Z',
    'publishedScope': '',
    'status': 'ACTIVE',
    'externalStatus': 'ACTIVE',
    'followExternalStatus': False,
    'tags': [],
    'templateSuffix': None,
    'vendor': 'Pear',
    'syncAt': None,
    'deletedAt': None,
    'delisted': False,
    'excludedByImportingTag': False,
    'isFeatured': False,
    'featuredScore': None,
    'inventoryQuantity': 9998,
    'inventoryQuantityOriginal': 9998,
    'soldQuantity': 0,
    'priceDisplay': 150,
    'priceDisplayAnchor': 0,
    'priceMin': 150,
    'priceMinAnchor': 0,
    'priceMax': 150,
    'priceMaxAnchor': 0,
    'priceImportedMin': 0,
    'priceImportedMax': 0,
    'imageCount': 3,
    'isUsed': 'NWT',
    'shippingType': 'INHERIT_SHIPPING',
    'additionalShippingFee': 0,
    'deliveryTime': [
        3,
        5,
    ],
    'returnPolicyApplied': True,
    'isAvailable': True,
    'commissionRate': None,
    'textForShare': None,
    'priceSyncImported': False,
    'coverImage': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1770363520/uploaded_images/qwssqx5coxzhbv5qbzdd.webp',
        'width': 474,
        'height': 265,
        'mediaSrc': None,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'reviewCount': None,
    'reviewOverallScore': None,
    'reviewAggregate': None,
    'displayReviews': True,
    'links': None,
    'taxEnable': False,
    'taxJarCategory': '',
    'customTaxRate': None,
    'subscriptionPlanId': None,
    'reviewRedirectProductId': None,
    'reviewSummary': None,
    'customFieldsInfo': None,
    'listingType': 'REGULAR',
    'shippingOptions': [
        {
            'catalogId': '2ff36ba8-8a95-4b65-ae4b-39045e4fe28b',
            'deliveryTime': [
                0,
                5,
            ],
            'enableFreeShippingThreshold': False,
            'freeShippingThreshold': 0,
            'shippingFee': 4.99,
            'title': 'Flat Shipping',
            'additionalShippingFee': 0,
            'enableAdditionalShippingFee': False,
            'id': 'a69b5f3b-a5de-47b3-b570-75e460bc33b9',
            'productId': '50cfb015-c43d-463e-8357-4556d592bf26',
            'note': None,
            'selected': True,
            'isDefault': True,
            'weightBasedShippingRates': None,
            'enableWeightBasedShippingRates': False,
            'priceBasedShippingRates': None,
            'enablePriceBasedShippingRates': False,
            'profileName': None,
            'from': 'PEAR',
        },
    ],
    'shippingNote': None,
    'autoFulfill': False,
    'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
    'copyFromId': None,
    'stopSellingAfter': None,
    'deliveryMethod': 'SHIPPING',
    'thirdPartyDeliveryMessage': '',
    'isMultipleDaysPassEnabled': False,
    'multipleDaysPass': None,
    'isPickupEtaEnabled': None,
    'atDoorTicketConfig': None,
    'excludeFromPostSync': False,
    'expirationTime': None,
    'allowAtDoorSales': False,
    'options': [
        {
            'remote_id': None,
            'productId': '50cfb015-c43d-463e-8357-4556d592bf26',
            'name': 'Title',
            'position': 1,
            'values': [
                'Default Title',
            ],
            'images': [
                {
                    'value': 'Default Title',
                    'imageId': None,
                },
            ],
        },
    ],
    'variants': [
        {
            'id': 'd4493a35-6b62-47cb-b531-86bcd591af87',
            'remote_id': None,
            'createdAt': '2026-03-10T07:29:06.728Z',
            'updatedAt': '2026-03-10T07:29:06.728Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'inventoryQuantity': 9998,
            'inventoryQuantityOriginal': 9998,
            'soldQuantity': 0,
            'option': {
                'option1': 'Default Title',
            },
            'position': 1,
            'price': '150',
            'priceAnchor': 230,
            'priceImported': '0.00',
            'productId': '50cfb015-c43d-463e-8357-4556d592bf26',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Default Title',
            'weight': 10,
            'weightUnit': 'lb',
            'platform': None,
            'fees': None,
            'transactionFee': {},
            'ticketPrice': 0,
            'isMinPurchaseQuantityEnabled': False,
            'minPurchaseQuantity': None,
            'isMaxPurchaseQuantityEnabled': False,
            'maxPurchaseQuantity': None,
            'isPackSizeEnabled': False,
            'packSize': None,
        },
    ],
    'catalogCommissionRate': 25,
    'isReturnPolicyAllowed': True,
    'earliestTime': '2026-03-10T08:43:26.741Z',
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
    },
    'isProductFormEnabled': True,
    'productForm': {
        'id': '5b1d5a44-ec0f-4eaf-a377-3280b6e5dbb9',
        'title': 'contact form purchase',
        'subtitle': 'Updates by linda',
        'formFields': [
            {
                'id': '50ea3594-2f35-4fa6-9347-ac84625cf517',
                'title': 'hello',
                'field': 'SHORT_ANSWER',
                'required': True,
                'description': '',
                'tooltip': '',
            },
            {
                'id': 'd5488114-3e8d-4a1c-a9f0-cbcb3604746e',
                'title': 'Phone number',
                'field': 'PHONE_NUMBER',
                'required': True,
                'description': '',
                'tooltip': '',
            },
            {
                'id': 'bda50ed5-d870-4005-acbe-fb433df77015',
                'title': 'Instagram',
                'field': 'SOCIAL',
                'required': False,
                'description': '',
                'tooltip': '',
                'extensions': {
                    'socialPlatform': 'INSTAGRAM',
                },
            },
        ],
    },
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'overrideEventTax': False,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'id': 'ebe83e9e-24c1-4b4c-990d-582d6b4dd79e',
            'remote_id': None,
            'createdAt': '2026-03-10T07:29:06.728Z',
            'updatedAt': '2026-03-10T07:29:06.728Z',
            'height': 265,
            'width': 474,
            'position': 1,
            'productId': '50cfb015-c43d-463e-8357-4556d592bf26',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1770363520/uploaded_images/qwssqx5coxzhbv5qbzdd.webp',
            'variantIds': [],
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'contributedBy': 3,
            'contributorId': None,
            'productImageType': 'PRODUCT',
            'source': 'UPLOAD',
        },
        {
            'id': '0c5bf3a8-8a13-4a6f-b742-0b236b72d7ef',
            'remote_id': None,
            'createdAt': '2026-03-10T07:29:06.728Z',
            'updatedAt': '2026-03-10T07:29:06.728Z',
            'height': 2250,
            'width': 3397,
            'position': 2,
            'productId': '50cfb015-c43d-463e-8357-4556d592bf26',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1769158656/uploaded_images/htfzut2cueemhhe9b5ed.webp',
            'variantIds': [],
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'contributedBy': 3,
            'contributorId': None,
            'productImageType': 'PRODUCT',
            'source': 'UPLOAD',
        },
        {
            'id': 'f37adbd3-0e06-4111-8597-36d8d5b3c888',
            'remote_id': None,
            'createdAt': '2026-03-10T07:29:06.728Z',
            'updatedAt': '2026-03-10T07:29:06.728Z',
            'height': 1267,
            'width': 1920,
            'position': 3,
            'productId': '50cfb015-c43d-463e-8357-4556d592bf26',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1769392941/uploaded_images/yb49qhdybizoym9cppvs.webp',
            'variantIds': [],
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'contributedBy': 3,
            'contributorId': None,
            'productImageType': 'PRODUCT',
            'source': 'UPLOAD',
        },
    ],
}, token='linda05_token')
    vars['catalog_price'] = 'variant.price'
    vars['compare_price'] = 'variant.priceAnchor'
    # step 3: guest get token
    _resp3 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    })
    vars['access_token'] = (_resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 4: Guest visit the post and check the price is the different from the catalog price
    _resp4 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 's1o6x7'})
