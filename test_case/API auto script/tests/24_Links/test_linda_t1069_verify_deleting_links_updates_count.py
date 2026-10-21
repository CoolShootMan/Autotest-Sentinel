"""ONES case: Verify after deleting 2 Links the count in Links is updated"""
NAME = "After verifying that Curator deletes 2 Links, the count in the upper right corner of Links is updated"
TAGS = ["p0", "links", "suite:linda"]
PRIORITY = 0
CASE_ID = "YBHW17eS"
ENV_NAME = "Release"

import base64
import json
from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def _user_id(ctx: "Context") -> str:
    tok = ctx.get("linda997_token") or ""
    parts = tok.split(".")
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    return json.loads(base64.urlsafe_b64decode(payload)).get("userId")


def test_delete_links_updates_count(ctx: "Context"):
    """ONES case #YBHW17eS: create 2 links, delete both, verify list count decreases"""
    vars = ctx
    uid = _user_id(ctx)

    link_ids = []
    for i in range(2):
        resp = ctx.api.links.create(body={
            "title": f"Delete Target {i}",
            "url": f"https://deleteme{i}.com",
            "type": "GENERAL",
            "showBelowTitle": False,
        }, token="linda997_token")
        expect(resp).json("$.code").equals("200")
        link_ids.append(resp.path("$.data.id"))

    for lid in link_ids:
        resp = ctx.api.links.delete_by_id(id=lid, token="linda997_token")
        expect(resp).json("$.code").equals("200")

    resp_list = ctx.api.links.list_by_user_id(user_id=uid, token="linda997_token")
    expect(resp_list).json("$.code").equals("200")
    for lid in link_ids:
        expect(resp_list).json("$.data.items..id").not_includes(lid)
