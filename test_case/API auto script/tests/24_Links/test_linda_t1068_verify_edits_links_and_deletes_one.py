"""ONES case: Verify that Curator edits 3 links and deletes 1 link during editing"""
NAME = "Verify that Curator edits 3 links to test.com and deletes 1 link during editing"
TAGS = ["p0", "links", "suite:linda"]
PRIORITY = 0
CASE_ID = "TeTSm9Gu"
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


def test_edit_links_and_delete_one(ctx: "Context"):
    """ONES case #TeTSm9Gu: create 3 links, edit their URLs, delete one"""
    vars = ctx
    uid = _user_id(ctx)

    link_ids = []
    for i in range(3):
        resp = ctx.api.links.create(body={
            "title": f"Autotest Link {i}",
            "url": f"https://www.youtube.com/playlist?list=autotest{i}",
            "type": "GENERAL",
            "showBelowTitle": False,
        }, token="linda997_token")
        expect(resp).json("$.code").equals("200")
        link_ids.append(resp.path("$.data.id"))

    for i, lid in enumerate(link_ids):
        resp = ctx.api.links.update_by_id(id=lid, body={
            "title": f"Edited Link {i}",
            "url": "https://music.youtube.com/playlist?list=autotest-edited",
        }, token="linda997_token")
        expect(resp).json("$.code").equals("200")
        expect(resp).json("$.data.url").equals("https://music.youtube.com/playlist?list=autotest-edited")

    delete_resp = ctx.api.links.delete_by_id(id=link_ids[1], token="linda997_token")
    expect(delete_resp).json("$.code").equals("200")

    for lid in link_ids:
        if lid != link_ids[1]:
            ctx.api.links.delete_by_id(id=lid, token="linda997_token")
