"""ONES case: Verify that there is no limit to the number of words in Store Description."""
NAME = "Verify shop description supports special characters and emoji"
TAGS = ["p1", "customize_shop", "suite:linda"]
PRIORITY = 1
CASE_ID = "PxkFoH3s"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t1060_verify_shop_description_supports_special_chars(ctx: "Context"):
    """ONES case PxkFoH3s: description with emoji / symbols / quotes survives a save."""
    vars = ctx
    desc = "Shop 🛍️ — new arrivals 50% off! <b>tags</b> & 'quotes' \"double\" émoji ✓"

    snap = h.snapshot(ctx)
    info = h.build_info(snap, description=desc)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.description").equals(desc)

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.description").equals(desc)

    h.restore(ctx, snap)
