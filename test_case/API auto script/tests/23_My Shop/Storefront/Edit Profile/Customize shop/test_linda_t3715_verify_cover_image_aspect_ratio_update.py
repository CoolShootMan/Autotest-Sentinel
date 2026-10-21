"""ONES case: Verify when choosing the aspect ratio for the cover image, then it will update on the My shop page."""
NAME = "Verify when choosing the aspect ratio for the cover image, then it will update"
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


def test_linda_t3715_verify_cover_image_aspect_ratio_update(ctx: "Context"):
    """ONES case MqWXSXhu: changing the cover crop dimensions (aspect ratio) is persisted."""
    vars = ctx
    square = {"src": h.IMG_A, "width": 1080, "height": 1080}

    snap = h.snapshot(ctx)
    info = h.build_info(snap, backgroundSource=square)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.backgroundSource.width").equals(1080)
    expect(resp).json("$.data.backgroundSource.height").equals(1080)

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.backgroundSource.width").equals(1080)
    expect(check).json("$.data.backgroundSource.height").equals(1080)

    h.restore(ctx, snap)
