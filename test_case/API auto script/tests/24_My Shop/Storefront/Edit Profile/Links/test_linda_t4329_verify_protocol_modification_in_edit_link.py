"""ONES case: Verify protocol modification and saving in Edit link window"""
NAME = "Verify protocol modification and saving in Edit link window"
TAGS = ["p0", "links", "suite:linda"]
PRIORITY = 0
CASE_ID = "UpG1hPou"
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


def test_update_link_protocol(ctx: "Context"):
    """ONES case #UpG1hPou: edit a link to change its URL/protocol and verify persistence"""
    vars = ctx
    uid = _user_id(ctx)

    resp_create = ctx.api.links.create(body={
        "title": "Protocol Test Link",
        "url": "https://old.example.com",
        "type": "GENERAL",
        "showBelowTitle": False,
    }, token="linda997_token")
    expect(resp_create).json("$.code").equals("200")
    ctx.extract("link_id", resp_create, "$.data.id")

    resp_update = ctx.api.links.update_by_id(id=ctx["link_id"], body={
        "title": "Protocol Test Link Updated",
        "url": "https://new.example.com/page",
    }, token="linda997_token")
    expect(resp_update).json("$.code").equals("200")
    expect(resp_update).json("$.data.title").equals("Protocol Test Link Updated")
    expect(resp_update).json("$.data.url").equals("https://new.example.com/page")

    resp_get = ctx.api.links.by_id(id=ctx["link_id"], token="linda997_token")
    expect(resp_get).json("$.code").equals("200")
    expect(resp_get).json("$.data.title").equals("Protocol Test Link Updated")
    expect(resp_get).json("$.data.url").equals("https://new.example.com/page")

    ctx.api.links.delete_by_id(id=ctx["link_id"], token="linda997_token")
