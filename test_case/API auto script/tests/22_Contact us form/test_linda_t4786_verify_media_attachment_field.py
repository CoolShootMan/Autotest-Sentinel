"""ONES case: Verify adding a new field Media on the Add new form page"""
NAME = "Verify adding a new field Media on the Add new form page"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "UxcM6Sbu"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4786_verify_media_attachment_field(ctx: "Context"):
    """ONES case #UxcM6Sbu: Verify adding a new field Media on the Add new form page"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "ATTACHMENT", "title": "Upload a screenshot", "required": False},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4786_form_id', _create, '$.data.id')

    _get = ctx.api.forms.by_id(id=vars['t4786_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields[0].field').equals("ATTACHMENT")
    expect(_get).json('$.data.formFields[0].title').equals("Upload a screenshot")

    _del = ctx.api.forms.delete_by_id(id=vars['t4786_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

