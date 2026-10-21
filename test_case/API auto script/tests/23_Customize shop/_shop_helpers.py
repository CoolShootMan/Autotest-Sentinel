"""Shared helpers for the Customize-shop API suite.

Every test follows the same safe read-modify-write cycle:

1. ``snapshot(ctx)``  -> GET the current curator profile (edit-page source of truth).
2. ``build_info(snap, **over)`` -> a ``userInfo`` object that *echoes* every current
   field (storeName, vanityUrl, socialMedias, storeFront, ...) and overrides only the
   field under test. Because storeName/vanityUrl are copied from the live snapshot,
   the shop name and shop URL are **never** changed.
3. ``save(ctx, info)`` -> PUT /store-front.
4. ``restore(ctx, snap)`` -> PUT /store-front writing the snapshot back (teardown).

This module is intentionally not collected by pytest (name does not start with
``test_``).
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.context import Context

TOKEN = "linda997_token"

# Two distinct, valid cloudinary assets reused for avatar/cover mutations.
IMG_A = "https://res.cloudinary.com/dr9io1zjv/image/upload/v1764821680/setting/wrbmwobccxtbsy1e79h0.webp"
IMG_B = "https://res.cloudinary.com/dr9io1zjv/image/upload/c_fill,w_200,h_200/v1764821680/setting/wrbmwobccxtbsy1e79h0.webp"


def vanity(ctx: "Context") -> str:
    """The shop's vanity URL, read from environment config (never hardcoded)."""
    return ctx.get("partner997_vanityUrl")


def snapshot(ctx: "Context") -> dict[str, Any]:
    """GET /user/vanity-url/{vanity} and return the ``data`` block."""
    r = ctx.api.users.profile_by_vanity_url(vanityUrl=vanity(ctx), token=TOKEN, app_headers=True)
    return r.json_safe().get("data") or {}


def compact(ctx: "Context") -> dict[str, Any]:
    """GET /user/shop-info/{vanity} and return the ``data`` block."""
    r = ctx.api.users.shop_info_by_vanity_url(vanityUrl=vanity(ctx), token=TOKEN, app_headers=True)
    return r.json_safe().get("data") or {}


def build_info(snap: dict[str, Any], **over: Any) -> dict[str, Any]:
    """Echo every current field into a PUT /store-front ``userInfo`` payload.

    ``storeName`` / ``vanityUrl`` are copied verbatim from ``snap`` so they are
    preserved (never renamed). Pass keyword overrides to mutate only the field
    under test.
    """
    info: dict[str, Any] = {
        "storeName": snap["storeName"],
        "vanityUrl": snap["vanityUrl"],
        "description": snap.get("description") or "",
        "subTitle": snap.get("subTitle") or "",
        "logo": snap.get("logo"),
        "backgroundSource": snap.get("backgroundSource"),
        "socialMedias": snap.get("socialMedias") or [],
        "storeFront": snap.get("storeFront") or {"storeTabs": []},
        "displayShopNameOnStorefront": snap.get("displayShopNameOnStorefront"),
    }
    info.update(over)
    # drop explicit None for the display flag unless it was intentionally set
    if info.get("displayShopNameOnStorefront") is None:
        info.pop("displayShopNameOnStorefront", None)
    return info


def save(ctx: "Context", info: dict[str, Any]):
    """PUT /store-front with a userInfo payload."""
    return ctx.api.storefront.update(
        body=json.dumps({"userInfo": info}), token=TOKEN, app_headers=True)


def restore(ctx: "Context", snap: dict[str, Any]):
    """Teardown: write the snapshot back verbatim (restores all fields)."""
    return save(ctx, build_info(snap))
