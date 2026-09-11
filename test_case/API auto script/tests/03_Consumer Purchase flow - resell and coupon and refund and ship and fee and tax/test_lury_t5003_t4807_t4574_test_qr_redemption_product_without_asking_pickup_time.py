"""Migrated from Apifox case #7969438. Source folder: Consumer Purchase flow - resell and coupon and refund and ship and fee and tax."""
# Apifox Case ID: 7969438  (traceability only — not needed to run)
NAME = "&T4807&T4574 Test QR redemption product without asking pickup time"
TAGS = ["p0", "consumer_purchase_flow_resell_and_coupon_and_refund_and_ship_and_fee_and_tax", "suite:lury"]
PRIORITY = 0


CASE_ID = 7969438
ENV_NAME = "Release"

# --- step 1: Consumer-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 1;
# pre:     item_percentage_fee = 0.085;
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
# pre: setTimeout(() => {
# pre:     console.log('两秒后执行');
# pre: }, 2000);
# pre: 
# post[customScript]: pm.test("Check QR redemption product 0228", function () {
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
# post:         if (line_item["title"] === "QR redemption product 0228"){
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["unitPrice"]).to.eql(10);
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(10);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["fulfillmentCount"]).to.eql(1);
# post:             pm.expect(line_item["listingType"]).to.eql("QR_REDEMPTION");
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
# post:             var redeem_list = line_item["orderLineItemUnits"];
# post:             for (var redeem of redeem_list){
# post:                 pm.expect(redeem["status"]).to.eql("IN_PROCESSING");
# post:                 pm.environment.set("numberCode",redeem["numberCode"])
# post:             }
# post:             pm.expect(line_item["extraInfo"]["businessName"]).to.eql("Automation name");
# post:             pm.expect(line_item["extraInfo"]["businessHours"]).to.eql("Monday");
# post:             pm.expect(line_item["extraInfo"]["businessAddress"]).to.eql("470 East Colorado Avenue, Denver, CO, USA");
# post:             pm.expect(line_item["extraInfo"]["businessTimezone"]).to.eql("America/Denver");
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
# post:     var numberCode = pm.environment.get("numberCode");
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
# post:            if (line_item["variantInfo"]["id"] === "39aae2f5-e536-4c1e-bf24-3ac5cd94fdc8"){
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
# post:             pm.expect(line_item["listingType"]).to.eql("QR_REDEMPTION");
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
# post:             pm.expect(line_item["variantInfo"]["extraInfo"]["businessName"]).to.eql("Automation name");
# post:             pm.expect(line_item["variantInfo"]["extraInfo"]["businessHours"]).to.eql("Monday");
# post:             pm.expect(line_item["variantInfo"]["extraInfo"]["businessAddress"]).to.eql("470 East Colorado Avenue, Denver, CO, USA");
# post:             pm.expect(line_item["variantInfo"]["extraInfo"]["businessTimezone"]).to.eql("America/Denver");
# post:             var line_item_unit = line_item["orderLineItemUnits"]
# post:             for (var unit of line_item_unit){
# post:                 pm.expect(unit["numberCode"]).to.eql(numberCode);
# post:                 pm.expect(unit["status"]).to.eql("IN_PROCESSING");
# post:             }
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });




from core.assertions import expect

def test_lury_t5003_t4807_t4574_test_qr_redemption_product_without_asking_pickup_time(ctx):
    """Apifox case #7969438: Lury_T5003_T4807_T4574_Test_QR_redemption_product_without_asking_pickup_time"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.refreshToken')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "9deb8571-c23e-4b0e-b988-40a29a1d67dd",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "39aae2f5-e536-4c1e-bf24-3ac5cd94fdc8",\n            "price": 10,\n            "postId": "9deb8571-c23e-4b0e-b988-40a29a1d67dd",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "6a6ee3fd-1c26-4577-bfd5-e7a0eb091ad4",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/gd7pgj"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "39aae2f5-e536-4c1e-bf24-3ac5cd94fdc8",\n            "postId": "9deb8571-c23e-4b0e-b988-40a29a1d67dd",\n            "price": 10,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Automation",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "{{shippingAddressId}}",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 5: get consumer order detail
    _resp5 = ctx.api.orders.consumer_detail_by_order_number()
    ctx.extract('numberCode', _resp5, '$.data.lineItems[0].orderLineItemUnits[0].numberCode')
    # step 6: Login-M1
    _resp6 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp6, '$.data.token')
    # step 7: get M1 order detail v2
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantID8c}}'})
