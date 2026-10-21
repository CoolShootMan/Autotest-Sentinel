"""ONES case: Verify Form Social Field Input Format Validation"""
NAME = "Verify Form Social Field Input Format Validation"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "HJMx2fPy"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4973_verify_social_field_input_format(ctx: "Context"):
    """ONES case #HJMx2fPy: Verify Form Social Field Input Format Validation"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SOCIAL", "title": "Instagram", "required": False},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4973_form_id', _create, '$.data.id')
    f_social = _create.path('$.data.formFields[0].id')

    # end-user submits a short handle, a handle with @, and a full URL — all accepted
    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4973_form_id'],
        "emailMessage": [
            {"title": "Instagram", "field": "SOCIAL", "fieldId": f_social, "value": "@iamsupermush"},
        ],
    })
    expect(_sub).json('$.code').equals('200')
    expect(_sub).json('$.data.success').equals(True)

    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4973_form_id']})
    expect(_list).json('$.data.totalCount').greater_than(0)
    ctx.extract('t4973_inq_id', _list, '$.data.items[0].id')

    ctx.api.forms.delete_inquiries(body={"ids": [vars['t4973_inq_id']]}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4973_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

