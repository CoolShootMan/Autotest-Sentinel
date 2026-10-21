"""ONES case: Verify adding a new field Date and time on the Add new form page"""
NAME = "Verify adding a new field Date and time on the Add new form page"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "FtNSREAz"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4792_verify_date_time_field(ctx: "Context"):
    """ONES case #FtNSREAz: Verify adding a new field Date and time on the Add new form page"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "DATETIME", "title": "Preferred contact date", "required": False},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4792_form_id', _create, '$.data.id')

    _get = ctx.api.forms.by_id(id=vars['t4792_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields[0].field').equals("DATETIME")
    expect(_get).json('$.data.formFields[0].title').equals("Preferred contact date")

    _del = ctx.api.forms.delete_by_id(id=vars['t4792_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

