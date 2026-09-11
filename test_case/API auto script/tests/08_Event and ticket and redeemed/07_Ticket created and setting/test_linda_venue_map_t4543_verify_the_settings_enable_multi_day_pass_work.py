"""Migrated from Apifox case #8660683. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8660683  (traceability only — not needed to run)
NAME = "(Linda)(Venue map)T4543 Verify the settings Enable multi-day pass work"
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:linda"]
PRIORITY = 0


CASE_ID = 8660683
ENV_NAME = "Release"

# --- step 1: 91c574f3-fdab-47be-bf60-472750a263b8 ---
# post[extractor]: {"variableName": "yuxiao999_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: e9985ede-c59f-4723-bad2-ed9a86c642f2 ---
# pre: pm.environment.set("event_title", "event-for-api-auto-venue-map");
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 指定目标 Event 的 title（可以从环境变量拿，也可以在此指定）
# post: const targetEventTitle = pm.environment.get("event_title") || "Auto-Test-post-setting";
# post: 
# post: // 3. 查找匹配的 Event 对象
# post: const targetEvent = responseData.data?.items?.find(
# post:     item => item.title === targetEventTitle
# post: );
# post: 
# post: // 4. 断言并提取 event_id
# post: pm.test(`找到 title 为 [${targetEventTitle}] 的事件并提取 event_id`, function () {
# post:     pm.expect(targetEvent, `列表中未找到 title 为 [${targetEventTitle}] 的事件`).to.be.an('object');
# post:     pm.expect(targetEvent.id, "提取的 event_id 格式不正确").to.be.a('string').and.not.empty;
# post: 
# post:     const eventId = targetEvent.id;
# post:     pm.environment.set("event_id", eventId);
# post:     console.log(`已成功提取 event_id [${eventId}]（对应标题: ${targetEventTitle}）`);
# post: });
# post: 
# post: // 5. 从该 Event 内部提取指定 Ticket 的 ID 并设置为 copyFromId
# post: pm.test("从匹配的事件中动态提取 copyFromId", function () {
# post:     // 确保 Event 存在且 tickets 数组不为空
# post:     pm.expect(targetEvent?.tickets, "目标事件下未查找到任何 tickets").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 方案 A：如果要找特定 Ticket 标题（例如 "General Admission 01"）
# post:     const targetTicketTitle = "General Admission 01"; 
# post:     let matchedTicket = targetEvent.tickets.find(t => t.title === targetTicketTitle);
# post: 
# post:     // 方案 B（备用）：如果找不到指定标题，默认取该事件下的第 1 个 Ticket
# post:     if (!matchedTicket) {
# post:         matchedTicket = targetEvent.tickets[0];
# post:     }
# post: 
# post:     // 校验 Ticket 及 ID
# post:     pm.expect(matchedTicket, "未提取到有效的 Ticket 对象").to.be.an('object');
# post:     pm.expect(matchedTicket.id, "提取的 ticket id 格式不正确").to.be.a('string').and.not.empty;
# post: 
# post:     // 设置环境变量
# post:     const copyFromId = matchedTicket.id;
# post:     pm.environment.set("copyFromId", copyFromId);
# post: 
# post:     console.log(`已成功提取 copyFromId [${copyFromId}]（对应 Ticket 标题: ${matchedTicket.title}）`);
# post: });
# --- step 3: 4760ca1d-561e-48c2-94ce-e17af75a0809 ---
# post[customScript]: // 1. 解析响应体为 JSON 对象
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 从 data.items 数组中提取第一个元素的 id
# post: // 使用可选链 (?.) 确保在数据结构异常时不会报错
# post: const postId = responseData.data?.items[0]?.id;
# post: 
# post: // 3. 校验提取到的 ID 是否存在
# post: if (postId) {
# post:     // 4. 将提取到的 ID 设置为环境变量 post0_id
# post:     pm.environment.set("post0_id", postId);
# post:     
# post:     // 打印日志方便调试
# post:     console.log("成功提取 post0_id:", postId);
# post: } else {
# post:     console.error("未能从响应中提取到 items[0].id");
# post: }
# post: 
# post: // 5. (可选) 添加一个简单的断言校验
# post: pm.test("成功提取并设置环境变量 post0_id", function () {
# post:     pm.expect(postId).to.be.a('string').and.not.empty;
# post: });
# --- step 4: 3e0bddb6-1e9e-49f5-9fba-2847e4d6c290 ---
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
# --- step 5: 2a013c4d-46d5-4977-a422-b98dad043210 ---
# post[customScript]: // 1. 解析响应数据
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 状态码与数据合法性校验
# post: pm.test("响应状态为 200 且包含 relatedProducts", function () {
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.data?.relatedProducts).to.be.an('array');
# post: });
# post: 
# post: // 3. 循环提取所有产品的目标 ID
# post: const products = responseData.data?.relatedProducts || [];
# post: 
# post: products.forEach((product, index) => {
# post:     pm.test(`提取产品 [${product.title || index}] 的 ID 环境变量`, function () {
# post:         // 格式化标题作为变量后缀：替换空格为下划线，如 "General_Admission_02"
# post:         const formattedTitle = product.title 
# post:             ? product.title.trim().replace(/\s+/g, '_') 
# post:             : `index_${index}`;
# post: 
# post:         // 1. 提取 productId (优先取 merchantProductId，无则取 shippingView.productId)
# post:         const productId = product.merchantProductId || product.shippingView?.productId;
# post:         pm.expect(productId, "productId 不存在").to.be.a('string').and.not.empty;
# post:         const productIdVar = `productId_${formattedTitle}`;
# post:         pm.environment.set(productIdVar, productId);
# post: 
# post:         // 2. 提取 promoterProductId
# post:         const promoterProductId = product.promoterProductId;
# post:         pm.expect(promoterProductId, "promoterProductId 不存在").to.be.a('string').and.not.empty;
# post:         const promoterProductIdVar = `promoterProductId_${formattedTitle}`;
# post:         pm.environment.set(promoterProductIdVar, promoterProductId);
# post: 
# post:         // 3. 提取 merchantProductVariantId (取 variants 数组第一项中的变体 ID)
# post:         const merchantProductVariantId = product.variants?.[0]?.merchantProductVariantId;
# post:         pm.expect(merchantProductVariantId, "merchantProductVariantId 不存在").to.be.a('string').and.not.empty;
# post:         const variantIdVar = `merchantProductVariantId_${formattedTitle}`;
# post:         pm.environment.set(variantIdVar, merchantProductVariantId);
# post: 
# post:         // 4. 补充：提取 displayVariantId (优先取 variants[0] 中的，无则取 product 层级)
# post:         const displayVariantId = product.variants?.[0]?.displayVariantId || product.displayVariantId;
# post:         pm.expect(displayVariantId, "displayVariantId 不存在").to.be.a('string').and.not.empty;
# post:         const displayVariantIdVar = `displayVariantId_${formattedTitle}`;
# post:         pm.environment.set(displayVariantIdVar, displayVariantId);
# post: 
# post:         console.log(`[提取成功] ${formattedTitle}:`);
# post:         console.log(`  - ${productIdVar}: ${productId}`);
# post:         console.log(`  - ${promoterProductIdVar}: ${promoterProductId}`);
# post:         console.log(`  - ${variantIdVar}: ${merchantProductVariantId}`);
# post:         console.log(`  - ${displayVariantIdVar}: ${displayVariantId}`);
# post:     });
# post: });
# --- step 6: 3e9b843d-988b-42d1-8b61-a2b00674881f ---
# post[customScript]: // 1. 解析响应数据
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 筛选出 orderNumber 为 null 的所有项
# post: const items = responseData.data?.items || [];
# post: const nullOrderItems = items.filter(item => item.orderNumber === null);
# post: 
# post: // 3. 断言并随机提取 unitid、seatNumber 以及 venueUnitCategoryId
# post: pm.test("随机提取 orderNumber 为 null 的 item 字段并设置环境变量", function () {
# post:     // 校验是否有满足条件的项
# post:     pm.expect(nullOrderItems, "未找到 orderNumber 为 null 的数据项").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 随机生成索引
# post:     const randomIndex = Math.floor(Math.random() * nullOrderItems.length);
# post:     const selectedItem = nullOrderItems[randomIndex];
# post: 
# post:     // 校验 id 并设置为 unitid 环境变量
# post:     pm.expect(selectedItem.id, "提取的 id 格式不正确或为空").to.be.a('string').and.not.empty;
# post:     const unitId = selectedItem.id;
# post:     pm.environment.set("unitid", unitId);
# post: 
# post:     // 校验 number 并设置为 seatNumber 环境变量
# post:     pm.expect(selectedItem.number, "提取的 number 不存在或为空").to.exist;
# post:     const seatNumber = String(selectedItem.number);
# post:     pm.environment.set("seatNumber", seatNumber);
# post: 
# post:     // 校验 categoryId 并设置为 venueUnitCategoryId 环境变量
# post:     pm.expect(selectedItem.categoryId, "提取的 categoryId 格式不正确或为空").to.be.a('string').and.not.empty;
# post:     const venueUnitCategoryId = selectedItem.categoryId;
# post:     pm.environment.set("venueUnitCategoryId", venueUnitCategoryId);
# post: 
# post:     console.log(`[提取成功] 从 ${nullOrderItems.length} 个符合条件的项中随机选中 index ${randomIndex}:`);
# post:     console.log(`  - unitid: ${unitId}`);
# post:     console.log(`  - seatNumber: ${seatNumber}`);
# post:     console.log(`  - venueUnitCategoryId: ${venueUnitCategoryId}`);
# post: });
# --- step 7: 22636666-ccc5-49cb-b69a-99c8d7968a4f ---
# pre: // 1. 获取当前时间作为开始时间
# pre: const startDate = new Date();
# pre: 
# pre: // 2. 格式化 startDateDisplay (YYYY-MM-DD)
# pre: const startYear = startDate.getFullYear();
# pre: const startMonth = String(startDate.getMonth() + 1).padStart(2, '0');
# pre: const startDay = String(startDate.getDate()).padStart(2, '0');
# pre: const startDateDisplay = `${startYear}-${startMonth}-${startDay}`;
# pre: 
# pre: // 3. 计算 3 天后的结束时间（共 4 天生效区间）
# pre: const endDate = new Date(startDate);
# pre: endDate.setDate(startDate.getDate() + 3);
# pre: 
# pre: // 4. 格式化 endDateDisplay (YYYY-MM-DD)
# pre: const endYear = endDate.getFullYear();
# pre: const endMonth = String(endDate.getMonth() + 1).padStart(2, '0');
# pre: const endDay = String(endDate.getDate()).padStart(2, '0');
# pre: const endDateDisplay = `${endYear}-${endMonth}-${endDay}`;
# pre: 
# pre: // 5. 动态生成多日票 multipleDaysPass 数组（生成 8 天的数据）
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
# pre: // 6. 写入环境变量
# pre: pm.environment.set("startDateDisplay", startDateDisplay);
# pre: pm.environment.set("endDateDisplay", endDateDisplay);
# pre: pm.environment.set("multipleDaysPass_days", JSON.stringify(dynamicDays));
# pre: 
# pre: // 7. 日志输出验证
# pre: console.log(`[日期范围]: ${startDateDisplay} ~ ${endDateDisplay}`);
# pre: console.log("[动态 Days 数据]:", dynamicDays);
# --- step 9: Get consumer linda10 token ---
# post[extractor]: {"variableName": "linda10_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: aaf8fee2-2d4c-4302-aaae-c1d41577fb10 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: bf3716bc-8788-4f3f-a07e-d88ba2c334a8 ---
# post[extractor]: {"variableName": "orderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 12: place order ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础状态码断言（已将 status 201 修正为匹配 200）
# post: pm.test("响应状态码为 200 且 message 为 success", function () {
# post:     pm.expect(responseData.message).to.eql("success");
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
# post:     // 从环境变量中获取预期的日期字符串
# post:     const expectedStartDate = pm.environment.get("startDateDisplay");
# post:     const expectedEndDate = pm.environment.get("endDateDisplay");
# post:     const orderNumbers = responseData.data?.orderNumbers;
# post:     
# post:     // 校验 orderNumbers 数组存在且不为空
# post:     pm.expect(orderNumbers, "orderNumbers 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post:     pm.expect(orderNumbers[0], "orderNumbers[0] 值为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 定位 lineItems[0]
# post:     const lineItem = responseData.data?.confirmation?.lineItems?.[0];
# post:     pm.expect(lineItem, "lineItems[0] 不存在").to.be.an('object');
# post: 
# post:     // 1) 断言多天票开关开启
# post:     pm.expect(lineItem.isMultipleDaysPassEnabled, "isMultipleDaysPassEnabled 不为 true").to.be.true;
# post: 
# post:     // 2) 断言 multipleDaysPass 对象结构
# post:     const pass = lineItem.multipleDaysPass;
# post:     pm.expect(pass, "multipleDaysPass 对象不存在").to.be.an('object');
# post: 
# post:     // 日期范围字段（结构未变，保持原断言）
# post:     pm.expect(pass.startDate, "startDate 格式不正确").to.be.a('string').and.not.empty;
# post:     pm.expect(pass.endDate, "endDate 格式不正确").to.be.a('string').and.not.empty;
# post: 
# post:     // ===== 新结构：校验 days 数组（替代原 duration / checkInOpens）=====
# post:     pm.expect(pass.days, "days 数组不存在或为空").to.be.an('array').that.is.not.empty;
# post: 
# post:     // 校验每一天的结构完整性
# post:     pass.days.forEach(function (day, index) {
# post:         pm.expect(day.date, "days[" + index + "].date 不存在或为空").to.be.a('string').and.not.empty;
# post:         pm.expect(day.enabled, "days[" + index + "].enabled 必须为布尔值").to.be.a('boolean');
# post:         pm.expect(day.checkInStart, "days[" + index + "].checkInStart 不存在或为空").to.be.a('string').and.not.empty;
# post:         pm.expect(day.checkInEnd, "days[" + index + "].checkInEnd 不存在或为空").to.be.a('string').and.not.empty;
# post:     });
# post: 
# post:     // 至少有一天 enabled（有效天数 > 0）
# post:     const enabledDays = pass.days.filter(function (day) { return day.enabled === true; });
# post:     pm.expect(enabledDays.length > 0, "days 中没有 enabled=true 的有效日期").to.be.true;
# post: 
# post:     // 3) 与环境变量进行校验（如果存在环境变量则进行比对）
# post:     if (expectedStartDate) {
# post:         pm.expect(pass.startDateDisplay, "startDateDisplay 与环境变量不匹配").to.eql(expectedStartDate);
# post:     }
# post:     if (expectedEndDate) {
# post:         pm.expect(pass.endDateDisplay, "endDateDisplay 与环境变量不匹配").to.eql(expectedEndDate);
# post:     }
# post: 
# post:     console.log("multipleDaysPass 匹配成功！有效天数:", enabledDays.length, "实际值:", JSON.stringify(pass));
# post: });
# post: 
# --- step 13: Check the merchant order detail exist ticket Redemptions contents ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础状态码断言
# post: pm.test("响应状态码为 200 且 message 为 success", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post: });
# post: 
# post: // 3. 断言 isMultipleDaysPassEnabled 及 ticketRedemptions 与环境变量的逻辑对应关系
# post: pm.test("断言 ticketRedemptions 的日期区间及连续性匹配环境变量", function () {
# post:     // 从环境变量中获取预期的开始和结束日期 (格式如 "2026-08-12")
# post:     const expectedStartDate = pm.environment.get("startDateDisplay");
# post:     const expectedEndDate = pm.environment.get("endDateDisplay");
# post: 
# post:     // 定位 lineItems[0]
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
# post:     // 3) 基础属性完整性校验
# post:     redemptions.forEach((item, index) => {
# post:         pm.expect(item.id, `第 ${index} 项缺少 id`).to.be.a('string').and.not.empty;
# post:         pm.expect(item.status, `第 ${index} 项 status 不正确`).to.eql("IN_PROCESSING");
# post:         pm.expect(item.validDateTimeStartDisplay, `第 ${index} 项缺少 validDateTimeStartDisplay`).to.be.a('string').and.not.empty;
# post:     });
# post: 
# post:     // 4) 关联环境变量做逻辑性断言
# post:     if (expectedStartDate && expectedEndDate) {
# post:         // 提取第一天和最后一天的日期字符串 (例如从 "2026-08-12 00:00:00" 截取 "2026-08-12")
# post:         const actualFirstDate = redemptions[0].validDateTimeStartDisplay.split(" ")[0];
# post:         const actualLastDate = redemptions[redemptions.length - 1].validDateTimeStartDisplay.split(" ")[0];
# post: 
# post:         // A. 校验首尾日期匹配
# post:         pm.expect(actualFirstDate, "首项日期与 startDateDisplay 不符").to.eql(expectedStartDate);
# post:         pm.expect(actualLastDate, "末项日期与 endDateDisplay 不符").to.eql(expectedEndDate);
# post: 
# post:         // B. 计算预期天数 (包含首尾两天的天数)
# post:         const startTimestamp = new Date(expectedStartDate).getTime();
# post:         const endTimestamp = new Date(expectedEndDate).getTime();
# post:         const expectedDaysCount = Math.round((endTimestamp - startTimestamp) / (1000 * 60 * 60 * 24)) + 1;
# post: 
# post:         // C. 校验数组长度等于预期天数
# post:         pm.expect(redemptions.length, "ticketRedemptions 天数与预期的首尾间隔天数不一致").to.eql(expectedDaysCount);
# post: 
# post:         // D. 校验日期的连续性
# post:         for (let i = 0; i < redemptions.length; i++) {
# post:             const currentDate = new Date(expectedStartDate);
# post:             currentDate.setDate(currentDate.getDate() + i);
# post: 
# post:             // 格式化为 YYYY-MM-DD
# post:             const year = currentDate.getFullYear();
# post:             const month = String(currentDate.getMonth() + 1).padStart(2, '0');
# post:             const day = String(currentDate.getDate()).padStart(2, '0');
# post:             const expectedCurrentDateStr = `${year}-${month}-${day}`;
# post: 
# post:             const actualDateStr = redemptions[i].validDateTimeStartDisplay.split(" ")[0];
# post:             pm.expect(actualDateStr, `第 ${i + 1} 天的日期不连续或与预期不符`).to.eql(expectedCurrentDateStr);
# post:         }
# post: 
# post:         console.log(`ticketRedemptions 日期逻辑校验成功！共 ${redemptions.length} 天，区间为 ${actualFirstDate} 至 ${actualLastDate}`);
# post:     } else {
# post:         console.warn("未设置 startDateDisplay 或 endDateDisplay 环境变量，跳过逻辑区间断言");
# post:     }
# post: });




# NOTE: 迁移脚本此处原本生成过一个本地 `_get_path`（实现正确，用 `path.split('.')`），
# 但紧随其后的 `from core.compat import get_path as _get_path` 把它整体**遮蔽**，
# 实际生效的是当时仍「逐字符迭代字符串」的 core.compat 版本 —— 这正是本用例
# `data.token` / `data.orderId` / `code` / `message` 提取**恒为 None** 的直接原因。
# 现统一以 core.compat 为唯一实现（已修正字符串路径语义），删除本地重复定义。

def _json(resp):
    return resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}

import datetime
import json

from core.assertions import expect

from core.compat import get_path as _get_path
from core.compat import legacy_render

def test_linda_venue_map_t4543_verify_the_settings_enable_multi_day_pass_work(ctx):
    """Apifox case #8660683 — ported from the pre/post/extractor/assertion scripts
preserved as comments above. Variables resolve from env/Global.yaml + env/Release.yaml
+ the co-located <slug>.vars.yaml via the shared _ctx fixture (no live Apifox fetch)."""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    _render = legacy_render(ctx)
    """Apifox case #8660683 — ported from the pre/post/extractor/assertion scripts
    preserved as comments above. Variables resolve from env/Global.yaml + env/Release.yaml
    + the co-located <slug>.vars.yaml via the shared _ctx fixture (no live Apifox fetch)."""
    # case-specific test data (externalized in <slug>.vars.yaml)
    vars.setdefault('event_title', 'event-for-api-auto-venue-map')
    vars.setdefault('target_ticket_title', 'General Admission 01')
    # step 1: 91c574f3-fdab-47be-bf60-472750a263b8  (POST /auth/sign-in)
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{UIauto_partner_email}}",\r\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\r\n\r\n}', app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    vars['yuxiao999_token'] = _get_path(_json(_resp1), ['data', 'token'])
    # step 2: e9985ede-c59f-4723-bad2-ed9a86c642f2  (GET /product-event/list)
    _resp2 = ctx.api.events.list(params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    _j2 = _json(_resp2)
    _items2 = (_j2.get('data') or {}).get('items') or []
    _evt = next((it for it in _items2 if it.get('title') == vars['event_title']), None)
    assert _evt is not None, f"列表中未找到 title 为 [{vars['event_title']}] 的事件"
    assert isinstance(_evt.get('id'), str) and _evt['id'], "提取的 event_id 格式不正确"
    vars['event_id'] = _evt['id']
    _tickets = _evt.get('tickets') or []
    _matched = next((t for t in _tickets if t.get('title') == vars['target_ticket_title']), None) or (_tickets[0] if _tickets else None)
    assert _matched is not None, "目标事件下未查找到任何 tickets / 未匹配到 Ticket"
    assert isinstance(_matched.get('id'), str) and _matched['id'], "提取的 ticket id 格式不正确"
    vars['copyFromId'] = _matched['id']
    # step 3: 4760ca1d-561e-48c2-94ce-e17af75a0809  (GET /posts/curator/event/{{event_id}}/posts)
    _resp3 = ctx.api.posts.curator_event_posts(token='yuxiao999_token')
    _j3 = _json(_resp3)
    _items3 = (_j3.get('data') or {}).get('items') or []
    assert _items3, "posts 列表为空，无法提取 post0_id"
    _post0 = _items3[0].get('id')
    assert isinstance(_post0, str) and _post0, "提取的 post0_id 格式不正确"
    vars['post0_id'] = _post0
    # step 4: 3e0bddb6-1e9e-49f5-9fba-2847e4d6c290  (GET /product-event/default-catalog)
    _resp4 = ctx.api.events.default_catalog(token='yuxiao999_token')
    _j4 = _json(_resp4)
    _data4 = _j4.get('data')
    assert isinstance(_data4, dict) and isinstance(_data4.get('id'), str) and _data4.get('id'), "data.id 为空或不存在"
    vars['catalog_id'] = _data4['id']
    # step 5: 2a013c4d-46d5-4977-a422-b98dad043210  (GET {{adminurl}}/post/v2/{{post0_id}}/relate-products)
    _resp5 = ctx.api.admin.post_v2_relate_products(token='admin_token')
    _j5 = _json(_resp5)
    _products = (_j5.get('data') or {}).get('relatedProducts') or []
    for _p in _products:
        _title = _p.get('title') or ''
        _fmt = _title.strip().replace(' ', '_') or f'index_{_products.index(_p)}'
        _pid = _p.get('merchantProductId') or (_p.get('shippingView') or {}).get('productId')
        _promo = _p.get('promoterProductId')
        _variants = _p.get('variants') or [{}]
        _mvid = _variants[0].get('merchantProductVariantId')
        _dvid = _variants[0].get('displayVariantId') or _p.get('displayVariantId')
        assert isinstance(_pid, str) and _pid, "productId 不存在"
        assert isinstance(_promo, str) and _promo, "promoterProductId 不存在"
        assert isinstance(_mvid, str) and _mvid, "merchantProductVariantId 不存在"
        assert isinstance(_dvid, str) and _dvid, "displayVariantId 不存在"
        vars[f'productId_{_fmt}'] = _pid
        vars[f'promoterProductId_{_fmt}'] = _promo
        vars[f'merchantProductVariantId_{_fmt}'] = _mvid
        vars[f'displayVariantId_{_fmt}'] = _dvid
    # step 6: 3e9b843d-988b-42d1-8b61-a2b00674881f  (GET /product-event/tickets/{{productId_General_Admission_01}}/venue-units)
    _resp6 = ctx.api.events.tickets_venue_units(params={'pageNumber': '1', 'pageSize': '30', 'variantId': '{{merchantProductVariantId_General_Admission_01}}'}, token='yuxiao999_token', path_vars={'productId_General_Admission_02': '{{productId_General_Admission_01}}'})
    _j6 = _json(_resp6)
    _items6 = (_j6.get('data') or {}).get('items') or []
    _null_order = [it for it in _items6 if it.get('orderNumber') is None]
    assert _null_order, "未找到 orderNumber 为 null 的数据项"
    # NOTE: original Apifox used Math.random() to pick; we pick the first match for determinism.
    _sel = _null_order[0]
    assert isinstance(_sel.get('id'), str) and _sel['id'], "提取的 id 格式不正确或为空"
    vars['unitid'] = _sel['id']
    assert _sel.get('number') is not None, "提取的 number 不存在或为空"
    vars['seatNumber'] = str(_sel['number'])
    assert isinstance(_sel.get('categoryId'), str) and _sel['categoryId'], "提取的 categoryId 格式不正确或为空"
    vars['venueUnitCategoryId'] = _sel['categoryId']
    # step 7: 22636666-ccc5-49cb-b69a-99c8d7968a4f  (PUT /v2/products/{{productId_General_Admission_01}})
    # pre-script: compute the multi-day pass window (8 days; enabled for the first 4 days)
    _today = datetime.date.today()
    _end = _today + datetime.timedelta(days=3)
    _start_display = _today.strftime('%Y-%m-%d')
    _end_display = _end.strftime('%Y-%m-%d')
    _dynamic_days = []
    for _i in range(8):
        _d = _today + datetime.timedelta(days=_i)
        _ds = _d.strftime('%Y-%m-%d')
        _dynamic_days.append({
            "date": _ds,
            "enabled": _today <= _d <= _end,
            "checkInStart": f"{_ds} 00:00:00",
            "checkInEnd": f"{_ds} 23:59:59",
        })
    vars['startDateDisplay'] = _start_display
    vars['endDateDisplay'] = _end_display
    vars['multipleDaysPass_days'] = json.dumps(_dynamic_days)
    # render the product body (substitutes {{catalog_id}}/{{productId_...}}/{{multipleDaysPass_days}}), then attach the parsed array
    _body7 = json.loads(_render('{\n    "id": "{{productId_General_Admission_01}}",\n    "remote_id": null,\n    "platform": "PEAR",\n    "createdAt": "2026-08-25T06:03:23.925Z",\n    "updatedAt": "2026-08-25T06:09:57.463Z",\n    "merchantId": "{{catalog_id}}",\n    "title": "General Admission 01",\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n    "originalBodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n    "isBodyHtmlOverridden": false,\n    "bodyText": "\\n",\n    "handle": null,\n    "productType": "",\n    "publishedAt": "2026-08-25T06:03:23.965Z",\n    "publishedScope": "",\n    "status": "ACTIVE",\n    "externalStatus": "ACTIVE",\n    "followExternalStatus": false,\n    "tags": [],\n    "templateSuffix": null,\n    "vendor": "Pear",\n    "syncAt": null,\n    "deletedAt": null,\n    "delisted": false,\n    "excludedByImportingTag": false,\n    "isFeatured": false,\n    "featuredScore": null,\n    "inventoryQuantity": 15,\n    "inventoryQuantityOriginal": 15,\n    "soldQuantity": 0,\n    "priceDisplay": 67.77,\n    "priceDisplayAnchor": 0,\n    "priceMin": 67.77,\n    "priceMinAnchor": 0,\n    "priceMax": 67.77,\n    "priceMaxAnchor": 0,\n    "priceImportedMin": 0,\n    "priceImportedMax": 0,\n    "imageCount": 1,\n    "isUsed": "NWT",\n    "shippingType": "NO_SHIPPING_REQUIRED",\n    "additionalShippingFee": 0,\n    "deliveryTime": [\n        0,\n        5\n    ],\n    "returnPolicyApplied": true,\n    "isAvailable": true,\n    "commissionRate": 7,\n    "textForShare": null,\n    "priceSyncImported": false,\n    "coverImage": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "position": 0,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n    },\n    "useEventPosterAsCover": true,\n    "reviewCount": null,\n    "reviewOverallScore": null,\n    "reviewAggregate": null,\n    "displayReviews": true,\n    "links": null,\n    "taxEnable": false,\n    "taxJarCategory": "",\n    "customTaxRate": null,\n    "subscriptionPlanId": null,\n    "reviewRedirectProductId": null,\n    "reviewSummary": null,\n    "customFieldsInfo": null,\n    "listingType": "TICKET",\n    "ticketType": "TICKET_TYPE_STANDARD",\n    "ticketHubInfo": null,\n    "customizedFields": [],\n    "shippingOptions": [],\n    "shippingNote": null,\n    "autoFulfill": true,\n    "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",\n    "copyFromId": "{{copyFromId}}",\n    "stopSellingAfter": null,\n    "deliveryMethod": "QR_CODE",\n    "thirdPartyDeliveryMessage": "",\n    "isMultipleDaysPassEnabled": true,\n    "isVenueUnitEnabled": true,\n    "venueUnitCategoryId": "{{venueUnitCategoryId}}",\n    "multipleDaysPass": {\n        "days":{{multipleDaysPass_days}}\n    },\n    "isPickupEtaEnabled": null,\n    "eventMatchingRules": null,\n    "expirationTime": null,\n    "allowAtDoorSales": false,\n    "isTipEnabled": false,\n    "isPlatformFeeConfigCustomized": false,\n    "isVariantPlatformFeeConfigCustomized": false,\n    "transactionFeeConfig": {\n        "baseConfig": {\n            "unitFixedFee": 1,\n            "unitPercentageFee": 0.1\n        }\n    },\n    "transactionFeeRebateConfig": {\n        "baseConfig": {\n            "unitFixedFee": 0,\n            "unitPercentageFee": 0\n        }\n    },\n    "transactionCustomFeeConfig": null,\n    "options": [\n        {\n            "remote_id": null,\n            "productId": "{{productId_General_Admission_01}}",\n            "name": "Title",\n            "position": 1,\n            "values": [\n                "Default Title"\n            ],\n            "images": [\n                {\n                    "value": "Default Title",\n                    "imageId": null\n                }\n            ]\n        }\n    ],\n    "variants": [\n        {\n            "id": "{{merchantProductVariantId_General_Admission_01}}",\n            "remote_id": null,\n            "createdAt": "2026-08-25T06:03:24.017Z",\n            "updatedAt": "2026-08-25T06:09:57.779Z",\n            "compareAtPrice": null,\n            "fulfillmentService": "manual",\n            "grams": 0,\n            "imageIds": [],\n            "inventoryItemId": null,\n            "inventoryManagement": "Pear",\n            "inventoryPolicy": "DENY",\n            "isInventoryQuantityUnlimited": false,\n            "inventoryQuantity": 15,\n            "inventoryQuantityOriginal": 15,\n            "soldQuantity": 0,\n            "option": {\n                "option1": "Default Title"\n            },\n            "position": 1,\n            "price": 67.77,\n            "priceAnchor": 0,\n            "priceImported": "0.00",\n            "productId": "{{productId_General_Admission_01}}",\n            "sku": "",\n            "taxCode": null,\n            "taxable": true,\n            "title": "Default Title",\n            "weight": null,\n            "weightUnit": "lb",\n            "platform": null,\n            "fees": 7.77,\n            "transactionFee": {\n                "platformFee": 7.77,\n                "customFee": 0,\n                "customFeeBreakdown": {\n                    "TAX": {\n                        "title": "Taxes",\n                        "unitFixedFee": 0,\n                        "unitPercentageFee": 0,\n                        "index": 0,\n                        "itemFee": 0\n                    }\n                },\n                "transactionItemFee": 7.77\n            },\n            "ticketPrice": 60,\n            "isMinPurchaseQuantityEnabled": false,\n            "minPurchaseQuantity": null,\n            "isMaxPurchaseQuantityEnabled": false,\n            "maxPurchaseQuantity": null,\n            "isPackSizeEnabled": false,\n            "packSize": null,\n            "transactionFeeConfig": null,\n            "transactionFeeRebateConfig": null,\n            "minPriceForCheckFees": 0\n        }\n    ],\n    "readOnlyFields": [],\n    "isInventoryQuantityUnlimited": false,\n    "showInEventPost": true,\n    "visibleInPosts": [\n        {\n            "postId": "{{post0_id}}",\n            "isVisible": true\n        }\n    ],\n    "excludeFromPostSync": false,\n    "catalogCommissionRate": 0,\n    "hasLimitPurchaseQuantity": false,\n    "hasSpecialRedemption": false,\n    "earliestTime": "2026-08-25T04:00:00.000Z",\n    "styleSettings": {\n        "recentUsedColors": [\n            "#ffffff"\n        ]\n    },\n    "isProductFormEnabled": false,\n    "isInclusionsEnabled": false,\n    "inclusions": [],\n    "isVariantPriceDisplayEnabled": false,\n    "stopSellingAfterDisplay": "",\n    "overrideEventTax": false,\n    "overrideEventCustomFee": false,\n    "hideFees": false,\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n    "images": [\n        {\n            "id": "52d5b590-879c-4b67-b466-ff33a41915db",\n            "remote_id": null,\n            "createdAt": "2026-08-25T06:03:24.017Z",\n            "updatedAt": "2026-08-25T06:03:24.017Z",\n            "height": 1000,\n            "width": 1000,\n            "position": 1,\n            "productId": "{{productId_General_Admission_01}}",\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",\n            "variantIds": [],\n            "mediaType": "IMAGE",\n            "mediaSrc": null,\n            "mediaDuration": 0,\n            "contributedBy": 3,\n            "contributorId": null,\n            "productImageType": "PRODUCT",\n            "source": null,\n            "setThumbnail": true\n        }\n    ],\n    "eventId": "{{event_id}}",\n    "isExpirationEnabled": false\n}', vars))
    _body7['isMultipleDaysPassEnabled'] = True
    _body7['multipleDaysPass'] = {"days": json.loads(vars['multipleDaysPass_days'])}
    _resp7 = ctx.api.products.by_product_id_general_admission_02(body=json.dumps(_body7), token='yuxiao999_token', path_vars={'productId_General_Admission_02': '{{productId_General_Admission_01}}'})
    # === 断言（step7 PUT 启用 multi-day pass 的响应校验）===
    _j7 = _json(_resp7)
    assert _resp7.status_code == 200, f"step7 status != 200, got {_resp7.status_code}"
    assert str(_j7.get('code')) == '200', f"step7 code != 200, got {_j7.get('code')}"
    assert str(_j7.get('message')) == 'success', f"step7 message != success, got {_j7.get('message')}"
    _p7 = (_j7.get('data') or {}).get('multipleDaysPass')
    assert isinstance(_p7, dict), "step7 返回中 multipleDaysPass 缺失"
    assert isinstance(_p7.get('days'), list) and _p7.get('days'), "step7 multipleDaysPass.days 缺失或为空"
    assert any(_d.get('enabled') is True for _d in _p7['days']), "step7 multipleDaysPass.days 无 enabled=true 项"
    # step 9: Get consumer linda10 token  (POST /auth/sign-in)
    _resp9 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+10@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}')
    # extractor: linda10_token = $.data.token
    vars['linda10_token'] = _get_path(_json(_resp9), ['data', 'token'])
    # step 10: aaf8fee2-2d4c-4302-aaae-c1d41577fb10  (DELETE /cart)
    _resp10 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertions: $.code == 200 ; $.message == success
    assert str(_get_path(_json(_resp10), ['code'])) == '200', f"step10 code != 200, got {_get_path(_json(_resp10), ['code'])}"
    assert str(_get_path(_json(_resp10), ['message'])) == 'success', "step10 message != success"
    # step 11: bf3716bc-8788-4f3f-a07e-d88ba2c334a8  (POST /order/checkout/express)
    _resp11 = ctx.api.orders.checkout_express(body='{\n  "fbAdParams": {\n    "eventID": "0e23d7da-dab0-4dc8-a27c-96ea822f38ad",\n    "pixelId": [\n      "268933192948110"\n    ],\n    "fbBrowserId": "fb.1.1787626769799.674084567126480531",\n    "externalId": "7d70692d-84f0-4b50-bcda-abc39b7d165a",\n    "eventSourceUrl": "https://release.pear.us/autotestshop/post/event-for-api-auto-venue-map"\n  },\n  "items": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "{{displayVariantId_General_Admission_01}}",\n      "price": 112.22,\n      "postId": "{{post0_id}}",\n      "eventId": "{{event_id}}",\n      "sectionName": "General Admission 01",\n      "seatRow": "",\n      "seatNumber": "{{seatNumber}}",\n      "unitId": "{{unitid}}",\n      "selected": true\n    }\n  ],\n  "subdomainVanityUrl": ""\n}', app_headers=True, token='linda10_token')
    # extractor: orderId = $.data.orderId
    vars['orderId'] = _get_path(_json(_resp11), ['data', 'orderId'])
    # step 12: place order  (POST {{base_app_url}}/order)
    _resp12 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "linda.zhou.ext+10@1m.app"\n    },\n    "shippingAddressId": "{{shippingAddressId}}",\n    "fbAdParams": {\n        "eventID": "58e159af-0e82-4244-b86d-00f37277e6a0",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1745806891240.683423600239274570",\n        "externalId": "9e32874f-1af5-4a26-88ad-a0a5cf1ad10c",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=ff6bbfb6-7146-44d9-985b-26eefbf740e3"\n    }\n}', app_headers=True, token='linda10_token')
    # extractor: orderNumber = data.orderNumbers[0]
    _j12 = _json(_resp12)
    _order_numbers = (_j12.get('data') or {}).get('orderNumbers') or []
    assert _order_numbers, "orderNumbers 数组不存在或为空"
    assert isinstance(_order_numbers[0], str) and _order_numbers[0], "orderNumbers[0] 值为空"
    vars['orderNumber'] = _order_numbers[0]
    # assertions
    assert str(_j12.get('message')) == 'success', f"step12 message != success, got {_j12.get('message')}"
    _li12 = ((_j12.get('data') or {}).get('confirmation') or {}).get('lineItems', [{}])[0]
    assert isinstance(_li12, dict), "lineItems[0] 不存在"
    assert _li12.get('isMultipleDaysPassEnabled') is True, "isMultipleDaysPassEnabled 不为 true"
    _pass = _li12.get('multipleDaysPass')
    assert isinstance(_pass, dict), "multipleDaysPass 对象不存在"
    assert isinstance(_pass.get('startDate'), str) and _pass.get('startDate'), "startDate 格式不正确"
    assert isinstance(_pass.get('endDate'), str) and _pass.get('endDate'), "endDate 格式不正确"
    _days = _pass.get('days')
    assert isinstance(_days, list) and _days, "days 数组不存在或为空"
    for _day in _days:
        assert isinstance(_day.get('date'), str) and _day.get('date'), "days[].date 不存在或为空"
        assert isinstance(_day.get('enabled'), bool), "days[].enabled 必须为布尔值"
        assert isinstance(_day.get('checkInStart'), str) and _day.get('checkInStart'), "days[].checkInStart 不存在或为空"
        assert isinstance(_day.get('checkInEnd'), str) and _day.get('checkInEnd'), "days[].checkInEnd 不存在或为空"
    _enabled_days = [d for d in _days if d.get('enabled') is True]
    assert len(_enabled_days) > 0, "days 中没有 enabled=true 的有效日期"
    if vars.get('startDateDisplay'):
        assert _pass.get('startDateDisplay') == vars['startDateDisplay'], "startDateDisplay 与环境变量不匹配"
    if vars.get('endDateDisplay'):
        assert _pass.get('endDateDisplay') == vars['endDateDisplay'], "endDateDisplay 与环境变量不匹配"
    # step 13: Check merchant order detail ticket Redemptions  (GET /order/merchant/{{catalog_id}}/detail/{{orderNumber}}/v2)
    _resp13 = ctx.api.orders.merchant_detail_v2(token='yuxiao999_token', path_vars={'merchantId': '{{catalog_id}}'})
    _j13 = _json(_resp13)
    assert _resp13.status_code == 200, f"step13 status != 200, got {_resp13.status_code}"
    assert str(_j13.get('code')) == '200', f"step13 code != 200, got {_j13.get('code')}"
    assert str(_j13.get('message')) == 'success', "step13 message != success"
    _li13 = (_j13.get('data') or {}).get('lineItems', [{}])[0]
    assert isinstance(_li13, dict), "lineItems[0] 不存在"
    assert _li13.get('isMultipleDaysPassEnabled') is True, "isMultipleDaysPassEnabled 不为 true"
    _unit = (_li13.get('orderLineItemUnits') or [{}])[0]
    assert isinstance(_unit, dict), "orderLineItemUnits[0] 不存在"
    _redemptions = _unit.get('ticketRedemptions')
    assert isinstance(_redemptions, list) and _redemptions, "ticketRedemptions 数组不存在或为空"
    for _r in _redemptions:
        assert isinstance(_r.get('id'), str) and _r.get('id'), f"第 {_redemptions.index(_r)} 项缺少 id"
        assert _r.get('status') == 'IN_PROCESSING', f"第 {_redemptions.index(_r)} 项 status 不正确"
        assert isinstance(_r.get('validDateTimeStartDisplay'), str) and _r.get('validDateTimeStartDisplay'), f"第 {_redemptions.index(_r)} 项缺少 validDateTimeStartDisplay"
    if vars.get('startDateDisplay') and vars.get('endDateDisplay'):
        _first = _redemptions[0].get('validDateTimeStartDisplay').split(' ')[0]
        _last = _redemptions[-1].get('validDateTimeStartDisplay').split(' ')[0]
        assert _first == vars['startDateDisplay'], "首项日期与 startDateDisplay 不符"
        assert _last == vars['endDateDisplay'], "末项日期与 endDateDisplay 不符"
        _start_ts = datetime.datetime.strptime(vars['startDateDisplay'], '%Y-%m-%d').timestamp()
        _end_ts = datetime.datetime.strptime(vars['endDateDisplay'], '%Y-%m-%d').timestamp()
        _expected_days = int(round((_end_ts - _start_ts) / (24 * 3600))) + 1
        assert len(_redemptions) == _expected_days, "ticketRedemptions 天数与预期首尾间隔天数不一致"
        for _i in range(len(_redemptions)):
            _cur = _today + datetime.timedelta(days=_i)
            _expected_cur = _cur.strftime('%Y-%m-%d')
            _actual_cur = _redemptions[_i].get('validDateTimeStartDisplay').split(' ')[0]
            assert _actual_cur == _expected_cur, f"第 {_i + 1} 天的日期不连续或与预期不符"
