#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONES 测试状态更新工具 v5 (带调试)

使用方法:
    python tools/update_test_status.py [report_dir]
"""

import json
import os
import re
import sys
import time
from playwright.sync_api import sync_playwright


def _extract_test_case_ids(name: str) -> list:
    """从测试函数名提取所有 T 编号。"""
    m = re.match(r'^.*?T(\d+)(.*)', name)
    if not m:
        return []
    
    first_num = m.group(1)
    rest = m.group(2)
    result = ['T' + first_num]
    
    # 处理 _T数字 或 _数字
    nums = re.findall(r'[&_]T?(\d+)', rest)
    for num in nums:
        result.append('T' + num)
    
    return result


def parse_behaviors_json(report_dir: str) -> dict:
    """从 Allure behaviors.json 解析测试用例状态。"""
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
            
            if status not in ("passed", "failed"):
                status = "failed"
            
            tc_list = _extract_test_case_ids(name)
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
    """获取最新的 Allure HTML 报告目录。"""
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
    登录 ONES 并更新测试用例状态。
    """
    status_map = {
        "passed": "通过",
        "failed": "失败"
    }
    
    total = len(test_results)
    print(f"[INFO] Total cases to update: {total}")
    print(f"[INFO] Cases: {', '.join(sorted(test_results.keys()))}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(30000)
        
        # 1. 登录
        print("\n[1/6] 登录 ONES...")
        page.goto("https://ones.cn/identity/login")
        
        # 等待登录表单加载
        try:
            page.wait_for_selector("input[name], input[type='text'], input[type='email']", timeout=15000)
        except:
            print("    [ERROR] 登录页面加载超时")
            return
        
        page.get_by_role("textbox", name="* 邮箱").fill("yuxiao.zhu.ext@1m.app")
        page.get_by_role("textbox", name="* 密码").fill("zyx@1032970941")
        page.get_by_role("button", name="登录").click()
        page.wait_for_timeout(500)
        page.get_by_role("link", name="测试管理").click()
        page.wait_for_timeout(2000)
        
        print("    [OK] 登录成功")
        
        # 2. 进入测试管理
        print("\n[2/6] 进入测试管理...")
        
        # 3. 找到测试计划
        print(f"\n[3/6] 查找测试计划: {test_plan_name or 'refactor regression'}...")
        
        plan_regex = re.compile(test_plan_name or "refactor regression", re.IGNORECASE)
        
        try:
            page.get_by_text(plan_regex).first.wait_for(state="visible", timeout=10000)
            page.get_by_text(plan_regex).first.click()
            page.wait_for_timeout(2000)
            print("    [OK] 进入测试计划")
        except Exception as e:
            print(f"    [ERROR] 查找测试计划失败: {e}")
            print("    当前页面内容片段:")
            body_text = page.inner_text("body")[:500]
            print(f"    {body_text}")
            input("    按回车继续...")
        
        page.wait_for_timeout(2000)
        
        # 4. 跳过等待列表加载（滚动加载，无法等待）
        
        # 5. 逐个更新用例
        print("\n[5/6] 更新用例...")
        print("-" * 60)
        
        updated = 0
        failed = 0
        skipped = 0
        
        # 先展开搜索框
        print("    展开搜索框...")
        search_btn = page.locator("div.testcase-search-input > button").first
        search_btn.click(timeout=3000)
        page.wait_for_timeout(500)
        
        search_input = page.locator("div.testcase-search-input input").first
        if search_input.count() == 0:
            print("    [ERROR] 找不到搜索框")
            return
        
        for i, (tc_id, status) in enumerate(sorted(test_results.items()), 1):
            print(f"[{i}/{total}] {tc_id} -> {status}", end=" ")
            
            try:
                # 清空并输入新编号
                search_input.fill("")
                page.wait_for_timeout(200)
                search_input.fill(tc_id)
                page.wait_for_timeout(2000)  # 等待搜索结果
                
                # 找行：先尝试 role="row"
                row = page.get_by_role("row").filter(has_text=tc_id)
                
                if row.count() == 0:
                    # 尝试 div[class*='table-row']
                    row = page.locator("div[class*='table-row']").filter(has_text=tc_id)
                
                if row.count() == 0:
                    # 尝试 div + checkbox 组合
                    row = page.locator("div").filter(has_text=tc_id).filter(has=page.locator("input[type='checkbox']")).last
                
                if row.count() > 1:
                    row = row.first
                
                if row.count() == 0:
                    print(f"[SKIP-{tc_id}]")
                    skipped += 1
                    continue
                
                # 勾选
                checkbox = row.locator("input[type='checkbox']").first
                if not checkbox.is_checked():
                    checkbox.check()
                
                # 改状态
                website_status = status_map.get(status, status)
                if website_status:
                    page.get_by_role("button", name="更改执行结果").click()
                    page.wait_for_timeout(500)
                    # 在模态框内找状态
                    page.locator(".ones-modal-wrap").get_by_text(website_status, exact=True).click()
                    page.get_by_role("button", name="确定").click()
                    page.get_by_role("button", name="确定").wait_for(state="hidden", timeout=5000)
                
                # 取消勾选
                if checkbox.is_checked():
                    checkbox.uncheck()
                
                print("[OK]")
                updated += 1
                
            except Exception as e:
                print(f"[FAIL - {str(e)[:40]}]")
                failed += 1
                try:
                    page.keyboard.press("Escape")
                except:
                    pass
        
        # 6. 完成
        print("-" * 60)
        print(f"\n[6/6] 完成!")
        print(f"    Updated: {updated}")
        print(f"    Failed: {failed}")
        print(f"    Skipped: {skipped}")
        
        context.close()
        browser.close()


if __name__ == "__main__":
    report_dir = sys.argv[1] if len(sys.argv) > 1 else None
    test_plan_name = "refactor regression"
    
    if report_dir:
        if not os.path.isabs(report_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            report_dir = os.path.join(base_dir, report_dir)
    else:
        print("=" * 60)
        print("ONES Test Status Updater v5")
        print("=" * 60)
        print("\n[1/3] 查找最新报告...")
        report_dir = get_latest_report_dir()
    
    if not report_dir:
        sys.exit(1)
    
    print(f"\n    Report: {report_dir}")
    
    print("\n[2/3] 解析测试状态...")
    test_results = parse_behaviors_json(report_dir)
    passed = sum(1 for v in test_results.values() if v == "passed")
    failed = sum(1 for v in test_results.values() if v == "failed")
    print(f"    Total: {len(test_results)} (Passed: {passed}, Failed: {failed})")
    
    if test_results:
        print("\n[3/3] 开始更新 ONES...")
        print("    (浏览器将打开)")
        update_ones(test_results, test_plan_name)
    else:
        print("\n[ERROR] No test results found")
