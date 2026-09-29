# ============================================================
# Shared UI locators — single source of truth for selectors.
#
# Usage in YAML:  locator: "{{@key_name}}"
# The framework replaces {{@key_name}} with the actual selector at runtime.
# Group selectors by page/feature so they stay discoverable.
# ============================================================

# --- Admin: User profile > Features tab ---
ADMIN_FEATURES = {
    "features_tab":          "#platform-tab-9",
    "flag_header_checkbox":  "tr:has(td:has-text('hideStorefrontHeader')) input[type='checkbox']",
    "flag_cover_checkbox":   "tr:has(td:has-text('hideStorefrontCover')) input[type='checkbox']",
}

# --- Storefront (visitor-facing shop page) ---
STOREFRONT = {
    "login_btn":   "text=Log in",
    "cover_image":  "img[alt='background']",
}

# --- Meta Pixel post page (mehost.cn) ---
META_PIXEL = {
    "pixel_script":       "script[src*='connect.facebook.net']",
    "btn_buy_ticket":     "button:has-text('Buy Ticket') >> nth=0",
    "dialog":             "[role='dialog']",
    "btn_buy_now":        "[role='dialog'] button:has-text('Buy now')",
    "btn_continue_card":  "button:has-text('Continue with credit card')",
}

# Flattened dict for {{@key}} lookup (keys must be unique across groups)
LOCATORS = {}
for _group in (ADMIN_FEATURES, STOREFRONT, META_PIXEL):
    for _k, _v in _group.items():
        if _k in LOCATORS:
            raise ValueError(f"Duplicate locator key: {_k}")
        LOCATORS[_k] = _v
