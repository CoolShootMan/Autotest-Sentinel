"""ONES case: Verify internal system fallback for Shop Name."""
NAME = "Verify internal system fallback for Shop Name"
TAGS = ["p1", "customize_shop", "suite:linda"]
PRIORITY = 1
CASE_ID = "kgMMuEi5"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t5305_verify_shop_name_returned_in_profile(ctx: "Context"):
    """ONES case kgMMuEi5: the shop profile always exposes a non-empty storeName (read-only)."""
    vars = ctx

    check = ctx.api.users.shop_info_by_vanity_url(
        vanityUrl=h.vanity(ctx), token=h.TOKEN, app_headers=True)
    expect(check).json("$.code").equals("200")
    expect(check).json("$.data.storeName").is_not_empty()
    expect(check).json("$.data.vanityUrl").equals(h.vanity(ctx))
    expect(check).json("$.data.id").is_not_empty()
