"""Auto-generated from Apifox case #7557782. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7557782
# Folder: 
# Case: (Lury)T4084_Verify_the_commission_charge_and_earnings_for_wholesale_mode_after_partial_refund_the_order
# Priority: P0
# Created: 2025-11-24T08:25:17.000Z
# Updated: 2026-08-11T10:08:54.000Z


CASE_ID = 7557782
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
# pre: var order_level_transaction_fee = Math.floor((5 * 0.085)*100)/100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(100,1)*100)/100;
# pre: var p1_transaction_fee_item = Math.round(((0.75/100 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var promoter_transaction_fee = Math.round(((92.5/100 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var p1_transaction_fee = Number((p1_transaction_fee_item + order_level_transaction_fee).toFixed(2));
# pre: var merchant_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee_item - promoter_transaction_fee).toFixed(2));
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(promoter_transaction_fee)
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
# --- step 4: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(105);
# post: });
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: get consumer order detail ---
# post[extractor]: {"variableName": "lineItemId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].id", "extractSettings": {"expression": "$.data.lineItems[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 7: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 processing fee and earnings", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var total_payout = Number((data["totalCommissionNet"] - p1_transaction_fee + data["totalShippingNet"] + data["totalTaxAmount"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(p1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(0.75);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(0.75);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(5);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(5);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: 
# post: });
# --- step 8: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 9: get merchant orders ---
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
# --- step 10: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - merchant_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(merchant_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(6.75);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(6.75);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "7cd6c140-0203-4e63-badb-f2a581795b06"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(10);
# post:             pm.expect(line_item["retailPrice"]).to.eql(10);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionGross"]).to.eql(9.25);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(2.5);
# post:             pm.expect(line_item["costPrice"]).to.eql(0.75);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(10);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(6.75);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(6.75);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_WHOLESALE");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });
# --- step 11: Login - promoter ---
# post[customScript]: pm.test("Check promoter login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("promoter_access_token",res['data']['token']);
# post: });
# --- step 12: get promoter orders ---
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
# --- step 13: get promoter order detail v2 ---
# post[customScript]: pm.test("Check Promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - promoter_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(promoter_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(92.5);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(92.5);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "7cd6c140-0203-4e63-badb-f2a581795b06"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(100);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionGross"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(7.5);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(100);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(92.5);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_WHOLESALE");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });
# --- step 14: 63114d51-2d8f-4039-87a8-a05239d83ee4 ---
# post[customScript]:     if(pm.response.to.have.status(201)){
# post:         var res = JSON.parse(responseBody);
# post:         pm.environment.set("admin_access_token",res['data']['token']);
# post:     }
# --- step 15: 759bc570-8fd4-4c49-8cdf-ffd29549e658 ---
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
# --- step 16: 69d6faf8-acf5-473f-a9da-810a5db37d4e ---
# post[customScript]: pm.test("Status code is 201", function () {
# post:     pm.response.to.have.status(201);
# post: });
# --- step 17: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 18: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 processing fee and earnings", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var total_payout = Number((data["totalCommissionNet"] - p1_transaction_fee + data["totalShippingNet"] + data["totalTaxAmount"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(p1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(0.75);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0.34);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(0.41);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(5);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(5);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: 
# post: });
# --- step 19: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 20: get merchant orders ---
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
# --- step 21: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - merchant_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(eval(merchant_transaction_fee));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(6.75);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(3.03);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(3.72);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "7cd6c140-0203-4e63-badb-f2a581795b06"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(10);
# post:             pm.expect(line_item["retailPrice"]).to.eql(10);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionGross"]).to.eql(9.25);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(2.5);
# post:             pm.expect(line_item["costPrice"]).to.eql(0.75);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(10);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(6.75);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(3.03);
# post:             pm.expect(line_item["commissionNet"]).to.eql(3.72);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(4.5);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_WHOLESALE");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });
# --- step 22: Login - promoter ---
# post[customScript]: pm.test("Check promoter login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("promoter_access_token",res['data']['token']);
# post: });
# --- step 23: get promoter order detail v2 ---
# post[customScript]: pm.test("Check Promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - promoter_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(promoter_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(92.5);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(41.63);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(50.87);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "7cd6c140-0203-4e63-badb-f2a581795b06"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(100);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionGross"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(7.5);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(100);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(41.63);
# post:             pm.expect(line_item["commissionNet"]).to.eql(50.87);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(45);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_WHOLESALE");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });
# --- step 24: e8a42d09-c5c1-412c-b47c-b914537514a2 ---
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
# --- step 25: e37eecae-6f58-41f5-a8aa-703d5f547015 ---
# post[customScript]: pm.test("Check total refunded on admin tool after refunded full", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['orderRefund']["totalRefunded"]).to.eql(55);
# post:     pm.expect(res['data']['updatedOrder']["totalRefunded"]).to.eql(100);
# post: 
# post: });
# --- step 26: 47705d28-4732-4fb1-b2c4-726148604787 ---
# post[customScript]: pm.test("Check total refunded on admin tool after refunded full", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['orderRefund']["totalRefunded"]).to.eql(5);
# post:     pm.expect(res['data']['updatedOrder']["totalRefunded"]).to.eql(105);
# post: 
# post: });
# --- step 27: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 28: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 processing fee and earnings", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var transaction_fee = p1_transaction_fee + promoter_transaction_fee + merchant_transaction_fee
# post:     var total_payout = Number((data["totalCommissionNet"] - transaction_fee + data["totalShippingNet"] + data["totalTaxAmount"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(transaction_fee );
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(0.75);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0.75);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(0);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(5);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(5);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: 
# post: });
# --- step 29: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 30: get merchant orders ---
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
# --- step 31: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var total_payout = res['data']['totalCommissionNet'];
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(6.75);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(6.75);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(0);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "7cd6c140-0203-4e63-badb-f2a581795b06"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(10);
# post:             pm.expect(line_item["retailPrice"]).to.eql(10);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionGross"]).to.eql(9.25);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(2.5);
# post:             pm.expect(line_item["costPrice"]).to.eql(0.75);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(10);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(6.75);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(6.75);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(10);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_WHOLESALE");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });
# --- step 32: Login - promoter ---
# post[customScript]: pm.test("Check promoter login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("promoter_access_token",res['data']['token']);
# post: });
# --- step 33: get promoter order detail v2 ---
# post[customScript]: pm.test("Check Promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var total_payout = res['data']['totalCommissionNet']
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(92.5);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(92.5);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(0);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "7cd6c140-0203-4e63-badb-f2a581795b06"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(100);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionGross"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(7.5);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(100);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(92.5);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(100);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_WHOLESALE");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });





from core.assertions import expect

def test__7557782__Lury_T4084_Verify_the_commission_charge_and_earnings_for_wholesale_mode_after_partial_refund_the_order(ctx):
    """Apifox case #7557782: Lury_T4084_Verify_the_commission_charge_and_earnings_for_wholesale_mode_after_pa"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['p1_transaction_fee'] = 'p1_transaction_fee'
    vars['promoter_transaction_fee'] = 'promoter_transaction_fee'
    vars['merchant_transaction_fee'] = 'merchant_transaction_fee'
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.token')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete(token='consumer_access_token')
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "7cd6c140-0203-4e63-badb-f2a581795b06",\n            "price": 100,\n            "postId": "dd568e7b-0d2f-41fa-a703-50f73f514c02",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "cf3c1ecd-999f-4bd3-9bbd-b2af300fd8d3",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "3151d61c-1a69-48a2-9b44-e9f55542fe12",\n        "eventSourceUrl": "https://release.pear.us/luryp4/post/k6amjl?source=pear"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "7cd6c140-0203-4e63-badb-f2a581795b06",\n            "postId": "dd568e7b-0d2f-41fa-a703-50f73f514c02",\n            "price": 100,\n            "customFields": []\n        }\n    ]\n}', token='consumer_access_token')
    vars['orderNumber'] = 'orderNumber'
    vars['orderId'] = 'orderId'
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}', token='consumer_access_token')
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp4, '$.data.orderNumbers[0]')
    # step 5: get consumer order detail
    _resp5 = ctx.api.orders.consumer_detail_by_order_number(token='consumer_access_token')
    # extractor: lineItemId = $.data.lineItems[0].id
    ctx.extract('lineItemId', _resp5, '$.data.lineItems[0].id')
    # step 6: Login - P1
    _resp6 = ctx.api.auth.sign_in(body='{\n    "password": "{{P1_password}}",\n    "email": "{{P1}}"\n}')
    ctx.extract('P1_access_token', _resp6, '$.data.token')
    # step 7: get P1 order detail v2
    _resp7 = ctx.api.orders.merchant_bed7b1d8_16d8_4d27_ab1a_dc4a8f19e0c6_detail_v2(token='P1_access_token')
    # step 8: Login - merchant
    _resp8 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp8, '$.data.token')
    # step 9: get merchant orders
    _resp9 = ctx.api.orders.promoter(token='merchant_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 10: get merhcant order detail v2
    _resp10 = ctx.api.orders.promoter_detail_v2(token='merchant_access_token')
    # step 11: Login - promoter
    _resp11 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{promoter_email}}"\n}')
    ctx.extract('promoter_access_token', _resp11, '$.data.token')
    # step 12: get promoter orders
    _resp12 = ctx.api.orders.promoter(token='promoter_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['promoterOrderId'] = 'promoterOrderId'
    # step 13: get promoter order detail v2
    _resp13 = ctx.api.orders.promoter_detail_v2(token='promoter_access_token', path_vars={'merchantOrderId': '{{promoterOrderId}}'})
    # step 14: 63114d51-2d8f-4039-87a8-a05239d83ee4
    _resp14 = ctx.api.admin.auth_login(body='{"email":"dian.yuhong.ext@1m.app","password":"Lastd!y8"}')
    ctx.extract('admin_access_token', _resp14, '$.data.token')
    # step 15: 759bc570-8fd4-4c49-8cdf-ffd29549e658
    _resp15 = ctx.api.admin.orders_search(body='{"query":"{{orderNumber}}","startTime":null,"endTime":null,"includePartnerTesting":true,"free":false,"pageSize":50,"pageNumber":1}', token='admin_access_token')
    vars['admin_orderId'] = 'admin_orderId'
    vars['merchantOrderId'] = 'merchantOrderId'
    # step 16: 69d6faf8-acf5-473f-a9da-810a5db37d4e
    _resp16 = ctx.api.admin.orders_refunds(body='{\n    "lineItems": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId}}",\n            "itemAmount": 45,\n            "taxAmount": 0,\n            "totalAmount": 45,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId}}",\n                "refundableItem": 100,\n                "refundableTax": 0,\n                "totalRefundable": 100,\n                "refundableQuantity": 1\n            },\n            "changedFields": []\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "shippingAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "refundableShipping": 5,\n                "refundableShippingTax": 0,\n                "totalRefundable": 5\n            }\n        }\n    ],\n    "refundTotals": {\n        "totalItemsRefund": 45,\n        "totalItemsQuantityRefund": 0,\n        "totalShippingRefund": 0,\n        "totalItemsTaxRefund": 0,\n        "totalShippingTaxRefund": 0,\n        "totalTaxRefund": 0,\n        "totalRefund": 45\n    },\n    "transactions": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "totalRefund": 45,\n            "totalRefundable": 105,\n            "changedFields": []\n        }\n    ]\n}', token='admin_access_token')
    # step 17: Login - P1
    _resp17 = ctx.api.auth.sign_in(body='{\n    "password": "{{P1_password}}",\n    "email": "{{P1}}"\n}')
    ctx.extract('P1_access_token', _resp17, '$.data.token')
    # step 18: get P1 order detail v2
    _resp18 = ctx.api.orders.merchant_bed7b1d8_16d8_4d27_ab1a_dc4a8f19e0c6_detail_v2(token='P1_access_token')
    # step 19: Login - merchant
    _resp19 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp19, '$.data.token')
    # step 20: get merchant orders
    _resp20 = ctx.api.orders.promoter(token='merchant_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 21: get merhcant order detail v2
    _resp21 = ctx.api.orders.promoter_detail_v2(token='merchant_access_token')
    # step 22: Login - promoter
    _resp22 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{promoter_email}}"\n}')
    ctx.extract('promoter_access_token', _resp22, '$.data.token')
    # step 23: get promoter order detail v2
    _resp23 = ctx.api.orders.promoter_detail_v2(token='promoter_access_token', path_vars={'merchantOrderId': '{{promoterOrderId}}'})
    # step 24: e8a42d09-c5c1-412c-b47c-b914537514a2
    _resp24 = ctx.api.admin.orders_search(body='{"query":"{{orderNumber}}","startTime":null,"endTime":null,"includePartnerTesting":true,"free":false,"pageSize":50,"pageNumber":1}', token='admin_access_token')
    vars['admin_orderId'] = 'admin_orderId'
    vars['merchantOrderId'] = 'merchantOrderId'
    # step 25: e37eecae-6f58-41f5-a8aa-703d5f547015
    _resp25 = ctx.api.admin.orders_refunds(body='{\n    "lineItems": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "id": "{{lineItemId}}",\n            "itemAmount": 55,\n            "taxAmount": 0,\n            "totalAmount": 55,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId}}",\n                "refundableItem": 55,\n                "refundableTax": 0,\n                "totalRefundable": 55,\n                "refundableQuantity": 1\n            },\n            "changedFields": []\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "shippingAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "refundableShipping": 5,\n                "refundableShippingTax": 0,\n                "totalRefundable": 5\n            }\n        }\n    ],\n    "refundTotals": {\n        "totalItemsRefund": 55,\n        "totalItemsQuantityRefund": 0,\n        "totalShippingRefund": 0,\n        "totalItemsTaxRefund": 0,\n        "totalShippingTaxRefund": 0,\n        "totalTaxRefund": 0,\n        "totalRefund": 55\n    },\n    "transactions": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "totalRefund": 55,\n            "totalRefundable": 60,\n            "changedFields": []\n        }\n    ]\n}', token='admin_access_token')
    # step 26: 47705d28-4732-4fb1-b2c4-726148604787
    _resp26 = ctx.api.admin.orders_refunds(body='{\n    "lineItems": [\n        {\n            "merchantOrderId": "1896c907-851c-4623-af81-7cdfd864dfa8",\n            "id": "{{lineItemId}}",\n            "itemAmount": 0,\n            "taxAmount": 0,\n            "totalAmount": 0,\n            "quantity": 0,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "lineItemId": "{{lineItemId}}",\n                "refundableItem": 0,\n                "refundableTax": 0,\n                "totalRefundable": 0,\n                "refundableQuantity": 1\n            },\n            "changedFields": []\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "shippingAmount": 5,\n            "taxAmount": 0,\n            "totalAmount": 5,\n            "refundable": {\n                "merchantOrderId": "{{merchantOrderId}}",\n                "refundableShipping": 5,\n                "refundableShippingTax": 0,\n                "totalRefundable": 5\n            }\n        }\n    ],\n    "refundTotals": {\n        "totalItemsRefund": 0,\n        "totalItemsQuantityRefund": 0,\n        "totalShippingRefund": 5,\n        "totalItemsTaxRefund": 0,\n        "totalShippingTaxRefund": 0,\n        "totalTaxRefund": 0,\n        "totalRefund": 5\n    },\n    "transactions": [\n        {\n            "merchantOrderId": "{{merchantOrderId}}",\n            "totalRefund": 5,\n            "totalRefundable": 5,\n            "changedFields": []\n        }\n    ]\n}', token='admin_access_token')
    # step 27: Login - P1
    _resp27 = ctx.api.auth.sign_in(body='{\n    "password": "{{P1_password}}",\n    "email": "{{P1}}"\n}')
    ctx.extract('P1_access_token', _resp27, '$.data.token')
    # step 28: get P1 order detail v2
    _resp28 = ctx.api.orders.merchant_bed7b1d8_16d8_4d27_ab1a_dc4a8f19e0c6_detail_v2(token='P1_access_token')
    # step 29: Login - merchant
    _resp29 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp29, '$.data.token')
    # step 30: get merchant orders
    _resp30 = ctx.api.orders.promoter(token='merchant_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 31: get merhcant order detail v2
    _resp31 = ctx.api.orders.promoter_detail_v2(token='merchant_access_token')
    # step 32: Login - promoter
    _resp32 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{promoter_email}}"\n}')
    ctx.extract('promoter_access_token', _resp32, '$.data.token')
    # step 33: get promoter order detail v2
    _resp33 = ctx.api.orders.promoter_detail_v2(token='promoter_access_token', path_vars={'merchantOrderId': '{{promoterOrderId}}'})
