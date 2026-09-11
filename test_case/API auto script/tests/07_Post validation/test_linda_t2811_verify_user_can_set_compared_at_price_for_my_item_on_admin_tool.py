"""Migrated from Apifox case #6111088. Source folder: Post validation."""
# Apifox Case ID: 6111088  (traceability only — not needed to run)
NAME = "Verify user can set compared at price for my item on admin tool"
TAGS = ["p0", "post_validation", "suite:linda"]
PRIORITY = 0


CASE_ID = 6111088
ENV_NAME = "Release"

# --- step 1: Get Partner linda00 token ---
# post[extractor]: {"variableName": "linda00_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: 1df491e4-654f-4bca-9fed-758dbdaf74da ---
# pre: pm.environment.set("productId","af691383-afcd-48b5-b9ae-792c6ca12021");
# pre: pm.environment.set("VariantsId", "b52f488d-1c5f-4b9a-a252-ec0e5a3b7c30");
# pre: 
# pre: 
# pre: // 生成一个 100 到 999 之间的随机整数
# pre: var CompareAtPrice = Math.floor(100 + Math.random() * 900);
# pre: 
# pre: // 设置环境变量
# pre: pm.environment.set("CompareAtPrice", CompareAtPrice);
# pre: 
# pre: // 打印变量值
# pre: console.log("CompareAtPrice is", CompareAtPrice);
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: Check the compate-at-price sync to the catalog ---
# pre: pm.environment.set("merchantProductName", "PlayTime SuperSocks");
# pre: pm.environment.set("merchantId", "7c2db5d2-92f0-4090-a1ef-55a811b12a6f");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{CompareAtPrice}}", "path": "$.data.items[0].priceDisplayAnchor", "multipleValue": [], "extractSettings": {"expression": "$.data.items[0].priceDisplayAnchor", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect
import random as _random

def test_linda_t2811_verify_user_can_set_compared_at_price_for_my_item_on_admin_tool(ctx):
    """Apifox case #6111088: Linda_T2811_Verify_user_can_set_compared_at_price_for_my_item_on_admin_tool"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda00 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+00@1m.app"\n}', app_headers=True)
    # extractor: linda00_token = $.data.token
    ctx.extract('linda00_token', _resp1, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    # step 2 前置脚本（迁移时被丢弃的计算式）：
    #   var CompareAtPrice = Math.floor(100 + Math.random() * 900);
    #   pm.environment.set("CompareAtPrice", CompareAtPrice);
    # 缺失时 {{CompareAtPrice}} 渲染为空 -> priceAnchor 为空，断言比对失败。
    vars['CompareAtPrice'] = _random.randint(100, 999)
    # step 2: 1df491e4-654f-4bca-9fed-758dbdaf74da
    _resp2 = ctx.api.admin.merchant_product_by_product_id(body='{\r\n    "variants": [\r\n        {\r\n            "priceAnchor": "{{CompareAtPrice}}",\r\n            "title": "Default Title",\r\n            "id": "{{VariantsId}}",\r\n            "option": {\r\n                "option1": "Default Title",\r\n                "option2": null,\r\n                "option3": null\r\n            }\r\n        }\r\n    ]\r\n}', token='admin_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3 前置脚本同样被丢弃：
    #   pm.environment.set("merchantProductName", "PlayTime SuperSocks");
    #   pm.environment.set("merchantId", "7c2db5d2-92f0-4090-a1ef-55a811b12a6f");
    # 注意 merchantId 与 step1 后置脚本的 822a3e59-... 不同，此处是 step3 的取值。
    vars['merchantProductName'] = 'PlayTime SuperSocks'
    vars['merchantId'] = '7c2db5d2-92f0-4090-a1ef-55a811b12a6f'
    # step 3: Check the compate-at-price sync to the catalog
    _resp3 = ctx.api.products.list(token='linda00_token', params={'keyword': '{{merchantProductName}}', 'sortCreatedAt': 'desc', 'merchantId': '{{merchantId}}', 'status[]': ['ACTIVE', 'DRAFT'], 'pageSize': '50', 'pageNumber': '1'})
    # assertion 3.assertion: responseJson equal {{CompareAtPrice}}
    expect(_resp3).json('$.data.items[0].priceDisplayAnchor').equals(ctx.render_text('{{CompareAtPrice}}'))
