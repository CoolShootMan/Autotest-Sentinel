"""ONES case: Verify form input validation logic"""
NAME = "Verify form input validation logic"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "CxScgCSo"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4280_verify_form_input_validation(ctx: "Context"):
    """ONES case #CxScgCSo: Verify form input validation logic"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "EMAIL_ADDRESS", "title": "Email", "required": True},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4280_form_id', _create, '$.data.id')
    f_email = _create.path('$.data.formFields[0].id')

    # a submission referencing a non-UUID fieldId must be rejected
    _bad_field = ctx.api.forms.submit(body={
        "contactId": vars['t4280_form_id'],
        "emailMessage": [
            {"title": "Email", "field": "EMAIL_ADDRESS", "fieldId": "not-a-uuid", "value": "a@b.com"},
        ],
    })
    expect(_bad_field).json('$.code').equals(400)

    # a submission referencing an unknown field enum must be rejected
    _bad_enum = ctx.api.forms.submit(body={
        "contactId": vars['t4280_form_id'],
        "emailMessage": [
            {"title": "Email", "field": "NOT_A_FIELD", "fieldId": f_email, "value": "a@b.com"},
        ],
    })
    expect(_bad_enum).json('$.code').equals(400)

    # a well-formed submission succeeds
    _good = ctx.api.forms.submit(body={
        "contactId": vars['t4280_form_id'],
        "emailMessage": [
            {"title": "Email", "field": "EMAIL_ADDRESS", "fieldId": f_email, "value": "real@example.com"},
        ],
    })
    expect(_good).json('$.data.success').equals(True)

    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4280_form_id']})
    ids = [it['id'] for it in _list.json_safe()['data']['items']]
    if ids:
        ctx.api.forms.delete_inquiries(body={"ids": ids}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4280_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

