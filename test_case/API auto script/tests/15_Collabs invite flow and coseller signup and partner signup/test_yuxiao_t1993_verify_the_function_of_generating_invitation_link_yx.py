"""Migrated from Apifox case #5526402. Source folder: Collabs invite flow and coseller signup and partner signup."""
# Apifox Case ID: 5526402  (traceability only — not needed to run)
NAME = "Verify the function of generating invitation link-yx"
TAGS = ["p0", "collabs_invite_flow_and_coseller_signup_and_partner_signup", "suite:linda"]
PRIORITY = 0


CASE_ID = 5526402
ENV_NAME = "Release"

# --- step 1: 972a59a0-a5ce-41ed-8831-40870e5a99b8 ---
# post[customScript]: // 1. 解析响应体
# post: const response = pm.response.json();
# post: const data = response.data;
# post: 
# post: /**
# post:  * 2. 提取 ID 为环境变量 new_invitation_link
# post:  */
# post: if (data && data.id) {
# post:     pm.environment.set("new_invitation_link", data.id);
# post:     console.log("成功提取 ID 并存入变量 new_invitation_link:", data.id);
# post: } else {
# post:     pm.expect.fail("提取失败：响应体中没有找到 data.id");
# post: }
# post: 
# post: /**
# post:  * 3. 业务断言
# post:  */
# post: 
# post: /**
# post:  * 校验状态码为 200 或 201
# post:  */
# post: pm.test("Status code is 200 or 201", function () {
# post:     pm.expect(pm.response.code).to.be.oneOf([200, 201]);
# post: });
# post: 
# post: // 断言具体字段内容
# post: pm.test("校验邀请信息详情", () => {
# post:     // 校验描述内容
# post:     pm.expect(data.description).to.eql("automation test by linda");
# post:     
# post:     // 校验邀请码格式（非空字符串）
# post:     pm.expect(data.invitationCode).to.be.a('string').and.not.empty;
# post:     
# post:     // 校验使用状态
# post:     pm.expect(data.used).to.be.false;
# post:     pm.expect(data.usedNum).to.eql(0);
# post: });
# post: 
# post: // 校验时间格式 (ISO Date)
# post: pm.test("创建时间格式正确", () => {
# post:     pm.expect(data.createdAt).to.match(/^\d{4}-\d{2}-\d{2}T/);
# post: });
# --- step 2: invitation link list ---
# pre: var petId = pm.environment.get("new_invitation_link");
# pre: console.log(petId)
# post[customScript]: // 1. 解析响应体
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 获取预期的 ID 变量 (假设存放在环境变量中)
# post: const expectedId = pm.environment.get("new_invitation_link");
# post: 
# post: // 3. 编写断言
# post: pm.test("校验指定 description 对应的 ID 是否正确", function () {
# post:     // 寻找 description 匹配的项
# post:     const targetItem = responseData.data.items.find(item => 
# post:         item.description === "automation test by linda"
# post:     );
# post: 
# post:     // 首先确保找到了该项，避免报错
# post:     pm.expect(targetItem).to.not.be.undefined;
# post: 
# post:     // 校验该项的 id 是否等于变量中的值
# post:     pm.expect(targetItem.id).to.eql(expectedId);
# post:     
# post:     console.log(`校验成功！匹配到的 ID 为: ${targetItem.id}`);
# post: });
# --- step 3: edeb40ed-c93a-4b1e-91c9-7caada7631ec ---
# post[customScript]: // 1. 解析响应 JSON
# post: const response = pm.response.json();
# post: const data = response.data;
# post: 
# post: /**
# post:  * 2. 状态码兼容性断言
# post:  * 兼容外部 201 和内部 code 200 的情况
# post:  */
# post: pm.test("响应状态正常 (200/201)", () => {
# post:     pm.expect(pm.response.code).to.be.oneOf([200, 201]);
# post:     pm.expect(response.code).to.eql(200);
# post: });
# post: 
# post: /**
# post:  * 3. 核心字段断言：Description
# post:  */
# post: pm.test("校验 Description 内容正确", () => {
# post:     // 确保 data 存在
# post:     pm.expect(data).to.be.an('object');
# post:     
# post:     // 精准匹配描述文字
# post:     const expectedDesc = "automation test by linda";
# post:     pm.expect(data.description).to.eql(expectedDesc);
# post:     
# post:     // 额外校验：确保描述不是空的
# post:     pm.expect(data.description).to.be.a('string').and.not.empty;
# post: });
# post: 
# post: /**
# post:  * 4. 辅助校验（可选）
# post:  */
# post: pm.test("校验其他关键字段", () => {
# post:     pm.expect(data.invitationCode).to.have.lengthOf(6); // 校验邀请码长度是否为 6 位
# post:     pm.expect(data.useShortURL).to.be.true;
# post: });
# post: 
# post: // 如果需要提取 ID 供后续使用
# post: if (data && data.id) {
# post:     pm.environment.set("invitation_id", data.id);
# post: }




import json
import re

from core.assertions import expect

def test_yuxiao_t1993_verify_the_function_of_generating_invitation_link_yx(ctx):
    """Apifox case #5526402: Yuxiao_T1993_Verify_the_function_of_generating_invitation_link_yx"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 972a59a0-a5ce-41ed-8831-40870e5a99b8
    _resp1 = ctx.api.promoters.invitation_link_2(body='{\r\n  "description": "automation test by linda",\r\n  "oneTimeUse": false,\r\n  "expiredAt": null,\r\n  "isExpire": false,\r\n  "useShortURL": true\r\n}', token='linda05_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp1.status_code in (200, 201), f"状态码期望200/201，实际={_resp1.status_code}"
    _d1 = _j1.get('data')
    assert _d1 is not None, f"响应缺少data字段，实际={_j1}"
    # 校验邀请信息详情
    assert _d1.get('description') == "automation test by linda", f"description不匹配：{_d1.get('description')!r}"
    assert isinstance(_d1.get('invitationCode'), str) and _d1.get('invitationCode'), f"invitationCode应为非空字符串，实际={_d1.get('invitationCode')!r}"
    assert _d1.get('used') is False, f"used应为false，实际={_d1.get('used')!r}"
    assert _d1.get('usedNum') == 0, f"usedNum应为0，实际={_d1.get('usedNum')!r}"
    # 校验时间格式 (ISO Date)
    _created = _d1.get('createdAt') or ''
    assert re.match(r'^\d{4}-\d{2}-\d{2}T', str(_created)), f"createdAt格式不正确：{_created!r}"
    ctx.extract('new_invitation_link', _resp1, '$.data.id')
    # step 2: invitation link list
    _resp2 = ctx.api.promoters.invitation_link(app_headers=False, token='linda05_token', params={'new invitation-link': '{{new_invitation_link}}'})
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp2.status_code == 200, f"状态码期望200，实际={_resp2.status_code}"
    _d2 = _j2.get('data') or {}
    # Apifox 原文是「取第一条 description 匹配的项，再断言其 id 等于新建 id」——
    # 仅在环境中该 description 只有一条时成立。每条用例都会新建一条同描述的邀请链接，
    # 历史运行遗留后 `next(...)` 取到的是旧记录，断言必然失败（实测取到 c94aa16d… 而新建 c4a50d10…）。
    # 改为：在同描述项里定位「本次新建的那一条」，既保留原断言意图（新链接已出现在列表且描述正确），
    # 又不受遗留数据影响。
    _cands2 = [_item for _item in (_d2.get('items') or []) if _item.get('description') == "automation test by linda"]
    _target2 = next((_item for _item in _cands2 if _item.get('id') == vars.get('new_invitation_link')), None)
    assert _target2 is not None, (
        f"列表中未找到 id={vars.get('new_invitation_link')!r} 的邀请项"
        f"（description='automation test by linda' 共 {len(_cands2)} 条）"
    )
    assert _target2.get('description') == "automation test by linda", f"目标项 description 不符：{_target2.get('description')!r}"
    # step 3: edeb40ed-c93a-4b1e-91c9-7caada7631ec
    _resp3 = ctx.api.promoters.invitation_link_by_new_invitation_link(body=None, token='linda05_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j3 = _resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp3.status_code in (200, 201), f"状态码期望200/201，实际={_resp3.status_code}"
    assert _j3.get('code') == 200, f"响应code期望200，实际={_j3.get('code')!r}"
    _d3 = _j3.get('data')
    assert isinstance(_d3, dict), f"data应为对象，实际={_d3!r}"
    assert _d3.get('description') == "automation test by linda", f"description不匹配：{_d3.get('description')!r}"
    assert len(_d3.get('invitationCode') or '') == 6, f"invitationCode长度应为6，实际={_d3.get('invitationCode')!r}"
    assert _d3.get('useShortURL') is True, f"useShortURL应为true，实际={_d3.get('useShortURL')!r}"
    ctx.extract('invitation_id', _resp3, '$.data.id')
