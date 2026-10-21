"""ONES case: Verify the custom Reset colors and fonts and layout feature"""
NAME = "Verify the custom Reset colors and fonts and layout feature"
TAGS = ["p0", "style", "suite:linda"]
PRIORITY = 0
CASE_ID = "DZ1eYFvz"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_t4100_verify_reset_colors_fonts_and_layout(ctx: "Context"):
    """ONES case #T4100: Verify the custom Reset colors and fonts and layout feature"""
    vars = ctx

    profile = ctx.api.storefront.self_profile(token="linda997_token").json()["data"]
    store_tabs = (profile.get("storeFront") or {}).get("storeTabs", [])

    set_resp = ctx.api.storefront.update(body={
        "userInfo": {
            "storeName": profile["storeName"],
            "logo": profile.get("logo"),
            "backgroundSource": profile.get("backgroundSource"),
            "description": profile.get("description", ""),
            "subTitle": profile.get("subTitle", ""),
            "socialMedias": profile.get("socialMedias", []),
            "vanityUrl": profile["vanityUrl"],
            "storeFront": {
                "storeTabs": store_tabs,
                "colors": {"backgroundColor": "#FFF4E0"},
                "fonts": {"fontFamily": "Arial", "fontSize": 24},
            },
        },
    }, token="linda997_token")
    expect(set_resp).json("$.code").equals("200")

    ctx.api.storefront.layout(body={
        "storeTabs": store_tabs,
        "productCardLayout": "TopAligned",
        "linkCardLayout": "Compact",
    }, token="linda997_token")

    after = ctx.api.storefront.self_profile(token="linda997_token")
    expect(after).json("$.data.storeFront.colors.backgroundColor").equals("#FFF4E0")
    expect(after).json("$.data.storeFront.fonts.fontFamily").equals("Arial")
    expect(after).json("$.data.storeFront.fonts.fontSize").equals(24)
    expect(after).json("$.data.storeFront.productCardLayout").equals("TopAligned")
    expect(after).json("$.data.storeFront.linkCardLayout").equals("Compact")

    reset = ctx.api.storefront.update(body={
        "userInfo": {
            "storeName": profile["storeName"],
            "logo": profile.get("logo"),
            "backgroundSource": profile.get("backgroundSource"),
            "description": profile.get("description", ""),
            "subTitle": profile.get("subTitle", ""),
            "socialMedias": profile.get("socialMedias", []),
            "vanityUrl": profile["vanityUrl"],
            "storeFront": {"storeTabs": store_tabs},
        },
    }, token="linda997_token")
    expect(reset).json("$.code").equals("200")

    cleared = ctx.api.storefront.self_profile(token="linda997_token").json()["data"]
    sf2 = cleared.get("storeFront") or {}
    assert "colors" not in sf2, f"colors not cleared: {sf2.get('colors')}"
    assert "fonts" not in sf2, f"fonts not cleared: {sf2.get('fonts')}"
    assert "productCardLayout" not in sf2, f"productCardLayout not cleared: {sf2.get('productCardLayout')}"
    assert "linkCardLayout" not in sf2, f"linkCardLayout not cleared: {sf2.get('linkCardLayout')}"
