"""ONES case: The user successfully carried out personalized settings for the store details."""
NAME = "Verify shop name and URL remain unchanged through description/avatar/cover edits"
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "Esh1wukR"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t1059_verify_store_name_unchanged_after_mutations(ctx: "Context"):
    """Guard: after editing description, logo and cover, storeName and vanityUrl are preserved."""
    vars = ctx

    snap = h.snapshot(ctx)
    original_name = snap["storeName"]
    original_url = snap["vanityUrl"]

    info = h.build_info(
        snap,
        description="guard check",
        logo=h.IMG_B,
        backgroundSource={"src": h.IMG_B, "width": 800, "height": 800},
    )
    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.storeName").equals(original_name)
    expect(check).json("$.data.vanityUrl").equals(original_url)

    h.restore(ctx, snap)
