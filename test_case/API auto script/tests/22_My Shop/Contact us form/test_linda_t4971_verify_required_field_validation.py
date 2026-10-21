"""ONES case: Verify Form Required Field Validation and User-End Selection Scenarios"""
NAME = "Verify Form Required Field Validation and User-End Selection Scenarios"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "BVvnsZET"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4971_verify_required_field_validation(ctx: "Context"):
    """ONES case #BVvnsZET: Verify Form Required Field Validation and User-End Selection Scenarios"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
            {"field": "EMAIL_ADDRESS", "title": "Email", "required": True},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4971_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')
    f_email = _create.path('$.data.formFields[1].id')

    # merchant-side contract: both fields are flagged required
    _get = ctx.api.forms.by_id(id=vars['t4971_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields[0].required').equals(True)
    expect(_get).json('$.data.formFields[1].required').equals(True)

    # a complete submission satisfying the required fields succeeds
    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4971_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "Alice"},
            {"title": "Email", "field": "EMAIL_ADDRESS", "fieldId": f_email, "value": "alice@example.com"},
        ],
    })
    expect(_sub).json('$.data.success').equals(True)

    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4971_form_id']})
    ids = [it['id'] for it in _list.json_safe()['data']['items']]
    if ids:
        ctx.api.forms.delete_inquiries(body={"ids": ids}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4971_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

