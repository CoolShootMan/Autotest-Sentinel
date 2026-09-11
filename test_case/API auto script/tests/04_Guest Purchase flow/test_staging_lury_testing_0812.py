"""Migrated from Apifox case #8619916. Source folder: Guest Purchase flow."""
# Apifox Case ID: 8619916  (traceability only — not needed to run)
NAME = "Staging Lury testing 0812"
TAGS = ["p0", "guest_purchase_flow"]
PRIORITY = 0


CASE_ID = 8619916
ENV_NAME = "Release"

# --- step 1: guest get token ---
# pre: 
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 2: buy now ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post:     pm.expect(res["data"]["totalToPay"]).to.eql(0);
# post: });
# --- step 3: create Order ---
# post[assertion]: {"name": "verify status is 200", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}, "value": 200}}




import json

from core.assertions import expect

def test_staging_lury_testing_0812(ctx):
    """Apifox case #8619916: Staging_Lury_testing_0812"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda"\n}')
    vars['access_token'] = (_resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 2: buy now
    _resp2 = ctx.api.orders.buy_now(body='{\n  "postIdForFilter": "09adb4ea-aa28-4a23-a500-2cfcd8886536",\n  "updateCartItems": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "3c169bf2-ac51-4fdd-9bb7-6ee2d3a1af56",\n      "price": 0,\n      "postId": "09adb4ea-aa28-4a23-a500-2cfcd8886536",\n      "selected": true,\n      "customFields": []\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "b3016df7-3f0c-420d-9b96-e6b06ece9653",\n    "pixelId": [\n      "268933192948110"\n    ],\n    "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n    "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n    "eventSourceUrl": "https://release.pear.us/auto-merchant/post/lury-automation-testing-0323"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 1,\n      "id": "3c169bf2-ac51-4fdd-9bb7-6ee2d3a1af56",\n      "postId": "09adb4ea-aa28-4a23-a500-2cfcd8886536",\n      "price": 0,\n      "customFields": []\n    }\n  ]\n}', app_headers=True, token='access_token')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp2, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp2, 'orderId')
    # step 3: create Order
    _resp3 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "zhiyong.song.ext+customer@1m.app",\n        "firstName": "DC",\n        "lastName": "state",\n        "phoneNumber": "+16502469802"\n    },\n    "fbAdParams": {\n        "eventID": "0a0e358d-41d8-4e10-985f-9a060bd02b1d",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1770024421386.76306656737520437",\n        "externalId": "bb3a0ce0-2fd8-44c2-9017-745a62aaf7d8",\n        "eventSourceUrl": "https://release.pear.us/auto-merchant/post/lury-campaign-test-0126"\n    }\n}', app_headers=True, skip_notifications=False, token='access_token')
    # assertion 3.verify status is 200: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
