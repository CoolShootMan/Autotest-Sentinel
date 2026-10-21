"""ONES case: Configure redirect URL and verify redirect after form submission"""
NAME = "Configure redirect URL and verify redirect after form submission"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "RasykFr3"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5500_verify_redirect_url_after_submit(ctx: "Context"):
    """ONES case #RasykFr3: Configure redirect URL and verify redirect after form submission"""
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
        "confirmationMessage": {
            "title": "Thanks",
            "body": "We will follow up",
            "enableRedirect": True,
            "targetRedirectUrl": "https://example.com/thank-you",
        },
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t5500_form_id', _create, '$.data.id')

    # public form exposes the configured redirect
    _pub = ctx.api.forms.public_by_id(id=vars['t5500_form_id'])
    expect(_pub).json('$.data.confirmationMessage.enableRedirect').equals(True)
    expect(_pub).json('$.data.confirmationMessage.targetRedirectUrl').equals("https://example.com/thank-you")

    _del = ctx.api.forms.delete_by_id(id=vars['t5500_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

