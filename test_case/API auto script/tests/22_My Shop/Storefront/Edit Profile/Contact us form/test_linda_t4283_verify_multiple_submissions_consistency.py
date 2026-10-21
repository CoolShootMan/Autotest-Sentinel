"""ONES case: Verify multiple submissions and data consistency"""
NAME = "Verify multiple submissions and data consistency"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "SKfEiaeh"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4283_verify_multiple_submissions_consistency(ctx: "Context"):
    """ONES case #SKfEiaeh: Verify multiple submissions and data consistency"""
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
    ctx.extract('t4283_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')

    # submit twice
    for who in ["Alice", "Bob"]:
        _sub = ctx.api.forms.submit(body={
            "contactId": vars['t4283_form_id'],
            "emailMessage": [
                {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": who},
            ],
        })
        expect(_sub).json('$.data.success').equals(True)

    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4283_form_id']})
    expect(_list).json('$.code').equals('200')
    expect(_list).json('$.data.totalCount').equals(2)

    ids = [it['id'] for it in _list.json_safe()['data']['items']]
    ctx.api.forms.delete_inquiries(body={"ids": ids}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4283_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

