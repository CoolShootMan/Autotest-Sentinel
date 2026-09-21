"""Migrated from Apifox case #8503325. Source folder: Event Report."""
# Apifox Case ID: 8503325  (traceability only — not needed to run)
NAME = "(Lury)KAT-11581 Verify all data are correct in event report if sold by Venue App"
TAGS = ["p0", "event_report", "suite:lury"]
PRIORITY = 0


CASE_ID = 8503325
ENV_NAME = "Release"

# --- step 1: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 2: 2e243101-2328-4a76-8473-39dde92c6a5b ---
# post[customScript]: pm.test("Check sales event report page -  gross sales", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["grossSalesBeforeDiscount"]).to.eql(1679.19);  // gross sales before promotion
# post:     pm.expect(data["totalDiscount"]).to.eql(0);  // promotion
# post:     pm.expect(data["grossSales"]).to.eql(1679.19);   // gross sales
# post:     pm.expect(data["totalRefund"]).to.eql(154.06);  // total refund
# post: });
# post: 
# post: 
# post:     // Net revenue
# post: pm.test("Check sales event report page -  net revenue", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["netRevenue"]).to.eql(1525.13);               // Total net reveue
# post:     pm.expect(data["netTicketRevenue"]).to.eql(377.13);           // Total ticket net revenue
# post:     pm.expect(data["netMerchRevenue"]).to.eql(1148);          // Total merch net revenue
# post:     pm.expect(data["totalCommissionPaid"]).to.eql(0);  // Total commission
# post:     pm.expect(data["totalTransactionFee"]).to.eql(207.82); // Total transaction fees
# post: 
# post: //tax, custom fee and rebate
# post:     pm.expect(data["totalCustomFeeBreakdown"]["TAX"]["net"]).to.eql(9.67);   // Total taxes
# post:     pm.expect(data["totalCustomFeeBreakdown"]["custom_fee1"]["net"]).to.eql(6.45);  // Total custom fee1
# post:     pm.expect(data["totalRebate"]).to.eql(104.56);   // Total rebate
# post:     pm.expect(data["totalTransactionRebate"]).to.eql(33.7);  // Total transaction rebate
# post:     pm.expect(data["totalAppRebate"]).to.eql(70.86);   // Total app rebate
# post: 
# post:     //total revenue share
# post:     pm.expect(data["totalEarningShared"]).to.eql(0);   //total revenue  share
# post: 
# post: });
# post: 
# post: pm.test("Check sales event report page -  Net earnings and tip", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["netEarnings"]).to.eql(1437.99);  // net earning
# post:     pm.expect(data["remainingNetEarnings"]).to.eql(1252.71);  // remaining net earnings
# post:     pm.expect(data["totalEarnedTips"]).to.eql(202.85);   //total tip earned
# post:     pm.expect(data["totalTip"]).to.eql(185.28);  // total tip
# post:     pm.expect(data["totalTipTransactionFee"]).to.eql(17.57);  // total tip fee
# post:     pm.expect(data["averageOrderValue"]).to.eql(88.38);  // Average order value
# post: });
# post: 
# post: pm.test("Check sales event report page -  number of sold", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNumberOfOrders"]).to.eql(19);  // total number of or orders
# post:     pm.expect(data["totalItemsSold"]).to.eql(26);  // total item sold
# post:     pm.expect(data["totalTicketSold"]).to.eql(15);   //total ticket sold
# post:     pm.expect(data["totalMerchSold"]).to.eql(11);  // total merch sold
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(24);  // total item redeemed
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(24);  // total item redeemable
# post: 
# post: });
# post: 
# post: pm.test("Check sales event report page -  co-selling commission sales", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["promoterGrossSales"]).to.eql(0);  // promoter gross sales
# post:     pm.expect(data["totalItemsSoldByPromoter"]).to.eql(0);  // total item sold by promoter
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(26);   //total item sold by staff
# post:     pm.expect(data["totalItemsSoldPercentage"]).to.eql(0);  // total item sold by promoter percentage
# post:     pm.expect(data["promoterTotalItemsRedeemed"]).to.eql(0);  // total item sold by promoter redeemed 
# post: });
# post: 
# post: 
# post: pm.test("Check sales event report page -  total sold view details", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var totalItemsSoldDetail = data["totalItemsSoldDetail"];
# post: 
# post:     for (var total_details of totalItemsSoldDetail){       //view total sold details
# post:            if (total_details["productId"] === "31dd45f0-5096-4b2f-9b7f-135dc5b8e581"){
# post:             pm.expect(total_details["totalItemsRedeemed"]).to.eql(10);
# post:             pm.expect(total_details["productTitle"]).to.eql("Merch - tip");
# post:             pm.expect(total_details["quantity"]).to.eql(11);
# post:             pm.expect(total_details["event"]).to.eql("Lury event app tip testing");
# post:             pm.expect(total_details["redeemableCount"]).to.eql(10);
# post:            }
# post:            else if(total_details["productId"] === "71e1a9de-cc72-42c7-a138-a68c306000b6"){
# post:             pm.expect(total_details["totalItemsRedeemed"]).to.eql(4);
# post:             pm.expect(total_details["productTitle"]).to.eql("ticket 3");
# post:             pm.expect(total_details["quantity"]).to.eql(4);
# post:             pm.expect(total_details["event"]).to.eql("Lury event app tip testing");
# post:             pm.expect(total_details["redeemableCount"]).to.eql(4);
# post:            }
# post:            else if(total_details["productId"] === "84ca33f0-49f4-4565-82c3-d691cec864d8"){
# post:             pm.expect(total_details["totalItemsRedeemed"]).to.eql(6);
# post:             pm.expect(total_details["productTitle"]).to.eql("ticket 1");
# post:             pm.expect(total_details["quantity"]).to.eql(6);
# post:             pm.expect(total_details["event"]).to.eql("Lury event app tip testing");
# post:             pm.expect(total_details["redeemableCount"]).to.eql(6);
# post:            }
# post:            else if(total_details["productId"] === "a0b826d8-a96d-42e6-9da6-569fea72ee42"){
# post:             pm.expect(total_details["totalItemsRedeemed"]).to.eql(4);
# post:             pm.expect(total_details["productTitle"]).to.eql("ticket 2");
# post:             pm.expect(total_details["quantity"]).to.eql(5);
# post:             pm.expect(total_details["event"]).to.eql("Lury event app tip testing");
# post:             pm.expect(total_details["redeemableCount"]).to.eql(4);
# post:            }
# post:     }
# post: 
# post: 
# post: });
# --- step 3: 27b4004b-4e5a-4905-8ff2-4dfdf571c44e ---
# post[customScript]: pm.test("Check sales event report page -  satff gross sales data", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["staffGrossSales"]).to.eql(1679.19);  // gross sales from staff
# post:     pm.expect(data["staffTotalItemsRedeemed"]).to.eql(24);  // total item redeemed sold by staff
# post:     pm.expect(data["totalItemsSoldByStaff"]).to.eql(26);   // total item sold by staff
# post:     pm.expect(data["totalItemsSoldPercentageByStaff"]).to.eql(100);  // item sold by staff percentage
# post:     pm.expect(data["totalOrdersByStaff"]).to.eql(19);  // total order sold by staff
# post:     pm.expect(data["totalOrdersPercentageByStaff"]).to.eql(100);  // order sold by staff percentage
# post: });
# post: 
# post: 
# --- step 4: 3cbe8184-1909-483f-b1e0-43c87cbbca23 ---
# post[customScript]: pm.test("Check sales event report page -  satff gross sales data", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var items = res['data']["items"]
# post:     for (var item of items){       //view each staff details
# post:            if (item["id"] === "ow222"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(3);
# post:             pm.expect(item["totalItemsSold"]).to.eql(6);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(4);
# post:             pm.expect(item["totalTipToPay"]).to.eql(53.1);
# post:             pm.expect(item["grossSales"]).to.eql(413.69);
# post:            }
# post:            else if(item["id"] === "ad222"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(2);
# post:             pm.expect(item["totalItemsSold"]).to.eql(3);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(3);
# post:             pm.expect(item["totalTipToPay"]).to.eql(6.09);
# post:             pm.expect(item["grossSales"]).to.eql(144.29);
# post:            }
# post:            else if(item["id"] === "lury"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(2);
# post:             pm.expect(item["totalItemsSold"]).to.eql(3);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(3);
# post:             pm.expect(item["totalTipToPay"]).to.eql(25.62);
# post:             pm.expect(item["grossSales"]).to.eql(202.1);
# post:            }
# post:            else if(item["id"] === "lury2"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(2);
# post:             pm.expect(item["totalItemsSold"]).to.eql(3);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(3);
# post:             pm.expect(item["totalTipToPay"]).to.eql(24.61);
# post:             pm.expect(item["grossSales"]).to.eql(176.29);
# post:            }
# post:            else if(item["id"] === "op111"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(3);
# post:             pm.expect(item["totalItemsSold"]).to.eql(3);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(3);
# post:             pm.expect(item["totalTipToPay"]).to.eql(37.52);
# post:             pm.expect(item["grossSales"]).to.eql(253.94);
# post:            }
# post:            else if(item["id"] === "ow111"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(2);
# post:             pm.expect(item["totalItemsSold"]).to.eql(3);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(3);
# post:             pm.expect(item["totalTipToPay"]).to.eql(14.6);
# post:             pm.expect(item["grossSales"]).to.eql(188.86);
# post:            }
# post:            else if(item["id"] === "ad111"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(2);
# post:             pm.expect(item["totalItemsSold"]).to.eql(2);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(2);
# post:             pm.expect(item["totalTipToPay"]).to.eql(18.74);
# post:             pm.expect(item["grossSales"]).to.eql(156.93);
# post:            }
# post:            else if(item["id"] === "op222"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(2);
# post:             pm.expect(item["totalItemsSold"]).to.eql(2);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(2);
# post:             pm.expect(item["totalTipToPay"]).to.eql(5);
# post:             pm.expect(item["grossSales"]).to.eql(130.15);
# post:            }
# post:            else if(item["id"] === "test"){
# post:             pm.expect(item["totalNumberOfOrders"]).to.eql(1);
# post:             pm.expect(item["totalItemsSold"]).to.eql(1);
# post:             pm.expect(item["totalItemsRedeemed"]).to.eql(1);
# post:             pm.expect(item["totalTipToPay"]).to.eql(0);
# post:             pm.expect(item["grossSales"]).to.eql(12.94);
# post:            }
# post: 
# post:     }
# post: });
# post: 
# post: 
# --- step 5: 4cdd7fbb-9c00-40f7-8a20-0d7883dfe4fe ---
# post[customScript]: pm.test("Check sales event report page -  satff gross sales data", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var items = res['data']["items"]
# post:     for (var item of items){       //view each staff details
# post:            if (item["orderNumber"] === "P158482"){
# post:             pm.expect(item["netTip"]).to.eql(36);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(3.06);
# post:             pm.expect(item["tipToPay"]).to.eql(32.94);
# post:            }
# post:            else if(item["orderNumber"] === "P158504"){
# post:             pm.expect(item["netTip"]).to.eql(22.45);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(1.9);
# post:             pm.expect(item["tipToPay"]).to.eql(20.55);
# post:            }
# post:            else if(item["orderNumber"] === "P158500"){
# post:             pm.expect(item["netTip"]).to.eql(18);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(1.53);
# post:             pm.expect(item["tipToPay"]).to.eql(16.47);
# post:            }
# post:            else if(item["orderNumber"] === "P158488"){
# post:             pm.expect(item["netTip"]).to.eql(18);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(1.53);
# post:             pm.expect(item["tipToPay"]).to.eql(16.47);
# post:            }
# post:            else if(item["orderNumber"] === "P158443"){
# post:             pm.expect(item["netTip"]).to.eql(18);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(1.53);
# post:             pm.expect(item["tipToPay"]).to.eql(16.47);
# post:            }
# post:            else if(item["orderNumber"] === "P158441"){
# post:             pm.expect(item["netTip"]).to.eql(18);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(1.53);
# post:             pm.expect(item["tipToPay"]).to.eql(16.47);
# post:            }
# post:            else if(item["orderNumber"] === "P158449"){
# post:             pm.expect(item["netTip"]).to.eql(15);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(1.27);
# post:             pm.expect(item["tipToPay"]).to.eql(13.73);
# post:            }
# post:            else if(item["orderNumber"] === "P158473"){
# post:             pm.expect(item["netTip"]).to.eql(10.94);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.92);
# post:             pm.expect(item["tipToPay"]).to.eql(10.02);
# post:            }
# post:            else if(item["orderNumber"] === "P158499"){
# post:             pm.expect(item["netTip"]).to.eql(10);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.85);
# post:             pm.expect(item["tipToPay"]).to.eql(9.15);
# post:            }
# post:            else if(item["orderNumber"] === "P158487"){
# post:             pm.expect(item["netTip"]).to.eql(8.89);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.75);
# post:             pm.expect(item["tipToPay"]).to.eql(8.14);
# post:            }
# post:            else if(item["orderNumber"] === "P158454"){
# post:             pm.expect(item["netTip"]).to.eql(5.65);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.48);
# post:             pm.expect(item["tipToPay"]).to.eql(5.17);
# post:            }
# post:            else if(item["orderNumber"] === "P158448"){
# post:             pm.expect(item["netTip"]).to.eql(5.47);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.46);
# post:             pm.expect(item["tipToPay"]).to.eql(5.01);
# post:            }
# post:            else if(item["orderNumber"] === "P158463"){
# post:             pm.expect(item["netTip"]).to.eql(5);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.42);
# post:             pm.expect(item["tipToPay"]).to.eql(4.58);
# post:            }
# post:            else if(item["orderNumber"] === "P158438"){
# post:             pm.expect(item["netTip"]).to.eql(5);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.42);
# post:             pm.expect(item["tipToPay"]).to.eql(4.58);
# post:            }
# post:            else if(item["orderNumber"] === "P158478"){
# post:             pm.expect(item["netTip"]).to.eql(0);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.39);
# post:             pm.expect(item["tipToPay"]).to.eql(-0.39);
# post:            }
# post:            else if(item["orderNumber"] === "P158445"){
# post:             pm.expect(item["netTip"]).to.eql(4.45);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.37);
# post:             pm.expect(item["tipToPay"]).to.eql(4.08);
# post:            }
# post:            else if(item["orderNumber"] === "P158459"){
# post:             pm.expect(item["netTip"]).to.eql(1);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.08);
# post:             pm.expect(item["tipToPay"]).to.eql(0.92);
# post:            }
# post:            else if(item["orderNumber"] === "P158446"){
# post:             pm.expect(item["netTip"]).to.eql(1);
# post:             pm.expect(item["tipTransactionFee"]).to.eql(0.08);
# post:             pm.expect(item["tipToPay"]).to.eql(0.92);
# post:            }
# post:            
# post:     }
# post: });
# post: 
# post: 
# --- step 6: 6e848201-ab1a-429c-88cd-3a0f1d780d9f ---
# post[customScript]: pm.test("Check sales - orders page total net earnings", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNetEarnings"]).to.eql(1437.99);  
# post:     pm.expect(data["totalCurrentEventNetEarnings"]).to.eql(1437.99);  
# post:     pm.expect(data["totalCurrentEventFilteredNetEarnings"]).to.eql(1437.99);   
# post:     pm.expect(data["totalOtherEventNetEarnings"]).to.eql(0);  
# post:     pm.expect(data["totalOrders"]).to.eql(19);  
# post:     pm.expect(data["totalItems"]).to.eql(26);  
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(24);  
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(24);  
# post: 
# post: });
# --- step 7: c6512f91-9d3e-42cd-a20f-9b40268803ba ---
# post[customScript]: pm.test("Check sales - orders page total net earnings after filtering by ticket 2", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["totalNetEarnings"]).to.eql(194.31);  
# post:     pm.expect(data["totalCurrentEventNetEarnings"]).to.eql(194.31);  
# post:     pm.expect(data["totalCurrentEventFilteredNetEarnings"]).to.eql(115.16);   
# post:     pm.expect(data["totalOtherEventNetEarnings"]).to.eql(0);  
# post:     pm.expect(data["totalOrders"]).to.eql(5);  
# post:     pm.expect(data["totalItems"]).to.eql(9);  
# post:     pm.expect(data["totalRedeemableItems"]).to.eql(7);  
# post:     pm.expect(data["totalItemsRedeemed"]).to.eql(7);  
# post: 
# post: });




from typing import Any, TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_kat_11581_verify_all_data_are_correct_in_event_report_if_sold_by_venue_app(ctx: "Context"):
    """Apifox case #8503325: Lury_KAT_11581_Verify_all_data_are_correct_in_event_report_if_sold_by_Venue_App"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Login-M1
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{M1}}",
    })
    # extractor: M1_access_token = $.data.token
    ctx.extract('M1_access_token', _resp1, '$.data.token')
    # step 2: GET Check the event report data correct
    _resp2 = ctx.api.events.bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_summary(body=None, token='M1_access_token')
    # step 3: GET Check the event report - staff gross sales data
    _resp3 = ctx.api.events.bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_staff_summary(body=None, token='M1_access_token')
    # step 4: GET Check the event report - staff details info
    _resp4 = ctx.api.events.bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_staff(body=None, params={'pageNumber': '1', 'pageSize': '30'}, token='M1_access_token')
    # step 5: GET Check the event report - view total payable tips
    _resp5 = ctx.api.events.bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_tipped_orders(body=None, params={'pageSize': '30', 'pageNumber': '1'}, token='M1_access_token')
    # step 6: GET Check the sales > orders page date is correct
    _resp6 = ctx.api.events.bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_orders_summary(body=None, params={'dateText': 'Custom', 'productIds': '84ca33f0-49f4-4565-82c3-d691cec864d8,a0b826d8-a96d-42e6-9da6-569fea72ee42,71e1a9de-cc72-42c7-a138-a68c306000b6,31dd45f0-5096-4b2f-9b7f-135dc5b8e581'}, token='M1_access_token')
    # step 7: GET Check the sales > orders page date is correct after filtering by ticket2
    _resp7 = ctx.api.events.bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_orders_summary(body=None, params={'dateText': 'Custom', 'productIds': 'a0b826d8-a96d-42e6-9da6-569fea72ee42'}, token='M1_access_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    # step 1: Login-M1
    expect(_resp1).status().is_(201)
    # step 2: metrics summary
    expect(_resp2).status().is_(200)
    _j2: dict[str, Any] = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    _d2: dict[str, Any] = _j2.get('data') or {}
    # gross sales
    expect(_resp2).json('$.data.grossSalesBeforeDiscount').close_to(1679.19)
    expect(_resp2).json('$.data.totalDiscount').close_to(0)
    expect(_resp2).json('$.data.grossSales').close_to(1679.19)
    expect(_resp2).json('$.data.totalRefund').close_to(154.06)
    # net revenue
    expect(_resp2).json('$.data.netRevenue').close_to(1525.13)
    expect(_resp2).json('$.data.netTicketRevenue').close_to(377.13)
    expect(_resp2).json('$.data.netMerchRevenue').close_to(1148)
    expect(_resp2).json('$.data.totalCommissionPaid').close_to(0)
    expect(_resp2).json('$.data.totalTransactionFee').close_to(207.82)
    # tax / rebate
    expect(_resp2).json('$.data.totalCustomFeeBreakdown.TAX.net').close_to(9.67)
    expect(_resp2).json('$.data.totalCustomFeeBreakdown.custom_fee1.net').close_to(6.45)
    expect(_resp2).json('$.data.totalRebate').close_to(104.56)
    expect(_resp2).json('$.data.totalTransactionRebate').close_to(33.7)
    expect(_resp2).json('$.data.totalAppRebate').close_to(70.86)
    expect(_resp2).json('$.data.totalEarningShared').close_to(0)
    # net earnings and tip
    expect(_resp2).json('$.data.netEarnings').close_to(1437.99)
    expect(_resp2).json('$.data.remainingNetEarnings').close_to(1252.71)
    expect(_resp2).json('$.data.totalEarnedTips').close_to(202.85)
    expect(_resp2).json('$.data.totalTip').close_to(185.28)
    expect(_resp2).json('$.data.totalTipTransactionFee').close_to(17.57)
    expect(_resp2).json('$.data.averageOrderValue').close_to(88.38)
    # number of sold
    expect(_resp2).json('$.data.totalNumberOfOrders').equals(19)
    expect(_resp2).json('$.data.totalItemsSold').equals(26)
    expect(_resp2).json('$.data.totalTicketSold').equals(15)
    expect(_resp2).json('$.data.totalMerchSold').equals(11)
    expect(_resp2).json('$.data.totalItemsRedeemed').equals(24)
    expect(_resp2).json('$.data.totalRedeemableItems').equals(24)
    # co-selling commission sales
    expect(_resp2).json('$.data.promoterGrossSales').close_to(0)
    expect(_resp2).json('$.data.totalItemsSoldByPromoter').equals(0)
    expect(_resp2).json('$.data.totalItemsSoldByStaff').equals(26)
    expect(_resp2).json('$.data.totalItemsSoldPercentage').equals(0)
    expect(_resp2).json('$.data.promoterTotalItemsRedeemed').equals(0)
    # total sold view details (by productId)
    _exp_details = {
        '31dd45f0-5096-4b2f-9b7f-135dc5b8e581': (10, 'Merch - tip', 11, 'Lury event app tip testing', 10),
        '71e1a9de-cc72-42c7-a138-a68c306000b6': (4, 'ticket 3', 4, 'Lury event app tip testing', 4),
        '84ca33f0-49f4-4565-82c3-d691cec864d8': (6, 'ticket 1', 6, 'Lury event app tip testing', 6),
        'a0b826d8-a96d-42e6-9da6-569fea72ee42': (4, 'ticket 2', 5, 'Lury event app tip testing', 4),
    }
    for _td in _d2.get('totalItemsSoldDetail') or []:
        _pk = _td.get('productId')
        if _pk in _exp_details:
            _red, _title, _qty, _evt, _rc = _exp_details[_pk]
            assert _td.get('totalItemsRedeemed') == _red, f"{_pk}.redeemed={_td.get('totalItemsRedeemed')!r}"
            assert _td.get('productTitle') == _title, f"{_pk}.title={_td.get('productTitle')!r}"
            assert _td.get('quantity') == _qty, f"{_pk}.qty={_td.get('quantity')!r}"
            assert _td.get('event') == _evt, f"{_pk}.event={_td.get('event')!r}"
            assert _td.get('redeemableCount') == _rc, f"{_pk}.redeemableCount={_td.get('redeemableCount')!r}"
    # step 3: staff gross sales summary
    expect(_resp3).status().is_(200)
    expect(_resp3).json('$.data.staffGrossSales').close_to(1679.19)
    expect(_resp3).json('$.data.staffTotalItemsRedeemed').equals(24)
    expect(_resp3).json('$.data.totalItemsSoldByStaff').equals(26)
    expect(_resp3).json('$.data.totalItemsSoldPercentageByStaff').equals(100)
    expect(_resp3).json('$.data.totalOrdersByStaff').equals(19)
    expect(_resp3).json('$.data.totalOrdersPercentageByStaff').equals(100)
    # step 4: staff detail list (by staff id)
    expect(_resp4).status().is_(200)
    _j4: dict[str, Any] = _resp4.json() if _resp4.headers.get('content-type', '').startswith('application/json') else {}
    _staff_exp = {
        'ow222': (3, 6, 4, 53.1, 413.69),
        'ad222': (2, 3, 3, 6.09, 144.29),
        'lury': (2, 3, 3, 25.62, 202.1),
        'lury2': (2, 3, 3, 24.61, 176.29),
        'op111': (3, 3, 3, 37.52, 253.94),
        'ow111': (2, 3, 3, 14.6, 188.86),
        'ad111': (2, 2, 2, 18.74, 156.93),
        'op222': (2, 2, 2, 5, 130.15),
        'test': (1, 1, 1, 0, 12.94),
    }
    for _it in (_j4.get('data') or {}).get('items') or []:
        _sid = _it.get('id')
        if _sid in _staff_exp:
            _no, _is, _ir, _tip, _gs = _staff_exp[_sid]
            assert _it.get('totalNumberOfOrders') == _no, f"{_sid}.orders={_it.get('totalNumberOfOrders')!r}"
            assert _it.get('totalItemsSold') == _is, f"{_sid}.sold={_it.get('totalItemsSold')!r}"
            assert _it.get('totalItemsRedeemed') == _ir, f"{_sid}.redeemed={_it.get('totalItemsRedeemed')!r}"
            assert abs((_it.get('totalTipToPay') or 0) - _tip) < 0.01, f"{_sid}.tipToPay={_it.get('totalTipToPay')!r}"
            assert abs((_it.get('grossSales') or 0) - _gs) < 0.01, f"{_sid}.grossSales={_it.get('grossSales')!r}"
    # step 5: tipped orders list (by orderNumber)
    expect(_resp5).status().is_(200)
    _j5: dict[str, Any] = _resp5.json() if _resp5.headers.get('content-type', '').startswith('application/json') else {}
    _tip_exp = {
        'P158482': (36, 3.06, 32.94), 'P158504': (22.45, 1.9, 20.55),
        'P158500': (18, 1.53, 16.47), 'P158488': (18, 1.53, 16.47),
        'P158443': (18, 1.53, 16.47), 'P158441': (18, 1.53, 16.47),
        'P158449': (15, 1.27, 13.73), 'P158473': (10.94, 0.92, 10.02),
        'P158499': (10, 0.85, 9.15), 'P158487': (8.89, 0.75, 8.14),
        'P158454': (5.65, 0.48, 5.17), 'P158448': (5.47, 0.46, 5.01),
        'P158463': (5, 0.42, 4.58), 'P158438': (5, 0.42, 4.58),
        'P158478': (0, 0.39, -0.39), 'P158445': (4.45, 0.37, 4.08),
        'P158459': (1, 0.08, 0.92), 'P158446': (1, 0.08, 0.92),
    }
    for _it in (_j5.get('data') or {}).get('items') or []:
        _on = _it.get('orderNumber')
        if _on in _tip_exp:
            _nt, _ttf, _ttp = _tip_exp[_on]
            assert abs((_it.get('netTip') or 0) - _nt) < 0.01, f"{_on}.netTip={_it.get('netTip')!r}"
            assert abs((_it.get('tipTransactionFee') or 0) - _ttf) < 0.01, f"{_on}.tipTxFee={_it.get('tipTransactionFee')!r}"
            assert abs((_it.get('tipToPay') or 0) - _ttp) < 0.01, f"{_on}.tipToPay={_it.get('tipToPay')!r}"
    # step 6: orders page total net earnings
    expect(_resp6).status().is_(200)
    expect(_resp6).json('$.data.totalNetEarnings').close_to(1437.99)
    expect(_resp6).json('$.data.totalCurrentEventNetEarnings').close_to(1437.99)
    expect(_resp6).json('$.data.totalCurrentEventFilteredNetEarnings').close_to(1437.99)
    expect(_resp6).json('$.data.totalOtherEventNetEarnings').close_to(0)
    expect(_resp6).json('$.data.totalOrders').equals(19)
    expect(_resp6).json('$.data.totalItems').equals(26)
    expect(_resp6).json('$.data.totalRedeemableItems').equals(24)
    expect(_resp6).json('$.data.totalItemsRedeemed').equals(24)
    # step 7: orders page total net earnings after filtering by ticket 2
    expect(_resp7).status().is_(200)
    expect(_resp7).json('$.data.totalNetEarnings').close_to(194.31)
    expect(_resp7).json('$.data.totalCurrentEventNetEarnings').close_to(194.31)
    expect(_resp7).json('$.data.totalCurrentEventFilteredNetEarnings').close_to(115.16)
    expect(_resp7).json('$.data.totalOtherEventNetEarnings').close_to(0)
    expect(_resp7).json('$.data.totalOrders').equals(5)
    expect(_resp7).json('$.data.totalItems').equals(9)
    expect(_resp7).json('$.data.totalRedeemableItems').equals(7)
    expect(_resp7).json('$.data.totalItemsRedeemed').equals(7)
