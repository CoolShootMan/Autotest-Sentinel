"""ONES case: Verify Form Single/Multiple Choice Field Configuration and End-to-End Submission Flow"""
NAME = "Verify Form Single/Multiple Choice Field Configuration and End-to-End Submission Flow"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "r1CUJkgC"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4969_verify_single_multiple_choice_field_e2e(ctx: "Context"):
    """ONES case #r1CUJkgC: Verify Form Single/Multiple Choice Field Configuration and End-to-End Submission Flow"""
    vars = ctx
    # step 1: create form with single-choice and multiple-choice fields
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SINGLE_CHOICE", "title": "Topic", "required": True},
            {"field": "MULTIPLE_CHOICE", "title": "Interests", "required": False},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4969_form_id', _create, '$.data.id')
    f_single = _create.path('$.data.formFields[0].id')
    f_multi = _create.path('$.data.formFields[1].id')

    # step 2: field types are persisted
    _get = ctx.api.forms.by_id(id=vars['t4969_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields[0].field').equals("SINGLE_CHOICE")
    expect(_get).json('$.data.formFields[1].field').equals("MULTIPLE_CHOICE")

    # step 3: end-user submits selections
    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4969_form_id'],
        "emailMessage": [
            {"title": "Topic", "field": "SINGLE_CHOICE", "fieldId": f_single, "value": "Billing"},
            {"title": "Interests", "field": "MULTIPLE_CHOICE", "fieldId": f_multi, "value": ["Ticket info", "Refund"]},
        ],
    })
    expect(_sub).json('$.code').equals('200')
    expect(_sub).json('$.data.success').equals(True)

    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4969_form_id']})
    expect(_list).json('$.data.totalCount').greater_than(0)
    ctx.extract('t4969_inq_id', _list, '$.data.items[0].id')

    ctx.api.forms.delete_inquiries(body={"ids": [vars['t4969_inq_id']]}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4969_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

