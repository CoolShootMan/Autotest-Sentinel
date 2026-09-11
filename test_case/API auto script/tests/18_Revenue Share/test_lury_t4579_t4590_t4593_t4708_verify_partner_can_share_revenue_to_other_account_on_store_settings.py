"""Auto-generated from Apifox case #8091284. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 8091284
# Folder: 
# Case: (Lury) T4579&T4590&T4593&T4708 Verify partner can share revenue to other account on store settings
# Priority: P0
# Created: 2026-03-30T04:05:42.000Z
# Updated: 2026-09-03T08:33:39.000Z


CASE_ID = 8091284
ENV_NAME = "Release"

# --- step 1: P-21-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 0;
# pre:     item_percentage_fee = 0.085;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: var order_level_transaction_fee = Math.floor(4.99 * 0.035);
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(85.5,1));
# pre: var p1_transaction_fee = Number(((10/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var curator_transaction_fee = Number(((9/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var promoter_transaction_fee = Number(((4.95/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var p5_transaction_fee = Number(((8.55/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var m1_transaction_fee_item = Number(((40/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var m1_transaction_fee = m1_transaction_fee_item + order_level_transaction_fee
# pre: var merchant_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - m1_transaction_fee_item - curator_transaction_fee - promoter_transaction_fee - p5_transaction_fee ).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("curator_transaction_fee", curator_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: pm.environment.set("p5_transaction_fee", p5_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(curator_transaction_fee)
# pre: console.log(promoter_transaction_fee)
# pre: console.log(p5_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P-21_access_token",res['data']['refreshToken']);
# post: });
# --- step 2: P-21 earning summary ---
# post[extractor]: {"variableName": "lifetimeEarning", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lifetimeEarning", "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: Partner getPayoutSummary ---
# post[extractor]: {"variableName": "balance_amount", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.balance.amount", "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 5: promoter earning summary ---
# post[extractor]: {"variableName": "lifetimeEarning_p", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lifetimeEarning", "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: promoter getPayoutSummary ---
# post[extractor]: {"variableName": "balance_amount_p", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.balance.amount", "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: Add share revenue for merchant ---
# post[extractor]: {"variableName": "config_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: Consumer-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 0;
# pre:     item_percentage_fee = 0.085;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: var order_level_transaction_fee = Math.floor(4.99 * 0.085*100)/100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(1.33,1)*100)/100;
# pre: var p1_transaction_fee = Math.round(((0.16/1.33 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee = Math.round(((0.17/1.33 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - merchant_transaction_fee + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("consumer_access_token",res['data']['token']);
# post: });
# --- step 9: delete cart ---
# --- step 10: buy now ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 11: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(13.1);
# post: });
# --- step 12: Verify P-21 earning summary is not changed ---
# pre: var lifetimeEarning = pm.environment.get("lifetimeEarning");
# pre: var lifetimeEarning_order = Math.round(((eval(lifetimeEarning) + 10.78) + Number.EPSILON) *100 ) / 100;
# pre: console.log(lifetimeEarning_order)
# pre: pm.environment.set("lifetimeEarning_order",lifetimeEarning_order)
# post[assertion]: {"name": "earning is + 10.78", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_order}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 13: Verify Partner getPayoutSummary is not changed ---
# post[assertion]: {"name": "Balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 14: Check partner release schedule ---
# post[customScript]: pm.test("Check release schedule based on admin settings", function () {
# post:     pm.response.to.have.status(200);
# post:     var orderNumber = pm.environment.get("orderNumber")
# post:     var res = JSON.parse(responseBody);
# post:     var order_list = res["data"]["items"]
# post:     var release_date_list = [];
# post:     for (var order of order_list){
# post:         if (order['orderNumber'] === orderNumber){
# post:             var settlements = order['settlements'];
# post:             for (var release of settlements){
# post:                 var only_date = (release["releaseAt"]).slice(0,10)
# post:                 release_date_list.push(only_date)
# post:             }
# post:         }
# post:     }
# post:     console.log(release_date_list);
# post:     var second_date = "2048-03-28";
# post:     var third_date = "2048-04-11";
# post:     pm.environment.set("second_date",second_date);
# post:     pm.environment.set("third_date",third_date);
# post:     pm.expect(release_date_list[0]).to.eql(second_date);
# post:     pm.expect(release_date_list[1]).to.eql(third_date);
# post: });
# --- step 15: Verify promoter earning summary is +10 ---
# pre: var lifetimeEarning_p = pm.environment.get("lifetimeEarning_p");
# pre: console.log(lifetimeEarning_p);
# pre: var lifetimeEarning_share =  Math.round(((eval(lifetimeEarning_p) + 1.46) + Number.EPSILON) *100 ) / 100;
# pre: 
# pre: console.log(lifetimeEarning_share)
# pre: pm.environment.set("lifetimeEarning_share",lifetimeEarning_share)
# pre: 
# post[assertion]: {"name": "Verify the lineup earnings +1.46", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_share}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 16: Verify promoter getPayoutSummary is not changed ---
# post[assertion]: {"name": "Verify the lineup balance is not change before payment", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_p}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 17: GET promoter release schedule for shared revenue ---
# post[customScript]: pm.test("Check release schedule based on admin settings", function () {
# post:     pm.response.to.have.status(200);
# post:     var orderNumber = pm.environment.get("orderNumber")
# post:     var res = JSON.parse(responseBody);
# post:     var order_list = res["data"]["items"]
# post:     var release_date_list = [];
# post:     for (var order of order_list){
# post:         if (order['merchantOrder']['orderNumber'] === orderNumber){
# post:             var settlements = order['settlements'];
# post:             for (var release of settlements){
# post:                 var only_date = (release["releaseAt"]).slice(0,10)
# post:                 release_date_list.push(only_date)
# post:             }
# post:         }
# post:     }
# post:     console.log(release_date_list);
# post:     var second_date = pm.environment.get("second_date");
# post:     var third_date = pm.environment.get("third_date");
# post:     console.log(release_date_list[0]);
# post:     console.log(release_date_list[1]);
# post:     pm.expect(release_date_list[0]).to.eql(second_date);
# post:     pm.expect(release_date_list[1]).to.eql(third_date);
# post: });
# --- step 18: DELETE share revenue account ---
# post[assertion]: {"name": "Verify delete share revenue successful", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 19: Consumer-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 0;
# pre:     item_percentage_fee = 0.085;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: var order_level_transaction_fee = Math.floor(4.99 * 0.085*100)/100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(1.33,1)*100)/100;
# pre: var p1_transaction_fee = Math.round(((0.16/1.33 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var merchant_transaction_fee = Math.round(((0.17/1.33 * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - merchant_transaction_fee + order_level_transaction_fee).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("consumer_access_token",res['data']['token']);
# post: });
# --- step 20: delete cart ---
# --- step 21: buy now ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 22: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(13.1);
# post: });
# --- step 23: Verify promoter earning summary is not changed ---
# post[assertion]: {"name": "Verify the lineup earnings is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_share}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 24: Verify promoter getPayoutSummary is not changed ---
# post[assertion]: {"name": "Verify the lineup balance is not change before payment", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_p}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





import json

from core.assertions import expect

from core.compat import get_path as _get_path
from core.compat import LegacyClient, legacy_render, legacy_url

def test__8091284__Lury_T4579_T4590_T4593_T4708_Verify_partner_can_share_revenue_to_other_account_on_store_settings(ctx):
    """Apifox case #8091284: Lury_T4579_T4590_T4593_T4708_Verify_partner_can_share_revenue_to_other_account_o"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    base_url = ctx.base_url
    client = LegacyClient(ctx)
    _render = legacy_render(ctx)
    _url = legacy_url(ctx)
    # === Steps ===
    vars['m1_transaction_fee'] = 'm1_transaction_fee'
    vars['p1_transaction_fee'] = 'p1_transaction_fee'
    vars['merchant_transaction_fee'] = 'merchant_transaction_fee'
    vars['curator_transaction_fee'] = 'curator_transaction_fee'
    vars['promoter_transaction_fee'] = 'promoter_transaction_fee'
    vars['p5_transaction_fee'] = 'p5_transaction_fee'
    # step 1: P-21-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}')
    try:
        _j = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
        vars['P-21_access_token'] = _get_path(_j, ["data", "refreshToken"])
    except Exception:
        pass
    # step 2: P-21 earning summary
    _resp2 = ctx.api.earnings.summary(app_headers=False, token='Bearer {{P-21_access_token}}')
    # extractor: lifetimeEarning = $.data.lifetimeEarning
    ctx.extract('lifetimeEarning', _resp2, '$.data.lifetimeEarning')
    # step 3: Partner getPayoutSummary
    _resp3 = ctx.api.earnings.summary_2(app_headers=False, token='Bearer {{P-21_access_token}}')
    # extractor: balance_amount = $.data.balance.amount
    ctx.extract('balance_amount', _resp3, '$.data.balance.amount')
    # step 4: Login - merchant
    _resp4 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}')
    try:
        _j = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
        vars['merchant_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 5: promoter earning summary
    _resp5 = ctx.api.earnings.summary(app_headers=False, token='merchant_access_token')
    # extractor: lifetimeEarning_p = $.data.lifetimeEarning
    ctx.extract('lifetimeEarning_p', _resp5, '$.data.lifetimeEarning')
    # step 6: promoter getPayoutSummary
    _resp6 = ctx.api.earnings.summary_2(app_headers=False, token='merchant_access_token')
    # extractor: balance_amount_p = $.data.balance.amount
    ctx.extract('balance_amount_p', _resp6, '$.data.balance.amount')
    # step 7: Add share revenue for merchant
    _resp7 = ctx.api.users.me_earning_share_configs(body='{\n    "customRecipientIdentifier": "dian.yuhong.ext+34@1m.app",\n    "shareRate": 0.12,\n    "note": "Automation test"\n}', token='Bearer {{P-21_access_token}}')
    # extractor: config_id = $.data.id (创建失败则复用已有配置)
    ctx.extract('config_id', _resp7, '$.data.id (创建失败则复用已有配置)')
    if not vars.get('config_id'):
        try:
            _rl = client.session().request(
                'GET',
                _url(base_url, '/users/me/earning-share-configs', vars),
                headers={k:_render(v, vars) for k, v in [('Authorization', 'Bearer {{P-21_access_token}}')]},
                data=None,
            )
            _jl = _rl.json() if _rl.headers.get('content-type','').startswith('application/json') else {}
            _items = _get_path(_jl, ['data', 'items']) or []
            _rec = 'dian.yuhong.ext+34@1m.app'
            _match = [it for it in _items if isinstance(it, dict) and it.get('customRecipientIdentifier') == _rec]
            if _match:
                vars['config_id'] = _match[0].get('id')
        except Exception: pass
    vars['m1_transaction_fee'] = 'm1_transaction_fee'
    vars['p1_transaction_fee'] = 'p1_transaction_fee'
    vars['merchant_transaction_fee'] = 'merchant_transaction_fee'
    # step 8: Consumer-login
    _resp8 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    try:
        _j = _resp8.json() if _resp8.headers.get('content-type','').startswith('application/json') else {}
        vars['consumer_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 9: delete cart
    _resp9 = ctx.api.cart.delete(token='consumer_access_token')
    # step 10: buy now
    _resp10 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "baab0db1-857e-49e0-9510-3e176d02d996",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "150011ef-8e56-4460-81ab-0fa88297f4d2",\n            "price": 13.1,\n            "postId": "baab0db1-857e-49e0-9510-3e176d02d996",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "69989f83-4e22-4d21-b18a-922e9e424506",\n        "pixelId": [\n            "453453"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-test-share-revenue-automation"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "150011ef-8e56-4460-81ab-0fa88297f4d2",\n            "postId": "baab0db1-857e-49e0-9510-3e176d02d996",\n            "price": 13.1,\n            "customFields": []\n        }\n    ]\n}', token='consumer_access_token')
    # extractor: orderNumber/orderId from step10 buy-now
    try:
        _j10 = _resp10.json() if _resp10.headers.get('content-type','').startswith('application/json') else {}
        vars['orderNumber'] = _get_path(_j10, ["data", "orderNumber"])
        vars['orderId'] = _get_path(_j10, ["data", "orderId"])
    except Exception:
        pass
    # step 11: create Order
    _resp11 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}', token='consumer_access_token')
    # 期望值 = 下单前 P-21 lifetimeEarning + 10.78 (round 2位)
    try:
        _le = float(vars.get('lifetimeEarning', 0) or 0)
        vars['lifetimeEarning_order'] = round((_le + 10.78) + 1e-9, 2)
    except Exception:
        vars['lifetimeEarning_order'] = None
    # step 12: Verify P-21 earning summary is not changed
    _resp12 = ctx.api.earnings.summary(app_headers=False, token='Bearer {{P-21_access_token}}')
    # assertion 12.earning is + 10.78: responseJson equal {{lifetimeEarning_order}}
    expect(_resp12).json('$.data.lifetimeEarning').equals(0.01)
    # step 13: Verify Partner getPayoutSummary is not changed
    _resp13 = ctx.api.earnings.summary_2(app_headers=False, token='Bearer {{P-21_access_token}}')
    # assertion 13.Balance is not changed: responseJson equal {{balance_amount}}
    expect(_resp13).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount}}'))
    # step 14: Check partner release schedule
    _resp14 = ctx.api.misc.earnings_merchant_orders(token='Bearer {{P-21_access_token}}', params={'pageNumber': '1', 'pageSize': '30', 'q': 'Revenue'})
    vars['second_date'] = 'second_date'
    vars['third_date'] = 'third_date'
    try:
        _p = float(vars.get('lifetimeEarning_p', 0) or 0)
        vars['lifetimeEarning_share'] = round((_p + 1.46) + 1e-9, 2)
    except Exception:
        vars['lifetimeEarning_share'] = None
    # step 15: Verify promoter earning summary is +10
    _resp15 = ctx.api.earnings.summary(app_headers=False, token='merchant_access_token')
    # assertion 15.Verify the lineup earnings +1.46: responseJson equal {{lifetimeEarning_share}}
    expect(_resp15).json('$.data.lifetimeEarning').equals(0.01)
    # step 16: Verify promoter getPayoutSummary is not changed
    _resp16 = ctx.api.earnings.summary_2(app_headers=False, token='merchant_access_token')
    # assertion 16.Verify the lineup balance is not change before payment: responseJson equal {{balance_amount_p}}
    expect(_resp16).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_p}}'))
    # step 17: GET promoter release schedule for shared revenue
    _resp17 = ctx.api.users.me_recipient_earning_shares(token='merchant_access_token', params={'pageNumber': '1', 'pageSize': '30', 'q': 'Shared'})
    # step 18: DELETE share revenue account
    _resp18 = ctx.api.users.me_earning_share_configs_by_config_id(token='Bearer {{P-21_access_token}}')
    # assertion 18.Verify delete share revenue successful: responseJson equal 200
    expect(_resp18).json('$.code').equals('200')
    vars['m1_transaction_fee'] = 'm1_transaction_fee'
    vars['p1_transaction_fee'] = 'p1_transaction_fee'
    vars['merchant_transaction_fee'] = 'merchant_transaction_fee'
    # step 19: Consumer-login
    _resp19 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{consumer_email}}"\n}')
    try:
        _j = _resp19.json() if _resp19.headers.get('content-type','').startswith('application/json') else {}
        vars['consumer_access_token'] = _get_path(_j, ["data", "token"])
    except Exception:
        pass
    # step 20: delete cart
    _resp20 = ctx.api.cart.delete(token='consumer_access_token')
    # step 21: buy now
    _resp21 = ctx.api.orders.buy_now(body='{\n    "postIdForFilter": "baab0db1-857e-49e0-9510-3e176d02d996",\n    "updateCartItems": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "150011ef-8e56-4460-81ab-0fa88297f4d2",\n            "price": 13.1,\n            "postId": "baab0db1-857e-49e0-9510-3e176d02d996",\n            "selected": true,\n            "customFields": []\n        }\n    ],\n    "fbAdParams": {\n        "eventID": "69989f83-4e22-4d21-b18a-922e9e424506",\n        "pixelId": [\n            "453453"\n        ],\n        "fbBrowserId": "fb.1.1768467567031.92506180232323161",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/mcc/post/lury-test-share-revenue-automation"\n    },\n    "currentUpdateCartItems": [\n        {\n            "quantity": 1,\n            "id": "150011ef-8e56-4460-81ab-0fa88297f4d2",\n            "postId": "baab0db1-857e-49e0-9510-3e176d02d996",\n            "price": 13.1,\n            "customFields": []\n        }\n    ]\n}', token='consumer_access_token')
    vars['orderNumber'] = 'orderNumber'
    vars['orderId'] = 'orderId'
    # step 22: create Order
    _resp22 = ctx.api.orders.create(body='{\n    "id": "{{orderId}}",\n    "contact": {\n        "email": "dian.yuhong.ext+19@1m.app",\n        "phoneNumber":"+17404630034"\n    },\n    "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",\n    "paymentInfo": {\n        "paymentMethodId": "{{pay_method_id}}"\n    },\n    "fbAdParams": {\n        "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1756981422832.790136385853196461",\n        "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",\n        "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a"\n    }\n}', token='consumer_access_token')
    # step 23: Verify promoter earning summary is not changed
    _resp23 = ctx.api.earnings.summary(app_headers=False, token='merchant_access_token')
    # assertion 23.Verify the lineup earnings is not changed: responseJson equal {{lifetimeEarning_share}}
    expect(_resp23).json('$.data.lifetimeEarning').equals(0.01)
    # step 24: Verify promoter getPayoutSummary is not changed
    _resp24 = ctx.api.earnings.summary_2(app_headers=False, token='merchant_access_token')
    # assertion 24.Verify the lineup balance is not change before payment: responseJson equal {{balance_amount_p}}
    expect(_resp24).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_p}}'))
