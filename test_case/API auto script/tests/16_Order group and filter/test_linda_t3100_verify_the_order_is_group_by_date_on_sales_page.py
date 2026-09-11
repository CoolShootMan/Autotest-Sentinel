"""Auto-generated from Apifox case #5942267. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 5942267
# Folder: 
# Case: (Linda)T3100 Verify the order is group by date on sales page
# Priority: P0
# Created: 2025-02-08T06:47:42.000Z
# Updated: 2026-08-11T07:26:47.000Z


CASE_ID = 5942267
ENV_NAME = "Release"

# --- step 1: c0054035-df18-4100-a877-b2a95ec9952c ---
# pre: pm.environment.set("timeZoneAsia", "Asia/Shanghai");
# pre: pm.environment.set("merchant_id", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# pre: pm.environment.set("consumer_id", "7bc6ed8d-51de-446b-8c64-fd321cf1a45d");
# pre: 
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{timeZoneAsia}}", "path": "$.data.timeZone", "multipleValue": [], "extractSettings": {"expression": "$.data.timeZone", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: Check the commission earnings list group by date ---
# pre: pm.environment.set("expected_paid", 100)
# post[customScript]:     if(pm.response.to.have.status(200)){
# post:         var res = JSON.parse(responseBody);
# post:         var orderNumber = pm.environment.get("orderNumber");
# post:         var order_detail;
# post:         var sale_order_id = "";
# post:         var order_exist = false;
# post:         for (var order of res['data']['items']){
# post:             if (orderNumber === order["orderNumber"]){
# post:                 order_exist =true;
# post:                 sale_order_id = order["id"]
# post:                 pm.environment.set("curator_sale_order_id",sale_order_id)
# post:             }
# post:        }
# post:     }
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count0}}", "path": "$.data.extra[0].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[0].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count1}}", "path": "$.data.extra[1].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[1].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count2}}", "path": "$.data.extra[2].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[2].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date0}}", "path": "$.data.extra[0].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[0].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date1}}", "path": "$.data.extra[1].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[1].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date2}}", "path": "$.data.extra[2].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[2].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{sales}}", "path": "$.data.totalCount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 1a52d6ee-7ed2-4f81-8048-4acbb8211a10 ---
# pre: pm.environment.set("timeZoneAsiaAmerica", "America/Los_Angeles");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{timeZoneAsiaAmerica}}", "path": "$.data.timeZone", "multipleValue": [], "extractSettings": {"expression": "$.data.timeZone", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: Check the commission earnings list group by date ---
# pre: pm.environment.set("expected_paid", 100)
# post[customScript]:     if(pm.response.to.have.status(200)){
# post:         var res = JSON.parse(responseBody);
# post:         var orderNumber = pm.environment.get("orderNumber");
# post:         var order_detail;
# post:         var sale_order_id = "";
# post:         var order_exist = false;
# post:         for (var order of res['data']['items']){
# post:             if (orderNumber === order["orderNumber"]){
# post:                 order_exist =true;
# post:                 sale_order_id = order["id"]
# post:                 pm.environment.set("curator_sale_order_id",sale_order_id)
# post:             }
# post:        }
# post:     }
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count0}}", "path": "$.data.extra[0].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[0].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count1}}", "path": "$.data.extra[1].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[1].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count2}}", "path": "$.data.extra[2].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[2].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date1}}", "path": "$.data.extra[1].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[1].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date2}}", "path": "$.data.extra[2].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[2].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{sales}}", "path": "$.data.totalCount", "multipleValue": [], "extractSettings": {"expression": "$.data.totalCount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





from core.assertions import expect

def test__5942267__Linda_T3100_Verify_the_order_is_group_by_date_on_sales_page(ctx):
    """Apifox case #5942267: Linda_T3100_Verify_the_order_is_group_by_date_on_sales_page"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['timeZoneAsia'] = 'Asia/Shanghai'
    vars['merchant_id'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    vars['consumer_id'] = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'
    # step 1: c0054035-df18-4100-a877-b2a95ec9952c
    _resp1 = ctx.api.misc.user_business_operation(body='{\r\n    "notificationSettings": {\r\n        "userId": "7bc6ed8d-51de-446b-8c64-fd321cf1a45d",\r\n        "verifyingSenderEmail": "lindazhou@2925.com",\r\n        "verifyingSenderEmailVerificationStatus": "SUCCESS",\r\n        "emailEnabled": true,\r\n        "createdAt": "2025-03-19T03:24:01.390Z",\r\n        "updatedAt": "2026-01-27T06:59:20.734Z"\r\n    },\r\n    "supportContact": {\r\n        "email": "linda.zhou.ext@1m.app",\r\n        "url": ""\r\n    },\r\n    "salesNotificationEmails": [\r\n        "linda.zhou.ext+00@1m.app"\r\n    ],\r\n    "timeZone": "{{timeZoneAsia}}",\r\n    "emailSalesNotificationFrequency": "SALES_NOTIFY_WEEKLY",\r\n    "smsSalesNotificationFrequency": "SALES_NOTIFY_NONE"\r\n}', token='linda00_token')
    # assertion 1.assertion: responseJson equal {{timeZoneAsia}}
    expect(_resp1).json('$.data.timeZone').equals(ctx.render_text('{{timeZoneAsia}}'))
    vars['expected_paid'] = '100'
    # step 2: Check the commission earnings list group by date
    # DB 步骤（Apifox database 处理器）: Select the order account group by created_da
    ctx.run_db(112809, """-- 外层查询用于按天分组统计前 30 条记录
SELECT
    TO_CHAR((created_at)::date, 'YYYY-MM-DD') AS order_date,
    COUNT(*) AS order_count
FROM (
    -- 内层子查询用于获取前 30 条记录
    SELECT created_at
    FROM "PromoterOrder" po
    WHERE promoter_id = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'
    ORDER BY created_at DESC
    LIMIT 30
) subquery
GROUP BY
    order_date
ORDER BY
    order_date DESC;""", [('order_date0', '$[0].order_date'), ('order_count0', '$[0].order_count'), ('order_date1', '$[1].order_date'), ('order_count1', '$[1].order_count'), ('order_date2', '$[2].order_date'), ('order_count2', '$[2].order_count')])
    # DB 步骤（Apifox database 处理器）: Count the sales account
    ctx.run_db(112809, """select count(*) as sales from "PromoterOrder" po WHERE promoter_id = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'""", [('sales', '$[0].sales')])
    _resp2 = ctx.api.orders.promoter(token='linda00_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['curator_sale_order_id'] = 'sale_order_id'
    # assertion 2.assertion: responseJson equal {{order_count0}}
    expect(_resp2).json('$.data.extra[0].count').equals(ctx.render_text('{{order_count0}}'))
    # assertion 2.assertion: responseJson equal {{order_count1}}
    expect(_resp2).json('$.data.extra[1].count').equals(ctx.render_text('{{order_count1}}'))
    # assertion 2.assertion: responseJson equal {{order_count2}}
    expect(_resp2).json('$.data.extra[2].count').equals(ctx.render_text('{{order_count2}}'))
    # assertion 2.assertion: responseJson equal {{order_date0}}
    expect(_resp2).json('$.data.extra[0].createdDay').equals(ctx.render_text('{{order_date0}}'))
    # assertion 2.assertion: responseJson equal {{order_date1}}
    expect(_resp2).json('$.data.extra[1].createdDay').equals(ctx.render_text('{{order_date1}}'))
    # assertion 2.assertion: responseJson equal {{order_date2}}
    expect(_resp2).json('$.data.extra[2].createdDay').equals(ctx.render_text('{{order_date2}}'))
    # assertion 2.assertion: responseJson equal {{sales}}
    expect(_resp2).json('$.data.totalCount').equals(ctx.render_text('{{sales}}'))
    vars['timeZoneAsiaAmerica'] = 'America/Los_Angeles'
    # step 3: 1a52d6ee-7ed2-4f81-8048-4acbb8211a10
    _resp3 = ctx.api.misc.user_business_operation(body='{\r\n    "notificationSettings": {\r\n        "userId": "7bc6ed8d-51de-446b-8c64-fd321cf1a45d",\r\n        "verifyingSenderEmail": "lindazhou@2925.com",\r\n        "verifyingSenderEmailVerificationStatus": "SUCCESS",\r\n        "emailEnabled": true,\r\n        "createdAt": "2025-03-19T03:24:01.390Z",\r\n        "updatedAt": "2026-01-27T06:59:20.734Z"\r\n    },\r\n    "supportContact": {\r\n        "email": "linda.zhou.ext@1m.app",\r\n        "url": ""\r\n    },\r\n    "salesNotificationEmails": [\r\n        "linda.zhou.ext+00@1m.app"\r\n    ],\r\n    "timeZone": "{{timeZoneAsiaAmerica}}",\r\n    "emailSalesNotificationFrequency": "SALES_NOTIFY_WEEKLY",\r\n    "smsSalesNotificationFrequency": "SALES_NOTIFY_NONE"\r\n}', token='linda00_token')
    # assertion 3.assertion: responseJson equal {{timeZoneAsiaAmerica}}
    expect(_resp3).json('$.data.timeZone').equals(ctx.render_text('{{timeZoneAsiaAmerica}}'))
    vars['expected_paid'] = '100'
    # step 4: Check the commission earnings list group by date
    # DB 步骤（Apifox database 处理器）: Select the order account group by created_da
    ctx.run_db(112809, """-- 外层查询用于按天分组统计前 30 条记录
SELECT
    -- 将 created_at 减去 8 小时并格式化为 'YYYY-MM-DD' 作为 order_date
    -- sql时间比US时间-8  比上海时间 +8
    TO_CHAR(created_at, 'YYYY-MM-DD') AS order_date,
    -- 统计每个日期分组下的记录数量
    COUNT(*) AS order_count
FROM (
    -- 内层子查询用于获取前 30 条记录
    SELECT created_at
    FROM "PromoterOrder" po
    WHERE promoter_id = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'
    ORDER BY created_at DESC
    LIMIT 30
) subquery
GROUP BY
    -- 按格式化后的日期进行分组
    order_date
ORDER BY
    -- 按格式化后的日期降序排序
    order_date DESC;""", [('order_date0', '$[0].order_date'), ('order_count0', '$[0].order_count'), ('order_date1', '$[1].order_date'), ('order_count1', '$[1].order_count'), ('order_date2', '$[2].order_date'), ('order_count2', '$[2].order_count')])
    # DB 步骤（Apifox database 处理器）: Count the sales account
    ctx.run_db(112809, """select count(*) as sales from "PromoterOrder" po WHERE promoter_id = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'""", [('sales', '$[0].sales')])
    _resp4 = ctx.api.orders.promoter(token='linda00_token', params={'pageSize': '30', 'pageNumber': '1'})
    vars['curator_sale_order_id'] = 'sale_order_id'
    # assertion 4.assertion: responseJson equal {{order_count0}}
    expect(_resp4).json('$.data.extra[0].count').equals(ctx.render_text('{{order_count0}}'))
    # assertion 4.assertion: responseJson equal {{order_count1}}
    expect(_resp4).json('$.data.extra[1].count').equals(ctx.render_text('{{order_count1}}'))
    # assertion 4.assertion: responseJson equal {{order_count2}}
    expect(_resp4).json('$.data.extra[2].count').equals(ctx.render_text('{{order_count2}}'))
    # assertion 4.assertion: responseJson equal {{order_date1}}
    expect(_resp4).json('$.data.extra[1].createdDay').equals(ctx.render_text('{{order_date1}}'))
    # assertion 4.assertion: responseJson equal {{order_date2}}
    expect(_resp4).json('$.data.extra[2].createdDay').equals(ctx.render_text('{{order_date2}}'))
    # assertion 4.assertion: responseJson equal {{sales}}
    expect(_resp4).json('$.data.totalCount').equals(ctx.render_text('{{sales}}'))
