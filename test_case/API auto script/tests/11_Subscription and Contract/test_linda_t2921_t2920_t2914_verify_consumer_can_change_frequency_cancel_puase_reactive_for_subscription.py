"""Auto-generated from Apifox case #6129906. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 6129906
# Folder: 
# Case: (Linda)T2921 &T2920 & T2914  Verify consumer can change frequency &Cancel & Puase & Reactive for subscription
# Priority: P0
# Created: 2025-03-10T06:33:15.000Z
# Updated: 2026-08-11T06:23:25.000Z


CASE_ID = 6129906
ENV_NAME = "Release"

# --- step 1: update contract - change frequency ---
# pre: pm.environment.set("subscriptionPlanOptionId", "4965c739-adc4-4a2a-a803-74283126837d");
# pre: pm.environment.set("contractId", "ce86abb3-3181-40e8-86e6-adaf06e91aa9");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{subscriptionPlanOptionId}}", "path": "$.data.subscriptionPlanOptionId", "multipleValue": [], "extractSettings": {"expression": "$.data.subscriptionPlanOptionId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: const assert = require('assert');
# post: 
# post: const data = {
# post:     id: 'a1d25fb7-5d5c-437d-b5f4-db9ac41b7bdf'
# post: };
# post: 
# post: const expectedId = 'a1d25fb7-5d5c-437d-b5f4-db9ac41b7bdf ';
# post: 
# post: // 去除字符串两端的空格
# post: const trimmedExpectedId = expectedId.trim();
# post: 
# post: try {
# post:     assert.deepStrictEqual(data.id, trimmedExpectedId);
# post:     console.log('断言通过');
# post: } catch (error) {
# post:     console.error(error);
# post: }
# --- step 2: update contract - pause the subscription ---
# pre: // pm.environment.set("subscriptionPlanOptionId", "4965c739-adc4-4a2a-a803-74283126837d");
# pre: // pm.environment.set("contractId", "a1d25fb7-5d5c-437d-b5f4-db9ac41b7bdf");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "PAUSED", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{contractId}}", "path": "$.data.id", "multipleValue": [], "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: update contract - reactive the subscription ---
# pre: // pm.environment.set("subscriptionPlanOptionId", "4965c739-adc4-4a2a-a803-74283126837d");
# pre: // pm.environment.set("contractId", "a1d25fb7-5d5c-437d-b5f4-db9ac41b7bdf");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "NORMAL", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{contractId}}", "path": "$.data.id", "multipleValue": [], "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: update contract - Cancel the subscription ---
# pre: // pm.environment.set("subscriptionPlanOptionId", "4965c739-adc4-4a2a-a803-74283126837d");
# pre: // pm.environment.set("contractId", "a1d25fb7-5d5c-437d-b5f4-db9ac41b7bdf");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "CANCELED", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{contractId}}", "path": "$.data.id", "multipleValue": [], "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





from core.assertions import expect

def test__6129906__Linda_T2921_T2920_T2914_Verify_consumer_can_change_frequency_Cancel_Puase_Reactive_for_subscription(ctx):
    """Apifox case #6129906: Linda_T2921_T2920_T2914_Verify_consumer_can_change_frequency_Cancel_Puase_Reacti"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['subscriptionPlanOptionId'] = '4965c739-adc4-4a2a-a803-74283126837d'
    vars['contractId'] = 'ce86abb3-3181-40e8-86e6-adaf06e91aa9'
    # step 1: update contract - change frequency
    _resp1 = ctx.api.users.self_contracts_by_contract_id(body='{\r\n    "contractId": "{{contractId}}",\r\n    "subscriptionPlanOptionId": "{{subscriptionPlanOptionId}}"\r\n}', token='linda10_token')
    # assertion 1.assertion: responseJson equal {{subscriptionPlanOptionId}}
    expect(_resp1).json('$.data.subscriptionPlanOptionId').equals(ctx.render_text('{{subscriptionPlanOptionId}}'))
    vars['subscriptionPlanOptionId'] = '4965c739-adc4-4a2a-a803-74283126837d'
    # 注意：Apifox 原文此处对 contractId 的重新赋值是 `//` 注释掉的，
    # 即 step3/4/5 沿用 step2 的 ce86abb3；迁移器误把注释当有效代码，
    # 取了另一个已不存在的合约 → 404。
    vars['contractId'] = 'ce86abb3-3181-40e8-86e6-adaf06e91aa9'
    # step 2: update contract - pause the subscription
    _resp2 = ctx.api.users.self_contracts_by_contract_id(body='{\r\n    "contractId": "{{contractId}}",\r\n    "status": "PAUSED"\r\n}', token='linda10_token')
    # assertion 2.assertion: responseJson equal PAUSED
    expect(_resp2).json('$.data.status').equals('PAUSED')
    # assertion 2.assertion: responseJson equal {{contractId}}
    expect(_resp2).json('$.data.id').equals(ctx.render_text('{{contractId}}'))
    vars['subscriptionPlanOptionId'] = '4965c739-adc4-4a2a-a803-74283126837d'
    # 注意：Apifox 原文此处对 contractId 的重新赋值是 `//` 注释掉的，
    # 即 step3/4/5 沿用 step2 的 ce86abb3；迁移器误把注释当有效代码，
    # 取了另一个已不存在的合约 → 404。
    vars['contractId'] = 'ce86abb3-3181-40e8-86e6-adaf06e91aa9'
    # step 3: update contract - reactive the subscription
    _resp3 = ctx.api.users.self_contracts_by_contract_id(body='{\r\n    "contractId": "{{contractId}}",\r\n    "status": "NORMAL"\r\n}', token='linda10_token')
    # assertion 3.assertion: responseJson equal NORMAL
    expect(_resp3).json('$.data.status').equals('NORMAL')
    # assertion 3.assertion: responseJson equal {{contractId}}
    expect(_resp3).json('$.data.id').equals(ctx.render_text('{{contractId}}'))
    vars['subscriptionPlanOptionId'] = '4965c739-adc4-4a2a-a803-74283126837d'
    # 注意：Apifox 原文此处对 contractId 的重新赋值是 `//` 注释掉的，
    # 即 step3/4/5 沿用 step2 的 ce86abb3；迁移器误把注释当有效代码，
    # 取了另一个已不存在的合约 → 404。
    vars['contractId'] = 'ce86abb3-3181-40e8-86e6-adaf06e91aa9'
    # step 4: update contract - Cancel the subscription
    _resp4 = ctx.api.users.self_contracts_by_contract_id(body='{\r\n    "contractId": "{{contractId}}",\r\n    "status": "CANCELED"\r\n}', token='linda10_token')
    # assertion 4.assertion: responseJson equal CANCELED
    expect(_resp4).json('$.data.status').equals('CANCELED')
    # assertion 4.assertion: responseJson equal {{contractId}}
    expect(_resp4).json('$.data.id').equals(ctx.render_text('{{contractId}}'))
