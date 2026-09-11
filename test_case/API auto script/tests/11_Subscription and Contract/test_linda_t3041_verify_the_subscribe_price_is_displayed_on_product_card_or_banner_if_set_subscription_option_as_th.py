"""Migrated from Apifox case #5827980. Source folder: Subscription and Contract."""
# Apifox Case ID: 5827980  (traceability only — not needed to run)
NAME = "Verify the subscribe price is displayed on product card or banner if set subscription option as the default purchase option -- With shipping fee"
TAGS = ["p0", "subscription_and_contract", "suite:linda"]
PRIORITY = 0


CASE_ID = 5827980
ENV_NAME = "Release"

# --- step 1: get address list ---
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
# --- step 2: ad955c67-d7e3-408d-9144-d81c0f03b595 ---
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
# pre: 
# pre: console.log(order_id)
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
# post[extractor]: {"variableName": "", "variableType": "local", "subject": "responseJson", "template": "", "expression": "", "extractSettings": {"expression": "", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: check the new contract details ---
# post[extractor]: {"variableName": "contractNumber", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.contractNumber", "extractSettings": {"expression": "$.data.contractNumber", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{contractNumber}}", "path": "$.data.contractNumber", "multipleValue": [], "extractSettings": {"expression": "$.data.contractNumber", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: Check price is subscription price - check merchant order detail ---
# pre: var merchant_token = pm.environment.get("merchant_token");
# pre: var orderNumber = pm.environment.get("orderNumber");
# pre: pm.variables.set("merchantId", "ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "140", "path": "$.data.totalCommissionSubtotal", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCommissionSubtotal", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "UNFULFILLED", "path": "$.data.lineItems[0].fulfillmentStatus", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].fulfillmentStatus", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "60", "path": "$.data.lineItems[0].lineItemDiscount", "multipleValue": [], "extractSettings": {"expression": "$.data.lineItems[0].lineItemDiscount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "132.67", "path": "$.data.totalPayoutToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalPayoutToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import json

from core.assertions import expect

from core.compat import get_path as _get_path

def test_linda_t3041_verify_the_subscribe_price_is_displayed_on_product_card_or_banner_if_set_subscription_option_as_th(ctx):
    """Apifox case #5827980: Linda_T3041_Verify_the_subscribe_price_is_displayed_on_product_card_or_banner_if"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: get address list
    _resp1 = ctx.api.address.list(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    # Apifox 后置脚本（迁移时被丢弃）：优先取默认地址，否则取第一个
    _items = _get_path(_resp1.json(), ['data', 'items']) or []
    _dft = next((_i for _i in _items if _i.get('isDefault') is True), None)
    vars['addressId'] = ((_dft or _items[0]).get('id', '') if _items else '')
    # step 2: ad955c67-d7e3-408d-9144-d81c0f03b595
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
    _resp4 = ctx.api.orders.buy_now(body='{\n  "updateCartItems": [\n    {\n    "quantity": 1,\n    "promoterProductVariantId": "{{promoterProductVariantId}}",\n    "price": 200,\n    "postId": "{{postid}}",\n    "selected": true,\n    "subscriptionPlanOptionId": "{{subscriptionPlanOptionid}}"\n  }\n  ],\n  "currentUpdateCartItems": [\n    {\n    "quantity": 1,\n    "id": "{{promoterProductVariantId}}",\n    "postId": "{{postid}}",\n    "price": 200\n  }\n  ]\n}', app_headers=True, token='linda10_token')
    # assertion 4.assertion: responseJson equal 144.99
    expect(_resp4).json('$.data.totalToPay').equals('144.99')
    # extractor: order_id = $.data.orderId
    ctx.extract('order_id', _resp4, '$.data.orderId')
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body='{\n  "lineItemsDTO": [\n    {\n      "quantity": 1,\n      "price": 140,\n      "promoterVariantId": "{{promoterProductVariantId}}"\n    }\n  ],\n  "id": "{{order_id}}",\n  "contact": {\n    "email": "linda.zhou.ext+10@1m.app"\n  },\n   "shippingAddressId": "{{addressId}}" \n}', app_headers=True, token='linda10_token', params={'order_id': '{{order_id}}'})
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
    # extractor:  = 
    # step 8: check the new contract details
    _resp8 = ctx.api.users.self_contracts_by_contract_id_2(token='linda10_token')
    _j = _resp7.json() if _resp8.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "items"]) or []
    _x = next((_z for _z in _arr if _z.get('id') == vars.get('contractId')), None)
    if _x: vars['contractNumber'] = _x.get('contractNumber')
    # assertion 8.assertion: responseJson equal {{contractNumber}}
    expect(_resp8).json('$.data.contractNumber').equals(ctx.render_text('{{contractNumber}}'))
    vars['merchantId'] = 'ece8c85b-29b8-4eed-8cfe-1f4d453ad2a4'
    # step 9: Check price is subscription price - check merchant order detail
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
