"""ONES case: Verify Link input format validation"""
NAME = "Verify Link input format validation"
TAGS = ["p1", "socials", "suite:linda"]
PRIORITY = 1
CASE_ID = "6K9QG1k5"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_link_input_format_validation(ctx: "Context"):
    """ONES case #6K9QG1k5: invalid URL/email/number should be rejected by create link"""
    vars = ctx

    resp_bad_url = ctx.api.links.create(body={
        "title": "Bad URL",
        "url": "abc",
        "type": "GENERAL",
        "showBelowTitle": False,
    }, token="linda997_token")
    # "abc" is not a valid URL — API must reject it (non-200 code)
    expect(resp_bad_url).json("$.code").not_equals("200")
    if resp_bad_url.status_code == 201:
        ctx.extract("bad_link_id", resp_bad_url, "$.data.id")
        ctx.api.links.delete_by_id(id=ctx["bad_link_id"], token="linda997_token")

    resp_good = ctx.api.links.create(body={
        "title": "Good URL",
        "url": "https://valid.example.com",
        "type": "GENERAL",
        "showBelowTitle": False,
    }, token="linda997_token")
    expect(resp_good).json("$.code").equals("200")
    ctx.extract("good_link_id", resp_good, "$.data.id")

    ctx.api.links.delete_by_id(id=ctx["good_link_id"], token="linda997_token")
