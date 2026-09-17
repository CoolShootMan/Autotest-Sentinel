"""Migrated from Apifox case #8177553. Source folder: Event and ticket and redeemed/Lineup payment."""
# Apifox Case ID: 8177553  (traceability only — not needed to run)
NAME = "Verify lineup payment after deleting event"
TAGS = ["p0", "event_and_ticket_and_redeemed_lineup_payment"]
PRIORITY = 0


CASE_ID = 8177553
ENV_NAME = "Release"

# --- step 1: P-21-login ---
# pre: function get_transaction_fee_item_level_general(unit_price,quantity){
# pre:     unit_fixed_fee = 0;
# pre:     item_percentage_fee = 0.085;
# pre:     if (unit_price > 0){
# pre:         return (unit_fixed_fee + unit_price * item_percentage_fee) * quantity
# pre:     }
# pre:     else{
# pre:         return 0
# pre:     }
# pre: }
# pre: var order_level_transaction_fee = Number((4.99 * 0.035).toFixed(2));
# pre: var transaction_fee_item_level = Number((get_transaction_fee_item_level_general(85.5,1)).toFixed(2));
# pre: var p1_transaction_fee = Number(((10/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var curator_transaction_fee = Number(((9/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var promoter_transaction_fee = Number(((4.95/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var p5_transaction_fee = Number(((8.55/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var m1_transaction_fee_item = Number(((40/85.5) * transaction_fee_item_level).toFixed(2));
# pre: var m1_transaction_fee = m1_transaction_fee_item + order_level_transaction_fee
# pre: var merchant_transaction_fee = Number((transaction_fee_item_level - p1_transaction_fee - m1_transaction_fee_item - curator_transaction_fee - promoter_transaction_fee - p5_transaction_fee ).toFixed(2));
# pre: pm.environment.set("m1_transaction_fee", m1_transaction_fee);
# pre: pm.environment.set("p1_transaction_fee", p1_transaction_fee);
# pre: pm.environment.set("merchant_transaction_fee", merchant_transaction_fee);
# pre: pm.environment.set("curator_transaction_fee", curator_transaction_fee);
# pre: pm.environment.set("promoter_transaction_fee", promoter_transaction_fee);
# pre: pm.environment.set("p5_transaction_fee", p5_transaction_fee);
# pre: console.log(transaction_fee_item_level)
# pre: console.log(p1_transaction_fee)
# pre: console.log(merchant_transaction_fee)
# pre: console.log(curator_transaction_fee)
# pre: console.log(promoter_transaction_fee)
# pre: console.log(p5_transaction_fee)
# pre: console.log(m1_transaction_fee)
# pre: 
# post[customScript]: pm.test("Check consumer login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("P-21_access_token",res['data']['refreshToken']);
# post: });
# --- step 2: P-21 earning summary ---
# post[extractor]: {"variableName": "lifetimeEarning", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lifetimeEarning", "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: Partner getPayoutSummary ---
# post[extractor]: {"variableName": "balance_amount", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.balance.amount", "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 4: Login - merchant ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("merchant_access_token",res['data']['token']);
# post: });
# --- step 5: promoter earning summary ---
# post[extractor]: {"variableName": "lifetimeEarning_p", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lifetimeEarning", "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 6: promoter getPayoutSummary ---
# post[extractor]: {"variableName": "balance_amount_p", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.balance.amount", "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 7: Create event ---
# pre: 
# pre: var today = new Date();
# pre: var year = today.getUTCFullYear();
# pre: var day = today.getUTCDate();
# pre: var mon = today.getUTCMonth();
# pre: var newday = day < 10 ? "0"+ day : day;
# pre: var newmon = (mon+1) > 10 ? (mon+1) : "0"+(mon+1);
# pre: console.log(year,newmon,newday)
# pre: var start_time = year + "-" + newmon + "-" + newday + " 23:59"
# pre: console.log(start_time)
# pre: pm.environment.set("start_time", start_time);
# pre: 
# pre: var post_title = "Lury automation lineup payment";
# pre: var location = "123 West Lane Avenue, Columbus, OH";
# pre: var event_venu = "123 Street";
# pre: pm.environment.set("post_title", post_title);
# pre: pm.environment.set("location", location);
# pre: pm.environment.set("event_venu", event_venu);
# pre: 
# post[customScript]: pm.test("Get catalog id and event id", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     var event_post_id = res['data']['autoCreatedPostId'];
# post:     var event_id = res['data']['id'];
# post:     pm.environment.set("event_post_id", event_post_id);
# post:     pm.environment.set("event_id", event_id);
# post:     console.log(event_id)
# post:     console.log(event_post_id)
# post: })
# --- step 8: Create event ticket ---
# post[assertion]: {"name": "get_200_status", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 9: Add lineup and payment in event ---
# post[assertion]: {"name": "get_status_code", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "lineup_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lineup[0].id", "extractSettings": {"expression": "$.data.lineup[0].id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 10: Delete event ---
# --- step 11: Verify P-21 earning summary is not changed ---
# post[assertion]: {"name": "earning is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 12: Verify Partner getPayoutSummary is not changed ---
# post[assertion]: {"name": "Balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 13: Verify promoter earning summary is +10 ---
# post[assertion]: {"name": "Verify the old lineup earnings is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_p}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 14: Verify promoter getPayoutSummary is not changed ---
# post[assertion]: {"name": "Verify the lineup balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_p}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_t5118_verify_lineup_payment_after_deleting_event(ctx: "Context"):
    """Apifox case #8177553: Lury_T5118_Verify_lineup_payment_after_deleting_event"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: P-21-login
    _resp1 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{M1}}",
    }, app_headers=True)
    ctx.extract('P-21_access_token', _resp1, '$.data.refreshToken')
    # step 2: P-21 earning summary
    _resp2 = ctx.api.earnings.summary()
    # extractor: lifetimeEarning = $.data.lifetimeEarning
    ctx.extract('lifetimeEarning', _resp2, '$.data.lifetimeEarning')
    # step 3: Partner getPayoutSummary
    _resp3 = ctx.api.earnings.summary_2()
    # extractor: balance_amount = $.data.balance.amount
    ctx.extract('balance_amount', _resp3, '$.data.balance.amount')
    # step 4: Login - merchant
    _resp4 = ctx.api.auth.sign_in(body={
        "password": "{{merchant_password}}",
        "email": "{{merchant_email}}",
    }, app_headers=True)
    ctx.extract('merchant_access_token', _resp4, '$.data.token')
    # step 5: promoter earning summary
    _resp5 = ctx.api.earnings.summary(token='merchant_access_token')
    # extractor: lifetimeEarning_p = $.data.lifetimeEarning
    ctx.extract('lifetimeEarning_p', _resp5, '$.data.lifetimeEarning')
    # step 6: promoter getPayoutSummary
    _resp6 = ctx.api.earnings.summary_2(token='merchant_access_token')
    # extractor: balance_amount_p = $.data.balance.amount
    ctx.extract('balance_amount_p', _resp6, '$.data.balance.amount')
    # step 7: Create event
    _resp7 = ctx.api.events.v2(body={
        "status": "UPCOMING",
        "allowAutoComplete": False,
        "isTaxEnabled": False,
        "isAddressRevealEnabled": False,
        "title": "{{post_title}}",
        "note": "{{post_title}}",
        "description": "",
        "location": "{{event_location}}",
        "venue": "{{event_venue}}",
        "timezone": {
            "timeZoneId": "America/New_York",
            "timeZoneName": "Eastern Standard Time",
            "dstOffset": 0,
            "rawOffset": -18000,
        },
        "poster": {
            "height": 2048,
            "width": 3072,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "mediaType": "IMAGE",
        },
        "startDateDisplay": "{{start_time}}",
    })
    # extractor: event_post_id = event_post_id
    ctx.extract('event_post_id', _resp7, 'event_post_id')
    # extractor: event_id = event_id
    ctx.extract('event_id', _resp7, 'event_id')
    # step 8: Create event ticket
    _resp8 = ctx.api.events.v2_ticket_batch_v2(body={
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'listingType': 'TICKET',
    'isTaxEnabled': True,
    'taxConfig': {
        'calculationType': 'CUSTOM',
        'customTaxRate': 6,
    },
    'tickets': [
        {
            'listingType': 'TICKET',
            'images': [
                {
                    'id': '80f43627-4bef-49b0-934b-cd63d49f8787',
                    'height': 1000,
                    'width': 1000,
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png',
                    'mediaType': 'IMAGE',
                },
            ],
            'title': 't001',
            'bodyJson': '',
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
                    'inventoryQuantity': 100,
                    'ticketPrice': 1,
                    'price': 2.38,
                    'fees': 1.38,
                    'priceAnchor': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'transactionFee': {
                        'platformFee': 1.24,
                        'customFee': 0.14,
                        'customFeeBreakdown': {
                            'TAX': {
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0.06,
                                'itemFee': 0.14,
                            },
                        },
                        'transactionItemFee': 1.38,
                    },
                },
            ],
        },
    ],
    'coSellingCommissionRate': 25,
})
    # assertion 8.get_200_status: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # step 9: Add lineup and payment in event
    _resp9 = ctx.api.events.v2_lineup_batch(body={
        "lineup": [
            {
                "title": "P-22",
                "poster": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",
                    "width": 160,
                    "height": 160,
                    "mediaType": "IMAGE",
                },
                "introduction": "DJ - automation",
                "isHeadliner": True,
                "posterBackend": [
                    {
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",
                        "width": 160,
                        "height": 160,
                        "mediaType": "IMAGE",
                    },
                ],
                "customRecipientIdentifier": "dian.yuhong.ext+34@1m.app",
                "recipientVanityUrl": "https://release.pear.us/auto-merchant",
                "fee": 10,
                "isPaymentAfterEventEnabled": True,
                "order": 0,
            },
        ],
    })
    # assertion 9.get_status_code: responseJson equal 200
    expect(_resp9).json('$.code').equals('200')
    # extractor: lineup_id = $.data.lineup[0].id
    ctx.extract('lineup_id', _resp9, '$.data.lineup[0].id')
    # step 10: Delete event
    _resp10 = ctx.api.events.by_event_id()
    # step 11: Verify P-21 earning summary is not changed
    _resp11 = ctx.api.earnings.summary()
    # assertion 11.earning is not changed: responseJson equal {{lifetimeEarning}}
    expect(_resp11).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning}}'))
    # step 12: Verify Partner getPayoutSummary is not changed
    _resp12 = ctx.api.earnings.summary_2()
    # assertion 12.Balance is not changed: responseJson equal {{balance_amount}}
    expect(_resp12).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount}}'))
    # step 13: Verify promoter earning summary is +10
    _resp13 = ctx.api.earnings.summary(token='merchant_access_token')
    # assertion 13.Verify the old lineup earnings is not changed: responseJson equal {{lifetimeEarning_p}}
    expect(_resp13).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning_p}}'))
    # step 14: Verify promoter getPayoutSummary is not changed
    _resp14 = ctx.api.earnings.summary_2(token='merchant_access_token')
    # assertion 14.Verify the lineup balance is not changed: responseJson equal {{balance_amount_p}}
    expect(_resp14).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_p}}'))
