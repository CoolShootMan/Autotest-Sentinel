"""(Venue map) T4838 Add and Remove guest."""
NAME = "(Linda)(Venue map)T4838 Add and Remove guest"
TAGS = ["p2", "event_and_ticket_and_redeemed_attendees", "suite:linda"]
PRIORITY = 2

CASE_ID = 8709199
ENV_NAME = "Release"

import random
from typing import Any, TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_linda_venue_map_t4838_add_and_remove_guest(ctx: "Context"):
    """验证 Guest 可以添加和删除。

    流程：
    1. 查找预置 event（title = "event-for-api-auto-venue-map"）
    2. 生成随机手机号和邮箱，添加 guest
    3. 删除 guest
    """
    vars = ctx

    # step 1: 查找预置 event，提取 event_id
    if 'event_title' not in vars or not vars['event_title']:
        vars['event_title'] = 'event-for-api-auto-venue-map'
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    _j1: dict[str, Any] = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    _items1: list[Any] = (_j1.get('data') or {}).get('items') or []
    _target1 = next((it for it in _items1 if it.get('title') == vars['event_title']), None)
    assert _target1 is not None, f"列表中未找到 title 为 [{vars['event_title']}] 的事件"
    vars['event_id'] = _target1.get('id')
    vars['event_title'] = _target1.get('title')

    # 生成随机手机号和邮箱
    _areaCodes = ["202", "312", "415", "650", "212", "310", "408", "213", "707"]
    vars['usPhoneNumber'] = '+1' + random.choice(_areaCodes) + str(random.randint(200, 999)) + str(random.randint(1000, 9999))
    vars['randomEmail'] = 'qa_guests_' + str(random.randint(100000, 999999)) + '@test.com'

    # step 2: 添加 Guest
    _resp2 = ctx.api.events.guests(body={
        "phoneNumber": "{{usPhoneNumber}}",
        "email": "{{randomEmail}}",
        "firstName": "{{$randomFirstName}}",
        "lastName": "{{$randomLastName}}",
        "groupIds": [],
        "eventId": "{{event_id}}",
    }, token='yuxiao999_token')

    # 断言：Guest 添加成功
    _j2: dict[str, Any] = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert isinstance(_j2.get('data'), dict), f"data 不是对象: {_j2!r}"
    _gid2 = _j2['data'].get('id')
    assert isinstance(_gid2, str) and _gid2, f"guest_id 为空: {_j2.get('data')!r}"
    vars['guest_id'] = _gid2

    # step 3: 删除 Guest
    _resp3 = ctx.api.events.guests_batch(body={
        "guestIds": ["{{guest_id}}"],
        "eventId": "{{event_id}}",
    }, token='yuxiao999_token')

    # 断言：Guest 删除成功
    expect(_resp3).json('$.code').equals('200')
