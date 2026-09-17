"""Migrated from Apifox case #8620470. Source folder: Event and ticket and redeemed/Event created and setting."""
# Apifox Case ID: 8620470  (traceability only — not needed to run)
NAME = "&T4724 Verify the Event can create and duplicate and delete and switch status"
TAGS = ["p1", "event_and_ticket_and_redeemed_event_created_and_setting", "suite:linda"]
PRIORITY = 1


CASE_ID = 8620470
ENV_NAME = "Release"

# --- step 1: 31523ce3-41cd-44be-8ce5-322acb4d98d9 ---
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
# --- step 2: Partner Create event ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: const resJson = pm.response.json();
# post: 
# post: pm.test("活动创建成功，响应包含合法ID", function () {
# post: // 断言状态码和业务响应正常
# post: pm.response.to.have.status(201);
# post: pm.expect(resJson.code).to.eql(200); // 响应体中code字段为200（按实际业务码调整）
# post: pm.expect(resJson.message).to.eql("success");
# post:   
# post: // 核心断言：确保 data 存在且包含 id 字段
# post: pm.expect(resJson.data).to.exist.and.to.be.an("object", "响应体缺少 data 字段");
# post: pm.expect(resJson.data.id).to.exist.and.to.be.a("string", "data 字段中缺少 id（活动ID）");
# post: });
# post: 
# post: const eventId = resJson.data.id;
# post: pm.environment.set("created_event_id", eventId);
# post: 
# post: console.log("✅ 已成功提取活动ID：", eventId);
# post: console.log("✅ 环境变量 created_event_id 已更新为：", pm.environment.get("created_event_id"));
# --- step 3: e3e0b07b-ca07-46cd-81c9-a3944c74547e ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 78adc986-7caf-46cc-ab7b-42b010e77f12 ---
# --- step 5: 6b136fb9-5b69-4781-8a2b-c4d0a0925f61 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: 1f79ab2a-5352-49f4-a445-96accf653e08 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: // 1. Parse the response JSON
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: 
# post: // --- Assertion for the Title ---
# post: pm.test("Verify the event title is correct", function () {
# post:     // Assert that the title strictly matches "API auto test T4166"
# post:     pm.expect(data.title).to.eql("Verify the Event can create and duplicate and delete success")
# post: });
# post: 
# post: 
# post: //--- 2. Extract Environment Variables ---
# post: pm.test("Extract IDs to environment variables", function () {
# post:     // Extract Ticket ID
# post:     const ticketId = data.tickets[0].id;
# post:     pm.environment.set("ticket_id", ticketId);
# post:     
# post:     // Extract Variant ID
# post:     const variantId = data.tickets[0].variants[0].id;
# post:     pm.environment.set("variant_id", variantId);
# post:     
# post:     // Log for debugging
# post:     console.log("Extracted ticket_id:", ticketId);
# post:     console.log("Extracted variant_id:", variantId);
# post:     
# post:     // Safety assertion to ensure extraction worked
# post:     pm.expect(ticketId).to.be.a('string').and.not.empty;
# post:     pm.expect(variantId).to.be.a('string').and.not.empty;
# post: });
# --- step 7: a94879d6-2c75-4727-a315-996b5f67b588 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 在 items 数组中查找 title 为 "Verify the Event can create and duplicate and delete success" 的事件
# post: const targetEvent = responseData.data.items.find(
# post:     item => item.title === "Verify the Event can create and duplicate and delete success"
# post: );
# post: 
# post: // 3. 断言并设置环境变量 event_id
# post: pm.test("找到 title 为 'Verify the Event can create and duplicate and delete success' 的事件并提取 id 设置为 event_id", function () {
# post:     // 断言找到目标事件
# post:     pm.expect(targetEvent, "未找到 title 为 'Verify the Event can create and duplicate and delete success' 的事件").to.not.be.undefined;
# post:     pm.expect(targetEvent.id, "提取的 id 为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 获取并设置环境变量
# post:     const eventId = targetEvent.id;
# post:     pm.environment.set("event_id", eventId);
# post:     
# post:     console.log("已成功提取 event_id:", eventId);
# post: });
# --- step 8: 33516490-440b-4838-a47f-1461996a3f0f ---
# pre: pm.environment.set("event_title", "Duplicate Verify the Event can create and duplicate and delete success");
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: 
# post: // 3. 提取 data.id 并设置为环境变量 dup_event_id
# post: pm.test("提取 data.id 并设置为环境变量 dup_event_id", function () {
# post:     const eventId = responseData.data?.id;
# post:     pm.expect(eventId, "data.id 不存在或为空").to.be.a('string').and.not.empty;
# post:     
# post:     // 设置环境变量
# post:     pm.environment.set("dup_event_id", eventId);
# post:     console.log("已成功提取 dup_event_id:", eventId);
# post: });
# post: 
# post: // 4. 提取 lineup[0].id 并设置为环境变量 lineup_id
# post: pm.test("提取 lineup id 并设置为环境变量 lineup_id", function () {
# post:     const lineupList = responseData.data?.lineup;
# post:     pm.expect(lineupList, "lineup 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     const lineupId = lineupList[0]?.id;
# post:     pm.expect(lineupId, "lineup[0].id 不存在或为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 设置环境变量
# post:     pm.environment.set("lineup_id", lineupId);
# post:     console.log("已成功提取 lineup_id:", lineupId);
# post: });
# post: 
# post: // 5. 断言税费、自定义费用及票种限购相关配置
# post: pm.test("断言 isTaxEnabled, taxConfig, customFeeConfig 及 tickets/variants 限购配置", function () {
# post:     const data = responseData.data;
# post:     pm.expect(data, "data 对象不存在").to.be.an('object');
# post: 
# post:     // 1) 断言 isTaxEnabled 和 taxConfig
# post:     pm.expect(data.isTaxEnabled, "isTaxEnabled 不为 true").to.be.true;
# post:     pm.expect(data.taxConfig, "taxConfig 对象不存在").to.be.an('object');
# post:     pm.expect(data.taxConfig.customTaxRate, "customTaxRate 不等于 10").to.eql(10);
# post:     pm.expect(data.taxConfig.calculationType, "calculationType 不等于 CUSTOM").to.eql("CUSTOM");
# post: 
# post:     // 2) 断言 customFeeConfig
# post:     pm.expect(data.customFeeConfig, "customFeeConfig 对象不存在").to.be.an('object');
# post:     pm.expect(data.customFeeConfig.items, "customFeeConfig.items 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post:     
# post:     const feeItem = data.customFeeConfig.items[0];
# post:     pm.expect(feeItem.title, "custom fee title 不正确").to.eql("custom fee");
# post:     pm.expect(feeItem.unitFixedFee, "unitFixedFee 不等于 0").to.eql(0);
# post:     pm.expect(feeItem.unitPercentageFee, "unitPercentageFee 不等于 0.1").to.eql(0.1);
# post: 
# post:     // 3) 断言 tickets -> variants 下的限购与库存配置
# post:     pm.expect(data.tickets, "tickets 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post:     const ticket = data.tickets[0];
# post:     
# post:     // 校验 ticket 层级库存设置
# post:     pm.expect(ticket.isInventoryQuantityUnlimited, "ticket.isInventoryQuantityUnlimited 不为 false").to.be.false;
# post: 
# post:     pm.expect(ticket.variants, "variants 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post:     const variant = ticket.variants[0];
# post: 
# post:     // 校验 variant 层级库存与限购设置
# post:     pm.expect(variant.isInventoryQuantityUnlimited, "variant.isInventoryQuantityUnlimited 不为 false").to.be.false;
# post:     pm.expect(variant.isMinPurchaseQuantityEnabled, "isMinPurchaseQuantityEnabled 不为 true").to.be.true;
# post:     pm.expect(variant.minPurchaseQuantity, "minPurchaseQuantity 不等于 2").to.eql(2);
# post:     pm.expect(variant.isMaxPurchaseQuantityEnabled, "isMaxPurchaseQuantityEnabled 不为 true").to.be.true;
# post:     pm.expect(variant.maxPurchaseQuantity, "maxPurchaseQuantity 不等于 5").to.eql(5);
# post:     pm.expect(variant.isPackSizeEnabled, "isPackSizeEnabled 不为 true").to.be.true;
# post:     pm.expect(variant.packSize, "packSize 不等于 3").to.eql(3);
# post: 
# post:     console.log("所有配置字段断言成功！");
# post: });
# --- step 9: db5f22cf-c39a-4076-923d-1f60f4c0c4d8 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 从环境变量中获取 event_title 的实际字符串
# post: const targetTitle = pm.environment.get("event_title");
# post: 
# post: // 3. 在 items 列表中查找匹配的项
# post: const targetItem = responseData.data?.items?.find(
# post:     item => item.title === targetTitle
# post: );
# post: 
# post: if (targetItem) {
# post:     // 设置环境变量 postId
# post:     pm.environment.set("postId", targetItem.id);
# post:     console.log("成功提取 postId:", targetItem.id);
# post: } else {
# post:     console.error("未找到匹配的 item，期望的 title 为:", targetTitle);
# post: }
# post: 
# post: // 4. 加上 Postman 断言校验
# post: pm.test("能够查找到匹配 title 的 post 并成功设置 postId", function () {
# post:     pm.expect(targetItem, `列表中未找到 title 为 [${targetTitle}] 的项`).to.be.an('object');
# post:     pm.expect(targetItem.id).to.be.a('string').and.not.empty;
# post: });
# --- step 10: 6ee46b75-9a00-4f23-9767-b88d0e800310 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应状态码断言
# post: pm.test("响应状态码为 200 且 message 为 success", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post: });
# post: 
# post: // 3. 断言 status 字段为 ON_HOLD
# post: pm.test("断言 status 字段为 ON_HOLD", function () {
# post:     const status = responseData.data?.status;
# post:     
# post:     pm.expect(status, "data.status 字段不存在").to.be.a('string');
# post:     pm.expect(status).to.eql("ON_HOLD");
# post: 
# post:     console.log(" status 断言成功，当前值为:", status);
# post: });
# --- step 11: aebe025b-b18e-4701-b839-832a224e758a ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应状态码断言
# post: pm.test("响应message 为 success", function () {
# post:     pm.expect(responseData.message).to.eql("success");
# post: });
# post: 
# post: // 3. 断言 lifecycleStatus 与 status 字段
# post: pm.test("断言 status 为 ACTIVE 且 lifecycleStatus 为 LIFECYCLE_STATUS_ON_HOLD", function () {
# post:     const data = responseData.data;
# post:     pm.expect(data, "data 对象不存在").to.be.an('object');
# post: 
# post:     // 断言 status
# post:     pm.expect(data.status, "status 值不等于 ACTIVE").to.eql("ACTIVE");
# post: 
# post:     // 断言 lifecycleStatus
# post:     pm.expect(data.lifecycleStatus, "lifecycleStatus 值不等于 LIFECYCLE_STATUS_ON_HOLD").to.eql("LIFECYCLE_STATUS_ON_HOLD");
# post: 
# post:     console.log(`断言通过: status=${data.status}, lifecycleStatus=${data.lifecycleStatus}`);
# post: });
# post: 
# post: // 4. 提取 data.id 并设置为环境变量 productId
# post: pm.test("提取 data.id 并设置为环境变量 productId", function () {
# post:     const idValue = responseData.data?.id;
# post:     pm.expect(idValue, "data.id 不存在或为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 设置环境变量 productId
# post:     pm.environment.set("productId", idValue);
# post: 
# post:     console.log("已成功将 data.id 设置为环境变量 productId:", idValue);
# post: });
# --- step 12: ede1c307-aff2-4b87-a848-a21a181c7832 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 13: df7a27c2-2d97-48ff-87ea-86664d852da8 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 查找 title 为 "ticket on hold" 的目标产品
# post: const targetProduct = responseData.data.relatedProducts.find(
# post:     item => item.title === "ticket on hold"
# post: );
# post: 
# post: // 3. 断言并提取 displayVariantId 为环境变量 promoterProductId
# post: pm.test("找到目标产品并提取 displayVariantId 作为 promoterProductId", function () {
# post:     // 断言目标产品存在
# post:     pm.expect(targetProduct, "未找到目标产品").to.not.be.undefined;
# post:     pm.expect(targetProduct.displayVariantId).to.be.a('string').and.not.empty;
# post: 
# post:     // 获取 displayVariantId
# post:     const targetVariantId = targetProduct.displayVariantId;
# post: 
# post:     // 设置为环境变量 promoterProductId
# post:     pm.environment.set("promoterProductId", targetVariantId);
# post:     console.log("已成功将 displayVariantId 设置为 promoterProductId:", targetVariantId);
# post: });
# post: 
# post: // 4. 新增：断言并提取 merchantProductVariantId 为环境变量 merchantProductVariantId
# post: pm.test("提取 merchantProductVariantId 作为环境变量", function () {
# post:     // 断言 variants 数组存在且不为空
# post:     pm.expect(targetProduct.variants, "variants 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post:     
# post:     // 获取第一个 variant 的 merchantProductVariantId
# post:     const merchantProductVariantId = targetProduct.variants[0].merchantProductVariantId;
# post:     
# post:     // 断言获取到的 ID 格式正常
# post:     pm.expect(merchantProductVariantId).to.be.a('string').and.not.empty;
# post: 
# post:     // 设置环境变量
# post:     pm.environment.set("merchantProductVariantId", merchantProductVariantId);
# post:     console.log("已成功将 merchantProductVariantId 设置为环境变量:", merchantProductVariantId);
# post: });
# --- step 14: e0be15d0-ecb6-43e3-bae4-69810fd15ef2 ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 15: 6a63e37a-9371-40bb-a030-afe77af30aa0 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 16: buy now ---
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 17: 4295886c-6402-40b0-a39c-73db7a874f7b ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 状态码与异常响应断言
# post: pm.test("响应状态码为 400 且 code 为 400", function () {
# post:     pm.response.to.have.status(400);
# post:     pm.expect(responseData.code).to.eql(400);
# post: });
# post: 
# post: // 3. 断言 message 返回正确的错误提示信息
# post: pm.test("断言 message 为商品不可用提示", function () {
# post:     // 精确匹配
# post:     pm.expect(responseData.message).to.eql("The product(ticket on hold)is not available.");
# post:     
# post:     // 包含关键信息的泛化匹配（可选，防止商品名称变动导致断言失败）
# post:     pm.expect(responseData.message).to.include("is not available.");
# post: 
# post:     console.log("错误信息断言成功，实际 message 为:", responseData.message);
# post: });
# --- step 18: ae434884-2837-49a2-a94f-355beb0683e5 ---
# post[customScript]: // 1. Parse the response JSON
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: const items = data.items || [];
# post: 
# post: // --- 1. Assertions for Response Logic ---
# post: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: pm.test("Response contains shipping items", function () {
# post:     pm.expect(response.message).to.eql("success");
# post:     pm.expect(items).to.be.an('array').that.is.not.empty;
# post:     pm.expect(data.totalCount).to.be.at.least(1);
# post: });
# post: 
# post: // --- 2. Assertion for Item Details ---
# post: pm.test("Verify default shipping details", function () {
# post:     const firstItem = items[0];
# post:     pm.expect(firstItem.title).to.eql("Flat Shipping");
# post:     pm.expect(firstItem.shippingFee).to.eql(4.99);
# post:     pm.expect(firstItem.isDefault).to.be.true;
# post: });
# post: 
# post: // --- 3. Extract shipping_option_id ---
# post: pm.test("Extract shipping_option_id to environment", function () {
# post:     const shippingId = items[0].id;
# post:     
# post:     // Ensure ID is valid before setting
# post:     pm.expect(shippingId).to.be.a('string').and.not.empty;
# post:     
# post:     // Set environment variable
# post:     pm.environment.set("shipping_option_id", shippingId);
# post:     
# post:     console.log("Successfully extracted shipping_option_id: " + shippingId);
# post: });
# --- step 19: c4dc4dbe-13c6-4e92-adf9-8419218f554d ---
# post[customScript]: pm.test("Status is CANCELED", function () {
# post:     var jsonData = pm.response.json();
# post:     pm.expect(jsonData.data.status).to.eql("CANCELED");
# post: });
# --- step 20: bdbbe12c-9544-4aa7-8c41-e9e11c242c41 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 状态码与异常响应断言
# post: pm.test("响应状态码为 400 且 code 为 400", function () {
# post:     pm.response.to.have.status(400);
# post:     pm.expect(responseData.code).to.eql(400);
# post: });
# post: 
# post: // 3. 断言 message 返回正确的错误提示信息
# post: pm.test("断言 message 为商品不可用提示", function () {
# post:     // 精确匹配
# post:     pm.expect(responseData.message).to.eql("The product(ticket on hold)is not available.");
# post:     
# post:     // 包含关键信息的泛化匹配（可选，防止商品名称变动导致断言失败）
# post:     pm.expect(responseData.message).to.include("is not available.");
# post: 
# post:     console.log("错误信息断言成功，实际 message 为:", responseData.message);
# post: });
# --- step 21: 25adfc9b-e1a0-42fa-a968-a2b8b8401cd9 ---
# post[customScript]: pm.test("Status is CANCELED", function () {
# post:     var jsonData = pm.response.json();
# post:     pm.expect(jsonData.data.status).to.eql("COMPLETED");
# post: });
# --- step 22: daf51c48-ca74-4e09-b3d4-e1742c173f58 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 24: 5b75a378-b2bd-4139-866f-1b291c50dbbf ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 25: buy now ---
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 26: place order ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础状态码与通用字段断言
# post: pm.test("响应message 为 success", function () {
# post:     pm.expect(responseData.message, "message 不为 success").to.eql("success");
# post: });
# post: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 27: c1a42e8d-0063-45b1-b9a3-5803214ff8fb ---
# post[customScript]: pm.test("Status is CANCELED", function () {
# post:     var jsonData = pm.response.json();
# post:     pm.expect(jsonData.data.status).to.eql("COMPLETED");
# post: });
# --- step 28: 153154e0-221e-4615-acde-5662193081aa ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "400", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "Cannot revert an event that has sales.", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 29: 0ad73083-c17d-4069-a02c-0ca61a6507ba ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应状态断言
# post: pm.test("响应状态码为 200 且 message 为 success", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post: });
# post: 
# post: // 3. 断言 data 字段值为 "ok"
# post: pm.test("断言 data 字段返回为 ok", function () {
# post:     pm.expect(responseData.data).to.eql("ok");
# post:     console.log("接口返回验证通过，data 值为:", responseData.data);
# post: });
# --- step 30: e69a5388-6d49-4619-be84-53577e16d996 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应状态断言
# post: pm.test("响应状态码为 200 且 message 为 success", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post: });
# post: 
# post: // 3. 断言 data 字段值为 "ok"
# post: pm.test("断言 data 字段返回为 ok", function () {
# post:     pm.expect(responseData.data).to.eql("ok");
# post:     console.log("接口返回验证通过，data 值为:", responseData.data);
# post: });




import json

from typing import Any, TYPE_CHECKING

from core.assertions import expect

from core.compat import get_path as _get_path

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t4180_t4724_verify_the_event_can_create_and_duplicate_and_delete_and_switch_status(ctx: "Context"):
    """Apifox case #8620470: Linda_T4180_T4724_Verify_the_Event_can_create_and_duplicate_and_delete_and_switc"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # restored from dropped Apifox step-8 pre-script:
    # pm.environment.set("event_title", "Duplicate Verify the Event can create and duplicate and delete success")
    vars['event_title'] = 'Duplicate Verify the Event can create and duplicate and delete success'
    # === Steps ===
    # step 1: 31523ce3-41cd-44be-8ce5-322acb4d98d9
    _resp1 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    vars['catalog_id'] = (_resp1.json().get('data', {}) or {}).get('id')
    # step 2: Partner Create event
    _resp2 = ctx.api.events.v2(body={
        "ignoreStartTime": True,
        "ignoreEndTime": True,
        "isTimeUnspecified": False,
        "allowAutoComplete": True,
        "description": "",
        "note": "linda note",
        "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",
        "status": "UPCOMING",
        "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
        "isTaxEnabled": False,
        "isAddressRevealEnabled": False,
        "title": "Verify the Event can create and duplicate and delete success",
        "venue": "Instagram Live, Zoom, In-person",
        "timezone": {
            "timeZoneId": "America/Chicago",
            "timeZoneName": "Central Daylight Time",
            "dstOffset": 3600,
            "rawOffset": -21600,
        },
        "poster": {
            "height": 2048,
            "width": 3072,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "mediaType": "IMAGE",
        },
        "startDateDisplay": "2053-04-17",
        "styleSettings": {
            "fontFamily": "Inter",
            "color": "#FFFFFF",
            "backgroundColor": "#000000",
            "borderColor": "#000000",
            "dividerColor": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "announcementCarousel": {
                "color": "#000000",
                "backgroundColor": "#F6CA7C",
            },
            "title": {
                "color": "#F6CA7C",
                "fontFamily": "Inter",
                "fontSize": 24,
                "fontWeight": 700,
            },
            "columnTitle": {
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 700,
                "color": "#FFFFFF",
            },
            "subtitle": {
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 400,
                "color": "#FFFFFF",
            },
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000",
                "borderColor": "#000000",
                "borderRadius": 12,
                "boxShadow": "none",
                "fontSize": 16,
                "fontWeight": 700,
            },
            "secondaryButton": {
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF",
                "borderColor": "#F6CA7C",
                "borderRadius": 12,
                "boxShadow": "none",
            },
            "textButton": {
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF",
            },
            "selectButton": {
                "borderColor": "#000000",
            },
            "relatedLink": {
                "borderRadius": 99,
                "color": "#000000 ",
                "borderColor": "#0000",
                "backgroundColor": "#FAFAFA",
            },
            "featuredProducts": {
                "borderRadius": 16,
                "backgroundColor": "#000000",
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 14,
                    "fontWeight": 400,
                    "color": "#FFFFFF",
                },
            },
            "product": {
                "backgroundColor": "#000000",
                "borderRadius": 8,
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
            },
            "discount": {
                "backgroundColor": "#D32A09",
                "color": "#FFFFFF",
                "priceColor": "#FFFFFF",
            },
            "freeShipping": {
                "backgroundColor": "#EBF5EF",
                "color": "#268E46",
            },
            "starRatingColor": "#FAAF03",
            "layoutFeatureCard": {
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 16,
                    "fontWeight": 700,
                    "color": "#FFFFFF",
                },
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "button": {
                    "backgroundColor": "#F6CA7C",
                    "color": "#000000",
                },
            },
            "lineupBanner": {
                "titleText": "#FFFFFF",
                "descriptionText": "#E0E0E0",
            },
            "eventInfoBanner": {
                "text": "#FFFFFF",
                "secondaryText": "#E0E0E0",
            },
            "eventDescription": {
                "text": "#E0E0E0",
                "title": "#FFFFFF",
            },
        },
    }, token='yuxiao999_token')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    vars['created_event_id'] = (_resp2.json().get('data', {}) or {}).get('id')
    # step 3: e3e0b07b-ca07-46cd-81c9-a3944c74547e
    _resp3 = ctx.api.events.v2_media_batch_create(body={
        "poster": {
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "width": 3072,
            "height": 2048,
            "position": 0,
            "mediaType": "IMAGE",
            "mediaDuration": 0,
        },
        "posterBackend": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                "width": 3072,
                "height": 2048,
                "position": 0,
                "mediaType": "IMAGE",
                "mediaDuration": 0,
            },
        ],
        "medias": [],
        "mediaTextConfig": {
            "headline": "Missed our last event?",
            "subtitle": "Here's a lil recap of our last eventð",
            "align": "center",
        },
    }, token='yuxiao999_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # step 4: 78adc986-7caf-46cc-ab7b-42b010e77f12
    _resp4 = ctx.api.products.calculate_ticket_batch(body={
        "listingType": "TICKET",
        "customTaxRate": 10,
        "items": [
            {
                "variants": [
                    {
                        "ticketPrice": 5,
                        "overrideEventTax": False,
                        "customTaxRate": 0,
                        "overrideEventCustomFee": False,
                        "transactionCustomFeeConfig": None,
                    },
                ],
            },
            {
                "variants": [
                    {
                        "ticketPrice": 10,
                        "overrideEventTax": False,
                        "customTaxRate": 0,
                        "overrideEventCustomFee": False,
                        "transactionCustomFeeConfig": None,
                    },
                ],
            },
        ],
        "customFeeConfig": {
            "isEnabled": True,
            "items": [
                {
                    "title": "custom fee",
                    "unitFixedFee": 0,
                    "unitPercentageFee": 0.1,
                },
            ],
        },
    }, token='yuxiao999_token')
    # step 5: 6b136fb9-5b69-4781-8a2b-c4d0a0925f61
    _resp5 = ctx.api.events.v2_ticket_batch_v2(body={
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'listingType': 'TICKET',
    'isTaxEnabled': True,
    'taxConfig': {
        'calculationType': 'CUSTOM',
        'customTaxRate': 10,
    },
    'autoReplace': True,
    'tickets': [
        {
            'listingType': 'TICKET',
            'ticketType': 'TICKET_TYPE_STANDARD',
            'images': [
                {
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'width': 3072,
                    'height': 2048,
                    'position': 0,
                    'mediaType': 'IMAGE',
                    'mediaDuration': 0,
                },
            ],
            'title': 'Early Bird',
            'bodyJson': '',
            'options': [
                {
                    'name': 'Title',
                    'values': [
                        'Default Title',
                    ],
                    'images': [],
                },
            ],
            'variants': [
                {
                    'inventoryQuantity': 50,
                    'ticketPrice': 5,
                    'price': 8.57,
                    'fees': 3.57,
                    'priceAnchor': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'transactionFee': {
                        'platformFee': 1.85,
                        'customFee': 1.72,
                        'customFeeBreakdown': {
                            'custom_custom fee_1': {
                                'title': 'custom fee',
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0.1,
                                'index': 1,
                                'itemFee': 0.86,
                            },
                            'TAX': {
                                'title': 'Taxes',
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0.1,
                                'index': 0,
                                'itemFee': 0.86,
                            },
                        },
                        'transactionItemFee': 3.57,
                    },
                    'minPriceForCheckFees': 0,
                    'isSlotWindowEnabled': False,
                    'ignoreStartTime': False,
                    'ignoreEndTime': False,
                    'slotWindow': None,
                    'isMinPurchaseQuantityEnabled': True,
                    'isMaxPurchaseQuantityEnabled': True,
                    'isPackSizeEnabled': True,
                    'minPurchaseQuantity': 2,
                    'maxPurchaseQuantity': 5,
                    'packSize': 3,
                },
            ],
            'useEventPosterAsCover': True,
        },
    ],
    'coSellingCommissionRate': 0,
    'customFeeConfig': {
        'isEnabled': True,
        'items': [
            {
                'title': 'custom fee',
                'unitFixedFee': 0,
                'unitPercentageFee': 0.1,
            },
        ],
    },
}, token='yuxiao999_token', path_vars={'event_id': '{{created_event_id}}'})
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson equal success
    expect(_resp5).json('$.message').equals('success')
    # step 6: 1f79ab2a-5352-49f4-a445-96accf653e08
    _resp6 = ctx.api.events.v2_lineup_batch(body={
        "lineup": [
            {
                "title": "lineup",
                "poster": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",
                    "width": 160,
                    "height": 160,
                    "mediaType": "IMAGE",
                },
                "introduction": "001",
                "isHeadliner": False,
                "posterBackend": [
                    {
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",
                        "width": 160,
                        "height": 160,
                        "mediaType": "IMAGE",
                    },
                ],
                "order": 0,
            },
        ],
    }, token='yuxiao999_token', path_vars={'event_id': '{{created_event_id}}'})
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    _d6: dict[str, Any] = _resp6.json().get('data', {}) or {}
    _tk6 = (_d6.get('tickets') or [{}])[0]
    vars['ticket_id'] = _tk6.get('id')
    vars['variant_id'] = (_tk6.get('variants') or [{}])[0].get('id')
    # step 7: a94879d6-2c75-4727-a315-996b5f67b588
    _resp7 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    _d7: dict[str, Any] = _resp7.json().get('data', {}) or {}
    _items7: list[Any] = _d7.get('items') or []
    _target7 = next((i for i in _items7 if i.get('title') == 'Verify the Event can create and duplicate and delete success'), None)
    vars['event_id'] = _target7.get('id') if _target7 else None
    # step 8: 33516490-440b-4838-a47f-1461996a3f0f
    # === pre-script（由 Apifox customScript 翻译）===
    vars['event_title'] = "Duplicate Verify the Event can create and duplicate and delete success"

    _resp8 = ctx.api.events.v2_duplicate(body={
    'title': '{{event_title}}',
    'curatorId': '{{catalog_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2053-04-17T05:00:00.000Z',
    'endDate': None,
    'venue': 'Instagram Live, Zoom, In-person',
    'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
    'status': 'UPCOMING',
    'isTaxEnabled': True,
    'taxConfig': {
        'customTaxRate': 10,
        'calculationType': 'CUSTOM',
        'configUpdatedAt': '2026-08-12T08:22:35.111Z',
    },
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap of our last event👇",
        'align': 'center',
    },
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2053-04-17',
    'note': 'linda note',
    'timezone': {
        'timeZoneId': 'America/Chicago',
        'timeZoneName': 'Central Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -21600,
    },
    'isAddressRevealEnabled': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'PEAR',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Chicago',
        'line1': '789 River East Art Center Promenade',
        'line2': '',
        'state': 'IL',
        'country': 'US',
        'placeId': None,
        'zipcode': None,
        'stateName': 'Illinois',
        'stripeLocationId': None,
    },
    'country': 'US',
    'state': 'IL',
    'autoReplace': True,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'excludeOnsiteSalesFromReport': False,
    'venueMapId': None,
    'ticketHubInfo': None,
    'readOnlyFields': [],
    'medias': [],
    'tickets': [
        {
            'id': '{{ticket_id}}',
            'remote_id': None,
            'platform': 'PEAR',
            'createdAt': '2026-08-12T08:22:35.128Z',
            'updatedAt': '2026-08-12T08:22:35.146Z',
            'merchantId': 'eb05c2a1-6b2d-4715-bcde-f17573ec82e9',
            'title': 'Early Bird',
            'bodyHtml': '',
            'originalBodyHtml': '',
            'isBodyHtmlOverridden': False,
            'bodyText': '',
            'handle': None,
            'productType': '',
            'publishedAt': '2026-08-12T08:22:35.141Z',
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
            'inventoryQuantity': 50,
            'inventoryQuantityOriginal': 50,
            'soldQuantity': 0,
            'priceDisplay': 8.57,
            'priceDisplayAnchor': 0,
            'priceMin': 8.57,
            'priceMinAnchor': 0,
            'priceMax': 8.57,
            'priceMaxAnchor': 0,
            'priceImportedMin': 0,
            'priceImportedMax': 0,
            'imageCount': 1,
            'isUsed': 'NWT',
            'shippingType': 'NO_SHIPPING_REQUIRED',
            'additionalShippingFee': 0,
            'deliveryTime': [
                0,
                5,
            ],
            'returnPolicyApplied': True,
            'isAvailable': True,
            'commissionRate': 0,
            'textForShare': None,
            'priceSyncImported': False,
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'useEventPosterAsCover': True,
            'reviewCount': None,
            'reviewOverallScore': None,
            'reviewAggregate': None,
            'displayReviews': True,
            'links': None,
            'taxEnable': True,
            'taxJarCategory': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'subscriptionPlanId': None,
            'reviewRedirectProductId': None,
            'reviewSummary': None,
            'customFieldsInfo': None,
            'listingType': 'TICKET',
            'ticketType': 'TICKET_TYPE_STANDARD',
            'extraInfo': {
                'date': 'Thu Apr 17, 2053 CDT',
                'event': 'Verify the Event can create and duplicate and delete success',
                'venue': 'Instagram Live, Zoom, In-person',
                'lineup': [],
                'poster': {
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'width': 3072,
                    'height': 2048,
                    'position': 0,
                    'mediaType': 'IMAGE',
                    'mediaDuration': 0,
                },
                'status': 'UPCOMING',
                'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
                'eventNote': 'linda note',
                'startDate': '2053-04-17T05:00:00.000Z',
                'timeZoneId': 'America/Chicago',
                'isAddressHidden': False,
                'addressRevealConfig': None,
            },
            'ticketHubInfo': None,
            'bodyJson': None,
            'shippingOptions': None,
            'shippingNote': None,
            'autoFulfill': True,
            'eventId': '{{event_id}}',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'copyFromId': 'd803da14-0ec6-415e-a00d-470853354452',
            'stopSellingAfter': None,
            'stopSellingAfterDisplay': None,
            'deliveryMethod': 'QR_CODE',
            'thirdPartyDeliveryMessage': None,
            'isMultipleDaysPassEnabled': False,
            'isVenueUnitEnabled': False,
            'multipleDaysPass': None,
            'isPickupEtaEnabled': None,
            'eventMatchingRules': None,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'allowAtDoorSales': False,
            'isProductFormEnabled': False,
            'isVariantPriceDisplayEnabled': False,
            'isTipEnabled': False,
            'hideFees': False,
            'isPlatformFeeConfigCustomized': False,
            'isVariantPlatformFeeConfigCustomized': False,
            'transactionFeeConfig': {
                'baseConfig': {
                    'unitFixedFee': 1,
                    'unitPercentageFee': 0.1,
                },
            },
            'transactionFeeRebateConfig': {
                'baseConfig': {
                    'unitFixedFee': 0,
                    'unitPercentageFee': 0,
                },
            },
            'transactionCustomFeeConfig': None,
            'overrideEventCustomFee': False,
            'isInclusionsEnabled': False,
            'images': [
                {
                    'id': '3ff228a7-6e14-4653-8fc5-7965f06c2efc',
                    'remote_id': None,
                    'createdAt': '2026-08-12T08:22:35.146Z',
                    'updatedAt': '2026-08-12T08:22:35.146Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{ticket_id}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'name': 'Title',
                    'images': [
                        {
                            'value': 'Default Title',
                            'image': None,
                        },
                    ],
                },
            ],
            'variants': [
                {
                    'id': '{{variant_id}}',
                    'remote_id': None,
                    'createdAt': '2026-08-12T08:22:35.146Z',
                    'updatedAt': '2026-08-12T08:22:35.146Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 50,
                    'inventoryQuantityOriginal': 50,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '8.57',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{ticket_id}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
                    'platform': None,
                    'fees': 3.57,
                    'transactionFee': {
                        'customFee': 1.72,
                        'platformFee': 1.85,
                        'customFeeBreakdown': {
                            'TAX': {
                                'index': 0,
                                'title': 'Taxes',
                                'itemFee': 0.86,
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0.1,
                            },
                            'custom_custom fee_1': {
                                'index': 1,
                                'title': 'custom fee',
                                'itemFee': 0.86,
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0.1,
                            },
                        },
                        'transactionItemFee': 3.57,
                    },
                    'ticketPrice': 5,
                    'isMinPurchaseQuantityEnabled': True,
                    'minPurchaseQuantity': 2,
                    'isMaxPurchaseQuantityEnabled': True,
                    'maxPurchaseQuantity': 5,
                    'isPackSizeEnabled': True,
                    'packSize': 3,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                    'image': None,
                },
            ],
            'inclusions': [],
            'productForm': None,
        },
    ],
    'lineup': [
        {
            'eventId': '{{event_id}}',
            'title': 'lineup',
            'introduction': '001',
            'poster': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf',
                'width': 160,
                'height': 160,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'order': 0,
            'isHeadliner': False,
            'createdAt': '2026-08-12T08:22:35.605Z',
            'updatedAt': '2026-08-12T08:22:35.605Z',
            'id': '6cc3508d-61d0-42dd-b940-de7c5844b7c7',
        },
    ],
    'eventProducts': [],
    'ignoreStartTime': True,
    'ignoreEndTime': True,
    'duplicateEventId': '{{event_id}}',
    'posterBackend': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
            'height': 2048,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': {
        'items': [
            {
                'title': 'custom fee',
                'unitFixedFee': 0,
                'unitPercentageFee': 0.1,
            },
        ],
        'isEnabled': True,
    },
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'WarmAtelier',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'fontFamily': 'Inter',
        'color': '#2C2623',
        'backgroundColor': '#EDE7E2',
        'borderColor': '#EDE7E2',
        'dividerColor': '#858585',
        'secondaryTextColor': '#7A6F68',
        'announcementCarousel': {
            'color': '#2C2623',
            'backgroundColor': '#DDD4CF',
        },
        'title': {
            'color': '#2C2623',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 800,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#4A403B',
        },
        'subtitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#000000',
        },
        'button': {
            'fontSize': 16,
            'fontWeight': 400,
            'color': '#FFFFFF',
            'backgroundColor': '#B77A4A',
            'borderRadius': 0,
            'borderColor': '#0000',
            'boxShadow': 'none',
        },
        'secondaryButton': {
            'fontSize': 16,
            'fontWeight': 400,
            'color': '#2C2623',
            'borderRadius': 0,
            'borderColor': '#B77A4A',
            'boxShadow': 'none',
        },
        'textButton': {
            'fontSize': 16,
            'fontWeight': 700,
            'color': '#B77A4A',
        },
        'selectButton': {
            'borderColor': '#C1C1C3',
        },
        'relatedLink': {
            'backgroundColor': '#DDD4CF',
            'borderColor': '#0000',
            'color': '#2C2623',
            'borderRadius': 0,
        },
        'featuredProducts': {
            'borderRadius': 0,
            'backgroundColor': '#DDD4CF',
            'color': '#2C2623',
            'secondaryTextColor': '#4A403B',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#2C2623',
            },
        },
        'product': {
            'backgroundColor': '#DDD4CF',
            'borderRadius': 0,
            'color': '#2C2623',
            'secondaryTextColor': '#4A403B',
        },
        'discount': {
            'backgroundColor': '#D32A08',
            'color': '#FFFFFF',
            'priceColor': '#C06E38',
        },
        'freeShipping': {
            'backgroundColor': '#EBF5EF',
            'color': '#268E46',
        },
        'starRatingColor': '#FAAF00',
        'layoutFeatureCard': {
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 16,
                'fontWeight': 700,
                'color': '#FFFFFF',
            },
            'color': '#FFFFFF',
            'secondaryTextColor': '#5D5D5D',
            'button': {
                'backgroundColor': '#B77A4A',
                'color': '#2C2623',
            },
        },
        'lineupBanner': {
            'titleText': '#2C2623',
            'descriptionText': '#7A6F68',
        },
        'eventInfoBanner': {
            'text': '#4A403B',
            'secondaryText': '#7A6F68',
        },
        'eventDescription': {
            'text': '#000000',
            'title': '#000000',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#110921',
            '#ECA416',
            '#FFEEBE',
            '#0000',
            '#0D0D14',
            '#2D2108',
            '#5D5D5D',
            '#CBBE9C',
            '#000000',
            '#EDA415',
            '#FFFFFF',
            '#CFCFCF',
            '#ABABAB',
            '#C1C1C3',
            '#858585',
            '#F6CA7C',
            '#E0E0E0',
        ],
    },
}, token='yuxiao999_token')
    _d8: dict[str, Any] = _resp8.json().get('data', {}) or {}
    vars['dup_event_id'] = _d8.get('id')
    vars['lineup_id'] = (_d8.get('lineup') or [{}])[0].get('id')
    # step 9: db5f22cf-c39a-4076-923d-1f60f4c0c4d8
    _resp9 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
    _d9: dict[str, Any] = _resp9.json().get('data', {}) or {}
    _items9: list[Any] = _d9.get('items') or []
    # Apifox 原文按 `item.title === event_title` 精确匹配。实测服务端「复制事件」后自动生成的
    # post 有时把新标题只落在 `headline` 上、`title` 仍是源事件标题，于是精确匹配偶发失败，
    # 表现为 postId=None → 下游 request body 里残留未渲染的 "{{postId}}"
    # → 400 `posts.0.postId must be a UUID`（全量跑时命中，单跑则通过）。
    # 这里放宽为 title/headline 任一命中，再退化为「列表唯一项」，并显式断言，
    # 避免静默把 None 发出去。
    _target9 = (next((i for i in _items9 if i.get('title') == vars.get('event_title')), None)
                or next((i for i in _items9 if i.get('headline') == vars.get('event_title')), None)
                or (_items9[0] if len(_items9) == 1 else None))
    assert _target9, (f"step9 未能在事件 {vars.get('dup_event_id')} 的 posts 中找到目标 post"
                      f"（items={len(_items9)}）")
    vars['postId'] = _target9.get('id')
    # step 10: 6ee46b75-9a00-4f23-9767-b88d0e800310
    _resp10 = ctx.api.events.by_dup_event_id(body={
        "id": "{{dup_event_id}}",
        "title": "{{event_title}}",
        "curatorId": "{{catalog_id}}",
        "description": "",
        "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
        "startDate": "2053-04-17T05:00:00.000Z",
        "endDate": None,
        "venue": "Instagram Live, Zoom, In-person",
        "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",
        "status": "ON_HOLD",
        "isTaxEnabled": True,
        "taxConfig": {
            "calculationType": "CUSTOM",
            "configUpdatedAt": "2026-08-12T09:03:30.384Z",
            "customTaxRate": 10,
        },
        "mediaTextConfig": {
            "headline": "Missed our last event?",
            "subtitle": "Here's a lil recap of our last eventð",
            "align": "center",
        },
        "poster": {
            "height": 2048,
            "mediaDuration": 0,
            "mediaType": "IMAGE",
            "position": 0,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "width": 3072,
        },
        "startDateDisplay": "2053-04-17",
        "note": "linda note",
        "timezone": {
            "timeZoneId": "America/Chicago",
            "timeZoneName": "Central Daylight Time",
            "dstOffset": 3600,
            "rawOffset": -21600,
        },
        "isAddressRevealEnabled": False,
        "messageInfo": {
            "cooldownMinutes": 15,
            "emailMaxLimit": 5,
            "smsMaxLimit": 3,
        },
        "platform": "PEAR",
        "creationStep": "COMPLETED",
        "extraInfo": None,
        "locationDetails": {
            "city": "Chicago",
            "country": "US",
            "line1": "789 River East Art Center Promenade",
            "line2": "",
            "placeId": None,
            "state": "IL",
            "stateName": "Illinois",
            "stripeLocationId": None,
            "zipcode": None,
        },
        "country": "US",
        "state": "IL",
        "autoReplace": True,
        "lineupTransactionId": None,
        "lineupTransactionStatus": None,
        "autoPayLineupStatus": "PENDING",
        "venueMapId": None,
        "ticketHubInfo": None,
        "readOnlyFields": [],
        "medias": [],
        "tickets": [],
        "lineup": [
            {
                "title": "lineup",
                "introduction": "001",
                "poster": {
                    "height": 160,
                    "mediaDuration": 0,
                    "mediaType": "IMAGE",
                    "position": 0,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",
                    "width": 160,
                },
                "isHeadliner": False,
                "order": 0,
                "isPaymentAfterEventEnabled": False,
                "id": "{{lineup_id}}",
            },
        ],
        "eventProducts": [],
        "products": [],
        "statistics": {
            "totalAvailableTickets": 0,
            "totalSoldTickets": 0,
            "totalRedeemedTickets": 0,
            "totalTickets": 0,
            "totalMerch": 0,
            "totalSoldMerch": 0,
            "totalAvailableMerch": 0,
            "totalRedeemedMerch": 0,
        },
        "hasPaidSales": False,
        "accessType": "OWNER",
        "ignoreStartTime": True,
        "ignoreEndTime": True,
        "posterBackend": [
            {
                "height": 2048,
                "mediaDuration": 0,
                "mediaType": "IMAGE",
                "position": 0,
                "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                "width": 3072,
            },
        ],
        "customFeeConfig": {
            "isEnabled": True,
            "items": [
                {
                    "title": "custom fee",
                    "unitFixedFee": 0,
                    "unitPercentageFee": 0.1,
                },
            ],
        },
        "allowAutoComplete": True,
        "styleSettings": {
            "template": "ClearSky",
            "themeName": "WarmAtelier",
            "layout": {
                "pageHeader": {
                    "style": "DEDICATED_HEADER_BAR",
                    "displayText": "SHOP_NAME",
                    "height": "MEDIUM",
                },
                "productBanner": {
                    "ctaButton": "VIEW_PRODUCT",
                    "display": "HIDE",
                },
            },
            "fontFamily": "Inter",
            "color": "#2C2623",
            "backgroundColor": "#EDE7E2",
            "borderColor": "#EDE7E2",
            "dividerColor": "#858585",
            "secondaryTextColor": "#7A6F68",
            "announcementCarousel": {
                "color": "#2C2623",
                "backgroundColor": "#DDD4CF",
            },
            "title": {
                "color": "#2C2623",
                "fontFamily": "Inter",
                "fontSize": 24,
                "fontWeight": 800,
            },
            "columnTitle": {
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 700,
                "color": "#4A403B",
            },
            "subtitle": {
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 700,
                "color": "#000000",
            },
            "button": {
                "fontSize": 16,
                "fontWeight": 400,
                "color": "#FFFFFF",
                "backgroundColor": "#B77A4A",
                "borderRadius": 0,
                "borderColor": "#0000",
                "boxShadow": "none",
            },
            "secondaryButton": {
                "fontSize": 16,
                "fontWeight": 400,
                "color": "#2C2623",
                "borderRadius": 0,
                "borderColor": "#B77A4A",
                "boxShadow": "none",
            },
            "textButton": {
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#B77A4A",
            },
            "selectButton": {
                "borderColor": "#C1C1C3",
            },
            "relatedLink": {
                "backgroundColor": "#DDD4CF",
                "borderColor": "#0000",
                "color": "#2C2623",
                "borderRadius": 0,
            },
            "featuredProducts": {
                "borderRadius": 0,
                "backgroundColor": "#DDD4CF",
                "color": "#2C2623",
                "secondaryTextColor": "#4A403B",
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 14,
                    "fontWeight": 400,
                    "color": "#2C2623",
                },
            },
            "product": {
                "backgroundColor": "#DDD4CF",
                "borderRadius": 0,
                "color": "#2C2623",
                "secondaryTextColor": "#4A403B",
            },
            "discount": {
                "backgroundColor": "#D32A08",
                "color": "#FFFFFF",
                "priceColor": "#C06E38",
            },
            "freeShipping": {
                "backgroundColor": "#EBF5EF",
                "color": "#268E46",
            },
            "starRatingColor": "#FAAF00",
            "layoutFeatureCard": {
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 16,
                    "fontWeight": 700,
                    "color": "#FFFFFF",
                },
                "color": "#FFFFFF",
                "secondaryTextColor": "#5D5D5D",
                "button": {
                    "backgroundColor": "#B77A4A",
                    "color": "#2C2623",
                },
            },
            "lineupBanner": {
                "titleText": "#2C2623",
                "descriptionText": "#7A6F68",
            },
            "eventInfoBanner": {
                "text": "#4A403B",
                "secondaryText": "#7A6F68",
            },
            "eventDescription": {
                "text": "#000000",
                "title": "#000000",
            },
            "featuredProduct": {
                "cover": {
                    "borderRadius": 0,
                },
            },
            "recentUsedColors": [
                "#110921",
                "#ECA416",
                "#FFEEBE",
                "#0000",
                "#0D0D14",
                "#2D2108",
                "#5D5D5D",
                "#CBBE9C",
                "#000000",
                "#EDA415",
                "#FFFFFF",
                "#CFCFCF",
                "#ABABAB",
                "#C1C1C3",
                "#858585",
                "#F6CA7C",
                "#E0E0E0",
            ],
        },
    }, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 11: aebe025b-b18e-4701-b839-832a224e758a
    _resp11 = ctx.api.products.create(body={
    'merchantId': '{{catalog_id}}',
    'shippingType': 'NO_SHIPPING_REQUIRED',
    'isFeatured': False,
    'commissionRate': 0,
    'priceSyncImported': False,
    'additionalShippingFee': 0,
    'returnPolicyApplied': True,
    'title': 'ticket on hold',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'status': 'ACTIVE',
    'isUsed': 'NWT',
    'taxJarCategory': '',
    'platform': 'PEAR',
    'autoFulfill': True,
    'options': [
        {
            'name': 'Title',
            'values': [
                'Default Title',
            ],
            'images': [],
        },
    ],
    'variants': [
        {
            'inventoryQuantity': 10,
            'price': 0,
            'priceAnchor': 0,
            'option': {
                'option1': 'Default Title',
            },
            'fees': 0,
            'ticketPrice': 0,
            'transactionFee': {
                'platformFee': 0,
                'customFee': 0,
                'customFeeBreakdown': {},
                'transactionItemFee': 0,
            },
            'minPriceForCheckFees': 0,
            'weightUnit': 'lb',
        },
    ],
    'listingType': 'TICKET',
    'ticketType': 'TICKET_TYPE_STANDARD',
    'soldQuantity': 0,
    'excludeFromPostSync': False,
    'isTipEnabled': False,
    'useEventPosterAsCover': True,
    'catalogCommissionRate': 0,
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'taxEnable': True,
    'customTaxRate': None,
    'earliestTime': '2026-08-12T09:32:07.963Z',
    'styleSettings': {
        'recentUsedColors': [
            '#110921',
            '#ECA416',
            '#FFEEBE',
            '#0000',
            '#0D0D14',
            '#2D2108',
            '#5D5D5D',
            '#CBBE9C',
            '#000000',
            '#EDA415',
            '#FFFFFF',
            '#CFCFCF',
            '#ABABAB',
            '#C1C1C3',
            '#858585',
            '#F6CA7C',
            '#E0E0E0',
        ],
    },
    'isInclusionsEnabled': False,
    'inclusions': [],
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'extraInfo': {
        'businessTimezone': 'America/Los_Angeles',
    },
    'overrideEventTax': False,
    'overrideEventCustomFee': False,
    'hideFees': False,
    'transactionCustomFeeConfig': None,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'height': 2048,
            'mediaDuration': 0,
            'mediaType': 'IMAGE',
            'position': 0,
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
        },
    ],
    'eventId': '{{dup_event_id}}',
    'isExpirationEnabled': False,
}, token='yuxiao999_token')
    vars['productId'] = (_resp11.json().get('data', {}) or {}).get('id')
    # step 12: ede1c307-aff2-4b87-a848-a21a181c7832
    _resp12 = ctx.api.events.v2_show_in_post(body={
        "productIds": [
            "{{productId}}",
        ],
        "posts": [
            {
                "postId": "{{postId}}",
                "isVisible": True,
            },
        ],
    }, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
    # assertion 12.assertion: responseJson equal 200
    expect(_resp12).json('$.code').equals('200')
    # step 13: df7a27c2-2d97-48ff-87ea-86664d852da8
    _resp13 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token', path_vars={'post0_id': '{{postId}}'})
    _d13: dict[str, Any] = _resp13.json().get('data', {}) or {}
    _rels13: list[Any] = _d13.get('relatedProducts') or []
    _tp13 = next((p for p in _rels13 if p.get('title') == 'ticket on hold'), None)
    vars['promoterProductId'] = _tp13.get('displayVariantId') if _tp13 else None
    _j: dict[str, Any] = _resp13.json() if _resp13.headers.get('content-type','').startswith('application/json') else {}
    vars['merchantProductVariantId'] = _get_path(_j, ['data', 'relatedProducts', 0, 'variants', 0, 'merchantProductVariantId'])
    # step 14: e0be15d0-ecb6-43e3-bae4-69810fd15ef2
    _resp14 = ctx.api.auth.guest_login(body={
        "consumerId": "{{__uuid_0}}",
    })
    vars['access_token'] = (_resp14.json() if _resp14.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 15: 6a63e37a-9371-40bb-a030-afe77af30aa0
    _resp15 = ctx.api.cart.delete(body={}, app_headers=True, token='access_token')
    # assertion 15.assertion: responseJson equal 200
    expect(_resp15).json('$.code').equals('200')
    # assertion 15.assertion: responseJson equal success
    expect(_resp15).json('$.message').equals('success')
    # step 16: buy now
    _resp16 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "{{postId}}",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 2,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "{{event_id}}",
            "pixelId": [
                "test",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "{{productId}}",
                "postId": "{{postId}}",
                "price": 2,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='access_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp16, '$.data.orderId')
    # step 17: 4295886c-6402-40b0-a39c-73db7a874f7b
    _resp17 = ctx.api.orders.checkout_express(body={
        "items": [
            {
                "quantity": 3,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 8.57,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "{{dup_event_id}}",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1786526453224.334258892692108835",
            "externalId": "b0b0ed9c-8bc8-426f-b590-9a97f10dcd24",
            "eventSourceUrl": "https://release.pear.us/autotestshop/post/duplicate-verify-the-event-can-create-and-duplicate-and-delete-success",
        },
        "subdomainVanityUrl": "",
    }, app_headers=True, token='access_token')
    # step 18: ae434884-2837-49a2-a94f-355beb0683e5
    _resp18 = ctx.api.merchants.shipping_options(body=None, token='yuxiao999_token')
    _d18: dict[str, Any] = _resp18.json().get('data', {}) or {}
    _items18: list[Any] = _d18.get('items') or []
    vars['shipping_option_id'] = _items18[0].get('id') if _items18 else None
    # step 19: c4dc4dbe-13c6-4e92-adf9-8419218f554d
    _resp19 = ctx.api.events.by_dup_event_id(body={
    'id': '{{dup_event_id}}',
    'title': '{{event_title}}',
    'curatorId': '{{catalog_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2053-04-17T05:00:00.000Z',
    'endDate': None,
    'venue': 'Instagram Live, Zoom, In-person',
    'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
    'status': 'CANCELED',
    'isTaxEnabled': True,
    'taxConfig': {
        'customTaxRate': 10,
        'calculationType': 'CUSTOM',
        'configUpdatedAt': '2026-08-14T02:04:30.036Z',
    },
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap of our last event👇",
        'align': 'center',
    },
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2053-04-17',
    'note': 'linda note',
    'timezone': {
        'timeZoneId': 'America/Chicago',
        'timeZoneName': 'Central Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -21600,
    },
    'isAddressRevealEnabled': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'PEAR',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Chicago',
        'line1': '789 River East Art Center Promenade',
        'line2': None,
        'state': 'IL',
        'country': 'US',
        'placeId': None,
        'zipcode': None,
        'stateName': 'Illinois',
        'stripeLocationId': None,
    },
    'country': 'US',
    'state': 'IL',
    'autoReplace': True,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'venueMapId': None,
    'ticketHubInfo': None,
    'readOnlyFields': [],
    'medias': [],
    'tickets': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
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
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_ON_HOLD',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
            'copyFromId': '{{productId}}',
        },
    ],
    'lineup': [
        {
            'title': 'lineup',
            'introduction': '001',
            'poster': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf',
                'width': 160,
                'height': 160,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'isHeadliner': False,
            'order': 0,
            'isPaymentAfterEventEnabled': False,
            'id': 'ae6d0a8a-221b-4bec-8ada-f2fea16b4443',
        },
    ],
    'eventProducts': [],
    'products': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
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
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_ON_HOLD',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
        },
    ],
    'statistics': {
        'totalAvailableTickets': 10,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
        'totalTickets': 10,
        'totalMerch': 0,
        'totalSoldMerch': 0,
        'totalAvailableMerch': 0,
        'totalRedeemedMerch': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': True,
    'ignoreEndTime': True,
    'posterBackend': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
            'height': 2048,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': {
        'isEnabled': True,
        'items': [
            {
                'title': 'custom fee',
                'unitFixedFee': 0,
                'unitPercentageFee': 0.1,
            },
        ],
    },
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'MidnightGlow',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'dividerColor': '#5D5D5D',
        'secondaryTextColor': '#E0E0E0',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 700,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'subtitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 400,
            'color': '#FFFFFF',
        },
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderColor': '#000000',
            'borderRadius': 0,
            'boxShadow': 'none',
            'fontSize': 16,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'fontSize': 16,
            'fontWeight': 400,
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'boxShadow': 'none',
        },
        'textButton': {
            'fontSize': 16,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'selectButton': {
            'borderColor': '#000000',
        },
        'relatedLink': {
            'borderRadius': 0,
            'color': '#000000 ',
            'borderColor': '#0000',
            'backgroundColor': '#FAFAFA',
        },
        'featuredProducts': {
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'product': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
        },
        'discount': {
            'backgroundColor': '#D32A09',
            'color': '#FFFFFF',
            'priceColor': '#FFFFFF',
        },
        'freeShipping': {
            'backgroundColor': '#EBF5EF',
            'color': '#268E46',
        },
        'starRatingColor': '#FAAF03',
        'layoutFeatureCard': {
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 16,
                'fontWeight': 700,
                'color': '#FFFFFF',
            },
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'button': {
                'backgroundColor': '#F6CA7C',
                'color': '#000000',
            },
        },
        'lineupBanner': {
            'titleText': '#FFFFFF',
            'descriptionText': '#E0E0E0',
        },
        'eventInfoBanner': {
            'text': '#FFFFFF',
            'secondaryText': '#E0E0E0',
        },
        'eventDescription': {
            'text': '#E0E0E0',
            'title': '#FFFFFF',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#ffffff',
        ],
    },
}, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 20: bdbbe12c-9544-4aa7-8c41-e9e11c242c41
    _resp20 = ctx.api.orders.checkout_express(body={
        "items": [
            {
                "quantity": 3,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 8.57,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "{{dup_event_id}}",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1786526453224.334258892692108835",
            "externalId": "b0b0ed9c-8bc8-426f-b590-9a97f10dcd24",
            "eventSourceUrl": "https://release.pear.us/autotestshop/post/duplicate-verify-the-event-can-create-and-duplicate-and-delete-success",
        },
        "subdomainVanityUrl": "",
    }, app_headers=True, token='access_token')
    # step 21: 25adfc9b-e1a0-42fa-a968-a2b8b8401cd9
    _resp21 = ctx.api.events.by_dup_event_id(body={
    'id': '{{dup_event_id}}',
    'title': '{{event_title}}',
    'curatorId': '{{catalog_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2053-04-17T05:00:00.000Z',
    'endDate': None,
    'venue': 'Instagram Live, Zoom, In-person',
    'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
    'status': 'COMPLETED',
    'isTaxEnabled': True,
    'taxConfig': {
        'customTaxRate': 10,
        'calculationType': 'CUSTOM',
        'configUpdatedAt': '2026-08-14T02:04:30.036Z',
    },
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap of our last event👇",
        'align': 'center',
    },
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2053-04-17',
    'note': 'linda note',
    'timezone': {
        'timeZoneId': 'America/Chicago',
        'timeZoneName': 'Central Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -21600,
    },
    'isAddressRevealEnabled': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'PEAR',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Chicago',
        'line1': '789 River East Art Center Promenade',
        'line2': None,
        'state': 'IL',
        'country': 'US',
        'placeId': None,
        'zipcode': None,
        'stateName': 'Illinois',
        'stripeLocationId': None,
    },
    'country': 'US',
    'state': 'IL',
    'autoReplace': True,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'venueMapId': None,
    'ticketHubInfo': None,
    'readOnlyFields': [],
    'medias': [],
    'tickets': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
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
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_CANCELED',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
            'copyFromId': '{{productId}}',
        },
    ],
    'lineup': [
        {
            'title': 'lineup',
            'introduction': '001',
            'poster': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf',
                'width': 160,
                'height': 160,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'isHeadliner': False,
            'order': 0,
            'isPaymentAfterEventEnabled': False,
            'id': 'ae6d0a8a-221b-4bec-8ada-f2fea16b4443',
        },
    ],
    'eventProducts': [],
    'products': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
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
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_CANCELED',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
        },
    ],
    'statistics': {
        'totalAvailableTickets': 10,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
        'totalTickets': 10,
        'totalMerch': 0,
        'totalSoldMerch': 0,
        'totalAvailableMerch': 0,
        'totalRedeemedMerch': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': True,
    'ignoreEndTime': True,
    'posterBackend': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
            'height': 2048,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': {
        'isEnabled': True,
        'items': [
            {
                'title': 'custom fee',
                'unitFixedFee': 0,
                'unitPercentageFee': 0.1,
            },
        ],
    },
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'MidnightGlow',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'dividerColor': '#5D5D5D',
        'secondaryTextColor': '#E0E0E0',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 700,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'subtitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 400,
            'color': '#FFFFFF',
        },
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderColor': '#000000',
            'borderRadius': 0,
            'boxShadow': 'none',
            'fontSize': 16,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'fontSize': 16,
            'fontWeight': 400,
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'boxShadow': 'none',
        },
        'textButton': {
            'fontSize': 16,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'selectButton': {
            'borderColor': '#000000',
        },
        'relatedLink': {
            'borderRadius': 0,
            'color': '#000000 ',
            'borderColor': '#0000',
            'backgroundColor': '#FAFAFA',
        },
        'featuredProducts': {
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'product': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
        },
        'discount': {
            'backgroundColor': '#D32A09',
            'color': '#FFFFFF',
            'priceColor': '#FFFFFF',
        },
        'freeShipping': {
            'backgroundColor': '#EBF5EF',
            'color': '#268E46',
        },
        'starRatingColor': '#FAAF03',
        'layoutFeatureCard': {
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 16,
                'fontWeight': 700,
                'color': '#FFFFFF',
            },
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'button': {
                'backgroundColor': '#F6CA7C',
                'color': '#000000',
            },
        },
        'lineupBanner': {
            'titleText': '#FFFFFF',
            'descriptionText': '#E0E0E0',
        },
        'eventInfoBanner': {
            'text': '#FFFFFF',
            'secondaryText': '#E0E0E0',
        },
        'eventDescription': {
            'text': '#E0E0E0',
            'title': '#FFFFFF',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#ffffff',
        ],
    },
}, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 22: daf51c48-ca74-4e09-b3d4-e1742c173f58
    _resp22 = ctx.api.admin.events_by_dup_event_id(body={
        "status": "UPCOMING",
    }, token='admin_token')
    # assertion 22.assertion: responseJson equal 200
    expect(_resp22).json('$.code').equals('200')
    # assertion 22.assertion: responseJson equal success
    expect(_resp22).json('$.message').equals('success')
    # step 24: 5b75a378-b2bd-4139-866f-1b291c50dbbf
    _resp24 = ctx.api.cart.delete(body={}, app_headers=True, token='access_token')
    # assertion 24.assertion: responseJson equal 200
    expect(_resp24).json('$.code').equals('200')
    # assertion 24.assertion: responseJson equal success
    expect(_resp24).json('$.message').equals('success')
    # step 25: buy now
    _resp25 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "{{postId}}",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 2,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "{{event_id}}",
            "pixelId": [
                "test",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "{{productId}}",
                "postId": "{{postId}}",
                "price": 2,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='access_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp25, '$.data.orderId')
    # step 26: place order
    _resp26 = ctx.api.orders.create(body={
        "inviterCampaign": {},
        "id": "{{orderId}}",
        "contact": {
            "email": "{{$internet.email(locale='en')}}",
            "firstName": "test",
            "lastName": "linda",
            "phoneNumber": "+16502396646",
        },
        "fbAdParams": {
            "eventID": "586718a7-e342-4210-88b9-280e6cb3a836",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1769653368885.141808310869967644",
            "externalId": "b7090865-489e-4861-9aa3-d7760e80ee16",
            "eventSourceUrl": "https://hui.staging.pear.us/lury-merchant/post/300-orders-automation",
        },
    }, app_headers=True, token='access_token')
    # assertion 26.assertion: responseJson equal success
    expect(_resp26).json('$.message').equals('success')
    # step 27: c1a42e8d-0063-45b1-b9a3-5803214ff8fb
    _resp27 = ctx.api.events.by_dup_event_id(body={
    'id': '{{dup_event_id}}',
    'title': '{{event_title}}',
    'curatorId': '{{catalog_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2053-04-17T05:00:00.000Z',
    'endDate': None,
    'venue': 'Instagram Live, Zoom, In-person',
    'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
    'status': 'COMPLETED',
    'isTaxEnabled': True,
    'taxConfig': {
        'customTaxRate': 10,
        'calculationType': 'CUSTOM',
        'configUpdatedAt': '2026-08-14T02:04:30.036Z',
    },
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap of our last event👇",
        'align': 'center',
    },
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2053-04-17',
    'note': 'linda note',
    'timezone': {
        'timeZoneId': 'America/Chicago',
        'timeZoneName': 'Central Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -21600,
    },
    'isAddressRevealEnabled': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'PEAR',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Chicago',
        'line1': '789 River East Art Center Promenade',
        'line2': None,
        'state': 'IL',
        'country': 'US',
        'placeId': None,
        'zipcode': None,
        'stateName': 'Illinois',
        'stripeLocationId': None,
    },
    'country': 'US',
    'state': 'IL',
    'autoReplace': True,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'venueMapId': None,
    'ticketHubInfo': None,
    'readOnlyFields': [],
    'medias': [],
    'tickets': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
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
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_CANCELED',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
            'copyFromId': '{{productId}}',
        },
    ],
    'lineup': [
        {
            'title': 'lineup',
            'introduction': '001',
            'poster': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf',
                'width': 160,
                'height': 160,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'isHeadliner': False,
            'order': 0,
            'isPaymentAfterEventEnabled': False,
            'id': 'ae6d0a8a-221b-4bec-8ada-f2fea16b4443',
        },
    ],
    'eventProducts': [],
    'products': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
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
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_CANCELED',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
        },
    ],
    'statistics': {
        'totalAvailableTickets': 10,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
        'totalTickets': 10,
        'totalMerch': 0,
        'totalSoldMerch': 0,
        'totalAvailableMerch': 0,
        'totalRedeemedMerch': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': True,
    'ignoreEndTime': True,
    'posterBackend': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
            'height': 2048,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': {
        'isEnabled': True,
        'items': [
            {
                'title': 'custom fee',
                'unitFixedFee': 0,
                'unitPercentageFee': 0.1,
            },
        ],
    },
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'MidnightGlow',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'dividerColor': '#5D5D5D',
        'secondaryTextColor': '#E0E0E0',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 700,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'subtitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 400,
            'color': '#FFFFFF',
        },
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderColor': '#000000',
            'borderRadius': 0,
            'boxShadow': 'none',
            'fontSize': 16,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'fontSize': 16,
            'fontWeight': 400,
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'boxShadow': 'none',
        },
        'textButton': {
            'fontSize': 16,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'selectButton': {
            'borderColor': '#000000',
        },
        'relatedLink': {
            'borderRadius': 0,
            'color': '#000000 ',
            'borderColor': '#0000',
            'backgroundColor': '#FAFAFA',
        },
        'featuredProducts': {
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'product': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
        },
        'discount': {
            'backgroundColor': '#D32A09',
            'color': '#FFFFFF',
            'priceColor': '#FFFFFF',
        },
        'freeShipping': {
            'backgroundColor': '#EBF5EF',
            'color': '#268E46',
        },
        'starRatingColor': '#FAAF03',
        'layoutFeatureCard': {
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 16,
                'fontWeight': 700,
                'color': '#FFFFFF',
            },
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'button': {
                'backgroundColor': '#F6CA7C',
                'color': '#000000',
            },
        },
        'lineupBanner': {
            'titleText': '#FFFFFF',
            'descriptionText': '#E0E0E0',
        },
        'eventInfoBanner': {
            'text': '#FFFFFF',
            'secondaryText': '#E0E0E0',
        },
        'eventDescription': {
            'text': '#E0E0E0',
            'title': '#FFFFFF',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#ffffff',
        ],
    },
}, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 28: 153154e0-221e-4615-acde-5662193081aa
    _resp28 = ctx.api.admin.events_by_dup_event_id(body={
        "status": "UPCOMING",
    }, token='admin_token')
    # assertion 28.assertion: responseJson equal 400
    expect(_resp28).json('$.code').equals('400')
    # assertion 28.assertion: responseJson equal Cannot revert an event that has sales.
    expect(_resp28).json('$.message').equals('Cannot revert an event that has sales.')
    # step 29: 0ad73083-c17d-4069-a02c-0ca61a6507ba
    _resp29 = ctx.api.events.by_event_id(body=None, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
    # step 30: e69a5388-6d49-4619-be84-53577e16d996
    _resp30 = ctx.api.events.by_event_id(body=None, token='yuxiao999_token')
