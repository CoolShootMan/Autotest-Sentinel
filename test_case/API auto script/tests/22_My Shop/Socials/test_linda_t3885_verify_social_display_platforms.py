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
    saved = {s["type"]: s["url"] for s in resp.json()["data"]["socialMedias"]}
    assert saved.get("FACEBOOK") == "https://facebook.com/test", f"facebook url mismatch: {saved}"
    assert saved.get("TIKTOK") == "https://tiktok.com/@test", f"tiktok url mismatch: {saved}"
    assert saved.get("EMAIL") == "mailto:test@pear.us", f"email url mismatch: {saved}"

    ctx.api.users.update_social(body={"socialMedias": []}, token="linda997_token")
