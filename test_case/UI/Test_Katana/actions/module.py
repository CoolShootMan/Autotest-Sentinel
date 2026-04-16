import re as _re
from playwright.sync_api import Page
from loguru import logger
from .base import smart_click

def click_module_edit_button(page: Page, v: dict):
    module_name = v.get("module_name")
    logger.info(f"Clicking edit button for module: {module_name}")
    # Use double-locator pattern: Find the container that has both the module name and buttons
    # Then click the second button (usually the 'More/Edit' icon)
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button")).last
    container.scroll_into_view_if_needed()
    btn = container.get_by_role("button").nth(1)
    btn.wait_for(state="visible", timeout=10000)
    btn.click(timeout=15000)
    page.wait_for_timeout(1000) # Wait for potential UI transitions

def click_module_paragraph(page: Page, v: dict):
    # Click on module paragraph using smart logic
    smart_click(page, {"role": "paragraph", "name": v.get("text"), "timeout": 10000, **v})

def click_add_new_product(page: Page, v: dict):
    # Click "Add new" button within specific module header
    module_name = v.get("module_name")
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    container.get_by_role("button", name="Add new").click(timeout=15000)

def click_module_add_new(page: Page, v: dict):
    # Click the "Add new" button specifically for the named module
    # Uses refined double-locator pattern:
    module_name = v.get("module_name")
    logger.info(f"Clicking 'Add new' for module: {module_name}")
    
    # 1. Find the deepest div that contains the module title AND an 'Add new' button
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    
    # 2. Click the button within that container
    container.get_by_role("button", name="Add new").click(timeout=10000)

def click_module_post_view_event_cta(page: Page, v: dict):
    post_title = v.get("post_title")
    module_name = v.get("module_name")
    logger.info(f"Clicking view event cta for module: {module_name} and post title: {post_title}")
    container = page.locator("div", has_text=module_name).filter(has_text=post_title).last
    container.get_by_role("button", name="View event").first.click(timeout=10000)

def click_module_collapse(page: Page, v: dict):
    """Collapse a module by clicking its arrow-up icon."""
    module_name = v.get("module_name")
    logger.info(f"Collapsing module: {module_name}")
    # Locate the definitive module header container
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    container.get_by_test_id("arrow-up-icon").first.click(timeout=10000)

def click_module_expand(page: Page, v: dict):
    """Expand a module by clicking its toggle icon.
    The test-id does not change to arrow-down, so we click the same arrow-up-icon.
    """
    module_name = v.get("module_name")
    logger.info(f"Expanding module: {module_name}")
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    container.get_by_test_id("arrow-up-icon").first.click(timeout=10000)

def verify_module_collapsed(page: Page, v: dict):
    """Verifies that a module's body is collapsed by checking its overall container height shrinks."""
    module_name = v.get("module_name")
    logger.info(f"Verifying module '{module_name}' is collapsed by measuring height...")
    # Find the top-level outer wrapper containing this module header.
    # Usually it's the parent of the header container.
    header = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    
    import time
    start_time = time.time()
    # Poll for height to shrink (e.g. < 150px means body is folded, just header left)
    while time.time() - start_time < 5.0:
        box = header.locator("..").bounding_box()
        if box and box['height'] < 150:
            logger.info(f"Module '{module_name}' is successfully collapsed (Visual Height: {box['height']:.1f}px)")
            return
        time.sleep(0.5)
    raise AssertionError(f"Module '{module_name}' did not collapse. Current Height: {box['height']:.1f}px")

def verify_module_expanded(page: Page, v: dict):
    """Verifies that a module's body is expanded by checking its overall container height grows."""
    module_name = v.get("module_name")
    logger.info(f"Verifying module '{module_name}' is expanded by measuring height...")
    header = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last

    import time
    start_time = time.time()
    # Poll for height to grow (e.g. > 150px means body is unfolded)
    while time.time() - start_time < 5.0:
        box = header.locator("..").bounding_box()
        if box and box['height'] > 150:
            logger.info(f"Module '{module_name}' is successfully expanded (Visual Height: {box['height']:.1f}px)")
            return
        time.sleep(0.5)
    raise AssertionError(f"Module '{module_name}' did not expand. Current Height: {box['height']:.1f}px")


def verify_no_sibling_text(page: Page, v: dict):
    """
    Verify that an element's siblings do NOT contain the specified text.
    
    Supported parameters:
    - locator: Element locator (required)
    - index: Element index, supports negative values like -1 for last (default: -1)
    - text: The text that should NOT exist in sibling elements (required)
    - timeout: Timeout in milliseconds (default: 5000)
    
    Usage in YAML:
        verify_no_sibling_add_new:
            locator: '[data-testid="base-more-horiz-icon-cta"]'
            index: -1
            text: 'Add new'
    """
    locator_str = v.get("locator")
    text = v.get("text", "Add new")
    target_index = v.get("index", -1)
    timeout = v.get("timeout", 5000)
    
    if not locator_str:
        raise ValueError("verify_no_sibling_text: 'locator' parameter is required")
    
    logger.info(f"Verifying no sibling with text '{text}' for element: {locator_str}[{target_index}]")
    
    # Find the target element
    el = page.locator(locator_str).nth(target_index)
    el.wait_for(state="visible", timeout=timeout)
    
    # Check parent container for siblings containing the text
    parent = el.locator("xpath=..")
    sibling_with_text = parent.locator(f":text-is('{text}')").or_(
        parent.locator(f"button:has-text('{text}')")
    ).or_(
        parent.locator(f"[data-testid]:has-text('{text}')")
    )
    
    count = sibling_with_text.count()
    if count > 0:
        # Also check visibility
        for i in range(count):
            if sibling_with_text.nth(i).is_visible():
                page.screenshot(path=f"fail_sibling_{text[:10]}.png")
                raise AssertionError(
                    f"Found sibling element with text '{text}' near '{locator_str}[{target_index}]', "
                    f"but it should NOT exist for co-seller."
                )
    
    logger.info(f"Confirmed: no sibling with text '{text}' found near '{locator_str}[{target_index}]'")


def verify_element_style(page: Page, v: dict):
    """
    Verify CSS style properties of an element

    Supported parameters:
    - locator: Element locator (required)
    - container: Container element name/text to search within (optional)
    - container_filter: Filter criteria for finding stable parent container (optional)
      - attributes: Dict of attribute names to match (e.g., {"data-testid": "module"})
      - exclude_dynamic_attrs: List of attribute patterns to exclude (e.g., ["id", "class"])
      - max_levels: Maximum number of parent levels to search (default: 5)
    - property: CSS property name to verify (single string or list)
    - expected: Expected value (single value or dictionary)
    - operator: Comparison operator, default 'equals', supports: equals, contains, gt, lt, gte, lte
    - timeout: Timeout in milliseconds, default 5000

    Usage examples:

    1. Verify single property:
       verify_element_style:
           locator: ".my-element"
           property: "display"
           expected: "none"

    2. Verify within a container:
       verify_element_style:
           container: "My Module"
           locator: ".button"
           property: "color"
           expected: "rgb(255, 0, 0)"

    3. Verify with smart container filtering:
       verify_element_style:
           container: "My Module"
           locator: ".button"
           property: "height"
           expected: "100px"

    4. Verify multiple properties:
       verify_element_style:
           locator: ".my-element"
           property: ["display", "color"]
           expected: {"display": "none", "color": "rgb(255, 0, 0)"}

    5. Verify numeric comparison:
       verify_element_style:
           locator: ".my-element"
           property: "height"
           expected: "100px"
           operator: "gte"  # Greater than or equal

    6. Get and print all styles (for debugging):
       verify_element_style:
           locator: ".my-element"
           property: "all"  # Print all computed styles
    """
    locator_str = v.get("locator")
    container_name = v.get("container")
    if not locator_str:
        raise ValueError("verify_element_style: 'locator' parameter is required")

    timeout = v.get("timeout", 5000)
    container_filter = v.get("container_filter")

    # Apply container filter if specified
    if container_name:
        logger.info(f"Searching within container: {container_name}")

        # Find initial container by text
        container = page.locator("div", has_text=container_name).locator(f"xpath={container_filter}").last

        locator = container.locator(locator_str)
    else:
        locator = page.locator(locator_str)

    # Wait for element to be visible
    locator.wait_for(state="visible", timeout=timeout)

    property_names = v.get("property")
    expected = v.get("expected")
    operator = v.get("operator", "equals")

    container_info = f" (in container: {container_name})" if container_name else ""
    logger.info(f"Verifying element style - Locator: {locator_str}{container_info}, Property: {property_names}")

    # If 'all', print all computed styles and return
    if property_names == "all":
        styles = locator.evaluate("el => window.getComputedStyle(el)")
        logger.info(f"Element complete stylesheet:\n{styles}")
        return

    # Support single property or property list
    if isinstance(property_names, str):
        properties = [property_names]
    else:
        properties = property_names

    # Get all computed styles
    computed_styles = locator.evaluate("el => window.getComputedStyle(el)")

    results = []
    for prop in properties:
        actual_value = computed_styles.get(prop, "")

        # Determine expected value
        if isinstance(expected, dict):
            exp_value = expected.get(prop, "")
        else:
            exp_value = expected if len(properties) == 1 else ""

        # Verification logic
        passed = False
        if operator == "equals":
            passed = actual_value == exp_value
        elif operator == "contains":
            passed = exp_value in actual_value
        elif operator == "gt":
            passed = float(actual_value) > float(exp_value)
        elif operator == "lt":
            passed = float(actual_value) < float(exp_value)
        elif operator == "gte":
            passed = float(actual_value) >= float(exp_value)
        elif operator == "lte":
            passed = float(actual_value) <= float(exp_value)
        else:
            raise ValueError(f"Unsupported operator: {operator}")

        status = "✓" if passed else "✗"
        result_msg = f"{status} {prop}: {actual_value}"
        if exp_value:
            result_msg += f" (expected: {exp_value}, operator: {operator})"
        results.append(result_msg)

        if not passed:
            logger.error(result_msg)
        else:
            logger.info(result_msg)

    # Summarize results
    if any("✗" in r for r in results):
        raise AssertionError(f"Style verification failed:\n" + "\n".join(results))
    else:
        logger.info("All style verifications passed")


def verify_child_element_count(page: Page, v: dict):
    """
    Verify the number of child elements within a parent element

    Supported parameters:
    - parent_locator: Parent element locator (required)
    - child_locator: Child element selector to count (required)
    - expected: Expected count of child elements (required)
    - operator: Comparison operator, default 'equals', supports: equals, gt, lt, gte, lte, ne
    - container: Parent container name/text to search within (optional)
    - timeout: Timeout in milliseconds, default 5000

    Usage examples:

    1. Verify exact count:
       verify_child_element_count:
           parent_locator: ".my-module"
           child_locator: ".item"
           expected: 5

    2. Verify within a container:
       verify_child_element_count:
           container: "My Module"
           parent_locator: ".content"
           child_locator: "button"
           expected: 3

    3. Verify minimum count:
       verify_child_element_count:
           parent_locator: "[data-testid='module']"
           child_locator: ".product-card"
           expected: 2
           operator: "gte"  # Greater than or equal

    4. Verify maximum count:
       verify_child_element_count:
           parent_locator: ".gallery"
           child_locator: "img"
           expected: 10
           operator: "lte"  # Less than or equal
    """
    parent_locator_str = v.get("parent_locator")
    child_locator_str = v.get("child_locator")
    expected_count = v.get("expected")
    container_name = v.get("container")

    if not parent_locator_str:
        raise ValueError("verify_child_element_count: 'parent_locator' parameter is required")
    if not child_locator_str:
        raise ValueError("verify_child_element_count: 'child_locator' parameter is required")
    if expected_count is None:
        raise ValueError("verify_child_element_count: 'expected' parameter is required")

    timeout = v.get("timeout", 5000)
    operator = v.get("operator", "equals")

    # Apply container filter if specified
    if container_name:
        logger.info(f"Searching within container: {container_name}")
        # Find parent container by text
        container_elem = page.locator("div").filter(has=page.get_by_text(container_name, exact=True)).last
        parent_locator = container_elem.locator(f"xpath={parent_locator_str}")

        container_info = f" (in container: {container_name})"
    else:
        parent_locator = page.locator(parent_locator_str)
        container_info = ""

    # Wait for parent element to be visible
    parent_locator.wait_for(state="visible", timeout=timeout)

    # Count child elements
    child_locator = parent_locator.locator(child_locator_str)
    actual_count = child_locator.count()

    logger.info(f"Counting child elements - Parent: {parent_locator_str}{container_info}, Child: {child_locator_str}")
    logger.info(f"Actual count: {actual_count}, Expected: {expected_count}, Operator: {operator}")

    # Perform comparison
    passed = False
    if operator == "equals":
        passed = actual_count == expected_count
    elif operator == "gt":
        passed = actual_count > expected_count
    elif operator == "lt":
        passed = actual_count < expected_count
    elif operator == "gte":
        passed = actual_count >= expected_count
    elif operator == "lte":
        passed = actual_count <= expected_count
    elif operator == "ne":
        passed = actual_count != expected_count
    else:
        raise ValueError(f"Unsupported operator: {operator}")

    status = "✓" if passed else "✗"
    result_msg = f"{status} Child element count: {actual_count} (expected: {expected_count}, operator: {operator})"

    if not passed:
        logger.error(result_msg)
        raise AssertionError(f"Child element count verification failed:\n{result_msg}")
    else:
        logger.info(result_msg)
        logger.info("Child element count verification passed")


