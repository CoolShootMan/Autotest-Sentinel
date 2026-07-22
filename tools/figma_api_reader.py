#!/usr/bin/env python3
"""
Figma REST API reader for QA automation.

Given a Figma URL (e.g. https://www.figma.com/design/<file_key>/...?node-id=<node_id>),
this tool:
  1. Fetches the node tree via Figma REST API.
  2. Extracts all TEXT nodes for content analysis.
  3. Optionally downloads PNG screenshots of the target node and its children.

Requires a Figma Personal Access Token with:
  - file_content:read
  - file_metadata:read

Token can be passed via --token or the FIGMA_TOKEN environment variable.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.figma.com/v1"


def load_env() -> dict:
    """Read key=value pairs from backend/.env if present."""
    env = {}
    env_path = Path("backend/.env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def parse_figma_url(url: str) -> tuple[str, str | None]:
    """Extract file_key and optional node_id from a Figma URL."""
    # file key is always the third path segment for /design/... URLs
    m = re.search(r"/design/([a-zA-Z0-9]+)", url)
    if not m:
        raise ValueError(f"Could not parse Figma file key from URL: {url}")
    file_key = m.group(1)

    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    node_id = query.get("node-id", [None])[0]
    return file_key, node_id


def api_request(path: str, token: str, timeout: int = 60, retries: int = 3) -> dict:
    """Make a GET request to the Figma API with simple retry/back-off."""
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers={"X-Figma-Token": token})
    last_error = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:500]
            last_error = RuntimeError(f"Figma API error {e.code}: {body}")
            if e.code == 429 and attempt < retries:
                wait = 2 ** attempt
                print(f"  Rate limited, retrying in {wait}s ...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise last_error from e
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise last_error
    raise last_error or RuntimeError("Unknown API error")


def fetch_node_tree(file_key: str, node_id: str, token: str) -> dict:
    """Fetch the document tree for the given node."""
    return api_request(f"/files/{file_key}/nodes?ids={node_id}", token)


def fetch_images(file_key: str, node_ids: list[str], token: str, scale: int = 2, format: str = "png") -> dict[str, str]:
    """Batch fetch image URLs from the Figma images endpoint."""
    ids = ",".join(node_ids)
    path = f"/images/{file_key}?ids={ids}&format={format}&scale={scale}"
    data = api_request(path, token, timeout=120)
    return data.get("images", {})


def extract_texts(node: dict) -> list[str]:
    """Recursively extract all TEXT node strings."""
    texts = []
    if node.get("type") == "TEXT":
        chars = node.get("characters", "").strip()
        if chars:
            texts.append(chars)
    for child in node.get("children", []):
        texts.extend(extract_texts(child))
    return texts


def collect_text_from_node(node: dict) -> str:
    """Return a single concatenated string of all text inside a node."""
    return " ".join(extract_texts(node))


def extract_annotations(node: dict) -> list[dict]:
    """
    Extract design annotations: STICKY nodes or INSTANCE nodes whose name
    suggests they are annotation/note widgets (e.g. 'Annotation', 'Note').
    Returns list of {id, name, type, text, x, y, width, height}.
    """
    annotations = []
    ntype = node.get("type", "")
    name = node.get("name", "")
    is_annotation = (
        ntype == "STICKY"
        or (ntype == "INSTANCE" and any(k in name.lower() for k in ("annotation", "note", "comment")))
        or (ntype == "FRAME" and any(k in name.lower() for k in ("annotation", "note")))
    )
    if is_annotation:
        bbox = node.get("absoluteBoundingBox", {})
        text = collect_text_from_node(node)
        if text.strip():
            annotations.append({
                "id": node.get("id", ""),
                "name": name,
                "type": ntype,
                "text": text.strip(),
                "x": bbox.get("x"),
                "y": bbox.get("y"),
                "width": bbox.get("width"),
                "height": bbox.get("height"),
            })
    for child in node.get("children", []):
        annotations.extend(extract_annotations(child))
    return annotations


def extract_connectors(node: dict) -> list[dict]:
    """
    Extract CONNECTOR nodes with their start/end endpoint node ids.
    Returns list of {id, name, start_node_id, end_node_id, start_magnet, end_magnet, text}.
    """
    connectors = []
    if node.get("type") == "CONNECTOR":
        start = node.get("connectorStart", {})
        end = node.get("connectorEnd", {})
        connectors.append({
            "id": node.get("id", ""),
            "name": node.get("name", ""),
            "start_node_id": start.get("endpointNodeId"),
            "start_magnet": start.get("magnet"),
            "end_node_id": end.get("endpointNodeId"),
            "end_magnet": end.get("magnet"),
            "text": node.get("characters", "").strip(),
        })
    for child in node.get("children", []):
        connectors.extend(extract_connectors(child))
    return connectors


def is_meaningful_screen_name(name: str) -> bool:
    """Return True if a node name looks like a meaningful screen/section label."""
    if not name or not name.strip():
        return False
    name = name.strip()
    generic = {
        "frame 1", "frame 2", "frame 3", "frame 4", "frame 5",
        "frame 6", "frame 7", "frame 8", "frame 9", "frame",
        "annotation", "annotation block title", "connector line",
        "ellipse", "vector", "rectangle", "line", "group",
        "button", "icon", "arrow", "dot", "handle",
    }
    return name.lower() not in generic and not name.lower().startswith("frame ")


def build_node_index(
    node: dict,
    index: dict | None = None,
    ancestor_screen: str | None = None,
) -> dict:
    """
    Build an id -> {name, type, text_summary, ancestor_screen} lookup table.
    ancestor_screen is the nearest meaningful FRAME/SECTION/INSTANCE/CANVAS name
    above this node, which helps map connector endpoints to the screen they belong to.
    """
    if index is None:
        index = {}
    nid = node.get("id")
    ntype = node.get("type", "")
    name = node.get("name", "")

    # A node can become the new "screen" if it is a container and has a meaningful name.
    next_ancestor = ancestor_screen
    if ntype in ("FRAME", "SECTION", "INSTANCE", "CANVAS") and is_meaningful_screen_name(name):
        next_ancestor = name

    if nid:
        text = collect_text_from_node(node)
        index[nid] = {
            "name": name,
            "type": ntype,
            "text_summary": text[:200] if text else "",
            "ancestor_screen": next_ancestor,
        }
    for child in node.get("children", []):
        build_node_index(child, index, next_ancestor)
    return index


def direct_node_text(node: dict) -> str:
    """Best-effort short text label for a single node (not its whole subtree)."""
    if node.get("type") == "TEXT":
        return node.get("characters", "").strip()
    for child in node.get("children", []):
        if child.get("type") == "TEXT":
            return child.get("characters", "").strip()
    return ""


def resolve_connector_targets(connectors: list[dict], index: dict, raw_root: dict) -> list[dict]:
    """Enrich connector records with readable start/end node descriptions and ancestor screens."""

    def find_node(node: dict, target_id: str):
        if node.get("id") == target_id:
            return node
        for child in node.get("children", []):
            found = find_node(child, target_id)
            if found:
                return found
        return None

    enriched = []
    for c in connectors:
        start = index.get(c["start_node_id"], {})
        end = index.get(c["end_node_id"], {})
        start_raw = find_node(raw_root, c["start_node_id"]) or {}
        end_raw = find_node(raw_root, c["end_node_id"]) or {}

        def describe(n: dict, raw: dict) -> str:
            screen = n.get("ancestor_screen")
            name = n.get("name") or "?"
            summary = (n.get("text_summary") or "").strip()
            direct = direct_node_text(raw)
            is_generic = not is_meaningful_screen_name(name)

            if direct and not is_generic:
                return direct
            if screen and is_generic:
                # Prefer the meaningful ancestor screen for generic endpoints.
                return screen
            if screen and screen != name:
                return f"{screen} / {name}"
            if is_generic and direct:
                return direct
            if is_generic and summary:
                return f"{summary[:60]}{'...' if len(summary) > 60 else ''}"
            return name

        enriched.append({
            **c,
            "start_name": describe(start, start_raw),
            "start_type": start.get("type", "?"),
            "start_screen": start.get("ancestor_screen", ""),
            "start_summary": start.get("text_summary", ""),
            "start_direct": direct_node_text(start_raw),
            "end_name": describe(end, end_raw),
            "end_type": end.get("type", "?"),
            "end_screen": end.get("ancestor_screen", ""),
            "end_summary": end.get("text_summary", ""),
            "end_direct": direct_node_text(end_raw),
        })
    return enriched


def list_screenshot_candidates(node: dict, depth: int = 0, max_depth: int = 2) -> list[dict]:
    """
    Walk the tree and pick FRAME/SECTION/CANVAS nodes worth screenshotting.
    Returns list of {id, name, type, width, height, children_count}.
    """
    candidates = []
    ntype = node.get("type", "")
    if ntype in ("FRAME", "SECTION", "CANVAS", "INSTANCE"):
        bbox = node.get("absoluteBoundingBox", {})
        candidates.append({
            "id": node.get("id", ""),
            "name": node.get("name", ""),
            "type": ntype,
            "width": int(bbox.get("width", 0) or 0),
            "height": int(bbox.get("height", 0) or 0),
            "children_count": len(node.get("children", [])),
        })
    if depth < max_depth:
        for child in node.get("children", []):
            candidates.extend(list_screenshot_candidates(child, depth + 1, max_depth))
    return candidates


def sanitize_filename(name: str) -> str:
    """Make a filesystem-safe filename."""
    name = re.sub(r"[^\w\-_. ]+", "_", name)
    name = re.sub(r"\s+", "_", name).strip("_.")
    return name[:80] or "untitled"


def download_image(url: str, out_path: Path, retries: int = 3) -> None:
    """Download a PNG from a Figma image URL with retry/back-off."""
    last_error = None
    for attempt in range(retries + 1):
        try:
            urllib.request.urlretrieve(url, out_path)
            return
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise last_error


def build_analysis_markdown(
    figma_url: str,
    file_key: str,
    node_id: str,
    root_node: dict,
    texts: list[str],
    candidates: list[dict],
    screenshot_dir: Path,
    annotations: list[dict] | None = None,
    connectors: list[dict] | None = None,
) -> str:
    """Generate a structured analysis markdown document."""
    annotations = annotations or []
    connectors = connectors or []
    lines = [
        "# Figma Analysis",
        "",
        f"- **Source**: {figma_url}",
        f"- **File key**: {file_key}",
        f"- **Node ID**: {node_id}",
        f"- **Root node**: {root_node.get('name', '?')} ({root_node.get('type', '?')})",
        f"- **Screenshots**: {len(candidates)} PNGs saved to `{screenshot_dir}`",
        f"- **Annotations**: {len(annotations)} design notes extracted",
        f"- **Connectors**: {len(connectors)} flow arrows extracted",
        "",
        "## All Text Elements",
        "",
    ]
    seen = set()
    for t in texts:
        if t not in seen:
            seen.add(t)
            lines.append(f"- {t}")
    lines.append("")

    if annotations:
        lines.append("## Design Annotations (Notes / Sticky / Comment widgets)")
        lines.append("")
        lines.append("| Type | Name | Text | Position |")
        lines.append("|------|------|------|----------|")
        for a in annotations:
            pos = f"({a.get('x')}, {a.get('y')}) {a.get('width')}x{a.get('height')}"
            name = a.get("name", "").replace("|", "\\|")
            text = a.get("text", "").replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {a.get('type')} | {name} | {text} | {pos} |")
        lines.append("")

    if connectors:
        lines.append("## Flow Connectors")
        lines.append("")
        lines.append("These arrows show screen-to-screen or element-to-element relationships in the design.")
        lines.append("")
        lines.append("| Start | -> | End | Connector Text |")
        lines.append("|-------|----|-----|----------------|")
        for c in connectors:
            start = c.get("start_name", c["start_node_id"]).replace("|", "\\|")[:80]
            end = c.get("end_name", c["end_node_id"]).replace("|", "\\|")[:80]
            text = (c.get("text") or "").replace("|", "\\|") or "—"
            lines.append(f"| {start} | -> | {end} | {text} |")
            start_direct = (c.get("start_direct") or "").replace("|", "\\|").replace("\n", " ")[:80]
            end_direct = (c.get("end_direct") or "").replace("|", "\\|").replace("\n", " ")[:80]
            if start_direct or end_direct:
                summary = " → ".join(filter(None, [start_direct, end_direct])) or "—"
                lines.append(f"| | | | _{summary}_ |")
        lines.append("")

    lines.append("## Screenshot Index")
    lines.append("")
    lines.append("| File | Name | Type | Size | Children |")
    lines.append("|------|------|------|------|----------|")
    for c in candidates:
        safe_name = sanitize_filename(c["name"])
        fname = f"{safe_name}_{c['id'].replace(':', '-')}.png"
        lines.append(
            f"| `{fname}` | {c['name']} | {c['type']} | "
            f"{c['width']}x{c['height']} | {c['children_count']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read and screenshot a Figma design via REST API.")
    parser.add_argument("--url", "-u", required=True, help="Figma URL with optional node-id.")
    parser.add_argument("--token", "-t", help="Figma personal access token (or env FIGMA_TOKEN).")
    parser.add_argument("--output", "-o", default="data/figma_output", help="Output directory.")
    parser.add_argument("--scale", type=int, default=2, help="Image scale (1 or 2).")
    parser.add_argument("--depth", type=int, default=2, help="How deep to screenshot child nodes.")
    parser.add_argument("--max-images", type=int, default=40, help="Max screenshots to download.")
    parser.add_argument("--analyze", action="store_true", help="Generate analysis markdown.")
    parser.add_argument("--no-images", action="store_true", help="Skip image download; only fetch node tree and text.")
    args = parser.parse_args()

    env = load_env()
    token = args.token or env.get("FIGMA_TOKEN") or os.environ.get("FIGMA_TOKEN")
    if not token:
        print("ERROR: Figma token required. Pass --token or set FIGMA_TOKEN in backend/.env.", file=sys.stderr)
        return 1

    file_key, node_id = parse_figma_url(args.url)
    if not node_id:
        print("WARNING: No node-id in URL; falling back to the file's top-level canvas.", file=sys.stderr)
        node_id = "0:1"

    print(f"Fetching Figma node tree for {file_key} / {node_id} ...")
    data = fetch_node_tree(file_key, node_id, token)
    # Figma API may return node keys with colons even if the URL used hyphens.
    colon_id = node_id.replace("-", ":")
    root = data["nodes"].get(node_id, data["nodes"].get(colon_id, {})).get("document")
    if not root:
        available = list(data.get("nodes", {}).keys())[:5]
        print(f"ERROR: Node {node_id} not found. Available keys: {available}", file=sys.stderr)
        return 1

    texts = extract_texts(root)
    print(f"Extracted {len(texts)} text elements ({len(set(texts))} unique).")

    annotations = extract_annotations(root)
    connectors = extract_connectors(root)
    node_index = build_node_index(root)
    resolved_connectors = resolve_connector_targets(connectors, node_index, root)
    if annotations:
        print(f"Extracted {len(annotations)} design annotations.")
    if resolved_connectors:
        print(f"Extracted {len(resolved_connectors)} connectors.")

    output_dir = Path(args.output)
    screenshot_dir = output_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    if not args.no_images:
        candidates = list_screenshot_candidates(root, max_depth=args.depth)
        # Prefer larger, more meaningful frames; drop tiny ones.
        candidates = [c for c in candidates if c["width"] >= 50 and c["height"] >= 50]
        candidates = candidates[:args.max_images]
        print(f"Preparing to download {len(candidates)} screenshots ...")

        if candidates:
            node_ids = [c["id"] for c in candidates]
            image_map = fetch_images(file_key, node_ids, token, scale=args.scale)
            for c in candidates:
                img_url = image_map.get(c["id"])
                if not img_url:
                    print(f"  SKIP {c['name']}: no render URL returned")
                    continue
                safe_name = sanitize_filename(c["name"])
                fname = f"{safe_name}_{c['id'].replace(':', '-')}.png"
                out_path = screenshot_dir / fname
                try:
                    download_image(img_url, out_path)
                    print(f"  OK {fname} ({c['width']}x{c['height']})")
                except Exception as e:
                    print(f"  FAIL {fname}: {e}")
                time.sleep(0.1)
        else:
            print("No screenshot candidates found.")
    else:
        candidates = []

    if args.analyze:
        md = build_analysis_markdown(
            figma_url=args.url,
            file_key=file_key,
            node_id=node_id,
            root_node=root,
            texts=texts,
            candidates=candidates,
            screenshot_dir=screenshot_dir.relative_to(output_dir) if output_dir.is_absolute() else screenshot_dir,
            annotations=annotations,
            connectors=resolved_connectors,
        )
        analysis_path = output_dir / "analysis.md"
        analysis_path.write_text(md, encoding="utf-8")
        print(f"Analysis written to {analysis_path}")

    # Always save raw node tree for later inspection.
    raw_path = output_dir / "nodes_raw.json"
    raw_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Raw node tree written to {raw_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
