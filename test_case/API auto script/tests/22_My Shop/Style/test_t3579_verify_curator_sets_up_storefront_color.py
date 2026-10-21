"""ONES case: Verify that curator sets up Storefront color"""
NAME = "Verify that curator sets up Storefront color"
TAGS = ["p0", "style", "suite:linda"]
PRIORITY = 0
CASE_ID = "2WoFQudB"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_t3579_verify_curator_sets_up_storefront_color(ctx: "Context"):
    """ONES case #T3579: Verify that curator sets up Storefront color"""
    vars = ctx

    profile = ctx.api.storefront.self_profile(token="linda997_token").json()["data"]
    store_tabs = (profile.get("storeFront") or {}).get("storeTabs", [])

    body = {
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
                    "backgroundColor": "#E9DCDC",
                    "textColor": "#363331",
                    "cardBackgroundColor": "#B8E986",
                    "cardBorderColor": "#000000",
                    "buttonBackgroundColor": "#8B572A",
                    "buttonTextColor": "#363331",
                },
            },
        },
    }

    resp = ctx.api.storefront.update(body=body, token="linda997_token")
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.message").equals("success")

    fetched = ctx.api.storefront.self_profile(token="linda997_token")
    expect(fetched).json("$.data.storeFront.colors.backgroundColor").equals("#E9DCDC")
    expect(fetched).json("$.data.storeFront.colors.textColor").equals("#363331")
    expect(fetched).json("$.data.storeFront.colors.cardBackgroundColor").equals("#B8E986")
    expect(fetched).json("$.data.storeFront.colors.cardBorderColor").equals("#000000")
    expect(fetched).json("$.data.storeFront.colors.buttonBackgroundColor").equals("#8B572A")
    expect(fetched).json("$.data.storeFront.colors.buttonTextColor").equals("#363331")

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
