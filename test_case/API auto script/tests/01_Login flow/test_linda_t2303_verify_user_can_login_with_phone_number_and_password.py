"""Migrated from Apifox case #6112669. Source folder: Login flow."""
# Apifox Case ID: 6112669  (traceability only — not needed to run)
NAME = "Verify user can login with phone number and password"
TAGS = ["p0", "login_flow"]
PRIORITY = 0


CASE_ID = 6112669
ENV_NAME = "Release"

# --- step 1: 7c4016b9-fcac-40a3-a8e9-15a21ce309ec ---
# pre: 
# pre: pm.variables.set("phoneNumber","+16502396646");
# pre: pm.variables.set("password","7EbE8F4BdE4A38768AcF9C2833aF2Db5");
# pre: 
# post[assertion]: {"name": "code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "token", "variableType": "local", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "message", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_linda_t2303_verify_user_can_login_with_phone_number_and_password(ctx):
    """Apifox case #6112669: Linda_T2303_Verify_user_can_login_with_phone_number_and_password"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # phoneNumber comes from this case's .vars.yaml; password from env/Release.yaml
    # step 1: 7c4016b9-fcac-40a3-a8e9-15a21ce309ec
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "phoneNumber": "{{phoneNumber}}",\r\n    "password": "{{password}}"\r\n\r\n}', app_headers=True)
    # assertion 1.code: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # extractor: token = $.data.token
    ctx.extract('token', _resp1, '$.data.token')
    # assertion 1.message: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
