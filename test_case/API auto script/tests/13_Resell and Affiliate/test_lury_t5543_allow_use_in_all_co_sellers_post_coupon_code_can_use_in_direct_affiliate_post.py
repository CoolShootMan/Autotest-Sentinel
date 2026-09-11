"""Migrated from Apifox case #8547898. Source folder: Resell and Affiliate."""
# Apifox Case ID: 8547898  (traceability only — not needed to run)
NAME = "\"Allow use in all co-sellers' post\" coupon code can use in direct affiliate post"
TAGS = ["p0", "resell_and_affiliate", "suite:lury"]
PRIORITY = 0


CASE_ID = 8547898
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
# pre: var unit_price = 9;
# pre: var quantity = 1;
# pre: var commission_rate = 0.25;
# pre: var aff_earnings = Math.round(((unit_price * quantity * commission_rate) + Number.EPSILON) *100 ) / 100;
# pre: var m1_earnings = Number((unit_price * quantity - aff_earnings ).toFixed(2));
# pre: var m1_rebate = Math.floor(set_rebate(unit_price,quantity) *100 ) / 100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(unit_price,quantity)*100)/100;
# pre: var aff_transaction_fee = Math.round(((commission_rate * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - aff_transaction_fee ).toFixed(2));
# pre: 
# pre: pm.environment.set("aff_transaction_fee", aff_transaction_fee);
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("m1_rebate", m1_rebate);
# pre: pm.environment.set("aff_earnings", aff_earnings);
# pre: pm.environment.set("m1_earnings", m1_earnings);
# pre: console.log("aff_transaction_fee: " + aff_transaction_fee)
# pre: console.log("m1_transaction_fee: " + m1_transaction_fee)
# pre: console.log("m1_rebate: " + m1_rebate)
# pre: console.log("aff_earnings: " + aff_earnings)
# pre: console.log("m1_earnings: " + m1_earnings)
# pre: 
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("consumer_access_token",res['data']['token']);
# post: });
# --- step 2: delete cart ---
# --- step 3: buy now  ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 4: apply promotion ---
# post[customScript]: pm.test("Apply coupon and Get Line Item ID", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     var line_items = res["data"]["lineItems"]
# post:     for (var line of line_items){
# post:         var lineItemId = line['lineItemId'];
# post:     }
# post:     pm.environment.set("lineItemId",lineItemId);
# post: });
# --- step 5: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(9);
# post: });
# --- step 6: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 7: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_earnings = pm.environment.get("m1_earnings");
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var m1_rebate = pm.environment.get("m1_rebate");
# post:     var total_payout = Number((m1_earnings - m1_transaction_fee + m1_rebate).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(6.75);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(6.75);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(1.18);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: });
# post: 
# --- step 8: Login -affiliate ---
# post[customScript]: pm.test("Check P5 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("affiliate_access_token",res['data']['token']);
# post: });
# --- step 9: get affiliate promoter orders ---
# post[customScript]: pm.test("Get P5 order ID", function () {
# post:     var res = JSON.parse(responseBody);
# post:     order_list = res['data']['items']
# post:     var orderNumber = pm.environment.get("orderNumber");
# post:     console.log(orderNumber)
# post:     var curatorOrderId = "";
# post:     for (var order of order_list){
# post:         if (order['orderNumber'] === orderNumber){
# post:             var curatorOrderId = order['id'];
# post:             console.log(curatorOrderId);
# post:         }
# post:     }
# post:     pm.environment.set("P5_OrderId",curatorOrderId);
# post: });
# --- step 10: get affiliate order detail v2 ---
# post[customScript]: pm.test("Check P5 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var aff_earnings = pm.environment.get("aff_earnings");
# post:     var aff_transaction_fee = pm.environment.get("aff_transaction_fee");
# post:     var total_payout = Number((aff_earnings - aff_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(aff_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(aff_earnings);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(aff_earnings);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "35811870-0f2f-43e7-955a-887fb052f2dd"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(9);
# post:             pm.expect(line_item["retailPrice"]).to.eql(10);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(1);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(2.25);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(6.75);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(9);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(2.25);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(2.25);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(1);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_lury_t5543_allow_use_in_all_co_sellers_post_coupon_code_can_use_in_direct_affiliate_post(ctx):
    """Apifox case #8547898: Lury_T5543_Allow_use_in_all_co_sellers_post_coupon_code_can_use_in_direct_affili"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.token')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now 
    _resp3 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "3f6a6723-9223-418e-953c-e861a0c9969e",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "35811870-0f2f-43e7-955a-887fb052f2dd",\n            "price": 10,\n            "postId": "3f6a6723-9223-418e-953c-e861a0c9969e",\n            "selected": true,\n            "affiliateCode": "70zd9u",\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "74ec16cb-ed91-45a4-86f0-782c3bfe0f07",\n        "pixelId": [\n            "453453"\n        ],\n        "externalId": "9080b930-2796-4b96-8a52-64c70ff1e65c",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-affiliate-coupon-code-testing?aff=70zd9u"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "35811870-0f2f-43e7-955a-887fb052f2dd",\n            "postId": "3f6a6723-9223-418e-953c-e861a0c9969e",\n            "price": 10,\n            "affiliateCode": "70zd9u",\n            "customFields": []\n        }\n    ],\n    "subdomainVanityUrl": ""\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: apply promotion
    _resp4 = ctx.api.orders.update_promotions(body='{\n  "orderId": "{{orderId}}",\n  "shippingAddress": {\n    "line1": "",\n    "city": "",\n    "zipcode": "",\n    "state": ""\n  },\n  "applicableCode": "affcode"\n}')
    _j = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "lineItems"]) or []
    if _arr:
        vars['lineItemId'] = _arr[0].get('lineItemId')
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 6: Login-M1
    _resp6 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp6, '$.data.token')
    # step 7: get M1 order detail v2
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # step 8: Login -affiliate
    _resp8 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{affiliate_promoter}}"\n}')
    ctx.extract('affiliate_access_token', _resp8, '$.data.token')
    # step 9: get affiliate promoter orders
    _resp9 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    vars['P5_OrderId'] = 'curatorOrderId'
    # step 10: get affiliate order detail v2
    _resp10 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{P5_OrderId}}'})
