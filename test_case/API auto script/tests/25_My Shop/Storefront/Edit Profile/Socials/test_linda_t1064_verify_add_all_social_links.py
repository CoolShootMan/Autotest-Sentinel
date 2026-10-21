"""ONES case: Verify Curator adds all external social links successfully"""
NAME = "Verify that the Curator adds all external links and shares the successfully opened icons with Consumer"
TAGS = ["p0", "socials", "suite:linda"]
PRIORITY = 0
CASE_ID = "UsVX3fAi"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_set_all_social_platforms(ctx: "Context"):
    """ONES case #UsVX3fAi: set Facebook/Instagram/TikTok/X/YouTube/LinkedIn/Threads/Email"""
    vars = ctx

    original = ctx.api.users.update_social(body={"socialMedias": []}, token="linda997_token")

    socials = [
        {"type": "FACEBOOK", "url": "https://facebook.com/curator997"},
        {"type": "INSTAGRAM", "url": "https://instagram.com/curator997"},
        {"type": "TIKTOK", "url": "https://tiktok.com/@curator997"},
        {"type": "X", "url": "https://x.com/curator997"},
        {"type": "YOUTUBE", "url": "https://youtube.com/@curator997"},
        {"type": "LINKEDIN", "url": "https://linkedin.com/in/curator997"},
        {"type": "THREADS", "url": "https://threads.net/@curator997"},
        {"type": "EMAIL", "url": "mailto:curator997@pear.us"},
    ]
    resp = ctx.api.users.update_social(body={"socialMedias": socials}, token="linda997_token")
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.socialMedias").length(8)
    expect(resp).json("$.data.socialMedias..type").includes("FACEBOOK")
    expect(resp).json("$.data.socialMedias..type").includes("INSTAGRAM")
    expect(resp).json("$.data.socialMedias..type").includes("TIKTOK")
    expect(resp).json("$.data.socialMedias..type").includes("LINKEDIN")

    ctx.api.users.update_social(body={"socialMedias": []}, token="linda997_token")
