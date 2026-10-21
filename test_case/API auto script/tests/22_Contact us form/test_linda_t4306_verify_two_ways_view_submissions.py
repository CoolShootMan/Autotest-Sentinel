"""ONES case: Two ways for merchants to view submissions"""
NAME = "Two ways for merchants to view submissions"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "RKMziJx5"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4306_verify_two_ways_view_submissions(ctx: "Context"):
    """ONES case #RKMziJx5: Two ways for merchants to view submissions"""
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
    ctx.extract('t4306_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')

    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4306_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "ViewMe"},
        ],
    })
    expect(_sub).json('$.data.success').equals(True)

    # way 1: customer submissions list
    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4306_form_id']})
    expect(_list).json('$.code').equals('200')
    expect(_list).json('$.data.totalCount').greater_than(0)

    # way 2: form detail lists the submission context
    _get = ctx.api.forms.by_id(id=vars['t4306_form_id'], token='linda997_token')
    expect(_get).json('$.code').equals('200')
    expect(_get).json('$.data.id').equals(vars['t4306_form_id'])

    ctx.extract('t4306_inq_id', _list, '$.data.items[0].id')
    ctx.api.forms.delete_inquiries(body={"ids": [vars['t4306_inq_id']]}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4306_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

