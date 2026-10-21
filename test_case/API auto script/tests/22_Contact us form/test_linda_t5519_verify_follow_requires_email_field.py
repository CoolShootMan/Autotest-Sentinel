"""ONES case: Verify red validation error appears when Follow is enabled but required phone/email field is missing"""
NAME = "Verify red validation error appears when Follow is enabled but required phone/email field is missing"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "YNMtJVJK"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5519_verify_follow_requires_email_field(ctx: "Context"):
    """ONES case #YNMtJVJK: Verify red validation error appears when Follow is enabled but required phone/email field is missing"""
    vars = ctx
    # autoFollow requires an email/phone field on the form; without one it must be rejected
    _bad = ctx.api.forms.create(body={
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
            "body": "Follow us",
            "autoFollow": True,
        },
    }, token='linda997_token')
    expect(_bad).json('$.code').not_equals('200')

