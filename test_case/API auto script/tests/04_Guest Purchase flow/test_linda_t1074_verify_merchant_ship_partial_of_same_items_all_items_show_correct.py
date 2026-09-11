"""Migrated from Apifox case #5814765. Source folder: Guest Purchase flow."""
# Apifox Case ID: 5814765  (traceability only — not needed to run)
NAME = "Verify merchant ship partial of same items, all items show correct"
TAGS = ["p0", "guest_purchase_flow", "suite:linda"]
PRIORITY = 0


CASE_ID = 5814765
ENV_NAME = "Release"

# --- step 1: Guest login ---
# post[extractor]: {"variableName": "access_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data", "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 56727729-8340-4343-83b7-edcdd51cff5d ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 3 items buy now ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "60", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: Unfulfill - check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "60", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "lineItems_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].orderLineItemId", "extractSettings": {"expression": "$.data.lineItems[0].orderLineItemId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: 5a7c0d38-f109-4b10-807b-942f77dc0ad9 ---
# --- step 7: Partial Fulfillment - check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "60", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "lineItems_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].id", "extractSettings": {"expression": "$.data.lineItems[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "PARTIALLY_FULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_linda_t1074_verify_merchant_ship_partial_of_same_items_all_items_show_correct(ctx):
    """Apifox case #5814765: Linda_T1074_Verify_merchant_ship_partial_of_same_items_all_items_show_correct"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: Guest login
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "{{__uuid_0}}"\n}')
    # extractor: access_token = $.data
    ctx.extract('access_token', _resp1, '$.data')
    # step 2: 56727729-8340-4343-83b7-edcdd51cff5d
    _resp2 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3: 3 items buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n  "updateCartItems": [\n    {\n    "quantity": 3,\n    "promoterProductVariantId": "380e9b2b-47f9-49e4-8a6f-504b655fb6cf",\n    "price": 20,\n    "postId": "cb9ffbf6-7d76-49f5-a009-891af45aeee5",\n    "selected": true\n  }\n  ],\n  "currentUpdateCartItems": [\n    {\n    "quantity": 3,\n    "id": "380e9b2b-47f9-49e4-8a6f-504b655fb6cf",\n    "postId": "cb9ffbf6-7d76-49f5-a009-891af45aeee5",\n    "price": 20\n  }\n  ]\n}', app_headers=True, token='access_token')
    # assertion 3.assertion: responseJson equal 60
    expect(_resp3).json('$.data.totalToPay').equals('60')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp3, '$.data.orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 18,\n      "promoterVariantId": "19c3d76d-999d-4369-ae68-9d873a44111f"\n    }\n  ],\n  "inviterCampaign": {},\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "43@qibua.com"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+13022804650",\n    "ignoreVerifyPhoneNumber": "True"\n  }\n}', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 4.code: responseJson equal 200
    expect(_resp4).json('$.code').equals('200')
    # assertion 4.assertion: responseJson exists 
    expect(_resp4).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp4, '$.data.orderNumbers[0]')
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 5: Unfulfill - check merchant order detail
    _resp5 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda00_token')
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson equal 60
    expect(_resp5).json('$.data.totalCommissionSubtotal').equals('60')
    # extractor: lineItems_id = $.data.lineItems[0].orderLineItemId
    ctx.extract('lineItems_id', _resp5, '$.data.lineItems[0].orderLineItemId')
    # assertion 5.assertion: responseJson equal UNFULFILLED
    expect(_resp5).json('$.data.lineItems[0].fulfillmentStatus').equals('UNFULFILLED')
    # step 6: 5a7c0d38-f109-4b10-807b-942f77dc0ad9
    _resp6 = ctx.api.orders.fulfillment_merchant_by_order_number(body='{\r\n    "trackingNumber": "{{$number.bigInt}}",\r\n    "makeShippingLineItems": [\r\n        {\r\n            "orderLineItemId": "{{lineItems_id}}",  \r\n            "quantity": 1\r\n        }\r\n    ]\r\n}', token='linda00_token')
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 7: Partial Fulfillment - check merchant order detail
    _resp7 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda00_token')
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal 60
    expect(_resp7).json('$.data.totalCommissionSubtotal').equals('60')
    # extractor: lineItems_id = $.data.lineItems[0].id
    ctx.extract('lineItems_id', _resp7, '$.data.lineItems[0].id')
    # assertion 7.assertion: responseJson equal PARTIALLY_FULFILLED
    expect(_resp7).json('$.data.lineItems[0].fulfillmentStatus').equals('PARTIALLY_FULFILLED')
