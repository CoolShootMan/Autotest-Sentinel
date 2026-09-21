#!/usr/bin/env python3
"""把当前 main 的「通用件子集」同步到个人仓库（remote `personal`）。

背景：同一条工作树要服务两个远端 —— `origin`（公司仓，全量）与 `personal`（个人仓，只留通用件）。
`main` 全量推 `origin`；本脚本按 DENY 名单过滤出 `personal` 分支（只含通用工具/skill/框架），
再把 `personal` 推到 `personal` remote 的 `main`。

原理（纯 plumbing，**不碰工作区、不切 HEAD**）：
  1. `git read-tree <source>` 到临时 index
  2. `git rm -r --cached --ignore-unmatch <DENY...>` 剔除业务路径
  3. `git write-tree` → `git commit-tree`（父 = personal 现有 tip，首次 = origin/main）→ `update-ref`
  4. `git push <token-url> refs/heads/personal:refs/heads/main`

镜像提交固定用**个人身份**（见 MIRROR_*），避免把公司邮箱写进个人仓历史。

用法：
  py -3.9 tools/sync_personal.py --dry-run    # 只报告会保留/剔除多少文件（无副作用）
  py -3.9 tools/sync_personal.py --no-push    # 只更新本地 personal 分支
  py -3.9 tools/sync_personal.py              # 生成 personal 并推 personal remote

DENY 名单在下方，按需增删；边界原则：**业务用例/业务数据/生成物 → 剔除；工具/框架/skill/文档 → 保留**。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gh_push  # noqa: E402  复用凭据读取与 remote 解析

SOURCE = "main"            # 全量来源分支
LOCAL_BRANCH = "personal"  # 本地过滤分支名
REMOTE = "personal"        # 个人仓 remote 名（origin 已是公司仓）
REMOTE_BRANCH = "main"     # 个人仓目标分支

# 镜像提交使用的个人身份（与公司仓库的 local user.email 无关）
MIRROR_NAME = "CoolShootMan"
MIRROR_EMAIL = "66861349+CoolShootMan@users.noreply.github.com"

# —— 剔除名单：业务用例 / 业务数据 / 生成物 ——
# 注意：test_case/UI/{smoke_testing.yaml, Katana_curator_smoke_release.yaml}
# 故意**保留** —— 让个人仓至少有一套能直接跑起来的冒烟用例。
DENY = [
    # UI 业务用例（保留两个 smoke 文件，见上）
    "test_case/UI/All_YAML",
    # API 业务用例
    "test_case/API auto script/tests",
    "test_case/API auto script/suites",
    "test_case/API auto script/_apifox_export",
    # 性能业务用例
    "test_case/performance testing",
    # 业务素材 / 数据 / 报告
    "use_cases",
    "data",
    "recordings",
    "allure",
    "Error_Test_Case_Diagnosis_Report",
    # 业务向根级报告
    "overview_T1742_diagnosis.md",
    "overview_T3690_duplicate_key_fix.md",
    "overview_T4866_net_aborted_fix.md",
    "overview_post_venue_map_debug.md",
]


def git(*args, index=None, extra_env=None):
    env = dict(os.environ)
    if index:
        env["GIT_INDEX_FILE"] = index
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["git", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )


def build_tree(source: str):
    """返回 (tree_sha, kept_count, total_count)。用临时 index，无副作用。"""
    fd, idx = tempfile.mkstemp(prefix="syncidx_")
    os.close(fd)
    try:
        r = git("read-tree", source, index=idx)
        if r.returncode != 0:
            raise SystemExit(f"[FAIL] read-tree {source}: {r.stderr.strip()}")
        r = git("rm", "-r", "-q", "--cached", "--ignore-unmatch", "--", *DENY, index=idx)
        if r.returncode != 0:
            raise SystemExit(f"[FAIL] index rm: {r.stderr.strip()}")
        r = git("write-tree", index=idx)
        if r.returncode != 0:
            raise SystemExit(f"[FAIL] write-tree: {r.stderr.strip()}")
        tree = r.stdout.strip()
    finally:
        try:
            os.remove(idx)
        except OSError:
            pass
    total = len(git("ls-tree", "-r", "--name-only", source).stdout.splitlines())
    kept = len(git("ls-tree", "-r", "--name-only", tree).stdout.splitlines())
    return tree, kept, total


def parent_commit():
    """镜像分支的父提交 = 个人仓当前 tip（origin/main）。

    始终以远端 tip 为父 → 每次生成的都是「origin/main + 1 个过滤提交」，
    保证 push 是快进、不会出现分叉被拒。本地 personal 分支只作兜底。
    """
    r = git("rev-parse", "--verify", "-q", f"refs/remotes/{REMOTE}/{REMOTE_BRANCH}")
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    r = git("rev-parse", "--verify", "-q", f"refs/heads/{LOCAL_BRANCH}")
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    return None


def _token_url():
    host, slug, user_hint = gh_push.resolve_target(REMOTE)
    cred = gh_push.resolve_cred_target(REMOTE, host)
    user, token = gh_push.read_credential(cred, user_hint)
    if not token:
        print(f"[FAIL] 凭据管理器里读不到 {cred}", file=sys.stderr)
        return None, None
    return f"https://{user}:{token}@{host}/{slug}.git", token


def fetch() -> int:
    url, token = _token_url()
    if not url:
        return 1
    r = git("fetch", url, f"{REMOTE_BRANCH}:refs/remotes/{REMOTE}/{REMOTE_BRANCH}")
    print(((r.stdout or "") + (r.stderr or "")).replace(token, "***").strip())
    return r.returncode


def push(commit: str) -> int:
    url, token = _token_url()
    if not url:
        return 1
    r = git("push", url, f"refs/heads/{LOCAL_BRANCH}:refs/heads/{REMOTE_BRANCH}")
    print(((r.stdout or "") + (r.stderr or "")).replace(token, "***").strip())
    if r.returncode != 0:
        return r.returncode
    git("update-ref", f"refs/remotes/{REMOTE}/{REMOTE_BRANCH}", commit)
    print(f"[OK] {REMOTE}/{REMOTE_BRANCH} -> {commit[:12]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="同步通用件子集到个人仓")
    ap.add_argument("--source", default=SOURCE, help=f"全量来源分支（默认 {SOURCE}）")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不建立分支/不推送")
    ap.add_argument("--no-push", action="store_true", help="只更新本地 personal 分支，不推")
    ap.add_argument("--fetch", action="store_true", help="推送前先拉取 origin 最新")
    args = ap.parse_args()

    if args.fetch and not args.dry_run:
        rc = fetch()
        if rc != 0:
            return rc

    tree, kept, total = build_tree(args.source)
    removed = total - kept
    print(f"源分支 {args.source}: {total} 文件 → 通用件 {kept} 保留 / {removed} 剔除")
    for d in DENY:
        print(f"   - {d}")
    if args.dry_run:
        print("[DRY] 未创建分支、未推送")
        return 0

    parent = parent_commit()
    if parent is None:
        print(f"[FAIL] 找不到 {LOCAL_BRANCH} 或 {REMOTE}/{REMOTE_BRANCH} 作为父提交", file=sys.stderr)
        return 1

    env = {
        "GIT_AUTHOR_NAME": MIRROR_NAME, "GIT_AUTHOR_EMAIL": MIRROR_EMAIL,
        "GIT_COMMITTER_NAME": MIRROR_NAME, "GIT_COMMITTER_EMAIL": MIRROR_EMAIL,
    }
    msg = f"chore(mirror): sync generic subset from {args.source} ({kept} files)"
    r = git("commit-tree", tree, "-p", parent, "-m", msg, extra_env=env)
    if r.returncode != 0:
        print(f"[FAIL] commit-tree: {r.stderr.strip()}", file=sys.stderr)
        return 1
    commit = r.stdout.strip()

    if commit == parent:
        print("[OK] 内容无变化，跳过")
        return 0

    git("update-ref", f"refs/heads/{LOCAL_BRANCH}", commit)
    print(f"[OK] {LOCAL_BRANCH} -> {commit[:12]}  ({msg})")

    if args.no_push:
        print("[SKIP] --no-push，未推送到远端")
        return 0
    return push(commit)


if __name__ == "__main__":
    sys.exit(main())
