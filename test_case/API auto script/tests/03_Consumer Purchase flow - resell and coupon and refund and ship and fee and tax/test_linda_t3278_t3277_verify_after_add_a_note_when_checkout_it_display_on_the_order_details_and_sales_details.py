"""Migrated from Apifox case #6112168. Source folder: Consumer Purchase flow - resell and coupon and refund and ship and fee and tax."""
# Apifox Case ID: 6112168  (traceability only — not needed to run)
NAME = "& T3277 Verify after add a note when checkout, it display on the order details and sales details"
TAGS = ["p0", "consumer_purchase_flow_resell_and_coupon_and_refund_and_ship_and_fee_and_tax", "suite:linda"]
PRIORITY = 0


CASE_ID = 6112168
ENV_NAME = "Release"

# --- step 1: get address list ---
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
# --- step 2: 32ece22e-a265-40fe-9dff-15be514034ec ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: post detail ---
# post[extractor]: {"variableName": "promoterProductVariantId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[0].variants[0].id", "extractSettings": {"expression": "$.data.relatedProducts[0].variants[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "subscriptionPlanOptionid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId", "extractSettings": {"expression": "$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "postid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: buy now ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "144.99", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# pre: 
# pre: pm.environment.set("instructions", "API test by add a note");
# pre: 
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: Check the "note" display on the consumer order detail ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "144.99", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "60", "path": "$.data.totalLineItemSubscriptionDiscount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalLineItemSubscriptionDiscount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "contractId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].contractId", "extractSettings": {"expression": "$.data.lineItems[0].contractId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{instructions}}", "path": "$.data.instructions", "multipleValue": [], "extractSettings": {"expression": "$.data.instructions", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: Check the "note" display on the merchant sales detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{instructions}}", "path": "$.data.instructions", "multipleValue": [], "extractSettings": {"expression": "$.data.instructions", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.compat import get_path as _get_path
from core.assertions import expect
from core.compat import legacy_render

def test_linda_t3278_t3277_verify_after_add_a_note_when_checkout_it_display_on_the_order_details_and_sales_details(ctx):
    """Apifox case #6112168: Linda_T3278_T3277_Verify_after_add_a_note_when_checkout_it_display_on_the_order_"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    _render = legacy_render(ctx)
    # === Steps ===
    # step 1: get address list
    _resp1 = ctx.api.address.list(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    # Apifox 后置脚本（迁移时被丢弃）：优先取默认地址，否则取第一个
    _items = _get_path(_resp1.json(), ['data', 'items']) or []
    _dft = next((_i for _i in _items if _i.get('isDefault') is True), None)
    vars['addressId'] = ((_dft or _items[0]).get('id', '') if _items else '')
    # step 2: 32ece22e-a265-40fe-9dff-15be514034ec
    _resp2 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3: post detail
    _resp3 = ctx.api.posts.consumer_detail(params={'urlAlias': 'zr20it', 'vanityUrl': 'mcc'}, token='linda10_token')
    # extractor: promoterProductVariantId = $.data.relatedProducts[0].variants[0].id
    ctx.extract('promoterProductVariantId', _resp3, '$.data.relatedProducts[0].variants[0].id')
    # extractor: subscriptionPlanOptionid = $.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId
    ctx.extract('subscriptionPlanOptionid', _resp3, '$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId')
    # extractor: postid = $.data.id
    ctx.extract('postid', _resp3, '$.data.id')
    # step 4: buy now
    _resp4 = ctx.api.orders.buy_now(body='{\n  "updateCartItems": [\n    {\n    "quantity": 1,\n    "promoterProductVariantId": "{{promoterProductVariantId}}",\n    "price": 200,\n    "postId": "{{postid}}",\n    "selected": true,\n    "subscriptionPlanOptionId": "{{subscriptionPlanOptionid}}"\n  }\n  ],\n  "currentUpdateCartItems": [\n    {\n    "quantity": 1,\n    "id": "{{promoterProductVariantId}}",\n    "postId": "{{postid}}",\n    "price": 200\n  }\n  ]\n}', app_headers=True, token='linda10_token')
    # assertion 4.assertion: responseJson equal 144.99
    expect(_resp4).json('$.data.totalToPay').equals('144.99')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp4, '$.data.orderId')
    # step 5: create Order
    vars['instructions'] = 'API test by add a note'
    _resp5 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 140,\n      "promoterVariantId": "{{promoterProductVariantId}}"\n    }\n  ],\n  "id": "{{order_id}}",\n  "instructions": "{{instructions}}",\n  "contact": {\n    "email": "fos.zyx@gmail.com"\n  },\n  "shippingAddressId": "{{addressId}}"\n}\n\n\n\n\n\n', app_headers=True, token='linda10_token', params={'order_id': '{{order_id}}'})
    # assertion 5.code: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson exists 
    expect(_resp5).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp5, '$.data.orderNumbers[0]')
    # step 6: Check the "note" display on the consumer order detail
    _resp6 = ctx.api.orders.consumer_detail_by_order_number(app_headers=True, token='linda10_token')
    # assertion 6.assertion: responseJson equal UNFULFILLED
    expect(_resp6).json('$.data.lineItems[0].fulfillmentStatus').equals('UNFULFILLED')
    # assertion 6.assertion: responseJson equal 144.99
    expect(_resp6).json('$.data.totalToPay').equals('144.99')
    # assertion 6.assertion: responseJson equal 60
    expect(_resp6).json('$.data.totalLineItemSubscriptionDiscount').equals('60')
    # extractor: contractId = $.data.lineItems[0].contractId
    ctx.extract('contractId', _resp6, '$.data.lineItems[0].contractId')
    # assertion 6.assertion: responseJson equal {{instructions}}
    expect(_resp6).json('$.data.instructions').equals(str(_render('{{instructions}}', vars)))
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 7: Check the "note" display on the merchant sales detail
    _resp7 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda00_token')
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal {{instructions}}
    expect(_resp7).json('$.data.instructions').equals(str(_render('{{instructions}}', vars)))
