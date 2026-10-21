"""ONES case: Verify the search bar on the Customer submissions page returns correct results by keyword"""
NAME = "Verify the search bar on the Customer submissions page returns correct results by keyword"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "YQuuawjj"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4537_verify_search_submissions_by_keyword(ctx: "Context"):
    """ONES case #YQuuawjj: Verify the search bar on the Customer submissions page returns correct results by keyword"""
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
    ctx.extract('t4537_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')

    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4537_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "SearchableKeyword"},
        ],
    })
    expect(_sub).json('$.data.success').equals(True)

    # list inquiries filtered by this form
    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4537_form_id']})
    expect(_list).json('$.code').equals('200')
    expect(_list).json('$.data.totalCount').greater_than(0)
    ctx.extract('t4537_inq_id', _list, '$.data.items[0].id')

    ctx.api.forms.delete_inquiries(body={"ids": [vars['t4537_inq_id']]}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4537_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

