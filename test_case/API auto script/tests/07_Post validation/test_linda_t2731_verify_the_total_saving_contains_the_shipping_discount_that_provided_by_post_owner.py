"""Auto-generated from Apifox case #5800997. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 5800997
# Folder: 
# Case: (Linda)T2731 Verify the total saving contains the shipping discount that provided by post owner
# Priority: P0
# Created: 2025-01-08T09:11:02.000Z
# Updated: 2026-02-06T06:45:42.000Z


CASE_ID = 5800997
ENV_NAME = "Release"

# --- step 1: 34e3dfd9-5db3-48bf-b01e-d440c8be34a6 ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 2: buy now ---
# pre: // Pre-request Script
# pre: pm.environment.unset("order_id");
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "20", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: // buy now 接口的后置脚本
# post: const res = pm.response.json();
# post: if (res.data && res.data.orderId) {
# post:     // 使用 String() 强制转换，确保存入的是纯字符串
# post:     pm.environment.set("order_id", String(res.data.orderId));
# post:     console.log("Verified Order ID saved as string: " + res.data.orderId);
# post: }
# --- step 3: 2c078bbd-0029-462f-9f74-ef3cfb498c8e ---
# post[customScript]: // 1. 验证 HTTP 状态码是否为 200 (针对 400 报错进行拦截)
# post: pm.test("Status code is 201", function () {
# post:     pm.response.to.have.status(201);
# post: });
# post: 
# post: // 获取响应 JSON 数据
# post: const jsonData = pm.response.json();
# post: 
# post: /**
# post:  * 下面是针对你图片中要求的三个断言逻辑的 Postman 脚本实现
# post:  */
# post: 
# post: // 2. 断言 $.data.totalToPay 等于 20   no shipping
# post: pm.test("Verify totalToPay is 20.", function () {
# post:     pm.expect(jsonData.data.totalToPay).to.eql(20.);
# post: });
# post: 
# post: 





import json

from core.assertions import expect

def test__5800997__Linda_T2731_Verify_the_total_saving_contains_the_shipping_discount_that_provided_by_post_owner(ctx):
    """Apifox case #5800997: Linda_T2731_Verify_the_total_saving_contains_the_shipping_discount_that_provided"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: 34e3dfd9-5db3-48bf-b01e-d440c8be34a6
    _resp1 = ctx.api.auth.guest_login(body='{\r\n    "consumerId": "{{__uuid_0}}"\r\n}')
    vars['access_token'] = (_resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 2: buy now
    _resp2 = ctx.api.orders.buy_now(body='{\n  "updateCartItems": [\n    {\n      "quantity": 1,\n      "promoterProductVariantId": "380e9b2b-47f9-49e4-8a6f-504b655fb6cf",\n      "price": 20,\n      "postId": "cb9ffbf6-7d76-49f5-a009-891af45aeee5",\n      "selected": true,\n      "customFields": []\n    }\n  ],\n  "fbAdParams": {\n    "eventID": "80ed5e0c-5956-496d-b804-31b2cfd97865",\n    "pixelId": [\n      "147258369",\n      "8888888888",\n      "77777777777",\n      "666666666"\n    ],\n    "fbBrowserId": "fb.1.1768875803590.54427593028429772",\n    "externalId": "450bc2ab-5fcf-412d-a938-3f30e8fc8b9c",\n    "eventSourceUrl": "https://release.pear.us/linda/post/t2731"\n  },\n  "currentUpdateCartItems": [\n    {\n      "quantity": 1,\n      "id": "380e9b2b-47f9-49e4-8a6f-504b655fb6cf",\n      "postId": "cb9ffbf6-7d76-49f5-a009-891af45aeee5",\n      "price": 20,\n      "customFields": []\n    }\n  ]\n}', token='access_token')
    # assertion 2.assertion: responseJson equal 20
    expect(_resp2).json('$.data.totalToPay').equals('20')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp2, '$.data.orderId')
    # order_id 已由上方 extractor 提取
    # step 3: 2c078bbd-0029-462f-9f74-ef3cfb498c8e
    _resp3 = ctx.api.orders.checkout(body='{}', app_headers=True, params={'fbAdParams[eventID\\]': 'b960373e-2266-40ec-a22f-0831aef7593e'})
