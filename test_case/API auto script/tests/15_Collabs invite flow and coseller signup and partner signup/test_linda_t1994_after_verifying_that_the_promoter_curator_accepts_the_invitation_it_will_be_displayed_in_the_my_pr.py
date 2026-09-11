"""Migrated from Apifox case #7708861. Source folder: Collabs invite flow and coseller signup and partner signup."""
# Apifox Case ID: 7708861  (traceability only — not needed to run)
NAME = "After verifying that the Promoter/Curator accepts the invitation, it will be displayed in the My promoters/My Curator list"
TAGS = ["p2", "collabs_invite_flow_and_coseller_signup_and_partner_signup", "suite:linda"]
PRIORITY = 2


CASE_ID = 7708861
ENV_NAME = "Release"

# --- step 1: edd8f0c2-5016-4c4d-958c-6bd0a2e3cc64 ---
# pre: // 生成 100 到 999 之间的随机整数
# pre: const randomNum = Math.floor(Math.random() * (999 - 100 + 1)) + 100;
# pre: 
# pre: // 拼接成目标邮箱格式
# pre: const dynamicEmail = `linda.zhou.ext+${randomNum}@1m.app`;
# pre: 
# pre: // 将生成的邮箱设置为全局临时变量，变量名为 "dynamic_email"
# pre: pm.variables.set("dynamic_email", dynamicEmail);
# pre: 
# pre: // 在控制台打印，方便调试查看
# pre: console.log("生成的随机邮箱是: " + dynamicEmail);
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
# --- step 2: accept Invite By Promoter ---
# --- step 3: 01a670e4-daf9-412b-aa97-a22db28795ef ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 9a6f7c7f-0026-4639-9c49-d7535e8755db ---
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
# post: pm.test("数据库返回的invited_by是INVITED_BY_CURATOR", function () {
# post:     pm.expect(dbInvitedBy).to.be.eql("INVITED_BY_CURATOR");
# post: });




from core.assertions import expect

def test_linda_t1994_after_verifying_that_the_promoter_curator_accepts_the_invitation_it_will_be_displayed_in_the_my_pr(ctx):
    """Apifox case #7708861: Linda_T1994_After_verifying_that_the_Promoter_Curator_accepts_the_invitation_it_"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['dynamic_email'] = 'dynamicEmail'
    # step 1: edd8f0c2-5016-4c4d-958c-6bd0a2e3cc64
    _resp1 = ctx.api.auth.promoter_login(body='{\r\n    "inviterCampaign": {},\r\n    "code": "0000",\r\n    "email": "{{CosellerEmailT1994}}"\r\n}', headers={'X-Auto-Testing': 'true'})
    ctx.extract('auth_token', _resp1, '$.data.token')
    ctx.extract('auth_refresh_token', _resp1, '$.data.refreshToken')
    ctx.extract('user_id', _resp1, '$.data.id')
    # step 2: accept Invite By Promoter
    _resp2 = ctx.api.promoters.promoter(body='{\n    "lead": "SELF_LISTING",\n    "promoterInvitationCode": "u1balj"\n}', token='auth_token')
    # step 3: 01a670e4-daf9-412b-aa97-a22db28795ef
    _resp3 = ctx.api.auth.promoter_signup(body='{"firstName":"linda","lastName":"zhou32"}', token='auth_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # step 4: 9a6f7c7f-0026-4639-9c49-d7535e8755db
    _resp4 = ctx.api.posts.curator_shop(body=None, params={'pageSize': '30', 'pageNumber': '1'}, token='auth_token')
    # assertion 4.assertion: responseJson equal 200
    expect(_resp4).json('$.code').equals('200')
