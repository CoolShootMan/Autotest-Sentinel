"""Migrated from Apifox case #7897954. Source folder: Event and ticket and redeemed/Ticket redeemed."""
# Apifox Case ID: 7897954  (traceability only — not needed to run)
NAME = "Verify the ticket can be redeemd success"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_redeemed", "suite:linda"]
PRIORITY = 0


CASE_ID = 7897954
ENV_NAME = "Release"

# --- step 1: Get Partner linda05 token ---
# post[extractor]: {"variableName": "linda05_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 44837e99-63db-4850-898c-6b8c6cf5e12f ---
# post[customScript]: const responseData = pm.response.json();
# post: 
# post: 
# post: // 校验业务 code
# post: pm.test("业务 code 为 200", function () {
# post:     pm.expect(responseData.code).to.eql(200);
# post: });
# post: 
# post: // 校验核心数据 count
# post: pm.test("核心数据 count 等于 1", function () {
# post:     pm.expect(responseData.data.units.count).to.eql(1);
# post:     
# post:     // 顺便校验一下 count 的数据类型是数字(Number)
# post:     pm.expect(responseData.data.units.count).to.be.a('number');
# post: });
# --- step 3: 3af00c65-523b-4e80-accb-5b6cf2cd9fc6 ---
# post[customScript]: // ========== 1. 解析响应数据 ==========
# post: let responseData;
# post: try {
# post:   responseData = pm.response.json();
# post: } catch (error) {
# post:   pm.test("响应格式校验：返回有效JSON", () => {
# post:     pm.expect.fail(`JSON解析失败：${error.message}`);
# post:   });
# post:   return;
# post: }
# post: 
# post: // ========== 2. 核心断言：返回成功 ==========
# post: pm.test("接口返回成功", () => {
# post:   // 仅校验核心成功标识
# post:   pm.expect(responseData.code).to.equal(200);
# post:   pm.expect(responseData.message).to.equal("success");
# post:   pm.expect(responseData.data).to.not.be.undefined; // 确保data层级存在
# post: });
# post: 
# post: // ========== 3. 提取totalItemsRedeemed到环境变量 ==========
# post: try {
# post:   // 提取数值
# post:   const totalItemsRedeemed = responseData.data.totalItemsRedeemed;
# post:   // 存入环境变量（供后续接口使用）
# post:   pm.environment.set("totalItemsRedeemed", totalItemsRedeemed);
# post:   
# post:   console.log(`✅ 提取成功：totalItemsRedeemed = ${totalItemsRedeemed}`);
# post: } catch (error) {
# post:   pm.test("提取totalItemsRedeemed失败", () => {
# post:     pm.expect.fail(`提取失败原因：${error.message}`);
# post:   });
# post: }
# --- step 4: 9740ec98-e46c-4e1e-9f04-732b196c2f05 ---
# pre: pm.environment.set("scan_token", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXJhdG9ySWQiOiI4NGEwZGU0NC00N2U0LTRhMzgtODgzZS1kOTllZDE5NGQ3ZDciLCJldmVudElkIjoiZmI1ZGYwOTUtYjY4ZC00NWY2LWFkYzAtMjIxMTQyOGQwYThjIn0.mBczmfnf7zWhLvcX3gW0jRnxKWFpIbDyiz6_76N_xGU");
# pre: 
# post[customScript]: // ========== 配置区（所有预期值集中管理，便于维护） ==========
# post: const ASSERT_CONFIG = {
# post:   // 基础响应状态配置
# post:   base: {
# post:     code: 200,
# post:     message: "success"
# post:   },
# post:   // 核销成功核心状态配置
# post:   redemption: {
# post:     listingType: "TICKET",
# post:     mainStatus: "COMPLETED", // 外层data.status
# post:     itemStatus: "COMPLETED", // items[0].status
# post:     itemOrderStatus: "COMPLETED", // items[0].orderStatus
# post:     eventName: "Automation test T4131" // 校验活动名称，确保订单归属正确
# post:   }
# post: };
# post: 
# post: // ========== 1. 解析响应数据（带异常处理） ==========
# post: let responseData;
# post: try {
# post:   responseData = pm.response.json();
# post: } catch (error) {
# post:   pm.test("响应体格式校验：返回有效的JSON数据", () => {
# post:     pm.expect.fail(`JSON解析失败，原因：${error.message}`);
# post:   });
# post:   return;
# post: }
# post: 
# post: // ========== 通用工具函数 ==========
# post: /**
# post:  * 安全获取嵌套对象属性，避免层级缺失报错
# post:  * @param {Object} obj 源对象
# post:  * @param {Array} path 属性路径数组
# post:  * @param {*} defaultValue 默认值
# post:  * @returns {*} 属性值或默认值
# post:  */
# post: function getNestedProperty(obj, path, defaultValue = undefined) {
# post:   return path.reduce((acc, curr) => {
# post:     return (acc !== null && acc !== undefined) ? acc[curr] : defaultValue;
# post:   }, obj);
# post: }
# post: 
# post: // ========== 2. 核心字段断言 ==========
# post: /**
# post:  * 断言1：校验基础响应状态（code/message/request_id）
# post:  */
# post: pm.test("响应状态校验：code=200 且 message=success", () => {
# post:   // 校验code字段
# post:   pm.expect(responseData).to.have.property("code");
# post:   pm.expect(responseData.code)
# post:     .to.be.a("number")
# post:     .and.equal(ASSERT_CONFIG.base.code, `code应为${ASSERT_CONFIG.base.code}，实际为${responseData.code}`);
# post:   
# post:   // 校验message字段
# post:   pm.expect(responseData).to.have.property("message");
# post:   pm.expect(responseData.message)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.base.message, `message应为"${ASSERT_CONFIG.base.message}"，实际为"${responseData.message}"`);
# post:   
# post:   // 校验request_id存在且为非空字符串
# post:   pm.expect(responseData).to.have.property("request_id");
# post:   pm.expect(responseData.request_id)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post: });
# post: 
# post: /**
# post:  * 断言2：校验数据结构完整性（基础层级）
# post:  */
# post: pm.test("数据结构校验：核心层级字段完整", () => {
# post:   // 校验data根节点存在
# post:   pm.expect(responseData).to.have.property("data");
# post:   const data = responseData.data;
# post: 
# post:   // 校验外层核心字段存在
# post:   pm.expect(data).to.have.property("listingType");
# post:   pm.expect(data).to.have.property("status");
# post:   pm.expect(data).to.have.property("numberCode");
# post:   pm.expect(data).to.have.property("orderNumber");
# post:   pm.expect(data).to.have.property("items");
# post: 
# post:   // 校验items为非空数组
# post:   pm.expect(data.items)
# post:     .to.be.an("array")
# post:     .and.not.be.empty;
# post: });
# post: 
# post: /**
# post:  * 断言3：核心校验 - 核销成功状态（重点）
# post:  */
# post: pm.test("核销状态校验：订单已完成核销（COMPLETED）", () => {
# post:   const data = responseData.data;
# post:   const firstItem = data.items[0];
# post: 
# post:   // 1. 校验外层status为COMPLETED
# post:   pm.expect(data.status)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.redemption.mainStatus, 
# post:       `外层status应为${ASSERT_CONFIG.redemption.mainStatus}，实际为${data.status}`);
# post:   
# post:   // 2. 校验items[0].status为COMPLETED
# post:   pm.expect(firstItem).to.have.property("status");
# post:   pm.expect(firstItem.status)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.redemption.itemStatus, 
# post:       `items[0].status应为${ASSERT_CONFIG.redemption.itemStatus}，实际为${firstItem.status}`);
# post:   
# post:   // 3. 校验items[0].orderStatus为COMPLETED
# post:   pm.expect(firstItem).to.have.property("orderStatus");
# post:   pm.expect(firstItem.orderStatus)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.redemption.itemOrderStatus, 
# post:       `items[0].orderStatus应为${ASSERT_CONFIG.redemption.itemOrderStatus}，实际为${firstItem.orderStatus}`);
# post:   
# post:   // 4. 校验核销时间存在（redeemedAt非空），进一步验证核销完成
# post:   pm.expect(firstItem).to.have.property("redeemedAt");
# post:   pm.expect(firstItem.redeemedAt)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post: });
# post: 
# post: /**
# post:  * 断言4：校验核心业务字段（确保订单归属正确）
# post:  */
# post: pm.test("业务字段校验：订单及活动信息匹配", () => {
# post:   const data = responseData.data;
# post:   const firstItem = data.items[0];
# post:   const extraInfo = getNestedProperty(firstItem, ['extraInfo']);
# post: 
# post:   // 1. 校验listingType为TICKET（票务类型）
# post:   pm.expect(data.listingType)
# post:     .to.equal(ASSERT_CONFIG.redemption.listingType, 
# post:       `listingType应为${ASSERT_CONFIG.redemption.listingType}，实际为${data.listingType}`);
# post:   
# post:   // 2. 校验活动名称匹配
# post:   pm.expect(extraInfo).to.have.property("event");
# post:   pm.expect(extraInfo.event)
# post:     .to.equal(ASSERT_CONFIG.redemption.eventName, 
# post:       `活动名称应为${ASSERT_CONFIG.redemption.eventName}，实际为${extraInfo.event}`);
# post:   
# post:   // 3. 校验订单号一致性（外层与item内订单号一致）
# post:   pm.expect(data.orderNumber)
# post:     .to.equal(firstItem.orderNumber, 
# post:       `外层orderNumber与items内不一致，外层：${data.orderNumber}，item内：${firstItem.orderNumber}`);
# post:   
# post:   // 4. 校验核销数量为1（正常核销数量）
# post:   pm.expect(firstItem.quantity)
# post:     .to.be.a("number")
# post:     .and.equal(1, `核销数量应为1，实际为${firstItem.quantity}`);
# post: });
# post: 
# post: // ========== 3. 校验通过提示 ==========
# post: console.log("✅ 核销状态校验完成，订单已成功核销！");
# post: console.log("订单号：", responseData.data.orderNumber);
# post: console.log("核销时间：", responseData.data.items[0].redeemedAt);
# post: console.log("订单状态：", responseData.data.items[0].orderStatus);
# --- step 6: 0c7a54ab-93db-4faf-bdc1-7ed00195d329 ---
# post[customScript]: // ========== 1. 解析响应数据 ==========
# post: let responseData;
# post: try {
# post:   responseData = pm.response.json();
# post: } catch (error) {
# post:   pm.test("响应格式校验：返回有效JSON", () => {
# post:     pm.expect.fail(`JSON解析失败：${error.message}`);
# post:   });
# post:   return;
# post: }
# post: 
# post: // ========== 2. 基础断言：接口返回成功 ==========
# post: pm.test("接口返回成功", () => {
# post:   pm.expect(responseData.code).to.equal(200);
# post:   pm.expect(responseData.message).to.equal("success");
# post:   pm.expect(responseData.data).to.not.be.undefined;
# post: });
# post: 
# post: // ========== 3. 核心断言：totalItemsRedeemed = 原值 + 1 ==========
# post: pm.test("核销后totalItemsRedeemed数值正确（原值+1）", () => {
# post:   // 1. 读取核销前存入的数值（环境变量）
# post:   const preRedeemedCount = pm.environment.get("totalItemsRedeemed");
# post:   // 校验环境变量存在，避免前置步骤未执行
# post:   pm.expect(preRedeemedCount, "未找到核销前的totalItemsRedeemed值，请先运行前置接口").to.not.be.undefined;
# post:   
# post:   // 2. 转换为数字类型（避免字符串拼接）
# post:   const preCount = Number(preRedeemedCount);
# post:   pm.expect(!isNaN(preCount), "核销前数值格式错误，非有效数字").to.be.true;
# post: 
# post:   // 3. 获取核销后的数值
# post:   const currentRedeemedCount = responseData.data.totalItemsRedeemed;
# post:   pm.expect(currentRedeemedCount, "核销后totalItemsRedeemed字段缺失").to.not.be.undefined;
# post: 
# post:   // 4. 核心校验：当前值 = 原值 + 1
# post:   pm.expect(currentRedeemedCount)
# post:     .to.equal(preCount + 1, 
# post:       `核销后数值错误！预期：${preCount + 1}（原值${preCount}+1），实际：${currentRedeemedCount}`);
# post:   
# post:   console.log(`✅ 数值校验通过：核销前=${preCount}，核销后=${currentRedeemedCount}`);
# post: });
# --- step 7: 02705f5d-2197-49bd-a5fd-b84785940596 ---
# pre: pm.environment.set("scan_token", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXJhdG9ySWQiOiI4NGEwZGU0NC00N2U0LTRhMzgtODgzZS1kOTllZDE5NGQ3ZDciLCJldmVudElkIjoiZmI1ZGYwOTUtYjY4ZC00NWY2LWFkYzAtMjIxMTQyOGQwYThjIn0.mBczmfnf7zWhLvcX3gW0jRnxKWFpIbDyiz6_76N_xGU");
# pre: 
# post[customScript]: // ========== 配置区（核心预期值集中管理） ==========
# post: const ASSERT_CONFIG = {
# post:   // 核心错误状态配置
# post:   error: {
# post:     code: 400,
# post:     message: "This item has already been redeemed"
# post:   },
# post:   // 核销状态辅助校验（已核销的特征值）
# post:   redemption: {
# post:     mainStatus: "COMPLETED",
# post:     itemStatus: "COMPLETED",
# post:     itemOrderStatus: "COMPLETED"
# post:   }
# post: };
# post: 
# post: // ========== 1. 解析响应数据（带异常处理） ==========
# post: let responseData;
# post: try {
# post:   responseData = pm.response.json();
# post: } catch (error) {
# post:   pm.test("响应体格式校验：返回有效的JSON数据", () => {
# post:     pm.expect.fail(`JSON解析失败，原因：${error.message}`);
# post:   });
# post:   return;
# post: }
# post: 
# post: // ========== 通用工具函数 ==========
# post: /**
# post:  * 安全获取嵌套对象属性，避免层级缺失报错
# post:  * @param {Object} obj 源对象
# post:  * @param {Array} path 属性路径数组
# post:  * @param {*} defaultValue 默认值
# post:  * @returns {*} 属性值或默认值
# post:  */
# post: function getNestedProperty(obj, path, defaultValue = undefined) {
# post:   return path.reduce((acc, curr) => {
# post:     return (acc !== null && acc !== undefined) ? acc[curr] : defaultValue;
# post:   }, obj);
# post: }
# post: 
# post: // ========== 2. 核心断言（重点校验400和错误提示） ==========
# post: /**
# post:  * 断言1：核心错误状态校验 - code=400 且 message=This item has already been redeemed
# post:  */
# post: pm.test("错误状态校验：code=400 且 message=This item has already been redeemed（核销码已被使用）", () => {
# post:   // 校验code字段（重点：400错误码）
# post:   pm.expect(responseData).to.have.property("code");
# post:   pm.expect(responseData.code)
# post:     .to.be.a("number")
# post:     .and.equal(ASSERT_CONFIG.error.code, 
# post:       `错误码应为${ASSERT_CONFIG.error.code}，实际为${responseData.code}`);
# post:   
# post:   // 校验message字段（重点：核销码已被使用的提示）
# post:   pm.expect(responseData).to.have.property("message");
# post:   pm.expect(responseData.message)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.error.message, 
# post:       `错误提示应为"${ASSERT_CONFIG.error.message}"，实际为"${responseData.message}"`);
# post: });
# post: 
# post: /**
# post:  * 断言2：辅助校验 - request_id和stack字段存在（错误日志完整性）
# post:  */
# post: pm.test("错误日志校验：request_id和stack字段存在", () => {
# post:   // 校验request_id存在且非空
# post:   pm.expect(responseData).to.have.property("request_id");
# post:   pm.expect(responseData.request_id)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post:   
# post:   // 校验stack字段存在（错误堆栈，便于排查问题）
# post:   pm.expect(responseData).to.have.property("stack");
# post:   pm.expect(responseData.stack)
# post:     .to.be.a("string")
# post:     .and.include(ASSERT_CONFIG.error.message, "错误堆栈应包含核销码已被使用的提示");
# post: });
# post: 
# post: /**
# post:  * 断言3：业务辅助校验 - 核销状态为COMPLETED（佐证码已被核销）
# post:  */
# post: pm.test("核销状态校验：数据中status均为COMPLETED（佐证码已被使用）", () => {
# post:   const data = responseData.data;
# post:   pm.expect(data, "data字段缺失").to.not.be.undefined;
# post: 
# post:   // 校验外层status为COMPLETED
# post:   pm.expect(data.status)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.redemption.mainStatus, 
# post:       `外层status应为${ASSERT_CONFIG.redemption.mainStatus}，实际为${data.status}`);
# post:   
# post:   // 校验items[0]的status和orderStatus均为COMPLETED
# post:   const firstItem = getNestedProperty(data, ['items', 0]);
# post:   pm.expect(firstItem, "items[0]字段缺失").to.not.be.undefined;
# post:   
# post:   pm.expect(firstItem.status)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.redemption.itemStatus, 
# post:       `items[0].status应为${ASSERT_CONFIG.redemption.itemStatus}，实际为${firstItem.status}`);
# post:   
# post:   pm.expect(firstItem.orderStatus)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.redemption.itemOrderStatus, 
# post:       `items[0].orderStatus应为${ASSERT_CONFIG.redemption.itemOrderStatus}，实际为${firstItem.orderStatus}`);
# post:   
# post:   // 校验redeemedAt存在（有核销时间，进一步佐证码已被使用）
# post:   pm.expect(firstItem.redeemedAt)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post: });
# post: 
# post: // ========== 3. 校验通过提示 ==========
# post: console.log(`✅ 核心错误断言完成：code=${responseData.code}，message="${responseData.message}"`);
# post: console.log("核销码已被使用，核销时间：", responseData.data.items[0].redeemedAt);
# post: console.log("订单号：", responseData.data.orderNumber);




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_linda_t4293_verify_the_ticket_can_be_redeemd_success(ctx):
    """Apifox case #7897954: Linda_T4293_Verify_the_ticket_can_be_redeemd_success"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # Original Apifox pre-script set scan_token to a hardcoded curator/event JWT used
    # by the /order/verification (redeem) steps. The migration dropped this pre-script,
    # so we restore it here. (Apifox pre: pm.environment.set("scan_token", "eyJhbGci..."))
    vars['scan_token'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXJhdG9ySWQiOiI4NGEwZGU0NC00N2U0LTRhMzgtODgzZS1kOTllZDE5NGQ3ZDciLCJldmVudElkIjoiZmI1ZGYwOTUtYjY4ZC00NWY2LWFkYzAtMjIxMTQyOGQwYThjIn0.mBczmfnf7zWhLvcX3gW0jRnxKWFpIbDyiz6_76N_xGU'
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+05@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}')
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    # step 2: 44837e99-63db-4850-898c-6b8c6cf5e12f
    _resp2 = ctx.api.orders.ticket_status(body='{\r\n    "orderLineItemId": "4043096b-7df1-4c2b-880a-9c7b7baec411",\r\n    "orderLineItemUnitIds": [\r\n        "763118ce-9ac4-4778-9683-d8e799192083"\r\n    ],\r\n    "status": "IN_PROCESSING"\r\n}', token='linda05_token')
    # === 断言（由Apifox customScript翻译）===
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"step2 code != 200, got {_j2.get('code')}"
    _units2 = (_j2.get('data') or {}).get('units') or {}
    assert _units2.get('count') == 1, f"step2 data.units.count != 1, got {_units2.get('count')}"
    assert isinstance(_units2.get('count'), (int, float)), f"step2 count 非数字: {_units2.get('count')}"
    # step 3: 3af00c65-523b-4e80-accb-5b6cf2cd9fc6
    _resp3 = ctx.api.events.fb5df095_b68d_45f6_adc0_2211428d0a8c_metrics_summary(body=None, token='linda05_token')
    # === 断言/提取（由Apifox customScript翻译）===
    _j3 = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
    assert _j3.get('code') == 200, f"step3 code != 200, got {_j3.get('code')}"
    assert _j3.get('message') == 'success', f"step3 message != success, got {_j3.get('message')}"
    assert _j3.get('data') is not None, "step3 data 缺失"
    _totalRedeemed = _get_path(_j3, ["data", "totalItemsRedeemed"])
    assert _totalRedeemed is not None, "step3 totalItemsRedeemed 缺失"
    vars['totalItemsRedeemed'] = _totalRedeemed
    # step 4: 9740ec98-e46c-4e1e-9f04-732b196c2f05
    _resp4 = ctx.api.orders.verification(body='{\n    "token": "{{scan_token}}",\n    "id": "33804632",\n    "forceRedeem": false\n}', token='linda05_token')
    # === 断言（由Apifox customScript翻译）===
    _j4 = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
    assert _j4.get('code') == 200, f"step4 code != 200, got {_j4.get('code')}"
    assert _j4.get('message') == 'success', f"step4 message != success, got {_j4.get('message')}"
    assert isinstance(_j4.get('request_id'), str) and _j4.get('request_id'), "step4 request_id 缺失"
    _d4 = _j4.get('data')
    assert isinstance(_d4, dict), "step4 data 非对象"
    for _k in ('listingType', 'status', 'numberCode', 'orderNumber', 'items'):
        assert _k in _d4, f"step4 data 缺少字段 {_k}"
    _items4 = _d4.get('items')
    assert isinstance(_items4, list) and len(_items4) > 0, "step4 data.items 为空"
    _fi4 = _items4[0]
    assert _d4.get('status') == 'COMPLETED', f"step4 data.status != COMPLETED, got {_d4.get('status')}"
    assert _fi4.get('status') == 'COMPLETED', f"step4 items[0].status != COMPLETED, got {_fi4.get('status')}"
    assert _fi4.get('orderStatus') == 'COMPLETED', f"step4 items[0].orderStatus != COMPLETED, got {_fi4.get('orderStatus')}"
    assert isinstance(_fi4.get('redeemedAt'), str) and _fi4.get('redeemedAt'), "step4 redeemedAt 缺失"
    assert _d4.get('listingType') == 'TICKET', f"step4 listingType != TICKET, got {_d4.get('listingType')}"
    _extra4 = _fi4.get('extraInfo') or {}
    assert _extra4.get('event') == 'Automation test T4131', f"step4 活动名不匹配: {_extra4.get('event')}"
    assert _d4.get('orderNumber') == _fi4.get('orderNumber'), f"step4 订单号不一致: 外层{_d4.get('orderNumber')} vs item{_fi4.get('orderNumber')}"
    assert isinstance(_fi4.get('quantity'), (int, float)) and _fi4.get('quantity') == 1, f"step4 quantity != 1, got {_fi4.get('quantity')}"
    # step 6: 0c7a54ab-93db-4faf-bdc1-7ed00195d329
    _resp6 = ctx.api.events.fb5df095_b68d_45f6_adc0_2211428d0a8c_metrics_summary(body=None, token='linda05_token')
    # === 断言（由Apifox customScript翻译）===
    _j6 = _resp6.json() if _resp6.headers.get('content-type','').startswith('application/json') else {}
    assert _j6.get('code') == 200, f"step6 code != 200, got {_j6.get('code')}"
    assert _j6.get('message') == 'success', f"step6 message != success, got {_j6.get('message')}"
    assert _j6.get('data') is not None, "step6 data 缺失"
    _preCount6 = vars.get('totalItemsRedeemed')
    assert _preCount6 is not None, "未找到核销前 totalItemsRedeemed"
    _preNum6 = float(_preCount6)
    _cur6 = _get_path(_j6, ["data", "totalItemsRedeemed"])
    assert _cur6 is not None, "step6 totalItemsRedeemed 缺失"
    assert _cur6 == _preNum6 + 1, f"step6 核销后数值错误: 预期{_preNum6 + 1}, 实际{_cur6}"
    # step 7: 02705f5d-2197-49bd-a5fd-b84785940596
    _resp7 = ctx.api.orders.verification(body='{\n    "token": "{{scan_token}}",\n    "id": "33804632",\n    "forceRedeem": false\n}', token='linda05_token')
    # === 断言（由Apifox customScript翻译）===
    _j7 = _resp7.json() if _resp7.headers.get('content-type','').startswith('application/json') else {}
    assert _j7.get('code') == 400, f"step7 code != 400, got {_j7.get('code')}"
    assert _j7.get('message') == 'This item has already been redeemed', f"step7 message 不匹配: {_j7.get('message')}"
    assert isinstance(_j7.get('request_id'), str) and _j7.get('request_id'), "step7 request_id 缺失"
    assert isinstance(_j7.get('stack'), str) and 'This item has already been redeemed' in _j7.get('stack', ''), "step7 stack 未包含错误提示"
    _d7 = _j7.get('data')
    assert _d7 is not None, "step7 data 缺失"
    assert _d7.get('status') == 'COMPLETED', f"step7 data.status != COMPLETED, got {_d7.get('status')}"
    _fi7 = (_d7.get('items') or [{}])[0]
    assert _fi7.get('status') == 'COMPLETED', f"step7 items[0].status != COMPLETED, got {_fi7.get('status')}"
    assert _fi7.get('orderStatus') == 'COMPLETED', f"step7 items[0].orderStatus != COMPLETED, got {_fi7.get('orderStatus')}"
    assert isinstance(_fi7.get('redeemedAt'), str) and _fi7.get('redeemedAt'), "step7 redeemedAt 缺失"
