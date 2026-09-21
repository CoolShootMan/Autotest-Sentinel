#!/usr/bin/env python3
"""推送当前分支到 GitHub —— 经 Windows 凭据管理器取 token。

为什么需要这个脚本：本机在**无头 shell 里直接 `git push` 会挂死**（卡在凭据交互）。
所以改为从 Windows 凭据管理器读取 GitHub 凭据（target: `git:https://github.com`），
拼成 token URL 推送。**token 绝不打印**（输出一律脱敏）。

用法：
    py -3.9 tools/gh_push.py                     # 推当前分支到 origin
    py -3.9 tools/gh_push.py --branch main
    py -3.9 tools/gh_push.py --remote upstream
    py -3.9 tools/gh_push.py --dry-run           # 只打印将执行的动作（脱敏）

坑（都在这台机器上实测过）：
    - git 的输出是 **GBK**；不指定 encoding 会 UnicodeDecodeError。
    - `git rebase` 会损坏中途态 → 合并请用 `git merge`。
    - 推完记得修 tracking，否则 `git status` 会误报 ahead/behind。
"""
from __future__ import annotations

import argparse
import ctypes
import subprocess
import sys
from ctypes import wintypes

SLUG = "CoolShootMan/Autotest-Sentinel"
HOST = "github.com"
CRED_TARGET = "git:https://github.com"
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


def read_credential(target: str):
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
    user = c.UserName or "CoolShootMan"
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


def main() -> int:
    ap = argparse.ArgumentParser(description="经凭据管理器推送 GitHub")
    ap.add_argument("--remote", default="origin", help="远端名（默认 origin）")
    ap.add_argument("--branch", default=None, help="分支（默认当前分支）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将执行的动作")
    args = ap.parse_args()

    branch = args.branch
    if not branch:
        r = git("rev-parse", "--abbrev-ref", "HEAD")
        branch = (r.stdout or "").strip()
    if not branch or branch == "HEAD":
        print("[FAIL] 无法确定当前分支（是否处于 detached HEAD？）", file=sys.stderr)
        return 1

    user, token = read_credential(CRED_TARGET)
    if not token:
        print(f"[FAIL] 凭据管理器里读不到 {CRED_TARGET}（用 cmdkey /list 确认）", file=sys.stderr)
        return 1

    url = f"https://{user}:{token}@{HOST}/{SLUG}.git"
    safe = f"https://{HOST}/{SLUG}.git"

    if args.dry_run:
        print(f"[DRY] git push {safe} {branch}   (身份: {user})")
        return 0

    r = git("push", url, branch)
    print(((r.stdout or "") + (r.stderr or "")).replace(token, "***").strip())
    if r.returncode != 0:
        return r.returncode

    # 修 tracking，避免 status 误报 ahead/behind
    head = (git("rev-parse", "HEAD").stdout or "").strip()
    if head:
        git("update-ref", f"refs/remotes/{args.remote}/{branch}", head)
        print(f"[OK] {args.remote}/{branch} -> {head[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
