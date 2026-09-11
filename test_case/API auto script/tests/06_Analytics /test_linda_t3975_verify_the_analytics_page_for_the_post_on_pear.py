"""Migrated from Apifox case #7750519. Source folder: Analytics ."""
# Apifox Case ID: 7750519  (traceability only — not needed to run)
NAME = "Verify the Analytics page for the post on Pear"
TAGS = ["p0", "analytics", "suite:linda"]
PRIORITY = 0


CASE_ID = 7750519
ENV_NAME = "Release"

# --- step 1: da5cc6c6-6328-4a17-8cd8-1c73513bee2c ---
# pre: // ========== 1. 日期处理工具函数 ==========
# pre: /**
# pre:  * 格式化日期为 YYYY-MM-DD 格式（补0，如1月→01，5日→05）
# pre:  * @param {Date} date - 日期对象
# pre:  * @returns {string} 格式化后的日期字符串
# pre:  */
# pre: function formatDate(date) {
# pre:     const year = date.getFullYear();
# pre:     const month = String(date.getMonth() + 1).padStart(2, '0');
# pre:     const day = String(date.getDate()).padStart(2, '0');
# pre:     return `${year}-${month}-${day}`;
# pre: }
# pre: 
# pre: // ========== 2. 计算时间范围（昨天的前一周） ==========
# pre: const today = new Date();          // 获取当前日期
# pre: const yesterday = new Date(today); // 复制当前日期对象
# pre: yesterday.setDate(today.getDate() - 1); // 计算昨天的日期
# pre: 
# pre: const lastWeekOfYesterday = new Date(yesterday); // 复制昨天的日期对象
# pre: lastWeekOfYesterday.setDate(yesterday.getDate() - 7); // 昨天往前推7天
# pre: 
# pre: // 格式化日期
# pre: const endTime = formatDate(yesterday);        // 结束时间：昨天
# pre: const startTime = formatDate(lastWeekOfYesterday); // 开始时间：昨天-7天
# pre: 
# pre: // ========== 3. 替换请求体中的时间 ==========
# pre: const requestBody = pm.request.body.raw;
# pre: if (requestBody) {
# pre:     try {
# pre:         const bodyObj = JSON.parse(requestBody);
# pre:         // 替换timeRanges第一个元素的时间
# pre:         if (bodyObj.timeRanges && bodyObj.timeRanges.length > 0) {
# pre:             bodyObj.timeRanges[0].startTime = startTime;
# pre:             bodyObj.timeRanges[0].endTime = endTime;
# pre:         }
# pre:         // 重新设置请求体（保留JSON格式化缩进）
# pre:         pm.request.body.update(JSON.stringify(bodyObj, null, 2));
# pre:         
# pre:         // 控制台打印调试信息
# pre:         console.log("✅ 时间范围已自动替换：");
# pre:         console.log("startTime（昨天的前7天）：", startTime);
# pre:         console.log("endTime（昨天）：", endTime);
# pre:     } catch (error) {
# pre:         console.error("❌ 替换时间失败：", error.message);
# pre:     }
# pre: }
# post[customScript]: // 1. 解析响应并捕获异常
# post: let responseData;
# post: try {
# post:     responseData = pm.response.json();
# post: } catch (e) {
# post:     pm.test("响应体为有效JSON", () => pm.expect.fail("JSON解析失败: " + e.message));
# post:     return;
# post: }
# post: 
# post: // 2. 校验code和message
# post: pm.test("响应码code等于200", () => {
# post:     pm.expect(responseData).to.have.property("code");
# post:     pm.expect(responseData.code).to.equal(200);
# post: });
# post: 
# post: pm.test("响应消息message等于success", () => {
# post:     pm.expect(responseData).to.have.property("message");
# post:     pm.expect(responseData.message).to.equal("success");
# post: });
# post: 
# post: // 3. 校验totalCount存在且有效
# post: pm.test("totalCount字段存在且值有效", () => {
# post:     pm.expect(responseData).to.have.property("data");
# post:     pm.expect(responseData.data).to.have.property("totalCount");
# post:     const totalCount = responseData.data.totalCount;
# post:     pm.expect(totalCount).to.be.a("number").and.at.least(0);
# post: });
# post: 
# post: // 4. 校验items中的title、vanityUrl、alias
# post: pm.test("items中title、vanityUrl、alias字段有效", () => {
# post:     // 校验data.items存在且非空
# post:     pm.expect(responseData.data).to.have.property("items");
# post:     pm.expect(responseData.data.items).to.be.an("array").and.not.be.empty;
# post:     
# post:     const firstItem = responseData.data.items[0];
# post:     pm.expect(firstItem).to.have.property("detail");
# post:     const detail = firstItem.detail;
# post:     
# post:     // 校验title（存在、非空字符串）
# post:     pm.expect(detail).to.have.property("title");
# post:     pm.expect(detail.title).to.be.a("string").and.not.be.empty;
# post:     pm.expect(detail.title).to.equal("Automation test Event with In-person delivery");
# post:     
# post:     // 校验vanityUrl
# post:     pm.expect(detail).to.have.property("vanityUrl");
# post:     pm.expect(detail.vanityUrl).to.be.a("string").and.equal("lindazhoucurator");
# post:     
# post:     // 校验alias
# post:     pm.expect(detail).to.have.property("alias");
# post:     pm.expect(detail.alias).to.be.a("string").and.equal("automation-test-event-with-in-person-delivery-t4251");
# post: });
# --- step 2: 1fc2ed76-622b-49a4-8e4f-60951912f284 ---
# pre: // ========== 1. 日期处理工具函数 ==========
# pre: /**
# pre:  * 格式化日期为 YYYY-MM-DD 格式（补0，如1月→01，5日→05）
# pre:  * @param {Date} date - 日期对象
# pre:  * @returns {string} 格式化后的日期字符串
# pre:  */
# pre: function formatDate(date) {
# pre:     const year = date.getFullYear();
# pre:     const month = String(date.getMonth() + 1).padStart(2, '0');
# pre:     const day = String(date.getDate()).padStart(2, '0');
# pre:     return `${year}-${month}-${day}`;
# pre: }
# pre: 
# pre: // ========== 2. 计算目标日期 ==========
# pre: const today = new Date(); // 当前日期
# pre: 
# pre: // 计算昨天（-1天）、前天（-2天）、前前前天（-3天）
# pre: const yesterday = new Date(today);
# pre: yesterday.setDate(today.getDate() - 1); // 昨天
# pre: 
# pre: const dayBeforeYesterday = new Date(today);
# pre: dayBeforeYesterday.setDate(today.getDate() - 2); // 前天
# pre: 
# pre: const threeDaysAgo = new Date(today);
# pre: threeDaysAgo.setDate(today.getDate() - 3); // 前前前天
# pre: 
# pre: // 格式化所有日期
# pre: const yesterdayStr = formatDate(yesterday);
# pre: const dayBeforeYesterdayStr = formatDate(dayBeforeYesterday);
# pre: const threeDaysAgoStr = formatDate(threeDaysAgo);
# pre: 
# pre: // ========== 3. 替换请求体中的时间 ==========
# pre: const requestBody = pm.request.body.raw;
# pre: if (requestBody) {
# pre:     try {
# pre:         const bodyObj = JSON.parse(requestBody);
# pre:         // 确保timeRanges数组存在且长度足够
# pre:         if (bodyObj.timeRanges && bodyObj.timeRanges.length >= 3) {
# pre:             // 第一个时间对象：昨天（startTime和endTime都为昨天）
# pre:             bodyObj.timeRanges[0].startTime = yesterdayStr;
# pre:             bodyObj.timeRanges[0].endTime = yesterdayStr;
# pre:             
# pre:             // 第二个时间对象：前天
# pre:             bodyObj.timeRanges[1].startTime = dayBeforeYesterdayStr;
# pre:             bodyObj.timeRanges[1].endTime = dayBeforeYesterdayStr;
# pre:             
# pre:             // 第三个时间对象：前前前天
# pre:             bodyObj.timeRanges[2].startTime = threeDaysAgoStr;
# pre:             bodyObj.timeRanges[2].endTime = threeDaysAgoStr;
# pre:         }
# pre:         // 重新设置请求体（保留JSON缩进，便于查看）
# pre:         pm.request.body.update(JSON.stringify(bodyObj, null, 2));
# pre:         
# pre:         // 控制台打印调试信息，确认替换结果
# pre:         console.log("✅ 时间已自动替换：");
# pre:         console.log("第一个时间（昨天）：", yesterdayStr);
# pre:         console.log("第二个时间（前天）：", dayBeforeYesterdayStr);
# pre:         console.log("第三个时间（前前前天）：", threeDaysAgoStr);
# pre:     } catch (error) {
# pre:         console.error("❌ 替换时间失败：", error.message);
# pre:     }
# pre: }
# post[customScript]: // ========== 1. 解析响应数据（异常处理） ==========
# post: let responseData;
# post: try {
# post:     responseData = pm.response.json();
# post: } catch (error) {
# post:     pm.test("响应体格式校验：返回有效的JSON数据", () => {
# post:         pm.expect.fail(`JSON解析失败，原因：${error.message}`);
# post:     });
# post:     return; // 解析失败时终止后续校验
# post: }
# post: 
# post: // ========== 2. 基础状态字段校验（固定值） ==========
# post: pm.test("基础状态校验：code=200 且 message=success", () => {
# post:     // 校验code字段
# post:     pm.expect(responseData).to.have.property("code");
# post:     pm.expect(responseData.code).to.be.a("number").and.equal(200);
# post:     
# post:     // 校验message字段
# post:     pm.expect(responseData).to.have.property("message");
# post:     pm.expect(responseData.message).to.be.a("string").and.equal("success");
# post:     
# post:     // 校验request_id存在（非空字符串）
# post:     pm.expect(responseData).to.have.property("request_id");
# post:     pm.expect(responseData.request_id).to.be.a("string").and.not.be.empty;
# post: });
# post: 
# post: // ========== 3. 数据层级基础校验 ==========
# post: pm.test("数据结构校验：data/items/totalCount存在且有效", () => {
# post:     // 校验data层级
# post:     pm.expect(responseData).to.have.property("data");
# post:     const data = responseData.data;
# post:     
# post:     // 校验totalCount（存在、数字、≥0，不固定具体值）
# post:     pm.expect(data).to.have.property("totalCount");
# post:     pm.expect(data.totalCount).to.be.a("number").and.at.least(0);
# post:     
# post:     // 校验items数组（存在、非空数组）
# post:     pm.expect(data).to.have.property("items");
# post:     pm.expect(data.items).to.be.an("array").and.not.be.empty;
# post:     
# post:     // 校验第一个item的detail字段存在
# post:     const firstItem = data.items[0];
# post:     pm.expect(firstItem).to.have.property("detail");
# post: });
# post: 
# post: // ========== 4. detail详情字段精准校验（固定值） ==========
# post: pm.test("详情字段校验：title/vanityUrl/alias值正确", () => {
# post:     const detail = responseData.data.items[0].detail;
# post:     
# post:     // 校验title
# post:     pm.expect(detail).to.have.property("title");
# post:     pm.expect(detail.title).to.be.a("string").and.equal("Automation test Event with In-person delivery");
# post:     
# post:     // 校验vanityUrl
# post:     pm.expect(detail).to.have.property("vanityUrl");
# post:     pm.expect(detail.vanityUrl).to.be.a("string").and.equal("lindazhoucurator");
# post:     
# post:     // 校验alias
# post:     pm.expect(detail).to.have.property("alias");
# post:     pm.expect(detail.alias).to.be.a("string").and.equal("automation-test-event-with-in-person-delivery-t4251");
# post: });
# post: 
# post: // ========== 5. 多组mutiStatistics数据校验（动态值仅校验有效性） ==========
# post: pm.test("多组统计数据校验：mutiStatistics结构有效，动态Total值合理", () => {
# post:     const mutiStatistics = responseData.data.items[0].mutiStatistics;
# post:     
# post:     // 校验mutiStatistics是长度为3的数组（结构固定）
# post:     pm.expect(mutiStatistics).to.be.an("array").and.have.lengthOf(3);
# post:     
# post:     // 遍历所有统计组，校验动态Total值的有效性
# post:     mutiStatistics.forEach((stat, index) => {
# post:         pm.test(`第${index+1}组统计数据有效性校验`, () => {
# post:             // 1. 校验Total Unique Visitors的Total值：数字、≥0
# post:             const totalVisitors = stat.visitors["Total Unique Visitors"].total;
# post:             pm.expect(totalVisitors).to.be.a("number").and.at.least(0);
# post:             
# post:             // 2. 校验devices下的Total值（如有）：数字、≥0
# post:             if (stat.devices && Object.keys(stat.devices).length > 0) {
# post:                 Object.values(stat.devices).forEach(device => {
# post:                     pm.expect(device.total).to.be.a("number").and.at.least(0);
# post:                 });
# post:             }
# post:             
# post:             // 3. 校验platforms下的Total值：数字、≥0
# post:             Object.values(stat.platforms).forEach(platform => {
# post:                 pm.expect(platform.total).to.be.a("number").and.at.least(0);
# post:             });
# post:             
# post:             // 4. 校验orderQuantity：数字、≥0（固定规则）
# post:             pm.expect(stat.orderQuantity).to.be.a("number").and.equal(0);
# post:         });
# post:     });
# post: });
# post: 
# post: // ========== 6. 控制台输出动态值（便于调试） ==========
# post: const firstStatTotal = responseData.data.items[0].mutiStatistics[0].visitors["Total Unique Visitors"].total;
# post: console.log("✅ 所有断言执行完成，动态值校验通过");
# post: console.log("第一组访客总数（动态值）：", firstStatTotal);
# post: console.log("mutiStatistics组数：", responseData.data.items[0].mutiStatistics.length);




import datetime
import json

from core.assertions import expect

def test_linda_t3975_verify_the_analytics_page_for_the_post_on_pear(ctx):
    """Apifox case #7750519: Linda_T3975_Verify_the_Analytics_page_for_the_post_on_Pear"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # 动态生成日期范围（对应原 Apifox pre-script 的 formatDate / yesterday 计算）
    _today = datetime.datetime.now()
    _fmt = lambda d: d.strftime('%Y-%m-%d')
    vars['startTime'] = _fmt(_today - datetime.timedelta(days=8))
    vars['endTime'] = _fmt(_today - datetime.timedelta(days=1))
    vars['Yesterday'] = _fmt(_today - datetime.timedelta(days=1))
    vars['dayBeforeYesterday'] = _fmt(_today - datetime.timedelta(days=2))
    vars['threeDaysAgo'] = _fmt(_today - datetime.timedelta(days=3))
    # === Steps ===
    # step 1: da5cc6c6-6328-4a17-8cd8-1c73513bee2c
    _resp1 = ctx.api.analytics.post_summary(body='{\r\n    "postId": [\r\n        "5972f262-ba27-44fc-91cd-cf1054d632a9"\r\n    ],\r\n    "timeRanges": [\r\n        {\r\n            "startTime": "{{startTime}}",\r\n            "endTime": "{{endTime}}"\r\n        }\r\n    ]\r\n}', token='linda01_token')
    # step 2: 1fc2ed76-622b-49a4-8e4f-60951912f284
    _resp2 = ctx.api.analytics.post_summary(body='{\r\n    "postString": [\r\n        "https://release.pear.us/lindazhoucurator/post/automation-test-event-with-in-person-delivery-t4251"\r\n    ],\r\n    "timeRanges": [\r\n        {\r\n            "startTime": "{{Yesterday}}",\r\n            "endTime": "{{Yesterday}}"\r\n        },\r\n        {\r\n            "startTime": "{{dayBeforeYesterday}}",\r\n            "endTime": "{{dayBeforeYesterday}}"\r\n        },\r\n        {\r\n            "startTime": "{{threeDaysAgo}}",\r\n            "endTime": "{{threeDaysAgo}}"\r\n        }\r\n    ]\r\n}', token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    # ---- step1: postId 查询 ----
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    assert _j1.get('code') == 200, f"响应码code应为200，实际={_j1.get('code')!r}"
    assert _j1.get('message') == 'success', f"响应消息message应为success，实际={_j1.get('message')!r}"
    _d1 = _j1.get('data') or {}
    assert isinstance(_d1.get('totalCount'), (int, float)) and _d1.get('totalCount') >= 0, f"totalCount应为非负数字，实际={_d1.get('totalCount')!r}"
    _items1 = _d1.get('items') or []
    assert len(_items1) > 0, "data.items 为空数组"
    _det1 = _items1[0].get('detail') or {}
    assert _det1.get('title') == 'Automation test Event with In-person delivery', f"title不符，实际={_det1.get('title')!r}"
    assert _det1.get('vanityUrl') == 'lindazhoucurator', f"vanityUrl不符，实际={_det1.get('vanityUrl')!r}"
    assert _det1.get('alias') == 'automation-test-event-with-in-person-delivery-t4251', f"alias不符，实际={_det1.get('alias')!r}"
    # ---- step2: postString 查询 ----
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"响应码code应为200，实际={_j2.get('code')!r}"
    assert _j2.get('message') == 'success', f"响应消息message应为success，实际={_j2.get('message')!r}"
    assert isinstance(_j2.get('request_id'), str) and _j2.get('request_id'), f"request_id应为非空字符串，实际={_j2.get('request_id')!r}"
    _d2 = _j2.get('data') or {}
    assert isinstance(_d2.get('totalCount'), (int, float)) and _d2.get('totalCount') >= 0, f"totalCount应为非负数字，实际={_d2.get('totalCount')!r}"
    _items2 = _d2.get('items') or []
    assert len(_items2) > 0, "data.items 为空数组"
    _it2 = _items2[0]
    assert _it2.get('detail') is not None, "第一个item的detail字段缺失"
    _det2 = _it2.get('detail') or {}
    assert _det2.get('title') == 'Automation test Event with In-person delivery', f"title不符，实际={_det2.get('title')!r}"
    assert _det2.get('vanityUrl') == 'lindazhoucurator', f"vanityUrl不符，实际={_det2.get('vanityUrl')!r}"
    assert _det2.get('alias') == 'automation-test-event-with-in-person-delivery-t4251', f"alias不符，实际={_det2.get('alias')!r}"
    _ms2 = _it2.get('mutiStatistics') or []
    assert len(_ms2) == 3, f"mutiStatistics 长度应为3，实际={len(_ms2)}"
    for _i, _stat in enumerate(_ms2):
        _vis = (_stat.get('visitors') or {}).get('Total Unique Visitors') or {}
        assert isinstance(_vis.get('total'), (int, float)) and _vis.get('total') >= 0, f"第{_i+1}组访客总数非法：{_vis.get('total')!r}"
        for _dn, _dv in (_stat.get('devices') or {}).items():
            _dt = (_dv or {}).get('total')
            assert isinstance(_dt, (int, float)) and _dt >= 0, f"第{_i+1}组devices[{_dn}].total非法：{_dt!r}"
        for _pn, _pv in (_stat.get('platforms') or {}).items():
            _pt = (_pv or {}).get('total')
            assert isinstance(_pt, (int, float)) and _pt >= 0, f"第{_i+1}组platforms[{_pn}].total非法：{_pt!r}"
        assert _stat.get('orderQuantity') == 0, f"第{_i+1}组orderQuantity应为0，实际={_stat.get('orderQuantity')!r}"
