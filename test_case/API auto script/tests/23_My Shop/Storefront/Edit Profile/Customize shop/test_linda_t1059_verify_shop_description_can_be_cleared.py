"""ONES case: The user successfully carried out personalized settings for the store details."""
NAME = "The user can clear the shop description"
TAGS = ["p1", "customize_shop", "suite:linda"]
PRIORITY = 1
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


def test_linda_t1059_verify_shop_description_can_be_cleared(ctx: "Context"):
    """ONES case Esh1wukR: setting the description to an empty string is persisted."""
    vars = ctx

    snap = h.snapshot(ctx)
    info = h.build_info(snap, description="")

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.description").equals("")
    expect(check).json("$.data.storeName").equals(snap["storeName"])

    h.restore(ctx, snap)
