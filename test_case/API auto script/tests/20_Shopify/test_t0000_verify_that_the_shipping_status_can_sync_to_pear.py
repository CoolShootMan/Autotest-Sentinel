"""Migrated from Apifox case #8287376. Source folder: Shopify."""
# Apifox Case ID: 8287376  (traceability only — not needed to run)
NAME = "T0000 Verify that the shipping status can sync to pear"
TAGS = ["p2", "shopify", "suite:linda"]
PRIORITY = 2


CASE_ID = 8287376
ENV_NAME = "Release"

# --- step 1: Get Partner linda00 token ---
# post[extractor]: {"variableName": "linda00_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: 785e35bb-0db7-41e4-adce-b39b0f3a08ba ---
# pre: pm.environment.set("merchantId", "d1fdc475-8b15-49f0-8718-67c9efa988bf");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_t0000_verify_that_the_shipping_status_can_sync_to_pear(ctx):
    """Apifox case #8287376: T0000_Verify_that_the_shipping_status_can_sync_to_pear"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda00 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+00@1m.app"\n}', app_headers=True)
    # extractor: linda00_token = $.data.token
    ctx.extract('linda00_token', _resp1, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    # step 2: 785e35bb-0db7-41e4-adce-b39b0f3a08ba
    _resp2 = ctx.api.merchants.v_822a3e59_fdf3_4d9b_be57_f8f0b3af1023_sync_shopify_shipping(body=None, token='linda00_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
