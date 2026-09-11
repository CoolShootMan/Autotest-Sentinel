"""Migrated from Apifox case #5807704. Source folder: Account."""
# Apifox Case ID: 5807704  (traceability only — not needed to run)
NAME = "Verify in payment methods, It can add or delete new cards"
TAGS = ["p0", "account"]
PRIORITY = 0


CASE_ID = 5807704
ENV_NAME = "Release"

# --- step 1: b6e5133c-e65c-449d-a911-058f97c5b6f0 ---
# post[extractor]: {"variableName": "yuxiao999_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: d839d154-8a3c-4fa3-acab-5036fdb85260 ---
# post[extractor]: {"variableName": "Stripeid", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "clientSecret", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.clientSecret", "extractSettings": {"expression": "$.data.clientSecret", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: df310935-2bed-4643-9fdb-8b70acdc688c ---
# post[extractor]: {"variableName": "paymentMethod", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.payment_method", "extractSettings": {"expression": "$.payment_method", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: create payment ---
# post[extractor]: {"variableName": "paymentMethodId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 5: 109a1fd7-38da-4947-9bec-017dad357ab9 ---
# post[extractor]: {"variableName": "methods", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.items", "extractSettings": {"expression": "$.data.items", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}, "extractRange": "partial"}
# post[customScript]: const jsonData = pm.environment.get('methods');
# post: console.log(jsonData)
# post: const targetExternalId = pm.environment.get('paymentMethod');
# post: 
# post: pm.test("Check the new card added on the payment method", function () {
# post:     const data = JSON.parse(jsonData);
# post:     console.log(data, targetExternalId)
# post:     let isContained = false;
# post:     if (data) {
# post:         data.forEach(item => {
# post:             if (item.externalId === targetExternalId) {
# post:                 isContained = true;
# post:             }
# post:         });
# post:     }
# post:     //check the new parment method contains 
# post:     pm.expect(isContained).to.be.true;
# post: });
# --- step 6: 5e22113c-b770-4025-9a39-e696840aa896 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: dfea8472-cddd-447b-a5cf-c1402bde746e ---
# post[extractor]: {"variableName": "methods", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.items", "extractSettings": {"expression": "$.data.items", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}, "extractRange": "partial"}
# post[customScript]: const jsonData = pm.environment.get('methods');
# post: console.log(jsonData)
# post: const targetExternalId = pm.environment.get('paymentMethod');
# post: 
# post: pm.test("Check the new card delete on the payment method", function () {
# post:     const data = JSON.parse(jsonData);
# post:     console.log(data, targetExternalId)
# post:     let isContained = false;
# post:     if (data) {
# post:         data.forEach(item => {
# post:             if (item.externalId === targetExternalId) {
# post:                 isContained = true;
# post:             }
# post:         });
# post:     }
# post:     //check the parment method doesn't contains, it deleted
# post:     pm.expect(isContained).to.be.false;
# post: });




from core.assertions import expect

def test_linda_t917_verify_in_payment_methods_it_can_add_or_delete_new_cards(ctx):
    """Apifox case #5807704: Linda_T917_Verify_in_payment_methods_It_can_add_or_delete_new_cards"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: b6e5133c-e65c-449d-a911-058f97c5b6f0
    _resp1 = ctx.api.auth.sign_in(body='{\r\n    "email": "{{UIauto_partner_email}}",\r\n    "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5"\r\n\r\n}', app_headers=True)
    # extractor: yuxiao999_token = $.data.token
    ctx.extract('yuxiao999_token', _resp1, '$.data.token')
    # step 2: d839d154-8a3c-4fa3-acab-5036fdb85260
    _resp2 = ctx.api.payments.stripe_setup_intent(body='{}', token='yuxiao999_token')
    # extractor: Stripeid = $.data.id
    ctx.extract('Stripeid', _resp2, '$.data.id')
    # extractor: clientSecret = $.data.clientSecret
    ctx.extract('clientSecret', _resp2, '$.data.clientSecret')
    # step 3: df310935-2bed-4643-9fdb-8b70acdc688c
    _resp3 = ctx.api.external.v1_setup_intents_confirm(body=None, token='yuxiao999_token')
    # extractor: paymentMethod = $.payment_method
    ctx.extract('paymentMethod', _resp3, '$.payment_method')
    # step 4: create payment
    _resp4 = ctx.api.payments.method(body='{\n    "billingAddressRequirementLevel": "FULL",\n    "externalId": "{{paymentMethod}}"\n}', token='yuxiao999_token')
    # extractor: paymentMethodId = $.data.id
    ctx.extract('paymentMethodId', _resp4, '$.data.id')
    # assertion 4.assertion: responseJson equal 200
    expect(_resp4).json('$.code').equals('200')
    # step 5: 109a1fd7-38da-4947-9bec-017dad357ab9
    _resp5 = ctx.api.payments.methods(body=None, token='yuxiao999_token')
    # extractor: methods = $.data.items
    ctx.extract('methods', _resp5, '$.data.items')
    # step 6: 5e22113c-b770-4025-9a39-e696840aa896
    _resp6 = ctx.api.payments.method_2(body='{"externalId":"{{paymentMethod}}","paymentMethodId":"{{paymentMethodId}}"}', token='yuxiao999_token')
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # step 7: dfea8472-cddd-447b-a5cf-c1402bde746e
    _resp7 = ctx.api.payments.methods(body=None, token='yuxiao999_token')
    # extractor: methods = $.data.items
    ctx.extract('methods', _resp7, '$.data.items')
