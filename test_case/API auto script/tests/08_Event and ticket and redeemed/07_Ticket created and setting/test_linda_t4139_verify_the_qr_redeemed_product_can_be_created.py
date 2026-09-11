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
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+01@1m.app"\n}')
    # extractor: linda01_token = $.data.token
    ctx.extract('linda01_token', _resp1, '$.data.token')
    # step: Login-merchant -> merchant_token
    _resp_m = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+00@1m.app"\n}')
    # extractor: merchant_token = $.data.token
    ctx.extract('merchant_token', _resp_m, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    # step 2: 1cf6d8c8-7d1f-4230-8166-6ae9170139d2
    _resp2 = ctx.api.products.create(body='{\r\n    "id": "898f1cff-c7ce-4a1e-81fa-8db55bb4bea4",\r\n    "remote_id": null,\r\n    "platform": "PEAR",\r\n    "createdAt": "2026-01-23T03:53:29.053Z",\r\n    "updatedAt": "2026-01-23T03:53:29.053Z",\r\n    "merchantId": "ed6b8696-1939-4511-a4d3-dcff78f34c51",\r\n    "title": "QR Redemption Product automation test",\r\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\r\n    "originalBodyHtml": "",\r\n    "isBodyHtmlOverridden": false,\r\n    "bodyText": "",\r\n    "handle": null,\r\n    "productType": "",\r\n    "publishedAt": "2026-01-23T03:53:29.047Z",\r\n    "publishedScope": "",\r\n    "status": "ACTIVE",\r\n    "externalStatus": "ACTIVE",\r\n    "followExternalStatus": false,\r\n    "tags": [],\r\n    "templateSuffix": null,\r\n    "vendor": "Pear",\r\n    "syncAt": null,\r\n    "deletedAt": null,\r\n    "delisted": false,\r\n    "excludedByImportingTag": false,\r\n    "isFeatured": false,\r\n    "featuredScore": null,\r\n    "inventoryQuantity": 100,\r\n    "inventoryQuantityOriginal": 100,\r\n    "soldQuantity": 0,\r\n    "priceDisplay": 20,\r\n    "priceDisplayAnchor": 0,\r\n    "priceMin": 20,\r\n    "priceMinAnchor": 0,\r\n    "priceMax": 20,\r\n    "priceMaxAnchor": 0,\r\n    "priceImportedMin": 0,\r\n    "priceImportedMax": 0,\r\n    "imageCount": 1,\r\n    "isUsed": "NWT",\r\n    "shippingType": "NO_SHIPPING_REQUIRED",\r\n    "additionalShippingFee": 0,\r\n    "deliveryTime": [\r\n        3,\r\n        5\r\n    ],\r\n    "returnPolicyApplied": true,\r\n    "isAvailable": true,\r\n    "commissionRate": null,\r\n    "textForShare": null,\r\n    "priceSyncImported": false,\r\n    "coverImage": {\r\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1766131678/uploaded_images/vnabt4syvxm4jecoxnae.webp",\r\n        "width": 1280,\r\n        "height": 800,\r\n        "mediaSrc": null,\r\n        "mediaType": "IMAGE",\r\n        "mediaDuration": 0\r\n    },\r\n    "reviewCount": null,\r\n    "reviewOverallScore": null,\r\n    "reviewAggregate": null,\r\n    "displayReviews": true,\r\n    "links": null,\r\n    "taxEnable": false,\r\n    "taxJarCategory": "",\r\n    "customTaxRate": null,\r\n    "subscriptionPlanId": null,\r\n    "reviewRedirectProductId": null,\r\n    "reviewSummary": null,\r\n    "customFieldsInfo": null,\r\n    "listingType": "QR_REDEMPTION",\r\n    "shippingOptions": [\r\n        {\r\n            "catalogId": "ed6b8696-1939-4511-a4d3-dcff78f34c51",\r\n            "deliveryTime": [\r\n                0,\r\n                5\r\n            ],\r\n            "enableFreeShippingThreshold": false,\r\n            "freeShippingThreshold": 0,\r\n            "shippingFee": 4.99,\r\n            "title": "Flat Shipping",\r\n            "additionalShippingFee": 0,\r\n            "enableAdditionalShippingFee": false,\r\n            "id": "eaa5d02c-63d7-4cce-b025-7d06ec39df9f",\r\n            "productId": "898f1cff-c7ce-4a1e-81fa-8db55bb4bea4",\r\n            "note": null,\r\n            "selected": true,\r\n            "isDefault": true,\r\n            "weightBasedShippingRates": null,\r\n            "enableWeightBasedShippingRates": false,\r\n            "priceBasedShippingRates": null,\r\n            "enablePriceBasedShippingRates": false,\r\n            "profileName": null,\r\n            "from": "PEAR"\r\n        }\r\n    ],\r\n    "shippingNote": "",\r\n    "autoFulfill": true,\r\n    "copyFromId": null,\r\n    "stopSellingAfter": null,\r\n    "deliveryMethod": "QR_CODE",\r\n    "thirdPartyDeliveryMessage": "",\r\n    "isMultipleDaysPassEnabled": false,\r\n    "multipleDaysPass": null,\r\n    "isPickupEtaEnabled": false,\r\n    "atDoorTicketConfig": null,\r\n    "excludeFromPostSync": false,\r\n    "expirationTime": null,\r\n    "allowAtDoorSales": false,\r\n    "options": [\r\n        {\r\n            "remote_id": null,\r\n            "productId": "898f1cff-c7ce-4a1e-81fa-8db55bb4bea4",\r\n            "name": "Title",\r\n            "position": 1,\r\n            "values": [\r\n                "Default Title"\r\n            ],\r\n            "images": [\r\n                {\r\n                    "value": "Default Title",\r\n                    "imageId": null\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "variants": [\r\n        {\r\n            "id": "80729a86-1062-436f-87c1-12bc4a84ea79",\r\n            "remote_id": null,\r\n            "createdAt": "2026-01-23T03:53:29.053Z",\r\n            "updatedAt": "2026-01-23T03:53:29.053Z",\r\n            "compareAtPrice": null,\r\n            "fulfillmentService": "manual",\r\n            "grams": 0,\r\n            "imageIds": [],\r\n            "inventoryItemId": null,\r\n            "inventoryManagement": "Pear",\r\n            "inventoryPolicy": "DENY",\r\n            "inventoryQuantity": 100,\r\n            "inventoryQuantityOriginal": 100,\r\n            "soldQuantity": 0,\r\n            "option": {\r\n                "option1": "Default Title"\r\n            },\r\n            "position": 1,\r\n            "price": "20",\r\n            "priceAnchor": "0",\r\n            "priceImported": "0.00",\r\n            "productId": "898f1cff-c7ce-4a1e-81fa-8db55bb4bea4",\r\n            "sku": "",\r\n            "taxCode": null,\r\n            "taxable": true,\r\n            "title": "Default Title",\r\n            "weight": null,\r\n            "weightUnit": null,\r\n            "platform": "PEAR",\r\n            "fees": 0,\r\n            "transactionFee": {},\r\n            "ticketPrice": 0,\r\n            "isMinPurchaseQuantityEnabled": false,\r\n            "minPurchaseQuantity": null,\r\n            "isMaxPurchaseQuantityEnabled": false,\r\n            "maxPurchaseQuantity": null,\r\n            "isPackSizeEnabled": false,\r\n            "packSize": null\r\n        }\r\n    ],\r\n    "catalogCommissionRate": 25,\r\n    "isReturnPolicyAllowed": true,\r\n    "earliestTime": "2026-04-15T03:54:18.391Z",\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#ECA416FF",\r\n            "#B7E2E0FF",\r\n            "#757575FF",\r\n            "#FFFFFFFF",\r\n            "#110921FF",\r\n            "#FFCDD2FF",\r\n            "#CB135BFF",\r\n            "#FF9800",\r\n            "#1B5E20",\r\n            "#FFF59D",\r\n            "#F57C00",\r\n            "#7986CBFF",\r\n            "#FFEEBEFF",\r\n            "#7132F4FF",\r\n            "#616161FF",\r\n            "#0B99FFFF",\r\n            "#E0E0E0FF"\r\n        ]\r\n    },\r\n    "isProductFormEnabled": false,\r\n    "isVariantPriceDisplayEnabled": false,\r\n    "stopSellingAfterDisplay": "",\r\n    "extraInfo": {\r\n        "businessName": "Business Name 001",\r\n        "businessHours": "Monday - Friday, 10:00 AM",\r\n        "businessAddress": "123 Main St, Austin, TX  456 Main St, Austin, TX",\r\n        "businessTimezone": "America/Chicago"\r\n    },\r\n    "overrideEventTax": false,\r\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\r\n    "images": [\r\n        {\r\n            "id": "28d50d43-836e-4598-ae92-190dcbcc61e9",\r\n            "remote_id": null,\r\n            "createdAt": "2026-01-23T03:53:29.053Z",\r\n            "updatedAt": "2026-01-23T03:53:29.053Z",\r\n            "height": 800,\r\n            "width": 1280,\r\n            "position": 1,\r\n            "productId": "898f1cff-c7ce-4a1e-81fa-8db55bb4bea4",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1766131678/uploaded_images/vnabt4syvxm4jecoxnae.webp",\r\n            "variantIds": [],\r\n            "mediaType": "IMAGE",\r\n            "mediaSrc": null,\r\n            "mediaDuration": 0,\r\n            "contributedBy": 3,\r\n            "contributorId": null,\r\n            "productImageType": "PRODUCT",\r\n            "source": "UPLOAD"\r\n        }\r\n    ]\r\n}', token='linda01_token')
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
