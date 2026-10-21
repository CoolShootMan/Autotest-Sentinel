"""ONES case: Verify that the currently saved shop topic is a brand new preset"""
NAME = "Verify that the currently saved shop topic is a brand new preset and does not overwrite the previous preset"
TAGS = ["p1", "style", "suite:linda"]
PRIORITY = 1
CASE_ID = "54Yyfd5R"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_t4095_verify_saved_shop_topic_is_new_preset(ctx: "Context"):
    """ONES case #T4095: saved theme preset appears in list and does not overwrite prior preset"""
    vars = ctx

    me = ctx.api.storefront.self_profile(token="linda997_token").json()["data"]
    curator_id = me["id"]

    created_ids = []
    try:
        for name in ["apifox-test-preset-a", "apifox-test-preset-b"]:
            resp = ctx.api.storefront.create_theme(body={
                "curatorId": curator_id,
                "themeName": name,
                "styleSettings": {
                    "colors": {"backgroundColor": "#972C2C", "buttonBackgroundColor": "#B8A797"},
                    "fonts": {"fontFamily": "Dosis", "fontSize": 14},
                },
            }, token="linda997_token")
            expect(resp).json("$.code").equals("200")
            tid = resp.json()["data"]["id"]
            created_ids.append(tid)

        listing = ctx.api.storefront.theme_list(token="linda997_token")
        expect(listing).json("$.code").equals("200")
        names = [item["themeName"] for item in listing.json()["data"]["items"]]
        assert "apifox-test-preset-a" in names, f"preset A missing: {names}"
        assert "apifox-test-preset-b" in names, f"preset B missing: {names}"
    finally:
        for tid in created_ids:
            ctx.api.storefront.delete_theme(theme_id=tid, token="linda997_token")
