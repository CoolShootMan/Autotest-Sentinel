"""ONES case: Verify Contact us header information display (Title required, Image/Subtitle optional)"""
NAME = "Verify Contact us header information display (Title required, Image/Subtitle optional)"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "S1SRew8i"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4276_verify_header_info_display(ctx: "Context"):
    """ONES case #S1SRew8i: Verify Contact us header information display (Title required, Image/Subtitle optional)"""
    vars = ctx
    # subtitle / image are optional: a form with title only still creates
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    expect(_create).json('$.data.title').equals("Contact us")
    ctx.extract('t4276_form_id', _create, '$.data.id')

    # title is required: creating without a title must be rejected (non-2xx)
    _notitle = ctx.api.forms.create(body={
        "subtitle": "no title",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [],
    }, token='linda997_token')
    expect(_notitle).json('$.code').not_equals('200')

    _del = ctx.api.forms.delete_by_id(id=vars['t4276_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

