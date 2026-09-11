"""Auto-generated from Apifox case #5961755. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 5961755
# Folder: 
# Case: (Linda)T3164 Verify the OTP option is selected by default if unchecked Default to subscription
# Priority: P0
# Created: 2025-02-10T02:17:32.000Z
# Updated: 2026-08-11T02:31:31.000Z


CASE_ID = 5961755
ENV_NAME = "Release"

# --- step 1: aa94e0f7-e56f-4537-80f9-5d2fe76bec09 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "true", "path": "$.data.freeShipping", "multipleValue": [], "extractSettings": {"expression": "$.data.freeShipping", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: guest login ---
# post[extractor]: {"variableName": "guest_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data", "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: on the post details, Check che catalog price is displayed on the product card and the freeshipping is true ---
# post[assertion]: {"name": "Check the price display is the same as catalog price", "subject": "responseJson", "comparison": "equal", "value": "68", "path": "$.data.relatedProducts[0].priceDisplay", "multipleValue": [], "extractSettings": {"expression": "$.data.relatedProducts[0].priceDisplay", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Check setDefaultSubscription as False", "subject": "responseJson", "comparison": "equal", "value": "false", "path": "$.data.relatedProducts[0].isDefaultToSubscription", "multipleValue": [], "extractSettings": {"expression": "$.data.relatedProducts[0].isDefaultToSubscription", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "true", "path": "$.data.relatedProducts[0].subscriptionPlan.freeShipping", "multipleValue": [], "extractSettings": {"expression": "$.data.relatedProducts[0].subscriptionPlan.freeShipping", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





from core.assertions import expect

def test__5961755__Linda_T3164_Verify_the_OTP_option_is_selected_by_default_if_unchecked_Default_to_subscription(ctx):
    """Apifox case #5961755: Linda_T3164_Verify_the_OTP_option_is_selected_by_default_if_unchecked_Default_to"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: aa94e0f7-e56f-4537-80f9-5d2fe76bec09
    _resp1 = ctx.api.merchants.v_7c2db5d2_92f0_4090_a1ef_55a811b12a6f_subscription_plan_693b2288_c958_4312_92a9_910b948bb6c3(body='{\r\n    "id": "693b2288-c958-4312-92a9-910b948bb6c3",\r\n    "merchantId": "7c2db5d2-92f0-4090-a1ef-55a811b12a6f",\r\n    "status": "ACTIVE",\r\n    "title": "test by linda",\r\n    "optionTitle": "test by linda Title",\r\n    "optionDescription": "test by linda test by linda Title Description Description Description Description Description",\r\n    "freeShipping": true,\r\n    "createdAt": "2024-12-12T07:02:06.763Z",\r\n    "updatedAt": "2024-12-12T07:04:43.172Z",\r\n    "deletedAt": null,\r\n    "options": [\r\n        {\r\n            "id": "b090980b-dc33-447c-85dc-ce46f42da354",\r\n            "subscriptionPlanId": "693b2288-c958-4312-92a9-910b948bb6c3",\r\n            "position": 1,\r\n            "pricingPolicies": [\r\n                {\r\n                    "discountType": "PERCENTAGE",\r\n                    "discountValue": 10\r\n                }\r\n            ],\r\n            "billingPolicy": {\r\n                "interval": "MONTH",\r\n                "intervalCount": 1\r\n            },\r\n            "createdAt": "2024-12-12T07:02:06.763Z",\r\n            "updatedAt": "2024-12-12T07:04:43.192Z",\r\n            "deletedAt": null\r\n        },\r\n        {\r\n            "id": "5920325f-052c-477d-89a5-7d56763ad0d3",\r\n            "subscriptionPlanId": "693b2288-c958-4312-92a9-910b948bb6c3",\r\n            "position": 2,\r\n            "pricingPolicies": [\r\n                {\r\n                    "discountType": "PERCENTAGE",\r\n                    "discountValue": 20\r\n                }\r\n            ],\r\n            "billingPolicy": {\r\n                "interval": "WEEK",\r\n                "intervalCount": 1\r\n            },\r\n            "createdAt": "2024-12-12T07:02:06.763Z",\r\n            "updatedAt": "2024-12-12T07:04:43.192Z",\r\n            "deletedAt": null\r\n        },\r\n        {\r\n            "id": "f631b161-79a6-4f6b-8130-8a2ab235ca4a",\r\n            "subscriptionPlanId": "693b2288-c958-4312-92a9-910b948bb6c3",\r\n            "position": 3,\r\n            "pricingPolicies": [\r\n                {\r\n                    "discountType": "PERCENTAGE",\r\n                    "discountValue": 30\r\n                }\r\n            ],\r\n            "billingPolicy": {\r\n                "interval": "YEAR",\r\n                "intervalCount": 1\r\n            },\r\n            "createdAt": "2024-12-12T07:02:06.763Z",\r\n            "updatedAt": "2024-12-12T07:04:43.193Z",\r\n            "deletedAt": null\r\n        }\r\n    ],\r\n    "contractsCount": 0,\r\n    "contractsCountByOptions": {},\r\n    "productIds": [\r\n        "1646adbb-7714-4efc-862d-238107cf17c0",\r\n        "f8c7d59d-a9c2-4016-a003-300a56c18ec2",\r\n        "0d522260-be08-4a09-8360-595c4823ccd5",\r\n        "9180fbc7-b21a-4601-95a5-0133c8c53faa",\r\n        "08cab0ca-1d5f-4c4f-a848-a04f68555168",\r\n        "04e9a538-01b3-4bfb-b046-d4404df1e161",\r\n        "1c1d1244-ca55-490e-8bdc-5601bb171f85",\r\n        "06453a6a-4b34-45ed-87bd-257133bdbeb4",\r\n        "0ce8352c-4432-4ecf-b4ee-e30eb4e8200e"\r\n    ]\r\n}', token='linda00_token')
    # assertion 1.assertion: responseJson equal true
    expect(_resp1).json('$.data.freeShipping').equals('true')
    # step 2: guest login
    _resp2 = ctx.api.auth.guest_login(body='{\n    "consumerId": "{{__uuid_0}}"\n}', app_headers=False)
    # extractor: guest_token = $.data
    ctx.extract('guest_token', _resp2, '$.data')
    # step 3: on the post details, Check che catalog price is displayed on the product card and the freeshipping is true
    _resp3 = ctx.api.posts.consumer_detail(app_headers=False, token='guest_token', params={'urlAlias': 't3164', 'vanityUrl': 'linda'})
    # assertion 3.Check the price display is the same as catalog price: responseJson equal 68
    expect(_resp3).json('$.data.relatedProducts[0].priceDisplay').equals('68')
    # assertion 3.Check setDefaultSubscription as False: responseJson equal false
    expect(_resp3).json('$.data.relatedProducts[0].isDefaultToSubscription').equals('false')
    # assertion 3.assertion: responseJson equal true
    expect(_resp3).json('$.data.relatedProducts[0].subscriptionPlan.freeShipping').equals('true')
