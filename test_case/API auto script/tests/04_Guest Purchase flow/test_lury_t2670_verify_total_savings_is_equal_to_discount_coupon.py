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

from typing import Any, TYPE_CHECKING

from core.assertions import expect

from core.compat import get_path as _get_path

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_t2670_verify_total_savings_is_equal_to_discount_coupon(ctx: "Context"):
    """Apifox case #5926824: Lury_T2670_Verify_total_savings_is_equal_to_discount_coupon"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    }, app_headers=False)
    vars['access_token'] = (_resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 2: buy now
    _resp2 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "934e7fb1-94d7-4507-84fd-0bddd03eba62",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "bb380ac8-eaea-4278-963e-a1e70e28b862",
                "price": 2,
                "postId": "934e7fb1-94d7-4507-84fd-0bddd03eba62",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "fa2e3f3c-8fd9-49ea-bca6-22c1675990d6",
            "pixelId": [
                "test",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "bb380ac8-eaea-4278-963e-a1e70e28b862",
                "postId": "934e7fb1-94d7-4507-84fd-0bddd03eba62",
                "price": 2,
                "customFields": [],
            },
        ],
    })
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp2, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp2, 'orderId')
    # step 3: get Checkout
    _resp3 = ctx.api.orders.checkout_2()
    _j: dict[str, Any] = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "lineItems"]) or []
    for _item in _arr:
        if _item.get('productTitle') == "general + In-person":
            vars['lineItemId'] = _item.get('lineItemId')
    # step 4: apply promotion
    _resp4 = ctx.api.orders.update_promotions(body={
        "postIdForFilter": "934e7fb1-94d7-4507-84fd-0bddd03eba62",
        "orderId": "{{orderId}}",
        "shippingAddress": {
            "line1": "11111 Research Boulevard",
            "state": "TX",
            "city": "Austin",
            "zipcode": "78759",
        },
        "applicableCode": "autocoupon10",
    })
