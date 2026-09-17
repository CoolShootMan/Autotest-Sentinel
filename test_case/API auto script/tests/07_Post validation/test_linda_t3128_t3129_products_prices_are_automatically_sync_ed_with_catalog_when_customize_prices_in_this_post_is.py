"""Migrated from Apifox case #8002034. Source folder: Post validation."""
# Apifox Case ID: 8002034  (traceability only — not needed to run)
NAME = "& T3129 Products' prices are automatically sync\u2019ed with catalog, when \u201cCustomize prices in this post\u201c is unchecked."
TAGS = ["p0", "post_validation", "suite:linda"]
PRIORITY = 0


CASE_ID = 8002034
ENV_NAME = "Release"

# --- step 1: Get Partner linda05 token ---
# post[extractor]: {"variableName": "linda05_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: ef97c015-e8da-4d6e-b6fe-810743047a51 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: ddca356f-5135-44c3-843d-8874ecd9084c ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: 
# post: // 2. 获取第一个变体对象
# post: const firstVariant = response.data.variants[0];
# post: 
# post: // 3. 断言验证：验证价格是否更新为 500
# post: pm.test("验证第一个变体的价格是否为 500", function () {
# post:     // 注意：JSON中价格是字符串 "500"，这里进行严格相等检查
# post:     pm.expect(firstVariant.price).to.eql("500");
# post:     console.log("价格验证通过，当前价格为: " + firstVariant.price);
# post: });
# post: 
# post: // 4. 提取价格并设置为全局/环境变量
# post: // 将 "500" 转换为数字或保留字符串，取决于你后续接口的需求
# post: const newCatalogPrice = firstVariant.price;
# post: pm.environment.set("catalog_price", newCatalogPrice);
# post: 
# post: console.log("已成功提取 catalog_price 为: " + newCatalogPrice);
# --- step 4: guest get token ---
# pre: 
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 5: 571d96f4-9159-4150-92e2-6b1021dcc907 ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: // 确保变量名与你设置时使用的 "catalog_price" 完全一致
# post: const expectedPrice = pm.environment.get("catalog_price"); 
# post: 
# post: // 2. 验证路径（根据你的 JSON 结构）
# post: const product = response.data && response.data.relatedProducts && response.data.relatedProducts[0];
# post: const actualVariant = product && product.variants && product.variants[0];
# post: 
# post: pm.test("验证价格是否与上一接口一致", function () {
# post:     pm.expect(actualVariant, "未在响应中找到 variants 数据").to.not.be.undefined;
# post:     
# post:     // 确保 expectedPrice 存在后再进行比较，防止再次出现 TypeError
# post:     pm.expect(expectedPrice, "环境变量 catalog_price 未定义，请检查上一个接口是否运行").to.not.be.undefined;
# post:     
# post:     const actualPrice = actualVariant.price;
# post:     pm.expect(actualPrice.toString()).to.eql(expectedPrice.toString());
# post: });
# post: 
# post: console.log("预期价格 (catalog_price): " + expectedPrice + ", 实际价格: " + (actualVariant ? actualVariant.price : "N/A"));
# --- step 6: 08cc6f65-5bae-4aab-91f7-ba4883ab6cbb ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: 
# post: // 2. 获取第一个变体对象
# post: const firstVariant = response.data.variants[0];
# post: 
# post: // 3. 断言验证：验证价格是否更新为 100
# post: pm.test("验证第一个变体的价格是否为 100", function () {
# post:     // 注意：JSON中价格是字符串 "100"，这里进行严格相等检查
# post:     pm.expect(firstVariant.price).to.eql("100");
# post:     console.log("价格验证通过，当前价格为: " + firstVariant.price);
# post: });
# post: 
# post: // 4. 提取价格并设置为全局/环境变量
# post: // 将 "100" 转换为数字或保留字符串，取决于你后续接口的需求
# post: const newCatalogPrice = firstVariant.price;
# post: pm.environment.set("catalog_price", newCatalogPrice);
# post: 
# post: console.log("已成功提取 catalog_price 为: " + newCatalogPrice);




import json

from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t3128_t3129_products_prices_are_automatically_sync_ed_with_catalog_when_customize_prices_in_this_post_is(ctx: "Context"):
    """Apifox case #8002034: Linda_T3128_T3129_Products_prices_are_automatically_sync_ed_with_catalog_when_Cu"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
        "email": "linda.zhou.ext+05@1m.app",
    }, app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    # step 2: ef97c015-e8da-4d6e-b6fe-810743047a51
    _resp2 = ctx.api.posts.curator_9fd62b45_6f4a_4bca_ac59_778e44c2813b(body={
        "id": "9fd62b45-6f4a-4bca-ac59-778e44c2813b",
        "announcements": [],
        "createFromEventId": None,
        "title": "API Test T3158 & t3129",
        "subTitle": "",
        "links": [],
        "allowPromotersResell": False,
        "financeModeForPromoters": "FINANCE_MODE_COMMISSION",
        "financeMode": "FINANCE_MODE_COMMISSION",
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
        "canSetPrice": False,
        "downlineNoteBodyHtml": None,
        "downlineNoteBodyJson": None,
        "featuredSectionTitle": "Featured products",
        "enableRedirectUrl": False,
        "redirectUrl": "",
        "redirectDestinationName": "",
        "additionalContentPosition": "aboveTickets",
        "bodyHtml": "<div data-id=\"32808496-9c58-4425-9cb5-6626817dcf63\" data-width=\"100%\" data-height=\"\" data-product-id=\"2efee169-7e73-4d20-8d56-d99d7f4ab699\" data-available-purchase-types=\"ONE_TIME\" data-cta-label=\"Buy now\" data-variant-id=\"cd72c453-be00-4c8c-9190-da2b38d09309\" data-primary-action=\"buy-now\"></div>",
        "currentDate": "2026-03-10T05:56:29.980Z",
        "relatedProducts": [
            {
                "type": "PRODUCT",
                "merchantProductId": "2efee169-7e73-4d20-8d56-d99d7f4ab699",
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
                        "wholesalePriceForPromoters": 75,
                        "price": 100,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "cd72c453-be00-4c8c-9190-da2b38d09309",
                        "commissionRateForPromoters": 25,
                    },
                    {
                        "wholesalePriceForPromoters": 150,
                        "price": 200,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "9beef69a-1abc-469c-b640-e325a9bc371d",
                        "commissionRateForPromoters": 25,
                    },
                    {
                        "wholesalePriceForPromoters": 225,
                        "price": 300,
                        "costPrice": 0,
                        "isExcluded": False,
                        "isDefault": False,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "9524a540-b15c-4edc-a2b3-700d34f1335a",
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
        "timeKey": 1773122189980,
        "originEnablePaymentRestriction": False,
        "syncEnabled": False,
        "postType": "STANDARD",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"32808496-9c58-4425-9cb5-6626817dcf63\",\"productId\":\"2efee169-7e73-4d20-8d56-d99d7f4ab699\",\"variantId\":\"cd72c453-be00-4c8c-9190-da2b38d09309\",\"width\":\"100%\",\"height\":\"\",\"availablePurchaseTypes\":[\"ONE_TIME\"],\"ctaLabel\":\"Buy now\",\"action\":\"buy-now\",\"layout\":\"text-focus\",\"type\":\"show-product-banner\",\"version\":3}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
        "needRefreshHTML": True,
        "additionalContent": "{}",
        "showAdditionalContent": False,
        "media": [],
        "othersCanCopy": False,
        "enableDownlineNote": False,
        "allowVisitorCreateAffiliateLink": False,
        "expiredAt": None,
        "urlAlias": "c77lcn",
        "headline": "API Test T3158 & t3129",
        "isPaymentRestrictionEnabled": False,
    }, token='linda05_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: ddca356f-5135-44c3-843d-8874ecd9084c
    _resp3 = ctx.api.products.v_2efee169_7e73_4d20_8d56_d99d7f4ab699(body={
    'id': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-03-10T03:53:11.833Z',
    'updatedAt': '2026-03-10T04:05:00.934Z',
    'merchantId': '2ff36ba8-8a95-4b65-ae4b-39045e4fe28b',
    'title': 'API Test T3128 & T3129',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'isBodyHtmlOverridden': False,
    'bodyText': '\n',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-03-10T03:53:11.828Z',
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
    'inventoryQuantity': 29994,
    'inventoryQuantityOriginal': 29994,
    'soldQuantity': 0,
    'priceDisplay': 100,
    'priceDisplayAnchor': 0,
    'priceMin': 100,
    'priceMinAnchor': 0,
    'priceMax': 300,
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
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
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
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
            'name': 'Color',
            'position': 1,
            'values': [
                'yellow',
                'Glacier Silver',
                'Forest Green',
            ],
            'images': [
                {
                    'value': 'yellow',
                    'imageId': None,
                },
                {
                    'value': 'Glacier Silver',
                    'imageId': None,
                },
                {
                    'value': 'Forest Green',
                    'imageId': None,
                },
            ],
        },
    ],
    'variants': [
        {
            'id': 'cd72c453-be00-4c8c-9190-da2b38d09309',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
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
                'option1': 'yellow',
            },
            'position': 1,
            'price': 500,
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'yellow',
            'weight': None,
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
        {
            'id': '9beef69a-1abc-469c-b640-e325a9bc371d',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
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
                'option1': 'Glacier Silver',
            },
            'position': 2,
            'price': '200',
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Glacier Silver',
            'weight': None,
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
        {
            'id': '9524a540-b15c-4edc-a2b3-700d34f1335a',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
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
                'option1': 'Forest Green',
            },
            'position': 3,
            'price': '300',
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Forest Green',
            'weight': None,
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
    'earliestTime': '2026-03-10T06:15:04.511Z',
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
        'id': 'cb5870cb-f05b-406c-8ef6-0f6b2c956aeb',
        'title': 'contact form purchase',
        'subtitle': 'Updates by linda',
        'formFields': [
            {
                'id': '841797f4-93b0-4796-a7ce-c523de2c8d5e',
                'title': 'hello',
                'field': 'SHORT_ANSWER',
                'required': True,
                'description': '',
                'tooltip': '',
            },
            {
                'id': '4fd172d8-34b2-4964-943b-df5296679565',
                'title': 'Phone number',
                'field': 'PHONE_NUMBER',
                'required': True,
                'description': '',
                'tooltip': '',
            },
            {
                'id': '2452bc06-d1b7-4374-a8de-58fc7c5096ef',
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
            'id': 'd73143b3-78aa-44e3-9414-8af7069f123a',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
            'height': 265,
            'width': 474,
            'position': 1,
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
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
            'id': 'fe59e6e0-678f-4cfb-ad00-5c9f4956c0ec',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
            'height': 2250,
            'width': 3397,
            'position': 2,
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
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
            'id': '1e5a900e-d2f2-4148-9c64-ebd8907c6152',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
            'height': 1267,
            'width': 1920,
            'position': 3,
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
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
    vars['catalog_price'] = 'newCatalogPrice'
    # step 4: guest get token
    _resp4 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    })
    vars['access_token'] = (_resp4.json() if _resp4.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 5: 571d96f4-9159-4150-92e2-6b1021dcc907
    _resp5 = ctx.api.posts.consumer_detail(body=None, params={'vanityUrl': 'resident', 'urlAlias': 'c77lcn'}, token='access_token')
    # step 6: 08cc6f65-5bae-4aab-91f7-ba4883ab6cbb
    _resp6 = ctx.api.products.v_2efee169_7e73_4d20_8d56_d99d7f4ab699(body={
    'id': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-03-10T03:53:11.833Z',
    'updatedAt': '2026-03-10T06:29:41.447Z',
    'merchantId': '2ff36ba8-8a95-4b65-ae4b-39045e4fe28b',
    'title': 'API Test T3128 & T3129',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'isBodyHtmlOverridden': False,
    'bodyText': '\n',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-03-10T03:53:11.828Z',
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
    'inventoryQuantity': 29994,
    'inventoryQuantityOriginal': 29994,
    'soldQuantity': 0,
    'priceDisplay': 200,
    'priceDisplayAnchor': 0,
    'priceMin': 200,
    'priceMinAnchor': 0,
    'priceMax': 500,
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
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
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
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
            'name': 'Color',
            'position': 1,
            'values': [
                'yellow',
                'Glacier Silver',
                'Forest Green',
            ],
            'images': [
                {
                    'value': 'yellow',
                    'imageId': None,
                },
                {
                    'value': 'Glacier Silver',
                    'imageId': None,
                },
                {
                    'value': 'Forest Green',
                    'imageId': None,
                },
            ],
        },
    ],
    'variants': [
        {
            'id': 'cd72c453-be00-4c8c-9190-da2b38d09309',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
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
                'option1': 'yellow',
            },
            'position': 1,
            'price': 100,
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'yellow',
            'weight': None,
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
        {
            'id': '9beef69a-1abc-469c-b640-e325a9bc371d',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
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
                'option1': 'Glacier Silver',
            },
            'position': 2,
            'price': '200',
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Glacier Silver',
            'weight': None,
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
        {
            'id': '9524a540-b15c-4edc-a2b3-700d34f1335a',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
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
                'option1': 'Forest Green',
            },
            'position': 3,
            'price': '300',
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Forest Green',
            'weight': None,
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
    'earliestTime': '2026-03-10T06:52:40.050Z',
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
        'id': 'cb5870cb-f05b-406c-8ef6-0f6b2c956aeb',
        'title': 'contact form purchase',
        'subtitle': 'Updates by linda',
        'formFields': [
            {
                'id': '841797f4-93b0-4796-a7ce-c523de2c8d5e',
                'title': 'hello',
                'field': 'SHORT_ANSWER',
                'required': True,
                'description': '',
                'tooltip': '',
            },
            {
                'id': '4fd172d8-34b2-4964-943b-df5296679565',
                'title': 'Phone number',
                'field': 'PHONE_NUMBER',
                'required': True,
                'description': '',
                'tooltip': '',
            },
            {
                'id': '2452bc06-d1b7-4374-a8de-58fc7c5096ef',
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
            'id': 'd73143b3-78aa-44e3-9414-8af7069f123a',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
            'height': 265,
            'width': 474,
            'position': 1,
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
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
            'id': 'fe59e6e0-678f-4cfb-ad00-5c9f4956c0ec',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
            'height': 2250,
            'width': 3397,
            'position': 2,
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
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
            'id': '1e5a900e-d2f2-4148-9c64-ebd8907c6152',
            'remote_id': None,
            'createdAt': '2026-03-10T03:53:11.833Z',
            'updatedAt': '2026-03-10T03:53:11.833Z',
            'height': 1267,
            'width': 1920,
            'position': 3,
            'productId': '2efee169-7e73-4d20-8d56-d99d7f4ab699',
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
    vars['catalog_price'] = 'newCatalogPrice'
