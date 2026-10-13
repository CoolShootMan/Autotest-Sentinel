# Autotest-monster Actions Module Documentation

This document is auto-generated from `__init__.py` and provides a detailed reference for all action commands and their routing mechanisms.

## 1. Core Routing Mechanism (`get_action`)

When parsing YAML test cases, the framework uses `get_action(name)` to locate the corresponding execution handler. It employs a **two-layer matching strategy**:

1. **Exact Match**: First looks up the exact key in the `ACTIONS` dictionary. If found, returns the handler directly.
2. **Prefix Match**: If exact match fails, performs fuzzy matching via `name.startswith(...)` rules. This enables dynamic naming like `click_login_button` or `verify_user_name` to automatically route to `smart_click` or `verify_text_visible`.

---

## 2. Base Interaction Actions

Common browser interactions invoked via prefix mapping or exact naming:

| Action Prefix / Name | Binds To | Description |
| :--- | :--- | :--- |
| `open` | `open_url` | Opens a specified URL |
| `click`, `R_click`, `l_click` | `smart_click` | Smart click — fast locator, no full-page scan by default |
| `fill` | `smart_fill` | Smart text input |
| `fill_numeric` | `fill_numeric` | Numeric-only input |
| `check`, `uncheck` | `smart_check` | Check or uncheck checkboxes/radio buttons |
| `swipe`, `scroll` | `smart_swipe` | Page swipe or in-element scroll |
| `press` | `smart_press` | Keyboard actions (e.g. Enter, Escape) |
| `sleep` | `smart_sleep` | Forced wait (sleep) |
| `upload`, `wait_for_upload` | `smart_upload` | File upload operations |
| `screenshot` | `smart_screenshot` | Smart screenshot |
| `if_` | `smart_if` | **YAML conditional execution** — branches the action flow based on conditions |

---

## 3. Verification & Assertion Actions

All actions starting with `verify_`, primarily used for test result checking:

| Action Prefix / Name | Binds To | Description |
| :--- | :--- | :--- |
| `verify` (generic prefix) | `verify_text_visible` | Verifies text or element is visible |
| `verify_hidden` | `verify_text_hidden` | Verifies text or element is hidden |
| `verify_value` | `verify_value` | Verifies element's specific value |
| `verify_toast` | `verify_toast_message` | Verifies global toast notification text |
| `verify_no_sibling` | `verify_no_sibling_text` | Verifies a sibling text does not exist |
| `verify_element_style` | `verify_element_style` | Verifies element's CSS style |
| `verify_child_element_count` | `verify_child_element_count` | Verifies number of child elements |

---

## 4. Advanced & System Control Actions

Actions involving session management, modal handling, and page state waiting:

| Action Prefix / Name | Binds To | Description |
| :--- | :--- | :--- |
| `create_session`, `session_` | `create_session` | Creates a new browser session context |
| `switch_session` | `switch_session` | Switches between multiple sessions |
| `close_session` | `close_session` | Closes the current session |
| `handle_modal` | `handle_modal` | Manually handles a specific modal |
| `auto_handle_modals` | `auto_handle_modals` | Auto-handles common page modals |
| `wait_for_selector` | `wait_for_selector` | Waits for a specific DOM element to appear |
| `wait_for_url`, `verify_navigation` | `wait_for_url` | Waits for page navigation to a specific URL |
| `wait_` (generic prefix) | `smart_wait` | Smart wait |

---

## 5. Smart Scan Click — `smart_click_scan`

- **Trigger keywords**: `R_click_scan`, `click_scan`
- **Bound method**: `smart_click_scan(page, v)`
- **Core description**:
  This is the full-fallback version of `smart_click` with `fallback_scan=True` forced on internally. It triggers **Page-level Search and AI-assisted element location**.
- **Recommended for**: Complex scenarios where traditional locators struggle, such as nested modals, multi-layer Drawers, or elements heavily obscured by containers. For normal cases, use `click` directly to ensure speed.

---

## 6. Business Domain Actions

Framework encapsulates many domain-specific methods for Product, Form, Layout, and other modules.

### Module / Component Operations
- `click_module_edit_button`: Clicks the module edit button
- `click_add_new_product`: Clicks "Add New Product"
- `click_module_collapse` / `expand`: Collapses or expands a module
- `drag_element` / `drag_and_drop_by_coordinates`: Element drag-and-drop operations

### Product & Social Operations
- `click_product_image`: Clicks a product image
- `verify_post_exists`: Verifies a post exists
- `R_click_follow`: Smart follow action
- `select_replacement_product`: Selects a replacement product (maps to `select_a_for_b` and similar syntax)

### Form & Layout Operations
- `verify_submission_details`: Verifies form submission details
- `download_submission_csv` / `verify_csv_data`: CSV report download and data verification
- `goto_storefront`: Navigates to the Storefront (with layout suffixes like `waterfall`, etc.)
- `publish_button_click`: Clicks the publish button and handles related flow
