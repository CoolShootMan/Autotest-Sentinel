"""Auto-generated from Apifox case #7551337. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7551337
# Folder: 
# Case: (Lury)T4172_From_HUI_Verify_the_transaction_fee_is_correct_with_different_listing_type_and_commission_mode
# Priority: P0
# Created: 2025-11-21T07:46:41.000Z
# Updated: 2026-07-21T07:23:41.000Z


CASE_ID = 7551337
ENV_NAME = "Release"

# --- step 1: Consumer-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity,type){
# pre:     unit_fixed_fee = 0;
# pre:     item_percentage_fee = 0.085;
# pre:     unit_fixed_fee_ticket = 1;
# pre:     item_percentage_fee_ticket = 0.1;
# pre:     if (type === "ticket"){
# pre:         return (unit_fixed_fee_ticket + unit_price * item_percentage_fee_ticket) * quantity
# pre:     }
# pre:     else{
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre: }
# pre: var order_level_transaction_fee = Math.floor((4.99 * 0.085)*100)/100;
# pre: var transaction_fee_item1_level = Math.floor(get_transaction_fee_item_level_general(15,2)*100)/100;
# pre: var transaction_fee_item2_level = Math.floor(get_transaction_fee_item_level_general(35,1)*100)/100;
# pre: var transaction_fee_item3_level = Math.floor(get_transaction_fee_item_level_general(23,3,"ticket")*100)/100;
# pre: var transaction_fee_item4_level = Math.floor(get_transaction_fee_item_level_general(12,4,"ticket")*100)/100;
# pre: var p1_transaction_fee_item1 = Math.round(((0.1 * transaction_fee_item1_level) + Number.EPSILON) *100 ) / 100;
# pre: var p1_transaction_fee_item2 = Math.round(((0.1 * transaction_fee_item2_level) + Number.EPSILON) *100 ) / 100;
# pre: var p1_transaction_fee_item3 = Math.round(((0.1 * transaction_fee_item3_level) + Number.EPSILON) *100 ) / 100;
# pre: var p1_transaction_fee_item4 = Math.round(((0.1 * transaction_fee_item4_level) + Number.EPSILON) *100 ) / 100;
# pre: var p1_transaction_fee = p1_transaction_fee_item2 + p1_transaction_fee_item3 + p1_transaction_fee_item4;
# pre: var merchant_transaction_fee_item1 = Math.round(((0.2 * transaction_fee_item1_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee_item2 = Math.round(((0.2 * transaction_fee_item2_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee_item3 = Math.round(((0.2 * transaction_fee_item3_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee_item4 = Math.round(((0.2 * transaction_fee_item4_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee = merchant_transaction_fee_item2 + merchant_transaction_fee_item3 + merchant_transaction_fee_item4;
# pre: var m1_transaction_fee_item1 = Number((transaction_fee_item1_level - p1_transaction_fee_item1 - merchant_transaction_fee_item1).toFixed(2));
# pre: var m1_transaction_fee_item2 = Number((transaction_fee_item2_level - p1_transaction_fee_item2 - merchant_transaction_fee_item2).toFixed(2));
# pre: var m1_transaction_fee_item3 = Number((transaction_fee_item3_level - p1_transaction_fee_item3 - merchant_transaction_fee_item3).toFixed(2));
# pre: var m1_transaction_fee_item4 = Number((transaction_fee_item4_level - p1_transaction_fee_item4 - merchant_transaction_fee_item4).toFixed(2));
# pre: var m1_transaction_fee = Number((transaction_fee_item1_level + m1_transaction_fee_item2 + order_level_transaction_fee).toFixed(2));
# pre: var m1_transaction_fee_ticket = m1_transaction_fee_item3 + m1_transaction_fee_item4
# pre: 
# pre: 
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("m1_transaction_fee_ticket", m1_transaction_fee_ticket);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: 
# pre: console.log(merchant_transaction_fee_item1)
# pre: console.log(merchant_transaction_fee_item2)
# pre: console.log(merchant_transaction_fee_item3)
# pre: console.log(merchant_transaction_fee_item4)
# pre: console.log(p1_transaction_fee_item1)
# pre: console.log(p1_transaction_fee_item2)
# pre: console.log(p1_transaction_fee_item3)
# pre: console.log(p1_transaction_fee_item4)
# pre: console.log(m1_transaction_fee_item1)
# pre: console.log(m1_transaction_fee_item2)
# pre: console.log(m1_transaction_fee_item3)
# pre: console.log(m1_transaction_fee_item4)
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     var token = res['data']['token'];
# post:     pm.environment.set("consumer_access_token",token);
# post:     console.log(token)
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
# post:     pm.expect(res['data']['totalTopay']).to.eql(186.99);
# post: });
# --- step 5: get consumer order detail ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var line_items = res["data"]["lineItems"]
# post:     for (var line of line_items){
# post:         if (line["unitPrice"] == 12){
# post:             var lineItemId_12 = line['id'];
# post:         }
# post:         else if (line["unitPrice"] == 35){
# post:             var lineItemId_35 = line['id'];
# post:         }
# post:         else if (line["unitPrice"] == 23){
# post:             var lineItemId_23 = line['id'];
# post:         }
# post:         else if (line["unitPrice"] == 15){
# post:             var lineItemId_15 = line['id'];
# post:         }
# post:     }
# post:     pm.environment.set("lineItemId_12",lineItemId_12);
# post:     pm.environment.set("lineItemId_35",lineItemId_35);
# post:     pm.environment.set("lineItemId_23",lineItemId_23);
# post:     pm.environment.set("lineItemId_15",lineItemId_15);
# post: 
# post: 
# post: });
# --- step 6: 67559ad7-dd02-4b05-b22a-b365f63b1e15 ---
# post[customScript]:     if(pm.response.to.have.status(201)){
# post:         var res = JSON.parse(responseBody);
# post:         pm.environment.set("admin_access_token",res['data']['token']);
# post:     }
# --- step 7: d081cd68-8e3f-4e66-a5b9-48332b153b85 ---
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
# post:     }
# post:     pm.environment.set("admin_orderId",admin_orderId);
# post:     pm.environment.set("merchantOrderId",merchantOrderId);
# post: });
# post: 
# --- step 8: 3bc6a2cb-94cc-406f-b258-7b93e5e215b1 ---
# post[customScript]: pm.test("Status code is 201", function () {
# post:     pm.response.to.have.status(201);
# post: });
# --- step 9: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post:     M1_access_token = res['data']['token'];
# post:     console.log(M1_access_token)
# post: });
# --- step 10: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_transaction_fee_ticket = pm.environment.get("m1_transaction_fee_ticket");
# post:     var total_payout = Number((60.9 - m1_transaction_fee_ticket + data["transactionFeeRebate"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee_ticket);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(81.9);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(21);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(60.9);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(11.8);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "c2435065-b42a-4637-a64b-0220189b4220"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(69);
# post:             pm.expect(line_item["retailPrice"]).to.eql(69);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(69);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(20.7);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(69);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(48.3);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(21);
# post:             pm.expect(line_item["commissionNet"]).to.eql(27.3);          
# post:             pm.expect(line_item["quantity"]).to.eql(3);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(3);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(30);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");}
# post:         else if (line_item["variantInfo"]["id"] === "6f18bd7f-b51f-4eff-accd-78b3df1facb6"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(48);
# post:             pm.expect(line_item["retailPrice"]).to.eql(48);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(48);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(14.4);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(48);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(33.6);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(33.6);          
# post:             pm.expect(line_item["quantity"]).to.eql(4);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(4);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");}
# post:             else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post: 
# post:     }
# post: });
# --- step 11: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var total_payout = Number((24.5 - m1_transaction_fee + 4.99 + data["transactionFeeRebate"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(45.5);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(21);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(24.5);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(4.99);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "30cbbedb-5fa2-400f-93ba-a4dba2ad68cb"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(30);
# post:             pm.expect(line_item["retailPrice"]).to.eql(30);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(30);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(9);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(30);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(21);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(21);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(30);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:             }
# post:         else if (line_item["variantInfo"]["id"] === "759dffb4-2dfa-4ec8-a22b-c69b254c0dc5"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(35);
# post:             pm.expect(line_item["retailPrice"]).to.eql(35);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(35);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(10.5);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(35);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(24.5);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(24.5);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");}
# post:             else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post: 
# post:     }
# post: });
# --- step 12: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 13: get P1 orders ---
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
# post:     console.log(curatorOrderId)
# post: });
# --- step 14: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var total_payout = Number((12.2 - p1_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(p1_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(18.2);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(6);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(12.2);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "30cbbedb-5fa2-400f-93ba-a4dba2ad68cb"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(30);
# post:             pm.expect(line_item["retailPrice"]).to.eql(30);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionGross"]).to.eql(9);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(6);
# post:             pm.expect(line_item["costPrice"]).to.eql(21);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(30);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(3);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(3);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(30);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:             }
# post:         else if (line_item["variantInfo"]["id"] === "c2435065-b42a-4637-a64b-0220189b4220"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(69);
# post:             pm.expect(line_item["retailPrice"]).to.eql(69);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionGross"]).to.eql(20.7);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(13.8);
# post:             pm.expect(line_item["costPrice"]).to.eql(48.3);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(69);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(6.9);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(3);
# post:             pm.expect(line_item["commissionNet"]).to.eql(3.9);          
# post:             pm.expect(line_item["quantity"]).to.eql(3);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(3);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(30);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");}
# post:         else if (line_item["variantInfo"]["id"] === "759dffb4-2dfa-4ec8-a22b-c69b254c0dc5"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(35);
# post:             pm.expect(line_item["retailPrice"]).to.eql(35);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionGross"]).to.eql(10.5);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(7);
# post:             pm.expect(line_item["costPrice"]).to.eql(24.5);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(35);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(3.5);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(3.5);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");}
# post:         else if (line_item["variantInfo"]["id"] === "6f18bd7f-b51f-4eff-accd-78b3df1facb6"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(48);
# post:             pm.expect(line_item["retailPrice"]).to.eql(48);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(30);
# post:             pm.expect(line_item["commissionGross"]).to.eql(14.4);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(9.6);
# post:             pm.expect(line_item["costPrice"]).to.eql(33.6);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(48);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(4.8);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(4.8);          
# post:             pm.expect(line_item["quantity"]).to.eql(4);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(4);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");}
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });
# post: 
# --- step 15: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 16: get merchant orders ---
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
# --- step 17: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var total_payout = Number((24.4 - merchant_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(merchant_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(36.4);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(12);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(24.4);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "30cbbedb-5fa2-400f-93ba-a4dba2ad68cb"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(30);
# post:             pm.expect(line_item["retailPrice"]).to.eql(30);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionGross"]).to.eql(6);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(24);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(30);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(6);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(6);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(30);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:             }
# post:         else if (line_item["variantInfo"]["id"] === "c2435065-b42a-4637-a64b-0220189b4220"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(69);
# post:             pm.expect(line_item["retailPrice"]).to.eql(69);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionGross"]).to.eql(13.8);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(55.2);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(69);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(13.8);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(6);
# post:             pm.expect(line_item["commissionNet"]).to.eql(7.8);          
# post:             pm.expect(line_item["quantity"]).to.eql(3);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(3);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(30);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");}
# post:         else if (line_item["variantInfo"]["id"] === "759dffb4-2dfa-4ec8-a22b-c69b254c0dc5"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(35);
# post:             pm.expect(line_item["retailPrice"]).to.eql(35);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionGross"]).to.eql(7);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(28);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(35);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(7);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(7);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");}
# post:         else if (line_item["variantInfo"]["id"] === "6f18bd7f-b51f-4eff-accd-78b3df1facb6"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(48);
# post:             pm.expect(line_item["retailPrice"]).to.eql(48);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(20);
# post:             pm.expect(line_item["commissionGross"]).to.eql(9.6);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(38.4);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(48);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(9.6);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(9.6);          
# post:             pm.expect(line_item["quantity"]).to.eql(4);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(4);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");}
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });





from core.assertions import expect

def test__7551337__Lury_T4172_From_HUI_Verify_the_transaction_fee_is_correct_with_different_listing_type_and_commission_mode(ctx):
    """Apifox case #7551337: Lury_T4172_From_HUI_Verify_the_transaction_fee_is_correct_with_different_listing"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['m1_transaction_fee'] = 'm1_transaction_fee'
    vars['m1_transaction_fee_ticket'] = 'm1_transaction_fee_ticket'
    vars['p1_transaction_fee'] = 'p1_transaction_fee'
    vars['merchant_transaction_fee'] = 'merchant_transaction_fee'
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    vars['consumer_access_token'] = 'token'
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete(token='consumer_access_token')
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "759dffb4-2dfa-4ec8-a22b-c69b254c0dc5",\n            "price": 35,\n            "postId": "e8c02c4a-6b51-4d5c-86ad-615fe64c106c",\n            "selected": true,\n            "customFields": []\n        },\n        {\n            "quantity": 3,\n            "promoterProductVariantId": "c2435065-b42a-4637-a64b-0220189b4220",\n            "price": 23,\n            "postId": "e8c02c4a-6b51-4d5c-86ad-615fe64c106c",\n            "selected": true,\n            "customFields": []\n        },\n        {\n            "quantity": 4,\n            "promoterProductVariantId": "d3141a58-9d3e-4fc7-829d-f1443c2aad6f",\n            "price": 12,\n            "postId": "e8c02c4a-6b51-4d5c-86ad-615fe64c106c",\n            "selected": true,\n            "customFields": []\n        },\n        {\n            "quantity": 2,\n            "promoterProductVariantId": "30cbbedb-5fa2-400f-93ba-a4dba2ad68cb",\n            "price": 15,\n            "postId": "e8c02c4a-6b51-4d5c-86ad-615fe64c106c",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "8fa8e671-758f-4568-840e-087c90d6e0fb",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",\n        "eventSourceUrl": "https://release.pear.us/auto-promoter/post/grlb54"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "759dffb4-2dfa-4ec8-a22b-c69b254c0dc5",\n            "postId": "e8c02c4a-6b51-4d5c-86ad-615fe64c106c",\n            "price": 35,\n            "customFields": []\n        },\n        {\n            "quantity": 3,\n            "id": "c2435065-b42a-4637-a64b-0220189b4220",\n            "postId": "e8c02c4a-6b51-4d5c-86ad-615fe64c106c",\n            "price": 69,\n            "customFields": []\n        },\n        {\n            "quantity": 4,\n            "id": "d3141a58-9d3e-4fc7-829d-f1443c2aad6f",\n            "postId": "e8c02c4a-6b51-4d5c-86ad-615fe64c106c",\n            "price": 48,\n            "customFields": []\n        },\n        {\n            "quantity": 2,\n            "id": "30cbbedb-5fa2-400f-93ba-a4dba2ad68cb",\n            "postId": "e8c02c4a-6b51-4d5c-86ad-615fe64c106c",\n            "price": 30,\n            "customFields": []\n        }\n    ]\n}', token='consumer_access_token')
    vars['orderNumber'] = 'orderNumber'
    vars['orderId'] = 'orderId'
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Automation",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}', token='consumer_access_token')
    # step 5: get consumer order detail
    _resp5 = ctx.api.orders.consumer_detail_by_order_number(token='consumer_access_token')
    vars['lineItemId_12'] = 'lineItemId_12'
    vars['lineItemId_35'] = 'lineItemId_35'
    vars['lineItemId_23'] = 'lineItemId_23'
    vars['lineItemId_15'] = 'lineItemId_15'
    # step 6: 67559ad7-dd02-4b05-b22a-b365f63b1e15
    _resp6 = ctx.api.admin.auth_login(body='{"email":"dian.yuhong.ext@1m.app","password":"Lastd!y8"}')
    ctx.extract('admin_access_token', _resp6, '$.data.token')
    # step 7: d081cd68-8e3f-4e66-a5b9-48332b153b85
    _resp7 = ctx.api.admin.orders_search(body='{\n    "query": "{{orderNumber}}",\n    "includePartnerTesting": true,\n    "pageSize": 50,\n    "pageNumber": 1\n}', token='admin_access_token')
    vars['admin_orderId'] = 'admin_orderId'
    vars['merchantOrderId'] = 'merchantOrderId'
    # step 8: 3bc6a2cb-94cc-406f-b258-7b93e5e215b1
    _resp8 = ctx.api.admin.orders_refunds(body='{\n    "lineItems": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId_23}}",\n            "itemAmount": 30,\n            "taxAmount": 0,\n            "totalAmount": 30,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId_23}}",\n                "refundableItem": 69,\n                "refundableTax": 0,\n                "totalRefundable": 69,\n                "refundableQuantity": 3\n            },\n            "changedFields": []\n        },\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId_15}}",\n            "itemAmount": 30,\n            "taxAmount": 0,\n            "totalAmount": 30,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId_15}}",\n                "refundableItem": 30,\n                "refundableTax": 0,\n                "totalRefundable": 30,\n                "refundableQuantity": 2\n            },\n            "changedFields": []\n        },\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId_35}}",\n            "itemAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId_35}}",\n                "refundableItem": 35,\n                "refundableTax": 0,\n                "totalRefundable": 35,\n                "refundableQuantity": 1\n            },\n            "changedFields": []\n        },\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId_12}}",\n            "itemAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId_12}}",\n                "refundableItem": 48,\n                "refundableTax": 0,\n                "totalRefundable": 48,\n                "refundableQuantity": 4\n            },\n            "changedFields": []\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "shippingAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "refundableShipping": 4.99,\n                "refundableShippingTax": 0,\n                "totalRefundable": 4.99\n            }\n        }\n    ],\n    "refundTotals": {\n        "totalItemsRefund": 60,\n        "totalItemsQuantityRefund": 0,\n        "totalShippingRefund": 0,\n        "totalItemsTaxRefund": 0,\n        "totalShippingTaxRefund": 0,\n        "totalTaxRefund": 0,\n        "totalRefund": 60\n    },\n    "transactions": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "totalRefund": 60,\n            "totalRefundable": 186.99,\n            "changedFields": []\n        }\n    ]\n}', token='admin_access_token')
    # step 9: Login-M1
    _resp9 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp9, '$.data.token')
    # step 10: get M1 order detail v2
    _resp10 = ctx.api.orders.merchant_detail_v2(token='M1_access_token', path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # step 11: get M1 order detail v2
    _resp11 = ctx.api.orders.merchant_detail_v2(token='M1_access_token', path_vars={'merchantId': '{{M1_merchantIe6}}'})
    # step 12: Login - P1
    _resp12 = ctx.api.auth.sign_in(body='{\n    "password": "{{P1_password}}",\n    "email": "{{P1}}"\n}')
    ctx.extract('P1_access_token', _resp12, '$.data.token')
    # step 13: get P1 orders
    _resp13 = ctx.api.orders.promoter(token='P1_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['P1_OrderId'] = 'curatorOrderId'
    # step 14: get P1 order detail v2
    _resp14 = ctx.api.orders.promoter_detail_v2(token='P1_access_token', path_vars={'merchantOrderId': '{{P1_OrderId}}'})
    # step 15: Login - merchant
    _resp15 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp15, '$.data.token')
    # step 16: get merchant orders
    _resp16 = ctx.api.orders.promoter(token='merchant_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 17: get merhcant order detail v2
    _resp17 = ctx.api.orders.promoter_detail_v2(token='merchant_access_token')
