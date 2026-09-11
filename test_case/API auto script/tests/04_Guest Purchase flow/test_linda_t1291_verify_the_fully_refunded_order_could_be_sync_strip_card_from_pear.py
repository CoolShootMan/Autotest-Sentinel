"""Migrated from Apifox case #5748560. Source folder: Guest Purchase flow."""
# Apifox Case ID: 5748560  (traceability only — not needed to run)
NAME = "Verify the fully refunded order could be sync  -- Strip Card - From Pear"
TAGS = ["p0", "guest_purchase_flow", "suite:linda"]
PRIORITY = 0


CASE_ID = 5748560
ENV_NAME = "Release"

# --- step 1: 2194cf7a-ddac-4fcb-aa6a-73ad81100e8b ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 2: 6ffbf71c-7422-4b1b-8ae9-26dd2e030b50 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: buy now ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "734.51", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: get merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "d1fdc475-8b15-49f0-8718-67c9efa988bf");
# pre: 
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "587.61", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "NONE", "path": "$.data.lineItems[0].refundStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].refundStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "lineItems_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].id", "extractSettings": {"expression": "$.data.lineItems[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderLineItemId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].orderLineItemId", "extractSettings": {"expression": "$.data.lineItems[0].orderLineItemId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "dataId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderLineItemUnits", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].orderLineItemUnits[0].id", "extractSettings": {"expression": "$.data.lineItems[0].orderLineItemUnits[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: Create Merchant Refund ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: After Full Refunds, Get sale detail for order  ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "REFUNDED", "path": "$.data.lineItems[0].orderLineItemUnits[0].status", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].orderLineItemUnits[0].status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "FULLY_REFUNDED", "path": "$.data.paymentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.paymentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "-74.45", "path": "$.data.totalEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.totalEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "include", "value": "REFUNDED", "path": "$.data..orderLineItemUnits..ticketRedemptions..status", "multipleValue": [], "extractSettings": {"expression": "$.data..orderLineItemUnits..ticketRedemptions..status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: const json = pm.response.json(); 
# post: const v = Number(String(json.data.totalPayoutToPay).trim()); 
# post: pm.expect(v).to.be.closeTo(-74.45, 0.001)




import json

from core.assertions import expect

def test_linda_t1291_verify_the_fully_refunded_order_could_be_sync_strip_card_from_pear(ctx):
    """Apifox case #5748560: Linda_T1291_Verify_the_fully_refunded_order_could_be_sync_Strip_Card_From_Pear"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: 2194cf7a-ddac-4fcb-aa6a-73ad81100e8b
    _resp1 = ctx.api.auth.guest_login(body='{\r\n    "consumerId": "{{__uuid_0}}"\r\n}')
    vars['access_token'] = (_resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 2: 6ffbf71c-7422-4b1b-8ae9-26dd2e030b50
    _resp2 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n  "postIdForFilter": "02c93ce5-6e72-4252-a7b6-9b3525259985",\n  "updateCartItems": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "e1d7b321-bba5-4114-b252-ab08dbe32321",\n      "price": 778.89,\n      "postId": "02c93ce5-6e72-4252-a7b6-9b3525259985",\n      "selected": true\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "5eec4c14-7088-455a-a959-d95f348663cd",\n    "pixelId": [\n      "268933192948110"\n    ],\n    "fbBrowserId": "fb.1.1764140798676.563642823270509365",\n    "externalId": "4ab411c8-7faa-4c10-a01b-8399ca5015de",\n    "eventSourceUrl": "https://release.pear.us/lindazhoupromoter2/post/t4159"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 1,\n      "id": "e1d7b321-bba5-4114-b252-ab08dbe32321",\n      "postId": "02c93ce5-6e72-4252-a7b6-9b3525259985",\n      "price": 778.89\n    }\n  ]\n}', app_headers=True, token='access_token')
    # assertion 3.assertion: responseJson equal 734.51
    expect(_resp3).json('$.data.totalToPay').equals('734.51')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp3, '$.data.orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 20,\n      "promoterVariantId": "c4c30344-535d-48a1-a500-dcf5a2f59eb4"\n    }\n  ],\n  "inviterCampaign": {},\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "43@qibua.com"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+13022804650",\n    "ignoreVerifyPhoneNumber": "True"\n  }\n}\n\n\n\n', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 4.code: responseJson equal 200
    expect(_resp4).json('$.code').equals('200')
    # assertion 4.assertion: responseJson exists 
    expect(_resp4).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp4, '$.data.orderNumbers[0]')
    # step 5: get merchant order detail
    vars['merchantId'] = 'd1fdc475-8b15-49f0-8718-67c9efa988bf'
    _resp5 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda01_token', params={'catalogId': '9bd92082-07cd-4af5-8407-710d5f352a93', 'orderNumber': '{{orderNumber}}'})
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson equal 587.61
    expect(_resp5).json('$.data.totalCommissionSubtotal').equals('587.61')
    # assertion 5.assertion: responseJson equal NONE
    expect(_resp5).json('$.data.lineItems[0].refundStatus').equals('NONE')
    # extractor: lineItems_id = $.data.lineItems[0].id
    ctx.extract('lineItems_id', _resp5, '$.data.lineItems[0].id')
    # extractor: orderLineItemId = $.data.lineItems[0].orderLineItemId
    ctx.extract('orderLineItemId', _resp5, '$.data.lineItems[0].orderLineItemId')
    # extractor: dataId = $.data.id
    ctx.extract('dataId', _resp5, '$.data.id')
    # extractor: orderLineItemUnits = $.data.lineItems[0].orderLineItemUnits[0].id
    ctx.extract('orderLineItemUnits', _resp5, '$.data.lineItems[0].orderLineItemUnits[0].id')
    # step 6: Create Merchant Refund
    _resp6 = ctx.api.orders.refunds(body='{\n  "lineItems": [\n    {\n      "id": "{{orderLineItemId}}",\n      "quantity": 1,\n      "lineItemUnitIds": [\n        "{{orderLineItemUnits}}"\n      ]\n    }\n  ],\n  "shippingLines": [\n    {\n      "merchantOrderId": "{{dataId}}"\n    }\n  ],\n  "tipLines": [\n    {\n      "merchantOrderId": "{{dataId}}",\n      "tipAmount": 0\n    }\n  ],\n  "note": "refund test"\n}\n\n', app_headers=True, token='linda01_token', path_vars={'refund_id': '{{dataId}}'})
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # step 7: After Full Refunds, Get sale detail for order 
    _resp7 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda01_token')
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal REFUNDED
    expect(_resp7).json('$.data.lineItems[0].orderLineItemUnits[0].status').equals('REFUNDED')
    # assertion 7.assertion: responseJson equal FULLY_REFUNDED
    expect(_resp7).json('$.data.paymentStatus').equals('FULLY_REFUNDED')
    # assertion 7.assertion: responseJson equal -74.45
    expect(_resp7).json('$.data.totalEarning').equals('-74.45')
    # assertion 7.assertion: responseJson include REFUNDED
    expect(_resp7).json('$.data..orderLineItemUnits..ticketRedemptions..status').includes('REFUNDED')
