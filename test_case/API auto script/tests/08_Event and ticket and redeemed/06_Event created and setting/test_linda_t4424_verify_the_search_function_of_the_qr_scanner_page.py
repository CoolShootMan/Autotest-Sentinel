"""Migrated from Apifox case #7676278. Source folder: Event and ticket and redeemed/Event created and setting."""
# Apifox Case ID: 7676278  (traceability only — not needed to run)
NAME = "Verify the search function of the QR scanner page"
TAGS = ["p1", "event_and_ticket_and_redeemed_event_created_and_setting", "suite:linda"]
PRIORITY = 1


CASE_ID = 7676278
ENV_NAME = "Release"

# --- step 1: 77e37c25-4f20-4147-a480-5e6e7598d629 ---
# pre: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# pre: 
# post[customScript]: // ========== 核心验证逻辑 ==========
# post: try {
# post:     // 1. 解析接口响应体
# post:     const response = pm.response.json();
# post:     console.log("接口响应数据：", response);
# post: 
# post:     // 2. 验证接口访问成功（基础响应格式）
# post:     pm.test("接口访问成功，基础响应格式正确", () => {
# post:         // 验证状态码200（HTTP层面）
# post:         pm.expect(pm.response.code).to.equal(200);
# post:         // 验证业务码200、message为success、request_id存在
# post:         pm.expect(response.code).to.equal(200);
# post:         pm.expect(response.message).to.equal("success");
# post:         pm.expect(response.request_id).to.not.be.empty;
# post:         // 验证data对象存在
# post:         pm.expect(response.data).to.be.an("object").and.not.be.empty;
# post:     });
# post: 
# post:     // 3. 提取需要验证的字段并校验类型
# post:     const { totalSold, totalRedeemed } = response.data;
# post:     pm.test("totalSold和totalRedeemed为有效数值类型", () => {
# post:         // 验证字段存在且为数值（兼容整数/浮点数，排除NaN/Infinity）
# post:         pm.expect(totalSold).to.exist.and.satisfy(val => {
# post:             return typeof val === "number" && Number.isFinite(val);
# post:         }, "totalSold必须是有效数值（整数/浮点数）");
# post:         
# post:         pm.expect(totalRedeemed).to.exist.and.satisfy(val => {
# post:             return typeof val === "number" && Number.isFinite(val);
# post:         }, "totalRedeemed必须是有效数值（整数/浮点数）");
# post:     });
# post: 
# post:     // 4. 验证totalSold >= totalRedeemed
# post:     pm.test("totalSold大于等于totalRedeemed", () => {
# post:         pm.expect(totalSold).to.be.at.least(totalRedeemed, 
# post:             `totalSold(${totalSold}) 小于 totalRedeemed(${totalRedeemed})，不符合预期`);
# post:     });
# post: 
# post: } catch (e) {
# post:     // 捕获脚本执行异常，标记测试失败并输出日志
# post:     pm.test("脚本执行异常", () => {
# post:         pm.expect.fail(`后置脚本执行出错：${e.message}`);
# post:     });
# post:     console.error("脚本错误详情：", e);
# post: }
# --- step 2: 083ece80-9b25-4f4b-8cba-34f87cd3cbdd ---
# post[customScript]: try {
# post:     const responseJson = pm.response.json();
# post: 
# post:     // 基础验证（保持不变）
# post:     pm.test("响应码验证：code应为200", () => {
# post:         pm.expect(responseJson.code).to.equal(200, `code预期200，实际${responseJson.code}`);
# post:     });
# post:     pm.test("响应消息验证：message应为success", () => {
# post:         pm.expect(responseJson.message).to.equal("success", `message预期success，实际${responseJson.message}`);
# post:     });
# post:     pm.test("data.items字段验证：存在且为非空数组", () => {
# post:         pm.expect(responseJson.data).to.not.be.undefined.and.not.be.null;
# post:         pm.expect(responseJson.data.items).to.be.an("array").that.is.not.empty;
# post:     });
# post: 
# post:     // 核心调整：匹配范围扩大为firstName或email包含“linda”
# post:     const searchKeyword = "linda";
# post:     const items = responseJson.data.items;
# post:     let failItems = [];
# post: 
# post:     items.forEach((outerItem, outerIndex) => {
# post:         if (outerItem.items && Array.isArray(outerItem.items)) {
# post:             outerItem.items.forEach((innerItem, innerIndex) => {
# post:                 // 提取firstName和email并转小写
# post:                 const firstName = (innerItem.firstName || "").toLowerCase().trim();
# post:                 const email = (innerItem.email || "").toLowerCase().trim();
# post:                 // 检查任意一个字段包含关键字
# post:                 const isMatch = firstName.includes(searchKeyword.toLowerCase()) 
# post:                               || email.includes(searchKeyword.toLowerCase());
# post:                 
# post:                 if (!isMatch) {
# post:                     failItems.push({
# post:                         outerIndex: outerIndex + 1,
# post:                         innerIndex: innerIndex + 1,
# post:                         orderNumber: outerItem.orderNumber,
# post:                         firstName: innerItem.firstName,
# post:                         email: innerItem.email,
# post:                         itemId: innerItem.id
# post:                     });
# post:                 }
# post:             });
# post:         } else {
# post:             failItems.push({
# post:                 outerIndex: outerIndex + 1,
# post:                 orderNumber: outerItem.orderNumber,
# post:                 error: "内层items字段缺失或非数组"
# post:             });
# post:         }
# post:     });
# post: 
# post:     pm.test(`所有搜索结果的firstName/email包含关键字「${searchKeyword}」`, () => {
# post:         if (failItems.length > 0) {
# post:             console.error("❌ 不符合条件的条目：", JSON.stringify(failItems, null, 2));
# post:             pm.expect.fail(
# post:                 `发现${failItems.length}条结果的firstName/email均未包含关键字「${searchKeyword}」，详情见控制台。\n` +
# post:                 `失败条目示例：${JSON.stringify(failItems[0], null, 2)}`
# post:             );
# post:         } else {
# post:             console.log(`✅ 所有${items.length}条搜索结果均符合匹配条件`);
# post:         }
# post:     });
# post: 
# post: } catch (error) {
# post:     pm.test("脚本执行异常", () => {
# post:         pm.expect.fail(`❌ 错误信息：${error.message}`);
# post:     });
# post: }
# --- step 3: 394dd60a-39a0-4a7e-bd60-8f8d2632a1b0 ---
# post[customScript]: try {
# post:     // 1. 解析响应体为JSON对象
# post:     const responseJson = pm.response.json();
# post:     // 定义本次搜索关键字
# post:     const searchKeyword = "PR79024";
# post: 
# post:     // 2. 基础验证：接口响应状态正常
# post:     pm.test("响应码验证：code = 200", () => {
# post:         pm.expect(responseJson.code, `code预期200，实际${responseJson.code || '无'}`).to.equal(200);
# post:     });
# post:     pm.test("响应消息验证：message = success", () => {
# post:         pm.expect(responseJson.message, `message预期success，实际${responseJson.message || '无'}`).to.equal("success");
# post:     });
# post:     pm.test("data字段验证：存在且包含核心分页/列表字段", () => {
# post:         pm.expect(responseJson.data, "data字段缺失").to.not.be.undefined.and.not.be.null;
# post:         // 验证分页和列表字段存在
# post:         pm.expect(responseJson.data.items, "data.items字段缺失").to.be.an("array");
# post:         pm.expect(responseJson.data.totalCount, "data.totalCount字段缺失").to.be.a("number");
# post:         pm.expect(responseJson.data.pageNumber, "data.pageNumber字段缺失").to.be.a("number");
# post:         pm.expect(responseJson.data.pageSize, "data.pageSize字段缺失").to.be.a("number");
# post:     });
# post: 
# post:     // 3. 核心验证：搜索结果匹配关键字「PR79024」
# post:     const dataItems = responseJson.data.items;
# post:     // 筛选出orderNumber等于PR79024的条目
# post:     const matchedItems = dataItems.filter(item => item.orderNumber === searchKeyword);
# post: 
# post:     pm.test(`搜索结果包含关键字「${searchKeyword}」的条目`, () => {
# post:         pm.expect(matchedItems.length, `未找到orderNumber=${searchKeyword}的条目`).to.be.greaterThan(0);
# post:     });
# post: 
# post:     pm.test(`搜索结果仅返回1条匹配条目（totalCount=1）`, () => {
# post:         pm.expect(dataItems.length, `预期返回1条结果，实际返回${dataItems.length}条`).to.equal(1);
# post:         pm.expect(responseJson.data.totalCount, `totalCount预期为1，实际为${responseJson.data.totalCount}`).to.equal(1);
# post:     });
# post: 
# post:     // 4. 验证匹配条目的核心字段正确性（可选，按需补充）
# post:     if (matchedItems.length > 0) {
# post:         const targetItem = matchedItems[0];
# post:         pm.test(`匹配条目核心字段验证（PR79024）`, () => {
# post:             // 验证id/orderId和orderNumber关联的唯一性
# post:             pm.expect(targetItem.id, "条目id与orderId不一致").to.equal(targetItem.orderId);
# post:             pm.expect(targetItem.type, "条目type预期为order").to.equal("order");
# post:             // 验证内层items非空（确保订单包含用户信息）
# post:             pm.expect(targetItem.items, "内层items为空").to.be.an("array").that.is.not.empty;
# post:             // 验证内层条目的id和外层一致
# post:             pm.expect(targetItem.items[0].id, "内层条目id与外层不一致").to.equal(targetItem.id);
# post:         });
# post:     }
# post: 
# post: } catch (error) {
# post:     // 捕获解析/执行异常，标记测试失败
# post:     pm.test("脚本执行异常", () => {
# post:         pm.expect.fail(`❌ 错误原因：${error.message}`);
# post:     });
# post: }




import json

from core.assertions import expect

def test_linda_t4424_verify_the_search_function_of_the_qr_scanner_page(ctx):
    """Apifox case #7676278: Linda_T4424_Verify_the_search_function_of_the_QR_scanner_page"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 77e37c25-4f20-4147-a480-5e6e7598d629
    _resp1 = ctx.api.orders.verification_ticket_statistics(body=None, params={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXJhdG9ySWQiOiJmNGE2YjNmMS1kOWU4LTQ1N2MtODFjYi1hODg1MWViN2VlNGUiLCJldmVudElkIjoiNzllYzY4MDMtOWYxMC00OTM3LTlmZGUtODIzNDY4ZTBlNTQzIn0.KqN5axrnb-eU_Zhbkrp9RjcAQpYaauuewImSbdv5vmk'}, token='linda01_token')
    # step 2: 083ece80-9b25-4f4b-8cba-34f87cd3cbdd
    _resp2 = ctx.api.orders.verification_search(body=None, params={'search': 'linda', 'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXJhdG9ySWQiOiJmNGE2YjNmMS1kOWU4LTQ1N2MtODFjYi1hODg1MWViN2VlNGUiLCJldmVudElkIjoiNzllYzY4MDMtOWYxMC00OTM3LTlmZGUtODIzNDY4ZTBlNTQzIn0.KqN5axrnb-eU_Zhbkrp9RjcAQpYaauuewImSbdv5vmk', 'pageSize': '30', 'pageNumber': '1'}, token='linda01_token')
    # step 3: 394dd60a-39a0-4a7e-bd60-8f8d2632a1b0
    _resp3 = ctx.api.orders.verification_search(body=None, params={'search': 'PR79024', 'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXJhdG9ySWQiOiJmNGE2YjNmMS1kOWU4LTQ1N2MtODFjYi1hODg1MWViN2VlNGUiLCJldmVudElkIjoiNzllYzY4MDMtOWYxMC00OTM3LTlmZGUtODIzNDY4ZTBlNTQzIn0.KqN5axrnb-eU_Zhbkrp9RjcAQpYaauuewImSbdv5vmk', 'pageSize': '30', 'pageNumber': '1'}, token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    # ---- step1: 核销统计 ----
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp1.status_code == 200, f"HTTP状态码应为200，实际={_resp1.status_code}"
    assert _j1.get('code') == 200, f"业务码应为200，实际={_j1.get('code')!r}"
    assert _j1.get('message') == 'success', f"message应为success，实际={_j1.get('message')!r}"
    assert _j1.get('request_id'), f"request_id应为非空，实际={_j1.get('request_id')!r}"
    _d1 = _j1.get('data') or {}
    assert isinstance(_d1, dict) and len(_d1) > 0, "data 应为非空对象"
    assert _d1.get('totalSold') is not None and isinstance(_d1.get('totalSold'), (int, float)), f"totalSold 应为有效数值，实际={_d1.get('totalSold')!r}"
    assert _d1.get('totalRedeemed') is not None and isinstance(_d1.get('totalRedeemed'), (int, float)), f"totalRedeemed 应为有效数值，实际={_d1.get('totalRedeemed')!r}"
    assert _d1.get('totalSold') >= _d1.get('totalRedeemed'), f"totalSold({_d1.get('totalSold')}) 应 >= totalRedeemed({_d1.get('totalRedeemed')})"
    # ---- step2: search=linda 搜索结果匹配 ----
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"code预期200，实际={_j2.get('code')!r}"
    assert _j2.get('message') == 'success', f"message预期success，实际={_j2.get('message')!r}"
    _d2 = _j2.get('data')
    assert _d2 is not None, "data 缺失"
    _items2 = _d2.get('items') or []
    assert len(_items2) > 0, "data.items 应为非空数组"
    _fail2 = []
    for _oi, _outer in enumerate(_items2):
        _inner_list = _outer.get('items')
        if not isinstance(_inner_list, list):
            _fail2.append({'outerIndex': _oi + 1, 'orderNumber': _outer.get('orderNumber'), 'error': '内层items字段缺失或非数组'})
            continue
        for _ii, _inner in enumerate(_inner_list):
            _fn = (_inner.get('firstName') or '').lower().strip()
            _em = (_inner.get('email') or '').lower().strip()
            if 'linda' not in _fn and 'linda' not in _em:
                _fail2.append({'outerIndex': _oi + 1, 'innerIndex': _ii + 1, 'orderNumber': _outer.get('orderNumber'), 'firstName': _inner.get('firstName'), 'email': _inner.get('email'), 'itemId': _inner.get('id')})
    assert not _fail2, f"发现{len(_fail2)}条结果的firstName/email未包含关键字「linda」，示例：{_fail2[0] if _fail2 else ''}"
    # ---- step3: search=PR79024 精确匹配 ----
    _j3 = _resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}
    assert _j3.get('code') == 200, f"code预期200，实际={_j3.get('code')!r}"
    assert _j3.get('message') == 'success', f"message预期success，实际={_j3.get('message')!r}"
    _d3 = _j3.get('data')
    assert _d3 is not None, "data 字段缺失"
    assert isinstance(_d3.get('items'), list), "data.items 字段缺失或非数组"
    assert isinstance(_d3.get('totalCount'), (int, float)), "data.totalCount 字段缺失或非数字"
    assert isinstance(_d3.get('pageNumber'), (int, float)), "data.pageNumber 字段缺失或非数字"
    assert isinstance(_d3.get('pageSize'), (int, float)), "data.pageSize 字段缺失或非数字"
    _data3 = _d3.get('items') or []
    _matched = [it for it in _data3 if it.get('orderNumber') == 'PR79024']
    assert len(_matched) > 0, "未找到 orderNumber=PR79024 的条目"
    assert len(_data3) == 1, f"预期返回1条结果，实际返回{len(_data3)}条"
    assert _d3.get('totalCount') == 1, f"totalCount预期为1，实际={_d3.get('totalCount')!r}"
    _t3 = _matched[0]
    assert _t3.get('id') == _t3.get('orderId'), f"条目id与orderId不一致：{_t3.get('id')!r} vs {_t3.get('orderId')!r}"
    assert _t3.get('type') == 'order', f"条目type预期为order，实际={_t3.get('type')!r}"
    assert isinstance(_t3.get('items'), list) and len(_t3.get('items') or []) > 0, "内层items为空"
    assert (_t3.get('items') or [])[0].get('id') == _t3.get('id'), "内层条目id与外层不一致"
