"""ONES case: Verify the profile can upload success."""
NAME = "Verify shop-info endpoint reflects the avatar"
TAGS = ["p2", "customize_shop", "suite:linda"]
PRIORITY = 2
CASE_ID = "W9dnv5qS"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t1445_verify_shop_info_reflects_avatar(ctx: "Context"):
    """ONES case W9dnv5qS: the compact shop-info read also returns the set logo."""
    vars = ctx

    snap = h.snapshot(ctx)
    info = h.build_info(snap, logo=h.IMG_A)
    h.save(ctx, info)

    check = ctx.api.users.shop_info_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.code").equals("200")
    expect(check).json("$.data.logo").equals(h.IMG_A)

    h.restore(ctx, snap)
