"""
duplicate_post.py — 复制 Post（独立脚本，不依赖浏览器上下文）

流程：
  1. 从 cookie_release.json 读取 cookie
  2. 使用硬编码的旧 JWT token 调用 GET /auth/refreshToken 换新 JWT
  3. 用新 JWT 调用 GET /posts/curator/duplicate/verify/{id}（验证）
  4. 用新 JWT 调用 GET /posts/curator/duplicate/{id}（执行，创建草稿）

输出：
  - 新草稿 post id 写入当前目录的 .duplicate_result.json
  - 供 base.py  duplicate_post action 读取
"""
import json
import os
import sys
import base64
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

# ========== 配置 ==========
# 硬编码绝对路径，避免动态路径计算错误
COOKIE_FILE = "d:/monster_test/Autotest-monster/test_case/UI/Test_Katana/cookie_release.json"
API_BASE = "https://release.katana-api.1m.app"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_FILE = os.path.join(SCRIPT_DIR, ".duplicate_result.json")

# 硬编码有效的旧JWT token（用于刷新获取新token）
HARDCODED_VALID_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI0OTkzMjFhNi1lNWRiLTQ1ZjItYjQ0MC1mZWI4NGQ1NWQ0ZjciLCJlbnYiOiJyZWxlYXNlIiwiaWF0IjoxNzc2NzQwNDA4LCJleHAiOjE4MDgyOTgwMDh9.6sZCDIfP33GIjZ8HQXNiAO_FX8srJckicKnTA1qn-as"

print(f"[DEBUG] COOKIE_FILE={COOKIE_FILE}", flush=True)
print(f"[DEBUG] EXISTS={os.path.exists(COOKIE_FILE)}", flush=True)


def load_cookies():
    """从 storage_state JSON 加载 cookie 字符串"""
    cookie_file = COOKIE_FILE
    with open(cookie_file, "r", encoding="utf-8") as f:
        state = json.load(f)

    cookie_str = "; ".join(
        f"{c['name']}={c['value']}"
        for c in state.get("cookies", [])
    )
    return cookie_str, state.get("cookies", [])


# extract_jwt_from_cookie 函数已不再需要，已删除


def refresh_token(cookie_str: str) -> str:
    """使用硬编码JWT换取新JWT"""
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
    """Step 1: 验证 duplicate"""
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
    """Step 2: 执行 duplicate（返回草稿 post id）"""
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
        or data.get("copyFromPostId")  # 有时直接返回原 post
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

    # 1. 加载 cookie
    cookie_str, cookies = load_cookies()
    print(f"[duplicate_post] Cookie loaded ({len(cookies)} entries)")
    print(f"[duplicate_post] Using hardcoded JWT (prefix={HARDCODED_VALID_JWT[:30]}...)")

    # 2. 检查 cookie 是否存在（仅作记录，不再强制要求）
    refresh_cookie_found = False
    for c in cookies:
        if c.get("name") == "release_katana_web_auth_token_refresh":
            refresh_cookie_found = True
            print(f"[duplicate_post] Found refresh cookie (len={len(c.get('value', ''))})")
            break
    
    if not refresh_cookie_found:
        print("[WARNING] release_katana_web_auth_token_refresh cookie not found, using hardcoded JWT instead")

    # 3. 刷新 token（使用硬编码JWT）
    new_jwt = refresh_token(cookie_str)
    print(f"[duplicate_post] New JWT refreshed (prefix={new_jwt[:30]}...)")

    # 4. Verify
    verify_data = duplicate_verify(new_jwt, post_id, cookie_str)
    print(f"[duplicate_post] Verify OK: {str(verify_data)[:100]}")

    # 5. Execute
    new_post_id = duplicate_execute(new_jwt, post_id, cookie_str)
    print(f"[duplicate_post] Done: {post_id} -> {new_post_id}")

    # 6. 写入结果文件，供 base.py 读取
    result = {"post_id": post_id, "new_post_id": new_post_id}
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(f"[duplicate_post] Result written to {RESULT_FILE}")
    return True


if __name__ == "__main__":
    # 支持两种调用方式：
    # 1. python duplicate_post.py '{"post_id": "xxx"}'
    # 2. python duplicate_post.py --post-id xxx
    args = {}
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("--"):
            # 命令行参数风格
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
