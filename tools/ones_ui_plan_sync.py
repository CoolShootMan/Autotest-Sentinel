#!/usr/bin/env python3
"""
ONES UI Plan Sync — 让测试计划 TXs6dagf 与本地 UI YAML 自动化脚本保持一致。
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

PLAN_UUID = "TXs6dagf"
YAML_DIR = PROJECT / "test_case/UI/All_YAML"


def main():
    env = load_env()
    client = OnesClient(env)

    # ── 1. 从 YAML 提取已自动化的 T 编号 ──
    auto_t_numbers = set()
    for f in YAML_DIR.rglob("*.yaml"):
        text = f.read_text(encoding="utf-8")
        # 1a. 从 testT 开头的用例名提取，支持 compound: T3683_T3684, T4600_4602, T5210_5211_5212
        for m in re.finditer(r'^test((?:T\d{4})(?:_?T?\d{4})*)', text, re.MULTILINE):
            raw = m.group(1)
            # Split: T3683_T3684 -> T3683, T3684; T4600_4602 -> T4600, T4602
            parts = re.findall(r'T?(\d{4})', raw)
            for p in parts:
                auto_t_numbers.add(f"T{p}")
        # 1b. 从注释提取: # T1742: ... 或 # T3686_teardown
        for m in re.finditer(r'#\s*(T\d{4})', text):
            auto_t_numbers.add(m.group(1))
    print(f"本地 UI 自动化用例 T 编号: {len(auto_t_numbers)} 条")
    print(f"  T编号: {sorted(auto_t_numbers)}")

    # ── 2. Plan 现有用例 ──
    plan_cases = client.cases_by_plan(PLAN_UUID)
    plan_by_tnum = {}
    for c in plan_cases:
        tnum = f"T{c.get('number', 0)}"
        plan_by_tnum[tnum] = c
    print(f"Plan 现有用例: {len(plan_cases)} 条")

    # ── 3. 匹配 ──
    auto_set = set(auto_t_numbers)
    plan_tnums = set(plan_by_tnum.keys())

    to_remove_tnums = plan_tnums - auto_set
    to_pass_tnums = plan_tnums & auto_set
    # New automated cases not in plan
    to_add_tnums = auto_set - plan_tnums

    print(f"  需移除（未自动化）: {len(to_remove_tnums)}")
    print(f"  已在 plan 需标记 Passed: {len(to_pass_tnums)}")
    print(f"  新自动化需加入: {len(to_add_tnums)}")

    # ── 4. 移除未自动化用例 ──
    if to_remove_tnums:
        remove_uuids = [plan_by_tnum[t]["uuid"] for t in to_remove_tnums]
        team = client.team
        for i in range(0, len(remove_uuids), 50):
            chunk = remove_uuids[i:i+50]
            body = json.dumps({"case_uuids": chunk}).encode()
            req = urllib.request.Request(
                f"{client.base}/project/api/project/team/{team}/testcase/plan/{PLAN_UUID}/cases/delete",
                data=body, method="POST",
                headers={"Authorization": f"Bearer {client.token}",
                         "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req) as r:
                    print(f"  移除批次 {i//50+1}: {len(chunk)} 条")
            except urllib.error.HTTPError as e:
                print(f"  移除失败: HTTP {e.code} {e.read().decode()[:200]}")

    # ── 5. 标记自动化用例为 Passed ──
    passed = 0
    for tnum in to_pass_tnums:
        case_uuid = plan_by_tnum[tnum]["uuid"]
        key = f"testcase_plan_case-{PLAN_UUID}-{case_uuid}"
        q = """mutation($key: String!, $result: String!) {
          updateTestcasePlanCase(key: $key, result: $result) { result }
        }"""
        status, resp = client.gql(q, {"key": key, "result": "passed"})
        if status == 200 and isinstance(resp, dict) and resp.get("data"):
            passed += 1
        else:
            print(f"  标记 {tnum} 失败: {status} {str(resp)[:150]}")
    print(f"  标记 Passed: {passed}/{len(to_pass_tnums)}")

    # ── 6. 新自动化用例需要先在库里找到 UUID 再加入 plan ──
    if to_add_tnums:
        # Search library for these cases
        print(f"\n  查找 {len(to_add_tnums)} 条新自动化用例的 UUID...")
        all_cases = client.cases_by_library()
        by_num = {}
        for c in all_cases:
            n = c.get("number")
            if n:
                by_num[n] = c["uuid"]

        add_uuids = []
        for tnum in to_add_tnums:
            num = int(tnum[1:])  # strip T
            if num in by_num:
                add_uuids.append(by_num[num])
            else:
                print(f"    {tnum} 不在库中，跳过")

        if add_uuids:
            team = client.team
            body = json.dumps({"case_uuids": add_uuids}).encode()
            req = urllib.request.Request(
                f"{client.base}/project/api/project/team/{team}/testcase/plan/{PLAN_UUID}/cases/add",
                data=body, method="POST",
                headers={"Authorization": f"Bearer {client.token}",
                         "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req) as r:
                    resp = json.loads(r.read())
                    added = resp.get("success_cases", [])
                    print(f"  新加入 plan: {len(added)} 条")
                    # Mark them passed too
                    for cid in added:
                        key = f"testcase_plan_case-{PLAN_UUID}-{cid}"
                        q = """mutation($key: String!, $result: String!) {
                          updateTestcasePlanCase(key: $key, result: $result) { result }
                        }"""
                        client.gql(q, {"key": key, "result": "passed"})
            except urllib.error.HTTPError as e:
                print(f"  加入失败: HTTP {e.code} {e.read().decode()[:200]}")

    print("\n✅ UI Plan 同步完成")


if __name__ == "__main__":
    main()
