"""Auto-generated from Apifox case #7541878. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7541878
# Folder: 
# Case: (Lury)T6429_Check_earnings_for_all_users_after_partial_and_full_refund_on_admin_tool
# Priority: P0
# Created: 2025-11-20T03:28:08.000Z
# Updated: 2026-08-24T04:06:53.000Z


CASE_ID = 7541878
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
# post:     pm.expect(res['data']['totalTopay']).to.eql(90.49);
# post: });
# --- step 6: 70886c17-f39b-4ebd-83b1-dcc7280b8345 ---
# post[customScript]:     if(pm.response.to.have.status(201)){
# post:         var res = JSON.parse(responseBody);
# post:         pm.environment.set("admin_access_token",res['data']['token']);
# post:     }
# --- step 7: 3b0570e7-6822-4518-932c-dbbb83b9fd8c ---
# post[customScript]: pm.test("Get merchant order ID", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     var order_list = res["data"]["items"]
# post:     var orderNumber = pm.environment.get("orderNumber");
# post:     for (var order of order_list){
# post:         if (order['orderNumber'] === orderNumber){
# post:             var admin_orderId = order['id'];
# post:             var merchantOrderId = order['merchantOrderId'];
# post:         }
# post:         else{
# post:             console.log("Cannot find the order on admin tool.")
# post:         }
# post:     }
# post:     pm.environment.set("admin_orderId",admin_orderId);
# post:     pm.environment.set("merchantOrderId",merchantOrderId);
# post:     console.log(admin_orderId);
# post:     console.log(merchantOrderId)
# post: });
# post: 
# --- step 8: 9eb3d1e9-e022-4250-9496-1b7dbdf3f3ed ---
# post[customScript]: pm.test("Status code is 201", function () {
# post:     pm.response.to.have.status(201);
# post: });
# --- step 9: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 10: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var total_payout = Number((16.6 - m1_transaction_fee + 4.99).toFixed(2));
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(40);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(23.4);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(16.6);
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(4.99);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: });
# --- step 11: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 12: get P1 orders ---
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
# --- step 13: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var total_payout = Number((4.15 - p1_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(10);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(5.85);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(4.15);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(p1_transaction_fee);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(5.85);
# post:             pm.expect(line_item["commissionNet"]).to.eql(4.15);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(58.48);
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
# --- step 14: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 15: get merchant orders ---
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
# --- step 16: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var total_payout = Number((5.4 - merchant_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(13);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(7.6);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(5.4);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(merchant_transaction_fee);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(7.6);
# post:             pm.expect(line_item["commissionNet"]).to.eql(5.4);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(52.63);
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
# --- step 17: Login - curator ---
# post[customScript]: pm.test("Check curator login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("curator_access_token",res['data']['token']);
# post: });
# --- step 18: get curator orders ---
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
# --- step 19: get curator order detail v2 ---
# post[customScript]: pm.test("Check curator earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var curator_transaction_fee = pm.environment.get("curator_transaction_fee");
# post:     var total_payout = Number((3.74 - curator_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(9);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(5.26);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(3.74);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(curator_transaction_fee);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(5.26);
# post:             pm.expect(line_item["commissionNet"]).to.eql(3.74);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(52.63);
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
# --- step 20: Login - promoter ---
# post[customScript]: pm.test("Check promoter login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("promoter_access_token",res['data']['token']);
# post: });
# --- step 21: get promoter orders ---
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
# --- step 22: get promoter order detail v2 ---
# post[customScript]: pm.test("Check Promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var total_payout = Number((2.06 - promoter_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(4.95);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(2.89);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(2.06);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(promoter_transaction_fee);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(2.89);
# post:             pm.expect(line_item["commissionNet"]).to.eql(2.06);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(50);
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
# --- step 23: Login -P5 ---
# post[customScript]: pm.test("Check P5 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P5_access_token",res['data']['token']);
# post: });
# --- step 24: get P5 orders ---
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
# --- step 25: get P5 order detail v2 ---
# post[customScript]: pm.test("Check P5 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var p5_transaction_fee = pm.environment.get("p5_transaction_fee");
# post:     var total_payout = Number((3.55 - p5_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(8.55);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(5);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(3.55);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(p5_transaction_fee);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(5);
# post:             pm.expect(line_item["commissionNet"]).to.eql(3.55);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(50);
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
# --- step 26: d11758be-1d97-4ae9-82ea-48a845d71972 ---
# post[customScript]: pm.test("Get merchant order ID", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     var order_list = res["data"]["items"]
# post:     var orderNumber = pm.environment.get("orderNumber");
# post:     for (var order of order_list){
# post:         if (order['orderNumber'] === orderNumber){
# post:             var admin_orderId = order['id'];
# post:             var merchantOrderId = order['merchantOrderId'];
# post:         }
# post:         else{
# post:             console.log("Cannot find the order on admin tool.")
# post:         }
# post:     }
# post:     pm.environment.set("admin_orderId",admin_orderId);
# post:     pm.environment.set("merchantOrderId",merchantOrderId);
# post:     console.log(admin_orderId);
# post:     console.log(merchantOrderId)
# post: });
# post: 
# --- step 27: bbcd3ea5-a4ec-4226-b1cd-acf5cbb44d10 ---
# post[customScript]: pm.test("Check total refunded on admin tool after refunded full", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['orderRefund']["totalRefunded"]).to.eql(35.5);
# post:     pm.expect(res['data']['updatedOrder']["totalRefunded"]).to.eql(85.5);
# post: 
# post: });
# --- step 28: ccacd30f-df62-4636-924d-75ee76b3fed6 ---
# post[customScript]: pm.test("Check total refunded on admin tool after refunded full", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post: 
# post: });
# --- step 29: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var curator_transaction_fee = pm.environment.get("curator_transaction_fee");
# post:     var p5_transaction_fee = pm.environment.get("p5_transaction_fee");
# post:     var total_transaction_fee = Number((m1_transaction_fee + p1_transaction_fee + merchant_transaction_fee + promoter_transaction_fee + curator_transaction_fee + p5_transaction_fee).toFixed(2));
# post:     var total_payout = Number((0 - total_transaction_fee).toFixed(2));
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(40);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(40);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(0);
# post:     pm.expect(data["transactionFee"]).to.eql(total_transaction_fee);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(4.99);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: });
# --- step 30: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(10);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(10);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(0);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(0);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(10);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(100);
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
# --- step 31: get merchant orders ---
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
# --- step 32: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(13);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(13);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(0);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(0);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(13);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(90);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: });
# --- step 33: get curator order detail v2 ---
# post[customScript]: pm.test("Check curator earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(9);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(9);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(0);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(0);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(9);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(90);
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
# --- step 34: get promoter order detail v2 ---
# post[customScript]: pm.test("Check Promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(4.95);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(4.95);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(0);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(0);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(4.95);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(85.5);
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
# --- step 35: get P5 order detail v2 ---
# post[customScript]: pm.test("Check P5 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(8.55);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(8.55);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(0);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(0);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
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
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(8.55);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(85.5);
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





from core.assertions import expect

def test__7541878__Lury_T6429_Check_earnings_for_all_users_after_partial_and_full_refund_on_admin_tool(ctx):
    """Apifox case #7541878: Lury_T6429_Check_earnings_for_all_users_after_partial_and_full_refund_on_admin_t"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['m1_transaction_fee'] = 'm1_transaction_fee'
    vars['p1_transaction_fee'] = 'p1_transaction_fee'
    vars['merchant_transaction_fee'] = 'merchant_transaction_fee'
    vars['curator_transaction_fee'] = 'curator_transaction_fee'
    vars['promoter_transaction_fee'] = 'promoter_transaction_fee'
    vars['p5_transaction_fee'] = 'p5_transaction_fee'
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.token')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete(token='consumer_access_token')
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "e42ccfbd-0b24-44cc-808c-725469132854",\n            "price": 100,\n            "postId": "e775b9ee-91d6-4315-b7f1-b08f80966bb0",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "cf3c1ecd-999f-4bd3-9bbd-b2af300fd8d3",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "3151d61c-1a69-48a2-9b44-e9f55542fe12",\n        "eventSourceUrl": "https://release.pear.us/luryp4/post/k6amjl?source=pear"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "e42ccfbd-0b24-44cc-808c-725469132854",\n            "postId": "e775b9ee-91d6-4315-b7f1-b08f80966bb0",\n            "price": 100,\n            "customFields": []\n        }\n    ]\n}', token='consumer_access_token')
    vars['orderNumber'] = 'orderNumber'
    vars['orderId'] = 'orderId'
    # step 4: apply promotion
    _resp4 = ctx.api.orders.update_promotions(body='{\n    "shippingAddress": {\n        "line1": "Fort Collins Municipal Railway",\n        "city": "Fort Collins",\n        "zipcode": "80521",\n        "state": "CO"\n    },\n    "applicableCode": "manual5",\n    "orderId": "{{orderId}}"\n}', token='consumer_access_token')
    vars['lineItemId'] = 'lineItemId'
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Real",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}', token='consumer_access_token')
    # step 6: 70886c17-f39b-4ebd-83b1-dcc7280b8345
    _resp6 = ctx.api.admin.auth_login(body='{"email":"dian.yuhong.ext@1m.app","password":"Lastd!y8"}')
    ctx.extract('admin_access_token', _resp6, '$.data.token')
    # step 7: 3b0570e7-6822-4518-932c-dbbb83b9fd8c
    _resp7 = ctx.api.admin.orders_search(body='{"query":"{{orderNumber}}","startTime":null,"endTime":null,"includePartnerTesting":true,"free":false,"pageSize":50,"pageNumber":1}', token='admin_access_token')
    vars['admin_orderId'] = 'admin_orderId'
    vars['merchantOrderId'] = 'merchantOrderId'
    # step 8: 9eb3d1e9-e022-4250-9496-1b7dbdf3f3ed
    _resp8 = ctx.api.admin.orders_refunds(body='{\n    "lineItems": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId}}",\n            "itemAmount": 50,\n            "taxAmount": 0,\n            "totalAmount": 50,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId}}",\n                "refundableItem": 85.5,\n                "refundableTax": 0,\n                "totalRefundable": 85.5,\n                "refundableQuantity": 1\n            },\n            "changedFields": []\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "shippingAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "refundableShipping": 4.99,\n                "refundableShippingTax": 0,\n                "totalRefundable": 4.99\n            }\n        }\n    ],\n    "refundTotals": {\n        "totalItemsRefund": 50,\n        "totalItemsQuantityRefund": 0,\n        "totalShippingRefund": 0,\n        "totalItemsTaxRefund": 0,\n        "totalShippingTaxRefund": 0,\n        "totalTaxRefund": 0,\n        "totalRefund": 50\n    },\n    "transactions": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "totalRefund": 50,\n            "totalRefundable": 90.49,\n            "changedFields": []\n        }\n    ]\n}', token='admin_access_token')
    # step 9: Login-M1
    _resp9 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp9, '$.data.token')
    # step 10: get M1 order detail v2
    _resp10 = ctx.api.orders.merchant_detail_v2(token='M1_access_token', path_vars={'merchantId': '{{merchantId8}}'})
    # step 11: Login - P1
    _resp11 = ctx.api.auth.sign_in(body='{\n    "password": "{{P1_password}}",\n    "email": "{{P1}}"\n}')
    ctx.extract('P1_access_token', _resp11, '$.data.token')
    # step 12: get P1 orders
    _resp12 = ctx.api.orders.promoter(token='P1_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['P1_OrderId'] = 'curatorOrderId'
    # step 13: get P1 order detail v2
    _resp13 = ctx.api.orders.promoter_detail_v2(token='P1_access_token', path_vars={'merchantOrderId': '{{P1_OrderId}}'})
    # step 14: Login - merchant
    _resp14 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp14, '$.data.token')
    # step 15: get merchant orders
    _resp15 = ctx.api.orders.promoter(token='merchant_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 16: get merhcant order detail v2
    _resp16 = ctx.api.orders.promoter_detail_v2(token='merchant_access_token')
    # step 17: Login - curator
    _resp17 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{curator_email}}"\n}')
    ctx.extract('curator_access_token', _resp17, '$.data.token')
    # step 18: get curator orders
    _resp18 = ctx.api.orders.promoter(token='curator_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['curatorOrderId'] = 'curatorOrderId'
    # step 19: get curator order detail v2
    _resp19 = ctx.api.orders.promoter_detail_v2(token='curator_access_token', path_vars={'merchantOrderId': '{{curatorOrderId}}'})
    # step 20: Login - promoter
    _resp20 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{promoter_email}}"\n}')
    ctx.extract('promoter_access_token', _resp20, '$.data.token')
    # step 21: get promoter orders
    _resp21 = ctx.api.orders.promoter(token='promoter_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['promoterOrderId'] = 'promoterOrderId'
    # step 22: get promoter order detail v2
    _resp22 = ctx.api.orders.promoter_detail_v2(token='promoter_access_token', path_vars={'merchantOrderId': '{{promoterOrderId}}'})
    # step 23: Login -P5
    _resp23 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{P5}}"\n}')
    ctx.extract('P5_access_token', _resp23, '$.data.token')
    # step 24: get P5 orders
    _resp24 = ctx.api.orders.promoter(token='P5_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['P5_OrderId'] = 'curatorOrderId'
    # step 25: get P5 order detail v2
    _resp25 = ctx.api.orders.promoter_detail_v2(token='P5_access_token', path_vars={'merchantOrderId': '{{P5_OrderId}}'})
    # step 26: d11758be-1d97-4ae9-82ea-48a845d71972
    _resp26 = ctx.api.admin.orders_search(body='{"query":"{{orderNumber}}","startTime":null,"endTime":null,"includePartnerTesting":true,"free":false,"pageSize":50,"pageNumber":1}', token='admin_access_token')
    vars['admin_orderId'] = 'admin_orderId'
    vars['merchantOrderId'] = 'merchantOrderId'
    # step 27: bbcd3ea5-a4ec-4226-b1cd-acf5cbb44d10
    _resp27 = ctx.api.admin.orders_refunds(body='{\n    "lineItems": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId}}",\n            "itemAmount": 35.5,\n            "taxAmount": 0,\n            "totalAmount": 35.5,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId}}",\n                "refundableItem": 35.5,\n                "refundableTax": 0,\n                "totalRefundable": 35.5,\n                "refundableQuantity": 1\n            },\n            "changedFields": []\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "shippingAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "refundableShipping": 4.99,\n                "refundableShippingTax": 0,\n                "totalRefundable": 4.99\n            }\n        }\n    ],\n    "refundTotals": {\n        "totalItemsRefund": 35.5,\n        "totalItemsQuantityRefund": 0,\n        "totalShippingRefund": 0,\n        "totalItemsTaxRefund": 0,\n        "totalShippingTaxRefund": 0,\n        "totalTaxRefund": 0,\n        "totalRefund": 35.5\n    },\n    "transactions": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "totalRefund": 35.5,\n            "totalRefundable": 40.49,\n            "changedFields": []\n        }\n    ]\n}', token='admin_access_token')
    # step 28: ccacd30f-df62-4636-924d-75ee76b3fed6
    _resp28 = ctx.api.admin.orders_refunds(body='{\n    "lineItems": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId}}",\n            "itemAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId}}",\n                "refundableItem": 0,\n                "refundableTax": 0,\n                "totalRefundable": 0,\n                "refundableQuantity": 1,\n                "initialRefundableItem": 85.5,\n                "refundedItem": 85.5,\n                "initialRefundableQuantity": 1,\n                "refundedQuantity": 0\n            },\n            "changedFields": []\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "shippingAmount": 4.99,\n            "taxAmount": 0,\n            "totalAmount": 4.99,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "refundableShipping": 4.99,\n                "refundableShippingTax": 0,\n                "totalRefundable": 4.99\n            }\n        }\n    ],\n    "refundTotals": {\n        "totalItemsRefund": 0,\n        "totalItemsQuantityRefund": 0,\n        "totalShippingRefund": 4.99,\n        "totalItemsTaxRefund": 0,\n        "totalShippingTaxRefund": 0,\n        "totalTaxRefund": 0,\n        "totalRefund": 4.99\n    },\n    "transactions": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "totalRefund": 4.99,\n            "totalRefundable": 4.99,\n            "changedFields": []\n        }\n    ]\n}', token='admin_access_token')
    # step 29: get M1 order detail v2
    _resp29 = ctx.api.orders.merchant_detail_v2(token='M1_access_token', path_vars={'merchantId': '{{merchantId8}}'})
    # step 30: get P1 order detail v2
    _resp30 = ctx.api.orders.promoter_detail_v2(token='P1_access_token', path_vars={'merchantOrderId': '{{P1_OrderId}}'})
    # step 31: get merchant orders
    _resp31 = ctx.api.orders.promoter(token='merchant_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 32: get merhcant order detail v2
    _resp32 = ctx.api.orders.promoter_detail_v2(token='merchant_access_token')
    # step 33: get curator order detail v2
    _resp33 = ctx.api.orders.promoter_detail_v2(token='curator_access_token', path_vars={'merchantOrderId': '{{curatorOrderId}}'})
    # step 34: get promoter order detail v2
    _resp34 = ctx.api.orders.promoter_detail_v2(token='promoter_access_token', path_vars={'merchantOrderId': '{{promoterOrderId}}'})
    # step 35: get P5 order detail v2
    _resp35 = ctx.api.orders.promoter_detail_v2(token='P5_access_token', path_vars={'merchantOrderId': '{{P5_OrderId}}'})
