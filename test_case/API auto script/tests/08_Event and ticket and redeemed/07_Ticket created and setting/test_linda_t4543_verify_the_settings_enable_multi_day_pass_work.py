"""Migrated from Apifox case #7802190. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 7802190  (traceability only — not needed to run)
NAME = "Verify the settings Enable multi-day pass work"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:linda"]
PRIORITY = 0


CASE_ID = 7802190
ENV_NAME = "Release"

# --- step 1: dece4880-ddc9-4ca0-8561-c369469fb798 ---
# post[extractor]: {"variableName": "yuxiao999_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: d5306c79-bc8c-4be8-bcec-9b3d520ced47 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 在 items 数组中查找 title 为 "event-for-API-testing" 的事件
# post: const targetEvent = responseData.data?.items?.find(
# post:     item => item.title === "event-for-API-testing"
# post: );
# post: 
# post: // 3. 断言并设置环境变量 (event_id, startDateDisplay, endDateDisplay)
# post: pm.test("找到 title 为 'event-for-API-testing' 的事件并提取相关环境变量", function () {
# post:     // 断言找到目标事件
# post:     pm.expect(targetEvent, "未找到 title 为 'event-for-API-testing' 的事件").to.not.be.undefined;
# post:     
# post:     // 提取并断言 event_id
# post:     pm.expect(targetEvent.id, "提取的 id 为空").to.be.a('string').and.not.empty;
# post:     pm.environment.set("event_id", targetEvent.id);
# post:     
# post:     // 提取并断言 startDateDisplay 与 endDateDisplay
# post:     pm.expect(targetEvent.startDateDisplay, "startDateDisplay 为空").to.be.a('string').and.not.empty;
# post:     pm.expect(targetEvent.endDateDisplay, "endDateDisplay 为空").to.be.a('string').and.not.empty;
# post:     
# post:     pm.environment.set("startDateDisplay", targetEvent.startDateDisplay);
# post:     pm.environment.set("endDateDisplay", targetEvent.endDateDisplay);
# post: 
# post:     console.log("已成功提取 event_id:", targetEvent.id);
# post:     console.log("已成功提取 startDateDisplay:", targetEvent.startDateDisplay);
# post:     console.log("已成功提取 endDateDisplay:", targetEvent.endDateDisplay);
# post: });
# --- step 3: a162f41c-de75-439f-ba5f-5022f8dbb567 ---
# post[customScript]: // 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 查找 title 为 'event-for-API-testing' 的项
# post: const targetItem = responseData.data.items.find(
# post:     item => item.title === "event-for-API-testing"
# post: );
# post: 
# post: if (targetItem) {
# post:     // 设置环境变量 postId
# post:     pm.environment.set("postId", targetItem.id);
# post:     console.log("成功提取 postId:", targetItem.id);
# post: } else {
# post:     console.error("未找到匹配的 item");
# post: }
# --- step 4: 806f3d0e-23bc-4980-933f-70d2cb989003 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 断言并设置环境变量 catalog_id
# post: pm.test("成功提取 data.id 并设置为环境变量 catalog_id", function () {
# post:     // 校验 data 及其 id 字段存在
# post:     pm.expect(responseData.data).to.be.an('object').that.is.not.null;
# post:     pm.expect(responseData.data.id, "data.id 为空或不存在").to.be.a('string').and.not.empty;
# post: 
# post:     // 获取并保存环境变量
# post:     const catalogId = responseData.data.id;
# post:     pm.environment.set("catalog_id", catalogId);
# post: 
# post:     console.log("已成功提取 catalog_id:", catalogId);
# post: });
# --- step 5: 3259d9bd-b11c-4e6c-b6e2-7d46b9409108 ---
# pre: // 1. 从环境变量获取上一步提取出的日期字符串
# pre: const startDateStr = pm.environment.get("startDateDisplay"); // 例: "2026-08-27"
# pre: const endDateStr = pm.environment.get("endDateDisplay");     // 例: "2026-09-03"
# pre: 
# pre: // 解析为 Date 对象（附加 "T00:00:00" 确保按本地/零时区精确解析，避免时区偏差）
# pre: const startDate = new Date(`${startDateStr}T00:00:00`);
# pre: const endDate = new Date(`${endDateStr}T00:00:00`);
# pre: 
# pre: // 2. 动态生成多日票 multipleDaysPass 数组（生成 8 天的数据）
# pre: const totalDays = 8;
# pre: const dynamicDays = [];
# pre: 
# pre: for (let i = 0; i < totalDays; i++) {
# pre:     const currentDate = new Date(startDate);
# pre:     currentDate.setDate(startDate.getDate() + i);
# pre: 
# pre:     const year = currentDate.getFullYear();
# pre:     const month = String(currentDate.getMonth() + 1).padStart(2, '0');
# pre:     const day = String(currentDate.getDate()).padStart(2, '0');
# pre:     const formattedDate = `${year}-${month}-${day}`;
# pre: 
# pre:     // 自动判定：在 startDate 到 endDate 范围内的日期为 true，超出范围的为 false
# pre:     const isEnabled = currentDate >= startDate && currentDate <= endDate;
# pre: 
# pre:     dynamicDays.push({
# pre:         "date": formattedDate,
# pre:         "enabled": isEnabled,
# pre:         "checkInStart": `${formattedDate} 00:00:00`,
# pre:         "checkInEnd": `${formattedDate} 23:59:59`
# pre:     });
# pre: }
# pre: 
# pre: // 3. 写入环境变量
# pre: pm.environment.set("multipleDaysPass_days", JSON.stringify(dynamicDays));
# pre: 
# pre: // 4. 日志输出验证
# pre: console.log(`[使用提取的日期范围]: ${startDateStr} ~ ${endDateStr}`);
# pre: console.log("[动态 Days 数据]:", dynamicDays);
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础断言
# post: pm.test("HTTP Status Code 201", function () {
# post:     pm.response.to.have.status(201);
# post: });
# post: 
# post: pm.test("Response code is 200 and message is success", function () {
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post:     pm.expect(responseData.data.id).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 3. 提取 data.id 并设置环境变量 productId
# post: if (responseData.data && responseData.data.id) {
# post:     pm.environment.set("productId", responseData.data.id);
# post:     console.log("设置环境变量 productId:", responseData.data.id);
# post:     }
# --- step 7: 978083e9-c8fa-43a6-98fb-69cdf3d1b8f5 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: cb7226e4-64d6-4967-8caf-10aacfcfbbaa ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 查找 title 为 "auto-test Verify the Require customer-provided details can be apply success" 的产品
# post: const targetProduct = responseData.data.relatedProducts.find(
# post:     item => item.title === "auto testing with turn on multiple day pass"
# post: );
# post: 
# post: // 2. 断言并提取 displayVariantId 为环境变量 promoterProductId
# post: pm.test("找到目标产品并提取 displayVariantId 作为 promoterProductId", function () {
# post:     // 断言目标产品存在
# post:     // pm.expect(targetProduct).to.not.be.undefined;
# post:     pm.expect(targetProduct.displayVariantId).to.be.a('string').and.not.empty;
# post: 
# post:     // 获取 displayVariantId
# post:     const targetVariantId = targetProduct.displayVariantId;
# post: 
# post:     // 设置为环境变量 promoterProductId
# post:     pm.environment.set("promoterProductId", targetVariantId);
# post:     console.log("已成功将 displayVariantId 设置为 promoterProductId:", targetVariantId);
# post: });
# --- step 9: Get consumer linda10 token ---
# post[extractor]: {"variableName": "linda10_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: 75f96309-d89c-4691-90ca-f0b52e3df23b ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: buy now ---
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 12: place order ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应断言
# post: pm.test("响应message 为 success", function () {
# post:     pm.expect(responseData.message, "message 返回不正确").to.eql("success");
# post: });
# post: 
# post: // 3. 提取 orderNumbers[0] 并设置为环境变量 orderNumber
# post: pm.test("提取 orderNumber 并设置为环境变量", function () {
# post:     const orderNumber = responseData.data?.orderNumbers?.[0];
# post:     pm.expect(orderNumber, "orderNumbers[0] 不存在或为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 设置环境变量 orderNumber
# post:     pm.environment.set("orderNumber", orderNumber);
# post:     console.log("已成功提取 orderNumber:", orderNumber);
# post: });
# post: 
# post: // 4. 断言 isMultipleDaysPassEnabled 和 multipleDaysPass 对象
# post: pm.test("断言 isMultipleDaysPassEnabled 为 true 且 multipleDaysPass 数据匹配", function () {
# post:     // 获取环境变量预期的日期
# post:     const expectedStartDate = pm.environment.get("startDateDisplay");
# post:     const expectedEndDate = pm.environment.get("endDateDisplay");
# post: 
# post:     // 定位 confirmation.lineItems[0]
# post:     const lineItem = responseData.data?.confirmation?.lineItems?.[0];
# post:     pm.expect(lineItem, "confirmation.lineItems[0] 不存在").to.be.an('object');
# post: 
# post:     // 1) 断言多天票开关开启
# post:     pm.expect(lineItem.isMultipleDaysPassEnabled, "isMultipleDaysPassEnabled 不为 true").to.be.true;
# post: 
# post:     // 2) 断言 multipleDaysPass 对象结构
# post:     const pass = lineItem.multipleDaysPass;
# post:     pm.expect(pass, "multipleDaysPass 对象不存在").to.be.an('object');
# post: 
# post:     // 校验时间戳字段 startDate / endDate
# post:     pm.expect(pass.startDate, "startDate 格式不正确").to.be.a('string').and.not.empty;
# post:     pm.expect(pass.endDate, "endDate 格式不正确").to.be.a('string').and.not.empty;
# post: 
# post:     // 校验与环境变量比对的显示日期（startDateDisplay / endDateDisplay）
# post:     pm.expect(pass.startDateDisplay, "startDateDisplay 不存在或为空").to.be.a('string').and.not.empty;
# post:     pm.expect(pass.endDateDisplay, "endDateDisplay 不存在或为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 3) 校验 days 数组完整性
# post:     pm.expect(pass.days, "days 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     pass.days.forEach(function (day, index) {
# post:         pm.expect(day.date, `days[${index}].date 不存在`).to.be.a('string').and.not.empty;
# post:         pm.expect(day.enabled, `days[${index}].enabled 必须为布尔值`).to.be.a('boolean');
# post:         pm.expect(day.checkInStart, `days[${index}].checkInStart 不存在`).to.be.a('string').and.not.empty;
# post:         pm.expect(day.checkInEnd, `days[${index}].checkInEnd 不存在`).to.be.a('string').and.not.empty;
# post:     });
# post: 
# post:     // 筛选并验证存在 enabled=true 的有效天数
# post:     const enabledDays = pass.days.filter(day => day.enabled === true);
# post:     pm.expect(enabledDays.length, "days 中没有 enabled=true 的有效日期").to.be.above(0);
# post: 
# post:     // 4) 与环境变量存储的值比对
# post:     if (expectedStartDate) {
# post:         pm.expect(pass.startDateDisplay, "startDateDisplay 与环境变量不匹配").to.eql(expectedStartDate);
# post:     }
# post:     if (expectedEndDate) {
# post:         // 说明：响应中 pass.endDateDisplay 是多日票实际开启有效期的最后一天（如 2026-08-30）
# post:         console.log(`[日期比对] 响应展示截至日期: ${pass.endDateDisplay}, 环境变量预期范围截至: ${expectedEndDate}`);
# post:     }
# post: 
# post:     console.log(`multipleDaysPass 校验成功！共 ${pass.days.length} 天，其中有效天数: ${enabledDays.length}`);
# post: });
# --- step 13: Check the merchant order detail exist ticket Redemptions contents ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础状态码与业务 code 断言
# post: pm.test("响应状态码为 200 且 message 为 success", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message, "message 返回不正确").to.eql("success");
# post: });
# post: 
# post: // 3. 断言 isMultipleDaysPassEnabled 及 ticketRedemptions 的逻辑性
# post: pm.test("断言 ticketRedemptions 的日期区间及连续性匹配", function () {
# post:     // 从环境变量中获取预期的开始日期 (如 "2026-08-27")
# post:     const expectedStartDate = pm.environment.get("startDateDisplay");
# post: 
# post:     // 定位 data.lineItems[0]
# post:     const lineItem = responseData.data?.lineItems?.[0];
# post:     pm.expect(lineItem, "lineItems[0] 不存在").to.be.an('object');
# post: 
# post:     // 1) 断言多天票开关开启
# post:     pm.expect(lineItem.isMultipleDaysPassEnabled, "isMultipleDaysPassEnabled 不为 true").to.be.true;
# post: 
# post:     // 2) 获取 orderLineItemUnits[0] 下的 ticketRedemptions 数组
# post:     const unit = lineItem.orderLineItemUnits?.[0];
# post:     pm.expect(unit, "orderLineItemUnits[0] 不存在").to.be.an('object');
# post: 
# post:     const redemptions = unit.ticketRedemptions;
# post:     pm.expect(redemptions, "ticketRedemptions 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 3) 基础属性完整性校验 (id, status, validDateTimeStartDisplay, expired)
# post:     redemptions.forEach((item, index) => {
# post:         pm.expect(item.id, `第 ${index} 项缺少 id`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.status, `第 ${index} 项 status 不正确`).to.eql("IN_PROCESSING");
# post:         pm.expect(item.validDateTimeStartDisplay, `第 ${index} 项缺少 validDateTimeStartDisplay`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.validDateTimeEndDisplay, `第 ${index} 项缺少 validDateTimeEndDisplay`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.expired, `第 ${index} 项缺少 expired 状态`).to.be.a('boolean');
# post:     });
# post: 
# post:     // 4) 连续性与首项日期校验
# post:     const actualFirstDate = redemptions[0].validDateTimeStartDisplay.split(" ")[0];
# post:     const actualLastDate = redemptions[redemptions.length - 1].validDateTimeStartDisplay.split(" ")[0];
# post: 
# post:     // A. 首项日期与环境变量 startDateDisplay 对齐
# post:     if (expectedStartDate) {
# post:         pm.expect(actualFirstDate, "首项日期与 startDateDisplay 不符").to.eql(expectedStartDate);
# post:     }
# post: 
# post:     // B. 校验日期的连续性 (逐天递增 +1 天)
# post:     const baseDate = new Date(`${actualFirstDate}T00:00:00`);
# post:     
# post:     redemptions.forEach((item, i) => {
# post:         const currentDate = new Date(baseDate);
# post:         currentDate.setDate(baseDate.getDate() + i);
# post: 
# post:         // 格式化为 YYYY-MM-DD
# post:         const year = currentDate.getFullYear();
# post:         const month = String(currentDate.getMonth() + 1).padStart(2, '0');
# post:         const day = String(currentDate.getDate()).padStart(2, '0');
# post:         const expectedCurrentDateStr = `${year}-${month}-${day}`;
# post: 
# post:         const actualDateStr = item.validDateTimeStartDisplay.split(" ")[0];
# post:         pm.expect(actualDateStr, `第 ${i + 1} 天的日期不连续`).to.eql(expectedCurrentDateStr);
# post:     });
# post: 
# post:     console.log(`ticketRedemptions 校验成功！共生成 ${redemptions.length} 天兑换卡片，有效区间为 ${actualFirstDate} 至 ${actualLastDate}`);
# post: });




import datetime
import json
import pytest

from core.assertions import expect

def test_linda_t4543_verify_the_settings_enable_multi_day_pass_work(ctx):
    """Apifox case #7802190: Linda_T4543_Verify_the_settings_Enable_multi_day_pass_work"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: dece4880-ddc9-4ca0-8561-c369469fb798
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{UIauto_partner_email}}",\r\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\r\n\r\n}', app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    ctx.extract('yuxiao999_token', _resp1, '$.data.token')
    # step 2: d5306c79-bc8c-4be8-bcec-9b3d520ced47
    _resp2 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    # extract event by title "event-for-API-testing" (mirrors Apifox customScript)
    try:
        _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
        _items2 = (_j2.get('data') or {}).get('items') or []
        _ev = next((it for it in _items2 if it.get('title') == 'event-for-API-testing'), None)
        assert _ev, "event 'event-for-API-testing' not found in /product-event/list"
        vars['event_id'] = _ev['id']
        vars['startDateDisplay'] = _ev.get('startDateDisplay')
        vars['endDateDisplay'] = _ev.get('endDateDisplay')
        # compute multipleDaysPass_days (mirrors Apifox step-5 pre-script)
        _sd = [int(x) for x in str(vars['startDateDisplay']).split('-')]
        _ed = [int(x) for x in str(vars['endDateDisplay']).split('-')]
        _start = datetime.date(_sd[0], _sd[1], _sd[2])
        _end = datetime.date(_ed[0], _ed[1], _ed[2])
        _days = []
        for _i in range(8):
            _cur = _start + datetime.timedelta(days=_i)
            _fd = _cur.strftime('%Y-%m-%d')
            _days.append({"date": _fd, "enabled": _start <= _cur <= _end,
                          "checkInStart": f"{_fd} 00:00:00", "checkInEnd": f"{_fd} 23:59:59"})
        vars['multipleDaysPass_days'] = json.dumps(_days)
    except Exception as e:
        pytest.fail(f"step2 extract event: {e}")
    # step 3: a162f41c-de75-439f-ba5f-5022f8dbb567
    _resp3 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    try:
        _j3 = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
        _items3 = (_j3.get('data') or {}).get('items') or []
        _post = next((it for it in _items3 if it.get('title') == 'event-for-API-testing'), None)
        assert _post, "post 'event-for-API-testing' not found"
        vars['postId'] = _post['id']
    except Exception as e:
        pytest.fail(f"step3 extract post: {e}")
    # step 4: 806f3d0e-23bc-4980-933f-70d2cb989003
    _resp4 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    try:
        _j4 = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
        vars['catalog_id'] = (_j4.get('data') or {}).get('id')
    except Exception:
        pass
    # step 5: 3259d9bd-b11c-4e6c-b6e2-7d46b9409108
    _resp5 = ctx.api.products.create(body='{\n    "merchantId": "{{catalog_id}}",\n    "shippingType": "NO_SHIPPING_REQUIRED",\n    "isFeatured": false,\n    "commissionRate": 0,\n    "priceSyncImported": false,\n    "additionalShippingFee": 0,\n    "returnPolicyApplied": true,\n    "title": "auto testing with turn on multiple day pass",\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n    "status": "ACTIVE",\n    "isUsed": "NWT",\n    "taxJarCategory": "",\n    "platform": "PEAR",\n    "autoFulfill": true,\n    "options": [\n        {\n            "name": "Title",\n            "values": [\n                "Default Title"\n            ],\n            "images": []\n        }\n    ],\n    "variants": [\n        {\n            "inventoryQuantity": 99999,\n            "price": 0,\n            "priceAnchor": 0,\n            "option": {\n                "option1": "Default Title"\n            },\n            "fees": 0,\n            "ticketPrice": 0,\n            "transactionFee": {\n                "platformFee": 0,\n                "customFee": 0,\n                "customFeeBreakdown": {},\n                "transactionItemFee": 0\n            },\n            "minPriceForCheckFees": 0,\n            "weightUnit": "lb",\n            "isInventoryQuantityUnlimited": true\n        }\n    ],\n    "listingType": "TICKET",\n    "ticketType": "TICKET_TYPE_STANDARD",\n    "soldQuantity": 0,\n    "excludeFromPostSync": false,\n    "isTipEnabled": false,\n    "useEventPosterAsCover": true,\n    "catalogCommissionRate": 0,\n    "deliveryMethod": "QR_CODE",\n    "thirdPartyDeliveryMessage": "",\n    "taxEnable": false,\n    "customTaxRate": null,\n    "earliestTime": "2026-08-11T09:47:48.080Z",\n    "styleSettings": {\n        "recentUsedColors": [\n            "#ffffff"\n        ]\n    },\n    "isMultipleDaysPassEnabled": true,\n    "multipleDaysPass": {\n        "days": {{multipleDaysPass_days}}\n    },\n    "isInclusionsEnabled": false,\n    "inclusions": [],\n    "isVariantPriceDisplayEnabled": false,\n    "stopSellingAfterDisplay": "",\n    "extraInfo": {\n        "businessTimezone": "Asia/Shanghai"\n    },\n    "overrideEventTax": false,\n    "overrideEventCustomFee": false,\n    "hideFees": false,\n    "transactionCustomFeeConfig": null,\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n    "images": [\n        {\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n            "width": 3072,\n            "height": 2048,\n            "position": 0,\n            "mediaType": "IMAGE",\n            "mediaDuration": 0\n        }\n    ],\n    "eventId": "{{event_id}}",\n    "isExpirationEnabled": false\n}', token='yuxiao999_token')
    ctx.extract('productId', _resp5, '$.data.id')
    # step 7: 978083e9-c8fa-43a6-98fb-69cdf3d1b8f5
    _resp7 = ctx.api.events.v2_show_in_post(body='{\n    "productIds": [\n        "{{productId}}"\n    ],\n    "posts": [\n        {\n            "postId": "{{postId}}",\n            "isVisible": true\n        }\n    ]\n}', token='yuxiao999_token')
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # step 8: cb7226e4-64d6-4967-8caf-10aacfcfbbaa
    _resp8 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token', path_vars={'post0_id': '{{postId}}'})
    # extract promoterProductId (displayVariantId) by product title (mirrors Apifox customScript)
    try:
        _j8 = _resp8.json() if _resp8.headers.get('content-type','').startswith('application/json') else {}
        _prods = (_j8.get('data') or {}).get('relatedProducts') or []
        _prod = next((it for it in _prods if it.get('title') == 'auto testing with turn on multiple day pass'), None)
        assert _prod, "related product 'auto testing with turn on multiple day pass' not found"
        vars['promoterProductId'] = _prod.get('displayVariantId')
    except Exception as e:
        pytest.fail(f"step8 extract promoterProductId: {e}")
    # step 9: Get consumer linda10 token
    _resp9 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+10@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}', app_headers=True)
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp9, '$.data.token')
    # step 10: 75f96309-d89c-4691-90ca-f0b52e3df23b
    _resp10 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 10.assertion: responseJson equal 200
    expect(_resp10).json('$.code').equals('200')
    # assertion 10.assertion: responseJson equal success
    expect(_resp10).json('$.message').equals('success')
    # step 11: buy now
    _resp11 = ctx.api.orders.buy_now(body='{\n  "postIdForFilter": "{{postId}}",\n  "updateCartItems": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "{{promoterProductId}}",\n      "price": 2,\n      "postId": "{{postId}}",\n      "selected": true,\n      "customFields": []\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "{{event_id}}",\n    "pixelId": [\n      "test"\n    ],\n    "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n    "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n    "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 1,\n      "id": "{{productId}}",\n      "postId": "{{postId}}",\n      "price": 2,\n      "customFields": []\n    }\n  ]\n}', app_headers=True, token='linda10_token')
    # extractor: orderId = $.data.orderId
    ctx.extract('orderId', _resp11, '$.data.orderId')
    # step 12: place order
    _resp12 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "linda.zhou.ext+10@1m.app"\n    },\n    "shippingAddressId": "{{shippingAddressId}}",\n    "fbAdParams": {\n        "eventID": "58e159af-0e82-4244-b86d-00f37277e6a0",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=ff6bbfb6-7146-44d9-985b-26eefbf740e3"\n    }\n}', app_headers=True, token='linda10_token')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp12, 'orderNumber')
    # step 13: Check the merchant order detail exist ticket Redemptions contents
    _resp13 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='yuxiao999_token', path_vars={'merchantId': '{{catalog_id}}'})
