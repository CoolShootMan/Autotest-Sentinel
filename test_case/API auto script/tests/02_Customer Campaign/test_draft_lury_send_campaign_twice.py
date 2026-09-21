"""Migrated from Apifox case #8620168. Source folder: Customer Campaign ."""
# Apifox Case ID: 8620168  (traceability only — not needed to run)
NAME = "Draft (Lury) send campaign twice"
TAGS = ["p0", "customer_campaign"]
PRIORITY = 0


CASE_ID = 8620168
ENV_NAME = "Release"

# --- step 1: 34ac0960-4452-4fcd-b24c-c71e94d78ff0 ---




from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_draft_lury_send_campaign_twice(ctx: "Context"):
    """Apifox case #8620168: Draft_Lury_send_campaign_twice"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 34ac0960-4452-4fcd-b24c-c71e94d78ff0
    _resp1 = ctx.api.campaigns.send_campaign(
    body={
        "campaignId": "{{campaignId}}",
        "channel": "SMS",
        "paymentBreakdown": {"CAMPAIGN": 2.01},
    },
    token='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI4YzI2MDA3OC0xZTRiLTRmY2YtYWFkYi03MTkwYjgzZDQ1ZDkiLCJlbnYiOiJyZWxlYXNlIiwidXNlclJvbGUiOiJCVVNJTkVTU19QQVJUTkVSIiwidXNlclR5cGUiOiJTVEFOREFSRCIsInBob25lTnVtYmVyIjoiIiwiZW1haWwiOiJ6aGl5b25nLnNvbmcuZXh0QDFtLmFwcCIsImlhdCI6MTc3MjQzNDgwOSwiZXhwIjoxNzcyNDM0OTI5fQ.2gvUCLXZLBCMjB1fSJkotEViRP5xw0k7qcrunuCG37M',
)
    assert _resp1.status_code == 200, f"step1 send-campaign: {_resp1.status_code} {_resp1.text}"
