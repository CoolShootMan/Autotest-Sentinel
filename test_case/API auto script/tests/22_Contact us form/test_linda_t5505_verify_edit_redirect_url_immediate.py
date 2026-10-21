"""ONES case: Edit existing form's redirect URL and verify immediate effect"""
NAME = "Edit existing form's redirect URL and verify immediate effect"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "GUJzYYhE"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5505_verify_edit_redirect_url_immediate(ctx: "Context"):
    """ONES case #GUJzYYhE: Edit existing form's redirect URL and verify immediate effect"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
        ],
        "confirmationMessage": {"enableRedirect": False, "targetRedirectUrl": None},
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t5505_form_id', _create, '$.data.id')

    # edit: enable redirect with a new URL
    _up = ctx.api.forms.update_by_id(id=vars['t5505_form_id'], body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [{"field": "SHORT_ANSWER", "title": "Name", "required": True}],
        "confirmationMessage": {
            "title": "Thanks",
            "body": "done",
            "enableRedirect": True,
            "targetRedirectUrl": "https://example.com/updated",
        },
    }, token='linda997_token')
    expect(_up).json('$.code').equals('200')

    _pub = ctx.api.forms.public_by_id(id=vars['t5505_form_id'])
    expect(_pub).json('$.data.confirmationMessage.enableRedirect').equals(True)
    expect(_pub).json('$.data.confirmationMessage.targetRedirectUrl').equals("https://example.com/updated")

    _del = ctx.api.forms.delete_by_id(id=vars['t5505_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

