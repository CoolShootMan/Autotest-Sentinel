"""ONES case: Verify protocol selection and saving in Add new link window"""
NAME = "Verify protocol selection and saving in Add new link window"
TAGS = ["p0", "socials", "suite:linda"]
PRIORITY = 0
CASE_ID = "SdWZQAze"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect

if TYPE_CHECKING:
    from core.context import Context


def test_protocol_selection_add_link(ctx: "Context"):
    """ONES case #SdWZQAze: create links with https, mailto, tel, sms protocols"""
    vars = ctx

    link_ids = []
    cases = [
        ("https://example.com", "Web Link"),
        ("mailto:support@pear.us", "Email Link"),
        ("tel:+14155551234", "Phone Link"),
        ("sms:+14155551234", "SMS Link"),
    ]
    for url, title in cases:
        resp = ctx.api.links.create(body={
            "title": title,
            "url": url,
            "type": "GENERAL",
            "showBelowTitle": False,
        }, token="linda997_token")
        expect(resp).json("$.code").equals("200")
        expect(resp).json("$.data.url").equals(url)
        link_ids.append(resp.path("$.data.id"))

    for lid in link_ids:
        ctx.api.links.delete_by_id(id=lid, token="linda997_token")
