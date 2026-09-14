"""Auto-generated from Apifox case #7855343. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7855343
# Folder: 
# Case: (Lury) T4782&T2795 guest place order with 0 yuan and link order to existing account
# Priority: P0
# Created: 2026-01-26T03:35:24.000Z
# Updated: 2026-08-03T07:41:43.000Z


CASE_ID = 7855343
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
# post[assertion]: {"name": "Verify the order is linked to exsiting verified account", "subject": "responseJson", "comparison": "equal", "value": "986eb96d-be5a-4a52-8379-eeddddc6df56", "path": "$.data.newConsumerId", "multipleValue": [], "extractSettings": {"expression": "$.data.newConsumerId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





import json

from core.assertions import expect

def test__7855343__Lury_T4782_T2795_guest_place_order_with_0_yuan_and_link_order_to_existing_account(ctx):
    """Apifox case #7855343: Lury_T4782_T2795_guest_place_order_with_0_yuan_and_link_order_to_existing_accoun"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    }, app_headers=False)
    # customScript: extract access_token from step1 response data
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    vars['access_token'] = (_j1 or {}).get('data', '')
    # step 2: buy now
    _resp2 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "44ca4de2-7cd8-46dd-b131-ede0aeda1b0c",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "e2b3974a-871a-47df-89b6-329107cbca47",
                "price": 0,
                "postId": "44ca4de2-7cd8-46dd-b131-ede0aeda1b0c",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "e3afcbf0-d90a-4d74-8a23-61a3d3859922",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1768467567031.92506180232323161",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/auto-merchant/post/lury-automation-testing-0323",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "e2b3974a-871a-47df-89b6-329107cbca47",
                "postId": "44ca4de2-7cd8-46dd-b131-ede0aeda1b0c",
                "price": 0,
                "customFields": [],
            },
        ],
    }, token='access_token')
    # customScript: extract orderNumber/orderId from step2 response data
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    _d2 = _j2.get('data') or {}
    vars['orderNumber'] = _d2.get('orderNumber', '')
    vars['orderId'] = _d2.get('orderId', '')
    # step 3: create Order
    _resp3 = ctx.api.orders.create(body={
        "id": "{{orderId}}",
        "contact": {
            "email": "dian.yuhong.ext+19@1m.app",
            "firstName": "DC",
            "lastName": "state",
            "phoneNumber": "+16502469802",
        },
        "fbAdParams": {
            "eventID": "0a0e358d-41d8-4e10-985f-9a060bd02b1d",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1770024421386.76306656737520437",
            "externalId": "bb3a0ce0-2fd8-44c2-9017-745a62aaf7d8",
            "eventSourceUrl": "https://release.pear.us/auto-merchant/post/lury-campaign-test-0126",
        },
    }, token='access_token')
    # assertion 3.Verify the order is linked to exsiting verified account: responseJson equal 986eb96d-be5a-4a52-8379-eeddddc6df56
    expect(_resp3).json('$.data.newConsumerId').equals('986eb96d-be5a-4a52-8379-eeddddc6df56')
