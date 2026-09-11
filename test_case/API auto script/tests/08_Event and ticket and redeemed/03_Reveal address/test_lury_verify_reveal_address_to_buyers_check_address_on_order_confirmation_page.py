"""Migrated from Apifox case #8600624. Source folder: Event and ticket and redeemed/Reveal address."""
# Apifox Case ID: 8600624  (traceability only — not needed to run)
NAME = "(Lury)Verify reveal address to buyers check address on order confirmation page"
TAGS = ["p0", "event_and_ticket_and_redeemed_reveal_address", "suite:lury"]
PRIORITY = 0


CASE_ID = 8600624
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
# --- step 3: buy now ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 4: create Order and check address ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(0);
# post:     var line_item_list = res['data']["confirmation"]['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["merchantProductId"] === "70990c9a-f53a-4887-b7a1-9e4881d769cd"){
# post:             pm.expect(line_item["extraInfo"]["isAddressHidden"]).to.eql(false);
# post:             pm.expect(line_item["extraInfo"]["location"]).to.eql("111 South Grant Avenue, Columbus, OH");
# post:             pm.expect(line_item["extraInfo"]["event"]).to.eql("Lury event reveal address to buyer automation testing 0806");
# post:             pm.expect(line_item["extraInfo"]["venue"]).to.eql("reveal address to buyers");
# post:         }
# post:     }
# post: 
# post: });




from core.assertions import expect

def test_lury_verify_reveal_address_to_buyers_check_address_on_order_confirmation_page(ctx):
    """Apifox case #8600624: Lury_Verify_reveal_address_to_buyers_check_address_on_order_confirmation_page"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.refreshToken')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.checkout_express(body='{\n    "items": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "5a6fff14-1a8d-47d4-af60-aa59e3070800",\n            "price": 0,\n            "postId": "0eb07cc8-6f41-49f7-9fb8-bb13f3c3f763",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "744eb9a3-55df-4655-b9ee-2759b89058a0",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "154873ad-8fbe-4f69-bdf0-e11205c4eab8",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-event-dont-reveal-address-automation-testing-0806"\n    },\n    "subdomainVanityUrl": ""\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: create Order and check address
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "firstName":"Lury",\n        "lastName":"don\'t reveal address",\n        "phoneNumber":"+17404630034"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
