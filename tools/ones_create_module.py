#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create an ONES testcase (sub-)module via REST.

ONES exposes no documented module-creation API and `items/add` with
`item_type=testcase_module` returns 500 -- but the dedicated endpoint below
works and is what the web UI itself uses:

    POST {ONES_URL}/project/api/project/team/{team}/testcase/library/{lib}/modules/add
    body = {"module": {"name": ..., "parent_uuid": ..., "library_uuid": ...}}

Note the body MUST be wrapped in a top-level `module` key; the flat
`{"name": ..., "parent_uuid": ...}` shape returns HTTP 500.  Discovered
2026-09-18 while onboarding KAT-12117.

Usage
-----
    py -3.9 tools/ones_create_module.py --name "Contact email" --parent MbFknFcK
    py -3.9 tools/ones_create_module.py --name "Contact email" --parent MbFknFcK --dry-run

Prints the new module UUID on success.  Verifies the module actually appears
in the module tree (GraphQL) before reporting success.

Exit codes: 0 ok, 1 create failed, 2 verification failed, 3 module already exists.
"""
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from ones_writer import api_call, get_modules, load_env  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="module name (English)")
    ap.add_argument("--parent", required=True, help="parent module UUID")
    ap.add_argument("--dry-run", action="store_true", help="only check for an existing same-name sibling")
    args = ap.parse_args()

    env = load_env()
    team = env["ONES_TEAM_UUID"]
    lib = env["ONES_LIBRARY_UUID"]

    mods = get_modules(env)
    if not mods:
        print("[module] could not read the module tree (token expired?) -- "
              "run: py -3.9 tools/ones_writer.py refresh-token", file=sys.stderr)
        return 2

    parent = next((m for m in mods if m["uuid"] == args.parent), None)
    if parent is None:
        print(f"[module] parent module {args.parent} not found in library {lib}", file=sys.stderr)
        return 2

    for m in mods:
        if m.get("name") == args.name and (m.get("parent") or {}).get("uuid") == args.parent:
            print(f"[module] already exists under {parent.get('name')}: {m['uuid']} ({m['name']})")
            return 3

    if args.dry_run:
        print(f"[module] dry-run: would create '{args.name}' under {parent.get('name')} ({args.parent})")
        return 0

    body = {"module": {"name": args.name, "parent_uuid": args.parent, "library_uuid": lib}}
    st, resp = api_call(
        "POST",
        f"/project/api/project/team/{team}/testcase/library/{lib}/modules/add",
        body,
        env=env,
    )
    if st != 200 or not isinstance(resp, dict) or "module" not in resp:
        short = json.dumps(resp, ensure_ascii=False)[:300] if isinstance(resp, (dict, list)) else str(resp)[:300]
        print(f"[module] create failed: HTTP {st} {short}", file=sys.stderr)
        return 1

    created = resp["module"]
    uuid = created["uuid"]

    # verify it is really in the tree
    after = get_modules(env)
    hit = next((m for m in after if m["uuid"] == uuid), None)
    if not hit:
        print(f"[module] created uuid={uuid} but it is missing from the module tree", file=sys.stderr)
        return 2

    print(f"[module] created '{hit['name']}' uuid={uuid} parent={args.parent} cases={hit.get('testcaseCaseCount')}")
    print(f"[module] ONES URL: https://ones.cn/project/#/testcase/team/{team}/library/{lib}/module/{uuid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
