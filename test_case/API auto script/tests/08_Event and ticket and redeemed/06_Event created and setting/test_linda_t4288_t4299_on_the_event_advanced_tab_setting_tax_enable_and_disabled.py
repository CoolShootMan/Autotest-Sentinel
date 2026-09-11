"""Migrated from Apifox case #7757330. Source folder: Event and ticket and redeemed/Event created and setting."""
# Apifox Case ID: 7757330  (traceability only — not needed to run)
NAME = "& T4299 On the event advanced tab setting tax enable and disabled"
TAGS = ["p0", "event_and_ticket_and_redeemed_event_created_and_setting", "suite:linda"]
PRIORITY = 0


CASE_ID = 7757330
ENV_NAME = "Release"

# --- step 1: Get Partner linda01 token ---
# post[extractor]: {"variableName": "linda01_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: 587d6edf-679c-4242-93ce-a71785a615cb ---
# post[customScript]: // ===================== 完整断言脚本（已修复浮点数精度与状态码问题） =====================
# post: 
# post: // 1. 验证接口响应状态码（根据最新的 JSON 返回值，已修正为 200）
# post: pm.test("接口响应状态码为 200", function () {
# post:     pm.response.to.have.status(201);
# post: });
# post: 
# post: // 2. 解析响应 JSON 数据
# post: let responseData = pm.response.json();
# post: 
# post: // 提取核心数据
# post: let variant = responseData.data.items[0].variants[0];
# post: let ticketPrice = variant.ticketPrice; // 26.56
# post: let price = variant.price; // 34.44
# post: let platformFee = variant.fees.platformFee; // 4.44
# post: let customFee = variant.fees.customFee; // 3.44
# post: let transactionItemFee = variant.fees.transactionItemFee; // 7.88
# post: let taxPercentage = variant.fees.customFeeBreakdown.TAX.unitPercentageFee; // 0.1
# post: 
# post: // 3. 验证 TAX 费率是否为 10%（0.1）
# post: pm.test("TAX 费率验证：10%", function () {
# post:     pm.expect(taxPercentage).to.equal(0.1, "TAX 费率不是预期的 10%");
# post: });
# post: 
# post: // 4. 验证 TAX 金额计算（price * 10% = customFee）
# post: pm.test("TAX 金额计算验证（price * 10% = customFee）", function () {
# post:     let expectedCustomFee = price * 0.1; // 34.44 * 0.1 = 3.444
# post:     // 允许两位小数精度误差
# post:     pm.expect(customFee).to.be.closeTo(expectedCustomFee, 0.01, "TAX 金额计算错误");
# post: });
# post: 
# post: // 5. 验证 platformFee（平台费）计算规则 —— 【已修复：改用 closeTo 解决 4.4399999 报错】
# post: pm.test("platformFee 计算验证", function () {
# post:     let expectedPlatformFee = transactionItemFee - customFee; // 7.88 - 3.44
# post:     pm.expect(platformFee).to.be.closeTo(expectedPlatformFee, 0.01, "平台费计算错误");
# post: });
# post: 
# post: // 6. 验证最终价格（price = ticketPrice + transactionItemFee） —— 【已修复：改用 closeTo 预防浮点误差】
# post: pm.test("最终价格验证（ticketPrice + transactionItemFee = price）", function () {
# post:     let expectedPrice = ticketPrice + transactionItemFee; // 26.56 + 7.88 = 34.44
# post:     pm.expect(price).to.be.closeTo(expectedPrice, 0.01, "最终价格计算错误");
# post: });
# post: 
# post: // 7. 验证 transactionItemFee 总和（platformFee + customFee） —— 【已修复：改用 closeTo 解决 7.88000001 报错】
# post: pm.test("总手续费验证（platformFee + customFee = transactionItemFee）", function () {
# post:     let expectedTransactionFee = platformFee + customFee; // 4.44 + 3.44
# post:     pm.expect(transactionItemFee).to.be.closeTo(expectedTransactionFee, 0.01, "总手续费计算错误");
# post: });
# --- step 3: 5c5ebff3-c289-4600-b24b-a6f953ced00f ---
# post[customScript]: // 1. 验证基础状态
# post: pm.test("接口响应状态码为 201", () => pm.response.to.have.status(201));
# post: pm.test("接口返回 code 为 200", () => pm.expect(pm.response.json().code).to.equal(200));
# post: pm.test("接口返回 message 为 success", () => pm.expect(pm.response.json().message).to.equal("success"));
# post: 
# post: // 2. 提取数据（严格匹配响应的层级结构）
# post: const res = pm.response.json();
# post: const variant = res.data.items[0].variants[0]; // 定位到目标variant
# post: // 逐个提取字段（确保层级正确）
# post: const ticketPrice = variant.ticketPrice;
# post: const platformFee = variant.fees.platformFee;
# post: const customFee = variant.fees.customFee;
# post: const transactionItemFee = variant.fees.transactionItemFee; // 正确层级：variant直接下的字段
# post: const price = variant.price;
# post: const taxPercentage = variant.fees.customFeeBreakdown.TAX.unitPercentageFee;
# post: const taxItemFee = variant.fees.customFeeBreakdown.TAX.itemFee;
# post: 
# post: // 3. 执行断言
# post: pm.test("TAX 费率验证（20%）", () => {
# post:     pm.expect(taxPercentage).to.equal(0.2);
# post: });
# post: pm.test("TAX 金额计算验证", () => {
# post:     pm.expect(taxItemFee).to.be.closeTo(customFee, 0.01);
# post: });
# post: pm.test("platformFee 计算验证", () => {
# post:     const expected = transactionItemFee - customFee;
# post:     pm.expect(platformFee).to.be.closeTo(expected, 0.01);
# post: });
# post: pm.test("最终价格验证", () => {
# post:     const expected = ticketPrice + transactionItemFee;
# post:     pm.expect(price).to.be.closeTo(expected, 0.01);
# post: });
# post: pm.test("总手续费验证", () => {
# post:     const expected = platformFee + customFee;
# post:     pm.expect(transactionItemFee).to.be.closeTo(expected, 0.01);
# post: });
# --- step 4: 56005cad-c875-4053-beb9-e541c2b029ca ---
# post[customScript]: // ===================== disable tax 场景  =====================
# post: // 适配场景：税费禁用后，所有TAX相关字段为0，手续费逻辑匹配响应数据
# post: 
# post: // 1. 验证HTTP响应状态码（匹配实际返回的201）
# post: pm.test("✅ 接口响应状态码为201", function () {
# post:     pm.response.to.have.status(201);
# post: });
# post: 
# post: // 2. 解析响应JSON数据（提前做异常处理，避免解析失败）
# post: let responseData;
# post: pm.test("✅ 响应数据为合法JSON格式", function () {
# post:     pm.expect(pm.response.text()).to.be.not.empty;
# post:     try {
# post:         responseData = pm.response.json();
# post:         pm.expect(responseData).to.be.an("object");
# post:     } catch (e) {
# post:         pm.expect.fail("响应数据无法解析为JSON格式：" + e.message);
# post:     }
# post: });
# post: 
# post: // 3. 验证核心返回字段（code/message）
# post: pm.test("✅ 接口返回code为200", function () {
# post:     pm.expect(responseData).to.have.property("code").that.is.a("number").and.equal(200);
# post: });
# post: pm.test("✅ 接口返回message为success", function () {
# post:     pm.expect(responseData).to.have.property("message").that.is.a("string").and.equal("success");
# post: });
# post: 
# post: // 4. 验证data层级基础结构
# post: pm.test("✅ data字段存在且为对象", function () {
# post:     pm.expect(responseData).to.have.property("data").that.is.an("object");
# post: });
# post: pm.test("✅ data.items为非空数组", function () {
# post:     pm.expect(responseData.data).to.have.property("items").that.is.an("array").with.length.greaterThan(0);
# post: });
# post: pm.test("✅ data.totalCount为合法数值", function () {
# post:     pm.expect(responseData.data).to.have.property("totalCount").that.is.a("number").and.greaterThan(0);
# post: });
# post: 
# post: // 5. 遍历items和variants，验证核心业务逻辑
# post: responseData.data.items.forEach((item, itemIndex) => {
# post:     // 验证当前item的variants为非空数组
# post:     pm.test(`✅ items[${itemIndex}].variants为非空数组`, function () {
# post:         pm.expect(item).to.have.property("variants").that.is.an("array").with.length.greaterThan(0);
# post:     });
# post: 
# post:     // 遍历每个variant，验证disable tax逻辑
# post:     item.variants.forEach((variant, varIndex) => {
# post:         // 提取核心字段（带默认值，避免字段缺失）
# post:         const ticketPrice = variant.ticketPrice || 0;
# post:         const price = variant.price || 0;
# post:         const fees = variant.fees || {};
# post:         const platformFee = fees.platformFee || 0;
# post:         const customFee = fees.customFee || 0;
# post:         const transactionItemFee = fees.transactionItemFee || 0;
# post:         const taxBreakdown = (fees.customFeeBreakdown || {}).TAX || {};
# post:         const taxFixedFee = taxBreakdown.unitFixedFee || 0;
# post:         const taxPercentageFee = taxBreakdown.unitPercentageFee || 0;
# post:         const taxItemFee = taxBreakdown.itemFee || 0;
# post: 
# post:         // ------------------- 核心：disable tax 税费验证 -------------------
# post:         pm.test(`✅ items[${itemIndex}].variants[${varIndex}] TAX固定费率为0`, function () {
# post:             pm.expect(taxFixedFee).to.be.a("number").and.equal(0);
# post:         });
# post:         pm.test(`✅ items[${itemIndex}].variants[${varIndex}] TAX百分比费率为0`, function () {
# post:             pm.expect(taxPercentageFee).to.be.a("number").and.equal(0);
# post:         });
# post:         pm.test(`✅ items[${itemIndex}].variants[${varIndex}] TAX金额为0`, function () {
# post:             pm.expect(taxItemFee).to.be.a("number").and.equal(0);
# post:         });
# post:         pm.test(`✅ items[${itemIndex}].variants[${varIndex}] 自定义税费customFee为0`, function () {
# post:             pm.expect(customFee).to.be.a("number").and.equal(0);
# post:         });
# post: 
# post:         // ------------------- 手续费计算逻辑验证 -------------------
# post:         pm.test(`✅ items[${itemIndex}].variants[${varIndex}] platformFee等于transactionItemFee（税费为0）`, function () {
# post:             pm.expect(platformFee).to.be.closeTo(transactionItemFee, 0.01);
# post:         });
# post:         pm.test(`✅ items[${itemIndex}].variants[${varIndex}] 总手续费验证（platformFee+customFee=transactionItemFee）`, function () {
# post:             const expectedTransactionFee = platformFee + customFee;
# post:             pm.expect(transactionItemFee).to.be.closeTo(expectedTransactionFee, 0.01);
# post:         });
# post: 
# post:         // ------------------- 最终价格验证 -------------------
# post:         pm.test(`✅ items[${itemIndex}].variants[${varIndex}] 最终价格验证（ticketPrice+transactionItemFee=price）`, function () {
# post:             const expectedPrice = ticketPrice + transactionItemFee;
# post:             pm.expect(price).to.be.closeTo(expectedPrice, 0.01);
# post:         });
# post:     });
# post: });




import json

from core.assertions import expect

def test_linda_t4288_t4299_on_the_event_advanced_tab_setting_tax_enable_and_disabled(ctx):
    """Apifox case #7757330: Linda_T4288_T4299_On_the_event_advanced_tab_setting_tax_enable_and_disabled"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda01 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+01@1m.app"\n}')
    # extractor: linda01_token = $.data.token
    ctx.extract('linda01_token', _resp1, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    # step 2: 587d6edf-679c-4242-93ce-a71785a615cb
    _resp2 = ctx.api.products.calculate_ticket_batch(body='{\r\n    "listingType": "TICKET",\r\n    "customTaxRate": 10,\r\n    "items": [\r\n        {\r\n            "variants": [\r\n                {\r\n                    "price": 34.44\r\n                }\r\n            ]\r\n        }\r\n    ]\r\n}', token='linda01_token')
    # === 断言（由Apifox customScript翻译）===
    assert _resp2.status_code == 201, f"step2 status != 201, got {_resp2.status_code}"
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    _v2 = ((_j2.get('data') or {}).get('items') or [{}])[0].get('variants') or [{}]
    _v2 = _v2[0]
    _t2 = _v2.get('ticketPrice')
    _p2 = _v2.get('price')
    _f2 = _v2.get('fees') or {}
    _pf2 = _f2.get('platformFee')
    _cf2 = _f2.get('customFee')
    _tf2 = _f2.get('transactionItemFee')
    _tax2 = (_f2.get('customFeeBreakdown') or {}).get('TAX') or {}
    _taxPct2 = _tax2.get('unitPercentageFee')
    assert _taxPct2 == 0.1, f"step2 TAX费率 != 0.1, got {_taxPct2}"
    assert abs(_cf2 - _p2 * 0.1) <= 0.01, f"step2 TAX金额计算错误: customFee={_cf2}, price*0.1={_p2*0.1}"
    assert abs(_pf2 - (_tf2 - _cf2)) <= 0.01, f"step2 platformFee计算错误: platformFee={_pf2}, transactionItemFee-customFee={_tf2-_cf2}"
    assert abs(_p2 - (_t2 + _tf2)) <= 0.01, f"step2 最终价格错误: price={_p2}, ticketPrice+transactionItemFee={_t2+_tf2}"
    assert abs(_tf2 - (_pf2 + _cf2)) <= 0.01, f"step2 总手续费错误: transactionItemFee={_tf2}, platformFee+customFee={_pf2+_cf2}"
    # step 3: 5c5ebff3-c289-4600-b24b-a6f953ced00f
    _resp3 = ctx.api.products.calculate_ticket_batch(body='{\r\n    "listingType": "TICKET",\r\n    "customTaxRate": 20,\r\n    "items": [\r\n        {\r\n            "variants": [\r\n                {\r\n                    "price": 34.44\r\n                }\r\n            ]\r\n        }\r\n    ]\r\n}', token='linda01_token')
    # === 断言（由Apifox customScript翻译）===
    assert _resp3.status_code == 201, f"step3 status != 201, got {_resp3.status_code}"
    _j3 = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
    assert _j3.get('code') == 200, f"step3 code != 200, got {_j3.get('code')}"
    assert _j3.get('message') == 'success', f"step3 message != success, got {_j3.get('message')}"
    _v3 = ((_j3.get('data') or {}).get('items') or [{}])[0].get('variants') or [{}]
    _v3 = _v3[0]
    _t3 = _v3.get('ticketPrice')
    _p3 = _v3.get('price')
    _f3 = _v3.get('fees') or {}
    _pf3 = _f3.get('platformFee')
    _cf3 = _f3.get('customFee')
    _tf3 = _f3.get('transactionItemFee')
    _tax3 = (_f3.get('customFeeBreakdown') or {}).get('TAX') or {}
    _taxPct3 = _tax3.get('unitPercentageFee')
    _taxItem3 = _tax3.get('itemFee')
    assert _taxPct3 == 0.2, f"step3 TAX费率 != 0.2, got {_taxPct3}"
    assert abs(_taxItem3 - _cf3) <= 0.01, f"step3 TAX金额错误: itemFee={_taxItem3}, customFee={_cf3}"
    assert abs(_pf3 - (_tf3 - _cf3)) <= 0.01, f"step3 platformFee计算错误: platformFee={_pf3}, transactionItemFee-customFee={_tf3-_cf3}"
    assert abs(_p3 - (_t3 + _tf3)) <= 0.01, f"step3 最终价格错误: price={_p3}, ticketPrice+transactionItemFee={_t3+_tf3}"
    assert abs(_tf3 - (_pf3 + _cf3)) <= 0.01, f"step3 总手续费错误: transactionItemFee={_tf3}, platformFee+customFee={_pf3+_cf3}"
    # step 4: 56005cad-c875-4053-beb9-e541c2b029ca
    _resp4 = ctx.api.products.calculate_ticket_batch(body='{\r\n    "listingType": "TICKET",\r\n    "customTaxRate": 0,\r\n    "items": [\r\n        {\r\n            "variants": [\r\n                {\r\n                    "price": 34.44\r\n                }\r\n            ]\r\n        }\r\n    ]\r\n}', token='linda01_token')
    # === 断言（由Apifox customScript翻译）===
    assert _resp4.status_code == 201, f"step4 status != 201, got {_resp4.status_code}"
    _j4 = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
    assert _j4.get('code') == 200, f"step4 code != 200, got {_j4.get('code')}"
    assert _j4.get('message') == 'success', f"step4 message != success, got {_j4.get('message')}"
    _d4 = _j4.get('data')
    assert isinstance(_d4, dict), "step4 data 非对象"
    _items4 = _d4.get('items') or []
    assert isinstance(_items4, list) and len(_items4) > 0, "step4 data.items 为空"
    assert isinstance(_d4.get('totalCount'), (int, float)) and _d4.get('totalCount') > 0, f"step4 totalCount 非法: {_d4.get('totalCount')}"
    for _item4 in _items4:
        _vs4 = _item4.get('variants') or []
        assert isinstance(_vs4, list) and len(_vs4) > 0, "step4 variant 为空"
        for _v4 in _vs4:
            _f4 = _v4.get('fees') or {}
            _tb4 = (_f4.get('customFeeBreakdown') or {}).get('TAX') or {}
            assert _tb4.get('unitFixedFee', 0) == 0, f"step4 TAX固定费率非0: {_tb4.get('unitFixedFee')}"
            assert _tb4.get('unitPercentageFee', 0) == 0, f"step4 TAX百分比费率非0: {_tb4.get('unitPercentageFee')}"
            assert _tb4.get('itemFee', 0) == 0, f"step4 TAX金额非0: {_tb4.get('itemFee')}"
            assert _f4.get('customFee', 0) == 0, f"step4 customFee非0: {_f4.get('customFee')}"
            _pf4 = _f4.get('platformFee', 0); _tf4 = _f4.get('transactionItemFee', 0); _cf4 = _f4.get('customFee', 0)
            assert abs(_pf4 - _tf4) <= 0.01, f"step4 platformFee != transactionItemFee: {_pf4} vs {_tf4}"
            assert abs(_tf4 - (_pf4 + _cf4)) <= 0.01, f"step4 总手续费错误: {_tf4} vs {_pf4 + _cf4}"
            assert abs(_v4.get('price', 0) - (_v4.get('ticketPrice', 0) + _tf4)) <= 0.01, f"step4 最终价格错误"
