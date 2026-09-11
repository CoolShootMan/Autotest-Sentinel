"""Migrated from Apifox case #8059203. Source folder: Consumer Purchase flow - resell and coupon and refund and ship and fee and tax."""
# Apifox Case ID: 8059203  (traceability only — not needed to run)
NAME = "Verify consumer can purchase event product and check transaction fee"
TAGS = ["p0", "consumer_purchase_flow_resell_and_coupon_and_refund_and_ship_and_fee_and_tax", "suite:lury"]
PRIORITY = 0


CASE_ID = 8059203
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
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(10,1)*100)/100;
# pre: 
# pre: pm.environment.set("m1_transaction_fee", transaction_fee_item_level);
# pre: console.log(transaction_fee_item_level)
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
# post:     pm.expect(res['data']['totalTopay']).to.eql(10);
# post: });
# --- step 5: get consumer order detail ---
# post[customScript]: pm.test("Check event product on order details page", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalLineItemPrice']).to.eql(10);
# post:     pm.expect(res['data']['totalToPay']).to.eql(10);
# post:     pm.expect(res['data']['totalPaid']).to.eql(10);
# post:     pm.expect(res['data']['totalTax']).to.eql(0);
# post:     pm.expect(res['data']['totalLineItemSubtotal']).to.eql(10);
# post:     pm.expect(res['data']['fulfillmentStatus']).to.eql("FULFILLED");
# post:     pm.expect(res['data']['totalTicketFees']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["title"] === "event product - automation"){
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["unitPrice"]).to.eql(10);
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(10);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["fulfillmentCount"]).to.eql(1);
# post:             pm.expect(line_item["listingType"]).to.eql("EVENT_PRODUCT");
# post:             pm.expect(line_item["shippingFee"]).to.eql(0);
# post:             pm.expect(line_item["additionalShippingFee"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["discount"]).to.eql(0);
# post:             pm.expect(line_item["realShippingFee"]).to.eql(0);
# post:             pm.expect(line_item["autoFulfill"]).to.eql(true);
# post:             pm.expect(line_item["productTaxEnable"]).to.eql(false);
# post:             pm.expect(line_item["ticketFees"]).to.eql(0);
# post:             pm.expect(line_item["ticketFeesAfterRefund"]).to.eql(0);
# post:             pm.expect(line_item["deliveryMethod"]).to.eql("QR_CODE");
# post:             pm.expect(line_item["thirdPartyDeliveryMessage"]).to.eql(null);
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
# post:             pm.expect(line_item["multipleDaysPass"]).to.eql(null);
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
# post:             
# post:         }
# post:         else{
# post:             pm.expect(1).to.eql(2);
# post:            }
# post:     }
# post: 
# post: 
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
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var total_payout = Number((10 - m1_transaction_fee).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(10);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(10);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "b6b82325-d2cd-440f-8e4f-2e85d3ac73a6"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(10);
# post:             pm.expect(line_item["retailPrice"]).to.eql(10);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(10);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(10);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(10);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(10);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(1);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:             pm.expect(line_item["isSamplePurchase"]).to.eql(false);
# post:             pm.expect(line_item["shippingType"]).to.eql("NO_SHIPPING_REQUIRED");
# post:             pm.expect(line_item["listingType"]).to.eql("EVENT_PRODUCT");
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
# post: 
# post: 
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });




from core.assertions import expect

def test_lury_t4483_verify_consumer_can_purchase_event_product_and_check_transaction_fee(ctx):
    """Apifox case #8059203: Lury_T4483_Verify_consumer_can_purchase_event_product_and_check_transaction_fee"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.refreshToken')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "bc4c8157-c1c0-405e-b46b-847450ca17d8",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "b6b82325-d2cd-440f-8e4f-2e85d3ac73a6",\n            "price": 10,\n            "postId": "bc4c8157-c1c0-405e-b46b-847450ca17d8",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "5288d163-c4f5-412d-b578-46dd69f8f334",\n        "pixelId": [\n            "453453"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-event-0119"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "b6b82325-d2cd-440f-8e4f-2e85d3ac73a6",\n            "postId": "bc4c8157-c1c0-405e-b46b-847450ca17d8",\n            "price": 10,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Automation",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "{{shippingAddressId}}",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 5: get consumer order detail
    _resp5 = ctx.api.orders.consumer_detail_by_order_number()
    # step 6: Login-M1
    _resp6 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp6, '$.data.token')
    # step 7: get M1 order detail v2
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
