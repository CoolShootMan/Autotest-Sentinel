"""ONES case: Verify Form Field Option Quantity and Content Boundary Validation"""
NAME = "Verify Form Field Option Quantity and Content Boundary Validation"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "E6ZUWacc"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4970_verify_choice_option_boundary(ctx: "Context"):
    """ONES case #E6ZUWacc: Verify Form Field Option Quantity and Content Boundary Validation"""
    vars = ctx
    # a choice field with many options is accepted and persisted
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SINGLE_CHOICE", "title": "Reason", "required": True},
            {"field": "MULTIPLE_CHOICE", "title": "Topics", "required": False},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4970_form_id', _create, '$.data.id')

    _get = ctx.api.forms.by_id(id=vars['t4970_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields').length(2)
    expect(_get).json('$.data.formFields[0].field').equals("SINGLE_CHOICE")
    expect(_get).json('$.data.formFields[1].field').equals("MULTIPLE_CHOICE")

    # unknown field type must be rejected
    _bad = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [{"field": "NOT_A_REAL_TYPE", "title": "X", "required": False}],
    }, token='linda997_token')
    expect(_bad).json('$.code').equals(400)

    _del = ctx.api.forms.delete_by_id(id=vars['t4970_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

