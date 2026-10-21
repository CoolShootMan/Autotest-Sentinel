"""ONES case: Verify adding a new field Yes / No option on the Add new form page"""
NAME = "Verify adding a new field Yes / No option on the Add new form page"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "HomvwJvh"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4793_verify_yes_no_checkbox_field(ctx: "Context"):
    """ONES case #HomvwJvh: Verify adding a new field Yes / No option on the Add new form page"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "CHECKBOX", "title": "Subscribe to our newsletter", "required": False},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4793_form_id', _create, '$.data.id')

    _get = ctx.api.forms.by_id(id=vars['t4793_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields[0].field').equals("CHECKBOX")
    expect(_get).json('$.data.formFields[0].title').equals("Subscribe to our newsletter")

    _del = ctx.api.forms.delete_by_id(id=vars['t4793_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

