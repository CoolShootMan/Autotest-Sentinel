"""Migrated from Apifox case #8604667. Source folder: Login flow."""
# Apifox Case ID: 8604667  (traceability only — not needed to run)
NAME = "Precondition - obtain all accounts token"
TAGS = ["p0", "login_flow", "suite:linda"]
PRIORITY = 0


CASE_ID = 8604667
ENV_NAME = "Release"

# --- step 1: c7f494a6-dffa-477a-bbe1-c97568f3181f ---
# post[customScript]: // 1. 解析响应数据
# post: const jsonData = pm.response.json();
# post: 
# post: // 2. 断言
# post: pm.test("Status code is 201", function () {
# post:     pm.response.to.have.status(201);
# post: });
# post: 
# post: pm.test("Response code is 200 and message is success", function () {
# post:     pm.expect(jsonData.code).to.eql(200);
# post:     pm.expect(jsonData.message).to.eql("success");
# post:     pm.expect(jsonData.data.token).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: // 3. 将 token 提取并设置为环境变量 admin_token
# post: if (jsonData.data && jsonData.data.token) {
# post:     pm.environment.set("admin_token", jsonData.data.token);
# post: }
# --- step 2: Get Partner linda00 token ---
# post[extractor]: {"variableName": "linda00_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 3: Get Partner linda01 token ---
# post[extractor]: {"variableName": "linda01_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 4: Get Partner linda05 token ---
# post[extractor]: {"variableName": "linda05_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: Get Partner xuan22 token ---
# post[extractor]: {"variableName": "xuan22_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: Get Co-seller linda06 token ---
# post[extractor]: {"variableName": "linda06_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: Get consumer linda10 token ---
# post[extractor]: {"variableName": "linda10_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: 8fe52a2b-549e-4b7c-b05f-e23267a11b20 ---
# post[extractor]: {"variableName": "yuxiao999_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: 84f647aa-5119-4add-bd41-89431821320f ---
# post[extractor]: {"variableName": "yuxiao998_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_linda_t0000_precondition_obtain_all_accounts_token(ctx):
    """Apifox case #8604667: Linda_T0000_Precondition_obtain_all_accounts_token"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: c7f494a6-dffa-477a-bbe1-c97568f3181f
    _resp1 = ctx.api.admin.auth_login(body='{"email":"{{admin_email}}","password":"{{adminpassword}}"}')
    ctx.extract('admin_token', _resp1, '$.data.token')
    # step 2: Get Partner linda00 token
    _resp2 = ctx.api.auth.sign_in(body='{\n    "password": "{{password}}",\n    "email": "{{p00_email}}"\n}')
    # extractor: linda00_token = $.data.token
    ctx.extract('linda00_token', _resp2, '$.data.token')
    # step 3: Get Partner linda01 token
    _resp3 = ctx.api.auth.sign_in(body='{\n    "password": "{{password}}",\n    "email": "{{p01_email}}"\n}')
    # extractor: linda01_token = $.data.token
    ctx.extract('linda01_token', _resp3, '$.data.token')
    # step 4: Get Partner linda05 token
    _resp4 = ctx.api.auth.sign_in(body='{\n    "email": "{{p05_email}}",\n    "password": "{{password}}"\n}')
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp4, '$.data.token')
    # step 5: Get Partner xuan22 token
    _resp5 = ctx.api.auth.sign_in(body='{\n    "email": "{{xuan_email}}",\n    "password": "{{xuan_password}}"\n}')
    # extractor: xuan22_token = $.data.token
    ctx.extract('xuan22_token', _resp5, '$.data.token')
    # step 6: Get Co-seller linda06 token
    _resp6 = ctx.api.auth.sign_in(body='{\n    "email": "{{p06_email}}",\n    "password": "{{password}}"\n}')
    # extractor: linda06_token = $.data.token
    ctx.extract('linda06_token', _resp6, '$.data.token')
    # step 7: Get consumer linda10 token
    _resp7 = ctx.api.auth.sign_in(body='{\n    "email": "{{p10_email}}",\n    "password": "{{password}}"\n}')
    # extractor: linda10_token = $.data.token
    ctx.extract('linda10_token', _resp7, '$.data.token')
    # step 8: 8fe52a2b-549e-4b7c-b05f-e23267a11b20
    _resp8 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{UIauto_partner_email}}",\r\n    "password": "{{password}}"\r\n\r\n}', app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    ctx.extract('yuxiao999_token', _resp8, '$.data.token')
    # step 9: 84f647aa-5119-4add-bd41-89431821320f
    _resp9 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{UIauto_coseller_email}}",\r\n    "password": "{{password}}"\r\n\r\n}', app_headers=True)
    # extractor: yuxiao998_token = $.data.token
    ctx.extract('yuxiao998_token', _resp9, '$.data.token')
    # Persist tokens so later cases (which depend on t0000's output) can read them.
    _tokens = {k: vars.get(k) for k in [
        "admin_token", "linda00_token", "linda01_token", "linda05_token",
        "xuan22_token", "linda06_token", "linda10_token",
        "yuxiao999_token", "yuxiao998_token",
    ] if vars.get(k)}
    ctx.save_runtime(list(_tokens))
    # Precondition assertions: tokens must be real, non-empty strings.
    for _k in ["admin_token", "linda00_token", "linda01_token"]:
        assert _tokens.get(_k), f"precondition failed: {_k} not obtained"
