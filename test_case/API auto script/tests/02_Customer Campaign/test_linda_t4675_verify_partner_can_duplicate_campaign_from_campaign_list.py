"""Auto-generated from Apifox case #7631342. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 7631342
# Folder: 
# Case: (Linda)T4675 Verify partner can duplicate campaign from campaign list
# Priority: P2
# Created: 2025-12-11T08:23:45.000Z
# Updated: 2026-08-11T03:32:10.000Z


CASE_ID = 7631342
ENV_NAME = "Release"


import json

from core.assertions import expect

from core.compat import LegacyClient, legacy_render, legacy_url

def test__7631342__Linda_T4675_Verify_partner_can_duplicate_campaign_from_campaign_list(ctx):
    """Apifox case #7631342: Linda_T4675_Verify_partner_can_duplicate_campaign_from_campaign_list"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    base_url = ctx.base_url
    client = LegacyClient(ctx)
    _render = legacy_render(ctx)
    _url = legacy_url(ctx)
    # === Steps ===
    # step 1:
    # Fix: 原逻辑限定 COMPLETED 状态 + 固定第 8 页，环境无 COMPLETED 数据导致空 id。
    # 改为多页拉取合并，按 updatedAt 取最新 Email/SMS 任务（任意状态均可被 duplicate）。
    _emailAll, _smsAll = [], []
    for _pg in range(1, 6):
        _resp1 = client.session().request(
            'GET',
            _url(base_url, '/campaigns?search=automation&pageSize=100&pageNumber=' + str(_pg), vars),
            headers={k:_render(v, vars) for k, v in [('Pear-AutoTesting', '{{Pear-AutoTesting}}'), ('Pear-Client-Id', '{{pear_client_id}}'), ('Pear-Client-Secret', '{{pear_client_secret}}'), ('Authorization', 'Bearer {{linda01_token}}')]},
            data=None,
        )
        _items = (_resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}).get('data', {}).get('items', []) or []
        _emailAll += [t for t in _items if t.get('name') == 'automation by linda Email' and t.get('channel') == 'EMAIL' and '- copy' not in (t.get('name') or '')]
        _smsAll += [t for t in _items if t.get('name') == 'automation by linda SMS' and t.get('channel') == 'SMS' and '- copy' not in (t.get('name') or '')]
        if len(_items) < 100:
            break
    _emailAll.sort(key=lambda t: t.get('updatedAt', '') or '', reverse=True)
    _smsAll.sort(key=lambda t: t.get('updatedAt', '') or '', reverse=True)
    vars['emailCompletedId'] = _emailAll[0].get('id', '') if _emailAll else ''
    vars['smsCompletedId'] = _smsAll[0].get('id', '') if _smsAll else ''
    # step 2: Duplicate EMAIL campaign
    _resp2 = ctx.api.campaigns.duplicate(
        body={"fromId": "{{emailCompletedId}}"},
        token='linda01_token',
    )
    vars['newEmailCampaignId'] = (_resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}).get('data', {}).get('id', '')
    # assertion 2.assertion: responseJson equal DRAFT
    expect(_resp2).json('$.data.status').equals('DRAFT')
    # assertion 2.assertion: responseJson equal NOT_STARTED
    expect(_resp2).json('$.data.sentStatus').equals('NOT_STARTED')
    # step 3: Save recipients for duplicated EMAIL campaign
    _resp3 = ctx.api.campaigns.save_recipients(
        body={
            "campaignId": "{{newEmailCampaignId}}",
            "channel": "EMAIL",
            "isSelectAll": False,
            "followerIds": ["5617efb6-1b25-4b22-af65-5a76ca51dcea"],
            "searchKey": "",
        },
        token='linda01_token',
    )
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # assertion 3.assertion: responseJson equal DRAFT
    expect(_resp3).json('$.data.status').equals('DRAFT')
    # assertion 3.assertion: responseJson equal UNPAID
    expect(_resp3).json('$.data.paymentStatus').equals('UNPAID')
    # step 4: Verify duplicated EMAIL campaign details
    _resp4 = ctx.api.campaigns.by_campaign_id(
        body={
            "id": "{{newEmailCampaignId}}",
            "name": "automation by linda Email",
            "status": "DRAFT",
            "paymentStatus": "UNPAID",
            "channel": "Email",
            "content": "Subject: Your Order #7892 Has Shipped!",
            "selectAll": False,
            "totalSelectedCount": 1,
            "totalSegments": 1,
            "fixedFee": 2,
            "unitPrice": 0.01,
            "totalToPay": 2.01,
            "usageFee": 0.01,
            "paymentBreakdown": {"PAYOUT": 2.01, "DEPOSIT": 0, "CAMPAIGN": 0},
        },
        token='linda01_token',
        path_vars={'campaignId': '{{newEmailCampaignId}}'},
    )
    # step 5: Duplicate SMS campaign
    _resp5 = ctx.api.campaigns.duplicate(
        body={"fromId": "{{smsCompletedId}}"},
        token='linda01_token',
    )
    vars['newSMSCampaignId'] = (_resp5.json() if _resp5.headers.get('content-type', '').startswith('application/json') else {}).get('data', {}).get('id', '')
    # assertion 5.assertion: responseJson equal DRAFT
    expect(_resp5).json('$.data.status').equals('DRAFT')
    # assertion 5.assertion: responseJson equal NOT_STARTED
    expect(_resp5).json('$.data.sentStatus').equals('NOT_STARTED')
    # step 6: Save recipients for duplicated SMS campaign
    _resp6 = ctx.api.campaigns.save_recipients(
        body={
            "campaignId": "{{newSMSCampaignId}}",
            "channel": "SMS",
            "isSelectAll": False,
            "followerIds": ["bbf4a1ee-d93d-4e92-9e73-53ba168d7a66"],
            "searchKey": "",
        },
        token='linda01_token',
    )
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # assertion 6.assertion: responseJson equal DRAFT
    expect(_resp6).json('$.data.status').equals('DRAFT')
    # assertion 6.assertion: responseJson equal UNPAID
    expect(_resp6).json('$.data.paymentStatus').equals('UNPAID')
    # step 7: Verify duplicated SMS campaign details
    _resp7 = ctx.api.campaigns.by_campaign_id(
        body={
            "id": "{{newSMSCampaignId}}",
            "name": "automation by linda SMS",
            "status": "DRAFT",
            "paymentStatus": "UNPAID",
            "channel": "SMS",
            "content": "Subject: Your Order #7892 Has Shipped!",
            "selectAll": False,
            "totalSelectedCount": 1,
            "totalSegments": 1,
            "fixedFee": 2,
            "unitPrice": 0.01,
            "totalToPay": 2.01,
            "usageFee": 0.01,
            "paymentBreakdown": {"PAYOUT": 2.01, "DEPOSIT": 0, "CAMPAIGN": 0},
        },
        token='linda01_token',
        path_vars={'campaignId': '{{newSMSCampaignId}}'},
    )
