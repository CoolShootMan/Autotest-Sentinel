"""Migrated from Apifox case #8660973. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8660973  (traceability only — not needed to run)
NAME = "&T5026 Verify check-in expiration time on checkout page and order confirmation details"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:lury"]
PRIORITY = 0


CASE_ID = 8660973
ENV_NAME = "Release"

# --- step 1: Consumer-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 1;
# pre:     item_percentage_fee = 0.1;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: 
# pre: function get_tax(unit_price,quantity){
# pre:     tax_rate = 0.06;
# pre:     return unit_price * quantity * tax_rate
# pre: }
# pre: 
# pre: function set_rebate(unit_price,quantity){
# pre:     unit_fixed_rebate = 0.6;
# pre:     item_percentage_rebate = 0.065;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_rebate + unit_price * item_percentage_rebate) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }    
# pre: }
# pre: var unit_price = 13.1;
# pre: var quantity = 2;
# pre: var commission_rate = 0.25;
# pre: var merchant_earnings =  Math.round(((unit_price * quantity * commission_rate) + Number.EPSILON) *100 ) / 100;
# pre: var m1_earnings = Number((unit_price * quantity - merchant_earnings ).toFixed(2));
# pre: 
# pre: var m1_rebate = Math.floor(set_rebate(unit_price,quantity) *100 ) / 100;
# pre: var tax_total = Math.floor(get_tax(unit_price,quantity)*100 ) / 100;
# pre: 
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(unit_price,quantity)*100)/100;
# pre: var merchant_transaction_fee = Math.round(((commission_rate * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_tax = Math.round(((commission_rate * tax_total) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - merchant_transaction_fee ).toFixed(2));
# pre: var m1_tax = Number((tax_total - merchant_tax ).toFixed(2));
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("m1_rebate", m1_rebate);
# pre: pm.environment.set("merchant_tax", merchant_tax);
# pre: pm.environment.set("m1_tax", m1_tax);
# pre: pm.environment.set("tax_total", tax_total);
# pre: pm.environment.set("merchant_earnings", merchant_earnings);
# pre: pm.environment.set("m1_earnings", m1_earnings);
# pre: console.log("merchant_transaction_fee: " + merchant_transaction_fee)
# pre: console.log("m1_transaction_fee: " + m1_transaction_fee)
# pre: console.log("m1_rebate: " + m1_rebate)
# pre: console.log("merchant_tax: " + merchant_tax)
# pre: console.log("m1_tax: " + m1_tax)
# pre: console.log("tax_total: " + tax_total)
# pre: console.log("merchant_earnings: " + merchant_earnings)
# pre: console.log("m1_earnings: " + m1_earnings)
# pre: 
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("consumer_access_token",res['data']['refreshToken']);
# post: });
# --- step 2: delete cart ---
# --- step 3: buy now after check-in expiration ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     pm.response.to.have.status(400);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['message']).to.eql("This ticket has expired. Expiration time: 2026-08-25 00:00");
# post: });
# --- step 4: buy now before check-in expiration ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post:     var lineItems = res['data']['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["promoterVariantId"]).to.eql("7cfecd2e-4bda-43e9-a048-1d66f45bc9bd");
# post:         pm.expect(line_item["expirationTime"]).to.eql("2048-08-25T05:00:00.000Z");
# post:         pm.expect(line_item["expirationTimeDisplay"]).to.eql("2048-08-25 01:00");
# post:         pm.expect(line_item["variant"]["isAvailable"]).to.eql(true);
# post:     }
# post: });
# --- step 5: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(8.23);
# post:     var lineItems = res['data']["confirmation"]['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["merchantProductId"]).to.eql("f136d88b-2c36-43d5-af1e-79b18bbde88e");
# post:         pm.expect(line_item["expirationTime"]).to.eql("2048-08-25T05:00:00.000Z");
# post:         pm.expect(line_item["expirationTimeDisplay"]).to.eql("2048-08-25 01:00");
# post:     }
# post: });
# --- step 6: get consumer order detail ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalLineItemPrice']).to.eql(8.23);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         pm.expect(line_item["merchantProductId"]).to.eql("f136d88b-2c36-43d5-af1e-79b18bbde88e");
# post:         pm.expect(line_item["expirationTime"]).to.eql("2048-08-25T05:00:00.000Z");
# post:         pm.expect(line_item["expirationTimeDisplay"]).to.eql("2048-08-25 01:00");
# post:     }
# post: 
# post: 
# post: });




from core.assertions import expect

def test_lury_t5022_t5026_verify_check_in_expiration_time_on_checkout_page_and_order_confirmation_details(ctx):
    """Apifox case #8660973: Lury_T5022_T5026_Verify_check_in_expiration_time_on_checkout_page_and_order_conf"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{consumer_email}}",
    })
    ctx.extract('consumer_access_token', _resp1, '$.data.refreshToken')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now after check-in expiration
    _resp3 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "885eaa07-e64b-4eff-90aa-d5b1582034e9",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "f43e3810-6773-4aa4-a4b8-5155cdd58a18",
                "price": 14.11,
                "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "5c622faf-26eb-4833-905b-ece92ed1f45e",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-test-check-in-expiration",
        },
    })
    # step 4: buy now before check-in expiration
    _resp4 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "885eaa07-e64b-4eff-90aa-d5b1582034e9",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "7cfecd2e-4bda-43e9-a048-1d66f45bc9bd",
                "price": 8.23,
                "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "5c622faf-26eb-4833-905b-ece92ed1f45e",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-test-check-in-expiration",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "7cfecd2e-4bda-43e9-a048-1d66f45bc9bd",
                "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",
                "price": 8.23,
                "customFields": [],
            },
        ],
    })
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp4, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp4, 'orderId')
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body={
        "id": "{{orderId}}",
        "contact": {
            "email": "dian.yuhong.ext+19@1m.app",
            "phoneNumber": "+17404630034",
        },
        "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",
        "paymentInfo": {
            "paymentMethodId": "{{pay_method_id}}",
        },
        "fbAdParams": {
            "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a",
        },
    })
    # step 6: get consumer order detail
    _resp6 = ctx.api.orders.consumer_detail_by_order_number()
