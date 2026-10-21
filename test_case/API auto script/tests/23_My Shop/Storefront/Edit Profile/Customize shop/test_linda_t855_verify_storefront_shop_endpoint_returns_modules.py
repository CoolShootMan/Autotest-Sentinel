"""ONES case: Curator successfully copies the store link in "My Shop" and opens it."""
NAME = "Verify the public storefront shop endpoint returns the shop modules"
TAGS = ["p0", "customize_shop", "suite:linda"]
PRIORITY = 0
CASE_ID = "88HBEQm3"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
import os
import sys
from core.assertions import expect

sys.path.insert(0, os.path.dirname(__file__))
import _shop_helpers as h
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t855_verify_storefront_shop_endpoint_returns_modules(ctx: "Context"):
    """ONES case 88HBEQm3: GET /store-front/shop/{vanity} returns 200 with shopModules."""
    vars = ctx

    resp = ctx.api.storefront.shop(
        path_vars={"partner_vanityUrl": h.vanity(ctx)},
        params={"public": "false"}, token=h.TOKEN, app_headers=True)
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.message").equals("success")
    expect(resp).json("$.data.shopModules").is_not_empty()
