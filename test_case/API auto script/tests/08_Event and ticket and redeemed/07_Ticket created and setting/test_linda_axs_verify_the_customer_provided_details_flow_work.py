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





from typing import TYPE_CHECKING, Callable, TypeVar

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


_T = TypeVar("_T")

def _pick_first(items: list[_T], predicate: Callable[[_T], bool]) -> _T | None:
    """返回 items 中第一个满足 predicate 的元素；未命中返回 None。"""
    return next((i for i in items if predicate(i)), None)


def _product_has_stock(product: dict) -> bool:
    """原 post-script 的库存判定：优先 ``variants[0].inventoryQuantity``，
    回退 ``product.inventoryQuantity``，> 0 视为有货。"""
    variants = product.get('variants') or []
    inv = variants[0].get('inventoryQuantity') if variants else None
    if inv is None:
        inv = product.get('inventoryQuantity')
    try:
        return float(inv or 0) > 0
    except (TypeError, ValueError):
        return False


def _apply_related_product(ctx: "Context", product: dict) -> None:
    """把「首个库存 > 0 的关联产品」的字段写入上下文（原 step5 post-script）。

    一律写空串/0 而非 None —— ``templating.render_text`` 会**跳过 None** 的值，
    占位符便无法被替换而原样残留进 request body。
    """
    variants = product.get('variants') or []
    variant0 = variants[0] if variants else {}
    assert isinstance(variant0, dict), "variants 元素应为 dict"
    hub = (product.get('extraInfo') or {}).get('ticketHubInfo') or {}
    sections = hub.get('sectionOptions') or []
    section0 = sections[0] if sections else {}
    assert isinstance(section0, dict), "sectionOptions 元素应为 dict"
    try:
        quantity = int(float(section0.get('availableQuantity') or 0))
    except (TypeError, ValueError):
        quantity = 0
    ctx.set('ticket_title', (product.get('title') or '').strip())
    ctx.set('productId', product.get('merchantProductId')
            or (product.get('shippingView') or {}).get('productId') or '')
    ctx.set('promoterProductId', product.get('promoterProductId') or '')
    ctx.set('merchantProductVariantId', variant0.get('merchantProductVariantId') or '')
    ctx.set('displayVariantId', variant0.get('displayVariantId')
            or product.get('displayVariantId') or '')
    ctx.set('ticketHubInfo_id', hub.get('ticketHandle') or '')
    ctx.set('ticketHandle', section0.get('ticketHandle') or '')
    ctx.set('availableQuantity', quantity)
    ctx.set('sectionIds', section0.get('label') or '')
    # 源 section 自带 isGeneralAdmission（GA 票为 True、有座区为 False）。
    # 下游 step6 的 body 把它写死成 True，与源数据不一致会让 hub 校验失败，故按源值透传。
    ctx.set('isGeneralAdmission', bool(section0.get('isGeneralAdmission', True)))



def test__8706050__Linda_AXS_Verify_the_Customer_provided_details_flow_work(ctx: "Context"):
    from core.compat import get_path as _get_path
    """Apifox case #8706050: Linda_AXS_Verify_the_Customer_provided_details_flow_work"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: f25b1efc-89d7-45ce-970f-da05a0ac3925
    _resp1 = ctx.api.auth.sign_in(body={
        "email": "{{UIauto_partner_email}}",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    }, app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    ctx.extract('yuxiao999_token', _resp1, '$.data.token')
    # step 2: 66d5d716-3a02-4b8c-a925-0485796bcb40
    _resp2 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    # 原 step2 post-script: 在 data.items 中找首个 platform === "AXS" 的项目，
    # 取其 id/title 写入 event_id/event_title。
    _items2: list[dict] = (_resp2.json().get('data') or {}).get('items') or []
    _axs_event = _pick_first(_items2, lambda i: i.get('platform') == 'AXS')
    assert _axs_event, f"step2 事件列表中未找到 platform=AXS 的项目（items={len(_items2)}）"
    ctx.set('event_id', _axs_event.get('id') or '')
    ctx.set('event_title', _axs_event.get('title') or '')
    # step 3: c10ed67d-5174-4977-9f37-b1a977fddbb2
    _resp3 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    _post0id_val = _get_path(_resp3.json(), ['data', 'items', 0, 'id'])
    vars['post0_id'] = _post0id_val if _post0id_val is not None else ''
    # step 4: 3a42a638-1733-468e-8343-378e4a35997f
    _resp4 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    # 原 Apifox post-script: const catalogId = responseData.data.id → 提取为变量
    ctx.extract('catalog_id', _resp4, '$.data.id')
    # step 5: 335db91f-b619-4cb9-9bf3-799455463f16
    _resp5 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    # 原 step5 post-script: 在 data.relatedProducts 中取首个库存 > 0 的产品，提取
    # title/merchantProductId/promoterProductId/variants[0].*/ticketHubInfo.* 共 9 个变量。
    _rels5: list[dict] = (_resp5.json().get('data') or {}).get('relatedProducts') or []
    _prod5 = _pick_first(_rels5, _product_has_stock)
    assert _prod5, f"step5 未找到库存 > 0 的关联产品（relatedProducts={len(_rels5)}）"
    _apply_related_product(ctx, _prod5)
    # step 6: 7a6d4176-bb6b-499b-9cc7-b7e7ba3ce08b
    _resp6 = ctx.api.products.by_product_id_general_admission_02(body={
    'id': '{{productId}}',
    'remote_id': None,
    'platform': 'AXS',
    'createdAt': '2026-09-03T09:44:42.495Z',
    'updatedAt': '2026-09-04T07:34:07.545Z',
    'merchantId': '{{catalog_id}}',
    'title': '{{ticket_title}}',
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
        'mediaSrc': None,
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
    'shippingOptions': [],
    'shippingNote': None,
    'autoFulfill': True,
    'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
    'copyFromId': None,
    'stopSellingAfter': None,
    'deliveryMethod': 'THIRD_PARTY_ISSUED',
    'thirdPartyDeliveryMessage': 'Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.',
    'isMultipleDaysPassEnabled': False,
    'isVenueUnitEnabled': False,
    'venueUnitCategoryId': None,
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
            'createdAt': '2026-09-03T09:44:42.518Z',
            'updatedAt': '2026-09-03T09:44:42.518Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'isInventoryQuantityUnlimited': False,
            'inventoryQuantityOriginal': '{{availableQuantity}}',
            'soldQuantity': 0,
            'position': 1,
            'priceImported': '0.00',
            'productId': '{{productId}}',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'weight': None,
            'weightUnit': 'lb',
            'platform': None,
            'transactionFee': {
                'platformFee': 6.58,
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
                'transactionItemFee': 6.58,
            },
            'isMinPurchaseQuantityEnabled': True,
            'minPurchaseQuantity': 1,
            'isMaxPurchaseQuantityEnabled': True,
            'maxPurchaseQuantity': 4,
            'isPackSizeEnabled': False,
            'packSize': None,
            'transactionFeeConfig': None,
            'transactionFeeRebateConfig': None,
            'minPriceForCheckFees': 0,
            'title': 'Default Title',
            'option': {
                'option1': 'Default Title',
            },
            'price': 55.88,
            'ticketPrice': 49.3,
            'fees': 6.58,
            'priceAnchor': 0,
            'inventoryQuantity': '{{availableQuantity}}',
        },
    ],
    'readOnlyFields': [
        'ticketPrice',
        'fees',
        'price',
        'priceAnchor',
        'inventoryQuantity',
        'variantsEnabled',
        'tax',
        'customFees',
    ],
    'isInventoryQuantityUnlimited': False,
    'showInEventPost': True,
    'visibleInPosts': [
        {
            'postId': '{{post0_id}}',
            'isVisible': True,
        },
    ],
    'excludeFromPostSync': False,
    'catalogCommissionRate': 25,
    'hasLimitPurchaseQuantity': True,
    'hasSpecialRedemption': False,
    'earliestTime': '2026-09-03T09:44:42.495Z',
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
            'setThumbnail': True,
        },
    ],
    'eventId': '{{event_id}}',
    'isExpirationEnabled': False,
}, token='yuxiao999_token', path_vars={'productId_General_Admission_02': '{{productId}}'})
    # step 8: Get consumer linda10 token
    _resp8 = ctx.api.auth.sign_in(body={
        "email": "linda.zhou.ext+10@1m.app",
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
    })
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp8, '$.data.token')
    # step 9: f76d84f0-f008-4e1d-9681-cb886143e8fc
    _resp9 = ctx.api.cart.delete(body={}, app_headers=True, token='linda10_token')
    # assertion 9.assertion: responseJson equal 200
    expect(_resp9).json('$.code').equals('200')
    # assertion 9.assertion: responseJson equal success
    expect(_resp9).json('$.message').equals('success')
    # 原 pre-request script: usPhoneNumber = `+1${randomAreaCode}${random7Digits}`
    # （随机生成美国手机号）。此前迁移成了把变量名本身当值写死的 'usPhoneNumber'。
    import random as _random
    ctx.set('usPhoneNumber',
            '+1' + _random.choice(['202', '312', '415', '650', '212', '310'])
            + str(_random.randint(1000000, 9999999)))
    # step 10: 25bd242e-da1a-4a23-8754-10ad95bb3bef
    _resp10 = ctx.api.orders.checkout_express(body={
        "items": [
            {
                "promoterProductVariantId": "{{displayVariantId}}",
                "postId": "{{post0_id}}",
                "quantity": 1,
                "price": 55.88,
                "sectionIds": [
                    "{{sectionIds}}",
                ],
                "ticketHandle": "{{ticketHandle}}",
                "eventId": "{{event_id}}",
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
        "fbAdParams": {
            "eventID": "dc72ffe2-6310-4f66-b5c3-ca3074a83af9",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1788427187167.268347998920074386",
            "externalId": "a35633fe-c8b3-4542-a776-64f146731b31",
            "eventSourceUrl": "https://release.pear.us/autotestshop/post/zack-fox-dj-set-1",
        },
        "subdomainVanityUrl": "",
    }, app_headers=True, token='linda10_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp10, '$.data.orderId')
    # step 11: place order
    _resp11 = ctx.api.orders.create(body={
        "id": "{{orderId}}",
        "contact": {
            "email": "linda.zhou.ext+10@1m.app",
        },
        "shippingAddressId": "{{shippingAddressId}}",
        "paymentInfo": {
            "paymentMethodId": "{{pay_method_id}}",
        },
        "fbAdParams": {
            "eventID": "58e159af-0e82-4244-b86d-00f37277e6a0",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1745806891240.683423600239274570",
            "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",
            "eventSourceUrl": "https://release.pear.us/checkout?postId=ff6bbfb6-7146-44d9-985b-26eefbf740e3",
        },
    }, skip_notifications=False, token='linda10_token')
    # order_number 取自 place order 的响应（原 step11 post-script: responseData.data.orderNumbers[0]）。
    _ordernumber_val = _get_path(_resp11.json(), ['data', 'orderNumbers', 0])
    vars['order_number'] = _ordernumber_val if _ordernumber_val is not None else ''
    # step 12: Check the merchant order detail exist ticket Redemptions contents
    _resp12 = ctx.api.orders.merchant_detail_v2(token='yuxiao999_token', path_vars={'merchantId': '{{catalog_id}}', 'orderNumber': '{{order_number}}'})
