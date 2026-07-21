"""
Update all 7 KAT-11397 test case steps via the REAL ONES REST API:

  POST /project/api/project/team/{team}/testcase/library/{library_uuid}/cases/update

Body format (captured from ONES UI):
{
  "cases": [
    {
      "uuid": "RasykFr3",
      "condition": "...",
      "desc": "...",
      "library_uuid": "XcAFFViB",
      "module_uuid": "8tMnELNg",
      "name": "...",
      "assign": "...",
      "type": "...",
      "priority": "...",
      "steps": [
        {"desc": "...", "index": 0, "key": "testcase_case_step-{uuid}",
         "result": "...", "testcaseCase": {"uuid": "RasykFr3"}, "uuid": "{uuid}"}
      ]
    }
  ]
}
"""
import json
import urllib.request
import urllib.error
import uuid
import sys


def load_env():
    env = {}
    with open('backend/.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def short_uuid():
    """Generate 8-char UUID like ONES uses."""
    return uuid.uuid4().hex[:8]


env = load_env()
team = env['ONES_TEAM_UUID']
base = env.get('ONES_URL', 'https://sz.ones.cn')
token = env['ONES_AUTH_TOKEN']

TEAM = env.get('ONES_TEAM_UUID', 'T7u1zXum')
LIBRARY_UUID = 'XcAFFViB'
MODULE_UUID = '8tMnELNg'
ASSIGN_UUID = 'HKJxJn4E'

# Type/priority UUIDs from earlier work
TYPE_UUID = '7qLS7W5f'  # functional
PRIORITY_UUIDS = {
    'highest': '3g7bLpa1',   # P0
    'high': 'VRXHXgbp',      # P1
    'normal': None,
    'low': None,
}

UUIDS = ['RasykFr3', 'KYHLfaYw', 'VPJX3dus', '3Terx3zi', 'DKhUPRof', 'GUJzYYhE', 'XPWbZjfm']

# Priority UUIDs as currently set in ONES (T1=P0, T2-T7=P1)
CASE_PRIORITY = {
    'RasykFr3': '3g7bLpa1',   # P0
    'KYHLfaYw': 'VRXHXgbp',  # P1
    'VPJX3dus': 'VRXHXgbp',
    '3Terx3zi': 'VRXHXgbp',
    'DKhUPRof': 'VRXHXgbp',
    'GUJzYYhE': 'VRXHXgbp',
    'XPWbZjfm': 'VRXHXgbp',
}


def rest_post(path, body):
    url = f'{base}{path}'
    data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        url, data=data, method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'x-request-csrf-token': '1',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')[:2000]
    except Exception as e:
        return 0, str(e)[:500]


def gql(query, variables=None):
    url = f'{base}/project/api/project/team/{team}/items/graphql'
    body = json.dumps({'query': query, 'variables': variables or {}}).encode('utf-8')
    req = urllib.request.Request(
        url, data=body, method='POST',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'x-request-csrf-token': '1'},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')[:1000]


# Load cases
with open('data/kat-11397_test_cases.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# ── Test T1 first ────────────────────────────────────────────────────────
print('=== Test: Update T1 via REST API ===\n')
case_data = cases[0]
case_uuid = UUIDS[0]
steps = []
for i, s in enumerate(case_data.get('steps', [])):
    step_uuid = short_uuid()
    steps.append({
        'desc': s.get('desc', ''),
        'index': i,
        'key': f'testcase_case_step-{step_uuid}',
        'result': s.get('result', ''),
        'testcaseCase': {'uuid': case_uuid},
        'uuid': step_uuid,
    })

body = {
    'cases': [
        {
            'uuid': case_uuid,
            'condition': case_data.get('condition', ''),
            'desc': case_data.get('desc', ''),
            'library_uuid': LIBRARY_UUID,
            'module_uuid': MODULE_UUID,
            'name': case_data['name'],
            'assign': ASSIGN_UUID,
            'type': TYPE_UUID,
            'priority': CASE_PRIORITY[case_uuid],
            'steps': steps,
        }
    ]
}

status, resp = rest_post(f'/project/api/project/team/{team}/testcase/library/{LIBRARY_UUID}/cases/update', body)
print(f'T1 update status: {status}')
print(f'Response: {json.dumps(resp, ensure_ascii=False, indent=2)[:1000]}')

if status == 200:
    # Verify
    q = 'query R($f:Filter){testcaseCaseSteps(filter:$f,orderBy:{index:ASC}){key uuid desc result index}}'
    s, r = gql(q, {'f': {'testcaseCase_in': [case_uuid]}})
    if s == 200 and isinstance(r, dict):
        saved = r.get('data', {}).get('testcaseCaseSteps', [])
        print(f'\nT1 verified steps: {len(saved)}/{len(steps)}')
        if len(saved) == len(steps):
            print('T1 OK! Proceeding to batch update all 7 cases.\n')
        else:
            print('T1 step count mismatch. Aborting batch.\n')
            sys.exit(1)
    else:
        print(f'Verify failed: {str(r)[:300]}')
        sys.exit(1)
else:
    print('T1 update failed. Aborting.\n')
    sys.exit(1)

# ── Batch update all 7 cases ─────────────────────────────────────────────
print('=== Batch update all 7 cases ===\n')
success_count = 0

for i, (case_data, case_uuid) in enumerate(zip(cases, UUIDS)):
    tag = f'T{i+1}'
    steps = []
    for j, s in enumerate(case_data.get('steps', [])):
        step_uuid = short_uuid()
        steps.append({
            'desc': s.get('desc', ''),
            'index': j,
            'key': f'testcase_case_step-{step_uuid}',
            'result': s.get('result', ''),
            'testcaseCase': {'uuid': case_uuid},
            'uuid': step_uuid,
        })

    body = {
        'cases': [
            {
                'uuid': case_uuid,
                'condition': case_data.get('condition', ''),
                'desc': case_data.get('desc', ''),
                'library_uuid': LIBRARY_UUID,
                'module_uuid': MODULE_UUID,
                'name': case_data['name'],
                'assign': ASSIGN_UUID,
                'type': TYPE_UUID,
                'priority': CASE_PRIORITY[case_uuid],
                'steps': steps,
            }
        ]
    }

    status, resp = rest_post(f'/project/api/project/team/{team}/testcase/library/{LIBRARY_UUID}/cases/update', body)

    if status == 200:
        # Verify
        s, r = gql(q, {'f': {'testcaseCase_in': [case_uuid]}})
        if s == 200 and isinstance(r, dict):
            saved = r.get('data', {}).get('testcaseCaseSteps', [])
            if len(saved) == len(steps):
                print(f'  OK  {tag}: {len(saved)} steps')
                success_count += 1
            else:
                print(f'  PARTIAL {tag}: expected {len(steps)}, got {len(saved)}')
        else:
            print(f'  API OK but verify failed {tag}: {str(r)[:200]}')
    else:
        print(f'  FAIL {tag}: {status} {str(resp)[:200]}')

print(f'\n=== Result: {success_count}/7 cases updated ===')

# Also verify via UI detail query
print('\n=== Final verification via plancase-detail ===')
for i, case_uuid in enumerate(UUIDS):
    tag = f'T{i+1}'
    s, r = gql(q, {'f': {'testcaseCase_in': [case_uuid]}})
    if s == 200 and isinstance(r, dict):
        saved = r.get('data', {}).get('testcaseCaseSteps', [])
        print(f'  {tag}: {len(saved)} steps')
    else:
        print(f'  {tag}: verify error')
