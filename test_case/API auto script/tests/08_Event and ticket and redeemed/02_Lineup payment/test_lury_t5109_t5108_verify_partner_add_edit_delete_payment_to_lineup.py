"""Migrated from Apifox case #8041780. Source folder: Event and ticket and redeemed/Lineup payment."""
# Apifox Case ID: 8041780  (traceability only — not needed to run)
NAME = "&T5108 Verify partner add/edit/delete payment to lineup"
TAGS = ["p0", "event_and_ticket_and_redeemed_lineup_payment"]
PRIORITY = 0


CASE_ID = 8041780
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
# --- step 14: Verify the lineup payment before event completed ---
# post[assertion]: {"name": "Verify the lineup payment is 0", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.totalLineupFee", "multipleValue": [], "extractSettings": {"expression": "$.data.totalLineupFee", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "Verify the total net earnings is 0", "subject": "responseJson", "comparison": "equal", "value": "0", "path": "$.data.netEarnings", "multipleValue": [], "extractSettings": {"expression": "$.data.netEarnings", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 15: Update lineup payment amount ---
# --- step 16: Verify P-21 earning summary is not changed ---
# post[assertion]: {"name": "earning is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 17: Verify Partner getPayoutSummary is not changed ---
# post[assertion]: {"name": "Balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 18: Verify promoter earning summary is +10 ---
# pre: var lifetimeEarning_p = pm.environment.get("lifetimeEarning_p");
# pre: console.log(lifetimeEarning_p);
# pre: var lifetimeEarning_p_lineup = eval(lifetimeEarning_p) + 1;
# pre: console.log(lifetimeEarning_p_lineup)
# pre: pm.environment.set("lifetimeEarning_p_lineup",lifetimeEarning_p_lineup)
# pre: 
# post[assertion]: {"name": "Verify the lineup earnings +1", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_p_lineup}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 19: Verify promoter getPayoutSummary is not changed ---
# post[assertion]: {"name": "Verify the lineup balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_p}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 20: Login - promoter ---
# post[customScript]: pm.test("Check merchant login", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("promoter_access_token",res['data']['token']);
# post: });
# --- step 21: Lineup2 earning summary ---
# post[extractor]: {"variableName": "lifetimeEarning_promoter", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.lifetimeEarning", "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 22: Lineup2 getPayoutSummary ---
# post[extractor]: {"variableName": "balance_amount_promoter", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.balance.amount", "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 23: Update lineup email ---
# --- step 24: Verify P-21 earning summary is not changed ---
# post[assertion]: {"name": "earning is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 25: Verify Partner getPayoutSummary is not changed ---
# post[assertion]: {"name": "Balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 26: Verify lineup1 earning summary is not changed ---
# post[assertion]: {"name": "Verify the old lineup earnings is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_p}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 27: Verify lineup1 balance is not changed ---
# post[assertion]: {"name": "Verify the old lineup balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_p}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 28: Verify lineup2 earning summary is +1 ---
# pre: var lifetimeEarning_promoter = pm.environment.get("lifetimeEarning_promoter");
# pre: var lifetimeEarning_lineup2 = eval(lifetimeEarning_promoter) + 1;
# pre: console.log(lifetimeEarning_lineup2)
# pre: pm.environment.set("lifetimeEarning_lineup2",lifetimeEarning_lineup2)
# post[assertion]: {"name": "Verify the new lineup earnings is +1", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_lineup2}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 29: Verify lineup2 balance is not changed ---
# post[assertion]: {"name": "Verify the new lineup balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_promoter}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 30: DELETE /product-event/{eventId}/lineup/{lineupId} ---
# --- step 31: Verify P-21 earning summary is not changed ---
# post[assertion]: {"name": "earning is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 32: Verify Partner getPayoutSummary is not changed ---
# post[assertion]: {"name": "Balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 33: Verify promoter earning summary is +10 ---
# post[assertion]: {"name": "Verify the old lineup earnings is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{lifetimeEarning_p}}", "path": "$.data.lifetimeEarning", "multipleValue": [], "extractSettings": {"expression": "$.data.lifetimeEarning", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 34: Verify promoter getPayoutSummary is not changed ---
# post[assertion]: {"name": "Verify the lineup balance is not changed", "subject": "responseJson", "comparison": "equal", "value": "{{balance_amount_p}}", "path": "$.data.balance.amount", "multipleValue": [], "extractSettings": {"expression": "$.data.balance.amount", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 35: Delete event ---




from core.assertions import expect

def test_lury_t5109_t5108_verify_partner_add_edit_delete_payment_to_lineup(ctx):
    """Apifox case #8041780: Lury_T5109_T5108_Verify_partner_add_edit_delete_payment_to_lineup"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: P-21-login
    _resp1 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{M1}}"\n}', app_headers=True)
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
    # extractor: lineup_id = $.data.lineup[0].id
    ctx.extract('lineup_id', _resp9, '$.data.lineup[0].id')
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
    # step 14: Verify the lineup payment before event completed
    _resp14 = ctx.api.events.metrics_summary()
    # assertion 14.Verify the lineup payment is 0: responseJson equal 0
    expect(_resp14).json('$.data.totalLineupFee').equals('0')
    # assertion 14.Verify the total net earnings is 0: responseJson equal 0
    expect(_resp14).json('$.data.netEarnings').equals('0')
    # step 15: Update lineup payment amount
    _resp15 = ctx.api.events.lineup_by_lineup_id(body='{\n  "eventId": "{{event_id}}",\n  "id": "{{lineup_id}}",\n  "title": "P-22",\n  "introduction": "DJ - automation",\n  "poster": {\n    "src": "https://res.cloudinary.com/dr9io1zjv/v1773824130/uploaded_images/jiwuqqbej1dgynpdz84m.webp",\n    "width": 799,\n    "height": 799,\n    "position": 0,\n    "mediaType": "IMAGE",\n    "mediaDuration": 0\n  },\n  "isHeadliner": true,\n  "order": 0,\n  "customRecipientIdentifier": "dian.yuhong.ext+34@1m.app",\n  "recipientVanityUrl": "https://release.pear.us/auto-merchant",\n  "fee": 1,\n  "isPaymentAfterEventEnabled": true,\n  "userId": "85990297-fba4-40ea-a49c-50a310ed6c89",\n  "posterBackend": [\n    {\n      "src": "https://res.cloudinary.com/dr9io1zjv/v1773824130/uploaded_images/jiwuqqbej1dgynpdz84m.webp",\n      "width": 799,\n      "height": 799,\n      "position": 0,\n      "mediaType": "IMAGE",\n      "mediaDuration": 0\n    }\n  ]\n}')
    # step 16: Verify P-21 earning summary is not changed
    _resp16 = ctx.api.earnings.summary()
    # assertion 16.earning is not changed: responseJson equal {{lifetimeEarning}}
    expect(_resp16).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning}}'))
    # step 17: Verify Partner getPayoutSummary is not changed
    _resp17 = ctx.api.earnings.summary_2()
    # assertion 17.Balance is not changed: responseJson equal {{balance_amount}}
    expect(_resp17).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount}}'))
    # step 18: Verify promoter earning summary is +10
    _resp18 = ctx.api.earnings.summary(token='merchant_access_token')
    # assertion 18.Verify the lineup earnings +1: responseJson equal {{lifetimeEarning_p_lineup}}
    expect(_resp18).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning_p_lineup}}'))
    # step 19: Verify promoter getPayoutSummary is not changed
    _resp19 = ctx.api.earnings.summary_2(token='merchant_access_token')
    # assertion 19.Verify the lineup balance is not changed: responseJson equal {{balance_amount_p}}
    expect(_resp19).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_p}}'))
    # step 20: Login - promoter
    _resp20 = ctx.api.auth.sign_in(body='{\n    "password": "{{merchant_password}}",\n    "email": "{{promoter_email}}"\n}', app_headers=True)
    ctx.extract('promoter_access_token', _resp20, '$.data.token')
    # step 21: Lineup2 earning summary
    _resp21 = ctx.api.earnings.summary(token='promoter_access_token')
    # extractor: lifetimeEarning_promoter = $.data.lifetimeEarning
    ctx.extract('lifetimeEarning_promoter', _resp21, '$.data.lifetimeEarning')
    # step 22: Lineup2 getPayoutSummary
    _resp22 = ctx.api.earnings.summary_2(token='promoter_access_token')
    # extractor: balance_amount_promoter = $.data.balance.amount
    ctx.extract('balance_amount_promoter', _resp22, '$.data.balance.amount')
    # step 23: Update lineup email
    _resp23 = ctx.api.events.lineup_by_lineup_id(body='{\n  "eventId": "{{event_id}}",\n  "id": "{{lineup_id}}",\n  "title": "P-35",\n  "introduction": "DJ - automation",\n  "poster": {\n    "src": "https://res.cloudinary.com/dr9io1zjv/v1773824130/uploaded_images/jiwuqqbej1dgynpdz84m.webp",\n    "width": 799,\n    "height": 799,\n    "position": 0,\n    "mediaType": "IMAGE",\n    "mediaDuration": 0\n  },\n  "isHeadliner": true,\n  "order": 0,\n  "customRecipientIdentifier": "dian.yuhong.ext+35@1m.app",\n  "recipientVanityUrl": "https://release.pear.us/auto-promoter",\n  "fee": 1,\n  "isPaymentAfterEventEnabled": true,\n  "userId": "85990297-fba4-40ea-a49c-50a310ed6c89",\n  "posterBackend": [\n    {\n      "src": "https://res.cloudinary.com/dr9io1zjv/v1773824130/uploaded_images/jiwuqqbej1dgynpdz84m.webp",\n      "width": 799,\n      "height": 799,\n      "position": 0,\n      "mediaType": "IMAGE",\n      "mediaDuration": 0\n    }\n  ]\n}')
    # step 24: Verify P-21 earning summary is not changed
    _resp24 = ctx.api.earnings.summary()
    # assertion 24.earning is not changed: responseJson equal {{lifetimeEarning}}
    expect(_resp24).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning}}'))
    # step 25: Verify Partner getPayoutSummary is not changed
    _resp25 = ctx.api.earnings.summary_2()
    # assertion 25.Balance is not changed: responseJson equal {{balance_amount}}
    expect(_resp25).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount}}'))
    # step 26: Verify lineup1 earning summary is not changed
    _resp26 = ctx.api.earnings.summary(token='merchant_access_token')
    # assertion 26.Verify the old lineup earnings is not changed: responseJson equal {{lifetimeEarning_p}}
    expect(_resp26).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning_p}}'))
    # step 27: Verify lineup1 balance is not changed
    _resp27 = ctx.api.earnings.summary_2(token='merchant_access_token')
    # assertion 27.Verify the old lineup balance is not changed: responseJson equal {{balance_amount_p}}
    expect(_resp27).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_p}}'))
    # step 28: Verify lineup2 earning summary is +1
    _resp28 = ctx.api.earnings.summary(token='promoter_access_token')
    # assertion 28.Verify the new lineup earnings is +1: responseJson equal {{lifetimeEarning_lineup2}}
    expect(_resp28).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning_lineup2}}'))
    # step 29: Verify lineup2 balance is not changed
    _resp29 = ctx.api.earnings.summary_2(token='promoter_access_token')
    # assertion 29.Verify the new lineup balance is not changed: responseJson equal {{balance_amount_promoter}}
    expect(_resp29).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_promoter}}'))
    # step 30: DELETE /product-event/{eventId}/lineup/{lineupId}
    _resp30 = ctx.api.events.lineup_l_lineup_id()
    # step 31: Verify P-21 earning summary is not changed
    _resp31 = ctx.api.earnings.summary()
    # assertion 31.earning is not changed: responseJson equal {{lifetimeEarning}}
    expect(_resp31).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning}}'))
    # step 32: Verify Partner getPayoutSummary is not changed
    _resp32 = ctx.api.earnings.summary_2()
    # assertion 32.Balance is not changed: responseJson equal {{balance_amount}}
    expect(_resp32).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount}}'))
    # step 33: Verify promoter earning summary is +10
    _resp33 = ctx.api.earnings.summary(token='merchant_access_token')
    # assertion 33.Verify the old lineup earnings is not changed: responseJson equal {{lifetimeEarning_p}}
    expect(_resp33).json('$.data.lifetimeEarning').equals(ctx.render_text('{{lifetimeEarning_p}}'))
    # step 34: Verify promoter getPayoutSummary is not changed
    _resp34 = ctx.api.earnings.summary_2(token='merchant_access_token')
    # assertion 34.Verify the lineup balance is not changed: responseJson equal {{balance_amount_p}}
    expect(_resp34).json('$.data.balance.amount').equals(ctx.render_text('{{balance_amount_p}}'))
    # step 35: Delete event
    _resp35 = ctx.api.events.by_event_id(path_vars={'event_id': '{{id}}'})
