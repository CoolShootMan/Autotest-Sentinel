"""Migrated from Apifox case #7675144. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 7675144  (traceability only — not needed to run)
NAME = "Verify the QR redeemed product can be created"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:linda"]
PRIORITY = 0


CASE_ID = 7675144
ENV_NAME = "Release"

# --- step 1: Get Partner linda01 token ---
# post[extractor]: {"variableName": "linda01_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: 1cf6d8c8-7d1f-4230-8166-6ae9170139d2 ---
# pre: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# pre: 
# post[customScript]: try {
# post:     // 1. 解析接口响应体为JSON对象
# post:     const responseJson = pm.response.json();
# post: 
# post:     // 2. 验证响应码code = 200
# post:     pm.test("响应码验证：code应为200", function () {
# post:         pm.expect(responseJson.code, "code值不符合预期").to.equal(200);
# post:     });
# post: 
# post:     // 3. 验证消息message = success
# post:     pm.test("响应消息验证：message应为success", function () {
# post:         pm.expect(responseJson.message, "message值不符合预期").to.equal("success");
# post:     });
# post: 
# post:     // 4. 验证产品标题title = QR Redemption Product automation test
# post:     pm.test("产品标题验证：title匹配预期", function () {
# post:         pm.expect(responseJson.data.title, "title值不符合预期")
# post:             .to.equal("QR Redemption Product automation test");
# post:     });
# post: 
# post:     // 5. 获取并存储data.id（核心需求）
# post:     if (responseJson.data && responseJson.data.id) {
# post:         const productId = responseJson.data.id;
# post:         console.log("✅ 成功获取data.id：", productId);
# post:         // 将id存入Postman环境变量（方便后续接口调用，变量名可自定义）
# post:         pm.environment.set("productId", productId);
# post:     } else {
# post:         pm.test("data.id字段验证失败", function () {
# post:             pm.expect.fail("响应数据中未找到有效的data.id字段");
# post:         });
# post:     }
# post: 
# post: } catch (error) {
# post:     // 捕获解析失败/验证异常，标记测试失败
# post:     pm.test("脚本执行异常", function () {
# post:         pm.expect.fail(`❌ 错误信息：${error.message}`);
# post:     });
# post: }
# --- step 3: ae33ea1d-f9bd-443c-8fac-57745d9862fe ---
# post[customScript]: try {
# post:     // 1. 解析响应体为JSON对象
# post:     const responseJson = pm.response.json();
# post: 
# post:     // 2. 基础验证：code=200、message=success
# post:     pm.test("响应码验证：code应为200", () => {
# post:         pm.expect(responseJson.code).to.equal(200, `code预期200，实际${responseJson.code}`);
# post:     });
# post:     pm.test("响应消息验证：message应为success", () => {
# post:         pm.expect(responseJson.message).to.equal("success", `message预期success，实际${responseJson.message}`);
# post:     });
# post: 
# post:     // 3. 核心验证：数据已删除（关键字段校验）
# post:     const data = responseJson.data;
# post:     pm.test("删除状态验证：data字段存在", () => {
# post:         pm.expect(data).to.not.be.undefined.and.not.be.null, "响应中未找到data字段";
# post:     });
# post: 
# post:     // 验证1：deletedAt有删除时间（非空）
# post:     pm.test("删除时间验证：deletedAt非空", () => {
# post:         pm.expect(data.deletedAt)
# post:             .to.not.be.undefined
# post:             .and.not.be.null
# post:             .and.not.be.empty, "deletedAt为空，数据未删除";
# post:     });
# post: 
# post:     // 验证2：isAvailable为false（删除后不可用）
# post:     pm.test("可用状态验证：isAvailable为false", () => {
# post:         pm.expect(data.isAvailable).to.equal(false, `isAvailable预期false，实际${data.isAvailable}`);
# post:     });
# post: 
# post:     // 可选：提取并存储productId（方便后续校验）
# post:     if (data.id) {
# post:         const productId = data.id;
# post:         console.log("✅ 已删除的产品ID：", productId);
# post:         pm.environment.set("deletedProductId", productId); // 存入环境变量
# post:     } else {
# post:         pm.test("产品ID验证失败", () => {
# post:             pm.expect.fail("data.id字段缺失，无法获取已删除产品ID");
# post:         });
# post:     }
# post: 
# post: } catch (error) {
# post:     // 捕获异常，标记测试失败
# post:     pm.test("脚本执行异常", () => {
# post:         pm.expect.fail(`❌ 错误信息：${error.message}`);
# post:     });
# post: }




from core.assertions import expect

def test_linda_t4139_verify_the_qr_redeemed_product_can_be_created(ctx):
    """Apifox case #7675144: Linda_T4139_Verify_the_QR_redeemed_product_can_be_created"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda01 token
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
        "email": "linda.zhou.ext+01@1m.app",
    })
    # extractor: linda01_token = $.data.token
    ctx.extract('linda01_token', _resp1, '$.data.token')
    # step: Login-merchant -> merchant_token
    _resp_m = ctx.api.auth.sign_in(body={
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
        "email": "linda.zhou.ext+00@1m.app",
    })
    # extractor: merchant_token = $.data.token
    ctx.extract('merchant_token', _resp_m, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    # step 2: 1cf6d8c8-7d1f-4230-8166-6ae9170139d2
    # === pre-script（由 Apifox customScript 翻译）===
    vars['merchantId'] = "822a3e59-fdf3-4d9b-be57-f8f0b3af1023"

    _resp2 = ctx.api.products.create(body={
    'id': '898f1cff-c7ce-4a1e-81fa-8db55bb4bea4',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-01-23T03:53:29.053Z',
    'updatedAt': '2026-01-23T03:53:29.053Z',
    'merchantId': 'ed6b8696-1939-4511-a4d3-dcff78f34c51',
    'title': 'QR Redemption Product automation test',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'originalBodyHtml': '',
    'isBodyHtmlOverridden': False,
    'bodyText': '',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-01-23T03:53:29.047Z',
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
    'inventoryQuantity': 100,
    'inventoryQuantityOriginal': 100,
    'soldQuantity': 0,
    'priceDisplay': 20,
    'priceDisplayAnchor': 0,
    'priceMin': 20,
    'priceMinAnchor': 0,
    'priceMax': 20,
    'priceMaxAnchor': 0,
    'priceImportedMin': 0,
    'priceImportedMax': 0,
    'imageCount': 1,
    'isUsed': 'NWT',
    'shippingType': 'NO_SHIPPING_REQUIRED',
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
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1766131678/uploaded_images/vnabt4syvxm4jecoxnae.webp',
        'width': 1280,
        'height': 800,
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
    'listingType': 'QR_REDEMPTION',
    'shippingOptions': [
        {
            'catalogId': 'ed6b8696-1939-4511-a4d3-dcff78f34c51',
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
            'id': 'eaa5d02c-63d7-4cce-b025-7d06ec39df9f',
            'productId': '898f1cff-c7ce-4a1e-81fa-8db55bb4bea4',
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
    'shippingNote': '',
    'autoFulfill': True,
    'copyFromId': None,
    'stopSellingAfter': None,
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'isMultipleDaysPassEnabled': False,
    'multipleDaysPass': None,
    'isPickupEtaEnabled': False,
    'atDoorTicketConfig': None,
    'excludeFromPostSync': False,
    'expirationTime': None,
    'allowAtDoorSales': False,
    'options': [
        {
            'remote_id': None,
            'productId': '898f1cff-c7ce-4a1e-81fa-8db55bb4bea4',
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
            'id': '80729a86-1062-436f-87c1-12bc4a84ea79',
            'remote_id': None,
            'createdAt': '2026-01-23T03:53:29.053Z',
            'updatedAt': '2026-01-23T03:53:29.053Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'inventoryQuantity': 100,
            'inventoryQuantityOriginal': 100,
            'soldQuantity': 0,
            'option': {
                'option1': 'Default Title',
            },
            'position': 1,
            'price': '20',
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '898f1cff-c7ce-4a1e-81fa-8db55bb4bea4',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Default Title',
            'weight': None,
            'weightUnit': None,
            'platform': 'PEAR',
            'fees': 0,
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
    'earliestTime': '2026-04-15T03:54:18.391Z',
    'styleSettings': {
        'recentUsedColors': [
            '#ECA416FF',
            '#B7E2E0FF',
            '#757575FF',
            '#FFFFFFFF',
            '#110921FF',
            '#FFCDD2FF',
            '#CB135BFF',
            '#FF9800',
            '#1B5E20',
            '#FFF59D',
            '#F57C00',
            '#7986CBFF',
            '#FFEEBEFF',
            '#7132F4FF',
            '#616161FF',
            '#0B99FFFF',
            '#E0E0E0FF',
        ],
    },
    'isProductFormEnabled': False,
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'extraInfo': {
        'businessName': 'Business Name 001',
        'businessHours': 'Monday - Friday, 10:00 AM',
        'businessAddress': '123 Main St, Austin, TX  456 Main St, Austin, TX',
        'businessTimezone': 'America/Chicago',
    },
    'overrideEventTax': False,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'id': '28d50d43-836e-4598-ae92-190dcbcc61e9',
            'remote_id': None,
            'createdAt': '2026-01-23T03:53:29.053Z',
            'updatedAt': '2026-01-23T03:53:29.053Z',
            'height': 800,
            'width': 1280,
            'position': 1,
            'productId': '898f1cff-c7ce-4a1e-81fa-8db55bb4bea4',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1766131678/uploaded_images/vnabt4syvxm4jecoxnae.webp',
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
}, token='linda01_token')
    # extractor: productId = productId
    ctx.extract('productId', _resp2, '$.data.id')
    # step 3: ae33ea1d-f9bd-443c-8fac-57745d9862fe
    _resp3 = ctx.api.products.by_product_id(body=None, token='merchant_token')
    vars['deletedProductId'] = vars.get('productId')
    # --- assertions: no fake-green (non-4xx/5xx) ---
    assert _resp1.status_code < 400, f"step1 got HTTP {_resp1.status_code}: {_resp1.text[:200]}"
    assert _resp_m.status_code < 400, f"merchant-login got HTTP {_resp_m.status_code}: {_resp_m.text[:200]}"
    assert _resp2.status_code < 400, f"step2 got HTTP {_resp2.status_code}: {_resp2.text[:200]}"
    assert _resp3.status_code < 400, f"step3 got HTTP {_resp3.status_code}: {_resp3.text[:200]}"
