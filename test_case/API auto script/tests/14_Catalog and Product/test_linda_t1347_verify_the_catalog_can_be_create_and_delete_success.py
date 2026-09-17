"""Migrated from Apifox case #6112400. Source folder: Catalog and Product."""
# Apifox Case ID: 6112400  (traceability only — not needed to run)
NAME = "Verify the catalog can be create and delete success"
TAGS = ["p0", "catalog_and_product", "suite:linda"]
PRIORITY = 0


CASE_ID = 6112400
ENV_NAME = "Release"

# --- step 1: get merchant list ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: d9305e7c-e723-439d-b435-99f084ee810b ---
# pre: 
# pre: pm.environment.set("commissionRate", "25");
# pre: pm.environment.set("storeName", "API test by linda T1347");
# pre: pm.environment.set("isVisible", "true");
# pre: 
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{commissionRate}}", "path": "$.data.commissionRate", "multipleValue": [], "extractSettings": {"expression": "$.data.commissionRate", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{storeName}}", "path": "$.data.storeName", "multipleValue": [], "extractSettings": {"expression": "$.data.storeName", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "merchantId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: delete merchant - data recover ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t1347_verify_the_catalog_can_be_create_and_delete_success(ctx: "Context"):
    """Apifox case #6112400: Linda_T1347_Verify_the_catalog_can_be_create_and_delete_success"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: get merchant list
    _resp1 = ctx.api.merchants.list(token='merchant_token', params={'platform': 'PEAR'})
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # step 2: d9305e7c-e723-439d-b435-99f084ee810b
    # === pre-script（由 Apifox customScript 翻译）：设置创建 merchant 所需的参数 ===
    vars['commissionRate'] = "25"
    vars['storeName'] = "API test by linda T1347"
    vars['isVisible'] = "true"
    _resp2 = ctx.api.merchants.create(body={
        "commissionRate": "{{commissionRate}}",
        "storeName": "{{storeName}}",
        "isVisible": "{{isVisible}}",
    }, token='merchant_token')
    # assertion 2.assertion: responseJson equal {{commissionRate}}
    expect(_resp2).json('$.data.commissionRate').equals(ctx.render_text('{{commissionRate}}'))
    # assertion 2.assertion: responseJson equal {{storeName}}
    expect(_resp2).json('$.data.storeName').equals(ctx.render_text('{{storeName}}'))
    # extractor: merchantId = $.data.id
    ctx.extract('merchantId', _resp2, '$.data.id')
    # step 3: delete merchant - data recover
    _resp3 = ctx.api.merchants.by_merchant_id(token='merchant_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
