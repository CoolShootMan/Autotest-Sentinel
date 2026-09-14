"""Migrated from Apifox case #7627714. Source folder: Customer Campaign ."""
# Apifox Case ID: 7627714  (traceability only — not needed to run)
NAME = "Verify partner can delete campaign on campaigns page"
TAGS = ["p1", "customer_campaign", "suite:linda"]
PRIORITY = 1


CASE_ID = 7627714
ENV_NAME = "Release"


import json

from core.assertions import expect

def test_linda_t4676_verify_partner_can_delete_campaign_on_campaigns_page(ctx):
    """Apifox case #7627714: Linda_T4676_Verify_partner_can_delete_campaign_on_campaigns_page"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1:
    _resp1 = ctx.api.campaigns.list(body=None, params={'search': '', 'pageSize': '30', 'pageNumber': '1'}, token='linda01_token')
    # customScript: 从 campaigns 列表筛选 name 含 "automation by linda" 且 status 为 DRAFT/COMPLETED 的任务，随机取一个 id
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    _items = ((_j1 or {}).get('data') or {}).get('items') or []
    _targets = [t.get('id') for t in _items
                if t.get('name') and t.get('status')
                and 'automation by linda' in t.get('name')
                and t.get('status') in ('DRAFT', 'COMPLETED')]
    import random as _random
    vars['randomLindaAutomationId'] = _random.choice(_targets) if _targets else ''
    # step 2:
    _resp2 = ctx.api.campaigns.by_random_linda_automation_id(body=None, token='linda01_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3:
    _resp3 = ctx.api.campaigns.list(body=None, params={'search': '', 'pageSize': '30', 'pageNumber': '1'}, token='linda01_token')
    vars['deleteVerifyResult'] = 'failed'
    vars['deleteVerifyResult'] = 'failed'
    vars['deleteVerifyResult'] = 'success'
    vars['deleteVerifyResult'] = 'failed'
