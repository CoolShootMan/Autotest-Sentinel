"""Migrated from Apifox case #5451512. Source folder: Subdomain."""
# Apifox Case ID: 5451512  (traceability only — not needed to run)
NAME = "Verify multiple subdomain point to the same shop, go visit success"
TAGS = ["p0", "subdomain", "suite:linda"]
PRIORITY = 0


CASE_ID = 5451512
ENV_NAME = "Release"

# --- step 1: notip.com.cn ---
# post[customScript]: // 验证状态码是否为 200
# post: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: // 验证返回的是否为 HTML 格式
# post: pm.test("Content-Type is HTML", function () {
# post:     pm.expect(pm.response.headers.get("Content-Type")).to.include("text/html");
# post: });
# post: 
# post: // 验证网页源码中是否包含特定文字
# post: pm.test("Body contains specific text", function () {
# post:     pm.expect(pm.response.text()).to.include("katana");
# post: });
# --- step 2: notip.com.cm/promoter ---
# post[customScript]: // 验证状态码是否为 200
# post: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: // 验证返回的是否为 HTML 格式
# post: pm.test("Content-Type is HTML", function () {
# post:     pm.expect(pm.response.headers.get("Content-Type")).to.include("text/html");
# post: });
# post: 
# post: // 验证网页源码中是否包含特定文字
# post: pm.test("Body contains specific text", function () {
# post:     pm.expect(pm.response.text()).to.include("katana");
# post: });
# --- step 3: notip.com.cn/promoter/postdetail ---
# post[customScript]: // 验证状态码是否为 200
# post: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: // 验证返回的是否为 HTML 格式
# post: pm.test("Content-Type is HTML", function () {
# post:     pm.expect(pm.response.headers.get("Content-Type")).to.include("text/html");
# post: });
# post: 
# post: // 验证网页源码中是否包含特定文字
# post: pm.test("Body contains specific text", function () {
# post:     pm.expect(pm.response.text()).to.include("katana");
# post: });
# --- step 4: suddomain ---
# post[customScript]: // 验证状态码是否为 200
# post: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: // 验证返回的是否为 HTML 格式
# post: pm.test("Content-Type is HTML", function () {
# post:     pm.expect(pm.response.headers.get("Content-Type")).to.include("text/html");
# post: });
# post: 
# post: // 验证网页源码中是否包含特定文字
# post: pm.test("Body contains specific text", function () {
# post:     pm.expect(pm.response.text()).to.include("katana");
# post: });
# --- step 5: subdomain post detail ---
# post[customScript]: // 验证状态码是否为 200
# post: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: // 验证返回的是否为 HTML 格式
# post: pm.test("Content-Type is HTML", function () {
# post:     pm.expect(pm.response.headers.get("Content-Type")).to.include("text/html");
# post: });
# post: 
# post: // 验证网页源码中是否包含特定文字
# post: pm.test("Body contains specific text", function () {
# post:     pm.expect(pm.response.text()).to.include("katana");
# post: });
# --- step 6: subdomain/promoter/postdetail ---
# post[customScript]: // 验证状态码是否为 200
# post: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# post: 
# post: // 验证返回的是否为 HTML 格式
# post: pm.test("Content-Type is HTML", function () {
# post:     pm.expect(pm.response.headers.get("Content-Type")).to.include("text/html");
# post: });
# post: 
# post: // 验证网页源码中是否包含特定文字
# post: pm.test("Body contains specific text", function () {
# post:     pm.expect(pm.response.text()).to.include("katana");
# post: });




from core.assertions import expect

def test_linda_t3024_verify_multiple_subdomain_point_to_the_same_shop_go_visit_success(ctx):
    """Apifox case #5451512: Linda_T3024_Verify_multiple_subdomain_point_to_the_same_shop_go_visit_success"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: notip.com.cn
    _resp1 = ctx.api.external.list()
    # step 2: notip.com.cm/promoter
    _resp2 = ctx.api.external.lindazhou_curator()
    # step 3: notip.com.cn/promoter/postdetail
    _resp3 = ctx.api.misc.linda_post_lindapromoter()
    # step 4: suddomain
    _resp4 = ctx.api.misc.list()
    # step 5: subdomain post detail
    _resp5 = ctx.api.posts.tiubyg()
    # step 6: subdomain/promoter/postdetail
    _resp6 = ctx.api.external.demi_release_post_538yja()
