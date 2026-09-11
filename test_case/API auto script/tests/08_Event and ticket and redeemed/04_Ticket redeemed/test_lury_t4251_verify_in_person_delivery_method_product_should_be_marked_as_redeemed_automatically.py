"""Migrated from Apifox case #7687520. Source folder: Event and ticket and redeemed/Ticket redeemed."""
# Apifox Case ID: 7687520  (traceability only — not needed to run)
NAME = "Verify In-person delivery method product should be marked as redeemed automatically"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_redeemed", "suite:lury"]
PRIORITY = 0


CASE_ID = 7687520
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
# pre: var unit_price = 12.22;
# pre: var quantity = 1;
# pre: var commission_rate = 0.25;
# pre: var promoter_earnings =  Math.round(((unit_price * quantity * commission_rate) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_earnings = Number((unit_price * quantity - promoter_earnings ).toFixed(2));
# pre: 
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(unit_price,quantity)*100)/100;
# pre: var promoter_transaction_fee = Math.round(((promoter_earnings/(unit_price * quantity)* transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee = Number((transaction_fee_item_level - promoter_transaction_fee ).toFixed(2));
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: pm.environment.set("merchant_earnings", merchant_earnings);
# pre: pm.environment.set("promoter_earnings", promoter_earnings);
# pre: pm.environment.set("unit_price", unit_price);
# pre: console.log("merchant_transaction_fee: " + merchant_transaction_fee)
# pre: console.log("promoter_transaction_fee: " + promoter_transaction_fee)
# pre: console.log("merchant_earnings: " + merchant_earnings)
# pre: console.log("promoter_earnings: " + promoter_earnings)
# pre: 
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
# --- step 4: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(12.22);
# post: });
# --- step 5: get consumer order detail ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalLineItemPrice']).to.eql(12.22);
# post:     pm.expect(res['data']['totalToPay']).to.eql(12.22);
# post:     pm.expect(res['data']['totalPaid']).to.eql(12.22);
# post:     pm.expect(res['data']['totalTax']).to.eql(0);
# post:     pm.expect(res['data']['totalLineItemSubtotal']).to.eql(12.22);
# post:     pm.expect(res['data']['fulfillmentStatus']).to.eql("FULFILLED");
# post:     pm.expect(res['data']['totalTicketFees']).to.eql(2.22);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["title"] === "ticket-in person"){
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["unitPrice"]).to.eql(12.22);
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(12.22);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["fulfillmentCount"]).to.eql(1);
# post:             pm.expect(line_item["listingType"]).to.eql("TICKET");
# post:             pm.expect(line_item["shippingFee"]).to.eql(0);
# post:             pm.expect(line_item["additionalShippingFee"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["discount"]).to.eql(0);
# post:             pm.expect(line_item["realShippingFee"]).to.eql(0);
# post:             pm.expect(line_item["autoFulfill"]).to.eql(true);
# post:             pm.expect(line_item["productTaxEnable"]).to.eql(false);
# post:             pm.expect(line_item["ticketFees"]).to.eql(2.22);
# post:             pm.expect(line_item["ticketFeesAfterRefund"]).to.eql(2.22);
# post:             pm.expect(line_item["deliveryMethod"]).to.eql("IN_PERSON");
# post:             pm.expect(line_item["thirdPartyDeliveryMessage"]).to.eql(null);
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
# post:             pm.expect(line_item["multipleDaysPass"]).to.eql(null);
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
# post:             var redeem_list = line_item["orderLineItemUnits"];
# post:             for (var redeem of redeem_list){
# post:                 pm.expect(redeem["status"]).to.eql("COMPLETED");
# post:                 pm.environment.set("numberCode",redeem["numberCode"])
# post:             }
# post: 
# post:         }
# post:         else{
# post:             pm.expect(1).to.eql(2);
# post:            }
# post:     }
# post: 
# post: 
# post: });
# --- step 6: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['refreshToken']);
# post: });
# --- step 7: get merchant commission charge ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var merchant_earnings = pm.environment.get("merchant_earnings");
# post:     var numberCode = pm.environment.get("numberCode");
# post:     var total_payout = Number((merchant_earnings - merchant_transaction_fee + res['data']['transactionFeeRebate']).toFixed(2));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(merchant_earnings);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(merchant_earnings);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(merchant_transaction_fee);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(1.79);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "e377dc0b-0b01-4f7a-ad67-02dbfd849745"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(12.22);
# post:             pm.expect(line_item["retailPrice"]).to.eql(12.22);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(12.22);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(3.06);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(12.22);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(9.16);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(9.16);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(1);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:             var redeem_list = line_item["orderLineItemUnits"];
# post:             for (var redeem of redeem_list){
# post:                 pm.expect(redeem["status"]).to.eql("COMPLETED");
# post:                 pm.expect(redeem["numberCode"]).to.eql(numberCode);
# post:             }
# post:             }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });
# --- step 8: Login - curator ---
# post[customScript]: pm.test("Check promoter login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("curator_access_token",res['data']['token']);
# post: });
# --- step 9: get curator orders ---
# post[customScript]: pm.test("Get promoter order ID", function () {
# post:     var res = JSON.parse(responseBody);
# post:     order_list = res['data']['items']
# post:     var orderNumber = pm.environment.get("orderNumber");
# post:     console.log(orderNumber)
# post:     var promoterOrderId = "";
# post:     for (var order of order_list){
# post:         if (order['orderNumber'] === orderNumber){
# post:             var promoterOrderId = order['id'];
# post:             console.log(promoterOrderId);
# post:         }
# post:     }
# post:     pm.environment.set("promoterOrderId",promoterOrderId);
# post:     console.log(promoterOrderId)
# post: });
# --- step 10: get curator order detail v2 ---
# post[customScript]: pm.test("Check promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var promoter_earnings = pm.environment.get("promoter_earnings");
# post:     var unit_price = pm.environment.get("unit_price");
# post:     var total_payout = Number((promoter_earnings - promoter_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(promoter_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(promoter_earnings);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(promoter_earnings);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     pm.expect(res['data']['fulfillmentStatus']).to.eql("FULFILLED");
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "e377dc0b-0b01-4f7a-ad67-02dbfd849745"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(unit_price);
# post:             pm.expect(line_item["retailPrice"]).to.eql(unit_price);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(promoter_earnings);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(9.16);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(unit_price);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(promoter_earnings);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(promoter_earnings);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(1);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["variantInfo"]["listingType"]).to.eql("TICKET");
# post:             pm.expect(line_item["variantInfo"]["autoFulfill"]).to.eql(true);
# post:             pm.expect(line_item["variantInfo"]["deliveryMethod"]).to.eql("IN_PERSON");
# post:            }
# post:            else {
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_lury_t4251_verify_in_person_delivery_method_product_should_be_marked_as_redeemed_automatically(ctx):
    """Apifox case #7687520: Lury_T4251_Verify_In_person_delivery_method_product_should_be_marked_as_redeemed"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.refreshToken')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "ad8159a0-6273-4830-8fa4-55b7a3b9a9f8",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "e377dc0b-0b01-4f7a-ad67-02dbfd849745",\n            "price": 12.22,\n            "postId": "ad8159a0-6273-4830-8fa4-55b7a3b9a9f8",\n            "selected": true\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "aa2f9fca-9b51-4700-9826-8f43ac45f24a",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "d92e2649-9dc6-4370-9389-b2305c71cf78",\n        "eventSourceUrl": "https://release.pear.us/tester/post/automation-1222-lury-test-4251"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "e377dc0b-0b01-4f7a-ad67-02dbfd849745",\n            "postId": "ad8159a0-6273-4830-8fa4-55b7a3b9a9f8",\n            "price": 12.22\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "{{shippingAddressId}}",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 5: get consumer order detail
    _resp5 = ctx.api.orders.consumer_detail_by_order_number()
    ctx.extract('numberCode', _resp5, '$.data.lineItems[0].orderLineItemUnits[0].numberCode')
    # step 6: Login - merchant
    _resp6 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp6, '$.data.refreshToken')
    # step 7: get merchant commission charge
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{merchantIDf}}'})
    # step 8: Login - curator
    _resp8 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{curator_email}}"\n}')
    ctx.extract('curator_access_token', _resp8, '$.data.token')
    # step 9: get curator orders
    _resp9 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    _j = _resp9.json() if _resp9.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    for _order in _arr:
        if _order.get('orderNumber') == vars.get('orderNumber'):
            vars['promoterOrderId'] = _order.get('id')
    # step 10: get curator order detail v2
    _resp10 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{promoterOrderId}}'})
