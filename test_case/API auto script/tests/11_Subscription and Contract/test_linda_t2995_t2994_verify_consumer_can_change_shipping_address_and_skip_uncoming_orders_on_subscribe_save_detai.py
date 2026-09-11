"""Migrated from Apifox case #6108487. Source folder: Subscription and Contract."""
# Apifox Case ID: 6108487  (traceability only — not needed to run)
NAME = "&T2994 Verify consumer can change shipping address and Skip uncoming orders on subscribe & save details page"
TAGS = ["p0", "subscription_and_contract", "suite:linda"]
PRIORITY = 0


CASE_ID = 6108487
ENV_NAME = "Release"

# --- step 1: get address list ---
# post[customScript]: // 1. 【修正】Apifox中获取响应数据的正确方式是 pm.response.json()
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 获取 items 数组（存储地址数据的数组）
# post: const items = responseData.data?.items || [];
# post: 
# post: // 3. 检查数组长度是否至少有2条数据
# post: if (items.length < 2) {
# post:   console.error("错误：地址数据不足2条，无法提取两个不同的id");
# post: } else {
# post:   // 4. 生成两个不重复的随机索引
# post:   const len = items.length;
# post:   let index1 = Math.floor(Math.random() * len);
# post:   let index2;
# post:   do {
# post:     index2 = Math.floor(Math.random() * len);
# post:   } while (index2 === index1); // 确保两个索引不同
# post: 
# post:   // 5. 提取对应的id
# post:   const oldAddressId = items[index1].id;
# post:   const newAddressId = items[index2].id;
# post: 
# post:   // 6. 设置为环境变量
# post:   pm.environment.set("oldAddressId", oldAddressId);
# post:   pm.environment.set("newAddressId", newAddressId);
# post: 
# post:   // 打印日志确认
# post:   console.log("已提取并设置环境变量：");
# post:   console.log("oldAddressId =", oldAddressId);
# post:   console.log("newAddressId =", newAddressId);
# post: }
# --- step 2: 08c30916-bf6e-4f92-b77f-dd836d485c78 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: post detail ---
# post[extractor]: {"variableName": "promoterProductVariantId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[0].variants[0].id", "extractSettings": {"expression": "$.data.relatedProducts[0].variants[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "subscriptionPlanOptionid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId", "extractSettings": {"expression": "$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "postid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: buy now ---
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "144.99", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "order_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderId", "extractSettings": {"expression": "$.data.orderId", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: create Order ---
# pre: var order_id = pm.environment.get("order_id");
# pre: console.log(order_id)
# pre: 
# pre: // pm.environment.set("old_shippingAddressId", "b7a5386c-8b15-4237-91f6-db20a9b37dfc");
# pre: 
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "exists", "value": "", "path": "$.data.orderNumbers[0]", "multipleValue": [], "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "orderNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.orderNumbers[0]", "extractSettings": {"expression": "$.data.orderNumbers[0]", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: check the price is subscription price- consumer order detail ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "144.99", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "60", "path": "$.data.totalLineItemSubscriptionDiscount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalLineItemSubscriptionDiscount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
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
# --- step 8: check the new contract details ---
# post[extractor]: {"variableName": "contractNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.contractNumber", "extractSettings": {"expression": "$.data.contractNumber", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{contractNumber}}", "path": "$.data.contractNumber", "multipleValue": [], "extractSettings": {"expression": "$.data.contractNumber", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "upcomingOrderId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.upcomingOrderDates[0].id", "extractSettings": {"expression": "$.data.upcomingOrderDates[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: Check the shipping address is old - check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "140", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "60", "path": "$.data.lineItems[0].lineItemDiscount", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].lineItemDiscount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "132.67", "path": "$.data.totalPayoutToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalPayoutToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{oldAddressId}}", "path": "$.data.shippingAddress.id", "multipleValue": [], "extractSettings": {"expression": "$.data.shippingAddress.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: Consumer update contract shipping address ---
# pre: // pm.environment.set("new_shippingAddressId", "64e69349-d46d-4886-b70d-700a95d20200");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{newAddressId}}", "path": "$.data.shippingAddress.id", "multipleValue": [], "extractSettings": {"expression": "$.data.shippingAddress.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: Skipped -  update contract order ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "SKIPPED", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import random
import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_linda_t2995_t2994_verify_consumer_can_change_shipping_address_and_skip_uncoming_orders_on_subscribe_save_detai(ctx):
    """Apifox case #6108487: Linda_T2995_T2994_Verify_consumer_can_change_shipping_address_and_Skip_uncoming_"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: get address list
    _resp1 = ctx.api.address.list(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    _j = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    if _arr:
        vars['oldAddressId'] = random.choice(_arr).get('id')
    _j = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    if _arr:
        vars['newAddressId'] = random.choice(_arr).get('id')
    # step 2: 08c30916-bf6e-4f92-b77f-dd836d485c78
    _resp2 = ctx.api.cart.delete(body='{}', app_headers=True, token='linda10_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3: post detail
    _resp3 = ctx.api.posts.consumer_detail(token='linda10_token', params={'urlAlias': 't3041', 'vanityUrl': 'linda'})
    # extractor: promoterProductVariantId = $.data.relatedProducts[0].variants[0].id
    ctx.extract('promoterProductVariantId', _resp3, '$.data.relatedProducts[0].variants[0].id')
    # extractor: subscriptionPlanOptionid = $.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId
    ctx.extract('subscriptionPlanOptionid', _resp3, '$.data.relatedProducts[0].variants[0].subscriptionPlanOptionPrices[0].optionId')
    # extractor: postid = $.data.id
    ctx.extract('postid', _resp3, '$.data.id')
    # step 4: buy now
    _resp4 = ctx.api.orders.buy_now(body='{\n  "updateCartItems": [\n    {\n    "quantity": 1,\n    "promoterProductVariantId": "{{promoterProductVariantId}}",\n    "price": 200,\n    "postId": "{{postid}}",\n    "selected": true,\n    "subscriptionPlanOptionId": "{{subscriptionPlanOptionid}}"\n  }\n  ],\n  "currentUpdateCartItems":[\n     {\n    "quantity": 1,\n    "id": "{{promoterProductVariantId}}",\n    "postId": "{{postid}}",\n    "price": 200\n  }\n  ]\n}\n\n\n\n\n', app_headers=True, token='linda10_token')
    # assertion 4.assertion: responseJson equal 144.99
    expect(_resp4).json('$.data.totalToPay').equals('144.99')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp4, '$.data.orderId')
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 140,\n      "promoterVariantId": "{{promoterProductVariantId}}"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "linda.zhou.ext+10@1m.app"\n  },\n  "shippingAddressId": "{{oldAddressId}}"\n}', app_headers=True, token='linda10_token', params={'order_id': '{{order_id}}'})
    # assertion 5.code: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson exists 
    expect(_resp5).json('$.data.orderNumbers[0]').exists()
    # extractor: orderNumber = $.data.orderNumbers[0]
    ctx.extract('orderNumber', _resp5, '$.data.orderNumbers[0]')
    # step 6: check the price is subscription price- consumer order detail
    _resp6 = ctx.api.orders.consumer_detail_by_order_number(app_headers=True, token='linda10_token')
    # assertion 6.assertion: responseJson equal UNFULFILLED
    expect(_resp6).json('$.data.lineItems[0].fulfillmentStatus').equals('UNFULFILLED')
    # assertion 6.assertion: responseJson equal 144.99
    expect(_resp6).json('$.data.totalToPay').equals('144.99')
    # assertion 6.assertion: responseJson equal 60
    expect(_resp6).json('$.data.totalLineItemSubscriptionDiscount').equals('60')
    # extractor: contractId = $.data.lineItems[0].contractId
    ctx.extract('contractId', _resp6, '$.data.lineItems[0].contractId')
    # step 7: check the new contract id generate
    _resp7 = ctx.api.users.self_contracts(token='linda10_token')
    # step 8: check the new contract details
    _resp8 = ctx.api.users.self_contracts_by_contract_id_2(token='linda10_token')
    _j = _resp7.json() if _resp8.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    _x = next((_z for _z in _arr if _z.get('id') == vars.get('contractId')), None)
    if _x: vars['contractNumber'] = _x.get('contractNumber')
    # assertion 8.assertion: responseJson equal {{contractNumber}}
    expect(_resp8).json('$.data.contractNumber').equals(ctx.render_text('{{contractNumber}}'))
    # extractor: upcomingOrderId = $.data.upcomingOrderDates[0].id
    ctx.extract('upcomingOrderId', _resp8, '$.data.upcomingOrderDates[0].id')
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 9: Check the shipping address is old - check merchant order detail
    _resp9 = ctx.api.orders.merchant_detail_v2(app_headers=True, token='linda00_token')
    # assertion 9.assertion: responseJson equal 200
    expect(_resp9).json('$.code').equals('200')
    # assertion 9.assertion: responseJson equal 140
    expect(_resp9).json('$.data.totalCommissionSubtotal').equals('140')
    # assertion 9.assertion: responseJson equal UNFULFILLED
    expect(_resp9).json('$.data.lineItems[0].fulfillmentStatus').equals('UNFULFILLED')
    # assertion 9.assertion: responseJson equal 60
    expect(_resp9).json('$.data.lineItems[0].lineItemDiscount').equals('60')
    # assertion 9.assertion: responseJson equal 132.67
    expect(_resp9).json('$.data.totalPayoutToPay').equals('132.67')
    # assertion 9.assertion: responseJson equal {{oldAddressId}}
    expect(_resp9).json('$.data.shippingAddress.id').equals(ctx.render_text('{{oldAddressId}}'))
    # step 10: Consumer update contract shipping address
    _resp10 = ctx.api.users.self_contracts_by_contract_id(body='{\r\n    "contractId": "{{contractId}}",\r\n    "addressId": "{{newAddressId}}"\r\n}', app_headers=True, token='linda10_token')
    # assertion 10.assertion: responseJson equal {{newAddressId}}
    expect(_resp10).json('$.data.shippingAddress.id').equals(ctx.render_text('{{newAddressId}}'))
    # step 11: Skipped -  update contract order
    _resp11 = ctx.api.users.self_contracts_contract_orders_by_contract_order_id(body='{"status":"SKIPPED"}', token='linda10_token', contractOrderId=vars.get('upcomingOrderId'))
    # assertion 11.assertion: responseJson equal SKIPPED
    expect(_resp11).json('$.data.status').equals('SKIPPED')
