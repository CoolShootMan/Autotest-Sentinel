"""ONES case: Verify Recipient Email default value and required logic"""
NAME = "Verify Recipient Email default value and required logic"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "mxPnV6YV"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4281_verify_recipient_email_logic(ctx: "Context"):
    """ONES case #mxPnV6YV: Verify Recipient Email default value and required logic"""
    vars = ctx
    # form without recipientEmail can be created, but submission fails (no destination)
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4281_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')

    _bad = ctx.api.forms.submit(body={
        "contactId": vars['t4281_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "Bob"},
        ],
    })
    expect(_bad).json('$.code').not_equals('200')

    # once a recipient email is configured, submission succeeds
    _up = ctx.api.forms.update_by_id(id=vars['t4281_form_id'], body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [{"field": "SHORT_ANSWER", "title": "Name", "required": True}],
    }, token='linda997_token')
    expect(_up).json('$.code').equals('200')

    _good = ctx.api.forms.submit(body={
        "contactId": vars['t4281_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "Bob"},
        ],
    })
    expect(_good).json('$.code').equals('200')
    expect(_good).json('$.data.success').equals(True)

    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4281_form_id']})
    if _list.json_safe().get('data', {}).get('totalCount', 0):
        ctx.extract('t4281_inq_id', _list, '$.data.items[0].id')
        ctx.api.forms.delete_inquiries(body={"ids": [vars['t4281_inq_id']]}, token='linda997_token')

    _del = ctx.api.forms.delete_by_id(id=vars['t4281_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

