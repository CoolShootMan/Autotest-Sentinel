"""Migrated from Apifox case #8620149. Source folder: Customer Campaign ."""
# Apifox Case ID: 8620149  (traceability only — not needed to run)
NAME = "Draft (Lury) save campaign"
TAGS = ["p0", "customer_campaign"]
PRIORITY = 0


CASE_ID = 8620149
ENV_NAME = "Release"

# --- step 1: 9a75640c-d265-4ab9-9720-b744223feca8 ---
# pre: 
# pre: pm.variables.set("account_email_curator","linda.zhou.ext+01@1m.app");
# pre: pm.variables.set("password","7EbE8F4BdE4A38768AcF9C2833aF2Db5");
# pre: 
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "message", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 34598a15-1010-4b0a-b0c4-39a213a310d6 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "campaignId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 21e3b97e-07cf-4c8e-a0ed-7b8419fd4c24 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "selected_count_sms", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.totalSelectedCount", "extractSettings": {"expression": "$.data.totalSelectedCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}, "value": 992}}
# post[assertion]: {"name": "Check number of segment", "subject": "responseJson", "comparison": "equal", "value": "1", "path": "$.data.segmentsPerMessage", "multipleValue": [], "extractSettings": {"expression": "$.data.segmentsPerMessage", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}, "value": 1}}
# post[assertion]: {"name": "Check unit price for SMS", "subject": "responseJson", "comparison": "equal", "value": "0.01", "path": "$.data.unitPrice", "multipleValue": [], "extractSettings": {"expression": "$.data.unitPrice", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Check sms fixed fee", "subject": "responseJson", "comparison": "equal", "value": "2", "path": "$.data.fixedFee", "multipleValue": [], "extractSettings": {"expression": "$.data.fixedFee", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}, "value": 2}}
# post[extractor]: {"variableName": "total_fee", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.totalToPay", "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_draft_lury_save_campaign(ctx):
    """Apifox case #8620149: Draft_Lury_save_campaign"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['account_email_curator'] = 'linda.zhou.ext+01@1m.app'
    vars['password'] = '7EbE8F4BdE4A38768AcF9C2833aF2Db5'
    # step 1: 9a75640c-d265-4ab9-9720-b744223feca8
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{merchant_email}}",\r\n    "password": "{{merchant_password}}"\r\n\r\n}', app_headers=True)
    # assertion 1.code: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # extractor: token = $.data.token
    ctx.extract('token', _resp1, '$.data.token')
    # assertion 1.message: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # step 2: 34598a15-1010-4b0a-b0c4-39a213a310d6
    _resp2 = ctx.api.campaigns.create(body='{\r\n    "channel": "SMS",\r\n    "name": "Automation by Lury SMS",\r\n    "content": "This is test SMS message from Lury, It will don\'t send to any one"\r\n}', token='token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # extractor: campaignId = $.data.id
    ctx.extract('campaignId', _resp2, '$.data.id')
    # step 3: 21e3b97e-07cf-4c8e-a0ed-7b8419fd4c24
    _resp3 = ctx.api.campaigns.save_recipients(body='{\r\n    "campaignId": "{{campaignId}}",\r\n    "channel": "SMS",\r\n    "isSelectAll": false,\r\n    "followerIds": [\r\n        "d3435d0a-d6df-4f80-a9b2-f5da77b368fe"\r\n    ],\r\n    "excludeFollowers": [],\r\n    "searchKey": "6502469802"\r\n}', token='token')
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
