"""Auto-generated from Apifox case #8709247. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 8709247
# Folder: 
# Case: (Linda)(AXS)T4180&T4724 Verify the Event can create and duplicate and delete and switch status
# Priority: P1
# Created: 2026-09-04T09:54:59.000Z
# Updated: 2026-09-07T07:42:12.000Z


CASE_ID = 8709247
ENV_NAME = "Release"

# --- step 1: 79fd31fa-6a2e-4ec3-b070-60ac93210027 ---
# post[customScript]: // 1. 解析响应 Body
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 查找第一个 platform 为 "AXS" 的项目
# post: const axsEvent = responseData.data?.items?.find(item => item.platform === "AXS");
# post: 
# post: if (axsEvent) {
# post:     // 3. 设置 event_id 和 event_title 环境变量
# post:     pm.environment.set("event_id", axsEvent.id);
# post:     pm.environment.set("event_title", axsEvent.title);
# post: 
# post:     // 4. 提取首个 ticket 的 id 并保存为 copyFromId 环境变量
# post:     const copyFromId = axsEvent.tickets?.[0]?.id;
# post:     if (copyFromId) {
# post:         pm.environment.set("copyFromId", copyFromId);
# post:         console.log("成功提取 copyFromId：", copyFromId);
# post:     } else {
# post:         console.warn("未在该 AXS 项目下找到 tickets 数据");
# post:     }
# post: 
# post:     console.log("成功提取第一个 AXS 项目：", axsEvent.title, axsEvent.id);
# post: } else {
# post:     console.warn("未找到 platform 为 AXS 的数据");
# post: }
# --- step 2: cb92454b-5c3f-41bc-a204-17c47db601f0 ---
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
# --- step 3: 7722151d-7d59-4d5e-b875-a462da878e63 ---
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
# --- step 4: 3d38a45e-afec-4e75-8ad7-6338b5b7f6fc ---
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
# --- step 5: 5df31978-26c0-47bb-b668-d909ba23f7ed ---
# post[customScript]: // 1. 解析响应 Body
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 获取 productForm 对象
# post: const productForm = responseData.data?.product?.productForm;
# post: 
# post: // 3. 校验并存入环境变量
# post: if (productForm) {
# post:     // 将对象转为 JSON 字符串保存，方便在其他接口的 Request Body 中使用 {{productForm}}
# post:     pm.environment.set("productForm", JSON.stringify(productForm));
# post:     
# post:     console.log("成功提取 productForm 并存入环境变量：", productForm);
# post: } else {
# post:     console.warn("未在响应中找到 productForm 数据");
# post: }
# --- step 6: 96a11731-2fab-4457-8fc6-5b9912ed7f25 ---
# post[customScript]: try {
# post:     // 1. Parse the response JSON
# post:     var res = pm.response.json();
# post: 
# post:     // 2. Check if the items array exists and has at least one element
# post:     if (res.code === 200 && res.data && res.data.items && res.data.items.length > 0) {
# post:         
# post:         // 3. Extract the ID from the first item
# post:         var userId = res.data.items[0].id;
# post: 
# post:         // 4. Set the environment variable
# post:         pm.environment.set("user_id", userId);
# post: 
# post:         console.log("✅ Successfully extracted user_id: " + userId);
# post:     } else {
# post:         // If no user found, clear the variable to prevent logic errors
# post:         pm.environment.set("user_id", "");
# post:         console.warn("⚠️ No items found in response, user_id cleared.");
# post:     }
# post: } catch (e) {
# post:     console.error("Critical Error: Failed to parse items. " + e.message);
# post: }
# --- step 7: 46f46103-0698-46bb-8a31-851caf142fb6 ---
# pre: pm.environment.set("dul_event_title", "Duplicate Verify the AXS Event can create and duplicate and delete success");
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
# --- step 8: 49b770d0-3b1c-46eb-95ef-3bf4753fe5b1 ---
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
# --- step 9: 9775d52a-d543-4ead-8304-d92610b7ef8a ---
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
# --- step 10: 103a0db8-3d7f-4727-bb53-8a1ce5bf2abf ---
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
# --- step 11: 08306796-68a5-4c06-a064-41c855cb0242 ---
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
# --- step 12: 5e4763c0-213e-44d1-8ee0-15b388f36e32 ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 13: dd0455dd-1414-4f26-a71f-3cca80014da1 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 14: buy now ---
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 15: 33e4ab76-4fed-456c-85a4-6b1dd506eee7 ---
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
# --- step 16: 173d3229-281b-4285-bb4e-e8bcd5130909 ---
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
# --- step 17: 02bc9b66-ffbb-48ad-8d30-5b3b3764e578 ---
# post[customScript]: pm.test("Status is CANCELED", function () {
# post:     var jsonData = pm.response.json();
# post:     pm.expect(jsonData.data.status).to.eql("CANCELED");
# post: });
# --- step 18: 75dff304-6214-495f-bf52-0a136cbde768 ---
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
# --- step 19: d5d0f651-78ac-463f-b146-4ce5144867a6 ---
# post[customScript]: pm.test("Status is CANCELED", function () {
# post:     var jsonData = pm.response.json();
# post:     pm.expect(jsonData.data.status).to.eql("COMPLETED");
# post: });
# --- step 20: d46477ce-b6a0-431f-b0b4-877659fccc15 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 22: 50179345-fab4-45fb-a25d-70424adae873 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 23: buy now ---
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 24: place order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(90.49);
# post: });
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础状态码与通用字段断言
# post: pm.test("响应message 为 success", function () {
# post:     pm.expect(responseData.message, "message 不为 success").to.eql("success");
# post: });
# post: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 25: fdb455cc-78a7-4b08-91a7-1da4b9960204 ---
# post[customScript]: pm.test("Status is CANCELED", function () {
# post:     var jsonData = pm.response.json();
# post:     pm.expect(jsonData.data.status).to.eql("COMPLETED");
# post: });
# --- step 26: 486e02b9-ce12-4f83-87f4-1013d87bd6f5 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "400", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "Cannot revert an event that has sales.", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 27: 67d12801-155f-4437-9c63-7142fc198c99 ---
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

from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test__8709247__Linda_AXS_T4180_T4724_Verify_the_Event_can_create_and_duplicate_and_delete_and_switch_status(ctx: "Context"):
    from core.compat import get_path as _get_path
    """Apifox case #8709247: Linda_AXS_T4180_T4724_Verify_the_Event_can_create_and_duplicate_and_delete_and_s"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: 79fd31fa-6a2e-4ec3-b070-60ac93210027
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    vars['event_id'] = 'axsEvent.id'
    vars['event_title'] = 'axsEvent.title'
    vars['copyFromId'] = 'copyFromId'
    # step 2: cb92454b-5c3f-41bc-a204-17c47db601f0
    _resp2 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    vars['catalog_id'] = 'catalogId'
    # step 3: 7722151d-7d59-4d5e-b875-a462da878e63
    _resp3 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    _post0id_val = _get_path(_resp3.json(), ['data', 'items', 0, 'id'])
    vars['post0_id'] = _post0id_val if _post0id_val is not None else ''
    # step 4: 3d38a45e-afec-4e75-8ad7-6338b5b7f6fc
    _resp4 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    vars['ticket_title'] = 'ticketTitle'
    vars['productId'] = 'productId'
    vars['promoterProductId'] = 'promoterProductId'
    vars['merchantProductVariantId'] = 'merchantProductVariantId'
    vars['displayVariantId'] = 'displayVariantId'
    vars['ticketHubInfo_id'] = 'ticketHubInfo_id'
    vars['ticketHandle'] = 'ticketHandle'
    vars['availableQuantity'] = 'availableQuantity'
    vars['sectionIds'] = 'sectionIds'
    # step 5: 5df31978-26c0-47bb-b668-d909ba23f7ed
    _resp5 = ctx.api.products.by_product_id_2(body=None, token='yuxiao999_token')
    vars['productForm'] = 'JSON.stringify(productForm'
    # step 6: 96a11731-2fab-4457-8fc6-5b9912ed7f25
    _resp6 = ctx.api.admin.users_search(body={
        "query": "{{UIauto_partner_email}}",
        "filter": {
            "userRoles": [
                "PROMOTER",
                "BUSINESS_PARTNER",
            ],
            "userType": "ALL",
        },
        "pageSize": 100,
        "pageNumber": 1,
    }, token='admin_token')
    vars['user_id'] = 'userId'
    vars['user_id'] = ''
    vars['dul_event_title'] = 'Duplicate Verify the AXS Event can create and duplicate and delete success'
    # step 7: 46f46103-0698-46bb-8a31-851caf142fb6
    # === pre-script（由 Apifox customScript 翻译）===
    vars['dul_event_title'] = "Duplicate Verify the AXS Event can create and duplicate and delete success"

    _resp7 = ctx.api.events.v2_duplicate(body={
    'title': '{{dul_event_title}}',
    'curatorId': '{{user_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"This event has a tiered pricing structure in the General Admission area. All General Admission tiers have the same access. Once a price level sells out it may no longer be visible or available for selection. *Please note: multiple GA price levels may be available at the same time The event organizer has decided that ticket transfer will be delayed for this event. Ticket transfer will be available on or about three weeks prior to the event. Please review the terms of AXS’s Purchase Agreement for more information.","type":"extended-text","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2027-11-07T02:00:00.000Z',
    'endDate': '2027-12-01T05:15:00.000Z',
    'venue': 'Agora Theatre',
    'location': 'Cleveland, OH, United States',
    'status': 'UPCOMING',
    'isTaxEnabled': False,
    'taxConfig': None,
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap. Make sure you buy, tickets SOLD OUT last event!",
        'align': 'center',
    },
    'poster': {
        'src': 'https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
        'width': 1200,
        'height': 630,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2027-11-06 21:00',
    'endDateDisplay': '2027-12-01 00:15',
    'note': '{{dul_event_title}',
    'timezone': {
        'timeZoneId': 'America/New_York',
        'timeZoneName': 'Eastern Standard Time',
        'dstOffset': 0,
        'rawOffset': -18000,
    },
    'isAddressRevealEnabled': False,
    'isAddressHidden': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'AXS',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Cleveland',
        'line1': None,
        'line2': None,
        'state': 'OH',
        'country': 'United States',
        'placeId': None,
        'zipcode': None,
        'stateName': 'OH',
        'stripeLocationId': None,
    },
    'country': 'United States',
    'state': 'OH',
    'autoReplace': False,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'excludeOnsiteSalesFromReport': False,
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'venueMapId': None,
    'ticketHubInfo': {
        'contextId': '517840254',
        'contextDesc': 'AEG Great Lakes',
        'eventHandle': 'eyJwbGF0Zm9ybSI6IkFYUyIsImh1YklkIjoiYy1wS2o5Ujk1d0Z1bWl0RmNUYXFIb283dVNCcHktaXlRTmdNTFNGZnNybyJ9',
    },
    'readOnlyFields': [
        'tax',
        'customFees',
        'duplicateTicket',
        'addTicket',
        'addMerch',
        'duplicateMerch',
    ],
    'medias': [],
    'tickets': [
        {
            'id': '{{productId}}',
            'remote_id': None,
            'platform': 'AXS',
            'createdAt': '2026-09-03T09:44:42.495Z',
            'updatedAt': '2026-09-04T09:28:40.780Z',
            'merchantId': 'e1229bad-fb18-44b2-ac23-c4c3c1b5c3c3',
            'title': 'General Admission — Pear.US',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'isBodyHtmlOverridden': False,
            'bodyText': '\n',
            'handle': None,
            'productType': '',
            'publishedAt': '2026-09-03T09:44:42.508Z',
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
            'inventoryQuantity': '{{availableQuantity}}',
            'inventoryQuantityOriginal': '{{availableQuantity}}',
            'soldQuantity': 0,
            'priceDisplay': 55.88,
            'priceDisplayAnchor': 0,
            'priceMin': 55.88,
            'priceMinAnchor': 0,
            'priceMax': 55.88,
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
                'src': 'https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
                'width': 1200,
                'height': 630,
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
            'taxEnable': False,
            'taxJarCategory': '',
            'overrideEventTax': False,
            'customTaxRate': None,
            'subscriptionPlanId': None,
            'reviewRedirectProductId': None,
            'reviewSummary': None,
            'customFieldsInfo': None,
            'listingType': 'TICKET',
            'ticketType': 'TICKET_TYPE_STANDARD',
            'extraInfo': {
                'date': 'Fri Nov 6, 2026 9PM - Tue Dec 1, 12:15AM EST',
                'event': 'Zack Fox (DJ Set)',
                'venue': 'Agora Theatre',
                'lineup': [],
                'poster': {
                    'src': 'https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
                    'width': 1200,
                    'height': 630,
                    'position': 0,
                    'mediaType': 'IMAGE',
                    'mediaDuration': 0,
                },
                'status': 'UPCOMING',
                'endDate': '2026-12-01T05:15:00.000Z',
                'location': 'Cleveland, OH, United States',
                'eventNote': '',
                'startDate': '2026-11-07T02:00:00.000Z',
                'timeZoneId': 'America/New_York',
                'isAddressHidden': False,
                'addressRevealConfig': None,
            },
            'ticketHubInfo': {
                'ticketHandle': '{{ticketHubInfo_id}}',
                'priceSyncedAt': '2026-09-03T09:44:42.350Z',
                'sectionOptions': [
                    {
                        'label': 'GeneralAdmission',
                        'price': {
                            'amount': 4930,
                            'currency': 'USD',
                        },
                        'quantityRule': {
                            'max': 4,
                            'min': 1,
                            'step': 1,
                        },
                        'ticketHandle': '{{ticketHandle}}',
                        'availableQuantity': '{{availableQuantity}}',
                        'isGeneralAdmission': True,
                    },
                ],
            },
            'customizedFields': [],
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'shippingOptions': [],
            'shippingNote': None,
            'autoFulfill': True,
            'eventId': '{{event_id}}',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'copyFromId': '{{productId}}',
            'stopSellingAfter': None,
            'stopSellingAfterDisplay': None,
            'deliveryMethod': 'THIRD_PARTY_ISSUED',
            'thirdPartyDeliveryMessage': 'Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.',
            'isMultipleDaysPassEnabled': False,
            'isVenueUnitEnabled': False,
            'venueUnitCategoryId': None,
            'multipleDaysPass': None,
            'isPickupEtaEnabled': None,
            'eventMatchingRules': None,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'allowAtDoorSales': False,
            'isProductFormEnabled': True,
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
                    'id': '7b9ef5e8-a5ff-4d9b-95fc-7f75872008a9',
                    'remote_id': None,
                    'createdAt': '2026-09-03T09:44:42.518Z',
                    'updatedAt': '2026-09-03T09:44:42.518Z',
                    'height': 1000,
                    'width': 1000,
                    'position': 1,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png',
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
                    'id': '3{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-09-03T09:44:42.518Z',
                    'updatedAt': '2026-09-03T09:44:42.518Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': '{{availableQuantity}}',
                    'inventoryQuantityOriginal': '{{availableQuantity}}',
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '55.88',
                    'priceAnchor': '0.00',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 6.58,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 6.58,
                        'customFeeBreakdown': {
                            'TAX': {
                                'index': 0,
                                'title': 'Taxes',
                                'itemFee': 0,
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0,
                            },
                        },
                        'transactionItemFee': 6.58,
                    },
                    'ticketPrice': 49.3,
                    'isMinPurchaseQuantityEnabled': True,
                    'minPurchaseQuantity': 1,
                    'isMaxPurchaseQuantityEnabled': True,
                    'maxPurchaseQuantity': 4,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                    'image': None,
                },
            ],
            'inclusions': [],
            'productForm': '{{productForm}}',
        },
    ],
    'lineup': [],
    'eventProducts': [],
    'ignoreStartTime': False,
    'ignoreEndTime': False,
    'duplicateEventId': '{{event_id}}',
    'posterBackend': [
        {
            'src': 'https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
            'width': 1200,
            'height': 630,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': None,
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
        'version': 'v2',
        'backgroundColor': '#000000',
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
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'dividerColor': '#5D5D5D',
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderRadius': 0,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'fontWeight': 400,
        },
        'product': {
            'borderRadius': 0,
        },
        'featuredProducts': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'relatedLink': {
            'backgroundColor': '#FAFAFA',
            'color': '#000000 ',
            'borderRadius': 0,
        },
        'announcementCarousel': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#7132F4',
            '#FFFFFF',
        ],
    },
}, token='yuxiao999_token')
    _dupeventid_val = _get_path(_resp7.json(), ['data', 'id'])
    vars['dup_event_id'] = _dupeventid_val if _dupeventid_val is not None else ''
    _lineupid_val = _get_path(_resp7.json(), ['data', 'lineup', 0, 'id'])
    vars['lineup_id'] = _lineupid_val if _lineupid_val is not None else ''
    # step 8: 49b770d0-3b1c-46eb-95ef-3bf4753fe5b1
    _resp8 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
    _post0id_val = _get_path(_resp8.json(), ['data', 'items', 0, 'id'])
    vars['post0_id'] = _post0id_val if _post0id_val is not None else ''
    # step 9: 9775d52a-d543-4ead-8304-d92610b7ef8a
    _resp9 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    vars['ticket_title'] = 'ticketTitle'
    vars['productId'] = 'productId'
    vars['promoterProductId'] = 'promoterProductId'
    vars['merchantProductVariantId'] = 'merchantProductVariantId'
    vars['displayVariantId'] = 'displayVariantId'
    vars['ticketHubInfo_id'] = 'ticketHubInfo_id'
    vars['ticketHandle'] = 'ticketHandle'
    vars['availableQuantity'] = 'availableQuantity'
    vars['sectionIds'] = 'sectionIds'
    # step 10: 103a0db8-3d7f-4727-bb53-8a1ce5bf2abf
    _resp10 = ctx.api.events.by_dup_event_id(body={
    'id': '{{dup_event_id}}',
    'title': '{{dul_event_title}}',
    'curatorId': '{{user_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"This event has a tiered pricing structure in the General Admission area. All General Admission tiers have the same access. Once a price level sells out it may no longer be visible or available for selection. *Please note: multiple GA price levels may be available at the same time The event organizer has decided that ticket transfer will be delayed for this event. Ticket transfer will be available on or about three weeks prior to the event. Please review the terms of AXS’s Purchase Agreement for more information.","type":"extended-text","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2027-11-07T01:00:00.000Z',
    'endDate': '2027-12-01T05:15:00.000Z',
    'venue': 'Agora Theatre',
    'location': 'Cleveland, OH, United States',
    'status': 'ON_HOLD',
    'isTaxEnabled': False,
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap. Make sure you buy, tickets SOLD OUT last event!",
        'align': 'center',
    },
    'poster': {
        'height': 630,
        'mediaDuration': 0,
        'mediaType': 'IMAGE',
        'position': 0,
        'src': 'https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
        'width': 1200,
    },
    'startDateDisplay': '2027-11-06 21:00',
    'endDateDisplay': '2027-12-01 00:15',
    'note': '{{dul_event_title}}',
    'timezone': {
        'timeZoneId': 'America/New_York',
        'timeZoneName': 'Eastern Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -18000,
    },
    'isAddressRevealEnabled': False,
    'isAddressHidden': False,
    'messageInfo': {
        'cooldownMinutes': 15,
        'emailMaxLimit': 5,
        'smsMaxLimit': 3,
    },
    'platform': 'AXS',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Cleveland',
        'country': 'United States',
        'line1': None,
        'line2': None,
        'placeId': None,
        'state': 'OH',
        'stateName': 'OH',
        'stripeLocationId': None,
        'zipcode': None,
    },
    'country': 'United States',
    'state': 'OH',
    'autoReplace': False,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'ticketHubInfo': {
        'contextDesc': 'AEG Great Lakes',
        'contextId': '517840254',
        'eventHandle': 'eyJwbGF0Zm9ybSI6IkFYUyIsImh1YklkIjoiYy1wS2o5Ujk1d0Z1bWl0RmNUYXFIb283dVNCcHktaXlRTmdNTFNGZnNybyJ9',
    },
    'readOnlyFields': [
        'tax',
        'customFees',
        'duplicateTicket',
        'addTicket',
        'addMerch',
        'duplicateMerch',
    ],
    'medias': [],
    'tickets': [
        {
            'id': '{{productId}}',
            'title': 'General Admission — Pear.US',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'height': 630,
                'mediaDuration': 0,
                'mediaType': 'IMAGE',
                'position': 0,
                'src': 'https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
                'width': 1200,
            },
            'inventoryQuantity': 82,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 55.88,
            'priceMax': 55.88,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'contributedBy': 3,
                    'contributorId': None,
                    'createdAt': '2026-09-07T03:49:37.677Z',
                    'height': 1000,
                    'id': '6ca3d3dc-34f3-4898-84ca-e8a7776a757c',
                    'mediaDuration': 0,
                    'mediaSrc': None,
                    'mediaType': 'IMAGE',
                    'position': 1,
                    'productId': '{{productId}}',
                    'productImageType': 'PRODUCT',
                    'remote_id': None,
                    'source': None,
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png',
                    'updatedAt': '2026-09-07T03:49:37.677Z',
                    'variantIds': [],
                    'width': 1000,
                },
            ],
            'options': [
                {
                    'id': 'e3e6d794-4549-45f7-82a3-9d289715eedf',
                    'images': [
                        {
                            'imageId': None,
                            'value': 'Default Title',
                        },
                    ],
                    'name': 'Title',
                    'position': 1,
                    'productId': '{{productId}}',
                    'remote_id': None,
                    'values': [
                        'Default Title',
                    ],
                },
            ],
            'variants': [
                {
                    'compareAtPrice': None,
                    'createdAt': '2026-09-07T03:49:37.677Z',
                    'fees': 6.58,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'id': '{{merchantProductVariantId}}',
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 82,
                    'inventoryQuantityOriginal': 82,
                    'isInventoryQuantityUnlimited': False,
                    'isMaxPurchaseQuantityEnabled': True,
                    'isMinPurchaseQuantityEnabled': True,
                    'isPackSizeEnabled': False,
                    'maxPurchaseQuantity': 4,
                    'minPurchaseQuantity': 1,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'packSize': None,
                    'platform': None,
                    'position': 1,
                    'price': '55.88',
                    'priceAnchor': '0.00',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'remote_id': None,
                    'sku': '',
                    'soldQuantity': 0,
                    'taxCode': None,
                    'taxable': True,
                    'ticketPrice': 49.3,
                    'title': 'Default Title',
                    'transactionFee': {
                        'customFee': 0,
                        'customFeeBreakdown': {
                            'TAX': {
                                'index': 0,
                                'itemFee': 0,
                                'title': 'Taxes',
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0,
                            },
                        },
                        'platformFee': 6.58,
                        'transactionItemFee': 6.58,
                    },
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                    'updatedAt': '2026-09-07T03:49:37.677Z',
                    'weight': None,
                    'weightUnit': 'lb',
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-09-07T03:49:37.653Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': None,
            'deliveryMethod': 'THIRD_PARTY_ISSUED',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': 'Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.',
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '34z3as',
            'taxEnable': False,
            'taxJarCategory': '',
            'productFormId': '7dbd799d-032b-4333-9376-9a157c8ac31b',
            'isPlatformFeeConfigOutdated': False,
            'copyFromId': '{{productId}}',
        },
    ],
    'lineup': [],
    'eventProducts': [],
    'products': [
        {
            'id': '{{productId}}',
            'title': 'General Admission — Pear.US',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'height': 630,
                'mediaDuration': 0,
                'mediaType': 'IMAGE',
                'position': 0,
                'src': 'https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
                'width': 1200,
            },
            'inventoryQuantity': 82,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 55.88,
            'priceMax': 55.88,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'contributedBy': 3,
                    'contributorId': None,
                    'createdAt': '2026-09-07T03:49:37.677Z',
                    'height': 1000,
                    'id': '6ca3d3dc-34f3-4898-84ca-e8a7776a757c',
                    'mediaDuration': 0,
                    'mediaSrc': None,
                    'mediaType': 'IMAGE',
                    'position': 1,
                    'productId': '{{productId}}',
                    'productImageType': 'PRODUCT',
                    'remote_id': None,
                    'source': None,
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png',
                    'updatedAt': '2026-09-07T03:49:37.677Z',
                    'variantIds': [],
                    'width': 1000,
                },
            ],
            'options': [
                {
                    'id': 'e3e6d794-4549-45f7-82a3-9d289715eedf',
                    'images': [
                        {
                            'imageId': None,
                            'value': 'Default Title',
                        },
                    ],
                    'name': 'Title',
                    'position': 1,
                    'productId': '{{productId}}',
                    'remote_id': None,
                    'values': [
                        'Default Title',
                    ],
                },
            ],
            'variants': [
                {
                    'compareAtPrice': None,
                    'createdAt': '2026-09-07T03:49:37.677Z',
                    'fees': 6.58,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'id': '{{merchantProductVariantId}}',
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 82,
                    'inventoryQuantityOriginal': 82,
                    'isInventoryQuantityUnlimited': False,
                    'isMaxPurchaseQuantityEnabled': True,
                    'isMinPurchaseQuantityEnabled': True,
                    'isPackSizeEnabled': False,
                    'maxPurchaseQuantity': 4,
                    'minPurchaseQuantity': 1,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'packSize': None,
                    'platform': None,
                    'position': 1,
                    'price': '55.88',
                    'priceAnchor': '0.00',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'remote_id': None,
                    'sku': '',
                    'soldQuantity': 0,
                    'taxCode': None,
                    'taxable': True,
                    'ticketPrice': 49.3,
                    'title': 'Default Title',
                    'transactionFee': {
                        'customFee': 0,
                        'customFeeBreakdown': {
                            'TAX': {
                                'index': 0,
                                'itemFee': 0,
                                'title': 'Taxes',
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0,
                            },
                        },
                        'platformFee': 6.58,
                        'transactionItemFee': 6.58,
                    },
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                    'updatedAt': '2026-09-07T03:49:37.677Z',
                    'weight': None,
                    'weightUnit': 'lb',
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-09-07T03:49:37.653Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': None,
            'deliveryMethod': 'THIRD_PARTY_ISSUED',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': 'Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.',
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '34z3as',
            'taxEnable': False,
            'taxJarCategory': '',
            'productFormId': '7dbd799d-032b-4333-9376-9a157c8ac31b',
            'isPlatformFeeConfigOutdated': False,
        },
    ],
    'statistics': {
        'totalAvailableTickets': 82,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
        'totalTickets': 82,
        'totalMerch': 0,
        'totalSoldMerch': 0,
        'totalAvailableMerch': 0,
        'totalRedeemedMerch': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': False,
    'ignoreEndTime': False,
    'posterBackend': [
        {
            'height': 630,
            'mediaDuration': 0,
            'mediaType': 'IMAGE',
            'position': 0,
            'src': 'https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
            'width': 1200,
        },
    ],
    'customFeeConfig': {
        'isEnabled': False,
        'items': [],
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
        'version': 'v2',
        'backgroundColor': '#000000',
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
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'dividerColor': '#5D5D5D',
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderRadius': 0,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'fontWeight': 400,
        },
        'product': {
            'borderRadius': 0,
        },
        'featuredProducts': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'relatedLink': {
            'backgroundColor': '#FAFAFA',
            'color': '#000000 ',
            'borderRadius': 0,
        },
        'announcementCarousel': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#7132F4',
            '#FFFFFF',
        ],
    },
}, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 11: 08306796-68a5-4c06-a064-41c855cb0242
    _resp11 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    vars['promoterProductId'] = 'targetVariantId'
    vars['merchantProductVariantId'] = 'merchantProductVariantId'
    # step 12: 5e4763c0-213e-44d1-8ee0-15b388f36e32
    _resp12 = ctx.api.auth.guest_login(body={
        "consumerId": "{{__uuid_0}}",
    })
    vars['access_token'] = (_resp12.json() if _resp12.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 13: dd0455dd-1414-4f26-a71f-3cca80014da1
    _resp13 = ctx.api.cart.delete(body={}, app_headers=True, token='access_token')
    # assertion 13.assertion: responseJson equal 200
    expect(_resp13).json('$.code').equals('200')
    # assertion 13.assertion: responseJson equal success
    expect(_resp13).json('$.message').equals('success')
    # step 14: buy now
    _resp14 = ctx.api.orders.buy_now(body={
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
    }, token='access_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp14, '$.data.orderId')
    # step 15: 33e4ab76-4fed-456c-85a4-6b1dd506eee7
    _resp15 = ctx.api.orders.checkout_express(body={
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
    # step 16: 173d3229-281b-4285-bb4e-e8bcd5130909
    _resp16 = ctx.api.merchants.shipping_options(body=None, token='yuxiao999_token')
    vars['shipping_option_id'] = 'shippingId'
    # step 17: 02bc9b66-ffbb-48ad-8d30-5b3b3764e578
    _resp17 = ctx.api.events.by_dup_event_id(body={
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
    # step 18: 75dff304-6214-495f-bf52-0a136cbde768
    _resp18 = ctx.api.orders.checkout_express(body={
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
    # step 19: d5d0f651-78ac-463f-b146-4ce5144867a6
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
    # step 20: d46477ce-b6a0-431f-b0b4-877659fccc15
    _resp20 = ctx.api.admin.events_by_dup_event_id(body={
        "status": "UPCOMING",
    }, token='admin_token')
    # assertion 20.assertion: responseJson equal 200
    expect(_resp20).json('$.code').equals('200')
    # assertion 20.assertion: responseJson equal success
    expect(_resp20).json('$.message').equals('success')
    # step 22: 50179345-fab4-45fb-a25d-70424adae873
    _resp22 = ctx.api.cart.delete(body={}, app_headers=True, token='access_token')
    # assertion 22.assertion: responseJson equal 200
    expect(_resp22).json('$.code').equals('200')
    # assertion 22.assertion: responseJson equal success
    expect(_resp22).json('$.message').equals('success')
    # step 23: buy now
    _resp23 = ctx.api.orders.buy_now(body={
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
    }, token='access_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp23, '$.data.orderId')
    # step 24: place order
    _resp24 = ctx.api.orders.create(body={
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
    }, skip_notifications=False, token='access_token')
    # assertion 24.assertion: responseJson equal success
    expect(_resp24).json('$.message').equals('success')
    # step 25: fdb455cc-78a7-4b08-91a7-1da4b9960204
    _resp25 = ctx.api.events.by_dup_event_id(body={
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
    # step 26: 486e02b9-ce12-4f83-87f4-1013d87bd6f5
    _resp26 = ctx.api.admin.events_by_dup_event_id(body={
        "status": "UPCOMING",
    }, token='admin_token')
    # assertion 26.assertion: responseJson equal 400
    expect(_resp26).json('$.code').equals('400')
    # assertion 26.assertion: responseJson equal Cannot revert an event that has sales.
    expect(_resp26).json('$.message').equals('Cannot revert an event that has sales.')
    # step 27: 67d12801-155f-4437-9c63-7142fc198c99
    _resp27 = ctx.api.events.by_event_id(body=None, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
