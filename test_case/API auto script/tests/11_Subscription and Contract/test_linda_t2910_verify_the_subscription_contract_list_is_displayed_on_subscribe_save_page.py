"""Migrated from Apifox case #6130186. Source folder: Subscription and Contract."""
# Apifox Case ID: 6130186  (traceability only — not needed to run)
NAME = "Verify the subscription contract list is displayed on subscribe & save page"
TAGS = ["p0", "subscription_and_contract", "suite:linda"]
PRIORITY = 0


CASE_ID = 6130186
ENV_NAME = "Release"

# --- step 1:  Verify contract list is displayed ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: //  随机校验返回列表存在某个contract id
# post: 
# post: function validateFields() {
# post:     const jsonData = pm.response.json();
# post:     const items = jsonData.data.items;
# post:     for (let i = 0; i < items.length; i++) {
# post:         const item = items[i];
# post:         if (item.contractNumber === "PRC1825" && item.status === "CANCELED") {
# post:             return true;
# post:         }
# post:     }
# post:     return false;
# post: }
# post: 
# post: const isValid = validateFields();
# post: console.log(isValid ? "the contract PRC1825 exist and status is CANCELED " : "NOT FOUND");




from core.assertions import expect

def test_linda_t2910_verify_the_subscription_contract_list_is_displayed_on_subscribe_save_page(ctx):
    """Apifox case #6130186: Linda_T2910_Verify_the_subscription_contract_list_is_displayed_on_subscribe_save"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1:  Verify contract list is displayed
    _resp1 = ctx.api.users.self_contracts(token='linda10_token', params={'pageSize': '30', 'pageNumber': '1'})
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
