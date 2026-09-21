#!/usr/bin/env python3
"""
locator_lint.py - Static linter for Katana UI YAML test cases.

Catches the anti-patterns that historically cost days of mis-attribution,
BEFORE you run anything. Deterministic, offline, fast (whole suite < 1s).
No Playwright / browser / network required.

Rules
  E101 dup-key            Duplicate step key in the same mapping.
                          YAML folding keeps the LAST value but the FIRST
                          position -> the action silently runs "early"
                          (T3690: checkout email fired on the product page).
  W102 mui-combobox-name  `role: combobox` + `name:` on a MUI Select (div).
                          MUI Select accessible names are usually empty ->
                          count = 0 (T4540). Heuristic (the real name is a
                          runtime property) so it is a WARN, not an ERROR;
                          entries explicitly marked `tag: button` (DatePicker
                          triggers, which do carry an aria-label) are skipped.
  W201 hover-no-center    move_*/hover step without an explicit centered
                          x/y. Default x=y=0 lands top-left and is unstable
                          on circular / SVG icons.
  W202 dup-sleep-key      Duplicate sleep_* key. Known debt (~1000 occurrences)
                          - reported separately so it never drowns real errors.
                          Do NOT mass-rename; see project memory.
  W203 unresolved-action  Step key that resolves to no handler in
                          actions/__init__.py (typo in the prefix). Such a
                          step silently does nothing.

Usage
  python tools/locator_lint.py                     # lint all UI yaml
  python tools/locator_lint.py --files Post_setting.yaml
  python tools/locator_lint.py --rule E101,E102
  python tools/locator_lint.py --errors-only
  python tools/locator_lint.py --json
Exit code is 1 when any ERROR (E*) is found, else 0 -> safe for pre-commit / CI.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, OrderedDict

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required: pip install pyyaml\n")
    sys.exit(2)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ROOTS = [os.path.join(PROJECT_ROOT, "test_case", "UI", "Test_Katana")]
DEFAULT_EXCLUDES = [os.path.join("actions", "example")]
ACTIONS_FILE = os.path.join(PROJECT_ROOT, "test_case", "UI", "Test_Katana",
                            "actions", "__init__.py")

RULE_HELP = OrderedDict([
    ("E101", "duplicate key in the same mapping (folding reorders execution)"),
    ("W102", "role=combobox + name= on a MUI Select (likely empty name)"),
    ("W201", "hover/move step without centered x/y"),
    ("W202", "duplicate sleep_* key (known debt)"),
    ("W203", "step key resolves to no action handler"),
])

MOVE_PREFIXES = ("move_relative_to_selector", "move_mouse", "move_to", "hover")

RED, GREEN, YELLOW, CYAN, DIM, BOLD = (
    "\033[31m", "\033[32m", "\033[33m", "\033[36m", "\033[2m", "\033[1m")
RESET = "\033[0m"


# ---------------------------------------------------------------------------
# Action registry (static parse - no Playwright import)
# ---------------------------------------------------------------------------

def load_action_vocab():
    """Return (exact_names, prefixes) parsed from actions/__init__.py.

    Static parse so the linter stays dependency-light. Returns (None, None)
    if the file cannot be read, which disables the W203 rule.
    """
    try:
        with open(ACTIONS_FILE, "r", encoding="utf-8") as fh:
            src = fh.read()
    except OSError:
        return None, None

    exact = set(re.findall(r'^\s*["\']([A-Za-z0-9_]+)["\']\s*:\s*[\w.]+\s*,',
                           src, re.M))
    prefixes = set(re.findall(r'name\.startswith\(\s*["\']([^"\']+)["\']\s*\)',
                              src))
    if not exact or not prefixes:
        return None, None
    return exact, prefixes


def action_resolvable(key, exact, prefixes):
    if exact is None:
        return True
    if key in exact:
        return True
    return any(key.startswith(p) for p in prefixes)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

class Finding(object):
    __slots__ = ("rule", "file", "line", "message", "context")

    def __init__(self, rule, file, line, message, context=""):
        self.rule = rule
        self.file = file
        self.line = line
        self.message = message
        self.context = context

    def as_dict(self):
        return {"rule": self.rule, "file": self.file, "line": self.line,
                "message": self.message, "context": self.context}


def _pairs(mapping_node):
    """[(key, key_node, value_node)] for a MappingNode, null keys skipped."""
    out = []
    for k_node, v_node in mapping_node.value:
        if isinstance(k_node, yaml.ScalarNode) and k_node.value is not None:
            out.append((str(k_node.value), k_node, v_node))
    return out


def _path_str(path):
    return " > ".join(path) if path else "<root>"


def walk(node, path, rel_file, findings, exact, prefixes):
    if isinstance(node, yaml.MappingNode):
        pairs = _pairs(node)
        counts = Counter(key for key, _, _ in pairs)
        in_test_step = bool(path) and path[-1] == "test_step"
        emitted = set()

        for key, k_node, _v in pairs:
            line = k_node.start_mark.line + 1
            if counts[key] > 1 and key not in emitted:
                emitted.add(key)
                rule = "W202" if key.startswith("sleep") else "E101"
                findings.append(Finding(
                    rule, rel_file, line,
                    "duplicate key '%s' (x%d) in %s "
                    "- keeps LAST value, stays at FIRST position"
                    % (key, counts[key], _path_str(path)),
                    _path_str(path)))
            if in_test_step and not action_resolvable(key, exact, prefixes):
                findings.append(Finding(
                    "W203", rel_file, line,
                    "step '%s' resolves to no action handler "
                    "(silently does nothing)" % key,
                    _path_str(path)))

        for key, _k, v_node in pairs:
            if isinstance(v_node, yaml.MappingNode):
                child_keys = {}
                for kk, vv in v_node.value:
                    if isinstance(kk, yaml.ScalarNode) and kk.value is not None:
                        child_keys.setdefault(str(kk.value), vv)

                role_node = child_keys.get("role")
                tag_node = child_keys.get("tag")
                tag = str(tag_node.value).strip().lower() if tag_node is not None else ""
                if (role_node is not None and "name" in child_keys
                        and str(role_node.value).strip().lower() == "combobox"
                        and tag != "button"):
                    findings.append(Finding(
                        "W102", rel_file, role_node.start_mark.line + 1,
                        "role=combobox + name= on step '%s' "
                        "- MUI Select accessible name is usually empty (count=0); "
                        "confirm against the live DOM" % key,
                        _path_str(path)))

                if any(key.startswith(p) for p in MOVE_PREFIXES):
                    def _unset(k):
                        n = child_keys.get(k)
                        return n is None or str(n.value).strip() in ("", "0", "0.0")
                    if _unset("x") or _unset("y"):
                        mark = v_node.start_mark
                        findings.append(Finding(
                            "W201", rel_file, (mark.line if mark else 0) + 1,
                            "move step '%s' has no centered x/y "
                            "(defaults to top-left, unstable on icons)" % key,
                            _path_str(path)))

                walk(v_node, path + [key], rel_file, findings, exact, prefixes)
            elif isinstance(v_node, yaml.SequenceNode):
                walk(v_node, path + [key], rel_file, findings, exact, prefixes)

    elif isinstance(node, yaml.SequenceNode):
        for i, item in enumerate(node.value):
            walk(item, path + ["[%d]" % i], rel_file, findings, exact, prefixes)


def lint_file(abs_path, rel_file, exact, prefixes):
    try:
        with open(abs_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return [Finding("E000", rel_file, 0, "cannot read: %s" % exc)]
    try:
        root = yaml.compose(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = (mark.line + 1) if mark else 0
        return [Finding("E000", rel_file, line, "YAML parse error: %s"
                        % str(exc).splitlines()[0])]
    if root is None:
        return []
    findings = []
    walk(root, [], rel_file, findings, exact, prefixes)
    return findings


# ---------------------------------------------------------------------------
# File discovery / reporting
# ---------------------------------------------------------------------------

def find_yaml(roots, files_filter, excludes):
    found = []
    for root in roots:
        for dirpath, _dirnames, filenames in os.walk(root):
            norm = dirpath.replace("/", os.sep)
            if any(ex in norm for ex in excludes):
                continue
            for name in filenames:
                if not name.lower().endswith((".yaml", ".yml")):
                    continue
                abs_path = os.path.join(dirpath, name)
                try:
                    rel = os.path.relpath(abs_path, PROJECT_ROOT)
                except ValueError:          # different drive (e.g. --root on C:)
                    rel = abs_path
                if files_filter and not any(f.lower() in rel.lower()
                                            for f in files_filter):
                    continue
                found.append((abs_path, rel))
    return sorted(found, key=lambda t: t[1])


def main():
    ap = argparse.ArgumentParser(
        description="Static linter for Katana UI YAML test cases")
    ap.add_argument("--root", action="append", default=None,
                    help="override root dir (repeatable)")
    ap.add_argument("--files", nargs="*", default=None,
                    help="only lint files whose path contains any of these")
    ap.add_argument("--rule", default=None,
                    help="comma-separated rule codes to keep, e.g. E101,E102")
    ap.add_argument("--errors-only", action="store_true", help="hide W* rules")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--top", type=int, default=0,
                    help="limit findings listed per file (0 = all)")
    args = ap.parse_args()

    roots = args.root or DEFAULT_ROOTS
    keep = None
    if args.rule:
        keep = {r.strip().upper() for r in args.rule.split(",") if r.strip()}

    exact, prefixes = load_action_vocab()
    files = find_yaml(roots, args.files, DEFAULT_EXCLUDES)

    all_findings = []
    per_file = OrderedDict()
    for abs_path, rel in files:
        f = lint_file(abs_path, rel, exact, prefixes)
        if keep:
            f = [x for x in f if x.rule in keep]
        if args.errors_only:
            f = [x for x in f if x.rule.startswith("E")]
        if f:
            per_file[rel] = f
        all_findings.extend(f)

    counts = Counter(x.rule for x in all_findings)
    errors = sum(v for k, v in counts.items() if k.startswith("E"))

    if args.json:
        print(json.dumps({
            "files_scanned": len(files),
            "totals": dict(counts),
            "errors": errors,
            "rules": RULE_HELP,
            "findings": [x.as_dict() for x in all_findings],
        }, indent=2, ensure_ascii=False))
        return 1 if errors else 0

    print("%sKatana UI YAML linter%s  (%d files scanned)"
          % (BOLD, RESET, len(files)))
    if prefixes is None:
        print("%s  ! W203 disabled: could not parse action registry%s"
              % (YELLOW, RESET))
    print("")

    if not all_findings:
        print("%s  OK - no findings.%s" % (GREEN, RESET))
        return 0

    for rel, f in per_file.items():
        shown = f if not args.top else f[:args.top]
        print("%s%s%s  (%d findings)" % (BOLD, rel, RESET, len(f)))
        for x in shown:
            color = RED if x.rule.startswith("E") else YELLOW
            mark = "x" if x.rule.startswith("E") else "!"
            print("   %s%s%s %s%-4s%s L%-5d %s"
                  % (color, mark, RESET, color, x.rule, RESET, x.line,
                     x.message))
        if args.top and len(f) > args.top:
            print("   %s... %d more%s" % (DIM, len(f) - args.top, RESET))
        print("")

    print("%sSummary%s" % (BOLD, RESET))
    for rule in RULE_HELP:
        if counts.get(rule):
            color = RED if rule.startswith("E") else YELLOW
            print("  %s%-5s%s %4d  %s"
                  % (color, rule, RESET, counts[rule], RULE_HELP[rule]))
    print("  %s%d errors, %d warnings across %d file(s)%s"
          % (RED if errors else GREEN, errors,
             len(all_findings) - errors, len(per_file), RESET))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
