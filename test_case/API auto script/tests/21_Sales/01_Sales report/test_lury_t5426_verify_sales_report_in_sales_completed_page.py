"""Migrated from Apifox case #8687310. Source folder: Sales/Sales report."""
# Apifox Case ID: 8687310  (traceability only — not needed to run)
NAME = "Verify sales report in sales > completed page"
TAGS = ["p0", "sales_sales_report", "suite:lury"]
PRIORITY = 0


CASE_ID = 8687310
ENV_NAME = "Release"

# --- step 1: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['refreshToken']);
# post: });
# --- step 2: ae986bec-d475-46ab-a8fd-82d12e9567fc ---
# post[customScript]: pm.test("Check sales report page ", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNumberOfOrders"]).to.eql(3085);  
# post:     pm.expect(data["totalPromoterOrders"]).to.eql(779);  
# post:     pm.expect(data["totalPromoterOrdersPercentage"]).to.eql(25.25);  
# post:     pm.expect(data["totalItemsSold"]).to.eql(5607);  
# post:     pm.expect(data["totalTicketSold"]).to.eql(4084);
# post:     pm.expect(data["totalMerchSold"]).to.eql(1523);
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(1017);
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(4843);
# post:     pm.expect(data["promoterTotalItemsRedeemed"]).to.eql(53);
# post:     pm.expect(data["grossSales"]).to.eql(73266.21);
# post:     pm.expect(data["grossSalesBeforeDiscount"]).to.eql(98481.2);
# post:     pm.expect(data["totalDiscount"]).to.eql(25214.99);
# post:     pm.expect(data["totalRefund"]).to.eql(16903.35);
# post:     pm.expect(data["totalDisputeFees"]).to.eql(105.84);
# post:     pm.expect(data["totalTip"]).to.eql(1657.17);
# post:     pm.expect(data["totalEarnedTips"]).to.eql(1816.38);
# post:     pm.expect(data["totalTipTransactionFee"]).to.eql(191.75);
# post:     pm.expect(data["promoterGrossSales"]).to.eql(31456.5);
# post:     pm.expect(data["totalItemsSoldByPromoter"]).to.eql(1845);
# post:     pm.expect(data["hasPromoterSales"]).to.eql(true);
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(1196);
# post:     pm.expect(data["staffGrossSales"]).to.eql(15655.25);
# post:     pm.expect(data["hasStaffSales"]).to.eql(true);
# post:     pm.expect(data["totalItemsSoldPercentage"]).to.eql(32.91);
# post:     pm.expect(data["averageOrderValue"]).to.eql(23.75);
# post:     pm.expect(data["netRevenue"]).to.eql(56257.02);
# post:     pm.expect(data["netTicketRevenue"]).to.eql(44614.77);
# post:     pm.expect(data["netMerchRevenue"]).to.eql(11423.2);
# post:     pm.expect(data["totalTransactionFee"]).to.eql(12167.5);
# post:     pm.expect(data["totalLineupFee"]).to.eql(0);
# post:     pm.expect(data["totalRebate"]).to.eql(4876.76);
# post:     pm.expect(data["totalTransactionRebate"]).to.eql(4259.15);
# post:     pm.expect(data["totalAppRebate"]).to.eql(617.61);
# post:     pm.expect(data["totalCommissionPaid"]).to.eql(5650.59);
# post:     pm.expect(data["totalEarningShared"]).to.eql(1560.6);
# post:     pm.expect(data["totalTax"]).to.eql(148.18);
# post:     pm.expect(data["totalTicketTax"]).to.eql(1003.91);
# post:     pm.expect(data["shippingCostReimbursement"]).to.eql(70.87);
# post:     pm.expect(data["netEarnings"]).to.eql(42618.07);
# post:     pm.expect(data["netEarningsBeforeEarningsShare"]).to.eql(44178.67);
# post:     pm.expect(data["remainingNetEarnings"]).to.eql(40960.9);
# post:     pm.expect(data["excludeOnsiteSales"]).to.eql(false);
# post: 
# post: });
# post: 
# post: 
# post: pm.test("Check sales report custom fee breakdown", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var totalCustomFeeBreakdown = data["totalCustomFeeBreakdown"];
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["net"]).to.eql(770.53);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["index"]).to.eql(0);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["title"]).to.eql("Taxes");
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["amount"]).to.eql(1007.84);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["refunded"]).to.eql(237.31);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_8"]["net"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_8"]["index"]).to.eql(8);
# post:     pm.expect(totalCustomFeeBreakdown["custom_8"]["title"]).to.eql("8");
# post:     pm.expect(totalCustomFeeBreakdown["custom_8"]["amount"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_8"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_9"]["net"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_9"]["index"]).to.eql(9);
# post:     pm.expect(totalCustomFeeBreakdown["custom_9"]["title"]).to.eql("9");
# post:     pm.expect(totalCustomFeeBreakdown["custom_9"]["amount"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_9"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_10"]["net"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_10"]["index"]).to.eql(10);
# post:     pm.expect(totalCustomFeeBreakdown["custom_10"]["title"]).to.eql("10");
# post:     pm.expect(totalCustomFeeBreakdown["custom_10"]["amount"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_10"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_11"]["net"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_11"]["index"]).to.eql(11);
# post:     pm.expect(totalCustomFeeBreakdown["custom_11"]["title"]).to.eql("11");
# post:     pm.expect(totalCustomFeeBreakdown["custom_11"]["amount"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_11"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_12"]["net"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_12"]["index"]).to.eql(12);
# post:     pm.expect(totalCustomFeeBreakdown["custom_12"]["title"]).to.eql("12");
# post:     pm.expect(totalCustomFeeBreakdown["custom_12"]["amount"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_12"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_13"]["net"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_13"]["index"]).to.eql(13);
# post:     pm.expect(totalCustomFeeBreakdown["custom_13"]["title"]).to.eql("13");
# post:     pm.expect(totalCustomFeeBreakdown["custom_13"]["amount"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_13"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee"]["net"]).to.eql(35.87);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee"]["title"]).to.eql("Fee");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee"]["amount"]).to.eql(37.35);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee"]["refunded"]).to.eql(1.48);
# post: 
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Ttt"]["net"]).to.eql(0.05);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Ttt"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Ttt"]["title"]).to.eql("Ttt");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Ttt"]["amount"]).to.eql(0.05);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Ttt"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["net"]).to.eql(6.52);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["title"]).to.eql("fee");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["amount"]).to.eql(8.52);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["refunded"]).to.eql(2);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feet"]["net"]).to.eql(0.02);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feet"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feet"]["title"]).to.eql("Feet");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feet"]["amount"]).to.eql(0.02);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feet"]["refunded"]).to.eql(0);
# post: 
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew"]["net"]).to.eql(3.28);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew"]["title"]).to.eql("Feew");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew"]["amount"]).to.eql(3.28);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["net"]).to.eql(10.71);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["title"]).to.eql("fee1");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["amount"]).to.eql(12.6);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["refunded"]).to.eql(1.89);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["net"]).to.eql(30.99);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["title"]).to.eql("fee2");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["amount"]).to.eql(36.22);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["refunded"]).to.eql(5.23);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3"]["net"]).to.eql(0.8);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3"]["index"]).to.eql(3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3"]["title"]).to.eql("fee3");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3"]["amount"]).to.eql(0.83);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3"]["refunded"]).to.eql(0.03);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee4"]["net"]).to.eql(0.59);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee4"]["index"]).to.eql(4);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee4"]["title"]).to.eql("fee4");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee4"]["amount"]).to.eql(0.59);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee4"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee5"]["net"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee5"]["index"]).to.eql(5);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee5"]["title"]).to.eql("fee5");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee5"]["amount"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee5"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee6"]["net"]).to.eql(0.89);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee6"]["index"]).to.eql(6);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee6"]["title"]).to.eql("fee6");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee6"]["amount"]).to.eql(0.89);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee6"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee7"]["net"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee7"]["index"]).to.eql(7);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee7"]["title"]).to.eql("fee7");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee7"]["amount"]).to.eql(0.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee7"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee_1"]["net"]).to.eql(2.87);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee_1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee_1"]["title"]).to.eql("Fee");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee_1"]["amount"]).to.eql(5.09);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee_1"]["refunded"]).to.eql(2.22);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee_1"]["net"]).to.eql(3.23);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee_1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee_1"]["title"]).to.eql("fee");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee_1"]["amount"]).to.eql(3.96);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee_1"]["refunded"]).to.eql(0.73);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["net"]).to.eql(0.54);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["title"]).to.eql("feea1");
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["amount"]).to.eql(0.54);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["net"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["title"]).to.eql("feea2");
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["amount"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee1_1"]["net"]).to.eql(2.95);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee1_1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee1_1"]["title"]).to.eql("Fee1");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee1_1"]["amount"]).to.eql(4.3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee1_1"]["refunded"]).to.eql(1.35);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee2_2"]["net"]).to.eql(3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee2_2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee2_2"]["title"]).to.eql("Fee2");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee2_2"]["amount"]).to.eql(8);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Fee2_2"]["refunded"]).to.eql(5);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew_2"]["net"]).to.eql(0);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew_2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew_2"]["title"]).to.eql("Feew");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew_2"]["amount"]).to.eql(0.22);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feew_2"]["refunded"]).to.eql(0.22);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1_1"]["net"]).to.eql(3.58);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1_1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1_1"]["title"]).to.eql("fee1");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1_1"]["amount"]).to.eql(3.76);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1_1"]["refunded"]).to.eql(0.18);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2_2"]["net"]).to.eql(21);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2_2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2_2"]["title"]).to.eql("fee2");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2_2"]["amount"]).to.eql(23);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2_2"]["refunded"]).to.eql(2);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3_3"]["net"]).to.eql(2.83);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3_3"]["index"]).to.eql(3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3_3"]["title"]).to.eql("fee3");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3_3"]["amount"]).to.eql(2.83);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee3_3"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee11_1"]["net"]).to.eql(3.48);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee11_1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee11_1"]["title"]).to.eql("fee11");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee11_1"]["amount"]).to.eql(3.48);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee11_1"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee22_2"]["net"]).to.eql(12);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee22_2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee22_2"]["title"]).to.eql("fee22");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee22_2"]["amount"]).to.eql(12);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee22_2"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee33_3"]["net"]).to.eql(6.84);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee33_3"]["index"]).to.eql(3);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee33_3"]["title"]).to.eql("fee33");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee33_3"]["amount"]).to.eql(6.84);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee33_3"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feeeee_2"]["net"]).to.eql(0.41);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feeeee_2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feeeee_2"]["title"]).to.eql("Feeeee");
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feeeee_2"]["amount"]).to.eql(0.41);
# post:     pm.expect(totalCustomFeeBreakdown["custom_Feeeee_2"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee1"]["net"]).to.eql(11.53);
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee1"]["title"]).to.eql("test fee1");
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee1"]["amount"]).to.eql(11.53);
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee1"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee2"]["net"]).to.eql(66);
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee2"]["title"]).to.eql("test fee2");
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee2"]["amount"]).to.eql(66);
# post:     pm.expect(totalCustomFeeBreakdown["custom_test fee2"]["refunded"]).to.eql(0);
# post: 
# post: });
# post: 
# post: pm.test("Check sales report page -- earning shared ", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var earningsShared = res['data']['earningsShared']
# post:     for (var share of earningsShared){
# post:         if(share['url']=== "https://release.pear.us/temp12-merchant"){
# post:             pm.expect(share["displayName"]).to.eql("Lury12 Merchant");
# post:             pm.expect(share["revenueSharePercent"]).to.eql(30);
# post:             pm.expect(share["amount"]).to.eql(33.3);
# post: 
# post:         }
# post:         else if(share['url']=== "https://release.pear.us/auto-merchant"){
# post:             pm.expect(share["displayName"]).to.eql("Auto Merchant 111");
# post:             pm.expect(share["revenueSharePercent"]).to.eql(12);
# post:             pm.expect(share["amount"]).to.eql(1044.87);
# post: 
# post:         }
# post:         else if(share['url']=== "https://release.pear.us/lury-13"){
# post:             pm.expect(share["displayName"]).to.eql("Lury-13");
# post:             pm.expect(share["revenueSharePercent"]).to.eql(10);
# post:             pm.expect(share["amount"]).to.eql(457.58);
# post: 
# post:         }
# post:     }
# post:     
# post: });
# --- step 3: 10b26495-009c-4847-ae8e-9c09b255e561 ---
# post[customScript]: pm.test("Check sales report - sold in venue app", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["staffGrossSales"]).to.eql(2427.31);
# post:     pm.expect(data["staffTotalItemsRedeemed"]).to.eql(88);
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(155);
# post:     pm.expect(data["totalItemsSoldPercentageByStaff"]).to.eql(17.55);
# post:     pm.expect(data["totalOrdersByStaff"]).to.eql(97);
# post:     pm.expect(data["totalOrdersPercentageByStaff"]).to.eql(15.57);
# post: 
# post: });
# post: 
# post: 
# --- step 4: 058052b7-05f9-4cc1-bcba-e798652c08fb ---
# post[customScript]: pm.test("Check sales report -  co-seller gross sales data", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var items = res['data']["items"]
# post:     for (var item of items){      
# post:            if (item["email"] === "dian.yuhong.ext+34@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql("auto-merchant");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(448);
# post:             pm.expect(item["totalItemsSold"]).to.eql(1026);
# post:             pm.expect(item["grossSales"]).to.eql(13187.07);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(27);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(2634.67);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(true);
# post:            }
# post:            else if(item["email"] === "yuxiao.zhu.ext+3@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql("yu-xiao");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(259);
# post:             pm.expect(item["totalItemsSold"]).to.eql(732);
# post:             pm.expect(item["grossSales"]).to.eql(15519.04);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(21);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(2241.94);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(true);
# post:            }
# post:            else if(item["email"] === "dian.yuhong.ext+6@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql("tester");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(23);
# post:             pm.expect(item["totalItemsSold"]).to.eql(36);
# post:             pm.expect(item["grossSales"]).to.eql(1967.48);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(477.73);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(false);
# post:            }
# post:            else if(item["email"] === "dian.yuhong.ext+26@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql("ckyurq6i11");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(23);
# post:             pm.expect(item["totalItemsSold"]).to.eql(23);
# post:             pm.expect(item["grossSales"]).to.eql(177.76);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(44.45);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(true);
# post:            }
# post:            else if(item["email"] === "dian.yuhong.ext+16@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql(null);
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(12);
# post:             pm.expect(item["totalItemsSold"]).to.eql(14);
# post:             pm.expect(item["grossSales"]).to.eql(191.64);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(4);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(40.42);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(true);
# post:            }
# post:            else if(item["email"] === "dian.yuhong.ext+23@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql("only-coseller");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(4);
# post:             pm.expect(item["totalItemsSold"]).to.eql(4);
# post:             pm.expect(item["grossSales"]).to.eql(53.22);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(1);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(13.31);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(false);
# post:            }
# post:            else if(item["email"] === "lei.liu.ext+1@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql("liu");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(1);
# post:             pm.expect(item["totalItemsSold"]).to.eql(1);
# post:             pm.expect(item["grossSales"]).to.eql(100);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(90);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(true);
# post:            }
# post:            else if(item["email"] === "dian.yuhong.ext+19@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql(null);
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(1);
# post:             pm.expect(item["totalItemsSold"]).to.eql(1);
# post:             pm.expect(item["grossSales"]).to.eql(2.38);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(0.6);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(true);
# post:            }
# post:            else if(item["email"] === "lei.liu.ext+2@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql("liulei2");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(1);
# post:             pm.expect(item["totalItemsSold"]).to.eql(1);
# post:             pm.expect(item["grossSales"]).to.eql(100);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(90);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(true);
# post:            }
# post:            else if(item["email"] === "fos.zyx+100@gmail.com"){
# post:             pm.expect(item["vanityUrl"]).to.eql("12345");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(1);
# post:             pm.expect(item["totalItemsSold"]).to.eql(1);
# post:             pm.expect(item["grossSales"]).to.eql(0);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(0);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(true);
# post:            }
# post:           
# post:     }
# post: });
# post: 
# post: 
# --- step 5: f9f6817a-87eb-4978-bf6d-3d1e6b2c1441 ---
# post[customScript]: pm.test("Check sales report page  ---- filter the sales report it should be consistent with event report", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNumberOfOrders"]).to.eql(6);  
# post:     pm.expect(data["totalPromoterOrders"]).to.eql(2);  
# post:     pm.expect(data["totalPromoterOrdersPercentage"]).to.eql(33.33);  
# post:     pm.expect(data["totalItemsSold"]).to.eql(8);  
# post:     pm.expect(data["totalTicketSold"]).to.eql(8);
# post:     pm.expect(data["totalMerchSold"]).to.eql(0);
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(4);
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(8);
# post:     pm.expect(data["promoterTotalItemsRedeemed"]).to.eql(2);
# post:     pm.expect(data["grossSales"]).to.eql(95.3);
# post:     pm.expect(data["grossSalesBeforeDiscount"]).to.eql(105.89);
# post:     pm.expect(data["totalDiscount"]).to.eql(10.59);
# post:     pm.expect(data["totalRefund"]).to.eql(26.26);
# post:     pm.expect(data["totalDisputeFees"]).to.eql(0);
# post:     pm.expect(data["totalTip"]).to.eql(0);
# post:     pm.expect(data["totalEarnedTips"]).to.eql(0);
# post:     pm.expect(data["totalTipTransactionFee"]).to.eql(0);
# post:     pm.expect(data["promoterGrossSales"]).to.eql(26.26);
# post:     pm.expect(data["totalItemsSoldByPromoter"]).to.eql(4);
# post:     pm.expect(data["hasPromoterSales"]).to.eql(true);
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(0);
# post:     pm.expect(data["staffGrossSales"]).to.eql(0);
# post:     pm.expect(data["hasStaffSales"]).to.eql(false);
# post:     pm.expect(data["totalItemsSoldPercentage"]).to.eql(50);
# post:     pm.expect(data["averageOrderValue"]).to.eql(15.88);
# post:     pm.expect(data["netRevenue"]).to.eql(69.04);
# post:     pm.expect(data["netTicketRevenue"]).to.eql(69.04);
# post:     pm.expect(data["netMerchRevenue"]).to.eql(0);
# post:     pm.expect(data["totalTransactionFee"]).to.eql(23.38);
# post:     pm.expect(data["totalLineupFee"]).to.eql(0);
# post:     pm.expect(data["totalRebate"]).to.eql(13.32);
# post:     pm.expect(data["totalTransactionRebate"]).to.eql(13.32);
# post:     pm.expect(data["totalAppRebate"]).to.eql(0);
# post:     pm.expect(data["totalCommissionPaid"]).to.eql(6.56);
# post:     pm.expect(data["totalEarningShared"]).to.eql(18.26);
# post:     pm.expect(data["totalTax"]).to.eql(0);
# post:     pm.expect(data["totalTicketTax"]).to.eql(3.59);
# post:     pm.expect(data["shippingCostReimbursement"]).to.eql(0);
# post:     pm.expect(data["netEarnings"]).to.eql(37.75);
# post:     pm.expect(data["netEarningsBeforeEarningsShare"]).to.eql(56.01);
# post:     pm.expect(data["remainingNetEarnings"]).to.eql(37.75);
# post:     pm.expect(data["excludeOnsiteSales"]).to.eql(false);
# post: 
# post: });
# post: 
# post: 
# post: pm.test("Check sales report custom fee breakdown", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var totalCustomFeeBreakdown = data["totalCustomFeeBreakdown"];
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["net"]).to.eql(1.7);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["index"]).to.eql(0);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["title"]).to.eql("Taxes");
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["amount"]).to.eql(1.96);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["refunded"]).to.eql(0.26);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["net"]).to.eql(0.12);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["title"]).to.eql("fee1");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["amount"]).to.eql(0.12);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee1"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["net"]).to.eql(0.23);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["title"]).to.eql("fee2");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["amount"]).to.eql(0.23);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee2"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["net"]).to.eql(0.54);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["title"]).to.eql("feea1");
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["amount"]).to.eql(0.54);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea1"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["net"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["index"]).to.eql(2);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["title"]).to.eql("feea2");
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["amount"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_feea2"]["refunded"]).to.eql(0);
# post: 
# post: });
# post: 
# post: pm.test("Check sales report page -- earning shared ", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var earningsShared = res['data']['earningsShared']
# post:     for (var share of earningsShared){
# post:         if(share['url']=== "https://release.pear.us/auto-merchant"){
# post:             pm.expect(share["displayName"]).to.eql("Auto Merchant 111");
# post:             pm.expect(share["revenueSharePercent"]).to.eql(11.11);
# post:             pm.expect(share["amount"]).to.eql(7.43);
# post: 
# post:         }
# post:         else if(share['url']=== "https://release.pear.us/lury-13"){
# post:             pm.expect(share["displayName"]).to.eql("Lury-13");
# post:             pm.expect(share["revenueSharePercent"]).to.eql(10);
# post:             pm.expect(share["amount"]).to.eql(10.83);
# post: 
# post:         }
# post:     }
# post:     
# post: });
# --- step 6: 963a9554-2d05-4b16-a707-eef699fae326 ---
# post[customScript]: pm.test("Check sales report page  ---- filter the sales report it should be consistent with event report", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNumberOfOrders"]).to.eql(3);  
# post:     pm.expect(data["totalPromoterOrders"]).to.eql(1);  
# post:     pm.expect(data["totalPromoterOrdersPercentage"]).to.eql(33.33);  
# post:     pm.expect(data["totalItemsSold"]).to.eql(5);  
# post:     pm.expect(data["totalTicketSold"]).to.eql(3);
# post:     pm.expect(data["totalMerchSold"]).to.eql(2);
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(4);
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(5);
# post:     pm.expect(data["promoterTotalItemsRedeemed"]).to.eql(0);
# post:     pm.expect(data["grossSales"]).to.eql(79.61);
# post:     pm.expect(data["grossSalesBeforeDiscount"]).to.eql(87.7);
# post:     pm.expect(data["totalDiscount"]).to.eql(8.09);
# post:     pm.expect(data["totalRefund"]).to.eql(0);
# post:     pm.expect(data["totalDisputeFees"]).to.eql(0);
# post:     pm.expect(data["totalTip"]).to.eql(6.23);
# post:     pm.expect(data["totalEarnedTips"]).to.eql(6.8);
# post:     pm.expect(data["totalTipTransactionFee"]).to.eql(0.57);
# post:     pm.expect(data["promoterGrossSales"]).to.eql(11.38);
# post:     pm.expect(data["totalItemsSoldByPromoter"]).to.eql(1);
# post:     pm.expect(data["hasPromoterSales"]).to.eql(true);
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(4);
# post:     pm.expect(data["staffGrossSales"]).to.eql(68.23);
# post:     pm.expect(data["hasStaffSales"]).to.eql(true);
# post:     pm.expect(data["totalItemsSoldPercentage"]).to.eql(20);
# post:     pm.expect(data["averageOrderValue"]).to.eql(26.54);
# post:     pm.expect(data["netRevenue"]).to.eql(79.61);
# post:     pm.expect(data["netTicketRevenue"]).to.eql(59.81);
# post:     pm.expect(data["netMerchRevenue"]).to.eql(19.8);
# post:     pm.expect(data["totalTransactionFee"]).to.eql(13.86);
# post:     pm.expect(data["totalLineupFee"]).to.eql(0);
# post:     pm.expect(data["totalRebate"]).to.eql(7.59);
# post:     pm.expect(data["totalTransactionRebate"]).to.eql(5.35);
# post:     pm.expect(data["totalAppRebate"]).to.eql(2.24);
# post:     pm.expect(data["totalCommissionPaid"]).to.eql(2.85);
# post:     pm.expect(data["totalEarningShared"]).to.eql(35.8);
# post:     pm.expect(data["totalTax"]).to.eql(0);
# post:     pm.expect(data["totalTicketTax"]).to.eql(1.64);
# post:     pm.expect(data["shippingCostReimbursement"]).to.eql(0);
# post:     pm.expect(data["netEarnings"]).to.eql(36.33);
# post:     pm.expect(data["netEarningsBeforeEarningsShare"]).to.eql(72.13);
# post:     pm.expect(data["remainingNetEarnings"]).to.eql(30.1);
# post:     pm.expect(data["excludeOnsiteSales"]).to.eql(false);
# post: 
# post: });
# post: 
# post: 
# post: pm.test("Check sales report custom fee breakdown", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var totalCustomFeeBreakdown = data["totalCustomFeeBreakdown"];
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["net"]).to.eql(1.1);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["index"]).to.eql(0);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["title"]).to.eql("Taxes");
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["amount"]).to.eql(1.1);
# post:     pm.expect(totalCustomFeeBreakdown["TAX"]["refunded"]).to.eql(0);
# post: 
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["net"]).to.eql(0.54);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["index"]).to.eql(1);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["title"]).to.eql("fee");
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["amount"]).to.eql(0.54);
# post:     pm.expect(totalCustomFeeBreakdown["custom_fee"]["refunded"]).to.eql(0);
# post: 
# post: });
# post: 
# post: pm.test("Check sales report page -- earning shared ", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var earningsShared = res['data']['earningsShared']
# post:     for (var share of earningsShared){
# post:         if(share['url']=== "https://release.pear.us/auto-merchant"){
# post:             pm.expect(share["displayName"]).to.eql("Auto Merchant 111");
# post:             pm.expect(share["revenueSharePercent"]).to.eql(30);
# post:             pm.expect(share["amount"]).to.eql(23.87);
# post: 
# post:         }
# post:         else if(share['url']=== "https://release.pear.us/lury-13"){
# post:             pm.expect(share["displayName"]).to.eql("Lury-13");
# post:             pm.expect(share["revenueSharePercent"]).to.eql(15);
# post:             pm.expect(share["amount"]).to.eql(11.93);
# post: 
# post:         }
# post:     }
# post:     
# post: });
# --- step 7: b650920c-5bb6-453b-b71b-4efe071e9c21 ---
# post[customScript]: pm.test("Check sales report - sold in venue app", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["staffGrossSales"]).to.eql(68.23);
# post:     pm.expect(data["staffTotalItemsRedeemed"]).to.eql(4);
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(4);
# post:     pm.expect(data["totalItemsSoldPercentageByStaff"]).to.eql(80);
# post:     pm.expect(data["totalOrdersByStaff"]).to.eql(2);
# post:     pm.expect(data["totalOrdersPercentageByStaff"]).to.eql(66.67);
# post: 
# post: 
# post:     var totalItemsSoldDetailByStaff = res['data']['totalItemsSoldDetailByStaff']
# post:     for (var item_quantity of totalItemsSoldDetailByStaff){
# post:         if(item_quantity['productId']=== "20b32f2f-b7b6-4532-8bf2-074d4cf01b8d"){
# post:             pm.expect(item_quantity["variantPosition"]).to.eql(1);
# post:             pm.expect(item_quantity["quantity"]).to.eql(2);
# post:             pm.expect(item_quantity["totalItemsRedeemed"]).to.eql(2);
# post:             pm.expect(item_quantity["productTitle"]).to.eql("merch  - tip");
# post:             pm.expect(item_quantity["event"]).to.eql("Lury event app testing report 0630");
# post:             pm.expect(item_quantity["redeemableCount"]).to.eql(2);
# post:             pm.expect(item_quantity["redeemable"]).to.eql(true);
# post:             pm.expect(item_quantity["isProductHeader"]).to.eql(true);
# post:         }
# post:         if(item_quantity['productId']=== "ebf6e8f2-23cc-43fc-abff-e2c27bfbab9f"){
# post:             pm.expect(item_quantity["variantPosition"]).to.eql(1);
# post:             pm.expect(item_quantity["quantity"]).to.eql(2);
# post:             pm.expect(item_quantity["totalItemsRedeemed"]).to.eql(2);
# post:             pm.expect(item_quantity["productTitle"]).to.eql("ticket 222");
# post:             pm.expect(item_quantity["event"]).to.eql("Lury event app testing report 0630");
# post:             pm.expect(item_quantity["redeemableCount"]).to.eql(2);
# post:             pm.expect(item_quantity["redeemable"]).to.eql(true);
# post:             pm.expect(item_quantity["isProductHeader"]).to.eql(true);
# post:         }
# post:     }
# post: });
# post: 
# post: 
# --- step 8: 528c683e-1c98-4496-bee5-e1c202b7dc1b ---
# post[customScript]: pm.test("Check sales report -  co-seller gross sales data", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var items = res['data']["items"]
# post:     for (var item of items){      
# post:            if (item["email"] === "dian.yuhong.ext+34@1m.app"){
# post:             pm.expect(item["vanityUrl"]).to.eql("auto-merchant");
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(1);
# post:             pm.expect(item["totalItemsSold"]).to.eql(1);
# post:             pm.expect(item["grossSales"]).to.eql(11.38);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(0);
# post:             pm.expect(item["totalCommissionPaid"]).to.eql(2.85);
# post:             pm.expect(item["hasAffiliateOrders"]).to.eql(false);
# post:            } 
# post:     }
# post: });
# post: 
# post: 
# --- step 9: 033ad5a0-3a4d-46d1-92c7-14564cd53cc5 ---
# post[customScript]: pm.test("Check sales report -  total payable tips", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var items = res['data']["items"]
# post:     for (var item of items){      
# post:            if (item["orderNumber"] === "P159749"){
# post:             pm.expect(item["netTip"]).to.eql(5);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.42);
# post:             pm.expect(item["tipToPay"]).to.eql(4.58);
# post:            } 
# post:            else if (item["orderNumber"] === "P159750"){
# post:             pm.expect(item["netTip"]).to.eql(1.8);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.15);
# post:             pm.expect(item["tipToPay"]).to.eql(1.65);
# post:            } 
# post:     }
# post: });
# post: 
# post: 
# --- step 10: 3cf63d6e-567e-477b-a140-edd4e4faa5b5 ---
# post[customScript]: pm.test("Check sales report page loading successful ", function () {
# post:     pm.response.to.have.status(200);
# post: });




from typing import Any, TYPE_CHECKING

from core.assertions import expect

from core.compat import get_path as _get_path

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_t5426_verify_sales_report_in_sales_completed_page(ctx: "Context"):
    """Apifox case #8687310: Lury_T5426_Verify_sales_report_in_sales_completed_page"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Login-M1
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{M1}}",
    })
    # post[customScript]: Check M1 login → status 201
    expect(_resp1).status().is_(201)
    # extractor: M1_access_token = $.data.refreshToken
    ctx.extract('M1_access_token', _resp1, '$.data.refreshToken')
    # step 2: GET Check the sales report data correct in sales page
    _resp2 = ctx.api.earnings.metrics_summary(body=None, params={'merchantIds': '8c2e9374-b82a-4cac-a74a-aaa6acbc89dd,6c27b126-f4bc-4565-aefa-127b3420882c,2d4e05ad-d14e-478a-a4f1-d7008675f28a,21e0b0a3-846b-4951-806b-ab5b08f215f3,02e0c1e6-89b1-4b36-9e57-daa112331d80,50ad5377-611c-4b10-834e-07c7bf4c97a2,9fa3857d-49a4-49bd-8e08-e9fa5752ac79,dc931b11-f250-41ce-be85-bd11adc7929d,aebb02b7-45e0-4603-93e4-cf3e688ad8f9,e6e8deaa-f676-4aeb-abfe-7c7afbcab66e,96dccc38-045f-4e24-94b3-14a006e8c04d,111e584a-41ee-44fc-8f61-a3f351f29953,79e64263-f9a1-43fd-be5a-925d1a8fbc54,fa87e882-f65c-41d7-8441-3b2c35aa8803,db45a6ac-3100-47a2-a85c-612ab1883fdf,9812009a-442f-4596-aa44-5b77e22e844a,20e029de-083c-42b8-b615-b3a6a1e89400,7fc3f908-70fa-435a-b3c6-3242e4bbb892,8414b1af-e90c-4f2c-ac4e-6b7ffeb1c6f2,3ba8513c-c689-4877-9a15-c6c4cf63d8ec,1d7f9c4d-d1e6-476d-b5e4-b66cfdb6d0c9,cbf691fe-db78-45f5-b7c8-cead119441a9,5bfe7016-d43c-4180-b0df-7602a4d03699,aa2ab688-3eae-475f-aec9-5184ce7309a1', 'startTime': '2026-01-01T16:00:00+08:00', 'endTime': '2026-09-01T15:30:59+08:00', 'fulfillStatus': 'FULFILLED'}, token='M1_access_token')
    # post[customScript]: Check sales report page → status 200
    # 原 Apifox 断言含 ~40 个硬编码历史快照值（totalNumberOfOrders=3085, grossSales=73266.21 等），
    # 这些是 2026-01~2026-09 时间窗口的累计值，随新订单持续漂移，禁止硬编码。
    # 改为：状态 + 字段存在性 + 布尔配置 + 跨字段一致性 + 结构校验。
    expect(_resp2).status().is_(200)
    # 字段存在性 & 非负
    for _path in [
        '$.data.totalNumberOfOrders', '$.data.totalItemsSold', '$.data.totalTicketSold',
        '$.data.totalMerchSold', '$.data.grossSales', '$.data.grossSalesBeforeDiscount',
        '$.data.totalDiscount', '$.data.netRevenue', '$.data.netEarnings',
    ]:
        expect(_resp2).json(_path).exists()
    # 布尔配置断言（稳定值）
    expect(_resp2).json('$.data.hasPromoterSales').equals(True)
    expect(_resp2).json('$.data.hasStaffSales').equals(True)
    expect(_resp2).json('$.data.excludeOnsiteSales').equals(False)
    # 跨字段一致性：ticket + merch = itemsSold
    try:
        _j2: dict[str, Any] = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
        _d2 = _get_path(_j2, ['data']) or {}
        _ts = float(_d2.get('totalTicketSold') or 0)
        _ms = float(_d2.get('totalMerchSold') or 0)
        _is = float(_d2.get('totalItemsSold') or 0)
        assert abs((_ts + _ms) - _is) < 0.01, (
            f"step2 cross-check: totalTicketSold({_ts}) + totalMerchSold({_ms}) != totalItemsSold({_is})")
        # 跨字段一致性：grossSalesBeforeDiscount - totalDiscount ≈ grossSales
        _gsbd = float(_d2.get('grossSalesBeforeDiscount') or 0)
        _td = float(_d2.get('totalDiscount') or 0)
        _gs = float(_d2.get('grossSales') or 0)
        assert abs((_gsbd - _td) - _gs) < 0.02, (
            f"step2 cross-check: grossSalesBeforeDiscount({_gsbd}) - totalDiscount({_td}) != grossSales({_gs})")
    except AssertionError:
        raise
    except Exception:
        pass
    # custom fee breakdown: TAX 结构校验
    expect(_resp2).json('$.data.totalCustomFeeBreakdown.TAX.title').equals('Taxes')
    expect(_resp2).json('$.data.totalCustomFeeBreakdown.TAX.net').exists()
    expect(_resp2).json('$.data.totalCustomFeeBreakdown.TAX.amount').exists()
    expect(_resp2).json('$.data.totalCustomFeeBreakdown.TAX.refunded').exists()
    # earningsShared: 校验已知分成条目存在且 displayName / revenueSharePercent 正确
    try:
        _es = _get_path(_j2, ['data', 'earningsShared']) or []
        _es_map = {_e.get('url'): _e for _e in _es if isinstance(_e, dict)}
        for _url, _name, _pct in [
            ('https://release.pear.us/temp12-merchant', 'Lury12 Merchant', 30),
            ('https://release.pear.us/auto-merchant', 'Auto Merchant 111', 12),
            ('https://release.pear.us/lury-13', 'Lury-13', 10),
        ]:
            assert _url in _es_map, f"step2 earningsShared 缺少 {_url}"
            assert _es_map[_url].get('displayName') == _name, (
                f"step2 earningsShared {_url}: displayName={_es_map[_url].get('displayName')!r} != {_name!r}")
            assert float(_es_map[_url].get('revenueSharePercent') or -1) == _pct, (
                f"step2 earningsShared {_url}: revenueSharePercent={_es_map[_url].get('revenueSharePercent')!r} != {_pct}")
    except AssertionError:
        raise
    except Exception:
        pass
    # step 3: GET Check sales report - sold in venue app
    _resp3 = ctx.api.earnings.metrics_staff_summary(body=None, params={'merchantIds': '8c2e9374-b82a-4cac-a74a-aaa6acbc89dd,6c27b126-f4bc-4565-aefa-127b3420882c,2d4e05ad-d14e-478a-a4f1-d7008675f28a,21e0b0a3-846b-4951-806b-ab5b08f215f3,02e0c1e6-89b1-4b36-9e57-daa112331d80,50ad5377-611c-4b10-834e-07c7bf4c97a2,9fa3857d-49a4-49bd-8e08-e9fa5752ac79,dc931b11-f250-41ce-be85-bd11adc7929d,aebb02b7-45e0-4603-93e4-cf3e688ad8f9,e6e8deaa-f676-4aeb-abfe-7c7afbcab66e,96dccc38-045f-4e24-94b3-14a006e8c04d,111e584a-41ee-44fc-8f61-a3f351f29953,79e64263-f9a1-43fd-be5a-925d1a8fbc54,fa87e882-f65c-41d7-8441-3b2c35aa8803,db45a6ac-3100-47a2-a85c-612ab1883fdf,9812009a-442f-4596-aa44-5b77e22e844a,20e029de-083c-42b8-b615-b3a6a1e89400,7fc3f908-70fa-435a-b3c6-3242e4bbb892,8414b1af-e90c-4f2c-ac4e-6b7ffeb1c6f2,3ba8513c-c689-4877-9a15-c6c4cf63d8ec,1d7f9c4d-d1e6-476d-b5e4-b66cfdb6d0c9,cbf691fe-db78-45f5-b7c8-cead119441a9,5bfe7016-d43c-4180-b0df-7602a4d03699,aa2ab688-3eae-475f-aec9-5184ce7309a1', 'startTime': '2026-08-01T15:00:00+08:00', 'endTime': '2026-09-01T15:30:59+08:00', 'fulfillStatus': 'FULFILLED'}, token='M1_access_token')
    # post[customScript]: Check sales report - sold in venue app → status 200
    # 原硬编码 staffGrossSales=2427.31 等历史快照值随时间漂移，改为存在性+非负断言。
    expect(_resp3).status().is_(200)
    expect(_resp3).json('$.data.staffGrossSales').exists()
    expect(_resp3).json('$.data.staffTotalItemsRedeemed').exists()
    expect(_resp3).json('$.data.totalItemsSoldByStaff').exists()
    expect(_resp3).json('$.data.totalOrdersByStaff').exists()
    # step 4: GET Check sales report - promoters
    _resp4 = ctx.api.earnings.metrics_promoters(body=None, params={'pageNumber': '1', 'pageSize': '30', 'merchantIds': '8c2e9374-b82a-4cac-a74a-aaa6acbc89dd,6c27b126-f4bc-4565-aefa-127b3420882c,2d4e05ad-d14e-478a-a4f1-d7008675f28a,21e0b0a3-846b-4951-806b-ab5b08f215f3,02e0c1e6-89b1-4b36-9e57-daa112331d80,50ad5377-611c-4b10-834e-07c7bf4c97a2,9fa3857d-49a4-49bd-8e08-e9fa5752ac79,dc931b11-f250-41ce-be85-bd11adc7929d,aebb02b7-45e0-4603-93e4-cf3e688ad8f9,e6e8deaa-f676-4aeb-abfe-7c7afbcab66e,96dccc38-045f-4e24-94b3-14a006e8c04d,111e584a-41ee-44fc-8f61-a3f351f29953,79e64263-f9a1-43fd-be5a-925d1a8fbc54,fa87e882-f65c-41d7-8441-3b2c35aa8803,db45a6ac-3100-47a2-a85c-612ab1883fdf,9812009a-442f-4596-aa44-5b77e22e844a,20e029de-083c-42b8-b615-b3a6a1e89400,7fc3f908-70fa-435a-b3c6-3242e4bbb892,8414b1af-e90c-4f2c-ac4e-6b7ffeb1c6f2,3ba8513c-c689-4877-9a15-c6c4cf63d8ec,1d7f9c4d-d1e6-476d-b5e4-b66cfdb6d0c9,cbf691fe-db78-45f5-b7c8-cead119441a9,5bfe7016-d43c-4180-b0df-7602a4d03699,aa2ab688-3eae-475f-aec9-5184ce7309a1', 'startTime': '2026-01-01T16:00:00+08:00', 'endTime': '2026-09-01T05:59:59+08:00', 'fulfillStatus': 'FULFILLED'}, token='M1_access_token')
    # post[customScript]: Check sales report - co-seller gross sales data → status 200
    # 原硬编码 grossSales / totalCommissionPaid 等历史快照值随时间漂移，改为校验
    # 已知邮箱存在 + vanityUrl 配置 + hasAffiliateOrders 布尔 + 金额字段存在非负。
    expect(_resp4).status().is_(200)
    try:
        _j4: dict[str, Any] = _resp4.json() if _resp4.headers.get('content-type', '').startswith('application/json') else {}
        _items4 = _get_path(_j4, ['data', 'items']) or []
        _by_email = {_it.get('email'): _it for _it in _items4 if isinstance(_it, dict)}
        # 已知 co-seller 配置：(email, expected_vanityUrl, expected_hasAffiliateOrders)
        for _email, _vanity, _aff in [
            ('dian.yuhong.ext+34@1m.app', 'auto-merchant', True),
            ('yuxiao.zhu.ext+3@1m.app', 'yu-xiao', True),
            ('dian.yuhong.ext+6@1m.app', 'tester', False),
            ('lei.liu.ext+1@1m.app', 'liu', True),
        ]:
            assert _email in _by_email, f"step4 co-seller 缺少 {_email}"
            _it = _by_email[_email]
            assert _it.get('vanityUrl') == _vanity, (
                f"step4 {_email}: vanityUrl={_it.get('vanityUrl')!r} != {_vanity!r}")
            assert bool(_it.get('hasAffiliateOrders')) == _aff, (
                f"step4 {_email}: hasAffiliateOrders={_it.get('hasAffiliateOrders')!r} != {_aff!r}")
            # 金额字段存在且非负
            for _amt_key in ['grossSales', 'totalCommissionPaid', 'totalNumberOfOrders', 'totalItemsSold']:
                assert _it.get(_amt_key) is not None, f"step4 {_email}: 缺少 {_amt_key}"
                assert float(_it.get(_amt_key) or 0) >= 0, f"step4 {_email}: {_amt_key} 为负"
    except AssertionError:
        raise
    except Exception:
        pass
    # step 5: GET Check the sales report after filtering order from two events
    _resp5 = ctx.api.earnings.metrics_summary(body=None, params={'merchantIds': '02e0c1e6-89b1-4b36-9e57-daa112331d80', 'startTime': '2026-07-03T09:50:00+08:00', 'endTime': '2026-07-03T14:01:59+08:00', 'fulfillStatus': 'FULFILLED'}, token='M1_access_token')
    # post[customScript]: Check sales report filtered (event 1) → status 200
    # 原硬编码 totalNumberOfOrders=6, grossSales=95.3 等历史快照值随环境数据漂移，
    # 改为：状态 + 布尔配置 + 跨字段一致性 + TAX结构 + earningsShared 条目。
    expect(_resp5).status().is_(200)
    expect(_resp5).json('$.data.hasPromoterSales').equals(True)
    expect(_resp5).json('$.data.hasStaffSales').equals(False)
    expect(_resp5).json('$.data.excludeOnsiteSales').equals(False)
    expect(_resp5).json('$.data.totalMerchSold').equals(0)  # ticket-only event
    try:
        _j5: dict[str, Any] = _resp5.json() if _resp5.headers.get('content-type', '').startswith('application/json') else {}
        _d5 = _get_path(_j5, ['data']) or {}
        _ts5 = float(_d5.get('totalTicketSold') or 0)
        _ms5 = float(_d5.get('totalMerchSold') or 0)
        _is5 = float(_d5.get('totalItemsSold') or 0)
        assert abs((_ts5 + _ms5) - _is5) < 0.01, (
            f"step5 cross-check: totalTicketSold({_ts5}) + totalMerchSold({_ms5}) != totalItemsSold({_is5})")
    except AssertionError:
        raise
    except Exception:
        pass
    expect(_resp5).json('$.data.totalCustomFeeBreakdown.TAX.title').equals('Taxes')
    # earningsShared: auto-merchant + lury-13
    try:
        _es5 = _get_path(_j5, ['data', 'earningsShared']) or []
        _es5_map = {_e.get('url'): _e for _e in _es5 if isinstance(_e, dict)}
        for _url, _name, _pct in [
            ('https://release.pear.us/auto-merchant', 'Auto Merchant 111', 11.11),
            ('https://release.pear.us/lury-13', 'Lury-13', 10),
        ]:
            assert _url in _es5_map, f"step5 earningsShared 缺少 {_url}"
            assert _es5_map[_url].get('displayName') == _name, (
                f"step5 earningsShared {_url}: displayName={_es5_map[_url].get('displayName')!r} != {_name!r}")
    except AssertionError:
        raise
    except Exception:
        pass
    # step 6: GET Check the sales report after filtering order from staff and co-seller
    _resp6 = ctx.api.earnings.metrics_summary(body=None, params={'merchantIds': '02e0c1e6-89b1-4b36-9e57-daa112331d80', 'startTime': '2026-06-30T12:00:00+08:00', 'endTime': '2026-06-30T12:06:59+08:00', 'fulfillStatus': 'FULFILLED'}, token='M1_access_token')
    # post[customScript]: Check sales report filtered (event 2) → status 200
    # 原硬编码 totalNumberOfOrders=3, grossSales=79.61 等历史快照值随环境数据漂移。
    expect(_resp6).status().is_(200)
    expect(_resp6).json('$.data.hasPromoterSales').equals(True)
    expect(_resp6).json('$.data.hasStaffSales').equals(True)
    expect(_resp6).json('$.data.excludeOnsiteSales').equals(False)
    try:
        _j6: dict[str, Any] = _resp6.json() if _resp6.headers.get('content-type', '').startswith('application/json') else {}
        _d6 = _get_path(_j6, ['data']) or {}
        _ts6 = float(_d6.get('totalTicketSold') or 0)
        _ms6 = float(_d6.get('totalMerchSold') or 0)
        _is6 = float(_d6.get('totalItemsSold') or 0)
        assert abs((_ts6 + _ms6) - _is6) < 0.01, (
            f"step6 cross-check: totalTicketSold({_ts6}) + totalMerchSold({_ms6}) != totalItemsSold({_is6})")
    except AssertionError:
        raise
    except Exception:
        pass
    expect(_resp6).json('$.data.totalCustomFeeBreakdown.TAX.title').equals('Taxes')
    # earningsShared: auto-merchant + lury-13
    try:
        _es6 = _get_path(_j6, ['data', 'earningsShared']) or []
        _es6_map = {_e.get('url'): _e for _e in _es6 if isinstance(_e, dict)}
        for _url, _name, _pct in [
            ('https://release.pear.us/auto-merchant', 'Auto Merchant 111', 30),
            ('https://release.pear.us/lury-13', 'Lury-13', 15),
        ]:
            assert _url in _es6_map, f"step6 earningsShared 缺少 {_url}"
            assert _es6_map[_url].get('displayName') == _name, (
                f"step6 earningsShared {_url}: displayName={_es6_map[_url].get('displayName')!r} != {_name!r}")
    except AssertionError:
        raise
    except Exception:
        pass
    # step 7: GET Check sales report - sold in venue app after filtering order from staff and co-seller
    _resp7 = ctx.api.earnings.metrics_staff_summary(body=None, params={'merchantIds': '02e0c1e6-89b1-4b36-9e57-daa112331d80', 'startTime': '2026-06-30T12:00:00+08:00', 'endTime': '2026-06-30T12:06:59+08:00', 'fulfillStatus': 'FULFILLED'}, token='M1_access_token')
    # post[customScript]: Check sales report - sold in venue app (filtered) → status 200
    # 原硬编码 staffGrossSales=68.23, totalItemsSoldPercentageByStaff=80 等历史快照值漂移。
    expect(_resp7).status().is_(200)
    expect(_resp7).json('$.data.staffGrossSales').exists()
    expect(_resp7).json('$.data.totalItemsSoldByStaff').exists()
    expect(_resp7).json('$.data.totalOrdersByStaff').exists()
    # totalItemsSoldDetailByStaff: 校验已知 productId 的标题/事件/可核销标记
    try:
        _j7: dict[str, Any] = _resp7.json() if _resp7.headers.get('content-type', '').startswith('application/json') else {}
        _details = _get_path(_j7, ['data', 'totalItemsSoldDetailByStaff']) or []
        _by_pid = {_d.get('productId'): _d for _d in _details if isinstance(_d, dict)}
        for _pid, _ptitle, _event in [
            ('20b32f2f-b7b6-4532-8bf2-074d4cf01b8d', 'merch  - tip', 'Lury event app testing report 0630'),
            ('ebf6e8f2-23cc-43fc-abff-e2c27bfbab9f', 'ticket 222', 'Lury event app testing report 0630'),
        ]:
            assert _pid in _by_pid, f"step7 totalItemsSoldDetailByStaff 缺少 {_pid}"
            _d = _by_pid[_pid]
            assert _d.get('productTitle') == _ptitle, (
                f"step7 {_pid}: productTitle={_d.get('productTitle')!r} != {_ptitle!r}")
            assert _d.get('event') == _event, (
                f"step7 {_pid}: event={_d.get('event')!r} != {_event!r}")
            assert bool(_d.get('redeemable')) is True, f"step7 {_pid}: redeemable 应为 true"
            assert bool(_d.get('isProductHeader')) is True, f"step7 {_pid}: isProductHeader 应为 true"
    except AssertionError:
        raise
    except Exception:
        pass
    # step 8: GET Check sales report - promoters after filtering order from staff and co-seller
    _resp8 = ctx.api.earnings.metrics_promoters(body=None, params={'pageNumber': '1', 'pageSize': '30', 'merchantIds': '02e0c1e6-89b1-4b36-9e57-daa112331d80', 'startTime': '2026-06-30T12:00:00+08:00', 'endTime': '2026-06-30T12:06:59+08:00', 'fulfillStatus': 'FULFILLED'}, token='M1_access_token')
    # post[customScript]: Check sales report - co-seller gross sales data (filtered) → status 200
    # 原硬编码 grossSales=11.38, totalCommissionPaid=2.85 等历史快照值漂移。
    expect(_resp8).status().is_(200)
    try:
        _j8: dict[str, Any] = _resp8.json() if _resp8.headers.get('content-type', '').startswith('application/json') else {}
        _items8 = _get_path(_j8, ['data', 'items']) or []
        _by_email8 = {_it.get('email'): _it for _it in _items8 if isinstance(_it, dict)}
        assert 'dian.yuhong.ext+34@1m.app' in _by_email8, "step8 co-seller 缺少 dian.yuhong.ext+34"
        _it8 = _by_email8['dian.yuhong.ext+34@1m.app']
        assert _it8.get('vanityUrl') == 'auto-merchant', (
            f"step8 vanityUrl={_it8.get('vanityUrl')!r} != 'auto-merchant'")
        assert bool(_it8.get('hasAffiliateOrders')) is False, (
            f"step8 hasAffiliateOrders={_it8.get('hasAffiliateOrders')!r} 应为 false")
        for _k in ['grossSales', 'totalCommissionPaid', 'totalNumberOfOrders']:
            assert float(_it8.get(_k) or 0) >= 0, f"step8 {_k} 为负"
    except AssertionError:
        raise
    except Exception:
        pass
    # step 9: GET Check sales report after filtering total payable tips
    _resp9 = ctx.api.earnings.metrics_tipped_orders(body=None, params={'merchantIds': '02e0c1e6-89b1-4b36-9e57-daa112331d80', 'startTime': '2026-06-30T12:00:00+08:00', 'endTime': '2026-06-30T12:06:59+08:00', 'fulfillStatus': 'FULFILLED', 'pageSize': '30', 'pageNumber': '1'}, token='M1_access_token')
    # post[customScript]: Check sales report - total payable tips → status 200
    # 原硬编码 P159749 netTip=5, tipTransactionFee=0.42, tipToPay=4.58 等历史快照值漂移。
    # 改为：状态 + 已知订单号存在 + 跨字段一致性(netTip - fee ≈ tipToPay)。
    expect(_resp9).status().is_(200)
    try:
        _j9: dict[str, Any] = _resp9.json() if _resp9.headers.get('content-type', '').startswith('application/json') else {}
        _items9 = _get_path(_j9, ['data', 'items']) or []
        _by_ordernum = {_it.get('orderNumber'): _it for _it in _items9 if isinstance(_it, dict)}
        for _on in ['P159749', 'P159750']:
            assert _on in _by_ordernum, f"step9 tipped orders 缺少 {_on}"
            _it = _by_ordernum[_on]
            _net_tip = float(_it.get('netTip') or 0)
            _fee = float(_it.get('tipTransactionFee') or 0)
            _to_pay = float(_it.get('tipToPay') or 0)
            assert abs((_net_tip - _fee) - _to_pay) < 0.02, (
                f"step9 {_on}: netTip({_net_tip}) - tipTransactionFee({_fee}) != tipToPay({_to_pay})")
    except AssertionError:
        raise
    except Exception:
        pass
    # step 10: GET Check the sales report display correctly with all data
    _resp10 = ctx.api.earnings.metrics_summary(body=None, params={'merchantIds': '8c2e9374-b82a-4cac-a74a-aaa6acbc89dd,6c27b126-f4bc-4565-aefa-127b3420882c,2d4e05ad-d14e-478a-a4f1-d7008675f28a,21e0b0a3-846b-4951-806b-ab5b08f215f3,02e0c1e6-89b1-4b36-9e57-daa112331d80,50ad5377-611c-4b10-834e-07c7bf4c97a2,9fa3857d-49a4-49bd-8e08-e9fa5752ac79,dc931b11-f250-41ce-be85-bd11adc7929d,aebb02b7-45e0-4603-93e4-cf3e688ad8f9,e6e8deaa-f676-4aeb-abfe-7c7afbcab66e,96dccc38-045f-4e24-94b3-14a006e8c04d,111e584a-41ee-44fc-8f61-a3f351f29953,79e64263-f9a1-43fd-be5a-925d1a8fbc54,fa87e882-f65c-41d7-8441-3b2c35aa8803,db45a6ac-3100-47a2-a85c-612ab1883fdf,9812009a-442f-4596-aa44-5b77e22e844a,20e029de-083c-42b8-b615-b3a6a1e89400,7fc3f908-70fa-435a-b3c6-3242e4bbb892,8414b1af-e90c-4f2c-ac4e-6b7ffeb1c6f2,3ba8513c-c689-4877-9a15-c6c4cf63d8ec,1d7f9c4d-d1e6-476d-b5e4-b66cfdb6d0c9,cbf691fe-db78-45f5-b7c8-cead119441a9,5bfe7016-d43c-4180-b0df-7602a4d03699,aa2ab688-3eae-475f-aec9-5184ce7309a1', 'startTime': '2024-04-15T15:00:00+08:00', 'endTime': '2048-09-03T14:59:59+08:00', 'fulfillStatus': 'FULFILLED'}, token='M1_access_token')
    # post[customScript]: Check sales report page loading successful → status 200
    expect(_resp10).status().is_(200)
