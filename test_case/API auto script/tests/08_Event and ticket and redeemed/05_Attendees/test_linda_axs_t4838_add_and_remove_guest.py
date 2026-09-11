"""Migrated from Apifox case #8709199. Source folder: Event and ticket and redeemed/Attendees."""
# Apifox Case ID: 8709199  (traceability only — not needed to run)
NAME = "(Linda) (AXS)T4838 Add and Remove guest"
TAGS = ["p2", "event_and_ticket_and_redeemed_attendees", "suite:linda"]
PRIORITY = 2


CASE_ID = 8709199
ENV_NAME = "Release"

# --- step 1: cf2e1886-68cf-47e0-94d7-b2c2b33da7aa ---
# post[customScript]: // 1. 解析响应 Body
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 查找第一个 platform 为 "AXS" 的项目
# post: const axsEvent = responseData.data.items.find(item => item.platform === "AXS");
# post: 
# post: if (axsEvent) {
# post:     // 3. 设置环境变量
# post:     pm.environment.set("event_id", axsEvent.id);
# post:     pm.environment.set("event_title", axsEvent.title);
# post: 
# post:     console.log("成功提取第一个 AXS 项目：", axsEvent.title, axsEvent.id);
# post: } else {
# post:     console.warn("未找到 platform 为 AXS 的数据");
# post: }
# --- step 2: 0396addf-c425-4c88-a42a-00a6e1a1e5b5 ---
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
# --- step 3: a858fb40-ec56-43c2-94f5-38cb70174f2c ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import random
import json

from core.assertions import expect

def test_linda_axs_t4838_add_and_remove_guest(ctx):
    """Apifox case #8709199: Linda_AXS_T4838_Add_and_Remove_guest"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: cf2e1886-68cf-47e0-94d7-b2c2b33da7aa
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    # --- post 脚本: 从响应 data.items 中提取 event_id ---
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    _items1 = (_j1.get('data') or {}).get('items') or []
    _target1 = next((it for it in _items1 if it.get('platform') == "AXS"), None)
    assert _target1 is not None, "未找到匹配的事件"
    _eid1 = _target1.get('id')
    assert isinstance(_eid1, str) and _eid1, "event_id 为空"
    vars['event_id'] = _eid1
    vars['event_title'] = _target1.get('title')
    _areaCodes = ["202","312","415","650","212","310","408","213","707"]
    vars['usPhoneNumber'] = '+1' + random.choice(_areaCodes) + str(random.randint(200, 999)) + str(random.randint(1000, 9999))
    vars['randomEmail'] = 'qa_guests_' + str(random.randint(100000, 999999)) + '@test.com'
    # step 2: 0396addf-c425-4c88-a42a-00a6e1a1e5b5
    _resp2 = ctx.api.events.guests(body='{\n    "phoneNumber": "{{usPhoneNumber}}",\n    "email": "{{randomEmail}}",\n    "firstName": "{{$randomFirstName}}",\n    "lastName": "{{$randomLastName}}",\n    "groupIds": [],\n    "eventId": "{{event_id}}"\n}', token='yuxiao999_token')
    # --- post 脚本: 提取 guest_id ---
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    assert isinstance(_j2.get('data'), dict), f"data 不是对象: {_j2!r}"
    _gid2 = _j2['data'].get('id')
    assert isinstance(_gid2, str) and _gid2, f"guest_id 为空: {_j2.get('data')!r}"
    vars['guest_id'] = _gid2
    # step 3: a858fb40-ec56-43c2-94f5-38cb70174f2c
    _resp3 = ctx.api.events.guests_batch(body='{"guestIds":["{{guest_id}}"],"eventId":"{{event_id}}"}', token='yuxiao999_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
