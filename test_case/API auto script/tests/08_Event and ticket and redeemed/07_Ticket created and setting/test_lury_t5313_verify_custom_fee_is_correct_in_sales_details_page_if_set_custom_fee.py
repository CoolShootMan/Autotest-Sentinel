"""Migrated from Apifox case #8662436. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8662436  (traceability only — not needed to run)
NAME = "Verify custom fee is correct in sales details page if set custom fee"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:lury"]
PRIORITY = 0


CASE_ID = 8662436
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
# --- step 5: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 6: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(14.28);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(14.28);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(1.52);
# post: 
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee11_1"]["net"]).to.eql(0.29);
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee11_1"]["title"]).to.eql("fee11");
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee11_1"]["amount"]).to.eql(0.29);
# post: 
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee22_2"]["net"]).to.eql(1);
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee22_2"]["title"]).to.eql("fee22");
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee22_2"]["amount"]).to.eql(1);
# post: 
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee33_3"]["net"]).to.eql(0.57);
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee33_3"]["title"]).to.eql("fee33");
# post:     pm.expect(data["transactionItemCustomFeeBreakdown"]["custom_fee33_3"]["amount"]).to.eql(0.57);
# post: 
# post: });




from core.assertions import expect

def test_lury_t5313_verify_custom_fee_is_correct_in_sales_details_page_if_set_custom_fee(ctx):
    """Apifox case #8662436: Lury_T5313_Verify_custom_fee_is_correct_in_sales_details_page_if_set_custom_fee"""
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
    # step 5: Login-M1
    _resp5 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp5, '$.data.token')
    # step 6: get M1 order detail v2
    _resp6 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
