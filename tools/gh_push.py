#!/usr/bin/env python3
"""推送当前分支到一个或多个远端 —— 经 Windows 凭据管理器取 token。

为什么需要这个脚本：本机在**无头 shell 里直接 `git push` 会挂死**（卡在凭据交互）。
所以改为从 Windows 凭据管理器读取凭据，拼成 token URL 推送。**token 绝不打印**
（输出一律脱敏）。

**host / slug 自动从 `git remote get-url <remote>` 推导**，因此换托管站无需改本文件。
**凭据 target 按 remote 解析**，所以**同一 host 下可并存多账号**（例如个人 GitHub +
公司 org）—— 给某个 remote 配一条 `credtarget.<remote>` 即可与默认的 host 级凭据隔离。

用法：
    py -3.9 tools/gh_push.py                     # 推当前分支到 origin
    py -3.9 tools/gh_push.py --branch main
    py -3.9 tools/gh_push.py --remote origin company   # 一次推多个远端（双推）
    py -3.9 tools/gh_push.py --remote company --dry-run
    py -3.9 tools/gh_push.py --host github.1m.app --slug 1m-qa/Autotest-Sentinel

凭据 target 解析优先级：
    --cred-target  >  git config --local credTarget.<remote>  >  git:https://<host>
例（同一 host 下并存两个账号：用独立 remote + 独立凭据 target 隔离）：
    git config --local credTarget.<remote> "git:https://<host>/<org>/<repo>"
    cmdkey /generic:"git:https://<host>/<org>/<repo>" /user:<用户名> /pass:<token>

坑（都在这台机器上实测过）：
    - git 的输出是 **GBK**；不指定 encoding 会 UnicodeDecodeError。
    - `git rebase` 会损坏中途态 → 合并请用 `git merge`。
    - 推完记得修 tracking，否则 `git status` 会误报 ahead/behind（本脚本已自动做）。
"""
from __future__ import annotations

import argparse
import ctypes
import subprocess
import sys
from ctypes import wintypes

# 仅在无法从 git remote 推导时使用的兜底（保证默认仓库仍可用）
DEFAULT_HOST = "github.com"
DEFAULT_SLUG = "CoolShootMan/Autotest-Sentinel"
DEFAULT_USER = "CoolShootMan"
CRED_TYPE_GENERIC = 1


class CREDENTIAL_ATTRIBUTE(ctypes.Structure):
    _fields_ = [
        ("Keyword", wintypes.LPWSTR),
        ("Flags", wintypes.DWORD),
        ("ValueSize", wintypes.DWORD),
        ("Value", ctypes.POINTER(ctypes.c_byte)),
    ]


class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.POINTER(CREDENTIAL_ATTRIBUTE)),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


def read_credential(target: str, user_fallback: str = DEFAULT_USER):
    advapi32 = ctypes.windll.advapi32
    advapi32.CredReadW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.POINTER(ctypes.POINTER(CREDENTIAL)),
    ]
    advapi32.CredReadW.restype = wintypes.BOOL
    advapi32.CredFree.argtypes = [ctypes.c_void_p]

    pcred = ctypes.POINTER(CREDENTIAL)()
    if not advapi32.CredReadW(target, CRED_TYPE_GENERIC, 0, ctypes.byref(pcred)):
        return None, None
    c = pcred.contents
    blob = ctypes.string_at(c.CredentialBlob, c.CredentialBlobSize)
    token = blob.decode("utf-16-le").rstrip("\x00")
    user = c.UserName or user_fallback
    advapi32.CredFree(pcred)
    return user, token


def git(*args: str):
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="gbk",
        errors="replace",
    )


def parse_remote_url(url: str):
    """从 remote URL 解析 (netloc, slug)。兼容 https 与 scp-like ssh。

    https://[user[:pass]@]host[:port]/org/repo(.git)  -> ("host[:port]", "org/repo")
    git@host:org/repo(.git)                            -> ("host",        "org/repo")
    """
    u = (url or "").strip()
    if u.startswith("git@"):
        hostpart, _, path = u[4:].partition(":")
    elif "://" in u:
        hostpart, _, path = u.split("://", 1)[1].partition("/")
    else:
        hostpart, _, path = u.partition("/")
    netloc = hostpart.split("@")[-1].strip()  # 去 userinfo，保留 host[:port]
    slug = path[:-4] if path.endswith(".git") else path
    return netloc, slug.strip("/")


def resolve_target(remote: str, host_override=None, slug_override=None):
    """推导 (host, slug, user_hint)。优先级：CLI 覆盖 > git remote get-url > DEFAULT_*。"""
    r = git("remote", "get-url", remote)
    url = (r.stdout or "").strip()
    host = slug = ""
    if r.returncode == 0 and url:
        host, slug = parse_remote_url(url)
    host = host_override or host or DEFAULT_HOST
    slug = slug_override or slug or DEFAULT_SLUG
    # token URL 里的用户名对 PAT 鉴权不敏感；优先取凭据里的，其次取仓库 owner
    user_hint = slug.split("/")[0] if "/" in slug else DEFAULT_USER
    return host, slug, user_hint


def resolve_cred_target(remote: str, host: str, override=None):
    """凭据 target：--cred-target > git config credTarget.<remote> > git:https://<host>。"""
    if override:
        return override
    r = git("config", "--get", f"credTarget.{remote}")
    cfg = (r.stdout or "").strip()
    if r.returncode == 0 and cfg:
        return cfg
    return f"git:https://{host}"


def push_one(remote: str, branch: str, args) -> int:
    host, slug, user_hint = resolve_target(remote, args.host, args.slug)
    cred_target = resolve_cred_target(remote, host, args.cred_target)

    user, token = read_credential(cred_target, user_hint)
    if not token:
        print(f"[FAIL] ({remote}) 凭据管理器里读不到 {cred_target}", file=sys.stderr)
        print(
            f'       补一条：cmdkey /generic:"{cred_target}" /user:<用户名> /pass:<token>',
            file=sys.stderr,
        )
        return 1

    safe = f"https://{host}/{slug}.git"
    if args.dry_run:
        print(f"[DRY] ({remote}) git push {safe} {branch}   (身份: {user}, 凭据: {cred_target})")
        return 0

    url = f"https://{user}:{token}@{host}/{slug}.git"
    r = git("push", url, branch)
    print(f"[{remote}] " + ((r.stdout or "") + (r.stderr or "")).replace(token, "***").strip())
    if r.returncode != 0:
        return r.returncode

    # 修 tracking，避免 status 误报 ahead/behind
    # 注意：要解析**被推的分支**（branch）而非 HEAD —— 推非当前分支时两者不同
    head = (git("rev-parse", f"refs/heads/{branch}").stdout or "").strip()
    if not head:
        head = (git("rev-parse", "HEAD").stdout or "").strip()
    if head:
        git("update-ref", f"refs/remotes/{remote}/{branch}", head)
        print(f"[{remote}] [OK] {remote}/{branch} -> {head[:12]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="经凭据管理器推送（host/slug 自动从 remote 推导）")
    ap.add_argument("--remote", nargs="+", default=["origin"], help="远端名，可多个（默认 origin）")
    ap.add_argument("--branch", default=None, help="分支（默认当前分支）")
    ap.add_argument("--host", default=None, help="覆盖从 remote 推导的 host")
    ap.add_argument("--slug", default=None, help="覆盖从 remote 推导的 org/repo")
    ap.add_argument("--cred-target", default=None, help="覆盖凭据 target（默认按 remote 推导）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将执行的动作（脱敏）")
    args = ap.parse_args()

    branch = args.branch
    if not branch:
        r = git("rev-parse", "--abbrev-ref", "HEAD")
        branch = (r.stdout or "").strip()
    if not branch or branch == "HEAD":
        print("[FAIL] 无法确定当前分支（是否处于 detached HEAD？）", file=sys.stderr)
        return 1

    rc = 0
    for remote in args.remote:
        rc |= push_one(remote, branch, args)
    return rc


if __name__ == "__main__":
    sys.exit(main())
