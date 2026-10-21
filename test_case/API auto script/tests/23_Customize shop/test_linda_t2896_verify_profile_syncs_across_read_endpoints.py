"""ONES case: Verify that "My shop" and "Account" profile pages are merged and data is synchronized."""
NAME = 'Verify that "My shop" and "Account" profile pages are merged and data is synchronized'
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "NheTk8aa"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t2896_verify_profile_syncs_across_read_endpoints(ctx: "Context"):
    """ONES case NheTk8aa: a saved description is consistent between the two profile read endpoints."""
    vars = ctx
    desc = "Sync check across vanity-url and shop-info"

    snap = h.snapshot(ctx)
    h.save(ctx, h.build_info(snap, description=desc))

    full = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    compact = ctx.api.users.shop_info_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)

    expect(full).json("$.data.description").equals(desc)
    expect(compact).json("$.data.description").equals(desc)
    expect(full).json("$.data.storeName").equals(compact.json_safe()["data"]["storeName"])

    h.restore(ctx, snap)
