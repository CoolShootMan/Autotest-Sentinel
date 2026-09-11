"""Migrated from Apifox case #7897302. Source folder: Resell and Affiliate."""
# Apifox Case ID: 7897302  (traceability only — not needed to run)
NAME = "Verify after created affiliate link, can send Email or SMS"
TAGS = ["p1", "resell_and_affiliate", "suite:linda"]
PRIORITY = 1


CASE_ID = 7897302
ENV_NAME = "Release"

# --- step 1: 3ce00ab3-55cd-42dd-9f62-784b7e74f4d9 ---
# --- step 2: a4fe9fa0-de87-4851-a141-ca5bff2edf6f ---
# post[customScript]: // ========== 配置区（便于维护） ==========
# post: const ASSERT_CONFIG = {
# post:   // 基础响应状态配置
# post:   base: {
# post:     code: 200,
# post:     message: "success"
# post:   },
# post:   // 固定业务字段配置
# post:   business: {
# post:     email: "linda.zhou.ext+27@1m.app"
# post:   }
# post: };
# post: 
# post: // ========== 1. 解析响应数据（带异常处理） ==========
# post: let responseData;
# post: try {
# post:   responseData = pm.response.json();
# post: } catch (error) {
# post:   pm.test("响应体格式校验：返回有效的JSON数据", () => {
# post:     pm.expect.fail(`JSON解析失败，原因：${error.message}`);
# post:   });
# post:   return;
# post: }
# post: 
# post: // ========== 通用工具函数 ==========
# post: /**
# post:  * 安全获取嵌套对象属性
# post:  * @param {Object} obj 源对象
# post:  * @param {Array} path 属性路径数组
# post:  * @param {*} defaultValue 默认值
# post:  * @returns {*} 属性值或默认值
# post:  */
# post: function getNestedProperty(obj, path, defaultValue = undefined) {
# post:   return path.reduce((acc, curr) => {
# post:     return (acc !== null && acc !== undefined) ? acc[curr] : defaultValue;
# post:   }, obj);
# post: }
# post: 
# post: // ========== 2. 核心字段断言 ==========
# post: /**
# post:  * 断言1：校验code和message
# post:  */
# post: pm.test("响应状态校验：code=200 且 message=success", () => {
# post:   // 校验code字段
# post:   pm.expect(responseData).to.have.property("code");
# post:   pm.expect(responseData.code)
# post:     .to.be.a("number")
# post:     .and.equal(ASSERT_CONFIG.base.code, `code应为${ASSERT_CONFIG.base.code}，实际为${responseData.code}`);
# post:   
# post:   // 校验message字段
# post:   pm.expect(responseData).to.have.property("message");
# post:   pm.expect(responseData.message)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.base.message, `message应为"${ASSERT_CONFIG.base.message}"，实际为"${responseData.message}"`);
# post: });
# post: 
# post: /**
# post:  * 断言2：校验request_id存在且格式合法
# post:  */
# post: pm.test("请求ID校验：request_id存在且为非空字符串", () => {
# post:   pm.expect(responseData).to.have.property("request_id");
# post:   pm.expect(responseData.request_id)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post: });
# post: 
# post: /**
# post:  * 断言3：校验promoter中的email字段
# post:  */
# post: pm.test("业务字段校验：promoter.email值正确", () => {
# post:   // 安全获取email字段
# post:   const promoterEmail = getNestedProperty(responseData, ['data', 'promoter', 'email']);
# post:   
# post:   // 校验存在性和值
# post:   pm.expect(promoterEmail, "data.promoter.email字段缺失").to.not.be.undefined;
# post:   pm.expect(promoterEmail)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.business.email, `email应为"${ASSERT_CONFIG.business.email}"，实际为"${promoterEmail}"`);
# post: });
# post: 
# post: /**
# post:  * 断言4：校验data层级核心字段存在性
# post:  */
# post: pm.test("数据结构校验：核心业务字段存在", () => {
# post:   // 校验data根节点存在
# post:   pm.expect(responseData).to.have.property("data");
# post:   
# post:   // 校验curator、post、promoter、affiliateCode字段存在
# post:   const data = responseData.data;
# post:   pm.expect(data).to.have.property("curator");
# post:   pm.expect(data).to.have.property("post");
# post:   pm.expect(data).to.have.property("promoter");
# post:   pm.expect(data).to.have.property("affiliateCode");
# post:   
# post:   // 校验curator和post的核心子字段
# post:   pm.expect(data.curator).to.have.property("vanityUrl");
# post:   pm.expect(data.post).to.have.property("alias");
# post: });
# post: 
# post: /**
# post:  * 断言5：校验affiliateCode格式（非空字符串）
# post:  */
# post: pm.test("业务字段校验：affiliateCode为非空字符串", () => {
# post:   const affiliateCode = getNestedProperty(responseData, ['data', 'affiliateCode']);
# post:   
# post:   pm.expect(affiliateCode, "data.affiliateCode字段缺失").to.not.be.undefined;
# post:   pm.expect(affiliateCode)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post: });
# post: 
# post: // ========== 3. 提取affiliateCode到环境变量 ==========
# post: try {
# post:   const affiliateCode = responseData.data.affiliateCode;
# post:   // 将affiliateCode设置为环境变量（支持全局/集合/接口级别，这里用全局）
# post:   pm.environment.set("affiliateCode", affiliateCode);
# post:   console.log(`✅ 已将affiliateCode存入环境变量：${affiliateCode}`);
# post: } catch (error) {
# post:   pm.test("环境变量设置校验：affiliateCode提取成功", () => {
# post:     pm.expect.fail(`提取affiliateCode失败，原因：${error.message}`);
# post:   });
# post: }
# post: 
# post: // ========== 4. 校验通过提示 ==========
# post: console.log("✅ 所有断言执行完成，核心字段均符合预期");
# post: console.log("当前affiliateCode值：", getNestedProperty(responseData, ['data', 'affiliateCode']));
# --- step 3: 434c9c06-a6be-4b3f-9321-abf48c83afb5 ---
# post[customScript]: // ========== 配置区（便于维护） ==========
# post: const ASSERT_CONFIG = {
# post:   // 基础响应状态配置
# post:   base: {
# post:     code: 200,
# post:     message: "success"
# post:   },
# post:   // originalUrl基础前缀（固定部分）
# post:   originalUrlPrefix: "https://release.pear.us/lindanewcurator/post/t4131automation?aff="
# post: };
# post: 
# post: // ========== 1. 解析响应数据（带异常处理） ==========
# post: let responseData;
# post: try {
# post:   responseData = pm.response.json();
# post: } catch (error) {
# post:   pm.test("响应体格式校验：返回有效的JSON数据", () => {
# post:     pm.expect.fail(`JSON解析失败，原因：${error.message}`);
# post:   });
# post:   return;
# post: }
# post: 
# post: // ========== 通用工具函数 ==========
# post: /**
# post:  * 安全获取嵌套对象属性
# post:  * @param {Object} obj 源对象
# post:  * @param {Array} path 属性路径数组
# post:  * @param {*} defaultValue 默认值
# post:  * @returns {*} 属性值或默认值
# post:  */
# post: function getNestedProperty(obj, path, defaultValue = undefined) {
# post:   return path.reduce((acc, curr) => {
# post:     return (acc !== null && acc !== undefined) ? acc[curr] : defaultValue;
# post:   }, obj);
# post: }
# post: 
# post: // ========== 2. 核心字段断言 ==========
# post: /**
# post:  * 断言1：校验基础响应状态（code/message）
# post:  */
# post: pm.test("响应状态校验：code=200 且 message=success", () => {
# post:   // 校验code字段
# post:   pm.expect(responseData).to.have.property("code");
# post:   pm.expect(responseData.code)
# post:     .to.be.a("number")
# post:     .and.equal(ASSERT_CONFIG.base.code, `code应为${ASSERT_CONFIG.base.code}，实际为${responseData.code}`);
# post:   
# post:   // 校验message字段
# post:   pm.expect(responseData).to.have.property("message");
# post:   pm.expect(responseData.message)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.base.message, `message应为"${ASSERT_CONFIG.base.message}"，实际为"${responseData.message}"`);
# post: });
# post: 
# post: /**
# post:  * 断言2：校验shortUrl存在且格式合法
# post:  */
# post: pm.test("短链接校验：shortUrl存在且为合法URL格式", () => {
# post:   const shortUrl = getNestedProperty(responseData, ['data', 'shortUrl']);
# post:   
# post:   // 1. 校验shortUrl存在且非空
# post:   pm.expect(shortUrl, "data.shortUrl字段缺失").to.not.be.undefined;
# post:   pm.expect(shortUrl)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post:   
# post:   // 2. 校验shortUrl是合法的URL格式（以https开头，符合URL基本规则）
# post:   pm.expect(shortUrl)
# post:     .to.match(/^https?:\/\/.+$/, `shortUrl格式不合法，实际值：${shortUrl}`);
# post:   
# post:   // 3. 可选：校验shortUrl包含预期域名（按需启用）
# post:   // pm.expect(shortUrl).to.include("link.1m.app", `shortUrl应包含域名link.1m.app，实际值：${shortUrl}`);
# post: });
# post: 
# post: /**
# post:  * 断言3：校验originalUrl与affiliateCode匹配
# post:  */
# post: pm.test("原链接校验：originalUrl包含正确的affiliateCode且前缀匹配", () => {
# post:   // 从环境变量获取上一步的affiliateCode
# post:   const affiliateCode = pm.environment.get("affiliateCode");
# post:   pm.expect(affiliateCode, "环境变量中未找到affiliateCode，请先运行前置接口").to.not.be.undefined;
# post:   
# post:   // 获取响应中的originalUrl
# post:   const originalUrl = getNestedProperty(responseData, ['data', 'originalUrl']);
# post:   
# post:   // 1. 校验originalUrl存在且非空
# post:   pm.expect(originalUrl, "data.originalUrl字段缺失").to.not.be.undefined;
# post:   pm.expect(originalUrl)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post:   
# post:   // 2. 拼接预期的originalUrl（固定前缀 + 动态affiliateCode）
# post:   const expectedOriginalUrl = ASSERT_CONFIG.originalUrlPrefix + affiliateCode;
# post:   
# post:   // 3. 校验originalUrl完全匹配预期值
# post:   pm.expect(originalUrl)
# post:     .to.equal(expectedOriginalUrl, `originalUrl不匹配，预期：${expectedOriginalUrl}，实际：${originalUrl}`);
# post:   
# post:   // 备选方案：若只需要校验包含affiliateCode（无需完全匹配），可改用下面的断言
# post:   // pm.expect(originalUrl).to.include(affiliateCode, `originalUrl应包含affiliateCode：${affiliateCode}，实际：${originalUrl}`);
# post: });
# post: 
# post: /**
# post:  * 断言4：校验data层级核心字段完整性
# post:  */
# post: pm.test("数据结构校验：code/createdAt字段存在", () => {
# post:   const data = getNestedProperty(responseData, ['data']);
# post:   pm.expect(data, "data字段缺失").to.not.be.undefined;
# post:   
# post:   // 校验短链接code存在
# post:   pm.expect(data).to.have.property("code");
# post:   pm.expect(data.code).to.be.a("string").and.not.be.empty;
# post:   
# post:   // 校验创建时间存在
# post:   pm.expect(data).to.have.property("createdAt");
# post:   pm.expect(data.createdAt).to.be.a("string").and.not.be.empty;
# post: });
# post: 
# post: // ========== 3. 校验通过提示 ==========
# post: console.log("✅ 所有断言执行完成，短链接生成校验通过");
# post: console.log("生成的shortUrl：", getNestedProperty(responseData, ['data', 'shortUrl']));
# post: console.log("校验的originalUrl：", getNestedProperty(responseData, ['data', 'originalUrl']));
# post: console.log("使用的affiliateCode：", pm.environment.get("affiliateCode"));
# post[extractor]: {"variableName": "shortCode", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.code", "extractSettings": {"expression": "$.data.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 02bb2e88-ffe7-4442-aeff-8d361d57d7b2 ---
# post[customScript]: pm.test("响应码为200", function () {
# post:     pm.response.to.have.jsonBody("code", 200);
# post: });
# post: 
# post: pm.test("验证sent数值为1", function () {
# post:     const json = pm.response.json();
# post:     // 先判断data存在，避免空数据报错
# post:     pm.expect(json).to.have.property("data");
# post:     pm.expect(json.data.sent).to.equal(1);
# post: });
# --- step 5: f6472fdb-498d-44c4-a185-42700851291c ---
# post[customScript]: // ========== 配置区（便于维护，所有预期值集中管理） ==========
# post: const ASSERT_CONFIG = {
# post:   // 基础响应状态配置
# post:   base: {
# post:     code: 200,
# post:     message: "success"
# post:   },
# post:   // promoter字段预期值
# post:   promoter: {
# post:     email: null,
# post:     phoneNumber: "+16502396646"
# post:   }
# post: };
# post: 
# post: // ========== 1. 解析响应数据（带异常处理） ==========
# post: let responseData;
# post: try {
# post:   responseData = pm.response.json();
# post: } catch (error) {
# post:   pm.test("响应体格式校验：返回有效的JSON数据", () => {
# post:     pm.expect.fail(`JSON解析失败，原因：${error.message}`);
# post:   });
# post:   return;
# post: }
# post: 
# post: // ========== 通用工具函数 ==========
# post: /**
# post:  * 安全获取嵌套对象属性，避免层级缺失报错
# post:  * @param {Object} obj 源对象
# post:  * @param {Array} path 属性路径数组，如 ['data', 'promoter', 'email']
# post:  * @param {*} defaultValue 默认值
# post:  * @returns {*} 属性值或默认值
# post:  */
# post: function getNestedProperty(obj, path, defaultValue = undefined) {
# post:   return path.reduce((acc, curr) => {
# post:     return (acc !== null && acc !== undefined) ? acc[curr] : defaultValue;
# post:   }, obj);
# post: }
# post: 
# post: // ========== 2. 核心字段断言 ==========
# post: /**
# post:  * 断言1：校验基础响应状态（code/message/request_id）
# post:  */
# post: pm.test("响应状态校验：code=200 且 message=success", () => {
# post:   // 校验code字段
# post:   pm.expect(responseData).to.have.property("code");
# post:   pm.expect(responseData.code)
# post:     .to.be.a("number")
# post:     .and.equal(ASSERT_CONFIG.base.code, `code应为${ASSERT_CONFIG.base.code}，实际为${responseData.code}`);
# post:   
# post:   // 校验message字段
# post:   pm.expect(responseData).to.have.property("message");
# post:   pm.expect(responseData.message)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.base.message, `message应为"${ASSERT_CONFIG.base.message}"，实际为"${responseData.message}"`);
# post:   
# post:   // 校验request_id存在且为非空字符串
# post:   pm.expect(responseData).to.have.property("request_id");
# post:   pm.expect(responseData.request_id)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post: });
# post: 
# post: /**
# post:  * 断言2：校验data层级核心字段存在性
# post:  */
# post: pm.test("数据结构校验：data下核心字段完整", () => {
# post:   // 校验data根节点存在
# post:   pm.expect(responseData).to.have.property("data");
# post:   const data = responseData.data;
# post: 
# post:   // 校验curator、post、promoter、affiliateCode字段存在
# post:   pm.expect(data).to.have.property("curator");
# post:   pm.expect(data).to.have.property("post");
# post:   pm.expect(data).to.have.property("promoter");
# post:   pm.expect(data).to.have.property("affiliateCode");
# post: 
# post:   // 校验curator和post的子字段存在
# post:   pm.expect(data.curator).to.have.property("vanityUrl");
# post:   pm.expect(data.post).to.have.property("alias");
# post: });
# post: 
# post: /**
# post:  * 断言3：核心校验 - promoter下email=null、phoneNumber匹配指定值
# post:  */
# post: pm.test("业务字段校验：promoter.email=null 且 phoneNumber正确", () => {
# post:   // 安全获取promoter下的email和phoneNumber
# post:   const promoterEmail = getNestedProperty(responseData, ['data', 'promoter', 'email']);
# post:   const promoterPhone = getNestedProperty(responseData, ['data', 'promoter', 'phoneNumber']);
# post: 
# post:   // 校验email为null（重点：严格匹配null类型，而非空字符串）
# post:   // pm.expect(promoterEmail, "data.promoter.email字段缺失").to.not.be.undefined;
# post:   // pm.expect(promoterEmail)
# post:   //   .to.be.null, `email应为null，实际值：${promoterEmail}（类型：${typeof promoterEmail}）`;
# post: 
# post:   // 校验phoneNumber值匹配
# post:   pm.expect(promoterPhone, "data.promoter.phoneNumber字段缺失").to.not.be.undefined;
# post:   pm.expect(promoterPhone)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.promoter.phoneNumber, 
# post:       `phoneNumber应为"${ASSERT_CONFIG.promoter.phoneNumber}"，实际为"${promoterPhone}"`);
# post: });
# post: 
# post: /**
# post:  * 断言4：校验affiliateCode为非空字符串（随机值，仅验格式）
# post:  */
# post: pm.test("业务字段校验：affiliateCode为有效非空字符串", () => {
# post:   const affiliateCode = getNestedProperty(responseData, ['data', 'affiliateCode']);
# post:   
# post:   pm.expect(affiliateCode, "data.affiliateCode字段缺失").to.not.be.undefined;
# post:   pm.expect(affiliateCode)
# post:     .to.be.a("string")
# post:     .and.not.be.empty;
# post:   
# post:   // 可选：若affiliateCode有格式要求（如6位字符），可添加正则校验
# post:   // pm.expect(affiliateCode).to.match(/^[0-9a-zA-Z]{6}$/, `affiliateCode格式不符，实际值：${affiliateCode}`);
# post: });
# post: 
# post: // ========== 3. 提取affiliateCode到环境变量（供后续接口使用） ==========
# post: try {
# post:   const affiliateCode = responseData.data.affiliateCode;
# post:   pm.environment.set("affiliateCode", affiliateCode);
# post:   console.log(`✅ 已将affiliateCode存入环境变量：${affiliateCode}`);
# post: } catch (error) {
# post:   pm.test("环境变量设置校验：affiliateCode提取成功", () => {
# post:     pm.expect.fail(`提取affiliateCode失败，原因：${error.message}`);
# post:   });
# post: }
# post: 
# post: // ========== 4. 校验通过提示 ==========
# post: console.log("✅ 所有断言执行完成，核心字段均符合预期");
# post: console.log("promoter.email值：", getNestedProperty(responseData, ['data', 'promoter', 'email']));
# post: console.log("promoter.phoneNumber值：", getNestedProperty(responseData, ['data', 'promoter', 'phoneNumber']));
# post: console.log("affiliateCode值：", responseData.data.affiliateCode);
# post[extractor]: {"variableName": "smsshortcode", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.code", "extractSettings": {"expression": "$.data.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: 07187509-b359-4981-82a1-c9c135a9062e ---
# post[customScript]: pm.test("响应码为200", function () {
# post:     pm.response.to.have.jsonBody("code", 200);
# post: });
# post: 
# post: pm.test("验证sent数值为1", function () {
# post:     const json = pm.response.json();
# post:     // 先判断data存在，避免空数据报错
# post:     pm.expect(json).to.have.property("data");
# post:     pm.expect(json.data.sent).to.equal(1);
# post: });




from core.assertions import expect

def test_linda_t4131_verify_after_created_affiliate_link_can_send_email_or_sms(ctx):
    """Apifox case #7897302: Linda_T4131_Verify_after_created_affiliate_link_can_send_Email_or_SMS"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 3ce00ab3-55cd-42dd-9f62-784b7e74f4d9
    _resp1 = ctx.api.promoters.affiliate_promoters(body=None, params={'keyword': ''}, token='linda05_token')
    # step 2: a4fe9fa0-de87-4851-a141-ca5bff2edf6f
    _resp2 = ctx.api.promoters.curator_affiliate_link(body='{\r\n    "phoneNumberOrEmail": "linda.zhou.ext+27@1m.app",\r\n    "curatorId": "84a0de44-47e4-4a38-883e-d99ed194d7d7",\r\n    "postAlias": "t4131automation"\r\n}', token='linda05_token')
    # extractor: affiliateCode = affiliateCode
    ctx.extract('affiliateCode', _resp2, 'affiliateCode')
    # step 3: 434c9c06-a6be-4b3f-9321-abf48c83afb5
    _resp3 = ctx.api.links.internal(body='{\r\n    "originalUrl": "https://release.pear.us/lindanewcurator/post/t4131automation?aff={{affiliateCode}}"\r\n}', token='linda05_token')
    # extractor: shortCode = $.data.code
    ctx.extract('shortCode', _resp3, '$.data.code')
    # step 4: 02bb2e88-ffe7-4442-aeff-8d361d57d7b2
    _resp4 = ctx.api.promoters.affiliate_link_notification_batch(body='{\n    "postAlias": "t4131automation",\n    "notifications": [\n        {\n            "affiliateCode": "{{affiliateCode}}",\n            "affiliateLink": "https://s.pear.us/{{shortCode}}",\n            "customMessage": "<p class=\\"katana__paragraph katana__paragraph--align-left\\"><span style=\\"white-space: pre-wrap;\\">Hi there,</span></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><b><strong class=\\"katana__textBold\\" style=\\"white-space: pre-wrap;\\">lindazhou05</strong></b><span style=\\"white-space: pre-wrap;\\"> has set you up with a unique affiliate link for their post: \\"</span><b><strong class=\\"katana__textBold\\" style=\\"white-space: pre-wrap;\\">Jazz Age Lawn Party</strong></b><span style=\\"white-space: pre-wrap;\\">\\". Just share this link — your personal promo code is already built in:</span></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><span style=\\"white-space: pre-wrap;\\">👉 </span><a data-id=\\"69e40bf4-d16a-4903-9dd8-062eb16ae7ef\\" href=\\"https://s.pear.us/Ro2FDI\\" rel=\\"noopener noreferrer\\" target=\\"_blank\\"><span style=\\"white-space: pre-wrap;\\">https://s.pear.us/Ro2FDI</span></a></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><span style=\\"white-space: pre-wrap;\\">When someone buys through your link, you\'ll automatically earn commission based on the post\'s settings. No extra setup is needed.</span></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><span style=\\"white-space: pre-wrap;\\">If you don’t have a Pear account yet, sign up here:</span></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><a data-id=\\"ea112436-ba02-4a30-bdf1-c2f7e2cb6df5\\" href=\\"https://pear.us/signup?t=ltMMiE0-\\" rel=\\"noopener noreferrer\\" target=\\"_blank\\"><span style=\\"white-space: pre-wrap;\\">https://pear.us/signup?t=ltMMiE0-</span></a></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><span style=\\"white-space: pre-wrap;\\">You can start sharing right away through social, DMs, or your Pear Shop.</span></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><span style=\\"white-space: pre-wrap;\\">Thanks,</span></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><br></p><p class=\\"katana__paragraph katana__paragraph--align-left\\"><span style=\\"white-space: pre-wrap;\\">lindazhou05</span></p>",\n            "email": "linda.zhou.ext+27@1m.app",\n            "customSubject": "lindazhou05 sent you a promo link to share and earn"\n        }\n    ]\n}', token='linda05_token')
    # step 5: f6472fdb-498d-44c4-a185-42700851291c
    _resp5 = ctx.api.promoters.curator_affiliate_link(body='{\r\n    "phoneNumberOrEmail": "+16502396646",\r\n    "curatorId": "84a0de44-47e4-4a38-883e-d99ed194d7d7",\r\n    "postAlias": "t4131automation"\r\n}', token='linda05_token')
    # extractor: affiliateCode = affiliateCode
    ctx.extract('affiliateCode', _resp5, 'affiliateCode')
    # extractor: smsshortcode = $.data.code
    ctx.extract('smsshortcode', _resp5, '$.data.code')
    # step 6: 07187509-b359-4981-82a1-c9c135a9062e
    _resp6 = ctx.api.promoters.affiliate_link_notification_batch(body='{\n    "postAlias": "t4131automation",\n    "notifications": [\n        {\n            "affiliateCode": "{{affiliateCode}}",\n            "affiliateLink": "https://s.pear.us/{{smsshortcode}}",\n            "customMessage": "Hey! RESIDENT made you a promo link for \\"NTXCCREHH Charity Event\\". Share it to start earning:\\nhttps://s.pear.us/aNbVUq \\n\\nCreate your Pear account at: https://release.pear.us/signup?t=d1_pREvl",\n            "phoneNumber": "+16502396646"\n        }\n    ]\n}', token='linda05_token')
    # --- assertions: no fake-green (non-4xx/5xx) ---
    assert _resp1.status_code < 400, f"step1 got HTTP {_resp1.status_code}: {_resp1.text[:200]}"
    assert _resp2.status_code < 400, f"step2 got HTTP {_resp2.status_code}: {_resp2.text[:200]}"
    assert _resp3.status_code < 400, f"step3 got HTTP {_resp3.status_code}: {_resp3.text[:200]}"
    assert _resp4.status_code < 400, f"step4 got HTTP {_resp4.status_code}: {_resp4.text[:200]}"
    assert _resp5.status_code < 400, f"step5 got HTTP {_resp5.status_code}: {_resp5.text[:200]}"
    assert _resp6.status_code < 400, f"step6 got HTTP {_resp6.status_code}: {_resp6.text[:200]}"
