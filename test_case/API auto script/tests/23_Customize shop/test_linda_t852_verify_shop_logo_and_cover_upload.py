"""ONES case: Verify that Curator successfully added name and uploaded Shop logo and Cover image picture in My Shop."""
NAME = "Verify that Curator successfully uploaded Shop logo and Cover image"
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "SUP6uavz"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t852_verify_shop_logo_and_cover_upload(ctx: "Context"):
    """ONES case SUP6uavz: logo and cover (backgroundSource) are set together and persisted."""
    vars = ctx
    cover = {"src": h.IMG_A, "width": 1200, "height": 630}

    snap = h.snapshot(ctx)
    info = h.build_info(snap, logo=h.IMG_A, backgroundSource=cover)

    resp = h.save(ctx, info)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.logo").equals(h.IMG_A)
    expect(resp).json("$.data.backgroundSource.src").equals(cover["src"])

    check = ctx.api.users.profile_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.data.logo").equals(h.IMG_A)
    expect(check).json("$.data.backgroundImage").equals(cover["src"])

    h.restore(ctx, snap)
