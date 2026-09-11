"""Migrated from Apifox case #6179660. Source folder: Account."""
# Apifox Case ID: 6179660  (traceability only — not needed to run)
NAME = "Verify the shipping address can be added or deleted success"
TAGS = ["p1", "account", "suite:linda"]
PRIORITY = 1


CASE_ID = 6179660
ENV_NAME = "Release"

# --- step 1: get address list ---
# post[customScript]: // 1. 获取接口返回的JSON数据
# post: const responseData = pm.response.json();
# post: 
# post: // 2. 初始化地址ID变量（默认空值）
# post: let addressId = "";
# post: 
# post: // 3. 提取有效ID（优先默认地址，无则取第一个）
# post: if (responseData.data && responseData.data.items && responseData.data.items.length > 0) {
# post:     // 先找isDefault=true的默认地址
# post:     const defaultAddress = responseData.data.items.find(item => item.isDefault === true);
# post:     if (defaultAddress) {
# post:         addressId = defaultAddress.id;
# post:     } else {
# post:         // 无默认地址则取第一个地址的ID
# post:         addressId = responseData.data.items[0].id;
# post:     }
# post: }
# post: 
# post: // 4. 存入APIFOX全局变量（供下单接口引用）
# post: pm.globals.set("addressId", addressId)
# post: 
# post: // 【可选】打印日志验证（APIFOX控制台查看）
# post: console.log("提取的有效地址ID：", addressId);
# --- step 2: c3467ada-0ce8-4680-a3a1-83d3a356557f ---
# post[extractor]: {"variableName": "addess_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 672d4660-7657-4d0b-a10a-ebd7361919a2 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "API TEST", "path": "$.data.firstName", "multipleValue": [], "extractSettings": {"expression": "$.data.firstName", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_linda_t3354_verify_the_shipping_address_can_be_added_or_deleted_success(ctx):
    """Apifox case #6179660: Linda_T3354_Verify_the_shipping_address_can_be_added_or_deleted_success"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: get address list
    _resp1 = ctx.api.address.list(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    # step 2: c3467ada-0ce8-4680-a3a1-83d3a356557f
    _resp2 = ctx.api.address.create(body='{\r\n  "isDefault": false,\r\n  "phoneNumber": "17484538034",\r\n  "firstName": "API TEST",\r\n  "lastName": "linda",\r\n  "line1": "test",\r\n  "line2": "test",\r\n  "city": "london",\r\n  "state": "CA",\r\n  "zipcode": "90021", \r\n  "ignoreVerifyPhoneNumber": false\r\n}', token='linda10_token')
    # extractor: addess_id = $.data.id
    ctx.extract('address_id', _resp2, '$.data.id')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # step 3: 672d4660-7657-4d0b-a10a-ebd7361919a2
    _resp3 = ctx.api.address.by_address_id(body=None, token='linda10_token')
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal API TEST
    expect(_resp3).json('$.data.firstName').equals('API TEST')
