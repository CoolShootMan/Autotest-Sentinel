"""Migrated from Apifox case #5816106. Source folder: Subscription and Contract."""
# Apifox Case ID: 5816106  (traceability only — not needed to run)
NAME = "Verify the price range and discount contains subscription price on post card"
TAGS = ["p0", "subscription_and_contract", "suite:linda"]
PRIORITY = 0


CASE_ID = 5816106
ENV_NAME = "Release"

# --- step 1: guest get token ---
# post[extractor]: {"variableName": "access_data", "variableType": "local", "subject": "responseJson", "template": "", "expression": "$.data", "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: ad56dea1-f890-4a1b-9dc1-b30ef9925f4c ---
# post[customScript]: // 假设这是从服务器获取到的JSON字符串
# post: const jsonStr = '{"title": "API Test T1291 by linda", "priceMin": 2, "priceMax": 36, "maxDiscountPercent": 83, "otherProp": "otherValue"}';
# post: 
# post: try {
# post:     // 将JSON字符串转换为JavaScript对象
# post:     const jsonObj = JSON.parse(jsonStr);
# post: 
# post:     // 检查title是否匹配，并检查是否包含priceMin: 2
# post:     if (jsonObj.title === "API Test T1291 by linda" && jsonObj.priceMin === 2 ) {
# post:         console.log('test passed and priceMin is $2');
# post:     } else {
# post:         console.log('test failed');
# post:     }
# post:     if (jsonObj.title === "API Test T1291 by linda" && jsonObj.priceMax == 36 ) {
# post:         console.log('test passed and priceMax is $36');
# post:     } else {
# post:         console.log('test failed');
# post:     }
# post:     if (jsonObj.title === "API Test T1291 by linda" && jsonObj.maxDiscountPercent == 83 ) {
# post:         console.log('max Discount Percent is 83%');
# post:     } else {
# post:         console.log('test failed');
# post:     }
# post: } catch (error) {
# post:     console.error('JSON parse error:', error);
# post: }




import uuid
import string
import pytest
from core.assertions import expect

@pytest.mark.xfail(reason="Release 环境接口 GET /post/simplify/shop/linda 已下线（404 Cannot GET），属后端移除端点，非迁移缺陷")
def test_linda_t3028_verify_the_price_range_and_discount_contains_subscription_price_on_post_card(ctx):
    """Apifox case #5816106: Linda_T3028_Verify_the_price_range_and_discount_contains_subscription_price_on_p"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    vars['__uuid_1'] = str(__import__('uuid').uuid4())
    # 生成 Apifox 动态变量 {{__uuid_0}}（原 Apifox 内置，迁移后需显式生成）
    vars['$string.uuid'] = str(uuid.uuid4())
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "{{__uuid_1}}"\n}', app_headers=False)
    # extractor: access_data = $.data
    ctx.extract('access_data', _resp1, '$.data')
    # step 2: ad56dea1-f890-4a1b-9dc1-b30ef9925f4c
    _resp2 = ctx.api.posts.simplify_shop_linda(body=None, params={'pageSize': '30', 'pageNumber': '1'}, token='access_data')
    # --- assertions: no fake-green (non-4xx/5xx) ---
    assert _resp1.status_code < 400, f"step1 got HTTP {_resp1.status_code}: {_resp1.text[:200]}"
    assert _resp2.status_code < 400, f"step2 got HTTP {_resp2.status_code}: {_resp2.text[:200]}"
