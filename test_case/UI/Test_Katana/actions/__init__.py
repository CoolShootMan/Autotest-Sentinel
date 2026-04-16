
from .base import (
    open_url,
    smart_click,
    smart_fill,
    fill_numeric,
    smart_check,
    smart_swipe,
    smart_sleep,
    smart_press,
    smart_upload,
    smart_screenshot,
    smart_if,
    smart_wait,
    wait_for_selector,
    wait_for_url,
    save_html,
    click_modal_close,
    verify_text_visible,
    verify_text_hidden,
    verify_value,
    verify_value_near,
    verify_all_commission_values,
    reload_page,
    execute_not_recognized_scan,
    wait_toast,
    scroll_to_bottom,
)

from .module import click_module_edit_button, click_module_paragraph, click_add_new_product, click_module_add_new, click_module_post_view_event_cta, click_module_collapse, click_module_expand, verify_module_collapsed, verify_module_expanded, verify_element_style
from .product import (

    click_add_button_regex, verify_product_clickable, click_products_nav_icon,
    click_products_tab_t2129, click_bell_button, click_product_plus_button,
    click_product_image, verify_post_exists, R_click_follow, 
    click_close_toast, verify_toast_message, select_replacement_product,
    click_by_coordinates, click_relative_to_selector
)
from .form import (
    verify_submission_details, verify_message_content, click_form_more_menu,
    click_submission_details_back, click_contact_form,
    download_submission_csv, verify_csv_data, capture_total_count
)
from .layout import (
    verify_top_aligned_layout, verify_waterfall_layout,
    goto_storefront, publish_button_click, verify_navigation_after_publish,
    click_mui_svg_icon, click_products_text, wait_for_product_cards
)
from .collabs import verify_invitation_link_clipboard

# Registry for exact match keys
ACTIONS = {
    "open": open_url,
    # Generic overrides
    "click_modal_close": click_modal_close,
    "R_click": smart_click,
    "fill": smart_fill,
    "check": smart_check,
    "swipe": smart_swipe,
    "sleep": smart_sleep,
    "press": smart_press,
    "upload": smart_upload,
    "screenshot": smart_screenshot,
    
    # Module specific
    "click_module_edit_button": click_module_edit_button,
    "click_module_paragraph": click_module_paragraph,
    "click_add_new_product": click_add_new_product,
    "click_module_post_view_event_cta": click_module_post_view_event_cta,
    "click_module_collapse": click_module_collapse,
    "click_module_expand": click_module_expand,
    "verify_module_collapsed": verify_module_collapsed,
    "verify_module_expanded": verify_module_expanded,
    "verify_element_style": verify_element_style,
    
    # Product/Social specific
    "click_add_button_regex": click_add_button_regex,
    "click_add_button_regex_final": click_add_button_regex,
    "verify_product_clickable": verify_product_clickable,
    "click_products_nav_icon": click_products_nav_icon,
    "click_products_tab_t2129": click_products_tab_t2129,
    "click_bell_button": click_bell_button,
    "click_bell_button_reopen": click_bell_button, # Same handler
    "click_product_plus_button": click_product_plus_button,
    "click_product_image": click_product_image,
    "verify_post_exists": verify_post_exists,
    "R_click_follow": R_click_follow,
    
    # Form specific
    "verify_submission_details": verify_submission_details,
    "verify_message_content": verify_message_content,
    "verify_email_content": verify_message_content, # Reuse
    "verify_phone_content": verify_message_content, # Reuse
    "click_form_more_menu": click_form_more_menu,
    "click_submission_details_back": click_submission_details_back,
    "click_contact_form": click_contact_form,

    # Layout specific
    "verify_top_aligned_layout": verify_top_aligned_layout,
    "verify_waterfall_layout": verify_waterfall_layout,
    "verify_follow_message": verify_toast_message,
    "verify_unfollow_message": verify_toast_message,
    "verify_unfollow_message_final": verify_toast_message,
    "verify_refollow_message": verify_toast_message,

    # T3370 Layout Specific
    "goto_storefront_top_aligned": goto_storefront,
    "goto_storefront_waterfall": goto_storefront,
    "publish_button_click_top_aligned": publish_button_click,
    "publish_button_click_waterfall": publish_button_click,
    "verify_navigation_after_publish_top_aligned": verify_navigation_after_publish,
    "verify_navigation_after_publish_waterfall": verify_navigation_after_publish,
    "click_mui_svg_icon_top_aligned": click_mui_svg_icon,
    "click_mui_svg_icon_waterfall": click_mui_svg_icon,
    "click_products_text_top_aligned": click_products_text,
    "click_products_text_waterfall": click_products_text,
    "wait_for_product_cards_top_aligned": wait_for_product_cards,
    "wait_for_product_cards_waterfall": wait_for_product_cards,
    "check_label_top_aligned": smart_check,
    "check_label_waterfall": smart_check,
    "verify_invitation_link_clipboard": verify_invitation_link_clipboard,
    "verify_text_visible": verify_text_visible,
    "verify_text_hidden": verify_text_hidden,
    "verify_value": verify_value,
    "verify_value_near": verify_value_near,
    "verify_all_commission": verify_all_commission_values,
    "click_module_add_new": click_module_add_new,
    "verify_product_visible": verify_text_visible,
    "select_replacement_product": select_replacement_product,
    "click_by_coordinates": click_by_coordinates,
    "click_relative_to_selector": click_relative_to_selector,
    "reload": reload_page,
    "execute_not_recognized_scan": execute_not_recognized_scan,
    "download_submission_csv": download_submission_csv,
    "verify_csv_data": verify_csv_data,
    "capture_total_count": capture_total_count,
    "scroll_to_bottom": scroll_to_bottom,
}


def get_action(name):
    """
    Get action function by name.
    Supports exact match from ACTIONS registry,
    and fallback to smart handlers for prefixes.
    """
    # 1. Exact match
    if name in ACTIONS:
        return ACTIONS[name]
    
    # 2. Prefix mapping
    if name.startswith("click_module_edit_button"):
        return click_module_edit_button
    elif name.startswith("click_module_paragraph"):
        return click_module_paragraph
    elif name.startswith("click_add_new_product"):
        return click_add_new_product
    elif name.startswith("click_module_add_new"):
        return click_module_add_new
    elif name.startswith("click_module_post_view_event_cta"):
        return click_module_post_view_event_cta

    if name.startswith("R_click") or name.startswith("click") or name.startswith("l_click"):
        return smart_click
    elif name.startswith("if_"):
        return smart_if
    elif name.startswith("fill_numeric"):
        return fill_numeric
    elif name.startswith("fill"):
        return smart_fill
    elif name.startswith("check"):
        return smart_check
    elif name.startswith("swipe") or name.startswith("scroll"):
        return smart_swipe
    elif name.startswith("sleep"):
        return smart_sleep
    elif name.startswith("press"):
        return smart_press
    elif name.startswith("upload") or name.startswith("wait_for_upload"):
        return smart_upload
    elif name.startswith("screenshot"):
        return smart_screenshot
    elif name.startswith("save_html") or name.startswith("save_full_html"):
        return save_html
    elif name.startswith("wait_for_selector"):
        return wait_for_selector
    elif name.startswith("wait_for_url") or name.startswith("verify_navigation"):
        return wait_for_url
    elif name.startswith("open"):
        return open_url
    elif name.startswith("reload"):
        return reload_page
    elif name.startswith("wait_toast"):
        return wait_toast
    elif name.startswith("wait_"):
        return smart_wait

    
    # Special prefixes that map to specific functions
    if name.startswith("click_close_toast"):
        return click_close_toast
    
    if name.startswith("verify_toast"):
        return verify_toast_message
    if name.startswith("verify_hidden"):
        return verify_text_hidden
    if name.startswith("verify_value"):
        return verify_value
    if name.startswith("verify"):
        return verify_text_visible

        
    if name.startswith("select_a_for_b") or name.startswith("select_b_for_c"):
        return select_replacement_product
        
    # Add other prefix handlers here as we migrate them
    
    return None
