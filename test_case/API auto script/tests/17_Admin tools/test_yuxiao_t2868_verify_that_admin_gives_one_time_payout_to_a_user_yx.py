"""Migrated from Apifox case #5767709. Source folder: Admin tools."""
# Apifox Case ID: 5767709  (traceability only — not needed to run)
NAME = "Verify that admin gives one time payout to a user-yx"
TAGS = ["p0", "admin_tools", "suite:linda"]
PRIORITY = 0


CASE_ID = 5767709
ENV_NAME = "Release"

# --- step 1: 48d86b1b-5482-4a04-98c5-650b9e4af40f ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: e9509f91-78ff-42ae-b43b-a4326237cf32 ---
# pre: var rewarddata_id = pm.environment.get("rewarddata_id");
# pre: var newpayoutBalance = pm.environment.get("payoutBalance");
# pre: console.log(rewarddata_id, newpayoutBalance)
# pre: var promoterId = pm.environment.get("promoterId");
# post[assertion]: {"name": "检查rewarddata_rewardBalance", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.items[0].payoutBalance", "multipleValue": [], "extractSettings": {"expression": "$.data.items[0].payoutBalance", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{promoterId}}", "path": "$.data.items[0].promoterId", "multipleValue": [], "extractSettings": {"expression": "$.data.items[0].promoterId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_yuxiao_t2868_verify_that_admin_gives_one_time_payout_to_a_user_yx(ctx):
    """Apifox case #5767709: Yuxiao_T2868_Verify_that_admin_gives_one_time_payout_to_a_user_yx"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # mirror Apifox PRE customScript fallback: when promoterId is missing/too short,
    # force a known-good promoter UUID (original used a DB pre-processor + this fallback).
    if not vars.get('promoterId') or len(str(vars.get('promoterId'))) < 10:
        vars['promoterId'] = '2e7c410d-3aeb-429c-bdcf-b0c769a1e11e'
    # === Steps ===
    # step 1: 48d86b1b-5482-4a04-98c5-650b9e4af40f
    _resp1 = ctx.api.admin.promoters_reward(body='{\r\n    "amount": 10,\r\n    "holdTime": 0,\r\n    "reason": "One-off payout - loan",\r\n    "note": "21+",\r\n    "memo": "Auto test",\r\n    "type": "ONE_TIME_PAYOUT_LOAN",\r\n    "promoterId": "{{promoterId}}"\r\n}', token='admin_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # step 2: e9509f91-78ff-42ae-b43b-a4326237cf32
    _resp2 = ctx.api.admin.promoters_reward_by_promoter_id(body=None, params={'pageNumber': '1', 'pageSize': '10'}, token='admin_token')
    # assertion 2.检查rewarddata_rewardBalance: responseJson equal 0
    expect(_resp2).json('$.data.items[0].payoutBalance').equals('0')
    # assertion 2.assertion: responseJson equal {{promoterId}}
    expect(_resp2).json('$.data.items[0].promoterId').equals(str(vars.get('promoterId')))
