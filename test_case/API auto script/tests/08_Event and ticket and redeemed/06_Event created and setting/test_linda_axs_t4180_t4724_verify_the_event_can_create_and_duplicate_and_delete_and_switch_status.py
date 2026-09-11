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

from core.assertions import expect

def test__8709247__Linda_AXS_T4180_T4724_Verify_the_Event_can_create_and_duplicate_and_delete_and_switch_status(ctx):
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
    _resp6 = ctx.api.admin.users_search(body='{\r\n    "query": "{{UIauto_partner_email}}",\r\n    "filter": {\r\n        "userRoles": [\r\n            "PROMOTER",\r\n            "BUSINESS_PARTNER"\r\n        ],\r\n        "userType": "ALL"\r\n    },\r\n    "pageSize": 100,\r\n    "pageNumber": 1\r\n}', token='admin_token')
    vars['user_id'] = 'userId'
    vars['user_id'] = ''
    vars['dul_event_title'] = 'Duplicate Verify the AXS Event can create and duplicate and delete success'
    # step 7: 46f46103-0698-46bb-8a31-851caf142fb6
    _resp7 = ctx.api.events.v2_duplicate(body='{\n    "title": "{{dul_event_title}}",\n    "curatorId": "{{user_id}}",\n    "description": "",\n    "descriptionBodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[{\\"detail\\":0,\\"format\\":0,\\"mode\\":\\"normal\\",\\"style\\":\\"\\",\\"text\\":\\"This event has a tiered pricing structure in the General Admission area. All General Admission tiers have the same access. Once a price level sells out it may no longer be visible or available for selection. *Please note: multiple GA price levels may be available at the same time The event organizer has decided that ticket transfer will be delayed for this event. Ticket transfer will be available on or about three weeks prior to the event. Please review the terms of AXS’s Purchase Agreement for more information.\\",\\"type\\":\\"extended-text\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n    "startDate": "2027-11-07T02:00:00.000Z",\n    "endDate": "2027-12-01T05:15:00.000Z",\n    "venue": "Agora Theatre",\n    "location": "Cleveland, OH, United States",\n    "status": "UPCOMING",\n    "isTaxEnabled": false,\n    "taxConfig": null,\n    "mediaTextConfig": {\n        "headline": "Missed our last event?",\n        "subtitle": "Here\'s a lil recap. Make sure you buy, tickets SOLD OUT last event!",\n        "align": "center"\n    },\n    "poster": {\n        "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n        "width": 1200,\n        "height": 630,\n        "position": 0,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n    },\n    "startDateDisplay": "2027-11-06 21:00",\n    "endDateDisplay": "2027-12-01 00:15",\n    "note": "{{dul_event_title}",\n    "timezone": {\n        "timeZoneId": "America/New_York",\n        "timeZoneName": "Eastern Standard Time",\n        "dstOffset": 0,\n        "rawOffset": -18000\n    },\n    "isAddressRevealEnabled": false,\n    "isAddressHidden": false,\n    "messageInfo": {\n        "smsMaxLimit": 3,\n        "emailMaxLimit": 5,\n        "cooldownMinutes": 15\n    },\n    "platform": "AXS",\n    "creationStep": "COMPLETED",\n    "extraInfo": null,\n    "locationDetails": {\n        "city": "Cleveland",\n        "line1": null,\n        "line2": null,\n        "state": "OH",\n        "country": "United States",\n        "placeId": null,\n        "zipcode": null,\n        "stateName": "OH",\n        "stripeLocationId": null\n    },\n    "country": "United States",\n    "state": "OH",\n    "autoReplace": false,\n    "lineupTransactionId": null,\n    "lineupTransactionStatus": null,\n    "autoPayLineupStatus": "PENDING",\n    "excludeOnsiteSalesFromReport": false,\n    "showFeesBreakdown": false,\n    "showBuyerInfoOnVenueMap": false,\n    "venueMapId": null,\n    "ticketHubInfo": {\n        "contextId": "517840254",\n        "contextDesc": "AEG Great Lakes",\n        "eventHandle": "eyJwbGF0Zm9ybSI6IkFYUyIsImh1YklkIjoiYy1wS2o5Ujk1d0Z1bWl0RmNUYXFIb283dVNCcHktaXlRTmdNTFNGZnNybyJ9"\n    },\n    "readOnlyFields": [\n        "tax",\n        "customFees",\n        "duplicateTicket",\n        "addTicket",\n        "addMerch",\n        "duplicateMerch"\n    ],\n    "medias": [],\n    "tickets": [\n        {\n            "id": "{{productId}}",\n            "remote_id": null,\n            "platform": "AXS",\n            "createdAt": "2026-09-03T09:44:42.495Z",\n            "updatedAt": "2026-09-04T09:28:40.780Z",\n            "merchantId": "e1229bad-fb18-44b2-ac23-c4c3c1b5c3c3",\n            "title": "General Admission — Pear.US",\n            "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n            "originalBodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n            "isBodyHtmlOverridden": false,\n            "bodyText": "\\n",\n            "handle": null,\n            "productType": "",\n            "publishedAt": "2026-09-03T09:44:42.508Z",\n            "publishedScope": "",\n            "status": "ACTIVE",\n            "externalStatus": "ACTIVE",\n            "followExternalStatus": false,\n            "tags": [],\n            "templateSuffix": null,\n            "vendor": "Pear",\n            "syncAt": null,\n            "deletedAt": null,\n            "delisted": false,\n            "excludedByImportingTag": false,\n            "isFeatured": false,\n            "featuredScore": null,\n            "inventoryQuantity": {{availableQuantity}},\n            "inventoryQuantityOriginal": {{availableQuantity}},\n            "soldQuantity": 0,\n            "priceDisplay": 55.88,\n            "priceDisplayAnchor": 0,\n            "priceMin": 55.88,\n            "priceMinAnchor": 0,\n            "priceMax": 55.88,\n            "priceMaxAnchor": 0,\n            "priceImportedMin": 0,\n            "priceImportedMax": 0,\n            "imageCount": 1,\n            "isUsed": "NWT",\n            "shippingType": "NO_SHIPPING_REQUIRED",\n            "additionalShippingFee": 0,\n            "deliveryTime": [\n                0,\n                5\n            ],\n            "returnPolicyApplied": true,\n            "isAvailable": true,\n            "commissionRate": 0,\n            "textForShare": null,\n            "priceSyncImported": false,\n            "coverImage": {\n                "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n                "width": 1200,\n                "height": 630,\n                "position": 0,\n                "mediaType": "IMAGE",\n                "mediaDuration": 0\n            },\n            "useEventPosterAsCover": true,\n            "reviewCount": null,\n            "reviewOverallScore": null,\n            "reviewAggregate": null,\n            "displayReviews": true,\n            "links": null,\n            "taxEnable": false,\n            "taxJarCategory": "",\n            "overrideEventTax": false,\n            "customTaxRate": null,\n            "subscriptionPlanId": null,\n            "reviewRedirectProductId": null,\n            "reviewSummary": null,\n            "customFieldsInfo": null,\n            "listingType": "TICKET",\n            "ticketType": "TICKET_TYPE_STANDARD",\n            "extraInfo": {\n                "date": "Fri Nov 6, 2026 9PM - Tue Dec 1, 12:15AM EST",\n                "event": "Zack Fox (DJ Set)",\n                "venue": "Agora Theatre",\n                "lineup": [],\n                "poster": {\n                    "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n                    "width": 1200,\n                    "height": 630,\n                    "position": 0,\n                    "mediaType": "IMAGE",\n                    "mediaDuration": 0\n                },\n                "status": "UPCOMING",\n                "endDate": "2026-12-01T05:15:00.000Z",\n                "location": "Cleveland, OH, United States",\n                "eventNote": "",\n                "startDate": "2026-11-07T02:00:00.000Z",\n                "timeZoneId": "America/New_York",\n                "isAddressHidden": false,\n                "addressRevealConfig": null\n            },\n            "ticketHubInfo": {\n                "ticketHandle": "{{ticketHubInfo_id}}",\n                "priceSyncedAt": "2026-09-03T09:44:42.350Z",\n                "sectionOptions": [\n                    {\n                        "label": "GeneralAdmission",\n                        "price": {\n                            "amount": 4930,\n                            "currency": "USD"\n                        },\n                        "quantityRule": {\n                            "max": 4,\n                            "min": 1,\n                            "step": 1\n                        },\n                        "ticketHandle": "{{ticketHandle}}",\n                        "availableQuantity": {{availableQuantity}},\n                        "isGeneralAdmission": true\n                    }\n                ]\n            },\n            "customizedFields": [],\n            "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n            "shippingOptions": [],\n            "shippingNote": null,\n            "autoFulfill": true,\n            "eventId": "{{event_id}}",\n            "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",\n            "copyFromId": "{{productId}}",\n            "stopSellingAfter": null,\n            "stopSellingAfterDisplay": null,\n            "deliveryMethod": "THIRD_PARTY_ISSUED",\n            "thirdPartyDeliveryMessage": "Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.",\n            "isMultipleDaysPassEnabled": false,\n            "isVenueUnitEnabled": false,\n            "venueUnitCategoryId": null,\n            "multipleDaysPass": null,\n            "isPickupEtaEnabled": null,\n            "eventMatchingRules": null,\n            "isExpirationEnabled": false,\n            "expirationTime": null,\n            "expirationTimeDisplay": null,\n            "allowAtDoorSales": false,\n            "isProductFormEnabled": true,\n            "isVariantPriceDisplayEnabled": false,\n            "isTipEnabled": false,\n            "hideFees": false,\n            "isPlatformFeeConfigCustomized": false,\n            "isVariantPlatformFeeConfigCustomized": false,\n            "transactionFeeConfig": {\n                "baseConfig": {\n                    "unitFixedFee": 1,\n                    "unitPercentageFee": 0.1\n                }\n            },\n            "transactionFeeRebateConfig": {\n                "baseConfig": {\n                    "unitFixedFee": 0,\n                    "unitPercentageFee": 0\n                }\n            },\n            "transactionCustomFeeConfig": null,\n            "overrideEventCustomFee": false,\n            "isInclusionsEnabled": false,\n            "images": [\n                {\n                    "id": "7b9ef5e8-a5ff-4d9b-95fc-7f75872008a9",\n                    "remote_id": null,\n                    "createdAt": "2026-09-03T09:44:42.518Z",\n                    "updatedAt": "2026-09-03T09:44:42.518Z",\n                    "height": 1000,\n                    "width": 1000,\n                    "position": 1,\n                    "productId": "{{productId}}",\n                    "src": "https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png",\n                    "variantIds": [],\n                    "mediaType": "IMAGE",\n                    "mediaSrc": null,\n                    "mediaDuration": 0,\n                    "contributedBy": 3,\n                    "contributorId": null,\n                    "productImageType": "PRODUCT",\n                    "source": null\n                }\n            ],\n            "options": [\n                {\n                    "name": "Title",\n                    "images": [\n                        {\n                            "value": "Default Title",\n                            "image": null\n                        }\n                    ]\n                }\n            ],\n            "variants": [\n                {\n                    "id": "3{{merchantProductVariantId}}",\n                    "remote_id": null,\n                    "createdAt": "2026-09-03T09:44:42.518Z",\n                    "updatedAt": "2026-09-03T09:44:42.518Z",\n                    "compareAtPrice": null,\n                    "fulfillmentService": "manual",\n                    "grams": 0,\n                    "imageId": null,\n                    "imageIds": [],\n                    "inventoryItemId": null,\n                    "inventoryManagement": "Pear",\n                    "inventoryPolicy": "DENY",\n                    "isInventoryQuantityUnlimited": false,\n                    "inventoryQuantity": {{availableQuantity}},\n                    "inventoryQuantityOriginal": {{availableQuantity}},\n                    "soldQuantity": 0,\n                    "option": {\n                        "option1": "Default Title"\n                    },\n                    "position": 1,\n                    "price": "55.88",\n                    "priceAnchor": "0.00",\n                    "priceImported": "0.00",\n                    "productId": "{{productId}}",\n                    "sku": "",\n                    "taxCode": null,\n                    "taxable": true,\n                    "title": "Default Title",\n                    "weight": null,\n                    "weightUnit": "lb",\n                    "platform": null,\n                    "fees": 6.58,\n                    "transactionFee": {\n                        "customFee": 0,\n                        "platformFee": 6.58,\n                        "customFeeBreakdown": {\n                            "TAX": {\n                                "index": 0,\n                                "title": "Taxes",\n                                "itemFee": 0,\n                                "unitFixedFee": 0,\n                                "unitPercentageFee": 0\n                            }\n                        },\n                        "transactionItemFee": 6.58\n                    },\n                    "ticketPrice": 49.3,\n                    "isMinPurchaseQuantityEnabled": true,\n                    "minPurchaseQuantity": 1,\n                    "isMaxPurchaseQuantityEnabled": true,\n                    "maxPurchaseQuantity": 4,\n                    "isPackSizeEnabled": false,\n                    "packSize": null,\n                    "transactionFeeConfig": null,\n                    "transactionFeeRebateConfig": null,\n                    "image": null\n                }\n            ],\n            "inclusions": [],\n            "productForm": {{productForm}}\n        }\n    ],\n    "lineup": [],\n    "eventProducts": [],\n    "ignoreStartTime": false,\n    "ignoreEndTime": false,\n    "duplicateEventId": "{{event_id}}",\n    "posterBackend": [\n        {\n            "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n            "width": 1200,\n            "height": 630,\n            "position": 0,\n            "mediaType": "IMAGE",\n            "mediaDuration": 0\n        }\n    ],\n    "customFeeConfig": null,\n    "allowAutoComplete": true,\n    "styleSettings": {\n        "template": "ClearSky",\n        "themeName": "MidnightGlow",\n        "layout": {\n            "pageHeader": {\n                "style": "DEDICATED_HEADER_BAR",\n                "displayText": "SHOP_NAME",\n                "height": "MEDIUM"\n            },\n            "productBanner": {\n                "ctaButton": "VIEW_PRODUCT",\n                "display": "HIDE"\n            }\n        },\n        "version": "v2",\n        "backgroundColor": "#000000",\n        "title": {\n            "color": "#F6CA7C",\n            "fontFamily": "Inter",\n            "fontSize": 24,\n            "fontWeight": 700\n        },\n        "columnTitle": {\n            "fontFamily": "Inter",\n            "fontSize": 20,\n            "fontWeight": 700,\n            "color": "#FFFFFF"\n        },\n        "fontFamily": "Inter",\n        "color": "#FFFFFF",\n        "dividerColor": "#5D5D5D",\n        "button": {\n            "backgroundColor": "#F6CA7C",\n            "color": "#000000",\n            "borderRadius": 0,\n            "fontWeight": 400\n        },\n        "secondaryButton": {\n            "color": "#FFFFFF",\n            "borderColor": "#F6CA7C",\n            "borderRadius": 0,\n            "fontWeight": 400\n        },\n        "product": {\n            "borderRadius": 0\n        },\n        "featuredProducts": {\n            "backgroundColor": "#000000",\n            "borderRadius": 0,\n            "color": "#FFFFFF",\n            "secondaryTextColor": "#E0E0E0",\n            "title": {\n                "fontFamily": "Inter",\n                "fontSize": 14,\n                "fontWeight": 400,\n                "color": "#FFFFFF"\n            }\n        },\n        "relatedLink": {\n            "backgroundColor": "#FAFAFA",\n            "color": "#000000 ",\n            "borderRadius": 0\n        },\n        "announcementCarousel": {\n            "backgroundColor": "#F6CA7C",\n            "color": "#000000"\n        },\n        "featuredProduct": {\n            "cover": {\n                "borderRadius": 0\n            }\n        },\n        "recentUsedColors": [\n            "#7132F4",\n            "#FFFFFF"\n        ]\n    }\n}', token='yuxiao999_token')
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
    _resp10 = ctx.api.events.by_dup_event_id(body='{\n  "id": "{{dup_event_id}}",\n  "title": "{{dul_event_title}}",\n  "curatorId": "{{user_id}}",\n  "description": "",\n  "descriptionBodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[{\\"detail\\":0,\\"format\\":0,\\"mode\\":\\"normal\\",\\"style\\":\\"\\",\\"text\\":\\"This event has a tiered pricing structure in the General Admission area. All General Admission tiers have the same access. Once a price level sells out it may no longer be visible or available for selection. *Please note: multiple GA price levels may be available at the same time The event organizer has decided that ticket transfer will be delayed for this event. Ticket transfer will be available on or about three weeks prior to the event. Please review the terms of AXS’s Purchase Agreement for more information.\\",\\"type\\":\\"extended-text\\",\\"version\\":1}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n  "startDate": "2027-11-07T01:00:00.000Z",\n  "endDate": "2027-12-01T05:15:00.000Z",\n  "venue": "Agora Theatre",\n  "location": "Cleveland, OH, United States",\n  "status": "ON_HOLD",\n  "isTaxEnabled": false,\n  "mediaTextConfig": {\n    "headline": "Missed our last event?",\n    "subtitle": "Here\'s a lil recap. Make sure you buy, tickets SOLD OUT last event!",\n    "align": "center"\n  },\n  "poster": {\n    "height": 630,\n    "mediaDuration": 0,\n    "mediaType": "IMAGE",\n    "position": 0,\n    "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n    "width": 1200\n  },\n  "startDateDisplay": "2027-11-06 21:00",\n  "endDateDisplay": "2027-12-01 00:15",\n  "note": "{{dul_event_title}}",\n  "timezone": {\n    "timeZoneId": "America/New_York",\n    "timeZoneName": "Eastern Daylight Time",\n    "dstOffset": 3600,\n    "rawOffset": -18000\n  },\n  "isAddressRevealEnabled": false,\n  "isAddressHidden": false,\n  "messageInfo": {\n    "cooldownMinutes": 15,\n    "emailMaxLimit": 5,\n    "smsMaxLimit": 3\n  },\n  "platform": "AXS",\n  "creationStep": "COMPLETED",\n  "extraInfo": null,\n  "locationDetails": {\n    "city": "Cleveland",\n    "country": "United States",\n    "line1": null,\n    "line2": null,\n    "placeId": null,\n    "state": "OH",\n    "stateName": "OH",\n    "stripeLocationId": null,\n    "zipcode": null\n  },\n  "country": "United States",\n  "state": "OH",\n  "autoReplace": false,\n  "lineupTransactionId": null,\n  "lineupTransactionStatus": null,\n  "autoPayLineupStatus": "PENDING",\n  "showFeesBreakdown": false,\n  "showBuyerInfoOnVenueMap": false,\n  "ticketHubInfo": {\n    "contextDesc": "AEG Great Lakes",\n    "contextId": "517840254",\n    "eventHandle": "eyJwbGF0Zm9ybSI6IkFYUyIsImh1YklkIjoiYy1wS2o5Ujk1d0Z1bWl0RmNUYXFIb283dVNCcHktaXlRTmdNTFNGZnNybyJ9"\n  },\n  "readOnlyFields": [\n    "tax",\n    "customFees",\n    "duplicateTicket",\n    "addTicket",\n    "addMerch",\n    "duplicateMerch"\n  ],\n  "medias": [],\n  "tickets": [\n    {\n      "id": "{{productId}}",\n      "title": "General Admission — Pear.US",\n      "listingType": "TICKET",\n      "status": "ACTIVE",\n      "coverImage": {\n        "height": 630,\n        "mediaDuration": 0,\n        "mediaType": "IMAGE",\n        "position": 0,\n        "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n        "width": 1200\n      },\n      "inventoryQuantity": 82,\n      "soldQuantity": 0,\n      "isInventoryQuantityUnlimited": false,\n      "priceMin": 55.88,\n      "priceMax": 55.88,\n      "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n      "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n      "images": [\n        {\n          "contributedBy": 3,\n          "contributorId": null,\n          "createdAt": "2026-09-07T03:49:37.677Z",\n          "height": 1000,\n          "id": "6ca3d3dc-34f3-4898-84ca-e8a7776a757c",\n          "mediaDuration": 0,\n          "mediaSrc": null,\n          "mediaType": "IMAGE",\n          "position": 1,\n          "productId": "{{productId}}",\n          "productImageType": "PRODUCT",\n          "remote_id": null,\n          "source": null,\n          "src": "https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png",\n          "updatedAt": "2026-09-07T03:49:37.677Z",\n          "variantIds": [],\n          "width": 1000\n        }\n      ],\n      "options": [\n        {\n          "id": "e3e6d794-4549-45f7-82a3-9d289715eedf",\n          "images": [\n            {\n              "imageId": null,\n              "value": "Default Title"\n            }\n          ],\n          "name": "Title",\n          "position": 1,\n          "productId": "{{productId}}",\n          "remote_id": null,\n          "values": [\n            "Default Title"\n          ]\n        }\n      ],\n      "variants": [\n        {\n          "compareAtPrice": null,\n          "createdAt": "2026-09-07T03:49:37.677Z",\n          "fees": 6.58,\n          "fulfillmentService": "manual",\n          "grams": 0,\n          "id": "{{merchantProductVariantId}}",\n          "imageId": null,\n          "imageIds": [],\n          "inventoryItemId": null,\n          "inventoryManagement": "Pear",\n          "inventoryPolicy": "DENY",\n          "inventoryQuantity": 82,\n          "inventoryQuantityOriginal": 82,\n          "isInventoryQuantityUnlimited": false,\n          "isMaxPurchaseQuantityEnabled": true,\n          "isMinPurchaseQuantityEnabled": true,\n          "isPackSizeEnabled": false,\n          "maxPurchaseQuantity": 4,\n          "minPurchaseQuantity": 1,\n          "option": {\n            "option1": "Default Title"\n          },\n          "packSize": null,\n          "platform": null,\n          "position": 1,\n          "price": "55.88",\n          "priceAnchor": "0.00",\n          "priceImported": "0.00",\n          "productId": "{{productId}}",\n          "remote_id": null,\n          "sku": "",\n          "soldQuantity": 0,\n          "taxCode": null,\n          "taxable": true,\n          "ticketPrice": 49.3,\n          "title": "Default Title",\n          "transactionFee": {\n            "customFee": 0,\n            "customFeeBreakdown": {\n              "TAX": {\n                "index": 0,\n                "itemFee": 0,\n                "title": "Taxes",\n                "unitFixedFee": 0,\n                "unitPercentageFee": 0\n              }\n            },\n            "platformFee": 6.58,\n            "transactionItemFee": 6.58\n          },\n          "transactionFeeConfig": null,\n          "transactionFeeRebateConfig": null,\n          "updatedAt": "2026-09-07T03:49:37.677Z",\n          "weight": null,\n          "weightUnit": "lb"\n        }\n      ],\n      "merchantId": "{{catalog_id}}",\n      "createdAt": "2026-09-07T03:49:37.653Z",\n      "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",\n      "stopSellingAfterDisplay": null,\n      "deliveryMethod": "THIRD_PARTY_ISSUED",\n      "isMultipleDaysPassEnabled": false,\n      "multipleDaysPass": null,\n      "overrideEventTax": false,\n      "customTaxRate": null,\n      "overrideEventCustomFee": false,\n      "transactionCustomFeeConfig": null,\n      "thirdPartyDeliveryMessage": "Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.",\n      "ticketType": "TICKET_TYPE_STANDARD",\n      "isExpirationEnabled": false,\n      "expirationTime": null,\n      "expirationTimeDisplay": null,\n      "isVenueUnitEnabled": false,\n      "useEventPosterAsCover": true,\n      "readOnlyFields": [],\n      "urlAlias": "34z3as",\n      "taxEnable": false,\n      "taxJarCategory": "",\n      "productFormId": "7dbd799d-032b-4333-9376-9a157c8ac31b",\n      "isPlatformFeeConfigOutdated": false,\n      "copyFromId": "{{productId}}"\n    }\n  ],\n  "lineup": [],\n  "eventProducts": [],\n  "products": [\n    {\n      "id": "{{productId}}",\n      "title": "General Admission — Pear.US",\n      "listingType": "TICKET",\n      "status": "ACTIVE",\n      "coverImage": {\n        "height": 630,\n        "mediaDuration": 0,\n        "mediaType": "IMAGE",\n        "position": 0,\n        "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n        "width": 1200\n      },\n      "inventoryQuantity": 82,\n      "soldQuantity": 0,\n      "isInventoryQuantityUnlimited": false,\n      "priceMin": 55.88,\n      "priceMax": 55.88,\n      "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n      "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n      "images": [\n        {\n          "contributedBy": 3,\n          "contributorId": null,\n          "createdAt": "2026-09-07T03:49:37.677Z",\n          "height": 1000,\n          "id": "6ca3d3dc-34f3-4898-84ca-e8a7776a757c",\n          "mediaDuration": 0,\n          "mediaSrc": null,\n          "mediaType": "IMAGE",\n          "position": 1,\n          "productId": "{{productId}}",\n          "productImageType": "PRODUCT",\n          "remote_id": null,\n          "source": null,\n          "src": "https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png",\n          "updatedAt": "2026-09-07T03:49:37.677Z",\n          "variantIds": [],\n          "width": 1000\n        }\n      ],\n      "options": [\n        {\n          "id": "e3e6d794-4549-45f7-82a3-9d289715eedf",\n          "images": [\n            {\n              "imageId": null,\n              "value": "Default Title"\n            }\n          ],\n          "name": "Title",\n          "position": 1,\n          "productId": "{{productId}}",\n          "remote_id": null,\n          "values": [\n            "Default Title"\n          ]\n        }\n      ],\n      "variants": [\n        {\n          "compareAtPrice": null,\n          "createdAt": "2026-09-07T03:49:37.677Z",\n          "fees": 6.58,\n          "fulfillmentService": "manual",\n          "grams": 0,\n          "id": "{{merchantProductVariantId}}",\n          "imageId": null,\n          "imageIds": [],\n          "inventoryItemId": null,\n          "inventoryManagement": "Pear",\n          "inventoryPolicy": "DENY",\n          "inventoryQuantity": 82,\n          "inventoryQuantityOriginal": 82,\n          "isInventoryQuantityUnlimited": false,\n          "isMaxPurchaseQuantityEnabled": true,\n          "isMinPurchaseQuantityEnabled": true,\n          "isPackSizeEnabled": false,\n          "maxPurchaseQuantity": 4,\n          "minPurchaseQuantity": 1,\n          "option": {\n            "option1": "Default Title"\n          },\n          "packSize": null,\n          "platform": null,\n          "position": 1,\n          "price": "55.88",\n          "priceAnchor": "0.00",\n          "priceImported": "0.00",\n          "productId": "{{productId}}",\n          "remote_id": null,\n          "sku": "",\n          "soldQuantity": 0,\n          "taxCode": null,\n          "taxable": true,\n          "ticketPrice": 49.3,\n          "title": "Default Title",\n          "transactionFee": {\n            "customFee": 0,\n            "customFeeBreakdown": {\n              "TAX": {\n                "index": 0,\n                "itemFee": 0,\n                "title": "Taxes",\n                "unitFixedFee": 0,\n                "unitPercentageFee": 0\n              }\n            },\n            "platformFee": 6.58,\n            "transactionItemFee": 6.58\n          },\n          "transactionFeeConfig": null,\n          "transactionFeeRebateConfig": null,\n          "updatedAt": "2026-09-07T03:49:37.677Z",\n          "weight": null,\n          "weightUnit": "lb"\n        }\n      ],\n      "merchantId": "{{catalog_id}}",\n      "createdAt": "2026-09-07T03:49:37.653Z",\n      "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",\n      "stopSellingAfterDisplay": null,\n      "deliveryMethod": "THIRD_PARTY_ISSUED",\n      "isMultipleDaysPassEnabled": false,\n      "multipleDaysPass": null,\n      "overrideEventTax": false,\n      "customTaxRate": null,\n      "overrideEventCustomFee": false,\n      "transactionCustomFeeConfig": null,\n      "thirdPartyDeliveryMessage": "Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.",\n      "ticketType": "TICKET_TYPE_STANDARD",\n      "isExpirationEnabled": false,\n      "expirationTime": null,\n      "expirationTimeDisplay": null,\n      "isVenueUnitEnabled": false,\n      "useEventPosterAsCover": true,\n      "readOnlyFields": [],\n      "urlAlias": "34z3as",\n      "taxEnable": false,\n      "taxJarCategory": "",\n      "productFormId": "7dbd799d-032b-4333-9376-9a157c8ac31b",\n      "isPlatformFeeConfigOutdated": false\n    }\n  ],\n  "statistics": {\n    "totalAvailableTickets": 82,\n    "totalSoldTickets": 0,\n    "totalRedeemedTickets": 0,\n    "totalTickets": 82,\n    "totalMerch": 0,\n    "totalSoldMerch": 0,\n    "totalAvailableMerch": 0,\n    "totalRedeemedMerch": 0\n  },\n  "hasPaidSales": false,\n  "accessType": "OWNER",\n  "ignoreStartTime": false,\n  "ignoreEndTime": false,\n  "posterBackend": [\n    {\n      "height": 630,\n      "mediaDuration": 0,\n      "mediaType": "IMAGE",\n      "position": 0,\n      "src": "https://images.discovery-prod.axs.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg",\n      "width": 1200\n    }\n  ],\n  "customFeeConfig": {\n    "isEnabled": false,\n    "items": []\n  },\n  "allowAutoComplete": true,\n  "styleSettings": {\n    "template": "ClearSky",\n    "themeName": "MidnightGlow",\n    "layout": {\n      "pageHeader": {\n        "style": "DEDICATED_HEADER_BAR",\n        "displayText": "SHOP_NAME",\n        "height": "MEDIUM"\n      },\n      "productBanner": {\n        "ctaButton": "VIEW_PRODUCT",\n        "display": "HIDE"\n      }\n    },\n    "version": "v2",\n    "backgroundColor": "#000000",\n    "title": {\n      "color": "#F6CA7C",\n      "fontFamily": "Inter",\n      "fontSize": 24,\n      "fontWeight": 700\n    },\n    "columnTitle": {\n      "fontFamily": "Inter",\n      "fontSize": 20,\n      "fontWeight": 700,\n      "color": "#FFFFFF"\n    },\n    "fontFamily": "Inter",\n    "color": "#FFFFFF",\n    "dividerColor": "#5D5D5D",\n    "button": {\n      "backgroundColor": "#F6CA7C",\n      "color": "#000000",\n      "borderRadius": 0,\n      "fontWeight": 400\n    },\n    "secondaryButton": {\n      "color": "#FFFFFF",\n      "borderColor": "#F6CA7C",\n      "borderRadius": 0,\n      "fontWeight": 400\n    },\n    "product": {\n      "borderRadius": 0\n    },\n    "featuredProducts": {\n      "backgroundColor": "#000000",\n      "borderRadius": 0,\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0",\n      "title": {\n        "fontFamily": "Inter",\n        "fontSize": 14,\n        "fontWeight": 400,\n        "color": "#FFFFFF"\n      }\n    },\n    "relatedLink": {\n      "backgroundColor": "#FAFAFA",\n      "color": "#000000 ",\n      "borderRadius": 0\n    },\n    "announcementCarousel": {\n      "backgroundColor": "#F6CA7C",\n      "color": "#000000"\n    },\n    "featuredProduct": {\n      "cover": {\n        "borderRadius": 0\n      }\n    },\n    "recentUsedColors": [\n      "#7132F4",\n      "#FFFFFF"\n    ]\n  }\n}', params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 11: 08306796-68a5-4c06-a064-41c855cb0242
    _resp11 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    vars['promoterProductId'] = 'targetVariantId'
    vars['merchantProductVariantId'] = 'merchantProductVariantId'
    # step 12: 5e4763c0-213e-44d1-8ee0-15b388f36e32
    _resp12 = ctx.api.auth.guest_login(body='{\r\n    "consumerId": "{{__uuid_0}}"\r\n}')
    vars['access_token'] = (_resp12.json() if _resp12.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 13: dd0455dd-1414-4f26-a71f-3cca80014da1
    _resp13 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 13.assertion: responseJson equal 200
    expect(_resp13).json('$.code').equals('200')
    # assertion 13.assertion: responseJson equal success
    expect(_resp13).json('$.message').equals('success')
    # step 14: buy now
    _resp14 = ctx.api.orders.buy_now(body='{\n  "postIdForFilter": "{{postId}}",\n  "updateCartItems": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "{{promoterProductId}}",\n      "price": 2,\n      "postId": "{{postId}}",\n      "selected": true,\n      "customFields": []\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "{{event_id}}",\n    "pixelId": [\n      "test"\n    ],\n    "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n    "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n    "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 1,\n      "id": "{{productId}}",\n      "postId": "{{postId}}",\n      "price": 2,\n      "customFields": []\n    }\n  ]\n}', token='access_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp14, '$.data.orderId')
    # step 15: 33e4ab76-4fed-456c-85a4-6b1dd506eee7
    _resp15 = ctx.api.orders.checkout_express(body='{\n    "items": [\n        {\n            "quantity": 3,\n            "promoterProductVariantId": "{{promoterProductId}}",\n            "price": 8.57,\n            "postId": "{{postId}}",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "{{dup_event_id}}",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1786526453224.334258892692108835",\n        "externalId": "b0b0ed9c-8bc8-426f-b590-9a97f10dcd24",\n        "eventSourceUrl": "https://release.pear.us/autotestshop/post/duplicate-verify-the-event-can-create-and-duplicate-and-delete-success"\n    },\n    "subdomainVanityUrl": ""\n}', app_headers=True, token='access_token')
    # step 16: 173d3229-281b-4285-bb4e-e8bcd5130909
    _resp16 = ctx.api.merchants.shipping_options(body=None, token='yuxiao999_token')
    vars['shipping_option_id'] = 'shippingId'
    # step 17: 02bc9b66-ffbb-48ad-8d30-5b3b3764e578
    _resp17 = ctx.api.events.by_dup_event_id(body='{\n  "id": "{{dup_event_id}}",\n  "title": "{{event_title}}",\n  "curatorId": "{{catalog_id}}",\n  "description": "",\n  "descriptionBodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n  "startDate": "2053-04-17T05:00:00.000Z",\n  "endDate": null,\n  "venue": "Instagram Live, Zoom, In-person",\n  "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",\n  "status": "CANCELED",\n  "isTaxEnabled": true,\n  "taxConfig": {\n    "customTaxRate": 10,\n    "calculationType": "CUSTOM",\n    "configUpdatedAt": "2026-08-14T02:04:30.036Z"\n  },\n  "mediaTextConfig": {\n    "headline": "Missed our last event?",\n    "subtitle": "Here\'s a lil recap of our last event👇",\n    "align": "center"\n  },\n  "poster": {\n    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n    "width": 3072,\n    "height": 2048,\n    "position": 0,\n    "mediaType": "IMAGE",\n    "mediaDuration": 0\n  },\n  "startDateDisplay": "2053-04-17",\n  "note": "linda note",\n  "timezone": {\n    "timeZoneId": "America/Chicago",\n    "timeZoneName": "Central Daylight Time",\n    "dstOffset": 3600,\n    "rawOffset": -21600\n  },\n  "isAddressRevealEnabled": false,\n  "messageInfo": {\n    "smsMaxLimit": 3,\n    "emailMaxLimit": 5,\n    "cooldownMinutes": 15\n  },\n  "platform": "PEAR",\n  "creationStep": "COMPLETED",\n  "extraInfo": null,\n  "locationDetails": {\n    "city": "Chicago",\n    "line1": "789 River East Art Center Promenade",\n    "line2": null,\n    "state": "IL",\n    "country": "US",\n    "placeId": null,\n    "zipcode": null,\n    "stateName": "Illinois",\n    "stripeLocationId": null\n  },\n  "country": "US",\n  "state": "IL",\n  "autoReplace": true,\n  "lineupTransactionId": null,\n  "lineupTransactionStatus": null,\n  "autoPayLineupStatus": "PENDING",\n  "showFeesBreakdown": false,\n  "showBuyerInfoOnVenueMap": false,\n  "venueMapId": null,\n  "ticketHubInfo": null,\n  "readOnlyFields": [],\n  "medias": [],\n  "tickets": [\n    {\n      "id": "{{productId}}",\n      "title": "ticket on hold",\n      "listingType": "TICKET",\n      "status": "ACTIVE",\n      "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "mediaSrc": null,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "inventoryQuantity": 10,\n      "soldQuantity": 0,\n      "isInventoryQuantityUnlimited": false,\n      "priceMin": 0,\n      "priceMax": 0,\n      "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n      "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n      "images": [\n        {\n          "id": "c46b0869-dd26-44b4-af2f-1208626a74a9",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "height": 2048,\n          "width": 3072,\n          "position": 0,\n          "productId": "{{productId}}",\n          "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n          "variantIds": [],\n          "mediaType": "IMAGE",\n          "mediaSrc": null,\n          "mediaDuration": 0,\n          "contributedBy": 3,\n          "contributorId": null,\n          "productImageType": "PRODUCT",\n          "source": null\n        }\n      ],\n      "options": [\n        {\n          "id": "{{shipping_option_id}}",\n          "remote_id": null,\n          "productId": "{{productId}}",\n          "name": "Title",\n          "position": 1,\n          "values": [\n            "Default Title"\n          ],\n          "images": [\n            {\n              "value": "Default Title",\n              "imageId": null\n            }\n          ]\n        }\n      ],\n      "variants": [\n        {\n          "id": "{{merchantProductVariantId}}",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "compareAtPrice": null,\n          "fulfillmentService": "manual",\n          "grams": 0,\n          "imageId": null,\n          "imageIds": [],\n          "inventoryItemId": null,\n          "inventoryManagement": "Pear",\n          "inventoryPolicy": "DENY",\n          "isInventoryQuantityUnlimited": false,\n          "inventoryQuantity": 10,\n          "inventoryQuantityOriginal": 10,\n          "soldQuantity": 0,\n          "option": {\n            "option1": "Default Title"\n          },\n          "position": 1,\n          "price": "0",\n          "priceAnchor": "0",\n          "priceImported": "0.00",\n          "productId": "{{productId}}",\n          "sku": "",\n          "taxCode": null,\n          "taxable": true,\n          "title": "Default Title",\n          "weight": null,\n          "weightUnit": "lb",\n          "platform": null,\n          "fees": 0,\n          "transactionFee": {\n            "customFee": 0,\n            "platformFee": 0,\n            "customFeeBreakdown": {},\n            "transactionItemFee": 0\n          },\n          "ticketPrice": 0,\n          "isMinPurchaseQuantityEnabled": false,\n          "minPurchaseQuantity": null,\n          "isMaxPurchaseQuantityEnabled": false,\n          "maxPurchaseQuantity": null,\n          "isPackSizeEnabled": false,\n          "packSize": null,\n          "transactionFeeConfig": null,\n          "transactionFeeRebateConfig": null\n        }\n      ],\n      "merchantId": "{{catalog_id}}",\n      "createdAt": "2026-08-14T02:04:30.452Z",\n      "lifecycleStatus": "LIFECYCLE_STATUS_ON_HOLD",\n      "stopSellingAfterDisplay": "",\n      "deliveryMethod": "QR_CODE",\n      "isMultipleDaysPassEnabled": false,\n      "multipleDaysPass": null,\n      "overrideEventTax": false,\n      "customTaxRate": null,\n      "overrideEventCustomFee": false,\n      "transactionCustomFeeConfig": null,\n      "thirdPartyDeliveryMessage": null,\n      "ticketType": "TICKET_TYPE_STANDARD",\n      "isExpirationEnabled": false,\n      "expirationTime": null,\n      "expirationTimeDisplay": null,\n      "isVenueUnitEnabled": false,\n      "useEventPosterAsCover": true,\n      "readOnlyFields": [],\n      "urlAlias": "7vwa9v",\n      "taxEnable": true,\n      "taxJarCategory": "",\n      "productFormId": null,\n      "isPlatformFeeConfigOutdated": false,\n      "copyFromId": "{{productId}}"\n    }\n  ],\n  "lineup": [\n    {\n      "title": "lineup",\n      "introduction": "001",\n      "poster": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",\n        "width": 160,\n        "height": 160,\n        "position": 0,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "isHeadliner": false,\n      "order": 0,\n      "isPaymentAfterEventEnabled": false,\n      "id": "ae6d0a8a-221b-4bec-8ada-f2fea16b4443"\n    }\n  ],\n  "eventProducts": [],\n  "products": [\n    {\n      "id": "{{productId}}",\n      "title": "ticket on hold",\n      "listingType": "TICKET",\n      "status": "ACTIVE",\n      "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "mediaSrc": null,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "inventoryQuantity": 10,\n      "soldQuantity": 0,\n      "isInventoryQuantityUnlimited": false,\n      "priceMin": 0,\n      "priceMax": 0,\n      "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n      "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n      "images": [\n        {\n          "id": "c46b0869-dd26-44b4-af2f-1208626a74a9",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "height": 2048,\n          "width": 3072,\n          "position": 0,\n          "productId": "{{productId}}",\n          "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n          "variantIds": [],\n          "mediaType": "IMAGE",\n          "mediaSrc": null,\n          "mediaDuration": 0,\n          "contributedBy": 3,\n          "contributorId": null,\n          "productImageType": "PRODUCT",\n          "source": null\n        }\n      ],\n      "options": [\n        {\n          "id": "{{shipping_option_id}}",\n          "remote_id": null,\n          "productId": "{{productId}}",\n          "name": "Title",\n          "position": 1,\n          "values": [\n            "Default Title"\n          ],\n          "images": [\n            {\n              "value": "Default Title",\n              "imageId": null\n            }\n          ]\n        }\n      ],\n      "variants": [\n        {\n          "id": "{{merchantProductVariantId}}",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "compareAtPrice": null,\n          "fulfillmentService": "manual",\n          "grams": 0,\n          "imageId": null,\n          "imageIds": [],\n          "inventoryItemId": null,\n          "inventoryManagement": "Pear",\n          "inventoryPolicy": "DENY",\n          "isInventoryQuantityUnlimited": false,\n          "inventoryQuantity": 10,\n          "inventoryQuantityOriginal": 10,\n          "soldQuantity": 0,\n          "option": {\n            "option1": "Default Title"\n          },\n          "position": 1,\n          "price": "0",\n          "priceAnchor": "0",\n          "priceImported": "0.00",\n          "productId": "{{productId}}",\n          "sku": "",\n          "taxCode": null,\n          "taxable": true,\n          "title": "Default Title",\n          "weight": null,\n          "weightUnit": "lb",\n          "platform": null,\n          "fees": 0,\n          "transactionFee": {\n            "customFee": 0,\n            "platformFee": 0,\n            "customFeeBreakdown": {},\n            "transactionItemFee": 0\n          },\n          "ticketPrice": 0,\n          "isMinPurchaseQuantityEnabled": false,\n          "minPurchaseQuantity": null,\n          "isMaxPurchaseQuantityEnabled": false,\n          "maxPurchaseQuantity": null,\n          "isPackSizeEnabled": false,\n          "packSize": null,\n          "transactionFeeConfig": null,\n          "transactionFeeRebateConfig": null\n        }\n      ],\n      "merchantId": "{{catalog_id}}",\n      "createdAt": "2026-08-14T02:04:30.452Z",\n      "lifecycleStatus": "LIFECYCLE_STATUS_ON_HOLD",\n      "stopSellingAfterDisplay": "",\n      "deliveryMethod": "QR_CODE",\n      "isMultipleDaysPassEnabled": false,\n      "multipleDaysPass": null,\n      "overrideEventTax": false,\n      "customTaxRate": null,\n      "overrideEventCustomFee": false,\n      "transactionCustomFeeConfig": null,\n      "thirdPartyDeliveryMessage": null,\n      "ticketType": "TICKET_TYPE_STANDARD",\n      "isExpirationEnabled": false,\n      "expirationTime": null,\n      "expirationTimeDisplay": null,\n      "isVenueUnitEnabled": false,\n      "useEventPosterAsCover": true,\n      "readOnlyFields": [],\n      "urlAlias": "7vwa9v",\n      "taxEnable": true,\n      "taxJarCategory": "",\n      "productFormId": null,\n      "isPlatformFeeConfigOutdated": false\n    }\n  ],\n  "statistics": {\n    "totalAvailableTickets": 10,\n    "totalSoldTickets": 0,\n    "totalRedeemedTickets": 0,\n    "totalTickets": 10,\n    "totalMerch": 0,\n    "totalSoldMerch": 0,\n    "totalAvailableMerch": 0,\n    "totalRedeemedMerch": 0\n  },\n  "hasPaidSales": false,\n  "accessType": "OWNER",\n  "ignoreStartTime": true,\n  "ignoreEndTime": true,\n  "posterBackend": [\n    {\n      "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n      "width": 3072,\n      "height": 2048,\n      "position": 0,\n      "mediaType": "IMAGE",\n      "mediaDuration": 0\n    }\n  ],\n  "customFeeConfig": {\n    "isEnabled": true,\n    "items": [\n      {\n        "title": "custom fee",\n        "unitFixedFee": 0,\n        "unitPercentageFee": 0.1\n      }\n    ]\n  },\n  "allowAutoComplete": true,\n  "styleSettings": {\n    "template": "ClearSky",\n    "themeName": "MidnightGlow",\n    "layout": {\n      "pageHeader": {\n        "style": "DEDICATED_HEADER_BAR",\n        "displayText": "SHOP_NAME",\n        "height": "MEDIUM"\n      },\n      "productBanner": {\n        "ctaButton": "VIEW_PRODUCT",\n        "display": "HIDE"\n      }\n    },\n    "fontFamily": "Inter",\n    "color": "#FFFFFF",\n    "backgroundColor": "#000000",\n    "borderColor": "#000000",\n    "dividerColor": "#5D5D5D",\n    "secondaryTextColor": "#E0E0E0",\n    "announcementCarousel": {\n      "color": "#000000",\n      "backgroundColor": "#F6CA7C"\n    },\n    "title": {\n      "color": "#F6CA7C",\n      "fontFamily": "Inter",\n      "fontSize": 24,\n      "fontWeight": 700\n    },\n    "columnTitle": {\n      "fontFamily": "Inter",\n      "fontSize": 20,\n      "fontWeight": 700,\n      "color": "#FFFFFF"\n    },\n    "subtitle": {\n      "fontFamily": "Inter",\n      "fontSize": 20,\n      "fontWeight": 400,\n      "color": "#FFFFFF"\n    },\n    "button": {\n      "backgroundColor": "#F6CA7C",\n      "color": "#000000",\n      "borderColor": "#000000",\n      "borderRadius": 0,\n      "boxShadow": "none",\n      "fontSize": 16,\n      "fontWeight": 400\n    },\n    "secondaryButton": {\n      "fontSize": 16,\n      "fontWeight": 400,\n      "color": "#FFFFFF",\n      "borderColor": "#F6CA7C",\n      "borderRadius": 0,\n      "boxShadow": "none"\n    },\n    "textButton": {\n      "fontSize": 16,\n      "fontWeight": 700,\n      "color": "#FFFFFF"\n    },\n    "selectButton": {\n      "borderColor": "#000000"\n    },\n    "relatedLink": {\n      "borderRadius": 0,\n      "color": "#000000 ",\n      "borderColor": "#0000",\n      "backgroundColor": "#FAFAFA"\n    },\n    "featuredProducts": {\n      "borderRadius": 0,\n      "backgroundColor": "#000000",\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0",\n      "title": {\n        "fontFamily": "Inter",\n        "fontSize": 14,\n        "fontWeight": 400,\n        "color": "#FFFFFF"\n      }\n    },\n    "product": {\n      "backgroundColor": "#000000",\n      "borderRadius": 0,\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0"\n    },\n    "discount": {\n      "backgroundColor": "#D32A09",\n      "color": "#FFFFFF",\n      "priceColor": "#FFFFFF"\n    },\n    "freeShipping": {\n      "backgroundColor": "#EBF5EF",\n      "color": "#268E46"\n    },\n    "starRatingColor": "#FAAF03",\n    "layoutFeatureCard": {\n      "title": {\n        "fontFamily": "Inter",\n        "fontSize": 16,\n        "fontWeight": 700,\n        "color": "#FFFFFF"\n      },\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0",\n      "button": {\n        "backgroundColor": "#F6CA7C",\n        "color": "#000000"\n      }\n    },\n    "lineupBanner": {\n      "titleText": "#FFFFFF",\n      "descriptionText": "#E0E0E0"\n    },\n    "eventInfoBanner": {\n      "text": "#FFFFFF",\n      "secondaryText": "#E0E0E0"\n    },\n    "eventDescription": {\n      "text": "#E0E0E0",\n      "title": "#FFFFFF"\n    },\n    "featuredProduct": {\n      "cover": {\n        "borderRadius": 0\n      }\n    },\n    "recentUsedColors": [\n      "#ffffff"\n    ]\n  }\n}', params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 18: 75dff304-6214-495f-bf52-0a136cbde768
    _resp18 = ctx.api.orders.checkout_express(body='{\n    "items": [\n        {\n            "quantity": 3,\n            "promoterProductVariantId": "{{promoterProductId}}",\n            "price": 8.57,\n            "postId": "{{postId}}",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "{{dup_event_id}}",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1786526453224.334258892692108835",\n        "externalId": "b0b0ed9c-8bc8-426f-b590-9a97f10dcd24",\n        "eventSourceUrl": "https://release.pear.us/autotestshop/post/duplicate-verify-the-event-can-create-and-duplicate-and-delete-success"\n    },\n    "subdomainVanityUrl": ""\n}', app_headers=True, token='access_token')
    # step 19: d5d0f651-78ac-463f-b146-4ce5144867a6
    _resp19 = ctx.api.events.by_dup_event_id(body='{\n  "id": "{{dup_event_id}}",\n  "title": "{{event_title}}",\n  "curatorId": "{{catalog_id}}",\n  "description": "",\n  "descriptionBodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n  "startDate": "2053-04-17T05:00:00.000Z",\n  "endDate": null,\n  "venue": "Instagram Live, Zoom, In-person",\n  "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",\n  "status": "COMPLETED",\n  "isTaxEnabled": true,\n  "taxConfig": {\n    "customTaxRate": 10,\n    "calculationType": "CUSTOM",\n    "configUpdatedAt": "2026-08-14T02:04:30.036Z"\n  },\n  "mediaTextConfig": {\n    "headline": "Missed our last event?",\n    "subtitle": "Here\'s a lil recap of our last event👇",\n    "align": "center"\n  },\n  "poster": {\n    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n    "width": 3072,\n    "height": 2048,\n    "position": 0,\n    "mediaType": "IMAGE",\n    "mediaDuration": 0\n  },\n  "startDateDisplay": "2053-04-17",\n  "note": "linda note",\n  "timezone": {\n    "timeZoneId": "America/Chicago",\n    "timeZoneName": "Central Daylight Time",\n    "dstOffset": 3600,\n    "rawOffset": -21600\n  },\n  "isAddressRevealEnabled": false,\n  "messageInfo": {\n    "smsMaxLimit": 3,\n    "emailMaxLimit": 5,\n    "cooldownMinutes": 15\n  },\n  "platform": "PEAR",\n  "creationStep": "COMPLETED",\n  "extraInfo": null,\n  "locationDetails": {\n    "city": "Chicago",\n    "line1": "789 River East Art Center Promenade",\n    "line2": null,\n    "state": "IL",\n    "country": "US",\n    "placeId": null,\n    "zipcode": null,\n    "stateName": "Illinois",\n    "stripeLocationId": null\n  },\n  "country": "US",\n  "state": "IL",\n  "autoReplace": true,\n  "lineupTransactionId": null,\n  "lineupTransactionStatus": null,\n  "autoPayLineupStatus": "PENDING",\n  "showFeesBreakdown": false,\n  "showBuyerInfoOnVenueMap": false,\n  "venueMapId": null,\n  "ticketHubInfo": null,\n  "readOnlyFields": [],\n  "medias": [],\n  "tickets": [\n    {\n      "id": "{{productId}}",\n      "title": "ticket on hold",\n      "listingType": "TICKET",\n      "status": "ACTIVE",\n      "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "mediaSrc": null,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "inventoryQuantity": 10,\n      "soldQuantity": 0,\n      "isInventoryQuantityUnlimited": false,\n      "priceMin": 0,\n      "priceMax": 0,\n      "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n      "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n      "images": [\n        {\n          "id": "c46b0869-dd26-44b4-af2f-1208626a74a9",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "height": 2048,\n          "width": 3072,\n          "position": 0,\n          "productId": "{{productId}}",\n          "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n          "variantIds": [],\n          "mediaType": "IMAGE",\n          "mediaSrc": null,\n          "mediaDuration": 0,\n          "contributedBy": 3,\n          "contributorId": null,\n          "productImageType": "PRODUCT",\n          "source": null\n        }\n      ],\n      "options": [\n        {\n          "id": "{{shipping_option_id}}",\n          "remote_id": null,\n          "productId": "{{productId}}",\n          "name": "Title",\n          "position": 1,\n          "values": [\n            "Default Title"\n          ],\n          "images": [\n            {\n              "value": "Default Title",\n              "imageId": null\n            }\n          ]\n        }\n      ],\n      "variants": [\n        {\n          "id": "{{merchantProductVariantId}}",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "compareAtPrice": null,\n          "fulfillmentService": "manual",\n          "grams": 0,\n          "imageId": null,\n          "imageIds": [],\n          "inventoryItemId": null,\n          "inventoryManagement": "Pear",\n          "inventoryPolicy": "DENY",\n          "isInventoryQuantityUnlimited": false,\n          "inventoryQuantity": 10,\n          "inventoryQuantityOriginal": 10,\n          "soldQuantity": 0,\n          "option": {\n            "option1": "Default Title"\n          },\n          "position": 1,\n          "price": "0",\n          "priceAnchor": "0",\n          "priceImported": "0.00",\n          "productId": "{{productId}}",\n          "sku": "",\n          "taxCode": null,\n          "taxable": true,\n          "title": "Default Title",\n          "weight": null,\n          "weightUnit": "lb",\n          "platform": null,\n          "fees": 0,\n          "transactionFee": {\n            "customFee": 0,\n            "platformFee": 0,\n            "customFeeBreakdown": {},\n            "transactionItemFee": 0\n          },\n          "ticketPrice": 0,\n          "isMinPurchaseQuantityEnabled": false,\n          "minPurchaseQuantity": null,\n          "isMaxPurchaseQuantityEnabled": false,\n          "maxPurchaseQuantity": null,\n          "isPackSizeEnabled": false,\n          "packSize": null,\n          "transactionFeeConfig": null,\n          "transactionFeeRebateConfig": null\n        }\n      ],\n      "merchantId": "{{catalog_id}}",\n      "createdAt": "2026-08-14T02:04:30.452Z",\n      "lifecycleStatus": "LIFECYCLE_STATUS_CANCELED",\n      "stopSellingAfterDisplay": "",\n      "deliveryMethod": "QR_CODE",\n      "isMultipleDaysPassEnabled": false,\n      "multipleDaysPass": null,\n      "overrideEventTax": false,\n      "customTaxRate": null,\n      "overrideEventCustomFee": false,\n      "transactionCustomFeeConfig": null,\n      "thirdPartyDeliveryMessage": null,\n      "ticketType": "TICKET_TYPE_STANDARD",\n      "isExpirationEnabled": false,\n      "expirationTime": null,\n      "expirationTimeDisplay": null,\n      "isVenueUnitEnabled": false,\n      "useEventPosterAsCover": true,\n      "readOnlyFields": [],\n      "urlAlias": "7vwa9v",\n      "taxEnable": true,\n      "taxJarCategory": "",\n      "productFormId": null,\n      "isPlatformFeeConfigOutdated": false,\n      "copyFromId": "{{productId}}"\n    }\n  ],\n  "lineup": [\n    {\n      "title": "lineup",\n      "introduction": "001",\n      "poster": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",\n        "width": 160,\n        "height": 160,\n        "position": 0,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "isHeadliner": false,\n      "order": 0,\n      "isPaymentAfterEventEnabled": false,\n      "id": "ae6d0a8a-221b-4bec-8ada-f2fea16b4443"\n    }\n  ],\n  "eventProducts": [],\n  "products": [\n    {\n      "id": "{{productId}}",\n      "title": "ticket on hold",\n      "listingType": "TICKET",\n      "status": "ACTIVE",\n      "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "mediaSrc": null,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "inventoryQuantity": 10,\n      "soldQuantity": 0,\n      "isInventoryQuantityUnlimited": false,\n      "priceMin": 0,\n      "priceMax": 0,\n      "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n      "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n      "images": [\n        {\n          "id": "c46b0869-dd26-44b4-af2f-1208626a74a9",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "height": 2048,\n          "width": 3072,\n          "position": 0,\n          "productId": "{{productId}}",\n          "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n          "variantIds": [],\n          "mediaType": "IMAGE",\n          "mediaSrc": null,\n          "mediaDuration": 0,\n          "contributedBy": 3,\n          "contributorId": null,\n          "productImageType": "PRODUCT",\n          "source": null\n        }\n      ],\n      "options": [\n        {\n          "id": "{{shipping_option_id}}",\n          "remote_id": null,\n          "productId": "{{productId}}",\n          "name": "Title",\n          "position": 1,\n          "values": [\n            "Default Title"\n          ],\n          "images": [\n            {\n              "value": "Default Title",\n              "imageId": null\n            }\n          ]\n        }\n      ],\n      "variants": [\n        {\n          "id": "{{merchantProductVariantId}}",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "compareAtPrice": null,\n          "fulfillmentService": "manual",\n          "grams": 0,\n          "imageId": null,\n          "imageIds": [],\n          "inventoryItemId": null,\n          "inventoryManagement": "Pear",\n          "inventoryPolicy": "DENY",\n          "isInventoryQuantityUnlimited": false,\n          "inventoryQuantity": 10,\n          "inventoryQuantityOriginal": 10,\n          "soldQuantity": 0,\n          "option": {\n            "option1": "Default Title"\n          },\n          "position": 1,\n          "price": "0",\n          "priceAnchor": "0",\n          "priceImported": "0.00",\n          "productId": "{{productId}}",\n          "sku": "",\n          "taxCode": null,\n          "taxable": true,\n          "title": "Default Title",\n          "weight": null,\n          "weightUnit": "lb",\n          "platform": null,\n          "fees": 0,\n          "transactionFee": {\n            "customFee": 0,\n            "platformFee": 0,\n            "customFeeBreakdown": {},\n            "transactionItemFee": 0\n          },\n          "ticketPrice": 0,\n          "isMinPurchaseQuantityEnabled": false,\n          "minPurchaseQuantity": null,\n          "isMaxPurchaseQuantityEnabled": false,\n          "maxPurchaseQuantity": null,\n          "isPackSizeEnabled": false,\n          "packSize": null,\n          "transactionFeeConfig": null,\n          "transactionFeeRebateConfig": null\n        }\n      ],\n      "merchantId": "{{catalog_id}}",\n      "createdAt": "2026-08-14T02:04:30.452Z",\n      "lifecycleStatus": "LIFECYCLE_STATUS_CANCELED",\n      "stopSellingAfterDisplay": "",\n      "deliveryMethod": "QR_CODE",\n      "isMultipleDaysPassEnabled": false,\n      "multipleDaysPass": null,\n      "overrideEventTax": false,\n      "customTaxRate": null,\n      "overrideEventCustomFee": false,\n      "transactionCustomFeeConfig": null,\n      "thirdPartyDeliveryMessage": null,\n      "ticketType": "TICKET_TYPE_STANDARD",\n      "isExpirationEnabled": false,\n      "expirationTime": null,\n      "expirationTimeDisplay": null,\n      "isVenueUnitEnabled": false,\n      "useEventPosterAsCover": true,\n      "readOnlyFields": [],\n      "urlAlias": "7vwa9v",\n      "taxEnable": true,\n      "taxJarCategory": "",\n      "productFormId": null,\n      "isPlatformFeeConfigOutdated": false\n    }\n  ],\n  "statistics": {\n    "totalAvailableTickets": 10,\n    "totalSoldTickets": 0,\n    "totalRedeemedTickets": 0,\n    "totalTickets": 10,\n    "totalMerch": 0,\n    "totalSoldMerch": 0,\n    "totalAvailableMerch": 0,\n    "totalRedeemedMerch": 0\n  },\n  "hasPaidSales": false,\n  "accessType": "OWNER",\n  "ignoreStartTime": true,\n  "ignoreEndTime": true,\n  "posterBackend": [\n    {\n      "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n      "width": 3072,\n      "height": 2048,\n      "position": 0,\n      "mediaType": "IMAGE",\n      "mediaDuration": 0\n    }\n  ],\n  "customFeeConfig": {\n    "isEnabled": true,\n    "items": [\n      {\n        "title": "custom fee",\n        "unitFixedFee": 0,\n        "unitPercentageFee": 0.1\n      }\n    ]\n  },\n  "allowAutoComplete": true,\n  "styleSettings": {\n    "template": "ClearSky",\n    "themeName": "MidnightGlow",\n    "layout": {\n      "pageHeader": {\n        "style": "DEDICATED_HEADER_BAR",\n        "displayText": "SHOP_NAME",\n        "height": "MEDIUM"\n      },\n      "productBanner": {\n        "ctaButton": "VIEW_PRODUCT",\n        "display": "HIDE"\n      }\n    },\n    "fontFamily": "Inter",\n    "color": "#FFFFFF",\n    "backgroundColor": "#000000",\n    "borderColor": "#000000",\n    "dividerColor": "#5D5D5D",\n    "secondaryTextColor": "#E0E0E0",\n    "announcementCarousel": {\n      "color": "#000000",\n      "backgroundColor": "#F6CA7C"\n    },\n    "title": {\n      "color": "#F6CA7C",\n      "fontFamily": "Inter",\n      "fontSize": 24,\n      "fontWeight": 700\n    },\n    "columnTitle": {\n      "fontFamily": "Inter",\n      "fontSize": 20,\n      "fontWeight": 700,\n      "color": "#FFFFFF"\n    },\n    "subtitle": {\n      "fontFamily": "Inter",\n      "fontSize": 20,\n      "fontWeight": 400,\n      "color": "#FFFFFF"\n    },\n    "button": {\n      "backgroundColor": "#F6CA7C",\n      "color": "#000000",\n      "borderColor": "#000000",\n      "borderRadius": 0,\n      "boxShadow": "none",\n      "fontSize": 16,\n      "fontWeight": 400\n    },\n    "secondaryButton": {\n      "fontSize": 16,\n      "fontWeight": 400,\n      "color": "#FFFFFF",\n      "borderColor": "#F6CA7C",\n      "borderRadius": 0,\n      "boxShadow": "none"\n    },\n    "textButton": {\n      "fontSize": 16,\n      "fontWeight": 700,\n      "color": "#FFFFFF"\n    },\n    "selectButton": {\n      "borderColor": "#000000"\n    },\n    "relatedLink": {\n      "borderRadius": 0,\n      "color": "#000000 ",\n      "borderColor": "#0000",\n      "backgroundColor": "#FAFAFA"\n    },\n    "featuredProducts": {\n      "borderRadius": 0,\n      "backgroundColor": "#000000",\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0",\n      "title": {\n        "fontFamily": "Inter",\n        "fontSize": 14,\n        "fontWeight": 400,\n        "color": "#FFFFFF"\n      }\n    },\n    "product": {\n      "backgroundColor": "#000000",\n      "borderRadius": 0,\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0"\n    },\n    "discount": {\n      "backgroundColor": "#D32A09",\n      "color": "#FFFFFF",\n      "priceColor": "#FFFFFF"\n    },\n    "freeShipping": {\n      "backgroundColor": "#EBF5EF",\n      "color": "#268E46"\n    },\n    "starRatingColor": "#FAAF03",\n    "layoutFeatureCard": {\n      "title": {\n        "fontFamily": "Inter",\n        "fontSize": 16,\n        "fontWeight": 700,\n        "color": "#FFFFFF"\n      },\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0",\n      "button": {\n        "backgroundColor": "#F6CA7C",\n        "color": "#000000"\n      }\n    },\n    "lineupBanner": {\n      "titleText": "#FFFFFF",\n      "descriptionText": "#E0E0E0"\n    },\n    "eventInfoBanner": {\n      "text": "#FFFFFF",\n      "secondaryText": "#E0E0E0"\n    },\n    "eventDescription": {\n      "text": "#E0E0E0",\n      "title": "#FFFFFF"\n    },\n    "featuredProduct": {\n      "cover": {\n        "borderRadius": 0\n      }\n    },\n    "recentUsedColors": [\n      "#ffffff"\n    ]\n  }\n}', params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 20: d46477ce-b6a0-431f-b0b4-877659fccc15
    _resp20 = ctx.api.admin.events_by_dup_event_id(body='{"status":"UPCOMING"}', token='admin_token')
    # assertion 20.assertion: responseJson equal 200
    expect(_resp20).json('$.code').equals('200')
    # assertion 20.assertion: responseJson equal success
    expect(_resp20).json('$.message').equals('success')
    # step 22: 50179345-fab4-45fb-a25d-70424adae873
    _resp22 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 22.assertion: responseJson equal 200
    expect(_resp22).json('$.code').equals('200')
    # assertion 22.assertion: responseJson equal success
    expect(_resp22).json('$.message').equals('success')
    # step 23: buy now
    _resp23 = ctx.api.orders.buy_now(body='{\n  "postIdForFilter": "{{postId}}",\n  "updateCartItems": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "{{promoterProductId}}",\n      "price": 2,\n      "postId": "{{postId}}",\n      "selected": true,\n      "customFields": []\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "{{event_id}}",\n    "pixelId": [\n      "test"\n    ],\n    "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n    "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n    "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 1,\n      "id": "{{productId}}",\n      "postId": "{{postId}}",\n      "price": 2,\n      "customFields": []\n    }\n  ]\n}', token='access_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp23, '$.data.orderId')
    # step 24: place order
    _resp24 = ctx.api.orders.create(body='{\n  "inviterCampaign": {},\n  "id": "{{orderId}}",\n  "contact": {\n    "email": "{{$internet.email(locale=\'en\')}}",\n    "firstName": "test",\n    "lastName": "linda",\n    "phoneNumber": "+16502396646"\n  },\n  "fbAdParams": {\n    "eventID": "586718a7-e342-4210-88b9-280e6cb3a836",\n    "pixelId": [\n      "268933192948110"\n    ],\n    "fbBrowserId": "fb.1.1769653368885.141808310869967644",\n    "externalId": "b7090865-489e-4861-9aa3-d7760e80ee16",\n    "eventSourceUrl": "https://hui.staging.pear.us/lury-merchant/post/300-orders-automation"\n  }\n}', skip_notifications=False, token='access_token')
    # assertion 24.assertion: responseJson equal success
    expect(_resp24).json('$.message').equals('success')
    # step 25: fdb455cc-78a7-4b08-91a7-1da4b9960204
    _resp25 = ctx.api.events.by_dup_event_id(body='{\n  "id": "{{dup_event_id}}",\n  "title": "{{event_title}}",\n  "curatorId": "{{catalog_id}}",\n  "description": "",\n  "descriptionBodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n  "startDate": "2053-04-17T05:00:00.000Z",\n  "endDate": null,\n  "venue": "Instagram Live, Zoom, In-person",\n  "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",\n  "status": "COMPLETED",\n  "isTaxEnabled": true,\n  "taxConfig": {\n    "customTaxRate": 10,\n    "calculationType": "CUSTOM",\n    "configUpdatedAt": "2026-08-14T02:04:30.036Z"\n  },\n  "mediaTextConfig": {\n    "headline": "Missed our last event?",\n    "subtitle": "Here\'s a lil recap of our last event👇",\n    "align": "center"\n  },\n  "poster": {\n    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n    "width": 3072,\n    "height": 2048,\n    "position": 0,\n    "mediaType": "IMAGE",\n    "mediaDuration": 0\n  },\n  "startDateDisplay": "2053-04-17",\n  "note": "linda note",\n  "timezone": {\n    "timeZoneId": "America/Chicago",\n    "timeZoneName": "Central Daylight Time",\n    "dstOffset": 3600,\n    "rawOffset": -21600\n  },\n  "isAddressRevealEnabled": false,\n  "messageInfo": {\n    "smsMaxLimit": 3,\n    "emailMaxLimit": 5,\n    "cooldownMinutes": 15\n  },\n  "platform": "PEAR",\n  "creationStep": "COMPLETED",\n  "extraInfo": null,\n  "locationDetails": {\n    "city": "Chicago",\n    "line1": "789 River East Art Center Promenade",\n    "line2": null,\n    "state": "IL",\n    "country": "US",\n    "placeId": null,\n    "zipcode": null,\n    "stateName": "Illinois",\n    "stripeLocationId": null\n  },\n  "country": "US",\n  "state": "IL",\n  "autoReplace": true,\n  "lineupTransactionId": null,\n  "lineupTransactionStatus": null,\n  "autoPayLineupStatus": "PENDING",\n  "showFeesBreakdown": false,\n  "showBuyerInfoOnVenueMap": false,\n  "venueMapId": null,\n  "ticketHubInfo": null,\n  "readOnlyFields": [],\n  "medias": [],\n  "tickets": [\n    {\n      "id": "{{productId}}",\n      "title": "ticket on hold",\n      "listingType": "TICKET",\n      "status": "ACTIVE",\n      "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "mediaSrc": null,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "inventoryQuantity": 10,\n      "soldQuantity": 0,\n      "isInventoryQuantityUnlimited": false,\n      "priceMin": 0,\n      "priceMax": 0,\n      "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n      "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n      "images": [\n        {\n          "id": "c46b0869-dd26-44b4-af2f-1208626a74a9",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "height": 2048,\n          "width": 3072,\n          "position": 0,\n          "productId": "{{productId}}",\n          "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n          "variantIds": [],\n          "mediaType": "IMAGE",\n          "mediaSrc": null,\n          "mediaDuration": 0,\n          "contributedBy": 3,\n          "contributorId": null,\n          "productImageType": "PRODUCT",\n          "source": null\n        }\n      ],\n      "options": [\n        {\n          "id": "{{shipping_option_id}}",\n          "remote_id": null,\n          "productId": "{{productId}}",\n          "name": "Title",\n          "position": 1,\n          "values": [\n            "Default Title"\n          ],\n          "images": [\n            {\n              "value": "Default Title",\n              "imageId": null\n            }\n          ]\n        }\n      ],\n      "variants": [\n        {\n          "id": "{{merchantProductVariantId}}",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "compareAtPrice": null,\n          "fulfillmentService": "manual",\n          "grams": 0,\n          "imageId": null,\n          "imageIds": [],\n          "inventoryItemId": null,\n          "inventoryManagement": "Pear",\n          "inventoryPolicy": "DENY",\n          "isInventoryQuantityUnlimited": false,\n          "inventoryQuantity": 10,\n          "inventoryQuantityOriginal": 10,\n          "soldQuantity": 0,\n          "option": {\n            "option1": "Default Title"\n          },\n          "position": 1,\n          "price": "0",\n          "priceAnchor": "0",\n          "priceImported": "0.00",\n          "productId": "{{productId}}",\n          "sku": "",\n          "taxCode": null,\n          "taxable": true,\n          "title": "Default Title",\n          "weight": null,\n          "weightUnit": "lb",\n          "platform": null,\n          "fees": 0,\n          "transactionFee": {\n            "customFee": 0,\n            "platformFee": 0,\n            "customFeeBreakdown": {},\n            "transactionItemFee": 0\n          },\n          "ticketPrice": 0,\n          "isMinPurchaseQuantityEnabled": false,\n          "minPurchaseQuantity": null,\n          "isMaxPurchaseQuantityEnabled": false,\n          "maxPurchaseQuantity": null,\n          "isPackSizeEnabled": false,\n          "packSize": null,\n          "transactionFeeConfig": null,\n          "transactionFeeRebateConfig": null\n        }\n      ],\n      "merchantId": "{{catalog_id}}",\n      "createdAt": "2026-08-14T02:04:30.452Z",\n      "lifecycleStatus": "LIFECYCLE_STATUS_CANCELED",\n      "stopSellingAfterDisplay": "",\n      "deliveryMethod": "QR_CODE",\n      "isMultipleDaysPassEnabled": false,\n      "multipleDaysPass": null,\n      "overrideEventTax": false,\n      "customTaxRate": null,\n      "overrideEventCustomFee": false,\n      "transactionCustomFeeConfig": null,\n      "thirdPartyDeliveryMessage": null,\n      "ticketType": "TICKET_TYPE_STANDARD",\n      "isExpirationEnabled": false,\n      "expirationTime": null,\n      "expirationTimeDisplay": null,\n      "isVenueUnitEnabled": false,\n      "useEventPosterAsCover": true,\n      "readOnlyFields": [],\n      "urlAlias": "7vwa9v",\n      "taxEnable": true,\n      "taxJarCategory": "",\n      "productFormId": null,\n      "isPlatformFeeConfigOutdated": false,\n      "copyFromId": "{{productId}}"\n    }\n  ],\n  "lineup": [\n    {\n      "title": "lineup",\n      "introduction": "001",\n      "poster": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",\n        "width": 160,\n        "height": 160,\n        "position": 0,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "isHeadliner": false,\n      "order": 0,\n      "isPaymentAfterEventEnabled": false,\n      "id": "ae6d0a8a-221b-4bec-8ada-f2fea16b4443"\n    }\n  ],\n  "eventProducts": [],\n  "products": [\n    {\n      "id": "{{productId}}",\n      "title": "ticket on hold",\n      "listingType": "TICKET",\n      "status": "ACTIVE",\n      "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "mediaSrc": null,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n      },\n      "inventoryQuantity": 10,\n      "soldQuantity": 0,\n      "isInventoryQuantityUnlimited": false,\n      "priceMin": 0,\n      "priceMax": 0,\n      "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n      "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n      "images": [\n        {\n          "id": "c46b0869-dd26-44b4-af2f-1208626a74a9",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "height": 2048,\n          "width": 3072,\n          "position": 0,\n          "productId": "{{productId}}",\n          "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n          "variantIds": [],\n          "mediaType": "IMAGE",\n          "mediaSrc": null,\n          "mediaDuration": 0,\n          "contributedBy": 3,\n          "contributorId": null,\n          "productImageType": "PRODUCT",\n          "source": null\n        }\n      ],\n      "options": [\n        {\n          "id": "{{shipping_option_id}}",\n          "remote_id": null,\n          "productId": "{{productId}}",\n          "name": "Title",\n          "position": 1,\n          "values": [\n            "Default Title"\n          ],\n          "images": [\n            {\n              "value": "Default Title",\n              "imageId": null\n            }\n          ]\n        }\n      ],\n      "variants": [\n        {\n          "id": "{{merchantProductVariantId}}",\n          "remote_id": null,\n          "createdAt": "2026-08-14T02:04:30.452Z",\n          "updatedAt": "2026-08-14T02:04:30.452Z",\n          "compareAtPrice": null,\n          "fulfillmentService": "manual",\n          "grams": 0,\n          "imageId": null,\n          "imageIds": [],\n          "inventoryItemId": null,\n          "inventoryManagement": "Pear",\n          "inventoryPolicy": "DENY",\n          "isInventoryQuantityUnlimited": false,\n          "inventoryQuantity": 10,\n          "inventoryQuantityOriginal": 10,\n          "soldQuantity": 0,\n          "option": {\n            "option1": "Default Title"\n          },\n          "position": 1,\n          "price": "0",\n          "priceAnchor": "0",\n          "priceImported": "0.00",\n          "productId": "{{productId}}",\n          "sku": "",\n          "taxCode": null,\n          "taxable": true,\n          "title": "Default Title",\n          "weight": null,\n          "weightUnit": "lb",\n          "platform": null,\n          "fees": 0,\n          "transactionFee": {\n            "customFee": 0,\n            "platformFee": 0,\n            "customFeeBreakdown": {},\n            "transactionItemFee": 0\n          },\n          "ticketPrice": 0,\n          "isMinPurchaseQuantityEnabled": false,\n          "minPurchaseQuantity": null,\n          "isMaxPurchaseQuantityEnabled": false,\n          "maxPurchaseQuantity": null,\n          "isPackSizeEnabled": false,\n          "packSize": null,\n          "transactionFeeConfig": null,\n          "transactionFeeRebateConfig": null\n        }\n      ],\n      "merchantId": "{{catalog_id}}",\n      "createdAt": "2026-08-14T02:04:30.452Z",\n      "lifecycleStatus": "LIFECYCLE_STATUS_CANCELED",\n      "stopSellingAfterDisplay": "",\n      "deliveryMethod": "QR_CODE",\n      "isMultipleDaysPassEnabled": false,\n      "multipleDaysPass": null,\n      "overrideEventTax": false,\n      "customTaxRate": null,\n      "overrideEventCustomFee": false,\n      "transactionCustomFeeConfig": null,\n      "thirdPartyDeliveryMessage": null,\n      "ticketType": "TICKET_TYPE_STANDARD",\n      "isExpirationEnabled": false,\n      "expirationTime": null,\n      "expirationTimeDisplay": null,\n      "isVenueUnitEnabled": false,\n      "useEventPosterAsCover": true,\n      "readOnlyFields": [],\n      "urlAlias": "7vwa9v",\n      "taxEnable": true,\n      "taxJarCategory": "",\n      "productFormId": null,\n      "isPlatformFeeConfigOutdated": false\n    }\n  ],\n  "statistics": {\n    "totalAvailableTickets": 10,\n    "totalSoldTickets": 0,\n    "totalRedeemedTickets": 0,\n    "totalTickets": 10,\n    "totalMerch": 0,\n    "totalSoldMerch": 0,\n    "totalAvailableMerch": 0,\n    "totalRedeemedMerch": 0\n  },\n  "hasPaidSales": false,\n  "accessType": "OWNER",\n  "ignoreStartTime": true,\n  "ignoreEndTime": true,\n  "posterBackend": [\n    {\n      "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n      "width": 3072,\n      "height": 2048,\n      "position": 0,\n      "mediaType": "IMAGE",\n      "mediaDuration": 0\n    }\n  ],\n  "customFeeConfig": {\n    "isEnabled": true,\n    "items": [\n      {\n        "title": "custom fee",\n        "unitFixedFee": 0,\n        "unitPercentageFee": 0.1\n      }\n    ]\n  },\n  "allowAutoComplete": true,\n  "styleSettings": {\n    "template": "ClearSky",\n    "themeName": "MidnightGlow",\n    "layout": {\n      "pageHeader": {\n        "style": "DEDICATED_HEADER_BAR",\n        "displayText": "SHOP_NAME",\n        "height": "MEDIUM"\n      },\n      "productBanner": {\n        "ctaButton": "VIEW_PRODUCT",\n        "display": "HIDE"\n      }\n    },\n    "fontFamily": "Inter",\n    "color": "#FFFFFF",\n    "backgroundColor": "#000000",\n    "borderColor": "#000000",\n    "dividerColor": "#5D5D5D",\n    "secondaryTextColor": "#E0E0E0",\n    "announcementCarousel": {\n      "color": "#000000",\n      "backgroundColor": "#F6CA7C"\n    },\n    "title": {\n      "color": "#F6CA7C",\n      "fontFamily": "Inter",\n      "fontSize": 24,\n      "fontWeight": 700\n    },\n    "columnTitle": {\n      "fontFamily": "Inter",\n      "fontSize": 20,\n      "fontWeight": 700,\n      "color": "#FFFFFF"\n    },\n    "subtitle": {\n      "fontFamily": "Inter",\n      "fontSize": 20,\n      "fontWeight": 400,\n      "color": "#FFFFFF"\n    },\n    "button": {\n      "backgroundColor": "#F6CA7C",\n      "color": "#000000",\n      "borderColor": "#000000",\n      "borderRadius": 0,\n      "boxShadow": "none",\n      "fontSize": 16,\n      "fontWeight": 400\n    },\n    "secondaryButton": {\n      "fontSize": 16,\n      "fontWeight": 400,\n      "color": "#FFFFFF",\n      "borderColor": "#F6CA7C",\n      "borderRadius": 0,\n      "boxShadow": "none"\n    },\n    "textButton": {\n      "fontSize": 16,\n      "fontWeight": 700,\n      "color": "#FFFFFF"\n    },\n    "selectButton": {\n      "borderColor": "#000000"\n    },\n    "relatedLink": {\n      "borderRadius": 0,\n      "color": "#000000 ",\n      "borderColor": "#0000",\n      "backgroundColor": "#FAFAFA"\n    },\n    "featuredProducts": {\n      "borderRadius": 0,\n      "backgroundColor": "#000000",\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0",\n      "title": {\n        "fontFamily": "Inter",\n        "fontSize": 14,\n        "fontWeight": 400,\n        "color": "#FFFFFF"\n      }\n    },\n    "product": {\n      "backgroundColor": "#000000",\n      "borderRadius": 0,\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0"\n    },\n    "discount": {\n      "backgroundColor": "#D32A09",\n      "color": "#FFFFFF",\n      "priceColor": "#FFFFFF"\n    },\n    "freeShipping": {\n      "backgroundColor": "#EBF5EF",\n      "color": "#268E46"\n    },\n    "starRatingColor": "#FAAF03",\n    "layoutFeatureCard": {\n      "title": {\n        "fontFamily": "Inter",\n        "fontSize": 16,\n        "fontWeight": 700,\n        "color": "#FFFFFF"\n      },\n      "color": "#FFFFFF",\n      "secondaryTextColor": "#E0E0E0",\n      "button": {\n        "backgroundColor": "#F6CA7C",\n        "color": "#000000"\n      }\n    },\n    "lineupBanner": {\n      "titleText": "#FFFFFF",\n      "descriptionText": "#E0E0E0"\n    },\n    "eventInfoBanner": {\n      "text": "#FFFFFF",\n      "secondaryText": "#E0E0E0"\n    },\n    "eventDescription": {\n      "text": "#E0E0E0",\n      "title": "#FFFFFF"\n    },\n    "featuredProduct": {\n      "cover": {\n        "borderRadius": 0\n      }\n    },\n    "recentUsedColors": [\n      "#ffffff"\n    ]\n  }\n}', params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # step 26: 486e02b9-ce12-4f83-87f4-1013d87bd6f5
    _resp26 = ctx.api.admin.events_by_dup_event_id(body='{"status":"UPCOMING"}', token='admin_token')
    # assertion 26.assertion: responseJson equal 400
    expect(_resp26).json('$.code').equals('400')
    # assertion 26.assertion: responseJson equal Cannot revert an event that has sales.
    expect(_resp26).json('$.message').equals('Cannot revert an event that has sales.')
    # step 27: 67d12801-155f-4437-9c63-7142fc198c99
    _resp27 = ctx.api.events.by_event_id(body=None, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
