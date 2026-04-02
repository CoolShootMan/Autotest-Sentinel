from playwright.sync_api import sync_playwright

def hunt_forms():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            storage_state='test_case/UI/Test_Katana/cookie_release.json',
            viewport={'width': 430, 'height': 932},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        page.goto('https://release.pear.us/demi-release')
        page.wait_for_timeout(5000)
        
        # 1. Look for text "Forms"
        forms_elements = page.get_by_text("Forms", exact=True).all()
        print(f"Elements with exact text 'Forms': {len(forms_elements)}")
        for i, el in enumerate(forms_elements):
            tag = el.evaluate("e => e.tagName")
            print(f"  Element {i}: <{tag}> - class: {el.get_attribute('class')}")
            # Try to find the button nearby
            parent = el.locator('xpath=..')
            btns = parent.locator('button').all()
            if len(btns) > 0:
                print(f"    Buttons in parent of this 'Forms' element: {len(btns)}")
                for btn in btns:
                    print(f"      Button text: '{btn.inner_text()}'")
            
            # Try grandparent
            grandparent = el.locator('xpath=../..')
            gbtns = grandparent.locator('button').all()
            if len(gbtns) > 0:
                print(f"    Buttons in grandparent: {len(gbtns)}")
                for btn in gbtns:
                    print(f"      Button text: '{btn.inner_text()}'")
        
        browser.close()

if __name__ == "__main__":
    hunt_forms()
