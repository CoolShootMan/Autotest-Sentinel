"""ONES case: Verify the creation of shop topic presets and their application to post"""
NAME = "Verify the creation of shop topic presets and their application to post"
TAGS = ["p0", "style", "suite:linda"]
PRIORITY = 0
CASE_ID = "UdG4TvUE"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_t4093_verify_style_config_persists_after_save(ctx: "Context"):
    """ONES case #T4093: set colors + font, save, then GET self config and verify all values persist"""
    vars = ctx

    profile = ctx.api.storefront.self_profile(token="linda997_token").json()["data"]
    store_tabs = (profile.get("storeFront") or {}).get("storeTabs", [])

    save = ctx.api.storefront.update(body={
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
                    "backgroundColor": "#972C2C",
                    "cardBorderColor": "#C0B49E",
                    "cardBackgroundColor": "#B8A797",
                },
                "fonts": {"fontFamily": "Dosis", "fontSize": 14},
            },
        },
    }, token="linda997_token")
    expect(save).json("$.code").equals("200")

    fetched = ctx.api.storefront.self_profile(token="linda997_token")
    expect(fetched).json("$.data.storeFront.colors.backgroundColor").equals("#972C2C")
    expect(fetched).json("$.data.storeFront.colors.cardBorderColor").equals("#C0B49E")
    expect(fetched).json("$.data.storeFront.colors.cardBackgroundColor").equals("#B8A797")
    expect(fetched).json("$.data.storeFront.fonts.fontFamily").equals("Dosis")
    expect(fetched).json("$.data.storeFront.fonts.fontSize").equals(14)

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
