"""Migrated from Apifox case #7693353. Source folder: Collabs invite flow and coseller signup and partner signup."""
# Apifox Case ID: 7693353  (traceability only — not needed to run)
NAME = "Verify the promoter signup flow"
TAGS = ["p0", "collabs_invite_flow_and_coseller_signup_and_partner_signup", "suite:linda"]
PRIORITY = 0


CASE_ID = 7693353
ENV_NAME = "Release"

# --- step 1: 9ad7c5db-bb46-4e4e-af07-352fb39da5e5 ---
# post[customScript]: pm.environment.set("otp_request_ts", Date.now().toString());
# post: console.log("otp_request_ts =", new Date(Number(pm.environment.get("otp_request_ts"))).toISOString());
# post: 
# --- step 2: c040e9fd-b3aa-4e6b-9b4a-2cce550c433d ---
# post[customScript]: const json = pm.response.json();
# post: 
# post: pm.test("Login success", () => {
# post:   pm.expect(json.code).to.eql(200);
# post:   pm.expect(json.message).to.eql("success");
# post:   pm.expect(json.data.token).to.be.a("string").and.not.empty;
# post: });
# post: 
# post: // 保存 token
# post: pm.environment.set("auth_token", json.data.token);
# post: pm.environment.set("auth_refresh_token", json.data.refreshToken);
# post: pm.environment.set("user_id", json.data.id);
# post: 
# post: // 打印
# post: console.log("✅ Login success");
# post: console.log("user_id =", json.data.id);
# post: console.log("auth_token (masked) =", json.data.token.slice(0, 10) + "...");
# post: 
# --- step 3: b227bccf-82b6-44c8-a73c-d1f6611d3fe6 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 99541d3e-4fc5-49c6-be69-72cff6fd4d46 ---
# --- step 5: 6451e86a-f42c-4849-9961-1ab55889323d ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: 454fbf7a-685d-4bda-b2e6-df24b54fe31d ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: // 1. 获取提取到的数据库字段变量
# post: const dbUserRole = pm.variables.get("user_role");
# post: const dbType = pm.variables.get("type");
# post: const dbInvitedBy = pm.variables.get("invited_by");
# post: 
# post: // 2. 断言user_role等于BUSINESS_PARTNER
# post: pm.test("数据库返回的user_role是PROMOTER", function () {
# post:     pm.expect(dbUserRole).to.eql("PROMOTER");
# post: });
# post: 
# post: // 3. 断言type等于STANDARD
# post: pm.test("数据库返回的type是STANDARD", function () {
# post:     pm.expect(dbType).to.eql("STANDARD");
# post: });
# post: 
# post: // 4. 断言invited_by等于INVITED_BY_PEAR
# post: pm.test("数据库返回的invited_by是INVITED_BY_PEAR", function () {
# post:     pm.expect(dbInvitedBy).to.be.null;
# post: });




from core.assertions import expect

def test_linda_t3386_verify_the_promoter_signup_flow(ctx):
    """Apifox case #7693353: Linda_T3386_Verify_the_promoter_signup_flow"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 9ad7c5db-bb46-4e4e-af07-352fb39da5e5
    _resp1 = ctx.api.auth.code(body='{"email":"{{CosellerEmail}}"}')
    vars['otp_request_ts'] = 'Date.now('
    # step 2: c040e9fd-b3aa-4e6b-9b4a-2cce550c433d
    _resp2 = ctx.api.auth.promoter_login(body='{\r\n    "inviterCampaign": {},\r\n    "code": "{{gmail_code}}",\r\n    "email": "{{CosellerEmail}}"\r\n}', headers={'X-Auto-Testing': 'true'})
    ctx.extract('auth_token', _resp2, '$.data.token')
    ctx.extract('auth_refresh_token', _resp2, '$.data.refreshToken')
    ctx.extract('user_id', _resp2, '$.data.id')
    # step 3: b227bccf-82b6-44c8-a73c-d1f6611d3fe6
    _resp3 = ctx.api.auth.promoter_signup(body='{"firstName":"linda","lastName":"zhou31"}', token='auth_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # step 4: 99541d3e-4fc5-49c6-be69-72cff6fd4d46
    _resp4 = ctx.api.misc.invitation_profile(body='["katana_visitor_id"]', params={'isFirst': '1', 'signup': 'promoter'}, token='auth_token')
    # step 5: 6451e86a-f42c-4849-9961-1ab55889323d
    _resp5 = ctx.api.posts.promoter_simplify_list(body=None, params={'sortBy': 'publishedAt', 'pageSize': '30', 'pageNumber': '1'}, token='auth_token')
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # step 6: 454fbf7a-685d-4bda-b2e6-df24b54fe31d
    _resp6 = ctx.api.posts.curator_shop(body=None, params={'pageSize': '30', 'pageNumber': '1'}, token='auth_token')
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
