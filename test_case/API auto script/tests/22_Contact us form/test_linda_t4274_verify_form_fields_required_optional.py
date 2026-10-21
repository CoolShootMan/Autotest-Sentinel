"""ONES case: Verify Merchant can configure Form fields with required/optional logic and display correctly"""
NAME = "Verify Merchant can configure Form fields with required/optional logic and display correctly"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "CQaMbnte"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4274_verify_form_fields_required_optional(ctx: "Context"):
    """ONES case #CQaMbnte: Verify Merchant can configure Form fields with required/optional logic and display correctly"""
    vars = ctx
    # step 1: create form with two required + one optional field
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
            {"field": "EMAIL_ADDRESS", "title": "Email", "required": True},
            {"field": "PARAGRAPH", "title": "How did you hear about us", "required": False},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4274_form_id', _create, '$.data.id')

    # step 2: required flags are persisted as configured
    _get = ctx.api.forms.by_id(id=vars['t4274_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields[0].required').equals(True)
    expect(_get).json('$.data.formFields[1].required').equals(True)
    expect(_get).json('$.data.formFields[2].required').equals(False)

    # teardown
    _del = ctx.api.forms.delete_by_id(id=vars['t4274_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

