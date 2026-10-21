"""ONES case: Verify storefront visibility when shop name is hidden."""
NAME = "Verify storefront visibility when shop name is hidden"
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "U4o8vBjj"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5303_verify_shop_name_hidden_on_storefront(ctx: "Context"):
    """ONES case U4o8vBjj: turning displayShopNameOnStorefront off persists the flag."""
    vars = ctx

    snap = h.snapshot(ctx)
    info = h.build_info(snap, displayShopNameOnStorefront=False)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.displayShopNameOnStorefront").equals(False)
    expect(check).json("$.data.storeName").equals(snap["storeName"])

    h.restore(ctx, snap)
