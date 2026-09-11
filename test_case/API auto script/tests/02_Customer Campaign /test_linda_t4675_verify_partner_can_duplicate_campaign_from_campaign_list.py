"""Auto-generated from Apifox case #7631342. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7631342
# Folder: 
# Case: (Linda)T4675 Verify partner can duplicate campaign from campaign list
# Priority: P2
# Created: 2025-12-11T08:23:45.000Z
# Updated: 2026-08-11T03:32:10.000Z


CASE_ID = 7631342
ENV_NAME = "Release"

# --- step 1: 7ae9cb2b-f41b-4cf6-b709-acd79df3c009 ---
# post[customScript]: // ========== 1. 解析接口响应数据 ==========
# post: const responseData = pm.response.json();
# post: // 校验响应结构
# post: if (!responseData || !responseData.data || !Array.isArray(responseData.data.items)) {
# post:     console.error("【错误】接口响应格式异常，未找到任务列表");
# post:     // 异常时置空环境变量
# post:     pm.environment.set("emailCompletedId", "");
# post:     pm.environment.set("smsCompletedId", "");
# post:     return;
# post: }
# post: const taskList = responseData.data.items;
# post: console.log("【初始】任务列表总数:", taskList.length);
# post: 
# post: // ========== 2. 提取第一个ID：匹配 Email 条件 ==========
# post: // 条件：name="automation by linda Email" + channel="EMAIL" + status="COMPLETED"
# post: const emailTask = taskList.find(task => 
# post:     task.name === "automation by linda Email" && 
# post:     task.channel === "EMAIL" && 
# post:     task.status === "COMPLETED"
# post: );
# post: const emailCompletedId = emailTask?.id || "";
# post: if (emailCompletedId) {
# post:     console.log("【提取成功】Email条件匹配的ID:", emailCompletedId);
# post: } else {
# post:     console.warn("【提取失败】未找到符合条件的Email任务（name=automation by linda Email、channel=EMAIL、status=COMPLETED）");
# post: }
# post: 
# post: // ========== 3. 提取第二个ID：灵活匹配 SMS 条件（提取最新更新的任务） ==========
# post: // 条件：name="automation by linda SMS" + channel="SMS" + status="COMPLETED"
# post: // 第一步：筛选所有符合SMS业务条件的任务
# post: const validSmsTasks = taskList.filter(task => 
# post:     task.name === "automation by linda SMS" && 
# post:     task.channel === "SMS" && 
# post:     task.status === "COMPLETED"
# post: );
# post: 
# post: let smsCompletedId = "";
# post: // 第二步：若存在符合条件的任务，按updatedAt倒序排序，取第一个（最新更新）
# post: if (validSmsTasks.length > 0) {
# post:     // 按updatedAt时间戳倒序排序（新的在前）
# post:     const sortedSmsTasks = validSmsTasks.sort((taskA, taskB) => {
# post:         const timeA = new Date(taskA.updatedAt).getTime();
# post:         const timeB = new Date(taskB.updatedAt).getTime();
# post:         return timeB - timeA; // 倒序：时间大的（最新）排在前面
# post:     });
# post:     // 取排序后的第一个任务（最新更新）
# post:     const latestSmsTask = sortedSmsTasks[0];
# post:     smsCompletedId = latestSmsTask.id;
# post:     console.log("【提取成功】最新更新的SMS任务信息：", {
# post:         id: smsCompletedId,
# post:         name: latestSmsTask.name,
# post:         channel: latestSmsTask.channel,
# post:         status: latestSmsTask.status,
# post:         updatedAt: latestSmsTask.updatedAt
# post:     });
# post: } else {
# post:     console.warn("【提取失败】未找到符合条件的SMS任务（name=automation by linda SMS、channel=SMS、status=COMPLETED）");
# post: }
# post: 
# post: // ========== 4. 存储到环境变量（供下一个接口使用） ==========
# post: pm.environment.set("emailCompletedId", emailCompletedId);
# post: pm.environment.set("smsCompletedId", smsCompletedId);
# post: 
# post: // ========== 5. 输出提取结果总结 ==========
# post: console.log(`
# post: ===== ID提取结果总结 =====
# post: Email条件匹配ID（emailCompletedId）：${emailCompletedId || "无"}
# post: 最新更新SMS任务ID（smsCompletedId）：${smsCompletedId || "无"}
# post: `);
# --- step 2: 1f2f2d03-7a5d-4928-ae48-d2e46c39c3a0 ---
# post[customScript]: // ========== 1. 初始化校验状态 ==========
# post: let verifyPass = true; // 整体校验是否通过
# post: const verifyLogs = []; // 校验日志
# post: 
# post: // ========== 2. 解析接口响应数据 ==========
# post: const responseData = pm.response.json();
# post: console.log("【原始响应】邮件营销活动接口返回数据:", JSON.stringify(responseData, null, 2));
# post: 
# post: // ========== 3. 校验接口连通性（核心：code/message） ==========
# post: // 校验1：响应code为200（接口通的核心标志）
# post: if (responseData.code !== 200) {
# post:     verifyPass = false;
# post:     verifyLogs.push(`接口连通性失败：响应码期望200，实际${responseData.code}`);
# post: } else {
# post:     verifyLogs.push("✅ 接口连通性成功：响应码=200");
# post: }
# post: 
# post: // 校验2：响应message为success（接口业务层面通的标志）
# post: if (responseData.message !== "success") {
# post:     verifyPass = false;
# post:     verifyLogs.push(`接口连通性失败：响应message期望success，实际${responseData.message}`);
# post: } else {
# post:     verifyLogs.push("✅ 接口连通性成功：message=success");
# post: }
# post: 
# post: // ========== 4. 校验ID是否正确返回并提取 ==========
# post: let newEmailCampaignId = "";
# post: // 校验data字段存在
# post: if (!responseData.data) {
# post:     verifyPass = false;
# post:     verifyLogs.push("❌ ID校验失败：响应缺少data字段");
# post: } else {
# post:     // 校验data.id存在且非空（UUID格式兜底校验，可选）
# post:     newEmailCampaignId = responseData.data.id || "";
# post:     if (newEmailCampaignId && newEmailCampaignId.includes("-")) { // 简单校验UUID格式
# post:         verifyLogs.push(`✅ ID校验成功：提取到邮件营销活动ID = ${newEmailCampaignId}`);
# post:     } else {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ ID校验失败：data.id为空或非有效UUID格式，值=${newEmailCampaignId}`);
# post:         newEmailCampaignId = ""; // 置空无效ID
# post:     }
# post: }
# post: 
# post: // ========== 5. 存储ID到环境变量（核心优化：变量名改为newEmailCampaignId） ==========
# post: pm.environment.set("newEmailCampaignId", newEmailCampaignId);
# post: verifyLogs.push(`📌 环境变量设置完成：newEmailCampaignId = ${pm.environment.get("newEmailCampaignId")}`);
# post: 
# post: // ========== 6. 输出结构化校验总结（易读性优化） ==========
# post: console.log(`
# post: ==================== 校验 & 提取总结 ====================
# post: 整体结果：${verifyPass ? "✅ 全部通过" : "❌ 存在失败项"}
# post: -----------------------------------------------------
# post: ${verifyLogs.join("\n")}
# post: =====================================================
# post: `);
# post: 
# post: // 失败时高亮提醒（便于快速定位问题）
# post: if (!verifyPass) {
# post:     console.error("【关键警告】接口校验或ID提取失败，环境变量已置空！");
# post: }
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "DRAFT", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "NOT_STARTED", "path": "$.data.sentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.sentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 517f54f9-ea14-4a2e-b1b7-00e61a200064 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "DRAFT", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNPAID", "path": "$.data.paymentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.paymentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 489b71c1-7235-454f-89ac-257c3e20bf91 ---
# post[customScript]: // 1. 将响应体解析为 JSON 对象
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应状态断言
# post: pm.test("HTTP 状态码应该为 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: pm.test("业务层 code 和 message 应该正确", function () {
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post:     pm.expect(responseData.request_id).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 3. 核心业务字段断言 (固定配置和状态)
# post: pm.test("断言活动基础配置与状态", function () {
# post:     const data = responseData.data;
# post:     
# post:     pm.expect(data.name).to.eql("automation by linda Email");
# post:     pm.expect(data.channel).to.eql("EMAIL");
# post:     pm.expect(data.status).to.eql("DRAFT");
# post:     pm.expect(data.paymentStatus).to.eql("UNPAID");
# post:     pm.expect(data.sentStatus).to.eql("NOT_STARTED");
# post:     pm.expect(data.smsEncoding).to.null;
# post: });
# post: 
# post: // 4. 数据统计与计费逻辑断言（校验数值和计算公式）
# post: pm.test("断言短信条数与费用计算逻辑", function () {
# post:     const data = responseData.data;
# post:     
# post:     // 短信计费计数校验
# post:     pm.expect(data.totalSelectedCount).to.eql(0);
# post:     pm.expect(data.segmentsPerMessage).to.eql(1);
# post:     pm.expect(data.totalSegments).to.eql(0);
# post:     
# post:     // 费用校验
# post:     pm.expect(data.unitPrice).to.eql(0.001);
# post:     pm.expect(data.fixedFee).to.eql(1);
# post:     pm.expect(data.usageFee).to.eql(0);
# post:     pm.expect(data.totalToPay).to.eql(1);
# post:     
# post:     // 动态计算逻辑断言：应付金额 = 固定费 + 使用费
# post:     pm.expect(data.totalToPay).to.eql(data.fixedFee + data.usageFee);
# post:     pm.expect(data.paymentBreakdown.PAYOUT).to.eql(data.totalToPay);
# post: });
# post: 
# post: // 5. 动态数据【规避策略】：只校验类型、非空和格式，不校验具体值
# post: pm.test("校验动态生成的 ID 和时间戳格式（不校验具体值）", function () {
# post:     const data = responseData.data;
# post:     
# post:     // 1. 校验 ID 是否为非空字符串 (只要有值、是字符串就通过)
# post:     pm.expect(data.id).to.be.a('string').and.not.empty;
# post:     pm.expect(data.userId).to.be.a('string').and.not.empty;
# post:     
# post:     // 2. 使用正则表达式校验时间戳是否符合 ISO 8601 格式 (例如: 2026-06-10T03:30:52.011Z)
# post:     // 这样无论日期变成哪一天，只要格式对，断言就不会失败
# post:     const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
# post:     
# post:     pm.expect(data.createdAt).to.match(isoDateRegex);
# post:     pm.expect(data.updatedAt).to.match(isoDateRegex);
# post: });
# --- step 5: 199018d2-d106-427d-844b-1e955ec5da56 ---
# post[customScript]: // ========== 1. 初始化校验状态（语义贴合SMS场景） ==========
# post: let verifyPass = true; // 整体校验是否通过
# post: const verifyLogs = []; // 结构化校验日志
# post: 
# post: // ========== 2. 解析接口响应数据（打印格式化原始数据，便于调试） ==========
# post: const responseData = pm.response.json();
# post: console.log("【原始响应】SMS营销活动接口返回数据:\n", JSON.stringify(responseData, null, 2));
# post: 
# post: // ========== 3. 核心校验1：接口连通性（基础可用性） ==========
# post: // 校验响应码（接口通的核心标志）
# post: if (responseData.code !== 200) {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ 接口连通性失败：响应码期望200，实际${responseData.code}`);
# post: } else {
# post:     verifyLogs.push(`✅ 接口连通性成功：响应码=200`);
# post: }
# post: 
# post: // 校验业务状态（接口返回逻辑正确）
# post: if (responseData.message !== "success") {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ 接口业务状态失败：message期望success，实际${responseData.message}`);
# post: } else {
# post:     verifyLogs.push(`✅ 接口业务状态成功：message=success`);
# post: }
# post: 
# post: // ========== 4. 核心校验2：提取并校验SMS营销活动ID ==========
# post: let newSMSCampaignId = "";
# post: // 校验data字段存在性
# post: if (!responseData.data) {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ ID提取失败：响应缺少核心data字段`);
# post: } else {
# post:     // 提取ID并校验有效性（UUID格式+非空双重校验）
# post:     newSMSCampaignId = responseData.data.id || "";
# post:     const isUUIDFormat = newSMSCampaignId.includes("-") && newSMSCampaignId.length >= 32; // 简易UUID校验
# post:     if (newSMSCampaignId && isUUIDFormat) {
# post:         verifyLogs.push(`✅ ID提取成功：SMS营销活动ID = ${newSMSCampaignId}`);
# post:     } else {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ ID提取失败：data.id为空或非有效UUID格式（值：${newSMSCampaignId}）`);
# post:         newSMSCampaignId = ""; // 置空无效ID，避免下游接口传错值
# post:     }
# post: }
# post: 
# post: // ========== 5. 存储到环境变量（核心：变量名改为newSMSCampaignId） ==========
# post: pm.environment.set("newSMSCampaignId", newSMSCampaignId);
# post: verifyLogs.push(`📌 环境变量已设置：newSMSCampaignId = ${pm.environment.get("newSMSCampaignId")}`);
# post: 
# post: // ========== 6. 输出可视化校验总结（易读性最大化） ==========
# post: console.log(`
# post: =====================================================
# post:             SMS营销活动ID提取校验总结
# post: =====================================================
# post: 整体校验结果：${verifyPass ? "✅ 全部通过" : "❌ 存在失败项"}
# post: -----------------------------------------------------
# post: ${verifyLogs.join("\n")}
# post: =====================================================
# post: `);
# post: 
# post: // ========== 7. 失败兜底提醒（高亮错误，便于快速定位） ==========
# post: if (!verifyPass) {
# post:     console.error("【关键警告】SMS营销活动ID提取失败！环境变量已置空，请检查接口返回格式/数据有效性！");
# post: }
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "DRAFT", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "NOT_STARTED", "path": "$.data.sentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.sentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: 0a76cd94-607d-4f1f-92af-238924d2f660 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "DRAFT", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNPAID", "path": "$.data.paymentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.paymentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: bfe008d5-9baa-48c3-ab74-bb1be46524e7 ---
# post[customScript]: // 1. 将响应体解析为 JSON 对象
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础响应状态断言
# post: pm.test("HTTP 状态码应该为 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: pm.test("业务层 code 和 message 应该正确", function () {
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post:     pm.expect(responseData.request_id).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 3. 核心业务字段断言 (固定配置和状态)
# post: pm.test("断言活动基础配置与状态", function () {
# post:     const data = responseData.data;
# post:     
# post:     pm.expect(data.name).to.eql("automation by linda SMS");
# post:     pm.expect(data.channel).to.eql("SMS");
# post:     pm.expect(data.status).to.eql("DRAFT");
# post:     pm.expect(data.paymentStatus).to.eql("UNPAID");
# post:     pm.expect(data.sentStatus).to.eql("NOT_STARTED");
# post:     pm.expect(data.smsEncoding).to.eql("GSM_7");
# post: });
# post: 
# post: // 4. 数据统计与计费逻辑断言（校验数值和计算公式）
# post: pm.test("断言短信条数与费用计算逻辑", function () {
# post:     const data = responseData.data;
# post:     
# post:     // 短信计费计数校验
# post:     pm.expect(data.totalSelectedCount).to.eql(1);
# post:     pm.expect(data.segmentsPerMessage).to.eql(1);
# post:     pm.expect(data.totalSegments).to.eql(1);
# post:     
# post:     // 费用校验
# post:     pm.expect(data.unitPrice).to.eql(0.01);
# post:     pm.expect(data.fixedFee).to.eql(2);
# post:     pm.expect(data.usageFee).to.eql(0.01);
# post:     pm.expect(data.totalToPay).to.eql(2.01);
# post:     
# post:     // 动态计算逻辑断言：应付金额 = 固定费 + 使用费
# post:     pm.expect(data.totalToPay).to.eql(data.fixedFee + data.usageFee);
# post:     pm.expect(data.paymentBreakdown.PAYOUT).to.eql(data.totalToPay);
# post: });
# post: 
# post: // 5. 动态数据【规避策略】：只校验类型、非空和格式，不校验具体值
# post: pm.test("校验动态生成的 ID 和时间戳格式（不校验具体值）", function () {
# post:     const data = responseData.data;
# post:     
# post:     // 1. 校验 ID 是否为非空字符串 (只要有值、是字符串就通过)
# post:     pm.expect(data.id).to.be.a('string').and.not.empty;
# post:     pm.expect(data.userId).to.be.a('string').and.not.empty;
# post:     
# post:     // 2. 使用正则表达式校验时间戳是否符合 ISO 8601 格式 (例如: 2026-06-10T03:30:52.011Z)
# post:     // 这样无论日期变成哪一天，只要格式对，断言就不会失败
# post:     const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
# post:     
# post:     pm.expect(data.createdAt).to.match(isoDateRegex);
# post:     pm.expect(data.updatedAt).to.match(isoDateRegex);
# post: });





import json

from core.assertions import expect

from core.compat import LegacyClient, legacy_render, legacy_url

def test__7631342__Linda_T4675_Verify_partner_can_duplicate_campaign_from_campaign_list(ctx):
    """Apifox case #7631342: Linda_T4675_Verify_partner_can_duplicate_campaign_from_campaign_list"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    base_url = ctx.base_url
    client = LegacyClient(ctx)
    _render = legacy_render(ctx)
    _url = legacy_url(ctx)
    # === Steps ===
    # step 1: 7ae9cb2b-f41b-4cf6-b709-acd79df3c009
    # Fix: 原逻辑限定 COMPLETED 状态 + 固定第 8 页，环境无 COMPLETED 数据导致空 id。
    # 改为多页拉取合并，按 updatedAt 取最新 Email/SMS 任务（任意状态均可被 duplicate）。
    _emailAll, _smsAll = [], []
    for _pg in range(1, 6):
        _resp1 = client.session().request(
            'GET',
            _url(base_url, '/campaigns?search=automation&pageSize=100&pageNumber=' + str(_pg), vars),
            headers={k:_render(v, vars) for k, v in [('Pear-AutoTesting', '{{Pear-AutoTesting}}'), ('Pear-Client-Id', '{{pear_client_id}}'), ('Pear-Client-Secret', '{{pear_client_secret}}'), ('Authorization', 'Bearer {{linda01_token}}')]},
            data=None,
        )
        _items = (_resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}).get('data', {}).get('items', []) or []
        _emailAll += [t for t in _items if t.get('name') == 'automation by linda Email' and t.get('channel') == 'EMAIL' and '- copy' not in (t.get('name') or '')]
        _smsAll += [t for t in _items if t.get('name') == 'automation by linda SMS' and t.get('channel') == 'SMS' and '- copy' not in (t.get('name') or '')]
        if len(_items) < 100:
            break
    _emailAll.sort(key=lambda t: t.get('updatedAt', '') or '', reverse=True)
    _smsAll.sort(key=lambda t: t.get('updatedAt', '') or '', reverse=True)
    vars['emailCompletedId'] = _emailAll[0].get('id', '') if _emailAll else ''
    vars['smsCompletedId'] = _smsAll[0].get('id', '') if _smsAll else ''
    # step 2: 1f2f2d03-7a5d-4928-ae48-d2e46c39c3a0
    _resp2 = ctx.api.campaigns.duplicate(body='{"fromId":"{{emailCompletedId}}"}', token='linda01_token')
    vars['newEmailCampaignId'] = (_resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}).get('data', {}).get('id', '')
    # assertion 2.assertion: responseJson equal DRAFT
    expect(_resp2).json('$.data.status').equals('DRAFT')
    # assertion 2.assertion: responseJson equal NOT_STARTED
    expect(_resp2).json('$.data.sentStatus').equals('NOT_STARTED')
    # step 3: 517f54f9-ea14-4a2e-b1b7-00e61a200064
    _resp3 = ctx.api.campaigns.save_recipients(body='{\r\n    "campaignId": "{{newEmailCampaignId}}",\r\n    "channel": "EMAIL",\r\n    "isSelectAll": false,\r\n    "followerIds": [\r\n        "5617efb6-1b25-4b22-af65-5a76ca51dcea"\r\n    ],\r\n    "searchKey": ""\r\n}', token='linda01_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # assertion 3.assertion: responseJson equal DRAFT
    expect(_resp3).json('$.data.status').equals('DRAFT')
    # assertion 3.assertion: responseJson equal UNPAID
    expect(_resp3).json('$.data.paymentStatus').equals('UNPAID')
    # step 4: 489b71c1-7235-454f-89ac-257c3e20bf91
    _resp4 = ctx.api.campaigns.by_campaign_id(body='{\n    "name": "automation by linda Email",\n    "status": "DRAFT",\n    "paymentStatus": "UNPAID",\n    "updatedAt": "2026-06-10T02:59:30.733Z",\n    "channel": "Email",\n    "totalSelectedCount": 1,\n    "subject": null,\n    "content": "Subject: Your Order #7892 Has Shipped!",\n    "selectAll": false,\n    "totalSegments": 1,\n    "fixedFee": 2,\n    "unitPrice": 0.01,\n    "totalToPay": 2.01,\n    "usageFee": 0.01,\n    "paymentBreakdown": {\n        "PAYOUT": 2.01,\n        "DEPOSIT": 0,\n        "CAMPAIGN": 0\n    },\n    "paymentMethod": null,\n    "id": "{{newEmailCampaignId}}"\n}', token='linda01_token', path_vars={'campaignId': '{{newEmailCampaignId}}'})
    # step 5: 199018d2-d106-427d-844b-1e955ec5da56
    _resp5 = ctx.api.campaigns.duplicate(body='{"fromId":"{{smsCompletedId}}"}', token='linda01_token')
    vars['newSMSCampaignId'] = (_resp5.json() if _resp5.headers.get('content-type', '').startswith('application/json') else {}).get('data', {}).get('id', '')
    # assertion 5.assertion: responseJson equal DRAFT
    expect(_resp5).json('$.data.status').equals('DRAFT')
    # assertion 5.assertion: responseJson equal NOT_STARTED
    expect(_resp5).json('$.data.sentStatus').equals('NOT_STARTED')
    # step 6: 0a76cd94-607d-4f1f-92af-238924d2f660
    _resp6 = ctx.api.campaigns.save_recipients(body='{\r\n    "campaignId": "{{newSMSCampaignId}}",\r\n    "channel": "SMS",\r\n    "isSelectAll": false,\r\n    "followerIds": [\r\n        "bbf4a1ee-d93d-4e92-9e73-53ba168d7a66"\r\n    ],\r\n    "searchKey": ""\r\n}', token='linda01_token')
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # assertion 6.assertion: responseJson equal DRAFT
    expect(_resp6).json('$.data.status').equals('DRAFT')
    # assertion 6.assertion: responseJson equal UNPAID
    expect(_resp6).json('$.data.paymentStatus').equals('UNPAID')
    # step 7: bfe008d5-9baa-48c3-ab74-bb1be46524e7
    _resp7 = ctx.api.campaigns.by_campaign_id(body='{\n    "name": "automation by linda SMS",\n    "status": "DRAFT",\n    "paymentStatus": "UNPAID",\n    "updatedAt": "2026-06-10T02:59:30.733Z",\n    "channel": "SMS",\n    "totalSelectedCount": 1,\n    "subject": null,\n    "content": "Subject: Your Order #7892 Has Shipped!",\n    "selectAll": false,\n    "totalSegments": 1,\n    "fixedFee": 2,\n    "unitPrice": 0.01,\n    "totalToPay": 2.01,\n    "usageFee": 0.01,\n    "paymentBreakdown": {\n        "PAYOUT": 2.01,\n        "DEPOSIT": 0,\n        "CAMPAIGN": 0\n    },\n    "paymentMethod": null,\n    "id": "{{newSMSCampaignId}}"\n}', token='linda01_token', path_vars={'campaignId': '{{newSMSCampaignId}}'})
