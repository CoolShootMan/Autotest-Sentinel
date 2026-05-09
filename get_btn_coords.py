import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

def get_forms_button_coords():
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
        page.goto(os.environ.get("BASE_URL", "https://release.pear.us") + '/demi-release')
        page.wait_for_timeout(5000)
        
        # Methodology: Find "Forms" text, go to grandparent, find "Add new" button
        try:
            forms_text = page.get_by_text("Forms", exact=True).first
            btn = forms_text.locator('xpath=../..').get_by_role("button", name="Add new").first
            if btn.is_visible():
                box = btn.bounding_box()
                print(f"FORMS_BUTTON_COORDS: x={box['x'] + box['width']/2}, y={box['y'] + box['height']/2}")
                print(f"FORMS_BUTTON_BOX: {box}")
            else:
                print("Button found but not visible")
                
            # Full screen screenshot for manual check
            page.screenshot(path='debug_forms_button.png')
        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()

if __name__ == "__main__":
    get_forms_button_coords()
