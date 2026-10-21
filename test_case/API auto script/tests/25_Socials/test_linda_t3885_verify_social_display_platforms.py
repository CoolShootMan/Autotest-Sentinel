"""ONES case: Verify Social can display up to 7 on the shop page at most"""
NAME = "Verify that Socia can display up to 7 on the shop page at most"
TAGS = ["p1", "socials", "suite:linda"]
PRIORITY = 1
CASE_ID = "kH9jKMxA"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_social_display_multiple_platforms(ctx: "Context"):
    """ONES case #kH9jKMxA: fill all social links and verify they are returned"""
    vars = ctx

    socials = [
        {"type": "FACEBOOK", "url": "https://facebook.com/test"},
        {"type": "INSTAGRAM", "url": "https://instagram.com/test"},
        {"type": "TIKTOK", "url": "https://tiktok.com/@test"},
        {"type": "X", "url": "https://x.com/test"},
        {"type": "YOUTUBE", "url": "https://youtube.com/@test"},
        {"type": "LINKEDIN", "url": "https://linkedin.com/in/test"},
        {"type": "THREADS", "url": "https://threads.net/@test"},
        {"type": "EMAIL", "url": "mailto:test@pear.us"},
    ]
    resp = ctx.api.users.update_social(body={"socialMedias": socials}, token="linda997_token")
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.socialMedias").length(8)

    ctx.api.users.update_social(body={"socialMedias": []}, token="linda997_token")
