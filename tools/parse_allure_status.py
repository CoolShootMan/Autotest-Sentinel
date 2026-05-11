#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse test case statuses from Allure report's behaviors.json,
handle merged case numbers (e.g. T5033_5034), and generate a status map for ONES updates.
"""

import json
import os
import re
from datetime import datetime


def _extract_test_case_ids(name: str) -> list:
    """
    Extract all T-numbers from a test function name.
    
    Handles multiple formats:
    - testT3981_Verified -> ['T3981']
    - testT5033_5034_VerifyPartner -> ['T5033', 'T5034']
    - testT5210_5211_5212_Verify -> ['T5210', 'T5211', 'T5212']
    - testT3683_T3684_Guest -> ['T3683', 'T3684']
    """
    # Find the first T-number
    m = re.match(r'^.*?T(\d+)(.*)', name)
    if not m:
        return []
    
    first_num = m.group(1)
    rest = m.group(2)
    result = ['T' + first_num]
    
    # Find additional _Tnumber or _number in the remainder
    nums = re.findall(r'[&_]T?(\d+)', rest)
    for num in nums:
        result.append('T' + num)
    
    return result


def parse_behaviors_json(report_dir: str) -> dict:
    """
    Parse Allure behaviors.json and return test case statuses.
    Return format: { "T3981": "passed", "T5033": "failed", ... }
    """
    behaviors_path = os.path.join(report_dir, "data", "behaviors.json")

    if not os.path.exists(behaviors_path):
        print(f"[ERROR] behaviors.json not found at {behaviors_path}")
        return {}

    with open(behaviors_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_results = {}

    def extract_test_cases(item):
        """Recursively extract all test cases"""
        # item may represent a test case
        if "name" in item and "status" in item:
            name = item.get("name", "")
            status = item.get("status", "").lower()

            # Map status values
            if status == "passed":
                status = "passed"
            elif status == "failed":
                status = "failed"
            elif status in ("skipped", "broken"):
                status = "failed"  # ONES has no "broken" status, map to "failed"
            else:
                return  # Unknown status, skip

            # Extract T-numbers from name
            # Format: testT3981_Verified -> T3981
            # Format: testT5033_5034_VerifyPartner -> T5033, T5034
            # Format: testT5210_5211_5212_Verify -> T5210, T5211, T5212
            # Format: testT3683_T3684_Guest -> T3683, T3684
            tc_list = _extract_test_case_ids(name)
            for tc in tc_list:
                # If the same number appears multiple times, use the last result (most recent)
                test_results[tc] = status

        # Recurse into children
        if "children" in item:
            for child in item["children"]:
                extract_test_cases(child)

    if "children" in data:
        for child in data["children"]:
            extract_test_cases(child)

    return test_results


def parse_test_cases_from_yaml(yaml_files: list) -> dict:
    """
    Read test case list from YAML files to determine which cases need updating.
    Return format: { "Scanner.yaml": ["T3981", "T3981_Already", ...], ... }
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yaml_dir = os.path.join(base_dir, "test_case", "UI", "Test_Katana")
    test_cases = {}

    for yaml_file in yaml_files:
        yaml_path = os.path.join(yaml_dir, yaml_file.replace('/', os.sep).replace('\\', os.sep))
        if not os.path.exists(yaml_path):
            continue

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) if 'yaml' in dir() else {}

        cases = []
        if data:
            for key in data.keys():
                matches = re.findall(r'T\d+', key)
                cases.extend(matches)

        yaml_name = os.path.basename(yaml_file)
        test_cases[yaml_name] = list(set(cases))

    return test_cases


def get_latest_report_dir(base_dir: str = None) -> str:
    """Get the latest Allure HTML report directory"""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    html_dir = os.path.join(base_dir, "report", "html")

    if not os.path.exists(html_dir):
        print(f"[ERROR] HTML report directory not found: {html_dir}")
        return None

    # Get all subdirectories sorted by modification time
    subdirs = [d for d in os.listdir(html_dir) if os.path.isdir(os.path.join(html_dir, d))]
    subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(html_dir, x)), reverse=True)

    if not subdirs:
        print("[ERROR] No report directories found")
        return None

    latest = os.path.join(html_dir, subdirs[0])
    print(f"[OK] Latest report: {latest}")
    return latest


def generate_status_mapping(test_results: dict, yaml_cases: dict = None) -> dict:
    """
    Generate the final status mapping.
    If yaml_cases is provided, only retain statuses for those cases.
    """
    if yaml_cases:
        all_yaml_tc = set()
        for cases in yaml_cases.values():
            all_yaml_tc.update(cases)

        filtered = {}
        for tc, status in test_results.items():
            if tc in all_yaml_tc:
                filtered[tc] = status
            else:
                print(f"  Skipping {tc} (not in specified YAML files)")
        return filtered

    return test_results


if __name__ == "__main__":
    import sys

    # ============================================================
    # Configuration
    # ============================================================
    YAML_FILES = [
        "All_YAML/Events/Scanner.yaml",
        "All_YAML/Events/Sync_event_post.yaml",
        "All_YAML/Form/Storefront_form.yaml",
        "All_YAML/Form/Storefront_product_with_form.yaml",
        "All_YAML/Module/Module.yaml",
        "All_YAML/Post/Post_setting.yaml",
    ]

    # Report directory — defaults to latest
    REPORT_DIR = None  # Auto-select latest

    # ============================================================

    print("=" * 60)
    print("ONES Test Status Generator")
    print("=" * 60)

    # 1. Locate report directory
    if REPORT_DIR:
        report_dir = REPORT_DIR
    else:
        print("\n[1] Finding latest report directory...")
        report_dir = get_latest_report_dir()

    if not report_dir:
        sys.exit(1)

    # 2. Parse behaviors.json
    print("\n[2] Parsing behaviors.json...")
    test_results = parse_behaviors_json(report_dir)
    print(f"    Parsed {len(test_results)} test case statuses")

    # 3. Optional: filter by YAML
    # yaml_cases = parse_test_cases_from_yaml(YAML_FILES)
    # test_results = generate_status_mapping(test_results, yaml_cases)

    # 4. Output results
    print("\n[3] Test Status Summary:")
    print("-" * 40)

    passed = [k for k, v in test_results.items() if v == "passed"]
    failed = [k for k, v in test_results.items() if v == "failed"]

    print(f"PASSED: {len(passed)}")
    for tc in sorted(passed):
        print(f"   {tc}")

    print(f"\nFAILED: {len(failed)}")
    for tc in sorted(failed):
        print(f"   {tc}")

    print("\n" + "=" * 60)
    print("Status Mapping (for ONES update):")
    print("=" * 60)

    # Output as JSON for downstream consumption
    import json
    print(json.dumps(test_results, indent=2, ensure_ascii=False))
