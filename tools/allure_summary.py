#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
allure_summary.py
-----------------
Purpose:
  1. Read the latest (or specified) allure-results raw JSON, count PASS/FAIL/BROKEN/SKIP
  2. Write results back to YAML test case files as inline comments, e.g.:
       testT3554:  # [LAST: PASS 2026-05-06]

Usage:
  python tools/allure_summary.py                   # Count + annotate (uses yaml_files from main.py)
  python tools/allure_summary.py --dry-run          # Print only, no file changes
  python tools/allure_summary.py --results-dir <dir> --dry-run
  python tools/allure_summary.py --yaml <f1> <f2>   # Annotate specified files only

Note: Must be run from the project root, or add the root to PYTHONPATH.
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime

# ─── Project structure constants ────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_ROOT = os.path.join(BASE_DIR, 'allure-results')
YAML_BASE = os.path.join(BASE_DIR, 'test_case', 'UI', 'Test_Katana')

# Regex for inline marker: matches old markers for easy replacement
_MARKER_RE = re.compile(r'\s*#\s*\[LAST:.*?\]\s*$')

# ─── 1. Get latest results directory ─────────────────────────────────────────

def get_latest_results_dir():
    subdirs = sorted(
        (d for d in os.listdir(RESULTS_ROOT)
         if os.path.isdir(os.path.join(RESULTS_ROOT, d))),
        reverse=True
    )
    if not subdirs:
        print("[ERROR] No subdirectories found under allure-results/")
        return None
    latest = os.path.join(RESULTS_ROOT, subdirs[0])
    print(f"[INFO] Using latest results directory: {latest}")
    return latest


# ─── 2. Parse raw result.json ──────────────────────────────────────────────

def parse_results(results_dir: str) -> dict:
    """
    Returns { test_name: {'status': str, 'message': str} }
    status: 'passed' | 'failed' | 'broken' | 'skipped'
    """
    result_files = glob.glob(os.path.join(results_dir, '*-result.json'))
    data = {}
    for f in result_files:
        try:
            with open(f, encoding='utf-8') as fp:
                d = json.load(fp)
            name = d.get('name', '')
            if not name:
                continue
            status = d.get('status', 'unknown').lower()
            message = d.get('statusDetails', {}).get('message', '') or ''
            # Strip extra newlines from message, keep first line only
            message = message.split('\n')[0].strip()[:120]
            data[name] = {'status': status, 'message': message}
        except Exception as e:
            print(f"[WARN] Failed to parse {f}: {e}")
    return data


# ─── 3. Print summary ──────────────────────────────────────────────────────

def print_summary(results: dict, date_str: str):
    buckets = {'passed': [], 'failed': [], 'broken': [], 'skipped': []}
    for name, info in results.items():
        s = info['status']
        buckets.setdefault(s, []).append(name)

    icons = {'passed': '✅', 'failed': '❌', 'broken': '💥', 'skipped': '⏭ '}
    total = len(results)

    print(f"\n{'='*60}")
    print(f"  Allure Test Results Summary  ({date_str})  Total: {total}")
    print(f"{'='*60}")
    for status in ('passed', 'failed', 'broken', 'skipped'):
        names = sorted(buckets.get(status, []))
        icon = icons.get(status, '?')
        print(f"\n{icon} {status.upper()} ({len(names)}):")
        for n in names:
            msg = results[n]['message']
            suffix = f"  → {msg}" if msg and status != 'passed' else ''
            print(f"    {n}{suffix}")

    print(f"\n{'─'*60}")
    counts = {s: len(v) for s, v in buckets.items()}
    print(f"  PASS:{counts.get('passed',0)}  "
          f"FAIL:{counts.get('failed',0)}  "
          f"BROKEN:{counts.get('broken',0)}  "
          f"SKIP:{counts.get('skipped',0)}")
    print(f"{'='*60}\n")


# ─── 4. Annotate YAML files ────────────────────────────────────────────────

def _make_marker(status: str, date_str: str) -> str:
    label = status.upper()
    return f"  # [LAST: {label} {date_str}]"


def annotate_yaml(yaml_rel_path: str, results: dict, date_str: str, dry_run: bool):
    """
    Appends / updates inline status comments for each top-level test key in yaml_rel_path.
    yaml_rel_path is relative to YAML_BASE.
    """
    yaml_path = os.path.join(YAML_BASE, yaml_rel_path.replace('/', os.sep))
    if not os.path.exists(yaml_path):
        print(f"[WARN] File not found, skipping: {yaml_path}")
        return

    with open(yaml_path, encoding='utf-8') as f:
        lines = f.readlines()

    changed = 0
    new_lines = []
    for line in lines:
        # Detect top-level test key (no leading space, starts with 'test', contains colon)
        stripped = line.rstrip('\n')
        m = re.match(r'^(test\w+):\s*(#.*)?$', stripped)
        if m:
            key = m.group(1)
            if key in results:
                status = results[key]['status']
                # Remove old marker and append new one
                base = _MARKER_RE.sub('', stripped)
                new_line = base + _make_marker(status, date_str) + '\n'
                if new_line != line:
                    changed += 1
                new_lines.append(new_line)
                continue
        new_lines.append(line)

    rel = yaml_rel_path
    if changed == 0:
        print(f"[INFO] {rel} — no changes ({len(results)} results, 0 matched this file)")
    else:
        print(f"[INFO] {rel} — annotated {changed} test cases")

    if not dry_run and changed > 0:
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"       Written to {yaml_path}")


# ─── 5. Entry point ───────────────────────────────────────────────────────

# Default list of YAML files to annotate (relative to YAML_BASE)
DEFAULT_YAMLS = [
    'All_YAML/Module/Module.yaml',
    'All_YAML/Form/Storefront_form.yaml',
    'All_YAML/Form/Storefront_product_with_form.yaml',
    'All_YAML/Post/Post_setting.yaml',
    'All_YAML/Events/Scanner.yaml',
    'All_YAML/Events/Sync_event_post.yaml',
]


def main():
    parser = argparse.ArgumentParser(description='Parse Allure results and annotate YAML test case status')
    parser.add_argument('--results-dir', default=None,
                        help='Specify allure-results subdirectory (default: auto-select latest)')
    parser.add_argument('--yaml', nargs='+', default=None,
                        help='YAML files to annotate (relative to Test_Katana/, default: all)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print only, do not modify files')
    args = parser.parse_args()

    # 1. Determine results directory
    results_dir = args.results_dir or get_latest_results_dir()
    if not results_dir:
        sys.exit(1)

    # 2. Parse results
    results = parse_results(results_dir)
    if not results:
        print('[ERROR] No result.json found, exiting')
        sys.exit(1)

    # 3. Date label (from directory name, e.g. 20260506_154240)
    dirname = os.path.basename(results_dir)
    try:
        date_str = datetime.strptime(dirname[:8], '%Y%m%d').strftime('%Y-%m-%d')
    except ValueError:
        date_str = datetime.now().strftime('%Y-%m-%d')

    # 4. Print summary
    print_summary(results, date_str)

    # 5. Annotate YAML files
    yaml_files = args.yaml or DEFAULT_YAMLS
    if args.dry_run:
        print('[DRY-RUN] No files will be modified\n')
    for yf in yaml_files:
        annotate_yaml(yf, results, date_str, dry_run=args.dry_run)

    if args.dry_run:
        print('\n[DRY-RUN COMPLETE] Re-run without --dry-run to write files')
    else:
        print('\n[DONE] All YAML files updated')


if __name__ == '__main__':
    main()
