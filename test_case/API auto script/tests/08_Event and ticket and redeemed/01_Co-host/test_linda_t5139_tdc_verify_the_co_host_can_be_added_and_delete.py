"""Migrated from Apifox case #8709229. Source folder: Event and ticket and redeemed/Co-host."""
# Apifox Case ID: 8709229  (traceability only — not needed to run)
NAME = "(TDC)Verify the Co-host can be added and delete"
TAGS = ["p2", "event_and_ticket_and_redeemed_co_host", "suite:linda"]
PRIORITY = 2


CASE_ID = 8709229
ENV_NAME = "Release"

# --- step 1: d6baddd1-de37-49e5-ae36-f042683f841b ---
# post[customScript]: // 1. 解析响应 Body
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 查找第一个 platform 为 "TDC" 的项目
# post: const axsEvent = responseData.data.items.find(item => item.platform === "TDC");
# post: 
# post: if (axsEvent) {
# post:     // 3. 设置环境变量
# post:     pm.environment.set("event_id", axsEvent.id);
# post:     pm.environment.set("event_title", axsEvent.title);
# post: 
# post:     console.log("成功提取第一个 TDC 项目：", axsEvent.title, axsEvent.id);
# post: } else {
# post:     console.warn("未找到 platform 为 TDC 的数据");
# post: }
# --- step 2: 13bbae7b-1f91-4497-942f-22e0ead5c8b6 ---
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
# --- step 3: 55f823f2-ff85-412c-9569-35557162ed94 ---
# post[customScript]: // 1. 解析响应 JSON
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 获取环境变量中的预期值
# post: const expectedEventId = pm.environment.get("event_id");
# post: const expectedEventTitle = pm.environment.get("event_title");
# post: 
# post: // 3. 断言查找指定 title 的 item 并比对 id
# post: pm.test(`验证事件 ID 与环境变量一致 [Title: ${expectedEventTitle}]`, function () {
# post:     const items = responseData.data?.items;
# post:     
# post:     // 基础断言
# post:     pm.expect(items, "返回的 items 数组为空或不存在").to.be.an('array').that.is.not.empty;
# post:     pm.expect(expectedEventId, "环境变量 {{event_id}} 未定义或为空").to.be.a('string').that.is.not.empty;
# post:     pm.expect(expectedEventTitle, "环境变量 {{event_title}} 未定义或为空").to.be.a('string').that.is.not.empty;
# post: 
# post:     // 清理多余空格/制表符以进行稳健的比对
# post:     const cleanExpectedTitle = expectedEventTitle.replace(/\s+/g, ' ').trim();
# post: 
# post:     // 根据 title 精确匹配目标项（兼顾原值比对与去除空白后的比对）
# post:     const targetItem = items.find(item => {
# post:         if (!item.title) return false;
# post:         const cleanItemTitle = item.title.replace(/\s+/g, ' ').trim();
# post:         return item.title === expectedEventTitle || cleanItemTitle === cleanExpectedTitle;
# post:     });
# post: 
# post:     // 断言能找到该标题的事件
# post:     pm.expect(targetItem, `未在返回的 items 中找到匹配标题 '${expectedEventTitle}' 的数据`).to.not.be.undefined;
# post: 
# post:     // 校验其 id 是否与环境变量一致
# post:     pm.expect(targetItem.id).to.eql(expectedEventId);
# post: 
# post:     console.log(`[校验成功] 匹配到事件: "${targetItem.title}"，其 ID [${targetItem.id}] 与环境变量 event_id 匹配。`);
# post: });
# --- step 4: 1486948f-0ed0-480f-8d39-a74e44b25e0a ---
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
import re

from core.assertions import expect

def test_linda_t5139_tdc_verify_the_co_host_can_be_added_and_delete(ctx):
    """Apifox case #8709229: Linda_T5139_TDC_Verify_the_Co_host_can_be_added_and_delete"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: d6baddd1-de37-49e5-ae36-f042683f841b
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    _t1 = next((it for it in (_j1.get('data') or {}).get('items') or [] if it.get('platform') == 'TDC'), None)
    assert _t1 is not None, "未找到 platform 为 TDC 的项目"
    vars['event_id'] = _t1.get('id')
    vars['event_title'] = _t1.get('title')
    # --- 人工补丁：先清理该事件上遗留的同一协办人 ---
    # 本用例是「先增后删」。历史上若中途失败，协办人记录会永久遗留，此后每次运行
    # POST /event-collaborators 都返回 409「User is already a collaborator for this event」，
    # 而 409 不回传已存在记录的 id，用例本身无法自愈
    # （Release 上就遗留了一条 2026-09-08 的记录，导致本用例长期 409）。
    # 服务端有列表端点 GET /event-collaborators?eventId=…，Apifox 用例当时环境干净所以没用到；
    # 这里先按协办人邮箱清理，使用例可重复执行。
    _existing = ctx.api.events.collaborators(eventId=vars['event_id'], token='yuxiao999_token')
    for _c in ((_existing.json().get('data') or {}).get('items') or []):
        if _c.get('identifier') == ctx.get('UIauto_coseller_email'):
            ctx.api.events.by_co_hostid(path_vars={'co-hostid': _c['id']}, token='yuxiao999_token')
    # step 2: 13bbae7b-1f91-4497-942f-22e0ead5c8b6
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
    # step 3: 55f823f2-ff85-412c-9569-35557162ed94
    _resp3 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao998_token')
    # step 4: 1486948f-0ed0-480f-8d39-a74e44b25e0a
    _resp4 = ctx.api.events.by_co_hostid(body=None, token='yuxiao999_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    # ---- step3: 校验事件列表中的 event_id/event_title 一致 ----
    _j3 = _resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}
    _items3 = (_j3.get('data') or {}).get('items') or []
    assert len(_items3) > 0, "返回的 items 数组为空或不存在"
    _ev_id = vars.get('event_id')
    _ev_title = vars.get('event_title')
    assert isinstance(_ev_id, str) and _ev_id, "环境变量 {{event_id}} 未定义或为空"
    assert isinstance(_ev_title, str) and _ev_title, "环境变量 {{event_title}} 未定义或为空"
    _clean_expected = re.sub(r'\s+', ' ', _ev_title).strip()
    _t3 = None
    for _it in _items3:
        if not _it.get('title'):
            continue
        _clean_it = re.sub(r'\s+', ' ', _it.get('title')).strip()
        if _it.get('title') == _ev_title or _clean_it == _clean_expected:
            _t3 = _it
            break
    assert _t3 is not None, f"未在返回的 items 中找到匹配标题 '{_ev_title}' 的数据"
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
