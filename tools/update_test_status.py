#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONES Test Status Updater v5 (with debug output)

Usage:
    python tools/update_test_status.py [report_dir]
"""

import json
import os
import re
import sys
import time
import yaml
from playwright.sync_api import sync_playwright


def _extract_test_case_ids(name: str) -> list:
    """Extract all T-numbers from a test function name."""
    m = re.match(r'^.*?T(\d+)(.*)', name)
    if not m:
        return []
    
    first_num = m.group(1)
    rest = m.group(2)
    result = ['T' + first_num]
    
    # Handle _Tnumber or _number patterns
    nums = re.findall(r'[&_]T?(\d+)', rest)
    for num in nums:
        result.append('T' + num)
    
    return result


def _extract_covered_cases_from_yaml(yaml_path: str) -> dict:
    """
    Extract covered T-case numbers from YAML file comments.
    
    Returns a dict mapping function names to their covered T-cases.
    Comments belong to the FUNCTION THAT FOLLOWS THEM, not the one before.
    
    Example:
        # 覆盖用例: T1234
        function_name:   <- T1234 belongs to function_name
    """
    if not os.path.exists(yaml_path):
        return {}
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        result = {}
        pending_comments = []  # Comments collected for the NEXT function
        last_was_comment = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check if this is a comment line (starts with #)
            if stripped.startswith('#'):
                # Add to pending comments if it has T-numbers or is continuation
                if 'T' in stripped or last_was_comment:
                    pending_comments.append(stripped)
                    last_was_comment = True
                    continue
            
            # Reset flag
            last_was_comment = False
            
            # Only consider TOP-LEVEL keys (no indentation) as test functions
            indent = len(line) - len(line.lstrip())
            func_match = re.match(r'^(\w+)\s*:', stripped)
            
            if func_match and indent == 0:
                func_name = func_match.group(1)
                
                # Save pending comments to THIS function (they belong to this function!)
                if pending_comments:
                    all_t_cases = []
                    for comment in pending_comments:
                        t_numbers = re.findall(r'T(\d+)', comment)
                        all_t_cases.extend(['T' + n for n in t_numbers])
                    if all_t_cases:
                        result[func_name] = all_t_cases
                    pending_comments = []
                
                # Start tracking (may get more comments later)
        
        # Any remaining comments at end of file are not associated with a function
        # (they would have been saved when we hit the next function)
        
        return result
    except Exception as e:
        print(f"    [WARN] Failed to parse YAML {yaml_path}: {e}")
        return {}


def _get_yaml_path_from_params(parameters: list) -> str:
    """Extract __yaml_path__ from Allure parameters."""
    for param in parameters:
        if isinstance(param, str) and '__yaml_path__' in param:
            # Extract the path from the JSON-like string
            match = re.search(r"'__yaml_path__':\s*'([^']+)'", param)
            if match:
                path = match.group(1)
                # Convert escaped Windows paths
                path = path.replace('\\\\', '/').replace('\\', '/')
                return path
    return None


def parse_behaviors_json(report_dir: str) -> dict:
    """Parse test case statuses from Allure behaviors.json."""
    behaviors_path = os.path.join(report_dir, "data", "behaviors.json")
    
    if not os.path.exists(behaviors_path):
        print(f"[ERROR] behaviors.json not found: {behaviors_path}")
        return {}
    
    with open(behaviors_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    test_results = {}
    
    def extract_cases(item):
        if "name" in item and "status" in item:
            name = item.get("name", "")
            status = item.get("status", "").lower()
            parameters = item.get("parameters", [])
            
            # Allure → ONES status mapping
            if status == "passed":
                status = "通过"
            elif status == "failed":
                status = "失败"
            elif status == "broken":
                status = "阻塞"
            elif status == "skipped":
                status = "跳过"
            
            # First try to extract T-numbers from function name
            tc_list = _extract_test_case_ids(name)
            
            # If no T-numbers found, try to get covered cases from YAML comments
            if not tc_list:
                yaml_path = _get_yaml_path_from_params(parameters)
                if yaml_path:
                    covered_cases_dict = _extract_covered_cases_from_yaml(yaml_path)
                    # Get the covered cases for this specific function
                    tc_list = covered_cases_dict.get(name, [])
                    if tc_list:
                        print(f"    [INFO] {name} -> YAML covered: {tc_list}")
            
            for tc in tc_list:
                test_results[tc] = status
        
        if "children" in item:
            for child in item["children"]:
                extract_cases(child)
    
    if "children" in data:
        for child in data["children"]:
            extract_cases(child)
    
    return test_results


def get_latest_report_dir(base_dir: str = None) -> str:
    """Get the latest Allure HTML report directory."""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    html_dir = os.path.join(base_dir, "report", "html")
    
    if not os.path.exists(html_dir):
        print(f"[ERROR] Report directory not found: {html_dir}")
        return None
    
    subdirs = [d for d in os.listdir(html_dir) if os.path.isdir(os.path.join(html_dir, d))]
    subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(html_dir, x)), reverse=True)
    
    if not subdirs:
        print("[ERROR] No report directories found")
        return None
    
    return os.path.join(html_dir, subdirs[0])


def update_ones(test_results: dict, test_plan_name: str = None):
    """
    Log in to ONES and update test case statuses.
    """
    status_map = {
        "通过": "通过",
        "失败": "失败",
        "阻塞": "阻塞",
        "跳过": "跳过"
    }
    
    total = len(test_results)
    print(f"[INFO] Total cases to update: {total}")
    print(f"[INFO] Cases: {', '.join(sorted(test_results.keys()))}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(30000)
        
        # 1. Log in
        print("\n[1/6] Logging in to ONES...")
        page.goto("https://ones.cn/identity/login")
        
        # Wait for login form to load
        try:
            page.wait_for_selector("input[name], input[type='text'], input[type='email']", timeout=15000)
        except:
            print("    [ERROR] Login page load timed out")
            return
        
        page.get_by_role("textbox", name="* 邮箱").fill("yuxiao.zhu.ext@1m.app")
        page.get_by_role("textbox", name="* 密码").fill("zyx@1032970941")
        page.get_by_role("button", name="登录").click()
        page.wait_for_timeout(500)
        page.get_by_role("link", name="测试管理").click()
        page.wait_for_timeout(2000)
        
        print("    [OK] Login successful")
        
        # 2. Enter Test Management
        print("\n[2/6] Entering Test Management...")
        
        # 3. Find the test plan
        print(f"\n[3/6] Finding test plan: {test_plan_name or 'KAT-11058'}...")
        
        plan_regex = re.compile(test_plan_name or "KAT-11058", re.IGNORECASE)
        
        try:
            page.get_by_text(plan_regex).first.wait_for(state="visible", timeout=10000)
            page.get_by_text(plan_regex).first.click()
            page.wait_for_timeout(2000)
            print("    [OK] Entered test plan")
        except Exception as e:
            print(f"    [ERROR] Failed to find test plan: {e}")
            print("    Current page content snippet:")
            body_text = page.inner_text("body")[:500]
            print(f"    {body_text}")
            input("    Press Enter to continue...")
        
        page.wait_for_timeout(2000)
        
        # 4. Skip waiting for list to load (scroll-loaded, cannot wait)
        
        # 5. Update each case
        print("\n[5/6] Updating test cases...")
        print("-" * 60)
        
        updated = 0
        failed = 0
        skipped = 0
        
        # Expand search box first
        print("    Expanding search box...")
        search_btn = page.locator("div.testcase-search-input > button").first
        search_btn.click(timeout=3000)
        page.wait_for_timeout(500)
        
        search_input = page.locator("div.testcase-search-input input").first
        if search_input.count() == 0:
            print("    [ERROR] Search box not found")
            return
        
        for i, (tc_id, status) in enumerate(sorted(test_results.items()), 1):
            print(f"[{i}/{total}] {tc_id} -> {status}", end=" ")
            
            try:
                # Clear and type new ID
                search_input.fill("")
                page.wait_for_timeout(200)
                search_input.fill(tc_id)
                page.wait_for_timeout(2000)  # Wait for search results
                
                # Find row: try role="row" first
                row = page.get_by_role("row").filter(has_text=tc_id)
                
                if row.count() == 0:
                    # Try div[class*='table-row']
                    row = page.locator("div[class*='table-row']").filter(has_text=tc_id)
                
                if row.count() == 0:
                    # Try div + checkbox combination
                    row = page.locator("div").filter(has_text=tc_id).filter(has=page.locator("input[type='checkbox']")).last
                
                if row.count() > 1:
                    row = row.first
                
                if row.count() == 0:
                    print(f"[SKIP-{tc_id}]")
                    skipped += 1
                    continue
                
                # Check the checkbox
                checkbox = row.locator("input[type='checkbox']").first
                if not checkbox.is_checked():
                    checkbox.check(force=True)
                
                # Change status
                website_status = status_map.get(status, status)
                if website_status:
                    page.get_by_role("button", name="更改执行结果").click()
                    page.wait_for_timeout(500)
                    # Find status option inside modal
                    page.locator(".ones-modal-wrap").get_by_text(website_status, exact=True).click()
                    page.get_by_role("button", name="确定").click()
                    page.get_by_role("button", name="确定").wait_for(state="hidden", timeout=5000)
                
                # Uncheck the checkbox
                if checkbox.is_checked():
                    checkbox.uncheck(force=True)
                
                print("[OK]")
                updated += 1
                
            except Exception as e:
                print(f"[FAIL - {str(e)[:60]}]")
                failed += 1
                try:
                    page.keyboard.press("Escape")
                except:
                    pass
        
        # 6. Done
        print("-" * 60)
        print(f"\n[6/6] Done!")
        print(f"    Updated: {updated}")
        print(f"    Failed: {failed}")
        print(f"    Skipped: {skipped}")
        
        context.close()
        browser.close()


if __name__ == "__main__":
    report_dir = sys.argv[1] if len(sys.argv) > 1 else None
    test_plan_name = "KAT-11058"
    
    if report_dir:
        if not os.path.isabs(report_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            report_dir = os.path.join(base_dir, report_dir)
    else:
        print("=" * 60)
        print("ONES Test Status Updater v5")
        print("=" * 60)
        print("\n[1/3] Finding latest report...")
        report_dir = get_latest_report_dir()
    
    if not report_dir:
        sys.exit(1)
    
    print(f"\n    Report: {report_dir}")
    
    print("\n[2/3] Parsing test statuses...")
    test_results = parse_behaviors_json(report_dir)
    passed = sum(1 for v in test_results.values() if v == "通过")
    failed = sum(1 for v in test_results.values() if v == "失败")
    print(f"    Total: {len(test_results)} (Passed: {passed}, Failed: {failed})")
    
    if test_results:
        print("\n[3/3] Starting ONES update...")
        print("    (Browser will open)")
        update_ones(test_results, test_plan_name)
    else:
        print("\n[ERROR] No test results found")
