"""Migrated from Apifox case #8004777. Source folder: Post validation."""
# Apifox Case ID: 8004777  (traceability only — not needed to run)
NAME = "Verify the logic of replace items is correct"
TAGS = ["p0", "post_validation", "suite:linda"]
PRIORITY = 0


CASE_ID = 8004777
ENV_NAME = "Release"

# --- step 1: Get Partner linda05 token ---
# post[extractor]: {"variableName": "linda05_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: pm.environment.set("merchantId", "822a3e59-fdf3-4d9b-be57-f8f0b3af1023");
# post: 
# --- step 2: d20be068-d238-4265-9700-84b9d485cd5f ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: guest get token ---
# pre: 
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 4: Guest visit and check the product display the "Main ticket" ---
# post[customScript]: // 1. 获取响应数据的 data 部分
# post: const jsonData = pm.response.json().data;
# post: 
# post: // --- 严格存在性校验 ---
# post: const mainProduct = jsonData.relatedProducts ? jsonData.relatedProducts[0] : null;
# post: const variant = (mainProduct && mainProduct.variants) ? mainProduct.variants[0] : null;
# post: 
# post: pm.test("Confirm Core Data: Main ticket and Variant Details", function () {
# post:     // Ensure data structures exist before assertion
# post:     pm.expect(mainProduct).to.not.be.null;
# post:     pm.expect(variant).to.not.be.null;
# post: 
# post:     // 1. Validate Product Title
# post:     pm.expect(mainProduct.title).to.eql("Main ticket");
# post:     
# post:     // 2. Validate Variant Fields
# post:     pm.expect(variant.id).to.eql("b50e488e-575c-4e8c-81a4-881c9708fd6d");
# post:     pm.expect(variant.productId).to.eql("5589beae-d2ca-40fc-b361-03122952beb2");
# post:     
# post:     // REMOVED: pm.expect(variant.pointAmount).to.eql(0); // This field does not exist in your JSON
# post:     
# post:     pm.expect(variant.isExcluded).to.be.false;
# post:     pm.expect(variant.isDefault).to.be.false;
# post:     pm.expect(variant.merchantProductVariantId).to.eql("4640fcee-a802-4410-a90d-2fdd4227c777");
# post: });
# post: 
# post: // --- Negative Testing (Exclusion Check) ---
# post: pm.test("Strict Exclusion: Specific productIds and titles must NOT exist", function () {
# post:     const rawBody = pm.response.text();
# post:     
# post:     const forbiddenList = [
# post:         "f0a91cf5-c585-45d9-8b08-f59a6941e6d8",
# post:         "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7",
# post:         "a963f25a-44a3-439f-ae37-1817621f8c11",
# post:         "ticket replace1",
# post:         "ticket replace2",
# post:         "ticket replace3"
# post:     ];
# post: 
# post:     forbiddenList.forEach(item => {
# post:         pm.expect(rawBody).to.not.include(item, `Critical Error: Response contains blacklisted item "${item}"`);
# post:     });
# post: });
# --- step 5: 2e6d8144-f07c-42c1-88cc-e89ec0c94a3b ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: Guest visit and check the product display the "ticket replace1" ---
# post[customScript]: // 1. Get JSON response data
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: 
# post: // --- Part 1: Existence & Core Data Validation ---
# post: pm.test("Check: 'ticket replace1' and Variant core fields", function () {
# post:     // Navigate to the first related product
# post:     const product = data.relatedProducts && data.relatedProducts[0];
# post:     pm.expect(product, "Related product not found").to.exist;
# post:     
# post:     // Validate product title (trimmed to handle potential trailing spaces)
# post:     pm.expect(product.title.trim()).to.include("ticket replace1");
# post: 
# post:     // Navigate to the first Variant
# post:     const variant = product.variants && product.variants[0];
# post:     pm.expect(variant, "Variant not found").to.exist;
# post: 
# post:     // Strict field matching
# post:     pm.expect(variant.id).to.eql("2208929e-4b65-4655-9da9-80a440fd0659");
# post:     pm.expect(variant.productId).to.eql("f0a91cf5-c585-45d9-8b08-f59a6941e6d8");
# post:     pm.expect(variant.price).to.eql("167.77");
# post:     pm.expect(variant.fees).to.eql(17.77);
# post:     
# post:     // Status flags
# post:     pm.expect(variant.isExcluded).to.be.false;
# post:     pm.expect(variant.isDefault).to.be.false;
# post:     pm.expect(variant.merchantProductVariantId).to.eql("935e3c20-64b2-4e1a-95ff-34e68bbf55f4");
# post: });
# post: 
# post: // --- Part 2: Global Non-Existence (Blacklist) Validation ---
# post: pm.test("Check: Forbidden IDs and Titles absolutely absent", function () {
# post:     // Convert entire response to string for deep global search (including bodyHtml/bodyJson)
# post:     const fullBodyString = JSON.stringify(response);
# post: 
# post:     const forbiddenItems = [
# post:         "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7", // Disabled ID 1
# post:         "a963f25a-44a3-439f-ae37-1817621f8c11", // Disabled ID 2
# post:         "Main ticket",                          // Forbidden Title
# post:         "ticket replace2",                      // Forbidden Title
# post:         "ticket replace3"                       // Forbidden Title
# post:     ];
# post: 
# post:     forbiddenItems.forEach(item => {
# post:         pm.expect(fullBodyString).to.not.include(item, `Fatal Error: Forbidden content found in response -> ${item}`);
# post:     });
# post: });
# post: 
# post: // --- Part 3: Rich Text &
# --- step 7: 009021f6-938f-47c9-985b-e40c016d236a ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 8: Guest visit and check the product display the "ticket replace2" ---
# post[customScript]: // Parse the response JSON data
# post: const response = pm.response.json();
# post: const relatedProducts = response.data.relatedProducts || [];
# post: 
# post: /**
# post:  * 1. Validation: Verify specific product "ticket replace2" and its variant details.
# post:  * This checks for the exact Title, ID, ProductID, and Status flags.
# post:  */
# post: pm.test("Check existence of 'ticket replace2' with specific variant properties", function () {
# post:     const targetTitle = "ticket replace2";
# post:     
# post:     // Find the product by title in the relatedProducts array
# post:     const product = relatedProducts.find(item => item.title === targetTitle);
# post:     
# post:     pm.expect(product, `Product with title "${targetTitle}" was not found`).to.not.be.undefined;
# post: 
# post:     // Deeply validate specific fields within the variants array
# post:     const hasSpecificVariant = product.variants.some(v => 
# post:         v.id === "f7df3241-94e5-4d36-8266-94977612f17a" &&
# post:         v.productId === "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7" &&
# post:         v.isExcluded === false &&
# post:         v.isDefault === false &&
# post:         v.merchantProductVariantId === "fe01f82b-267c-4dfe-bdaa-714633d1e355"
# post:     );
# post: 
# post:     pm.expect(hasSpecificVariant, "The expected variant ID or ProductID details do not match the response").to.be.true;
# post: });
# post: 
# post: /**
# post:  * 2. Exclusion Validation (Blacklist): Ensure specific IDs and Titles are completely absent.
# post:  * We stringify the data object to perform a global search for total absence.
# post:  */
# post: pm.test("Verify exclusion of blacklisted IDs and Titles", function () {
# post:     const dataString = JSON.stringify(response.data);
# post: 
# post:     const blacklist = [
# post:         "a963f25a-44a3-439f-ae37-1817621f8c11", // Forbidden ID
# post:         "Main ticket",                        // Forbidden Title
# post:         "ticket replace1",                    // Forbidden Title
# post:         "ticket replace3"                     // Forbidden Title
# post:     ];
# post: 
# post:     blacklist.forEach(item => {
# post:         pm.expect(dataString, `Blacklisted content found: ${item}`).to.not.include(item);
# post:     });
# post: });
# --- step 9: 7c9139f2-c158-4601-98df-529b7a4f4fcd ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: Guest visit and check the product display the "ticket replace1" ---
# post[customScript]: // 1. Parse response data
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: 
# post: // --- Part 1: Core Field Existence & Value Validation ---
# post: pm.test("Verify 'ticket replace1' and its Variant details", function () {
# post:     // Ensure relatedProducts exists and is an array
# post:     pm.expect(data.relatedProducts).to.be.an('array').that.is.not.empty;
# post:     
# post:     const product = data.relatedProducts[0];
# post:     
# post:     // Validate Product Title (using trim to handle trailing spaces in the JSON)
# post:     pm.expect(product.title.trim()).to.eql("ticket replace1");
# post:     pm.expect(product.merchantProductId).to.eql("f0a91cf5-c585-45d9-8b08-f59a6941e6d8");
# post: 
# post:     // Validate Variants array
# post:     pm.expect(product.variants).to.be.an('array').that.is.not.empty;
# post:     const variant = product.variants[0];
# post:     
# post:     // Validate Variant specific IDs and pricing
# post:     pm.expect(variant.id).to.eql("2208929e-4b65-4655-9da9-80a440fd0659");
# post:     pm.expect(variant.price).to.eql("167.77");
# post:     pm.expect(variant.fees).to.eql(17.77);
# post:     
# post:     // Validate Status flags
# post:     pm.expect(variant.isExcluded).to.be.false;
# post:     pm.expect(variant.isDefault).to.be.false;
# post:     pm.expect(variant.merchantProductVariantId).to.eql("935e3c20-64b2-4e1a-95ff-34e68bbf55f4");
# post: });
# post: 
# post: // --- Part 2: Strict Non-Existence (Blacklist) Validation ---
# post: pm.test("Global Blacklist Check: Ensure deleted/disabled items are NOT in response", function () {
# post:     // Stringify the whole response once for efficient global search
# post:     const fullBodyString = JSON.stringify(response);
# post: 
# post:     const forbiddenItems = [
# post:         "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7", // Deleted ID 1
# post:         "a963f25a-44a3-439f-ae37-1817621f8c11", // Deleted ID 2
# post:         "Main ticket",                          // Legacy Title
# post:         "ticket replace2",                      // Forbidden Title
# post:         "ticket replace3"                       // Forbidden Title
# post:     ];
# post: 
# post:     forbiddenItems.forEach(item => {
# post:         pm.expect(fullBodyString).to.not.include(item, `Critical Error: Found forbidden item in response -> ${item}`);
# post:     });
# post: });
# post: 
# post: // --- Part 3: Rich Text (Lexical) Content
# --- step 11: d784d9cc-c945-4be6-9d7e-dd0e86299f0d ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 12: Guest visit and check the product display the "Main ticket" ---
# post[customScript]: // 1. 获取响应数据的 data 部分
# post: const jsonData = pm.response.json().data;
# post: 
# post: // --- 严格存在性校验 ---
# post: const mainProduct = jsonData.relatedProducts ? jsonData.relatedProducts[0] : null;
# post: const variant = (mainProduct && mainProduct.variants) ? mainProduct.variants[0] : null;
# post: 
# post: pm.test("Confirm Core Data: Main ticket and Variant Details", function () {
# post:     // Ensure data structures exist before assertion
# post:     pm.expect(mainProduct).to.not.be.null;
# post:     pm.expect(variant).to.not.be.null;
# post: 
# post:     // 1. Validate Product Title
# post:     pm.expect(mainProduct.title).to.eql("Main ticket");
# post:     
# post:     // 2. Validate Variant Fields
# post:     pm.expect(variant.id).to.eql("b50e488e-575c-4e8c-81a4-881c9708fd6d");
# post:     pm.expect(variant.productId).to.eql("5589beae-d2ca-40fc-b361-03122952beb2");
# post:     
# post:     // REMOVED: pm.expect(variant.pointAmount).to.eql(0); // This field does not exist in your JSON
# post:     
# post:     pm.expect(variant.isExcluded).to.be.false;
# post:     pm.expect(variant.isDefault).to.be.false;
# post:     pm.expect(variant.merchantProductVariantId).to.eql("4640fcee-a802-4410-a90d-2fdd4227c777");
# post: });
# post: 
# post: // --- Negative Testing (Exclusion Check) ---
# post: pm.test("Strict Exclusion: Specific productIds and titles must NOT exist", function () {
# post:     const rawBody = pm.response.text();
# post:     
# post:     const forbiddenList = [
# post:         "f0a91cf5-c585-45d9-8b08-f59a6941e6d8",
# post:         "a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7",
# post:         "a963f25a-44a3-439f-ae37-1817621f8c11",
# post:         "ticket replace1",
# post:         "ticket replace2",
# post:         "ticket replace3"
# post:     ];
# post: 
# post:     forbiddenList.forEach(item => {
# post:         pm.expect(rawBody).to.not.include(item, `Critical Error: Response contains blacklisted item "${item}"`);
# post:     });
# post: });




import json

from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t4259_verify_the_logic_of_replace_items_is_correct(ctx: "Context"):
    """Apifox case #8004777: Linda_T4259_Verify_the_logic_of_replace_items_is_correct"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner linda05 token
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "7EbE8F4BdE4A38768AcF9C2833aF2Db5",
        "email": "linda.zhou.ext+05@1m.app",
    }, app_headers=True)
    # extractor: linda05_token = $.data.token
    ctx.extract('linda05_token', _resp1, '$.data.token')
    vars['merchantId'] = '822a3e59-fdf3-4d9b-be57-f8f0b3af1023'
    # step 2: d20be068-d238-4265-9700-84b9d485cd5f
    _resp2 = ctx.api.posts.curator_update(post_id='{{T4259_post_id}}', body={
    'id': '{{T4259_post_id}}',
    'announcements': [],
    'createFromEventId': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
    'title': 'API Test T4259',
    'subTitle': '',
    'links': [],
    'allowPromotersResell': True,
    'financeModeForPromoters': 'FINANCE_MODE_COMMISSION',
    'financeMode': 'FINANCE_MODE_COMMISSION',
    'status': 'ACTIVE',
    'allowPromotersHideProducts': True,
    'allowPromotersCustomizeMedia': True,
    'allowPromotersCreateCoupon': True,
    'promotions': [
        {
            'promotionId': '1825',
            'applicableCode': 'jZ72wCee',
            'codeAliases': [],
            'oneTimeUsePerCustomer': False,
            'autoApplied': False,
            'isExtend': False,
            'startTime': 1772704733198,
            'title': '',
            'description': '',
            'amountThresholdDiscounts': [
                {
                    'amountThreshold': 100,
                    'discountAmount': 5,
                },
            ],
            'productIdsFilter': [],
        },
    ],
    'isPurchaseQuantityLimited': False,
    'purchaseQuantityLimit': 0,
    'isAccessRestricted': False,
    'allowPromotersAccess': False,
    'styleSettings': {
        'recentUsedColors': [
            '#B7E2E0FF',
            '#FFEEBEFF',
            '#E91E63FF',
            '#757575FF',
            '#0B99FFFF',
            '#F2F2F6FF',
            '#FFFFFF',
        ],
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'secondaryTextColor': '#E0E0E0FF',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontSize': 30,
            'fontFamily': 'Inter',
            'fontWeight': 700,
        },
        'columnTitle': {
            'color': '#FFFFFF',
            'fontSize': 20,
            'fontFamily': 'Inter',
            'fontWeight': 700,
        },
        'subtitle': {
            'color': '#FFFFFF',
            'fontSize': 20,
            'fontFamily': 'Inter',
            'fontWeight': 400,
        },
        'button': {
            'color': '#000000',
            'fontSize': 16,
            'boxShadow': 'none',
            'fontWeight': 400,
            'borderColor': '#0000',
            'borderRadius': 0,
            'backgroundColor': '#F6CA7C',
        },
        'secondaryButton': {
            'color': '#FFFFFF',
            'fontSize': 16,
            'boxShadow': 'none',
            'fontWeight': 400,
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
        },
        'textButton': {
            'color': '#FFFFFF',
            'fontSize': 16,
            'fontWeight': 700,
        },
        'selectButton': {
            'borderColor': '#000000',
        },
        'relatedLink': {
            'color': '#000000 ',
            'borderColor': '#0000',
            'borderRadius': 0,
            'backgroundColor': '#FFFFFF80',
        },
        'featuredProducts': {
            'color': '#FFFFFF',
            'title': {
                'color': '#FFFFFF',
                'fontSize': 14,
                'fontFamily': 'Inter',
                'fontWeight': 400,
            },
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'secondaryTextColor': '#E0E0E0FF',
        },
        'product': {
            'color': '#FFFFFF',
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'secondaryTextColor': '#E0E0E0FF',
        },
        'discount': {
            'color': '#FFFFFF',
            'priceColor': '#FFFFFF',
            'backgroundColor': '#D32A09',
        },
        'freeShipping': {
            'color': '#268E46',
            'backgroundColor': '#EBF5EF',
        },
        'starRatingColor': '#FAAF03',
        'layoutFeatureCard': {
            'color': '#FFFFFF',
            'title': {
                'color': '#FFFFFF',
                'fontSize': 16,
                'fontFamily': 'Inter',
                'fontWeight': 700,
            },
            'button': {
                'color': '#000000',
                'backgroundColor': '#F6CA7C',
            },
            'secondaryTextColor': '#E0E0E0FF',
        },
        'lineupBanner': {
            'titleText': '#FFFFFF',
            'descriptionText': '#F6CA7C',
        },
        'eventInfoBanner': {
            'text': '#FFFFFF',
            'secondaryText': '#ABABAB',
        },
        'eventDescription': {
            'text': '#E0E0E0FF',
            'title': '#FFFFFF',
        },
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'height': 'MEDIUM',
                'displayText': 'SHOP_NAME',
            },
            'productBanner': {
                'display': 'HIDE',
                'ctaButton': 'VIEW_PRODUCT',
            },
        },
        'template': 'ClearSky',
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
    },
    'hideInStore': False,
    'recommendationSectionTitle': '',
    'coverImages': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp',
            'width': 2100,
            'height': 2700,
            'mediaSrc': None,
            'position': 1,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'checkoutInPost': False,
    'allowAffiliateSharingOnly': False,
    'abTestingSettings': [],
    'enableAbTesting': False,
    'isOrderConfirmationNoteEnabled': False,
    'hideCouponBox': False,
    'allowCustomizeDisplayPrices': True,
    'customizeDisplayPrices': {
        'price': '1930 Pacific Ave | Wed, Apr 01 (CDT)',
        'priceColor': '#FFFFFF',
        'titleColor': '#FFFFFF',
        'discountPercent': 'Get Tickets',
        'discountPercentColor': '#D32A08',
    },
    'canSetPrice': False,
    'downlineNoteBodyHtml': None,
    'downlineNoteBodyJson': None,
    'featuredSectionTitle': '',
    'enableRedirectUrl': False,
    'redirectUrl': '',
    'redirectDestinationName': '',
    'event': {
        'id': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
        'status': 'UPCOMING',
        'title': 'API Test T4259 ',
        'venue': '1930 Pacific Ave',
        'location': '1930 Pacific Ave, Dallas, TX 75201, USA',
        'startDateDisplay': '2026-10-01',
        'endDateDisplay': None,
        'timezone': {
            'dstOffset': 3600,
            'rawOffset': -21600,
            'timeZoneId': 'America/Chicago',
            'timeZoneName': 'Central Daylight Time',
        },
        'poster': {
            'src': 'https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp',
            'width': 2100,
            'height': 2700,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    },
    'additionalContentPosition': 'aboveTickets',
    'bodyHtml': '<div class="lexical-root"><div class="katana-paragraph"><div class="event-info-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-node-id="24589ac1-54e1-49ef-a41a-ec4b2a31442a">Event Info</div></div><div class="katana-paragraph"><div class="ticket-banner" data-event-id="0fe6623e-a3ba-40fb-815d-3d6f444775c3" data-product-id="5589beae-d2ca-40fc-b361-03122952beb2" data-node-id="9dabf35b-ea00-4cc0-8b11-0db32f72a021">Buy Ticket</div></div><div class="katana-paragraph"><hr /></div><div class="katana-paragraph"><br></div></div>',
    'currentDate': '2026-03-11T06:10:24.602Z',
    'relatedProducts': [
        {
            'type': 'PRODUCT',
            'merchantProductId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': None,
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 51,
                    'price': 56.67,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '4640fcee-a802-4410-a90d-2fdd4227c777',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': [
                '5589beae-d2ca-40fc-b361-03122952beb2',
            ],
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 151,
                    'price': 167.78,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '935e3c20-64b2-4e1a-95ff-34e68bbf55f4',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': 'a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': [
                'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            ],
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 372.59,
                    'price': 413.99,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': 'fe01f82b-267c-4dfe-bdaa-714633d1e355',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
        {
            'type': 'PRODUCT',
            'merchantProductId': 'a963f25a-44a3-439f-ae37-1817621f8c11',
            'isVisible': True,
            'isPurchaseQuantityLimited': False,
            'isRecommendation': False,
            'hasDependentProducts': False,
            'dependentProductIds': [],
            'isFreeShipping': False,
            'isDefaultToSubscription': False,
            'toReplaceMerchantProductIds': [
                'a4b3f857-e6ae-4ddd-9b5c-692b48b5a3c7',
            ],
            'isCtaCustomized': False,
            'ctaConfig': {
                'type': 'BUY_NOW',
            },
            'syncWithCatalogPrice': True,
            'purchaseQuantityLimit': 1,
            'variants': [
                {
                    'wholesalePriceForPromoters': 930.14,
                    'price': 1033.49,
                    'costPrice': 0,
                    'isExcluded': False,
                    'isDefault': False,
                    'priceAnchor': 0,
                    'merchantProductVariantId': '2b8ff662-991e-4909-ae80-c80b1412a6a5',
                    'commissionRateForPromoters': 10,
                },
            ],
        },
    ],
    'accessSpecificUser': [],
    'featuredSectionEnable': False,
    'tab': {
        'value': 'Commerce',
        'label': 'Commerce',
        'mappingControl': [],
    },
    'timeKey': 1773209424602,
    'originEnablePaymentRestriction': False,
    'syncEnabled': False,
    'postType': 'EVENT',
    'bodyJson': '{"root":{"type":"root","children":[{"type":"katana-paragraph","children":[{"type":"event-info-banner","id":"24589ac1-54e1-49ef-a41a-ec4b2a31442a","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"id":"ba803dee-dc97-4dae-8c8e-16036550249f","type":"additional-content","version":1},{"type":"katana-paragraph","children":[{"type":"ticket-banner","id":"9dabf35b-ea00-4cc0-8b11-0db32f72a021","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","productId":"5589beae-d2ca-40fc-b361-03122952beb2","width":"100%","height":"","ctaLabel":"Buy Ticket","action":"buy-now","layout":"vertical","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"horizontalrule","version":1}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1},{"type":"katana-paragraph","children":[{"type":"post-event-description","id":"2b5c4282-4e48-4c90-88b3-a9d9d1749f05","eventId":"0fe6623e-a3ba-40fb-815d-3d6f444775c3","width":"100%","version":2}],"direction":null,"format":"","indent":0,"textFormat":0,"textStyle":"","version":1}],"direction":"ltr","format":"","indent":0,"version":1},"containerClassName":"","editorClassName":""}',
    'needRefreshHTML': True,
    'additionalContent': '{}',
    'showAdditionalContent': False,
    'media': [
        {
            'id': 'e493ac01-c092-47f3-bf1d-4737f51510d7',
            'src': 'https://res.cloudinary.com/dr9io1zjv/image/upload/v1770866073/uploaded_images/llp1lscl2yyagm1e3tuo.webp',
            'selected': True,
            'type': 'IMAGE',
            'height': 2700,
            'width': 2100,
            'mediaDuration': 0,
            'mediaSrc': None,
            'mediaType': 'IMAGE',
            'inherited': True,
            'position': 1,
            'referenceId': None,
            'source': None,
            'setThumbnail': False,
        },
    ],
    'othersCanCopy': False,
    'enableDownlineNote': False,
    'expiredAt': None,
    'urlAlias': 'api-test-t4259',
    'headline': '10612 Step 2 The Renaissance Room',
    'isPaymentRestrictionEnabled': False,
}, token='linda05_token')
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal ACTIVE
    expect(_resp2).json('$.data.status').equals('ACTIVE')
    # step 3: guest get token
    _resp3 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    })
    vars['access_token'] = (_resp3.json() if _resp3.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 4: Guest visit and check the product display the "Main ticket"
    _resp4 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t4259'})
    # step 5: 2e6d8144-f07c-42c1-88cc-e89ec0c94a3b
    _resp5 = ctx.api.products.v_5589beae_d2ca_40fc_b361_03122952beb2(body={
    'id': '5589beae-d2ca-40fc-b361-03122952beb2',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-03-11T06:01:35.629Z',
    'updatedAt': '2026-03-11T06:05:26.593Z',
    'merchantId': '67f02da6-a49c-4871-b907-f5134a62ece8',
    'title': 'Main ticket',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left"><span style="white-space: pre-wrap;">General Admission Tickets 🎟️ ALL TICKETS ARE FINAL SALE NON-REFUNDABLE DOORS OPEN @7PM</span></p>',
    'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left"><span style="white-space: pre-wrap;">General Admission Tickets 🎟️ ALL TICKETS ARE FINAL SALE NON-REFUNDABLE DOORS OPEN @7PM</span></p>',
    'isBodyHtmlOverridden': False,
    'bodyText': 'General Admission Tickets 🎟️ ALL TICKETS ARE FINAL SALE NON-REFUNDABLE DOORS\nOPEN @7PM',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-03-11T06:01:35.640Z',
    'publishedScope': '',
    'status': 'ACTIVE',
    'externalStatus': 'ACTIVE',
    'followExternalStatus': False,
    'tags': [],
    'templateSuffix': None,
    'vendor': 'Pear',
    'syncAt': None,
    'deletedAt': None,
    'delisted': False,
    'excludedByImportingTag': False,
    'isFeatured': False,
    'featuredScore': None,
    'inventoryQuantity': 1000,
    'inventoryQuantityOriginal': 1000,
    'soldQuantity': 0,
    'priceDisplay': 56.67,
    'priceDisplayAnchor': 0,
    'priceMin': 56.67,
    'priceMinAnchor': 0,
    'priceMax': 56.67,
    'priceMaxAnchor': 0,
    'priceImportedMin': 0,
    'priceImportedMax': 0,
    'imageCount': 1,
    'isUsed': 'NWT',
    'shippingType': 'NO_SHIPPING_REQUIRED',
    'additionalShippingFee': 0,
    'deliveryTime': [
        0,
        5,
    ],
    'returnPolicyApplied': True,
    'isAvailable': True,
    'commissionRate': 10,
    'textForShare': None,
    'priceSyncImported': False,
    'coverImage': {
        'src': 'https://posh-images-originals-production.s3.amazonaws.com/697a8c9aca3b9a7c24ee8202',
        'width': 1200,
        'height': 630,
        'mediaSrc': None,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'reviewCount': None,
    'reviewOverallScore': None,
    'reviewAggregate': None,
    'displayReviews': True,
    'links': None,
    'taxEnable': False,
    'taxJarCategory': '',
    'customTaxRate': None,
    'subscriptionPlanId': None,
    'reviewRedirectProductId': None,
    'reviewSummary': None,
    'customFieldsInfo': None,
    'listingType': 'TICKET',
    'shippingOptions': [],
    'shippingNote': None,
    'autoFulfill': True,
    'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
    'copyFromId': 'f2256921-0a58-426a-9181-16a21e5f78d5',
    'stopSellingAfter': None,
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'isMultipleDaysPassEnabled': False,
    'multipleDaysPass': None,
    'isPickupEtaEnabled': None,
    'atDoorTicketConfig': None,
    'excludeFromPostSync': False,
    'expirationTime': None,
    'allowAtDoorSales': False,
    'options': [
        {
            'remote_id': None,
            'productId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'name': 'Title',
            'position': 1,
            'values': [
                'Default Title',
            ],
            'images': [
                {
                    'value': 'Default Title',
                    'imageId': None,
                },
            ],
        },
    ],
    'variants': [
        {
            'id': '4640fcee-a802-4410-a90d-2fdd4227c777',
            'remote_id': None,
            'createdAt': '2026-03-11T06:05:26.593Z',
            'updatedAt': '2026-03-11T06:05:26.593Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'inventoryQuantity': 0,
            'inventoryQuantityOriginal': 1000,
            'soldQuantity': 0,
            'option': {
                'option1': 'Default Title',
            },
            'position': 1,
            'price': 56.67,
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Default Title',
            'weight': None,
            'weightUnit': None,
            'platform': None,
            'fees': 6.67,
            'transactionFee': {
                'platformFee': 6.67,
                'customFee': 0,
                'customFeeBreakdown': {
                    'TAX': {
                        'unitFixedFee': 0,
                        'unitPercentageFee': 0,
                        'itemFee': 0,
                    },
                },
                'transactionItemFee': 6.67,
            },
            'ticketPrice': 50,
            'isMinPurchaseQuantityEnabled': False,
            'minPurchaseQuantity': None,
            'isMaxPurchaseQuantityEnabled': False,
            'maxPurchaseQuantity': None,
            'isPackSizeEnabled': False,
            'packSize': None,
        },
    ],
    'catalogCommissionRate': 25,
    'earliestTime': '2026-03-11T06:01:35.629Z',
    'styleSettings': {
        'recentUsedColors': [
            '#B7E2E0FF',
            '#FFEEBEFF',
            '#E91E63FF',
            '#757575FF',
            '#0B99FFFF',
            '#F2F2F6FF',
            '#FFFFFF',
        ],
    },
    'isProductFormEnabled': False,
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'overrideEventTax': False,
    'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"General Admission Tickets 🎟️ ALL TICKETS ARE FINAL SALE NON-REFUNDABLE DOORS OPEN @7PM","type":"extended-text","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'id': '75a6c758-9997-4400-b42b-e9821f931c16',
            'remote_id': None,
            'createdAt': '2026-03-11T06:01:35.665Z',
            'updatedAt': '2026-03-11T06:01:35.665Z',
            'height': 630,
            'width': 1200,
            'position': 1,
            'productId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'src': 'https://posh-images-originals-production.s3.amazonaws.com/697a8c9aca3b9a7c24ee8202',
            'variantIds': [],
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'contributedBy': 3,
            'contributorId': None,
            'productImageType': 'PRODUCT',
            'source': None,
        },
    ],
    'eventId': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
    'isExpirationEnabled': False,
}, token='linda05_token')
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson equal success
    expect(_resp5).json('$.message').equals('success')
    # step 6: Guest visit and check the product display the "ticket replace1"
    _resp6 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t4259'})
    # step 7: 009021f6-938f-47c9-985b-e40c016d236a
    _resp7 = ctx.api.products.f0a91cf5_c585_45d9_8b08_f59a6941e6d8(body={
    'id': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-03-11T06:01:35.628Z',
    'updatedAt': '2026-03-11T06:05:34.178Z',
    'merchantId': '67f02da6-a49c-4871-b907-f5134a62ece8',
    'title': 'ticket replace1 ',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left"><span style="white-space: pre-wrap;">**Meet &amp; Greet Ticket (Final Sale):** This ticket grants exclusive pre-show access to meet the artists and DJ No Name with a photo opportunity and brief interaction before the encore experience; all sales are final with no refunds or exchanges.</span></p>',
    'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left"><span style="white-space: pre-wrap;">**Meet &amp; Greet Ticket (Final Sale):** This ticket grants exclusive pre-show access to meet the artists and DJ No Name with a photo opportunity and brief interaction before the encore experience; all sales are final with no refunds or exchanges.</span></p>',
    'isBodyHtmlOverridden': False,
    'bodyText': '**Meet & Greet Ticket (Final Sale):** This ticket grants exclusive pre-show\naccess to meet the artists and DJ No Name with a photo opportunity and brief\ninteraction before the encore experience; all sales are final with no refunds or\nexchanges.',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-03-11T06:01:35.648Z',
    'publishedScope': '',
    'status': 'ACTIVE',
    'externalStatus': 'ACTIVE',
    'followExternalStatus': False,
    'tags': [],
    'templateSuffix': None,
    'vendor': 'Pear',
    'syncAt': None,
    'deletedAt': None,
    'delisted': False,
    'excludedByImportingTag': False,
    'isFeatured': False,
    'featuredScore': None,
    'inventoryQuantity': 150,
    'inventoryQuantityOriginal': 150,
    'soldQuantity': 0,
    'priceDisplay': 167.77,
    'priceDisplayAnchor': 0,
    'priceMin': 167.77,
    'priceMinAnchor': 0,
    'priceMax': 167.77,
    'priceMaxAnchor': 0,
    'priceImportedMin': 0,
    'priceImportedMax': 0,
    'imageCount': 1,
    'isUsed': 'NWT',
    'shippingType': 'NO_SHIPPING_REQUIRED',
    'additionalShippingFee': 0,
    'deliveryTime': [
        0,
        5,
    ],
    'returnPolicyApplied': True,
    'isAvailable': True,
    'commissionRate': 10,
    'textForShare': None,
    'priceSyncImported': False,
    'coverImage': {
        'src': 'https://posh-images-originals-production.s3.amazonaws.com/697a8c9aca3b9a7c24ee8202',
        'width': 1200,
        'height': 630,
        'mediaSrc': None,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'reviewCount': None,
    'reviewOverallScore': None,
    'reviewAggregate': None,
    'displayReviews': True,
    'links': None,
    'taxEnable': False,
    'taxJarCategory': '',
    'customTaxRate': None,
    'subscriptionPlanId': None,
    'reviewRedirectProductId': None,
    'reviewSummary': None,
    'customFieldsInfo': None,
    'listingType': 'TICKET',
    'shippingOptions': [],
    'shippingNote': None,
    'autoFulfill': True,
    'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
    'copyFromId': '80cb53e9-a269-4acc-928d-124e4c43c341',
    'stopSellingAfter': None,
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'isMultipleDaysPassEnabled': False,
    'multipleDaysPass': None,
    'isPickupEtaEnabled': None,
    'atDoorTicketConfig': None,
    'excludeFromPostSync': False,
    'expirationTime': None,
    'allowAtDoorSales': False,
    'options': [
        {
            'remote_id': None,
            'productId': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            'name': 'Title',
            'position': 1,
            'values': [
                'Default Title',
            ],
            'images': [
                {
                    'value': 'Default Title',
                    'imageId': None,
                },
            ],
        },
    ],
    'variants': [
        {
            'id': '935e3c20-64b2-4e1a-95ff-34e68bbf55f4',
            'remote_id': None,
            'createdAt': '2026-03-11T06:03:33.315Z',
            'updatedAt': '2026-03-11T06:03:33.315Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'inventoryQuantity': 0,
            'inventoryQuantityOriginal': 150,
            'soldQuantity': 0,
            'option': {
                'option1': 'Default Title',
            },
            'position': 1,
            'price': 167.77,
            'priceAnchor': '0.00',
            'priceImported': '0.00',
            'productId': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Default Title',
            'weight': None,
            'weightUnit': None,
            'platform': None,
            'fees': 17.77,
            'transactionFee': {
                'platformFee': 17.77,
                'customFee': 0,
                'customFeeBreakdown': {
                    'TAX': {
                        'unitFixedFee': 0,
                        'unitPercentageFee': 0,
                        'itemFee': 0,
                    },
                },
                'transactionItemFee': 17.77,
            },
            'ticketPrice': 150,
            'isMinPurchaseQuantityEnabled': False,
            'minPurchaseQuantity': None,
            'isMaxPurchaseQuantityEnabled': False,
            'maxPurchaseQuantity': None,
            'isPackSizeEnabled': False,
            'packSize': None,
        },
    ],
    'catalogCommissionRate': 25,
    'isReturnPolicyAllowed': True,
    'earliestTime': '2026-03-11T06:01:35.628Z',
    'styleSettings': {
        'recentUsedColors': [
            '#B7E2E0FF',
            '#FFEEBEFF',
            '#E91E63FF',
            '#757575FF',
            '#0B99FFFF',
            '#F2F2F6FF',
            '#FFFFFF',
        ],
    },
    'isProductFormEnabled': False,
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'overrideEventTax': False,
    'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"**Meet & Greet Ticket (Final Sale):** This ticket grants exclusive pre-show access to meet the artists and DJ No Name with a photo opportunity and brief interaction before the encore experience; all sales are final with no refunds or exchanges.","type":"extended-text","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'id': 'b431f33e-f92f-4eca-abc9-c0058bc39b53',
            'remote_id': None,
            'createdAt': '2026-03-11T06:01:35.665Z',
            'updatedAt': '2026-03-11T06:01:35.665Z',
            'height': 630,
            'width': 1200,
            'position': 1,
            'productId': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            'src': 'https://posh-images-originals-production.s3.amazonaws.com/697a8c9aca3b9a7c24ee8202',
            'variantIds': [],
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'contributedBy': 3,
            'contributorId': None,
            'productImageType': 'PRODUCT',
            'source': None,
        },
    ],
    'eventId': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
    'isExpirationEnabled': False,
}, token='linda05_token')
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal success
    expect(_resp7).json('$.message').equals('success')
    # step 8: Guest visit and check the product display the "ticket replace2"
    _resp8 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t4259'})
    # step 9: 7c9139f2-c158-4601-98df-529b7a4f4fcd
    _resp9 = ctx.api.products.f0a91cf5_c585_45d9_8b08_f59a6941e6d8(body={
    'id': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-03-11T06:01:35.628Z',
    'updatedAt': '2026-03-11T06:39:00.346Z',
    'merchantId': '67f02da6-a49c-4871-b907-f5134a62ece8',
    'title': 'ticket replace1 ',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left"><span style="white-space: pre-wrap;">**Meet &amp; Greet Ticket (Final Sale):** This ticket grants exclusive pre-show access to meet the artists and DJ No Name with a photo opportunity and brief interaction before the encore experience; all sales are final with no refunds or exchanges.</span></p>',
    'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left"><span style="white-space: pre-wrap;">**Meet &amp; Greet Ticket (Final Sale):** This ticket grants exclusive pre-show access to meet the artists and DJ No Name with a photo opportunity and brief interaction before the encore experience; all sales are final with no refunds or exchanges.</span></p>',
    'isBodyHtmlOverridden': False,
    'bodyText': '**Meet & Greet Ticket (Final Sale):** This ticket grants exclusive pre-show\naccess to meet the artists and DJ No Name with a photo opportunity and brief\ninteraction before the encore experience; all sales are final with no refunds or\nexchanges.',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-03-11T06:01:35.648Z',
    'publishedScope': '',
    'status': 'ACTIVE',
    'externalStatus': 'ACTIVE',
    'followExternalStatus': False,
    'tags': [],
    'templateSuffix': None,
    'vendor': 'Pear',
    'syncAt': None,
    'deletedAt': None,
    'delisted': False,
    'excludedByImportingTag': False,
    'isFeatured': False,
    'featuredScore': None,
    'inventoryQuantity': 0,
    'inventoryQuantityOriginal': 0,
    'soldQuantity': 0,
    'priceDisplay': 167.77,
    'priceDisplayAnchor': 0,
    'priceMin': 167.77,
    'priceMinAnchor': 0,
    'priceMax': 167.77,
    'priceMaxAnchor': 0,
    'priceImportedMin': 0,
    'priceImportedMax': 0,
    'imageCount': 1,
    'isUsed': 'NWT',
    'shippingType': 'NO_SHIPPING_REQUIRED',
    'additionalShippingFee': 0,
    'deliveryTime': [
        0,
        5,
    ],
    'returnPolicyApplied': True,
    'isAvailable': True,
    'commissionRate': 10,
    'textForShare': None,
    'priceSyncImported': False,
    'coverImage': {
        'src': 'https://posh-images-originals-production.s3.amazonaws.com/697a8c9aca3b9a7c24ee8202',
        'width': 1200,
        'height': 630,
        'mediaSrc': None,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'reviewCount': None,
    'reviewOverallScore': None,
    'reviewAggregate': None,
    'displayReviews': True,
    'links': None,
    'taxEnable': False,
    'taxJarCategory': '',
    'customTaxRate': None,
    'subscriptionPlanId': None,
    'reviewRedirectProductId': None,
    'reviewSummary': None,
    'customFieldsInfo': None,
    'listingType': 'TICKET',
    'shippingOptions': [],
    'shippingNote': None,
    'autoFulfill': True,
    'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
    'copyFromId': '80cb53e9-a269-4acc-928d-124e4c43c341',
    'stopSellingAfter': None,
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'isMultipleDaysPassEnabled': False,
    'multipleDaysPass': None,
    'isPickupEtaEnabled': None,
    'atDoorTicketConfig': None,
    'excludeFromPostSync': False,
    'expirationTime': None,
    'allowAtDoorSales': False,
    'options': [
        {
            'remote_id': None,
            'productId': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            'name': 'Title',
            'position': 1,
            'values': [
                'Default Title',
            ],
            'images': [
                {
                    'value': 'Default Title',
                    'imageId': None,
                },
            ],
        },
    ],
    'variants': [
        {
            'id': '935e3c20-64b2-4e1a-95ff-34e68bbf55f4',
            'remote_id': None,
            'createdAt': '2026-03-11T06:03:33.315Z',
            'updatedAt': '2026-03-11T06:03:33.315Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'inventoryQuantity': 1000,
            'inventoryQuantityOriginal': 0,
            'soldQuantity': 0,
            'option': {
                'option1': 'Default Title',
            },
            'position': 1,
            'price': 167.77,
            'priceAnchor': '0.00',
            'priceImported': '0.00',
            'productId': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Default Title',
            'weight': None,
            'weightUnit': None,
            'platform': None,
            'fees': 17.77,
            'transactionFee': {
                'platformFee': 17.77,
                'customFee': 0,
                'customFeeBreakdown': {
                    'TAX': {
                        'unitFixedFee': 0,
                        'unitPercentageFee': 0,
                        'itemFee': 0,
                    },
                },
                'transactionItemFee': 17.77,
            },
            'ticketPrice': 150,
            'isMinPurchaseQuantityEnabled': False,
            'minPurchaseQuantity': None,
            'isMaxPurchaseQuantityEnabled': False,
            'maxPurchaseQuantity': None,
            'isPackSizeEnabled': False,
            'packSize': None,
        },
    ],
    'catalogCommissionRate': 25,
    'isReturnPolicyAllowed': True,
    'earliestTime': '2026-03-11T06:01:35.628Z',
    'styleSettings': {
        'recentUsedColors': [
            '#B7E2E0FF',
            '#FFEEBEFF',
            '#E91E63FF',
            '#757575FF',
            '#0B99FFFF',
            '#F2F2F6FF',
            '#FFFFFF',
        ],
    },
    'isProductFormEnabled': False,
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'overrideEventTax': False,
    'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"**Meet & Greet Ticket (Final Sale):** This ticket grants exclusive pre-show access to meet the artists and DJ No Name with a photo opportunity and brief interaction before the encore experience; all sales are final with no refunds or exchanges.","type":"extended-text","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'id': 'b431f33e-f92f-4eca-abc9-c0058bc39b53',
            'remote_id': None,
            'createdAt': '2026-03-11T06:01:35.665Z',
            'updatedAt': '2026-03-11T06:01:35.665Z',
            'height': 630,
            'width': 1200,
            'position': 1,
            'productId': 'f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            'src': 'https://posh-images-originals-production.s3.amazonaws.com/697a8c9aca3b9a7c24ee8202',
            'variantIds': [],
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'contributedBy': 3,
            'contributorId': None,
            'productImageType': 'PRODUCT',
            'source': None,
        },
    ],
    'eventId': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
    'isExpirationEnabled': False,
}, token='linda05_token')
    # assertion 9.assertion: responseJson equal 200
    expect(_resp9).json('$.code').equals('200')
    # assertion 9.assertion: responseJson equal success
    expect(_resp9).json('$.message').equals('success')
    # step 10: Guest visit and check the product display the "ticket replace1"
    _resp10 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t4259'})
    # step 11: d784d9cc-c945-4be6-9d7e-dd0e86299f0d
    _resp11 = ctx.api.products.v_5589beae_d2ca_40fc_b361_03122952beb2(body={
    'id': '5589beae-d2ca-40fc-b361-03122952beb2',
    'remote_id': None,
    'platform': 'PEAR',
    'createdAt': '2026-03-11T06:01:35.629Z',
    'updatedAt': '2026-03-11T06:30:34.904Z',
    'merchantId': '67f02da6-a49c-4871-b907-f5134a62ece8',
    'title': 'Main ticket',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left"><span style="white-space: pre-wrap;">General Admission Tickets 🎟️ ALL TICKETS ARE FINAL SALE NON-REFUNDABLE DOORS OPEN @7PM</span></p>',
    'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left"><span style="white-space: pre-wrap;">General Admission Tickets 🎟️ ALL TICKETS ARE FINAL SALE NON-REFUNDABLE DOORS OPEN @7PM</span></p>',
    'isBodyHtmlOverridden': False,
    'bodyText': 'General Admission Tickets 🎟️ ALL TICKETS ARE FINAL SALE NON-REFUNDABLE DOORS\nOPEN @7PM',
    'handle': None,
    'productType': '',
    'publishedAt': '2026-03-11T06:01:35.640Z',
    'publishedScope': '',
    'status': 'ACTIVE',
    'externalStatus': 'ACTIVE',
    'followExternalStatus': False,
    'tags': [],
    'templateSuffix': None,
    'vendor': 'Pear',
    'syncAt': None,
    'deletedAt': None,
    'delisted': False,
    'excludedByImportingTag': False,
    'isFeatured': False,
    'featuredScore': None,
    'inventoryQuantity': 0,
    'inventoryQuantityOriginal': 0,
    'soldQuantity': 0,
    'priceDisplay': 56.67,
    'priceDisplayAnchor': 0,
    'priceMin': 56.67,
    'priceMinAnchor': 0,
    'priceMax': 56.67,
    'priceMaxAnchor': 0,
    'priceImportedMin': 0,
    'priceImportedMax': 0,
    'imageCount': 1,
    'isUsed': 'NWT',
    'shippingType': 'NO_SHIPPING_REQUIRED',
    'additionalShippingFee': 0,
    'deliveryTime': [
        0,
        5,
    ],
    'returnPolicyApplied': True,
    'isAvailable': True,
    'commissionRate': 10,
    'textForShare': None,
    'priceSyncImported': False,
    'coverImage': {
        'src': 'https://posh-images-originals-production.s3.amazonaws.com/697a8c9aca3b9a7c24ee8202',
        'width': 1200,
        'height': 630,
        'mediaSrc': None,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'reviewCount': None,
    'reviewOverallScore': None,
    'reviewAggregate': None,
    'displayReviews': True,
    'links': None,
    'taxEnable': False,
    'taxJarCategory': '',
    'customTaxRate': None,
    'subscriptionPlanId': None,
    'reviewRedirectProductId': None,
    'reviewSummary': None,
    'customFieldsInfo': None,
    'listingType': 'TICKET',
    'shippingOptions': [],
    'shippingNote': None,
    'autoFulfill': True,
    'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
    'copyFromId': 'f2256921-0a58-426a-9181-16a21e5f78d5',
    'stopSellingAfter': None,
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'isMultipleDaysPassEnabled': False,
    'multipleDaysPass': None,
    'isPickupEtaEnabled': None,
    'atDoorTicketConfig': None,
    'excludeFromPostSync': False,
    'expirationTime': None,
    'allowAtDoorSales': False,
    'options': [
        {
            'remote_id': None,
            'productId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'name': 'Title',
            'position': 1,
            'values': [
                'Default Title',
            ],
            'images': [
                {
                    'value': 'Default Title',
                    'imageId': None,
                },
            ],
        },
    ],
    'variants': [
        {
            'id': '4640fcee-a802-4410-a90d-2fdd4227c777',
            'remote_id': None,
            'createdAt': '2026-03-11T06:05:26.593Z',
            'updatedAt': '2026-03-11T06:05:26.593Z',
            'compareAtPrice': None,
            'fulfillmentService': 'manual',
            'grams': 0,
            'imageIds': [],
            'inventoryItemId': None,
            'inventoryManagement': 'Pear',
            'inventoryPolicy': 'DENY',
            'inventoryQuantity': 1000,
            'inventoryQuantityOriginal': 0,
            'soldQuantity': 0,
            'option': {
                'option1': 'Default Title',
            },
            'position': 1,
            'price': 56.67,
            'priceAnchor': '0',
            'priceImported': '0.00',
            'productId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'sku': '',
            'taxCode': None,
            'taxable': True,
            'title': 'Default Title',
            'weight': None,
            'weightUnit': None,
            'platform': None,
            'fees': 6.67,
            'transactionFee': {
                'platformFee': 6.67,
                'customFee': 0,
                'customFeeBreakdown': {
                    'TAX': {
                        'unitFixedFee': 0,
                        'unitPercentageFee': 0,
                        'itemFee': 0,
                    },
                },
                'transactionItemFee': 6.67,
            },
            'ticketPrice': 50,
            'isMinPurchaseQuantityEnabled': False,
            'minPurchaseQuantity': None,
            'isMaxPurchaseQuantityEnabled': False,
            'maxPurchaseQuantity': None,
            'isPackSizeEnabled': False,
            'packSize': None,
        },
    ],
    'catalogCommissionRate': 25,
    'isReturnPolicyAllowed': True,
    'earliestTime': '2026-03-11T06:01:35.629Z',
    'styleSettings': {
        'recentUsedColors': [
            '#B7E2E0FF',
            '#FFEEBEFF',
            '#E91E63FF',
            '#757575FF',
            '#0B99FFFF',
            '#F2F2F6FF',
            '#FFFFFF',
        ],
    },
    'isProductFormEnabled': False,
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'overrideEventTax': False,
    'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"General Admission Tickets 🎟️ ALL TICKETS ARE FINAL SALE NON-REFUNDABLE DOORS OPEN @7PM","type":"extended-text","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'id': '75a6c758-9997-4400-b42b-e9821f931c16',
            'remote_id': None,
            'createdAt': '2026-03-11T06:01:35.665Z',
            'updatedAt': '2026-03-11T06:01:35.665Z',
            'height': 630,
            'width': 1200,
            'position': 1,
            'productId': '5589beae-d2ca-40fc-b361-03122952beb2',
            'src': 'https://posh-images-originals-production.s3.amazonaws.com/697a8c9aca3b9a7c24ee8202',
            'variantIds': [],
            'mediaType': 'IMAGE',
            'mediaSrc': None,
            'mediaDuration': 0,
            'contributedBy': 3,
            'contributorId': None,
            'productImageType': 'PRODUCT',
            'source': None,
        },
    ],
    'eventId': '0fe6623e-a3ba-40fb-815d-3d6f444775c3',
    'isExpirationEnabled': False,
}, token='linda05_token')
    # assertion 11.assertion: responseJson equal 200
    expect(_resp11).json('$.code').equals('200')
    # assertion 11.assertion: responseJson equal success
    expect(_resp11).json('$.message').equals('success')
    # step 12: Guest visit and check the product display the "Main ticket"
    _resp12 = ctx.api.posts.consumer_detail(token='access_token', params={'vanityUrl': 'resident', 'urlAlias': 'api-test-t4259'})
