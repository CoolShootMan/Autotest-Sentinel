"""(Venue map) Verify the Co-host can be added and delete."""
NAME = "(Linda)(Venue map)T5139 Verify the Co-host can be added and delete"
TAGS = ["p2", "event_and_ticket_and_redeemed_co_host", "suite:linda"]
PRIORITY = 2

CASE_ID = 8709242
ENV_NAME = "Release"

import re
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5139_venue_map_verify_the_co_host_can_be_added_and_delete(ctx: "Context"):
    """验证 Co-host 可以添加和删除。

    流程：
    1. 查找预置 event（title = "event-for-api-auto-venue-map"）
    2. 添加 Co-host（BASIC 角色）
    3. Co-seller 视角验证 event 可见
    4. 删除 Co-host
    """
    vars = ctx

    # step 1: 查找预置 event，提取 event_id
    if 'event_title' not in vars or not vars['event_title']:
        vars['event_title'] = 'event-for-api-auto-venue-map'
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='linda999_token')
    _j1: dict[str, Any] = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    _t1 = next((it for it in (_j1.get('data') or {}).get('items') or [] if it.get('title') == vars['event_title']), None)
    assert _t1 is not None, f"列表中未找到 title 为 [{vars['event_title']}] 的事件"
    vars['event_id'] = _t1.get('id')
    vars['event_title'] = _t1.get('title')

    # step 2: 添加 Co-host（BASIC 角色）
    _resp2 = ctx.api.events.create(body={
        "eventId": "{{event_id}}",
        "identifier": "{{UIauto_coseller_email}}",
        "role": "BASIC",
    }, token='linda999_token')
    ctx.extract('co-hostid', _resp2, '$.data.id')

    # 断言：Co-host 添加成功
    assert _resp2.status_code == 201, f"HTTP状态码应为201，实际={_resp2.status_code}"
    _j2: dict[str, Any] = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"code预期200，实际={_j2.get('code')!r}"
    assert _j2.get('message') == 'success', f"message预期success，实际={_j2.get('message')!r}"
    assert isinstance(_j2.get('request_id'), str) and _j2.get('request_id'), "request_id 应为非空字符串"
    _d2 = _j2.get('data')
    assert isinstance(_d2, dict) and _d2 is not None, "data 应为非空对象"
    assert isinstance(_d2.get('id'), str) and _d2.get('id'), "id 应为非空字符串"
    assert isinstance(_d2.get('eventId'), str) and _d2.get('eventId'), "eventId 应为非空字符串"
    assert isinstance(_d2.get('curatorId'), str) and _d2.get('curatorId'), "curatorId 应为非空字符串"
    assert isinstance(_d2.get('collaboratorUserId'), str) and _d2.get('collaboratorUserId'), "collaboratorUserId 应为非空字符串"
    assert _d2.get('role') == 'BASIC', f"role 预期 BASIC，实际={_d2.get('role')!r}"
    _idt2 = _d2.get('identifier')
    assert isinstance(_idt2, str) and '@' in _idt2, f"identifier 应为含@的字符串，实际={_idt2!r}"
    assert isinstance(_d2.get('createdAt'), str) and _d2.get('createdAt'), "createdAt 应为非空字符串"
    assert isinstance(_d2.get('updatedAt'), str) and _d2.get('updatedAt'), "updatedAt 应为非空字符串"
    assert _d2.get('deletedAt') is None, f"deletedAt 应为 null，实际={_d2.get('deletedAt')!r}"

    # step 3: Co-seller 视角验证 event 可见
    _resp3 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='linda998_token')
    _j3: dict[str, Any] = _resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}
    _items3: list[Any] = (_j3.get('data') or {}).get('items') or []
    assert len(_items3) > 0, "返回的 items 数组为空或不存在"

    # 断言：Co-seller 能看到该 event
    _ev_id = vars.get('event_id')
    _ev_title = vars.get('event_title')
    assert isinstance(_ev_id, str) and _ev_id, "event_id 未定义或为空"
    assert isinstance(_ev_title, str) and _ev_title, "event_title 未定义或为空"
    _clean_expected = re.sub(r'\s+', ' ', _ev_title).strip()
    _t3 = None
    for _it in _items3:
        if not _it.get('title'):
            continue
        _clean_it = re.sub(r'\s+', ' ', _it.get('title')).strip()
        if _it.get('title') == _ev_title or _clean_it == _clean_expected:
            _t3 = _it
            break
    assert _t3 is not None, f"未在 Co-seller 事件列表中找到标题 '{_ev_title}' 的事件"
    assert _t3.get('id') == _ev_id, f"事件 id {_t3.get('id')!r} 与 event_id {_ev_id!r} 不一致"

    # step 4: 删除 Co-host
    _resp4 = ctx.api.events.by_co_hostid(body=None, token='linda999_token')

    # 断言：Co-host 删除成功
    assert _resp4.status_code == 200, f"HTTP状态码应为200，实际={_resp4.status_code}"
    _j4: dict[str, Any] = _resp4.json() if _resp4.headers.get('content-type', '').startswith('application/json') else {}
    assert _j4.get('code') == 200, f"code预期200，实际={_j4.get('code')!r}"
    assert _j4.get('message') == 'success', f"message预期success，实际={_j4.get('message')!r}"
    assert isinstance(_j4.get('request_id'), str) and _j4.get('request_id'), "request_id 应为非空字符串"
    _d4 = _j4.get('data')
    assert isinstance(_d4, dict) and _d4 is not None, "data 应为非空对象"
    assert _d4.get('success') is True, f"data.success 应为 true，实际={_d4.get('success')!r}"
