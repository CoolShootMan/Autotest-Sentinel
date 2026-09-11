"""Migrated from Apifox case #8662408. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8662408  (traceability only — not needed to run)
NAME = "Verify fee is not displayed if ticekt set \"Do not display fees\""
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:lury"]
PRIORITY = 0


CASE_ID = 8662408
ENV_NAME = "Release"

# --- step 1: delete cart ---
# --- step 2: buy now ticket with custom fee ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post:     var lineItems = res['data']['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["promoterVariantId"]).to.eql("d5e8d02e-6038-4603-90a0-769012f620d5");
# post:         pm.expect(line_item["hideFees"]).to.eql(true);
# post:         pm.expect(line_item["ticketFees"]).to.eql(0);
# post:         pm.expect(line_item["subtotalTicketFees"]).to.eql(0);
# post:     }
# post: });
# --- step 3: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(14.28);
# post:     var lineItems = res['data']["confirmation"]['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["merchantProductId"]).to.eql("b0ce090f-1d6f-4962-bdce-3f2f1cbfa1d5");
# post:         pm.expect(line_item["hideFees"]).to.eql(true);
# post:         pm.expect(line_item["ticketFees"]).to.eql(0);
# post:     }
# post: });
# --- step 4: get consumer order detail ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalLineItemPrice']).to.eql(14.28);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         pm.expect(line_item["merchantProductId"]).to.eql("b0ce090f-1d6f-4962-bdce-3f2f1cbfa1d5");
# post:         pm.expect(line_item["hideFees"]).to.eql(true);
# post:         pm.expect(line_item["ticketFees"]).to.eql(0);
# post:     }
# post: });




from core.assertions import expect

def test_lury_t5408_verify_fee_is_not_displayed_if_ticekt_set_do_not_display_fees(ctx):
    """Apifox case #8662408: Lury_T5408_Verify_fee_is_not_displayed_if_ticekt_set_Do_not_display_fees"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: delete cart
    _resp1 = ctx.api.cart.delete()
    # step 2: buy now ticket with custom fee
    _resp2 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "885eaa07-e64b-4eff-90aa-d5b1582034e9",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "d5e8d02e-6038-4603-90a0-769012f620d5",\n            "price": 14.28,\n            "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "5c622faf-26eb-4833-905b-ece92ed1f45e",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-test-check-in-expiration"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "d5e8d02e-6038-4603-90a0-769012f620d5",\n            "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",\n            "price": 14.28,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp2, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp2, 'orderId')
    # step 3: create Order
    _resp3 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 4: get consumer order detail
    _resp4 = ctx.api.orders.consumer_detail_by_order_number()
