"""Migrated from Apifox case #7688715. Source folder: Collabs invite flow and coseller signup and partner signup."""
# Apifox Case ID: 7688715  (traceability only — not needed to run)
NAME = "Verifying the partner-signup link allows the user to register properly and be redirected to the my shop page"
TAGS = ["p0", "collabs_invite_flow_and_coseller_signup_and_partner_signup", "suite:linda"]
PRIORITY = 0


CASE_ID = 7688715
ENV_NAME = "Release"

# --- step 1: bc8e6063-e7c4-403d-8868-c778a8b58574 ---
# post[customScript]: pm.environment.set("otp_request_ts", Date.now().toString());
# post: console.log("otp_request_ts =", new Date(Number(pm.environment.get("otp_request_ts"))).toISOString());
# post: 
# --- step 2: c82e7033-66f9-4465-b1e6-a2650afc0fc5 ---
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
# --- step 3: 4a6f81ee-6d37-4d7b-aafe-473e3a30eb6b ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: // 1. 获取提取到的数据库字段变量
# post: const dbUserRole = pm.variables.get("user_role");
# post: const dbType = pm.variables.get("type");
# post: const dbInvitedBy = pm.variables.get("invited_by");
# post: 
# post: // 2. 断言user_role等于BUSINESS_PARTNER
# post: pm.test("数据库返回的user_role是BUSINESS_PARTNER", function () {
# post:     pm.expect(dbUserRole).to.eql("BUSINESS_PARTNER");
# post: });
# post: 
# post: // 3. 断言type等于STANDARD
# post: pm.test("数据库返回的type是STANDARD", function () {
# post:     pm.expect(dbType).to.eql("STANDARD");
# post: });
# post: 
# post: // 4. 断言invited_by等于INVITED_BY_PEAR
# post: pm.test("数据库返回的invited_by是INVITED_BY_PEAR", function () {
# post:     pm.expect(dbInvitedBy).to.eql("INVITED_BY_PEAR");
# post: });




from core.assertions import expect

def test_linda_t3096_verifying_the_partner_signup_link_allows_the_user_to_register_properly_and_be_redirected_to_the_my(ctx):
    """Apifox case #7688715: Linda_T3096_Verifying_the_partner_signup_link_allows_the_user_to_register_proper"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: bc8e6063-e7c4-403d-8868-c778a8b58574
    _resp1 = ctx.api.auth.code(body='{"email":"{{PartnerEmail}}"}')
    vars['otp_request_ts'] = 'Date.now('
    # step 2: c82e7033-66f9-4465-b1e6-a2650afc0fc5
    _resp2 = ctx.api.auth.merchant_login(body='{\r\n    "inviterCampaign": {},\r\n    "code": "{{gmail_code}}",\r\n    "email": "{{PartnerEmail}}"\r\n}', headers={'X-Auto-Testing': 'true'})
    ctx.extract('auth_token', _resp2, '$.data.token')
    ctx.extract('auth_refresh_token', _resp2, '$.data.refreshToken')
    ctx.extract('user_id', _resp2, '$.data.id')
    # step 3: 4a6f81ee-6d37-4d7b-aafe-473e3a30eb6b
    _resp3 = ctx.api.posts.curator_shop(body=None, params={'pageSize': '30', 'pageNumber': '1'}, token='auth_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
