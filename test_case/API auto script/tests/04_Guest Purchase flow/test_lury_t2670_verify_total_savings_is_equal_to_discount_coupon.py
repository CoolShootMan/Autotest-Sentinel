"""Migrated from Apifox case #5926824. Source folder: Guest Purchase flow."""
# Apifox Case ID: 5926824  (traceability only — not needed to run)
NAME = "Verify total savings is equal to discount + coupon"
TAGS = ["p0", "guest_purchase_flow", "suite:lury"]
PRIORITY = 0


CASE_ID = 5926824
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
# post:     pm.expect(res["data"]["totalToPay"]).to.eql(6.99);
# post: });
# --- step 3: get Checkout ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var items_list = res['data']['lineItems']
# post:     for (var item of items_list){
# post:         if (item["productTitle"] === "general + In-person"){
# post:             var lineItemId = item["lineItemId"]
# post:         }
# post:     }
# post:     pm.environment.set("lineItemId",lineItemId);
# post:     console.log(lineItemId)
# post: 
# post: });
# post: 
# --- step 4: apply promotion ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res["data"]["productSubtotal"]).to.eql(2);
# post:     pm.expect(res["data"]["totalLineItemCouponDiscount"]).to.eql(0.2);
# post:     pm.expect(res["data"]["totalLineItemSampleDiscount"]).to.eql(0);
# post:     pm.expect(res["data"]["totalLineItemSubtotal"]).to.eql(1.8);
# post:     pm.expect(res["data"]["totalShippingPrice"]).to.eql(4.99);
# post:     pm.expect(res["data"]["totalShippingDiscount"]).to.eql(0);
# post:     pm.expect(res["data"]["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(res["data"]["totalToPay"]).to.eql(6.79);
# post:     pm.expect(res["data"]["totalDiscount"]).to.eql(0.2);
# post: 
# post: });




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_lury_t2670_verify_total_savings_is_equal_to_discount_coupon(ctx):
    """Apifox case #5926824: Lury_T2670_Verify_total_savings_is_equal_to_discount_coupon"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda"\n}', app_headers=False)
    vars['access_token'] = (_resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 2: buy now
    _resp2 = ctx.api.orders.buy_now(body='{\n  "postIdForFilter": "934e7fb1-94d7-4507-84fd-0bddd03eba62",\n  "updateCartItems": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "bb380ac8-eaea-4278-963e-a1e70e28b862",\n      "price": 2,\n      "postId": "934e7fb1-94d7-4507-84fd-0bddd03eba62",\n      "selected": true,\n      "customFields": []\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "fa2e3f3c-8fd9-49ea-bca6-22c1675990d6",\n    "pixelId": [\n      "test"\n    ],\n    "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n    "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n    "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 1,\n      "id": "bb380ac8-eaea-4278-963e-a1e70e28b862",\n      "postId": "934e7fb1-94d7-4507-84fd-0bddd03eba62",\n      "price": 2,\n      "customFields": []\n    }\n  ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp2, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp2, 'orderId')
    # step 3: get Checkout
    _resp3 = ctx.api.orders.checkout_2()
    _j = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "lineItems"]) or []
    for _item in _arr:
        if _item.get('productTitle') == "general + In-person":
            vars['lineItemId'] = _item.get('lineItemId')
    # step 4: apply promotion
    _resp4 = ctx.api.orders.update_promotions(body='{\n    "postIdForFilter": "934e7fb1-94d7-4507-84fd-0bddd03eba62",\n    "orderId": "{{orderId}}",\n    "shippingAddress": {\n        "line1": "11111 Research Boulevard",\n        "state": "TX",\n        "city": "Austin",\n        "zipcode": "78759"\n    },\n    "applicableCode":"autocoupon10"\n}')
