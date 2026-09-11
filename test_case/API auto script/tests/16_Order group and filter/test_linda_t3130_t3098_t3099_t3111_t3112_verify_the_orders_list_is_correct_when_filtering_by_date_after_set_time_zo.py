"""Auto-generated from Apifox case #5875086. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 5875086
# Folder: 
# Case: (Linda)T3130 & T3098 & T3099 & T3111 & T3112 Verify the orders list is correct when filtering by date after set time zone 
# Priority: P0
# Created: 2025-01-20T07:56:39.000Z
# Updated: 2026-08-13T09:35:17.000Z


CASE_ID = 5875086
ENV_NAME = "Release"

# --- step 1: Get Partner linda00 token ---
# pre: pm.environment.set("account_email_merchant","dian.yuhong.ext@1m.app");
# pre: pm.environment.set("password_merchant","178Ad6e0aF0Ec22Ab948d8c0c69Ae072");
# post[customScript]:     if(pm.response.to.have.status(201)){
# post:         var res = JSON.parse(responseBody);
# post:         pm.environment.set("merchant_access_token",res['data']['token']);
# post:     }
# post[extractor]: {"variableName": "linda00_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: 214c5e81-1da1-4814-9f18-ee95bad4b279 ---
# pre: pm.environment.set("timeZoneAsia", "Asia/Shanghai");
# pre: pm.environment.set("merchant_id", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# pre: pm.environment.set("consumer_id", "7bc6ed8d-51de-446b-8c64-fd321cf1a45d");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{timeZoneAsia}}", "path": "$.data.timeZone", "multipleValue": [], "extractSettings": {"expression": "$.data.timeZone", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: Check "To fulfill" orders, the "Total orders" and "Total revenue"  --  yesterday  ---
# pre: // 获取当前日期对象
# pre: let today = new Date();
# pre: 
# pre: // 获取昨天的日期对象，通过将当前日期的毫秒数减去一天的毫秒数
# pre: let yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
# pre: 
# pre: // 获取昨天的起始时间（00:00:00）
# pre: let startTime = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate(), 0, 0, 0);
# pre: 
# pre: // 获取昨天的结束时间（23:59:59）
# pre: let endTime = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate(), 23, 59, 59);
# pre: 
# pre: // 将起始时间和结束时间存储为全局变量
# pre: pm.globals.set('startTime', startTime);
# pre: pm.globals.set('endTime', endTime);
# pre: 
# pre: console.log(startTime);
# pre: console.log(endTime);
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{today_count}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: // 解析 JSON 并将两端数据统一转为 2 位小数进行对比
# post: const apiVal = Number(pm.response.json()?.data?.extra?.totalRevenue).toFixed(2);
# post: const dbVal = Number(pm.environment.get("total_revenue")).toFixed(2);
# post: 
# post: pm.test("校验 totalRevenue 与数据库 total_revenue 相等", function () {
# post:     pm.expect(apiVal).to.eql(dbVal);
# post: });
# --- step 4: Check "FULFILLED" orders, the "Total orders" and "Total revenue"  --  yesterday  ---
# pre: // 获取当前日期对象
# pre: let today = new Date();
# pre: 
# pre: // 获取昨天的日期对象，通过将当前日期的毫秒数减去一天的毫秒数
# pre: let yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
# pre: 
# pre: // 获取昨天的起始时间（00:00:00）
# pre: let startTime = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate(), 0, 0, 0);
# pre: 
# pre: // 获取昨天的结束时间（23:59:59）
# pre: let endTime = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate(), 23, 59, 59);
# pre: 
# pre: // 将起始时间和结束时间存储为全局变量
# pre: pm.globals.set('startTime', startTime);
# pre: pm.globals.set('endTime', endTime);
# pre: 
# pre: console.log(startTime);
# pre: console.log(endTime);
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{today_count}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{total_revenue}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: Check consumer order list group by the current time zoon ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count1}}", "path": "$.data.extra[1].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[1].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count0}}", "path": "$.data.extra[0].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[0].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: // 获取存储在变量中的日期字符串
# post: const dateFromVariable = pm.variables.get('order_date0');
# post: 
# post: // 截取日期部分
# post: const formattedDateFromVariable = dateFromVariable.split('T')[0];
# post: 
# post: // 获取响应数据中的日期
# post: const responseData = pm.response.json();
# post: const dateFromResponse = responseData.data.extra[0].createdDay;
# post: 
# post: // 进行断言
# post: pm.test("日期部分应匹配", function () {
# post:     pm.expect(formattedDateFromVariable).to.equal(dateFromResponse);
# post: });
# post[customScript]: // 获取存储在变量中的日期字符串
# post: const dateFromVariable = pm.variables.get('order_date1');
# post: 
# post: // 截取日期部分
# post: const formattedDateFromVariable = dateFromVariable.split('T')[0];
# post: 
# post: // 获取响应数据中的日期
# post: const responseData = pm.response.json();
# post: const dateFromResponse = responseData.data.extra[1].createdDay;
# post: 
# post: // 进行断言
# post: pm.test("日期部分应匹配", function () {
# post:     pm.expect(formattedDateFromVariable).to.equal(dateFromResponse);
# post: });
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date0}}", "path": "$.data.extra[0].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[0].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date1}}", "path": "$.data.extra[1].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[1].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: 9faaec4b-543d-466d-9c8c-efcd846aa988 ---
# pre: pm.environment.set("timeZoneAsiaAmerica", "America/Los_Angeles");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{timeZoneAsiaAmerica}}", "path": "$.data.timeZone", "multipleValue": [], "extractSettings": {"expression": "$.data.timeZone", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: Check "FUIFILLED" orders, the "Total orders" and "Total revenue"  ---
# pre: // 获取当前日期对象
# pre: let today = new Date();
# pre: // 获取当天的起始时间（00:00:00）
# pre: let startTime = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 0, 0, 0);
# pre: // 获取当天的结束时间（23:59:59）
# pre: let endTime = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 23, 59, 59);
# pre: 
# pre: console.log(startTime)
# pre: console.log(endTime)
# pre: 
# pre: // 将起始时间转换为 ISO 8601 格式，并添加时区信息（假设为东八区）
# pre: let startTimeISO = startTime.toISOString().replace('Z', '%2B08:00');
# pre: let endTimeISO = endTime.toISOString().replace('Z', '%2B08:00');
# pre: 
# pre: 
# pre: // 将起始时间和结束时间存储为全局变量
# pre: pm.globals.set('startTime', startTimeISO);
# pre: pm.globals.set('endTime', endTimeISO);
# pre: 
# pre: console.log(startTime)
# pre: console.log(endTime)
# pre: 
# pre: // let currentDate = new Date();
# pre: // let isoString = currentDate.toISOString();
# pre: // console.log(isoString);
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{today_count}}", "path": "$.data.extra.totalOrders", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalOrders", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{total_revenue}}", "path": "$.data.extra.totalRevenue", "multipleValue": [], "extractSettings": {"expression": "$.data.extra.totalRevenue", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: Check consumer order list group by the current time zoon ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count1}}", "path": "$.data.extra[1].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[1].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_count0}}", "path": "$.data.extra[0].count", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[0].count", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: // 获取存储在变量中的日期字符串
# post: const dateFromVariable = pm.variables.get('order_date0');
# post: 
# post: // 截取日期部分
# post: const formattedDateFromVariable = dateFromVariable.split('T')[0];
# post: 
# post: // 获取响应数据中的日期
# post: const responseData = pm.response.json();
# post: const dateFromResponse = responseData.data.extra[0].createdDay;
# post: 
# post: // 进行断言
# post: pm.test("日期部分应匹配", function () {
# post:     pm.expect(formattedDateFromVariable).to.equal(dateFromResponse);
# post: });
# post[customScript]: // 获取存储在变量中的日期字符串
# post: const dateFromVariable = pm.variables.get('order_date1');
# post: 
# post: // 截取日期部分
# post: const formattedDateFromVariable = dateFromVariable.split('T')[0];
# post: 
# post: // 获取响应数据中的日期
# post: const responseData = pm.response.json();
# post: const dateFromResponse = responseData.data.extra[1].createdDay;
# post: 
# post: // 进行断言
# post: pm.test("日期部分应匹配", function () {
# post:     pm.expect(formattedDateFromVariable).to.equal(dateFromResponse);
# post: });
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date0}}", "path": "$.data.extra[0].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[0].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{order_date1}}", "path": "$.data.extra[1].createdDay", "multipleValue": [], "extractSettings": {"expression": "$.data.extra[1].createdDay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





import datetime
from zoneinfo import ZoneInfo

from core.assertions import expect

def test__5875086__Linda_T3130_T3098_T3099_T3111_T3112_Verify_the_orders_list_is_correct_when_filtering_by_date_after_set_time_zo(ctx):
    """Apifox case #5875086: Linda_T3130_T3098_T3099_T3111_T3112_Verify_the_orders_list_is_correct_when_filte"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['account_email_merchant'] = 'dian.yuhong.ext@1m.app'
    vars['password_merchant'] = '178Ad6e0aF0Ec22Ab948d8c0c69Ae072'
    # step 1: Get Partner linda00 token
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",\n    "email": "linda.zhou.ext+00@1m.app"\n}')
    ctx.extract('merchant_access_token', _resp1, '$.data.token')
    # extractor: linda00_token = $.data.token
    ctx.extract('linda00_token', _resp1, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    vars['timeZoneAsia'] = 'Asia/Shanghai'
    vars['merchant_id'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    vars['consumer_id'] = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'
    # step 2: 214c5e81-1da1-4814-9f18-ee95bad4b279
    _resp2 = ctx.api.misc.user_business_operation(body='{\r\n    "notificationSettings": {\r\n        "userId": "7bc6ed8d-51de-446b-8c64-fd321cf1a45d",\r\n        "verifyingSenderEmail": "lindazhou@2925.com",\r\n        "verifyingSenderEmailVerificationStatus": "SUCCESS",\r\n        "emailEnabled": true,\r\n        "createdAt": "2025-03-19T03:24:01.390Z",\r\n        "updatedAt": "2026-01-27T06:59:20.734Z"\r\n    },\r\n    "supportContact": {\r\n        "email": "linda.zhou.ext@1m.app",\r\n        "url": ""\r\n    },\r\n    "salesNotificationEmails": [\r\n        "linda.zhou.ext+00@1m.app"\r\n    ],\r\n    "timeZone": "{{timeZoneAsia}}",\r\n    "emailSalesNotificationFrequency": "SALES_NOTIFY_WEEKLY",\r\n    "smsSalesNotificationFrequency": "SALES_NOTIFY_NONE"\r\n}', token='linda00_token')
    # assertion 2.assertion: responseJson equal {{timeZoneAsia}}
    expect(_resp2).json('$.data.timeZone').equals(ctx.render_text('{{timeZoneAsia}}'))
    # --- 人工补丁：还原被丢弃的 startTime / endTime 时间窗口 ---
    # Apifox 用前置脚本 pm.globals.set('startTime'/'endTime', …) 计算窗口（三个步骤的窗口
    # 语义各不相同），迁移时整段丢弃、只留字面量占位 → 服务端 500
    # 「Invalid value for argument `gte`: input contains invalid characters.
    #   Expected ISO-8601 DateTime」。
    # 基准日期直接取自数据库 current_date，保证与断言基准 SQL 的窗口完全一致。
    _base_date = datetime.date.fromisoformat(
        ctx.run_db(112809, "SELECT current_date::text AS d")[0]["d"])

    def _window(_day, _tz, _is_end=False):
        _t = datetime.time(23, 59, 59) if _is_end else datetime.time(0, 0, 0)
        return datetime.datetime.combine(_day, _t, tzinfo=ZoneInfo(_tz)).isoformat()

    # 上海时区的「昨天」：对应 step3 / step4 两次 /order/merchant
    _sh_day = _base_date - datetime.timedelta(days=1)
    vars['startTime'] = _window(_sh_day, 'Asia/Shanghai')
    vars['endTime'] = _window(_sh_day, 'Asia/Shanghai', True)
    # step 3: Check "To fulfill" orders, the "Total orders" and "Total revenue"  --  yesterday 
    # DB 步骤（Apifox database 处理器）: To Fulfill  -- count the sales "Total orders" data
    ctx.run_db(112809, """-- 使用 CTE 定义昨天的时间范围
WITH time_range AS (
    -- 计算昨天的起始时间
    SELECT
        date_trunc('day', current_date - interval '1 day') at time zone 'Asia/Shanghai' AS start_time,
        -- 计算昨天的结束时间
        (date_trunc('day', current_date - interval '1 day') + interval '1 day - 1 second') at time zone 'Asia/Shanghai' AS end_time
)
SELECT COUNT(*)
FROM (
    SELECT "public"."MerchantOrder"."id"
    FROM "public"."MerchantOrder"
    -- 左连接 Order 表
    LEFT JOIN "public"."Order" AS "j1" ON "j1"."id" = "public"."MerchantOrder"."order_id"
    CROSS JOIN time_range
    WHERE
        -- 订单状态为已完成且订单 ID 不为空
        "j1"."status" = 'COMPLETED' AND "j1"."id" IS NOT NULL
        -- 筛选创建时间在昨天范围内的订单
        AND "public"."MerchantOrder"."created_at" at time zone 'Asia/Shanghai' >= time_range.start_time
        AND "public"."MerchantOrder"."created_at" at time zone 'Asia/Shanghai' <= time_range.end_time
        -- 筛选特定商家 ID 的订单
        AND "public"."MerchantOrder"."merchant_id" IN (
            SELECT ID
            FROM "Merchant"
            WHERE id = '{{merchant_id}}'
        )
        -- 排除符合特定条件的订单
        AND "public"."MerchantOrder"."id" NOT IN (
            SELECT "t2"."merchant_order_id"
            FROM "public"."OrderLineItem" AS "t2"
            WHERE
                -- 订单行项目的履行状态不为未履行
                NOT "t2"."fulfillment_status" = 'UNFULFILLED'
                -- 筛选特定商家 ID 的订单行项目
                AND "t2"."merchant_id" IN (
                    SELECT ID
                    FROM "Merchant"
                    WHERE id = '{{merchant_id}}'
                )
                AND "t2"."merchant_order_id" IS NOT NULL
        )
) AS "sub";""", [('today_count', '$.[0].count')])
    # DB 步骤（Apifox database 处理器）: To Fulfill  -- count the sales "Total revenue" data
    ctx.run_db(112809, """-- 使用 CTE（Common Table Expression）定义昨天的时间范围
WITH yesterday_range AS (
    -- 计算昨天的开始时间，使用 date_trunc 函数将时间截断到天，并转换到指定时区
    SELECT
        date_trunc('day', current_date - interval '1 day') AT TIME ZONE 'Asia/Shanghai' AS start_time,
        -- 计算昨天的结束时间，在开始时间基础上加一天并减去 1 秒
        (date_trunc('day', current_date - interval '1 day') + interval '1 day - 1 second') AT TIME ZONE 'Asia/Shanghai' AS end_time
)
-- 主查询，计算符合条件的总金额
-- sum  ROUND 保留两位2小数
-- 使用 COALESCE 函数处理 total_revenue 为 null 的情况
SELECT COALESCE(ROUND(SUM("total_merchant_payout_to_pay")::numeric, 2), 0) AS total_revenue
FROM (
    SELECT "public"."MerchantOrder"."total_merchant_payout_to_pay"
    FROM "public"."MerchantOrder"
    -- 左连接 "public"."Order" 表，通过 order_id 关联
    LEFT JOIN "public"."Order" AS "j1" ON "j1"."id" = "public"."MerchantOrder"."order_id"
    -- 交叉连接 yesterday_range，以便在后续条件中使用时间范围
    CROSS JOIN yesterday_range
    WHERE
        -- 订单状态为 'COMPLETED' 且订单 ID 不为空
        "j1"."status" = 'COMPLETED' AND "j1"."id" IS NOT NULL
        -- 订单创建时间在昨天的时间范围内
        AND "public"."MerchantOrder"."created_at" AT TIME ZONE 'Asia/Shanghai' >= yesterday_range.start_time
        AND "public"."MerchantOrder"."created_at" AT TIME ZONE 'Asia/Shanghai' <= yesterday_range.end_time
        -- 商家 ID 符合指定条件
        AND "public"."MerchantOrder"."merchant_id" IN (
            SELECT ID
            FROM "Merchant"
            WHERE id = '{{merchant_id}}'
        )
        -- 排除满足特定条件的订单 ID
        AND "public"."MerchantOrder"."id" NOT IN (
            SELECT "t2"."merchant_order_id"
            FROM "public"."OrderLineItem" AS "t2"
            WHERE
                -- 订单行项目的履行状态不为 'UNFULFILLED'
                NOT "t2"."fulfillment_status" = 'UNFULFILLED'
                -- 商家 ID 符合指定条件
                AND "t2"."merchant_id" IN (
                    SELECT ID
                    FROM "Merchant"
                    WHERE id = '{{merchant_id}}'
                )
                AND "t2"."merchant_order_id" IS NOT NULL
        )
) AS "sub";""", [('total_revenue', '$[0].total_revenue')])
    _resp3 = ctx.api.orders.merchant(token='linda00_token', params={'fulfillStatus': 'TO_FULFILL', 'merchantId': '{{merchant_id}}', 'platform': 'SHOPIFY', 'startTime': '{{startTime}}', 'endTime': '{{endTime}}'})
    # assertion 3.assertion: responseJson equal {{today_count}}
    expect(_resp3).json('$.data.extra.totalOrders').equals(ctx.render_text('{{today_count}}'))
    # （startTime/endTime 与上一步相同，无需重设）
    # step 4: Check "FULFILLED" orders, the "Total orders" and "Total revenue"  --  yesterday 
    # DB 步骤（Apifox database 处理器）: To Fulfill  -- count the sales "Total orders" data
    ctx.run_db(112809, """-- 使用 CTE 定义昨天的时间范围
WITH time_range AS (
    -- 计算昨天的起始时间
    SELECT
        date_trunc('day', current_date - interval '1 day') at time zone 'Asia/Shanghai' AS start_time,
        -- 计算昨天的结束时间
        (date_trunc('day', current_date - interval '1 day') + interval '1 day - 1 second') at time zone 'Asia/Shanghai' AS end_time
)
SELECT COUNT(*)
FROM (
    SELECT "public"."MerchantOrder"."id"
    FROM "public"."MerchantOrder"
    -- 左连接 Order 表
    LEFT JOIN "public"."Order" AS "j1" ON "j1"."id" = "public"."MerchantOrder"."order_id"
    CROSS JOIN time_range
    WHERE
        -- 订单状态为已完成且订单 ID 不为空
        "j1"."status" = 'COMPLETED' AND "j1"."id" IS NOT NULL
        -- 筛选创建时间在昨天范围内的订单
        AND "public"."MerchantOrder"."created_at" at time zone 'Asia/Shanghai' >= time_range.start_time
        AND "public"."MerchantOrder"."created_at" at time zone 'Asia/Shanghai' <= time_range.end_time
        -- 筛选特定商家 ID 的订单
        AND "public"."MerchantOrder"."merchant_id" IN (
            SELECT ID
            FROM "Merchant"
            WHERE id = '{{merchant_id}}'
        )
        -- 排除符合特定条件的订单
        AND "public"."MerchantOrder"."id" NOT IN (
            SELECT "t2"."merchant_order_id"
            FROM "public"."OrderLineItem" AS "t2"
            WHERE
                -- 订单行项目的履行状态不为未履行
                NOT "t2"."fulfillment_status" = 'FULFILLED'
                -- 筛选特定商家 ID 的订单行项目
                AND "t2"."merchant_id" IN (
                    SELECT ID
                    FROM "Merchant"
                    WHERE id = '{{merchant_id}}'
                )
                AND "t2"."merchant_order_id" IS NOT NULL
        )
) AS "sub";""", [('today_count', '$.[0].count')])
    # DB 步骤（Apifox database 处理器）: To Fulfill  -- count the sales "Total revenue" data
    ctx.run_db(112809, """-- 使用 CTE（Common Table Expression）定义昨天的时间范围
WITH yesterday_range AS (
    -- 计算昨天的开始时间，使用 date_trunc 函数将时间截断到天，并转换到指定时区
    SELECT
        date_trunc('day', current_date - interval '1 day') AT TIME ZONE 'Asia/Shanghai' AS start_time,
        -- 计算昨天的结束时间，在开始时间基础上加一天并减去 1 秒
        (date_trunc('day', current_date - interval '1 day') + interval '1 day - 1 second') AT TIME ZONE 'Asia/Shanghai' AS end_time
)
-- 主查询，计算符合条件的总金额
SELECT COALESCE(ROUND(SUM("total_merchant_payout_to_pay")::numeric, 2), 0) AS total_revenue
FROM (
    SELECT "public"."MerchantOrder"."total_merchant_payout_to_pay"
    FROM "public"."MerchantOrder"
    -- 左连接 "public"."Order" 表，通过 order_id 关联
    LEFT JOIN "public"."Order" AS "j1" ON "j1"."id" = "public"."MerchantOrder"."order_id"
    -- 交叉连接 yesterday_range，以便在后续条件中使用时间范围
    CROSS JOIN yesterday_range
    WHERE
        -- 订单状态为 'COMPLETED' 且订单 ID 不为空
        "j1"."status" = 'COMPLETED' AND "j1"."id" IS NOT NULL
        -- 订单创建时间在昨天的时间范围内
        AND "public"."MerchantOrder"."created_at" AT TIME ZONE 'Asia/Shanghai' >= yesterday_range.start_time
        AND "public"."MerchantOrder"."created_at" AT TIME ZONE 'Asia/Shanghai' <= yesterday_range.end_time
        -- 商家 ID 符合指定条件
        AND "public"."MerchantOrder"."merchant_id" IN (
            SELECT ID
            FROM "Merchant"
            WHERE id = '{{merchant_id}}'
        )
        -- 排除满足特定条件的订单 ID
        AND "public"."MerchantOrder"."id" NOT IN (
            SELECT "t2"."merchant_order_id"
            FROM "public"."OrderLineItem" AS "t2"
            WHERE
                -- 订单行项目的履行状态不为 'FULFILLED'
                NOT "t2"."fulfillment_status" = 'FULFILLED'
                -- 商家 ID 符合指定条件
                AND "t2"."merchant_id" IN (
                    SELECT ID
                    FROM "Merchant"
                    WHERE id = '{{merchant_id}}'
                )
                AND "t2"."merchant_order_id" IS NOT NULL
        )
) AS "sub";""", [('total_revenue', '$[0].total_revenue')])
    _resp4 = ctx.api.orders.merchant(token='linda00_token', params={'fulfillStatus': 'FULFILLED', 'merchantId': '{{merchant_id}}', 'platform': 'SHOPIFY', 'startTime': '{{startTime}}', 'endTime': '{{endTime}}'})
    # assertion 4.assertion: responseJson equal {{today_count}}
    expect(_resp4).json('$.data.extra.totalOrders').equals(ctx.render_text('{{today_count}}'))
    # assertion 4.assertion: responseJson equal {{total_revenue}}
    expect(_resp4).json('$.data.extra.totalRevenue').equals(ctx.render_text('{{total_revenue}}'))
    # step 5: Check consumer order list group by the current time zoon
    # DB 步骤（Apifox database 处理器）: search the order group by created date
    ctx.run_db(112809, """select
	TO_CHAR(DATE(created_at + INTERVAL '8 hours'), 'YYYY-MM-DD') AS order_date,
	COUNT(*) as order_count
from "Order" o
where consumer_id = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'
group by
	TO_CHAR(DATE(created_at + INTERVAL '8 hours'), 'YYYY-MM-DD')
order by
	order_date  desc ;""", [('order_date0', '$[0].order_date'), ('order_count0', '$[0].order_count'), ('order_date1', '$[1].order_date'), ('order_count1', '$[1].order_count')])
    _resp5 = ctx.api.orders.consumer(token='linda00_token')
    # assertion 5.assertion: responseJson equal {{order_count1}}
    expect(_resp5).json('$.data.extra[1].count').equals(ctx.render_text('{{order_count1}}'))
    # assertion 5.assertion: responseJson equal {{order_count0}}
    expect(_resp5).json('$.data.extra[0].count').equals(ctx.render_text('{{order_count0}}'))
    # assertion 5.assertion: responseJson equal {{order_date0}}
    expect(_resp5).json('$.data.extra[0].createdDay').equals(ctx.render_text('{{order_date0}}'))
    # assertion 5.assertion: responseJson equal {{order_date1}}
    expect(_resp5).json('$.data.extra[1].createdDay').equals(ctx.render_text('{{order_date1}}'))
    vars['timeZoneAsiaAmerica'] = 'America/Los_Angeles'
    # step 6: 9faaec4b-543d-466d-9c8c-efcd846aa988
    _resp6 = ctx.api.misc.user_business_operation(body='{\r\n    "notificationSettings": {\r\n        "userId": "7bc6ed8d-51de-446b-8c64-fd321cf1a45d",\r\n        "verifyingSenderEmail": "lindazhou@2925.com",\r\n        "verifyingSenderEmailVerificationStatus": "SUCCESS",\r\n        "emailEnabled": true,\r\n        "createdAt": "2025-03-19T03:24:01.390Z",\r\n        "updatedAt": "2026-01-27T06:59:20.734Z"\r\n    },\r\n    "supportContact": {\r\n        "email": "linda.zhou.ext@1m.app",\r\n        "url": ""\r\n    },\r\n    "salesNotificationEmails": [\r\n        "linda.zhou.ext+00@1m.app"\r\n    ],\r\n    "timeZone": "{{timeZoneAsiaAmerica}}",\r\n    "emailSalesNotificationFrequency": "SALES_NOTIFY_WEEKLY",\r\n    "smsSalesNotificationFrequency": "SALES_NOTIFY_NONE"\r\n}', token='linda00_token')
    # assertion 6.assertion: responseJson equal {{timeZoneAsiaAmerica}}
    expect(_resp6).json('$.data.timeZone').equals(ctx.render_text('{{timeZoneAsiaAmerica}}'))
    # --- 人工补丁：切到 America/Los_Angeles 的窗口（step7）---
    # 该窗口必须与它所对应的断言基准 SQL 对齐：那条 SQL 用的是
    # `current_date - interval '3 day'` 的洛杉矶本地日。
    _la_day = _base_date - datetime.timedelta(days=3)
    vars['startTime'] = _window(_la_day, 'America/Los_Angeles')
    vars['endTime'] = _window(_la_day, 'America/Los_Angeles', True)
    # step 7: Check "FUIFILLED" orders, the "Total orders" and "Total revenue" 
    # DB 步骤（Apifox database 处理器）: count the sales "to_fullfill" data
    ctx.run_db(112809, """-- 计算昨天的日期
WITH yesterday AS (
    SELECT (current_date - interval '3 day')::timestamp AS start_date
)
SELECT
    COUNT("public"."MerchantOrder".id) AS today_count,
    -- 使用 COALESCE 函数处理 total_revenue 为 null 的情况
    COALESCE(ROUND(SUM("total_merchant_payout_to_pay")::numeric, 2), 0) AS total_revenue
FROM
    "public"."MerchantOrder"
    LEFT JOIN "public"."Order" AS "j1" ON "j1"."id" = "public"."MerchantOrder"."order_id"
    CROSS JOIN yesterday
WHERE
    (
        ( "j1"."status" = 'COMPLETED' AND "j1"."id" IS NOT NULL )
        -- 使用动态计算的昨天日期作为起始时间
        AND "public"."MerchantOrder"."created_at" AT TIME ZONE 'UTC' at time zone 'America/Los_Angeles' >= yesterday.start_date
        AND "public"."MerchantOrder"."created_at" AT TIME ZONE 'UTC' at time zone 'America/Los_Angeles' <= (yesterday.start_date + interval '23 hours 59 minutes 59 seconds')
        AND "public"."MerchantOrder"."merchant_id" IN ( '{{merchant_id}}' )
        AND "public"."MerchantOrder"."id" IN (
            SELECT
                "t2"."merchant_order_id"
            FROM
                "public"."OrderLineItem" AS "t2"
            WHERE
                (
                    -- 人工补丁：Apifox 原文此处写的是 'TO_FULFILL'，但库中
                    -- FulfillmentStatus 枚举只有 UNFULFILLED/FULFILLED/PARTIALLY_FULFILLED，
                    -- 执行会报 invalid input value for enum。该步骤的 API 侧过滤是
                    -- fulfillStatus=TO_FULFILL，故基准应为 UNFULFILLED。
                    ( "t2"."fulfillment_status" = 'UNFULFILLED' )
                    AND "t2"."merchant_id" IN ( '{{merchant_id}}' )
                    AND "t2"."merchant_order_id" IS NOT NULL
                )
        )
    );""", [('today_count', '$.[0].today_count'), ('total_revenue0', '$.[0].total_revenue')])
    _resp7 = ctx.api.orders.merchant(token='linda00_token', params={'fulfillStatus': 'TO_FULFILL', 'merchantId': '{{merchant_id}}', 'platform': 'SHOPIFY', 'startTime': '{{startTime}}', 'endTime': '{{endTime}}'})
    # assertion 7.assertion: responseJson equal {{today_count}}
    expect(_resp7).json('$.data.extra.totalOrders').equals(ctx.render_text('{{today_count}}'))
    # assertion 7.assertion: responseJson equal {{total_revenue}}
    # 人工补丁：本步（Apifox step8）自己的基准 SQL 提取的是 total_revenue0，
    # 原文断言的 {{total_revenue}} 是上一步（FULFILLED）残留的陈旧值，恒为 0。
    expect(_resp7).json('$.data.extra.totalRevenue').equals(ctx.render_text('{{total_revenue0}}'))
    # step 8: Check consumer order list group by the current time zoon
    # DB 步骤（Apifox database 处理器）: search the order group by created date
    ctx.run_db(112809, """select
	TO_CHAR(DATE(created_at), 'YYYY-MM-DD') AS order_date,
	COUNT(*) as order_count
from "Order" o
where consumer_id = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'
group by
	TO_CHAR(DATE(created_at), 'YYYY-MM-DD')
order by
	order_date  desc ;""", [('order_date0', '$[0].order_date'), ('order_count0', '$[0].order_count'), ('order_date1', '$[1].order_date'), ('order_count1', '$[1].order_count')])
    _resp8 = ctx.api.orders.consumer(token='linda00_token')
    # assertion 8.assertion: responseJson equal {{order_count1}}
    expect(_resp8).json('$.data.extra[1].count').equals(ctx.render_text('{{order_count1}}'))
    # assertion 8.assertion: responseJson equal {{order_count0}}
    expect(_resp8).json('$.data.extra[0].count').equals(ctx.render_text('{{order_count0}}'))
    # assertion 8.assertion: responseJson equal {{order_date0}}
    expect(_resp8).json('$.data.extra[0].createdDay').equals(ctx.render_text('{{order_date0}}'))
    # assertion 8.assertion: responseJson equal {{order_date1}}
    expect(_resp8).json('$.data.extra[1].createdDay').equals(ctx.render_text('{{order_date1}}'))
