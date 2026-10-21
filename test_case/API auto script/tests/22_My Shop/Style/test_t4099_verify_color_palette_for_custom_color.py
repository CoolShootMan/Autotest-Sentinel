"""ONES case: Verify the Color palette function for custom Color"""
NAME = "Verify the Color palette function for custom Color"
TAGS = ["p0", "style", "suite:linda"]
PRIORITY = 0
CASE_ID = "T8kQUEdQ"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_t4099_verify_color_palette_for_custom_color(ctx: "Context"):
    """ONES case #T4099: Verify the Color palette function for custom Color"""
    vars = ctx

    profile = ctx.api.storefront.self_profile(token="linda997_token").json()["data"]
    store_tabs = (profile.get("storeFront") or {}).get("storeTabs", [])

    resp = ctx.api.storefront.update(body={
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
                "colors": {
                    "buttonBackgroundColor": "#FF0000",
                    "buttonTextColor": "#FFFFFF",
                },
            },
        },
    }, token="linda997_token")
    expect(resp).json("$.code").equals("200")

    fetched = ctx.api.storefront.self_profile(token="linda997_token")
    expect(fetched).json("$.data.storeFront.colors.buttonBackgroundColor").equals("#FF0000")
    expect(fetched).json("$.data.storeFront.colors.buttonTextColor").equals("#FFFFFF")

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
