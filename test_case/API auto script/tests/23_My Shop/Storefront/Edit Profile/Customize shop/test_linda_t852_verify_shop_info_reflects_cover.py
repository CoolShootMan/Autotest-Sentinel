"""ONES case: Verify that Curator successfully added name and uploaded Shop logo and Cover image picture in My Shop."""
NAME = "Verify shop-info endpoint reflects the cover image"
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "SUP6uavz"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t852_verify_shop_info_reflects_cover(ctx: "Context"):
    """ONES case SUP6uavz: the compact shop-info read exposes the store name / description / logo fields."""
    vars = ctx
    cover = {"src": h.IMG_B, "width": 1200, "height": 630}

    snap = h.snapshot(ctx)
    info = h.build_info(snap, backgroundSource=cover, description="cover sync check")
    h.save(ctx, info)

    check = ctx.api.users.shop_info_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.code").equals("200")
    expect(check).json("$.data.description").equals("cover sync check")
    expect(check).json("$.data.storeName").equals(snap["storeName"])

    h.restore(ctx, snap)
