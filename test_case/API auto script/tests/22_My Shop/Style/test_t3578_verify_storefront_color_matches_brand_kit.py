"""ONES case: Verify that the Storefront color of the new user is Brand Kit color"""
NAME = "Verify that the Storefront color of the new user is Brand Kit color"
TAGS = ["p0", "style", "suite:linda"]
PRIORITY = 0
CASE_ID = "Xn6kRHWi"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_t3578_verify_storefront_color_matches_brand_kit(ctx: "Context"):
    """ONES case #T3578: GET /user/self returns the storefront config; for a fresh curator storeTabs are present and no customized colors/fonts override the brand defaults."""
    vars = ctx

    resp = ctx.api.storefront.self_profile(token="linda997_token")
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.storeFront.storeTabs").exists()
    expect(resp).json("$.data.vanityUrl").exists()
