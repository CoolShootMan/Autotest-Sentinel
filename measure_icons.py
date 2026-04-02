from playwright.sync_api import sync_playwright

def measure():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state='test_case/UI/Test_Katana/cookie_prod.json',
            viewport={'width': 430, 'height': 932},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        page.goto('https://pear.us/events/create')
        page.wait_for_timeout(7000)
        
        icons = page.locator('[data-testid="CalendarLineIcon"]').all()
        print(f"Found {len(icons)} icons")
        for i, icon in enumerate(icons):
            box = icon.bounding_box()
            if box:
                center_x = box["x"] + box["width"] / 2
                center_y = box["y"] + box["height"] / 2
                print(f"Icon {i}: center X={center_x}, center Y={center_y}")
        
        browser.close()

if __name__ == "__main__":
    measure()
