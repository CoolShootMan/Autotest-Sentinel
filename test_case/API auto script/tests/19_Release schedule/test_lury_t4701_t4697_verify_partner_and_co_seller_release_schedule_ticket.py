"""Migrated from Apifox case #8177728. Source folder: Release schedule."""
# Apifox Case ID: 8177728  (traceability only — not needed to run)
NAME = "&T4697 Verify partner and co-seller release schedule - ticket"
TAGS = ["p0", "release_schedule", "suite:lury"]
PRIORITY = 0


CASE_ID = 8177728
ENV_NAME = "Release"

# --- step 1: Consumer-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 0;
# pre:     item_percentage_fee = 0.085;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: var order_level_transaction_fee = Math.floor(4.99 * 0.085*100)/100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(1.33,1)*100)/100;
# pre: var p1_transaction_fee = Math.round(((0.16/1.33 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee = Math.round(((0.17/1.33 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - merchant_transaction_fee + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(m1_transaction_fee)
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
# --- step 4: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(13.1);
# post: });
# --- step 5: M1-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 0;
# pre:     item_percentage_fee = 0.085;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: var order_level_transaction_fee = Number((4.99 * 0.035).toFixed(2));
# pre: var transaction_fee_item_level = Number((get_transaction_fee_item_level_general(85.5,1)).toFixed(2));
# pre: var p1_transaction_fee = Number(((10/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var curator_transaction_fee = Number(((9/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var promoter_transaction_fee = Number(((4.95/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var p5_transaction_fee = Number(((8.55/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var m1_transaction_fee_item = Number(((40/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var m1_transaction_fee = m1_transaction_fee_item + order_level_transaction_fee
# pre: var merchant_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - m1_transaction_fee_item - curator_transaction_fee - promoter_transaction_fee - p5_transaction_fee ).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("curator_transaction_fee", curator_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: pm.environment.set("p5_transaction_fee", p5_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(curator_transaction_fee)
# pre: console.log(promoter_transaction_fee)
# pre: console.log(p5_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P-21_access_token",res['data']['refreshToken']);
# post: });
# --- step 6: Check partner release schedule ---
# pre: console.log("event start date is 2048-03-20 without end date")
# pre: var second_date = "2048-03-28"
# pre: pm.environment.set("second_date",second_date);
# pre: var third_date = "2048-04-11"
# pre: pm.environment.set("third_date",third_date);
# pre: 
# pre: 
# pre: 
# pre: 
# pre: 
# post[customScript]: pm.test("Check release schedule based on admin settings", function () {
# post:     pm.response.to.have.status(200);
# post:     var orderNumber = pm.environment.get("orderNumber")
# post:     var res = JSON.parse(responseBody);
# post:     var order_list = res["data"]["items"]
# post:     var release_date_list = [];
# post:     var release_amount_list = [];
# post:     for (var order of order_list){
# post:         if (order['orderNumber'] === orderNumber){
# post:             net_earnings = order['totalMerchantPayoutToPay'];
# post:             var settlements = order['settlements'];
# post:             for (var release of settlements){
# post:                 var only_date = (release["releaseAt"]).slice(0,10)
# post:                 release_date_list.push(only_date);
# post:                 release_amount_list.push(release["releaseAmount"])
# post:             }
# post:         }
# post:     }
# post:     console.log(release_date_list);
# post:     var second_date = pm.environment.get("second_date");
# post:     var third_date = pm.environment.get("third_date");
# post:     var second_amount = Math.round(((net_earnings*0.95) + Number.EPSILON) *100 ) / 100;
# post:     var third_amount = Math.round(((net_earnings  - second_amount) + Number.EPSILON) *100 ) / 100;
# post:     console.log(release_date_list[0]);
# post:     console.log(release_date_list[1]);
# post:     pm.expect(release_date_list[0]).to.eql(second_date);
# post:     pm.expect(release_date_list[1]).to.eql(third_date);
# post:     pm.expect(release_amount_list[0]).to.eql(second_amount);
# post:     pm.expect(release_amount_list[1]).to.eql(third_amount);
# post: });
# --- step 7: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['refreshToken']);
# post: });
# --- step 8: Check merchant release schedule ---
# pre: console.log("event start date is 2048-03-20 without end date")
# pre: var second_date = "2048-03-28"
# pre: pm.environment.set("second_date",second_date);
# pre: var third_date = "2048-04-11"
# pre: pm.environment.set("third_date",third_date);
# pre: 
# post[customScript]: pm.test("Check release schedule based on admin settings", function () {
# post:     pm.response.to.have.status(200);
# post:     var orderNumber = pm.environment.get("orderNumber")
# post:     var res = JSON.parse(responseBody);
# post:     var order_list = res["data"]["items"]
# post:     var release_date_list = [];
# post:     var release_amount_list = [];
# post:     for (var order of order_list){
# post:         if (order['orderNumber'] === orderNumber){
# post:             net_earnings = order['totalPayoutToPay'];
# post:             var settlements = order['settlements'];
# post:             for (var release of settlements){
# post:                 var only_date = (release["releaseAt"]).slice(0,10);
# post:                 console.log(only_date);
# post:                 release_date_list.push(only_date)
# post:                 release_amount_list.push(release["releaseAmount"])
# post:             }
# post:         }
# post:     }
# post:     console.log(release_date_list);
# post:     var second_date = pm.environment.get("second_date");
# post:     var third_date = pm.environment.get("third_date");
# post:     console.log(release_date_list[0]);
# post:     console.log(release_date_list[1]);
# post:     var second_amount = Math.round(((net_earnings*0.95) + Number.EPSILON) *100 ) / 100;
# post:     var third_amount = Math.round(((net_earnings - second_amount) + Number.EPSILON) *100 ) / 100;
# post:     pm.expect(release_date_list[0]).to.eql(second_date);
# post:     pm.expect(release_date_list[1]).to.eql(third_date);
# post:     pm.expect(release_amount_list[0]).to.eql(second_amount);
# post:     pm.expect(release_amount_list[1]).to.eql(third_amount);
# post: });




from core.assertions import expect

def test_lury_t4701_t4697_verify_partner_and_co_seller_release_schedule_ticket(ctx):
    """Apifox case #8177728: Lury_T4701_T4697_Verify_partner_and_co_seller_release_schedule_ticket"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.refreshToken')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "e5dc7238-c7c0-4abe-a3ce-6962cffc5579",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "92f174ea-635e-48f0-9eda-4a66f793912c",\n            "price": 13.1,\n            "postId": "e5dc7238-c7c0-4abe-a3ce-6962cffc5579",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "69989f83-4e22-4d21-b18a-922e9e424506",\n        "pixelId": [\n            "453453"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-test-share-revenue-automation"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "92f174ea-635e-48f0-9eda-4a66f793912c",\n            "postId": "e5dc7238-c7c0-4abe-a3ce-6962cffc5579",\n            "price": 13.1,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 5: M1-login
    _resp5 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('P-21_access_token', _resp5, '$.data.refreshToken')
    # step 6: Check partner release schedule
    _resp6 = ctx.api.misc.earnings_merchant_orders(params={'pageNumber': '1', 'pageSize': '30', 'q': 'Revenue'})
    # step 7: Login - merchant
    _resp7 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp7, '$.data.refreshToken')
    # step 8: Check merchant release schedule
    _resp8 = ctx.api.misc.earnings_promoter_orders(params={'pageNumber': '1', 'pageSize': '30', 'q': 'Commissions'})
