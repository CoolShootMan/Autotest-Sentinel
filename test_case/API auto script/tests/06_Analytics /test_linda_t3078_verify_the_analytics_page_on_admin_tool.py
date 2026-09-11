"""Migrated from Apifox case #7750601. Source folder: Analytics ."""
# Apifox Case ID: 7750601  (traceability only — not needed to run)
NAME = "Verify the Analytics page on admin tool"
TAGS = ["p0", "analytics", "suite:linda"]
PRIORITY = 0


CASE_ID = 7750601
ENV_NAME = "Release"

# --- step 1: 23820f4a-f544-410c-a14e-43a6ef2482f0 ---
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
# post[customScript]: // ========== 配置区（便于维护和修改） ==========
# post: const ASSERT_CONFIG = {
# post:   // 基础响应状态配置
# post:   base: {
# post:     code: 200,
# post:     message: "success"
# post:   },
# post:   // 业务字段预期值配置
# post:   business: {
# post:     totalCount: 1, // 实际返回值为1，直接配置在这里
# post:     detail: {
# post:       title: "Automation test Event with In-person delivery",
# post:       vanityUrl: "lindazhoucurator",
# post:       alias: "automation-test-event-with-in-person-delivery-t4251"
# post:     },
# post:     visitors: {
# post:       "Total Unique Visitors": {
# post:         total: 0 // 修正为实际返回的0，解决报错核心问题
# post:       }
# post:     }
# post:   }
# post: };
# post: 
# post: // ========== 1. 解析响应数据（增强异常处理） ==========
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
# post: // ========== 通用工具函数（提升复用性） ==========
# post: /**
# post:  * 安全获取嵌套对象属性，避免层级缺失报错
# post:  * @param {Object} obj 源对象
# post:  * @param {Array} path 属性路径数组，如 ['data', 'items', 0, 'detail']
# post:  * @param {*} defaultValue 默认值（可选）
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
# post:  * 断言2：校验totalCount字段
# post:  */
# post: pm.test("数据总量校验：totalCount存在且值有效", () => {
# post:   // 安全获取totalCount
# post:   const totalCount = getNestedProperty(responseData, ['data', 'totalCount']);
# post:   
# post:   // 校验存在性
# post:   pm.expect(totalCount, "data.totalCount字段缺失").to.not.be.undefined;
# post:   // 校验类型和数值
# post:   pm.expect(totalCount)
# post:     .to.be.a("number", "totalCount应为数字类型")
# post:     .and.at.least(0, "totalCount应≥0")
# post:     .and.equal(ASSERT_CONFIG.business.totalCount, `totalCount应为${ASSERT_CONFIG.business.totalCount}，实际为${totalCount}`);
# post: });
# post: 
# post: /**
# post:  * 断言3：校验items数组中的detail字段
# post:  */
# post: pm.test("详情字段校验：title/vanityUrl/alias存在且值正确", () => {
# post:   // 安全获取第一个item的detail
# post:   const detail = getNestedProperty(responseData, ['data', 'items', 0, 'detail']);
# post:   
# post:   // 校验detail存在
# post:   pm.expect(detail, "第一个item的detail字段缺失").to.not.be.undefined;
# post:   
# post:   // 校验title
# post:   pm.expect(detail).to.have.property("title");
# post:   pm.expect(detail.title)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.business.detail.title, `title应为"${ASSERT_CONFIG.business.detail.title}"，实际为"${detail.title}"`);
# post:   
# post:   // 校验vanityUrl
# post:   pm.expect(detail).to.have.property("vanityUrl");
# post:   pm.expect(detail.vanityUrl)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.business.detail.vanityUrl, `vanityUrl应为"${ASSERT_CONFIG.business.detail.vanityUrl}"，实际为"${detail.vanityUrl}"`);
# post:   
# post:   // 校验alias
# post:   pm.expect(detail).to.have.property("alias");
# post:   pm.expect(detail.alias)
# post:     .to.be.a("string")
# post:     .and.equal(ASSERT_CONFIG.business.detail.alias, `alias应为"${ASSERT_CONFIG.business.detail.alias}"，实际为"${detail.alias}"`);
# post: });
# post: 
# post: /**
# post:  * 断言4：校验访客数等业务数据（修正预期值，解决报错）
# post:  */
# post: pm.test("业务数据校验：Total Unique Visitors总数正确", () => {
# post:   // 安全获取Total Unique Visitors的total值
# post:   const visitorsTotal = getNestedProperty(
# post:     responseData, 
# post:     ['data', 'items', 0, 'mutiStatistics', 0, 'visitors', 'Total Unique Visitors', 'total']
# post:   );
# post:   
# post:   // 校验存在性和值
# post:   pm.expect(visitorsTotal, "Total Unique Visitors.total字段缺失").to.not.be.undefined;
# post:   pm.expect(visitorsTotal)
# post:     .to.be.a("number")
# post:     .and.equal(ASSERT_CONFIG.business.visitors["Total Unique Visitors"].total, 
# post:       `Total Unique Visitors.total应为${ASSERT_CONFIG.business.visitors["Total Unique Visitors"].total}，实际为${visitorsTotal}`);
# post: });
# post: 
# post: // ========== 3. 校验通过提示 ==========
# post: console.log("✅ 所有断言执行完成，核心字段均符合预期");
# post: console.log("当前totalCount值：", getNestedProperty(responseData, ['data', 'totalCount']));
# post: console.log("第一个item的title：", getNestedProperty(responseData, ['data', 'items', 0, 'detail', 'title']));
# --- step 2: cd56c5f5-0e3d-48b5-8dd7-bd8e5595d9b0 ---
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
# post[customScript]: // ========== 1. 解析响应并处理异常 ==========
# post: let responseData;
# post: try {
# post:     responseData = pm.response.json();
# post: } catch (err) {
# post:     pm.test("响应体为有效JSON格式", () => {
# post:         pm.expect.fail(`JSON解析失败：${err.message}`);
# post:     });
# post:     return;
# post: }
# post: 
# post: // ========== 2. 核心状态字段校验（固定值） ==========
# post: pm.test("接口返回状态正常：code=200 且 message=success", () => {
# post:     // 校验code字段存在且值为200
# post:     pm.expect(responseData).to.have.property("code").that.is.a("number").and.equal(200);
# post:     // 校验message字段存在且值为success
# post:     pm.expect(responseData).to.have.property("message").that.is.a("string").and.equal("success");
# post: });
# post: 
# post: // ========== 3. 数据层级结构校验 ==========
# post: pm.test("数据结构完整：data/items/totalCount存在且有效", () => {
# post:     const data = responseData.data;
# post:     // 校验data层级存在
# post:     pm.expect(responseData).to.have.property("data");
# post:     // 校验totalCount：数字、≥0（兼容动态值，当前示例为1）
# post:     pm.expect(data).to.have.property("totalCount").that.is.a("number").and.at.least(0);
# post:     // 校验items数组非空
# post:     pm.expect(data).to.have.property("items").that.is.an("array").and.not.empty;
# post:     
# post:     const firstItem = data.items[0];
# post:     // 校验detail和mutiStatistics字段存在
# post:     pm.expect(firstItem).to.have.property("detail");
# post:     pm.expect(firstItem).to.have.property("mutiStatistics").that.is.an("array").and.have.lengthOf(3);
# post: });
# post: 
# post: // ========== 4. 详情字段精准校验（固定值） ==========
# post: pm.test("详情字段值符合预期", () => {
# post:     const detail = responseData.data.items[0].detail;
# post:     // 校验title
# post:     pm.expect(detail.title).to.equal("Automation test Event with In-person delivery");
# post:     // 校验vanityUrl
# post:     pm.expect(detail.vanityUrl).to.equal("lindazhoucurator");
# post:     // 校验alias
# post:     pm.expect(detail.alias).to.equal("automation-test-event-with-in-person-delivery-t4251");
# post: });
# post: 
# post: // ========== 5. 动态统计数据有效性校验 ==========
# post: pm.test("统计数据格式合法：所有Total值为非负数字", () => {
# post:     const mutiStats = responseData.data.items[0].mutiStatistics;
# post:     
# post:     // 遍历每组统计数据
# post:     mutiStats.forEach((stat, idx) => {
# post:         // 1. 校验Total Unique Visitors的total值
# post:         const totalUV = stat.visitors["Total Unique Visitors"].total;
# post:         pm.expect(totalUV, `第${idx+1}组访客总数`).to.be.a("number").and.at.least(0);
# post:         
# post:         // 2. 校验devices下的total值（如有）
# post:         if (Object.keys(stat.devices).length > 0) {
# post:             Object.values(stat.devices).forEach(device => {
# post:                 pm.expect(device.total).to.be.a("number").and.at.least(0);
# post:             });
# post:         }
# post:         
# post:         // 3. 校验platforms下的total值
# post:         Object.values(stat.platforms).forEach(platform => {
# post:             pm.expect(platform.total).to.be.a("number").and.at.least(0);
# post:         });
# post:         
# post:         // 4. 校验orderQuantity为0（若该值动态，可改为at.least(0)）
# post:         pm.expect(stat.orderQuantity).to.equal(0);
# post:     });
# post: });
# post: 
# post: // ========== 6. 调试信息输出 ==========
# post: console.log("✅ 所有核心校验通过！");
# post: console.log(`当前totalCount：${responseData.data.totalCount}`);
# post: console.log(`第一组访客数：${responseData.data.items[0].mutiStatistics[0].visitors["Total Unique Visitors"].total}`);




import datetime
import json

from core.assertions import expect

def test_linda_t3078_verify_the_analytics_page_on_admin_tool(ctx):
    """Apifox case #7750601: Linda_T3078_Verify_the_Analytics_page_on_admin_tool"""
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
    # step 1: 23820f4a-f544-410c-a14e-43a6ef2482f0
    _resp1 = ctx.api.admin.tracking_post_activities(body='{\r\n    "postId": [\r\n        "5972f262-ba27-44fc-91cd-cf1054d632a9"\r\n    ],\r\n    "timeRanges": [\r\n        {\r\n            "startTime": "{{startTime}}",\r\n            "endTime": "{{endTime}}"\r\n        }\r\n    ]\r\n}', token='admin_token')
    # step 2: cd56c5f5-0e3d-48b5-8dd7-bd8e5595d9b0
    _resp2 = ctx.api.admin.tracking_post_activities(body='{\r\n    "postString": [\r\n        "https://release.pear.us/lindazhoucurator/post/automation-test-event-with-in-person-delivery-t4251"\r\n    ],\r\n    "timeRanges": [\r\n        {\r\n            "startTime": "{{Yesterday}}",\r\n            "endTime": "{{Yesterday}}"\r\n        },\r\n        {\r\n            "startTime": "{{dayBeforeYesterday}}",\r\n            "endTime": "{{dayBeforeYesterday}}"\r\n        },\r\n        {\r\n            "startTime": "{{threeDaysAgo}}",\r\n            "endTime": "{{threeDaysAgo}}"\r\n        }\r\n    ]\r\n}', token='admin_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    # ---- step1: postId 查询 ----
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    assert _j1.get('code') == 200, f"code应为200，实际={_j1.get('code')!r}"
    assert _j1.get('message') == 'success', f"message应为success，实际={_j1.get('message')!r}"
    _d1 = _j1.get('data') or {}
    assert _d1.get('totalCount') == 1, f"totalCount应为1，实际={_d1.get('totalCount')!r}"
    _items1 = _d1.get('items') or []
    assert len(_items1) > 0, "data.items 为空数组"
    _det1 = _items1[0].get('detail') or {}
    assert _det1.get('title') == 'Automation test Event with In-person delivery', f"title不符，实际={_det1.get('title')!r}"
    assert _det1.get('vanityUrl') == 'lindazhoucurator', f"vanityUrl不符，实际={_det1.get('vanityUrl')!r}"
    assert _det1.get('alias') == 'automation-test-event-with-in-person-delivery-t4251', f"alias不符，实际={_det1.get('alias')!r}"
    _ms1 = (_items1[0].get('mutiStatistics') or [{}])[0]
    _uv1 = (_ms1.get('visitors') or {}).get('Total Unique Visitors') or {}
    assert _uv1.get('total') == 0, f"Total Unique Visitors.total 应为0，实际={_uv1.get('total')!r}"
    # ---- step2: postString 查询 ----
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"code应为200，实际={_j2.get('code')!r}"
    assert _j2.get('message') == 'success', f"message应为success，实际={_j2.get('message')!r}"
    _d2 = _j2.get('data') or {}
    assert isinstance(_d2.get('totalCount'), (int, float)) and _d2.get('totalCount') >= 0, f"totalCount应为非负数字，实际={_d2.get('totalCount')!r}"
    _items2 = _d2.get('items') or []
    assert len(_items2) > 0, "data.items 为空数组"
    _it2 = _items2[0]
    assert _it2.get('detail') is not None, "第一个item的detail字段缺失"
    _ms2 = _it2.get('mutiStatistics') or []
    assert len(_ms2) == 3, f"mutiStatistics 长度应为3，实际={len(_ms2)}"
    _det2 = _it2.get('detail') or {}
    assert _det2.get('title') == 'Automation test Event with In-person delivery', f"title不符，实际={_det2.get('title')!r}"
    assert _det2.get('vanityUrl') == 'lindazhoucurator', f"vanityUrl不符，实际={_det2.get('vanityUrl')!r}"
    assert _det2.get('alias') == 'automation-test-event-with-in-person-delivery-t4251', f"alias不符，实际={_det2.get('alias')!r}"
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
