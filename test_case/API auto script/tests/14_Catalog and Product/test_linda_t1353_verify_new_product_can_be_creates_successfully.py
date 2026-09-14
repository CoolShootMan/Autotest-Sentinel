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
    _resp2 = ctx.api.products.create(body={
    'merchantId': '369c31a5-9272-4abb-a1a6-2c18f7b6f8e3',
    'shippingType': 'INHERIT_SHIPPING',
    'isFeatured': False,
    'commissionRate': None,
    'priceSyncImported': False,
    'additionalShippingFee': 0,
    'returnPolicyApplied': True,
    'title': '{{randomNumber}}',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'status': 'ACTIVE',
    'isUsed': 'NWT',
    'taxJarCategory': '',
    'platform': 'PEAR',
    'autoFulfill': False,
    'options': [
        {
            'name': 'Title',
            'values': [
                'Default Title',
            ],
            'images': [],
        },
    ],
    'variants': [
        {
            'inventoryQuantity': 1000,
            'price': 10,
            'priceAnchor': 0,
            'option': {
                'option1': 'Default Title',
            },
            'weightUnit': 'lb',
        },
    ],
    'excludeFromPostSync': False,
    'listingType': 'REGULAR',
    'catalogCommissionRate': 25,
    'shippingOptions': [
        {
            'id': 'fdbf561b-0a4e-4364-b13d-3faedfbb5569',
            'catalogId': '369c31a5-9272-4abb-a1a6-2c18f7b6f8e3',
            'title': 'Flat Shipping',
            'shippingFee': 4.99,
            'deliveryTime': [
                0,
                5,
            ],
            'enableFreeShippingThreshold': False,
            'freeShippingThreshold': 0,
            'note': None,
            'isDefault': True,
            'weightBasedShippingRates': None,
            'enableWeightBasedShippingRates': False,
            'priceBasedShippingRates': None,
            'enablePriceBasedShippingRates': False,
            'profileName': None,
            'from': 'PEAR',
            'additionalShippingFee': 0,
            'enableAdditionalShippingFee': False,
        },
    ],
    'deliveryMethod': 'SHIPPING',
    'isReturnPolicyAllowed': True,
    'thirdPartyDeliveryMessage': '',
    'taxEnable': False,
    'customTaxRate': None,
    'earliestTime': '2026-04-15T05:45:21.339Z',
    'styleSettings': {
        'recentUsedColors': [
            '#ECA416FF',
            '#B7E2E0FF',
            '#757575FF',
            '#FFFFFFFF',
            '#110921FF',
            '#FFCDD2FF',
            '#CB135BFF',
            '#FF9800',
            '#1B5E20',
            '#FFF59D',
            '#F57C00',
            '#7986CBFF',
            '#FFEEBEFF',
            '#7132F4FF',
            '#616161FF',
            '#0B99FFFF',
            '#E0E0E0FF',
        ],
    },
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'extraInfo': {
        'businessTimezone': 'Asia/Shanghai',
    },
    'overrideEventTax': False,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762141834/uploaded_images/vdcheuqxljhmyl4oqbnx.webp',
            'height': 1061,
            'width': 1500,
            'source': 'UPLOAD',
            'position': 1,
            'setThumbnail': True,
            'origin': {
                'width': 1500,
                'height': 1061,
                'position': 1,
            },
            'productImageType': 'PRODUCT',
        },
    ],
    'isMultipleDaysPassEnabled': False,
}, app_headers=False, token='linda01_token')
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
