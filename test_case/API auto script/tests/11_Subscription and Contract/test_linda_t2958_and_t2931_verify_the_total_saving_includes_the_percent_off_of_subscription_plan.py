"""Migrated from Apifox case #5827160. Source folder: Subscription and Contract."""
# Apifox Case ID: 5827160  (traceability only — not needed to run)
NAME = "and &T2931 Verify the total saving includes the percent off of subscription plan"
TAGS = ["p0", "subscription_and_contract", "suite:linda"]
PRIORITY = 0


CASE_ID = 5827160
ENV_NAME = "Release"

# --- step 1: Get consumer linda10 token ---
# post[extractor]: {"variableName": "linda10_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: get address list ---
# post[customScript]: // 1. 获取接口返回的JSON数据
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 初始化地址ID变量（默认空值）
# post: let addressId = "";
# post: 
# post: // 3. 提取有效ID（优先默认地址，无则取第一个）
# post: if (responseData.data && responseData.data.items && responseData.data.items.length > 0) {
# post:     // 先找isDefault=true的默认地址
# post:     const defaultAddress = responseData.data.items.find(item => item.isDefault === true);
# post:     if (defaultAddress) {
# post:         addressId = defaultAddress.id;
# post:     } else {
# post:         // 无默认地址则取第一个地址的ID
# post:         addressId = responseData.data.items[0].id;
# post:     }
# post: }
# post: 
# post: // 4. 存入APIFOX全局变量（供下单接口引用）
# post: pm.globals.set("addressId", addressId)
# post: 
# post: // 【可选】打印日志验证（APIFOX控制台查看）
# post: console.log("提取的有效地址ID：", addressId);
# --- step 3: b774ddef-e7b8-4cac-9acd-54bebe6f7b4a ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: buy now ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "90", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: 
# pre: console.log(order_id)
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: check the price is subscription price- consumer order detail ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "90", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "10", "path": "$.data.totalLineItemSubscriptionDiscount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalLineItemSubscriptionDiscount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "contractId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineItems[0].contractId", "extractSettings": {"expression": "$.data.lineItems[0].contractId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: check the new contract id generate ---
# post[customScript]: // 获取接口返回的JSON数据
# post: const responseJson = pm.response.json();
# post: // 从返回数据的结构中获取到包含具体数据项的数组（根据你提供的JSON结构来提取）
# post: const items = responseJson.data.items;
# post: // 定义要查找的目标id
# post: const targetId = pm.environment.get("contractId");
# post: 
# post: console.log('contractId is ' + targetId)
# post: // 使用some方法遍历数组检查是否存在指定id的对象
# post: const found = items.some(item => item.id === targetId);
# post: if (found) {
# post:     console.log(`Find the contract id contains ${targetId}`);
# post:     const targetObject = items.find(item => item.id === targetId);
# post:     const contractNumber = targetObject.contractNumber;
# post:     console.log(`对应的contractNumber为：${contractNumber}`);
# post:     // 将获取到的contractNumber设置为全局变量，方便后续其他地方使用
# post:     pm.globals.set("contractNumber", contractNumber);
# post: 
# post: } else {
# post:     console.log(`Failed Find the contract id contains${targetId}`);
# post:     throw new Error(`Failed Find the contract id contains${targetId}`);
# post: 
# post: }
# post[extractor]: {"variableName": "", "variableType": "local", "subject": "responseJson", "template": "", "expression": "", "extractSettings": {"expression": "", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: check the new contract details ---
# post[extractor]: {"variableName": "contractNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.contractNumber", "extractSettings": {"expression": "$.data.contractNumber", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{contractNumber}}", "path": "$.data.contractNumber", "multipleValue": [], "extractSettings": {"expression": "$.data.contractNumber", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: Get Partner linda00 token ---
# post[extractor]: {"variableName": "linda00_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 10: Check The free shipping discount should be deducted from merchant payout ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "90", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "10", "path": "$.data.lineItems[0].subscriptionDiscount", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].subscriptionDiscount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "82.35", "path": "$.data.totalPayoutToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalPayoutToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Check the merchant shipping is $0", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.totalShippingSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalShippingSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_linda_t2958_and_t2931_verify_the_total_saving_includes_the_percent_off_of_subscription_plan(ctx):
    """Apifox case #5827160: Linda_T2958_and_T2931_Verify_the_total_saving_includes_the_percent_off_of_subscr"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # 订阅商品 variant（与 step4 buy-now 一致，确保 create order 有有效 promoterVariantId）
    vars['promoterProductVariantId'] = vars.get('promoterProductVariantId') or '5ca78b54-d87f-4c14-aa74-88668900394c'
    # === Steps ===
    # step 1: Get consumer linda10 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "email": "linda.zhou.ext+10@1m.app",\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\n}', app_headers=True)
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp1, '$.data.token')
    # step 2: get address list
    _resp2 = ctx.api.address.list(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    # extract addressId (原始 Apifox step2 post-script: 取默认地址 id，无则取第一个)
    try:
        _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
        _addr_items = (_j2.get('data') or {}).get('items') or []
        vars['addressId'] = next((x['id'] for x in _addr_items if x.get('isDefault')), (_addr_items[0]['id'] if _addr_items else ''))
    except Exception: pass
    # step 3: b774ddef-e7b8-4cac-9acd-54bebe6f7b4a
    _resp3 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # step 4: buy now
    _resp4 = ctx.api.orders.buy_now(body='{\n  "updateCartItems": [\n    {\n    "quantity": 1,\n    "promoterProductVariantId": "5ca78b54-d87f-4c14-aa74-88668900394c",\n    "price": 100,\n    "postId": "954aafe6-5be9-4371-b539-88de05506048",\n    "selected": true,\n    "subscriptionPlanOptionId": "1006d7b6-7340-4ce1-9aaf-d51c1df22592"\n  }\n  ],\n  "currentUpdateCartItems": [\n    {\n    "quantity": 1,\n    "id": "5ca78b54-d87f-4c14-aa74-88668900394c",\n    "postId": "954aafe6-5be9-4371-b539-88de05506048",\n    "price": 100\n  }\n  ]\n}', app_headers=True, token='linda10_token')
    # assertion 4.assertion: responseJson equal 90
    expect(_resp4).json('$.data.totalToPay').equals('90')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp4, '$.data.orderId')
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 140,\n      "promoterVariantId": "{{promoterProductVariantId}}"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "linda.zhou.ext+10@1m.app"\n  },\n  "shippingAddressId": "{{addressId}}"\n}', app_headers=True, token='linda10_token', params={'order_id': '{{order_id}}'})
    # assertion 5.code: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson exists (Apifox "exists" 翻译为「字段存在且非空」)
    expect(_resp5).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp5, '$.data.orderNumbers[0]')
    # step 6: check the price is subscription price- consumer order detail
    _resp6 = ctx.api.orders.consumer_detail_by_order_number(app_headers=True, token='linda10_token')
    # assertion 6.assertion: responseJson equal UNFULFILLED
    expect(_resp6).json('$.data.lineItems[0].fulfillmentStatus').equals('UNFULFILLED')
    # assertion 6.assertion: responseJson equal 90
    expect(_resp6).json('$.data.totalToPay').equals('90')
    # assertion 6.assertion: responseJson equal 10
    expect(_resp6).json('$.data.totalLineItemSubscriptionDiscount').equals('10')
    # extractor: contractId = $.data.lineItems[0].contractId
    ctx.extract('contractId', _resp6, '$.data.lineItems[0].contractId')
    # step 7: check the new contract id generate
    _resp7 = ctx.api.users.self_contracts(token='linda10_token')
    # extractor:  = 
    # step 8: check the new contract details
    _resp8 = ctx.api.users.self_contracts_by_contract_id_2(token='linda10_token')
    _j = _resp7.json() if _resp8.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    _x = next((_z for _z in _arr if _z.get('id') == vars.get('contractId')), None)
    if _x: vars['contractNumber'] = _x.get('contractNumber')
    # assertion 8.assertion: responseJson equal {{contractNumber}}
    import sys
    print("DEBUG contractId=", vars.get('contractId'), "step8 url path ok", file=sys.stderr)
    expect(_resp8).json('$.data.contractNumber').equals(ctx.render_text('{{contractNumber}}'))
    # step 9: Get Partner linda00 token
    _resp9 = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+00@1m.app"\n}', app_headers=True)
    # extractor: linda00_token = $.data.token
    ctx.extract('linda00_token', _resp9, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 10: Check The free shipping discount should be deducted from merchant payout
    _resp10 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda00_token')
    # assertion 10.assertion: responseJson equal 200
    expect(_resp10).json('$.code').equals('200')
    # assertion 10.assertion: responseJson equal 90
    expect(_resp10).json('$.data.totalCommissionSubtotal').equals('90')
    # assertion 10.assertion: responseJson equal UNFULFILLED
    expect(_resp10).json('$.data.lineItems[0].fulfillmentStatus').equals('UNFULFILLED')
    # assertion 10.assertion: responseJson equal 10
    expect(_resp10).json('$.data.lineItems[0].subscriptionDiscount').equals('10')
    # assertion 10.assertion: responseJson equal 82.35
    expect(_resp10).json('$.data.totalPayoutToPay').equals('82.35')
    # assertion 10.Check the merchant shipping is $0: responseJson equal 0
    expect(_resp10).json('$.data.totalShippingSubtotal').equals('0')
