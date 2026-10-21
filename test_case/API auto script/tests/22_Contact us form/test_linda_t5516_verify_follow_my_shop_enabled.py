"""ONES case: Verify Follow my shop can be enabled in After form submission settings"""
NAME = "Verify Follow my shop can be enabled in After form submission settings"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "LeLeimxB"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5516_verify_follow_my_shop_enabled(ctx: "Context"):
    """ONES case #LeLeimxB: Verify Follow my shop can be enabled in After form submission settings"""
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
        "confirmationMessage": {
            "title": "Thanks",
            "body": "Follow us",
            "autoFollow": True,
        },
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t5516_form_id', _create, '$.data.id')

    _pub = ctx.api.forms.public_by_id(id=vars['t5516_form_id'])
    expect(_pub).json('$.data.confirmationMessage.autoFollow').equals(True)

    _del = ctx.api.forms.delete_by_id(id=vars['t5516_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

