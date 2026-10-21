"""ONES case: Verify editing existing form's Follow configuration takes immediate effect"""
NAME = "Verify editing existing form's Follow configuration takes immediate effect"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "ArYyGv9v"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5521_verify_edit_follow_config_immediate(ctx: "Context"):
    """ONES case #ArYyGv9v: Verify editing existing form's Follow configuration takes immediate effect"""
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
        "confirmationMessage": {"autoFollow": False},
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t5521_form_id', _create, '$.data.id')

    _up = ctx.api.forms.update_by_id(id=vars['t5521_form_id'], body={
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
    expect(_up).json('$.code').equals('200')

    _pub = ctx.api.forms.public_by_id(id=vars['t5521_form_id'])
    expect(_pub).json('$.data.confirmationMessage.autoFollow').equals(True)

    _del = ctx.api.forms.delete_by_id(id=vars['t5521_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

