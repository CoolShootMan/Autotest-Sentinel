"""ONES case: Verify the profile can upload success."""
NAME = "Verify the profile can upload success"
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


def test_linda_t1445_verify_profile_avatar_upload_success(ctx: "Context"):
    """ONES case W9dnv5qS: setting a shop logo URL persists and is readable back."""
    vars = ctx

    snap = h.snapshot(ctx)
    info = h.build_info(snap, logo=h.IMG_A)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.logo").equals(h.IMG_A)

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.logo").equals(h.IMG_A)

    h.restore(ctx, snap)
