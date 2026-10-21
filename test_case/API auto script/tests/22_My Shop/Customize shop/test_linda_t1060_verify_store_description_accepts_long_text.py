"""ONES case: Verify that there is no limit to the number of words in Store Description."""
NAME = "Verify that there is no limit to the number of words in Store Description"
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


def test_linda_t1060_verify_store_description_accepts_long_text(ctx: "Context"):
    """ONES case PxkFoH3s: a ~600-char store description is saved without truncation."""
    vars = ctx
    long_desc = "Curator shop description line number. " * 18  # ~630 chars

    snap = h.snapshot(ctx)
    info = h.build_info(snap, description=long_desc)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.description").equals(long_desc)

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.description").equals(long_desc)
    expect(check).json("$.data.description").length(len(long_desc))
    expect(check).json("$.data.storeName").equals(snap["storeName"])

    h.restore(ctx, snap)
