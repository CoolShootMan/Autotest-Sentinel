"""Migrated from Apifox case #8607884. Source folder: Event and ticket and redeemed/Co-host."""
# Apifox Case ID: 8607884  (traceability only — not needed to run)
NAME = "Verify the Co-host can be added and delete"
TAGS = ["p2", "event_and_ticket_and_redeemed_co_host", "suite:linda"]
PRIORITY = 2


CASE_ID = 8607884
ENV_NAME = "Release"

# --- step 1: a460e4d7-1877-4965-a029-94f3dc89a5e5 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 在 items 数组中查找 title 为 "event-for-API-testing" 的事件
# post: const targetEvent = responseData.data.items.find(
# post:     item => item.title === "event-for-API-testing"
# post: );
# post: 
# post: // 3. 断言并设置环境变量 event_id
# post: pm.test("找到 title 为 'event-for-API-testing' 的事件并提取 id 设置为 event_id", function () {
# post:     // 断言找到目标事件
# post:     pm.expect(targetEvent, "未找到 title 为 'event-for-API-testing' 的事件").to.not.be.undefined;
# post:     pm.expect(targetEvent.id, "提取的 id 为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 获取并设置环境变量
# post:     const eventId = targetEvent.id;
# post:     pm.environment.set("event_id", eventId);
# post:     
# post:     console.log("已成功提取 event_id:", eventId);
# post: });
# --- step 2: 9d49f954-3250-44a2-aaf7-36a03af013ce ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 断言 HTTP 状态码与基础返回结构
# post: pm.test("响应状态码为 200 且操作成功", function () {
# post:     pm.response.to.have.status(201);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post:     pm.expect(responseData.request_id).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 3. 断言 data 数据业务结构与字段类型，并保存 co-hostid
# post: pm.test("验证返回的 data 字段及其类型并设置环境变量 co-hostid", function () {
# post:     const data = responseData.data;
# post: 
# post:     // 校验 data 存在且为对象
# post:     pm.expect(data).to.be.an('object').that.is.not.null;
# post: 
# post:     // 校验主要 ID 字段
# post:     pm.expect(data.id, "id 应为非空字符串").to.be.a('string').and.not.empty;
# post:     pm.expect(data.eventId, "eventId 应与请求的环境变量匹配").to.be.a('string').and.not.empty;
# post:     pm.expect(data.curatorId).to.be.a('string').and.not.empty;
# post:     pm.expect(data.collaboratorUserId).to.be.a('string').and.not.empty;
# post: 
# post:     // 保存 data.id 到环境变量 co-hostid
# post:     pm.environment.set("co-hostid", data.id);
# post:     console.log("已成功将 data.id 设置为环境变量 {{co-hostid}}:", data.id);
# post: 
# post:     // 校验业务属性
# post:     pm.expect(data.role).to.eql("BASIC");
# post:     pm.expect(data.identifier).to.be.a('string').that.includes("@");
# post: 
# post:     // 校验时间字段
# post:     pm.expect(data.createdAt).to.be.a('string').and.not.empty;
# post:     pm.expect(data.updatedAt).to.be.a('string').and.not.empty;
# post:     pm.expect(data.deletedAt).to.be.null;
# post: });
# --- step 3: ab2bca35-78b5-48bd-81b0-8ce3eda4e482 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 获取上一步保存在环境变量中的 event_id
# post: const expectedEventId = pm.environment.get("event_id");
# post: 
# post: // 3. 断言查找指定 title 的 item 并比对 id
# post: pm.test("验证 title 为 'event-for-API-testing' 的 items.id 与 {{event_id}} 一致", function () {
# post:     const items = responseData.data?.items;
# post:     pm.expect(items, "返回的 items 数组为空或不存在").to.be.an('array').that.is.not.empty;
# post:     pm.expect(expectedEventId, "环境变量 {{event_id}} 未定义或为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 根据 title 精确匹配目标项
# post:     const targetItem = items.find(item => item.title === "event-for-API-testing");
# post: 
# post:     // 断言能找到该标题的事件
# post:     pm.expect(targetItem, "未在返回的 items 中找到 title 为 'event-for-API-testing' 的数据").to.not.be.undefined;
# post: 
# post:     // 校验其 id 是否与环境变量一致
# post:     pm.expect(targetItem.id).to.eql(expectedEventId);
# post: 
# post:     console.log(`校验成功！匹配到事件 '${targetItem.title}'，其 id [${targetItem.id}] 与环境变量 [${expectedEventId}] 完全一致。`);
# post: });
# --- step 4: 84447ab5-4e1c-4bb4-b330-e95e57529c55 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 断言 HTTP 状态码与基础结构
# post: pm.test("响应状态码为 200 且操作成功", function () {
# post:     pm.response.to.have.status(200);
# post:     pm.expect(responseData.code).to.eql(200);
# post:     pm.expect(responseData.message).to.eql("success");
# post:     pm.expect(responseData.request_id).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 3. 断言 data.success 字段
# post: pm.test("验证返回的 data.success 为 true", function () {
# post:     pm.expect(responseData.data).to.be.an('object').that.is.not.null;
# post:     pm.expect(responseData.data.success).to.be.true;
# post: });




import json

from core.assertions import expect

def test_linda_t5139_verify_the_co_host_can_be_added_and_delete(ctx):
    """Apifox case #8607884: Linda_T5139_Verify_the_Co_host_can_be_added_and_delete"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: a460e4d7-1877-4965-a029-94f3dc89a5e5
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    _t1 = next((it for it in (_j1.get('data') or {}).get('items') or [] if it.get('title') == 'event-for-API-testing'), None)
    assert _t1 is not None, "未找到 title 为 'event-for-API-testing' 的事件"
    assert isinstance(_t1.get('id'), str) and _t1.get('id'), f"提取的 id 为空，实际={_t1.get('id')!r}"
    vars['event_id'] = _t1.get('id')
    # step 2: 9d49f954-3250-44a2-aaf7-36a03af013ce
    _resp2 = ctx.api.events.create(body='{\n    "eventId": "{{event_id}}",\n    "identifier": "{{UIauto_coseller_email}}",\n    "role": "BASIC"\n}', token='yuxiao999_token')
    ctx.extract('co-hostid', _resp2, '$.data.id')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    assert _resp2.status_code == 201, f"HTTP状态码应为201，实际={_resp2.status_code}"
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"code预期200，实际={_j2.get('code')!r}"
    assert _j2.get('message') == 'success', f"message预期success，实际={_j2.get('message')!r}"
    assert isinstance(_j2.get('request_id'), str) and _j2.get('request_id'), f"request_id应为非空字符串，实际={_j2.get('request_id')!r}"
    _d2 = _j2.get('data')
    assert isinstance(_d2, dict) and _d2 is not None, "data 应为非空对象"
    assert isinstance(_d2.get('id'), str) and _d2.get('id'), "id 应为非空字符串"
    assert isinstance(_d2.get('eventId'), str) and _d2.get('eventId'), "eventId 应为非空字符串"
    assert isinstance(_d2.get('curatorId'), str) and _d2.get('curatorId'), "curatorId 应为非空字符串"
    assert isinstance(_d2.get('collaboratorUserId'), str) and _d2.get('collaboratorUserId'), "collaboratorUserId 应为非空字符串"
    assert _d2.get('role') == 'BASIC', f"role预期BASIC，实际={_d2.get('role')!r}"
    assert isinstance(_d2.get('identifier'), str) and '@' in _d2.get('identifier'), f"identifier应为含@的字符串，实际={_d2.get('identifier')!r}"
    assert isinstance(_d2.get('createdAt'), str) and _d2.get('createdAt'), "createdAt 应为非空字符串"
    assert isinstance(_d2.get('updatedAt'), str) and _d2.get('updatedAt'), "updatedAt 应为非空字符串"
    assert _d2.get('deletedAt') is None, f"deletedAt 应为null，实际={_d2.get('deletedAt')!r}"
    # step 3: ab2bca35-78b5-48bd-81b0-8ce3eda4e482
    _resp3 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao998_token')
    # step 4: 84447ab5-4e1c-4bb4-b330-e95e57529c55
    _resp4 = ctx.api.events.by_co_hostid(body=None, token='yuxiao999_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    # ---- step3: 校验事件列表中的 event_id 一致 ----
    _j3 = _resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}
    _items3 = (_j3.get('data') or {}).get('items') or []
    assert len(_items3) > 0, "返回的 items 数组为空或不存在"
    _ev_id = vars.get('event_id')
    assert isinstance(_ev_id, str) and _ev_id, "环境变量 {{event_id}} 未定义或为空"
    _t3 = next((it for it in _items3 if it.get('title') == 'event-for-API-testing'), None)
    assert _t3 is not None, "未在返回的 items 中找到 title 为 'event-for-API-testing' 的数据"
    assert _t3.get('id') == _ev_id, f"匹配事件 id {_t3.get('id')!r} 与 {{event_id}} {_ev_id!r} 不一致"
    # ---- step4: 删除 co-host ----
    assert _resp4.status_code == 200, f"HTTP状态码应为200，实际={_resp4.status_code}"
    _j4 = _resp4.json() if _resp4.headers.get('content-type', '').startswith('application/json') else {}
    assert _j4.get('code') == 200, f"code预期200，实际={_j4.get('code')!r}"
    assert _j4.get('message') == 'success', f"message预期success，实际={_j4.get('message')!r}"
    assert isinstance(_j4.get('request_id'), str) and _j4.get('request_id'), f"request_id应为非空字符串，实际={_j4.get('request_id')!r}"
    _d4 = _j4.get('data')
    assert isinstance(_d4, dict) and _d4 is not None, "data 应为非空对象"
    assert _d4.get('success') is True, f"data.success 应为true，实际={_d4.get('success')!r}"
