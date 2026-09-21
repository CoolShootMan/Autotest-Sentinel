#!/usr/bin/env python3
"""用 GitHub REST API 开 / 合 PR —— 替代 `gh` CLI（本机没装），复用 gh_push 的凭据与 repo 解析。

背景：公司仓团队走 PR 流程（建分支 -> PR -> merge）。本机无 gh CLI，且裸 `git push` 会卡
凭据 GUI，所以统一：Windows 凭据管理器取 token + urllib 调 API。**token 绝不打印**。

用法（完整一轮）：
    # 1) 从最新 main 开分支
    git switch -c feat/KAT-xxxx-简述
    # 2) 改完提交（中文用文件，别用 -m）
    git commit -F .git/COMMIT_MSG.txt
    # 3) 推分支 + 开 PR（自动推分支，打印 PR URL）
    py -3.9 tools/gh_pr.py --push --title "fix(xxx): ..." --body "改动说明"
    # 4) 合掉（默认 merge 提交，符合本仓"禁 rebase"纪律）
    py -3.9 tools/gh_pr.py --merge --pr 12
    # 5) 回 main 并同步
    git switch main && py -3.9 tools/gh_push.py   # 拉/推公司仓 main（下次开分支前先更新）

常用选参：
    --base main（默认）   --branch <名>（默认当前分支）   --draft
    --dry-run（只打印将执行的 API，不真调）   --remote origin（默认）

坑：
    - 分支必须**先存在于远端**，否则 POST 报 422（用 --push 省事）。
    - head 与 base 之间**没有新提交**也会 422（GitHub 不开空 PR）。
    - 同分支重复开 PR -> 422 "already exists"，本脚本会**自动汇报现成 PR**，不报错。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gh_push  # noqa: E402  复用凭据读取与 remote 解析

API = "https://api.github.com"


def api(url, token, method="GET", payload=None):
    """返回 (http_status, body)。网络异常 -> (0, {...})。"""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": "token " + token,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "autotest-gh-pr",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            body = json.loads(raw)
        except Exception:
            body = {"message": raw}
        return e.code, body
    except Exception as e:  # 网络/超时/SSL
        return 0, {"message": "%s: %s" % (type(e).__name__, e)}


def main() -> int:
    ap = argparse.ArgumentParser(description="GitHub PR 工具（REST API；凭据取自 gh_push）")
    ap.add_argument("--remote", default="origin", help="远端名（默认 origin = 公司仓）")
    ap.add_argument("--host", default=None, help="覆盖 host")
    ap.add_argument("--slug", default=None, help="覆盖 org/repo")
    ap.add_argument("--cred-target", default=None, help="覆盖凭据 target")
    ap.add_argument("--branch", default=None, help="源分支（默认当前分支）")
    ap.add_argument("--base", default="main", help="目标分支（默认 main）")
    ap.add_argument("--title", default=None, help="PR 标题")
    ap.add_argument("--body", default="", help="PR 正文")
    ap.add_argument("--draft", action="store_true", help="开成草稿 PR")
    ap.add_argument("--push", action="store_true", help="开 PR 前先把分支推到 remote")
    ap.add_argument("--merge", action="store_true", help="合并指定 PR（需 --pr N）")
    ap.add_argument("--pr", type=int, default=None, help="要合并的 PR 号")
    ap.add_argument("--method", default="merge", choices=["merge", "squash", "rebase"], help="合并方式")
    ap.add_argument("--dry-run", action="store_true", help="只打印将执行的 API，不真调")
    args = ap.parse_args()

    host, slug, user_hint = gh_push.resolve_target(args.remote, args.host, args.slug)
    cred_target = gh_push.resolve_cred_target(args.remote, host, args.cred_target)
    user, token = gh_push.read_credential(cred_target, slug.split("/")[0])
    if not token:
        print("[FAIL] 凭据管理器里读不到 %s" % cred_target, file=sys.stderr)
        print('       补一条：cmdkey /generic:"%s" /user:<用户名> /pass:<token>' % cred_target, file=sys.stderr)
        return 1

    branch = args.branch
    if not branch:
        r = gh_push.git("rev-parse", "--abbrev-ref", "HEAD")
        branch = (r.stdout or "").strip()
    if not branch or branch == "HEAD":
        print("[FAIL] 无法确定当前分支（detached HEAD？）", file=sys.stderr)
        return 1

    # ---- 合并已有 PR ----
    if args.merge:
        if not args.pr:
            print("[FAIL] --merge 需要 --pr <号>", file=sys.stderr)
            return 1
        url = "%s/repos/%s/pulls/%d/merge" % (API, slug, args.pr)
        if args.dry_run:
            print("[DRY] PUT %s  merge_method=%s" % (url, args.method))
            return 0
        st, body = api(url, token, "PUT", {"merge_method": args.method})
        if st in (200, 201):
            print("[OK] PR #%d 已合并 (%s): %s" % (args.pr, args.method, (body.get("sha") or "")[:12]))
            return 0
        print("[FAIL] 合并 PR #%d 失败 [%s]: %s" % (args.pr, st, body), file=sys.stderr)
        return 1

    # ---- 先推分支 ----
    if args.push:
        ns = argparse.Namespace(
            host=args.host, slug=args.slug, cred_target=args.cred_target, dry_run=args.dry_run
        )
        rc = gh_push.push_one(args.remote, branch, ns)
        if rc:
            return rc

    # ---- 开 PR ----
    if not args.title:
        print("[FAIL] 开 PR 需要 --title", file=sys.stderr)
        return 1
    payload = {"title": args.title, "head": branch, "base": args.base, "body": args.body or ""}
    if args.draft:
        payload["draft"] = True

    url = "%s/repos/%s/pulls" % (API, slug)
    if args.dry_run:
        print("[DRY] POST %s" % url)
        print("      %s -> %s   draft=%s" % (branch, args.base, args.draft))
        print("      title: %s" % args.title)
        return 0

    st, body = api(url, token, "POST", payload)
    if st in (200, 201):
        print("[OK] PR #%s 已创建: %s" % (body.get("number"), body.get("html_url")))
        return 0

    # 同 head 已存在 PR -> 汇报现成的（不报错）
    if st == 422 and "already exists" in json.dumps(body).lower():
        owner = slug.split("/")[0]
        st2, lst = api("%s/repos/%s/pulls?state=all&head=%s:%s" % (API, slug, owner, branch), token)
        if st2 == 200 and isinstance(lst, list) and lst:
            p = lst[0]
            print("[SKIP] 该分支已有 PR #%s [%s]: %s" % (p.get("number"), p.get("state"), p.get("html_url")))
            return 0

    print("[FAIL] 开 PR 失败 [%s]: %s" % (st, body), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
