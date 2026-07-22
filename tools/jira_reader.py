#!/usr/bin/env python3
"""
Jira Reader Tool — Fetches and distills Jira ticket data via REST API.

Usage:
    python tools/jira_reader.py KAT-11397
    python tools/jira_reader.py KAT-11397 --format text
    python tools/jira_reader.py KAT-11397 --comments-only

Credentials are read from backend/.env:
    JIRA_EMAIL=...
    JIRA_API_TOKEN=...
    JIRA_BASE_URL=https://your-domain.atlassian.net

Output: Clean JSON (default) or human-readable text with key fields + comments.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# --- Config ---

def load_env(env_path: Path) -> dict:
    """Load .env file into a dict (simple parser, no external deps)."""
    env = {}
    if not env_path.exists():
        return env
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


# --- ADF Parser (Atlassian Document Format → plain text) ---

def parse_adf(node, indent=0) -> str:
    """Recursively convert Atlassian Document Format JSON to plain text."""
    if not node or not isinstance(node, dict):
        return ""

    node_type = node.get("type", "")
    content = node.get("content", [])
    prefix = "  " * indent

    if node_type == "text":
        text = node.get("text", "")
        # Extract link URLs from marks (ADF stores hyperlinks in marks, not in text)
        marks = node.get("marks", [])
        for mark in marks:
            if mark.get("type") == "link":
                href = mark.get("attrs", {}).get("href", "")
                if href and href not in text:
                    text = f"{text}({href})"
        return text

    if node_type == "inlineCard":
        url = node.get("attrs", {}).get("url", "")
        return f" {url} " if url else ""

    if node_type == "doc":
        return "\n".join(parse_adf(c, indent) for c in content)

    if node_type == "paragraph":
        text = "".join(parse_adf(c, indent) for c in content)
        return text  # caller adds newline

    if node_type == "heading":
        level = node.get("attrs", {}).get("level", 1)
        text = "".join(parse_adf(c, indent) for c in content)
        return f"{'#' * level} {text}"

    if node_type == "bulletList":
        lines = []
        for item in content:
            text = parse_adf(item, indent)
            lines.append(f"{prefix}- {text}")
        return "\n".join(lines)

    if node_type == "orderedList":
        lines = []
        for i, item in enumerate(content, 1):
            text = parse_adf(item, indent)
            lines.append(f"{prefix}{i}. {text}")
        return "\n".join(lines)

    if node_type == "listItem":
        return "\n".join(parse_adf(c, indent) for c in content)

    if node_type == "codeBlock":
        text = "".join(parse_adf(c, indent) for c in content)
        return f"```\n{text}\n```"

    if node_type == "blockquote":
        text = "\n".join(parse_adf(c, indent) for c in content)
        return "\n".join(f"{prefix}> {line}" for line in text.splitlines())

    if node_type == "table":
        rows = []
        for row in content:
            cells = []
            for cell in row.get("content", []):
                cell_text = "".join(parse_adf(c, indent) for c in cell.get("content", []))
                cells.append(cell_text.strip())
            rows.append(" | ".join(cells))
        return "\n".join(rows)

    if node_type == "tableRow" or node_type == "tableHeader" or node_type == "tableCell":
        return "\n".join(parse_adf(c, indent) for c in content)

    # Fallback: recurse into content
    if content:
        return "\n".join(parse_adf(c, indent) for c in content)

    return ""


# --- Jira API ---

def fetch_issue(base_url: str, email: str, token: str, issue_key: str) -> dict:
    """Fetch a Jira issue via REST API v3."""
    # Only request the fields we care about (reduces payload from ~50KB to ~5KB)
    fields = ",".join([
        "summary", "status", "priority", "issuetype", "assignee", "reporter",
        "labels", "parent", "description", "comment", "issuelinks",
        "subtasks", "fixVersions", "components", "created", "updated",
        "duedate", "environment", "attachment", "customfield_10083", "customfield_10090",
    ])
    url = f"{base_url}/rest/api/3/issue/{issue_key}?fields={fields}"

    import base64
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body[:500]}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)


def distill_issue(raw: dict) -> dict:
    """Extract only the useful fields from raw API response."""
    f = raw.get("fields", {})

    # Parse description from ADF to plain text
    desc_raw = f.get("description")
    description = parse_adf(desc_raw) if desc_raw else ""

    # Parse comments from ADF to plain text
    comments_raw = f.get("comment", {}).get("comments", [])
    comments = []
    for c in comments_raw:
        body_raw = c.get("body")
        body_text = parse_adf(body_raw) if body_raw else str(body_raw)
        comments.append({
            "author": c.get("author", {}).get("displayName", "Unknown"),
            "created": c.get("created", ""),
            "updated": c.get("updated", ""),
            "body": body_text,
        })

    # Issue links
    links = []
    for link in f.get("issuelinks", []):
        link_type = link.get("type", {})
        if "outwardIssue" in link:
            links.append({
                "type": link_type.get("outward", "relates to"),
                "issue": link["outwardIssue"]["key"],
                "summary": link["outwardIssue"].get("fields", {}).get("summary", ""),
                "status": link["outwardIssue"].get("fields", {}).get("status", {}).get("name", ""),
            })
        elif "inwardIssue" in link:
            links.append({
                "type": link_type.get("inward", "relates to"),
                "issue": link["inwardIssue"]["key"],
                "summary": link["inwardIssue"].get("fields", {}).get("summary", ""),
                "status": link["inwardIssue"].get("fields", {}).get("status", {}).get("name", ""),
            })

    # Subtasks
    subtasks = []
    for st in f.get("subtasks", []):
        subtasks.append({
            "key": st.get("key", ""),
            "summary": st.get("fields", {}).get("summary", ""),
            "status": st.get("fields", {}).get("status", {}).get("name", ""),
        })

    # Attachments (just names + URLs, don't download)
    attachments = []
    for att in f.get("attachment", []):
        attachments.append({
            "filename": att.get("filename", ""),
            "url": att.get("content", ""),
            "mime_type": att.get("mimeType", ""),
            "created": att.get("created", ""),
        })

    # QA assignee (custom field)
    qa_raw = f.get("customfield_10083")
    qa = []
    if isinstance(qa_raw, list):
        qa = [u.get("displayName", "") for u in qa_raw if isinstance(u, dict)]

    return {
        "key": raw.get("key", ""),
        "summary": f.get("summary", ""),
        "status": f.get("status", {}).get("name", ""),
        "priority": f.get("priority", {}).get("name", ""),
        "type": f.get("issuetype", {}).get("name", ""),
        "assignee": f.get("assignee", {}).get("displayName", "Unassigned") if f.get("assignee") else "Unassigned",
        "reporter": f.get("reporter", {}).get("displayName", "Unknown") if f.get("reporter") else "Unknown",
        "qa": qa,
        "labels": f.get("labels", []),
        "parent": {
            "key": f.get("parent", {}).get("key", ""),
            "summary": f.get("parent", {}).get("fields", {}).get("summary", ""),
        } if f.get("parent") else None,
        "description": description,
        "comments": comments,
        "issue_links": links,
        "subtasks": subtasks,
        "fix_versions": [v.get("name", "") for v in f.get("fixVersions", [])],
        "components": [c.get("name", "") for c in f.get("components", [])],
        "created": f.get("created", ""),
        "updated": f.get("updated", ""),
        "attachments": attachments,
    }


# --- Output Formatters ---

def to_text(issue: dict) -> str:
    """Human-readable text output."""
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"{issue['key']}: {issue['summary']}")
    lines.append(f"{'='*60}")
    lines.append(f"Status:    {issue['status']}")
    lines.append(f"Priority:  {issue['priority']}")
    lines.append(f"Type:      {issue['type']}")
    lines.append(f"Assignee:  {issue['assignee']}")
    lines.append(f"QA:        {', '.join(issue['qa']) if issue.get('qa') else 'N/A'}")
    lines.append(f"Reporter:  {issue['reporter']}")
    if issue.get("labels"):
        lines.append(f"Labels:    {', '.join(issue['labels'])}")
    if issue.get("parent"):
        lines.append(f"Parent:    {issue['parent']['key']} - {issue['parent']['summary']}")
    if issue.get("components"):
        lines.append(f"Components: {', '.join(issue['components'])}")
    if issue.get("fix_versions"):
        lines.append(f"Fix Versions: {', '.join(issue['fix_versions'])}")
    lines.append("")

    if issue["description"]:
        lines.append("--- Description ---")
        lines.append(issue["description"])
        lines.append("")

    if issue["comments"]:
        lines.append(f"--- Comments ({len(issue['comments'])}) ---")
        for c in issue["comments"]:
            lines.append(f"[{c['created'][:10]}] {c['author']}:")
            lines.append(f"  {c['body']}")
            lines.append("")

    if issue["issue_links"]:
        lines.append("--- Linked Issues ---")
        for link in issue["issue_links"]:
            lines.append(f"  {link['type']}: {link['issue']} - {link['summary']} ({link['status']})")
        lines.append("")

    if issue["subtasks"]:
        lines.append("--- Subtasks ---")
        for st in issue["subtasks"]:
            lines.append(f"  {st['key']}: {st['summary']} ({st['status']})")
        lines.append("")

    if issue["attachments"]:
        lines.append("--- Attachments ---")
        for att in issue["attachments"]:
            lines.append(f"  {att['filename']} ({att['mime_type']})")
        lines.append("")

    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Fetch and distill Jira ticket data")
    parser.add_argument("issue_key", help="Jira issue key (e.g. KAT-11397)")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--comments-only", action="store_true",
                        help="Only output comments")
    parser.add_argument("--env", default=None,
                        help="Path to .env file (default: backend/.env)")
    args = parser.parse_args()

    # Load credentials
    env_path = Path(args.env) if args.env else Path(__file__).parent.parent / "backend" / ".env"
    env = load_env(env_path)

    email = env.get("JIRA_EMAIL")
    token = env.get("JIRA_API_TOKEN")
    base_url = env.get("JIRA_BASE_URL")

    if not all([email, token, base_url]):
        print(f"Error: Missing Jira credentials in {env_path}", file=sys.stderr)
        print("Required: JIRA_EMAIL, JIRA_API_TOKEN, JIRA_BASE_URL", file=sys.stderr)
        sys.exit(1)

    # Fetch and distill
    raw = fetch_issue(base_url, email, token, args.issue_key)
    issue = distill_issue(raw)

    # Output
    if args.comments_only:
        if args.format == "json":
            print(json.dumps(issue["comments"], indent=2, ensure_ascii=False))
        else:
            for c in issue["comments"]:
                print(f"[{c['created'][:10]}] {c['author']}:")
                print(f"  {c['body']}")
                print()
    else:
        if args.format == "json":
            print(json.dumps(issue, indent=2, ensure_ascii=False))
        else:
            print(to_text(issue))


if __name__ == "__main__":
    main()
