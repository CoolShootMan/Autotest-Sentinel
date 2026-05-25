"""
dom_kb.py - DOM Knowledge Base for UI locator self-healing

Builds a FAISS vector index from UI snapshots so that failed test steps
can query the latest page DOM for similar elements.

Usage:
    # Build index from latest snapshot
    python tools/dom_kb.py build --env release --account main

    # Query: find elements similar to a failed locator
    python tools/dom_kb.py query --role button --name "Edit post"

    # Build + query in one shot (for debugging)
    python tools/dom_kb.py search --role button --name "Edit post" --url "{BASE_URL}/autotestshop"
"""

import typing
import json
import os
import sys
import argparse
import pickle

Dict = typing.Dict
List = typing.List
Optional = typing.Optional
Any = typing.Any

KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dom_kb")

# Snapshot loading (reuse from ui_snapshot)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui_snapshot import SNAPSHOT_DIR, load_latest_snapshot


# ---------------------------------------------------------------------------
# Text representation for embedding
# ---------------------------------------------------------------------------

def element_to_text(el: dict, url_template: str = "") -> str:
    """Convert a DOM element dict into a text representation for embedding.

    The text captures everything that makes an element identifiable:
    tag, role, aria-label, testid, visible text, placeholder, and page context.
    """
    parts = []
    if url_template:
        parts.append(f"page:{url_template}")
    tag = el.get("tag", "")
    if tag:
        parts.append(f"tag:{tag}")
    role = el.get("role", "")
    if role:
        parts.append(f"role:{role}")
    testid = el.get("testid", "")
    if testid:
        parts.append(f"testid:{testid}")
    aria = el.get("ariaLabel", "")
    if aria:
        parts.append(f"label:{aria}")
    name = el.get("name", "")
    if name and name != aria:
        parts.append(f"name:{name}")
    text = el.get("text", "")
    if text and text != name and text != aria:
        parts.append(f"text:{text}")
    placeholder = el.get("placeholder", "")
    if placeholder:
        parts.append(f"placeholder:{placeholder}")
    elem_type = el.get("type", "")
    if elem_type and elem_type != tag:
        parts.append(f"type:{elem_type}")
    return " ".join(parts)


def locator_to_text(role: str = "", name: str = "", text: str = "",
                    test_id: str = "", locator: str = "", label: str = "",
                    placeholder: str = "", url_hint: str = "") -> str:
    """Convert a YAML step locator into the same text format for querying."""
    parts = []
    if url_hint:
        parts.append(f"page:{url_hint}")
    if role:
        parts.append(f"role:{role}")
    if test_id:
        parts.append(f"testid:{test_id}")
    if label:
        parts.append(f"label:{label}")
    if name:
        parts.append(f"name:{name}")
    if text:
        parts.append(f"text:{text}")
    if placeholder:
        parts.append(f"placeholder:{placeholder}")
    if locator:
        parts.append(f"locator:{locator}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Embedding helper (local, no API needed)
# ---------------------------------------------------------------------------

_model = None

def get_embedder():
    """Lazy-load sentence-transformers model. Uses a small fast model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        model_name = "all-MiniLM-L6-v2"
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".models")
        if os.path.isdir(os.path.join(cache_dir, model_name)):
            _model = SentenceTransformer(model_name, cache_folder=cache_dir)
        else:
            print(f"[dom_kb] Loading model '{model_name}' (first run downloads ~80MB)...")
            os.makedirs(cache_dir, exist_ok=True)
            _model = SentenceTransformer(model_name, cache_folder=cache_dir)
            print(f"[dom_kb] Model loaded and cached to {cache_dir}")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts into vectors."""
    model = get_embedder()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return [e.tolist() for e in embeddings]


# ---------------------------------------------------------------------------
# FAISS index
# ---------------------------------------------------------------------------

def build_index(elements: List[dict], url_map: Dict[str, str]) -> str:
    """Build FAISS index from snapshot elements.

    Args:
        elements: list of element dicts from snapshot (must have _url_template)
        url_map: dict mapping url_template -> resolved url

    Returns:
        path to the saved index directory
    """
    import numpy as np
    import faiss

    os.makedirs(KB_DIR, exist_ok=True)

    # Deduplicate by (url_template, key) - prefer elements with testid/role
    seen = {}
    for el in elements:
        url_tpl = el.get("_url_template", "")
        key = el.get("key", "")
        dedup_key = f"{url_tpl}||{key}"
        existing = seen.get(dedup_key)
        if existing is None:
            seen[dedup_key] = el
        else:
            score_new = bool(el.get("testid")) + bool(el.get("role")) + bool(el.get("ariaLabel"))
            score_old = bool(existing.get("testid")) + bool(existing.get("role")) + bool(existing.get("ariaLabel"))
            if score_new > score_old:
                seen[dedup_key] = el

    deduped = list(seen.values())
    print(f"[dom_kb] {len(elements)} raw elements -> {len(deduped)} after dedup")

    # Build text representations
    texts = []
    for el in deduped:
        url_tpl = el.get("_url_template", "")
        texts.append(element_to_text(el, url_tpl))

    # Embed
    print(f"[dom_kb] Embedding {len(texts)} elements...")
    embeddings = embed_texts(texts)
    dim = len(embeddings[0])
    vectors = np.array(embeddings, dtype=np.float32)

    # Build FAISS index (Inner Product on normalized vectors = cosine similarity)
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    # Save index
    index_path = os.path.join(KB_DIR, "faiss.index")
    faiss.write_index(index, index_path)

    # Save metadata (aligned with FAISS index order)
    meta = {
        "elements": deduped,
        "texts": texts,
        "dim": dim,
        "url_map": url_map,
        "env": url_map.get("_env", ""),
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }
    meta_path = os.path.join(KB_DIR, "meta.pkl")
    with open(meta_path, "wb") as f:
        pickle.dump(meta, f)

    print(f"[dom_kb] Index saved: {index_path} ({len(deduped)} elements, {dim}d)")
    return KB_DIR


def load_index() -> Optional[tuple]:
    """Load FAISS index and metadata. Returns (index, meta) or None."""
    import faiss
    index_path = os.path.join(KB_DIR, "faiss.index")
    meta_path = os.path.join(KB_DIR, "meta.pkl")
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        return None
    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)
    return index, meta


def query(query_text: str, top_k: int = 5, url_filter: str = "") -> List[dict]:
    """Query the DOM knowledge base.

    Args:
        query_text: text representation of the failed locator
        top_k: number of results to return
        url_filter: if set, only return elements from this URL template

    Returns:
        list of dicts with keys: element, score, url_template
    """
    import numpy as np

    result = load_index()
    if result is None:
        return []
    index, meta = result

    # Embed query
    query_vec = embed_texts([query_text])
    q = np.array(query_vec, dtype=np.float32)

    # Search (over-fetch to allow URL filtering)
    scores, indices = index.search(q, min(top_k * 3, index.ntotal))
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        el = meta["elements"][idx]
        url_tpl = el.get("_url_template", "")

        # URL filter
        if url_filter and url_tpl != url_filter:
            continue

        # Skip low-similarity results
        if score < 0.3:
            continue

        results.append({
            "element": el,
            "score": float(score),
            "url_template": url_tpl,
        })

        if len(results) >= top_k:
            break

    return results


# ---------------------------------------------------------------------------
# Incremental add (for runtime DOM capture during test execution)
# ---------------------------------------------------------------------------

def add_elements(new_elements: List[dict], url_template: str = "") -> bool:
    """Add new DOM elements to the existing FAISS index incrementally.

    This is called by diagnose_failed.py after each step execution to
    capture the current page state into the knowledge base.

    Args:
        new_elements: list of element dicts (same format as snapshot)
        url_template: URL template for context

    Returns:
        True if successfully added, False otherwise
    """
    import numpy as np
    import faiss

    result = load_index()
    if result is None:
        return False
    index, meta = result

    # Tag elements with URL
    elements = []
    for el in new_elements:
        el_copy = dict(el)
        if url_template:
            el_copy["_url_template"] = url_template
        elements.append(el_copy)

    # Deduplicate against existing elements
    existing_keys = set()
    for el in meta["elements"]:
        url_tpl = el.get("_url_template", "")
        key = el.get("key", "")
        existing_keys.add(f"{url_tpl}||{key}")

    new_unique = []
    for el in elements:
        url_tpl = el.get("_url_template", "")
        key = el.get("key", "")
        dedup_key = f"{url_tpl}||{key}"
        if dedup_key not in existing_keys:
            new_unique.append(el)
            existing_keys.add(dedup_key)

    if not new_unique:
        return True  # Nothing new to add

    # Build text representations
    texts = []
    for el in new_unique:
        url_tpl = el.get("_url_template", "")
        texts.append(element_to_text(el, url_tpl))

    # Embed
    embeddings = embed_texts(texts)
    vectors = np.array(embeddings, dtype=np.float32)

    # Add to FAISS index
    index.add(vectors)

    # Update metadata
    meta["elements"].extend(new_unique)
    meta["texts"].extend(texts)
    meta["timestamp"] = __import__("datetime").datetime.now().isoformat()

    # Save updated index and metadata
    index_path = os.path.join(KB_DIR, "faiss.index")
    faiss.write_index(index, index_path)
    meta_path = os.path.join(KB_DIR, "meta.pkl")
    with open(meta_path, "wb") as f:
        pickle.dump(meta, f)

    return True


# ---------------------------------------------------------------------------
# Build from snapshot
# ---------------------------------------------------------------------------

def build_from_snapshot(env: str = "release", account: str = "main",
                        label: str = "baseline") -> str:
    """Load latest snapshot and build FAISS index."""
    result = load_latest_snapshot(label, env)
    if result is None:
        print(f"[dom_kb] No snapshot found for label='{label}', env='{env}'")
        print(f"[dom_kb] Run first: python tools/ui_snapshot.py snapshot --env {env} --account {account} --label {label}")
        return ""

    filepath, data = result
    print(f"[dom_kb] Loading snapshot: {filepath}")

    urls_data = data.get("urls", {})
    base_url = data.get("base_url", "")

    # Flatten all elements with URL context
    all_elements = []
    url_map = {"_env": env}
    for url_tpl, elements in urls_data.items():
        resolved = url_tpl.replace("{BASE_URL}", base_url)
        url_map[url_tpl] = resolved
        for el in elements:
            el_copy = dict(el)
            el_copy["_url_template"] = url_tpl
            el_copy["_resolved_url"] = resolved
            all_elements.append(el_copy)

    print(f"[dom_kb] Total elements across all pages: {len(all_elements)}")
    return build_index(all_elements, url_map)


# ---------------------------------------------------------------------------
# Query helper for diagnose_failed.py integration
# ---------------------------------------------------------------------------

def query_for_failed_step(step_value: dict, url_hint: str = "",
                          top_k: int = 5) -> List[dict]:
    """High-level query interface for diagnose_failed.py.

    Takes a YAML step value dict and returns similar elements from the DOM KB.

    Args:
        step_value: the step's locator dict, e.g. {"role": "button", "name": "Edit post"}
        url_hint: URL template to filter by (optional)
        top_k: max results

    Returns:
        list of dicts with keys: element, score, url_template
    """
    if not isinstance(step_value, dict):
        return []
    q = locator_to_text(
        role=step_value.get("role", ""),
        name=step_value.get("name", "") or step_value.get("text", ""),
        text=step_value.get("text", ""),
        test_id=step_value.get("test_id", ""),
        locator=step_value.get("locator", ""),
        label=step_value.get("label", ""),
        placeholder=step_value.get("placeholder", ""),
        url_hint=url_hint,
    )
    return query(q, top_k=top_k, url_filter=url_hint)


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_build(args):
    label = args.label or "baseline"
    kb_path = build_from_snapshot(env=args.env, account=args.account, label=label)
    if kb_path:
        print(f"\nKnowledge base ready at: {kb_path}")


def cmd_query(args):
    q = locator_to_text(
        role=args.role or "",
        name=args.name or "",
        text=args.text or "",
        test_id=args.test_id or "",
        locator=args.locator or "",
        label=args.label_arg or "",
        placeholder=args.placeholder or "",
        url_hint=args.url or "",
    )
    print(f"[query] {q}\n")

    results = query(q, top_k=args.top_k, url_filter=args.url or "")
    if not results:
        print("No results found. Try building the index first:")
        print("  python tools/dom_kb.py build --env release")
        return

    for i, r in enumerate(results):
        el = r["element"]
        score = r["score"]
        print(f"--- Result {i+1} (score: {score:.3f}) ---")
        print(f"  URL:    {r.get('url_template', '')}")
        print(f"  Tag:    {el.get('tag', '')}")
        print(f"  Role:   {el.get('role', '')}")
        print(f"  Name:   {el.get('name', '')}")
        print(f"  Label:  {el.get('ariaLabel', '')}")
        print(f"  TestID: {el.get('testid', '')}")
        print(f"  Text:   {el.get('text', '')}")
        print()


def main():
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--env", default="release")
    parent.add_argument("--account", default="main")

    parser = argparse.ArgumentParser(description="DOM Knowledge Base for locator self-healing")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Build vector index from snapshot", parents=[parent])
    p_build.add_argument("--label", default="baseline")

    p_query = sub.add_parser("query", help="Query similar elements", parents=[parent])
    p_query.add_argument("--role", default="")
    p_query.add_argument("--name", default="")
    p_query.add_argument("--text", default="")
    p_query.add_argument("--test_id", default="")
    p_query.add_argument("--locator", default="")
    p_query.add_argument("--label_arg", default="", help="aria-label (avoiding clash with --label)")
    p_query.add_argument("--placeholder", default="")
    p_query.add_argument("--url", default="", help="URL template filter")
    p_query.add_argument("--top_k", type=int, default=5)

    args = parser.parse_args()
    if args.command == "build":
        cmd_build(args)
    elif args.command == "query":
        cmd_query(args)


if __name__ == "__main__":
    main()
