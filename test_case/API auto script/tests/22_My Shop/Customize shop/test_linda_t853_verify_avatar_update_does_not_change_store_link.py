"""ONES case: Verify that the Curator has successfully changed personal information and that the store link will be updated."""
NAME = "Verify that the Curator has successfully changed personal information and that the store link will be updated"
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "5DHXUrsf"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t853_verify_avatar_update_does_not_change_store_link(ctx: "Context"):
    """ONES case 5DHXUrsf: updating the avatar changes the logo but leaves store name and URL untouched."""
    vars = ctx

    snap = h.snapshot(ctx)
    info = h.build_info(snap, logo=h.IMG_B)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.logo").equals(h.IMG_B)

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.logo").equals(h.IMG_B)
    expect(check).json("$.data.storeName").equals(snap["storeName"])
    expect(check).json("$.data.vanityUrl").equals(snap["vanityUrl"])

    h.restore(ctx, snap)
