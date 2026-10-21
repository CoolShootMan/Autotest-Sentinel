"""ONES case: The user successfully carried out personalized settings for the store details."""
NAME = "The user successfully carried out personalized settings for the store details"
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


def test_linda_t1059_verify_curator_can_update_shop_description(ctx: "Context"):
    """ONES case Esh1wukR: curator updates shop description and it is persisted."""
    vars = ctx
    new_desc = "Curator API test description - updated via PUT /store-front"

    snap = h.snapshot(ctx)
    info = h.build_info(snap, description=new_desc)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.description").equals(new_desc)

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.code").equals("200")
    expect(check).json("$.data.description").equals(new_desc)
    expect(check).json("$.data.storeName").equals(snap["storeName"])

    h.restore(ctx, snap)
