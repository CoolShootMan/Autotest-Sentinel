"""Migrated from Apifox case #8662407. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8662407  (traceability only — not needed to run)
NAME = "Verify ticket can be purchase before stop selling and ticket is unavailable after stop selling"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:lury"]
PRIORITY = 0


CASE_ID = 8662407
ENV_NAME = "Release"

# --- step 1: delete cart ---
# --- step 2: buy now after stop selling ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     pm.response.to.have.status(400);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['message']).to.eql("The variant(Default Title) of product(Stop selling after) is not available.");
# post: });
# --- step 3: buy now before stop selling ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post:     var lineItems = res['data']['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["promoterVariantId"]).to.eql("9cc2d6b5-fc07-48f0-b3b3-c40e3367f630");
# post:         pm.expect(line_item["variant"]["isAvailable"]).to.eql(true);
# post:     }
# post: });
# --- step 4: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(3.53);
# post:     var lineItems = res['data']["confirmation"]['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["merchantProductId"]).to.eql("4b7631fe-6a2a-4f39-b82d-eea9d207e994");
# post:     }
# post: });
# --- step 5: get consumer order detail ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalLineItemPrice']).to.eql(3.53);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         pm.expect(line_item["merchantProductId"]).to.eql("4b7631fe-6a2a-4f39-b82d-eea9d207e994");
# post:     }
# post: });




from core.assertions import expect

def test_lury_t4861_verify_ticket_can_be_purchase_before_stop_selling_and_ticket_is_unavailable_after_stop_selling(ctx):
    """Apifox case #8662407: Lury_T4861_Verify_ticket_can_be_purchase_before_stop_selling_and_ticket_is_unava"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: delete cart
    _resp1 = ctx.api.cart.delete()
    # step 2: buy now after stop selling
    _resp2 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "885eaa07-e64b-4eff-90aa-d5b1582034e9",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "9780ebc5-b542-4192-89ed-04add93800a5",\n            "price": 4.7,\n            "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "5c622faf-26eb-4833-905b-ece92ed1f45e",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-test-check-in-expiration"\n    }\n}')
    # step 3: buy now before stop selling
    _resp3 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "885eaa07-e64b-4eff-90aa-d5b1582034e9",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "9cc2d6b5-fc07-48f0-b3b3-c40e3367f630",\n            "price": 3.53,\n            "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "5c622faf-26eb-4833-905b-ece92ed1f45e",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-test-check-in-expiration"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "9cc2d6b5-fc07-48f0-b3b3-c40e3367f630",\n            "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",\n            "price": 3.53,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 5: get consumer order detail
    _resp5 = ctx.api.orders.consumer_detail_by_order_number()
