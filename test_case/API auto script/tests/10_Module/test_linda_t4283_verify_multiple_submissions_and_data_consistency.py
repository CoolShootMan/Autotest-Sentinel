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




from core.assertions import expect

def test_linda_t4283_verify_multiple_submissions_and_data_consistency(ctx):
    """Apifox case #7919438: Linda_T4283_Verify_multiple_submissions_and_data_consistency"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body='{\n    "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda"\n}', app_headers=False)
    # extractor: access_token = $.data
    ctx.extract('access_token', _resp1, '$.data')
    # step 2: 3a69c561-1d5c-4895-8bc0-f411db340189
    _resp2 = ctx.api.misc.submit(body='{\r\n    "contactId": "3084fc10-adfb-4dfd-bc22-e72d94e75848",\r\n    "emailMessage": [\r\n        {\r\n            "id": "3c6bb0bc-8992-475e-a72d-0b39e9111ec5",\r\n            "userContactFormId": "3084fc10-adfb-4dfd-bc22-e72d94e75848",\r\n            "title": "Name",\r\n            "field": "SHORT_ANSWER",\r\n            "required": true,\r\n            "position": 1,\r\n            "description": null,\r\n            "tooltip": null,\r\n            "extensions": null,\r\n            "createdAt": "2026-02-02T09:26:26.398Z",\r\n            "updatedAt": "2026-02-06T06:22:36.647Z",\r\n            "deletedAt": null,\r\n            "content": "lindatest",\r\n            "fieldId": "3c6bb0bc-8992-475e-a72d-0b39e9111ec5"\r\n        },\r\n        {\r\n            "id": "7ef1e7ee-0982-43d0-b8b8-a9d48c6cca0b",\r\n            "userContactFormId": "3084fc10-adfb-4dfd-bc22-e72d94e75848",\r\n            "title": "Email",\r\n            "field": "EMAIL_ADDRESS",\r\n            "required": true,\r\n            "position": 2,\r\n            "description": null,\r\n            "tooltip": null,\r\n            "extensions": null,\r\n            "createdAt": "2026-02-02T09:26:26.398Z",\r\n            "updatedAt": "2026-02-06T06:22:36.647Z",\r\n            "deletedAt": null,\r\n            "content": "linda.zhou.ext+100@1m.app",\r\n            "fieldId": "7ef1e7ee-0982-43d0-b8b8-a9d48c6cca0b"\r\n        },\r\n        {\r\n            "id": "c4f10fe1-a75a-471f-8f6d-df6edca14c72",\r\n            "userContactFormId": "3084fc10-adfb-4dfd-bc22-e72d94e75848",\r\n            "title": "Instagram",\r\n            "field": "SOCIAL",\r\n            "required": false,\r\n            "position": 3,\r\n            "description": "",\r\n            "tooltip": "",\r\n            "extensions": {\r\n                "socialPlatform": "INSTAGRAM"\r\n            },\r\n            "createdAt": "2026-02-02T09:26:49.320Z",\r\n            "updatedAt": "2026-02-06T06:22:36.647Z",\r\n            "deletedAt": null,\r\n            "content": "",\r\n            "fieldId": "c4f10fe1-a75a-471f-8f6d-df6edca14c72"\r\n        }\r\n    ]\r\n}', token='access_token')
    # --- assertions: no fake-green (non-4xx/5xx) ---
    assert _resp1.status_code < 400, f"step1 got HTTP {_resp1.status_code}: {_resp1.text[:200]}"
    assert _resp2.status_code < 400, f"step2 got HTTP {_resp2.status_code}: {_resp2.text[:200]}"
