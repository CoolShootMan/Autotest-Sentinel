"""Migrated from Apifox case #7557017. Source folder: Resell and Affiliate."""
# Apifox Case ID: 7557017  (traceability only — not needed to run)
NAME = "_and_T3687_wholesale_commission_and_affiliate_link"
TAGS = ["p0", "resell_and_affiliate", "suite:lury"]
PRIORITY = 0


CASE_ID = 7557017
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
# pre: var order_level_transaction_fee = Math.floor(4.99 * 0.085*100)/100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(76,1)*100)/100;
# pre: var p1_transaction_fee = Math.round(((20/76 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var cal = Math.trunc(17/76*1000)/1000;
# pre: var merchant_transaction_fee = Math.round(((cal.toFixed(3) * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var promoter_transaction_fee = Math.round(((9.5/76 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var affiliate_transaction_fee = Math.round(((9.5/76 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - merchant_transaction_fee - promoter_transaction_fee - affiliate_transaction_fee + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: pm.environment.set("affiliate_transaction_fee", affiliate_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(promoter_transaction_fee)
# pre: console.log(affiliate_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("consumer_access_token",res['data']['token']);
# post: });
# --- step 2: delete cart ---
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
# pre: var order_level_transaction_fee = Math.floor(4.99 * 0.085*100)/100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(76,1)*100)/100;
# pre: var p1_transaction_fee = Math.round(((20/76 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var cal = Math.trunc(17/76*1000)/1000;
# pre: var merchant_transaction_fee = Math.round(((cal.toFixed(3) * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var promoter_transaction_fee = Math.round(((9.5/76 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var affiliate_transaction_fee = Math.round(((9.5/76 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - merchant_transaction_fee - promoter_transaction_fee - affiliate_transaction_fee + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: pm.environment.set("affiliate_transaction_fee", affiliate_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(promoter_transaction_fee)
# pre: console.log(affiliate_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: buy now - auto applied coupon ---
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
# post:     pm.expect(res['data']['totalTopay']).to.eql(80.99);
# post: });
# --- step 5: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 6: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var total_payout = Number((data["totalCommissionNet"] - m1_transaction_fee + data["totalShippingNet"] + data["totalTaxAmount"]).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(20);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(20);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(0);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(4.99);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(4.99);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: });
# post: 
# --- step 7: Login - P1 ---
# post[customScript]: pm.test("Check P1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P1_access_token",res['data']['token']);
# post: });
# --- step 8: get P1 orders ---
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
# --- step 9: get P1 order detail v2 ---
# post[customScript]: pm.test("Check P1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var p1_transaction_fee = pm.environment.get("p1_transaction_fee");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - p1_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(p1_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(20);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(20);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "5221b77a-8291-4cdc-882e-738988d13d53"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(80);
# post:             pm.expect(line_item["retailPrice"]).to.eql(80);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(75);
# post:             pm.expect(line_item["commissionGross"]).to.eql(60);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(40);
# post:             pm.expect(line_item["costPrice"]).to.eql(20);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(80);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(50);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(20);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(20);          
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
# post: 
# post: 
# post: 
# post: 
# --- step 10: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 11: get merchant orders ---
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
# --- step 12: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - merchant_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(merchant_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(17);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(17);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "5221b77a-8291-4cdc-882e-738988d13d53"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(80);
# post:             pm.expect(line_item["retailPrice"]).to.eql(80);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(4);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(4);
# post:             pm.expect(line_item["commissionRate"]).to.eql(50);
# post:             pm.expect(line_item["commissionGross"]).to.eql(40);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(19);
# post:             pm.expect(line_item["costPrice"]).to.eql(40);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(76);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(17);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(17);          
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
# --- step 13: Login - promoter ---
# post[customScript]: pm.test("Check promoter login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("promoter_access_token",res['data']['token']);
# post: });
# --- step 14: get promoter orders ---
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
# --- step 15: get promoter order detail v2 ---
# post[customScript]: pm.test("Check Promoter earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var promoter_transaction_fee = pm.environment.get("promoter_transaction_fee");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - promoter_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(promoter_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(9.5);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(9.5);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "5221b77a-8291-4cdc-882e-738988d13d53"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(76);
# post:             pm.expect(line_item["retailPrice"]).to.eql(80);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(4);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(19);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(9.5);
# post:             pm.expect(line_item["costPrice"]).to.eql(57);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(76);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(12.5);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(9.5);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(9.5);          
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
# --- step 16: Login -affiliate ---
# post[customScript]: pm.test("Check P5 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("affiliate_access_token",res['data']['token']);
# post: });
# --- step 17: get affiliate promoter orders ---
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
# --- step 18: get affiliate order detail v2 ---
# post[customScript]: pm.test("Check P5 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var affiliate_transaction_fee = pm.environment.get("affiliate_transaction_fee");
# post:     var total_payout = Number((res['data']['totalCommissionNet'] - affiliate_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(affiliate_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(9.5);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(9.5);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "5221b77a-8291-4cdc-882e-738988d13d53"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(76);
# post:             pm.expect(line_item["retailPrice"]).to.eql(80);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(4);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(12.5);
# post:             pm.expect(line_item["commissionGross"]).to.eql(9.5);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(66.5);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(76);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(9.5);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(9.5);          
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
import time

from typing import Any, TYPE_CHECKING

from core.assertions import expect

from core.compat import get_path as _get_path

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_t3781_and_t3687_wholesale_commission_and_affiliate_link(ctx: "Context"):
    """Apifox case #7557017: Lury_T3781_and_T3687_wholesale_commission_and_affiliate_link"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{consumer_email}}",
    }, app_headers=True)
    try:
        _j = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
        vars['consumer_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete(app_headers=True, token='consumer_access_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # step 3: buy now - auto applied coupon
    _resp3 = ctx.api.orders.buy_now(body={
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "5221b77a-8291-4cdc-882e-738988d13d53",
                "price": 80,
                "postId": "ac77e9f0-c2b6-4f86-a56b-3fe23cbb574b",
                "selected": True,
                "affiliateCode": "70zd9u",
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "462e4cc6-23f9-4791-9f45-97baabd52744",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1753864240949.326618326180969222",
            "externalId": "ca3a717f-fd4b-470b-a839-62bf62714bce",
            "eventSourceUrl": "https://release.pear.us/auto-promoter/post/e02ic6?aff=70zd9u",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "5221b77a-8291-4cdc-882e-738988d13d53",
                "postId": "ac77e9f0-c2b6-4f86-a56b-3fe23cbb574b",
                "price": 80,
                "affiliateCode": "70zd9u",
                "customFields": [],
            },
        ],
    }, app_headers=True, token='consumer_access_token')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, '$.data.orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, '$.data.orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body={
        "id": "{{orderId}}",
        "contact": {
            "email": "dian.yuhong.ext+19@1m.app",
            "phoneNumber": "+17404630034",
        },
        "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",
        "paymentInfo": {
            "paymentMethodId": "{{pay_method_id}}",
        },
        "fbAdParams": {
            "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a",
        },
    }, app_headers=True, token='consumer_access_token')
    # step 5: Login-M1
    _resp5 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{M1}}",
    }, app_headers=True)
    try:
        _j = _resp5.json() if _resp5.headers.get('content-type','').startswith('application/json') else {}
        vars['M1_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 6: get M1 order detail v2
    _resp6 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='M1_access_token', path_vars={'merchantId': '{{M1_merchantID6}}'})
    # step 7: Login - P1
    _resp7 = ctx.api.auth.sign_in(body={
        "password": "{{P1_password}}",
        "email": "{{P1}}",
    }, app_headers=True)
    try:
        _j = _resp7.json() if _resp7.headers.get('content-type','').startswith('application/json') else {}
        vars['P1_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 8: get P1 orders
    # 2026-09-20 修复：promoter 订单列表为异步聚合（新单最多延迟数十秒才出现在首页），
    # 直接断言首页命中会偶发失败（admin 侧可查、detail 接口 200 但列表未同步）。
    # 改为条件轮询：最多 6 次 × 3s，命中即 break（与订阅用例同款模式）。
    vars['P1_OrderId'] = ''
    for _attempt in range(6):
        _resp8 = ctx.api.orders.promoter(app_headers=True, token='P1_access_token', params={'pageSize': '30', 'pageNumber': '1'})
        _j8 = _resp8.json() if _resp8.headers.get('content-type','').startswith('application/json') else {}
        _arr8 = _get_path(_j8, ['data', 'items']) or []
        _hit8 = next((o for o in _arr8 if o.get('orderNumber') == vars.get('orderNumber')), None)
        if _hit8:
            vars['P1_OrderId'] = _hit8.get('id')
            break
        time.sleep(3)
    assert vars.get('P1_OrderId'), (
        f"test_lury_t3781_and_t3687_wholesale_comm L513: promoter orders 中未找到 "
        f"orderNumber={vars.get('orderNumber')!r} 的订单（items={len(_arr8)}）")
    # step 9: get P1 order detail v2
    _resp9 = ctx.api.orders.promoter_detail_v2(app_headers=True, token='P1_access_token', path_vars={'merchantOrderId': '{{P1_OrderId}}'})
    # step 10: Login - merchant
    _resp10 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{merchant_email}}",
    }, app_headers=True)
    try:
        _j = _resp10.json() if _resp10.headers.get('content-type','').startswith('application/json') else {}
        vars['merchant_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 11: get merchant orders
    _resp11 = ctx.api.orders.promoter(app_headers=True, token='merchant_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 12: get merhcant order detail v2
    _resp12 = ctx.api.orders.promoter_detail_v2(app_headers=True, token='merchant_access_token')
    # step 13: Login - promoter
    _resp13 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{promoter_email}}",
    }, app_headers=True)
    try:
        _j = _resp13.json() if _resp13.headers.get('content-type','').startswith('application/json') else {}
        vars['promoter_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 14: get promoter orders
    _resp14 = ctx.api.orders.promoter(app_headers=True, token='promoter_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    _j = _resp14.json() if _resp14.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    for _order in _arr:
        if _order.get('orderNumber') == vars.get('orderNumber'):
            vars['promoterOrderId'] = _order.get('id')
    # step 15: get promoter order detail v2
    _resp15 = ctx.api.orders.promoter_detail_v2(app_headers=True, token='promoter_access_token', path_vars={'merchantOrderId': '{{promoterOrderId}}'})
    # step 16: Login -affiliate
    _resp16 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{affiliate_promoter}}",
    }, app_headers=True)
    try:
        _j: dict[str, Any] = _resp16.json() if _resp16.headers.get('content-type','').startswith('application/json') else {}
        vars['affiliate_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 17: get affiliate promoter orders
    _resp17 = ctx.api.orders.promoter(app_headers=True, token='affiliate_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    _j = _resp17.json() if _resp17.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ['data', 'items']) or []
    # 原 post-script: 在 data.items 中找 orderNumber 与全局 orderNumber 相等的那单，取 id。
    for _order in _arr:
        if _order.get('orderNumber') == vars.get('orderNumber'):
            vars['P5_OrderId'] = _order.get('id')
    assert vars.get('P5_OrderId'), (
        f"test_lury_t3781_and_t3687_wholesale_comm L562: promoter orders 中未找到 "
        f"orderNumber={vars.get('orderNumber')!r} 的订单（items={len(_arr)}）")
    # step 18: get affiliate order detail v2
    _resp18 = ctx.api.orders.promoter_detail_v2(app_headers=True, token='affiliate_access_token', path_vars={'merchantOrderId': '{{P5_OrderId}}'})
