"""ONES case: Verify time range filter correctly filters submission records"""
NAME = "Verify time range filter correctly filters submission records"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "S2xRF9NM"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4538_verify_time_range_filter(ctx: "Context"):
    """ONES case #S2xRF9NM: Verify time range filter correctly filters submission records"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4538_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')

    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4538_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "Tim"},
        ],
    })
    expect(_sub).json('$.data.success').equals(True)

    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    day = timedelta(days=1)
    # broad window covering the submission
    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={
        'formId': vars['t4538_form_id'],
        'startTime': (now - day).isoformat().replace('+00:00', 'Z'),
        'endTime': (now + day).isoformat().replace('+00:00', 'Z'),
    })
    expect(_list).json('$.code').equals('200')
    expect(_list).json('$.data.totalCount').greater_than(0)

    # future window must not include today's submission
    _future = ctx.api.forms.list_inquiry(token='linda997_token', params={
        'formId': vars['t4538_form_id'],
        'startTime': (now + day).isoformat().replace('+00:00', 'Z'),
        'endTime': (now + 2 * day).isoformat().replace('+00:00', 'Z'),
    })
    expect(_future).json('$.data.totalCount').equals(0)

    _all = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4538_form_id']})
    ids = [it['id'] for it in _all.json_safe()['data']['items']]
    if ids:
        ctx.api.forms.delete_inquiries(body={"ids": ids}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4538_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

