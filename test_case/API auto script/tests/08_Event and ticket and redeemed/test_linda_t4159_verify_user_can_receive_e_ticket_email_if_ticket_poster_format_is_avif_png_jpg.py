"""Auto-generated from Apifox case #7510819. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7510819
# Folder: 
# Case: (Linda)T4159 Verify user can receive e-ticket email if ticket poster format is avif/png/jpg
# Priority: P0
# Created: 2025-11-12T02:26:10.000Z
# Updated: 2026-09-07T07:32:43.000Z


CASE_ID = 7510819
ENV_NAME = "Release"

# --- step 1: guest login ---
# post[extractor]: {"variableName": "access_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data", "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: post detail ---
# post[extractor]: {"variableName": "promoterProductVariantId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[3].variants[0].id", "extractSettings": {"expression": "$.data.relatedProducts[3].variants[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "postid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "price", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[3].priceDisplay", "extractSettings": {"expression": "$.data.relatedProducts[3].priceDisplay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: buy now  ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "3147.78", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





from core.assertions import expect

def test__7510819__Linda_T4159_Verify_user_can_receive_e_ticket_email_if_ticket_poster_format_is_avif_png_jpg(ctx):
    """Apifox case #7510819: Linda_T4159_Verify_user_can_receive_e_ticket_email_if_ticket_poster_format_is_av"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: guest login
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "{{__uuid_0}}"\n}', app_headers=False)
    # extractor: access_token = $.data
    ctx.extract('access_token', _resp1, '$.data')
    # step 2: post detail
    _resp2 = ctx.api.posts.consumer_detail(params={'urlAlias': 't4159', 'vanityUrl': 'suyu'}, app_headers=False, token='access_token')
    # extractor: promoterProductVariantId = $.data.relatedProducts[3].variants[0].id
    ctx.extract('promoterProductVariantId', _resp2, '$.data.relatedProducts[3].variants[0].id')
    # extractor: postid = $.data.id
    ctx.extract('postid', _resp2, '$.data.id')
    # extractor: price = $.data.relatedProducts[3].priceDisplay
    ctx.extract('price', _resp2, '$.data.relatedProducts[3].priceDisplay')
    # step 3: buy now 
    _resp3 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n        "quantity": 6,\n        "promoterProductVariantId": "{{promoterProductVariantId}}",\n        "price": "{{price}}" ,\n        "postId": "{{postid}}",\n        "selected": true\n    }\n    ],\n    "currentUpdateCartItems": [\n        {\n        "quantity": 0,\n        "id": "{{promoterProductVariantId}}",\n        "postId": "{{postid}}",\n        "price": "{{price}}" \n    }\n    ]\n}', token='access_token')
    # assertion 3.assertion: responseJson equal 3147.78
    expect(_resp3).json('$.data.totalToPay').equals('3147.78')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp3, '$.data.orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n  "inviterCampaign": {},\n  "id": "{{order_id}}",\n  "paymentInfo": {\n    "paymentMethodId": "{{pay_method_id}}"\n  },\n  "contact": {\n    "phoneNumber": "+13022814650",\n    "email": "linda.zhou.ext+12@1m.app"\n  },\n  "fbAdParams": {\n    "eventID": "30561013-f59f-4f13-b124-1f5ed78efa43",\n    "pixelId": [\n      "268933192948110"\n    ],\n    "fbBrowserId": "fb.1.1764923328139.148987369846580641",\n    "externalId": "3778787a-2c96-4c9e-bea8-580aac281757",\n    "eventSourceUrl": "https://release.pear.us/checkout"\n  }\n}', token='access_token', params={'order_id': '{{order_id}}'})
    # assertion 4.code: responseJson equal 200
    print("STEP4DBG", _resp4.status_code, _resp4.text[:400], "oid=", vars.get('order_id'))
    expect(_resp4).json('$.code').equals('200')
    # assertion 4.assertion: responseJson exists 
    expect(_resp4).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp4, '$.data.orderNumbers[0]')
