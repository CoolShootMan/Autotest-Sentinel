"""ONES case: Verify default state of "Display shop name" checkbox."""
NAME = 'Verify default state of "Display shop name" checkbox'
TAGS = ["p1", "customize_shop", "suite:linda"]
PRIORITY = 1
CASE_ID = "YUzEYLCJ"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5302_verify_display_shop_name_flag_readable(ctx: "Context"):
    """ONES case YUzEYLCJ: the displayShopNameOnStorefront flag is readable on the shop (read-only)."""
    vars = ctx

    check = ctx.api.users.shop_info_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.code").equals("200")
    expect(check).json("$.data.displayShopNameOnStorefront").exists()
