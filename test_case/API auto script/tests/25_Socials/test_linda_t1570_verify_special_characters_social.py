"""ONES case: Verify the special characters supported by Social"""
NAME = "Verify the special characters supported by Social"
TAGS = ["p1", "socials", "suite:linda"]
PRIORITY = 1
CASE_ID = "9sxPfrtz"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_social_special_characters(ctx: "Context"):
    """ONES case #9sxPfrtz: social URLs with @, ., - should be accepted"""
    vars = ctx

    resp = ctx.api.users.update_social(body={"socialMedias": [
        {"type": "INSTAGRAM", "url": "https://instagram.com/user.name-123"},
        {"type": "TIKTOK", "url": "https://tiktok.com/@user.name-123"},
        {"type": "EMAIL", "url": "mailto:user.name+tag@example.com"},
    ]}, token="linda997_token")
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.socialMedias").length(3)

    ctx.api.users.update_social(body={"socialMedias": []}, token="linda997_token")
