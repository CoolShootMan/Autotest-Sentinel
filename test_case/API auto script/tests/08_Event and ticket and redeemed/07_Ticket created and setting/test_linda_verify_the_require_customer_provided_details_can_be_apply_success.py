"""Migrated from Apifox case #8612233. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8612233  (traceability only — not needed to run)
NAME = "(Linda) Verify the Require customer-provided details can be apply success"
TAGS = ["p1", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:linda"]
PRIORITY = 1


CASE_ID = 8612233
ENV_NAME = "Release"

# --- step 1: 1a2c0dc7-6dbd-43d5-b287-b7ca8d2cd3a3 ---
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
# --- step 2: be129430-0fcc-476b-a8a1-3024d026d3fa ---
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
# --- step 3: f8103b38-4568-4c92-b48c-0c7094e1b58a ---
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
# --- step 4: 4cbbf838-a62d-440a-9d77-634dffb20024 ---
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
# post:     }
# --- step 5: ebaf8d1c-cb03-4d5c-90da-bfdfc60a2397 ---
# --- step 6: 707dd083-2b7c-45d3-aa91-58cbe0def93e ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 查找 title 为 "auto-test Verify the Require customer-provided details can be apply success" 的产品
# post: const targetProduct = responseData.data.relatedProducts.find(
# post:     item => item.title === "auto-test Verify the Require customer-provided details can be apply success"
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
# --- step 7: get address list ---
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
# --- step 8: b73cbc93-9e57-4b4c-ad89-4b8efc36c53f ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: buy now failed without input form content ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 断言 HTTP 状态码与错误信息
# post: pm.test("校验错误信息: Required field \"Name\" is missing", function () {
# post:     // 校验 400 状态码
# post:     pm.response.to.have.status(400);
# post:     pm.expect(responseData.code).to.eql(400);
# post: 
# post:     // 精确断言错误提示 message
# post:     pm.expect(responseData.message).to.eql('Required field "Name" is missing');
# post: });
# --- step 10: buy now success with input form content ---
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
# --- step 12: Check the merchant order detail exist customer filed contents ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "d1fdc475-8b15-49f0-8718-67c9efa988bf");
# pre: 
# pre: 
# pre: 
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
from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_verify_the_require_customer_provided_details_can_be_apply_success(ctx: "Context"):
    from core.compat import get_path as _get_path
    """Apifox case #8612233: Linda_Verify_the_Require_customer_provided_details_can_be_apply_success"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 1a2c0dc7-6dbd-43d5-b287-b7ca8d2cd3a3
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    # 原 step1 post-script: 在 data.items 中找 title === "event-for-API-testing" 的事件，取其 id。
    _items1 = _get_path(_resp1.json(), ['data', 'items']) or []
    _ev1 = next((i for i in _items1 if i.get('title') == 'event-for-API-testing'), None)
    assert _ev1, f"step1 未找到 title='event-for-API-testing' 的事件（items={len(_items1)}）"
    ctx.set('event_id', _ev1.get('id') or '')
    # step 2: be129430-0fcc-476b-a8a1-3024d026d3fa
    _resp2 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    # 原 step2 post-script: 在 data.items 中找 title === "event-for-API-testing" 的 post，取其 id。
    _items2 = _get_path(_resp2.json(), ['data', 'items']) or []
    _post2 = next((i for i in _items2 if i.get('title') == 'event-for-API-testing'), None)
    assert _post2, f"step2 未找到 title='event-for-API-testing' 的 post（items={len(_items2)}）"
    ctx.set('postId', _post2.get('id') or '')
    # step 3: f8103b38-4568-4c92-b48c-0c7094e1b58a
    _resp3 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    # 原 Apifox post-script: const catalogId = responseData.data.id → 提取为变量（修复：此前误把 JS 变量名当字面量）
    ctx.extract('catalog_id', _resp3, '$.data.id')
    # step 4: 4cbbf838-a62d-440a-9d77-634dffb20024
    _resp4 = ctx.api.products.create(body={
    'merchantId': '{{catalog_id}}',
    'shippingType': 'NO_SHIPPING_REQUIRED',
    'isFeatured': False,
    'commissionRate': 0,
    'priceSyncImported': False,
    'additionalShippingFee': 0,
    'returnPolicyApplied': True,
    'title': 'auto-test Verify the Require customer-provided details can be apply success',
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
            'inventoryQuantity': 100,
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
    'isReturnPolicyAllowed': False,
    'thirdPartyDeliveryMessage': '',
    'taxEnable': False,
    'customTaxRate': None,
    'earliestTime': '2026-08-10T09:44:29.878Z',
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
        'description': '',
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
    'extraInfo': {
        'businessTimezone': 'Asia/Shanghai',
    },
    'overrideEventTax': False,
    'overrideEventCustomFee': False,
    'hideFees': False,
    'transactionCustomFeeConfig': None,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
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
    'eventId': '{{event_id}}',
    'isExpirationEnabled': False,
}, token='yuxiao999_token')
    ctx.extract('productId', _resp4, '$.data.id')
    # step 5: ebaf8d1c-cb03-4d5c-90da-bfdfc60a2397
    _resp5 = ctx.api.events.v2_show_in_post(body={
        "productIds": [
            "{{productId}}",
        ],
        "posts": [
            {
                "postId": "{{postId}}",
                "isVisible": True,
            },
        ],
    }, token='yuxiao999_token')
    # step 6: 707dd083-2b7c-45d3-aa91-58cbe0def93e
    _resp6 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token', path_vars={'post0_id': '{{postId}}'})
    # 原 step6 post-script: 在 data.relatedProducts 中找 title 为目标产品的那一项，
    # 取其 displayVariantId 写入 promoterProductId（取不到时回退到 variants[0]）。
    _rels6 = _get_path(_resp6.json(), ['data', 'relatedProducts']) or []
    _prod6 = next((x for x in _rels6
                   if x.get('title') == 'auto-test Verify the Require customer-provided details can be apply success'),
                  None)
    assert _prod6, f"step6 未找到目标关联产品（relatedProducts={len(_rels6)}）"
    _v06 = (_prod6.get('variants') or [{}])[0]
    ctx.set('promoterProductId',
            _prod6.get('displayVariantId') or _v06.get('displayVariantId') or _v06.get('id') or '')
    # step 7: get address list
    _resp7 = ctx.api.address.list(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    # step 8: b73cbc93-9e57-4b4c-ad89-4b8efc36c53f
    _resp8 = ctx.api.cart.delete(body={}, app_headers=True, token='linda10_token')
    # assertion 8.assertion: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # assertion 8.assertion: responseJson equal success
    expect(_resp8).json('$.message').equals('success')
    # step 9: buy now failed without input form content
    _resp9 = ctx.api.orders.buy_now(body={
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
                "price": 0,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='linda10_token')
    _areaCodes = ["202","312","415","650","212","310","408","213","707"]
    vars['usPhoneNumber'] = '+1' + random.choice(_areaCodes) + str(random.randint(200, 999)) + str(random.randint(1000, 9999))
    # step 10: buy now success with input form content
    _resp10 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "{{postId}}",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 2,
                "postId": "{{postId}}",
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
                        "content": "{{$randomLastName}}",
                        "field": "PHONE_NUMBER",
                        "position": 2,
                        "title": "Phone",
                    },
                ],
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
                "price": 0,
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
    }, app_headers=True, token='linda10_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp10, '$.data.orderId')
    # step 11: place order
    _resp11 = ctx.api.orders.create(body={
    'id': '{{orderId}}',
    'contact': {
        'email': 'linda.zhou.ext+10@1m.app',
    },
    'shippingAddressId': '{{shippingAddressId}}',
    'fbAdParams': {
        'eventID': '58e159af-0e82-4244-b86d-00f37277e6a0',
        'pixelId': [
            '268933192948110',
        ],
        'fbBrowserId': 'fb.1.1745806891240.683423600239274570',
        'externalId': '9e32874f-1af5-4a26-88ad-a0a5cf1ad10c',
        'eventSourceUrl': 'https://release.pear.us/checkout?postId=ff6bbfb6-7146-44d9-985b-26eefbf740e3',
    },
}, app_headers=True, token='linda10_token')
    _ordernumber_val = _get_path(_resp8.json(), ['data', 'orderNumbers', 0])
    vars['order_number'] = _ordernumber_val if _ordernumber_val is not None else ''
    # step 12: Check the merchant order detail exist customer filed contents
    # === pre-script（由 Apifox customScript 翻译）===
    merchant_token = vars.get('merchant_token')
    orderNumber = vars.get('orderNumber')
    vars['merchantId'] = "d1fdc475-8b15-49f0-8718-67c9efa988bf"

    _resp12 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='yuxiao999_token', path_vars={'merchantId': '{{catalog_id}}', 'orderNumber': '{{order_number}}'})
