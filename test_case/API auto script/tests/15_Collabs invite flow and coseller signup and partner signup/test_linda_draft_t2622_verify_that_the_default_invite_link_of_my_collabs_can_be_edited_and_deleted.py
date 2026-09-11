"""Migrated from Apifox case #8371959. Source folder: Collabs invite flow and coseller signup and partner signup."""
# Apifox Case ID: 8371959  (traceability only — not needed to run)
NAME = "(Linda) (Draft)T2622 Verify that the default invite link of \"My Collabs\" can be edited and deleted"
TAGS = ["p2", "collabs_invite_flow_and_coseller_signup_and_partner_signup"]
PRIORITY = 2


CASE_ID = 8371959
ENV_NAME = "Release"

# --- step 1: 0ff3698e-2b07-42d3-a885-282ab23ad2e8 ---




import json

from core.assertions import expect

def test_linda_draft_t2622_verify_that_the_default_invite_link_of_my_collabs_can_be_edited_and_deleted(ctx):
    """Apifox case #8371959: Linda_Draft_T2622_Verify_that_the_default_invite_link_of_My_Collabs_can_be_edite"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 0ff3698e-2b07-42d3-a885-282ab23ad2e8
    _resp1 = ctx.api.promoters.invitation_link(body=None, token='linda05_token')
    # === 断言（源头无断言，按接口通用格式设计）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    assert _resp1.status_code == 200, f"step1 status != 200, got {_resp1.status_code}"
    assert _j1.get('code') == 200, f"step1 code != 200, got {_j1.get('code')}"
    assert _j1.get('message') == 'success', f"step1 message != success, got {_j1.get('message')}"
    _d1 = _j1.get('data')
    assert _d1 is not None, "step1 data 缺失"
    _items1 = _d1.get('items')
    assert isinstance(_items1, list) and _items1, "step1 data.items 为空"
    assert isinstance(_d1.get('totalCount'), int) and _d1['totalCount'] > 0, "step1 totalCount 不正确"
    for _it in _items1:
        assert isinstance(_it.get('id'), str) and _it.get('id'), "item 缺少 id"
        assert isinstance(_it.get('invitationCode'), str) and _it.get('invitationCode'), "item 缺少 invitationCode"
        assert isinstance(_it.get('userId'), str) and _it.get('userId'), "item 缺少 userId"
