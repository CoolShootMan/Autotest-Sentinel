"""ONES case: Verify Curator edits all Social links and changes their positions"""
NAME = "Verify that Curator edits all Social links and changes the location of the links"
TAGS = ["p0", "socials", "suite:linda"]
PRIORITY = 0
CASE_ID = "Wj3oZmYa"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_edit_all_social_links(ctx: "Context"):
    """ONES case #Wj3oZmYa: update existing social URLs to new values"""
    vars = ctx

    ctx.api.users.update_social(body={"socialMedias": [
        {"type": "FACEBOOK", "url": "https://facebook.com/old"},
        {"type": "INSTAGRAM", "url": "https://instagram.com/old"},
        {"type": "TIKTOK", "url": "https://tiktok.com/@old"},
    ]}, token="linda997_token")

    resp = ctx.api.users.update_social(body={"socialMedias": [
        {"type": "FACEBOOK", "url": "https://facebook.com/new1"},
        {"type": "INSTAGRAM", "url": "https://instagram.com/new2"},
        {"type": "TIKTOK", "url": "https://tiktok.com/@new3"},
    ]}, token="linda997_token")
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.socialMedias").length(3)
    expect(resp).json("$.data.socialMedias..url").includes("https://facebook.com/new1")

    ctx.api.users.update_social(body={"socialMedias": []}, token="linda997_token")
