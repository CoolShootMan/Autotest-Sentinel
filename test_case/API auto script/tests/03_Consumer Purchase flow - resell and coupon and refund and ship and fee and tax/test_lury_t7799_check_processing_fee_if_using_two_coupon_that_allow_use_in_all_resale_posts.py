"""Migrated from Apifox case #7542529. Source folder: Consumer Purchase flow - resell and coupon and refund and ship and fee and tax."""
# Apifox Case ID: 7542529  (traceability only — not needed to run)
NAME = "_Check_processing_fee_if_using_two_coupon_that_allow_use_in_all_resale_posts"
TAGS = ["p0", "consumer_purchase_flow_resell_and_coupon_and_refund_and_ship_and_fee_and_tax", "suite:lury"]
PRIORITY = 0


CASE_ID = 7542529
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
# pre: var order_level_transaction_fee = Math.floor((4.99 * 0.085)*100)/100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(85.5,1)*100)/100;
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
# post:     pm.expect(res['data']['totalDiscount']).to.eql(14.5);
# post: });
# --- step 5: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(90.49);
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
# post:     var total_payout = Number((40 - m1_transaction_fee + 4.99).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(40);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(40);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(4.99);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: });
# --- step 8: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 9: get P1 orders ---
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
# --- step 10: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var total_payout = Number((10 - p1_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(p1_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(10);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(10);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "e42ccfbd-0b24-44cc-808c-725469132854"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(100);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(60);
# post:             pm.expect(line_item["commissionGross"]).to.eql(60);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(50);
# post:             pm.expect(line_item["costPrice"]).to.eql(40);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(100);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(50);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(10);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(10);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
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
# --- step 11: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 12: get merchant orders ---
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
# post:     pm.environment.set("merchantOrderId",curatorOrderId);
# post: });
# --- step 13: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var total_payout = Number((13 - merchant_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(merchant_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(13);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(13);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "e42ccfbd-0b24-44cc-808c-725469132854"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(100);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(10);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(10);
# post:             pm.expect(line_item["commissionRate"]).to.eql(50);
# post:             pm.expect(line_item["commissionGross"]).to.eql(50);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(27);
# post:             pm.expect(line_item["costPrice"]).to.eql(50);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(90);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(13);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(13);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
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
# --- step 14: Login - curator ---
# post[customScript]: pm.test("Check curator login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("curator_access_token",res['data']['token']);
# post: });
# --- step 15: get curator orders ---
# post[customScript]: pm.test("Get curator order ID", function () {
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
# post:     pm.environment.set("curatorOrderId",curatorOrderId);
# post: });
# --- step 16: get curator order detail v2 ---
# post[customScript]: pm.test("Check curator earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var curator_transaction_fee = pm.environment.get("curator_transaction_fee");
# post:     var total_payout = Number((9 - curator_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(curator_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(9);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(9);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "e42ccfbd-0b24-44cc-808c-725469132854"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(90);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(10);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionGross"]).to.eql(27);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(18);
# post:             pm.expect(line_item["costPrice"]).to.eql(63);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(90);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(9);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(9);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
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
# --- step 17: Login - promoter ---
# post[customScript]: pm.test("Check promoter login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("promoter_access_token",res['data']['token']);
# post: });
# --- step 18: get promoter orders ---
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
# post: });
# --- step 19: get promoter order detail v2 ---
# post[customScript]: pm.test("Check Promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var total_payout = Number((4.95 - promoter_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(promoter_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(4.95);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(4.95);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "e42ccfbd-0b24-44cc-808c-725469132854"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(90);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(10);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(4.5);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(4.5);
# post:             pm.expect(line_item["commissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionGross"]).to.eql(18);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(8.55);
# post:             pm.expect(line_item["costPrice"]).to.eql(72);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(85.5);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(10);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(4.95);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(4.95);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
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
# --- step 20: Login -P5 ---
# post[customScript]: pm.test("Check P5 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P5_access_token",res['data']['token']);
# post: });
# --- step 21: get P5 orders ---
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
# --- step 22: get P5 order detail v2 ---
# post[customScript]: pm.test("Check P5 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var p5_transaction_fee = pm.environment.get("p5_transaction_fee");
# post:     var total_payout = Number((8.55 - p5_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(p5_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(8.55);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(8.55);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "e42ccfbd-0b24-44cc-808c-725469132854"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(85.5);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(14.5);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(10);
# post:             pm.expect(line_item["commissionGross"]).to.eql(8.55);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(76.95);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(85.5);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(8.55);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(8.55);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
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

def test_lury_t7799_check_processing_fee_if_using_two_coupon_that_allow_use_in_all_resale_posts(ctx):
    """Apifox case #7542529: Lury_T7799_Check_processing_fee_if_using_two_coupon_that_allow_use_in_all_resale"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.token')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "e42ccfbd-0b24-44cc-808c-725469132854",\n            "price": 100,\n            "postId": "e775b9ee-91d6-4315-b7f1-b08f80966bb0",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "cf3c1ecd-999f-4bd3-9bbd-b2af300fd8d3",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "3151d61c-1a69-48a2-9b44-e9f55542fe12",\n        "eventSourceUrl": "https://release.pear.us/luryp4/post/k6amjl?source=pear"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "e42ccfbd-0b24-44cc-808c-725469132854",\n            "postId": "e775b9ee-91d6-4315-b7f1-b08f80966bb0",\n            "price": 100,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: apply promotion
    _resp4 = ctx.api.orders.update_promotions(body='{\n    "shippingAddress": {\n        "line1": "Fort Collins Municipal Railway",\n        "city": "Fort Collins",\n        "zipcode": "80521",\n        "state": "CO"\n    },\n    "applicableCode": "manual5",\n    "orderId": "{{orderId}}"\n}')
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
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{merchantId8}}'})
    # step 8: Login - P1
    _resp8 = ctx.api.auth.sign_in(body='{\n    "password": "{{P1_password}}",\n    "email": "{{P1}}"\n}')
    ctx.extract('P1_access_token', _resp8, '$.data.token')
    # step 9: get P1 orders
    _resp9 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    vars['P1_OrderId'] = 'curatorOrderId'
    # step 10: get P1 order detail v2
    _resp10 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{P1_OrderId}}'})
    # step 11: Login - merchant
    _resp11 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp11, '$.data.token')
    # step 12: get merchant orders
    _resp12 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 13: get merhcant order detail v2
    _resp13 = ctx.api.orders.promoter_detail_v2()
    # step 14: Login - curator
    _resp14 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{curator_email}}"\n}')
    ctx.extract('curator_access_token', _resp14, '$.data.token')
    # step 15: get curator orders
    _resp15 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    _j = _resp15.json() if _resp15.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    for _order in _arr:
        if _order.get('orderNumber') == vars.get('orderNumber'):
            vars['curatorOrderId'] = _order.get('id')
    # step 16: get curator order detail v2
    _resp16 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{curatorOrderId}}'})
    # step 17: Login - promoter
    _resp17 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{promoter_email}}"\n}')
    ctx.extract('promoter_access_token', _resp17, '$.data.token')
    # step 18: get promoter orders
    _resp18 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    _j = _resp18.json() if _resp18.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    for _order in _arr:
        if _order.get('orderNumber') == vars.get('orderNumber'):
            vars['promoterOrderId'] = _order.get('id')
    # step 19: get promoter order detail v2
    _resp19 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{promoterOrderId}}'})
    # step 20: Login -P5
    _resp20 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{P5}}"\n}')
    ctx.extract('P5_access_token', _resp20, '$.data.token')
    # step 21: get P5 orders
    _resp21 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    vars['P5_OrderId'] = 'curatorOrderId'
    # step 22: get P5 order detail v2
    _resp22 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{P5_OrderId}}'})
