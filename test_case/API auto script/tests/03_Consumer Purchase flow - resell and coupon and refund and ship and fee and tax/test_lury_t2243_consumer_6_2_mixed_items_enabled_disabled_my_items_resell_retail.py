"""Migrated from Apifox case #7542989. Source folder: Consumer Purchase flow - resell and coupon and refund and ship and fee and tax."""
# Apifox Case ID: 7542989  (traceability only — not needed to run)
NAME = "_Consumer_6-2_Mixed_items_enabled_disabled_my_items_resell_retail"
TAGS = ["p0", "consumer_purchase_flow_resell_and_coupon_and_refund_and_ship_and_fee_and_tax", "suite:lury"]
PRIORITY = 0


CASE_ID = 7542989
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
# pre: 
# pre: 
# pre: var order_level_transaction_fee = Math.floor((4.99* 0.085)*100) / 100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(120,1)*100)/100;
# pre: var merchant_transaction_fee = Math.round(((27/120 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var promoter_transaction_fee = Math.round(((18/120 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var p1_transaction_fee = Number((transaction_fee_item_level - merchant_transaction_fee - promoter_transaction_fee + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(promoter_transaction_fee)
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
# post:     pm.expect(res['data']['totalTopay']).to.eql(363.63);
# post: });
# --- step 5: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 6: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 processing fee and earnings", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var total_payout = Number((data["totalCommissionNet"] - p1_transaction_fee + data["totalShippingNet"] + data["totalTaxAmount"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(p1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(75);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(75);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(4.99);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: });
# --- step 7: get P1 order detail v2-fixed item ---
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
# pre: 
# pre: function customRound(number) {
# pre:     return (number % 1 >= 0.5) ? Math.ceil(number) : Math.floor(number);
# pre: }
# pre: 
# pre: var shipping_tax = 4.99 + 8.66
# pre: 
# pre: var order_level_transaction_fee = Math.floor((shipping_tax* 0.085)*100) / 100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(100,1)*100) /100;
# pre: var merchant_transaction_fee1 = Math.round(((10/100 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var promoter_transaction_fee1 = Math.round(((15/100 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var p1_transaction_fee1 = Number((transaction_fee_item_level - merchant_transaction_fee1 - promoter_transaction_fee1 + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("p1_transaction_fee1", p1_transaction_fee1);
# pre: pm.environment.set("merchant_transaction_fee1", merchant_transaction_fee1);
# pre: pm.environment.set("promoter_transaction_fee1", promoter_transaction_fee1);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee1)
# pre: console.log(merchant_transaction_fee1)
# pre: console.log(promoter_transaction_fee1)
# post[customScript]: pm.test("Check P1 processing fee and earnings", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var p1_transaction_fee1 = pm.environment.get("p1_transaction_fee1");
# post:     var total_payout = Number((data["totalCommissionNet"] - p1_transaction_fee1 + data["totalShippingNet"] + data["totalTaxAmount"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(p1_transaction_fee1);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(75);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(75);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(8.66);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(4.99);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(8.66);
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
# post:     var merchant_transaction_fee1 = pm.environment.get("merchant_transaction_fee1");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - merchant_transaction_fee - merchant_transaction_fee1).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(merchant_transaction_fee + merchant_transaction_fee1);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(37);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(37);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "e3a58292-0a2e-41ac-9d65-27cc6ea3ad27"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(120);
# post:             pm.expect(line_item["retailPrice"]).to.eql(120);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(45);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(18);
# post:             pm.expect(line_item["costPrice"]).to.eql(75);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(120);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(15);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(27);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(27);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:            }
# post:            else if(line_item["variantInfo"]["id"] === "0a080cde-22b7-457b-b843-02f1f5101769"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(100);
# post:             pm.expect(line_item["retailPrice"]).to.eql(100);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(25);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(15);
# post:             pm.expect(line_item["costPrice"]).to.eql(75);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(100);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(15);
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
# post: 
# post:            }
# post:     }
# post: 
# post: });
# --- step 11: get merchant commission charge ---
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
# pre: 
# pre: function customRound(number) {
# pre:     return (number % 1 >= 0.5) ? Math.ceil(number) : Math.floor(number);
# pre: }
# pre: 
# pre: 
# pre: var order_level_transaction_fee = Math.floor((4.99* 0.085)*100) / 100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(120,1)*100)/100;
# pre: var promoter_transaction_fee2 = Math.round(((18/120 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee2 = Number((transaction_fee_item_level - promoter_transaction_fee2 + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("merchant_transaction_fee2", merchant_transaction_fee2);
# pre: pm.environment.set("promoter_transaction_fee2", promoter_transaction_fee2);
# pre: console.log(merchant_transaction_fee2)
# pre: console.log(promoter_transaction_fee2)
# pre: 
# post[customScript]: pm.test("Check P1 processing fee and earnings", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var merchant_transaction_fee2 = pm.environment.get("merchant_transaction_fee2");
# post:     var total_payout = Number((data["totalCommissionNet"] - merchant_transaction_fee2 + data["totalShippingNet"] + data["totalTaxAmount"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(merchant_transaction_fee2);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(102);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(102);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(4.99);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: });
# --- step 12: Login - promoter ---
# post[customScript]: pm.test("Check promoter login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("promoter_access_token",res['data']['token']);
# post: });
# --- step 13: get promoter orders ---
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
# --- step 14: get promoter order detail v2 ---
# post[customScript]: pm.test("Check promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var promoter_transaction_fee1 = pm.environment.get("promoter_transaction_fee1");
# post:     var promoter_transaction_fee2 = pm.environment.get("promoter_transaction_fee2");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - promoter_transaction_fee - promoter_transaction_fee2 - promoter_transaction_fee1).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(promoter_transaction_fee + promoter_transaction_fee2 + promoter_transaction_fee1);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(51);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(51);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "fa60f26f-a4c3-4895-bc22-e2638dcd10cf"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(120);
# post:             pm.expect(line_item["retailPrice"]).to.eql(120);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(15);
# post:             pm.expect(line_item["commissionGross"]).to.eql(18);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(102);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(120);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(18);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(18);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:            }
# post:            else if(line_item["variantInfo"]["id"] === "e3a58292-0a2e-41ac-9d65-27cc6ea3ad27"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(120);
# post:             pm.expect(line_item["retailPrice"]).to.eql(120);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(15);
# post:             pm.expect(line_item["commissionGross"]).to.eql(18);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(102);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(120);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(18);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(18);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:            }
# post:            else if(line_item["variantInfo"]["id"] === "0a080cde-22b7-457b-b843-02f1f5101769"){
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(15);
# post:             pm.expect(line_item["commissionGross"]).to.eql(15);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(85);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(100);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(15);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(15);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(0);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("UNFULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:            }
# post:     }
# post: 
# post: });




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_lury_t2243_consumer_6_2_mixed_items_enabled_disabled_my_items_resell_retail(ctx):
    """Apifox case #7542989: Lury_T2243_Consumer_6_2_Mixed_items_enabled_disabled_my_items_resell_retail"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.token')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "fa60f26f-a4c3-4895-bc22-e2638dcd10cf",\n            "price": 120,\n            "postId": "6258400c-085e-4572-95d0-a0b4ad059489",\n            "selected": true,\n            "customFields": []\n        },\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "e3a58292-0a2e-41ac-9d65-27cc6ea3ad27",\n            "price": 120,\n            "postId": "6258400c-085e-4572-95d0-a0b4ad059489",\n            "selected": true,\n            "customFields": []\n        },\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "0a080cde-22b7-457b-b843-02f1f5101769",\n            "price": 100,\n            "postId": "6258400c-085e-4572-95d0-a0b4ad059489",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "e60509b1-ed54-4380-b21b-cbf6cf0159da",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",\n        "eventSourceUrl": "https://release.pear.us/auto-promoter/post/grlb54"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "fa60f26f-a4c3-4895-bc22-e2638dcd10cf",\n            "postId": "6258400c-085e-4572-95d0-a0b4ad059489",\n            "price": 120,\n            "customFields": []\n        },\n        {\n            "quantity": 1,\n            "id": "e3a58292-0a2e-41ac-9d65-27cc6ea3ad27",\n            "postId": "6258400c-085e-4572-95d0-a0b4ad059489",\n            "price": 120,\n            "customFields": []\n        },\n        {\n            "quantity": 1,\n            "id": "0a080cde-22b7-457b-b843-02f1f5101769",\n            "postId": "6258400c-085e-4572-95d0-a0b4ad059489",\n            "price": 100,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034",\n        "firstName": "Automation",\n        "lastName": "Lury"\n    },\n    "shippingAddressId": "{{shippingAddress_id}}",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 5: Login - P1
    _resp5 = ctx.api.auth.sign_in(body='{\n    "password": "{{P1_password}}",\n    "email": "{{P1}}"\n}')
    ctx.extract('P1_access_token', _resp5, '$.data.token')
    # step 6: get P1 order detail v2
    _resp6 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{P1_merchantIDb}}'})
    # step 7: get P1 order detail v2-fixed item
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{P1_merchantIDa}}'})
    # step 8: Login - merchant
    _resp8 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp8, '$.data.token')
    # step 9: get merchant orders
    _resp9 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 10: get merhcant order detail v2
    _resp10 = ctx.api.orders.promoter_detail_v2()
    # step 11: get merchant commission charge
    _resp11 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{merchantID7}}'})
    # step 12: Login - promoter
    _resp12 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{promoter_email}}"\n}')
    ctx.extract('promoter_access_token', _resp12, '$.data.token')
    # step 13: get promoter orders
    _resp13 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    _j = _resp13.json() if _resp13.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    for _order in _arr:
        if _order.get('orderNumber') == vars.get('orderNumber'):
            vars['promoterOrderId'] = _order.get('id')
    # step 14: get promoter order detail v2
    _resp14 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{promoterOrderId}}'})
