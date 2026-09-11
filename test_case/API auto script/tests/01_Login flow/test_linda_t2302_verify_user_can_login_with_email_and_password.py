"""Migrated from Apifox case #5494036. Source folder: Login flow."""
# Apifox Case ID: 5494036  (traceability only — not needed to run)
NAME = "Verify user can login with email and password"
TAGS = ["p0", "login_flow"]
PRIORITY = 0


CASE_ID = 5494036
ENV_NAME = "Release"

# --- step 1: d6fe9112-d218-4155-98f0-634820480833 ---
# pre: 
# pre: pm.variables.set("account_email_curator","linda.zhou.ext+00@1m.app");
# pre: pm.variables.set("password","7EbE8F4BdE4A38768AcF9C2833aF2Db5");
# pre: 
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "token", "variableType": "local", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "message", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_linda_t2302_verify_user_can_login_with_email_and_password(ctx):
    """Apifox case #5494036: Linda_T2302_Verify_user_can_login_with_email_and_password"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # account_email_curator comes from this case's .vars.yaml; password from env/Release.yaml
    # step 1: d6fe9112-d218-4155-98f0-634820480833
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{account_email_curator}}",\r\n    "password": "{{password}}"\r\n\r\n}', app_headers=True)
    # assertion 1.code: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # extractor: token = $.data.token
    ctx.extract('token', _resp1, '$.data.token')
    # assertion 1.message: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
