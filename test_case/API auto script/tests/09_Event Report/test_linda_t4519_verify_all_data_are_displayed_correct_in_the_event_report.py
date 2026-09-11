"""Migrated from Apifox case #7976339. Source folder: Event Report."""
# Apifox Case ID: 7976339  (traceability only — not needed to run)
NAME = "Verify all data are displayed correct in the Event report"
TAGS = ["p0", "event_report", "suite:linda"]
PRIORITY = 0


CASE_ID = 7976339
ENV_NAME = "Release"

# --- step 1: 01a255a7-7e95-419d-8f0c-82c84bc44069 ---
# post[customScript]: // 1. Data Parsing
# post: const response = pm.response.json();
# post: const summaryData = response.data; // For summary endpoints
# post: const coSellerItems = response.data.items; // For co-seller detail endpoints
# post: 
# post: // 2. Base Response Validation
# post: pm.test("Status Code is 200", function () {
# post:     pm.expect(response.code).to.eql(200);
# post: });
# post: 
# post: // 3. Financial Summary Validation (Referencing Report Page 1)
# post: pm.test("Page 1: Financial Summary Strict Reconciliation", function () {
# post:     // Gross sales before any deductions
# post:     pm.expect(summaryData.grossSalesBeforeDiscount).to.eql(19917.12); // Before promotion total
# post:     pm.expect(summaryData.totalDiscount).to.eql(3077.83);             // Promotion
# post:     pm.expect(summaryData.grossSales).to.eql(16839.29);              // Gross sales
# post:     
# post:     // Deductions and Net values
# post:     pm.expect(summaryData.totalRefund).to.eql(273.36);               // Total refund
# post:     pm.expect(summaryData.netRevenue).to.eql(16565.93);              // Net revenue
# post:     pm.expect(summaryData.totalCommissionPaid).to.eql(280.17);       // Total co-seller commission
# post:     pm.expect(summaryData.totalTransactionFee).to.eql(1941.45);      // Total transaction fees
# post:     
# post:     // Final Audit Figure
# post:     pm.expect(summaryData.netEarnings).to.eql(14344.31);             // Net earnings
# post: });
# post: 
# post: // 4. Operational Metrics Validation (Referencing Report Page 1)
# post: pm.test("Page 1: Operational Metrics Reconciliation", function () {
# post:     pm.expect(summaryData.totalItemsSold).to.eql(292);               // Total items sold
# post:     pm.expect(summaryData.totalItemsRedeemed).to.eql(212);           // Total items redeemed
# post:     pm.expect(summaryData.totalNumberOfOrders).to.eql(187);          // Total number of orders
# post:     pm.expect(summaryData.averageOrderValue).to.eql(90.05);          // Average order value
# post: });
# post: 
# post: // 5. Co-seller Report Summary (Referencing Report Page 1)
# post: pm.test("Page 1: Co-seller Sales Report Summary", function () {
# post:     pm.expect(summaryData.promoterGrossSales).to.eql(3251.20);       // Gross sales
# post:     pm.expect(summaryData.totalItemsSoldByPromoter).to.eql(76);      // Total items sold
# post:     pm.expect(summaryData.totalItemsSoldPercentage).to.eql(26.03);   // Percentage of total
# post:     pm.expect(summaryData.promoterTotalItemsRedeemed).to.eql(62);    // Total items redeemed
# post: });
# post: 
# --- step 2: b8de82bb-c8f9-45c2-873f-60a3b16c9d2f ---
# post[customScript]: // 1. Data Parsing
# post: const response = pm.response.json();
# post: const items = response.data.items; // Direct pointer to co-seller list
# post: 
# post: // 2. Base Response Check
# post: pm.test("Status Code is 200", function () {
# post:     pm.expect(response.code).to.eql(200);
# post: });
# post: 
# post: // 3. Co-seller Details Validation (Referencing PDF Page 2)
# post: pm.test("Co-seller Individual Metrics Validation", function () {
# post:     
# post:     // --- ELI Validation ---
# post:     const eli = items.find(i => i.shopName === "ELI");
# post:     pm.test("Validate Metrics for ELI", () => {
# post:         pm.expect(eli.totalNumberOfOrders).to.eql(29);  // [cite: 17]
# post:         pm.expect(eli.totalItemsSold).to.eql(42);       // [cite: 18]
# post:         pm.expect(eli.totalItemsRedeemed).to.eql(32);   // [cite: 19]
# post:     });
# post: 
# post:     // --- Dermano Validation ---
# post:     const dermano = items.find(i => i.shopName === "Dermano");
# post:     pm.test("Validate Metrics for Dermano", () => {
# post:         pm.expect(dermano.totalNumberOfOrders).to.eql(14); // [cite: 23]
# post:         pm.expect(dermano.totalItemsSold).to.eql(18);      // [cite: 25]
# post:         pm.expect(dermano.totalItemsRedeemed).to.eql(16);  // [cite: 27]
# post:     });
# post: 
# post:     // --- Chris Cauldron Validation ---
# post:     const chris = items.find(i => i.shopName === "Chris Cauldron");
# post:     pm.test("Validate Metrics for Chris Cauldron", () => {
# post:         pm.expect(chris.totalNumberOfOrders).to.eql(3);   // [cite: 31]
# post:         pm.expect(chris.totalItemsSold).to.eql(10);       // [cite: 33]
# post:         pm.expect(chris.totalItemsRedeemed).to.eql(10);   // [cite: 35]
# post:     });
# post: 
# post:     // --- Affiliate +18313229892 Validation ---
# post:     const affiliate1 = items.find(i => i.phoneNumber === "+18313229892");
# post:     pm.test("Validate Metrics for Affiliate +18313229892", () => {
# post:         pm.expect(affiliate1.totalNumberOfOrders).to.eql(2); // [cite: 46]
# post:         pm.expect(affiliate1.totalItemsSold).to.eql(4);      // [cite: 47]
# post:         pm.expect(affiliate1.totalItemsRedeemed).to.eql(4);  // [cite: 48]
# post:     });
# post: 
# post:     // --- Affiliate +16263218363 Validation ---
# post:     const affiliate2 = items.find(i => i.phoneNumber === "+16263218363");
# post:     pm.test("Validate Metrics for Affiliate +16263218363", () => {
# post:         pm.expect(affiliate2.totalNumberOfOrders).to.eql(1); // [cite: 49]
# post:         pm.expect(affiliate2.totalItemsSold).to.eql(2);      // [cite: 50]
# post:         pm.expect(affiliate2.totalItemsRedeemed).to.eql(0);  // [cite: 51]
# post:     });
# post: });
# post: 
# post: // 4. Data Consistency Check (Summation vs Page 1 Summary)
# post: pm.test("Co-seller Total Consistency Check", function () {
# post:     const totalSold = items.reduce((sum, i) => sum + i.totalItemsSold, 0);
# post:     const totalRedeemed = items.reduce((sum, i) => sum + i.totalItemsRedeemed, 0);
# post:     
# post:     // Matches Page 1: Co-seller Sales Report
# post:     pm.expect(totalSold).to.eql(76);      // [cite: 7]
# post:     pm.expect(totalRedeemed).to.eql(62);  // [cite: 7]
# post: });




import json

from core.assertions import expect

def test_linda_t4519_verify_all_data_are_displayed_correct_in_the_event_report(ctx):
    """Apifox case #7976339: Linda_T4519_Verify_all_data_are_displayed_correct_in_the_Event_report"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 01a255a7-7e95-419d-8f0c-82c84bc44069
    _resp1 = ctx.api.events.bea4cfb9_a9a6_4a1f_a1a8_96f7e9418d03_metrics_summary(body=None, token='linda05_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp1.status_code == 200, f"状态码期望200，实际={_resp1.status_code}"
    assert _j1.get('code') == 200, f"响应code期望200，实际={_j1.get('code')!r}"
    _s1 = _j1.get('data') or {}
    # Financial Summary（对应报告第1页）
    assert _s1.get('grossSalesBeforeDiscount') == 19917.12, f"grossSalesBeforeDiscount期望19917.12，实际={_s1.get('grossSalesBeforeDiscount')!r}"
    assert _s1.get('totalDiscount') == 3077.83, f"totalDiscount期望3077.83，实际={_s1.get('totalDiscount')!r}"
    assert _s1.get('grossSales') == 16839.29, f"grossSales期望16839.29，实际={_s1.get('grossSales')!r}"
    assert _s1.get('totalRefund') == 273.36, f"totalRefund期望273.36，实际={_s1.get('totalRefund')!r}"
    assert _s1.get('netRevenue') == 16565.93, f"netRevenue期望16565.93，实际={_s1.get('netRevenue')!r}"
    assert _s1.get('totalCommissionPaid') == 280.17, f"totalCommissionPaid期望280.17，实际={_s1.get('totalCommissionPaid')!r}"
    assert _s1.get('totalTransactionFee') == 1941.45, f"totalTransactionFee期望1941.45，实际={_s1.get('totalTransactionFee')!r}"
    assert _s1.get('netEarnings') == 14344.31, f"netEarnings期望14344.31，实际={_s1.get('netEarnings')!r}"
    # Operational Metrics（对应报告第1页）
    assert _s1.get('totalItemsSold') == 292, f"totalItemsSold期望292，实际={_s1.get('totalItemsSold')!r}"
    assert _s1.get('totalItemsRedeemed') == 212, f"totalItemsRedeemed期望212，实际={_s1.get('totalItemsRedeemed')!r}"
    assert _s1.get('totalNumberOfOrders') == 187, f"totalNumberOfOrders期望187，实际={_s1.get('totalNumberOfOrders')!r}"
    assert _s1.get('averageOrderValue') == 90.05, f"averageOrderValue期望90.05，实际={_s1.get('averageOrderValue')!r}"
    # Co-seller Sales Report Summary（对应报告第1页）
    assert _s1.get('promoterGrossSales') == 3251.20, f"promoterGrossSales期望3251.20，实际={_s1.get('promoterGrossSales')!r}"
    assert _s1.get('totalItemsSoldByPromoter') == 76, f"totalItemsSoldByPromoter期望76，实际={_s1.get('totalItemsSoldByPromoter')!r}"
    assert _s1.get('totalItemsSoldPercentage') == 26.03, f"totalItemsSoldPercentage期望26.03，实际={_s1.get('totalItemsSoldPercentage')!r}"
    assert _s1.get('promoterTotalItemsRedeemed') == 62, f"promoterTotalItemsRedeemed期望62，实际={_s1.get('promoterTotalItemsRedeemed')!r}"
    # step 2: b8de82bb-c8f9-45c2-873f-60a3b16c9d2f
    _resp2 = ctx.api.events.bea4cfb9_a9a6_4a1f_a1a8_96f7e9418d03_metrics_promoters(body=None, params={'pageSize': '30', 'pageNumber': '1'}, token='linda05_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp2.status_code == 200, f"状态码期望200，实际={_resp2.status_code}"
    assert _j2.get('code') == 200, f"响应code期望200，实际={_j2.get('code')!r}"
    _items2 = (_j2.get('data') or {}).get('items') or []
    # Co-seller Individual Metrics（对应报告第2页）
    _eli = next((_i for _i in _items2 if _i.get('shopName') == 'ELI'), None)
    assert _eli is not None, "未找到shopName=ELI的co-seller"
    assert _eli.get('totalNumberOfOrders') == 29, f"ELI.totalNumberOfOrders期望29，实际={_eli.get('totalNumberOfOrders')!r}"
    assert _eli.get('totalItemsSold') == 42, f"ELI.totalItemsSold期望42，实际={_eli.get('totalItemsSold')!r}"
    assert _eli.get('totalItemsRedeemed') == 32, f"ELI.totalItemsRedeemed期望32，实际={_eli.get('totalItemsRedeemed')!r}"
    _dermano = next((_i for _i in _items2 if _i.get('shopName') == 'Dermano'), None)
    assert _dermano is not None, "未找到shopName=Dermano的co-seller"
    assert _dermano.get('totalNumberOfOrders') == 14, f"Dermano.totalNumberOfOrders期望14，实际={_dermano.get('totalNumberOfOrders')!r}"
    assert _dermano.get('totalItemsSold') == 18, f"Dermano.totalItemsSold期望18，实际={_dermano.get('totalItemsSold')!r}"
    assert _dermano.get('totalItemsRedeemed') == 16, f"Dermano.totalItemsRedeemed期望16，实际={_dermano.get('totalItemsRedeemed')!r}"
    _chris = next((_i for _i in _items2 if _i.get('shopName') == 'Chris Cauldron'), None)
    assert _chris is not None, "未找到shopName=Chris Cauldron的co-seller"
    assert _chris.get('totalNumberOfOrders') == 3, f"Chris.totalNumberOfOrders期望3，实际={_chris.get('totalNumberOfOrders')!r}"
    assert _chris.get('totalItemsSold') == 10, f"Chris.totalItemsSold期望10，实际={_chris.get('totalItemsSold')!r}"
    assert _chris.get('totalItemsRedeemed') == 10, f"Chris.totalItemsRedeemed期望10，实际={_chris.get('totalItemsRedeemed')!r}"
    _aff1 = next((_i for _i in _items2 if _i.get('phoneNumber') == '+18313229892'), None)
    assert _aff1 is not None, "未找到phoneNumber=+18313229892的affiliate"
    assert _aff1.get('totalNumberOfOrders') == 2, f"Affiliate(+18313229892).totalNumberOfOrders期望2，实际={_aff1.get('totalNumberOfOrders')!r}"
    assert _aff1.get('totalItemsSold') == 4, f"Affiliate(+18313229892).totalItemsSold期望4，实际={_aff1.get('totalItemsSold')!r}"
    assert _aff1.get('totalItemsRedeemed') == 4, f"Affiliate(+18313229892).totalItemsRedeemed期望4，实际={_aff1.get('totalItemsRedeemed')!r}"
    _aff2 = next((_i for _i in _items2 if _i.get('phoneNumber') == '+16263218363'), None)
    assert _aff2 is not None, "未找到phoneNumber=+16263218363的affiliate"
    assert _aff2.get('totalNumberOfOrders') == 1, f"Affiliate(+16263218363).totalNumberOfOrders期望1，实际={_aff2.get('totalNumberOfOrders')!r}"
    assert _aff2.get('totalItemsSold') == 2, f"Affiliate(+16263218363).totalItemsSold期望2，实际={_aff2.get('totalItemsSold')!r}"
    assert _aff2.get('totalItemsRedeemed') == 0, f"Affiliate(+16263218363).totalItemsRedeemed期望0，实际={_aff2.get('totalItemsRedeemed')!r}"
    # Co-seller Total Consistency（与第1页汇总一致）
    _totalSold = sum((_i.get('totalItemsSold') or 0) for _i in _items2)
    _totalRedeemed = sum((_i.get('totalItemsRedeemed') or 0) for _i in _items2)
    assert _totalSold == 76, f"co-seller totalItemsSold合计期望76，实际={_totalSold}"
    assert _totalRedeemed == 62, f"co-seller totalItemsRedeemed合计期望62，实际={_totalRedeemed}"
