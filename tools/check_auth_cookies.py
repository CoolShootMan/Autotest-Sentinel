"""预检：3 个 UI 测试账号的 cookie 是否仍是「已登录」状态。

背景（2026-09-20 run 35487920412，20 条 UI 用例 19 条假失败）：
    API 预制脚本会**删除并重建**测试账号（yuxiao.zhu.ext+999/998/997）。
    若在 CI 正在跑 UI 的同时，本机又跑了一次预制（或 cookie 过期），
    账号被重建 / 会话失效 → CI 手里的 cookie 立刻变成访客态，
    整套 UI 用例会以大量 `element not found` 假失败收场：
    该 run 实测 20 条里 19 条假失败、白烧 16 分钟 runner，
    而真正的信号（登录态没了）只在日志里以一行 DEBUG 出现。

    所以在跑 pytest 之前做一次**廉价**预检：每个账号的 cookie 文件必须存在、
    可解析，且带当前环境的 auth token（access token，而不只是 refresh）。
    不通过就中止，避免产出一轮误导性的「测试失败」。

Usage:
    python tools/check_auth_cookies.py
    # 退出码 0 = 3 个账号都是登录态；1 = 有账号不是（stdout 会列出原因）
"""
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COOKIE_DIR = PROJECT_ROOT / "test_case" / "UI" 

# 与 tools/get_all_cookies.py 保持一致的域名 → 环境映射（cookie 文件名与 cookie 前缀都按它生成）
_ENV_MAP = {
    "https://staging.pear.us": "staging",
    "https://release.pear.us": "release",
    "https://pear.us": "prod",
}
BASE_URL = os.environ.get("BASE_URL", "https://release.pear.us")
ENV_NAME = _ENV_MAP.get(BASE_URL, "release")

AUTH_COOKIE = f"{ENV_NAME}_katana_web_auth_token"
REFRESH_COOKIE = f"{ENV_NAME}_katana_web_auth_token_refresh"

ACCOUNTS = [
    ("main (+999)", f"cookie_{ENV_NAME}.json"),
    ("co-seller (+998)", f"cookie_{ENV_NAME}_co_seller.json"),
    ("partner co-seller (+997)", f"cookie_{ENV_NAME}_partner_coseller.json"),
]


def check_one(filename: str) -> tuple[bool, str]:
    """检查单个 cookie 文件，返回 (是否登录态, 说明)。"""
    path = COOKIE_DIR / filename
    if not path.exists():
        return False, f"文件不存在：{path}"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return False, f"无法解析 JSON：{exc}"

    cookies = {
        c.get("name") or "": c for c in state.get("cookies", []) if isinstance(c, dict)
    }
    if AUTH_COOKIE not in cookies:
        if REFRESH_COOKIE in cookies:
            hint = f"只有 {REFRESH_COOKIE}（缺 access token → 会话已被服务端判失效）"
        else:
            hint = "访客态（连 refresh token 都没有）"
        return False, f"缺少 {AUTH_COOKIE} —— {hint}；现有 cookie：{sorted(cookies)}"
    if not str(cookies[AUTH_COOKIE].get("value") or "").strip():
        return False, f"{AUTH_COOKIE} 值为空"
    return True, f"{filename} 含 {AUTH_COOKIE}（共 {len(cookies)} 个 cookie）"


def main() -> int:
    print(f"=== Auth cookie preflight (env={ENV_NAME}, BASE_URL={BASE_URL}) ===")
    bad: list[str] = []
    for label, filename in ACCOUNTS:
        ok, msg = check_one(filename)
        print(f"  [{'OK ' if ok else 'BAD'}] {label}: {msg}")
        if not ok:
            bad.append(label)

    if bad:
        print("")
        print(f"!!! 登录态预检失败：{bad}")
        print("    这些账号不是登录态 → UI 用例必然大面积 element not found 假失败。")
        print("    常见原因：")
        print("      1) 跑 CI 的同时本机又跑了一次 API 预制脚本 —— 它会删除并重建这些账号；")
        print("      2) cookie 已过期（access token 当天过期）。")
        print("    处理：重跑 tools/get_all_cookies.py，并确认预制脚本不与 CI 并发。")
        return 1

    print("")
    print("=== 3 个账号 cookie 均为登录态 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
