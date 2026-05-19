
import sys, json, os
from playwright.sync_api import sync_playwright

RESOLVED_URLS = {"{BASE_URL}/events": "https://release.pear.us/events", "{BASE_URL}/autotestshop": "https://release.pear.us/autotestshop", "{BASE_URL}/catalog": "https://release.pear.us/catalog", "{BASE_URL}/dashboard": "https://release.pear.us/dashboard", "{BASE_URL}/post/create": "https://release.pear.us/post/create", "{BASE_URL}/events/create": "https://release.pear.us/events/create", "{BASE_URL}/events/settings": "https://release.pear.us/events/settings", "{BASE_URL}/collabs": "https://release.pear.us/collabs", "{BASE_URL}/shop": "https://release.pear.us/shop"}
COOKIE_PATH = 'D:\\monster_test\\Autotest-monster\\tools\\..\\test_case\\UI\\Test_Katana\\cookie_release.json'

JS_EXTRACT = '\n() => {\n    const SELECTORS = [\n        \'button\',\n        \'a\',\n        \'[role="menuitem"]\',\n        \'[role="tab"]\',\n        \'input\',\n        \'select\',\n        \'[role="combobox"]\',\n        \'[data-testid]\',\n    ];\n    const results = [];\n    // Check if element is visible (not hidden by display/visibility/opacity)\n    const isVisible = (el) => {\n        if (!el.offsetParent && el.tagName !== \'BODY\') return false;\n        const style = getComputedStyle(el);\n        if (style.display === \'none\') return false;\n        if (style.visibility === \'hidden\') return false;\n        if (parseFloat(style.opacity) === 0) return false;\n        return true;\n    };\n    SELECTORS.forEach(sel => {\n        document.querySelectorAll(sel).forEach(el => {\n            if (!isVisible(el)) return;\n            const entry = {\n                tag:        el.tagName ? el.tagName.toLowerCase() : \'\',\n                role:       el.getAttribute(\'role\') || \'\',\n                ariaLabel:  el.getAttribute(\'aria-label\') || \'\',\n                name:       (el.getAttribute(\'aria-label\') || el.innerText || \'\').trim().substring(0, 80),\n                testid:     el.getAttribute(\'data-testid\') || \'\',\n                type:       el.getAttribute(\'type\') || \'\',\n                placeholder: el.getAttribute(\'placeholder\') || \'\',\n                text:       (el.innerText || \'\').trim().substring(0, 80),\n            };\n            // Stable key for diffing\n            const key = entry.testid || entry.role + \'|\' + (entry.name || entry.text || \'\');\n            if (key) results.push({ key: key, ...entry });\n        });\n    });\n    return results;\n}\n'

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context_options = {}
    if COOKIE_PATH and os.path.exists(COOKIE_PATH):
        context_options["storage_state"] = COOKIE_PATH
    context = browser.new_context(**context_options)
    page = context.new_page()
    page.set_default_timeout(30000)

    for url_tpl, url in RESOLVED_URLS.items():
        print(f"Visiting: {url}", file=sys.stderr, flush=True)
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_selector("body", timeout=10000)
            elements = page.evaluate(JS_EXTRACT)
            results[url_tpl] = elements
            print(f"  Got {len(elements)} elements", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"  ERROR: {str(e)[:200]}", file=sys.stderr, flush=True)
            results[url_tpl] = []

    browser.close()

print(json.dumps(results, ensure_ascii=False), file=sys.stdout, flush=True)
