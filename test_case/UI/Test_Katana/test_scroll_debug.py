"""
Debug script to test scrolling to Posts tab on autotestshop page.
"""
from playwright.sync_api import sync_playwright
import time

def test_scroll_to_posts_tab():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}") if "error" in msg.text.lower() else None)
        
        # Open autotestshop page (guest view)
        print("Opening autotestshop page...")
        page.goto("https://release.pear.us/autotestshop")
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        # Take initial screenshot
        page.screenshot(path="debug_scroll_01_initial.png")
        print("Screenshot saved: debug_scroll_01_initial.png")
        
        # Log initial scroll position
        scroll_info = page.evaluate("""
            () => {
                const info = {
                    windowScrollY: window.scrollY,
                    documentHeight: document.body.scrollHeight,
                    windowHeight: window.innerHeight,
                    scrollable: document.body.scrollHeight - window.innerHeight
                };
                
                // Find scrollable containers
                const containers = [];
                document.querySelectorAll('div, section, article, main').forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
                        containers.push({
                            class: el.className.split(' ')[0],
                            scrollHeight: el.scrollHeight,
                            clientHeight: el.clientHeight,
                            scrollTop: el.scrollTop
                        });
                    }
                });
                info.containers = containers;
                
                return info;
            }
        """)
        print(f"Initial state: {scroll_info}")
        
        # Try page_scroll with enhanced logic
        print("\n=== Testing page_scroll ===")
        
        for i in range(5):
            print(f"\n--- Scroll attempt {i+1}/5 ---")
            
            result = page.evaluate("""
                () => {
                    const centerX = window.innerWidth / 2;
                    const centerY = window.innerHeight / 2;
                    const results = [];
                    
                    // Check window scroll
                    results.push(`window: scrollY=${window.scrollY}, max=${document.body.scrollHeight - window.innerHeight}`);
                    
                    // Try JS scroll on largest scrollable container
                    const allScrollable = [];
                    document.querySelectorAll('div, section, article, main, ul').forEach(el => {
                        const style = window.getComputedStyle(el);
                        if ((style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                            el.scrollHeight > el.clientHeight + 5) {
                            const rect = el.getBoundingClientRect();
                            if (rect.height > 0 && rect.top < window.innerHeight) {
                                allScrollable.push({
                                    el,
                                    scrollable: el.scrollHeight - el.clientHeight,
                                    className: el.className.split(' ')[0],
                                    rect
                                });
                            }
                        }
                    });
                    
                    if (allScrollable.length > 0) {
                        allScrollable.sort((a, b) => b.scrollable - a.scrollable);
                        const top = allScrollable[0];
                        top.el.scrollBy({ top: window.innerHeight * 0.8, behavior: 'instant' });
                        results.push(`JS_scroll(${top.className}): +${window.innerHeight * 0.8}px, now scrollTop=${top.el.scrollTop}`);
                    } else {
                        // Try element under cursor
                        let elem = document.elementFromPoint(centerX, centerY);
                        let found = false;
                        while (elem && elem !== document.body) {
                            if (elem.scrollHeight > elem.clientHeight) {
                                elem.scrollBy({ top: 500, behavior: 'instant' });
                                results.push(`elem_scroll(${elem.className.split(' ')[0]}): scrollTop=${elem.scrollTop}`);
                                found = true;
                                break;
                            }
                            elem = elem.parentElement;
                        }
                        if (!found) {
                            results.push('no_scrollable_found');
                        }
                    }
                    
                    return results;
                }
            """)
            print(f"  {result}")
            
            # Try mouse.wheel()
            page.mouse.move(640, 360)
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(300)
            print(f"  mouse.wheel(0, 500) executed")
            
            # Try keyboard
            page.keyboard.press("PageDown")
            page.wait_for_timeout(300)
            print(f"  keyboard PageDown executed")
            
            # Check if Posts tab is visible
            posts_tab = page.locator('[role="tab"][name="Posts"]')
            try:
                if posts_tab.is_visible(timeout=1000):
                    print(f"\n*** Posts tab is now VISIBLE! ***")
                    posts_tab.screenshot(path="debug_scroll_02_posts_visible.png")
                    break
                else:
                    print(f"  Posts tab still not visible")
            except:
                print(f"  Posts tab not found")
            
            # Final scroll position
            final = page.evaluate("() => `window.scrollY=${window.scrollY}, docHeight=${document.body.scrollHeight}`")
            print(f"  Final position: {final}")
            
            time.sleep(1)
        
        # Take final screenshot
        page.screenshot(path="debug_scroll_03_final.png")
        print("\nFinal screenshot saved: debug_scroll_03_final.png")
        
        browser.close()
        print("\nTest complete.")

if __name__ == "__main__":
    test_scroll_to_posts_tab()
