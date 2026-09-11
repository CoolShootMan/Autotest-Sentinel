"""Migrated from Apifox case #8677597. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8677597  (traceability only — not needed to run)
NAME = "(Linda)(TDC)T5379Verify the Additional QR codes flow work"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting"]
PRIORITY = 0


CASE_ID = 8677597
ENV_NAME = "Release"

# --- step 1: 5bbc6a1c-120f-404a-ae14-7079b17af1c3 ---
# post[extractor]: {"variableName": "yuxiao999_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: f9fdbfd2-b2cd-4ba6-9bf3-c74dff73da29 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应断言
# post: pm.test("响应状态码为 200 且 message 为 success", function () {
# post:     pm.response.to.have.status(201);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post: });
# post: 
# post: // 3. 筛选 platform 为 TDC 的第一个活动并存入环境变量
# post: pm.test("提取排序第一的 TDC 活动的 id 和 title", function () {
# post:     const items = responseData.data?.items;
# post:     
# post:     // 确保 items 数组存在且不为空
# post:     pm.expect(items, "data.items 数组不存在").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 查找第一个 platform 为 "TDC" 的元素
# post:     const tdcEvent = items.find(item => item.platform === "TDC");
# post:     
# post:     // 断言存在 TDC 平台对应的活动
# post:     pm.expect(tdcEvent, "未找到 platform 为 TDC 的活动").to.be.an('object');
# post: 
# post:     const eventId = tdcEvent.id;
# post:     const eventTitle = tdcEvent.title;
# post: 
# post:     // 校验提取出的字段值非空
# post:     pm.expect(eventId, "event_id 提取失败").to.be.a('string').and.not.empty;
# post:     pm.expect(eventTitle, "event_title 提取失败").to.be.a('string').and.not.empty;
# post: 
# post:     // 设置到环境变量
# post:     pm.environment.set("event_id", eventId);
# post:     pm.environment.set("event_title", eventTitle);
# post: 
# post:     console.log("提取结果 - event_id:", eventId);
# post:     console.log("提取结果 - event_title:", eventTitle);
# post: });
# --- step 3: d149d601-1c91-44e4-a1e1-e6e5c8b43d86 ---
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
# --- step 4: 67d34753-d40c-4576-9ac1-01ad291cc1b2 ---
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
# --- step 5: 122b2d2a-2827-4d8c-b162-de9276af7a0c ---
# post[customScript]: // 1. 解析响应数据
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 状态码与数据合法性校验
# post: pm.test("响应状态为 200 且包含 relatedProducts", function () {
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.data?.relatedProducts).to.be.an('array');
# post: });
# post: 
# post: // 3. 循环提取所有产品的目标 ID
# post: const products = responseData.data?.relatedProducts || [];
# post: 
# post: products.forEach((product, index) => {
# post:     pm.test(`提取产品 [${product.title || index}] 的 ID 环境变量`, function () {
# post:         // 格式化标题作为变量后缀：替换空格为下划线，如 "General_Admission_02"
# post:         const formattedTitle = product.title 
# post:             ? product.title.trim().replace(/\s+/g, '_') 
# post:             : `index_${index}`;
# post: 
# post:         // 1. 提取 productId (优先取 merchantProductId，无则取 shippingView.productId)
# post:         const productId = product.merchantProductId || product.shippingView?.productId;
# post:         pm.expect(productId, "productId 不存在").to.be.a('string').and.not.empty;
# post:         const productIdVar = `productId_${formattedTitle}`;
# post:         pm.environment.set(productIdVar, productId);
# post: 
# post:         // 2. 提取 promoterProductId
# post:         const promoterProductId = product.promoterProductId;
# post:         pm.expect(promoterProductId, "promoterProductId 不存在").to.be.a('string').and.not.empty;
# post:         const promoterProductIdVar = `promoterProductId_${formattedTitle}`;
# post:         pm.environment.set(promoterProductIdVar, promoterProductId);
# post: 
# post:         // 3. 提取 merchantProductVariantId (取 variants 数组第一项中的变体 ID)
# post:         const merchantProductVariantId = product.variants?.[0]?.merchantProductVariantId;
# post:         pm.expect(merchantProductVariantId, "merchantProductVariantId 不存在").to.be.a('string').and.not.empty;
# post:         const variantIdVar = `merchantProductVariantId_${formattedTitle}`;
# post:         pm.environment.set(variantIdVar, merchantProductVariantId);
# post: 
# post:         // 4. 补充：提取 displayVariantId (优先取 variants[0] 中的，无则取 product 层级)
# post:         const displayVariantId = product.variants?.[0]?.displayVariantId || product.displayVariantId;
# post:         pm.expect(displayVariantId, "displayVariantId 不存在").to.be.a('string').and.not.empty;
# post:         const displayVariantIdVar = `displayVariantId_${formattedTitle}`;
# post:         pm.environment.set(displayVariantIdVar, displayVariantId);
# post: 
# post:         console.log(`[提取成功] ${formattedTitle}:`);
# post:         console.log(`  - ${productIdVar}: ${productId}`);
# post:         console.log(`  - ${promoterProductIdVar}: ${promoterProductId}`);
# post:         console.log(`  - ${variantIdVar}: ${merchantProductVariantId}`);
# post:         console.log(`  - ${displayVariantIdVar}: ${displayVariantId}`);
# post:     });
# post: });
# --- step 6: 61e71fa6-c51d-495c-ae2a-e5ce68457d94 ---
# post[customScript]: // 1. 解析响应数据
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 筛选出 orderNumber 为 null 的所有项
# post: const items = responseData.data?.items || [];
# post: const nullOrderItems = items.filter(item => item.orderNumber === null);
# post: 
# post: // 3. 断言并随机提取 unitid、seatNumber 以及 venueUnitCategoryId
# post: pm.test("随机提取 orderNumber 为 null 的 item 字段并设置环境变量", function () {
# post:     // 校验是否有满足条件的项
# post:     pm.expect(nullOrderItems, "未找到 orderNumber 为 null 的数据项").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 随机生成索引
# post:     const randomIndex = Math.floor(Math.random() * nullOrderItems.length);
# post:     const selectedItem = nullOrderItems[randomIndex];
# post: 
# post:     // 校验 id 并设置为 unitid 环境变量
# post:     pm.expect(selectedItem.id, "提取的 id 格式不正确或为空").to.be.a('string').and.not.empty;
# post:     const unitId = selectedItem.id;
# post:     pm.environment.set("unitid", unitId);
# post: 
# post:     // 校验 number 并设置为 seatNumber 环境变量
# post:     pm.expect(selectedItem.number, "提取的 number 不存在或为空").to.exist;
# post:     const seatNumber = String(selectedItem.number);
# post:     pm.environment.set("seatNumber", seatNumber);
# post: 
# post:     // 校验 categoryId 并设置为 venueUnitCategoryId 环境变量
# post:     pm.expect(selectedItem.categoryId, "提取的 categoryId 格式不正确或为空").to.be.a('string').and.not.empty;
# post:     const venueUnitCategoryId = selectedItem.categoryId;
# post:     pm.environment.set("venueUnitCategoryId", venueUnitCategoryId);
# post: 
# post:     console.log(`[提取成功] 从 ${nullOrderItems.length} 个符合条件的项中随机选中 index ${randomIndex}:`);
# post:     console.log(`  - unitid: ${unitId}`);
# post:     console.log(`  - seatNumber: ${seatNumber}`);
# post:     console.log(`  - venueUnitCategoryId: ${venueUnitCategoryId}`);
# post: });
# --- step 7: 309acb6a-6b12-42b4-8689-4d51c67430f6 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 状态码与业务逻辑兼容校验
# post: pm.test("响应校验：成功(200)或包含预期的业务错误(400)", function () {
# post:     if (responseData.code === 200) {
# post:         // 场景 A：200 成功响应，校验 inclusions 数据结构
# post:         pm.expect(responseData.data, "200 响应缺少 data 字段").to.be.an('object');
# post:         pm.expect(responseData.data.inclusions, "inclusions 须为非空数组").to.be.an('array').that.is.not.empty;
# post:     } else if (responseData.code === 400) {
# post:         // 场景 B：400 预期的错误响应，校验错误 message
# post:         const expectedMessage = "Cannot delete inclusions: product has existing orders";
# post:         pm.expect(responseData.message, "400 错误的 message 不符合预期").to.include(expectedMessage);
# post:     } else {
# post:         // 其他未预期的状态码直接报错
# post:         pm.expect.fail(`未预期的响应状态码 code: ${responseData.code}`);
# post:     }
# post: });
# post: 
# post: // 3. 提取 inclusions 环境变量（仅在 200 且存在 inclusions 时执行）
# post: if (responseData.code === 200 && Array.isArray(responseData.data?.inclusions)) {
# post:     const inclusions = responseData.data.inclusions;
# post:     
# post:     // 提取所有 name 组成的数组并转 JSON 字符串保存
# post:     const inclusionNames = inclusions.map(item => item.name);
# post:     pm.environment.set("inclusionNames", JSON.stringify(inclusionNames));
# post:     
# post:     // 依次设置单个环境变量（inclusion_0, inclusion_1...）
# post:     inclusions.forEach((item, index) => {
# post:         pm.environment.set(`inclusion_${index}`, item.name);
# post:         console.log(`[提取成功] inclusion_${index}: ${item.name}`);
# post:     });
# post: } else if (responseData.code === 400) {
# post:     console.warn(`[业务拦截] 捕获到预期 400 异常: ${responseData.message}`);
# post: }
# --- step 9: Get consumer linda10 token ---
# post[extractor]: {"variableName": "linda10_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: e101d932-3e88-47ee-8dc0-76fdb2f88c85 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: dfada68f-a95b-43f8-934c-e452baf76dd7 ---
# post[extractor]: {"variableName": "orderId", "variableType": "local", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 12: place order ---
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
# --- step 13: Check the merchant order detail exist ticket Redemptions contents ---
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




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_linda_tdc_t5379verify_the_additional_qr_codes_flow_work(ctx):
    """Apifox case #8677597: Linda_TDC_T5379Verify_the_Additional_QR_codes_flow_work"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 5bbc6a1c-120f-404a-ae14-7079b17af1c3
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{UIauto_partner_email}}",\r\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\r\n\r\n}', app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    ctx.extract('yuxiao999_token', _resp1, '$.data.token')
    # step 2: f9fdbfd2-b2cd-4ba6-9bf3-c74dff73da29
    _resp2 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    vars['event_id'] = 'eventId'
    vars['event_title'] = 'eventTitle'
    # step 3: d149d601-1c91-44e4-a1e1-e6e5c8b43d86
    _resp3 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    _post0id_val = _get_path(_resp3.json(), ['data', 'items', 0, 'id'])
    vars['post0_id'] = _post0id_val if _post0id_val is not None else ''
    # step 4: 67d34753-d40c-4576-9ac1-01ad291cc1b2
    _resp4 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    vars['catalog_id'] = 'catalogId'
    # step 5: 122b2d2a-2827-4d8c-b162-de9276af7a0c
    _resp5 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    # step 6: 61e71fa6-c51d-495c-ae2a-e5ce68457d94
    _resp6 = ctx.api.events.tickets_venue_units(body=None, params={'pageNumber': '1', 'pageSize': '30', 'variantId': '{merchantProductVariantId_General_Admission_02}'}, token='yuxiao999_token')
    vars['unitid'] = 'unitId'
    _j = _resp6.json() if _resp6.headers.get('content-type','').startswith('application/json') else {}
    vars['seatNumber'] = str(_get_path(_j, ['data', 'items', 0, 'number']))
    _j = _resp6.json() if _resp6.headers.get('content-type','').startswith('application/json') else {}
    vars['venueUnitCategoryId'] = _get_path(_j, ['data', 'items', 0, 'categoryId'])
    # step 7: 309acb6a-6b12-42b4-8689-4d51c67430f6
    _resp7 = ctx.api.products.by_product_id_general_admission_02(body='{\n    "id": "{{productId_General_Admission_02}}",\n    "remote_id": null,\n    "platform": "PEAR",\n    "createdAt": "2026-08-24T07:50:43.279Z",\n    "updatedAt": "2026-08-24T07:50:43.353Z",\n    "merchantId": "{{catalog_id}}",\n    "title": "General Admission 02",\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n    "originalBodyHtml": "",\n    "isBodyHtmlOverridden": false,\n    "bodyText": "",\n    "handle": null,\n    "productType": "",\n    "publishedAt": "2026-08-24T07:50:43.309Z",\n    "publishedScope": "",\n    "status": "ACTIVE",\n    "externalStatus": "ACTIVE",\n    "followExternalStatus": false,\n    "tags": [],\n    "templateSuffix": null,\n    "vendor": "Pear",\n    "syncAt": null,\n    "deletedAt": null,\n    "delisted": false,\n    "excludedByImportingTag": false,\n    "isFeatured": false,\n    "featuredScore": null,\n    "inventoryQuantity": 10000,\n    "inventoryQuantityOriginal": 10000,\n    "soldQuantity": 0,\n    "priceDisplay": 112.22,\n    "priceDisplayAnchor": 0,\n    "priceMin": 112.22,\n    "priceMinAnchor": 0,\n    "priceMax": 112.22,\n    "priceMaxAnchor": 0,\n    "priceImportedMin": 0,\n    "priceImportedMax": 0,\n    "imageCount": 1,\n    "isUsed": "NWT",\n    "shippingType": "NO_SHIPPING_REQUIRED",\n    "additionalShippingFee": 0,\n    "deliveryTime": [\n        0,\n        5\n    ],\n    "returnPolicyApplied": true,\n    "isAvailable": true,\n    "commissionRate": 7,\n    "textForShare": null,\n    "priceSyncImported": false,\n    "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "position": 0,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n    },\n    "useEventPosterAsCover": true,\n    "reviewCount": null,\n    "reviewOverallScore": null,\n    "reviewAggregate": null,\n    "displayReviews": true,\n    "links": null,\n    "taxEnable": false,\n    "taxJarCategory": "",\n    "customTaxRate": null,\n    "subscriptionPlanId": null,\n    "reviewRedirectProductId": null,\n    "reviewSummary": null,\n    "customFieldsInfo": null,\n    "listingType": "TICKET",\n    "ticketType": "TICKET_TYPE_STANDARD",\n    "ticketHubInfo": null,\n    "customizedFields": [],\n    "shippingOptions": [],\n    "shippingNote": null,\n    "autoFulfill": true,\n    "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",\n    "copyFromId": "{{copyFromId}}",\n    "stopSellingAfter": null,\n    "deliveryMethod": "QR_CODE",\n    "thirdPartyDeliveryMessage": "",\n    "isMultipleDaysPassEnabled": false,\n    "isVenueUnitEnabled": true,\n    "venueUnitCategoryId": "{{venueUnitCategoryId}}",\n    "multipleDaysPass": null,\n    "isPickupEtaEnabled": null,\n    "eventMatchingRules": null,\n    "expirationTime": null,\n    "allowAtDoorSales": false,\n    "isTipEnabled": false,\n    "isPlatformFeeConfigCustomized": false,\n    "isVariantPlatformFeeConfigCustomized": false,\n    "transactionFeeConfig": {\n        "baseConfig": {\n            "unitFixedFee": 1,\n            "unitPercentageFee": 0.1\n        }\n    },\n    "transactionFeeRebateConfig": {\n        "baseConfig": {\n            "unitFixedFee": 0,\n            "unitPercentageFee": 0\n        }\n    },\n    "transactionCustomFeeConfig": null,\n    "options": [\n        {\n            "remote_id": null,\n            "productId": "{{productId_General_Admission_02}}",\n            "name": "Title",\n            "position": 1,\n            "values": [\n                "Default Title"\n            ],\n            "images": [\n                {\n                    "value": "Default Title",\n                    "imageId": null\n                }\n            ]\n        }\n    ],\n    "variants": [\n        {\n            "id": "{{merchantProductVariantId_General_Admission_02}}",\n            "remote_id": null,\n            "createdAt": "2026-08-24T07:50:43.353Z",\n            "updatedAt": "2026-08-24T07:50:43.353Z",\n            "compareAtPrice": null,\n            "fulfillmentService": "manual",\n            "grams": 0,\n            "imageIds": [],\n            "inventoryItemId": null,\n            "inventoryManagement": "Pear",\n            "inventoryPolicy": "DENY",\n            "isInventoryQuantityUnlimited": false,\n            "inventoryQuantity": 10000,\n            "inventoryQuantityOriginal": 10000,\n            "soldQuantity": 0,\n            "option": {\n                "option1": "Default Title"\n            },\n            "position": 1,\n            "price": 112.22,\n            "priceAnchor": 0,\n            "priceImported": "0.00",\n            "productId": "{{productId_General_Admission_02}}",\n            "sku": "",\n            "taxCode": null,\n            "taxable": true,\n            "title": "Default Title",\n            "weight": null,\n            "weightUnit": "lb",\n            "platform": null,\n            "fees": 12.22,\n            "transactionFee": {\n                "platformFee": 12.22,\n                "customFee": 0,\n                "customFeeBreakdown": {\n                    "TAX": {\n                        "title": "Taxes",\n                        "unitFixedFee": 0,\n                        "unitPercentageFee": 0,\n                        "index": 0,\n                        "itemFee": 0\n                    }\n                },\n                "transactionItemFee": 12.22\n            },\n            "ticketPrice": 100,\n            "isMinPurchaseQuantityEnabled": false,\n            "minPurchaseQuantity": null,\n            "isMaxPurchaseQuantityEnabled": false,\n            "maxPurchaseQuantity": null,\n            "isPackSizeEnabled": false,\n            "packSize": null,\n            "transactionFeeConfig": null,\n            "transactionFeeRebateConfig": null,\n            "minPriceForCheckFees": 0\n        }\n    ],\n    "readOnlyFields": [],\n    "isInventoryQuantityUnlimited": false,\n    "showInEventPost": false,\n    "visibleInPosts": [],\n    "excludeFromPostSync": false,\n    "catalogCommissionRate": 0,\n    "hasLimitPurchaseQuantity": false,\n    "hasSpecialRedemption": false,\n    "earliestTime": "2026-08-24T04:00:00.000Z",\n    "styleSettings": {\n        "recentUsedColors": [\n            "#ffffff"\n        ]\n    },\n    "isProductFormEnabled": false,\n    "isInclusionsEnabled": true,\n    "inclusions": [\n        {\n            "name": "additional QR codes 001",\n            "position": 0\n        },\n        {\n            "name": "additional QR codes 002",\n            "position": 1\n        },\n        {\n            "name": "additional QR codes 003",\n            "position": 2\n        },\n        {\n            "name": "additional QR codes 004",\n            "position": 3\n        },\n        {\n            "name": "additional QR codes 005",\n            "position": 4\n        }\n    ],\n    "isVariantPriceDisplayEnabled": false,\n    "stopSellingAfterDisplay": "",\n    "overrideEventTax": false,\n    "overrideEventCustomFee": false,\n    "hideFees": false,\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n    "images": [\n        {\n            "id": "40568f61-4d5c-4419-b167-316268bb7f68",\n            "remote_id": null,\n            "createdAt": "2026-08-24T07:50:43.353Z",\n            "updatedAt": "2026-08-24T07:50:43.353Z",\n            "height": 1000,\n            "width": 1000,\n            "position": 1,\n            "productId": "{{productId_General_Admission_02}}",\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",\n            "variantIds": [],\n            "mediaType": "IMAGE",\n            "mediaSrc": null,\n            "mediaDuration": 0,\n            "contributedBy": 3,\n            "contributorId": null,\n            "productImageType": "PRODUCT",\n            "source": null,\n            "setThumbnail": true\n        }\n    ],\n    "eventId": "{{event_id}}",\n    "isExpirationEnabled": false\n}', token='yuxiao999_token')
    vars['inclusionNames'] = 'JSON.stringify(inclusionNames'
    # step 9: Get consumer linda10 token
    _resp9 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+10@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}', app_headers=True)
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp9, '$.data.token')
    # step 10: e101d932-3e88-47ee-8dc0-76fdb2f88c85
    _resp10 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 10.assertion: responseJson equal 200
    expect(_resp10).json('$.code').equals('200')
    # assertion 10.assertion: responseJson equal success
    expect(_resp10).json('$.message').equals('success')
    # step 11: dfada68f-a95b-43f8-934c-e452baf76dd7
    _resp11 = ctx.api.orders.checkout_express(body='{\n  "fbAdParams": {\n    "eventID": "0e23d7da-dab0-4dc8-a27c-96ea822f38ad",\n    "pixelId": [\n      "268933192948110"\n    ],\n    "fbBrowserId": "fb.1.1787626769799.674084567126480531",\n    "externalId": "7d70692d-84f0-4b50-bcda-abc39b7d165a",\n    "eventSourceUrl": "https://release.pear.us/autotestshop/post/event-for-api-auto-venue-map"\n  },\n  "items": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "{{displayVariantId_General_Admission_02}}",\n      "price": 112.22,\n      "postId": "{{post0_id}}",\n      "eventId": "{{event_id}}",\n      "sectionName": "General Admission 02",\n      "seatRow": "",\n      "seatNumber": "{{seatNumber}}",\n      "unitId": "{{unitid}}",\n      "selected": true\n    }\n  ],\n  "subdomainVanityUrl": ""\n}', app_headers=True, token='linda10_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp11, '$.data.orderId')
    # step 12: place order
    _resp12 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "linda.zhou.ext+10@1m.app"\n    },\n    "shippingAddressId": "{{shippingAddressId}}",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "58e159af-0e82-4244-b86d-00f37277e6a0",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=ff6bbfb6-7146-44d9-985b-26eefbf740e3"\n    }\n}', app_headers=True, skip_notifications=False, token='linda10_token')
    _ordernumber_val = _get_path(_resp11.json(), ['data', 'orderNumbers', 0])
    vars['order_number'] = _ordernumber_val if _ordernumber_val is not None else ''
    # step 13: Check the merchant order detail exist ticket Redemptions contents
    _resp13 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='yuxiao999_token', path_vars={'merchantId': '{{catalog_id}}', 'orderNumber': '{{order_number}}'})
