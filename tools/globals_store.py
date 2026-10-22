#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inspect / edit the persistent cross-case global-variable store.

The store lives in  test_case/UI/global_vars_<env>.json  and is written by any step that
uses `save_as` + `global: true` (see actions/global_state.py).  Because it is a REAL global
(shared by every pytest process and every run), you sometimes want to look at it or wipe it:

    ./venv/bin/python tools/globals_store.py                 # list everything
    ./venv/bin/python tools/globals_store.py --get post_url  # one key
    ./venv/bin/python tools/globals_store.py --set post_url https://...   # force a value
    ./venv/bin/python tools/globals_store.py --clear         # wipe the store file

Environment: BASE_URL decides which file is used (release / staging / prod); override with
UI_GLOBAL_STATE_FILE=/abs/path.json or UI_GLOBAL_ENV=<name>.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_case", "UI"))

from actions import global_state as gs  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect/edit the UI global-variable store")
    ap.add_argument("--get", metavar="KEY", help="print one value")
    ap.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="publish a value")
    ap.add_argument("--clear", action="store_true", help="delete the store file")
    args = ap.parse_args()

    print(f"store file: {gs.state_path()}")

    if args.clear:
        gs.reset_globals(remove_file=True)
        print("cleared.")
        return 0

    if args.set:
        key, value = args.set
        gs.set_global(key, value)
        print(f"set {gs.describe(key)}")
        return 0

    if args.get:
        print(gs.describe(args.get))
        return 0

    vars_ = gs.refresh_globals(force=True)
    if not vars_:
        print("(empty)")
        return 0
    width = max(len(k) for k in vars_)
    for key in sorted(vars_):
        age = gs.age_seconds(key)
        age_txt = "-" if age is None else f"{int(age)}s ago"
        print(f"  {key.ljust(width)} = {vars_[key]!r}   ({age_txt})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
