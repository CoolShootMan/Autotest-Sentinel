"""Migrated from Apifox case #7627714. Source folder: Customer Campaign ."""
# Apifox Case ID: 7627714  (traceability only — not needed to run)
NAME = "Verify partner can delete campaign on campaigns page"
TAGS = ["p1", "customer_campaign", "suite:linda"]
PRIORITY = 1


CASE_ID = 7627714
ENV_NAME = "Release"

# --- step 1: baf038c4-2513-47dc-a2b3-d3483e839bf4 ---
# post[customScript]: // ========== 1. 解析接口响应数据 ==========
# post: const responseData = pm.response.json();
# post: // 严格校验响应结构，避免脚本异常
# post: if (!responseData || !responseData.data || !Array.isArray(responseData.data.items)) {
# post:     console.error("【错误】接口响应格式异常，未找到任务列表");
# post:     pm.environment.set("randomLindaAutomationId", ""); // 无数据时置空
# post:     return;
# post: }
# post: 
# post: const taskList = responseData.data.items;
# post: console.log("【初始】任务列表总数:", taskList.length);
# post: 
# post: // ========== 2. 筛选符合条件的任务ID ==========
# post: // 筛选条件：name含'autmation by linda' + status为DRAFT/COMPLETED
# post: const targetIds = taskList
# post:     .filter(task => {
# post:         if (!task.name || !task.status) return false;
# post:         const isNameMatch = task.name.includes("automation by linda");
# post:         const isStatusMatch = ["DRAFT", "COMPLETED"].includes(task.status);
# post:         return isNameMatch && isStatusMatch;
# post:     })
# post:     .map(task => task.id);
# post: 
# post: console.log("【筛选结果】符合条件的ID列表:", targetIds);
# post: console.log("【筛选结果】符合条件的ID数量:", targetIds.length);
# post: 
# post: // ========== 3. 随机抽取1个ID（核心优化） ==========
# post: let randomId = "";
# post: if (targetIds.length > 0) {
# post:     // 生成0 ~ 列表长度-1的随机索引
# post:     const randomIndex = Math.floor(Math.random() * targetIds.length);
# post:     randomId = targetIds[randomIndex];
# post:     console.log("【随机抽取】选中的ID:", randomId);
# post: } else {
# post:     console.warn("【警告】未找到符合条件的ID，无法抽取随机值");
# post: }
# post: 
# post: // ========== 4. 存储到环境变量（供下一个删除接口使用） ==========
# post: pm.environment.set("randomLindaAutomationId", randomId);
# post: console.log("【环境变量设置完成】变量名: randomLindaAutomationId，值:", randomId);
# --- step 2: 7fda4001-c1fe-4cf1-99f5-70714c1f51d8 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: a42d8fc3-6065-4fc4-abae-3795299a8f64 ---
# post[customScript]: // ========== 1. 读取待校验的删除ID（从环境变量中获取） ==========
# post: const deletedId = pm.environment.get("randomLindaAutomationId");
# post: // 先校验ID是否存在
# post: if (!deletedId) {
# post:     console.error("【校验失败】环境变量randomLindaAutomationId为空，无待校验的删除ID");
# post:     pm.environment.set("deleteVerifyResult", "failed"); // 标记校验失败
# post:     return;
# post: }
# post: console.log("【校验目标】待验证是否删除的ID:", deletedId);
# post: 
# post: // ========== 2. 解析GET接口返回的JSON数据 ==========
# post: const getResponseData = pm.response.json();
# post: // 严格校验GET接口响应结构
# post: if (!getResponseData || !getResponseData.data || !Array.isArray(getResponseData.data.items)) {
# post:     console.error("【校验失败】GET接口响应格式异常，无法提取任务ID列表");
# post:     pm.environment.set("deleteVerifyResult", "failed");
# post:     return;
# post: }
# post: 
# post: // 提取GET接口返回的所有任务ID
# post: const currentTaskIds = getResponseData.data.items.map(task => task.id);
# post: console.log("【GET接口返回】当前所有任务ID列表:", currentTaskIds);
# post: 
# post: // ========== 3. 核心校验：判断ID是否已被删除 ==========
# post: let isDeleted = false;
# post: if (!currentTaskIds.includes(deletedId)) {
# post:     isDeleted = true;
# post:     console.log(`【校验成功】ID ${deletedId} 已被成功删除（不在GET接口返回列表中）`);
# post:     pm.environment.set("deleteVerifyResult", "success"); // 标记删除成功
# post: } else {
# post:     console.error(`【校验失败】ID ${deletedId} 未被删除（仍存在于GET接口返回列表中）`);
# post:     pm.environment.set("deleteVerifyResult", "failed"); // 标记删除失败
# post: }
# post: 
# post: // ========== 4. 额外：输出校验总结（方便快速查看结果） ==========
# post: console.log(`
# post: ===== 删除结果校验总结 =====
# post: 待删除ID：${deletedId}
# post: 是否删除成功：${isDeleted ? "✅ 是" : "❌ 否"}
# post: 当前GET接口返回的任务总数：${currentTaskIds.length}
# post: `);




import json

from core.assertions import expect

def test_linda_t4676_verify_partner_can_delete_campaign_on_campaigns_page(ctx):
    """Apifox case #7627714: Linda_T4676_Verify_partner_can_delete_campaign_on_campaigns_page"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: baf038c4-2513-47dc-a2b3-d3483e839bf4
    _resp1 = ctx.api.campaigns.list(body=None, params={'search': '', 'pageSize': '30', 'pageNumber': '1'}, token='linda01_token')
    # customScript: 从 campaigns 列表筛选 name 含 "automation by linda" 且 status 为 DRAFT/COMPLETED 的任务，随机取一个 id
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    _items = ((_j1 or {}).get('data') or {}).get('items') or []
    _targets = [t.get('id') for t in _items
                if t.get('name') and t.get('status')
                and 'automation by linda' in t.get('name')
                and t.get('status') in ('DRAFT', 'COMPLETED')]
    import random as _random
    vars['randomLindaAutomationId'] = _random.choice(_targets) if _targets else ''
    # step 2: 7fda4001-c1fe-4cf1-99f5-70714c1f51d8
    _resp2 = ctx.api.campaigns.by_random_linda_automation_id(body=None, token='linda01_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3: a42d8fc3-6065-4fc4-abae-3795299a8f64
    _resp3 = ctx.api.campaigns.list(body=None, params={'search': '', 'pageSize': '30', 'pageNumber': '1'}, token='linda01_token')
    vars['deleteVerifyResult'] = 'failed'
    vars['deleteVerifyResult'] = 'failed'
    vars['deleteVerifyResult'] = 'success'
    vars['deleteVerifyResult'] = 'failed'
