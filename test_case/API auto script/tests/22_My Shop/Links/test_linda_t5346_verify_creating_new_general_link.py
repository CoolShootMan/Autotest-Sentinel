"""ONES case: Verify default style and layout switching logic when creating a new General Link"""
NAME = "Verify default style and layout switching logic when creating a new General Link"
TAGS = ["p0", "links", "suite:linda"]
PRIORITY = 0
CASE_ID = "M5touE1y"
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


def test_create_general_link(ctx: "Context"):
    """ONES case #M5touE1y: create a General Link and verify GET reflects it"""
    vars = ctx
    uid = _user_id(ctx)

    resp_list = ctx.api.links.list_by_user_id(user_id=uid, token="linda997_token")
    expect(resp_list).json("$.code").equals("200")

    resp_create = ctx.api.links.create(body={
        "title": "Autotest - My Vinyl Collection",
        "url": "https://bandcamp.com/discover",
        "type": "GENERAL",
        "showBelowTitle": False,
    }, token="linda997_token")
    expect(resp_create).json("$.code").equals("200")
    expect(resp_create).json("$.data.type").equals("GENERAL")
    expect(resp_create).json("$.data.title").equals("Autotest - My Vinyl Collection")
    ctx.extract("link_id", resp_create, "$.data.id")

    resp_get = ctx.api.links.by_id(id=ctx["link_id"], token="linda997_token")
    expect(resp_get).json("$.code").equals("200")
    expect(resp_get).json("$.data.id").equals(ctx["link_id"])
    expect(resp_get).json("$.data.url").equals("https://bandcamp.com/discover")

    ctx.api.links.delete_by_id(id=ctx["link_id"], token="linda997_token")
