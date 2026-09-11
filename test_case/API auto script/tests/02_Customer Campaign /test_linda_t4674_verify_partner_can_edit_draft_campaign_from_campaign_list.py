"""Migrated from Apifox case #7631803. Source folder: Customer Campaign ."""
# Apifox Case ID: 7631803  (traceability only — not needed to run)
NAME = "Verify partner can edit draft campaign from campaign list"
TAGS = ["p1", "customer_campaign", "suite:linda"]
PRIORITY = 1


CASE_ID = 7631803
ENV_NAME = "Release"

# --- step 1: 1d5d324e-c81f-419e-915a-3989ff0f93b3 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "campaignId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 35f6bb01-93b5-455e-9f2c-20f79dfec233 ---
# pre: // ========== 1. 定义随机生成工具函数 ==========
# pre: /**
# pre:  * 生成符合SMS场景的随机名称（≤20字符）
# pre:  * 语义：包含「场景关键词+随机时间/标识」，符合营销活动命名习惯
# pre:  */
# pre: function generateRandomSMSName() {
# pre:     // 基础关键词库（贴合SMS营销场景）
# pre:     const prefixes = ["SMS_Promo_", "Order_Alert_", "Sale_Reminder_", "Event_Notify_", "Coupon_SMS_"];
# pre:     const suffixes = [
# pre:         new Date().getMonth() + 1 + "_" + Math.floor(Math.random() * 30), // 月_日
# pre:         Math.floor(Math.random() * 1000).toString(), // 随机数字
# pre:         ["AM", "PM"][Math.floor(Math.random() * 2)] + Math.floor(Math.random() * 12) // 时段+小时
# pre:     ];
# pre: 
# pre:     // 随机组合前缀+后缀，确保总长度≤20
# pre:     const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];
# pre:     const randomSuffix = suffixes[Math.floor(Math.random() * suffixes.length)];
# pre:     let name = randomPrefix + randomSuffix;
# pre:     
# pre:     // 超长截断（兜底）
# pre:     if (name.length > 20) {
# pre:         name = name.substring(0, 20);
# pre:     }
# pre:     return name;
# pre: }
# pre: 
# pre: /**
# pre:  * 生成符合SMS场景的随机内容（≤160字符）
# pre:  * 语义：覆盖订单、促销、活动提醒等真实SMS场景，内容完整且有意义
# pre:  */
# pre: function generateRandomSMSContent() {
# pre:     // 真实SMS场景模板库（填充随机内容，确保语义合理）
# pre:     const templates = [
# pre:         // 订单通知模板
# pre:         "Your Order #{{orderNo}} Has Shipped! 📦 Track: {{trackNo}}. Delivery in {{days}} business days. Thank you!",
# pre:         // 促销模板
# pre:         "Exclusive Offer! {{discount}}% OFF on {{product}} – Valid till {{date}}. Use code: {{code}}. Reply STOP to unsubscribe.",
# pre:         // 活动提醒模板
# pre:         "Reminder: {{event}} on {{date}} at {{time}}! Don’t miss out – confirm via {{link}}. Reply YES to confirm.",
# pre:         // 优惠券模板
# pre:         "Free {{amount}} Coupon! Redeem at {{store}} till {{date}}. Code: {{code}}. Limited stock – act fast!"
# pre:     ];
# pre: 
# pre:     // 随机填充模板的动态值（语义合理）
# pre:     const randomTemplate = templates[Math.floor(Math.random() * templates.length)];
# pre:     const content = randomTemplate
# pre:         .replace("{{orderNo}}", Math.floor(Math.random() * 90000) + 10000) // 5位订单号
# pre:         .replace("{{trackNo}}", "TRK" + Math.floor(Math.random() * 900000) + 100000) // 追踪号
# pre:         .replace("{{days}}", Math.floor(Math.random() * 5) + 1) // 1-5天
# pre:         .replace("{{discount}}", [5, 10, 15, 20, 25][Math.floor(Math.random() * 5)]) // 折扣
# pre:         .replace("{{product}}", ["Electronics", "Clothing", "Groceries", "Beauty"][Math.floor(Math.random() * 4)]) // 商品类别
# pre:         .replace("{{date}}", (new Date().getMonth() + 1) + "/" + (Math.floor(Math.random() * 28) + 1)) // 日期
# pre:         .replace("{{code}}", Math.random().toString(36).substring(2, 8).toUpperCase()) // 6位优惠码
# pre:         .replace("{{event}}", ["Concert", "Workshop", "Sale Event", "Webinar"][Math.floor(Math.random() * 4)]) // 活动
# pre:         .replace("{{time}}", Math.floor(Math.random() * 12) + ":" + ["00", "15", "30", "45"][Math.floor(Math.random() * 4)]) // 时间
# pre:         .replace("{{link}}", "bit.ly/" + Math.random().toString(36).substring(2, 8)) // 短链接
# pre:         .replace("{{amount}}", ["$5", "$10", "$15", "$20"][Math.floor(Math.random() * 4)]) // 优惠券金额
# pre:         .replace("{{store}}", ["Our Store", "Online Shop", "Retail Outlet"][Math.floor(Math.random() * 3)]); // 店铺
# pre: 
# pre:     // 超长截断（SMS标准≤160字符，兜底处理）
# pre:     if (content.length > 160) {
# pre:         return content.substring(0, 160);
# pre:     }
# pre:     return content;
# pre: }
# pre: 
# pre: // ========== 2. 生成随机name和content ==========
# pre: const randomName = generateRandomSMSName();
# pre: const randomContent = generateRandomSMSContent();
# pre: console.log("【动态生成】name（长度：" + randomName.length + "）:", randomName);
# pre: console.log("【动态生成】content（长度：" + randomContent.length + "）:", randomContent);
# pre: 
# pre: // ========== 3. 构造完整入参JSON ==========
# pre: const requestBody = {
# pre:     "name": randomName,
# pre:     "status": "DRAFT",
# pre:     "updatedAt": new Date().toISOString(), // 动态生成当前时间（可选，也可固定）
# pre:     "channel": "SMS",
# pre:     "totalSelectedCount": 1,
# pre:     "subject": null,
# pre:     "content": randomContent,
# pre:     "selectAll": false,
# pre:     "id": "{{campaignId}}" // 保留APIFOX变量引用，会自动解析环境变量
# pre: };
# pre: 
# pre: // ========== 4. 设置为请求体（核心：替换原入参） ==========
# pre: pm.request.body.raw = JSON.stringify(requestBody, null, 2);
# pre: console.log("【最终入参】已替换为动态生成的内容:\n", pm.request.body.raw);
# post[customScript]: // ========== 1. 初始化校验配置 & 状态 ==========
# post: const verifyConfig = {
# post:     nameMaxLength: 20,        // name最大长度限制
# post:     contentMaxLength: 160,    // content最大长度限制
# post:     expectedStatus: "DRAFT",  // 预期status值
# post:     expectedSentStatus: "NOT_STARTED", // 预期sentStatus值
# post:     // name语义关键词（贴合SMS营销场景，确保生成的name有意义）
# post:     nameValidKeywords: ["SMS", "Order", "Promo", "Alert", "Reminder", "Notify", "Coupon"],
# post:     // content语义关键词（确保生成的content是真实SMS内容，非乱码）
# post:     contentValidKeywords: ["Order", "Track", "Delivery", "Offer", "Discount", "Code", "Reminder", "Coupon", "Shipped"]
# post: };
# post: 
# post: let verifyPass = true; // 整体校验是否通过
# post: const verifyLogs = []; // 结构化校验日志
# post: 
# post: // ========== 2. 解析响应数据 & 基础校验 ==========
# post: const responseData = pm.response.json();
# post: console.log("【原始响应】生成的SMS Campaign数据:\n", JSON.stringify(responseData, null, 2));
# post: 
# post: // 校验1：接口基础响应（code/message）
# post: if (responseData.code !== 200) {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ 接口响应失败：code期望200，实际${responseData.code}`);
# post: } else {
# post:     verifyLogs.push(`✅ 接口响应成功：code=200`);
# post: }
# post: if (responseData.message !== "success") {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ 接口业务状态失败：message期望success，实际${responseData.message}`);
# post: } else {
# post:     verifyLogs.push(`✅ 接口业务状态成功：message=success`);
# post: }
# post: 
# post: // 校验2：data字段存在性
# post: if (!responseData.data) {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ 响应缺少核心data字段，无法校验Campaign数据`);
# post: } else {
# post:     const campaignData = responseData.data;
# post: 
# post:     // ========== 3. 核心校验1：name有效性（非空+长度+语义） ==========
# post:     const name = campaignData.name || "";
# post:     // 3.1 name非空校验
# post:     if (!name) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ name校验失败：name为空`);
# post:     } else {
# post:         // 3.2 name长度校验（≤20字符）
# post:         if (name.length > verifyConfig.nameMaxLength) {
# post:             verifyPass = false;
# post:             verifyLogs.push(`❌ name长度校验失败：长度=${name.length}，超过最大限制${verifyConfig.nameMaxLength}`);
# post:         } else {
# post:             verifyLogs.push(`✅ name长度校验成功：长度=${name.length}（≤${verifyConfig.nameMaxLength}）`);
# post:         }
# post:         // 3.3 name语义校验（包含至少1个有效关键词，确保不是乱码）
# post:         const hasValidKeyword = verifyConfig.nameValidKeywords.some(keyword => name.includes(keyword));
# post:         if (!hasValidKeyword) {
# post:             verifyPass = false;
# post:             verifyLogs.push(`❌ name语义校验失败：name="${name}" 未包含有效关键词（${verifyConfig.nameValidKeywords.join("/")}）`);
# post:         } else {
# post:             verifyLogs.push(`✅ name语义校验成功：name="${name}" 包含有效SMS场景关键词`);
# post:         }
# post:     }
# post: 
# post:     // ========== 4. 核心校验2：content有效性（非空+长度+语义） ==========
# post:     const content = campaignData.content || "";
# post:     // 4.1 content非空校验
# post:     if (!content) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ content校验失败：content为空`);
# post:     } else {
# post:         // 4.2 content长度校验（≤160字符）
# post:         if (content.length > verifyConfig.contentMaxLength) {
# post:             verifyPass = false;
# post:             verifyLogs.push(`❌ content长度校验失败：长度=${content.length}，超过最大限制${verifyConfig.contentMaxLength}`);
# post:         } else {
# post:             verifyLogs.push(`✅ content长度校验成功：长度=${content.length}（≤${verifyConfig.contentMaxLength}）`);
# post:         }
# post:         // 4.3 content语义校验（包含至少1个有效关键词，确保内容有意义）
# post:         const hasValidContentKeyword = verifyConfig.contentValidKeywords.some(keyword => content.includes(keyword));
# post:         if (!hasValidContentKeyword) {
# post:             verifyPass = false;
# post:             verifyLogs.push(`❌ content语义校验失败：content未包含有效SMS业务关键词（${verifyConfig.contentValidKeywords.join("/")}）`);
# post:         } else {
# post:             verifyLogs.push(`✅ content语义校验成功：content包含有效SMS业务关键词`);
# post:         }
# post:     }
# post: 
# post:     // ========== 5. 核心校验3：status & sentStatus 准确性 ==========
# post:     // 5.1 status校验
# post:     const actualStatus = campaignData.status || "";
# post:     if (actualStatus !== verifyConfig.expectedStatus) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ status校验失败：期望${verifyConfig.expectedStatus}，实际${actualStatus}`);
# post:     } else {
# post:         verifyLogs.push(`✅ status校验成功：${verifyConfig.expectedStatus}`);
# post:     }
# post: 
# post:     // 5.2 sentStatus校验
# post:     const actualSentStatus = campaignData.sentStatus || "";
# post:     if (actualSentStatus !== verifyConfig.expectedSentStatus) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ sentStatus校验失败：期望${verifyConfig.expectedSentStatus}，实际${actualSentStatus}`);
# post:     } else {
# post:         verifyLogs.push(`✅ sentStatus校验成功：${verifyConfig.expectedSentStatus}`);
# post:     }
# post: 
# post:     // ========== 6. 额外校验：ID存在性（兜底） ==========
# post:     if (!campaignData.id) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ ID校验失败：生成的Campaign ID为空`);
# post:     } else {
# post:         verifyLogs.push(`✅ ID校验成功：生成的Campaign ID=${campaignData.id}`);
# post:     }
# post: }
# post: 
# post: // ========== 7. 存储校验结果到环境变量 ==========
# post: pm.environment.set("smsCampaignGenerateVerifyResult", verifyPass ? "success" : "failed");
# post: pm.environment.set("smsCampaignGenerateVerifyLogs", JSON.stringify(verifyLogs));
# post: 
# post: // ========== 8. 输出可视化校验总结 ==========
# post: console.log(`
# post: =====================================================
# post:             SMS Campaign生成结果校验总结
# post: =====================================================
# post: 整体校验结果：${verifyPass ? "✅ 全部通过" : "❌ 存在失败项"}
# post: -----------------------------------------------------
# post: ${verifyLogs.join("\n")}
# post: =====================================================
# post: `);
# post: 
# post: // 失败时高亮提醒
# post: if (!verifyPass) {
# post:     console.error(`【关键警告】SMS Campaign生成校验失败！请检查name/content/状态是否符合要求！`);
# post: }
# --- step 3: 947cf34c-0ca4-469a-9321-fbd634fa45b6 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "campaignEmailId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.totalSelectedCount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalSelectedCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: 51805720-b267-4085-827f-4e8463e6cbf2 ---
# pre: // ========== 1. 定义随机生成工具函数（贴合EMAIL营销场景） ==========
# pre: /**
# pre:  * 生成随机EMAIL名称（≤20字符）
# pre:  * 语义：包含邮件营销场景关键词，符合业务命名习惯
# pre:  */
# pre: function generateRandomEmailName() {
# pre:     // EMAIL场景核心关键词（确保name有意义）
# pre:     const prefixes = ["Email_Promo_", "Concert_Alert_", "Order_Update_", "Newsletter_", "Sale_Email_", "Event_Notify_"];
# pre:     const suffixes = [
# pre:         Math.floor(Math.random() * 1000).toString(), // 随机数字
# pre:         new Date().getDate().toString() + "_" + ["AM", "PM"][Math.floor(Math.random() * 2)], // 日期+时段
# pre:         ["2026", "Summer", "VIP"][Math.floor(Math.random() * 3)] // 场景标识
# pre:     ];
# pre: 
# pre:     // 随机组合+长度兜底
# pre:     const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];
# pre:     const randomSuffix = suffixes[Math.floor(Math.random() * suffixes.length)];
# pre:     let name = randomPrefix + randomSuffix;
# pre:     if (name.length > 20) name = name.substring(0, 20);
# pre:     return name;
# pre: }
# pre: 
# pre: /**
# pre:  * 生成随机EMAIL主题（贴合content场景，简短有意义）
# pre:  */
# pre: function generateRandomEmailSubject() {
# pre:     const subjects = [
# pre:         "Early Bird Tickets – 20% OFF!",
# pre:         "Your Order #{{orderNo}} Has Shipped!",
# pre:         "Exclusive Sale – Limited Time Only!",
# pre:         "Don’t Miss Our Summer Concert!",
# pre:         "Your VIP Invitation: [Event Name]",
# pre:         "Special Offer for Our Subscribers!"
# pre:     ];
# pre:     // 填充动态值（订单号）
# pre:     const randomSubject = subjects[Math.floor(Math.random() * subjects.length)]
# pre:         .replace("{{orderNo}}", Math.floor(Math.random() * 90000) + 10000);
# pre:     return randomSubject;
# pre: }
# pre: 
# pre: /**
# pre:  * 生成随机EMAIL内容（HTML格式，≤400字符，语义合理）
# pre:  * 场景：演唱会通知、订单通知、促销通知，HTML结构完整且简洁
# pre:  */
# pre: function generateRandomEmailContent() {
# pre:     // HTML模板库（精简结构，确保长度可控）
# pre:     const templates = [
# pre:         // 演唱会/活动模板
# pre:         `<p style="font-size:16px;line-height:24px;"><strong>Subject: {{subject}}</strong></p>
# pre:         <p>Dear Music Lover,</p>
# pre:         <p>Global superstar {{artist}} is performing in {{city}} on {{date}}! Early bird tickets are {{discount}}% off until {{deadline}}. Grab yours: {{link}}</p>
# pre:         <p>Best regards,<br>The ConcertPro Team</p>`,
# pre:         // 订单通知模板
# pre:         `<p style="font-size:16px;line-height:24px;"><strong>Subject: {{subject}}</strong></p>
# pre:         <p>Dear Customer,</p>
# pre:         <p>Your order #{{orderNo}} has shipped! Track: {{trackLink}}. Delivery in {{days}} business days.</p>
# pre:         <p>Thank you for your purchase!<br>The Support Team</p>`,
# pre:         // 促销模板
# pre:         `<p style="font-size:16px;line-height:24px;"><strong>Subject: {{subject}}</strong></p>
# pre:         <p>Hi there,</p>
# pre:         <p>Exclusive offer: {{discount}}% off all {{category}}! Use code {{code}} at checkout. Valid till {{date}}.</p>
# pre:         <p>Shop now: {{link}}<br>The Sales Team</p>`
# pre:     ];
# pre: 
# pre:     // 随机填充动态值（语义合理）
# pre:     const randomTemplate = templates[Math.floor(Math.random() * templates.length)];
# pre:     const content = randomTemplate
# pre:         .replace("{{subject}}", generateRandomEmailSubject()) // 关联主题
# pre:         .replace("{{artist}}", ["Taylor Swift", "Coldplay", "Beyoncé"][Math.floor(Math.random() * 3)])
# pre:         .replace("{{city}}", ["New York", "London", "Los Angeles"][Math.floor(Math.random() * 3)])
# pre:         .replace("{{date}}", (new Date().getMonth() + 1) + "/" + (Math.floor(Math.random() * 28) + 1) + "/2026")
# pre:         .replace("{{discount}}", [10, 15, 20, 25][Math.floor(Math.random() * 4)])
# pre:         .replace("{{link}}", "bit.ly/" + Math.random().toString(36).substring(2, 8))
# pre:         .replace("{{orderNo}}", Math.floor(Math.random() * 90000) + 10000)
# pre:         .replace("{{trackLink}}", "track.yourstore.com/" + Math.random().toString(36).substring(2, 10))
# pre:         .replace("{{days}}", Math.floor(Math.random() * 5) + 1)
# pre:         .replace("{{category}}", ["Electronics", "Clothing", "Home Goods"][Math.floor(Math.random() * 3)])
# pre:         .replace("{{code}}", Math.random().toString(36).substring(2, 8).toUpperCase());
# pre: 
# pre:     // 长度兜底（≤400字符，截断时保证HTML结构不破损）
# pre:     let finalContent = content;
# pre:     if (finalContent.length > 400) {
# pre:         // 截断到400字符，且确保最后是闭合标签（简单兜底）
# pre:         finalContent = finalContent.substring(0, 397) + "</p>";
# pre:     }
# pre:     return finalContent;
# pre: }
# pre: 
# pre: // ========== 2. 生成动态参数 ==========
# pre: const randomName = generateRandomEmailName();
# pre: const randomSubject = generateRandomEmailSubject();
# pre: const randomContent = generateRandomEmailContent();
# pre: 
# pre: // 打印生成结果（便于调试）
# pre: console.log("【动态生成】name（长度：" + randomName.length + "）:", randomName);
# pre: console.log("【动态生成】subject:", randomSubject);
# pre: console.log("【动态生成】content（长度：" + randomContent.length + "）:", randomContent);
# pre: 
# pre: // ========== 3. 构造完整入参并替换请求体 ==========
# pre: const requestBody = {
# pre:     "channel": "EMAIL", // 固定为EMAIL
# pre:     "content": randomContent,
# pre:     "name": randomName,
# pre:     "subject": randomSubject
# pre: };
# pre: 
# pre: // 替换请求体为动态生成的内容
# pre: pm.request.body.raw = JSON.stringify(requestBody, null, 2);
# pre: console.log("【最终入参】已替换为动态生成的EMAIL Campaign数据:\n", pm.request.body.raw);
# post[customScript]: // ========== 1. 初始化校验配置 & 状态 ==========
# post: const verifyConfig = {
# post:     nameMaxLength: 20,                // name最大长度限制（EMAIL场景）
# post:     expectedStatus: "DRAFT",          // 预期status值
# post:     expectedSentStatus: "NOT_STARTED",// 预期sentStatus值
# post:     // EMAIL场景name有效关键词（与动态生成脚本的关键词匹配，确保语义合理）
# post:     nameValidKeywords: ["Email", "Promo", "Concert", "Order", "Newsletter", "Sale", "Event", "Alert"]
# post: };
# post: 
# post: let verifyPass = true; // 整体校验是否通过
# post: const verifyLogs = []; // 结构化校验日志
# post: 
# post: // ========== 2. 解析响应数据 & 基础校验 ==========
# post: const responseData = pm.response.json();
# post: console.log("【原始响应】生成的EMAIL Campaign数据:\n", JSON.stringify(responseData, null, 2));
# post: 
# post: // 校验1：接口基础响应（确保接口调用成功）
# post: if (responseData.code !== 200) {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ 接口响应失败：code期望200，实际${responseData.code}`);
# post: } else {
# post:     verifyLogs.push(`✅ 接口响应成功：code=200`);
# post: }
# post: if (responseData.message !== "success") {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ 接口业务状态失败：message期望success，实际${responseData.message}`);
# post: } else {
# post:     verifyLogs.push(`✅ 接口业务状态成功：message=success`);
# post: }
# post: 
# post: // 校验2：核心data字段存在性
# post: if (!responseData.data) {
# post:     verifyPass = false;
# post:     verifyLogs.push(`❌ 响应缺少核心data字段，无法校验EMAIL Campaign数据`);
# post: } else {
# post:     const campaignData = responseData.data;
# post: 
# post:     // ========== 3. 核心校验1：EMAIL场景name有效性（非空+长度+语义） ==========
# post:     const name = campaignData.name || "";
# post:     // 3.1 name非空校验
# post:     if (!name) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ name校验失败：EMAIL Campaign名称为空`);
# post:     } else {
# post:         // 3.2 name长度校验（严格≤20字符）
# post:         if (name.length > verifyConfig.nameMaxLength) {
# post:             verifyPass = false;
# post:             verifyLogs.push(`❌ name长度校验失败：长度=${name.length}，超过最大限制${verifyConfig.nameMaxLength}`);
# post:         } else {
# post:             verifyLogs.push(`✅ name长度校验成功：长度=${name.length}（≤${verifyConfig.nameMaxLength}）`);
# post:         }
# post:         // 3.3 name语义校验（确保不是乱码，包含EMAIL场景关键词）
# post:         const hasValidKeyword = verifyConfig.nameValidKeywords.some(keyword => 
# post:             name.includes(keyword) // 匹配关键词（大小写敏感，与生成逻辑一致）
# post:         );
# post:         if (!hasValidKeyword) {
# post:             verifyPass = false;
# post:             verifyLogs.push(`❌ name语义校验失败：name="${name}" 未包含有效EMAIL场景关键词（${verifyConfig.nameValidKeywords.join("/")}）`);
# post:         } else {
# post:             verifyLogs.push(`✅ name语义校验成功：name="${name}" 包含有效EMAIL营销关键词`);
# post:         }
# post:     }
# post: 
# post:     // ========== 4. 核心校验2：status & sentStatus 准确性 ==========
# post:     // 4.1 status校验（DRAFT）
# post:     const actualStatus = campaignData.status || "";
# post:     if (actualStatus !== verifyConfig.expectedStatus) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ status校验失败：期望${verifyConfig.expectedStatus}，实际${actualStatus}`);
# post:     } else {
# post:         verifyLogs.push(`✅ status校验成功：${verifyConfig.expectedStatus}`);
# post:     }
# post: 
# post:     // 4.2 sentStatus校验（NOT_STARTED）
# post:     const actualSentStatus = campaignData.sentStatus || "";
# post:     if (actualSentStatus !== verifyConfig.expectedSentStatus) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ sentStatus校验失败：期望${verifyConfig.expectedSentStatus}，实际${actualSentStatus}`);
# post:     } else {
# post:         verifyLogs.push(`✅ sentStatus校验成功：${verifyConfig.expectedSentStatus}`);
# post:     }
# post: 
# post:     // ========== 5. 兜底校验：EMAIL Campaign ID存在性 ==========
# post:     if (!campaignData.id) {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ ID校验失败：生成的EMAIL Campaign ID为空`);
# post:     } else {
# post:         verifyLogs.push(`✅ ID校验成功：生成的EMAIL Campaign ID=${campaignData.id}`);
# post:     }
# post: 
# post:     // ========== 6. 额外兜底：channel是否为EMAIL（可选，确保场景匹配） ==========
# post:     if (campaignData.channel !== "EMAIL") {
# post:         verifyPass = false;
# post:         verifyLogs.push(`❌ channel校验失败：期望EMAIL，实际${campaignData.channel}`);
# post:     } else {
# post:         verifyLogs.push(`✅ channel校验成功：EMAIL（场景匹配）`);
# post:     }
# post: }
# post: 
# post: // ========== 7. 存储校验结果到环境变量（供后续流程使用） ==========
# post: pm.environment.set("emailCampaignGenerateVerifyResult", verifyPass ? "success" : "failed");
# post: pm.environment.set("emailCampaignGenerateVerifyLogs", JSON.stringify(verifyLogs));
# post: 
# post: // ========== 8. 输出可视化校验总结（易读性最大化） ==========
# post: console.log(`
# post: =====================================================
# post:             EMAIL Campaign生成结果校验总结
# post: =====================================================
# post: 整体校验结果：${verifyPass ? "✅ 全部通过" : "❌ 存在失败项"}
# post: -----------------------------------------------------
# post: ${verifyLogs.join("\n")}
# post: =====================================================
# post: `);
# post: 
# post: // 失败时高亮提醒（快速定位问题）
# post: if (!verifyPass) {
# post:     console.error(`【关键警告】EMAIL Campaign生成校验失败！请检查name/状态/场景是否符合要求！`);
# post: }




def _gen_random_sms_name():
    """对应原 Apifox pre-script 的 generateRandomSMSName()"""
    prefixes = ["SMS_Promo_", "Order_Alert_", "Sale_Reminder_", "Event_Notify_", "Coupon_SMS_"]
    suffixes = [
        f"{datetime.datetime.now().month}_{random.randint(0, 29)}",
        str(random.randint(0, 999)),
        f"{random.choice(['AM', 'PM'])}{random.randint(0, 11)}",
    ]
    name = random.choice(prefixes) + random.choice(suffixes)
    if len(name) > 20:
        name = name[:20]
    return name

def _gen_random_sms_content():
    """对应原 Apifox pre-script 的 generateRandomSMSContent()（模板内占位符全部填充）"""
    templates = [
        "Your Order #{{orderNo}} Has Shipped! 📦 Track: {{trackNo}}. Delivery in {{days}} business days. Thank you!",
        "Exclusive Offer! {{discount}}% OFF on {{product}} – Valid till {{date}}. Use code: {{code}}. Reply STOP to unsubscribe.",
        "Reminder: {{event}} on {{date}} at {{time}}! Don’t miss out – confirm via {{link}}. Reply YES to confirm.",
        "Free {{amount}} Coupon! Redeem at {{store}} till {{date}}. Code: {{code}}. Limited stock – act fast!"
    ]
    t = random.choice(templates)
    content = (t
        .replace("{{orderNo}}", str(random.randint(10000, 99999)))
        .replace("{{trackNo}}", "TRK" + str(random.randint(100000, 999999)))
        .replace("{{days}}", str(random.randint(1, 5)))
        .replace("{{discount}}", str(random.choice([5, 10, 15, 20, 25])))
        .replace("{{product}}", random.choice(["Electronics", "Clothing", "Groceries", "Beauty"]))
        .replace("{{date}}", f"{datetime.datetime.now().month}/{random.randint(1, 28)}")
        .replace("{{code}}", ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)).upper())
        .replace("{{event}}", random.choice(["Concert", "Workshop", "Sale Event", "Webinar"]))
        .replace("{{time}}", f"{random.randint(0, 11)}:{random.choice(['00', '15', '30', '45'])}")
        .replace("{{link}}", "bit.ly/" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)))
        .replace("{{amount}}", random.choice(["$5", "$10", "$15", "$20"]))
        .replace("{{store}}", random.choice(["Our Store", "Online Shop", "Retail Outlet"])))
    if len(content) > 160:
        content = content[:160]
    return content

import datetime
import random
import string
from core.assertions import expect

def test_linda_t4674_verify_partner_can_edit_draft_campaign_from_campaign_list(ctx):
    """Apifox case #7631803: Linda_T4674_Verify_partner_can_edit_draft_campaign_from_campaign_list"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # 动态生成 SMS name/content（对应原 Apifox pre-script 的 generateRandomSMSName / generateRandomSMSContent）
    vars['randomName'] = _gen_random_sms_name()
    vars['randomContent'] = _gen_random_sms_content()
    # === Steps ===
    # step 1: 1d5d324e-c81f-419e-915a-3989ff0f93b3
    _resp1 = ctx.api.campaigns.create(body='{\r\n    "channel": "SMS",\r\n    "name": "automation by linda SMS",\r\n    "content": "Subject: Your Order #7892 Has Shipped! "\r\n}', token='linda01_token')
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # extractor: campaignId = $.data.id
    ctx.extract('campaignId', _resp1, '$.data.id')
    # step 2: 35f6bb01-93b5-455e-9f2c-20f79dfec233
    _resp2 = ctx.api.campaigns.by_campaign_id(body='{\r\n    "name": "{{randomName}}",\r\n    "status": "DRAFT",\r\n    "updatedAt": "2025-12-11T09:05:35.745Z",\r\n    "channel": "SMS",\r\n    "totalSelectedCount": 1,\r\n    "subject": null,\r\n    "content": "{{randomContent}}",\r\n    "selectAll": false,\r\n    "id": "{{campaignId}}"\r\n}', token='linda01_token')
    vars['smsCampaignGenerateVerifyResult'] = 'verifyPass ? "success" : "failed"'
    vars['smsCampaignGenerateVerifyLogs'] = 'JSON.stringify(verifyLogs'
    # step 3: 947cf34c-0ca4-469a-9321-fbd634fa45b6
    _resp3 = ctx.api.campaigns.create(body='{\r\n    "channel": "EMAIL",\r\n    "content": "<p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><b><strong class=\\"katana__textBold\\" style=\\"color: rgb(0, 0, 0); font-size: 16px; line-height: 28px; white-space: pre-wrap;\\">Subject: Don’t Miss Out! Live Concert 2026 – Early Bird Tickets Now On Sale</strong></b></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Dear Music Lover,</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">We’re thrilled to announce that global superstar [Artist Name] is hitting the stage in your city this summer! The “Stellar Nights Tour” will light up [Venue Name] on [Date, Time], featuring hit songs from their latest album and classic fan favorites—plus exclusive stage visuals you won’t want to miss.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Secure your spot before prices rise: early bird tickets are 20% off until [Deadline]! Grab yours here: bit.ly/StellarNights2025. Limited VIP packages include meet-and-greets and backstage access—perfect for die-hard fans.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Hurry, tickets sell out fast for [Artist Name]’s tours! For group bookings or questions, email </span><a href=\\"mailto:support@concertpro.com\\" class=\\"katana__link\\" dir=\\"ltr\\"><span style=\\"white-space: pre-wrap;\\">support@concertpro.com</span></a><span style=\\"white-space: pre-wrap;\\"> or call +1-800-567-8901.</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Don’t let this unforgettable night slip away—see you at the show!</span></p><p class=\\"katana__paragraph katana__paragraph--align-start\\" dir=\\"ltr\\" style=\\"text-align: start;\\"><span style=\\"white-space: pre-wrap;\\">Best regards,The ConcertPro TeamYour Go-To for Unforgettable Live Music Experiences</span></p>",\r\n    "name": "automation by linda Email",\r\n    "subject": "Don’t Miss Out! "\r\n}', token='linda01_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # extractor: campaignEmailId = $.data.id
    ctx.extract('campaignEmailId', _resp3, '$.data.id')
    # assertion 3.assertion: responseJson equal 0
    expect(_resp3).json('$.data.totalSelectedCount').equals('0')
    # step 4: 51805720-b267-4085-827f-4e8463e6cbf2
    _resp4 = ctx.api.campaigns.by_campaign_id(body='{\r\n    "name": "{{randomName}}",\r\n    "status": "DRAFT",\r\n    "updatedAt": "2025-12-11T09:05:35.452Z",\r\n    "channel": "EMAIL",\r\n    "totalSelectedCount": 1,\r\n    "subject": "Don’t Miss Out! ",\r\n    "content": "{{randomContent}}",\r\n    "selectAll": false,\r\n    "id": "{{campaignEmailId}}"\r\n}\r\n', token='linda01_token', path_vars={'campaignId': '{{campaignEmailId}}'})
    vars['emailCampaignGenerateVerifyResult'] = 'verifyPass ? "success" : "failed"'
    vars['emailCampaignGenerateVerifyLogs'] = 'JSON.stringify(verifyLogs'
