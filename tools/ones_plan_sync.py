#!/usr/bin/env python3
"""
ONES Plan Sync — 让测试计划 RVEi7pVd 与本地自动化脚本保持一致。

操作：
1. 移除 plan 中未自动化的用例
2. 将已自动化的用例标记为 Passed
3. 新自动化的用例已通过 add API 加入
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


def main():
    env = load_env()
    client = OnesClient(env)

    # ── 1. 本地 CASE_ID 集合 ──
    local_cids = set()
    for f in TESTS_DIR.rglob("test_*.py"):
        text = f.read_text(encoding="utf-8")
        m = re.search(r'CASE_ID\s*=\s*["\']([^"\']+)["\']', text)
        if m and not m.group(1).startswith("None"):
            local_cids.add(m.group(1))
    print(f"本地自动化用例: {len(local_cids)} 条")

    # ── 2. Plan 现有用例 ──
    plan_cases = client.cases_by_plan(PLAN_UUID)
    plan_uuids = {c["uuid"] for c in plan_cases}
    print(f"Plan 现有用例: {len(plan_cases)} 条")

    # ── 3. 计算差异 ──
    to_remove = plan_uuids - local_cids
    to_pass = plan_uuids & local_cids
    print(f"  需移除（未自动化）: {len(to_remove)}")
    print(f"  需标记 Passed: {len(to_pass)}")

    # ── 4. 批量移除未自动化用例 ──
    if to_remove:
        team = client.team
        removed = 0
        for i, chunk_start in enumerate(range(0, len(to_remove), 50)):
            chunk = list(to_remove)[chunk_start:chunk_start+50]
            body = json.dumps({"case_uuids": chunk}).encode()
            req = urllib.request.Request(
                f"{client.base}/project/api/project/team/{team}/testcase/plan/{PLAN_UUID}/cases/delete",
                data=body, method="POST",
                headers={"Authorization": f"Bearer {client.token}",
                         "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req) as r:
                    removed += len(chunk)
                    print(f"  移除批次 {i+1}: {len(chunk)} 条 (累计 {removed})")
            except urllib.error.HTTPError as e:
                print(f"  移除批次 {i+1} 失败: HTTP {e.code} {e.read().decode()[:200]}")

    # ── 5. 标记自动化用例为 Passed ──
    passed = 0
    for cid in to_pass:
        key = f"testcase_plan_case-{PLAN_UUID}-{cid}"
        q = """mutation($key: String!, $result: String!) {
          updateTestcasePlanCase(key: $key, result: $result) { result }
        }"""
        status, resp = client.gql(q, {"key": key, "result": "passed"})
        if status == 200 and isinstance(resp, dict) and resp.get("data"):
            passed += 1
        else:
            print(f"  标记 {cid} 失败: {status} {str(resp)[:200]}")
    print(f"  标记 Passed: {passed}/{len(to_pass)}")

    print("\n✅ 同步完成")


if __name__ == "__main__":
    main()
