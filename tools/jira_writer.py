#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jira 写入工具 —— 更新 issue 的 description / 追加 comment（ADF 由简化 markdown 生成）。

背景：`tools/jira_reader.py` 只读；回填 `customfield_10090` 有 `tools/jira_backfill_test_link.py`。
但**补全 bug 票的描述**（把 Actual Result / 根因 / 影响写进去）一直缺工具 —— 本文件补上。

用法：
    # 看当前描述（纯文本）
    py -3.9 tools/jira_writer.py KAT-12123 --show-description

    # 用 markdown 文件整体替换描述；--keep-media 把原描述里的图片节点塞回 <!--MEDIA--> 处
    py -3.9 tools/jira_writer.py KAT-12123 --description-file d.md --keep-media --dry-run
    py -3.9 tools/jira_writer.py KAT-12123 --description-file d.md --keep-media

    # 追加一段到现有描述末尾（保留原文，最小侵入）
    py -3.9 tools/jira_writer.py KAT-12123 --append-description-file d.md

    # 发评论
    py -3.9 tools/jira_writer.py KAT-12123 --comment-file c.md

支持的 markdown 子集：`# / ## / ###` 标题、段落、`- ` 无序、`1. ` 有序、
``` 代码块 ```、`---` 分隔线、`> ` 引用、行内 `**粗体**` / `` `代码` `` / `[文字](url)`。
`<!--MEDIA-->` 单独成段时，会被替换为原描述里的图片节点（配合 `--keep-media`）。

注意：Jira description 是 ADF，不是 markdown。**重写前先 `--show-description` 看原文**，
并务必用 `--keep-media`，否则描述里的截图会丢。
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV_PATH = Path(__file__).parent.parent / "backend" / ".env"


def load_env() -> dict:
    env = {}
    if not ENV_PATH.exists():
        return env
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def _auth_headers(env: dict) -> dict:
    auth = base64.b64encode(
        f'{env["JIRA_EMAIL"]}:{env["JIRA_API_TOKEN"]}'.encode()
    ).decode()
    return {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def get_issue(key: str, env: dict, fields: str = "description") -> dict:
    url = f'{env["JIRA_BASE_URL"].rstrip("/")}/rest/api/3/issue/{key}?fields={fields}'
    req = urllib.request.Request(url, headers=_auth_headers(env))
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def put_fields(key: str, env: dict, fields: dict):
    url = f'{env["JIRA_BASE_URL"].rstrip("/")}/rest/api/3/issue/{key}'
    body = json.dumps({"fields": fields}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PUT", headers=_auth_headers(env))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:600]


def post_comment(key: str, env: dict, adf: dict):
    url = f'{env["JIRA_BASE_URL"].rstrip("/")}/rest/api/3/issue/{key}/comment'
    body = json.dumps({"body": adf}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers=_auth_headers(env))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8")).get("id", "")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:600]


# ---------------------------------------------------------------------------
# markdown -> ADF
# ---------------------------------------------------------------------------

# 行内：代码 / 粗体 / 链接
INLINE_RE = re.compile(r"(`[^`]+`)|(\*\*[^*]+\*\*)|(\[[^\]]+\]\([^)]+\))")


def _inlines(text: str) -> list:
    nodes, pos = [], 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            nodes.append({"type": "text", "text": text[pos:m.start()]})
        tok = m.group(0)
        if tok.startswith("`"):
            nodes.append({"type": "text", "text": tok[1:-1], "marks": [{"type": "code"}]})
        elif tok.startswith("**"):
            nodes.append({"type": "text", "text": tok[2:-2], "marks": [{"type": "strong"}]})
        else:
            m_link = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok)
            if not m_link:
                nodes.append({"type": "text", "text": tok})
            else:
                label, url = m_link.groups()
                nodes.append({
                    "type": "text",
                    "text": label,
                    "marks": [{"type": "link", "attrs": {"href": url}}],
                })
        pos = m.end()
    if pos < len(text):
        nodes.append({"type": "text", "text": text[pos:]})
    return nodes


def _para(text: str) -> dict:
    text = text.strip()
    if not text:
        return {"type": "paragraph"}
    return {"type": "paragraph", "content": _inlines(text)}


def _list(kind: str, items: list) -> dict:
    node = {
        "type": "bulletList" if kind == "ul" else "orderedList",
        "content": [{"type": "listItem", "content": [_para(t)]} for t in items],
    }
    if kind == "ol":
        node["attrs"] = {"order": 1}
    return node


def md_to_adf(md: str) -> dict:
    content = []
    ul, ol, code = [], [], None

    def flush():
        nonlocal ul, ol
        if ul:
            content.append(_list("ul", ul))
            ul = []
        if ol:
            content.append(_list("ol", ol))
            ol = []

    for raw in md.splitlines():
        line = raw.rstrip()

        if code is not None:
            if line.strip().startswith("```"):
                content.append({"type": "codeBlock", "content": [{"type": "text", "text": "\n".join(code)}]})
                code = None
            else:
                code.append(raw)
            continue
        if line.strip().startswith("```"):
            flush()
            code = []
            continue

        if not line.strip():
            flush()
            continue
        if line.strip() == "<!--MEDIA-->":
            flush()
            content.append({"__MEDIA__": True})
            continue
        if line.strip() in ("---", "***", "___"):
            flush()
            content.append({"type": "rule"})
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush()
            content.append({
                "type": "heading",
                "attrs": {"level": len(m.group(1))},
                "content": _inlines(m.group(2).strip()),
            })
            continue
        if line.lstrip().startswith("> "):
            flush()
            content.append({"type": "blockquote", "content": [_para(line.lstrip()[2:])]})
            continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            if ol:
                flush()
            ul.append(m.group(1).strip())
            continue
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            if ul:
                flush()
            ol.append(m.group(1).strip())
            continue

        flush()
        content.append(_para(line))

    if code is not None:
        content.append({"type": "codeBlock", "content": [{"type": "text", "text": "\n".join(code)}]})
    flush()
    return {"type": "doc", "version": 1, "content": content}


def collect_media(adf: dict) -> list:
    """深度收集原描述里的 mediaSingle（含 media）节点，顺序保留。"""
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "mediaSingle":
                found.append(node)
                return
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk((adf or {}).get("content", []))
    return found


def adf_to_text(node, indent=0) -> str:
    """极简 ADF -> 纯文本（够用即可；完整版在 tools/jira_reader.py）。"""
    if not isinstance(node, dict):
        return ""
    t = node.get("type", "")
    c = node.get("content", [])
    if t == "text":
        return node.get("text", "")
    if t == "doc":
        return "\n".join(adf_to_text(x) for x in c)
    if t == "paragraph":
        return "".join(adf_to_text(x) for x in c)
    if t == "heading":
        return "#" * node.get("attrs", {}).get("level", 1) + " " + "".join(adf_to_text(x) for x in c)
    if t in ("bulletList", "orderedList"):
        lines = []
        for i, it in enumerate(c, 1):
            bullet = "- " if t == "bulletList" else f"{i}. "
            lines.append(bullet + " ".join(adf_to_text(x) for x in it.get("content", [])))
        return "\n".join(lines)
    if t == "listItem":
        return " ".join(adf_to_text(x) for x in c)
    if t == "codeBlock":
        return "```\n" + "".join(adf_to_text(x) for x in c) + "\n```"
    if t == "rule":
        return "---"
    if t == "mediaSingle":
        return "[IMAGE]"
    if c:
        return "\n".join(adf_to_text(x) for x in c)
    return ""


def resolve_media(adf: dict, media_nodes: list) -> dict:
    """把 <!--MEDIA--> 占位替换成原图节点。"""
    out = []
    used = 0
    for node in adf["content"]:
        if node.get("__MEDIA__"):
            if media_nodes:
                out.append(media_nodes[used] if used < len(media_nodes) else media_nodes[-1])
                used += 1
            continue
        out.append(node)
    if media_nodes and used == 0:
        out.extend(media_nodes)
    adf["content"] = out
    return adf


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="更新 Jira issue 的 description / comment（ADF）")
    ap.add_argument("issue_key")
    ap.add_argument("--description-file", metavar="MD", help="整体替换描述（markdown 文件）")
    ap.add_argument("--append-description-file", metavar="MD", help="在现有描述末尾追加（markdown 文件）")
    ap.add_argument("--comment-file", metavar="MD", help="发一条评论（markdown 文件）")
    ap.add_argument("--keep-media", action="store_true",
                    help="把原描述里的图片节点保留到 <!--MEDIA--> 占位处")
    ap.add_argument("--show-description", action="store_true", help="只打印当前描述（纯文本）")
    ap.add_argument("--out", metavar="FILE",
                    help="配合 --show-description / --dry-run：写入 UTF-8 文件而不是 stdout"
                         "（Windows 控制台编码会把非 ASCII 打乱）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将写入的 ADF，不提交")
    args = ap.parse_args()

    env = load_env()
    if not env.get("JIRA_EMAIL") or not env.get("JIRA_API_TOKEN"):
        print("Missing JIRA_EMAIL / JIRA_API_TOKEN in backend/.env", file=sys.stderr)
        sys.exit(2)

    issue = get_issue(args.issue_key, env)
    cur = issue.get("fields", {}).get("description") or {"type": "doc", "version": 1, "content": []}

    def emit(text: str):
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print(f"written to {args.out}")
        else:
            print(text)

    if args.show_description:
        emit(adf_to_text(cur))
        return

    if args.comment_file:
        md = Path(args.comment_file).read_text(encoding="utf-8")
        adf = resolve_media(md_to_adf(md), collect_media(cur)) if args.keep_media else md_to_adf(md)
        if args.dry_run:
            emit(json.dumps(adf, ensure_ascii=False, indent=2)[:4000])
            return
        status, info = post_comment(args.issue_key, env, adf)
        print(f"comment HTTP {status} id={info}")
        sys.exit(0 if status in (200, 201) else 1)

    if args.description_file:
        md = Path(args.description_file).read_text(encoding="utf-8")
        new = md_to_adf(md)
        if args.keep_media:
            new = resolve_media(new, collect_media(cur))
    elif args.append_description_file:
        md = Path(args.append_description_file).read_text(encoding="utf-8")
        extra = md_to_adf(md)
        merged = dict(cur)
        merged["content"] = list(cur.get("content", [])) + [{"type": "paragraph"}] + extra["content"]
        new = merged
    else:
        ap.print_help()
        sys.exit(1)

    if args.dry_run:
        emit(json.dumps(new, ensure_ascii=False, indent=2)[:6000] + "\n\n--- preview ---\n" + adf_to_text(new))
        return

    status, err = put_fields(args.issue_key, env, {"description": new})
    print(f"PUT description HTTP {status} {err}")
    if status != 204:
        sys.exit(1)

    back = get_issue(args.issue_key, env).get("fields", {}).get("description")
    n_before = len(collect_media(cur))
    n_after = len(collect_media(back))
    print(f"verify: description updated, media nodes {n_before} -> {n_after}")
    if args.keep_media and n_after < n_before:
        print("WARNING: media node lost", file=sys.stderr)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
