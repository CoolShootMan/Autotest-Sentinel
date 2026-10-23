#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Release Smoke Test Plan Builder (Katana) — 每日发版冒烟 test plan 自动生成。

用途（每天锁版后运行，约 18:00 锁版、19:00+ 执行）：
  1) 找当天三个仓库（katana-admin-server / katana-server / katana-web）的"发版 PR"
     —— 发版 PR = base=main、head 分支名含当天日期（release-YYYYMMDD* 或 versions/release-YYYYMMDD*）
  2) 从发版 PR 的 commits 提取功能 PR 编号（"Merge pull request #N" / "xxx (#N)"）与直接提交
  3) 由功能 PR 标题 + 改动文件路径判定影响的功能模块（映射到 ONES 用例模块）
  4) 拉取受影响模块下的 P0/P1 冒烟用例；若某影响点无 P0/P1 用例，则按 PR 描述创建用例
     （assign = 该模块的固定 owner，owner 由库内既有用例的 assign 字段统计得出，缓存于 data/ones_module_owner.json）
  5) 创建当天 test plan（命名如 "2026 Oct 23 Smoke testing on Prod env"，UI 创建）并关联用例
  6) 输出报告（data/daily_smoke_plan_report.json）

用法：
  .venv-smoke/bin/python tools/daily_release_smoke_plan.py            # 当天
  .venv-smoke/bin/python tools/daily_release_smoke_plan.py --date 2026-10-20
  .venv-smoke/bin/python tools/daily_release_smoke_plan.py --dry-run  # 只分析不写 ONES / 不建 plan

依赖：
  - backend/.env：ONES_*、JIRA_*（ONES token 失效时自动 playwright 刷新，会弹浏览器登录）
  - GitHub 凭证：osxkeychain（git credential fill），不落盘
  - ONES Katana 用例库 XcAFFViB；模块树缓存 data/ones_module_tree.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENV_PATH = ROOT / "backend" / ".env"
DATA = ROOT / "data"
GITHUB_API = "https://api.github.com"

REPOS = [
    ("katana-admin-server", "bosinc"),
    ("katana-server", "bosinc"),
    ("katana-web", "bosinc"),
]

# ---------------------------------------------------------------- env/token

def load_env() -> dict:
    env = {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def gh_token() -> str:
    """GitHub PAT from osxkeychain via git credential fill; never printed."""
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, timeout=10,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                tok = line[len("password="):].strip()
                if tok:
                    return tok
    except Exception:
        pass
    return ""


def ones_client() -> "tuple[dict, object]":
    """Return (env, ones_writer_module). Refresh token if expired (may pop browser)."""
    sys.path.insert(0, str(HERE))
    import ones_writer as ow
    env = ow.load_env()
    ow.ensure_token(env)
    return env, ow


# ---------------------------------------------------------------- GitHub

def gh_get(env: dict, token: str, path: str) -> dict | list:
    req = urllib.request.Request(
        f"{GITHUB_API}{path}",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:300]}
    except Exception as e:
        return {"_error": str(e)}


def find_release_prs(token: str, release_date: str) -> list:
    """Find release PRs whose branch was cut on release_date (lock date).
    Release PR = base=main, head branch contains YYYYMMDD (release-YYYYMMDD* /
    versions/release-YYYYMMDD*). The plan date is the *next* day (go-live)."""
    ymd = release_date.replace("-", "")
    found = []
    for repo, org in REPOS:
        pulls = gh_get(None, token, f"/repos/{org}/{repo}/pulls?state=all&base=main&sort=updated&direction=desc&per_page=100")
        if not isinstance(pulls, list):
            continue
        for pr in pulls:
            head_ref = (pr.get("head") or {}).get("ref", "")
            if ymd in head_ref and ("release" in head_ref.lower() or "version" in head_ref.lower()):
                found.append({
                    "repo": repo,
                    "number": pr["number"],
                    "title": pr.get("title", ""),
                    "head": head_ref,
                    "base": (pr.get("base") or {}).get("ref"),
                    "state": pr.get("state"),
                    "created_at": pr.get("created_at"),
                    "merged_at": pr.get("merged_at"),
                    "url": pr.get("html_url", ""),
                })
        # 兼容：标题带日期但分支名不同的情况
        if not any(f["repo"] == repo for f in found):
            for pr in pulls:
                title = pr.get("title", "")
                created = (pr.get("created_at") or "")[:10]
                if (("release" in title.lower() or "versions/release" in title.lower())
                        and (created == date_str or ymd in title)):
                    found.append({
                        "repo": repo, "number": pr["number"], "title": title,
                        "head": (pr.get("head") or {}).get("ref", ""),
                        "base": (pr.get("base") or {}).get("ref"),
                        "state": pr.get("state"), "created_at": pr.get("created_at"),
                        "merged_at": pr.get("merged_at"), "url": pr.get("html_url", ""),
                    })
    return found


PR_NO_RE = re.compile(r"(?:Merge pull request|\(|\s)#(\d{4,6})")


def extract_feature_prs(token: str, release_pr: dict) -> list:
    """From release PR commits, extract feature PR numbers + direct commits."""
    org, repo = "bosinc", release_pr["repo"]
    commits = gh_get(None, token, f"/repos/{org}/{repo}/pulls/{release_pr['number']}/commits?per_page=100")
    if not isinstance(commits, list):
        return []
    prs, direct = [], []
    for c in commits:
        msg = (c.get("commit") or {}).get("message", "")
        first = msg.splitlines()[0] if msg else ""
        m = re.search(r"Merge pull request #(\d+)", first)
        if m:
            prs.append(int(m.group(1)))
            continue
        m2 = re.search(r"\(#(\d{4,6})\)\s*$", first)
        if m2:
            prs.append(int(m2.group(1)))
            continue
        direct.append({"sha": c.get("sha", ""), "message": first[:150]})
    return {"feature_prs": sorted(set(prs)), "direct": direct}


def pr_details(token: str, repo: str, pr_no: int) -> dict:
    org = "bosinc"
    pr = gh_get(None, token, f"/repos/{org}/{repo}/pulls/{pr_no}")
    files = gh_get(None, token, f"/repos/{org}/{repo}/pulls/{pr_no}/files?per_page=100")
    return {
        "number": pr_no,
        "repo": repo,
        "title": pr.get("title", "") if isinstance(pr, dict) else "",
        "merged_at": pr.get("merged_at"),
        "files": [f.get("filename", "") for f in files] if isinstance(files, list) else [],
    }


# ---------------------------------------------------------------- module map

def load_module_tree() -> dict:
    p = DATA / "ones_module_tree.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def load_owner_map() -> dict:
    """module_uuid -> owner user uuid, cached from case assign statistics."""
    p = DATA / "ones_module_owner.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_owner_map(m: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "ones_module_owner.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")


# 代码路径/PR 主题关键词 -> ONES 用例模块 uuid（多个表示同时拉取）
MODULE_MAP: dict = {
    "post": ["JUeuK8qU", "Qsq7yTkW"],
    "resell": ["XtxRnanY", "5zo3pB9r", "8CQx7zsM", "JP6WXiLH"],
    "coupon": ["TWyYDusQ", "9tUABARi", "K7UEnAuS", "Qjp8icUa"],
    "promotion": ["4arknoUt", "K7UEnAuS", "DNVB79mD", "88awEmZG"],
    "campaign": ["4arknoUt", "V4VfZwTa"],
    "event": ["5oJPK6bR", "7AJybMCD", "Lc89ekUe", "7CNPhpaS", "Kv2DQ7kK", "5KVtYUZ4", "L7BkQ8uE"],
    "venue": ["L7BkQ8uE", "BKE8knxH"],
    "ticket": ["Lc89ekUe", "4ZYZBH3U", "YMEYj3kF", "QP6sMLe7"],
    "merch": ["Lc89ekUe", "PKxhJSLv"],
    "product": ["PKxhJSLv", "4ZYZBH3U", "MPDGgowj", "P4fUVfnj", "Dz2epBx3"],
    "cart": ["6BiJLu9R"],
    "checkout": ["4qW8xtnM", "Fs3GoyCW", "X9rB3hfB", "DQreBPwJ"],
    "order": ["FayRCohe", "JVsWwCUP", "5Spr7tKX", "JSsSbazs", "PVYmDajN", "KoHsF9S6"],
    "payment": ["WobqKBtK", "69Wk3uPb", "2jmEmc7L", "M8DF1uzo", "35n1WnQr", "X9rB3hfB"],
    "paypal": ["2jmEmc7L"],
    "stripe": ["2jmEmc7L", "WobqKBtK"],
    "apple pay": ["M8DF1uzo"],
    "google pay": ["35n1WnQr"],
    "refund": ["5Spr7tKX", "NLWUFPca", "T5myzMAD", "5NjF3BwS", "Rgfg4jJw"],
    "commission": ["WtyncS5m", "45rhm3ho", "3YmakH6c"],
    "earning": ["45rhm3ho", "WtyncS5m"],
    "payout": ["45rhm3ho", "Pzwgwsc4", "EdAgRJqT", "VT354ugj"],
    "balance": ["45rhm3ho", "QhrCgRei"],
    "tax": ["DxtdbGXh", "UsbeTP8r", "998UFYub", "NGenTPC6", "SHzxC7T7"],
    "fee": ["3YmakH6c", "X9rB3hfB", "RNCSGbXm", "E9KCQZ2Q", "Y3ALiWV3"],
    "catalog": ["VWVBq6yw", "HrVKubkR", "PKxhJSLv", "AR4bAa25", "12GxT1Y1", "KHPKKvLZ"],
    "shopify": ["FLg6NAv4", "DQreBPwJ", "Vc221iWC", "KHPKKvLZ"],
    "shop": ["PFW9BwwA", "5vApajMA", "YCb9Xjmf", "XGdbvnZb"],
    "storefront": ["5vApajMA", "3moKQuHE", "8tMnELNg"],
    "profile": ["TSxXp1zc", "32ZwqLSB", "6bMoVG9t", "EYXrKUmZ"],
    "account": ["3EEw3jug", "D4wN1vwU", "69Wk3uPb", "R2t12zGh", "WfGoDiLu"],
    "auth": ["Wq8hnca4", "FeG8TGeo", "Sj4Jx7sE", "SuG7U9Rv"],
    "login": ["Wq8hnca4", "FeG8TGeo", "Sj4Jx7sE", "CjLdWgmB", "LTy7SkcD"],
    "signup": ["Wq8hnca4", "FeG8TGeo"],
    "email": ["J4DhBqYW", "VefBFsf9", "DvWDt5U9", "AEuPwfbo"],
    "notification": ["J4DhBqYW", "DvWDt5U9", "V2oa6vKF"],
    "sms": ["V4VfZwTa", "6coJYKYb", "KAv1x37m"],
    "guest": ["BHNbbmCP", "jFiy4PNr", "YMEYj3kF", "NGenTPC6", "FhVAY9PS"],
    "subdomain": ["WAJFLKFm", "AVcqXw41", "7kPXTmAE"],
    "approval": ["XPnS1fM5", "4Y57w7gW"],
    "purchase approval": ["XPnS1fM5"],
    "collab": ["3pfH7pm8", "K9GYKa95", "TZ2KFx4x"],
    "co-selling": ["3pfH7pm8", "QUtAT4CU", "K9GYKa95"],
    "onboarding": ["VTYsYoXy"],
    "subscribe": ["BjaXYL8R", "6coJYKYb", "SA4KGeFf"],
    "subscription": ["BjaXYL8R", "6coJYKYb", "SA4KGeFf"],
    "redeem": ["P4fUVfnj"],
    "qr": ["P4fUVfnj"],
    "tracking": ["djpBMqZC", "igPaBv4m"],
    "affiliate": ["MubhF9NV", "13_Resell and Affiliate" if False else "MubhF9NV"],
    "analytics": ["UosyVp9p", "5eLhZmJc", "PM6N84Lv", "Mz4advqq", "Sd12RXWA"],
    "report": ["MvKrjSoc", "Mz4advqq", "CnhVZduH", "YCViWFs2"],
    "admin": ["4jXZmEFk", "HiodjQrp"],
    "merchant": ["82G1ojdU", "NqVQ1X7w", "6boAtVna", "GZE12kDY"],
    "campaigns": ["4arknoUt"],
    "follow": ["XrotXH5L", "STpsswpq", "EeXnPkLv"],
    "on-sale": ["5KVtYUZ4", "UNRyVyAT"],
    "fulfill": ["PVYmDajN", "2f7zTcsb", "XBrWEyCE"],
    "shipping": ["TFSvX3Nn", "R2t12zGh", "XBrWEyCE"],
    "address": ["MRpTyuge", "R2t12zGh"],
    "pixel": ["XbnCn4Wt"],
    "ad": ["XbnCn4Wt"],
    "announcement": ["X6eVAFoz", "96yvfh5L"],
    "banner": ["FVp1oE7z"],
    "collection": ["3jadwbrJ"],
    "form": ["3moKQuHE", "8tMnELNg"],
    "blacklist": ["RbhMLyRc", "Vo1Wv3Gs"],
    "dispute": ["AXRRCa6J", "Rgfg4jJw"],
    "sales": ["JSsSbazs", "5KVtYUZ4", "UNRyVyAT", "PVYmDajN"],
    "ticket hub": ["L7BkQ8uE"],
    "axs": ["L7BkQ8uE"],
    "tdc": ["L7BkQ8uE"],
    "scanner": ["P4fUVfnj"],
    "purchase history": ["D4wN1vwU"],
    "my tickets": ["WfGoDiLu"],
    "payment method": ["69Wk3uPb"],
    "custom price": ["RBiSFL7H", "TEpK7dhV"],
    "any-day": ["KmXiJZ3m"],
    "multiday": ["XEgYVVwo"],
    "lineup": ["51XRwHgA"],
    "privacy": ["335psfPL"],
    "cookie": ["335psfPL"],
    "handoff": ["Wq8hnca4", "FeG8TGeo"],
    "token": ["Wq8hnca4", "FeG8TGeo"],
    "discount": ["TWyYDusQ", "4arknoUt", "DNVB79mD"],
    "threshold": ["TWyYDusQ", "4arknoUt"],
    "attendee": ["Be9JTiKW", "8WTXjjjC"],
    "rte": ["2ojXUdsv", "HBf7C9KE"],
    "scroll": ["2ojXUdsv"],
    "tickets section": ["WfGoDiLu", "5KVtYUZ4"],
    "amount off": ["TWyYDusQ", "9tUABARi"],
    "delivery notes": ["J4DhBqYW"],
    "order-login": ["Wq8hnca4", "FayRCohe"],
}

# 噪音 PR（不影响测试范围）：发版/chore/合并类
NOISE_PATTERNS = [
    "release v", "versions/release", "main to release", "merge branch",
    "merge remote-tracking", "chore: release", "perf(ci)", "vitest",
    "upgrade shared", "remove dead code", "squash migrations",
    "ci:", "cleanup", "backport main", "chore(sync)", "feat:field",
]
NOISE_NO = [2194, 2195, 2193]  # admin-server 的 "Main to release / remove mongo" 纯合并类


def is_noise_pr(pr: dict) -> bool:
    title = (pr.get("title") or "").lower()
    if pr.get("number") in NOISE_NO:
        return True
    if pr.get("direct") and any(p in title for p in NOISE_PATTERNS):
        return True
    return False


# server/web 路径前缀 -> 关键词
PATH_HINTS: list = [
    ("apps/web/src/app/account", "account"),
    ("apps/web/src/app/checkout", "checkout"),
    ("apps/web/src/app/cart", "cart"),
    ("apps/web/src/app/catalog", "catalog"),
    ("apps/web/src/app/events", "event"),
    ("apps/web/src/app/login", "login"),
    ("apps/web/src/app/signup", "signup"),
    ("apps/web/src/app/shop", "shop"),
    ("apps/web/src/app/onboarding", "onboarding"),
    ("apps/web/src/app/admin", "admin"),
    ("src/purchase-approval", "approval"),
    ("src/posts", "post"),
    ("src/post-form", "post"),
    ("src/post-purchase-count", "post"),
    ("src/promotion", "promotion"),
    ("src/promotion-stat", "promotion"),
    ("src/events", "event"),
    ("src/product-event", "event"),
    ("src/products", "product"),
    ("src/product-v2", "product"),
    ("src/cart-item", "cart"),
    ("src/checkout", "checkout"),
    ("src/payment", "payment"),
    ("src/payment-center", "payment"),
    ("src/payment-method", "payment"),
    ("src/payment-eligibility", "payment"),
    ("src/payment-settings", "payment"),
    ("src/paypal", "paypal"),
    ("src/order", "order"),
    ("src/fulfillment", "fulfill"),
    ("src/commission", "commission"),
    ("src/earnings", "earning"),
    ("src/earning-share", "earning"),
    ("src/payout", "payout"),
    ("src/balance", "balance"),
    ("src/campaigns", "campaign"),
    ("src/catalog", "catalog"),
    ("src/auth", "auth"),
    ("src/authentication", "auth"),
    ("src/user", "account"),
    ("src/email", "email"),
    ("src/notification-settings", "notification"),
    ("src/inbox", "notification"),
    ("src/ticket-redemption", "redeem"),
    ("src/collab", "collab"),
    ("src/co-selling", "co-selling"),
    ("src/merchant", "merchant"),
    ("src/subdomain", "subdomain"),
    ("src/ad-events", "ad"),
    ("src/venue", "venue"),
    ("src/venue-map", "venue"),
]


def impact_modules(pr: dict) -> list:
    """From PR title + files, resolve ONES module uuids (ordered, dedup)."""
    tree = load_module_tree()
    text = (pr.get("title") or "").lower()
    files = " ".join(pr.get("files") or []).lower()
    hits = []
    # 1) path hints（文件路径是最可靠证据）
    for prefix, kw in PATH_HINTS:
        if prefix.lower() in files:
            hits.append(kw)
    # 2) title/文件名关键词（仅精确匹配映射表 key，避免发散）
    for kw in MODULE_MAP:
        if kw in text:
            hits.append(kw)
    # 3) 文件名中含的关键词
    for kw in MODULE_MAP:
        if kw in files:
            hits.append(kw)
    # resolve
    uuids = []
    for h in hits:
        if h in MODULE_MAP:
            uuids.extend(MODULE_MAP[h])
        elif len(h) == 8 and h in tree:
            uuids.append(h)
    seen = []
    for u in uuids:
        if u not in seen:
            seen.append(u)
    return seen


# ---------------------------------------------------------------- ONES

def ones_graphql_cases(env: dict, module_uuids: list, priority_uuids: list, limit: int = 500) -> list:
    """Fetch cases in modules with given priorities via GraphQL, per-module to avoid cap."""
    if not module_uuids:
        return []
    import ones_writer as ow
    team = env.get("ONES_TEAM_UUID", "T7u1zXum")
    out, seen = [], set()
    # 分批（每批 12 模块），避免单请求过大
    for i in range(0, len(module_uuids), 12):
        batch = module_uuids[i:i + 12]
        query = {
            "query": (
                "query($mods:[String!],$pris:[String!],$lim:Int){"
                "testcaseCases(filter:{testcaseModule_in:$mods,priority_in:$pris},limit:$lim){"
                "uuid name number priority{uuid} testcaseModule{uuid name} }"
                "}"
            ),
            "variables": {"mods": batch, "pris": priority_uuids, "lim": limit},
        }
        status, resp = ow.api_call(
            "POST", f"/project/api/project/team/{team}/items/graphql", query, env=env)
        if status != 200:
            continue
        try:
            data = resp["data"]["testcaseCases"]
        except Exception:
            continue
        for c in data:
            u = c.get("uuid")
            if u in seen:
                continue
            seen.add(u)
            out.append({
                "uuid": u,
                "name": c.get("name", ""),
                "number": c.get("number"),
                "priority": (c.get("priority") or {}).get("uuid", ""),
                "module_uuid": (c.get("testcaseModule") or {}).get("uuid", ""),
                "module_name": (c.get("testcaseModule") or {}).get("name", ""),
            })
    return out


def build_owner_map(env: dict, ow) -> None:
    """Scan whole Katana library, compute module->most-common assign (owner)."""
    team = env.get("ONES_TEAM_UUID", "T7u1zXum")
    lib = env.get("ONES_LIBRARY_UUID", "XcAFFViB")
    status, resp = ow.api_call(
        "GET", f"/project/api/project/team/{team}/testcase/library/{lib}/cases", env=env)
    if status != 200:
        print(f"  [warn] owner map scan failed ({status})")
        return
    cases = resp.get("cases", []) if isinstance(resp, dict) else []
    counter = defaultdict(Counter)
    for c in cases:
        mod = c.get("module_uuid")
        assign = c.get("assign")
        if mod and assign:
            counter[mod][assign] += 1
    owner = {m: cnt.most_common(1)[0][0] for m, cnt in counter.items()}
    save_owner_map(owner)
    print(f"  owner map: {len(owner)} modules cached")


def ensure_owner_map(env: dict, ow) -> dict:
    m = load_owner_map()
    if not m:
        build_owner_map(env, ow)
        m = load_owner_map()
    return m


def create_smoke_case(env: dict, ow, module_uuid: str, owner_uuid: str, pr: dict, existing: list) -> dict:
    """Create a P0 smoke case from PR info if no P0/P1 case exists for this PR topic."""
    title = (pr.get("title") or "").strip()
    short = title[:80]
    case_data = {
        "name": f"[Smoke] {short}",
        "module_uuid": module_uuid,
        "priority": "highest",
        "type": "functional",
        "assign": owner_uuid,
        "condition": f"Release {pr.get('repo')} #{pr.get('number')}: {title}",
        "desc": (
            f"<p>Release smoke case auto-created from PR: {title}</p>"
            f"<p>Repo: {pr.get('repo')} PR: #{pr.get('number')}</p>"
        ),
        "steps": [
            {"desc": "打开受影响功能入口，确认页面可正常加载", "result": "页面加载正常，无报错"},
            {"desc": "按 PR 描述的变更执行核心冒烟操作", "result": "功能行为符合 PR 预期"},
            {"desc": "检查关键数据/状态流转正确", "result": "数据一致，无异常状态"},
            {"desc": "回归相邻相关功能（支付/订单/活动）", "result": "无回归异常"},
        ],
    }
    result = ow.create_case(case_data, env)
    return result


# ---------------------------------------------------------------- plan (UI)

def create_plan_ui(env: dict, plan_name: str) -> str:
    """Create a ONES test plan via UI (reuses ones_create_plan_v3 pattern). Returns uuid."""
    import ones_writer as ow
    sys.path.insert(0, str(HERE))
    from playwright.sync_api import sync_playwright

    team = env.get("ONES_TEAM_ID") or env.get("ONES_TEAM_UUID", "T7u1zXum")
    email = env.get("ONES_EMAIL", "")
    password = env.get("ONES_PASSWORD", "")
    plan_uuid = None
    captured = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=180)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        def on_resp(resp):
            if "testcase/plan" in resp.url and resp.request.method in ("POST", "PUT", "PATCH"):
                try:
                    captured.append({
                        "status": resp.status, "url": resp.url,
                        "method": resp.request.method,
                        "body": resp.body().decode("utf-8", errors="replace"),
                    })
                except Exception:
                    pass

        page.on("response", on_resp)

        page.goto("https://ones.cn/auth/login", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        try:
            page.get_by_role("textbox", name="* 邮箱").fill(email)
            page.get_by_role("textbox", name="* 密码").fill(password)
            page.get_by_role("button", name="登录").click()
            page.wait_for_timeout(6000)
        except Exception as e:
            print(f"  [warn] login form: {e}")

        page.goto(f"https://ones.cn/project/#/testcase/team/{team}/index",
                  wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(6000)

        # Create test plan button (EN/CN)
        btn = page.locator('button:has-text("Create test plan")').first
        if btn.count() == 0:
            btn = page.locator('button:has-text("新建测试计划")').first
        btn.click()
        page.wait_for_timeout(2500)

        modal = page.locator(".ones-modal-wrap").first
        # name
        name_input = modal.locator('input[placeholder="Please enter"]').first
        if name_input.count() == 0:
            name_input = modal.locator('input[placeholder*="名称"]').first
        name_input.fill(plan_name)
        page.wait_for_timeout(500)

        # assignee: pick current user (linda) from dropdown
        sel = modal.locator('input[placeholder="Please select"]').first
        sel.click()
        page.wait_for_timeout(1500)
        try:
            sbox = page.locator('.ant-select-dropdown:visible input, .ant-select-search__field:visible').first
            if sbox.count() > 0:
                sbox.fill("linda")
                page.wait_for_timeout(1500)
            opt = page.locator('.ant-select-item-option:visible:has-text("linda"), [role="option"]:visible:has-text("linda")').first
            if opt.count() > 0:
                opt.click()
                print("  assignee: linda picked")
            else:
                anyopt = page.locator('.ant-select-item-option:visible').first
                if anyopt.count() > 0:
                    anyopt.click()
                    print("  assignee: first option picked:", anyopt.inner_text()[:30])
        except Exception as e:
            print(f"  [warn] assignee pick: {e}")
        page.wait_for_timeout(1000)

        modal.screenshot(path="data/ones_plan_filled.png")

        # OK
        ok = modal.locator('button:has-text("OK"), button:has-text("确定")').first
        ok.click()
        page.wait_for_timeout(6000)

        # extract uuid from captured response
        for entry in captured:
            try:
                body = json.loads(entry.get("body", "{}"))
            except Exception:
                continue
            if isinstance(body, dict):
                if body.get("uuid"):
                    plan_uuid = body["uuid"]
                    break
                for key in ("plan", "testcasePlan", "item", "data"):
                    obj = body.get(key) if isinstance(body, dict) else None
                    if isinstance(obj, dict) and obj.get("uuid"):
                        plan_uuid = obj["uuid"]
                        break
                    if isinstance(obj, list):
                        for o in obj:
                            if isinstance(o, dict) and o.get("uuid"):
                                plan_uuid = o["uuid"]
                                break
                if plan_uuid:
                    break
        browser.close()

    if not plan_uuid:
        print("  [error] could not extract new plan uuid from UI flow")
    return plan_uuid


# ---------------------------------------------------------------- main

def plan_name_for(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%Y %b %d Smoke testing on Prod env")


def get_plan_cases(env: dict, ow, plan_uuid: str) -> list:
    """Fetch case uuids already in an existing plan (baseline smoke set)."""
    team = env.get("ONES_TEAM_UUID", "T7u1zXum")
    status, resp = ow.api_call(
        "GET",
        f"/project/api/project/team/{team}/testcase/plan/{plan_uuid}/cases?limit=2000",
        env=env)
    if status != 200:
        return []
    cases = resp.get("cases", []) if isinstance(resp, dict) else []
    return [
        {"uuid": c.get("uuid"), "module_uuid": c.get("module_uuid"),
         "name": c.get("name", "")}
        for c in cases if c.get("uuid")
    ]


# 旧冒烟基线 plan（全量冒烟用例集，94 模块 228 条，全 P0）
BASELINE_PLAN = "BCCj2wi9"


def run(date_str: str, dry_run: bool, skip_plan_ui: bool, prs: str = "") -> dict:
    print(f"=== Daily Release Smoke Plan @ {date_str} (dry_run={dry_run}) ===")
    env, ow = ones_client()
    token = gh_token()
    if not token:
        print("[error] GitHub token unavailable")
        return {"error": "gh token"}

    tree = load_module_tree()
    report = {"date": date_str, "release_prs": [], "feature_prs": [],
              "impact_modules": {}, "cases_pulled": [], "cases_created": [],
              "plan": None}

    # 1) release PRs: explicit --prs OR branch cut on previous day (lock date)
    if prs:
        release_prs = []
        for item in prs.split(","):
            item = item.strip()
            if ":" in item:
                repo, num = item.rsplit(":", 1)
            elif "/" in item:
                repo, num = item.rsplit("/", 1)
            else:
                continue
            release_prs.append({"repo": repo.strip(), "number": int(num.strip())})
    else:
        lock_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"  lock date: {lock_date} (branch cut), plan date: {date_str} (go-live)")
        release_prs = find_release_prs(token, lock_date)
    if not release_prs:
        print("[warn] no release PR found")
        report["warning"] = "no release PR found"
        return report
    # fill release PR details
    for rp in release_prs:
        d = gh_get(None, token, f"/repos/bosinc/{rp['repo']}/pulls/{rp['number']}")
        if isinstance(d, dict) and d.get("title"):
            rp["title"] = d.get("title", "")
            rp["head"] = (d.get("head") or {}).get("ref", "")
            rp["base"] = (d.get("base") or {}).get("ref", "")
            rp["state"] = d.get("state")
            rp["merged_at"] = d.get("merged_at")
            rp["url"] = d.get("html_url", "")
    report["release_prs"] = release_prs
    for rp in release_prs:
        print(f"  release PR: {rp['repo']} #{rp['number']} {rp.get('title','')} ({rp.get('state')})")

    # 2) feature PRs
    feature_list = []
    for rp in release_prs:
        ext = extract_feature_prs(token, rp)
        for n in ext["feature_prs"]:
            feature_list.append(pr_details(token, rp["repo"], n))
        for dc in ext["direct"]:
            feature_list.append({"number": None, "repo": rp["repo"],
                                 "title": dc["message"], "files": [], "direct": True})
    feature_list = [pr for pr in feature_list if not is_noise_pr(pr)]
    report["feature_prs"] = feature_list
    print(f"  feature PRs (after noise filter): {len(feature_list)}")

    # 3) impact modules
    all_modules = []
    for pr in feature_list:
        mods = impact_modules(pr)
        pr["impact_modules"] = mods
        all_modules.extend(mods)
        print(f"    #{pr['number'] or '-'} {pr['title'][:60]} -> {len(mods)} mods")
    all_modules = list(dict.fromkeys(all_modules))
    report["impact_modules"] = all_modules
    print(f"  impact ONES modules: {len(all_modules)}")
    for u in all_modules:
        print(f"    {u} {tree.get(u, '?')}")

    if not all_modules:
        print("[warn] no impact modules resolved; fallback to full smoke set")
        return report

    # 4) pull smoke cases: baseline ∩ impact modules + P0 fill for uncovered modules
    baseline = get_plan_cases(env, ow, BASELINE_PLAN)
    baseline_mods = set(c["module_uuid"] for c in baseline)
    in_impact = [c for c in baseline if c["module_uuid"] in all_modules]
    report["baseline_in_impact"] = in_impact
    print(f"  baseline(228) ∩ impact modules: {len(in_impact)} cases")

    uncovered = [u for u in all_modules if u not in baseline_mods]
    extra = []
    if uncovered:
        p0_only = [ow.PRIORITY_MAP["highest"]]
        pulled = ones_graphql_cases(env, uncovered, p0_only, limit=500)
        by_mod = defaultdict(list)
        for c in pulled:
            by_mod[c["module_uuid"]].append(c)
        for u in uncovered:
            for c in by_mod.get(u, [])[:3]:      # 每未覆盖模块补最多 3 条 P0
                extra.append(c)
    report["extra_p0_cases"] = extra
    print(f"  extra P0 fill for {len(uncovered)} uncovered modules: {len(extra)} cases")

    cases = in_impact + extra
    report["cases_pulled"] = cases
    print(f"  total smoke cases for plan: {len(cases)}")
    for c in cases[:15]:
        print(f"    - {c['name'][:70]}")

    # 5) create missing cases
    if not dry_run:
        owner_map = ensure_owner_map(env, ow)
        existing_topics = set()
        for c in cases:
            existing_topics.add(c["name"].lower())
        for pr in feature_list:
            if not pr.get("impact_modules"):
                continue
            topic = re.sub(r"\(#\d+\)", "", pr["title"]).strip().lower()[:60]
            if not topic or topic in existing_topics:
                continue
            mod = pr["impact_modules"][0]
            owner = owner_map.get(mod, env.get("ONES_USER_ID", ""))
            r = create_smoke_case(env, ow, mod, owner, pr, cases)
            report["cases_created"].append({**r, "pr": pr["number"], "module": mod, "owner": owner})
            print(f"    created case for #{pr['number']}: {r.get('success')} {r.get('uuid','')}")

    # 6) create plan + link
    if not dry_run and not skip_plan_ui:
        name = plan_name_for(date_str)
        plan_uuid = create_plan_ui(env, name)
        report["plan"] = {"name": name, "uuid": plan_uuid}
        if plan_uuid:
            case_uuids = [c["uuid"] for c in cases] + \
                         [c["uuid"] for c in report["cases_created"] if c.get("uuid")]
            if case_uuids:
                res = ow.add_cases_to_plan(plan_uuid, case_uuids, env)
                report["plan"]["cases_linked"] = len(res.get("added", []))
                print(f"  plan {name} ({plan_uuid}) linked {len(res.get('added', []))} cases")
    elif not dry_run:
        report["plan"] = {"skipped_ui": True}

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "daily_smoke_plan_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("=== done, report: data/daily_smoke_plan_report.json ===")
    return report


def main():
    ap = argparse.ArgumentParser(description="Daily Katana release smoke test plan builder")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--prs", default="",
                    help='explicit release PRs: "katana-server:10258,katana-web:17306,katana-admin-server:2196"')
    ap.add_argument("--dry-run", action="store_true", help="analysis only, no ONES writes")
    ap.add_argument("--no-plan-ui", action="store_true", help="skip plan creation via UI")
    args = ap.parse_args()
    run(args.date, args.dry_run, args.no_plan_ui, args.prs)


if __name__ == "__main__":
    main()
