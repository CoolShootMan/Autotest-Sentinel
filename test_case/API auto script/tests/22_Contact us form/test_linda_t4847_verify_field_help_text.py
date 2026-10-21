"""ONES case: Verify adding a Field help text to provide more clarity to customers"""
NAME = "Verify adding a Field help text to provide more clarity to customers"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "RViftwf9"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4847_verify_field_help_text(ctx: "Context"):
    """ONES case #RViftwf9: Verify adding a Field help text to provide more clarity to customers"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "PARAGRAPH", "title": "Your message", "required": True, "description": "Please describe your issue in detail"},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4847_form_id', _create, '$.data.id')

    _get = ctx.api.forms.by_id(id=vars['t4847_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields[0].description').equals("Please describe your issue in detail")

    _del = ctx.api.forms.delete_by_id(id=vars['t4847_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

