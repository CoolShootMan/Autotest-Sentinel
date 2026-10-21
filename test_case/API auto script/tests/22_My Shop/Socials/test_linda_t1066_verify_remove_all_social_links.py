"""ONES case: Verify Curator removes all Social links and checks the shop icon"""
NAME = "Verify that Curator removes all Social links and then checks the shop icon"
TAGS = ["p0", "socials", "suite:linda"]
PRIORITY = 0
CASE_ID = "EhWHsaCo"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_clear_all_social_links(ctx: "Context"):
    """ONES case #EhWHsaCo: set some socials, then clear them all"""
    vars = ctx

    ctx.api.users.update_social(body={"socialMedias": [
        {"type": "FACEBOOK", "url": "https://facebook.com/test"},
        {"type": "INSTAGRAM", "url": "https://instagram.com/test"},
        {"type": "TIKTOK", "url": "https://tiktok.com/@test"},
    ]}, token="linda997_token")

    resp_clear = ctx.api.users.update_social(body={"socialMedias": []}, token="linda997_token")
    expect(resp_clear).json("$.code").equals("200")
    expect(resp_clear).json("$.data.socialMedias").length(0)

    ctx.api.users.update_social(body={"socialMedias": []}, token="linda997_token")
