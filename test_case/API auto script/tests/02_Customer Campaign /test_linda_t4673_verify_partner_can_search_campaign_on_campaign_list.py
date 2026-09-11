"""Migrated from Apifox case #7631212. Source folder: Customer Campaign ."""
# Apifox Case ID: 7631212  (traceability only — not needed to run)
NAME = "Verify partner can search campaign on campaign list"
TAGS = ["p1", "customer_campaign", "suite:linda"]
PRIORITY = 1


CASE_ID = 7631212
ENV_NAME = "Release"

# --- step 1: 625a24c5-4f07-433d-87de-a920142dd9ff ---
# post[customScript]: // ========== 1. 定义校验基准（search关键词） ==========
# post: const targetSearchKey = "automation"; // 本次校验的search关键词
# post: console.log(`【校验目标】验证search=${targetSearchKey}的返回结果准确性`);
# post: 
# post: // ========== 2. 修复：提取请求URL中的search参数（Node.js兼容方式） ==========
# post: const requestUrl = pm.request.url.toString(); // 获取完整请求URL
# post: let requestSearchKey = "";
# post: 
# post: // 从URL中分割出查询参数部分（?后面的内容）
# post: const queryStr = requestUrl.split("?")[1] || "";
# post: if (queryStr) {
# post:     // 将查询参数拆分为[key=value]数组
# post:     const queryParams = queryStr.split("&");
# post:     // 遍历找到search对应的参数值
# post:     queryParams.forEach(param => {
# post:         const [key, value] = param.split("=");
# post:         if (key === "search") {
# post:             requestSearchKey = decodeURIComponent(value); // 解码URL编码的字符
# post:         }
# post:     });
# post: }
# post: 
# post: console.log("【请求参数】实际请求的search值:", requestSearchKey);
# post: 
# post: if (requestSearchKey !== targetSearchKey) {
# post:     console.warn(`【警告】请求的search参数(${requestSearchKey})与目标关键词(${targetSearchKey})不一致`);
# post: }
# post: 
# post: // ========== 3. 解析响应数据并校验基础结构 ==========
# post: const responseData = pm.response.json();
# post: let verifyResult = "success"; // 默认校验成功
# post: const verifyErrors = []; // 存储校验失败的原因
# post: 
# post: // 校验1：响应状态码和message
# post: if (responseData.code !== 200) {
# post:     verifyErrors.push(`响应code错误：期望200，实际${responseData.code}`);
# post:     verifyResult = "failed";
# post: }
# post: if (responseData.message !== "success") {
# post:     verifyErrors.push(`响应message错误：期望success，实际${responseData.message}`);
# post:     verifyResult = "failed";
# post: }
# post: 
# post: // 校验2：data字段结构（items是数组、totalCount/PageSize/PageNumber存在）
# post: if (!responseData.data) {
# post:     verifyErrors.push("响应缺少data字段");
# post:     verifyResult = "failed";
# post: } else {
# post:     if (!Array.isArray(responseData.data.items)) {
# post:         verifyErrors.push("data.items不是数组格式");
# post:         verifyResult = "failed";
# post:     }
# post:     if (typeof responseData.data.totalCount !== "number") {
# post:         verifyErrors.push("data.totalCount不是数字格式");
# post:         verifyResult = "failed";
# post:     }
# post:     if (typeof responseData.data.pageSize !== "number") {
# post:         verifyErrors.push("data.pageSize不是数字格式");
# post:         verifyResult = "failed";
# post:     }
# post:     if (typeof responseData.data.pageNumber !== "number") {
# post:         verifyErrors.push("data.pageNumber不是数字格式");
# post:         verifyResult = "failed";
# post:     }
# post: }
# post: 
# post: // ========== 4. 核心校验：所有items的name都包含targetSearchKey ==========
# post: const taskItems = responseData.data?.items || [];
# post: console.log(`【响应数据】返回的任务数量：${taskItems.length}，总数量totalCount：${responseData.data?.totalCount || 0}`);
# post: 
# post: if (taskItems.length > 0) {
# post:     taskItems.forEach((task, index) => {
# post:         const taskName = task.name || "";
# post:         // 校验name字段存在且包含目标关键词
# post:         if (!taskName.includes(targetSearchKey)) {
# post:             verifyErrors.push(`第${index+1}条任务name不包含${targetSearchKey}：${taskName}（ID：${task.id || "无"}）`);
# post:             verifyResult = "failed";
# post:         }
# post:     });
# post: } else {
# post:     verifyErrors.push("data.items为空数组，无数据可校验");
# post:     verifyResult = "failed";
# post: }
# post: 
# post: // 校验5：当前页数量与totalCount匹配（pageNumber=1且pageSize≥totalCount时，items长度应等于totalCount）
# post: if (responseData.data?.pageNumber === 1 && responseData.data?.pageSize >= responseData.data?.totalCount) {
# post:     if (taskItems.length !== responseData.data.totalCount) {
# post:         verifyErrors.push(`当前页数据量不匹配：期望${responseData.data.totalCount}条，实际${taskItems.length}条`);
# post:         verifyResult = "failed";
# post:     }
# post: }
# post: 
# post: // ========== 5. 输出校验结果（结构化日志） ==========
# post: console.log(`
# post: ===== search=${targetSearchKey} 校验结果 =====
# post: 最终结论：${verifyResult === "success" ? "✅ 全部校验通过" : "❌ 存在校验失败项"}
# post: 失败原因：${verifyErrors.length > 0 ? verifyErrors.join("；") : "无"}
# post: `);
# post: 
# post: // 若有失败项，逐条打印详情
# post: if (verifyErrors.length > 0) {
# post:     console.error("【失败详情】：");
# post:     verifyErrors.forEach((err, index) => {
# post:         console.error(`${index+1}. ${err}`);
# post:     });
# post: }
# post: 
# post: // ========== 6. 存储校验结果到环境变量 ==========
# post: pm.environment.set("searchVerifyResult", verifyResult);
# post: pm.environment.set("searchVerifyErrors", JSON.stringify(verifyErrors));




import json

from core.assertions import expect

def test_linda_t4673_verify_partner_can_search_campaign_on_campaign_list(ctx):
    """Apifox case #7631212: Linda_T4673_Verify_partner_can_search_campaign_on_campaign_list"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 625a24c5-4f07-433d-87de-a920142dd9ff
    _resp1 = ctx.api.campaigns.list(body=None, params={'search': 'automation', 'pageSize': '30', 'pageNumber': '1'}, token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    # 校验1: code 与 message
    assert _j1.get('code') == 200, f"响应code错误：期望200，实际={_j1.get('code')!r}"
    assert _j1.get('message') == 'success', f"响应message错误：期望success，实际={_j1.get('message')!r}"
    # 校验2: data 结构（items 数组 + 分页字段数字类型）
    _d1 = _j1.get('data')
    assert _d1 is not None, "响应缺少data字段"
    assert isinstance(_d1.get('items'), list), f"data.items不是数组格式，实际类型={type(_d1.get('items')).__name__}"
    assert isinstance(_d1.get('totalCount'), (int, float)), f"data.totalCount不是数字，实际={_d1.get('totalCount')!r}"
    assert isinstance(_d1.get('pageSize'), (int, float)), f"data.pageSize不是数字，实际={_d1.get('pageSize')!r}"
    assert isinstance(_d1.get('pageNumber'), (int, float)), f"data.pageNumber不是数字，实际={_d1.get('pageNumber')!r}"
    # 校验3: 核心——所有 items.name 包含搜索关键词 automation
    _items = _d1.get('items') or []
    assert len(_items) > 0, "data.items为空数组，无数据可校验"
    for _i, _task in enumerate(_items):
        _name = _task.get('name') or ''
        assert 'automation' in _name, f"第{_i+1}条任务name不包含automation：{_name}（ID:{_task.get('id') or '无'}）"
    # 校验4: 分页数量一致性（pageNumber=1 且 pageSize>=totalCount 时 items 长度应等于 totalCount）
    if _d1.get('pageNumber') == 1 and _d1.get('pageSize') >= _d1.get('totalCount'):
        assert len(_items) == _d1.get('totalCount'), f"当前页数据量不匹配：期望{_d1.get('totalCount')}条，实际{len(_items)}条"
