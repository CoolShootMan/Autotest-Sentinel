"""Migrated from Apifox case #7583841. Source folder: Event and ticket and redeemed/Event created and setting."""
# Apifox Case ID: 7583841  (traceability only — not needed to run)
NAME = "&T4625&T4626&T4628 Event creation whole process"
TAGS = ["p0", "event_and_ticket_and_redeemed_event_created_and_setting", "suite:linda"]
PRIORITY = 0


CASE_ID = 7583841
ENV_NAME = "Release"

# --- step 1: Get Partner linda05 token ---
# post[extractor]: {"variableName": "linda05_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: Get the target event id ---
# post[customScript]: // 配置项：抽离匹配关键词，便于后续修改
# post: const MATCH_TITLE = "API Test T4623";
# post: const MATCH_STATUS = "UPCOMING";
# post: 
# post: // 1. 安全解析JSON响应体（防止解析失败导致脚本崩溃）
# post: let responseData = {};
# post: try {
# post:     responseData = pm.response.json();
# post: } catch (parseError) {
# post:     console.error("❌ 响应体解析失败（非合法JSON）：", parseError.message);
# post:     pm.environment.unset("created_event_id"); // 清空旧变量
# post:     return; // 终止脚本
# post: }
# post: 
# post: // 2. 安全获取items数组（多层可选链，兼容接口返回结构变化）
# post: const eventItems = responseData?.data?.items || [];
# post: console.log(`📥 接口返回事件总数：${eventItems.length}`);
# post: 
# post: // 3. 筛选逻辑：title包含指定字符串 + status严格等于UPCOMING
# post: // 用find高效查找第一个匹配项，同时兼容title/status字段不存在的情况
# post: const targetItem = eventItems.find(item => {
# post:     // 标题包含关键词（非严格匹配）+ 状态严格匹配UPCOMING
# post:     const isTitleMatch = item?.title?.includes(MATCH_TITLE);
# post:     const isStatusMatch = item?.status === MATCH_STATUS;
# post:     return isTitleMatch && isStatusMatch;
# post: });
# post: 
# post: // 4. 结果处理：日志反馈 + 环境变量管理
# post: if (targetItem) {
# post:     const created_event_id = targetItem.id;
# post:     console.log(`✅ 找到符合条件的事件：`);
# post:     console.log(`   - ID：${created_event_id}`);
# post:     console.log(`   - 标题：${targetItem.title}`);
# post:     console.log(`   - 状态：${targetItem.status}`);
# post:     pm.environment.set("created_event_id", created_event_id); // 存入环境变量
# post: } else {
# post:     console.log(`❌ 未找到符合条件的事件（title包含"${MATCH_TITLE}" 且 status="${MATCH_STATUS}"）`);
# post:     // 可选：输出所有事件的title/status，便于调试
# post:     console.log(`💡 所有事件的title/status列表：`);
# post:     eventItems.forEach((item, index) => {
# post:         console.log(`   [${index+1}] 标题：${item?.title || "无"} | 状态：${item?.status || "无"}`);
# post:     });
# post:     pm.environment.unset("created_event_id"); // 清空旧的无效ID
# post: }
# --- step 3: d0ae0406-88bc-4919-80d6-4ff5d19ead0e ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "API Test T4623 ", "path": "$.data.title", "multipleValue": [], "extractSettings": {"expression": "$.data.title", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "newMediaId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 9a52ee2d-8472-44c2-b327-718b762d46dd ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "API TEST T4623", "path": "$.data.title", "multipleValue": [], "extractSettings": {"expression": "$.data.title", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "newticketid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: 7b1e33e6-33a8-46df-a36e-a5d89449f117 ---
# post[customScript]: // 1. Parse the response body to JSON
# post: const response = pm.response.json();
# post: const eventData = response.data || {};
# post: 
# post: /**
# post:  * Test Case: Validate Event Title
# post:  * Note: The expected title includes a trailing space as seen in the response data.
# post:  */
# post: 
# post: pm.test("Verify the event title matches exactly", function () {
# post:     const expectedTitle = "API Test T4623 "; 
# post:     pm.expect(eventData.title).to.eql(expectedTitle);
# post: });
# post: 
# post: /**
# post:  * Robust Validation: Verify title after trimming whitespace
# post:  * This ensures the core text is correct even if trailing spaces change.
# post:  */
# post: pm.test("Verify the event title (trimmed)", function () {
# post:     pm.expect(eventData.title.trim()).to.eql("API Test T4623");
# post: });
# post: 
# post: /**
# post:  * Test Case: Validate nested ticket information
# post:  */
# post: if (eventData.tickets && eventData.tickets.length > 0) {
# post:     pm.test("Verify the first ticket title", function () {
# post:         // Checking the first ticket in the array: "API TEST T4623"
# post:         pm.expect(eventData.tickets[0].title).to.eql("API TEST T4623");
# post:     });
# post: }
# post: 
# post: /**
# post:  * Test Case: Verify event status and ID
# post:  */
# post: pm.test("Verify Event metadata", function () {
# post:     pm.expect(eventData.status).to.eql("UPCOMING");
# post:     pm.expect(eventData.id).to.eql("1a2e22e6-076a-4176-949b-7ab63a149b3f");
# post: });
# post[customScript]: // 解析响应体
# post: const response = pm.response.json();
# post: 
# post: // 提取所有的 lineup ID
# post: const lineupIds = response.data.lineup.map(item => item.id);
# post: 
# post: // 打印到控制台查看
# post: console.log("Lineup IDs:", lineupIds);
# post: 
# post: // 如果你想把第一个 ID 存入环境变量
# post: if (lineupIds.length > 0) {
# post:     pm.environment.set("lineup_id", lineupIds[0]);
# post: }
# --- step 6: db28cc54-a7e6-40fa-8abc-69e4a9030aa0 ---
# post[customScript]: // 1. 解析响应体 (Parse JSON)
# post: const response = pm.response.json();
# post: const items = response.data.items;
# post: 
# post: 
# post: pm.test("Message is success", () => {
# post:     pm.expect(response.message).to.eql("success");
# post: });
# post: 
# post: /**
# post:  * 3. 提取 data.id 并进行断言
# post:  */
# post: if (items && items.length > 0) {
# post:     // 获取第一个 item 的 id
# post:     const itemId = items[0].id;
# post:     const itemTitle = items[0].title;
# post: 
# post:     // 提取为环境变量 (Variable Name: item_id)
# post:     pm.environment.set("item_id", itemId);
# post:     console.log("成功提取 ID:", itemId);
# post: 
# post:     // 断言 ID 存在且格式正确
# post:     pm.test("Verify the first item's ID and Title", () => {
# post:         pm.expect(itemId).to.be.a('string').and.not.empty;
# post:         pm.expect(itemTitle).to.eql("test 10282 002 by linda");
# post:     });
# post: 
# post:     // 断言 ListingType
# post:     pm.test("ListingType should be EVENT_PRODUCT", () => {
# post:         pm.expect(items[0].listingType).to.eql("EVENT_PRODUCT");
# post:     });
# post: 
# post: } else {
# post:     // 如果 items 数组为空，标记测试失败
# post:     pm.expect.fail("Data items array is empty or missing, cannot extract ID.");
# post: }
# --- step 7: ee56085f-b700-422e-8107-92a552641ce0 ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: const merchData = response.data;
# post: 
# post: /**
# post:  * 2. 提取 data.id 为环境变量 merch_id
# post:  */
# post: if (merchData && merchData.id) {
# post:     pm.environment.set("merch_id", merchData.id);
# post:     console.log("Successfully set merch_id:", merchData.id);
# post: }
# post: 
# post: 
# post: pm.test("Validate Merch Data", () => {
# post:     // 验证 ID 存在
# post:     pm.expect(merchData.id).to.be.a('string').and.not.empty;
# post:     
# post:     // 验证 Title (注意大小写和空格需完全一致)
# post:     pm.expect(merchData.title).to.eql("API Test merch products T4623");
# post:     
# post:     // 验证 ListingType
# post:     pm.expect(merchData.listingType).to.eql("EVENT_PRODUCT");
# post:     
# post:     // 验证状态为 ACTIVE
# post:     pm.expect(merchData.status).to.eql("ACTIVE");
# post:     pm.expect(merchData.externalStatus).to.eql("ACTIVE");
# post: });
# --- step 8: b17ed723-c593-4126-a859-b26344a554b4 ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: const responseData = response.data;
# post: 
# post: /**
# post:  * 2. 提取 data.id 为环境变量
# post:  */
# post: if (responseData && responseData.id) {
# post:     // 这里我将其存为 post_id，你可以根据业务改为 event_id 等
# post:     pm.environment.set("post_id", responseData.id);
# post:     console.log("Environment variable 'post_id' set to:", responseData.id);
# post: }
# post: 
# post: /**
# post:  * 3. 字段断言
# post:  */
# post: 
# post: 
# post: // 校验 ID 格式
# post: pm.test("ID is a valid string", () => {
# post:     pm.expect(responseData.id).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 校验封面图数组
# post: pm.test("Cover images array is valid", () => {
# post:     pm.expect(responseData.coverImages).to.be.an('array').and.not.empty;
# post:     pm.expect(responseData.coverImages[0].mediaType).to.eql("IMAGE");
# post: });
# post: 
# post: // 校验创建时间格式 (ISO Date)
# post: pm.test("CreatedAt is valid date format", () => {
# post:     pm.expect(responseData.createdAt).to.match(/^\d{4}-\d{2}-\d{2}T/);
# post: });
# --- step 9: 1fe4714e-a605-4c72-bc40-23ec3ebb9032 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "Product deleted successfully", "path": "$.data.message", "multipleValue": [], "extractSettings": {"expression": "$.data.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: 98b537e6-a10c-43ef-9dde-4d2def64ed8a ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: 
# post: // 2. 校验外层 data 对象下的 title
# post: pm.test("校验活动标题（Event Title）是否正确", function () {
# post:     const actualTitle = response.data.title;
# post:     
# post:     // 注意：引号内 T4623 后面有一个空格，必须完全匹配
# post:     pm.expect(actualTitle).to.eql("API Test T4623 ");
# post: });
# post: 
# post: // 3. (可选) 如果你想更稳健一点，防止空格导致的意外失败，可以使用 trim() 或包含断言
# post: pm.test("校验活动标题（忽略首尾空格）", function () {
# post:     pm.expect(response.data.title.trim()).to.eql("API Test T4623");
# post: });
# post: 
# post: 
# --- step 11: 2de9333e-192e-4582-b7dd-e1c9993b8fb6 ---
# post[customScript]: // 1. Parse the response body
# post: const response = pm.response.json();
# post: const data = response.data;
# post: 
# post: /**
# post:  * Test: Basic Response Validation
# post:  */
# post: pm.test("Status code is 200 and message is success", () => {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(response.message).to.eql("success");
# post: });
# post: 
# post: /**
# post:  * Test: Validate Lineup/User ID Metadata
# post:  * Checking if the IDs exist and match the expected UUID format
# post:  */
# post: pm.test("Verify ID and EventID format", () => {
# post:     pm.expect(data.id).to.be.a('string').and.not.empty;
# post:     pm.expect(data.eventId).to.be.a('string').and.not.empty;
# post:     // Log the ID for record keeping
# post:     console.log("Captured ID:", data.id);
# post: });
# post: 
# post: /**
# post:  * Test: Validate Content Details
# post:  */
# post: pm.test("Verify Lineup content details", () => {
# post:     pm.expect(data.title).to.eql("LINDA00");
# post:     pm.expect(data.isHeadliner).to.be.true;
# post:     pm.expect(data.fee).to.eql(10000);
# post: });
# post: 
# post: /**
# post:  * Test: Validate Poster information
# post:  */
# post: pm.test("Verify Poster object structure", () => {
# post:     pm.expect(data.poster).to.have.property('src').that.includes('cloudinary');
# post:     pm.expect(data.poster.mediaType).to.eql("IMAGE");
# post: });
# post: 
# post: /**
# post:  * Save variables for the next API call
# post:  * Usually we need the record ID for future GET/PUT/DELETE requests
# post:  */
# post: if (data.id) {
# post:     pm.environment.set("current_record_id", data.id);
# post: }
# --- step 12: feeba47f-92aa-41cb-9bd3-113716ee458c ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: const data = response.data;
# post: 
# post: /**
# post:  * 2. 提取 id 并设置为环境变量
# post:  * 变量名：event_id
# post:  */
# post: if (data && data.id) {
# post:     pm.environment.set("event_id", data.id);
# post:     console.log("已成功设置环境变量 event_id: " + data.id);
# post: }
# post: 
# post: /**
# post:  * 3. 断言校验
# post:  */
# post: 
# post: 
# post: pm.test("Message is success", function () {
# post:     pm.expect(response.message).to.eql("success");
# post: });
# post: 
# post: // 校验 ID 是否存在且格式正确（非空字符串）
# post: pm.test("Verify Event ID existence and format", function () {
# post:     pm.expect(data.id).to.be.a('string').and.not.empty;
# post:     
# post:     // 如果你已经有一个预期的 event_id 变量，想检查两者是否一致：
# post:     // let expectedId = pm.environment.get("some_other_id"); 
# post:     // pm.expect(data.id).to.eql(expectedId);
# post: });
# post: 
# post: // 校验 ID 是否符合 UUID 格式（可选，增加健壮性）
# post: pm.test("ID is a valid UUID", function () {
# post:     const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
# post:     pm.expect(data.id).to.match(uuidRegex);
# post: });
# --- step 13: 8b6ba4f8-538c-402b-930e-f5caaf201f67 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "Product deleted successfully", "path": "$.data.message", "multipleValue": [], "extractSettings": {"expression": "$.data.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 14: ca7fde97-a17d-446d-a5ce-21cd38a5aaba ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "Product deleted successfully", "path": "$.data.message", "multipleValue": [], "extractSettings": {"expression": "$.data.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_linda_t4623_t4625_t4626_t4628_event_creation_whole_process(ctx):
    """Apifox case #7583841: Linda_T4623_T4625_T4626_T4628_Event_creation_whole_process"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+05@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}', app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: Get the target event id
    _resp2 = ctx.api.events.list(token='linda05_token', params={'pageNumber': '1', 'pageSize': '50', 'statuses': ['undefined']})
    _j = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    vars['created_event_id'] = _get_path(_j, ['data', 'items', 0, 'id'])
    # step 3: d0ae0406-88bc-4919-80d6-4ff5d19ead0e
    _resp3 = ctx.api.events.v2_1a2e22e6_076a_4176_949b_7ab63a149b3f_media_batch_operate(body='{"contentType":"image/jpeg"}', token='linda05_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # assertion 3.assertion: responseJson equal API Test T4623 
    expect(_resp3).json('$.data.title').equals('API Test T4623 ')
    # extractor: newMediaId = $.data.id
    ctx.extract('newMediaId', _resp3, '$.data.id')
    # step 4: 9a52ee2d-8472-44c2-b327-718b762d46dd
    _resp4 = ctx.api.products.create(body='{\n    "id": "dbda7839-bf02-4902-abb0-3f60885cc26d",\n    "remote_id": null,\n    "platform": "PEAR",\n    "createdAt": "2026-03-25T07:43:26.462Z",\n    "updatedAt": "2026-04-07T07:38:43.388Z",\n    "merchantId": "2ff36ba8-8a95-4b65-ae4b-39045e4fe28b",\n    "title": "API TEST T4623",\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n    "originalBodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n    "isBodyHtmlOverridden": false,\n    "bodyText": "\\n",\n    "handle": null,\n    "productType": "",\n    "publishedAt": "2026-03-25T07:43:26.457Z",\n    "publishedScope": "",\n    "status": "ACTIVE",\n    "externalStatus": "ACTIVE",\n    "followExternalStatus": false,\n    "tags": [],\n    "templateSuffix": null,\n    "vendor": "Pear",\n    "syncAt": null,\n    "deletedAt": null,\n    "delisted": false,\n    "excludedByImportingTag": false,\n    "isFeatured": false,\n    "featuredScore": null,\n    "inventoryQuantity": 1000,\n    "inventoryQuantityOriginal": 1000,\n    "soldQuantity": 0,\n    "priceDisplay": 12.22,\n    "priceDisplayAnchor": 0,\n    "priceMin": 12.22,\n    "priceMinAnchor": 0,\n    "priceMax": 12.22,\n    "priceMaxAnchor": 0,\n    "priceImportedMin": 0,\n    "priceImportedMax": 0,\n    "imageCount": 1,\n    "isUsed": "NWT",\n    "shippingType": "NO_SHIPPING_REQUIRED",\n    "additionalShippingFee": 0,\n    "deliveryTime": [\n        3,\n        5\n    ],\n    "returnPolicyApplied": true,\n    "isAvailable": true,\n    "commissionRate": 10,\n    "textForShare": null,\n    "priceSyncImported": false,\n    "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1774424456/uploaded_images/vkmcrkmiwcwkv3q4aisr.webp",\n        "width": 2560,\n        "height": 3413,\n        "mediaSrc": null,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n    },\n    "reviewCount": null,\n    "reviewOverallScore": null,\n    "reviewAggregate": null,\n    "displayReviews": true,\n    "links": null,\n    "taxEnable": true,\n    "taxJarCategory": "",\n    "customTaxRate": 0,\n    "subscriptionPlanId": null,\n    "reviewRedirectProductId": null,\n    "reviewSummary": null,\n    "customFieldsInfo": null,\n    "listingType": "TICKET",\n    "shippingOptions": [],\n    "shippingNote": null,\n    "autoFulfill": true,\n    "copyFromId": null,\n    "stopSellingAfter": null,\n    "deliveryMethod": "QR_CODE",\n    "thirdPartyDeliveryMessage": "",\n    "isMultipleDaysPassEnabled": false,\n    "multipleDaysPass": null,\n    "isPickupEtaEnabled": null,\n    "atDoorTicketConfig": null,\n    "excludeFromPostSync": false,\n    "expirationTime": null,\n    "allowAtDoorSales": false,\n    "options": [\n        {\n            "remote_id": null,\n            "productId": "dbda7839-bf02-4902-abb0-3f60885cc26d",\n            "name": "Title",\n            "position": 1,\n            "values": [\n                "Default Title"\n            ],\n            "images": [\n                {\n                    "value": "Default Title",\n                    "imageId": null\n                }\n            ]\n        }\n    ],\n    "variants": [\n        {\n            "id": "30caa2df-3c09-407b-8641-bd42440f86be",\n            "remote_id": null,\n            "createdAt": "2026-03-25T07:43:26.462Z",\n            "updatedAt": "2026-03-25T07:43:26.462Z",\n            "compareAtPrice": null,\n            "fulfillmentService": "manual",\n            "grams": 0,\n            "imageIds": [],\n            "inventoryItemId": null,\n            "inventoryManagement": "Pear",\n            "inventoryPolicy": "DENY",\n            "inventoryQuantity": 1000,\n            "inventoryQuantityOriginal": 1000,\n            "soldQuantity": 0,\n            "option": {\n                "option1": "Default Title"\n            },\n            "position": 1,\n            "price": "12.22",\n            "priceAnchor": "0",\n            "priceImported": "0.00",\n            "productId": "dbda7839-bf02-4902-abb0-3f60885cc26d",\n            "sku": "",\n            "taxCode": null,\n            "taxable": true,\n            "title": "Default Title",\n            "weight": null,\n            "weightUnit": null,\n            "platform": null,\n            "fees": 2.22,\n            "transactionFee": {\n                "customFee": 0,\n                "platformFee": 2.22,\n                "customFeeBreakdown": {\n                    "TAX": {\n                        "itemFee": 0,\n                        "unitFixedFee": 0,\n                        "unitPercentageFee": 0\n                    }\n                },\n                "transactionItemFee": 2.22\n            },\n            "ticketPrice": 10,\n            "isMinPurchaseQuantityEnabled": false,\n            "minPurchaseQuantity": null,\n            "isMaxPurchaseQuantityEnabled": false,\n            "maxPurchaseQuantity": null,\n            "isPackSizeEnabled": false,\n            "packSize": null\n        }\n    ],\n    "catalogCommissionRate": 25,\n    "isReturnPolicyAllowed": true,\n    "earliestTime": "2026-03-25T07:43:26.462Z",\n    "styleSettings": {\n        "recentUsedColors": [\n            "#B7E2E0FF",\n            "#FFEEBEFF",\n            "#E91E63FF",\n            "#757575FF",\n            "#0B99FFFF",\n            "#F2F2F6FF",\n            "#FFFFFF"\n        ]\n    },\n    "isProductFormEnabled": false,\n    "isVariantPriceDisplayEnabled": false,\n    "stopSellingAfterDisplay": "",\n    "extraInfo": {\n        "businessTimezone": "America/Los_Angeles"\n    },\n    "overrideEventTax": true,\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n    "images": [\n        {\n            "id": "18c01e12-c223-41c2-af4f-908f3dac450c",\n            "remote_id": null,\n            "createdAt": "2026-03-25T07:43:26.462Z",\n            "updatedAt": "2026-03-25T07:43:26.462Z",\n            "height": 3413,\n            "width": 2560,\n            "position": 1,\n            "productId": "dbda7839-bf02-4902-abb0-3f60885cc26d",\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1774424456/uploaded_images/vkmcrkmiwcwkv3q4aisr.webp",\n            "variantIds": [],\n            "mediaType": "IMAGE",\n            "mediaSrc": null,\n            "mediaDuration": 0,\n            "contributedBy": 3,\n            "contributorId": null,\n            "productImageType": "PRODUCT",\n            "source": "UPLOAD"\n        }\n    ],\n    "eventId": "1a2e22e6-076a-4176-949b-7ab63a149b3f",\n    "isExpirationEnabled": false\n}', token='linda05_token')
    # assertion 4.assertion: responseJson equal success
    expect(_resp4).json('$.message').equals('success')
    # assertion 4.assertion: responseJson equal API TEST T4623
    expect(_resp4).json('$.data.title').equals('API TEST T4623')
    # extractor: newticketid = $.data.id
    ctx.extract('newticketid', _resp4, '$.data.id')
    # step 5: 7b1e33e6-33a8-46df-a36e-a5d89449f117
    _resp5 = ctx.api.events.v2_1a2e22e6_076a_4176_949b_7ab63a149b3f_lineup_batch(body='{\r\n    "lineup": [\r\n        {\r\n            "title": "LINDA00",\r\n            "poster": {\r\n                "src": "https://res.cloudinary.com/dr9io1zjv/v1773365227/uploaded_images/l72b3ha8fchmmyus0hw3.webp",\r\n                "width": 1142,\r\n                "height": 1142,\r\n                "position": 0,\r\n                "mediaType": "IMAGE",\r\n                "mediaDuration": 0\r\n            },\r\n            "isHeadliner": true,\r\n            "customRecipientIdentifier": "linda.zhou.ext+00@1m.app",\r\n            "recipientVanityUrl": "https://release.pear.us/linda",\r\n            "fee": 10000,\r\n            "isPaymentAfterEventEnabled": true,\r\n            "userId": "7bc6ed8d-51de-446b-8c64-fd321cf1a45d",\r\n            "order": 0\r\n        }\r\n    ]\r\n}', token='linda05_token')
    # extract lineup_id from step 5 response (orig: lineupIds[0] = response.data.lineup[0].id)
    try:
        _j5 = _resp5.json() if _resp5.headers.get('content-type','').startswith('application/json') else {}
        _lineup = (_j5.get('data') or {}).get('lineup') or []
        vars['lineup_id'] = _lineup[0]['id'] if _lineup else None
    except Exception:
        pass
    # step 6: db28cc54-a7e6-40fa-8abc-69e4a9030aa0
    _resp6 = ctx.api.products.batch(body='{\r\n    "products": [\r\n        {\r\n            "title": "test 10282 002 by linda",\r\n            "listingType": "EVENT_PRODUCT",\r\n            "status": "ACTIVE",\r\n            "coverImage": {\r\n                "src": "https://res.cloudinary.com/dr9io1zjv/v1769393079/uploaded_images/sgxntt4fpvuz1w01d3ql.webp",\r\n                "width": 1192,\r\n                "height": 710,\r\n                "mediaSrc": null,\r\n                "mediaType": "IMAGE",\r\n                "mediaDuration": 0\r\n            },\r\n            "inventoryQuantity": 10000,\r\n            "soldQuantity": 0,\r\n            "priceMin": 200,\r\n            "priceMax": 200,\r\n            "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\r\n            "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\r\n            "images": [\r\n                {\r\n                    "id": "50a542ee-eba4-4e02-8162-74c7741e4c20",\r\n                    "remote_id": null,\r\n                    "createdAt": "2026-03-13T01:30:02.273Z",\r\n                    "updatedAt": "2026-03-13T01:30:02.273Z",\r\n                    "height": 710,\r\n                    "width": 1192,\r\n                    "position": 1,\r\n                    "productId": "50184bdd-6f45-4a2c-bae9-33cdbbaeeff5",\r\n                    "src": "https://res.cloudinary.com/dr9io1zjv/v1769393079/uploaded_images/sgxntt4fpvuz1w01d3ql.webp",\r\n                    "variantIds": [],\r\n                    "mediaType": "IMAGE",\r\n                    "mediaSrc": null,\r\n                    "mediaDuration": 0,\r\n                    "contributedBy": 3,\r\n                    "contributorId": null,\r\n                    "productImageType": "PRODUCT",\r\n                    "source": null\r\n                }\r\n            ],\r\n            "options": [\r\n                {\r\n                    "id": "5ef59091-dfb5-4527-b654-4b9555c54763",\r\n                    "remote_id": null,\r\n                    "productId": "50184bdd-6f45-4a2c-bae9-33cdbbaeeff5",\r\n                    "name": "Title",\r\n                    "position": 1,\r\n                    "values": [\r\n                        "Default Title"\r\n                    ],\r\n                    "images": [\r\n                        {\r\n                            "value": "Default Title",\r\n                            "imageId": null\r\n                        }\r\n                    ]\r\n                }\r\n            ],\r\n            "variants": [\r\n                {\r\n                    "id": "dffbf9ee-a741-4a74-98a1-a15e30ea6db1",\r\n                    "remote_id": null,\r\n                    "createdAt": "2026-03-13T01:30:02.273Z",\r\n                    "updatedAt": "2026-03-13T01:30:02.273Z",\r\n                    "compareAtPrice": null,\r\n                    "fulfillmentService": "manual",\r\n                    "grams": 0,\r\n                    "imageId": null,\r\n                    "imageIds": [],\r\n                    "inventoryItemId": null,\r\n                    "inventoryManagement": "Pear",\r\n                    "inventoryPolicy": "DENY",\r\n                    "inventoryQuantity": 10000,\r\n                    "inventoryQuantityOriginal": 10000,\r\n                    "soldQuantity": 0,\r\n                    "option": {\r\n                        "option1": "Default Title"\r\n                    },\r\n                    "position": 1,\r\n                    "price": "200",\r\n                    "priceAnchor": "0",\r\n                    "priceImported": "0.00",\r\n                    "productId": "50184bdd-6f45-4a2c-bae9-33cdbbaeeff5",\r\n                    "sku": "",\r\n                    "taxCode": null,\r\n                    "taxable": true,\r\n                    "title": "Default Title",\r\n                    "weight": null,\r\n                    "weightUnit": null,\r\n                    "platform": null,\r\n                    "fees": null,\r\n                    "transactionFee": {},\r\n                    "ticketPrice": 0,\r\n                    "isMinPurchaseQuantityEnabled": false,\r\n                    "minPurchaseQuantity": null,\r\n                    "isMaxPurchaseQuantityEnabled": false,\r\n                    "maxPurchaseQuantity": null,\r\n                    "isPackSizeEnabled": false,\r\n                    "packSize": null\r\n                }\r\n            ],\r\n            "merchantId": "67f02da6-a49c-4871-b907-f5134a62ece8",\r\n            "createdAt": "2026-03-13T01:30:02.245Z",\r\n            "lifecycleStatus": "LIFECYCLE_STATUS_ARCHIVED",\r\n            "deliveryMethod": "QR_CODE",\r\n            "isMultipleDaysPassEnabled": false,\r\n            "multipleDaysPass": null,\r\n            "overrideEventTax": false,\r\n            "customTaxRate": null,\r\n            "thirdPartyDeliveryMessage": null,\r\n            "excludeFromPostSync": false,\r\n            "isExpirationEnabled": false,\r\n            "expirationTime": null,\r\n            "expirationTimeDisplay": null,\r\n            "urlAlias": "0u3gy1",\r\n            "moduleIds": [],\r\n            "eventId": "1a2e22e6-076a-4176-949b-7ab63a149b3f",\r\n            "hasStopSellingAfter": false,\r\n            "shippingType": "NO_SHIPPING_REQUIRED"\r\n        }\r\n    ]\r\n}', token='linda05_token')
    # extract item_id from step 6 response (orig: item_id = items[0].id)
    try:
        _j6 = _resp6.json() if _resp6.headers.get('content-type','').startswith('application/json') else {}
        _items6 = (_j6.get('data') or {}).get('items') or []
        vars['item_id'] = _items6[0]['id'] if _items6 else None
    except Exception:
        pass
    # step 7: ee56085f-b700-422e-8107-92a552641ce0
    _resp7 = ctx.api.products.create(body='{\r\n    "merchantId": "2ff36ba8-8a95-4b65-ae4b-39045e4fe28b",\r\n    "shippingType": "NO_SHIPPING_REQUIRED",\r\n    "isFeatured": false,\r\n    "commissionRate": 10,\r\n    "priceSyncImported": false,\r\n    "additionalShippingFee": 0,\r\n    "returnPolicyApplied": true,\r\n    "title": "API Test merch products T4623",\r\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\r\n    "status": "ACTIVE",\r\n    "isUsed": "NWT",\r\n    "taxJarCategory": "",\r\n    "platform": "PEAR",\r\n    "autoFulfill": true,\r\n    "options": [\r\n        {\r\n            "name": "Title",\r\n            "values": [\r\n                "Default Title"\r\n            ],\r\n            "images": []\r\n        }\r\n    ],\r\n    "variants": [\r\n        {\r\n            "inventoryQuantity": 1000,\r\n            "price": 10,\r\n            "priceAnchor": 0,\r\n            "option": {\r\n                "option1": "Default Title"\r\n            }\r\n        }\r\n    ],\r\n    "listingType": "EVENT_PRODUCT",\r\n    "excludeFromPostSync": false,\r\n    "catalogCommissionRate": 25,\r\n    "shippingOptions": [\r\n        {\r\n            "id": "a69b5f3b-a5de-47b3-b570-75e460bc33b9",\r\n            "catalogId": "2ff36ba8-8a95-4b65-ae4b-39045e4fe28b",\r\n            "title": "Flat Shipping",\r\n            "shippingFee": 4.99,\r\n            "deliveryTime": [\r\n                0,\r\n                5\r\n            ],\r\n            "enableFreeShippingThreshold": false,\r\n            "freeShippingThreshold": 0,\r\n            "note": null,\r\n            "isDefault": true,\r\n            "weightBasedShippingRates": null,\r\n            "enableWeightBasedShippingRates": false,\r\n            "priceBasedShippingRates": null,\r\n            "enablePriceBasedShippingRates": false,\r\n            "profileName": null,\r\n            "from": "PEAR",\r\n            "additionalShippingFee": 0,\r\n            "enableAdditionalShippingFee": false\r\n        }\r\n    ],\r\n    "deliveryMethod": "QR_CODE",\r\n    "thirdPartyDeliveryMessage": "",\r\n    "taxEnable": false,\r\n    "customTaxRate": null,\r\n    "earliestTime": "2026-03-25T08:45:50.002Z",\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#FFEEBEFF",\r\n            "#E91E63FF",\r\n            "#757575FF",\r\n            "#0B99FFFF",\r\n            "#F2F2F6FF",\r\n            "#FFFFFF"\r\n        ]\r\n    },\r\n    "isVariantPriceDisplayEnabled": false,\r\n    "stopSellingAfterDisplay": "",\r\n    "extraInfo": {\r\n        "businessTimezone": "America/Los_Angeles"\r\n    },\r\n    "overrideEventTax": false,\r\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\r\n    "images": [\r\n        {\r\n            "mediaType": "IMAGE",\r\n            "mediaSrc": null,\r\n            "mediaDuration": 0,\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1769158656/uploaded_images/htfzut2cueemhhe9b5ed.webp",\r\n            "height": 2250,\r\n            "width": 3397,\r\n            "source": "UPLOAD",\r\n            "position": 1,\r\n            "setThumbnail": true,\r\n            "origin": {\r\n                "width": 3397,\r\n                "height": 2250,\r\n                "position": 1\r\n            },\r\n            "productImageType": "PRODUCT"\r\n        }\r\n    ],\r\n    "isMultipleDaysPassEnabled": false,\r\n    "eventId": "1a2e22e6-076a-4176-949b-7ab63a149b3f",\r\n    "isExpirationEnabled": false\r\n}', token='linda05_token')
    # extract merch_id from step 7 response (orig: merch_id = response.data.id)
    try:
        _j7 = _resp7.json() if _resp7.headers.get('content-type','').startswith('application/json') else {}
        vars['merch_id'] = (_j7.get('data') or {}).get('id')
    except Exception:
        pass
    # step 8: b17ed723-c593-4126-a859-b26344a554b4
    _resp8 = ctx.api.posts.curator_from_event(body='{\r\n    "styleSettings": {\r\n        "template": "ClearSky",\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "displayText": "SHOP_NAME",\r\n                "height": "MEDIUM"\r\n            },\r\n            "productBanner": {\r\n                "ctaButton": "VIEW_PRODUCT",\r\n                "display": "HIDE"\r\n            }\r\n        },\r\n        "fontFamily": "Inter",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "dividerColor": "#FFFFFF",\r\n        "secondaryTextColor": "#E0E0E0FF",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontFamily": "Inter",\r\n            "fontSize": 24,\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "fontFamily": "Inter",\r\n            "fontSize": 20,\r\n            "fontWeight": 700,\r\n            "color": "#FFFFFF"\r\n        },\r\n        "subtitle": {\r\n            "fontFamily": "Inter",\r\n            "fontSize": 20,\r\n            "fontWeight": 400,\r\n            "color": "#FFFFFF"\r\n        },\r\n        "button": {\r\n            "backgroundColor": "#F6CA7C",\r\n            "color": "#000000",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "boxShadow": "none",\r\n            "fontSize": 16,\r\n            "fontWeight": 400\r\n        },\r\n        "secondaryButton": {\r\n            "fontSize": 16,\r\n            "fontWeight": 400,\r\n            "color": "#FFFFFF",\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 0,\r\n            "boxShadow": "none"\r\n        },\r\n        "textButton": {\r\n            "fontSize": 16,\r\n            "fontWeight": 700,\r\n            "color": "#FFFFFF"\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "borderRadius": 0,\r\n            "color": "#000000 ",\r\n            "borderColor": "#0000",\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "color": "#FFFFFF",\r\n            "secondaryTextColor": "#E0E0E0FF",\r\n            "title": {\r\n                "fontFamily": "Inter",\r\n                "fontSize": 14,\r\n                "fontWeight": 400,\r\n                "color": "#FFFFFF"\r\n            }\r\n        },\r\n        "product": {\r\n            "backgroundColor": "#000000",\r\n            "borderRadius": 0,\r\n            "color": "#FFFFFF",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "discount": {\r\n            "backgroundColor": "#D32A09",\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF"\r\n        },\r\n        "freeShipping": {\r\n            "backgroundColor": "#EBF5EF",\r\n            "color": "#268E46"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "title": {\r\n                "fontFamily": "Inter",\r\n                "fontSize": 16,\r\n                "fontWeight": 700,\r\n                "color": "#FFFFFF"\r\n            },\r\n            "color": "#FFFFFF",\r\n            "secondaryTextColor": "#E0E0E0FF",\r\n            "button": {\r\n                "backgroundColor": "#F6CA7C",\r\n                "color": "#000000"\r\n            }\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF",\r\n            "secondaryText": "#ABABAB"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#E0E0E0FF",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 0\r\n            }\r\n        },\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#FFEEBEFF",\r\n            "#E91E63FF",\r\n            "#757575FF",\r\n            "#0B99FFFF",\r\n            "#F2F2F6FF",\r\n            "#FFFFFF"\r\n        ]\r\n    },\r\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"id\\":\\"e7775562-8581-4178-b2c1-a82f4943d2b2\\",\\"eventId\\":\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\",\\"type\\":\\"event-info-banner\\",\\"version\\":2},{\\"id\\":\\"102e2f61-f848-4a58-983e-9d83274ed12d\\",\\"type\\":\\"additional-content\\",\\"version\\":1},{\\"id\\":\\"386932a9-c84b-416e-b52c-cccc22e3cd44\\",\\"eventId\\":\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\",\\"productId\\":\\"e88d004b-fa7b-4952-bb1f-e238e46d7b7c\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"RSVP\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"496399ac-f790-4f68-a6ef-4c152c4dfb99\\",\\"eventId\\":\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\",\\"productId\\":\\"11efed21-fb56-462c-bc8c-29d12a5df5a4\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"RSVP\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"b8f59ab0-3f8e-4356-a78c-792fae0c9553\\",\\"eventId\\":\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\",\\"productId\\":\\"c0311c0d-b3eb-4ca8-90c7-255bd26345db\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1},{\\"id\\":\\"c5bdb6da-3c8e-48bf-8a9c-4c2c8f23e43c\\",\\"eventId\\":\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\",\\"productId\\":\\"dbda7839-bf02-4902-abb0-3f60885cc26d\\",\\"width\\":\\"100%\\",\\"height\\":\\"\\",\\"ctaLabel\\":\\"Buy Ticket\\",\\"action\\":\\"buy-now\\",\\"layout\\":\\"vertical\\",\\"type\\":\\"ticket-banner\\",\\"version\\":1}],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\r\n    "title": "API Test T4623 ",\r\n    "allowCustomizeDisplayPrices": true,\r\n    "autoReplace": false,\r\n    "featuredSectionEnable": false,\r\n    "featuredSectionTitle": "",\r\n    "customizeDisplayPrices": {\r\n        "price": "Instagram Live, Zoom, In-person | Thu, Mar 20 (CDT)",\r\n        "discountPercent": "Get Tickets",\r\n        "priceColor": "",\r\n        "discountPercentColor": "",\r\n        "titleColor": ""\r\n    },\r\n    "allowPromotersCreateCoupon": true,\r\n    "allowPromotersHideProducts": true,\r\n    "allowPromotersCustomizeMedia": true,\r\n    "allowPromotersResell": true,\r\n    "bodyHtml": "<div data-id=\\"e7775562-8581-4178-b2c1-a82f4943d2b2\\" data-type=\\"event-info-banner\\" data-event-id=\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\" data-width=\\"100%\\"></div><div data-id=\\"102e2f61-f848-4a58-983e-9d83274ed12d\\" data-type=\\"additional-content\\"></div><div data-id=\\"386932a9-c84b-416e-b52c-cccc22e3cd44\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\" data-product-id=\\"e88d004b-fa7b-4952-bb1f-e238e46d7b7c\\" data-cta-label=\\"RSVP\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"496399ac-f790-4f68-a6ef-4c152c4dfb99\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\" data-product-id=\\"11efed21-fb56-462c-bc8c-29d12a5df5a4\\" data-cta-label=\\"RSVP\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"b8f59ab0-3f8e-4356-a78c-792fae0c9553\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\" data-product-id=\\"c0311c0d-b3eb-4ca8-90c7-255bd26345db\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div><div data-id=\\"c5bdb6da-3c8e-48bf-8a9c-4c2c8f23e43c\\" data-width=\\"100%\\" data-height=\\"\\" data-event-id=\\"1a2e22e6-076a-4176-949b-7ab63a149b3f\\" data-product-id=\\"dbda7839-bf02-4902-abb0-3f60885cc26d\\" data-cta-label=\\"Buy Ticket\\" data-primary-action=\\"buy-now\\" data-layout=\\"vertical\\" data-thumbnail-display=\\"showThumbnail\\" data-event-notes-display=\\"showEventNotes\\"></div>",\r\n    "checkoutInPost": true,\r\n    "createFromEventId": "1a2e22e6-076a-4176-949b-7ab63a149b3f",\r\n    "timeKey": 1774428708701,\r\n    "additionalContent": "{}",\r\n    "media": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n            "width": 3072,\r\n            "height": 2048,\r\n            "position": 0,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "eventFill": true\r\n        }\r\n    ],\r\n    "othersCanCopy": false,\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n            "width": 3072,\r\n            "height": 2048,\r\n            "position": 0,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "eventFill": true,\r\n            "setThumbnail": true\r\n        }\r\n    ],\r\n    "expiredAt": null,\r\n    "urlAlias": "{{$internet.url}}",\r\n    "relatedProducts": [\r\n        {\r\n            "merchantProductId": "e88d004b-fa7b-4952-bb1f-e238e46d7b7c",\r\n            "isCtaCustomized": false,\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 0,\r\n                    "price": 0,\r\n                    "costPrice": 0,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "f8c56c34-1fea-48cf-a56f-05203f8c29d5",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "merchantProductId": "11efed21-fb56-462c-bc8c-29d12a5df5a4",\r\n            "isCtaCustomized": false,\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 0,\r\n                    "price": 0,\r\n                    "costPrice": 0,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "cb41aed0-8f42-4c39-8248-69fe2a3a21cb",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "merchantProductId": "c0311c0d-b3eb-4ca8-90c7-255bd26345db",\r\n            "isCtaCustomized": false,\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 11,\r\n                    "price": 12.22,\r\n                    "costPrice": 0,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "bf083fe0-e98e-4f2b-a6f3-995cad1209ac",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "merchantProductId": "dbda7839-bf02-4902-abb0-3f60885cc26d",\r\n            "isCtaCustomized": false,\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 11,\r\n                    "price": 12.22,\r\n                    "costPrice": 0,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "30caa2df-3c09-407b-8641-bd42440f86be",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        },\r\n        {\r\n            "merchantProductId": "8e214ff5-b502-4342-b19c-1c585d4e6452",\r\n            "isCtaCustomized": false,\r\n            "syncWithCatalogPrice": true,\r\n            "purchaseQuantityLimit": 1,\r\n            "variants": [\r\n                {\r\n                    "wholesalePriceForPromoters": 180,\r\n                    "price": 200,\r\n                    "costPrice": 0,\r\n                    "priceAnchor": 0,\r\n                    "merchantProductVariantId": "4034446d-2c1c-42de-af0b-2fce0a2bb941",\r\n                    "commissionRateForPromoters": 10\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "headline": "API Test T4623 ",\r\n    "isPaymentRestrictionEnabled": false\r\n}', token='linda05_token')
    ctx.extract('post_id', _resp8, '$.id')
    # step 9: 1fe4714e-a605-4c72-bc40-23ec3ebb9032
    _resp9 = ctx.api.products.by_newticketid(body=None, token='linda05_token')
    # assertion 9.assertion: responseJson equal Product deleted successfully
    expect(_resp9).json('$.data.message').equals('Product deleted successfully')
    # step 10: 98b537e6-a10c-43ef-9dde-4d2def64ed8a
    _resp10 = ctx.api.events.v2_media_batch_operate(body='{"medias":[]}', token='linda05_token')
    # step 11: 2de9333e-192e-4582-b7dd-e1c9993b8fb6
    _resp11 = ctx.api.events.v_1a2e22e6_076a_4176_949b_7ab63a149b3f_lineup_by_lineup_id(body='{\r\n    "eventId": "1a2e22e6-076a-4176-949b-7ab63a149b3f",\r\n    "id": "463be28d-fc24-40ae-97f3-4f827c7f819a"\r\n}', token='linda05_token')
    ctx.extract('current_record_id', _resp11, '$.data.id')
    # step 12: feeba47f-92aa-41cb-9bd3-113716ee458c
    _resp12 = ctx.api.posts.curator_by_post_id_2(body=None, token='linda05_token')
    ctx.extract('event_id', _resp12, '$.data.id')
    # step 13: 8b6ba4f8-538c-402b-930e-f5caaf201f67
    _resp13 = ctx.api.products.by_newticketid(body=None, token='linda05_token', path_vars={'newticketid': '{{item_id}}'})
    # assertion 13.assertion: responseJson equal Product deleted successfully
    expect(_resp13).json('$.data.message').equals('Product deleted successfully')
    # step 14: ca7fde97-a17d-446d-a5ce-21cd38a5aaba
    _resp14 = ctx.api.products.by_newticketid(body=None, token='linda05_token', path_vars={'newticketid': '{{merch_id}}'})
    # assertion 14.assertion: responseJson equal Product deleted successfully
    expect(_resp14).json('$.data.message').equals('Product deleted successfully')
