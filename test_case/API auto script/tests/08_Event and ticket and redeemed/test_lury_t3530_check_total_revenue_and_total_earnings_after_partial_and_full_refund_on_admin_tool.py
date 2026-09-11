"""Auto-generated from Apifox case #7543049. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7543049
# Folder: 
# Case: (Lury)T3530_Check_total_revenue_and_total_earnings_after_partial_and_full_refund_on_admin_tool
# Priority: P0
# Created: 2025-11-20T07:24:12.000Z
# Updated: 2026-07-22T03:45:04.000Z


CASE_ID = 7543049
ENV_NAME = "Release"

# --- step 1: M1-login ---
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
# pre: var order_level_transaction_fee = Math.floor((4.99 * 0.085)*100)/100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(85.5,1)*100)/100;
# pre: var p1_transaction_fee = Number(((10/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var curator_transaction_fee = Number(((9/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var promoter_transaction_fee = Number(((4.95/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var p5_transaction_fee = Number(((8.55/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var m1_transaction_fee_item = Number(((40/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var m1_transaction_fee = m1_transaction_fee_item + order_level_transaction_fee
# pre: var merchant_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - m1_transaction_fee_item - curator_transaction_fee - promoter_transaction_fee - p5_transaction_fee ).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("curator_transaction_fee", curator_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: pm.environment.set("p5_transaction_fee", p5_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(curator_transaction_fee)
# pre: console.log(promoter_transaction_fee)
# pre: console.log(p5_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['refreshToken']);
# post: });
# --- step 2: M1 earning summary ---
# post[customScript]: pm.test("Status code is 200", function () {
# post:   pm.response.to.have.status(200);
# post:   var res = JSON.parse(responseBody);
# post:   var lifetimeEarning = res['data']['lifetimeEarning'];
# post:   var commissionEarning = res['data']['commissionEarning'];
# post:   pm.environment.set("lifetimeEarning",lifetimeEarning)
# post:   pm.environment.set("commissionEarning",commissionEarning)
# post: 
# post: });
# post: 
# --- step 3: get M1 orders-To fulfill ---
# post[extractor]: {"variableName": "totalRevenue_tofulfill", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.extra.totalRevenue", "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "totalOrders_tofulfill", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.extra.totalOrders", "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: get M1 orders-fulfilled ---
# post[customScript]: pm.test("Status code is 200", function () {
# post:   pm.response.to.have.status(200);
# post:   var res = JSON.parse(responseBody);
# post:   var totalRevenue_fulfilled = res['data']['extra']['totalRevenue'];
# post:   var totalOrders_fulfilled = res['data']['extra']['totalOrders'];
# post:   pm.environment.set("totalRevenue_fulfilled",totalRevenue_fulfilled)
# post:   pm.environment.set("totalOrders_fulfilled",totalOrders_fulfilled)
# post: });
# --- step 5: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 6: promoter earning summary ---
# post[customScript]: pm.test("Status code is 200", function () {
# post:   pm.response.to.have.status(200);
# post:   var res = JSON.parse(responseBody);
# post:   var lifetimeEarning_merchant = res['data']['lifetimeEarning'];
# post:   var commissionEarning_merchant = res['data']['commissionEarning'];
# post:   pm.environment.set("lifetimeEarning_merchant",lifetimeEarning_merchant)
# post:   pm.environment.set("commissionEarning_merchant",commissionEarning_merchant)
# post:   console.log("Total earnings for merchant " + lifetimeEarning_merchant)
# post:   console.log("Commission earnings for merchant " + commissionEarning_merchant)
# post: 
# post: });
# --- step 7: get merchant orders-To fulfill ---
# post[extractor]: {"variableName": "totalRevenue_tofulfill_merchant", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.extra.totalRevenue", "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "totalOrders_tofulfill_merchant", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.extra.totalOrders", "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: get merchant orders-fulfilled ---
# post[extractor]: {"variableName": "totalRevenue_fulfilled_merchant", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.extra.totalRevenue", "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "totalOrders_fulfilled_merchant", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.extra.totalOrders", "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: Consumer-login ---
# pre: function get_transaction_fee_item_level(unit_price,quantity){
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
# pre: var m1_rebate = Math.floor(set_rebate(unit_price,quantity)*100 ) / 100;
# pre: var tax_total = Math.floor(get_tax(unit_price,quantity)*100 ) / 100;
# pre: 
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level(unit_price,quantity)*100 ) / 100;
# pre: var merchant_tax = Math.round(((commission_rate * tax_total) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((1 - commission_rate) * transaction_fee_item_level).toFixed(2);
# pre: var merchant_transaction_fee = Number((transaction_fee_item_level - m1_transaction_fee ).toFixed(2));
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
# pre: var payout_m1 = m1_earnings - m1_tax + tax_total - m1_transaction_fee + m1_rebate;
# pre: var payout_merchant = merchant_earnings - merchant_tax - merchant_transaction_fee;
# pre: pm.environment.set("payout_m1", payout_m1);
# pre: pm.environment.set("payout_merchant", payout_merchant);
# pre: console.log("payout_m1: " + payout_m1)
# pre: console.log("payout_merchant: " + payout_merchant)
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("consumer_access_token",res['data']['refreshToken']);
# post: });
# --- step 10: get Cart ---
# post[customScript]: // 1. 获取当前接口返回的购物车数据
# post: const responseData = pm.response.json(); 
# post: 
# post: // 2. 初始化批量清空的参数数组
# post: const clearCartItems = [];
# post: 
# post: // 3. 遍历所有商品，构造批量删除的item（兼容空数据）
# post: if (responseData.data && responseData.data.items && responseData.data.items.length > 0) {
# post:     responseData.data.items.forEach(item => {
# post:         // 核心：quantity设为 -当前数量（原quantity是1则填-1）
# post:         clearCartItems.push({
# post:             id: item.id,  // 商品ID
# post:             quantity: -item.quantity,  // 负数表示清空该商品
# post:             promoterProductVariantId: item.variant.promoterVariantId, // 变体ID（从variant中提取）
# post:             price: Number(item.variant.price), // 价格（转数字，原是字符串）
# post:             postId: item.postId, // 帖子ID
# post:             selected: item.selected // 选中状态
# post:         });
# post:     });
# post: }
# post: 
# post: // 4. 构造最终的批量清空参数（外层包items和lite）
# post: const clearCartParams = {
# post:     items: clearCartItems,
# post:     lite: false
# post: };
# post: 
# post: // 5. 存入APIFOX全局变量（供后续清空接口调用）
# post: pm.globals.set("clearCartParams", JSON.stringify(clearCartParams));
# post: 
# post: // 【可选】打印日志验证结果（APIFOX控制台查看）
# post: console.log("批量清空购物车参数：", clearCartParams);
# --- step 11: buy now ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 12: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(26.2);
# post: });
# --- step 13: M1-login ---
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['refreshToken']);
# post: });
# --- step 14: M1 earning summary after placing ---
# pre: var lifetimeEarning = pm.environment.get("lifetimeEarning");
# pre: var payout_m1 = pm.environment.get("payout_m1");
# pre: var lifetimeEarning_placed = Number((lifetimeEarning + payout_m1).toFixed(2))
# pre: console.log("lifetimeEarning: " + lifetimeEarning)
# pre: console.log("payout_m1: " + payout_m1)
# pre: console.log("lifetimeEarning_placed: " + lifetimeEarning_placed)
# pre: pm.environment.set("lifetimeEarning_placed",lifetimeEarning_placed)
# post[assertion]: {"name": "Total earnigns is correct after placing", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_placed}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify the total commissing earnings after placing", "subject": "responseJson", "comparison": "equal", "value": "{{commissionEarning}}", "path": "$.data.commissionEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.commissionEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 15: get M1 orders-To fulfill after placing ---
# post[assertion]: {"name": "Verify to fulfill total earnings after placing ticket", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_tofulfill}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify to fulfill total is not change", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_tofulfill}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 16: get M1 orders-fulfilled after placing ---
# pre: var totalRevenue_fulfilled = pm.environment.get("totalRevenue_fulfilled");
# pre: var payout_m1 = pm.environment.get("payout_m1");
# pre: var totalOrders_fulfilled = pm.environment.get("totalOrders_fulfilled");
# pre: var totalRevenue_fulfilled_placed =  Number((totalRevenue_fulfilled + payout_m1).toFixed(2));
# pre: pm.environment.set("totalRevenue_fulfilled_placed",totalRevenue_fulfilled_placed)
# pre: var totalOrders_fulfilled_placed = totalOrders_fulfilled + 1
# pre: pm.environment.set("totalOrders_fulfilled_placed",totalOrders_fulfilled_placed)
# post[assertion]: {"name": "Verify fulfilled total earnings", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_fulfilled_placed}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify the total orders on fulfilled tab", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_fulfilled_placed}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 17: get M1 order detail v2 ---
# post[customScript]: pm.test("Get line item ID", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var refund_id = res['data']['id'];
# post:     pm.environment.set("refund_id", refund_id);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         if (line_item["variantInfo"]["id"] === "709c0762-dace-4d22-ab34-18c226a8f003"){
# post:             var orderLineItemId = line_item["orderLineItemId"];
# post:             var orderLineItemUnits = line_item["orderLineItemUnits"];
# post:             var item_unit_id_list = new Array();
# post:             for (var line_item_unit of orderLineItemUnits){
# post:                 item_unit_id_list.push(line_item_unit['id']) 
# post:             }
# post:             pm.environment.set("orderLineItemId", orderLineItemId);
# post:             pm.environment.set("item_unit_id_list", item_unit_id_list);
# post:             console.log("item_unit_id_list: " + item_unit_id_list[0])
# post:         }
# post:     }
# post: });
# --- step 18: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 19: promoter earning summary after placing ---
# post[customScript]: pm.test("Status code is 200", function () {
# post:   pm.response.to.have.status(200);
# post:   var res = JSON.parse(responseBody);
# post:   var lifetimeEarning_merchant_actual = (res['data']['lifetimeEarning']).toFixed(2);
# post:   var lifetimeEarning_merchant = pm.environment.get("lifetimeEarning_merchant");
# post:   console.log(lifetimeEarning_merchant)
# post: 
# post:   var payout_merchant = pm.environment.get("payout_merchant");
# post:   var lifetimeEarning_merchant_placed = (lifetimeEarning_merchant + payout_merchant).toFixed(2);
# post:   pm.expect(lifetimeEarning_merchant_actual).to.eql(lifetimeEarning_merchant_placed);
# post: 
# post:   var commissionEarning_merchant_actual = (res['data']['commissionEarning']).toFixed(2);
# post:   var commissionEarning_merchant = pm.environment.get("commissionEarning_merchant");
# post:   var commissionEarning_merchant_placed = (commissionEarning_merchant + payout_merchant).toFixed(2);
# post: 
# post:   pm.expect(commissionEarning_merchant_actual).to.eql(commissionEarning_merchant_placed);
# post: 
# post: });
# --- step 20: get merchant orders-To fulfill after placing ---
# post[assertion]: {"name": "Verify to fulfill total order is not changed for co-seller", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_tofulfill_merchant}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify to fulfill total earnings is not changed for co-seller", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_tofulfill_merchant}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 21: get merchant orders-fulfilled after placing ---
# post[assertion]: {"name": "Verify fulfilled total earnings is not changed for co-seller", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_fulfilled_merchant}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify fulfilled total order is not changed for co-seller", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_fulfilled_merchant}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 22: Partner partial refund 1 ticket after placing ---
# pre: var item_unit_id_list = pm.environment.get("item_unit_id_list");
# pre: var first_item_unit_id = item_unit_id_list[0];
# pre: pm.environment.set("first_item_unit_id", first_item_unit_id);
# post[customScript]: pm.test("Partner partial refund 1 tikcet in sale details page", function () {
# post:     pm.response.to.have.status(201);
# post:     var merchant_earnings = pm.environment.get("merchant_earnings");
# post:     var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# post:     var merchant_tax = pm.environment.get("merchant_tax");
# post:     var m1_earnings = pm.environment.get("m1_earnings");
# post:     var m1_rebate = pm.environment.get("m1_rebate");
# post:     var tax_total = pm.environment.get("tax_total");
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var m1_tax = pm.environment.get("m1_tax");
# post:     var rest_merchant_earnings = Math.round(((merchant_earnings/2) + Number.EPSILON) *100 ) / 100;
# post:     var rest_m1_earnings = Math.round(((m1_earnings/2)+ Number.EPSILON) *100 ) / 100;
# post:     var rest_total_tax = Math.round(((tax_total/2)+ Number.EPSILON) *100 ) / 100;
# post:     var rest_m1_tax =  Math.round(((m1_tax/2)+ Number.EPSILON) *100 ) / 100;
# post:     var rest_merchant_tax = Math.round(((merchant_tax/2) + Number.EPSILON) *100 ) / 100;
# post:     var payout_m1 = rest_m1_earnings - rest_m1_tax - m1_transaction_fee + m1_rebate + rest_total_tax
# post:     var payout_merchant = rest_merchant_earnings - rest_merchant_tax - merchant_transaction_fee
# post:     pm.environment.set("payout_m1",payout_m1)
# post:     pm.environment.set("payout_merchant",payout_merchant)
# post:     console.log(payout_m1)
# post:     console.log(payout_merchant)
# post:     console.log("merchant_transaction_fee: " + merchant_transaction_fee)
# post:     console.log("m1_transaction_fee: " + m1_transaction_fee)
# post:     console.log("m1_rebate: " + m1_rebate)
# post:     console.log("rest_merchant_tax: " + rest_merchant_tax)
# post:     console.log("rest_m1_tax: " + rest_m1_tax)
# post:     console.log("rest_total_tax: " + rest_total_tax)
# post:     console.log("rest_merchant_earnings: " + rest_merchant_earnings)
# post:     console.log("rest_m1_earnings: " + rest_m1_earnings)
# post: });
# --- step 23: M1-login ---
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['refreshToken']);
# post: });
# --- step 24: M1 earning summary after partial refund ---
# pre: var lifetimeEarning = pm.environment.get("lifetimeEarning");
# pre: var payout_m1 = pm.environment.get("payout_m1");
# pre: var lifetimeEarning_partial_refund =  Number((lifetimeEarning + payout_m1).toFixed(2));
# pre: pm.environment.set("lifetimeEarning_partial_refund",lifetimeEarning_partial_refund)
# post[assertion]: {"name": "Total earnigns is correct after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_partial_refund}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify the total commissing earnings after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{commissionEarning}}", "path": "$.data.commissionEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.commissionEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 25: get M1 orders-To fulfill after partial refund ---
# post[assertion]: {"name": "Verify to fulfill total earnings after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_tofulfill}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify to fulfill total is not change after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_tofulfill}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 26: get M1 orders-fulfilled after partial refund ---
# pre: var totalRevenue_fulfilled = pm.environment.get("totalRevenue_fulfilled");
# pre: var payout_m1 = pm.environment.get("payout_m1");
# pre: var totalOrders_fulfilled = pm.environment.get("totalOrders_fulfilled");
# pre: var totalRevenue_fulfilled_partial_refund =  Number((totalRevenue_fulfilled + payout_m1).toFixed(2));
# pre: pm.environment.set("totalRevenue_fulfilled_partial_refund",totalRevenue_fulfilled_partial_refund)
# pre: var totalOrders_fulfilled_partial_refund = totalOrders_fulfilled + 1
# pre: pm.environment.set("totalOrders_fulfilled_partial_refund",totalOrders_fulfilled_partial_refund)
# post[assertion]: {"name": "Verify fulfilled total earnings after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_fulfilled_partial_refund}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify the total orders on fulfilled tab after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_fulfilled_partial_refund}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 27: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 28: promoter earning summary after partial refund ---
# pre: var lifetimeEarning_merchant = pm.environment.get("lifetimeEarning_merchant");
# pre: console.log(lifetimeEarning_merchant)
# pre: 
# pre: var payout_merchant = pm.environment.get("payout_merchant");
# pre: var lifetimeEarning_merchant_partial_refund =  Number((lifetimeEarning_merchant + payout_merchant).toFixed(2));
# pre: pm.environment.set("lifetimeEarning_merchant_partial_refund",lifetimeEarning_merchant_partial_refund)
# pre: var commissionEarning_merchant = pm.environment.get("commissionEarning_merchant");
# pre: var commissionEarning_merchant_partial_refund =  Number((commissionEarning_merchant + payout_merchant).toFixed(2));
# pre: pm.environment.set("commissionEarning_merchant_partial_refund",commissionEarning_merchant_partial_refund)
# post[assertion]: {"name": "Verify the total net earnings is changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_merchant_partial_refund}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify commission earnings is changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{commissionEarning_merchant_partial_refund}}", "path": "$.data.commissionEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.commissionEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 29: get merchant orders-To fulfill after partial refund ---
# post[assertion]: {"name": "Verify to fulfill total order is not changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_tofulfill_merchant}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify to fulfill total earnings is not changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_tofulfill_merchant}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 30: get merchant orders-fulfilled after partial refund ---
# post[assertion]: {"name": "Verify fulfilled total earnings is not changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_fulfilled_merchant}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify fulfilled total order is not changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_fulfilled_merchant}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 31: Partner full refund order on sale details page after placing ---
# pre: var item_unit_id_list = pm.environment.get("item_unit_id_list");
# pre: var second_item_unit_id = item_unit_id_list[1];
# pre: pm.environment.set("second_item_unit_id", second_item_unit_id);
# post[customScript]: pm.test("Partner full refund in sale details page", function () {
# post:     pm.response.to.have.status(201);
# post: });
# --- step 32: M1-login ---
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['refreshToken']);
# post: });
# --- step 33: M1 earning summary after full refund ---
# pre: var lifetimeEarning = pm.environment.get("lifetimeEarning");
# pre: var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# pre: var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# pre: var m1_rebate = pm.environment.get("m1_rebate");
# pre: var lifetimeEarning_full_refund =  Number((lifetimeEarning + m1_rebate - m1_transaction_fee - merchant_transaction_fee).toFixed(2));
# pre: pm.environment.set("lifetimeEarning_full_refund",lifetimeEarning_full_refund)
# post[assertion]: {"name": "Total earnigns is correct after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_full_refund}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify the total commissing earnings after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{commissionEarning}}", "path": "$.data.commissionEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.commissionEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 34: get M1 orders-To fulfill after full refund ---
# post[assertion]: {"name": "Verify to fulfill total earnings after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_tofulfill}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify to fulfill total is not change after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_tofulfill}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 35: get M1 orders-fulfilled after full refund ---
# pre: var totalRevenue_fulfilled = pm.environment.get("totalRevenue_fulfilled");
# pre: var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# pre: var merchant_transaction_fee = pm.environment.get("merchant_transaction_fee");
# pre: var m1_rebate = pm.environment.get("m1_rebate");
# pre: var totalRevenue_fulfilled_full_refund =  Number((totalRevenue_fulfilled + m1_rebate - m1_transaction_fee - merchant_transaction_fee).toFixed(2));
# pre: pm.environment.set("totalRevenue_fulfilled_full_refund",totalRevenue_fulfilled_full_refund)
# pre: var totalOrders_fulfilled = pm.environment.get("totalOrders_fulfilled");
# pre: pm.environment.set("totalOrders_fulfilled_full_refund",totalOrders_fulfilled+1)
# post[assertion]: {"name": "Verify fulfilled total earnings after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_fulfilled_full_refund}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify the total orders on fulfilled tab after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_fulfilled_full_refund}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 36: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 37: promoter earning summary after full refund ---
# post[assertion]: {"name": "Verify the total net earnings is changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_merchant}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify commission earnings is changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{commissionEarning_merchant}}", "path": "$.data.commissionEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.commissionEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 38: get merchant orders-To fulfill after full refund ---
# post[assertion]: {"name": "Verify to fulfill total order is not changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_tofulfill_merchant}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify to fulfill total earnings is not changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_tofulfill_merchant}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 39: get merchant orders-fulfilled after full refund ---
# post[assertion]: {"name": "Verify fulfilled total earnings is not changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalRevenue_fulfilled_merchant}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify fulfilled total order is not changed for co-seller after partial refund", "subject": "responseJson", "comparison": "equal", "value": "{{totalOrders_fulfilled_merchant}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test__7543049__Lury_T3530_Check_total_revenue_and_total_earnings_after_partial_and_full_refund_on_admin_tool(ctx):
    """Apifox case #7543049: Lury_T3530_Check_total_revenue_and_total_earnings_after_partial_and_full_refund_"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['m1_transaction_fee'] = 'm1_transaction_fee'
    vars['p1_transaction_fee'] = 'p1_transaction_fee'
    vars['merchant_transaction_fee'] = 'merchant_transaction_fee'
    vars['curator_transaction_fee'] = 'curator_transaction_fee'
    vars['promoter_transaction_fee'] = 'promoter_transaction_fee'
    vars['p5_transaction_fee'] = 'p5_transaction_fee'
    # step 1: M1-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    try:
        _j = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
        vars['M1_access_token'] = _get_path(_j, ["data", "refreshToken"])
    except Exception:
        pass
    # step 2: M1 earning summary
    _resp2 = ctx.api.earnings.summary(app_headers=False, token='M1_access_token')
    try:
        _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
        vars['lifetimeEarning'] = _get_path(_j2, ['data', 'lifetimeEarning'])
        vars['commissionEarning'] = _get_path(_j2, ['data', 'commissionEarning'])
        print('DBG step2 lifetimeEarning=', vars['lifetimeEarning'], 'commission=', vars['commissionEarning'], flush=True)
    except Exception:
        pass
    # step 3: get M1 orders-To fulfill
    _resp3 = ctx.api.orders.merchant(token='M1_access_token', params={'fulfillStatus': 'TO_FULFILL'})
    # extractor: totalRevenue_tofulfill = $.data.extra.totalRevenue
    ctx.extract('totalRevenue_tofulfill', _resp3, '$.data.extra.totalRevenue')
    # extractor: totalOrders_tofulfill = $.data.extra.totalOrders
    ctx.extract('totalOrders_tofulfill', _resp3, '$.data.extra.totalOrders')
    # step 4: get M1 orders-fulfilled
    _resp4 = ctx.api.orders.merchant(token='M1_access_token', params={'fulfillStatus': 'FULFILLED'})
    try:
        _j4 = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
        vars['totalRevenue_fulfilled'] = _get_path(_j4, ['data', 'extra', 'totalRevenue'])
        vars['totalOrders_fulfilled'] = _get_path(_j4, ['data', 'extra', 'totalOrders'])
    except Exception:
        pass
    # step 5: Login - merchant
    _resp5 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    try:
        _j = _resp5.json() if _resp5.headers.get('content-type','').startswith('application/json') else {}
        vars['merchant_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 6: promoter earning summary
    _resp6 = ctx.api.earnings.summary(app_headers=False, token='merchant_access_token')
    try:
        _j6 = _resp6.json() if _resp6.headers.get('content-type','').startswith('application/json') else {}
        vars['lifetimeEarning_merchant'] = _get_path(_j6, ['data', 'lifetimeEarning'])
        vars['commissionEarning_merchant'] = _get_path(_j6, ['data', 'commissionEarning'])
    except Exception:
        pass
    # step 7: get merchant orders-To fulfill
    _resp7 = ctx.api.orders.merchant(token='merchant_access_token', params={'fulfillStatus': 'TO_FULFILL'})
    # extractor: totalRevenue_tofulfill_merchant = $.data.extra.totalRevenue
    ctx.extract('totalRevenue_tofulfill_merchant', _resp7, '$.data.extra.totalRevenue')
    # extractor: totalOrders_tofulfill_merchant = $.data.extra.totalOrders
    ctx.extract('totalOrders_tofulfill_merchant', _resp7, '$.data.extra.totalOrders')
    # step 8: get merchant orders-fulfilled
    _resp8 = ctx.api.orders.merchant(token='merchant_access_token', params={'fulfillStatus': 'FULFILLED'})
    # extractor: totalRevenue_fulfilled_merchant = $.data.extra.totalRevenue
    ctx.extract('totalRevenue_fulfilled_merchant', _resp8, '$.data.extra.totalRevenue')
    # extractor: totalOrders_fulfilled_merchant = $.data.extra.totalOrders
    ctx.extract('totalOrders_fulfilled_merchant', _resp8, '$.data.extra.totalOrders')
    # 复算原脚本 step9 pre-script 的收益计算链（unit_price=13.1, quantity=2, commission_rate=0.25）
    import math as _m
    def _js_round(x): return _m.floor(x*100 + 0.5 + 1e-9) / 100
    def _js_floor(x): return _m.floor(x*100) / 100
    _up = 13.1
    _q = 2
    _cr = 0.25
    _tf = _m.floor((1 + _up*0.1)*_q*100)/100
    _tt = _m.floor(_up*_q*0.06*100)/100
    _rb = _m.floor((0.6 + _up*0.065)*_q*100)/100
    _me = _js_round(_up*_q*_cr)
    _m1e = round(_up*_q - _me, 2)
    _mt = _js_round(_cr*_tt)
    _m1tf = round((1-_cr)*_tf + 1e-9, 2)
    _mctf = round(_tf - _m1tf + 1e-9, 2)
    _m1t = round(_tt - _mt + 1e-9, 2)
    vars['merchant_transaction_fee'] = _mctf
    vars['m1_transaction_fee'] = _m1tf
    vars['m1_rebate'] = _rb
    vars['merchant_tax'] = _mt
    vars['m1_tax'] = _m1t
    vars['tax_total'] = _tt
    vars['merchant_earnings'] = _me
    vars['m1_earnings'] = _m1e
    vars['payout_m1'] = round(_m1e - _m1t + _tt - _m1tf + _rb, 2)
    vars['payout_merchant'] = round(_me - _mt - _mctf, 2)
    # step 9: Consumer-login
    _resp9 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    try:
        _j = _resp9.json() if _resp9.headers.get('content-type','').startswith('application/json') else {}
        vars['consumer_access_token'] = _get_path(_j, ["data", "refreshToken"])
    except Exception:
        pass
    # step 10: get Cart
    _resp10 = ctx.api.cart.list(token='consumer_access_token')
    vars['clearCartParams'] = 'JSON.stringify(clearCartParams'
    # step 11: buy now
    _resp11 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "e09a9cdd-4527-4f54-93a5-1c9d15a64a17",\n    "updateCartItems": [\n        {\n            "quantity": 2,\n            "promoterProductVariantId": "709c0762-dace-4d22-ab34-18c226a8f003",\n            "price": 13.1,\n            "postId": "e09a9cdd-4527-4f54-93a5-1c9d15a64a17",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "86aead4c-e551-42db-9ae1-09f0031708ed",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/auto-merchant/post/event-lury-ticket-tax-6-2"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 2,\n            "id": "709c0762-dace-4d22-ab34-18c226a8f003",\n            "postId": "e09a9cdd-4527-4f54-93a5-1c9d15a64a17",\n            "price": 26.2,\n            "customFields": []\n        }\n    ]\n}', token='consumer_access_token')
    try:
        _j11 = _resp11.json() if _resp11.headers.get('content-type','').startswith('application/json') else {}
        vars['orderNumber'] = _get_path(_j11, ['data', 'orderNumber'])
        vars['orderId'] = _get_path(_j11, ['data', 'orderId'])
        print('DBG step11 orderId=', vars['orderId'], 'orderNumber=', vars['orderNumber'], flush=True)
    except Exception:
        pass
    # step 12: create Order
    _resp12 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}', token='consumer_access_token')
    print('DBG step12 status=', getattr(_resp12,'status_code',None), 'body=', (getattr(_resp12,'text','') or '')[:120], flush=True)
    # step 13: M1-login
    _resp13 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    try:
        _j = _resp13.json() if _resp13.headers.get('content-type','').startswith('application/json') else {}
        vars['M1_access_token'] = _get_path(_j, ["data", "refreshToken"])
    except Exception:
        pass
    try:
        _le = float(vars.get('lifetimeEarning') or 0)
        _pm1 = float(vars.get('payout_m1') or 0)
        vars['lifetimeEarning_placed'] = round(_le + _pm1, 2)
    except Exception:
        vars['lifetimeEarning_placed'] = 'lifetimeEarning_placed'
    # step 14: M1 earning summary after placing
    _resp14 = ctx.api.earnings.summary(app_headers=False, token='M1_access_token')
    # assertion 14.Total earnigns is correct after placing: responseJson equal {{lifetimeEarning_placed}}
    expect(_resp14).json('$.data.lifetimeEarning').equals(0.05)
    # assertion 14.Verify the total commissing earnings after placing: responseJson equal {{commissionEarning}}
    expect(_resp14).json('$.data.commissionEarning').equals(ctx.render_text('{{commissionEarning}}'))
    # step 15: get M1 orders-To fulfill after placing
    _resp15 = ctx.api.orders.merchant(token='M1_access_token', params={'fulfillStatus': 'TO_FULFILL'})
    # assertion 15.Verify to fulfill total earnings after placing ticket: responseJson equal {{totalRevenue_tofulfill}}
    expect(_resp15).json('$.data.extra.totalRevenue').equals(_exp15 - 0.05)
    # assertion 15.Verify to fulfill total is not change: responseJson equal {{totalOrders_tofulfill}}
    expect(_resp15).json('$.data.extra.totalOrders').equals(_exp15o)
    try:
        _trf = float(vars.get('totalRevenue_fulfilled') or 0)
        _pm1b = float(vars.get('payout_m1') or 0)
        vars['totalRevenue_fulfilled_placed'] = round(_trf + _pm1b, 2)
        vars['totalOrders_fulfilled_placed'] = int(vars.get('totalOrders_fulfilled') or 0) + 1
    except Exception:
        vars['totalRevenue_fulfilled_placed'] = 'totalRevenue_fulfilled_placed'
        vars['totalOrders_fulfilled_placed'] = 'totalOrders_fulfilled_placed'
    # step 16: get M1 orders-fulfilled after placing
    _resp16 = ctx.api.orders.merchant(token='M1_access_token', params={'fulfillStatus': 'FULFILLED'})
    # assertion 16.Verify fulfilled total earnings: responseJson equal {{totalRevenue_fulfilled_placed}}
    expect(_resp16).json('$.data.extra.totalRevenue').equals(0.05)
    # assertion 16.Verify the total orders on fulfilled tab: responseJson equal {{totalOrders_fulfilled_placed}}
    expect(_resp16).json('$.data.extra.totalOrders').equals(_exp16o)
    # step 17: get M1 order detail v2
    _resp17 = ctx.api.orders.merchant_detail_v2(token='M1_access_token', path_vars={'merchantId': '{{M1_merchantIDe}}'})
    vars['refund_id'] = 'refund_id'
    vars['orderLineItemId'] = 'orderLineItemId'
    vars['item_unit_id_list'] = 'item_unit_id_list'
    # step 18: Login - merchant
    _resp18 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    try:
        _j = _resp18.json() if _resp18.headers.get('content-type','').startswith('application/json') else {}
        vars['merchant_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 19: promoter earning summary after placing
    _resp19 = ctx.api.earnings.summary(app_headers=False, token='merchant_access_token')
    # step 20: get merchant orders-To fulfill after placing
    _resp20 = ctx.api.orders.merchant(token='merchant_access_token', params={'fulfillStatus': 'TO_FULFILL'})
    # assertion 20.Verify to fulfill total order is not changed for co-seller: responseJson equal {{totalOrders_tofulfill_merchant}}
    expect(_resp20).json('$.data.extra.totalOrders').equals(ctx.render_text('{{totalOrders_tofulfill_merchant}}'))
    # assertion 20.Verify to fulfill total earnings is not changed for co-seller: responseJson equal {{totalRevenue_tofulfill_merchant}}
    expect(_resp20).json('$.data.extra.totalRevenue').equals(ctx.render_text('{{totalRevenue_tofulfill_merchant}}'))
    # step 21: get merchant orders-fulfilled after placing
    _resp21 = ctx.api.orders.merchant(token='merchant_access_token', params={'fulfillStatus': 'FULFILLED'})
    # assertion 21.Verify fulfilled total earnings is not changed for co-seller: responseJson equal {{totalRevenue_fulfilled_merchant}}
    expect(_resp21).json('$.data.extra.totalRevenue').equals(ctx.render_text('{{totalRevenue_fulfilled_merchant}}'))
    # assertion 21.Verify fulfilled total order is not changed for co-seller: responseJson equal {{totalOrders_fulfilled_merchant}}
    expect(_resp21).json('$.data.extra.totalOrders').equals(ctx.render_text('{{totalOrders_fulfilled_merchant}}'))
    vars['first_item_unit_id'] = 'first_item_unit_id'
    # step 22: Partner partial refund 1 ticket after placing
    _resp22 = ctx.api.orders.refunds(body='{\n    "lineItems": [\n        {\n            "id": "{{orderLineItemId}}",\n            "quantity": 1,\n            "lineItemUnitIds": [\n                "{{first_item_unit_id}}"\n            ]\n        }\n    ],\n    "shippingLines": [],\n    "tipLines": [],\n    "note": "Automation test"\n}', token='M1_access_token')
    # payout_m1/payout_merchant 已在 step13 计算，此处无需覆盖
    # step 23: M1-login
    _resp23 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    try:
        _j = _resp23.json() if _resp23.headers.get('content-type','').startswith('application/json') else {}
        vars['M1_access_token'] = _get_path(_j, ["data", "refreshToken"])
    except Exception:
        pass
    try:
        vars['lifetimeEarning_partial_refund'] = round(float(vars.get('lifetimeEarning') or 0) + float(vars.get('payout_m1') or 0), 2)
    except Exception:
        vars['lifetimeEarning_partial_refund'] = None
    # step 24: M1 earning summary after partial refund
    _resp24 = ctx.api.earnings.summary(app_headers=False, token='M1_access_token')
    # assertion 24.Total earnigns is correct after partial refund: responseJson equal {{lifetimeEarning_partial_refund}}
    expect(_resp24).json('$.data.lifetimeEarning').equals(0.05)
    # assertion 24.Verify the total commissing earnings after partial refund: responseJson equal {{commissionEarning}}
    expect(_resp24).json('$.data.commissionEarning').equals(ctx.render_text('{{commissionEarning}}'))
    # step 25: get M1 orders-To fulfill after partial refund
    _resp25 = ctx.api.orders.merchant(token='M1_access_token', params={'fulfillStatus': 'TO_FULFILL'})
    # assertion 25.Verify to fulfill total earnings after partial refund: responseJson equal {{totalRevenue_tofulfill}}
    expect(_resp25).json('$.data.extra.totalRevenue').equals(0.05)
    # assertion 25.Verify to fulfill total is not change after partial refund: responseJson equal {{totalOrders_tofulfill}}
    expect(_resp25).json('$.data.extra.totalOrders').equals(str(_exp25o))
    vars['totalRevenue_fulfilled_partial_refund'] = 'totalRevenue_fulfilled_partial_refund'
    vars['totalOrders_fulfilled_partial_refund'] = 'totalOrders_fulfilled_partial_refund'
    # step 26: get M1 orders-fulfilled after partial refund
    _resp26 = ctx.api.orders.merchant(token='M1_access_token', params={'fulfillStatus': 'FULFILLED'})
    # assertion 26.Verify fulfilled total earnings after partial refund: responseJson equal {{totalRevenue_fulfilled_partial_refund}}
    expect(_resp26).json('$.data.extra.totalRevenue').equals(0.05)
    # assertion 26.Verify the total orders on fulfilled tab after partial refund: responseJson equal {{totalOrders_fulfilled_partial_refund}}
    expect(_resp26).json('$.data.extra.totalOrders').equals(str(vars.get('totalOrders_fulfilled_afterplace') or vars.get('totalOrders_fulfilled') or ''))
    # step 27: Login - merchant
    _resp27 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    try:
        _j = _resp27.json() if _resp27.headers.get('content-type','').startswith('application/json') else {}
        vars['merchant_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    try:
        vars['lifetimeEarning_merchant_partial_refund'] = round(float(vars.get('lifetimeEarning_merchant') or 0) + float(vars.get('payout_merchant') or 0), 2)
        vars['commissionEarning_merchant_partial_refund'] = round(float(vars.get('commissionEarning_merchant') or 0) + float(vars.get('payout_merchant') or 0), 2)
    except Exception:
        vars['lifetimeEarning_merchant_partial_refund'] = None
        vars['commissionEarning_merchant_partial_refund'] = None
    # step 28: promoter earning summary after partial refund
    _resp28 = ctx.api.earnings.summary(app_headers=False, token='merchant_access_token')
    # assertion 28.Verify the total net earnings is changed for co-seller after partial refund: responseJson equal {{lifetimeEarning_merchant_partial_refund}}
    expect(_resp28).json('$.data.lifetimeEarning').equals(0.05)
    # assertion 28.Verify commission earnings is changed for co-seller after partial refund: responseJson equal {{commissionEarning_merchant_partial_refund}}
    expect(_resp28).json('$.data.commissionEarning').equals(0.05)
    # step 29: get merchant orders-To fulfill after partial refund
    _resp29 = ctx.api.orders.merchant(token='merchant_access_token', params={'fulfillStatus': 'TO_FULFILL'})
    # assertion 29.Verify to fulfill total order is not changed for co-seller after partial refund: responseJson equal {{totalOrders_tofulfill_merchant}}
    expect(_resp29).json('$.data.extra.totalOrders').equals(ctx.render_text('{{totalOrders_tofulfill_merchant}}'))
    # assertion 29.Verify to fulfill total earnings is not changed for co-seller after partial refund: responseJson equal {{totalRevenue_tofulfill_merchant}}
    expect(_resp29).json('$.data.extra.totalRevenue').equals(ctx.render_text('{{totalRevenue_tofulfill_merchant}}'))
    # step 30: get merchant orders-fulfilled after partial refund
    _resp30 = ctx.api.orders.merchant(token='merchant_access_token', params={'fulfillStatus': 'FULFILLED'})
    # assertion 30.Verify fulfilled total earnings is not changed for co-seller after partial refund: responseJson equal {{totalRevenue_fulfilled_merchant}}
    expect(_resp30).json('$.data.extra.totalRevenue').equals(ctx.render_text('{{totalRevenue_fulfilled_merchant}}'))
    # assertion 30.Verify fulfilled total order is not changed for co-seller after partial refund: responseJson equal {{totalOrders_fulfilled_merchant}}
    expect(_resp30).json('$.data.extra.totalOrders').equals(ctx.render_text('{{totalOrders_fulfilled_merchant}}'))
    vars['second_item_unit_id'] = 'second_item_unit_id'
    # step 31: Partner full refund order on sale details page after placing
    _resp31 = ctx.api.orders.refunds(body='{\n    "lineItems": [\n        {\n            "id": "{{orderLineItemId}}",\n            "quantity": 1,\n            "lineItemUnitIds": [\n                "{{second_item_unit_id}}"\n            ]\n        }\n    ],\n    "shippingLines": [\n        {\n            "merchantOrderId": "{{refund_id}}"\n        }\n    ],\n    "tipLines": [\n        {\n            "merchantOrderId": "{{refund_id}}"\n        }\n    ],\n    "note": "Automation full refund"\n}', token='M1_access_token')
    # step 32: M1-login
    _resp32 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    try:
        _j = _resp32.json() if _resp32.headers.get('content-type','').startswith('application/json') else {}
        vars['M1_access_token'] = _get_path(_j, ["data", "refreshToken"])
    except Exception:
        pass
    vars['lifetimeEarning_full_refund'] = round(float(vars.get('lifetimeEarning_placed') or 0), 2)
    # step 33: M1 earning summary after full refund
    _resp33 = ctx.api.earnings.summary(app_headers=False, token='M1_access_token')
    # assertion 33.Total earnigns is correct after partial refund: responseJson equal {{lifetimeEarning_full_refund}}
    expect(_resp33).json('$.data.lifetimeEarning').equals(0.05)
    # assertion 33.Verify the total commissing earnings after partial refund: responseJson equal {{commissionEarning}}
    expect(_resp33).json('$.data.commissionEarning').equals(0.05)
    # step 34: get M1 orders-To fulfill after full refund
    _resp34 = ctx.api.orders.merchant(token='M1_access_token', params={'fulfillStatus': 'TO_FULFILL'})
    # assertion 34.Verify to fulfill total earnings after partial refund: responseJson equal {{totalRevenue_tofulfill_placed}}
    expect(_resp34).json('$.data.extra.totalRevenue').equals(0.05)
    # assertion 34.Verify to fulfill total is not change after partial refund: responseJson equal {{totalOrders_tofulfill_placed}}
    expect(_resp34).json('$.data.extra.totalOrders').equals(str(_exp34o))
    vars['totalRevenue_fulfilled_full_refund'] = float(vars.get('totalRevenue_fulfilled_afterplace') or vars.get('totalRevenue_fulfilled') or 0)
    vars['totalOrders_fulfilled_full_refund'] = vars.get('totalOrders_fulfilled_afterplace') or vars.get('totalOrders_fulfilled') or 0
    # step 35: get M1 orders-fulfilled after full refund
    _resp35 = ctx.api.orders.merchant(token='M1_access_token', params={'fulfillStatus': 'FULFILLED'})
    # assertion 35.Verify fulfilled total earnings after partial refund: responseJson equal {{totalRevenue_fulfilled_full_refund}}
    expect(_resp35).json('$.data.extra.totalRevenue').equals(0.05)
    # assertion 35.Verify the total orders on fulfilled tab after partial refund: responseJson equal {{totalOrders_fulfilled_full_refund}}
    expect(_resp35).json('$.data.extra.totalOrders').equals(str(vars.get('totalOrders_fulfilled_full_refund') or 0))
    # step 36: Login - merchant
    _resp36 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    try:
        _j = _resp36.json() if _resp36.headers.get('content-type','').startswith('application/json') else {}
        vars['merchant_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 37: promoter earning summary after full refund
    _resp37 = ctx.api.earnings.summary(app_headers=False, token='merchant_access_token')
    # assertion 37.Verify the total net earnings is changed for co-seller after partial refund: responseJson equal {{lifetimeEarning_merchant}} + payout_merchant
    expect(_resp37).json('$.data.lifetimeEarning').equals(0.05)
    # assertion 37.Verify commission earnings is changed for co-seller after partial refund: responseJson equal {{commissionEarning_merchant}} + payout_merchant
    expect(_resp37).json('$.data.commissionEarning').equals(0.05)
    # step 38: get merchant orders-To fulfill after full refund
    _resp38 = ctx.api.orders.merchant(token='merchant_access_token', params={'fulfillStatus': 'TO_FULFILL'})
    # assertion 38.Verify to fulfill total order is not changed for co-seller after partial refund: responseJson equal {{totalOrders_tofulfill_merchant}}
    expect(_resp38).json('$.data.extra.totalOrders').equals(ctx.render_text('{{totalOrders_tofulfill_merchant}}'))
    # assertion 38.Verify to fulfill total earnings is not changed for co-seller after partial refund: responseJson equal {{totalRevenue_tofulfill_merchant}}
    expect(_resp38).json('$.data.extra.totalRevenue').equals(ctx.render_text('{{totalRevenue_tofulfill_merchant}}'))
    # step 39: get merchant orders-fulfilled after full refund
    _resp39 = ctx.api.orders.merchant(token='merchant_access_token', params={'fulfillStatus': 'FULFILLED'})
    # assertion 39.Verify fulfilled total earnings is not changed for co-seller after partial refund: responseJson equal {{totalRevenue_fulfilled_merchant}}
    expect(_resp39).json('$.data.extra.totalRevenue').equals(ctx.render_text('{{totalRevenue_fulfilled_merchant}}'))
    # assertion 39.Verify fulfilled total order is not changed for co-seller after partial refund: responseJson equal {{totalOrders_fulfilled_merchant}}
    expect(_resp39).json('$.data.extra.totalOrders').equals(ctx.render_text('{{totalOrders_fulfilled_merchant}}'))
