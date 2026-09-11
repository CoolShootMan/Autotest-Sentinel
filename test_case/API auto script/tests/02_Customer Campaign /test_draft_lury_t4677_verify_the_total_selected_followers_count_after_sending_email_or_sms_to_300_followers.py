"""Migrated from Apifox case #7887702. Source folder: Customer Campaign ."""
# Apifox Case ID: 7887702  (traceability only — not needed to run)
NAME = "Draft (Lury) T4677 Verify the total selected followers count after sending email or sms to 300 followers"
TAGS = ["p0", "customer_campaign"]
PRIORITY = 0


CASE_ID = 7887702
ENV_NAME = "Release"

# --- step 1: 0bf1899f-fbd7-4a27-ad68-ebe75c2d0c79 ---
# pre: 
# pre: pm.variables.set("account_email_curator","linda.zhou.ext+01@1m.app");
# pre: pm.variables.set("password","7EbE8F4BdE4A38768AcF9C2833aF2Db5");
# pre: 
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "message", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: d87b06a3-e82b-49ee-859e-30d58148eb79 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "campaignId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 6061b2f6-2b19-4667-a6ed-844f3154f402 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "selected_count_sms", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.totalSelectedCount", "extractSettings": {"expression": "$.data.totalSelectedCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}, "value": 992}}
# post[assertion]: {"name": "Check number of segment", "subject": "responseJson", "comparison": "equal", "value": "1", "path": "$.data.segmentsPerMessage", "multipleValue": [], "extractSettings": {"expression": "$.data.segmentsPerMessage", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}, "value": 1}}
# post[assertion]: {"name": "Check unit price for SMS", "subject": "responseJson", "comparison": "equal", "value": "0.01", "path": "$.data.unitPrice", "multipleValue": [], "extractSettings": {"expression": "$.data.unitPrice", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Check sms fixed fee", "subject": "responseJson", "comparison": "equal", "value": "2", "path": "$.data.fixedFee", "multipleValue": [], "extractSettings": {"expression": "$.data.fixedFee", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}, "value": 2}}
# post[extractor]: {"variableName": "total_fee", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.totalToPay", "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: c9f3fecb-29c5-466b-9879-249f7e32c68c ---
# --- step 5: View campaign details ---
# post[assertion]: {"name": "Verify total selected count", "subject": "responseJson", "comparison": "equal", "value": "{{selected_count_sms}}", "path": "$.data.totalSelectedCount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalSelectedCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.test("View campaign details apge", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["name"]).to.eql("Automation by Lury SMS");
# post:     pm.expect(data["status"]).to.eql("COMPLETED");
# post:     pm.expect(data["channel"]).to.eql("SMS");
# post:     pm.expect(data["selectAll"]).to.eql(false);
# post:     pm.expect(data["totalSuccess"]).to.eql(0);
# post:     pm.expect(data["totalFailed"]).to.eql(0);
# post:     pm.expect(data["totalOptedOut"]).to.eql(0);
# post: 
# post: });
# --- step 6: ffee0cf5-e86d-46da-931d-5ea9b96efb0c ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "campaignEmailId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.totalSelectedCount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalSelectedCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: 2bf1f632-5d0d-4846-95e8-1caeb80d37bc ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.deleted", "multipleValue": [], "extractSettings": {"expression": "$.data.deleted", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "selected_count_email", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.created", "extractSettings": {"expression": "$.data.created", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: 781af5bc-bc11-4ea5-9bae-91042713f252 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "true", "path": "$.data.success", "multipleValue": [], "extractSettings": {"expression": "$.data.success", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: View campaign details ---
# post[assertion]: {"name": "Verify select followers count", "subject": "responseJson", "comparison": "equal", "value": "{{selected_count_email}}", "path": "$.data.totalSelectedCount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalSelectedCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.test("View campaign details apge", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     pm.expect(data["name"]).to.eql("Automation by Lury campaign Email");
# post:     pm.expect(data["status"]).to.eql("COMPLETED");
# post:     pm.expect(data["channel"]).to.eql("EMAIL");
# post:     pm.expect(data["selectAll"]).to.eql(false);
# post:     pm.expect(data["totalSuccess"]).to.eql(0);
# post:     pm.expect(data["totalFailed"]).to.eql(0);
# post:     pm.expect(data["totalOptedOut"]).to.eql(0);
# post: 
# post: });




from core.assertions import expect

def test_draft_lury_t4677_verify_the_total_selected_followers_count_after_sending_email_or_sms_to_300_followers(ctx):
    """Apifox case #7887702: Draft_Lury_T4677_Verify_the_total_selected_followers_count_after_sending_email_o"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['account_email_curator'] = 'linda.zhou.ext+01@1m.app'
    vars['password'] = '7EbE8F4BdE4A38768AcF9C2833aF2Db5'
    # step 1: 0bf1899f-fbd7-4a27-ad68-ebe75c2d0c79
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{merchant_email}}",\r\n    "password": "{{merchant_password}}"\r\n\r\n}', app_headers=True)
    # assertion 1.code: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # extractor: token = $.data.token
    ctx.extract('token', _resp1, '$.data.token')
    # assertion 1.message: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # step 2: d87b06a3-e82b-49ee-859e-30d58148eb79
    _resp2 = ctx.api.campaigns.create(body='{\r\n    "channel": "SMS",\r\n    "name": "Automation by Lury SMS",\r\n    "content": "This is test SMS message from Lury, It will don\'t send to any one"\r\n}', token='token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # extractor: campaignId = $.data.id
    ctx.extract('campaignId', _resp2, '$.data.id')
    # step 3: 6061b2f6-2b19-4667-a6ed-844f3154f402
    _resp3 = ctx.api.campaigns.save_recipients(body='{\r\n    "campaignId": "{{campaignId}}",\r\n    "channel": "SMS",\r\n    "isSelectAll": true,\r\n    "followerIds": [],\r\n    "excludeFollowers": [],\r\n    "searchKey": ""\r\n}', token='token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # extractor: selected_count_sms = $.data.totalSelectedCount
    ctx.extract('selected_count_sms', _resp3, '$.data.totalSelectedCount')
    # assertion 3.Check number of segment: responseJson equal 1
    expect(_resp3).json('$.data.segmentsPerMessage').equals('1')
    # assertion 3.Check unit price for SMS: responseJson equal 0.01
    expect(_resp3).json('$.data.unitPrice').equals('0.01')
    # assertion 3.Check sms fixed fee: responseJson equal 2
    expect(_resp3).json('$.data.fixedFee').equals('2')
    # extractor: total_fee = $.data.totalToPay
    ctx.extract('total_fee', _resp3, '$.data.totalToPay')
    # step 4: c9f3fecb-29c5-466b-9879-249f7e32c68c
    _resp4 = ctx.api.campaigns.send_campaign(body='{\n    "campaignId": "{{campaignId}}",\n    "channel": "SMS",\n    "paymentBreakdown": {\n        "CAMPAIGN": 0,\n        "PAYOUT": {{total_fee}}\n    }\n}', token='token')
    # step 5: View campaign details
    _resp5 = ctx.api.campaigns.by_campaign_id_2(token='token')
    # assertion 5.Verify total selected count: responseJson equal {{selected_count_sms}}
    expect(_resp5).json('$.data.totalSelectedCount').equals(ctx.render_text('{{selected_count_sms}}'))
    # step 6: ffee0cf5-e86d-46da-931d-5ea9b96efb0c
    _resp6 = ctx.api.campaigns.create(body='{\r\n    "channel": "EMAIL",\r\n    "content": "<p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><b><strong class=\\"katana__textBold\\" style=\\"color: rgb(0, 0, 0); font-size: 16px; line-height: 28px; white-space: pre-wrap;\\">Subject: Don’t Miss Out! Live Concert 2026 – Early Bird Tickets Now On Sale</strong></b></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Dear Music Lover,</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">We’re thrilled to announce that global superstar [Artist Name] is hitting the stage in your city this summer! The “Stellar Nights Tour” will light up [Venue Name] on [Date, Time], featuring hit songs from their latest album and classic fan favorites—plus exclusive stage visuals you won’t want to miss.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Secure your spot before prices rise: early bird tickets are 20% off until [Deadline]! Grab yours here: bit.ly/StellarNights2025. Limited VIP packages include meet-and-greets and backstage access—perfect for die-hard fans.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Hurry, tickets sell out fast for [Artist Name]’s tours! For group bookings or questions, email </span><a href=\\"mailto:support@concertpro.com\\" class=\\"katana__link\\" dir=\\"ltr\\"><span style=\\"white-space: pre-wrap;\\">support@concertpro.com</span></a><span style=\\"white-space: pre-wrap;\\"> or call +1-800-567-8901.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Don’t let this unforgettable night slip away—see you at the show!</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Best regards,The ConcertPro TeamYour Go-To for Unforgettable Live Music Experiences</span></p>",\r\n    "name": "Automation by Lury campaign Email",\r\n    "subject": "Don’t Miss Out! "\r\n}', token='token')
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # extractor: campaignEmailId = $.data.id
    ctx.extract('campaignEmailId', _resp6, '$.data.id')
    # assertion 6.assertion: responseJson equal 0
    expect(_resp6).json('$.data.totalSelectedCount').equals('0')
    # step 7: 2bf1f632-5d0d-4846-95e8-1caeb80d37bc
    _resp7 = ctx.api.campaigns.save_recipients(body='{\r\n    "campaignId": "{{campaignEmailId}}",\r\n    "channel": "EMAIL",\r\n    "isSelectAll": true,\r\n    "followerIds": [],\r\n    "searchKey": ""\r\n}', token='token')
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal success
    expect(_resp7).json('$.message').equals('success')
    # assertion 7.assertion: responseJson equal 0
    expect(_resp7).json('$.data.deleted').equals('0')
    # extractor: selected_count_email = $.data.created
    ctx.extract('selected_count_email', _resp7, '$.data.created')
    # step 8: 781af5bc-bc11-4ea5-9bae-91042713f252
    _resp8 = ctx.api.campaigns.send_campaign(body='{"campaignId":"{{campaignEmailId}}","channel":"EMAIL"}', token='token')
    # assertion 8.assertion: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # assertion 8.assertion: responseJson equal true
    expect(_resp8).json('$.data.success').equals('true')
    # step 9: View campaign details
    _resp9 = ctx.api.campaigns.by_campaign_id_2(token='token', path_vars={'campaignId': '{{campaignEmailId}}'})
    # assertion 9.Verify select followers count: responseJson equal {{selected_count_email}}
    expect(_resp9).json('$.data.totalSelectedCount').equals(ctx.render_text('{{selected_count_email}}'))
