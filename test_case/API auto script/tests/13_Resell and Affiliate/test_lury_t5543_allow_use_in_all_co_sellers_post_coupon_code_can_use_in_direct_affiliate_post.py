"""Migrated from Apifox case #8547898. Source folder: Resell and Affiliate."""
# Apifox Case ID: 8547898  (traceability only — not needed to run)
NAME = "\"Allow use in all co-sellers' post\" coupon code can use in direct affiliate post"
TAGS = ["p0", "resell_and_affiliate", "suite:lury"]
PRIORITY = 0


CASE_ID = 8547898
ENV_NAME = "Release"

# --- step 1: Consumer-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 1;
# pre:     item_percentage_fee = 0.1;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: 
# pre: function set_rebate(unit_price,quantity){
# pre:     unit_fixed_rebate = 0.6;
# pre:     item_percentage_rebate = 0.065;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_rebate + unit_price * item_percentage_rebate) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }    
# pre: }
# pre: var unit_price = 9;
# pre: var quantity = 1;
# pre: var commission_rate = 0.25;
# pre: var aff_earnings = Math.round(((unit_price * quantity * commission_rate) + Number.EPSILON) *100 ) / 100;
# pre: var m1_earnings = Number((unit_price * quantity - aff_earnings ).toFixed(2));
# pre: var m1_rebate = Math.floor(set_rebate(unit_price,quantity) *100 ) / 100;
# pre: var transaction_fee_item_level = Math.floor(get_transaction_fee_item_level_general(unit_price,quantity)*100)/100;
# pre: var aff_transaction_fee = Math.round(((commission_rate * transaction_fee_item_level) + Number.EPSILON) *100 ) / 100;
# pre: var m1_transaction_fee = Number((transaction_fee_item_level - aff_transaction_fee ).toFixed(2));
# pre: 
# pre: pm.environment.set("aff_transaction_fee", aff_transaction_fee);
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("m1_rebate", m1_rebate);
# pre: pm.environment.set("aff_earnings", aff_earnings);
# pre: pm.environment.set("m1_earnings", m1_earnings);
# pre: console.log("aff_transaction_fee: " + aff_transaction_fee)
# pre: console.log("m1_transaction_fee: " + m1_transaction_fee)
# pre: console.log("m1_rebate: " + m1_rebate)
# pre: console.log("aff_earnings: " + aff_earnings)
# pre: console.log("m1_earnings: " + m1_earnings)
# pre: 
# pre: 
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("consumer_access_token",res['data']['token']);
# post: });
# --- step 2: delete cart ---
# --- step 3: buy now  ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post: });
# --- step 4: apply promotion ---
# post[customScript]: pm.test("Apply coupon and Get Line Item ID", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     var line_items = res["data"]["lineItems"]
# post:     for (var line of line_items){
# post:         var lineItemId = line['lineItemId'];
# post:     }
# post:     pm.environment.set("lineItemId",lineItemId);
# post: });
# --- step 5: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(9);
# post: });
# --- step 6: Login-M1 ---
# post[customScript]: pm.test("Check M1 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("M1_access_token",res['data']['token']);
# post: });
# --- step 7: get M1 order detail v2 ---
# post[customScript]: pm.test("Check M1 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var data = res['data']
# post:     var m1_earnings = pm.environment.get("m1_earnings");
# post:     var m1_transaction_fee = pm.environment.get("m1_transaction_fee");
# post:     var m1_rebate = pm.environment.get("m1_rebate");
# post:     var total_payout = Number((m1_earnings - m1_transaction_fee + m1_rebate).toFixed(2));
# post:     pm.expect(data["transactionFee"]).to.eql(m1_transaction_fee);
# post:     pm.expect(data["totalPayoutToPay"]).to.eql(total_payout);
# post:     pm.expect(data["totalCommissionSubtotal"]).to.eql(6.75);
# post:     pm.expect(data["totalCommissionRefunded"]).to.eql(0);
# post:     pm.expect(data["totalCommissionNet"]).to.eql(6.75);
# post:     pm.expect(data["transactionFeeRebate"]).to.eql(1.18);
# post:     pm.expect(data["totalPaymentProcessingFee"]).to.eql(0);
# post:     pm.expect(data["totalShippingSubtotal"]).to.eql(0);
# post:     pm.expect(data["totalShippingRefunded"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmount"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountRefunded"]).to.eql(0);
# post:     pm.expect(data["totalShippingNet"]).to.eql(0);
# post:     pm.expect(data["totalTaxAmountNet"]).to.eql(0);
# post: });
# post: 
# --- step 8: Login -affiliate ---
# post[customScript]: pm.test("Check P5 login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("affiliate_access_token",res['data']['token']);
# post: });
# --- step 9: get affiliate promoter orders ---
# post[customScript]: pm.test("Get P5 order ID", function () {
# post:     var res = JSON.parse(responseBody);
# post:     order_list = res['data']['items']
# post:     var orderNumber = pm.environment.get("orderNumber");
# post:     console.log(orderNumber)
# post:     var curatorOrderId = "";
# post:     for (var order of order_list){
# post:         if (order['orderNumber'] === orderNumber){
# post:             var curatorOrderId = order['id'];
# post:             console.log(curatorOrderId);
# post:         }
# post:     }
# post:     pm.environment.set("P5_OrderId",curatorOrderId);
# post: });
# --- step 10: get affiliate order detail v2 ---
# post[customScript]: pm.test("Check P5 earnings and processing fee", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     var aff_earnings = pm.environment.get("aff_earnings");
# post:     var aff_transaction_fee = pm.environment.get("aff_transaction_fee");
# post:     var total_payout = Number((aff_earnings - aff_transaction_fee).toFixed(2));
# post:     pm.expect(res['data']['totalPayoutToPay']).to.eql(total_payout);
# post:     pm.expect(res['data']['transactionFee']).to.eql(aff_transaction_fee);
# post:     pm.expect(res['data']['totalCommissionSubtotal']).to.eql(aff_earnings);
# post:     pm.expect(res['data']['totalCommissionRefunded']).to.eql(0);
# post:     pm.expect(res['data']['totalCommissionNet']).to.eql(aff_earnings);
# post:     pm.expect(res['data']['totalPaymentProcessingFee']).to.eql(0);
# post:     pm.expect(res['data']['transactionFeeRebate']).to.eql(0);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:            if (line_item["variantInfo"]["id"] === "35811870-0f2f-43e7-955a-887fb052f2dd"){
# post:             pm.expect(line_item["lineItemPrice"]).to.eql(9);
# post:             pm.expect(line_item["retailPrice"]).to.eql(10);
# post:             pm.expect(line_item["upstreamLineItemDiscount"]).to.eql(1);
# post:             pm.expect(line_item["couponDiscount"]).to.eql(0);
# post:             pm.expect(line_item["subscriptionDiscount"]).to.eql(0);
# post:             pm.expect(line_item["lineItemDiscount"]).to.eql(0);
# post:             pm.expect(line_item["commissionRate"]).to.eql(25);
# post:             pm.expect(line_item["commissionGross"]).to.eql(2.25);
# post:             pm.expect(line_item["commissionDeduction"]).to.eql(0);
# post:             pm.expect(line_item["costPrice"]).to.eql(6.75);
# post:             pm.expect(line_item["lineItemSubtotal"]).to.eql(9);                     
# post:             pm.expect(line_item["downlineCommissionRate"]).to.eql(0);
# post:             pm.expect(line_item["commissionSubtotal"]).to.eql(2.25);
# post:             pm.expect(line_item["commissionRefunded"]).to.eql(0);
# post:             pm.expect(line_item["commissionNet"]).to.eql(2.25);          
# post:             pm.expect(line_item["quantity"]).to.eql(1);
# post:             pm.expect(line_item["quantityFulfilled"]).to.eql(1);
# post:             pm.expect(line_item["quantityRefunded"]).to.eql(0);
# post:             pm.expect(line_item["lineItemRefunded"]).to.eql(0);
# post:             pm.expect(line_item["fulfillmentStatus"]).to.eql("FULFILLED");
# post:             pm.expect(line_item["saleType"]).to.eql("POST_COMMISSION");
# post:             pm.expect(line_item["uplineSaleType"]).to.eql("POST_COMMISSION");
# post:            }
# post:            else{
# post:             pm.expect(1).to.eql(2);
# post: 
# post:            }
# post:     }
# post: 
# post: });




import json
import time

from typing import Any, TYPE_CHECKING

from core.assertions import expect

from core.compat import get_path as _get_path

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_t5543_allow_use_in_all_co_sellers_post_coupon_code_can_use_in_direct_affiliate_post(ctx: "Context"):
    """Apifox case #8547898: Lury_T5543_Allow_use_in_all_co_sellers_post_coupon_code_can_use_in_direct_affili"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Consumer-login
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{consumer_email}}",
    })
    ctx.extract('consumer_access_token', _resp1, '$.data.token')
    # 复算 pre-script（unit_price=9, qty=1, commission_rate=0.25）
    import math as _m
    def _js_round(x): return _m.floor(x * 100 + 0.5) / 100
    def _js_floor(x): return _m.floor(x * 100) / 100
    _up, _q, _cr = 9, 1, 0.25
    vars['aff_earnings'] = _js_round(_up * _q * _cr)            # 2.25
    vars['m1_earnings'] = round(_up * _q - vars['aff_earnings'], 2)  # 6.75
    vars['m1_rebate'] = _js_floor((0.6 + _up * 0.065) * _q)     # 1.18
    _tf_item = _js_floor((1 + _up * 0.1) * _q)                  # 1.9
    vars['aff_transaction_fee'] = _js_round(_cr * _tf_item)     # 0.48
    vars['m1_transaction_fee'] = round(_tf_item - vars['aff_transaction_fee'], 2)  # 1.42
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete(token='consumer_access_token')
    # step 3: buy now 
    _resp3 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "3f6a6723-9223-418e-953c-e861a0c9969e",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "35811870-0f2f-43e7-955a-887fb052f2dd",
                "price": 10,
                "postId": "3f6a6723-9223-418e-953c-e861a0c9969e",
                "selected": True,
                "affiliateCode": "70zd9u",
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "74ec16cb-ed91-45a4-86f0-782c3bfe0f07",
            "pixelId": [
                "453453",
            ],
            "externalId": "9080b930-2796-4b96-8a52-64c70ff1e65c",
            "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-affiliate-coupon-code-testing?aff=70zd9u",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "35811870-0f2f-43e7-955a-887fb052f2dd",
                "postId": "3f6a6723-9223-418e-953c-e861a0c9969e",
                "price": 10,
                "affiliateCode": "70zd9u",
                "customFields": [],
            },
        ],
        "subdomainVanityUrl": "",
    }, token='consumer_access_token')
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp3, '$.data.orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp3, '$.data.orderId')
    # step 4: apply promotion
    _resp4 = ctx.api.orders.update_promotions(body={
        "orderId": "{{orderId}}",
        "shippingAddress": {
            "line1": "",
            "city": "",
            "zipcode": "",
            "state": "",
        },
        "applicableCode": "affcode",
    }, token='consumer_access_token')
    _j: dict[str, Any] = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
    _arr = _get_path(_j, ["data", "lineItems"]) or []
    if _arr:
        vars['lineItemId'] = _arr[0].get('lineItemId')
    # step 5: create Order
    _resp5 = ctx.api.orders.create(body={
        "id": "{{orderId}}",
        "contact": {
            "email": "dian.yuhong.ext+19@1m.app",
            "phoneNumber": "+17404630034",
        },
        "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",
        "paymentInfo": {
            "paymentMethodId": "{{pay_method_id}}",
        },
        "fbAdParams": {
            "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a",
        },
    }, token='consumer_access_token')
    # assertion step5: create order status 201 + totalTopay=9
    expect(_resp5).status().is_(201)
    expect(_resp5).json('$.data.totalTopay').close_to(9)
    # step 6: Login-M1
    _resp6 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{M1}}",
    })
    ctx.extract('M1_access_token', _resp6, '$.data.token')
    # step 7: get M1 order detail v2
    _resp7 = ctx.api.orders.merchant_detail_v2(path_vars={'merchantId': '{{M1_merchantIDe}}'}, token='M1_access_token')
    # assertion step7: M1 earnings & processing fee
    expect(_resp7).status().is_(200)
    expect(_resp7).json('$.data.transactionFee').close_to(vars['m1_transaction_fee'])
    expect(_resp7).json('$.data.totalCommissionSubtotal').close_to(6.75)
    expect(_resp7).json('$.data.totalCommissionRefunded').close_to(0)
    expect(_resp7).json('$.data.totalCommissionNet').close_to(6.75)
    expect(_resp7).json('$.data.transactionFeeRebate').close_to(1.18)
    expect(_resp7).json('$.data.totalPaymentProcessingFee').close_to(0)
    expect(_resp7).json('$.data.totalShippingSubtotal').close_to(0)
    expect(_resp7).json('$.data.totalShippingRefunded').close_to(0)
    expect(_resp7).json('$.data.totalTaxAmount').close_to(0)
    expect(_resp7).json('$.data.totalTaxAmountRefunded').close_to(0)
    expect(_resp7).json('$.data.totalShippingNet').close_to(0)
    expect(_resp7).json('$.data.totalTaxAmountNet').close_to(0)
    # totalPayoutToPay = m1_earnings - m1_tf + m1_rebate（动态复算）
    _exp_payout7 = round(vars['m1_earnings'] - vars['m1_transaction_fee'] + vars['m1_rebate'], 2)
    expect(_resp7).json('$.data.totalPayoutToPay').close_to(_exp_payout7)
    # step 8: Login -affiliate
    _resp8 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{affiliate_promoter}}",
    })
    ctx.extract('affiliate_access_token', _resp8, '$.data.token')
    # step 9: get affiliate promoter orders
    # 2026-09-20 修复：promoter 订单列表为异步聚合（新单最多延迟数十秒才出现在首页），
    # 直接断言首页命中会偶发失败（admin 侧可查、detail 接口 200 但列表未同步）。
    # 改为条件轮询：最多 6 次 × 3s，命中即 break（与订阅用例同款模式）。
    vars['P5_OrderId'] = ''
    for _attempt in range(6):
        _resp9 = ctx.api.orders.promoter(params={'pageSize': '30', 'pageNumber': '1'}, token='affiliate_access_token')
        _j9 = _resp9.json() if _resp9.headers.get('content-type','').startswith('application/json') else {}
        _arr9 = _get_path(_j9, ['data', 'items']) or []
        _hit9 = next((o for o in _arr9 if o.get('orderNumber') == vars.get('orderNumber')), None)
        if _hit9:
            vars['P5_OrderId'] = _hit9.get('id')
            break
        time.sleep(3)
    assert vars.get('P5_OrderId'), (
        f"test_lury_t5543_allow_use_in_all_co_sell L302: promoter orders 中未找到 "
        f"orderNumber={vars.get('orderNumber')!r} 的订单（items={len(_arr9)}）")
    # step 10: get affiliate order detail v2
    _resp10 = ctx.api.orders.promoter_detail_v2(path_vars={'merchantOrderId': '{{P5_OrderId}}'}, token='affiliate_access_token')
    # assertion step10: affiliate earnings & processing fee + line item
    expect(_resp10).status().is_(200)
    _j10: dict[str, Any] = _resp10.json() if _resp10.headers.get('content-type','').startswith('application/json') else {}
    _d10: dict[str, Any] = _j10.get('data') or {}
    expect(_resp10).json('$.data.transactionFee').close_to(vars['aff_transaction_fee'])
    expect(_resp10).json('$.data.totalCommissionSubtotal').close_to(vars['aff_earnings'])
    expect(_resp10).json('$.data.totalCommissionRefunded').close_to(0)
    expect(_resp10).json('$.data.totalCommissionNet').close_to(vars['aff_earnings'])
    expect(_resp10).json('$.data.totalPaymentProcessingFee').close_to(0)
    expect(_resp10).json('$.data.transactionFeeRebate').close_to(0)
    _exp_payout10 = round(vars['aff_earnings'] - vars['aff_transaction_fee'], 2)
    expect(_resp10).json('$.data.totalPayoutToPay').close_to(_exp_payout10)
    for _li in _d10.get('lineItems') or []:
        if (_li.get('variantInfo') or {}).get('id') == '35811870-0f2f-43e7-955a-887fb052f2dd':
            assert abs((_li.get('lineItemPrice') or 0) - 9) < 0.01
            assert abs((_li.get('retailPrice') or 0) - 10) < 0.01
            assert abs((_li.get('upstreamLineItemDiscount') or 0) - 1) < 0.01
            assert abs((_li.get('couponDiscount') or 0) - 0) < 0.01
            assert abs((_li.get('subscriptionDiscount') or 0) - 0) < 0.01
            assert abs((_li.get('lineItemDiscount') or 0) - 0) < 0.01
            assert abs((_li.get('commissionRate') or 0) - 25) < 0.01
            assert abs((_li.get('commissionGross') or 0) - 2.25) < 0.01
            assert abs((_li.get('commissionDeduction') or 0) - 0) < 0.01
            assert abs((_li.get('costPrice') or 0) - 6.75) < 0.01
            assert abs((_li.get('lineItemSubtotal') or 0) - 9) < 0.01
            assert abs((_li.get('downlineCommissionRate') or 0) - 0) < 0.01
            assert abs((_li.get('commissionSubtotal') or 0) - 2.25) < 0.01
            assert abs((_li.get('commissionRefunded') or 0) - 0) < 0.01
            assert abs((_li.get('commissionNet') or 0) - 2.25) < 0.01
            assert _li.get('quantity') == 1
            assert _li.get('quantityFulfilled') == 1
            assert _li.get('quantityRefunded') == 0
            assert abs((_li.get('lineItemRefunded') or 0) - 0) < 0.01
            assert _li.get('fulfillmentStatus') == 'FULFILLED'
            assert _li.get('saleType') == 'POST_COMMISSION'
            assert _li.get('uplineSaleType') == 'POST_COMMISSION'
