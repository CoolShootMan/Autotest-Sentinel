"""Migrated from Apifox case #8677224. Source folder: Event and ticket and redeemed/Fee breakdown."""
# Apifox Case ID: 8677224  (traceability only — not needed to run)
NAME = "Verify no fee for ticket from event if set \"Show fee breakdown at checkout\" in event"
TAGS = ["p0", "event_and_ticket_and_redeemed_fee_breakdown", "suite:lury"]
PRIORITY = 0


CASE_ID = 8677224
ENV_NAME = "Release"

# --- step 1: guest get token ---
# pre: 
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 2: delete cart ---
# --- step 3: update Cart ---
# --- step 4: get Cart ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var lineItems = res['data']['items'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["merchantId"]).to.eql("02e0c1e6-89b1-4b36-9e57-daa112331d80");
# post:         pm.expect(line_item["showFeesBreakdown"]).to.eql(true);
# post:         pm.expect(line_item["faceValue"]).to.eql(5);
# post:         pm.expect(line_item["ticketFees"]).to.eql(3.04);
# post:         pm.expect(line_item["subtotal"]).to.eql(8.04);
# post:     }
# post: });
# --- step 5: create Checkout ---
# post[customScript]: pm.test("Check checkout drawer", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderId",orderId);
# post:     var feesBreakdown = res['data']['feesBreakdown'];
# post:     console.log(feesBreakdown)
# post:     var lineItems = res['data']['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["promoterVariantId"]).to.eql("699c557f-bc3e-4e45-8d8d-85ec913f963f");
# post:         pm.expect(line_item["showFeesBreakdown"]).to.eql(true);
# post:         pm.expect(line_item["faceValue"]).to.eql(5);
# post:         pm.expect(line_item["ticketFees"]).to.eql(3.04);
# post:         pm.expect(line_item["subtotalTicketFees"]).to.eql(3.04);
# post:         pm.expect(line_item["lineItemPrice"]).to.eql(8.04);
# post:         pm.expect(line_item["lineItemSubtotal"]).to.eql(8.04);
# post:     }
# post:     for (var fees of feesBreakdown){
# post:         if (fees["title"] === "Transaction fees"){
# post:             pm.expect(fees["amount"]).to.eql(1.8);
# post:         }
# post:         else if (fees["title"] === "Taxes"){
# post:             pm.expect(fees["amount"]).to.eql(0.16);
# post:         }
# post:         else if (fees["title"] === "fee1"){
# post:             pm.expect(fees["amount"]).to.eql(0.08);
# post:         }
# post:         else if (fees["title"] === "fee2"){
# post:             pm.expect(fees["amount"]).to.eql(1);
# post:         }
# post:     }
# post: });
# --- step 6: update Cart ---
# --- step 7: delete cart ---
# --- step 8: update Cart ---
# --- step 9: update Cart ---
# --- step 10: create Checkout ---
# post[customScript]: pm.test("Check checkout drawer", function () {
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']["showFeesBreakdown"]).to.eql(true);
# post:     var feesBreakdown = res['data']['feesBreakdown'];
# post:     for (var fees of feesBreakdown){
# post:         if (fees["title"] === "Transaction fees"){
# post:             pm.expect(fees["amount"]).to.eql(3.49);
# post:         }
# post:         else if (fees["title"] === "Taxes"){
# post:             pm.expect(fees["amount"]).to.eql(0.3);
# post:         }
# post:         else if (fees["title"] === "fee1"){
# post:             pm.expect(fees["amount"]).to.eql(0.22);
# post:         }
# post:         else if (fees["title"] === "fee2"){
# post:             pm.expect(fees["amount"]).to.eql(1);
# post:         }
# post:     }
# post: });
# --- step 11: delete cart ---
# --- step 12: express - resell post ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderId",orderId);
# post:     var lineItems = res['data']['lineItems'];
# post:     var feesBreakdown = res['data']['feesBreakdown'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["promoterProductId"]).to.eql("5fea319b-a3bf-4c4e-80c0-388cc8f83c97");
# post:         pm.expect(line_item["showFeesBreakdown"]).to.eql(true);
# post:         pm.expect(line_item["faceValue"]).to.eql(5);
# post:         pm.expect(line_item["ticketFees"]).to.eql(3.04);
# post:         pm.expect(line_item["subtotalTicketFees"]).to.eql(3.04);
# post:         pm.expect(line_item["lineItemPrice"]).to.eql(8.04);
# post:         pm.expect(line_item["lineItemSubtotal"]).to.eql(8.04);
# post:     }
# post:     for (var fees of feesBreakdown){
# post:         if (fees["title"] === "Transaction fees"){
# post:             pm.expect(fees["amount"]).to.eql(1.8);
# post:         }
# post:         else if (fees["title"] === "Taxes"){
# post:             pm.expect(fees["amount"]).to.eql(0.16);
# post:         }
# post:         else if (fees["title"] === "fee1"){
# post:             pm.expect(fees["amount"]).to.eql(0.08);
# post:         }
# post:         else if (fees["title"] === "fee2"){
# post:             pm.expect(fees["amount"]).to.eql(1);
# post:         }
# post:     }
# post: });
# --- step 13: update Cart ---
# --- step 14: get Cart ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var lineItems = res['data']['items'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["merchantId"]).to.eql("02e0c1e6-89b1-4b36-9e57-daa112331d80");
# post:         pm.expect(line_item["showFeesBreakdown"]).to.eql(true);
# post:         pm.expect(line_item["faceValue"]).to.eql(5);
# post:         pm.expect(line_item["ticketFees"]).to.eql(3.04);
# post:         pm.expect(line_item["subtotal"]).to.eql(8.04);
# post:     }
# post: });
# --- step 15: apply promotion ---
# pre: var orderId = pm.environment.get("orderId")
# pre: console.log(orderId)
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var lineItems = res['data']['lineItems'];
# post:     var feesBreakdown = res['data']['feesBreakdown'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["promoterProductId"]).to.eql("5fea319b-a3bf-4c4e-80c0-388cc8f83c97");
# post:         pm.expect(line_item["showFeesBreakdown"]).to.eql(true);
# post:         pm.expect(line_item["faceValue"]).to.eql(5);
# post:         pm.expect(line_item["ticketFees"]).to.eql(3.04);
# post:         pm.expect(line_item["subtotalTicketFees"]).to.eql(2.93);
# post:         pm.expect(line_item["lineItemPrice"]).to.eql(8.04);
# post:         pm.expect(line_item["lineItemSubtotal"]).to.eql(7.24);
# post:         pm.expect(line_item["couponDiscount"]).to.eql(0.8);
# post:         pm.expect(line_item["unitDiscount"]).to.eql(0.8);
# post:     }
# post:     for (var fees of feesBreakdown){
# post:         if (fees["title"] === "Transaction fees"){
# post:             pm.expect(fees["amount"]).to.eql(1.8);
# post:         }
# post:         else if (fees["title"] === "Taxes"){
# post:             pm.expect(fees["amount"]).to.eql(0.16);
# post:         }
# post:         else if (fees["title"] === "fee1"){
# post:             pm.expect(fees["amount"]).to.eql(0.08);
# post:         }
# post:         else if (fees["title"] === "fee2"){
# post:             pm.expect(fees["amount"]).to.eql(1);
# post:         }
# post:     }
# post: });




import json

from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_t5650_verify_no_fee_for_ticket_from_event_if_set_show_fee_breakdown_at_checkout_in_event(ctx: "Context"):
    """Apifox case #8677224: Lury_T5650_Verify_no_fee_for_ticket_from_event_if_set_Show_fee_breakdown_at_chec"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: guest get token
    _resp1 = ctx.api.auth.guest_login(body={
        "consumerId": "bc9a5b70-2b2a-40b7-81e1-4176e8ef4bda",
    }, app_headers=False)
    vars['access_token'] = (_resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 2: delete cart
    _resp2 = ctx.api.cart.delete(token='access_token')
    # step 3: update Cart
    _resp3 = ctx.api.cart.update(body={
        "fbAdParams": {
            "eventID": "806d4aae-8ba1-471f-8a1b-1c22c46844aa",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1768467567031.92506180232323161",
            "externalId": "154873ad-8fbe-4f69-bdf0-e11205c4eab8",
            "eventSourceUrl": "https://release.pear.us/mcc/post/lury-event-automation-fee-breakdown-0828",
        },
        "items": [
            {
                "quantity": 1,
                "promoterProductVariantId": "699c557f-bc3e-4e45-8d8d-85ec913f963f",
                "price": 8.04,
                "postId": "df1f8081-05b6-453e-8161-32b345d79f47",
                "customFields": [],
            },
        ],
        "lite": True,
        "subdomainVanityUrl": "",
    }, token='access_token')
    # step 4: get Cart
    _resp4 = ctx.api.cart.list(token='access_token')
    # step 5: create Checkout
    _resp5 = ctx.api.orders.checkout(body={
        "subdomainVanityUrl": "",
    }, token='access_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp5, '$.data.orderId')
    # step 6: update Cart
    _resp6 = ctx.api.cart.update(body={
        "items": [
            {
                "quantity": 1,
                "promoterProductVariantId": "699c557f-bc3e-4e45-8d8d-85ec913f963f",
                "price": 8.04,
                "postId": "df1f8081-05b6-453e-8161-32b345d79f47",
                "selected": True,
            },
        ],
        "lite": False,
        "subdomainVanityUrl": "",
    }, token='access_token')
    # step 7: delete cart
    _resp7 = ctx.api.cart.delete(token='access_token')
    # step 8: update Cart
    _resp8 = ctx.api.cart.update(body={
        "fbAdParams": {
            "eventID": "806d4aae-8ba1-471f-8a1b-1c22c46844aa",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1768467567031.92506180232323161",
            "externalId": "154873ad-8fbe-4f69-bdf0-e11205c4eab8",
            "eventSourceUrl": "https://release.pear.us/mcc/post/lury-event-automation-fee-breakdown-0828",
        },
        "items": [
            {
                "quantity": 1,
                "promoterProductVariantId": "699c557f-bc3e-4e45-8d8d-85ec913f963f",
                "price": 8.04,
                "postId": "df1f8081-05b6-453e-8161-32b345d79f47",
                "customFields": [],
            },
        ],
        "lite": True,
        "subdomainVanityUrl": "",
    }, token='access_token')
    # step 9: update Cart
    _resp9 = ctx.api.cart.update(body={
        "fbAdParams": {
            "eventID": "00d416bd-5247-44aa-8fcc-bb690c5252d6",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1768467567031.92506180232323161",
            "externalId": "154873ad-8fbe-4f69-bdf0-e11205c4eab8",
            "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-fee-breakdown-another-event",
        },
        "items": [
            {
                "quantity": 1,
                "promoterProductVariantId": "746a3b5e-c80b-4b22-8fac-bf0293f23ce3",
                "price": 6.97,
                "postId": "4737e8d2-24cd-4d96-8e58-8f37cd3a4d99",
                "customFields": [],
            },
        ],
        "lite": True,
        "subdomainVanityUrl": "",
    }, token='access_token')
    # step 10: create Checkout
    _resp10 = ctx.api.orders.checkout(body={
        "subdomainVanityUrl": "",
    }, token='access_token')
    # step 11: delete cart
    _resp11 = ctx.api.cart.delete(token='access_token')
    # step 12: express - resell post
    _resp12 = ctx.api.orders.checkout_express(body={
        "items": [
            {
                "quantity": 1,
                "promoterProductVariantId": "340b95c1-baf7-4395-bc9c-1fe4e89a02f9",
                "price": 8.04,
                "postId": "11bdca5a-bdd4-409c-811b-5e2e2cfcf90f",
                "selected": True,
            },
        ],
        "fbAdParams": {
            "eventID": "5ef2df9c-855f-4feb-934b-4fb28d083d70",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1768467567031.92506180232323161",
            "externalId": "154873ad-8fbe-4f69-bdf0-e11205c4eab8",
            "eventSourceUrl": "https://release.pear.us/auto-merchant/post/lury-event-automation-fee-breakdown-0828",
        },
        "subdomainVanityUrl": "",
    }, token='access_token')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp12, '$.data.orderId')
    # step 13: update Cart
    _resp13 = ctx.api.cart.update(body={
        "items": [
            {
                "quantity": 1,
                "promoterProductVariantId": "340b95c1-baf7-4395-bc9c-1fe4e89a02f9",
                "price": 8.04,
                "postId": "11bdca5a-bdd4-409c-811b-5e2e2cfcf90f",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "4f1f607b-4e3b-4a84-9455-5e14d2687e71",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1788161803289.37298529258249934",
            "externalId": "1b92a4c0-4c7f-42a9-ab6b-af24172d12ee",
            "eventSourceUrl": "https://release.pear.us/auto-merchant/post/lury-event-automation-fee-breakdown-0828",
        },
        "lite": False,
        "subdomainVanityUrl": "",
    }, token='access_token')
    # step 14: get Cart
    _resp14 = ctx.api.cart.list(token='access_token')
    # step 15: apply promotion
    _resp15 = ctx.api.orders.update_promotions(body={
        "postIdForFilter": "11bdca5a-bdd4-409c-811b-5e2e2cfcf90f",
        "orderId": "{{orderId}}",
        "shippingAddress": {
            "line1": "11111 Research Boulevard",
            "state": "TX",
            "city": "Austin",
            "zipcode": "78759",
        },
        "applicableCode": "autofee10",
    }, token='access_token')
