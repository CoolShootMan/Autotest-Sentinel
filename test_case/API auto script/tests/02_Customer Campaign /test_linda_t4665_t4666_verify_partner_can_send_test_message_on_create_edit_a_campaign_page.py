"""Migrated from Apifox case #7627466. Source folder: Customer Campaign ."""
# Apifox Case ID: 7627466  (traceability only — not needed to run)
NAME = "&T4666 Verify partner can send test message on create/edit a campaign page"
TAGS = ["p0", "customer_campaign", "suite:linda"]
PRIORITY = 0


CASE_ID = 7627466
ENV_NAME = "Release"

# --- step 1: 7ca979c8-3cf3-43ba-8d7c-e05e7376ca3e ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "campaignId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 44eb5382-8097-4e06-8560-ebd2977dfa90 ---
# post[customScript]: // 解析响应体
# post: const responseData = pm.response.json();
# post: 
# post: // 断言 data.success 为 true
# post: pm.test("断言 success 字段为 true", function () {
# post:     pm.expect(responseData.data.success).to.eql(true);
# post: });
# post: 
# post: // 断言 data.message 包含特定文本
# post: pm.test("断言 message 包含正确文本", function () {
# post:     pm.expect(responseData.data.message).to.eql("Test SMS sent to 1 recipients");
# post: });
# --- step 3: b92f242b-bdde-4990-a60b-dd28927d565f ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "DRAFT", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNPAID", "path": "$.data.paymentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.paymentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 23b926f2-e38a-4bd3-8e50-a62f6056dd5a ---
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
# --- step 5: 22cb6be9-87bc-4d2e-9b12-9f7ea3893fde ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "campaignEmailId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.totalSelectedCount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalSelectedCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: 61601488-2af7-4ca6-a02b-41ae83c1ea84 ---
# post[customScript]: // 解析响应体
# post: const responseData = pm.response.json();
# post: 
# post: // 断言 data.success 为 true
# post: pm.test("断言 success 字段为 true", function () {
# post:     pm.expect(responseData.data.success).to.eql(true);
# post: });
# post: 
# post: // 断言 data.message 包含特定文本
# post: pm.test("断言 message 包含正确文本", function () {
# post:     pm.expect(responseData.data.message).to.eql("Test email sent to 1 recipients");
# post: });
# --- step 7: 54e129b3-db56-40e8-ba4b-d571e363b0af ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "DRAFT", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNPAID", "path": "$.data.paymentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.paymentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: 01fafcc9-e6df-40c3-be23-b67ff3d052e3 ---
# post[customScript]: // 1. 将响应体解析为 JSON 对象
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 基础状态断言
# post: pm.test("响应状态码为 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: pm.test("业务状态码 code 应该为 200", function () {
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post: });
# post: 
# post: // 3. 核心业务数据断言 (data 内的字段)
# post: pm.test("断言活动关键状态字段", function () {
# post:     const data = responseData.data;
# post:     
# post:     // 验证核心状态
# post:     pm.expect(data.status).to.eql("DRAFT");
# post:     pm.expect(data.paymentStatus).to.eql("UNPAID");
# post:     pm.expect(data.sentStatus).to.eql("NOT_STARTED");
# post:     
# post:     // 验证名称和渠道
# post:     pm.expect(data.name).to.eql("automation by linda Email");
# post:     pm.expect(data.channel).to.eql("EMAIL");
# post:     
# post:     // 验证 ID 存在且不为空
# post:     pm.expect(data.id).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 4. 费用与计算逻辑断言
# post: pm.test("断言费用计算是否正确", function () {
# post:     const data = responseData.data;
# post:     pm.expect(data.unitPrice).to.eql(0.001);
# post:     pm.expect(data.totalToPay).to.eql(1);
# post:     pm.expect(data.paymentBreakdown.PAYOUT).to.eql(1);
# post: });




import json
import re

from core.assertions import expect

def test_linda_t4665_t4666_verify_partner_can_send_test_message_on_create_edit_a_campaign_page(ctx):
    """Apifox case #7627466: Linda_T4665_T4666_Verify_partner_can_send_test_message_on_create_edit_a_campaign"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 7ca979c8-3cf3-43ba-8d7c-e05e7376ca3e
    _resp1 = ctx.api.campaigns.create(body='{\r\n    "channel": "SMS",\r\n    "name": "automation by linda SMS",\r\n    "content": "Subject: Your Order #7892 Has Shipped!"\r\n}', token='linda01_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # extractor: campaignId = $.data.id
    ctx.extract('campaignId', _resp1, '$.data.id')
    # step 2: 44eb5382-8097-4e06-8560-ebd2977dfa90
    _resp2 = ctx.api.campaigns.test_sms(body='{\n    "phones": [\n        "+16502396646"\n    ],\n    "message": "Subject: Your Order #7892 Has Shipped!"\n}', token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert (_j2.get('data') or {}).get('success') is True, f"data.success应为true，实际={(_j2.get('data') or {}).get('success')!r}"
    assert (_j2.get('data') or {}).get('message') == "Test SMS sent to 1 recipients", f"data.message不匹配：{(_j2.get('data') or {}).get('message')!r}"
    # step 3: b92f242b-bdde-4990-a60b-dd28927d565f
    _resp3 = ctx.api.campaigns.save_recipients(body='{\r\n    "campaignId": "{{campaignId}}",\r\n    "channel": "SMS",\r\n    "isSelectAll": false,\r\n    "followerIds": [\r\n        "bbf4a1ee-d93d-4e92-9e73-53ba168d7a66"\r\n    ],\r\n    "searchKey": ""\r\n}', token='linda01_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # assertion 3.assertion: responseJson equal DRAFT
    expect(_resp3).json('$.data.status').equals('DRAFT')
    # assertion 3.assertion: responseJson equal UNPAID
    expect(_resp3).json('$.data.paymentStatus').equals('UNPAID')
    # step 4: 23b926f2-e38a-4bd3-8e50-a62f6056dd5a
    _resp4 = ctx.api.campaigns.by_campaign_id(body='{\n    "name": "automation by linda SMS",\n    "status": "DRAFT",\n    "paymentStatus": "UNPAID",\n    "updatedAt": "2026-06-10T02:59:30.733Z",\n    "channel": "SMS",\n    "totalSelectedCount": 1,\n    "subject": null,\n    "content": "Subject: Your Order #7892 Has Shipped!",\n    "selectAll": false,\n    "totalSegments": 1,\n    "fixedFee": 2,\n    "unitPrice": 0.01,\n    "totalToPay": 2.01,\n    "usageFee": 0.01,\n    "paymentBreakdown": {\n        "PAYOUT": 2.01,\n        "DEPOSIT": 0,\n        "CAMPAIGN": 0\n    },\n    "paymentMethod": null,\n    "id": "{{campaignId}}"\n}', token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j4 = _resp4.json() if _resp4.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp4.status_code == 200, f"HTTP状态码应为200，实际={_resp4.status_code}"
    assert _j4.get('code') == 200, f"业务code应为200，实际={_j4.get('code')!r}"
    assert _j4.get('message') == 'success', f"message应为success，实际={_j4.get('message')!r}"
    assert isinstance(_j4.get('request_id'), str) and _j4.get('request_id'), f"request_id应为非空字符串，实际={_j4.get('request_id')!r}"
    _d4 = _j4.get('data') or {}
    # 核心业务字段断言（固定配置和状态）
    assert _d4.get('name') == "automation by linda SMS", f"data.name不匹配：{_d4.get('name')!r}"
    assert _d4.get('channel') == "SMS", f"data.channel应为SMS，实际={_d4.get('channel')!r}"
    assert _d4.get('status') == "DRAFT", f"data.status应为DRAFT，实际={_d4.get('status')!r}"
    assert _d4.get('paymentStatus') == "UNPAID", f"data.paymentStatus应为UNPAID，实际={_d4.get('paymentStatus')!r}"
    assert _d4.get('sentStatus') == "NOT_STARTED", f"data.sentStatus应为NOT_STARTED，实际={_d4.get('sentStatus')!r}"
    assert _d4.get('smsEncoding') == "GSM_7", f"data.smsEncoding应为GSM_7，实际={_d4.get('smsEncoding')!r}"
    # 短信条数与费用计算逻辑
    assert _d4.get('totalSelectedCount') == 1, f"totalSelectedCount应为1，实际={_d4.get('totalSelectedCount')!r}"
    assert _d4.get('segmentsPerMessage') == 1, f"segmentsPerMessage应为1，实际={_d4.get('segmentsPerMessage')!r}"
    assert _d4.get('totalSegments') == 1, f"totalSegments应为1，实际={_d4.get('totalSegments')!r}"
    assert _d4.get('unitPrice') == 0.01, f"unitPrice应为0.01，实际={_d4.get('unitPrice')!r}"
    assert _d4.get('fixedFee') == 2, f"fixedFee应为2，实际={_d4.get('fixedFee')!r}"
    assert _d4.get('usageFee') == 0.01, f"usageFee应为0.01，实际={_d4.get('usageFee')!r}"
    assert _d4.get('totalToPay') == 2.01, f"totalToPay应为2.01，实际={_d4.get('totalToPay')!r}"
    assert _d4.get('totalToPay') == (_d4.get('fixedFee') or 0) + (_d4.get('usageFee') or 0), f"应付金额应=固定费+使用费，实际totalToPay={_d4.get('totalToPay')!r}"
    assert (_d4.get('paymentBreakdown') or {}).get('PAYOUT') == _d4.get('totalToPay'), f"paymentBreakdown.PAYOUT应等于totalToPay，实际={(_d4.get('paymentBreakdown') or {}).get('PAYOUT')!r}"
    # 动态数据：只校验类型、非空和格式
    assert isinstance(_d4.get('id'), str) and _d4.get('id'), f"data.id应为非空字符串，实际={_d4.get('id')!r}"
    assert isinstance(_d4.get('userId'), str) and _d4.get('userId'), f"data.userId应为非空字符串，实际={_d4.get('userId')!r}"
    _iso_re = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')
    assert _iso_re.match(str(_d4.get('createdAt') or '')), f"createdAt格式不正确：{_d4.get('createdAt')!r}"
    assert _iso_re.match(str(_d4.get('updatedAt') or '')), f"updatedAt格式不正确：{_d4.get('updatedAt')!r}"
    # step 5: 22cb6be9-87bc-4d2e-9b12-9f7ea3893fde
    _resp5 = ctx.api.campaigns.create(body='{\r\n    "channel": "EMAIL",\r\n    "content": "<p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><b><strong class=\\"katana__textBold\\" style=\\"color: rgb(0, 0, 0); font-size: 16px; line-height: 28px; white-space: pre-wrap;\\">Subject: Don’t Miss Out! Live Concert 2026 – Early Bird Tickets Now On Sale</strong></b></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Dear Music Lover,</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">We’re thrilled to announce that global superstar [Artist Name] is hitting the stage in your city this summer! The “Stellar Nights Tour” will light up [Venue Name] on [Date, Time], featuring hit songs from their latest album and classic fan favorites—plus exclusive stage visuals you won’t want to miss.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Secure your spot before prices rise: early bird tickets are 20% off until [Deadline]! Grab yours here: bit.ly/StellarNights2025. Limited VIP packages include meet-and-greets and backstage access—perfect for die-hard fans.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Hurry, tickets sell out fast for [Artist Name]’s tours! For group bookings or questions, email </span><a href=\\"mailto:support@concertpro.com\\" class=\\"katana__link\\" dir=\\"ltr\\"><span style=\\"white-space: pre-wrap;\\">support@concertpro.com</span></a><span style=\\"white-space: pre-wrap;\\"> or call +1-800-567-8901.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Don’t let this unforgettable night slip away—see you at the show!</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Best regards,The ConcertPro TeamYour Go-To for Unforgettable Live Music Experiences</span></p>",\r\n    "name": "automation by linda Email",\r\n    "subject": "Don’t Miss Out! "\r\n}', token='linda01_token')
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson equal success
    expect(_resp5).json('$.message').equals('success')
    # extractor: campaignEmailId = $.data.id
    ctx.extract('campaignEmailId', _resp5, '$.data.id')
    # assertion 5.assertion: responseJson equal 0
    expect(_resp5).json('$.data.totalSelectedCount').equals('0')
    # step 6: 61601488-2af7-4ca6-a02b-41ae83c1ea84
    _resp6 = ctx.api.campaigns.test_email(body='{\n    "emails": [\n        "linda.zhou.ext@1m.app"\n    ],\n    "subject": "Don’t Miss Out! ",\n    "content": "<p class=\\"katana__paragraph katana__paragraph--align-start\\" style=\\"text-align: start;\\"><b><strong class=\\"katana__textBold\\" style=\\"white-space: pre-wrap;\\">Subject: Don’t Miss Out! Live Concert 2026 – Early Bird Tickets Now On Sale</strong></b></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Dear Music Lover,</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">We’re thrilled to announce that global superstar [Artist Name] is hitting the stage in your city this summer! The “Stellar Nights Tour” will light up [Venue Name] on [Date, Time], featuring hit songs from their latest album and classic fan favorites—plus exclusive stage visuals you won’t want to miss.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Secure your spot before prices rise: early bird tickets are 20% off until [Deadline]! Grab yours here: bit.ly/StellarNights2025. Limited VIP packages include meet-and-greets and backstage access—perfect for die-hard fans.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Hurry, tickets sell out fast for [Artist Name]’s tours! For group bookings or questions, email </span><a data-id=\\"cdea418f-8db7-4f4d-9bb1-6844186cffa9\\" href=\\"mailto:support@concertpro.com\\"><span style=\\"white-space: pre-wrap;\\">support@concertpro.com</span></a><span style=\\"white-space: pre-wrap;\\"> or call +1-800-567-8901.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Don’t let this unforgettable night slip away—see you at the show!</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Best regards,The ConcertPro TeamYour Go-To for Unforgettable Live Music Experiences</span></p>"\n}', token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j6 = _resp6.json() if _resp6.headers.get('content-type', '').startswith('application/json') else {}
    assert (_j6.get('data') or {}).get('success') is True, f"data.success应为true，实际={(_j6.get('data') or {}).get('success')!r}"
    assert (_j6.get('data') or {}).get('message') == "Test email sent to 1 recipients", f"data.message不匹配：{(_j6.get('data') or {}).get('message')!r}"
    # step 7: 54e129b3-db56-40e8-ba4b-d571e363b0af
    _resp7 = ctx.api.campaigns.save_recipients(body='{\r\n    "campaignId": "{{campaignEmailId}}",\r\n    "channel": "EMAIL",\r\n    "isSelectAll": false,\r\n    "followerIds": [\r\n        "5617efb6-1b25-4b22-af65-5a76ca51dcea"\r\n    ],\r\n    "searchKey": ""\r\n}', token='linda01_token')
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal success
    expect(_resp7).json('$.message').equals('success')
    # assertion 7.assertion: responseJson equal DRAFT
    expect(_resp7).json('$.data.status').equals('DRAFT')
    # assertion 7.assertion: responseJson equal UNPAID
    expect(_resp7).json('$.data.paymentStatus').equals('UNPAID')
    # step 8: 01fafcc9-e6df-40c3-be23-b67ff3d052e3
    _resp8 = ctx.api.campaigns.by_campaign_id(body='{\n    "name": "automation by linda Email",\n    "status": "DRAFT",\n    "paymentStatus": "UNPAID",\n    "updatedAt": "2026-06-10T02:59:30.733Z",\n    "channel": "Email",\n    "totalSelectedCount": 1,\n    "subject": null,\n    "content": "Subject: Your Order #7892 Has Shipped!",\n    "selectAll": false,\n    "totalSegments": 1,\n    "fixedFee": 2,\n    "unitPrice": 0.01,\n    "totalToPay": 2.01,\n    "usageFee": 0.01,\n    "paymentBreakdown": {\n        "PAYOUT": 2.01,\n        "DEPOSIT": 0,\n        "CAMPAIGN": 0\n    },\n    "paymentMethod": null,\n    "id": "{{campaignEmailId}}"\n}', token='linda01_token', path_vars={'campaignId': '{{campaignEmailId}}'})
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j8 = _resp8.json() if _resp8.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp8.status_code == 200, f"响应状态码为200，实际={_resp8.status_code}"
    assert _j8.get('code') == 200, f"业务code应为200，实际={_j8.get('code')!r}"
    assert _j8.get('message') == 'success', f"message应为success，实际={_j8.get('message')!r}"
    _d8 = _j8.get('data') or {}
    # 核心业务数据断言
    assert _d8.get('status') == "DRAFT", f"data.status应为DRAFT，实际={_d8.get('status')!r}"
    assert _d8.get('paymentStatus') == "UNPAID", f"data.paymentStatus应为UNPAID，实际={_d8.get('paymentStatus')!r}"
    assert _d8.get('sentStatus') == "NOT_STARTED", f"data.sentStatus应为NOT_STARTED，实际={_d8.get('sentStatus')!r}"
    assert _d8.get('name') == "automation by linda Email", f"data.name不匹配：{_d8.get('name')!r}"
    assert _d8.get('channel') == "EMAIL", f"data.channel应为EMAIL，实际={_d8.get('channel')!r}"
    assert isinstance(_d8.get('id'), str) and _d8.get('id'), f"data.id应为非空字符串，实际={_d8.get('id')!r}"
    # 费用与计算逻辑断言
    assert _d8.get('unitPrice') == 0.001, f"unitPrice应为0.001，实际={_d8.get('unitPrice')!r}"
    assert _d8.get('totalToPay') == 1, f"totalToPay应为1，实际={_d8.get('totalToPay')!r}"
    assert (_d8.get('paymentBreakdown') or {}).get('PAYOUT') == 1, f"paymentBreakdown.PAYOUT应为1，实际={(_d8.get('paymentBreakdown') or {}).get('PAYOUT')!r}"
