"""ONES case: Verify user can complete and submit the Contact us form successfully"""
NAME = "Verify user can complete and submit the Contact us form successfully"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "G686Cuv8"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4279_verify_user_submit_contact_us_form_success(ctx: "Context"):
    """ONES case #G686Cuv8: Verify user can complete and submit the Contact us form successfully"""
    vars = ctx
    # step 1: merchant creates a form with Name + Email required fields
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "We are here to help",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
            {"field": "EMAIL_ADDRESS", "title": "Email", "required": True},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4279_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')
    f_email = _create.path('$.data.formFields[1].id')

    # step 2: end-user submits the form
    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4279_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "Alice"},
            {"title": "Email", "field": "EMAIL_ADDRESS", "fieldId": f_email, "value": "alice@example.com"},
        ],
    })
    expect(_sub).json('$.code').equals('200')
    expect(_sub).json('$.data.success').equals(True)

    # step 3: merchant sees the submission in customer submissions
    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4279_form_id']})
    expect(_list).json('$.code').equals('200')
    expect(_list).json('$.data.totalCount').greater_than(0)
    ctx.extract('t4279_inq_id', _list, '$.data.items[0].id')

    # teardown: delete inquiry + form
    ctx.api.forms.delete_inquiries(body={"ids": [vars['t4279_inq_id']]}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4279_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

