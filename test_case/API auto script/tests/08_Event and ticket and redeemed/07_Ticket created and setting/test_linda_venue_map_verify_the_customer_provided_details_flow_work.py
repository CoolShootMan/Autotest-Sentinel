"""Migrated from Apifox case #8660684. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8660684  (traceability only — not needed to run)
NAME = "(Linda)(Venue map) Verify the Customer-provided details flow work"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:linda"]
PRIORITY = 0


CASE_ID = 8660684
ENV_NAME = "Release"

# --- step 1: c9f8abe8-fc31-4afc-a02f-ed291aa77517 ---
# post[extractor]: {"variableName": "yuxiao999_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 1d0047fb-2151-45bb-9764-9ad95a222266 ---
# pre: pm.environment.set("event_title", "event-for-api-auto-venue-map");
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 指定目标 Event 的 title（可以从环境变量拿，也可以在此指定）
# post: const targetEventTitle = pm.environment.get("event_title") || "Auto-Test-post-setting";
# post: 
# post: // 3. 查找匹配的 Event 对象
# post: const targetEvent = responseData.data?.items?.find(
# post:     item => item.title === targetEventTitle
# post: );
# post: 
# post: // 4. 断言并提取 event_id
# post: pm.test(`找到 title 为 [${targetEventTitle}] 的事件并提取 event_id`, function () {
# post:     pm.expect(targetEvent, `列表中未找到 title 为 [${targetEventTitle}] 的事件`).to.be.an('object');
# post:     pm.expect(targetEvent.id, "提取的 event_id 格式不正确").to.be.a('string').and.not.empty;
# post: 
# post:     const eventId = targetEvent.id;
# post:     pm.environment.set("event_id", eventId);
# post:     console.log(`已成功提取 event_id [${eventId}]（对应标题: ${targetEventTitle}）`);
# post: });
# post: 
# post: // 5. 从该 Event 内部提取指定 Ticket 的 ID 并设置为 copyFromId
# post: pm.test("从匹配的事件中动态提取 copyFromId", function () {
# post:     // 确保 Event 存在且 tickets 数组不为空
# post:     pm.expect(targetEvent?.tickets, "目标事件下未查找到任何 tickets").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 方案 A：如果要找特定 Ticket 标题（例如 "General Admission"）
# post:     const targetTicketTitle = "General Admission"; 
# post:     let matchedTicket = targetEvent.tickets.find(t => t.title === targetTicketTitle);
# post: 
# post:     // 方案 B（备用）：如果找不到指定标题，默认取该事件下的第 1 个 Ticket
# post:     if (!matchedTicket) {
# post:         matchedTicket = targetEvent.tickets[0];
# post:     }
# post: 
# post:     // 校验 Ticket 及 ID
# post:     pm.expect(matchedTicket, "未提取到有效的 Ticket 对象").to.be.an('object');
# post:     pm.expect(matchedTicket.id, "提取的 ticket id 格式不正确").to.be.a('string').and.not.empty;
# post: 
# post:     // 设置环境变量
# post:     const copyFromId = matchedTicket.id;
# post:     pm.environment.set("copyFromId", copyFromId);
# post: 
# post:     console.log(`已成功提取 copyFromId [${copyFromId}]（对应 Ticket 标题: ${matchedTicket.title}）`);
# post: });
# --- step 3: 93f8576a-3627-40da-9e8c-da769061db88 ---
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
# --- step 4: 9e4780d8-8424-4058-b104-74921554cf20 ---
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
# --- step 5: 9ae76895-28f0-42c4-881a-00ee02925703 ---
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
# --- step 6: 2c877493-cea9-4398-b82d-6f44d1eb26ae ---
# --- step 7: 4eb88c11-4f3a-413b-b776-5f3a7f7f38d7 ---
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
# --- step 9: Get consumer linda10 token ---
# post[extractor]: {"variableName": "linda10_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: 7260d74e-6573-4b5c-89a3-ff30aead383a ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: bdeb5f48-4627-4476-b58e-b2424f1ce56d ---
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
# --- step 12: place order ---
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
# --- step 13: Check the merchant order detail exist ticket Redemptions contents ---
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




import random
import json

from typing import Any, TYPE_CHECKING

from core.assertions import expect

from core.compat import get_path as _get_path

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_venue_map_verify_the_customer_provided_details_flow_work(ctx: "Context"):
    """Apifox case #8660684: Linda_Venue_map_Verify_the_Customer_provided_details_flow_work"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: c9f8abe8-fc31-4afc-a02f-ed291aa77517
    _resp1 = ctx.api.auth.sign_in(body={
        "email": "{{UIauto_partner_email}}",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    ctx.extract('yuxiao999_token', _resp1, '$.data.token')
    # step 2: 1d0047fb-2151-45bb-9764-9ad95a222266
    # === pre-script（由 Apifox customScript 翻译）===
    vars['event_title'] = "event-for-api-auto-venue-map"

    _resp2 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    vars['event_id'] = 'eventId'
    _j: dict[str, Any] = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items", 0, "tickets"]) or []
    _x = next((_z for _z in _arr if _z.get('title') == "General Admission"), None)
    if _x: vars['copyFromId'] = _x.get('id')
    # step 3: 93f8576a-3627-40da-9e8c-da769061db88
    _resp3 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    _post0id_val = _get_path(_resp3.json(), ['data', 'items', 0, 'id'])
    vars['post0_id'] = _post0id_val if _post0id_val is not None else ''
    # step 4: 9e4780d8-8424-4058-b104-74921554cf20
    _resp4 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    vars['catalog_id'] = 'catalogId'
    # step 5: 9ae76895-28f0-42c4-881a-00ee02925703
    _resp5 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    # step 6: 2c877493-cea9-4398-b82d-6f44d1eb26ae
    _resp6 = ctx.api.products.by_product_id_general_admission_02(body={
    'id': '{{productId_General_Admission}}',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-08-25T06:03:23.924Z',
    'updatedAt': '2026-08-25T06:03:24.041Z',
    'merchantId': '{{catalog_id}}',
    'title': 'General Admission',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'originalBodyHtml': '',
    'isBodyHtmlOverridden': False,
    'bodyText': '',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-08-25T06:03:23.969Z',
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
    'inventoryQuantity': 10000,
    'inventoryQuantityOriginal': 10000,
    'soldQuantity': 0,
    'priceDisplay': 92.22,
    'priceDisplayAnchor': 0,
    'priceMin': 92.22,
    'priceMinAnchor': 0,
    'priceMax': 92.22,
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
    'commissionRate': 7,
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
    'taxEnable': False,
    'taxJarCategory': '',
    'customTaxRate': None,
    'subscriptionPlanId': None,
    'reviewRedirectProductId': None,
    'reviewSummary': None,
    'customFieldsInfo': None,
    'listingType': 'TICKET',
    'ticketType': 'TICKET_TYPE_STANDARD',
    'ticketHubInfo': None,
    'customizedFields': [],
    'shippingOptions': [],
    'shippingNote': None,
    'autoFulfill': True,
    'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
    'copyFromId': '{{copyFromId}}',
    'stopSellingAfter': None,
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'isMultipleDaysPassEnabled': False,
    'isVenueUnitEnabled': True,
    'venueUnitCategoryId': '{{venueUnitCategoryId}}',
    'multipleDaysPass': None,
    'isPickupEtaEnabled': None,
    'eventMatchingRules': None,
    'expirationTime': None,
    'allowAtDoorSales': False,
    'isTipEnabled': False,
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
    'options': [
        {
            'remote_id': None,
            'productId': '{{productId_General_Admission}}',
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
            'id': '{{merchantProductVariantId_General_Admission}}',
            'remote_id': None,
            'createdAt': '2026-08-25T06:03:24.041Z',
            'updatedAt': '2026-08-25T07:03:25.712Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'isInventoryQuantityUnlimited': False,
            'inventoryQuantity': 15,
            'inventoryQuantityOriginal': 10000,
            'soldQuantity': 0,
            'option': {
                'option1': 'Default Title',
            },
            'position': 1,
            'price': 92.22,
            'priceAnchor': 0,
            'priceImported': '0.00',
            'productId': '{{productId_General_Admission}}',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Default Title',
            'weight': None,
            'weightUnit': 'lb',
            'platform': None,
            'fees': 10.22,
            'transactionFee': {
                'platformFee': 10.22,
                'customFee': 0,
                'customFeeBreakdown': {
                    'TAX': {
                        'title': 'Taxes',
                        'unitFixedFee': 0,
                        'unitPercentageFee': 0,
                        'index': 0,
                        'itemFee': 0,
                    },
                },
                'transactionItemFee': 10.22,
            },
            'ticketPrice': 82,
            'isMinPurchaseQuantityEnabled': False,
            'minPurchaseQuantity': None,
            'isMaxPurchaseQuantityEnabled': False,
            'maxPurchaseQuantity': None,
            'isPackSizeEnabled': False,
            'packSize': None,
            'transactionFeeConfig': None,
            'transactionFeeRebateConfig': None,
            'minPriceForCheckFees': 0,
        },
    ],
    'readOnlyFields': [],
    'isInventoryQuantityUnlimited': False,
    'showInEventPost': True,
    'visibleInPosts': [
        {
            'postId': '{{post0_id}}',
            'isVisible': True,
        },
    ],
    'excludeFromPostSync': False,
    'catalogCommissionRate': 0,
    'hasLimitPurchaseQuantity': False,
    'hasSpecialRedemption': False,
    'earliestTime': '2026-08-25T04:00:00.000Z',
    'styleSettings': {
        'recentUsedColors': [
            '#ffffff',
        ],
    },
    'isProductFormEnabled': True,
    'isInclusionsEnabled': False,
    'inclusions': [],
    'productForm': {
        'title': 'contact form for autotest',
        'subtitle': 'autotest',
        'iconImage': '',
        'showImage': False,
        'formFields': [
            {
                'field': 'SHORT_ANSWER',
                'required': True,
                'title': 'Name',
                'position': 1,
                'label': 'Short answer text field',
                'isInitial': True,
            },
            {
                'field': 'PHONE_NUMBER',
                'required': True,
                'title': 'Phone',
                'position': 2,
                'label': 'Phone number',
                'isInitial': True,
            },
            {
                'field': 'EMAIL_ADDRESS',
                'required': True,
                'title': 'Email',
                'position': 3,
                'label': 'Email address',
                'isInitial': True,
            },
        ],
    },
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'overrideEventTax': False,
    'overrideEventCustomFee': False,
    'hideFees': False,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'id': '3e8e3f1e-5555-4dea-9a34-b27ef8592ab6',
            'remote_id': None,
            'createdAt': '2026-08-25T06:03:24.041Z',
            'updatedAt': '2026-08-25T06:03:24.041Z',
            'height': 1000,
            'width': 1000,
            'position': 1,
            'productId': '{{productId_General_Admission}}',
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png',
            'variantIds': [],
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'contributedBy': 3,
            'contributorId': None,
            'productImageType': 'PRODUCT',
            'source': None,
            'setThumbnail': True,
        },
    ],
    'eventId': '{{event_id}}',
    'isExpirationEnabled': False,
}, token='yuxiao999_token', path_vars={'productId_General_Admission_02': '{{productId_General_Admission}}'})
    # step 7: 4eb88c11-4f3a-413b-b776-5f3a7f7f38d7
    _resp7 = ctx.api.events.tickets_venue_units(body=None, params={'pageNumber': '1', 'pageSize': '30', 'variantId': '{merchantProductVariantId_General_Admission}'}, token='yuxiao999_token', path_vars={'productId_General_Admission_02': '{{productId_General_Admission}}'})
    vars['unitid'] = 'unitId'
    _j: dict[str, Any] = _resp7.json() if _resp7.headers.get('content-type','').startswith('application/json') else {}
    vars['seatNumber'] = str(_get_path(_j, ['data', 'items', 0, 'number']))
    _j: dict[str, Any] = _resp7.json() if _resp7.headers.get('content-type','').startswith('application/json') else {}
    vars['venueUnitCategoryId'] = _get_path(_j, ['data', 'items', 0, 'categoryId'])
    # step 9: Get consumer linda10 token
    _resp9 = ctx.api.auth.sign_in(body={
        "email": "linda.zhou.ext+10@1m.app",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp9, '$.data.token')
    # step 10: 7260d74e-6573-4b5c-89a3-ff30aead383a
    _resp10 = ctx.api.cart.delete(body={}, app_headers=True, token='linda10_token')
    # assertion 10.assertion: responseJson equal 200
    expect(_resp10).json('$.code').equals('200')
    # assertion 10.assertion: responseJson equal success
    expect(_resp10).json('$.message').equals('success')
    _areaCodes = ["202","312","415","650","212","310","408","213","707"]
    vars['usPhoneNumber'] = '+1' + random.choice(_areaCodes) + str(random.randint(200, 999)) + str(random.randint(1000, 9999))
    # step 11: bdeb5f48-4627-4476-b58e-b2424f1ce56d
    _resp11 = ctx.api.orders.checkout_express(body={
        "fbAdParams": {
            "eventID": "0e23d7da-dab0-4dc8-a27c-96ea822f38ad",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1787626769799.674084567126480531",
            "externalId": "7d70692d-84f0-4b50-bcda-abc39b7d165a",
            "eventSourceUrl": "https://release.pear.us/autotestshop/post/event-for-api-auto-venue-map",
        },
        "items": [
            {
                "quantity": 1,
                "promoterProductVariantId": "{{displayVariantId_General_Admission}}",
                "price": 112.22,
                "postId": "{{post0_id}}",
                "eventId": "{{event_id}}",
                "sectionName": "General Admission",
                "seatRow": "",
                "seatNumber": "{{seatNumber}}",
                "unitId": "{{unitid}}",
                "selected": True,
                "customFields": [
                    {
                        "content": "{{$internet.email(locale='en')}}",
                        "field": "EMAIL_ADDRESS",
                        "position": 3,
                        "title": "Email",
                    },
                    {
                        "content": "{{$randomFullName}}",
                        "field": "SHORT_ANSWER",
                        "position": 1,
                        "title": "Name",
                    },
                    {
                        "content": "{{usPhoneNumber}}",
                        "field": "PHONE_NUMBER",
                        "position": 2,
                        "title": "Phone",
                    },
                ],
            },
        ],
        "subdomainVanityUrl": "",
    }, app_headers=True, token='linda10_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp11, '$.data.orderId')
    # step 12: place order
    _resp12 = ctx.api.orders.create(body={
        "id": "{{orderId}}",
        "contact": {
            "email": "linda.zhou.ext+10@1m.app",
        },
        "shippingAddressId": "{{shippingAddressId}}",
        "fbAdParams": {
            "eventID": "58e159af-0e82-4244-b86d-00f37277e6a0",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1745806891240.683423600239274570",
            "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",
            "eventSourceUrl": "https://release.pear.us/checkout?postId=ff6bbfb6-7146-44d9-985b-26eefbf740e3",
        },
    }, app_headers=True, token='linda10_token')
    _ordernumber_val = _get_path(_resp11.json(), ['data', 'orderNumbers', 0])
    vars['order_number'] = _ordernumber_val if _ordernumber_val is not None else ''
    # step 13: Check the merchant order detail exist ticket Redemptions contents
    _resp13 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='yuxiao999_token', path_vars={'merchantId': '{{catalog_id}}', 'orderNumber': '{{order_number}}'})
