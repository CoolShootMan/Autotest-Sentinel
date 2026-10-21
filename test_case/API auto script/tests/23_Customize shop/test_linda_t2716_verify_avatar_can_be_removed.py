"""ONES case: If the profile does not have an image, then a default randomly image should be required."""
NAME = "Verify the shop avatar can be removed"
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "Wvr99HJx"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t2716_verify_avatar_can_be_removed(ctx: "Context"):
    """ONES case Wvr99HJx: setting logo to null clears the avatar (default-image state)."""
    vars = ctx

    snap = h.snapshot(ctx)
    info = h.build_info(snap, logo=h.IMG_A)
    h.save(ctx, info)

    remove = h.build_info(h.snapshot(ctx), logo=None)
    resp = h.save(ctx, remove)
    expect(resp).json("$.code").equals("200")

    check = ctx.api.users.shop_info_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.logo").is_empty()

    h.restore(ctx, snap)
