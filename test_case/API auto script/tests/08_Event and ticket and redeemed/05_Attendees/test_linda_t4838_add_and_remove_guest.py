"""Migrated from Apifox case #8607595. Source folder: Event and ticket and redeemed/Attendees."""
# Apifox Case ID: 8607595  (traceability only — not needed to run)
NAME = "Add and Remove guest"
TAGS = ["p2", "event_and_ticket_and_redeemed_attendees", "suite:linda"]
PRIORITY = 2


CASE_ID = 8607595
ENV_NAME = "Release"

# --- step 1: c4f45db2-78e3-441b-95c7-9e347f204312 ---
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
# --- step 2: e2202c93-05de-4d9d-aa0f-dee2a7ec8941 ---
# pre: // 1. 常见有效 US 区号 (Area Code: [2-9]XX)
# pre: const areaCodes = ['202', '312', '415', '650', '212', '310', '408', '213', '707'];
# pre: const randomAreaCode = areaCodes[Math.floor(Math.random() * areaCodes.length)];
# pre: 
# pre: // 2. 生成局号 Exchange Code (第一位必须为 2-9，范围 200-999)
# pre: const exchangeCode = Math.floor(200 + Math.random() * 800);
# pre: 
# pre: // 3. 生成 4 位线路号 Subscriber Number (0000-9999)
# pre: const subscriberNum = Math.floor(1000 + Math.random() * 9000);
# pre: 
# pre: // 4. 组合成标准的 E.164 格式号码，如: +14152345678
# pre: const usPhoneNumber = `+1${randomAreaCode}${exchangeCode}${subscriberNum}`;
# pre: 
# pre: // 5. 设置变量（如果请求 Body 里用 {{usPhoneNumber}}，用 pm.variables 或 pm.environment 均可）
# pre: pm.variables.set("usPhoneNumber", usPhoneNumber);
# pre: pm.environment.set("usPhoneNumber", usPhoneNumber); // 推荐同时设置环境变量，确保跨区域请求可用
# pre: 
# pre: console.log("生成的合规 US 手机号:", usPhoneNumber);
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 断言并设置环境变量 guest_id
# post: pm.test("成功提取 data.id 并设置为环境变量 guest_id", function () {
# post:     // 基础校验：断言 responseData.data 及其 id 字段存在
# post:     pm.expect(responseData.data).to.be.an('object');
# post:     pm.expect(responseData.data.id, "data.id 不存在或为空").to.be.a('string').and.not.empty;
# post: 
# post:     // 获取并设置环境变量
# post:     const guestId = responseData.data.id;
# post:     pm.environment.set("guest_id", guestId);
# post: 
# post:     console.log("已成功提取 guest_id:", guestId);
# post: });
# --- step 3: 962c7735-9f52-41dc-9bf9-ad892ab6de30 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import random
import json

from core.assertions import expect

def test_linda_t4838_add_and_remove_guest(ctx):
    """Apifox case #8607595: Linda_T4838_Add_and_Remove_guest"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: c4f45db2-78e3-441b-95c7-9e347f204312
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    # --- post 脚本: 从响应 data.items 中提取 event_id ---
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    _items1 = (_j1.get('data') or {}).get('items') or []
    _target1 = next((it for it in _items1 if it.get('title') == "event-for-API-testing"), None)
    assert _target1 is not None, "未找到匹配的事件"
    _eid1 = _target1.get('id')
    assert isinstance(_eid1, str) and _eid1, "event_id 为空"
    vars['event_id'] = _eid1
    _areaCodes = ["202","312","415","650","212","310","408","213","707"]
    vars['usPhoneNumber'] = '+1' + random.choice(_areaCodes) + str(random.randint(200, 999)) + str(random.randint(1000, 9999))
    vars['randomEmail'] = 'qa_guests_' + str(random.randint(100000, 999999)) + '@test.com'
    # step 2: e2202c93-05de-4d9d-aa0f-dee2a7ec8941
    _resp2 = ctx.api.events.guests(body='{\n    "phoneNumber": "{{usPhoneNumber}}",\n    "email": "{{randomEmail}}",\n    "firstName": "{{$randomFirstName}}",\n    "lastName": "{{$randomLastName}}",\n    "groupIds": [],\n    "eventId": "{{event_id}}"\n}', token='yuxiao999_token')
    # --- post 脚本: 提取 guest_id ---
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    assert isinstance(_j2.get('data'), dict), f"data 不是对象: {_j2!r}"
    _gid2 = _j2['data'].get('id')
    assert isinstance(_gid2, str) and _gid2, f"guest_id 为空: {_j2.get('data')!r}"
    vars['guest_id'] = _gid2
    # step 3: 962c7735-9f52-41dc-9bf9-ad892ab6de30
    _resp3 = ctx.api.events.guests_batch(body='{"guestIds":["{{guest_id}}"],"eventId":"{{event_id}}"}', token='yuxiao999_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
