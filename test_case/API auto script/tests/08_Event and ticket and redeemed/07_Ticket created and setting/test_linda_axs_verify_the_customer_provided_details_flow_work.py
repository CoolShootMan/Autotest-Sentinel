"""Auto-generated from Apifox case #8706050. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 8706050
# Folder: 
# Case: (Linda)(AXS) Verify the Customer-provided details flow work
# Priority: P0
# Created: 2026-09-04T07:10:30.000Z
# Updated: 2026-09-04T08:10:07.000Z


CASE_ID = 8706050
ENV_NAME = "Release"

# --- step 1: f25b1efc-89d7-45ce-970f-da05a0ac3925 ---
# post[extractor]: {"variableName": "yuxiao999_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 66d5d716-3a02-4b8c-a925-0485796bcb40 ---
# post[customScript]: // 1. 解析响应 Body
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 查找第一个 platform 为 "AXS" 的项目
# post: const axsEvent = responseData.data.items.find(item => item.platform === "AXS");
# post: 
# post: if (axsEvent) {
# post:     // 3. 设置环境变量
# post:     pm.environment.set("event_id", axsEvent.id);
# post:     pm.environment.set("event_title", axsEvent.title);
# post: 
# post:     console.log("成功提取第一个 AXS 项目：", axsEvent.title, axsEvent.id);
# post: } else {
# post:     console.warn("未找到 platform 为 AXS 的数据");
# post: }
# --- step 3: c10ed67d-5174-4977-9f37-b1a977fddbb2 ---
# post[customScript]: // 1. 解析响应体为 JSON 对象
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 从 data.items 数组中提取第一个元素的 id
# post: // 使用可选链 (?.) 确保在数据结构异常时不会报错
# post: const postId = responseData.data?.items[0]?.id;
# post: 
# post: // 3. 校验提取到的 ID 是否存在
# post: if (postId) {
# post:     // 4. 将提取到的 ID 设置为环境变量 post0_id
# post:     pm.environment.set("post0_id", postId);
# post:     
# post:     // 打印日志方便调试
# post:     console.log("成功提取 post0_id:", postId);
# post: } else {
# post:     console.error("未能从响应中提取到 items[0].id");
# post: }
# post: 
# post: // 5. (可选) 添加一个简单的断言校验
# post: pm.test("成功提取并设置环境变量 post0_id", function () {
# post:     pm.expect(postId).to.be.a('string').and.not.empty;
# post: });
# --- step 4: 3a42a638-1733-468e-8343-378e4a35997f ---
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
# --- step 5: 335db91f-b619-4cb9-9bf3-799455463f16 ---
# post[customScript]: // 1. 解析响应数据
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 状态码与数据合法性校验
# post: pm.test("响应状态为 200 且包含有效的 relatedProducts", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.data?.relatedProducts).to.be.an('array').that.is.not.empty;
# post: });
# post: 
# post: // 3. 过滤 inventoryQuantity > 0 且存在有效 ID 的第一个产品
# post: const products = responseData.data?.relatedProducts || [];
# post: 
# post: const validProduct = products.find(product => {
# post:     // 优先取 variants[0] 中的库存，无则取 product 外层库存
# post:     const inventory = product.variants?.[0]?.inventoryQuantity ?? product.inventoryQuantity;
# post:     return inventory > 0;
# post: });
# post: 
# post: if (validProduct) {
# post:     // 1. 提取 title
# post:     const ticketTitle = validProduct.title?.trim() || "";
# post:     
# post:     // 2. 提取 productId
# post:     const productId = validProduct.merchantProductId || validProduct.shippingView?.productId || "";
# post:     
# post:     // 3. 提取 promoterProductId
# post:     const promoterProductId = validProduct.promoterProductId || "";
# post:     
# post:     // 4. 提取 merchantProductVariantId
# post:     const merchantProductVariantId = validProduct.variants?.[0]?.merchantProductVariantId || "";
# post:     
# post:     // 5. 提取 displayVariantId
# post:     const displayVariantId = validProduct.variants?.[0]?.displayVariantId || validProduct.displayVariantId || "";
# post: 
# post:     // 6. 提取 ticketHubInfo_id
# post:     const ticketHubInfo_id = validProduct.extraInfo?.ticketHubInfo?.ticketHandle || "";
# post: 
# post:     // 7. 提取 ticketHandle
# post:     const ticketHandle = validProduct.extraInfo?.ticketHubInfo?.sectionOptions?.[0]?.ticketHandle || "";
# post: 
# post:     // 8. 提取 availableQuantity (确保为数字类型)
# post:     const rawQuantity = validProduct.extraInfo?.ticketHubInfo?.sectionOptions?.[0]?.availableQuantity;
# post:     const availableQuantity = typeof rawQuantity === 'number' ? rawQuantity : Number(rawQuantity) || 0;
# post: 
# post:     // 9. 新增：提取 label 为 sectionIds 环境变量
# post:     const sectionIds = validProduct.extraInfo?.ticketHubInfo?.sectionOptions?.[0]?.label || "";
# post: 
# post:     // 统一设置环境变量
# post:     pm.environment.set("ticket_title", ticketTitle);
# post:     pm.environment.set("productId", productId);
# post:     pm.environment.set("promoterProductId", promoterProductId);
# post:     pm.environment.set("merchantProductVariantId", merchantProductVariantId);
# post:     pm.environment.set("displayVariantId", displayVariantId);
# post:     pm.environment.set("ticketHubInfo_id", ticketHubInfo_id);
# post:     pm.environment.set("ticketHandle", ticketHandle);
# post:     pm.environment.set("availableQuantity", availableQuantity);
# post:     pm.environment.set("sectionIds", sectionIds);
# post: 
# post:     // 打印日志
# post:     console.log(`[提取成功] 命中首个库存 > 0 的产品: ${ticketTitle}`);
# post:     console.log(`  - ticket_title: ${ticketTitle}`);
# post:     console.log(`  - productId: ${productId}`);
# post:     console.log(`  - promoterProductId: ${promoterProductId}`);
# post:     console.log(`  - merchantProductVariantId: ${merchantProductVariantId}`);
# post:     console.log(`  - displayVariantId: ${displayVariantId}`);
# post:     console.log(`  - ticketHubInfo_id: ${ticketHubInfo_id}`);
# post:     console.log(`  - ticketHandle: ${ticketHandle}`);
# post:     console.log(`  - availableQuantity:`, availableQuantity);
# post:     console.log(`  - sectionIds: ${sectionIds}`);
# post: } else {
# post:     console.warn("[提取失败] 列表中未找到 inventoryQuantity > 0 的产品");
# post: }
# --- step 6: 7a6d4176-bb6b-499b-9cc7-b7e7ba3ce08b ---
# post[customScript]: // 1. 解析响应 Body 为 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 校验响应状态码为 200 且 isProductFormEnabled 为 true
# post: pm.test("校验 isProductFormEnabled 状态为 true", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.data?.isProductFormEnabled).to.be.true;
# post: });
# --- step 8: Get consumer linda10 token ---
# post[extractor]: {"variableName": "linda10_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: f76d84f0-f008-4e1d-9681-cb886143e8fc ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: 25bd242e-da1a-4a23-8754-10ad95bb3bef ---
# pre: // 产生 10 位随机数字（前 3 位为常见 US 区号，如 202, 312, 415, 650 等）
# pre: const areaCodes = ['202', '312', '415', '650', '212', '310'];
# pre: const randomAreaCode = areaCodes[Math.floor(Math.random() * areaCodes.length)];
# pre: const random7Digits = Math.floor(1000000 + Math.random() * 9000000);
# pre: 
# pre: // 组合成 +1 加上 10 位纯数字，例如: +16502396646
# pre: const usPhoneNumber = `+1${randomAreaCode}${random7Digits}`;
# pre: 
# pre: // 设置临时变量
# pre: pm.variables.set("usPhoneNumber", usPhoneNumber);
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: place order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(90.49);
# post: });
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础校验
# post: pm.test("响应状态码为 200 且数据结构正常", function () {
# post:     pm.response.to.have.status(201);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.data).to.be.an('object').that.is.not.null;
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
# post: // 4. 校验 lineItems 中的 customFields 数组不为空且包含数据
# post: pm.test("校验 lineItems[0].customFields 存在且包含填写的自定义字段", function () {
# post:     const confirmation = responseData.data.confirmation;
# post:     pm.expect(confirmation, "confirmation 节点不存在").to.be.an('object');
# post: 
# post:     const lineItems = confirmation.lineItems;
# post:     pm.expect(lineItems, "lineItems 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 校验第一个商品的 customFields
# post:     const customFields = lineItems[0].customFields;
# post:     pm.expect(customFields, "customFields 字段不存在").to.not.be.undefined;
# post:     pm.expect(customFields, "customFields 应为数组类型").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 验证包含具体的自定义字段内容（如 Email, Name, Phone）
# post:     const fieldTitles = customFields.map(field => field.title);
# post:     pm.expect(fieldTitles).to.include.members(["Email", "Name", "Phone"]);
# post: });
# --- step 12: Check the merchant order detail exist ticket Redemptions contents ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础校验 (适配状态码 200)
# post: pm.test("响应状态码为 200 且数据结构正常", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.data).to.be.an('object').that.is.not.null;
# post: });
# post: 
# post: // 3. 提取 orderNumber / orderNumbers 为环境变量
# post: pm.test("提取订单号并设置为环境变量 order_number", function () {
# post:     const data = responseData.data;
# post:     // 兼容新结构 (data.orderNumber) 和 旧结构 (data.orderNumbers[0])
# post:     const orderNumber = data.orderNumber || (data.orderNumbers && data.orderNumbers[0]);
# post:     
# post:     pm.expect(orderNumber, "订单号不存在或为空").to.be.a('string').that.is.not.empty;
# post: 
# post:     // 设置环境变量
# post:     pm.environment.set("order_number", orderNumber);
# post:     console.log("已成功提取 order_number:", orderNumber);
# post: });
# post: 
# post: // 4. 校验 lineItems[0].customFields 存在且包含填写的自定义字段
# post: pm.test("校验 lineItems[0].customFields 存在且包含填写的自定义字段", function () {
# post:     const data = responseData.data;
# post:     
# post:     // 直接从 data.lineItems 读取，适配新结构
# post:     const lineItems = data.lineItems || (data.confirmation && data.confirmation.lineItems);
# post:     pm.expect(lineItems, "lineItems 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 校验第一个商品的 customFields
# post:     const customFields = lineItems[0].customFields;
# post:     pm.expect(customFields, "customFields 字段不存在").to.not.be.undefined;
# post:     pm.expect(customFields, "customFields 应为非空数组").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 验证包含具体的自定义字段内容 (Email, Name, Phone)
# post:     const fieldTitles = customFields.map(field => field.title);
# post:     pm.expect(fieldTitles).to.include.members(["Email", "Name", "Phone"]);
# post: });
# post: 
# post: // 5. 校验根层级的 customFields 属性存在
# post: pm.test("校验 data.customFields 属性存在", function () {
# post:     const data = responseData.data;
# post:     // 适配新结构 data.customFields
# post:     pm.expect(data).to.have.property('customFields');
# post: });





from core.assertions import expect

def test__8706050__Linda_AXS_Verify_the_Customer_provided_details_flow_work(ctx):
    from core.compat import get_path as _get_path
    """Apifox case #8706050: Linda_AXS_Verify_the_Customer_provided_details_flow_work"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: f25b1efc-89d7-45ce-970f-da05a0ac3925
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{UIauto_partner_email}}",\r\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\r\n\r\n}', app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    ctx.extract('yuxiao999_token', _resp1, '$.data.token')
    # step 2: 66d5d716-3a02-4b8c-a925-0485796bcb40
    _resp2 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    vars['event_id'] = 'axsEvent.id'
    vars['event_title'] = 'axsEvent.title'
    # step 3: c10ed67d-5174-4977-9f37-b1a977fddbb2
    _resp3 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    _post0id_val = _get_path(_resp3.json(), ['data', 'items', 0, 'id'])
    vars['post0_id'] = _post0id_val if _post0id_val is not None else ''
    # step 4: 3a42a638-1733-468e-8343-378e4a35997f
    _resp4 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    vars['catalog_id'] = 'catalogId'
    # step 5: 335db91f-b619-4cb9-9bf3-799455463f16
    _resp5 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    vars['ticket_title'] = 'ticketTitle'
    vars['productId'] = 'productId'
    vars['promoterProductId'] = 'promoterProductId'
    vars['merchantProductVariantId'] = 'merchantProductVariantId'
    vars['displayVariantId'] = 'displayVariantId'
    vars['ticketHubInfo_id'] = 'ticketHubInfo_id'
    vars['ticketHandle'] = 'ticketHandle'
    vars['availableQuantity'] = 'availableQuantity'
    vars['sectionIds'] = 'sectionIds'
    # step 6: 7a6d4176-bb6b-499b-9cc7-b7e7ba3ce08b
    _resp6 = ctx.api.products.by_product_id_general_admission_02(body='{\n  "id": "{{productId}}",\n  "remote_id": null,\n  "platform": "AXS",\n  "createdAt": "2026-09-03T09:44:42.495Z",\n  "updatedAt": "2026-09-04T07:34:07.545Z",\n  "merchantId": "{{catalog_id}}",\n  "title": "{{ticket_title}}",\n  "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n  "originalBodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n  "isBodyHtmlOverridden": false,\n  "bodyText": "\\n",\n  "handle": null,\n  "productType": "",\n  "publishedAt": "2026-09-03T09:44:42.508Z",\n  "publishedScope": "",\n  "status": "ACTIVE",\n  "externalStatus": "ACTIVE",\n  "followExternalStatus": false,\n  "tags": [],\n  "templateSuffix": null,\n  "vendor": "Pear",\n  "syncAt": null,\n  "deletedAt": null,\n  "delisted": false,\n  "excludedByImportingTag": false,\n  "isFeatured": false,\n  "featuredScore": null,\n  "inventoryQuantity": {{availableQuantity}},\n  "inventoryQuantityOriginal": {{availableQuantity}},\n  "soldQuantity": 0,\n  "priceDisplay": 55.88,\n  "priceDisplayAnchor": 0,\n  "priceMin": 55.88,\n  "priceMinAnchor": 0,\n  "priceMax": 55.88,\n  "priceMaxAnchor": 0,\n  "priceImportedMin": 0,\n  "priceImportedMax": 0,\n  "imageCount": 1,\n  "isUsed": "NWT",\n  "shippingType": "NO_SHIPPING_REQUIRED",\n  "additionalShippingFee": 0,\n  "deliveryTime": [\n    0,\n    5\n  ],\n  "returnPolicyApplied": true,\n  "isAvailable": true,\n  "commissionRate": 0,\n  "textForShare": null,\n  "priceSyncImported": false,\n  "coverImage": {\n    "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n    "width": 1200,\n    "height": 630,\n    "mediaSrc": null,\n    "mediaType": "IMAGE",\n    "mediaDuration": 0\n  },\n  "useEventPosterAsCover": true,\n  "reviewCount": null,\n  "reviewOverallScore": null,\n  "reviewAggregate": null,\n  "displayReviews": true,\n  "links": null,\n  "taxEnable": false,\n  "taxJarCategory": "",\n  "customTaxRate": null,\n  "subscriptionPlanId": null,\n  "reviewRedirectProductId": null,\n  "reviewSummary": null,\n  "customFieldsInfo": null,\n  "listingType": "TICKET",\n  "ticketType": "TICKET_TYPE_STANDARD",\n  "ticketHubInfo": {\n    "ticketHandle": "{{ticketHubInfo_id}}",\n    "priceSyncedAt": "2026-09-03T09:44:42.350Z",\n    "sectionOptions": [\n      {\n        "label": "GeneralAdmission",\n        "price": {\n          "amount": 4930,\n          "currency": "USD"\n        },\n        "quantityRule": {\n          "max": 4,\n          "min": 1,\n          "step": 1\n        },\n        "ticketHandle": "{{ticketHandle}}",\n        "availableQuantity": {{availableQuantity}},\n        "isGeneralAdmission": true\n      }\n    ]\n  },\n  "customizedFields": [],\n  "shippingOptions": [],\n  "shippingNote": null,\n  "autoFulfill": true,\n  "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",\n  "copyFromId": null,\n  "stopSellingAfter": null,\n  "deliveryMethod": "THIRD_PARTY_ISSUED",\n  "thirdPartyDeliveryMessage": "Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.",\n  "isMultipleDaysPassEnabled": false,\n  "isVenueUnitEnabled": false,\n  "venueUnitCategoryId": null,\n  "multipleDaysPass": null,\n  "isPickupEtaEnabled": null,\n  "eventMatchingRules": null,\n  "expirationTime": null,\n  "allowAtDoorSales": false,\n  "isTipEnabled": false,\n  "isPlatformFeeConfigCustomized": false,\n  "isVariantPlatformFeeConfigCustomized": false,\n  "transactionFeeConfig": {\n    "baseConfig": {\n      "unitFixedFee": 1,\n      "unitPercentageFee": 0.1\n    }\n  },\n  "transactionFeeRebateConfig": {\n    "baseConfig": {\n      "unitFixedFee": 0,\n      "unitPercentageFee": 0\n    }\n  },\n  "transactionCustomFeeConfig": null,\n  "options": [\n    {\n      "remote_id": null,\n      "productId": "{{productId}}",\n      "name": "Title",\n      "position": 1,\n      "values": [\n        "Default Title"\n      ],\n      "images": [\n        {\n          "value": "Default Title",\n          "imageId": null\n        }\n      ]\n    }\n  ],\n  "variants": [\n    {\n      "id": "{{merchantProductVariantId}}",\n      "remote_id": null,\n      "createdAt": "2026-09-03T09:44:42.518Z",\n      "updatedAt": "2026-09-03T09:44:42.518Z",\n      "compareAtPrice": null,\n      "fulfillmentService": "manual",\n      "grams": 0,\n      "imageIds": [],\n      "inventoryItemId": null,\n      "inventoryManagement": "Pear",\n      "inventoryPolicy": "DENY",\n      "isInventoryQuantityUnlimited": false,\n      "inventoryQuantityOriginal": {{availableQuantity}},\n      "soldQuantity": 0,\n      "position": 1,\n      "priceImported": "0.00",\n      "productId": "{{productId}}",\n      "sku": "",\n      "taxCode": null,\n      "taxable": true,\n      "weight": null,\n      "weightUnit": "lb",\n      "platform": null,\n      "transactionFee": {\n        "platformFee": 6.58,\n        "customFee": 0,\n        "customFeeBreakdown": {\n          "TAX": {\n            "title": "Taxes",\n            "unitFixedFee": 0,\n            "unitPercentageFee": 0,\n            "index": 0,\n            "itemFee": 0\n          }\n        },\n        "transactionItemFee": 6.58\n      },\n      "isMinPurchaseQuantityEnabled": true,\n      "minPurchaseQuantity": 1,\n      "isMaxPurchaseQuantityEnabled": true,\n      "maxPurchaseQuantity": 4,\n      "isPackSizeEnabled": false,\n      "packSize": null,\n      "transactionFeeConfig": null,\n      "transactionFeeRebateConfig": null,\n      "minPriceForCheckFees": 0,\n      "title": "Default Title",\n      "option": {\n        "option1": "Default Title"\n      },\n      "price": 55.88,\n      "ticketPrice": 49.3,\n      "fees": 6.58,\n      "priceAnchor": 0,\n      "inventoryQuantity": {{availableQuantity}}\n    }\n  ],\n  "readOnlyFields": [\n    "ticketPrice",\n    "fees",\n    "price",\n    "priceAnchor",\n    "inventoryQuantity",\n    "variantsEnabled",\n    "tax",\n    "customFees"\n  ],\n  "isInventoryQuantityUnlimited": false,\n  "showInEventPost": true,\n  "visibleInPosts": [\n    {\n      "postId": "{{post0_id}}",\n      "isVisible": true\n    }\n  ],\n  "excludeFromPostSync": false,\n  "catalogCommissionRate": 25,\n  "hasLimitPurchaseQuantity": true,\n  "hasSpecialRedemption": false,\n  "earliestTime": "2026-09-03T09:44:42.495Z",\n  "styleSettings": {\n    "recentUsedColors": [\n      "#ffffff"\n    ]\n  },\n  "isProductFormEnabled": true,\n  "isInclusionsEnabled": false,\n  "inclusions": [],\n   "productForm": {\n        "title": "contact form for autotest",\n        "subtitle": "autotest",\n        "iconImage": "",\n        "showImage": false,\n        "formFields": [\n            {\n                "field": "SHORT_ANSWER",\n                "required": true,\n                "title": "Name",\n                "position": 1,\n                "label": "Short answer text field",\n                "isInitial": true\n            },\n            {\n                "field": "PHONE_NUMBER",\n                "required": true,\n                "title": "Phone",\n                "position": 2,\n                "label": "Phone number",\n                "isInitial": true\n            },\n            {\n                "field": "EMAIL_ADDRESS",\n                "required": true,\n                "title": "Email",\n                "position": 3,\n                "label": "Email address",\n                "isInitial": true\n            }\n        ]\n    },\n  "isVariantPriceDisplayEnabled": false,\n  "stopSellingAfterDisplay": "",\n  "overrideEventTax": false,\n  "overrideEventCustomFee": false,\n  "hideFees": false,\n  "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n  "images": [\n    {\n      "id": "7b9ef5e8-a5ff-4d9b-95fc-7f75872008a9",\n      "remote_id": null,\n      "createdAt": "2026-09-03T09:44:42.518Z",\n      "updatedAt": "2026-09-03T09:44:42.518Z",\n      "height": 1000,\n      "width": 1000,\n      "position": 1,\n      "productId": "{{productId}}",\n      "src": "https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png",\n      "variantIds": [],\n      "mediaType": "IMAGE",\n      "mediaSrc": null,\n      "mediaDuration": 0,\n      "contributedBy": 3,\n      "contributorId": null,\n      "productImageType": "PRODUCT",\n      "source": null,\n      "setThumbnail": true\n    }\n  ],\n  "eventId": "{{event_id}}",\n  "isExpirationEnabled": false\n}', token='yuxiao999_token', path_vars={'productId_General_Admission_02': '{{productId}}'})
    # step 8: Get consumer linda10 token
    _resp8 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+10@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}')
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp8, '$.data.token')
    # step 9: f76d84f0-f008-4e1d-9681-cb886143e8fc
    _resp9 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 9.assertion: responseJson equal 200
    expect(_resp9).json('$.code').equals('200')
    # assertion 9.assertion: responseJson equal success
    expect(_resp9).json('$.message').equals('success')
    vars['usPhoneNumber'] = 'usPhoneNumber'
    # step 10: 25bd242e-da1a-4a23-8754-10ad95bb3bef
    _resp10 = ctx.api.orders.checkout_express(body='{\n  "items": [\n    {\n      "promoterProductVariantId": "{{displayVariantId}}",\n      "postId": "{{post0_id}}",\n      "quantity": 1,\n      "price": 55.88,\n      "sectionIds": [\n        "{{sectionIds}}"\n      ],\n      "ticketHandle": "{{ticketHandle}}",\n      "eventId": "{{event_id}}",\n      "selected": true\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "dc72ffe2-6310-4f66-b5c3-ca3074a83af9",\n    "pixelId": [\n      "268933192948110"\n    ],\n    "fbBrowserId": "fb.1.1788427187167.268347998920074386",\n    "externalId": "a35633fe-c8b3-4542-a776-64f146731b31",\n    "eventSourceUrl": "https://release.pear.us/autotestshop/post/zack-fox-dj-set-1"\n  },\n  "subdomainVanityUrl": ""\n}', app_headers=True, token='linda10_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp10, '$.data.orderId')
    # step 11: place order
    _resp11 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "linda.zhou.ext+10@1m.app"\n    },\n    "shippingAddressId": "{{shippingAddressId}}",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "58e159af-0e82-4244-b86d-00f37277e6a0",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=ff6bbfb6-7146-44d9-985b-26eefbf740e3"\n    }\n}', skip_notifications=False, token='linda10_token')
    _ordernumber_val = _get_path(_resp10.json(), ['data', 'orderNumbers', 0])
    vars['order_number'] = _ordernumber_val if _ordernumber_val is not None else ''
    # step 12: Check the merchant order detail exist ticket Redemptions contents
    _resp12 = ctx.api.orders.merchant_detail_v2(token='yuxiao999_token', path_vars={'merchantId': '{{catalog_id}}', 'orderNumber': '{{order_number}}'})
