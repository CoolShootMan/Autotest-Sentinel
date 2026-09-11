"""Migrated from Apifox case #8601276. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8601276  (traceability only — not needed to run)
NAME = "Verify the Additional QR codes can be added/edited/deleted"
TAGS = ["p1", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:linda"]
PRIORITY = 1


CASE_ID = 8601276
ENV_NAME = "Release"

# --- step 1: 0103bf67-b8eb-4911-987e-f6529dccff3a ---
# post[extractor]: {"variableName": "yuxiao999_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: ee5d6ffb-b19f-49ea-96b5-58086027e448 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 在 items 数组中查找 title 为 "event-for-API-testing" 的事件
# post: const targetEvent = responseData.data.items.find(
# post:     item => item.title === "event-for-API-testing"
# post: );
# post: 
# post: // 3. 断言并设置环境变量 event_id
# post: pm.test("找到 title 为 'event-for-API-testing' 的事件并提取 id 设置为 event_id", function () {
# post:     // 断言找到目标事件
# post:     pm.expect(targetEvent, "未找到 title 为 'event-for-API-testing' 的事件").to.not.be.undefined;
# post:     pm.expect(targetEvent.id, "提取的 id 为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 获取并设置环境变量
# post:     const eventId = targetEvent.id;
# post:     pm.environment.set("event_id", eventId);
# post:     
# post:     console.log("已成功提取 event_id:", eventId);
# post: });
# --- step 3: d969467d-4e41-4f7d-9cd8-939c23b20f16 ---
# post[customScript]: // 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 查找 title 为 'event-for-API-testing' 的项
# post: const targetItem = responseData.data.items.find(
# post:     item => item.title === "event-for-API-testing"
# post: );
# post: 
# post: if (targetItem) {
# post:     // 设置环境变量 postId
# post:     pm.environment.set("postId", targetItem.id);
# post:     console.log("成功提取 postId:", targetItem.id);
# post: } else {
# post:     console.error("未找到匹配的 item");
# post: }
# --- step 4: 1d147e0c-10eb-4542-b1ba-9e08f1b76835 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 断言并设置环境变量 catalog_id
# post: pm.test("成功提取 data.id 并设置为环境变量 catalog_id", function () {
# post:     // 校验 data 及其 id 字段存在
# post:     pm.expect(responseData.data).to.be.an('object').that.is.not.null;
# post:     pm.expect(responseData.data.id, "data.id 为空或不存在").to.be.a('string').and.not.empty;
# post: 
# post:     // 获取并保存环境变量
# post:     const catalogId = responseData.data.id;
# post:     pm.environment.set("catalog_id", catalogId);
# post: 
# post:     console.log("已成功提取 catalog_id:", catalogId);
# post: });
# --- step 5: 5fe163d3-20f8-4e95-8a9f-895ac97b9b5d ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础断言
# post: pm.test("HTTP Status Code 201", function () {
# post:     pm.response.to.have.status(201);
# post: });
# post: 
# post: pm.test("Response code is 200 and message is success", function () {
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post:     pm.expect(responseData.data.id).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 3. 提取 data.id 并设置环境变量 productId
# post: if (responseData.data && responseData.data.id) {
# post:     pm.environment.set("productId", responseData.data.id);
# post:     console.log("设置环境变量 productId:", responseData.data.id);
# post: }
# post: 
# post: // 4. 依次提取 inclusions.name 数组并存为环境变量或输出
# post: if (responseData.data && Array.isArray(responseData.data.inclusions)) {
# post:     // 提取所有 name 组合成数组
# post:     const inclusionNames = responseData.data.inclusions.map(item => item.name);
# post:     
# post:     // 设置包含所有名称的数组到环境变量
# post:     pm.environment.set("inclusionNames", JSON.stringify(inclusionNames));
# post:     
# post:     // 依次设置单独的环境变量（如: inclusion_0, inclusion_1...）
# post:     responseData.data.inclusions.forEach((item, index) => {
# post:         pm.environment.set(`inclusion_${index}`, item.name);
# post:         console.log(`提取 inclusion [${index}]:`, item.name);
# post:     });
# post: }
# --- step 6: 4e2f6aa1-7162-41a8-a8f4-c70a4a555480 ---
# --- step 7: 6451f010-096a-49fe-af64-106701bd8a2e ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 查找 title 为 "autotest T5379" 的产品
# post: const targetProduct = responseData.data.relatedProducts.find(
# post:     item => item.title === "autotest T5379"
# post: );
# post: 
# post: // 3. 断言并提取 displayVariantId 为环境变量 promoterProductId
# post: pm.test("找到目标产品并提取 displayVariantId 作为 promoterProductId", function () {
# post:     // 断言目标产品存在
# post:     // pm.expect(targetProduct).to.not.be.undefined;
# post:     pm.expect(targetProduct.displayVariantId).to.be.a('string').and.not.empty;
# post: 
# post:     // 获取 displayVariantId
# post:     const targetVariantId = targetProduct.displayVariantId;
# post: 
# post:     // 设置为环境变量 promoterProductId
# post:     pm.environment.set("promoterProductId", targetVariantId);
# post:     console.log("已成功将 displayVariantId 设置为 promoterProductId:", targetVariantId);
# post: });
# --- step 8: get address list ---
# post[customScript]: // 1. 获取接口返回的JSON数据
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 初始化地址ID变量（默认空值）
# post: let addressId = "";
# post: 
# post: // 3. 提取有效ID（优先默认地址，无则取第一个）
# post: if (responseData.data && responseData.data.items && responseData.data.items.length > 0) {
# post:     // 先找isDefault=true的默认地址
# post:     const defaultAddress = responseData.data.items.find(item => item.isDefault === true);
# post:     if (defaultAddress) {
# post:         addressId = defaultAddress.id;
# post:     } else {
# post:         // 无默认地址则取第一个地址的ID
# post:         addressId = responseData.data.items[0].id;
# post:     }
# post: }
# post: 
# post: // 4. 存入APIFOX全局变量（供下单接口引用）
# post: pm.globals.set("addressId", addressId)
# post: 
# post: // 【可选】打印日志验证（APIFOX控制台查看）
# post: console.log("提取的有效地址ID：", addressId);
# --- step 9: e5273105-dae8-4673-864f-18a9ab8aa4ef ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: buy now ---
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: place order and check Inclusions content exist ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应断言
# post: pm.test("响应状态码为 201 且 message 为 success", function () {
# post:     pm.response.to.have.status(201);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post: });
# post: 
# post: // 3. 提取 orderNumbers[0] 并设置为环境变量 order_number
# post: pm.test("提取 orderNumbers[0] 并设置为环境变量 order_number", function () {
# post:     const orderNumbers = responseData.data?.orderNumbers;
# post:     
# post:     // 校验 orderNumbers 数组存在且不为空
# post:     pm.expect(orderNumbers, "orderNumbers 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post:     pm.expect(orderNumbers[0], "orderNumbers[0] 值为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 设置环境变量
# post:     const orderNumber = orderNumbers[0];
# post:     pm.environment.set("order_number", orderNumber);
# post: 
# post:     console.log("已成功提取 order_number:", orderNumber);
# post: });
# post: 
# post: // 4. 断言 orderInclusions 存在并匹配预期的 inclusionNames
# post: pm.test("验证 orderInclusions 数据结构及与预期的 inclusionNames 匹配", function () {
# post:     // 从环境变量中获取之前保存的预期 names 数组
# post:     const expectedInclusionNames = JSON.parse(pm.environment.get("inclusionNames") || "[]");
# post:     
# post:     // 定位 lineItems -> orderLineItemUnits
# post:     const lineItems = responseData.data?.confirmation?.lineItems;
# post:     pm.expect(lineItems).to.be.an('array').that.is.not.empty;
# post: 
# post:     const units = lineItems[0]?.orderLineItemUnits;
# post:     pm.expect(units).to.be.an('array').that.is.not.empty;
# post: 
# post:     // 获取实际的 orderInclusions 数组
# post:     const actualInclusions = units[0]?.orderInclusions;
# post:     pm.expect(actualInclusions).to.be.an('array').that.is.not.empty;
# post: 
# post:     // 逐项断言基础属性完整性 (id, name, numberCode, status)
# post:     actualInclusions.forEach((item, index) => {
# post:         pm.expect(item.id, `第 ${index} 项缺少 id`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.name, `第 ${index} 项缺少 name`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.numberCode, `第 ${index} 项缺少 numberCode`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.status, `第 ${index} 项 status 不正确`).to.eql("IN_PROCESSING");
# post:     });
# post: 
# post:     // 提取实际的 name 列表
# post:     const actualNames = actualInclusions.map(item => item.name);
# post: 
# post:     // 断言实际提取的 names 与上一步存储的环境变量完全一致
# post:     if (expectedInclusionNames.length > 0) {
# post:         pm.expect(actualNames).to.eql(expectedInclusionNames);
# post:         console.log("Inclusions 匹配成功！实际值:", actualNames);
# post:     } else {
# post:         console.warn("环境变量 inclusionNames 为空，仅验证了实际返回的数据格式。");
# post:     }
# post: });
# --- step 12: Check the merchant order detail and Inclusions content exist ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应断言
# post: pm.test("响应状态码为 200 且 message 为 success", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message, "message 返回不正确").to.eql("success");
# post: });
# post: 
# post: // 3. 提取 orderNumber 并设置为环境变量 order_number
# post: pm.test("提取 orderNumber 并设置为环境变量 order_number", function () {
# post:     const orderNumber = responseData.data?.orderNumber;
# post:     
# post:     // 校验 orderNumber 存在且为非空字符串
# post:     pm.expect(orderNumber, "orderNumber 值为空或不存在").to.be.a('string').and.not.empty;
# post: 
# post:     // 设置环境变量
# post:     pm.environment.set("order_number", orderNumber);
# post: 
# post:     console.log("已成功提取 order_number:", orderNumber);
# post: });
# post: 
# post: // 4. 断言 orderInclusions 存在并匹配预期的 inclusionNames
# post: pm.test("验证 orderInclusions 数据结构及与预期的 inclusionNames 匹配", function () {
# post:     // 从环境变量中获取之前保存的预期 names 数组
# post:     const expectedInclusionNames = JSON.parse(pm.environment.get("inclusionNames") || "[]");
# post:     
# post:     // 定位 lineItems -> orderLineItemUnits
# post:     const lineItems = responseData.data?.lineItems;
# post:     pm.expect(lineItems, "lineItems 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     const units = lineItems[0]?.orderLineItemUnits;
# post:     pm.expect(units, "orderLineItemUnits 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 获取实际的 orderInclusions 数组
# post:     const actualInclusions = units[0]?.orderInclusions;
# post:     pm.expect(actualInclusions, "orderInclusions 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 逐项断言基础属性完整性 (id, name, numberCode, status)
# post:     actualInclusions.forEach((item, index) => {
# post:         pm.expect(item.id, `第 ${index} 项缺少 id`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.name, `第 ${index} 项缺少 name`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.numberCode, `第 ${index} 项缺少 numberCode`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.status, `第 ${index} 项 status 不正确`).to.eql("IN_PROCESSING");
# post:     });
# post: 
# post:     // 提取实际的 name 列表
# post:     const actualNames = actualInclusions.map(item => item.name);
# post: 
# post:     // 断言实际提取的 names 与上一步存储的环境变量完全一致
# post:     if (expectedInclusionNames.length > 0) {
# post:         pm.expect(actualNames).to.eql(expectedInclusionNames);
# post:         console.log("Inclusions 匹配成功！实际值:", actualNames);
# post:     } else {
# post:         console.warn("环境变量 inclusionNames 为空，仅验证了实际返回的数据格式。");
# post:     }
# post: });




from core.assertions import expect

def test_linda_t5379_verify_the_additional_qr_codes_can_be_added_edited_deleted(ctx):
    from core.compat import get_path as _get_path
    """Apifox case #8601276: Linda_T5379_Verify_the_Additional_QR_codes_can_be_added_edited_deleted"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 0103bf67-b8eb-4911-987e-f6529dccff3a
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{UIauto_partner_email}}",\r\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\r\n\r\n}', app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    ctx.extract('yuxiao999_token', _resp1, '$.data.token')
    # step 2: ee5d6ffb-b19f-49ea-96b5-58086027e448
    _resp2 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    vars['event_id'] = 'eventId'
    # step 3: d969467d-4e41-4f7d-9cd8-939c23b20f16
    _resp3 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    vars['postId'] = 'targetItem.id'
    # step 4: 1d147e0c-10eb-4542-b1ba-9e08f1b76835
    _resp4 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    vars['catalog_id'] = 'catalogId'
    # step 5: 5fe163d3-20f8-4e95-8a9f-895ac97b9b5d
    _resp5 = ctx.api.products.create(body='{\n    "merchantId": "{{catalog_id}}",\n    "shippingType": "NO_SHIPPING_REQUIRED",\n    "isFeatured": false,\n    "commissionRate": 10,\n    "priceSyncImported": false,\n    "additionalShippingFee": 0,\n    "returnPolicyApplied": true,\n    "title": "autotest T5379",\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n    "status": "ACTIVE",\n    "isUsed": "NWT",\n    "taxJarCategory": "",\n    "platform": "PEAR",\n    "autoFulfill": true,\n    "options": [\n        {\n            "name": "Title",\n            "values": [\n                "Default Title"\n            ],\n            "images": []\n        }\n    ],\n    "variants": [\n        {\n            "inventoryQuantity": 99999,\n            "price": 0,\n            "priceAnchor": 0,\n            "option": {\n                "option1": "Default Title"\n            },\n            "fees": 0,\n            "ticketPrice": 0,\n            "transactionFee": {\n                "platformFee": 0,\n                "customFee": 0,\n                "customFeeBreakdown": {},\n                "transactionItemFee": 0\n            },\n            "minPriceForCheckFees": 0,\n            "weightUnit": "lb",\n            "isInventoryQuantityUnlimited": true\n        }\n    ],\n    "listingType": "TICKET",\n    "ticketType": "TICKET_TYPE_STANDARD",\n    "soldQuantity": 0,\n    "excludeFromPostSync": false,\n    "isTipEnabled": false,\n    "useEventPosterAsCover": true,\n    "catalogCommissionRate": 10,\n    // "shippingOptions": [\n    //     {\n    //         "id": "1cfa21d1-3512-462f-8e8c-339e4875b353",\n    //         "catalogId": "{{catalog_id}}",\n    //         "title": "Flat Shipping",\n    //         "shippingFee": 4.99,\n    //         "deliveryTime": [\n    //             0,\n    //             5\n    //         ],\n    //         "enableFreeShippingThreshold": false,\n    //         "freeShippingThreshold": 0,\n    //         "note": null,\n    //         "isDefault": true,\n    //         "weightBasedShippingRates": null,\n    //         "enableWeightBasedShippingRates": false,\n    //         "priceBasedShippingRates": null,\n    //         "enablePriceBasedShippingRates": false,\n    //         "profileName": null,\n    //         "from": "PEAR",\n    //         "additionalShippingFee": 0,\n    //         "enableAdditionalShippingFee": false\n    //     }\n    // ],\n    "deliveryMethod": "QR_CODE",\n    "thirdPartyDeliveryMessage": "",\n    "taxEnable": false,\n    "customTaxRate": null,\n    "earliestTime": "2026-08-07T06:13:32.412Z",\n    "styleSettings": {\n        "recentUsedColors": [\n            "#F2F2F6FF",\n            "#FFFFFF"\n        ]\n    },\n    "isInclusionsEnabled": true,\n    "inclusions": [\n        {\n            "name": "additional QR codes 001",\n            "position": 0\n        },\n        {\n            "name": "additional QR codes 002",\n            "position": 1\n        },\n        {\n            "name": "additional QR codes 003",\n            "position": 2\n        },\n        {\n            "name": "additional QR codes 004",\n            "position": 3\n        },\n        {\n            "name": "additional QR codes 005",\n            "position": 4\n        }\n    ],\n    "isVariantPriceDisplayEnabled": false,\n    "stopSellingAfterDisplay": "",\n    "extraInfo": {\n        "businessTimezone": "America/Los_Angeles"\n    },\n    "overrideEventTax": false,\n    "overrideEventCustomFee": false,\n    "hideFees": false,\n    "transactionCustomFeeConfig": null,\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n    "images": [\n        {\n            "height": 1672,\n            "mediaDuration": 0,\n            "mediaType": "IMAGE",\n            "position": 0,\n            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1784274442/uploaded_images/xh2nwr2ovgeiuxe5yptf.jpg",\n            "width": 941\n        }\n    ],\n    "eventId": "{{event_id}}",\n    "isExpirationEnabled": false\n}', token='yuxiao999_token')
    ctx.extract('productId', _resp5, '$.data.id')
    vars['inclusionNames'] = 'JSON.stringify(inclusionNames'
    # step 6: 4e2f6aa1-7162-41a8-a8f4-c70a4a555480
    _resp6 = ctx.api.events.v2_show_in_post(body='{\n    "productIds": [\n        "{{productId}}"\n    ],\n    "posts": [\n        {\n            "postId": "{{postId}}",\n            "isVisible": true\n        }\n    ]\n}', token='yuxiao999_token')
    # step 7: 6451f010-096a-49fe-af64-106701bd8a2e
    _resp7 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token', path_vars={'post0_id': '{{postId}}'})
    vars['promoterProductId'] = 'targetVariantId'
    # step 8: get address list
    _resp8 = ctx.api.address.list(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    # step 9: e5273105-dae8-4673-864f-18a9ab8aa4ef
    _resp9 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 9.assertion: responseJson equal 200
    expect(_resp9).json('$.code').equals('200')
    # assertion 9.assertion: responseJson equal success
    expect(_resp9).json('$.message').equals('success')
    # step 10: buy now
    _resp10 = ctx.api.orders.buy_now(body='{\n  "postIdForFilter": "{{postId}}",\n  "updateCartItems": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "{{promoterProductId}}",\n      "price": 2,\n      "postId": "{{postId}}",\n      "selected": true,\n      "customFields": []\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "{{event_id}}",\n    "pixelId": [\n      "test"\n    ],\n    "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n    "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n    "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 1,\n      "id": "{{productId}}",\n      "postId": "{{postId}}",\n      "price": 2,\n      "customFields": []\n    }\n  ]\n}', app_headers=True, token='linda10_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp10, '$.data.orderId')
    # step 11: place order and check Inclusions content exist
    _resp11 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "linda.zhou.ext+10@1m.app"\n    },\n    "shippingAddressId": "{{shippingAddressId}}",\n    // "paymentInfo": {\n    //     "paymentMethodId": "{{pay_method_id}}"\n    // },\n    "fbAdParams": {\n        "eventID": "58e159af-0e82-4244-b86d-00f37277e6a0",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=ff6bbfb6-7146-44d9-985b-26eefbf740e3"\n    }\n}', app_headers=True, token='linda10_token')
    _ordernumber_val = _get_path(_resp9.json(), ['data', 'orderNumbers', 0])
    vars['order_number'] = _ordernumber_val if _ordernumber_val is not None else ''
    # step 12: Check the merchant order detail and Inclusions content exist
    _resp12 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='yuxiao999_token', path_vars={'merchantId': '{{catalog_id}}', 'orderNumber': '{{order_number}}'}, params={'catalogId': '9bd92082-07cd-4af5-8407-710d5f352a93', 'orderNumber': '{{orderNumber}}'})
