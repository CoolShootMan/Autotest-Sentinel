"""Auto-generated from Apifox case #6080068. Source folder: . See header comments for the full case name."""
# Apifox Case ID: 6080068
# Folder: 
# Case: (Linda)T1353 Verify new product can be creates successfully
# Priority: P0
# Created: 2025-02-28T07:13:22.000Z
# Updated: 2026-08-11T06:31:37.000Z


CASE_ID = 6080068
ENV_NAME = "Release"

# --- step 1: exist Product ---
# pre: pm.environment.set("merchant_id", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# pre: pm.environment.set("consumer_id", "7bc6ed8d-51de-446b-8c64-fd321cf1a45d");
# pre: 
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "true", "path": "$.data", "multipleValue": [], "extractSettings": {"expression": "$.data", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: create product ---
# pre: pm.environment.set("productId", "{{__uuid_0}}");
# pre: 
# pre: 
# pre: // 假设这是之前定义的生成三位随机数的函数
# pre: function generateThreeDigitRandomNumber() {
# pre:     return Math.floor(Math.random() * 900) + 100;
# pre: }
# pre: 
# pre: // 使用模板字符串进行字符串拼接
# pre: const randomNumber = `API Test T1353 product by linda ${generateThreeDigitRandomNumber()}`;
# pre: console.log(randomNumber);
# pre: 
# pre: 
# pre: 
# pre: pm.environment.set("randomNumber", randomNumber);
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{randomNumber}}", "path": "$.data.title", "multipleValue": [], "extractSettings": {"expression": "$.data.title", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "productId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: delete the product - data clear ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{productId}}", "path": "$.data.id", "multipleValue": [], "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}





from core.assertions import expect

def test__6080068__Linda_T1353_Verify_new_product_can_be_creates_successfully(ctx):
    """Apifox case #6080068: Linda_T1353_Verify_new_product_can_be_creates_successfully"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    vars['merchant_id'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    vars['consumer_id'] = '7bc6ed8d-51de-446b-8c64-fd321cf1a45d'
    # step 1: exist Product
    _resp1 = ctx.api.products.exist_product(token='linda01_token')
    # assertion 1.assertion: responseJson equal true
    expect(_resp1).json('$.data').equals('true')
    # pre: 生成 productId(uuid) 与 randomNumber(带3位随机数)
    import uuid as _uuid, random as _random
    vars['productId'] = str(_uuid.uuid4())
    vars['randomNumber'] = f'API Test T1353 product by linda {_random.randint(100, 999)}'
    # step 2: create product
    _resp2 = ctx.api.products.create(body='{\n    "merchantId": "369c31a5-9272-4abb-a1a6-2c18f7b6f8e3",\n    "shippingType": "INHERIT_SHIPPING",\n    "isFeatured": false,\n    "commissionRate": null,\n    "priceSyncImported": false,\n    "additionalShippingFee": 0,\n    "returnPolicyApplied": true,\n    "title": "{{randomNumber}}",\n    "bodyHtml": "<p class=\\"katana__paragraph katana__paragraph--align-left\\" dir=\\"ltr\\"><br></p>",\n    "status": "ACTIVE",\n    "isUsed": "NWT",\n    "taxJarCategory": "",\n    "platform": "PEAR",\n    "autoFulfill": false,\n    "options": [\n        {\n            "name": "Title",\n            "values": [\n                "Default Title"\n            ],\n            "images": []\n        }\n    ],\n    "variants": [\n        {\n            "inventoryQuantity": 1000,\n            "price": 10,\n            "priceAnchor": 0,\n            "option": {\n                "option1": "Default Title"\n            },\n            "weightUnit": "lb"\n        }\n    ],\n    "excludeFromPostSync": false,\n    "listingType": "REGULAR",\n    "catalogCommissionRate": 25,\n    "shippingOptions": [\n        {\n            "id": "fdbf561b-0a4e-4364-b13d-3faedfbb5569",\n            "catalogId": "369c31a5-9272-4abb-a1a6-2c18f7b6f8e3",\n            "title": "Flat Shipping",\n            "shippingFee": 4.99,\n            "deliveryTime": [\n                0,\n                5\n            ],\n            "enableFreeShippingThreshold": false,\n            "freeShippingThreshold": 0,\n            "note": null,\n            "isDefault": true,\n            "weightBasedShippingRates": null,\n            "enableWeightBasedShippingRates": false,\n            "priceBasedShippingRates": null,\n            "enablePriceBasedShippingRates": false,\n            "profileName": null,\n            "from": "PEAR",\n            "additionalShippingFee": 0,\n            "enableAdditionalShippingFee": false\n        }\n    ],\n    "deliveryMethod": "SHIPPING",\n    "isReturnPolicyAllowed": true,\n    "thirdPartyDeliveryMessage": "",\n    "taxEnable": false,\n    "customTaxRate": null,\n    "earliestTime": "2026-04-15T05:45:21.339Z",\n    "styleSettings": {\n        "recentUsedColors": [\n            "#ECA416FF",\n            "#B7E2E0FF",\n            "#757575FF",\n            "#FFFFFFFF",\n            "#110921FF",\n            "#FFCDD2FF",\n            "#CB135BFF",\n            "#FF9800",\n            "#1B5E20",\n            "#FFF59D",\n            "#F57C00",\n            "#7986CBFF",\n            "#FFEEBEFF",\n            "#7132F4FF",\n            "#616161FF",\n            "#0B99FFFF",\n            "#E0E0E0FF"\n        ]\n    },\n    "isVariantPriceDisplayEnabled": false,\n    "stopSellingAfterDisplay": "",\n    "extraInfo": {\n        "businessTimezone": "Asia/Shanghai"\n    },\n    "overrideEventTax": false,\n    "bodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n    "images": [\n        {\n            "mediaType": "IMAGE",\n            "mediaSrc": null,\n            "mediaDuration": 0,\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762141834/uploaded_images/vdcheuqxljhmyl4oqbnx.webp",\n            "height": 1061,\n            "width": 1500,\n            "source": "UPLOAD",\n            "position": 1,\n            "setThumbnail": true,\n            "origin": {\n                "width": 1500,\n                "height": 1061,\n                "position": 1\n            },\n            "productImageType": "PRODUCT"\n        }\n    ],\n    "isMultipleDaysPassEnabled": false\n}', app_headers=False, token='linda01_token')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal {{randomNumber}}
    expect(_resp2).json('$.data.title').equals(ctx.render_text('{{randomNumber}}'))
    # extractor: productId = $.data.id
    ctx.extract('productId', _resp2, '$.data.id')
    # step 3: delete the product - data clear
    _resp3 = ctx.api.products.by_product_id(app_headers=False, token='linda01_token')
    # assertion 3.assertion: responseJson equal {{productId}}
    expect(_resp3).json('$.data.id').equals(ctx.render_text('{{productId}}'))
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
