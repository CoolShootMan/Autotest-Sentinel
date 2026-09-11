"""
Run a curated test suite defined in YAML/JSON — pure script-driven, no Apifox
runtime dependency. Cases are discovered by scanning tests/ (see case_index.py).

Usage
-----
    python run_suite.py suites/smoke.yaml              # run it
    python run_suite.py suites/smoke.yaml --dry-run    # just show what would run
    python run_suite.py --list                         # list available suite files

Suite file format (YAML or JSON)
--------------------------------
    name: smoke
    description: 登录 + 只读查询冒烟
    include:
      folders:            # case folder path contains any of these (readable!)
        - Login flow
        - Analytics
      tags:               # case must carry ALL of these tags
        - p0
        - suite:linda
      markers:            # pytest marker, e.g. p0 / folder_login_flow
        - p0
      names:              # list every case by its human-readable NAME, one per line.
                          # Best for curated suites: you see exactly which cases are
                          # included at a glance, and add/remove is a simple edit.
        - Verify the consumer can follow a shop
        - Create a guest account
      case_ids:           # legacy Apifox ids or func slugs (kept for compat)
        - 6112669
    exclude:
      folders:
        - Release schedule
      tags:
        - dangerous
      case_ids:
        - 8604667
    pytest_args:          # extra raw args passed to pytest
      - "-v"

Selection semantics: a case runs if it matches ANY include rule
(folder OR tag OR marker OR case_id). Exclude always wins.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Always run pytest with the managed venv python (OpenSSL 3.x) to avoid the
# system python's LibreSSL SSL handshake failures against the API.
_MANAGED = Path("/Users/a123456/.workbuddy/binaries/python/envs/default/bin/python")

# This framework needs Python >= 3.10 (PEP 604 unions, pytest 9). macOS ships
# /usr/bin/python3 = 3.9, and a bare `python run_suite.py` often resolves to it,
# which crashes at import time with a cryptic
# "unsupported operand type(s) for |: 'type' and 'NoneType'".
# Re-exec under the managed interpreter so the command just works either way.
if sys.version_info < (3, 10) and _MANAGED.exists():
    os.execv(
        str(_MANAGED),
        [str(_MANAGED), str(Path(__file__).resolve()), *sys.argv[1:]],
    )
if sys.version_info < (3, 10):
    sys.exit(
        f"需要 Python >= 3.10（当前 {sys.version.split()[0]}）。"
        f"请用 {_MANAGED} 运行，或先安装 Python 3.10+。"
    )

import case_index as ci  # noqa: E402

ROOT = Path(__file__).parent
SUITES_DIR = ROOT / "suites"

PYTEST = str(_MANAGED) if _MANAGED.exists() else sys.executable


def _load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".json",):
        return json.loads(text)
    import yaml  # noqa
    return yaml.safe_load(text) or {}


def select_cases(suite: dict, entries: list) -> list:
    inc = suite.get("include") or {}
    exc = suite.get("exclude") or {}

    inc_folders = [f.lower() for f in (inc.get("folders") or [])]
    inc_tags = [t.lower() for t in (inc.get("tags") or [])]
    inc_markers = [m.lower() for m in (inc.get("markers") or [])]
    inc_ids = {str(i).strip() for i in (inc.get("case_ids") or [])}
    inc_names = {n.strip().lower() for n in (inc.get("names") or [])}

    exc_folders = [f.lower() for f in (exc.get("folders") or [])]
    exc_tags = [t.lower() for t in (exc.get("tags") or [])]
    exc_ids = {str(i).strip() for i in (exc.get("case_ids") or [])}

    # resolve marker expressions -> func names / ids
    marker_funcs = set()
    for m in inc_markers:
        if m.startswith("case_"):
            marker_funcs.add(m[5:])
        elif m.startswith("p") and m[1:].isdigit():
            marker_funcs |= {e["func"] for e in entries if e.get("priority") == int(m[1:])}
        elif m.startswith("folder_"):
            slug = m[7:]
            marker_funcs |= {e["func"] for e in entries if e["folder"] and ci.slug(e["folder"]) == slug}

    selected = []
    for e in entries:
        folder = (e.get("folder") or "").lower()
        tags = [t.lower() for t in (e.get("tags") or [])]
        cid = str(e.get("case_id") or "")
        func = e.get("func") or ""
        name_l = (e.get("name") or "").lower()

        included = (
            any(f in folder for f in inc_folders)
            or (inc_tags and all(t in tags for t in inc_tags))
            or func in marker_funcs
            or cid in marker_funcs
            or (inc_ids and (cid in inc_ids or func in inc_ids))
            or (inc_names and name_l in inc_names)
        )
        if not included:
            continue
        if (any(f in folder for f in exc_folders)
                or (exc_tags and all(t in tags for t in exc_tags))
                or cid in exc_ids or func in exc_ids):
            continue
        selected.append(e)
    return selected


def main():
    ap = argparse.ArgumentParser(description="Run a script-defined test suite")
    ap.add_argument("suite", nargs="?", help="suite file (yaml/json) under suites/")
    ap.add_argument("--list", action="store_true", help="list available suites")
    ap.add_argument("--dry-run", action="store_true", help="show selected cases, do not run")
    ap.add_argument("--collect", action="store_true", help="hand off to pytest --collect-only")
    args = ap.parse_args()

    if args.list or not args.suite:
        if not SUITES_DIR.exists():
            print(f"No suites dir yet: {SUITES_DIR}")
            return
        for f in sorted(SUITES_DIR.glob("*.y*ml")) + sorted(SUITES_DIR.glob("*.json")):
            if f.name.startswith("field") or f.suffix == ".json" and f.name != "suites.json":
                continue
            try:
                s = _load_yaml(f)
                print(f"  {f.name:30} {s.get('name',''):22} {s.get('description','')}")
            except Exception as e:
                print(f"  {f.name:30} <parse error: {e}>")
        print(f"\nUsage: python {Path(__file__).name} suites/<file>.yaml [--dry-run]")
        return

    suite_path = Path(args.suite)
    if not suite_path.is_absolute():
        suite_path = SUITES_DIR / suite_path if not suite_path.exists() else suite_path

    suite = _load_yaml(suite_path)
    entries = ci.scan_tests()
    cases = select_cases(suite, entries)

    print(f"Suite : {suite.get('name', suite_path.stem)}")
    print(f"Desc  : {suite.get('description', '')}")
    print(f"Cases : {len(cases)} selected\n")

    # warn about include.names entries that matched no case (typo / removed case)
    inc = suite.get("include") or {}
    inc_names = [n.strip() for n in (inc.get("names") or [])]
    if inc_names:
        matched_names = {e.get("name", "").lower() for e in cases}
        for n in inc_names:
            if n.lower() not in matched_names:
                print(f"  [WARN] include.names 未匹配到用例: {n!r}")

    if args.dry_run:
        for e in cases:
            print(f"  {e.get('folder','-'):<42} {e.get('name','')[:60]}")
        print(f"\n{len(cases)} case(s) — nothing executed (--dry-run)")
        return

    if not cases:
        print("No cases matched. Check your include/exclude rules.")
        return

    # Hand the selected func names to pytest (works with or without case_id).
    funcs = [e["func"] for e in cases if e.get("func")]
    label = str(suite.get("name") or suite_path.stem)
    cmd = [PYTEST, "-m", "pytest", "tests/", "--case-ids", ",".join(funcs),
           "--run-label", label]
    cmd += list(suite.get("pytest_args") or [])
    if args.collect:
        cmd.append("--collect-only")

    print("Running:", " ".join(cmd), "\n")
    print("Report  : results/runs/<timestamp>_%s/  (summary.md / junit.xml / http.log)\n"
          % label.strip().lower().replace(" ", "-"))
    sys.exit(subprocess.call(cmd, cwd=str(ROOT)))


if __name__ == "__main__":
    main()
