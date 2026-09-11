"""Migrated from Apifox case #5735876. Source folder: Guest Purchase flow."""
# Apifox Case ID: 5735876  (traceability only — not needed to run)
NAME = "Verify the partilly refunded order could be sync  -- Strip Card - From Admin"
TAGS = ["p0", "guest_purchase_flow", "suite:linda"]
PRIORITY = 0


CASE_ID = 5735876
ENV_NAME = "Release"

# --- step 1: 31b4cf7b-2ce1-442d-a64f-f9caf7896d13 ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 2: 0503484f-b508-44cf-8ee3-3a83477fba43 ---
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
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "d1fdc475-8b15-49f0-8718-67c9efa988bf");
# pre: 
# pre: 
# pre: 
# pre: 
# pre: 
# pre: 
# pre: 
# pre: 
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "734.51", "path": "$.data.summary.productSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.summary.productSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "total", "subject": "responseJson", "comparison": "equal", "value": "369.64", "path": "$.data.summary.total", "multipleValue": [], "extractSettings": {"expression": "$.data.summary.total", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "NOT_REFUNDED", "path": "$.data.refundStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.refundStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "lineItems_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].id", "extractSettings": {"expression": "$.data.lineItems[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "merchantOrderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].merchantOrderId", "extractSettings": {"expression": "$.data.lineItems[0].merchantOrderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: adc5fa8a-c82d-4386-a483-e23fee773ead ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_id}}", "path": "$.data.orderRefund.orderId", "multipleValue": [], "extractSettings": {"expression": "$.data.orderRefund.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "12", "path": "$.data.orderRefund.totalLineItemRefunded", "multipleValue": [], "extractSettings": {"expression": "$.data.orderRefund.totalLineItemRefunded", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.orderRefund.totalShippingRefunded", "multipleValue": [], "extractSettings": {"expression": "$.data.orderRefund.totalShippingRefunded", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "12", "path": "$.data.orderRefund.totalRefunded", "multipleValue": [], "extractSettings": {"expression": "$.data.orderRefund.totalRefunded", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: After Parital Refunds, Get sale detail for order  ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "12", "path": "$.data.refundSummary.totalRefunded", "multipleValue": [], "extractSettings": {"expression": "$.data.refundSummary.totalRefunded", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "362.92", "path": "$.data.summary.total", "multipleValue": [], "extractSettings": {"expression": "$.data.summary.total", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "12", "path": "$.data.refundSummary.totalRefunded", "multipleValue": [], "extractSettings": {"expression": "$.data.refundSummary.totalRefunded", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "12", "path": "$.data.refundSummary.totalLineItemRefunded", "multipleValue": [], "extractSettings": {"expression": "$.data.refundSummary.totalLineItemRefunded", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.refundSummary.totalShippingRefunded", "multipleValue": [], "extractSettings": {"expression": "$.data.refundSummary.totalShippingRefunded", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import json

from core.assertions import expect
from core.compat import legacy_render

def test_linda_t1291_verify_the_partilly_refunded_order_could_be_sync_strip_card_from_admin(ctx):
    """Apifox case #5735876: Linda_T1291_Verify_the_partilly_refunded_order_could_be_sync_Strip_Card_From_Adm"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    _render = legacy_render(ctx)
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: 31b4cf7b-2ce1-442d-a64f-f9caf7896d13
    _resp1 = ctx.api.auth.guest_login(body='{\r\n    "consumerId": "{{__uuid_0}}"\r\n}')
    vars['access_token'] = (_resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 2: 0503484f-b508-44cf-8ee3-3a83477fba43
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
    _resp5 = ctx.api.orders.merchant_detail_by_order_number(token='linda01_token')
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson equal 734.51
    expect(_resp5).json('$.data.summary.productSubtotal').equals('734.51')
    # assertion 5.total: responseJson equal 369.64
    expect(_resp5).json('$.data.summary.total').equals('369.64')
    # assertion 5.assertion: responseJson equal NOT_REFUNDED
    expect(_resp5).json('$.data.refundStatus').equals('NOT_REFUNDED')
    # extractor: lineItems_id = $.data.lineItems[0].id
    ctx.extract('lineItems_id', _resp5, '$.data.lineItems[0].id')
    # extractor: merchantOrderId = $.data.lineItems[0].merchantOrderId
    ctx.extract('merchantOrderId', _resp5, '$.data.lineItems[0].merchantOrderId')
    # step 6: adc5fa8a-c82d-4386-a483-e23fee773ead
    _resp6 = ctx.api.admin.orders_refunds(body='{\r\n  "lineItems": [\r\n    {\r\n      "merchantOrderId": "{{merchantOrderId}}",\r\n      "id": "{{lineItems_id}}",\r\n      "itemAmount": 12,\r\n      "taxAmount": 0,\r\n      "totalAmount": 12,\r\n      "quantity": 1,\r\n      "refundable": {\r\n        "merchantOrderId": "{{merchantOrderId}}",\r\n        "lineItemId": "{{lineItems_id}}",\r\n        "refundableItem": 12,\r\n        "refundableTax": 0,\r\n        "totalRefundable": 12,\r\n        "refundableQuantity": 1\r\n      },\r\n      "changedFields": []\r\n    }\r\n  ],\r\n  "shippingLines": [\r\n    {\r\n      "merchantOrderId": "{{merchantOrderId}}",\r\n      "shippingAmount": 0,\r\n      "taxAmount": 0,\r\n      "totalAmount": 0,\r\n      "refundable": {\r\n        "merchantOrderId": "{{merchantOrderId}}",\r\n        "refundableShipping": 15.99,\r\n        "refundableShippingTax": 0,\r\n        "totalRefundable": 15.99\r\n      }\r\n    }\r\n  ],\r\n  "refundTotals": {\r\n    "totalItemsRefund": 12,\r\n    "totalItemsQuantityRefund": 1,\r\n    "totalShippingRefund": 0,\r\n    "totalItemsTaxRefund": 0,\r\n    "totalShippingTaxRefund": 0,\r\n    "totalTaxRefund": 0,\r\n    "totalRefund": 12\r\n  },\r\n  "transactions": [\r\n    {\r\n      "merchantOrderId": "{{merchantOrderId}}",\r\n      "totalRefund": 12,\r\n      "totalRefundable": 27.99,\r\n      "changedFields": []\r\n    }\r\n  ]\r\n}', token='admin_token', path_vars={'admin_orderId': '{{order_id}}'})
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal {{order_id}}
    expect(_resp6).json('$.data.orderRefund.orderId').equals(str(_render('{{order_id}}', vars)))
    # assertion 6.assertion: responseJson equal 12
    expect(_resp6).json('$.data.orderRefund.totalLineItemRefunded').equals('12')
    # assertion 6.assertion: responseJson equal 0
    expect(_resp6).json('$.data.orderRefund.totalShippingRefunded').equals('0')
    # assertion 6.assertion: responseJson equal 12
    expect(_resp6).json('$.data.orderRefund.totalRefunded').equals('12')
    # step 7: After Parital Refunds, Get sale detail for order 
    _resp7 = ctx.api.orders.merchant_detail_by_order_number(token='linda01_token')
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal 12
    expect(_resp7).json('$.data.refundSummary.totalRefunded').equals('12')
    # assertion 7.assertion: responseJson equal 362.92
    expect(_resp7).json('$.data.summary.total').equals('362.92')
    # assertion 7.assertion: responseJson equal 12
    expect(_resp7).json('$.data.refundSummary.totalRefunded').equals('12')
    # assertion 7.assertion: responseJson equal 12
    expect(_resp7).json('$.data.refundSummary.totalLineItemRefunded').equals('12')
    # assertion 7.assertion: responseJson equal 0
    expect(_resp7).json('$.data.refundSummary.totalShippingRefunded').equals('0')
