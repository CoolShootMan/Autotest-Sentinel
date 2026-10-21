"""ONES case: Verify when choosing the aspect ratio for the cover image, then it will update."""
NAME = "Verify the cover image source can be updated to a new image"
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "MqWXSXhu"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t3715_verify_cover_image_src_can_be_changed(ctx: "Context"):
    """ONES case MqWXSXhu: the cover backgroundImage src can be replaced with a new asset."""
    vars = ctx
    new_cover = {"src": h.IMG_B, "width": 1200, "height": 630}

    snap = h.snapshot(ctx)
    info = h.build_info(snap, backgroundSource=new_cover)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.backgroundImage").equals(h.IMG_B)

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.backgroundImage").equals(h.IMG_B)

    h.restore(ctx, snap)
