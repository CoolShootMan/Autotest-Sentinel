"""ONES case: Verify that users can switch the layout mode of the shop page"""
NAME = "Verify that users can switch the layout mode of the shop page"
TAGS = ["p0", "style", "suite:linda"]
PRIORITY = 0
CASE_ID = "VcyTzMBg"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_t4092_verify_user_can_switch_layout_mode(ctx: "Context"):
    """ONES case #T4092: Verify that users can switch the layout mode of the shop page"""
    vars = ctx

    profile = ctx.api.storefront.self_profile(token="linda997_token").json()["data"]
    store_tabs = (profile.get("storeFront") or {}).get("storeTabs", [])

    resp = ctx.api.storefront.layout(body={
        "storeTabs": store_tabs,
        "productCardLayout": "TopAligned",
        "linkCardLayout": "Compact",
    }, token="linda997_token")
    expect(resp).json("$.code").equals("200")
    expect(resp).json("$.data.productCardLayout").equals("TopAligned")
    expect(resp).json("$.data.linkCardLayout").equals("Compact")

    fetched = ctx.api.storefront.self_profile(token="linda997_token")
    expect(fetched).json("$.data.storeFront.productCardLayout").equals("TopAligned")
    expect(fetched).json("$.data.storeFront.linkCardLayout").equals("Compact")

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
