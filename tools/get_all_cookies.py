"""
Fetch cookies for three accounts in sequence, logging in one by one and saving to individual JSON files.
Usage: python tools/get_all_cookies.py

Cookie filenames are generated dynamically based on the current environment (e.g. cookie_release.json),
ensuring different environments never overwrite each other's cookie files.

Robustness notes:
- Each account is isolated: one failure does NOT abort the remaining accounts.
- The sign-in API response is logged. The login page shows NO error text when
  credentials are rejected, so without this a bad password looks like a UI
  problem ("still on login page"). On a 4xx from /auth/sign-in we fail fast
  instead of retrying, to avoid tripping account lockout.
- browser/context/page are always closed via try/finally, so a timeout on one
  account cannot leak a browser process that interferes with the next account.
- page.goto uses wait_until="domcontentloaded" + retry, because the login page's
  default "load" wait can hang on slow 3rd-party resources, and the release env
  may rate-limit rapid sequential logins from the same IP (causing goto to time out).
"""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(Path(__file__).parent.parent / ".env")

PROJECT_ROOT = Path(__file__).parent.parent
COOKIE_DIR = PROJECT_ROOT / "test_case" / "UI" 

# Read from BASE_URL environment variable, default to release environment
ENV_BASE = os.environ.get("BASE_URL", "https://release.pear.us")

# Reverse-map domain to environment name for cookie file naming
_ENV_MAP = {
    "https://staging.pear.us": "staging",
    "https://release.pear.us": "release",
    "https://pear.us": "prod",
}
CURRENT_ENV = _ENV_MAP.get(ENV_BASE, "release")

ACCOUNTS = [
    {
        "name": "main (+999)",
        "email": "linda.zhou.ext+999@1m.app",
        "password": "Happy123",
        "cookie_file": f"cookie_{CURRENT_ENV}.json",
    },
    {
        "name": "co-seller (+998)",
        "email": "linda.zhou.ext+998@1m.app",
        "password": "Happy123",
        "cookie_file": f"cookie_{CURRENT_ENV}_co_seller.json",
    },
    {
        "name": "partner co-seller (+997)",
        "email": "linda.zhou.ext+997@1m.app",
        "password": "Happy123",
        "cookie_file": f"cookie_{CURRENT_ENV}_partner_coseller.json",
    },
    {
        "name": "admin (linda.zhou)",
        "email": "linda.zhou.ext@1m.app",
        "password": "lindazhou",
        "cookie_file": "cookie_admin.json",
        "base_url": "https://release.admin.pear.us",
    },
    {
        "name": "linda (+01)",
        "email": "linda.zhou.ext+01@1m.app",
        "password": "Happy123",
        "cookie_file": "cookie_release_linda01.json",
    },
]

# Front-end texts the SPA shows when POST /auth/sign-in never gets an answer. They carry
# no HTTP status, so they must be detected from the DOM (see _page_shows_request_timeout).
_TIMEOUT_MARKERS = ("Request timed out", "Network Error", "Failed to fetch")

SUBMIT_RETRIES = 3
GOTO_RETRIES = 3
GOTO_TIMEOUT = 20000
BETWEEN_ACCOUNTS_DELAY = 3  # seconds; avoid hammering the login endpoint (rate-limit mitigation)

# Profile name used to finish the "What's your name?" step when a test account has just
# been re-created (see _complete_name_onboarding). No YAML asserts the owner's profile
# name, so any non-empty value works; we use the account owner's real name so the UI reads
# naturally if a human opens the account.
PROFILE_FIRST_NAME = "Yuxiao"
PROFILE_LAST_NAME = "Zhu"


def _complete_name_onboarding(page) -> bool:
    """Finish the "What's your name?" profile step that follows a fresh sign-in.

    WHY (2026-10-16): the API prefill suite DELETES and RECREATES the UI test accounts
    (yuxiao.zhu.ext+999/998/997). A re-created account has no profile name yet, so a
    successful sign-in (HTTP 201 from /auth/sign-in) is followed by an in-app onboarding
    screen (inputs `firstName` / `lastName` + a "Start Exploring" button) that keeps the
    SPA URL on `/login`. The old success check `"/login" not in url` could therefore never
    pass: the tool timed out, retried, found no "Log in" button any more and reported
    "'Log in' button not found" for all three accounts, leaving stale cookies behind and
    making the whole UI suite fail with `element not found`.

    Returns True when the onboarding step was detected and submitted (the caller can then
    wait for the SPA to leave /login), False when there was nothing to complete.
    """
    try:
        first = page.locator("input[name='firstName']").first
        first.wait_for(state="visible", timeout=8000)
    except Exception:
        return False

    print(f"  onboarding detected: \"What's your name?\" step found -> completing it")
    try:
        if not first.input_value().strip():
            first.fill(PROFILE_FIRST_NAME, timeout=10000)
        last = page.locator("input[name='lastName']").first
        if last.count() and not last.input_value().strip():
            last.fill(PROFILE_LAST_NAME, timeout=10000)
        page.keyboard.press("Tab")
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Start Exploring").first.click(timeout=15000)
    except Exception as e:
        page.screenshot(path="login_error_onboarding.png")
        raise RuntimeError(
            "found the profile-name onboarding step but could not complete it "
            f"(firstName/lastName + 'Start Exploring'): {e}"
        )
    try:
        page.locator("input[name='firstName']").first.wait_for(state="hidden", timeout=20000)
    except Exception:
        pass
    print("  onboarding completed")
    return True


def _page_shows_request_timeout(page) -> bool:
    """True when the SPA rendered its own network-failure text.

    WHY (2026-10-21): the co-seller refresh failed three times in a row with
    "submit attempt X/3 stayed on /login" and NO sign-in response at all. The page was
    actually showing `Request timed out: POST https://release.katana-api.1m.app/auth/sign-in`
    and the request had ended as net::ERR_ABORTED, so the status-code based logic above
    never saw a 4xx and the failure looked like a credential problem. This is the rarer
    sibling of the missing-hydration case below: here the request IS issued but never
    answered. Start the next attempt from a clean page instead of re-clicking a form
    that is stuck in its error state.
    """
    try:
        text = page.evaluate("() => (document.body ? document.body.innerText : '')") or ""
    except Exception:
        return False
    return any(m.lower() in text.lower() for m in _TIMEOUT_MARKERS)


def _fill_credentials(page, account: dict) -> list:
    """Fill email + password, blur to trigger validation, and echo the field values."""
    page.locator("input[name='email']").first.fill(account["email"], timeout=15000)
    page.locator("input[type='password']").first.fill(account["password"], timeout=15000)
    # The form validates on blur (react-hook-form mode:'onBlur'). Without a blur the
    # submit handler sees a stale isValid=false and the click is a silent no-op
    # (zero network requests). Tab off the password field first.
    page.keyboard.press("Tab")
    page.wait_for_timeout(800)
    values = page.evaluate(
        "() => Array.from(document.querySelectorAll('input'))"
        ".map(i => i.name + '=' + (i.type === 'password' ? '***' : i.value))"
    )
    print(f"  [{account['name']}] field values before submit: {values}")
    return values


def _is_hydrated(page) -> bool:
    """True when React has attached to the login form (the SPA is interactive)."""
    try:
        return bool(page.evaluate(
            """() => {
                const el = document.querySelector("input[name='email']") || document.querySelector('form');
                if (!el) return false;
                return Object.keys(el).some(
                    k => k.startsWith('__reactFiber') || k.startsWith('__reactProps'));
            }"""
        ))
    except Exception:
        return False


def _wait_until_hydrated(page, name: str, login_base: str, attempts: int = 5) -> bool:
    """Reload the login page until the SPA hydrates.

    A non-hydrated page swallows every click, so filling and submitting it can never
    work - reloading is the only way out.
    """
    for i in range(1, attempts + 1):
        if _is_hydrated(page):
            if i > 1:
                print(f"  [{name}] login page hydrated after {i - 1} reload(s)")
            return True
        print(f"  [{name}] login page not hydrated (React never attached) - "
              f"reloading ({i}/{attempts})")
        try:
            page.reload(wait_until="domcontentloaded", timeout=GOTO_TIMEOUT)
            page.wait_for_selector("input[name='email']", timeout=15000)
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"  [{name}] reload failed: {e}")
            try:
                page.goto(f"{login_base}/login", timeout=GOTO_TIMEOUT,
                          wait_until="domcontentloaded")
                page.wait_for_selector("input[name='email']", timeout=15000)
                page.wait_for_timeout(2000)
            except Exception as e2:
                print(f"  [{name}] goto fallback failed: {e2}")
    return _is_hydrated(page)


def _leaves_login(page, timeout_ms: int) -> bool:
    """Poll page.url until the SPA is off /login.

    WHY (2026-10-21): wait_for_url() only resolves on a real navigation. After a
    successful sign-in the SPA routes to /autotestshop client-side (history.pushState),
    so nothing navigates, wait_for_url timed out after 25s, and the retry loop then hit
    "'Log in' button not found" on a page where the login had in fact succeeded.
    """
    end = time.time() + timeout_ms / 1000.0
    while time.time() < end:
        if "/login" not in page.url:
            return True
        page.wait_for_timeout(500)
    return "/login" not in page.url


def _safe_close(obj, label):
    try:
        if obj is not None:
            obj.close()
    except Exception as e:
        print(f"  (warn) failed to close {label}: {e}")


def login_and_save(playwright, account: dict):
    name = account["name"]
    print(f"\n[{name}] Starting login...")
    browser = None
    context = None
    page = None
    try:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Capture the sign-in API response: the login page renders NO error text
        # when credentials are rejected (verified 2026-09-17: HTTP 403
        # {"code":403,"message":"Invalid account or password"} while the form
        # just sits there), which made failures look like a selector/UI problem.
        auth_errors = []

        def _on_response(resp):
            if "/auth/sign-in" not in resp.url or resp.status < 400:
                return
            body = ""
            try:
                body = resp.text()[:200].replace("\n", " ")
            except Exception:
                pass
            auth_errors.append((resp.status, body))
            print(f"  [{name}] sign-in API -> {resp.status} {body}")

        page.on("response", _on_response)

        # Retry navigation: default goto waits for "load", which hangs if any
        # 3rd-party resource stalls; the release env may also rate-limit rapid
        # sequential logins. Use domcontentloaded + retries to absorb both.
        login_base = account.get("base_url", ENV_BASE)
        last_err = None
        for attempt in range(1, GOTO_RETRIES + 1):
            try:
                page.goto(f"{login_base}/login", timeout=GOTO_TIMEOUT, wait_until="domcontentloaded")
                page.wait_for_selector(
                    "input[type='email'], input[name='email'], input[placeholder*='email' i]",
                    timeout=10000,
                )
                break
            except Exception as e:
                last_err = e
                print(f"  [{name}] goto attempt {attempt}/{GOTO_RETRIES} failed: {e}")
                page.wait_for_timeout(2000)
        else:
            page.screenshot(path=f"login_error_{name}.png")
            raise RuntimeError(
                f"[{name}] failed to load login page after {GOTO_RETRIES} attempts: {last_err}"
            )

        page.wait_for_timeout(2000)

        # The release SPA intermittently serves the SSR markup without hydrating: the
        # form renders and every button looks enabled, but clicks do nothing at all
        # (zero network requests, no console error) - verified 2026-10-21 by clicking
        # the "Use Phone" tab on a dead page, which did not react either. Submitting
        # such a page can only fail, so reload until React is attached.
        if not _wait_until_hydrated(page, name, login_base):
            page.screenshot(path=f"login_error_{name}.png")
            raise RuntimeError(
                f"[{name}] the login page never hydrated after 5 reloads - the SPA served"
                f" static HTML only, so no click could be registered. This is a"
                f" release-frontend problem, not a credential one; retry the refresh later."
            )

        # NOTE (2026-08-31): the email input on the release login page is
        # <input type="text" name="email" placeholder="Email"> -- it is NOT
        # type="email", so any selector relying on input[type='email'] silently
        # matches nothing and the form never validates. Always target by name.
        values = _fill_credentials(page, account)

        # Retry the submit: the first click occasionally lands before React has
        # committed the validated state, so re-blur and click again.
        last_url = page.url
        for attempt in range(1, SUBMIT_RETRIES + 1):
            clicked = page.evaluate(
                """() => {
                const b = Array.from(document.querySelectorAll('button')).find(
                    x => (x.innerText||'').trim() === 'Log in');
                if (!b) return false;
                b.setAttribute('data-login-submit','1');
                return true;
            }"""
            )
            if not clicked:
                if "/login" not in page.url:
                    # The sign-in already went through and the SPA moved on; no
                    # button is left to click, which is success rather than failure.
                    print(f"  [{name}] already off {page.url} - treating as signed in")
                    break
                raise RuntimeError(f"[{name}] 'Log in' button not found on {page.url}")
            # Separate "the click did nothing" from "the server said no".
            # On 2026-10-21 repeated attempts clicked an enabled button on a filled form
            # and produced ZERO network requests (the page had lost interactivity again),
            # while waiting 25s for a URL that could never change. Detect it in seconds.
            fired = True
            try:
                with page.expect_request(
                    lambda req: "/auth/sign-in" in req.url, timeout=15000
                ):
                    page.locator("[data-login-submit='1']").click(timeout=10000)
            except Exception:
                fired = False
            if not fired:
                print(f"  [{name}] submit attempt {attempt}/{SUBMIT_RETRIES}: the click "
                      f"sent no /auth/sign-in request (form state not committed) - "
                      f"re-blurring and retrying")
                page.keyboard.press("Tab")
                page.wait_for_timeout(1200)
                continue
            page.wait_for_timeout(300)
            # A re-created account answers the sign-in with 201 and then shows the
            # in-app "What's your name?" step while the URL stays on /login, so the
            # poll below would never succeed. Handle it before waiting on the URL.
            onboarded = _complete_name_onboarding(page)
            try:
                if onboarded:
                    # Either the SPA moved off /login or it stayed there with the
                    # onboarding layer gone - in both cases the sign-in cookies are set.
                    if not _leaves_login(page, 8000):
                        page.locator("input[name='firstName']").first.wait_for(
                            state="hidden", timeout=8000
                        )
                elif not _leaves_login(page, 25000):
                    raise TimeoutError(f"URL stayed on {page.url} for 25s")
                break
            except Exception:
                server_msg = f" | server said: {auth_errors[-1][1]}" if auth_errors else ""
                print(f"  [{name}] submit attempt {attempt}/{SUBMIT_RETRIES} "
                      f"stayed on {page.url}{server_msg}")
                timed_out = _page_shows_request_timeout(page)
                if timed_out:
                    print(f"  [{name}] the SPA reported a network failure for "
                          f"POST /auth/sign-in (no HTTP status) - the API was slow")
                # A 4xx from sign-in means the credentials themselves were
                # rejected - retrying cannot succeed and risks locking the
                # account, so fail fast with the real reason.
                if auth_errors and auth_errors[-1][0] in (400, 401, 403, 422):
                    page.screenshot(path=f"login_error_{name}.png")
                    raise RuntimeError(
                        f"[{name}] login rejected by server: "
                        f"HTTP {auth_errors[-1][0]} {auth_errors[-1][1]} "
                        f"(check the password for {account['email']}). "
                        f"NOTE: if only the co-seller (+998) fails while the others "
                        f"log in fine, its password was most likely rewritten by the "
                        f"API suite '00_UI Prefill' (it sets that account's password "
                        f"from the import response) - re-provision/reset the account "
                        f"instead of hunting for a UI/selector bug."
                    )
                if attempt == SUBMIT_RETRIES:
                    page.screenshot(path=f"login_error_{name}.png")
                    hint = (
                        " - the SPA reported `Request timed out` for POST /auth/sign-in, "
                        "which means the API never answered (slow, not a bad password); "
                        "retry the refresh later"
                    ) if timed_out else ""
                    raise RuntimeError(
                        f"[{name}] still on login page after {SUBMIT_RETRIES} "
                        f"submit attempts (fields: {values}){server_msg}{hint}"
                    )
                # After a request timeout the form keeps the error text and the button
                # can stay in its submitting state, so re-clicking it does nothing.
                # Reload, refill and submit from a clean page instead.
                if timed_out:
                    print(f"  [{name}] reloading the login page before the next attempt")
                    try:
                        page.goto(f"{login_base}/login", timeout=GOTO_TIMEOUT,
                                  wait_until="domcontentloaded")
                        page.wait_for_selector("input[name='email']", timeout=15000)
                        page.wait_for_timeout(1500)
                        values = _fill_credentials(page, account)
                    except Exception as reload_err:
                        print(f"  [{name}] reload + refill failed: {reload_err}")
                    continue
                # re-blur to re-trigger validation, then try again
                page.keyboard.press("Tab")
                page.wait_for_timeout(1500)
        else:
            # Every attempt took the "click sent nothing" branch above - never fall
            # through to saving a cookie file that is still a guest session.
            page.screenshot(path=f"login_error_{name}.png")
            raise RuntimeError(
                f"[{name}] the 'Log in' click never issued a /auth/sign-in request in "
                f"{SUBMIT_RETRIES} attempts (fields: {values}) - every click was swallowed, "
                f"so the SPA lost interactivity mid-flow (hydration) or its markup changed"
            )

        cookie_path = COOKIE_DIR / account["cookie_file"]
        context.storage_state(path=str(cookie_path))
        print(f"[{name}] Cookie saved -> {cookie_path}")
    finally:
        # Always clean up, regardless of success/failure, so a failed account
        # cannot leak a browser that interferes with the next account.
        _safe_close(page, "page")
        _safe_close(context, "context")
        _safe_close(browser, "browser")


def main():
    print("=== Starting bulk cookie collection ===")
    results = []
    with sync_playwright() as pw:
        for i, account in enumerate(ACCOUNTS):
            try:
                login_and_save(pw, account)
                results.append((account["name"], "OK"))
            except Exception as e:
                print(f"!!! [{account['name']}] FAILED: {e}")
                results.append((account["name"], f"FAILED: {e}"))
            # Delay between accounts to avoid hammering the login endpoint
            # (rate-limiting on the release env can cause subsequent gotos to hang).
            if i < len(ACCOUNTS) - 1:
                print(f"  (waiting {BETWEEN_ACCOUNTS_DELAY}s before next account...)")
                time.sleep(BETWEEN_ACCOUNTS_DELAY)

    print("\n=== Cookie collection summary ===")
    for name, status in results:
        print(f"  {name}: {status}")

    failed = [n for n, s in results if s != "OK"]
    if failed:
        print(f"\nWARNING: {len(failed)} account(s) failed: {failed}")
        sys.exit(1)
    print("\n=== All accounts completed ===")


if __name__ == "__main__":
    main()
