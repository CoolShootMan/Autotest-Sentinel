"""ONES case: Invalid redirect URL format is rejected by configuration"""
NAME = "Invalid redirect URL format is rejected by configuration"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "KYHLfaYw"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5501_verify_invalid_redirect_url_rejected(ctx: "Context"):
    """ONES case #KYHLfaYw: Invalid redirect URL format is rejected by configuration"""
    vars = ctx
    _bad = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [],
        "confirmationMessage": {
            "enableRedirect": True,
            "targetRedirectUrl": "not-a-valid-url",
        },
    }, token='linda997_token')
    expect(_bad).json('$.code').not_equals('200')
    _msg = _bad.json().get('message', '') or _bad.json().get('error', '')
    assert any(k in str(_msg).lower() for k in ['url', 'redirect', 'valid']), f"expected URL validation error, got: {_msg}"

