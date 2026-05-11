"""
duplicate_post.py — Duplicate a Post (standalone script, no browser context dependency)

Workflow:
  1. Load cookie from cookie_release.json
  2. Use hardcoded JWT token to call GET /auth/refreshToken to get a new JWT
  3. Use new JWT to call GET /posts/curator/duplicate/verify/{id} (verify)
  4. Use new JWT to call GET /posts/curator/duplicate/{id} (execute, creates a draft)

Output:
  - New draft post id written to .duplicate_result.json in current directory
  - Read by base.py duplicate_post action
"""
import json
import os
import sys
import base64
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

# ========== Configuration ==========
# Hardcoded absolute path to avoid dynamic path calculation errors
COOKIE_FILE = "d:/monster_test/Autotest-monster/test_case/UI/Test_Katana/cookie_release.json"
API_BASE = "https://release.katana-api.1m.app"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_FILE = os.path.join(SCRIPT_DIR, ".duplicate_result.json")

# Hardcoded valid old JWT token (used to refresh and get a new token)
HARDCODED_VALID_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI0OTkzMjFhNi1lNWRiLTQ1ZjItYjQ0MC1mZWI4NGQ1NWQ0ZjciLCJlbnYiOiJyZWxlYXNlIiwiaWF0IjoxNzc2NzQwNDA4LCJleHAiOjE4MDgyOTgwMDh9.6sZCDIfP33GIjZ8HQXNiAO_FX8srJckicKnTA1qn-as"

print(f"[DEBUG] COOKIE_FILE={COOKIE_FILE}", flush=True)
print(f"[DEBUG] EXISTS={os.path.exists(COOKIE_FILE)}", flush=True)


def load_cookies():
    """Load cookie string from Playwright storage-state JSON"""
    cookie_file = COOKIE_FILE
    with open(cookie_file, "r", encoding="utf-8") as f:
        state = json.load(f)

    cookie_str = "; ".join(
        f"{c['name']}={c['value']}"
        for c in state.get("cookies", [])
    )
    return cookie_str, state.get("cookies", [])


# extract_jwt_from_cookie function is no longer needed and has been removed


def refresh_token(cookie_str: str) -> str:
    """Use hardcoded JWT to obtain a new JWT"""
    headers = {
        "accept": "application/json",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
        "authorization": f"Bearer {HARDCODED_VALID_JWT}",
        "content-type": "application/json;charset=utf-8",
        "origin": os.environ.get("BASE_URL", "https://release.pear.us"),
        "referer": os.environ.get("BASE_URL", "https://release.pear.us") + "/",
        "cookie": cookie_str,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site"
    }
    url = f"{API_BASE}/auth/refreshToken?subdomainVanityUrl="
    resp = requests.get(url, headers=headers, timeout=15)

    if resp.status_code != 200:
        raise RuntimeError(f"refreshToken failed: HTTP {resp.status_code} — {resp.text[:200]}")

    data = resp.json()
    new_token = data.get("token") or data.get("data", {}).get("token") or data.get("data")
    if not new_token:
        raise RuntimeError(f"refreshToken response has no token: {data}")
    return new_token


def duplicate_verify(new_jwt: str, post_id: str, cookie_str: str) -> dict:
    """Step 1: Verify duplicate"""
    headers = {
        "authorization": f"Bearer {new_jwt}",
        "accept": "application/json",
        "cookie": cookie_str,
    }
    url = f"{API_BASE}/posts/curator/duplicate/verify/{post_id}"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code not in (200, 304):
        raise RuntimeError(f"duplicate verify failed: HTTP {resp.status_code} — {resp.text[:200]}")
    return resp.json()


def duplicate_execute(new_jwt: str, post_id: str, cookie_str: str) -> str:
    """Step 2: Execute duplicate (returns draft post id)"""
    headers = {
        "authorization": f"Bearer {new_jwt}",
        "accept": "application/json",
        "cookie": cookie_str,
    }
    url = f"{API_BASE}/posts/curator/duplicate/{post_id}"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code not in (200, 304):
        raise RuntimeError(f"duplicate execute failed: HTTP {resp.status_code} — {resp.text[:200]}")

    data = resp.json()
    new_post_id = (
        data.get("id")
        or (data.get("data") or {}).get("id")
        or data.get("copyFromPostId")  # sometimes the original post id is returned directly
    )
    return new_post_id


def run(params) -> bool:
    if isinstance(params, str):
        try:
            params = json.loads(params)
        except Exception:
            params = {}
    post_id = params.get("post_id")
    if not post_id:
        print("[ERROR] post_id is required")
        return False

    print(f"[duplicate_post] post_id={post_id}")

    # 1. Load cookie
    cookie_str, cookies = load_cookies()
    print(f"[duplicate_post] Cookie loaded ({len(cookies)} entries)")
    print(f"[duplicate_post] Using hardcoded JWT (prefix={HARDCODED_VALID_JWT[:30]}...)")

    # 2. Check if cookie exists (log only, not required)
    refresh_cookie_found = False
    for c in cookies:
        if c.get("name") == "release_katana_web_auth_token_refresh":
            refresh_cookie_found = True
            print(f"[duplicate_post] Found refresh cookie (len={len(c.get('value', ''))})")
            break
    
    if not refresh_cookie_found:
        print("[WARNING] release_katana_web_auth_token_refresh cookie not found, using hardcoded JWT instead")

    # 3. Refresh token (using hardcoded JWT)
    new_jwt = refresh_token(cookie_str)
    print(f"[duplicate_post] New JWT refreshed (prefix={new_jwt[:30]}...)")

    # 4. Verify
    verify_data = duplicate_verify(new_jwt, post_id, cookie_str)
    print(f"[duplicate_post] Verify OK: {str(verify_data)[:100]}")

    # 5. Execute
    new_post_id = duplicate_execute(new_jwt, post_id, cookie_str)
    print(f"[duplicate_post] Done: {post_id} -> {new_post_id}")

    # 6. Write result file for base.py to read
    result = {"post_id": post_id, "new_post_id": new_post_id}
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(f"[duplicate_post] Result written to {RESULT_FILE}")
    return True


if __name__ == "__main__":
    # Supports two calling styles:
    # 1. python duplicate_post.py '{"post_id": "xxx"}'
    # 2. python duplicate_post.py --post-id xxx
    args = {}
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("--"):
            # CLI argument style
            for i in range(1, len(sys.argv)):
                if sys.argv[i] == "--post-id" and i + 1 < len(sys.argv):
                    args["post_id"] = sys.argv[i + 1]
        else:
            try:
                args = json.loads(sys.argv[1])
            except Exception:
                pass

    success = run(args)
    sys.exit(0 if success else 1)
