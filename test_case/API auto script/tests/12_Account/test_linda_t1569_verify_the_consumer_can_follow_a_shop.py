"""Migrated from Apifox case #5815402. Source folder: Account."""
# Apifox Case ID: 5815402  (traceability only — not needed to run)
NAME = "Verify the consumer can follow a shop"
TAGS = ["p0", "account", "suite:linda"]
PRIORITY = 0


CASE_ID = 5815402
ENV_NAME = "Release"

# --- step 1: cf2d2348-42de-4581-a164-f1b242383c21 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "subscribe done", "path": "$.data", "multipleValue": [], "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: d1b034f7-0547-4480-ad5f-ccdf00833e22 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "subscribe done", "path": "$.data", "multipleValue": [], "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_linda_t1569_verify_the_consumer_can_follow_a_shop(ctx):
    """Apifox case #5815402: Linda_T1569_Verify_the_consumer_can_follow_a_shop"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: cf2d2348-42de-4581-a164-f1b242383c21
    _resp1 = ctx.api.promoters.create(body='{\r\n    "promoterId": "7bc6ed8d-51de-446b-8c64-fd321cf1a45d",\r\n    "smsSubscribe": true,\r\n    "emailSubscribe": true\r\n}', token='linda10_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal subscribe done
    expect(_resp1).json('$.data').equals('subscribe done')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # step 2: d1b034f7-0547-4480-ad5f-ccdf00833e22
    _resp2 = ctx.api.promoters.create(body='{\r\n    "promoterId": "7bc6ed8d-51de-446b-8c64-fd321cf1a45d",\r\n    "smsSubscribe": false,\r\n    "emailSubscribe": false\r\n}', token='linda10_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal subscribe done
    expect(_resp2).json('$.data').equals('subscribe done')
