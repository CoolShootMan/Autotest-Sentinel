#!/usr/bin/env python3
"""
ONES Plan Sync — 让测试计划 RVEi7pVd 与本地 API 自动化脚本保持一致。
扫描所有 tests/ 下的 .py 文件，从 CASE_ID 变量和文件名中提取 T 编号。
"""
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

PROJECT = Path("/Users/a123456/Desktop/Pear automation")
sys.path.insert(0, str(PROJECT / "tools"))
from ones_reader import OnesClient, load_env

PLAN_UUID = "RVEi7pVd"
TESTS_DIR = PROJECT / "test_case/API auto script/tests"


def extract_auto_cases():
    """从 tests/ 下所有 .py 提取已自动化的 ONES case UUID。
    新用例: CASE_ID 变量直接是 UUID。
    老用例: 文件名含 t4543 等编号，需查库映射。
    """
    case_uuids = set()
    t_numbers = set()

    for f in TESTS_DIR.rglob("test_*.py"):
        text = f.read_text(encoding="utf-8")
        # 1. CASE_ID variable
        m = re.search(r'CASE_ID\s*=\s*["\']([^"\']+)["\']', text)
        if m and not m.group(1).startswith("None"):
            case_uuids.add(m.group(1))
        # 2. T-numbers from filename
        for tm in re.finditer(r'[._](t\d{4})', f.name.lower()):
            t_numbers.add("T" + tm.group(1)[1:].upper())

    return case_uuids, t_numbers


def main():
    env = load_env()
    client = OnesClient(env)

    # Check token, refresh if expired
    if not client.check_token():
        from ones_writer import refresh_token_via_playwright
        client.token = refresh_token_via_playwright()
        env["ONES_AUTH_TOKEN"] = client.token

    case_uuids, t_numbers = extract_auto_cases()
    print(f"本地: CASE_ID={len(case_uuids)}, 文件名T编号={len(t_numbers)}")

    # Map T-number -> UUID via library
    all_lib = client.cases_by_library()
    tnum_to_uuid = {f"T{c['number']}": c["uuid"] for c in all_lib if c.get("number")}

    auto_uuids = set(case_uuids)
    for tn in t_numbers:
        if tn in tnum_to_uuid:
            auto_uuids.add(tnum_to_uuid[tn])
    print(f"匹配到 ONES UUID: {len(auto_uuids)} 条")

    # Plan cases
    plan_cases = client.cases_by_plan(PLAN_UUID)
    plan_uuids = {c["uuid"] for c in plan_cases}
    print(f"Plan 现有: {len(plan_cases)} 条")

    to_remove = plan_uuids - auto_uuids
    to_pass = plan_uuids & auto_uuids
    to_add = auto_uuids - plan_uuids
    print(f"  需移除: {len(to_remove)}, 需标记Passed: {len(to_pass)}, 需加入: {len(to_add)}")

    # Remove
    if to_remove:
        team = client.team
        for i in range(0, len(to_remove), 50):
            chunk = list(to_remove)[i:i+50]
            body = json.dumps({"case_uuids": chunk}).encode()
            req = urllib.request.Request(
                f"{client.base}/project/api/project/team/{team}/testcase/plan/{PLAN_UUID}/cases/delete",
                data=body, method="POST",
                headers={"Authorization": f"Bearer {client.token}", "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req) as r:
                    print(f"  移除批次 {i//50+1}: {len(chunk)}")
            except urllib.error.HTTPError as e:
                print(f"  移除失败: {e.code} {e.read().decode()[:150]}")

    # Add new
    if to_add:
        team = client.team
        body = json.dumps({"case_uuids": list(to_add)}).encode()
        req = urllib.request.Request(
            f"{client.base}/project/api/project/team/{team}/testcase/plan/{PLAN_UUID}/cases/add",
            data=body, method="POST",
            headers={"Authorization": f"Bearer {client.token}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                resp = json.loads(r.read())
                added = resp.get("success_cases", [])
                print(f"  新加入: {len(added)}")
                to_pass = to_pass | set(added)
        except urllib.error.HTTPError as e:
            print(f"  加入失败: {e.code} {e.read().decode()[:150]}")

    # Mark passed
    passed = 0
    for cid in to_pass:
        key = f"testcase_plan_case-{PLAN_UUID}-{cid}"
        q = """mutation($key: String!, $result: String!) {
          updateTestcasePlanCase(key: $key, result: $result) { result }
        }"""
        status, resp = client.gql(q, {"key": key, "result": "passed"})
        if status == 200 and isinstance(resp, dict) and resp.get("data"):
            passed += 1
    print(f"  标记 Passed: {passed}")
    print("\n✅ 同步完成")


if __name__ == "__main__":
    main()
