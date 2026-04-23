#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Allure 报告的 behaviors.json 解析测试用例状态，
处理合并编号（如 T5033_5034），生成 ONES 更新用的状态映射。
"""

import json
import os
import re
from datetime import datetime


def _extract_test_case_ids(name: str) -> list:
    """
    从测试函数名提取所有 T 编号。
    
    处理多种格式:
    - testT3981_Verified -> ['T3981']
    - testT5033_5034_VerifyPartner -> ['T5033', 'T5034']
    - testT5210_5211_5212_Verify -> ['T5210', 'T5211', 'T5212']
    - testT3683_T3684_Guest -> ['T3683', 'T3684']
    """
    # 找第一个 T 编号
    m = re.match(r'^.*?T(\d+)(.*)', name)
    if not m:
        return []
    
    first_num = m.group(1)
    rest = m.group(2)
    result = ['T' + first_num]
    
    # 从 rest 中找 _T数字 或 _数字
    nums = re.findall(r'[&_]T?(\d+)', rest)
    for num in nums:
        result.append('T' + num)
    
    return result


def parse_behaviors_json(report_dir: str) -> dict:
    """
    解析 Allure behaviors.json，返回测试用例状态。
    返回格式: { "T3981": "passed", "T5033": "failed", ... }
    """
    behaviors_path = os.path.join(report_dir, "data", "behaviors.json")

    if not os.path.exists(behaviors_path):
        print(f"[ERROR] behaviors.json not found at {behaviors_path}")
        return {}

    with open(behaviors_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_results = {}

    def extract_test_cases(item):
        """递归提取所有测试用例"""
        # item 可能是测试用例
        if "name" in item and "status" in item:
            name = item.get("name", "")
            status = item.get("status", "").lower()

            # 映射状态
            if status == "passed":
                status = "passed"
            elif status == "failed":
                status = "failed"
            elif status in ("skipped", "broken"):
                status = "failed"  # ONES 没有"中断"，用"失败"
            else:
                return  # 未知状态，跳过

            # 从 name 提取 T 编号
            # 格式: testT3981_Verified -> T3981
            # 格式: testT5033_5034_VerifyPartner -> T5033, T5034
            # 格式: testT5210_5211_5212_Verify -> T5210, T5211, T5212
            # 格式: testT3683_T3684_Guest -> T3683, T3684
            tc_list = _extract_test_case_ids(name)
            for tc in tc_list:
                # 如果同一个编号有多个结果，以最后一个为准（取最新）
                test_results[tc] = status

        # 递归处理 children
        if "children" in item:
            for child in item["children"]:
                extract_test_cases(child)

    if "children" in data:
        for child in data["children"]:
            extract_test_cases(child)

    return test_results


def parse_test_cases_from_yaml(yaml_files: list) -> dict:
    """
    从 YAML 文件读取用例列表，用于确认哪些用例需要更新。
    返回格式: { "Scanner.yaml": ["T3981", "T3981_Already", ...], ... }
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
    """获取最新的 Allure 报告目录"""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    html_dir = os.path.join(base_dir, "report", "html")

    if not os.path.exists(html_dir):
        print(f"[ERROR] HTML report directory not found: {html_dir}")
        return None

    # 获取所有子目录，按修改时间排序
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
    生成最终的状态映射。
    如果指定了 yaml_cases，则只保留这些用例的状态。
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
                print(f"  跳过 {tc} (不在指定的 YAML 文件中)")
        return filtered

    return test_results


if __name__ == "__main__":
    import sys

    # ============================================================
    # 配置区
    # ============================================================
    YAML_FILES = [
        "All_YAML/Events/Scanner.yaml",
        "All_YAML/Events/Sync_event_post.yaml",
        "All_YAML/Form/Storefront_form.yaml",
        "All_YAML/Form/Storefront_product_with_form.yaml",
        "All_YAML/Module/Module.yaml",
        "All_YAML/Post/Post_setting.yaml",
    ]

    # 报告目录，默认使用最新的
    REPORT_DIR = None  # 自动选择最新

    # ============================================================

    print("=" * 60)
    print("ONES 测试状态生成工具")
    print("=" * 60)

    # 1. 获取报告目录
    if REPORT_DIR:
        report_dir = REPORT_DIR
    else:
        print("\n[1] 查找最新报告目录...")
        report_dir = get_latest_report_dir()

    if not report_dir:
        sys.exit(1)

    # 2. 解析 behaviors.json
    print("\n[2] 解析 behaviors.json...")
    test_results = parse_behaviors_json(report_dir)
    print(f"    解析到 {len(test_results)} 个测试用例状态")

    # 3. 可选：从 YAML 过滤
    # yaml_cases = parse_test_cases_from_yaml(YAML_FILES)
    # test_results = generate_status_mapping(test_results, yaml_cases)

    # 4. 输出结果
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

    # 输出 JSON 格式，方便后续使用
    import json
    print(json.dumps(test_results, indent=2, ensure_ascii=False))
