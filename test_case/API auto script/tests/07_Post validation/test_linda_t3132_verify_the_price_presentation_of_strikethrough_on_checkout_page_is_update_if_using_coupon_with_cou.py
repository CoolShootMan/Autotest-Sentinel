"""Migrated from Apifox case #5853677. Source folder: Post validation."""
# Apifox Case ID: 5853677  (traceability only — not needed to run)
NAME = "Verify the price presentation of strikethrough on checkout page is update if using coupon with coupon code"
TAGS = ["p0", "post_validation", "suite:linda"]
PRIORITY = 0


CASE_ID = 5853677
ENV_NAME = "Release"

# --- step 1: guest login ---
# post[extractor]: {"variableName": "access_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data", "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: post detail ---
# post[extractor]: {"variableName": "promoterProductVariantId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[0].variants[0].id", "extractSettings": {"expression": "$.data.relatedProducts[0].variants[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "subscriptionPlanOptionid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId", "extractSettings": {"expression": "$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "postid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 0b0509d4-e797-4f2f-8144-98066a2cb5bf ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: buy now  ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "80", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: apply 10% coupon on the checkout page ---
# --- step 6: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_linda_t3132_verify_the_price_presentation_of_strikethrough_on_checkout_page_is_update_if_using_coupon_with_cou(ctx):
    """Apifox case #5853677: Linda_T3132_Verify_the_price_presentation_of_strikethrough_on_checkout_page_is_u"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: guest login
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "{{__uuid_0}}"\n}')
    # extractor: access_token = $.data
    ctx.extract('access_token', _resp1, '$.data')
    # step 2: post detail
    _resp2 = ctx.api.posts.consumer_detail(token='access_token', params={'urlAlias': 't3132', 'vanityUrl': 'linda'})
    # extractor: promoterProductVariantId = $.data.relatedProducts[0].variants[0].id
    ctx.extract('promoterProductVariantId', _resp2, '$.data.relatedProducts[0].variants[0].id')
    # extractor: subscriptionPlanOptionid = $.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId
    ctx.extract('subscriptionPlanOptionid', _resp2, '$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId')
    # extractor: postid = $.data.id
    ctx.extract('postid', _resp2, '$.data.id')
    # step 3: 0b0509d4-e797-4f2f-8144-98066a2cb5bf
    _resp3 = ctx.api.cart.delete(body='{}', app_headers=True, token='access_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # step 4: buy now 
    _resp4 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n        "quantity": 1,\n        "promoterProductVariantId": "{{promoterProductVariantId}}",\n        "price": "80" ,\n        "postId": "{{postid}}",\n        "selected": true\n    }\n    ],\n    "currentUpdateCartItems": [\n        {\n        "quantity": 1,\n        "id": "{{promoterProductVariantId}}",\n        "postId": "{{postid}}",\n        "price": "80" \n    }\n    ]\n}', app_headers=True, token='access_token')
    # assertion 4.assertion: responseJson equal 80
    expect(_resp4).json('$.data.totalToPay').equals('80')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp4, '$.data.orderId')
    # step 5: apply 10% coupon on the checkout page
    _resp5 = ctx.api.orders.points_and_promotions(body='{\n    "shippingAddress": {\n        "line1": "",\n        "city": "",\n        "zipcode": "",\n        "state": ""\n    },\n    "applicableCode": "API Auto Test with 10% discount",\n    "orderId": "{{order_id}}"\n}', token='access_token')
    # step 6: create Order
    _resp6 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 72,\n      "promoterVariantId": "{{promoterProductVariantId}}"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "linda.zhou.ext+10@qibua.com"\n  },\n  "addressRequest": {\n    "isDefault": true,\n    "firstName": "linda43",\n    "lastName": "zhou",\n    "line1": "1800 Zollinger Road",\n    "state": "OH",\n    "city": "Columbus",\n    "zipcode": "43221",\n    "line2": "test",\n    "phoneNumber": "+16502396646",\n     "ignoreVerifyPhoneNumber": "True"\n  }\n}', app_headers=True, token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 6.code: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson exists 
    expect(_resp6).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp6, '$.data.orderNumbers[0]')
