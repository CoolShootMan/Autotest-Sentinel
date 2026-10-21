"""ONES case: Verify that Curator adds links and changes their positions (reorder)"""
NAME = "Verify that Curator adds 10 links and changes their positions"
TAGS = ["p0", "links", "suite:linda"]
PRIORITY = 0
CASE_ID = "Q5StUacM"
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


def test_reorder_links(ctx: "Context"):
    """ONES case #Q5StUacM: create 2 links, reorder them via PUT /user-link/sorts"""
    vars = ctx
    uid = _user_id(ctx)

    id_a = None
    id_b = None
    try:
        resp_a = ctx.api.links.create(body={
            "title": "Spotify - Autotest Playlist",
            "url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
            "type": "GENERAL",
            "showBelowTitle": False,
        }, token="linda997_token")
        expect(resp_a).json("$.code").equals("200")
        id_a = resp_a.path("$.data.id")

        resp_b = ctx.api.links.create(body={
            "title": "Apple Music - Autotest Radio",
            "url": "https://music.apple.com/us/radio/apple-music-1",
            "type": "GENERAL",
            "showBelowTitle": False,
        }, token="linda997_token")
        expect(resp_b).json("$.code").equals("200")
        id_b = resp_b.path("$.data.id")

        resp_sort = ctx.api.links.sorts(body={
            "items": [
                {"id": id_b, "position": 0},
                {"id": id_a, "position": 1},
            ]
        }, token="linda997_token")
        expect(resp_sort).json("$.code").equals("200")

        resp_list = ctx.api.links.list_by_user_id(user_id=uid, token="linda997_token")
        expect(resp_list).json("$.code").equals("200")
        expect(resp_list).json("$.data.items[0].id").equals(id_b)
    finally:
        for lid in [id_a, id_b]:
            if lid:
                ctx.api.links.delete_by_id(id=lid, token="linda997_token")
