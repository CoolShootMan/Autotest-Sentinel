"""Migrated from Apifox case #8000177. Source folder: Consumer Purchase flow - resell and coupon and refund and ship and fee and tax."""
# Apifox Case ID: 8000177  (traceability only — not needed to run)
NAME = "&T4140 Verify the event coupon can be used for all events"
TAGS = ["p0", "consumer_purchase_flow_resell_and_coupon_and_refund_and_ship_and_fee_and_tax", "suite:lury"]
PRIORITY = 0


CASE_ID = 8000177
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
# pre: var unit_price = 2.13;
# pre: var m1_rebate = Math.floor(set_rebate(unit_price,1)*100)/100;
# pre: var m1_transaction_fee = Math.floor(get_transaction_fee_item_level_general(unit_price,1)*100)/100;
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("m1_rebate", m1_rebate);
# pre: tax_value = Number(0.06 * unit_price).toFixed(2);
# pre: pm.environment.set("tax_value", tax_value);
# pre: console.log(m1_transaction_fee)
# pre: console.log(m1_rebate)
# pre: console.log(tax_value)
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("consumer_access_token",res['data']['token']);
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
# post:     pm.expect(res['data']['totalTopay']).to.eql(2.13);
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
# post:     var tax_value = pm.environment.get("tax_value");
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var transaction_fee = Number((eval(tax_value) + eval(m1_transaction_fee)).toFixed(2));
# post:     var m1_rebate = pm.environment.get("m1_rebate");
# post:     var total_payout = Number((2.13 - m1_transaction_fee + m1_rebate).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(2.13);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(2.13);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(m1_rebate);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(eval(tax_value));
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(eval(tax_value));
# post: });
# post: 
# --- step 8: delete cart ---
# --- step 9: buy now ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 10: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(0);
# post: });
# --- step 11: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["transactionFee"]).to.eql(0);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(0);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(0);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(eval(0));
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(eval(0));
# post: });
# post: 
# --- step 12: delete cart ---
# --- step 13: buy now ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 14: apply promotion ---
# post[customScript]: pm.test("Apply coupon and Get Line Item ID", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     var line_items = res["data"]["lineItems"]
# post:     for (var line of line_items){
# post:         var lineItemId = line['lineItemId'];
# post:     }
# post:     pm.environment.set("lineItemId",lineItemId);
# post: });
# --- step 15: create Order -any day ticket ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(22);
# post: });
# --- step 16: get M1 order detail v2 ---
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
# pre: var m1_rebate = Math.floor(set_rebate(11,2)*100)/100;
# pre: var m1_transaction_fee = Math.floor(get_transaction_fee_item_level_general(11,2)*100)/100;
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("m1_rebate", m1_rebate);
# pre: console.log(m1_transaction_fee)
# pre: console.log(m1_rebate)
# pre: 
# pre: 
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var m1_rebate = pm.environment.get("m1_rebate");
# post:     var total_payout = Number((22 - m1_transaction_fee + m1_rebate).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(22);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(22);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(m1_rebate);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(eval(0));
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(eval(0));
# post: });
# post: 
# --- step 17: delete cart ---
# --- step 18: buy now ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 19: create Order - resell event product ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(0);
# post: });
# --- step 20: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["transactionFee"]).to.eql(0);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(0);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(0);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(eval(0));
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(eval(0));
# post: });
# post: 
# --- step 21: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 22: get P1 orders ---
# post[customScript]: pm.test("Get P1 order ID", function () {
# post:     pm.response.to.have.status(200);
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
# post:     pm.environment.set("P1_OrderId",curatorOrderId);
# post: });
# --- step 23: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(0);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(0);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "6f967b77-b82a-4bd1-95ca-d21dfe1424af"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(0);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(100);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(0);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(0);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(0);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
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
# post: 
# post: 
# post: 
# post: 




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_lury_t5064_t4140_verify_the_event_coupon_can_be_used_for_all_events(ctx):
    """Apifox case #8000177: Lury_T5064_T4140_Verify_the_event_coupon_can_be_used_for_all_events"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.token')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "c9110e39-abb6-41eb-b810-4faba53fd9c0",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "def1a21f-b0eb-4187-9587-5489b76a09fd",\n            "price": 2.37,\n            "postId": "c9110e39-abb6-41eb-b810-4faba53fd9c0",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "290ba429-d466-404b-b991-c0156e7a6cd7",\n        "pixelId": [\n            "453453"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-event-0309-1"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "def1a21f-b0eb-4187-9587-5489b76a09fd",\n            "postId": "c9110e39-abb6-41eb-b810-4faba53fd9c0",\n            "price": 2.37,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: apply promotion
    _resp4 = ctx.api.orders.update_promotions(body='{\n  "orderId": "{{orderId}}",\n  "shippingAddress": {\n    "line1": "",\n    "city": "",\n    "zipcode": "",\n    "state": ""\n  },\n  "applicableCode": "eventcc"\n}')
    _j = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "lineItems"]) or []
    if _arr:
        vars['lineItemId'] = _arr[0].get('lineItemId')
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Real",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 6: Login-M1
    _resp6 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp6, '$.data.token')
    # step 7: get M1 order detail v2
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # step 8: delete cart
    _resp8 = ctx.api.cart.delete()
    # step 9: buy now
    _resp9 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "6968b611-abc3-4d5d-9f91-fe90d45f8540",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "a1e7a176-8103-4e4d-93b7-71984bb41efd",\n            "price": 100,\n            "postId": "6968b611-abc3-4d5d-9f91-fe90d45f8540",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "a46d22d5-8806-439a-a42f-5f9292ede25c",\n        "pixelId": [\n            "453453"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-event-automation-with-ticket-100"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "a1e7a176-8103-4e4d-93b7-71984bb41efd",\n            "postId": "6968b611-abc3-4d5d-9f91-fe90d45f8540",\n            "price": 100,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp9, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp9, 'orderId')
    # step 10: create Order
    _resp10 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Real",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 11: get M1 order detail v2
    _resp11 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # step 12: delete cart
    _resp12 = ctx.api.cart.delete()
    # step 13: buy now
    _resp13 = ctx.api.orders.buy_now(body='{\n  "updateCartItems": [\n    {\n      "quantity": 2,\n      "promoterProductVariantId": "3d9e7c13-f770-4a69-83e3-b803a0acc5f4",\n      "price": 12.22,\n      "selected": true,\n      "customFields": [],\n      "eventId": "766d1e39-bc84-4b80-a562-e1ced347f0d4"\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "b4fcaf45-67c4-48db-af05-96f05cd6a288",\n    "pixelId": [\n      "453453"\n    ],\n    "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n    "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n    "eventSourceUrl": "https://release.pear.us/mcc"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 2,\n      "id": "3d9e7c13-f770-4a69-83e3-b803a0acc5f4",\n      "price": 24.44,\n      "customFields": []\n    }\n  ],\n  "subdomainVanityUrl": ""\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp13, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp13, 'orderId')
    # step 14: apply promotion
    _resp14 = ctx.api.orders.update_promotions(body='{\n    "orderId": "{{orderId}}",\n    "shippingAddress": {\n        "id": "41ef3748-0466-4e91-95c2-a7983d14e151",\n        "firstName": "dian",\n        "lastName": "Automation",\n        "fullName": "dian dian",\n        "line1": "11111 Research Boulevard",\n        "line2": "",\n        "city": "Austin",\n        "state": "TX",\n        "stateName": "Texas",\n        "zipcode": "78759",\n        "userId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "isDefault": true,\n        "phoneNumber": "+17404630034",\n        "createdAt": "2025-10-27T08:02:35.026Z",\n        "deletedAt": null,\n        "updatedAt": "2025-11-25T09:39:09.769Z",\n        "email": null\n    },\n    "applicableCode": "eventcc"\n}')
    _j = _resp14.json() if _resp14.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "lineItems"]) or []
    if _arr:
        vars['lineItemId'] = _arr[0].get('lineItemId')
    # step 15: create Order -any day ticket
    _resp15 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Automation",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 16: get M1 order detail v2
    _resp16 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # step 17: delete cart
    _resp17 = ctx.api.cart.delete()
    # step 18: buy now
    _resp18 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "229a5dfb-24b0-4c70-aefd-bdc2bb1b7c37",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "6f967b77-b82a-4bd1-95ca-d21dfe1424af",\n            "price": 100,\n            "postId": "229a5dfb-24b0-4c70-aefd-bdc2bb1b7c37",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "2899d9d0-ec03-4490-83bd-a0dfe504b6e0",\n        "pixelId": [\n            "test",\n            "vvvvxxxx",\n            "20260112",\n            "20260113"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/yu-xiao/post/lury-event-0310"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "6f967b77-b82a-4bd1-95ca-d21dfe1424af",\n            "postId": "229a5dfb-24b0-4c70-aefd-bdc2bb1b7c37",\n            "price": 100,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp18, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp18, 'orderId')
    # step 19: create Order - resell event product
    _resp19 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Automation",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 20: get M1 order detail v2
    _resp20 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # step 21: Login - P1
    _resp21 = ctx.api.auth.sign_in(body='{\n    "password": "{{P1_password}}",\n    "email": "{{P1}}"\n}')
    ctx.extract('P1_access_token', _resp21, '$.data.token')
    # step 22: get P1 orders
    _resp22 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    vars['P1_OrderId'] = 'curatorOrderId'
    # step 23: get P1 order detail v2
    _resp23 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{P1_OrderId}}'})
