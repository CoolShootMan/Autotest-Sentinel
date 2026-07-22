"""Create ONES test plan via UI and link existing cases via API."""
import json
import re
import subprocess
import sys
import time
import urllib.request
import base64
from pathlib import Path

from playwright.sync_api import sync_playwright


def load_env():
    env = {}
    with open('backend/.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def refresh_token():
    """Refresh ONES token using ones_writer.py."""
    print('Token refresh requested...')
    result = subprocess.run(
        [sys.executable, 'tools/ones_writer.py', 'refresh-token'],
        capture_output=True, text=True, encoding='utf-8'
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError('Failed to refresh ONES token')
    return load_env()['ONES_AUTH_TOKEN']


def ensure_token(env):
    """Verify token is still valid; refresh if needed."""
    token = env.get('ONES_AUTH_TOKEN', '')
    if not token:
        return refresh_token()

    import urllib.request
    base = env.get('ONES_URL', 'https://sz.ones.cn')
    req = urllib.request.Request(
        f"{base}/project/api/project/users/me",
        headers={
            'Authorization': f'Bearer {token}',
            'x-request-csrf-token': '1',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return token if resp.status == 200 else refresh_token()
    except Exception:
        return refresh_token()


def extract_plan_uuid(captured):
    """Try to extract the newly created plan UUID from captured network traffic."""
    # Look for JSON responses that contain a plan uuid
    for entry in captured:
        if 'resp' not in entry:
            continue
        resp = entry['resp']
        if resp.get('status') not in (200, 201):
            continue
        try:
            body = json.loads(resp.get('body', '{}'))
        except Exception:
            continue
        # Common shapes: {"plan": {...}} or {"item": {...}}
        for key in ('plan', 'item', 'testcasePlan'):
            obj = body.get(key) if isinstance(body, dict) else None
            if obj and isinstance(obj, dict) and obj.get('uuid'):
                return obj['uuid']
        if isinstance(body, dict) and body.get('uuid'):
            return body['uuid']
    return None


def add_cases_to_plan(plan_uuid, case_uuids, env):
    """Call ones_writer.py add-to-plan to link cases via API."""
    print(f'\nLinking {len(case_uuids)} case(s) to plan {plan_uuid}...')
    cmd = [sys.executable, 'tools/ones_writer.py', 'add-to-plan', plan_uuid] + case_uuids
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return False
    return True


def find_plan_by_name(env, plan_name, ticket_key):
    """List plans via API and find the one matching plan_name or ticket_key."""
    import urllib.request
    base = env.get('ONES_URL', 'https://ones.cn')
    team = env.get('ONES_TEAM_UUID', '')
    token = env.get('ONES_AUTH_TOKEN', '')
    url = f"{base}/project/api/project/team/{team}/testcase/plans"
    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {token}',
            'x-request-csrf-token': '1',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        plans = data.get('plans', [])
        for p in plans:
            if p.get('name') == plan_name:
                return p.get('uuid')
        # Fuzzy fallback: match by ticket key
        for p in plans:
            if ticket_key in (p.get('name') or ''):
                return p.get('uuid')
    except Exception as e:
        print(f'   find_plan_by_name error: {e}')
    return None


def fetch_jira_issue(env, issue_key):
    """Fetch QA assignee displayName and issue summary from Jira.
    Returns (qa_display_name, summary)."""
    email = env.get('JIRA_EMAIL', '')
    token = env.get('JIRA_API_TOKEN', '')
    base = env.get('JIRA_BASE_URL', '')
    if not all([email, token, base, issue_key]):
        return '', ''
    auth = base64.b64encode(f'{email}:{token}'.encode()).decode()
    url = f'{base}/rest/api/3/issue/{issue_key}?fields=customfield_10083,summary'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Basic {auth}',
        'Accept': 'application/json',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        fields = data.get('fields', {})
        qa_raw = fields.get('customfield_10083', [])
        qa_name = qa_raw[0].get('displayName', '') if qa_raw and isinstance(qa_raw, list) else ''
        summary = fields.get('summary', '')
        return qa_name, summary
    except Exception as e:
        print(f'   Could not fetch Jira issue {issue_key}: {e}')
        return '', ''


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Create ONES test plan via UI and link cases.')
    parser.add_argument('ticket', help='Jira ticket key (e.g. KAT-11397)')
    parser.add_argument('--owner', required=True,
                        help='Owner search query for ONES dropdown (e.g. yuxiao)')
    parser.add_argument('--plan-name', default=None,
                        help='Override plan name (default: "TICKET: <jira summary>")')
    args = parser.parse_args()

    env = load_env()
    TEAM = env['ONES_TEAM_UUID']
    EMAIL = env.get('ONES_EMAIL', '')
    if not EMAIL:
        raise RuntimeError('ONES_EMAIL not set in backend/.env')

    JIRAKEY = args.ticket

    # Fetch QA owner display name and issue summary from Jira
    qa_name, jira_summary = fetch_jira_issue(env, JIRAKEY)
    NAME = qa_name or 'Unknown'
    PLAN_NAME = args.plan_name or (f'{JIRAKEY}: {jira_summary}' if jira_summary else JIRAKEY)
    OWNER_QUERY = args.owner

    print(f'Ticket: {JIRAKEY}')
    print(f'Plan name: {PLAN_NAME}')
    print(f'Owner query: "{OWNER_QUERY}" (Jira QA: {NAME})')

    # Ensure API token is fresh (used later for linking cases)
    ensure_token(env)

    captured = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        def on_response(resp):
            if 'testcase/plan' in resp.url and resp.request.method in ('POST', 'PUT', 'PATCH'):
                try:
                    body = resp.body().decode('utf-8', errors='replace')
                except Exception:
                    body = ''
                captured.append({
                    'resp': {
                        'status': resp.status,
                        'url': resp.url,
                        'method': resp.request.method,
                        'body': body,
                    }
                })

        page.on('response', on_response)

        # 0. Login via UI (cookie-based session required)
        login_url = 'https://ones.cn/auth/login'
        print(f'0. Logging in at: {login_url}')
        page.goto(login_url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(3000)
        try:
            page.get_by_role('textbox', name='* 邮箱').fill(EMAIL)
            page.get_by_role('textbox', name='* 密码').fill(env['ONES_PASSWORD'])
            page.get_by_role('button', name='登录').click()
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f'   Login form error (will try to continue): {e}')
        print(f'   After login URL: {page.url}')

        # 1. Navigate to the test plan page
        url = f'https://ones.cn/project/#/testcase/team/{TEAM}/index'
        print(f'1. Navigating to: {url}')
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(5000)
        print(f'   Current URL: {page.url}')
        page.screenshot(path='data/ones_plan_list.png', full_page=True)

        # 2. Click "+ 新建测试计划"
        print('2. Looking for "新建测试计划" button...')
        create_btn = page.locator('button:has-text("新建测试计划")').first
        if create_btn.count() == 0:
            create_btn = page.get_by_role('button', name='新建测试计划').first
        if create_btn.count() == 0:
            create_btn = page.locator('button:has(> i:has-text("+")), button:has(> span:has-text("+"))').first
        if create_btn.count() == 0:
            raise RuntimeError('Could not find "新建测试计划" button')
        create_btn.click()
        page.wait_for_timeout(2000)
        page.screenshot(path='data/ones_plan_modal.png', full_page=True)
        print('   Modal opened')

        # 3. Fill plan name
        modal = page.locator('.ones-modal-wrap').first
        if modal.count() == 0:
            modal = page.locator('.ant-modal').first
        print('3. Filling plan name...')
        name_input = modal.locator('input[placeholder*="计划名称"]').first
        if name_input.count() == 0:
            name_input = modal.locator('input[placeholder*="名称"]').first
        if name_input.count() == 0:
            name_input = modal.locator('input[type="text"]').first
        if name_input.count() > 0:
            name_input.fill(PLAN_NAME)
            page.wait_for_timeout(500)
            print(f'   Name: {PLAN_NAME}')
        page.screenshot(path='data/ones_plan_name_filled.png', full_page=True)

        # 4. Set owner (负责人) — OWNER_QUERY passed from argparse
        print(f'4. Setting owner to "{OWNER_QUERY}"...')
        owner_field = page.locator('.ones-modal-wrap .ones-user-select, .ant-modal-wrap .ones-user-select, .ant-modal .ones-user-select').first
        if owner_field.count() == 0:
            owner_field = page.locator('input[placeholder="请选择"]').first
        if owner_field.count() > 0:
            owner_field.click()
            page.wait_for_timeout(2000)
            page.screenshot(path='data/ones_plan_owner_dropdown.png', full_page=True)

            # Wait for the dropdown's search input to appear and type the owner query there.
            search = page.locator('.ones-select-dropdown input[type="text"], .ant-select-dropdown input[type="text"], .ones-select-dropdown input, .ant-select-dropdown input').first
            if search.count() == 0:
                # Some selects embed the search input inside the trigger; look inside the select.
                search = owner_field.locator('input').first
            if search.count() > 0:
                search.fill(OWNER_QUERY)
                print(f'   Typed "{OWNER_QUERY}" into owner search')
                page.wait_for_timeout(1500)
                page.screenshot(path='data/ones_plan_owner_search.png', full_page=True)

                # Filter the dropdown options: only click the one that actually contains
                # the owner query. Never fall back to "first option" — that previously picked
                # "aaric.zheng" by accident because Enter highlighted a different row.
                opts = page.locator('.ones-select-dropdown .ones-select-item-option, .ones-select-dropdown .ones-select-item, .ant-select-dropdown .ant-select-item-option, .ant-select-dropdown .ant-select-item').all()
                target_opt = None
                for opt in opts:
                    text = (opt.text_content() or '').strip()
                    if OWNER_QUERY.lower() in text.lower():
                        target_opt = opt
                        print(f'   Matched owner option: {text[:60]}')
                        break
                if target_opt is None:
                    raise RuntimeError(
                        f'Owner "{OWNER_QUERY}" not found in dropdown. '
                        f'Available options: {[ (o.text_content() or "").strip()[:40] for o in opts ]}'
                    )
                target_opt.click()
                page.wait_for_timeout(500)
            else:
                raise RuntimeError('Could not locate owner search input after opening dropdown')

            # Close dropdown by clicking back on the name input (inside modal, won't close modal)
            if name_input.count() > 0:
                name_input.click()
            page.wait_for_timeout(500)
        page.screenshot(path='data/ones_plan_after_owner.png', full_page=True)

        # 5. Set phase to 功能测试 (default for ticket-based plans)
        print('5. Setting phase to 功能测试...')
        phase_label = modal.locator('.ones-form-item-label:has-text("测试阶段"), label:has-text("测试阶段")').first
        if phase_label.count() > 0:
            # Locate the select via the form item (label -> parent -> select)
            phase_select = phase_label.locator('xpath=../.././/div[contains(@class,"ones-select")][1]').first
            if phase_select.count() == 0:
                phase_select = phase_label.locator('xpath=../.././/div[contains(@class,"ant-select")][1]').first
        else:
            # Fallback: select currently showing 冒烟测试
            phase_select = modal.locator('.ones-select:has(.ones-select-selection-item:has-text("冒烟测试")), .ant-select:has(.ant-select-selection-item:has-text("冒烟测试"))').first
        if phase_select.count() > 0:
            phase_select.click()
            page.wait_for_timeout(1500)
            page.screenshot(path='data/ones_plan_phase_open.png', full_page=True)
            phase_opt = page.locator('.ones-select-dropdown .ones-select-item-option:has-text("功能测试"), .ant-select-dropdown .ant-select-item-option:has-text("功能测试")').first
            if phase_opt.count() > 0:
                phase_opt.click()
                print('   Selected 功能测试')
            else:
                print('   WARNING: 功能测试 option not found, leaving default')
            # Close dropdown by clicking back on the name input
            name_input.click() if name_input.count() > 0 else None
            page.wait_for_timeout(500)
        else:
            print('   WARNING: Could not locate phase dropdown')
        page.screenshot(path='data/ones_plan_after_phase.png', full_page=True)

        # 6. Set date (执行日期 = 日期)
        print('6. Setting date (today)...')
        picker = page.locator('.ones-modal-wrap .ones-picker, .ant-modal-wrap .ones-picker, .ant-modal .ones-picker').first
        if picker.count() == 0:
            picker = page.locator('.ones-picker').first
        if picker.count() > 0:
            picker.click()
            page.wait_for_timeout(1500)
            page.screenshot(path='data/ones_plan_date_open.png', full_page=True)
            today = page.locator('a:has-text("今天"), button:has-text("今天"), .ones-picker-today, .ant-picker-today-btn').first
            if today.count() > 0:
                today.click()
                print('   Selected today')
            # Close date picker by clicking back on the name input
            name_input.click() if name_input.count() > 0 else None
            page.wait_for_timeout(500)
        page.screenshot(path='data/ones_plan_form_complete.png', full_page=True)

        # 7. Save
        print('7. Saving plan...')
        save_btn = page.locator('button:has-text("确定")').filter(visible=True).first
        if save_btn.count() == 0 or not save_btn.is_visible():
            save_btn = page.locator('.ant-modal-footer button:has-text("确定"), .ant-modal-wrap button:has-text("确定"), .ones-modal-wrap button:has-text("确定")').first
        if save_btn.count() == 0:
            save_btn = page.locator('button:has-text("保存")').filter(visible=True).first
        if save_btn.count() == 0:
            save_btn = page.locator('button:has-text("创建")').filter(visible=True).first
        if save_btn.count() == 0:
            save_btn = page.locator('button.ones-button-primary, .ant-btn-primary').filter(visible=True).first
        if save_btn.count() == 0:
            raise RuntimeError('Could not find save/confirm button')
        save_btn.click()
        page.wait_for_timeout(5000)
        page.screenshot(path='data/ones_plan_after_save.png', full_page=True)
        print(f'   After save URL: {page.url}')

        page.wait_for_timeout(3000)
        page.screenshot(path='data/ones_plan_final.png', full_page=True)
        browser.close()

    # Save captured traffic for debugging
    captured_path = Path('data/ones_plan_create_api.json')
    captured_path.parent.mkdir(parents=True, exist_ok=True)
    with open(captured_path, 'w', encoding='utf-8') as f:
        json.dump(captured, f, indent=2, ensure_ascii=False)
    print(f'\nCaptured {len(captured)} plan API responses -> {captured_path}')

    # 7. Extract plan UUID and link cases
    plan_uuid = extract_plan_uuid(captured)
    if not plan_uuid:
        print('WARNING: Could not extract new plan UUID from network traffic.')
        print('   Falling back to API listing by plan name...')
        plan_uuid = find_plan_by_name(env, PLAN_NAME, JIRAKEY)
    if not plan_uuid:
        print('ERROR: Could not find new plan. Please check the captured API responses or manually link cases.')
        return

    print(f'\nNew plan UUID: {plan_uuid}')
    plan_meta = {
        'plan_name': PLAN_NAME,
        'plan_uuid': plan_uuid,
        'owner': NAME,
        'phase': '功能测试',
    }
    with open('data/ones_create_plan.json', 'w', encoding='utf-8') as f:
        json.dump(plan_meta, f, indent=2, ensure_ascii=False)
    print(f'Plan metadata saved to data/ones_create_plan.json')

    # Load case UUIDs from previous creation results
    results_path = Path('data/ones_create_results.json')
    if results_path.exists():
        with open(results_path, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        case_uuids = [c['uuid'] for c in cases if c.get('uuid')]
        if case_uuids:
            add_cases_to_plan(plan_uuid, case_uuids, env)
        else:
            print('No case UUIDs found in data/ones_create_results.json')
    else:
        print('data/ones_create_results.json not found; skipping case linking')


if __name__ == '__main__':
    main()
