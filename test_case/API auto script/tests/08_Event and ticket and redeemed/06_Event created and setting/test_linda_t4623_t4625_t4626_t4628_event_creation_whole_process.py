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

from typing import Any, TYPE_CHECKING

from core.assertions import expect

from core.compat import get_path as _get_path

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t4623_t4625_t4626_t4628_event_creation_whole_process(ctx: "Context"):
    """Apifox case #7583841: Linda_T4623_T4625_T4626_T4628_Event_creation_whole_process"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body={
        "email": "linda.zhou.ext+05@1m.app",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: Get the target event id
    _resp2 = ctx.api.events.list(token='linda05_token', params={'pageNumber': '1', 'pageSize': '50', 'statuses': ['undefined']})
    _j: dict[str, Any] = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    vars['created_event_id'] = _get_path(_j, ['data', 'items', 0, 'id'])
    # step 3: d0ae0406-88bc-4919-80d6-4ff5d19ead0e
    _resp3 = ctx.api.events.v2_1a2e22e6_076a_4176_949b_7ab63a149b3f_media_batch_operate(body={
        "contentType": "image/jpeg",
    }, token='linda05_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # assertion 3.assertion: responseJson equal API Test T4623 
    expect(_resp3).json('$.data.title').equals('API Test T4623 ')
    # extractor: newMediaId = $.data.id
    ctx.extract('newMediaId', _resp3, '$.data.id')
    # step 4: 9a52ee2d-8472-44c2-b327-718b762d46dd
    _resp4 = ctx.api.products.create(body={
    'id': 'dbda7839-bf02-4902-abb0-3f60885cc26d',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-03-25T07:43:26.462Z',
    'updatedAt': '2026-04-07T07:38:43.388Z',
    'merchantId': '2ff36ba8-8a95-4b65-ae4b-39045e4fe28b',
    'title': 'API TEST T4623',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'isBodyHtmlOverridden': False,
    'bodyText': '\n',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-03-25T07:43:26.457Z',
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
    'inventoryQuantity': 1000,
    'inventoryQuantityOriginal': 1000,
    'soldQuantity': 0,
    'priceDisplay': 12.22,
    'priceDisplayAnchor': 0,
    'priceMin': 12.22,
    'priceMinAnchor': 0,
    'priceMax': 12.22,
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
    'commissionRate': 10,
    'textForShare': None,
    'priceSyncImported': False,
    'coverImage': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1774424456/uploaded_images/vkmcrkmiwcwkv3q4aisr.webp',
        'width': 2560,
        'height': 3413,
        'mediaSrc': None,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'reviewCount': None,
    'reviewOverallScore': None,
    'reviewAggregate': None,
    'displayReviews': True,
    'links': None,
    'taxEnable': True,
    'taxJarCategory': '',
    'customTaxRate': 0,
    'subscriptionPlanId': None,
    'reviewRedirectProductId': None,
    'reviewSummary': None,
    'customFieldsInfo': None,
    'listingType': 'TICKET',
    'shippingOptions': [],
    'shippingNote': None,
    'autoFulfill': True,
    'copyFromId': None,
    'stopSellingAfter': None,
    'deliveryMethod': 'QR_CODE',
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
            'productId': 'dbda7839-bf02-4902-abb0-3f60885cc26d',
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
            'id': '30caa2df-3c09-407b-8641-bd42440f86be',
            'remote_id': None,
            'createdAt': '2026-03-25T07:43:26.462Z',
            'updatedAt': '2026-03-25T07:43:26.462Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'inventoryQuantity': 1000,
            'inventoryQuantityOriginal': 1000,
            'soldQuantity': 0,
            'option': {
                'option1': 'Default Title',
            },
            'position': 1,
            'price': '12.22',
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': 'dbda7839-bf02-4902-abb0-3f60885cc26d',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Default Title',
            'weight': None,
            'weightUnit': None,
            'platform': None,
            'fees': 2.22,
            'transactionFee': {
                'customFee': 0,
                'platformFee': 2.22,
                'customFeeBreakdown': {
                    'TAX': {
                        'itemFee': 0,
                        'unitFixedFee': 0,
                        'unitPercentageFee': 0,
                    },
                },
                'transactionItemFee': 2.22,
            },
            'ticketPrice': 10,
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
    'earliestTime': '2026-03-25T07:43:26.462Z',
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
    'isProductFormEnabled': False,
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'extraInfo': {
        'businessTimezone': 'America/Los_Angeles',
    },
    'overrideEventTax': True,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'id': '18c01e12-c223-41c2-af4f-908f3dac450c',
            'remote_id': None,
            'createdAt': '2026-03-25T07:43:26.462Z',
            'updatedAt': '2026-03-25T07:43:26.462Z',
            'height': 3413,
            'width': 2560,
            'position': 1,
            'productId': 'dbda7839-bf02-4902-abb0-3f60885cc26d',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1774424456/uploaded_images/vkmcrkmiwcwkv3q4aisr.webp',
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
    'eventId': '1a2e22e6-076a-4176-949b-7ab63a149b3f',
    'isExpirationEnabled': False,
}, token='linda05_token')
    # assertion 4.assertion: responseJson equal success
    expect(_resp4).json('$.message').equals('success')
    # assertion 4.assertion: responseJson equal API TEST T4623
    expect(_resp4).json('$.data.title').equals('API TEST T4623')
    # extractor: newticketid = $.data.id
    ctx.extract('newticketid', _resp4, '$.data.id')
    # step 5: 7b1e33e6-33a8-46df-a36e-a5d89449f117
    _resp5 = ctx.api.events.v2_1a2e22e6_076a_4176_949b_7ab63a149b3f_lineup_batch(body={
        "lineup": [
            {
                "title": "LINDA00",
                "poster": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1773365227/uploaded_images/l72b3ha8fchmmyus0hw3.webp",
                    "width": 1142,
                    "height": 1142,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0,
                },
                "isHeadliner": True,
                "customRecipientIdentifier": "linda.zhou.ext+00@1m.app",
                "recipientVanityUrl": "https://release.pear.us/linda",
                "fee": 10000,
                "isPaymentAfterEventEnabled": True,
                "userId": "7bc6ed8d-51de-446b-8c64-fd321cf1a45d",
                "order": 0,
            },
        ],
    }, token='linda05_token')
    # extract lineup_id from step 5 response (orig: lineupIds[0] = response.data.lineup[0].id)
    try:
        _j5: dict[str, Any] = _resp5.json() if _resp5.headers.get('content-type','').startswith('application/json') else {}
        _lineup: list[Any] = (_j5.get('data') or {}).get('lineup') or []
        vars['lineup_id'] = _lineup[0]['id'] if _lineup else None
    except Exception:
        pass
    # step 6: db28cc54-a7e6-40fa-8abc-69e4a9030aa0
    _resp6 = ctx.api.products.batch(body={
    'products': [
        {
            'title': 'test 10282 002 by linda',
            'listingType': 'EVENT_PRODUCT',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1769393079/uploaded_images/sgxntt4fpvuz1w01d3ql.webp',
                'width': 1192,
                'height': 710,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10000,
            'soldQuantity': 0,
            'priceMin': 200,
            'priceMax': 200,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': '50a542ee-eba4-4e02-8162-74c7741e4c20',
                    'remote_id': None,
                    'createdAt': '2026-03-13T01:30:02.273Z',
                    'updatedAt': '2026-03-13T01:30:02.273Z',
                    'height': 710,
                    'width': 1192,
                    'position': 1,
                    'productId': '50184bdd-6f45-4a2c-bae9-33cdbbaeeff5',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1769393079/uploaded_images/sgxntt4fpvuz1w01d3ql.webp',
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
                    'id': '5ef59091-dfb5-4527-b654-4b9555c54763',
                    'remote_id': None,
                    'productId': '50184bdd-6f45-4a2c-bae9-33cdbbaeeff5',
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
                    'id': 'dffbf9ee-a741-4a74-98a1-a15e30ea6db1',
                    'remote_id': None,
                    'createdAt': '2026-03-13T01:30:02.273Z',
                    'updatedAt': '2026-03-13T01:30:02.273Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 10000,
                    'inventoryQuantityOriginal': 10000,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '200',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '50184bdd-6f45-4a2c-bae9-33cdbbaeeff5',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
            'merchantId': '67f02da6-a49c-4871-b907-f5134a62ece8',
            'createdAt': '2026-03-13T01:30:02.245Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_ARCHIVED',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': '0u3gy1',
            'moduleIds': [],
            'eventId': '1a2e22e6-076a-4176-949b-7ab63a149b3f',
            'hasStopSellingAfter': False,
            'shippingType': 'NO_SHIPPING_REQUIRED',
        },
    ],
}, token='linda05_token')
    # extract item_id from step 6 response (orig: item_id = items[0].id)
    try:
        _j6: dict[str, Any] = _resp6.json() if _resp6.headers.get('content-type','').startswith('application/json') else {}
        _items6: list[Any] = (_j6.get('data') or {}).get('items') or []
        vars['item_id'] = _items6[0]['id'] if _items6 else None
    except Exception:
        pass
    # step 7: ee56085f-b700-422e-8107-92a552641ce0
    _resp7 = ctx.api.products.create(body={
    'merchantId': '2ff36ba8-8a95-4b65-ae4b-39045e4fe28b',
    'shippingType': 'NO_SHIPPING_REQUIRED',
    'isFeatured': False,
    'commissionRate': 10,
    'priceSyncImported': False,
    'additionalShippingFee': 0,
    'returnPolicyApplied': True,
    'title': 'API Test merch products T4623',
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
            'inventoryQuantity': 1000,
            'price': 10,
            'priceAnchor': 0,
            'option': {
                'option1': 'Default Title',
            },
        },
    ],
    'listingType': 'EVENT_PRODUCT',
    'excludeFromPostSync': False,
    'catalogCommissionRate': 25,
    'shippingOptions': [
        {
            'id': 'a69b5f3b-a5de-47b3-b570-75e460bc33b9',
            'catalogId': '2ff36ba8-8a95-4b65-ae4b-39045e4fe28b',
            'title': 'Flat Shipping',
            'shippingFee': 4.99,
            'deliveryTime': [
                0,
                5,
            ],
            'enableFreeShippingThreshold': False,
            'freeShippingThreshold': 0,
            'note': None,
            'isDefault': True,
            'weightBasedShippingRates': None,
            'enableWeightBasedShippingRates': False,
            'priceBasedShippingRates': None,
            'enablePriceBasedShippingRates': False,
            'profileName': None,
            'from': 'PEAR',
            'additionalShippingFee': 0,
            'enableAdditionalShippingFee': False,
        },
    ],
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'taxEnable': False,
    'customTaxRate': None,
    'earliestTime': '2026-03-25T08:45:50.002Z',
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
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'extraInfo': {
        'businessTimezone': 'America/Los_Angeles',
    },
    'overrideEventTax': False,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1769158656/uploaded_images/htfzut2cueemhhe9b5ed.webp',
            'height': 2250,
            'width': 3397,
            'source': 'UPLOAD',
            'position': 1,
            'setThumbnail': True,
            'origin': {
                'width': 3397,
                'height': 2250,
                'position': 1,
            },
            'productImageType': 'PRODUCT',
        },
    ],
    'isMultipleDaysPassEnabled': False,
    'eventId': '1a2e22e6-076a-4176-949b-7ab63a149b3f',
    'isExpirationEnabled': False,
}, token='linda05_token')
    # extract merch_id from step 7 response (orig: merch_id = response.data.id)
    try:
        _j7: dict[str, Any] = _resp7.json() if _resp7.headers.get('content-type','').startswith('application/json') else {}
        vars['merch_id'] = (_j7.get('data') or {}).get('id')
    except Exception:
        pass
    # step 8: b17ed723-c593-4126-a859-b26344a554b4
    _resp8 = ctx.api.posts.curator_from_event(body={
        "styleSettings": {
            "template": "ClearSky",
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
            "color": "#FFFFFF",
            "backgroundColor": "#000000",
            "borderColor": "#000000",
            "dividerColor": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0FF",
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
                "borderColor": "#0000",
                "borderRadius": 0,
                "boxShadow": "none",
                "fontSize": 16,
                "fontWeight": 400,
            },
            "secondaryButton": {
                "fontSize": 16,
                "fontWeight": 400,
                "color": "#FFFFFF",
                "borderColor": "#F6CA7C",
                "borderRadius": 0,
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
                "borderRadius": 0,
                "color": "#000000 ",
                "borderColor": "#0000",
                "backgroundColor": "#FFFFFF80",
            },
            "featuredProducts": {
                "borderRadius": 0,
                "backgroundColor": "#000000",
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0FF",
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 14,
                    "fontWeight": 400,
                    "color": "#FFFFFF",
                },
            },
            "product": {
                "backgroundColor": "#000000",
                "borderRadius": 0,
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0FF",
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
                "secondaryTextColor": "#E0E0E0FF",
                "button": {
                    "backgroundColor": "#F6CA7C",
                    "color": "#000000",
                },
            },
            "lineupBanner": {
                "titleText": "#FFFFFF",
                "descriptionText": "#F6CA7C",
            },
            "eventInfoBanner": {
                "text": "#FFFFFF",
                "secondaryText": "#ABABAB",
            },
            "eventDescription": {
                "text": "#E0E0E0FF",
                "title": "#FFFFFF",
            },
            "featuredProduct": {
                "cover": {
                    "borderRadius": 0,
                },
            },
            "recentUsedColors": [
                "#B7E2E0FF",
                "#FFEEBEFF",
                "#E91E63FF",
                "#757575FF",
                "#0B99FFFF",
                "#F2F2F6FF",
                "#FFFFFF",
            ],
        },
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"e7775562-8581-4178-b2c1-a82f4943d2b2\",\"eventId\":\"1a2e22e6-076a-4176-949b-7ab63a149b3f\",\"type\":\"event-info-banner\",\"version\":2},{\"id\":\"102e2f61-f848-4a58-983e-9d83274ed12d\",\"type\":\"additional-content\",\"version\":1},{\"id\":\"386932a9-c84b-416e-b52c-cccc22e3cd44\",\"eventId\":\"1a2e22e6-076a-4176-949b-7ab63a149b3f\",\"productId\":\"e88d004b-fa7b-4952-bb1f-e238e46d7b7c\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"RSVP\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"496399ac-f790-4f68-a6ef-4c152c4dfb99\",\"eventId\":\"1a2e22e6-076a-4176-949b-7ab63a149b3f\",\"productId\":\"11efed21-fb56-462c-bc8c-29d12a5df5a4\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"RSVP\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"b8f59ab0-3f8e-4356-a78c-792fae0c9553\",\"eventId\":\"1a2e22e6-076a-4176-949b-7ab63a149b3f\",\"productId\":\"c0311c0d-b3eb-4ca8-90c7-255bd26345db\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1},{\"id\":\"c5bdb6da-3c8e-48bf-8a9c-4c2c8f23e43c\",\"eventId\":\"1a2e22e6-076a-4176-949b-7ab63a149b3f\",\"productId\":\"dbda7839-bf02-4902-abb0-3f60885cc26d\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"type\":\"ticket-banner\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
        "title": "API Test T4623 ",
        "allowCustomizeDisplayPrices": True,
        "autoReplace": False,
        "featuredSectionEnable": False,
        "featuredSectionTitle": "",
        "customizeDisplayPrices": {
            "price": "Instagram Live, Zoom, In-person | Thu, Mar 20 (CDT)",
            "discountPercent": "Get Tickets",
            "priceColor": "",
            "discountPercentColor": "",
            "titleColor": "",
        },
        "allowPromotersCreateCoupon": True,
        "allowPromotersHideProducts": True,
        "allowPromotersCustomizeMedia": True,
        "allowPromotersResell": True,
        "bodyHtml": "<div data-id=\"e7775562-8581-4178-b2c1-a82f4943d2b2\" data-type=\"event-info-banner\" data-event-id=\"1a2e22e6-076a-4176-949b-7ab63a149b3f\" data-width=\"100%\"></div><div data-id=\"102e2f61-f848-4a58-983e-9d83274ed12d\" data-type=\"additional-content\"></div><div data-id=\"386932a9-c84b-416e-b52c-cccc22e3cd44\" data-width=\"100%\" data-height=\"\" data-event-id=\"1a2e22e6-076a-4176-949b-7ab63a149b3f\" data-product-id=\"e88d004b-fa7b-4952-bb1f-e238e46d7b7c\" data-cta-label=\"RSVP\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"496399ac-f790-4f68-a6ef-4c152c4dfb99\" data-width=\"100%\" data-height=\"\" data-event-id=\"1a2e22e6-076a-4176-949b-7ab63a149b3f\" data-product-id=\"11efed21-fb56-462c-bc8c-29d12a5df5a4\" data-cta-label=\"RSVP\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"b8f59ab0-3f8e-4356-a78c-792fae0c9553\" data-width=\"100%\" data-height=\"\" data-event-id=\"1a2e22e6-076a-4176-949b-7ab63a149b3f\" data-product-id=\"c0311c0d-b3eb-4ca8-90c7-255bd26345db\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div><div data-id=\"c5bdb6da-3c8e-48bf-8a9c-4c2c8f23e43c\" data-width=\"100%\" data-height=\"\" data-event-id=\"1a2e22e6-076a-4176-949b-7ab63a149b3f\" data-product-id=\"dbda7839-bf02-4902-abb0-3f60885cc26d\" data-cta-label=\"Buy Ticket\" data-primary-action=\"buy-now\" data-layout=\"vertical\" data-thumbnail-display=\"showThumbnail\" data-event-notes-display=\"showEventNotes\"></div>",
        "checkoutInPost": True,
        "createFromEventId": "1a2e22e6-076a-4176-949b-7ab63a149b3f",
        "timeKey": 1774428708701,
        "additionalContent": "{}",
        "media": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                "width": 3072,
                "height": 2048,
                "position": 0,
                "mediaType": "IMAGE",
                "mediaDuration": 0,
                "eventFill": True,
            },
        ],
        "othersCanCopy": False,
        "coverImages": [
            {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                "width": 3072,
                "height": 2048,
                "position": 0,
                "mediaType": "IMAGE",
                "mediaDuration": 0,
                "eventFill": True,
                "setThumbnail": True,
            },
        ],
        "expiredAt": None,
        "urlAlias": "{{$internet.url}}",
        "relatedProducts": [
            {
                "merchantProductId": "e88d004b-fa7b-4952-bb1f-e238e46d7b7c",
                "isCtaCustomized": False,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 0,
                        "costPrice": 0,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "f8c56c34-1fea-48cf-a56f-05203f8c29d5",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
            {
                "merchantProductId": "11efed21-fb56-462c-bc8c-29d12a5df5a4",
                "isCtaCustomized": False,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 0,
                        "price": 0,
                        "costPrice": 0,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "cb41aed0-8f42-4c39-8248-69fe2a3a21cb",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
            {
                "merchantProductId": "c0311c0d-b3eb-4ca8-90c7-255bd26345db",
                "isCtaCustomized": False,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 11,
                        "price": 12.22,
                        "costPrice": 0,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "bf083fe0-e98e-4f2b-a6f3-995cad1209ac",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
            {
                "merchantProductId": "dbda7839-bf02-4902-abb0-3f60885cc26d",
                "isCtaCustomized": False,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 11,
                        "price": 12.22,
                        "costPrice": 0,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "30caa2df-3c09-407b-8641-bd42440f86be",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
            {
                "merchantProductId": "8e214ff5-b502-4342-b19c-1c585d4e6452",
                "isCtaCustomized": False,
                "syncWithCatalogPrice": True,
                "purchaseQuantityLimit": 1,
                "variants": [
                    {
                        "wholesalePriceForPromoters": 180,
                        "price": 200,
                        "costPrice": 0,
                        "priceAnchor": 0,
                        "merchantProductVariantId": "4034446d-2c1c-42de-af0b-2fce0a2bb941",
                        "commissionRateForPromoters": 10,
                    },
                ],
            },
        ],
        "headline": "API Test T4623 ",
        "isPaymentRestrictionEnabled": False,
    }, token='linda05_token')
    ctx.extract('post_id', _resp8, '$.id')
    # step 9: 1fe4714e-a605-4c72-bc40-23ec3ebb9032
    _resp9 = ctx.api.products.by_newticketid(body=None, token='linda05_token')
    # assertion 9.assertion: responseJson equal Product deleted successfully
    expect(_resp9).json('$.data.message').equals('Product deleted successfully')
    # step 10: 98b537e6-a10c-43ef-9dde-4d2def64ed8a
    _resp10 = ctx.api.events.v2_media_batch_operate(body={
        "medias": [],
    }, token='linda05_token')
    # step 11: 2de9333e-192e-4582-b7dd-e1c9993b8fb6
    _resp11 = ctx.api.events.v_1a2e22e6_076a_4176_949b_7ab63a149b3f_lineup_by_lineup_id(body={
        "eventId": "1a2e22e6-076a-4176-949b-7ab63a149b3f",
        "id": "463be28d-fc24-40ae-97f3-4f827c7f819a",
    }, token='linda05_token')
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
