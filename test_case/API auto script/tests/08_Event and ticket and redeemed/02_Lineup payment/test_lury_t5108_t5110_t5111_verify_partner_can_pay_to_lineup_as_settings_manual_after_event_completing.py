"""Migrated from Apifox case #8037428. Source folder: Event and ticket and redeemed/Lineup payment."""
# Apifox Case ID: 8037428  (traceability only — not needed to run)
NAME = "&T5110&T5111 Verify partner can pay to lineup as settings manual after event completing"
TAGS = ["p0", "event_and_ticket_and_redeemed_lineup_payment"]
PRIORITY = 0


CASE_ID = 8037428
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
# --- step 10: Verify P-21 earning summary is not changed ---
# post[assertion]: {"name": "earning is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 11: Verify Partner getPayoutSummary is not changed ---
# post[assertion]: {"name": "Balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 12: Verify promoter earning summary is +10 ---
# pre: var lifetimeEarning_p = pm.environment.get("lifetimeEarning_p");
# pre: console.log(lifetimeEarning_p);
# pre: var lifetimeEarning_p_lineup = eval(lifetimeEarning_p) + 10;
# pre: console.log(lifetimeEarning_p_lineup)
# pre: pm.environment.set("lifetimeEarning_p_lineup",lifetimeEarning_p_lineup)
# pre: 
# post[assertion]: {"name": "Verify the lineup earnings +10", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_p_lineup}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 13: Verify promoter getPayoutSummary is not changed ---
# post[assertion]: {"name": "Verify the lineup balance is not change before payment", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_p}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 14: 41d2912f-f3d1-47f0-a02b-6ddd7992872b ---
# post[customScript]:     if(pm.response.to.have.status(201)){
# post:         var res = JSON.parse(responseBody);
# post:         pm.environment.set("admin_access_token",res['data']['token']);
# post:     }
# --- step 15: 724552f3-338c-48df-bdcf-fe8ffa356e12 ---
# post[customScript]: pm.test("Get merchant order ID", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     var total_count= res["data"]["totalCount"]
# post:     pm.expect(total_count).to.eql(1);
# post: });
# post: 
# --- step 16: 664ef608-9495-4b30-b303-85889cade164 ---
# post[customScript]: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(200);
# post: });
# --- step 17: payment for lineup ---
# post[customScript]: pm.test("Status code is 200", function () {
# post:     pm.response.to.have.status(201);
# post: });
# --- step 18: Verify P-21 earning summary is not changed ---
# post[assertion]: {"name": "earning is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 19: Verify Partner getPayoutSummary is not changed ---
# pre: var balance_amount = pm.environment.get("balance_amount");
# pre: var balance_amount_lineup = eval(balance_amount) - 10;
# pre: console.log(balance_amount_lineup)
# pre: pm.environment.set("balance_amount_lineup",balance_amount_lineup)
# post[assertion]: {"name": "Balance is -10", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_lineup}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 20: Verify promoter earning summary is +10 ---
# pre: var lifetimeEarning_p = pm.environment.get("lifetimeEarning_p");
# pre: console.log(lifetimeEarning_p);
# pre: var lifetimeEarning_p_lineup = eval(lifetimeEarning_p) + 10;
# pre: console.log(lifetimeEarning_p_lineup)
# pre: pm.environment.set("lifetimeEarning_p_lineup",lifetimeEarning_p_lineup)
# pre: 
# post[assertion]: {"name": "Verify the lineup earnings +10", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_p_lineup}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 21: Verify promoter getPayoutSummary is not changed ---
# pre: var balance_amount_p = pm.environment.get("balance_amount_p");
# pre: var balance_amount_p_lineup = eval(balance_amount_p) + 10;
# pre: console.log(balance_amount_p_lineup)
# pre: pm.environment.set("balance_amount_p_lineup",balance_amount_p_lineup)
# post[assertion]: {"name": "Verify the lineup balance is +10 after payment", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_p_lineup}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 22: Verify the lineup payment show in event report ---
# post[assertion]: {"name": "Verify the lineup payment is 10", "subject": "responseJson", "comparison": "equal", "value": "10", "path": "$.data.totalLineupFee", "multipleValue": [], "extractSettings": {"expression": "$.data.totalLineupFee", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify the total net earnings is -10", "subject": "responseJson", "comparison": "equal", "value": "-10", "path": "$.data.netEarnings", "multipleValue": [], "extractSettings": {"expression": "$.data.netEarnings", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_lury_t5108_t5110_t5111_verify_partner_can_pay_to_lineup_as_settings_manual_after_event_completing(ctx):
    """Apifox case #8037428: Lury_T5108_T5110_T5111_Verify_partner_can_pay_to_lineup_as_settings_manual_after"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: P-21-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}', app_headers=True)
    ctx.extract('P-21_access_token', _resp1, '$.data.refreshToken')
    # step 2: P-21 earning summary
    _resp2 = ctx.api.earnings.summary(token='admin_access_token')
    # extractor: lifetimeEarning = $.data.lifetimeEarning
    ctx.extract('lifetimeEarning', _resp2, '$.data.lifetimeEarning')
    # step 3: Partner getPayoutSummary
    _resp3 = ctx.api.earnings.summary_2(token='admin_access_token')
    # extractor: balance_amount = $.data.balance.amount
    ctx.extract('balance_amount', _resp3, '$.data.balance.amount')
    # step 4: Login - merchant
    _resp4 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{merchant_email}}"\n}', app_headers=True)
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
    _resp7 = ctx.api.events.v2(body='{\n    "status": "UPCOMING",\n    "allowAutoComplete": false,\n    "isTaxEnabled": false,\n    "isAddressRevealEnabled": false,\n    "title": "{{post_title}}",\n    "note": "{{post_title}}",\n    "description": "",\n    "location": "{{event_location}}",\n    "venue": "{{event_venue}}",\n    "timezone": {\n        "timeZoneId": "America/New_York",\n        "timeZoneName": "Eastern Standard Time",\n        "dstOffset": 0,\n        "rawOffset": -18000\n    },\n    "poster": {\n        "height": 2048,\n        "width": 3072,\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "mediaType": "IMAGE"\n    },\n    "startDateDisplay": "{{start_time}}"\n}')
    # extractor: event_post_id = event_post_id
    ctx.extract('event_post_id', _resp7, 'event_post_id')
    # extractor: event_id = event_id
    ctx.extract('event_id', _resp7, 'event_id')
    # step 8: Create event ticket
    _resp8 = ctx.api.events.v2_ticket_batch_v2(body='{\n    "poster": {\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "width": 3072,\n        "height": 2048,\n        "position": 0,\n        "mediaType": "IMAGE",\n        "mediaDuration": 0\n    },\n    "listingType": "TICKET",\n    "isTaxEnabled": true,\n    "taxConfig": {\n        "calculationType": "CUSTOM",\n        "customTaxRate": 6\n    },\n    "tickets": [\n        {\n            "listingType": "TICKET",\n            "images": [\n                {\n                    "id": "80f43627-4bef-49b0-934b-cd63d49f8787",\n                    "height": 1000,\n                    "width": 1000,\n                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",\n                    "mediaType": "IMAGE"\n                }\n            ],\n            "title": "t001",\n            "bodyJson": "",\n            "options": [\n                {\n                    "name": "Title",\n                    "values": [\n                        "Default Title"\n                    ],\n                    "images": []\n                }\n            ],\n            "variants": [\n                {\n                    "inventoryQuantity": 100,\n                    "ticketPrice": 1,\n                    "price": 2.38,\n                    "fees": 1.38,\n                    "priceAnchor": 0,\n                    "option": {\n                        "option1": "Default Title"\n                    },\n                    "transactionFee": {\n                        "platformFee": 1.24,\n                        "customFee": 0.14,\n                        "customFeeBreakdown": {\n                            "TAX": {\n                                "unitFixedFee": 0,\n                                "unitPercentageFee": 0.06,\n                                "itemFee":0.14\n                            }\n                        },\n                        "transactionItemFee": 1.38\n                    }\n                }\n            ]\n        }\n    ],\n    "coSellingCommissionRate": 25\n}')
    # assertion 8.get_200_status: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # step 9: Add lineup and payment in event
    _resp9 = ctx.api.events.v2_lineup_batch(body='{\n    "lineup": [\n        {\n            "title": "P-22",\n            "poster": {\n                "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",\n                "width": 160,\n                "height": 160,\n                "mediaType": "IMAGE"\n            },\n            "introduction": "DJ - automation",\n            "isHeadliner": true,\n            "posterBackend": [\n                {\n                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf",\n                    "width": 160,\n                    "height": 160,\n                    "mediaType": "IMAGE"\n                }\n            ],\n            "customRecipientIdentifier": "dian.yuhong.ext+34@1m.app",\n            "recipientVanityUrl": "https://release.pear.us/auto-merchant",\n            "fee": 10,\n            "isPaymentAfterEventEnabled": true,\n            "order": 0\n        }\n    ]\n}')
    # assertion 9.get_status_code: responseJson equal 200
    expect(_resp9).json('$.code').equals('200')
    # step 10: Verify P-21 earning summary is not changed
    _resp10 = ctx.api.earnings.summary()
    # assertion 10.earning is not changed: responseJson equal {{lifetimeEarning}}
    expect(_resp10).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning}}'))
    # step 11: Verify Partner getPayoutSummary is not changed
    _resp11 = ctx.api.earnings.summary_2()
    # assertion 11.Balance is not changed: responseJson equal {{balance_amount}}
    expect(_resp11).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount}}'))
    # step 12: Verify promoter earning summary is +10
    _resp12 = ctx.api.earnings.summary(token='merchant_access_token')
    # assertion 12.Verify the lineup earnings +10: responseJson equal {{lifetimeEarning_p_lineup}}
    expect(_resp12).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning_p_lineup}}'))
    # step 13: Verify promoter getPayoutSummary is not changed
    _resp13 = ctx.api.earnings.summary_2(token='merchant_access_token')
    # assertion 13.Verify the lineup balance is not change before payment: responseJson equal {{balance_amount_p}}
    expect(_resp13).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_p}}'))
    # step 14: 41d2912f-f3d1-47f0-a02b-6ddd7992872b
    _resp14 = ctx.api.admin.auth_login(body='{"email":"dian.yuhong.ext@1m.app","password":"Lastd!y8"}')
    ctx.extract('admin_access_token', _resp14, '$.data.token')
    # step 15: 724552f3-338c-48df-bdcf-fe8ffa356e12
    _resp15 = ctx.api.admin.events_search(body='{\n    "query": "{{event_id}}",\n    "testing": true,\n    "hasPaidTickets": true,\n    "pearOpsSupported": false,\n    "pageSize": 50,\n    "pageNumber": 1\n}', token='admin_access_token')
    # step 16: 664ef608-9495-4b30-b303-85889cade164
    _resp16 = ctx.api.admin.events_by_dup_event_id(body='{"status":"COMPLETED"}', token='admin_access_token', path_vars={'dup_event_id': '{{event_id}}'})
    # step 17: payment for lineup
    _resp17 = ctx.api.events.lineup_transactions(body='{"eventId":"{{event_id}}"}')
    # step 18: Verify P-21 earning summary is not changed
    _resp18 = ctx.api.earnings.summary()
    # assertion 18.earning is not changed: responseJson equal {{lifetimeEarning}}
    expect(_resp18).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning}}'))
    # step 19: Verify Partner getPayoutSummary is not changed
    _resp19 = ctx.api.earnings.summary_2()
    # assertion 19.Balance is -10: responseJson equal {{balance_amount_lineup}}
    expect(_resp19).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_lineup}}'))
    # step 20: Verify promoter earning summary is +10
    _resp20 = ctx.api.earnings.summary(token='merchant_access_token')
    # assertion 20.Verify the lineup earnings +10: responseJson equal {{lifetimeEarning_p_lineup}}
    expect(_resp20).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning_p_lineup}}'))
    # step 21: Verify promoter getPayoutSummary is not changed
    _resp21 = ctx.api.earnings.summary_2(token='merchant_access_token')
    # assertion 21.Verify the lineup balance is +10 after payment: responseJson equal {{balance_amount_p_lineup}}
    expect(_resp21).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_p_lineup}}'))
    # step 22: Verify the lineup payment show in event report
    _resp22 = ctx.api.events.metrics_summary()
    # assertion 22.Verify the lineup payment is 10: responseJson equal 10
    expect(_resp22).json('$.data.totalLineupFee').equals('10')
    # assertion 22.Verify the total net earnings is -10: responseJson equal -10
    expect(_resp22).json('$.data.netEarnings').equals('-10')
