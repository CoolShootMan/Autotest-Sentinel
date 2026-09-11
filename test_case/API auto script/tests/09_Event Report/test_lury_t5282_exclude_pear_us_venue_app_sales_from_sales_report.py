"""Migrated from Apifox case #8660144. Source folder: Event Report."""
# Apifox Case ID: 8660144  (traceability only — not needed to run)
NAME = "Exclude Pear.Us Venue app sales from sales report"
TAGS = ["p0", "event_report", "suite:lury"]
PRIORITY = 0


CASE_ID = 8660144
ENV_NAME = "Release"

# --- step 1: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 2: 481ed3af-9c3a-454a-81fd-617b35b1102d ---
# post[customScript]: pm.test("Check sales event report page -  gross sales", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNumberOfOrders"]).to.eql(1);
# post:     pm.expect(data["totalPromoterOrders"]).to.eql(0);  
# post:     pm.expect(data["totalPromoterOrdersPercentage"]).to.eql(0);  
# post:     pm.expect(data["totalItemsSold"]).to.eql(2);  
# post:     pm.expect(data["totalTicketSold"]).to.eql(2);  
# post:     pm.expect(data["totalMerchSold"]).to.eql(0);  
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(2);  
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(2);  
# post:     pm.expect(data["promoterTotalItemsRedeemed"]).to.eql(0);  
# post:     pm.expect(data["grossSales"]).to.eql(14.77);  
# post:     pm.expect(data["grossSalesBeforeDiscount"]).to.eql(14.77);
# post:     pm.expect(data["totalDiscount"]).to.eql(0);
# post:     pm.expect(data["totalRefund"]).to.eql(0);
# post:     pm.expect(data["totalDisputeFees"]).to.eql(0);
# post:     pm.expect(data["totalTip"]).to.eql(0);
# post:     pm.expect(data["totalEarnedTips"]).to.eql(0);
# post:     pm.expect(data["totalTipTransactionFee"]).to.eql(0);
# post:     pm.expect(data["promoterGrossSales"]).to.eql(0);
# post:     pm.expect(data["totalItemsSoldByPromoter"]).to.eql(0);
# post:     pm.expect(data["hasPromoterSales"]).to.eql(false);
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(3);
# post:     pm.expect(data["staffGrossSales"]).to.eql(171.67);
# post:     pm.expect(data["hasStaffSales"]).to.eql(true);
# post:     pm.expect(data["totalItemsSoldPercentage"]).to.eql(0);
# post:     pm.expect(data["averageOrderValue"]).to.eql(14.77);
# post:     pm.expect(data["netRevenue"]).to.eql(14.77);
# post:     pm.expect(data["netTicketRevenue"]).to.eql(14.77);
# post:     pm.expect(data["netMerchRevenue"]).to.eql(0);
# post:     pm.expect(data["totalTransactionFee"]).to.eql(4.37);
# post:     pm.expect(data["totalLineupFee"]).to.eql(0);
# post:     pm.expect(data["totalRebate"]).to.eql(2.16);
# post:     pm.expect(data["totalTransactionRebate"]).to.eql(2.16);
# post:     pm.expect(data["totalAppRebate"]).to.eql(0);
# post:     pm.expect(data["totalCommissionPaid"]).to.eql(0);
# post:     pm.expect(data["totalEarningShared"]).to.eql(0);
# post:     pm.expect(data["totalTax"]).to.eql(0);
# post:     pm.expect(data["totalTicketTax"]).to.eql(0.89);
# post:     pm.expect(data["shippingCostReimbursement"]).to.eql(0);
# post:     pm.expect(data["netEarnings"]).to.eql(13.45);
# post:     pm.expect(data["netEarningsBeforeEarningsShare"]).to.eql(13.45);
# post:     pm.expect(data["remainingNetEarnings"]).to.eql(13.45);
# post:     pm.expect(data["earningsShared"]).to.eql([]);
# post:     pm.expect(data["excludeOnsiteSales"]).to.eql(true);
# post: 
# post: });
# post: 
# post: 




from core.assertions import expect

def test_lury_t5282_exclude_pear_us_venue_app_sales_from_sales_report(ctx):
    """Apifox case #8660144: Lury_T5282_Exclude_Pear_Us_Venue_app_sales_from_sales_report"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Login-M1
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    # extractor: M1_access_token = $.data.token
    ctx.extract('M1_access_token', _resp1, '$.data.token')
    # step 2: 481ed3af-9c3a-454a-81fd-617b35b1102d
    _resp2 = ctx.api.events.v_39014a10_14e7_4cfa_993b_485f5c5485ac_metrics_summary(body=None, token='M1_access_token')
    # --- assertions: no fake-green (non-4xx/5xx) ---
    assert _resp1.status_code < 400, f"step1 got HTTP {_resp1.status_code}: {_resp1.text[:200]}"
    assert _resp2.status_code < 400, f"step2 got HTTP {_resp2.status_code}: {_resp2.text[:200]}"
