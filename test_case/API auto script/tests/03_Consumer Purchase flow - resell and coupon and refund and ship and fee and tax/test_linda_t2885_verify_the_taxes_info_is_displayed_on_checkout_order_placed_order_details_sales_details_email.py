"""Migrated from Apifox case #6151203. Source folder: Consumer Purchase flow - resell and coupon and refund and ship and fee and tax."""
# Apifox Case ID: 6151203  (traceability only — not needed to run)
NAME = "Verify the taxes info is displayed on checkout/order placed/order details/sales details/email"
TAGS = ["p0", "consumer_purchase_flow_resell_and_coupon_and_refund_and_ship_and_fee_and_tax", "suite:linda"]
PRIORITY = 0


CASE_ID = 6151203
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
# --- step 2: 2165a45d-d601-417c-8b81-d0ee0919d8b2 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: buy now ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "20", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: check UNFULFILLED - consumer order detail ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "20", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: Unfulfill - check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "20", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "lineItems_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].orderLineItemId", "extractSettings": {"expression": "$.data.lineItems[0].orderLineItemId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: make shipping ---
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "1", "path": "$.data.items[0].lineItems[0].fulfilledQuantity", "multipleValue": [], "extractSettings": {"expression": "$.data.items[0].lineItems[0].fulfilledQuantity", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "", "variableType": "local", "subject": "responseJson", "template": "", "expression": "", "extractSettings": {"expression": "", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: Fulfillment - check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "20", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "lineItems_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].id", "extractSettings": {"expression": "$.data.lineItems[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "FULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "1", "path": "$.data.lineItems[0].quantityFulfilled", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].quantityFulfilled", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "FULFILLED", "path": "$.data.fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: check "Fulfillment"  consumer order detail ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "FULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "20", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import json

from core.assertions import expect

def test_linda_t2885_verify_the_taxes_info_is_displayed_on_checkout_order_placed_order_details_sales_details_email(ctx):
    """Apifox case #6151203: Linda_T2885_Verify_the_taxes_info_is_displayed_on_checkout_order_placed_order_de"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: get address list
    _resp1 = ctx.api.address.list(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    # customScript: 提取地址ID（优先默认地址，无则取第一个）
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    _addr_items = ((_j1 or {}).get('data') or {}).get('items') or []
    _default_addr = next((a for a in _addr_items if a.get('isDefault') is True), None)
    vars['addressId'] = (_default_addr or _addr_items[0]).get('id') if _addr_items else ''
    # step 2: 2165a45d-d601-417c-8b81-d0ee0919d8b2
    _resp2 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n  "updateCartItems": [\n    {\n    "quantity": 1,\n    "promoterProductVariantId": "380e9b2b-47f9-49e4-8a6f-504b655fb6cf",\n    "price": 20,\n    "postId": "cb9ffbf6-7d76-49f5-a009-891af45aeee5",\n    "selected": true\n  }\n  ],\n  "currentUpdateCartItems": [\n    {\n    "quantity": 1,\n    "id": "380e9b2b-47f9-49e4-8a6f-504b655fb6cf",\n    "postId": "cb9ffbf6-7d76-49f5-a009-891af45aeee5",\n    "price": 20\n  }\n  ]\n}', app_headers=True, token='linda10_token')
    # assertion 3.assertion: responseJson equal 20
    expect(_resp3).json('$.data.totalToPay').equals('20')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp3, '$.data.orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 18,\n      "promoterVariantId": "19c3d76d-999d-4369-ae68-9d873a44111f"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "linda.zhou.ext+10@1m.app"\n  },\n  "shippingAddressId": "{{addressId}}"\n}', app_headers=True, token='linda10_token', params={'order_id': '{{order_id}}'})
    # assertion 4.code: responseJson equal 200
    expect(_resp4).json('$.code').equals('200')
    # assertion 4.assertion: responseJson exists 
    expect(_resp4).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp4, '$.data.orderNumbers[0]')
    # step 5: check UNFULFILLED - consumer order detail
    _resp5 = ctx.api.orders.consumer_detail_by_order_number(app_headers=True, token='linda10_token')
    # assertion 5.assertion: responseJson equal UNFULFILLED
    expect(_resp5).json('$.data.lineItems[0].fulfillmentStatus').equals('UNFULFILLED')
    # assertion 5.assertion: responseJson equal 20
    expect(_resp5).json('$.data.totalToPay').equals('20')
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 6: Unfulfill - check merchant order detail
    _resp6 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda00_token')
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal 20
    expect(_resp6).json('$.data.totalCommissionSubtotal').equals('20')
    # extractor: lineItems_id = $.data.lineItems[0].orderLineItemId
    ctx.extract('lineItems_id', _resp6, '$.data.lineItems[0].orderLineItemId')
    # assertion 6.assertion: responseJson equal UNFULFILLED
    expect(_resp6).json('$.data.lineItems[0].fulfillmentStatus').equals('UNFULFILLED')
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 7: make shipping
    _resp7 = ctx.api.orders.fulfillment_merchant_by_order_number(body='{\n    "trackingNumber": "{{$number.bigInt}}",\n    "makeShippingLineItems": [\n        {\n            "orderLineItemId": "{{lineItems_id}}",\n            "quantity": 1\n        }\n    ]\n}\n\n\n\n\n', token='linda00_token')
    # assertion 7.assertion: responseJson equal 1
    expect(_resp7).json('$.data.items[0].lineItems[0].fulfilledQuantity').equals('1')
    # extractor:  = 
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 8: Fulfillment - check merchant order detail
    _resp8 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda00_token')
    # assertion 8.assertion: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # assertion 8.assertion: responseJson equal 20
    expect(_resp8).json('$.data.totalCommissionSubtotal').equals('20')
    # extractor: lineItems_id = $.data.lineItems[0].id
    ctx.extract('lineItems_id', _resp8, '$.data.lineItems[0].id')
    # assertion 8.assertion: responseJson equal FULFILLED
    expect(_resp8).json('$.data.lineItems[0].fulfillmentStatus').equals('FULFILLED')
    # assertion 8.assertion: responseJson equal 1
    expect(_resp8).json('$.data.lineItems[0].quantityFulfilled').equals('1')
    # assertion 8.assertion: responseJson equal FULFILLED
    expect(_resp8).json('$.data.fulfillmentStatus').equals('FULFILLED')
    # step 9: check "Fulfillment"  consumer order detail
    _resp9 = ctx.api.orders.consumer_detail_by_order_number(app_headers=True, token='linda10_token')
    # assertion 9.assertion: responseJson equal FULFILLED
    expect(_resp9).json('$.data.lineItems[0].fulfillmentStatus').equals('FULFILLED')
    # assertion 9.assertion: responseJson equal 20
    expect(_resp9).json('$.data.totalToPay').equals('20')
