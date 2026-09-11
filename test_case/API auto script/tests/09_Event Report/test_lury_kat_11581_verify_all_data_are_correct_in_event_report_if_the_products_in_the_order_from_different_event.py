"""Migrated from Apifox case #8499887. Source folder: Event Report."""
# Apifox Case ID: 8499887  (traceability only — not needed to run)
NAME = "(Lury)KAT-11581 Verify all data are correct in event report if the products in the order from different event"
TAGS = ["p0", "event_report", "suite:lury"]
PRIORITY = 0


CASE_ID = 8499887
ENV_NAME = "Release"

# --- step 1: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 2: 173b63b5-165b-4824-b797-9834d8b6c5f8 ---
# post[customScript]: pm.test("Check sales event report page -  gross sales", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["grossSalesBeforeDiscount"]).to.eql(74.04);  // gross sales before promotion
# post:     pm.expect(data["totalDiscount"]).to.eql(7.39);  // promotion
# post:     pm.expect(data["grossSales"]).to.eql(66.65);   // gross sales
# post:     pm.expect(data["totalRefund"]).to.eql(22);  // total refund
# post: });
# post: 
# post: 
# post:     // Net revenue
# post: pm.test("Check sales event report page -  net revenue", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["netRevenue"]).to.eql(44.65);               // Total net reveue
# post:     pm.expect(data["netTicketRevenue"]).to.eql(44.65);           // Total ticket net revenue
# post:     pm.expect(data["netMerchRevenue"]).to.eql(0);          // Total merch net revenue
# post:     pm.expect(data["totalCommissionPaid"]).to.eql(5.5);  // Total commission
# post:     pm.expect(data["totalTransactionFee"]).to.eql(12.18); // Total transaction fees
# post: 
# post: //tax, custom fee and rebate
# post:     pm.expect(data["totalCustomFeeBreakdown"]["TAX"]["net"]).to.eql(0.23);   // Total taxes
# post:     pm.expect(data["totalCustomFeeBreakdown"]["custom_fee1"]["net"]).to.eql(0.12);  // Total custom fee1
# post:     pm.expect(data["totalCustomFeeBreakdown"]["custom_fee2"]["net"]).to.eql(0.23);  // Total custom fee2
# post:     pm.expect(data["totalRebate"]).to.eql(7.9);   // Total rebate
# post:     pm.expect(data["totalTransactionRebate"]).to.eql(7.9);  // Total transaction rebate
# post:     pm.expect(data["totalAppRebate"]).to.eql(0);   // Total app rebate
# post: 
# post:     //total revenue share
# post:     pm.expect(data["totalEarningShared"]).to.eql(12.6);   //total revenue  share
# post: 
# post:     var earning_shared = data["earningsShared"]   
# post: 
# post:     for (var share_account of earning_shared){       //each account revenue share
# post:            if (share_account["url"] === "https://release.pear.us/auto-merchant"){
# post:             pm.expect(share_account["revenueSharePercent"]).to.eql(11.11);
# post:             pm.expect(share_account["amount"]).to.eql(4.84);
# post:            }
# post:            else{
# post:             pm.expect(share_account["revenueSharePercent"]).to.eql(10);
# post:             pm.expect(share_account["amount"]).to.eql(7.76);
# post:            }
# post:     }
# post: });
# post: 
# post: pm.test("Check sales event report page -  Net earnings and tip", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["netEarnings"]).to.eql(22.85);  // net earning
# post:     pm.expect(data["remainingNetEarnings"]).to.eql(22.85);  // remaining net earnings
# post:     pm.expect(data["totalEarnedTips"]).to.eql(0);   //total tip earned
# post:     pm.expect(data["totalTip"]).to.eql(0);  // total tip
# post:     pm.expect(data["totalTipTransactionFee"]).to.eql(0);  // total tip fee
# post:     pm.expect(data["averageOrderValue"]).to.eql(11.11);  // Average order value
# post: });
# post: 
# post: pm.test("Check sales event report page -  number of sold", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNumberOfOrders"]).to.eql(6);  // total number of or orders
# post:     pm.expect(data["totalItemsSold"]).to.eql(4);  // total item sold
# post:     pm.expect(data["totalTicketSold"]).to.eql(4);   //total ticket sold
# post:     pm.expect(data["totalMerchSold"]).to.eql(0);  // total merch sold
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(0);  // total item redeemed
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(4);  // total item redeemable
# post: 
# post: });
# post: 
# post: pm.test("Check sales event report page -  co-selling commission sales", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["promoterGrossSales"]).to.eql(22);  // promoter gross sales
# post:     pm.expect(data["totalItemsSoldByPromoter"]).to.eql(2);  // total item sold by promoter
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(0);   //total item sold by staff
# post:     pm.expect(data["totalItemsSoldPercentage"]).to.eql(50);  // total item sold by promoter percentage
# post:     pm.expect(data["promoterTotalItemsRedeemed"]).to.eql(0);  // total item sold by promoter redeemed 
# post: });
# post: 
# post: 
# post: pm.test("Check sales event report page -  total sold view details", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var totalItemsSoldDetail = data["totalItemsSoldDetail"];
# post:     var promoterTotalItemsSoldDetail = data["promoterTotalItemsSoldDetail"]
# post:     for (var total_details of totalItemsSoldDetail){       //view total sold details
# post:            if (total_details["productId"] === "64d232ec-370c-4b08-8ed1-02f8ab56baf9"){
# post:             pm.expect(total_details["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(total_details["productTitle"]).to.eql("General Admission");
# post:             pm.expect(total_details["quantity"]).to.eql(3);
# post:             pm.expect(total_details["event"]).to.eql("Lury event report testing 0703 - other items");
# post:             pm.expect(total_details["redeemableCount"]).to.eql(3);
# post:            }
# post:            else if(total_details["productId"] === "af42a47a-1b65-4563-9f16-680f9d7eae22"){
# post:             pm.expect(total_details["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(total_details["productTitle"]).to.eql("ticket with custom fee");
# post:             pm.expect(total_details["quantity"]).to.eql(1);
# post:             pm.expect(total_details["event"]).to.eql("Lury event report testing 0703 - other items");
# post:             pm.expect(total_details["redeemableCount"]).to.eql(1);
# post:            }
# post:     }
# post: 
# post:     for (var view_details of promoterTotalItemsSoldDetail){       //view total sold details
# post:            if (view_details["productId"] === "64d232ec-370c-4b08-8ed1-02f8ab56baf9"){
# post:             pm.expect(view_details["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(view_details["productTitle"]).to.eql("General Admission");
# post:             pm.expect(view_details["quantity"]).to.eql(2);
# post:             pm.expect(view_details["event"]).to.eql("Lury event report testing 0703 - other items");
# post:             pm.expect(view_details["redeemableCount"]).to.eql(2);
# post:            }
# post:     }
# post: 
# post: });
# --- step 3: c9b059aa-7ace-47a0-85ce-a420ca35db9e ---
# post[customScript]: pm.test("Check sales event report page -  promotion view details", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var items = res['data']["items"]
# post:     for (var item of items){       //view each staff details
# post:            if (item["iorderNumberd"] === "P159990"){
# post:             pm.expect(item["orderDiscount"]).to.eql(1.29);
# post:            }
# post:            else if(item["iorderNumberd"] === "P159987"){
# post:             pm.expect(item["orderDiscount"]).to.eql(1.22);
# post:            }
# post:            else if(item["iorderNumberd"] === "P159986"){
# post:             pm.expect(item["orderDiscount"]).to.eql(1.22);
# post:            }
# post:            else if(item["iorderNumberd"] === "P159985"){
# post:             pm.expect(item["orderDiscount"]).to.eql(1.22);
# post:            }
# post:            else if(item["iorderNumberd"] === "P159981"){
# post:             pm.expect(item["orderDiscount"]).to.eql(1.22);
# post:            }
# post:            else if(item["iorderNumberd"] === "P159979"){
# post:             pm.expect(item["orderDiscount"]).to.eql(1.22);
# post:            }
# post: 
# post:     }
# post: });
# --- step 4: 8ca7d390-9a3c-424f-9ce3-5ffdbde1b249 ---
# post[customScript]: pm.test("Check sales - orders page total net earnings", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNetEarnings"]).to.eql(37.75);  
# post:     pm.expect(data["totalCurrentEventNetEarnings"]).to.eql(22.85);  
# post:     pm.expect(data["totalCurrentEventFilteredNetEarnings"]).to.eql(22.85);   
# post:     pm.expect(data["totalOtherEventNetEarnings"]).to.eql(14.9);  
# post:     pm.expect(data["totalOrders"]).to.eql(6);  
# post:     pm.expect(data["totalItems"]).to.eql(4);  
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(4);  
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(0);  
# post: 
# post: });




from core.assertions import expect

def test_lury_kat_11581_verify_all_data_are_correct_in_event_report_if_the_products_in_the_order_from_different_event(ctx):
    """Apifox case #8499887: Lury_KAT_11581_Verify_all_data_are_correct_in_event_report_if_the_products_in_th"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Login-M1
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    # extractor: M1_access_token = $.data.token
    ctx.extract('M1_access_token', _resp1, '$.data.token')
    # step 2: 173b63b5-165b-4824-b797-9834d8b6c5f8
    _resp2 = ctx.api.events.dad4b563_4eaf_47cd_a825_e63d61e48de1_metrics_summary(body=None, token='M1_access_token')
    # step 3: c9b059aa-7ace-47a0-85ce-a420ca35db9e
    _resp3 = ctx.api.events.dad4b563_4eaf_47cd_a825_e63d61e48de1_metrics_discount_orders(body=None, params={'pageSize': '30', 'pageNumber': '1'}, token='M1_access_token')
    # step 4: 8ca7d390-9a3c-424f-9ce3-5ffdbde1b249
    _resp4 = ctx.api.events.dad4b563_4eaf_47cd_a825_e63d61e48de1_metrics_orders_summary(body=None, params={'dateText': 'Custom', 'productIds': 'af42a47a-1b65-4563-9f16-680f9d7eae22,64d232ec-370c-4b08-8ed1-02f8ab56baf9'}, token='M1_access_token')
    # --- assertions: no fake-green (non-4xx/5xx) ---
    assert _resp1.status_code < 400, f"step1 got HTTP {_resp1.status_code}: {_resp1.text[:200]}"
    assert _resp2.status_code < 400, f"step2 got HTTP {_resp2.status_code}: {_resp2.text[:200]}"
    assert _resp3.status_code < 400, f"step3 got HTTP {_resp3.status_code}: {_resp3.text[:200]}"
    assert _resp4.status_code < 400, f"step4 got HTTP {_resp4.status_code}: {_resp4.text[:200]}"
