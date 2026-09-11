"""Migrated from Apifox case #7581016. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 7581016  (traceability only — not needed to run)
NAME = "&T4134&T4123&T4127&T5098_Earnings_tax_Rebate_Ticket_refund_commission rate"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:lury"]
PRIORITY = 0


CASE_ID = 7581016
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
# pre: function get_tax(unit_price,quantity){
# pre:     tax_rate = 0.06;
# pre:     return unit_price * quantity * tax_rate
# pre: }
# pre: 
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
# pre: var unit_price = 13.1;
# pre: var quantity = 2;
# pre: var commission_rate = 0.25;
# pre: var merchant_earnings =  Math.round(((unit_price * quantity * commission_rate) + Number.EPSILON) *100 ) / 100;
# pre: var m1_earnings = Number((unit_price * quantity - merchant_earnings ).toFixed(2));
# pre: 
# pre: var m1_rebate = Math.floor(set_rebate(unit_price,quantity) *100 ) / 100;
# pre: var tax_total = Math.floor(get_tax(unit_price,quantity)*100 ) / 100;
# pre: 
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(unit_price,quantity)*100)/100;
# pre: var merchant_transaction_fee = Math.round(((commission_rate * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_tax = Math.round(((commission_rate * tax_total) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - merchant_transaction_fee ).toFixed(2));
# pre: var m1_tax = Number((tax_total - merchant_tax ).toFixed(2));
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("m1_rebate", m1_rebate);
# pre: pm.environment.set("merchant_tax", merchant_tax);
# pre: pm.environment.set("m1_tax", m1_tax);
# pre: pm.environment.set("tax_total", tax_total);
# pre: pm.environment.set("merchant_earnings", merchant_earnings);
# pre: pm.environment.set("m1_earnings", m1_earnings);
# pre: console.log("merchant_transaction_fee: " + merchant_transaction_fee)
# pre: console.log("m1_transaction_fee: " + m1_transaction_fee)
# pre: console.log("m1_rebate: " + m1_rebate)
# pre: console.log("merchant_tax: " + merchant_tax)
# pre: console.log("m1_tax: " + m1_tax)
# pre: console.log("tax_total: " + tax_total)
# pre: console.log("merchant_earnings: " + merchant_earnings)
# pre: console.log("m1_earnings: " + m1_earnings)
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
# post:     pm.expect(res['data']['totalTopay']).to.eql(26.2);
# post: });
# --- step 5: get consumer order detail ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalLineItemPrice']).to.eql(26.2);
# post:     pm.expect(res['data']['totalToPay']).to.eql(26.2);
# post:     pm.expect(res['data']['totalPaid']).to.eql(26.2);
# post:     pm.expect(res['data']['totalTax']).to.eql(0);
# post:     pm.expect(res['data']['totalLineItemSubtotal']).to.eql(26.2);
# post:     pm.expect(res['data']['fulfillmentStatus']).to.eql("FULFILLED");
# post:     pm.expect(res['data']['totalTicketFees']).to.eql(6.19);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["title"] === "ticket - automation"){
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["unitPrice"]).to.eql(13.1);
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["fulfillmentCount"]).to.eql(2);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["listingType"]).to.eql("TICKET");
# post:             pm.expect(line_item["shippingFee"]).to.eql(0);
# post:             pm.expect(line_item["additionalShippingFee"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["discount"]).to.eql(0);
# post:             pm.expect(line_item["realShippingFee"]).to.eql(0);
# post:             pm.expect(line_item["autoFulfill"]).to.eql(true);
# post:             pm.expect(line_item["productTaxEnable"]).to.eql(true);
# post:             pm.expect(line_item["ticketFees"]).to.eql(6.19);
# post:             pm.expect(line_item["ticketFeesAfterRefund"]).to.eql(6.19);
# post:             pm.expect(line_item["deliveryMethod"]).to.eql("QR_CODE");
# post:             pm.expect(line_item["thirdPartyDeliveryMessage"]).to.eql(null);
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
# post:             pm.expect(line_item["multipleDaysPass"]).to.eql(null);
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
# post:             pm.expect(line_item["isMultipleDaysPassEnabled"]).to.eql(false);
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
# post:     var refund_id = data['id'];
# post:     pm.environment.set("refund_id", refund_id);
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var m1_rebate = pm.environment.get("m1_rebate");
# post:     var m1_tax = pm.environment.get("m1_tax");
# post:     var tax_total = pm.environment.get("tax_total");
# post:     var m1_earnings = pm.environment.get("m1_earnings")
# post:     var total_payout = Number((m1_earnings + tax_total - m1_transaction_fee - m1_tax + m1_rebate).toFixed(2));
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(m1_earnings);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(m1_earnings);
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee + m1_tax);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(m1_rebate);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(tax_total);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(tax_total);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "709c0762-dace-4d22-ab34-18c226a8f003"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["retailPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(26.2);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(6.55);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(26.2);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(19.65);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(19.65);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(2);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:             var orderLineItemId = line_item["orderLineItemId"];
# post:             var orderLineItemUnits = line_item["orderLineItemUnits"];
# post:             var item_unit_id_list = new Array();
# post:             for (var line_item_unit of orderLineItemUnits){
# post:                 item_unit_id_list.push(line_item_unit['id']) 
# post:             }
# post:             pm.environment.set("orderLineItemId", orderLineItemId);
# post:             pm.environment.set("item_unit_id_list", item_unit_id_list);
# post:             console.log("item_unit_id_list: " + item_unit_id_list[0] )
# post:             }
# post:             else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post: 
# post:     }
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
# post:     var merchant_tax = pm.environment.get("merchant_tax");
# post:     var merchant_earnings = pm.environment.get("merchant_earnings");
# post:     var total_payout = Number((merchant_earnings - merchant_tax - merchant_transaction_fee).toFixed(2));
# post:     var total_transaction_fee = Number((merchant_tax + merchant_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(merchant_earnings);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(merchant_earnings);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(total_transaction_fee);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "709c0762-dace-4d22-ab34-18c226a8f003"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["retailPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(6.55);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(19.65);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(26.2);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(6.55);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(6.55);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(2);
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
# --- step 11: Partner partial refund 1 ticket ---
# pre: var item_unit_id_list = pm.environment.get("item_unit_id_list");
# pre: var first_item_unit_id = item_unit_id_list[0];
# pre: pm.environment.set("first_item_unit_id", first_item_unit_id);
# post[customScript]: pm.test("Partner partial refund 1 tikcet in sale details page", function () {
# post:     pm.response.to.have.status(201);
# post: });
# --- step 12: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 13: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var m1_rebate = pm.environment.get("m1_rebate");
# post:     var m1_tax = pm.environment.get("m1_tax");
# post:     var tax_total = pm.environment.get("tax_total");
# post:     var tax_refunded = Number((tax_total/2).toFixed(2));
# post:     var m1_earnings = pm.environment.get("m1_earnings")
# post:     var total_payout = Number((m1_earnings - 9.82 + tax_total - tax_refunded - m1_transaction_fee - m1_tax/2 + m1_rebate ).toFixed(2));
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(m1_earnings);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(9.82);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(Number((m1_earnings - 9.82).toFixed(2)));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee + m1_tax/2 );
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(m1_rebate);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(tax_total);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(tax_refunded);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(tax_total - tax_refunded);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "709c0762-dace-4d22-ab34-18c226a8f003"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["retailPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(26.2);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(6.55);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(26.2);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(19.65);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(9.82);
# post:             pm.expect(line_item["commissionNet"]).to.eql(9.83);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(2);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(1);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(13.1);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:             }
# post:             else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post: 
# post:     }
# post: });
# --- step 14: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 15: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var merchant_tax = pm.environment.get("merchant_tax");
# post:     var merchant_refunded_tax = Number((merchant_tax/2).toFixed(2));
# post:     var merchant_earnings = pm.environment.get("merchant_earnings");
# post:     var total_payout = Number((merchant_earnings - 3.28 - merchant_tax - merchant_transaction_fee+ merchant_refunded_tax).toFixed(2));
# post:     var total_transaction_fee = Number((merchant_tax + merchant_transaction_fee - merchant_refunded_tax).toFixed(2));
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(merchant_earnings);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(3.28);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(merchant_earnings - 3.28);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(total_transaction_fee);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "709c0762-dace-4d22-ab34-18c226a8f003"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["retailPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(6.55);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(19.65);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(26.2);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(6.55);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(3.28);
# post:             pm.expect(line_item["commissionNet"]).to.eql(3.27);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(2);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(1);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(13.1);
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
# --- step 16: Partner full refund order on sale details page ---
# pre: var item_unit_id_list = pm.environment.get("item_unit_id_list");
# pre: var second_item_unit_id = item_unit_id_list[1];
# pre: pm.environment.set("second_item_unit_id", second_item_unit_id);
# post[customScript]: pm.test("Partner partial refund 1 tikcet in sale details page", function () {
# post:     pm.response.to.have.status(201);
# post: });
# --- step 17: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 18: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var m1_rebate = pm.environment.get("m1_rebate");
# post:     var tax_total = pm.environment.get("tax_total");
# post:     var m1_earnings = pm.environment.get("m1_earnings")
# post:     var total_payout = Number((0 - m1_transaction_fee +  m1_rebate - merchant_transaction_fee).toFixed(2));
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(m1_earnings);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(m1_earnings);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(Number(m1_earnings - m1_earnings));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee + merchant_transaction_fee);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(m1_rebate);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(tax_total);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(tax_total);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "709c0762-dace-4d22-ab34-18c226a8f003"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["retailPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionGross"]).to.eql(26.2);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(6.55);
# post:             pm.expect(line_item["costPrice"]).to.eql(0);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(26.2);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(19.65);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(19.65);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(2);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(2);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(26.2);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_WHOLESALE");
# post:             }
# post:             else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post: 
# post:     }
# post: });
# --- step 19: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 20: get merhcant order detail v2 ---
# post[customScript]: pm.test("Check merchant earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var merchant_earnings = pm.environment.get("merchant_earnings");
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(merchant_earnings);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(merchant_earnings);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(merchant_earnings -merchant_earnings);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(0);
# post:     pm.expect(res['data']['transactionFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "709c0762-dace-4d22-ab34-18c226a8f003"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["retailPrice"]).to.eql(26.2);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(6.55);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(19.65);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(26.2);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(6.55);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(6.55);
# post:             pm.expect(line_item["commissionNet"]).to.eql(0);          
# post:             pm.expect(line_item["quantity"]).to.eql(2);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(2);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(2);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(26.2);
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




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_lury_t4353_t4134_t4123_t4127_t5098_earnings_tax_rebate_ticket_refund_commission_rate(ctx):
    """Apifox case #7581016: Lury_T4353_T4134_T4123_T4127_T5098_Earnings_tax_Rebate_Ticket_refund_commission_"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    ctx.extract('consumer_access_token', _resp1, '$.data.refreshToken')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete()
    # step 3: buy now
    _resp3 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "e09a9cdd-4527-4f54-93a5-1c9d15a64a17",\n    "updateCartItems": [\n        {\n            "quantity": 2,\n            "promoterProductVariantId": "709c0762-dace-4d22-ab34-18c226a8f003",\n            "price": 13.1,\n            "postId": "e09a9cdd-4527-4f54-93a5-1c9d15a64a17",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "86aead4c-e551-42db-9ae1-09f0031708ed",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/auto-merchant/post/event-lury-ticket-tax-6-2"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 2,\n            "id": "709c0762-dace-4d22-ab34-18c226a8f003",\n            "postId": "e09a9cdd-4527-4f54-93a5-1c9d15a64a17",\n            "price": 26.2,\n            "customFields": []\n        }\n    ]\n}')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, 'orderId')
    # step 4: create Order
    _resp4 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}')
    # step 5: get consumer order detail
    _resp5 = ctx.api.orders.consumer_detail_by_order_number()
    # step 6: Login-M1
    _resp6 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp6, '$.data.token')
    # step 7: get M1 order detail v2
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # extractor: refund_id = refund_id
    ctx.extract('refund_id', _resp7, 'refund_id')
    _j = _resp7.json() if _resp7.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "lineItems"]) or []
    for _line_item in _arr:
        if _line_item.get('variantInfo', {}).get('id') == "709c0762-dace-4d22-ab34-18c226a8f003":
            vars['orderLineItemId'] = _line_item.get('orderLineItemId')
    _j = _resp7.json() if _resp7.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "lineItems"]) or []
    vars['item_unit_id_list'] = [_u.get('id') for _p in _arr for _u in _p.get('orderLineItemUnits') or []]
    # step 8: Login - merchant
    _resp8 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp8, '$.data.token')
    # step 9: get merchant orders
    _resp9 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'})
    vars['merchantOrderId'] = 'curatorOrderId'
    # step 10: get merhcant order detail v2
    _resp10 = ctx.api.orders.promoter_detail_v2()
    # step 11: Partner partial refund 1 ticket
    _resp11 = ctx.api.orders.refunds(body='{\n    "lineItems": [\n        {\n            "id": "{{orderLineItemId}}",\n            "quantity": 1,\n            "lineItemUnitIds": [\n                "{{first_item_unit_id}}"\n            ]\n        }\n    ],\n    "shippingLines": [],\n    "tipLines": [],\n    "note": "Automation test"\n}')
    # step 12: Login-M1
    _resp12 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp12, '$.data.token')
    # step 13: get M1 order detail v2
    _resp13 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # step 14: Login - merchant
    _resp14 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp14, '$.data.token')
    # step 15: get merhcant order detail v2
    _resp15 = ctx.api.orders.promoter_detail_v2()
    # step 16: Partner full refund order on sale details page
    _resp16 = ctx.api.orders.refunds(body='{\n    "lineItems": [\n        {\n            "id": "{{orderLineItemId}}",\n            "quantity": 1,\n            "lineItemUnitIds": [\n                "{{second_item_unit_id}}"\n            ]\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{refund_id}}"\n        }\n    ],\n    "tipLines": [\n        {\n            "merchantOrderId": "{{refund_id}}"\n        }\n    ],\n    "note": "Automation full refund"\n}')
    # step 17: Login-M1
    _resp17 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    ctx.extract('M1_access_token', _resp17, '$.data.token')
    # step 18: get M1 order detail v2
    _resp18 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'})
    # step 19: Login - merchant
    _resp19 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    ctx.extract('merchant_access_token', _resp19, '$.data.token')
    # step 20: get merhcant order detail v2
    _resp20 = ctx.api.orders.promoter_detail_v2()
