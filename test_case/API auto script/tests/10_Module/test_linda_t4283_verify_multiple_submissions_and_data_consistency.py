"""Migrated from Apifox case #7919438. Source folder: Module."""
# Apifox Case ID: 7919438  (traceability only — not needed to run)
NAME = "Verify multiple submissions and data consistency"
TAGS = ["p1", "module", "suite:linda"]
PRIORITY = 1


CASE_ID = 7919438
ENV_NAME = "Release"

# --- step 1: guest get token ---
# pre: 
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 2: 3a69c561-1d5c-4895-8bc0-f411db340189 ---




from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t4283_verify_multiple_submissions_and_data_consistency(ctx: "Context"):
    """Apifox case #7919438: Linda_T4283_Verify_multiple_submissions_and_data_consistency"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    }, app_headers=False)
    # extractor: access_token = $.data
    ctx.extract('access_token', _resp1, '$.data')
    # step 2: 3a69c561-1d5c-4895-8bc0-f411db340189
    _resp2 = ctx.api.misc.submit(body={
        "contactId": "3084fc10-adfb-4dfd-bc22-e72d94e75848",
        "emailMessage": [
            {
                "id": "3c6bb0bc-8992-475e-a72d-0b39e9111ec5",
                "userContactFormId": "3084fc10-adfb-4dfd-bc22-e72d94e75848",
                "title": "Name",
                "field": "SHORT_ANSWER",
                "required": True,
                "position": 1,
                "description": None,
                "tooltip": None,
                "extensions": None,
                "createdAt": "2026-02-02T09:26:26.398Z",
                "updatedAt": "2026-02-06T06:22:36.647Z",
                "deletedAt": None,
                "content": "lindatest",
                "fieldId": "3c6bb0bc-8992-475e-a72d-0b39e9111ec5",
            },
            {
                "id": "7ef1e7ee-0982-43d0-b8b8-a9d48c6cca0b",
                "userContactFormId": "3084fc10-adfb-4dfd-bc22-e72d94e75848",
                "title": "Email",
                "field": "EMAIL_ADDRESS",
                "required": True,
                "position": 2,
                "description": None,
                "tooltip": None,
                "extensions": None,
                "createdAt": "2026-02-02T09:26:26.398Z",
                "updatedAt": "2026-02-06T06:22:36.647Z",
                "deletedAt": None,
                "content": "linda.zhou.ext+100@1m.app",
                "fieldId": "7ef1e7ee-0982-43d0-b8b8-a9d48c6cca0b",
            },
            {
                "id": "c4f10fe1-a75a-471f-8f6d-df6edca14c72",
                "userContactFormId": "3084fc10-adfb-4dfd-bc22-e72d94e75848",
                "title": "Instagram",
                "field": "SOCIAL",
                "required": False,
                "position": 3,
                "description": "",
                "tooltip": "",
                "extensions": {
                    "socialPlatform": "INSTAGRAM",
                },
                "createdAt": "2026-02-02T09:26:49.320Z",
                "updatedAt": "2026-02-06T06:22:36.647Z",
                "deletedAt": None,
                "content": "",
                "fieldId": "c4f10fe1-a75a-471f-8f6d-df6edca14c72",
            },
        ],
    }, token='access_token')
    # --- assertions: no fake-green (non-4xx/5xx) ---
    assert _resp1.status_code < 400, f"step1 got HTTP {_resp1.status_code}: {_resp1.text[:200]}"
    assert _resp2.status_code < 400, f"step2 got HTTP {_resp2.status_code}: {_resp2.text[:200]}"
