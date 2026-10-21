"""ONES case: Verify submission handling in failure scenarios"""
NAME = "Verify submission handling in failure scenarios"
TAGS = ['p1', 'contact_us_form', 'suite:linda']
PRIORITY = 1
CASE_ID = "Gp9p6zpQ"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4282_verify_submission_failure_scenarios(ctx: "Context"):
    """ONES case #Gp9p6zpQ: Verify submission handling in failure scenarios"""
    vars = ctx
    # submitting to a non-existent form id must fail
    _no_form = ctx.api.forms.submit(body={
        "contactId": "00000000-0000-0000-0000-000000000000",
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": "00000000-0000-0000-0000-000000000000", "value": "x"},
        ],
    })
    expect(_no_form).json('$.code').not_equals('200')

    # submitting with empty contactId must be rejected
    _no_id = ctx.api.forms.submit(body={
        "contactId": "",
        "emailMessage": [],
    })
    expect(_no_id).json('$.code').equals(400)

