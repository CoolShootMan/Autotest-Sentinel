"""Auto-generated from Apifox case #5808749. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 5808749
# Folder: 
# Case: (Linda)T1058 Verify the $4.99 or free shipping fee is consisntence on the checkout page
# Priority: P1
# Created: 2025-01-09T08:59:13.000Z
# Updated: 2026-08-11T03:50:15.000Z


CASE_ID = 5808749
ENV_NAME = "Release"

# --- step 1: guest get token ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "access_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data", "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: get Cart ---
# post[customScript]: // 1. 获取当前接口返回的购物车数据
# post: const responseData = pm.response.json(); 
# post: 
# post: // 2. 初始化批量清空的参数数组
# post: const clearCartItems = [];
# post: 
# post: // 3. 遍历所有商品，构造批量删除的item（兼容空数据）
# post: if (responseData.data && responseData.data.items && responseData.data.items.length > 0) {
# post:     responseData.data.items.forEach(item => {
# post:         // 核心：quantity设为 -当前数量（原quantity是1则填-1）
# post:         clearCartItems.push({
# post:             id: item.id,  // 商品ID
# post:             quantity: -item.quantity,  // 负数表示清空该商品
# post:             promoterProductVariantId: item.variant.promoterVariantId, // 变体ID（从variant中提取）
# post:             price: Number(item.variant.price), // 价格（转数字，原是字符串）
# post:             postId: item.postId, // 帖子ID
# post:             selected: item.selected // 选中状态
# post:         });
# post:     });
# post: }
# post: 
# post: // 4. 构造最终的批量清空参数（外层包items和lite）
# post: const clearCartParams = {
# post:     items: clearCartItems,
# post:     lite: false
# post: };
# post: 
# post: // 5. 存入APIFOX全局变量（供后续清空接口调用）
# post: pm.globals.set("clearCartParams", JSON.stringify(clearCartParams));
# post: 
# post: // 【可选】打印日志验证结果（APIFOX控制台查看）
# post: console.log("批量清空购物车参数：", clearCartParams);
# --- step 3: Clean Cart ---
# pre: // 1. 从全局变量取出之前存储的清空参数（兼容空值）
# pre: const clearCartParams = JSON.parse(pm.globals.get("clearCartParams") || '{"items": [], "lite":false}');
# pre: 
# pre: // 2. 【可选】动态调整参数（比如过滤掉selected=false的商品、修改quantity等）
# pre: clearCartParams.items = clearCartParams.items.map(item => {
# pre:     // 示例：强制quantity为-1（不管原数量）
# pre:     return {...item, quantity: -1};
# pre: });
# pre: 
# pre: // 3. 将调整后的参数存入临时变量（供请求体引用）
# pre: pm.variables.set("dynamicClearCartParams", JSON.stringify(clearCartParams));
# pre: 
# pre: // 【可选】打印日志验证
# pre: console.log("动态调整后的清空参数：", clearCartParams);
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "isEmpty", "value": "", "path": "$.data.items", "multipleValue": [], "extractSettings": {"expression": "$.data.items", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: Add item with shipping fee Fee to Cart ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.data.items[0].variant.price", "multipleValue": [], "extractSettings": {"expression": "$.data.items[0].variant.price", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: Add item with shipping fee $4.99 to Cart ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.data.items[1].variant.price", "multipleValue": [], "extractSettings": {"expression": "$.data.items[1].variant.price", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.data.items[0].variant.price", "multipleValue": [], "extractSettings": {"expression": "$.data.items[0].variant.price", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: Checkout ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "604.99", "path": "$.data.totalToPay", "multipleValue": [], "extractSettings": {"expression": "$.data.totalToPay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





import json

from core.assertions import expect

def test__5808749__Linda_T1058_Verify_the_4_99_or_free_shipping_fee_is_consisntence_on_the_checkout_page(ctx):
    """Apifox case #5808749: Linda_T1058_Verify_the_4_99_or_free_shipping_fee_is_consisntence_on_the_checkout"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "{{__uuid_0}}"\n}', app_headers=False)
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # extractor: access_token = $.data
    ctx.extract('access_token', _resp1, '$.data')
    # step 2: get Cart
    _resp2 = ctx.api.cart.list(token='access_token')
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    _cartItems = (_j2.get('data') or {}).get('items') or []
    _clearItems = []
    for _it in _cartItems:
        _var = _it.get('variant') or {}
        _clearItems.append({
            'id': _it.get('id'),
            'quantity': -1,
            'promoterProductVariantId': _var.get('promoterVariantId'),
            'price': float(_var.get('price') or 0),
            'postId': _it.get('postId'),
            'selected': _it.get('selected')
        })
    vars['dynamicClearCartParams'] = json.dumps({'items': _clearItems, 'lite': False})
    # step 3: Clean Cart
    _resp3 = ctx.api.cart.update(body='{{dynamicClearCartParams}}', token='access_token')
    # assertion 3.assertion: responseJson isEmpty 
    expect(_resp3).json('$.data.items').is_empty()
    # step 4: Add item with shipping fee Fee to Cart
    _resp4 = ctx.api.cart.update(body='{\n    "currentUpdateCartItem": [{\n        "quantity": 1,\n        "id": "be267fed-b034-49ae-a902-569ee2b2fcbf",\n        "postId": "d7bd9117-796d-4f4f-b251-1795447b66aa",\n        "price": 200\n    }\n    ],\n    "items": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "be267fed-b034-49ae-a902-569ee2b2fcbf",\n            "price": 200,\n            "postId": "d7bd9117-796d-4f4f-b251-1795447b66aa"\n        }\n    ],\n    "lite": true\n}', token='access_token')
    # assertion 4.assertion: responseJson equal 200
    expect(_resp4).json('$.data.items[0].variant.price').equals('200')
    # step 5: Add item with shipping fee $4.99 to Cart
    _resp5 = ctx.api.cart.update(body='{\n    "currentUpdateCartItem": [{\n        "quantity": 1,\n        "id": "4cd483cd-60ae-4e40-886b-35c6e7fd8477",\n        "postId": "d7bd9117-796d-4f4f-b251-1795447b66aa",\n        "price": 200\n    }\n    ],\n    "items": [\n        {\n            "promoterProductVariantId": "be267fed-b034-49ae-a902-569ee2b2fcbf",\n            "price": 200,\n            "quantity": 1,\n            "postId": "d7bd9117-796d-4f4f-b251-1795447b66aa",\n            "selected": true,\n            "subscriptionPlanOptionId": null\n        },\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "4cd483cd-60ae-4e40-886b-35c6e7fd8477",\n            "price": 200,\n            "postId": "d7bd9117-796d-4f4f-b251-1795447b66aa"\n        }\n    ],\n    "lite": true\n}', token='access_token')
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.data.items[1].variant.price').equals('200')
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.data.items[0].variant.price').equals('200')
    # step 6: Checkout
    _resp6 = ctx.api.orders.checkout(body='{}', token='access_token')
    # assertion 6.assertion: responseJson equal 604.99
    expect(_resp6).json('$.data.totalToPay').equals('604.99')
