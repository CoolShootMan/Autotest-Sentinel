"""
Build a case index by scanning the tests/ directory — no Apifox dependency.

Each test module *may* declare module-level metadata near the top:

    NAME     = "Human readable case name"
    TAGS     = ["p0", "catalog", "suite:linda"]
    PRIORITY = 0
    CASE_ID  = 6080068   # original Apifox id, kept only for traceability

When those are absent (legacy migrated files), the index falls back to the
header comments written by the converter:
    # Apifox Case ID: 6080068
    # Case: (Linda)T1353 Verify new product can be created successfully
    # Priority: P0

Scanning uses the `ast` module only (no import of the test modules), so it is
safe (no requests/db side effects) and fast.
"""
from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
TESTS_DIR = ROOT / "tests"

ID_IN_NAME_RE = re.compile(r"^test__(\d+)__(.+)$")
HEADER_CASE_RE = re.compile(r"^#\s*Case:\s*(.+)$", re.M)
HEADER_PRI_RE = re.compile(r"^#\s*Priority:\s*P?(\d+)", re.M)
HEADER_ID_RE = re.compile(r"^#\s*Apifox Case ID:\s*(\d+)", re.M)


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")


def _literal_assign(tree: ast.Module) -> dict:
    """Pull simple module-level assignments (NAME/TAGS/PRIORITY/CASE_ID)."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            tgt = node.targets[0]
            if isinstance(tgt, ast.Name):
                try:
                    val = ast.literal_eval(node.value)
                except Exception:
                    continue
                if tgt.id in ("NAME", "CASE_ID", "PRIORITY") and val is not None:
                    out[tgt.id] = val
                elif tgt.id == "TAGS" and isinstance(val, (list, tuple)):
                    out["TAGS"] = [str(x) for x in val]
    return out


def _parse_headers(src: str) -> dict:
    out = {}
    m = HEADER_CASE_RE.search(src)
    if m:
        # strip a leading "(Author)T1234 " style prefix for the readable name
        name = re.sub(r"^\([^)]*\)\s*T?\d+\s*", "", m.group(1)).strip()
        out["name"] = name or m.group(1).strip()
    m = HEADER_PRI_RE.search(src)
    if m:
        out["priority"] = int(m.group(1))
    m = HEADER_ID_RE.search(src)
    if m:
        out["case_id"] = int(m.group(1))
    return out


def _module_entry(path: Path) -> dict:
    rel = path.relative_to(ROOT)
    parts = list(path.with_suffix("").relative_to(TESTS_DIR).parts)
    folder = "/".join(parts[:-1])          # e.g. "Catalog and Product"
    module = parts[-1]                     # e.g. "test__6080068__Linda_T1353_..."
    src = path.read_text(encoding="utf-8")

    # find the test function name
    func = None
    try:
        tree = ast.parse(src)
        assigns = _literal_assign(tree)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
                func = node.name
                break
    except SyntaxError:
        assigns = {}
        func = None

    hdr = _parse_headers(src)
    name = assigns.get("NAME") or hdr.get("name") or module
    case_id = assigns.get("CASE_ID") or hdr.get("case_id")
    priority = assigns.get("PRIORITY")
    if priority is None:
        priority = hdr.get("priority")
    tags = list(assigns.get("TAGS") or [])

    # derived default tags (so suites can use tags before explicit TAGS exist)
    derived = []
    if priority is not None:
        derived.append(f"p{priority}")
    if folder:
        derived.append(slug(folder))
    for t in tags:
        if t not in derived:
            derived.append(t)

    slug_name = module
    m = ID_IN_NAME_RE.match(module)
    if m:
        slug_name = m.group(2)

    return {
        "path": str(rel),
        "folder": folder,
        "module": module,
        "func": func,
        "name": name,
        "case_id": case_id,
        "priority": priority,
        "tags": derived,
        "explicit_tags": tags,
        "slug": slug_name,
    }


def _load_apifox_order():
    """Read Apifox scenario_tree.json and return exact folder/case ordering.

    Only the tree under "QA automation testing/Runable" is used. This is an
    optional traceability file — if it is missing, scan_tests() falls back to
    filesystem order.
    Returns:
        folder_rank_by_path: dict[str, list[int]]   # e.g. {"Login flow": [0]}
        case_order_by_id:  dict[int, int]           # Apifox scenario id -> folder-local index
    """
    tree_path = ROOT / "_apifox_export" / "scenario_tree.json"
    if not tree_path.exists():
        return {}, {}

    try:
        data = json.loads(tree_path.read_text())
    except Exception:
        return {}, {}

    folders = data.get("data", {}).get("testScenarioFolders", [])
    scenarios = data.get("data", {}).get("testScenarios", [])
    fid2f = {f["id"]: f for f in folders}

    qa = next((f for f in folders if f.get("name") == "QA automation testing"), None)
    if qa is None:
        return {}, {}
    runable = next((f for f in folders
                    if f.get("name") == "Runable" and f.get("parentId") == qa["id"]), None)
    if runable is None:
        return {}, {}
    runable_id = runable["id"]

    children = defaultdict(list)
    for f in folders:
        children[f.get("parentId")].append(f)
    for pid in children:
        children[pid].sort(key=lambda f: (f.get("ordering") or 0, f["id"]))

    def is_under_runable(fid):
        while fid:
            if fid == runable_id:
                return True
            f = fid2f.get(fid)
            if not f:
                break
            fid = f.get("parentId")
        return False

    def folder_path(fid):
        parts = []
        while fid and fid != runable_id:
            f = fid2f.get(fid)
            if not f:
                break
            parts.append(f["name"])
            fid = f.get("parentId")
        return "/".join(reversed(parts))

    def sibling_index(fid):
        f = fid2f[fid]
        sibs = children.get(f.get("parentId"), [])
        for i, s in enumerate(sibs):
            if s["id"] == fid:
                return i
        return 999

    def rank(fid):
        r = []
        while fid and fid != runable_id:
            r.append(sibling_index(fid))
            fid = fid2f[fid].get("parentId")
        return list(reversed(r))

    folder_rank_by_path = {}
    for f in folders:
        if is_under_runable(f["id"]):
            fp = folder_path(f["id"])
            folder_rank_by_path[fp] = rank(f["id"])

    folder_scenarios = defaultdict(list)
    for s in scenarios:
        if s.get("folderId") and is_under_runable(s["folderId"]):
            folder_scenarios[s["folderId"]].append(s)
    for fid in folder_scenarios:
        folder_scenarios[fid].sort(key=lambda s: (s.get("ordering") or 0, s["id"]))

    case_order_by_id = {}
    for lst in folder_scenarios.values():
        for i, s in enumerate(lst):
            case_order_by_id[s["id"]] = i

    return folder_rank_by_path, case_order_by_id


_FOLDER_RANK_BY_PATH, _CASE_ORDER_BY_ID = _load_apifox_order()


def scan_tests(tests_dir: Path | None = None) -> list:
    """Return a list of case entries scanned from tests/, ordered like Apifox."""
    base = TESTS_DIR if tests_dir is None else Path(tests_dir)
    entries = []
    for p in sorted(base.rglob("test_*.py")):
        if p.name == "test___init__.py" or p.name.startswith("__"):
            continue
        try:
            entries.append(_module_entry(p))
        except Exception:
            continue

    # attach Apifox folder/case ordering when the exported tree is available
    fallback_fpos = {}
    for e in entries:
        f = e["folder"]
        if f not in _FOLDER_RANK_BY_PATH and f not in fallback_fpos:
            fallback_fpos[f] = len(fallback_fpos) + 10000

    local: dict[str, int] = {}
    _num_prefix = re.compile(r"^\d+_(.*)$")

    def _strip_prefix(folder: str) -> str:
        m = _num_prefix.match(folder)
        return m.group(1) if m else folder

    for e in entries:
        f = e["folder"]
        folder_rank = (_FOLDER_RANK_BY_PATH.get(f)
                       or _FOLDER_RANK_BY_PATH.get(f.rstrip())
                       or _FOLDER_RANK_BY_PATH.get(_strip_prefix(f))
                       or _FOLDER_RANK_BY_PATH.get(_strip_prefix(f).rstrip()))
        if folder_rank is None:
            folder_rank = [fallback_fpos.get(f, 99999)]
        case_order = _CASE_ORDER_BY_ID.get(e.get("case_id")) if e.get("case_id") is not None else None
        if case_order is None:
            case_order = local.get(f, 0)
            local[f] = case_order + 1
        e["folder_rank"] = folder_rank
        e["case_order"] = case_order
        e["case_sort_key"] = folder_rank + [case_order]

    entries.sort(key=lambda e: (e.get("case_sort_key", [99999]), e["name"]))
    return entries


def index_by_id(entries: list | None = None) -> dict:
    if entries is None:
        entries = scan_tests()
    return {e["case_id"]: e for e in entries if e["case_id"] is not None}


if __name__ == "__main__":
    es = scan_tests()
    print(f"scanned {len(es)} case files")
    for e in es[:5]:
        print(f"  [{e['folder']}] {e['name'][:50]}  tags={e['tags']}")
