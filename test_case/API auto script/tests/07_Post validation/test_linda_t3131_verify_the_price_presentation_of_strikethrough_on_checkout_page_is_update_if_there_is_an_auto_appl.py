"""Migrated from Apifox case #5860786. Source folder: Post validation."""
# Apifox Case ID: 5860786  (traceability only — not needed to run)
NAME = "Verify the price presentation of strikethrough on checkout page is update if there is an auto-applied coupon"
TAGS = ["p0", "post_validation", "suite:linda"]
PRIORITY = 0


CASE_ID = 5860786
ENV_NAME = "Release"

# --- step 1: guest login ---
# post[extractor]: {"variableName": "access_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data", "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: post detail ---
# post[extractor]: {"variableName": "promoterProductVariantId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[0].variants[0].id", "extractSettings": {"expression": "$.data.relatedProducts[0].variants[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "subscriptionPlanOptionid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId", "extractSettings": {"expression": "$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "postid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 018aeb5f-dd54-47a7-925a-fb45eb46c768 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4:  auto coupon discount by merchant id - buy now  ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "64", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: Login-merchant ---
# post[extractor]: {"variableName": "merchant_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: Check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "17c3a9b5-3382-4d02-a0c4-071f50cfa525");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "64", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: e6ce196f-d132-4904-b8c8-684476534673 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9:  auto coupon discount by products buy now ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "64", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: Check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "17c3a9b5-3382-4d02-a0c4-071f50cfa525");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "64", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 12: f7ba3778-8cdf-46ae-b63d-d96fdafff9ec ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 13:  auto coupon Minimum quantity products buy now --2 products  ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "128", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 14: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 15: Check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "17c3a9b5-3382-4d02-a0c4-071f50cfa525");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "128", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 16: 8f98cc17-9730-4b56-a926-19d870b543aa ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 17:  auto coupon Minimum quantity products buy now --3 products  ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "192", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 18: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 19: Check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "17c3a9b5-3382-4d02-a0c4-071f50cfa525");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "192", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 20: f3797de9-6dc0-4a41-bde0-077bc656a06b ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 21: auto coupon Minimum purchase amount - 150 -10% ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "128", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 22: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 23: Check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "17c3a9b5-3382-4d02-a0c4-071f50cfa525");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "128", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 24: b221e3c2-95a7-497a-bf67-b7f26ad5fdf1 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 25: auto coupon Minimum purchase amount - 200 -20% ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "192", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 26: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 27: Check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.environment.set("merchantId", "17c3a9b5-3382-4d02-a0c4-071f50cfa525");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "192", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_linda_t3131_verify_the_price_presentation_of_strikethrough_on_checkout_page_is_update_if_there_is_an_auto_appl(ctx):
    """Apifox case #5860786: Linda_T3131_Verify_the_price_presentation_of_strikethrough_on_checkout_page_is_u"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: guest login
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "{{__uuid_0}}"\n}')
    # extractor: access_token = $.data
    ctx.extract('access_token', _resp1, '$.data')
    # step 2: post detail
    _resp2 = ctx.api.posts.consumer_detail(token='access_token', params={'urlAlias': 't3131', 'vanityUrl': 'linda'})
    # extractor: promoterProductVariantId = $.data.relatedProducts[0].variants[0].id
    ctx.extract('promoterProductVariantId', _resp2, '$.data.relatedProducts[0].variants[0].id')
    # extractor: subscriptionPlanOptionid = $.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId
    ctx.extract('subscriptionPlanOptionid', _resp2, '$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId')
    # extractor: postid = $.data.id
    ctx.extract('postid', _resp2, '$.data.id')
    # step 3: 018aeb5f-dd54-47a7-925a-fb45eb46c768
    _resp3 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # step 4:  auto coupon discount by merchant id - buy now 
    _resp4 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n        "quantity": 1,\n        "promoterProductVariantId": "73fe38bf-4a74-4c87-a296-e9f664ea9b43",\n        "price": "80" ,\n        "postId": "{{postid}}",\n        "selected": true\n    }\n    ],\n    "currentUpdateCartItems": [\n        {\n        "quantity": 1,\n        "id": "73fe38bf-4a74-4c87-a296-e9f664ea9b43",\n        "postId": "{{postid}}",\n        "price": "80" \n    }\n    ]\n}', app_headers=True, token='access_token')
    # assertion 4.assertion: responseJson equal 64
    expect(_resp4).json('$.data.totalToPay').equals('64')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp4, '$.data.orderId')
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 72,\n      "promoterVariantId": "{{promoterProductVariantId}}"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "linda.zhou.ext+10@1m.app"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+16502396646",\n     "ignoreVerifyPhoneNumber": "True"\n  }\n}', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 5.code: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson exists 
    expect(_resp5).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp5, '$.data.orderNumbers[0]')
    # step 6: Login-merchant
    _resp6 = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+00@1m.app"\n}', app_headers=True)
    # extractor: merchant_token = $.data.token
    ctx.extract('merchant_token', _resp6, '$.data.token')
    # step 7: Check merchant order detail
    vars['merchantId'] = '17c3a9b5-3382-4d02-a0c4-071f50cfa525'
    _resp7 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='merchant_token')
    # assertion 7.assertion: responseJson equal 64
    expect(_resp7).json('$.data.totalCommissionSubtotal').equals('64')
    # step 8: e6ce196f-d132-4904-b8c8-684476534673
    _resp8 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 8.assertion: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # assertion 8.assertion: responseJson equal success
    expect(_resp8).json('$.message').equals('success')
    # step 9:  auto coupon discount by products buy now
    _resp9 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n        "quantity": 1,\n        "promoterProductVariantId": "1e3fb5fd-4dd9-467f-9c8e-9c4ef1bebd58",\n        "price": "80" ,\n        "postId": "{{postid}}",\n        "selected": true\n    }\n    ],\n    "currentUpdateCartItems": [\n        {\n        "quantity": 1,\n        "id": "1e3fb5fd-4dd9-467f-9c8e-9c4ef1bebd58",\n        "postId": "{{postid}}",\n        "price": "80" \n    }\n    ]\n}', app_headers=True, token='access_token')
    # assertion 9.assertion: responseJson equal 64
    expect(_resp9).json('$.data.totalToPay').equals('64')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp9, '$.data.orderId')
    # step 10: create Order
    _resp10 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 72,\n      "promoterVariantId": "1e3fb5fd-4dd9-467f-9c8e-9c4ef1bebd58"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "fos.zyx@gmail.com"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+16502396646",\n     "ignoreVerifyPhoneNumber": "True"\n  }\n}', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 10.code: responseJson equal 200
    expect(_resp10).json('$.code').equals('200')
    # assertion 10.assertion: responseJson exists 
    expect(_resp10).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp10, '$.data.orderNumbers[0]')
    # step 11: Check merchant order detail
    vars['merchantId'] = '17c3a9b5-3382-4d02-a0c4-071f50cfa525'
    _resp11 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='merchant_token')
    # assertion 11.assertion: responseJson equal 64
    expect(_resp11).json('$.data.totalCommissionSubtotal').equals('64')
    # step 12: f7ba3778-8cdf-46ae-b63d-d96fdafff9ec
    _resp12 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 12.assertion: responseJson equal 200
    expect(_resp12).json('$.code').equals('200')
    # assertion 12.assertion: responseJson equal success
    expect(_resp12).json('$.message').equals('success')
    # step 13:  auto coupon Minimum quantity products buy now --2 products 
    _resp13 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n        "quantity": 2,\n        "promoterProductVariantId": "4e4d198f-b54a-40cb-a4d3-d0b1ede77f47",\n        "price": "80" ,\n        "postId": "{{postid}}",\n        "selected": true\n    }\n    ],\n    "currentUpdateCartItems": [\n        {\n        "quantity": 2,\n        "id": "4e4d198f-b54a-40cb-a4d3-d0b1ede77f47",\n        "postId": "{{postid}}",\n        "price": "80" \n    }\n    ]\n}', app_headers=True, token='access_token')
    # assertion 13.assertion: responseJson equal 128
    expect(_resp13).json('$.data.totalToPay').equals('128')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp13, '$.data.orderId')
    # step 14: create Order
    _resp14 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 72,\n      "promoterVariantId": "4e4d198f-b54a-40cb-a4d3-d0b1ede77f47"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "fos.zyx@gmail.com"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+16502396646",\n     "ignoreVerifyPhoneNumber": "True"\n  }\n}', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 14.code: responseJson equal 200
    expect(_resp14).json('$.code').equals('200')
    # assertion 14.assertion: responseJson exists 
    expect(_resp14).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp14, '$.data.orderNumbers[0]')
    # step 15: Check merchant order detail
    vars['merchantId'] = '17c3a9b5-3382-4d02-a0c4-071f50cfa525'
    _resp15 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='merchant_token')
    # assertion 15.assertion: responseJson equal 128
    expect(_resp15).json('$.data.totalCommissionSubtotal').equals('128')
    # step 16: 8f98cc17-9730-4b56-a926-19d870b543aa
    _resp16 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 16.assertion: responseJson equal 200
    expect(_resp16).json('$.code').equals('200')
    # assertion 16.assertion: responseJson equal success
    expect(_resp16).json('$.message').equals('success')
    # step 17:  auto coupon Minimum quantity products buy now --3 products 
    _resp17 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n        "quantity": 3,\n        "promoterProductVariantId": "4e4d198f-b54a-40cb-a4d3-d0b1ede77f47",\n        "price": "80" ,\n        "postId": "{{postid}}",\n        "selected": true\n    }\n    ],\n    "currentUpdateCartItems": [\n        {\n        "quantity": 3,\n        "id": "4e4d198f-b54a-40cb-a4d3-d0b1ede77f47",\n        "postId": "{{postid}}",\n        "price": "80" \n    }\n    ]\n}', app_headers=True, token='access_token')
    # assertion 17.assertion: responseJson equal 192
    expect(_resp17).json('$.data.totalToPay').equals('192')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp17, '$.data.orderId')
    # step 18: create Order
    _resp18 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 72,\n      "promoterVariantId": "4e4d198f-b54a-40cb-a4d3-d0b1ede77f47"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "fos.zyx@gmail.com"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+16502396646",\n     "ignoreVerifyPhoneNumber": "True"\n  }\n}', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 18.code: responseJson equal 200
    expect(_resp18).json('$.code').equals('200')
    # assertion 18.assertion: responseJson exists 
    expect(_resp18).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp18, '$.data.orderNumbers[0]')
    # step 19: Check merchant order detail
    vars['merchantId'] = '17c3a9b5-3382-4d02-a0c4-071f50cfa525'
    _resp19 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='merchant_token')
    # assertion 19.assertion: responseJson equal 192
    expect(_resp19).json('$.data.totalCommissionSubtotal').equals('192')
    # step 20: f3797de9-6dc0-4a41-bde0-077bc656a06b
    _resp20 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 20.assertion: responseJson equal 200
    expect(_resp20).json('$.code').equals('200')
    # assertion 20.assertion: responseJson equal success
    expect(_resp20).json('$.message').equals('success')
    # step 21: auto coupon Minimum purchase amount - 150 -10%
    _resp21 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n        "quantity": 2,\n        "promoterProductVariantId": "faf4c6fc-b8b9-4f1d-9ceb-28a4a9653b57",\n        "price": "80" ,\n        "postId": "{{postid}}",\n        "selected": true\n    }\n    ],\n    "currentUpdateCartItems": [\n        {\n        "quantity": 2,\n        "id": "faf4c6fc-b8b9-4f1d-9ceb-28a4a9653b57",\n        "postId": "{{postid}}",\n        "price": "80" \n    }\n    ]\n}', app_headers=True, token='access_token')
    # assertion 21.assertion: responseJson equal 128
    expect(_resp21).json('$.data.totalToPay').equals('128')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp21, '$.data.orderId')
    # step 22: create Order
    _resp22 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 72,\n      "promoterVariantId": "faf4c6fc-b8b9-4f1d-9ceb-28a4a9653b57"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "fos.zyx@gmail.com"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+16502396646",\n     "ignoreVerifyPhoneNumber": "True"\n  }\n}', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 22.code: responseJson equal 200
    expect(_resp22).json('$.code').equals('200')
    # assertion 22.assertion: responseJson exists 
    expect(_resp22).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp22, '$.data.orderNumbers[0]')
    # step 23: Check merchant order detail
    vars['merchantId'] = '17c3a9b5-3382-4d02-a0c4-071f50cfa525'
    _resp23 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='merchant_token')
    # assertion 23.assertion: responseJson equal 128
    expect(_resp23).json('$.data.totalCommissionSubtotal').equals('128')
    # step 24: b221e3c2-95a7-497a-bf67-b7f26ad5fdf1
    _resp24 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 24.assertion: responseJson equal 200
    expect(_resp24).json('$.code').equals('200')
    # assertion 24.assertion: responseJson equal success
    expect(_resp24).json('$.message').equals('success')
    # step 25: auto coupon Minimum purchase amount - 200 -20%
    _resp25 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n        "quantity": 3,\n        "promoterProductVariantId": "faf4c6fc-b8b9-4f1d-9ceb-28a4a9653b57",\n        "price": "80" ,\n        "postId": "{{postid}}",\n        "selected": true\n    }\n    ],\n    "currentUpdateCartItems": [\n        {\n        "quantity": 3,\n        "id": "faf4c6fc-b8b9-4f1d-9ceb-28a4a9653b57",\n        "postId": "{{postid}}",\n        "price": "80" \n    }\n    ]\n}', app_headers=True, token='access_token')
    # assertion 25.assertion: responseJson equal 192
    expect(_resp25).json('$.data.totalToPay').equals('192')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp25, '$.data.orderId')
    # step 26: create Order
    _resp26 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 72,\n      "promoterVariantId": "faf4c6fc-b8b9-4f1d-9ceb-28a4a9653b57"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "fos.zyx@gmail.com"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+16502396646",\n     "ignoreVerifyPhoneNumber": "True"\n  }\n}', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 26.code: responseJson equal 200
    expect(_resp26).json('$.code').equals('200')
    # assertion 26.assertion: responseJson exists 
    expect(_resp26).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp26, '$.data.orderNumbers[0]')
    # step 27: Check merchant order detail
    vars['merchantId'] = '17c3a9b5-3382-4d02-a0c4-071f50cfa525'
    _resp27 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='merchant_token')
    # assertion 27.assertion: responseJson equal 192
    expect(_resp27).json('$.data.totalCommissionSubtotal').equals('192')
