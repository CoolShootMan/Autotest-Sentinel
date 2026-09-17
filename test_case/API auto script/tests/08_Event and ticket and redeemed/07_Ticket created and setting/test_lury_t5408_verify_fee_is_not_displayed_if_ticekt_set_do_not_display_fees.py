"""Migrated from Apifox case #8662408. Source folder: Event and ticket and redeemed/Ticket created and setting."""
# Apifox Case ID: 8662408  (traceability only — not needed to run)
NAME = "Verify fee is not displayed if ticekt set \"Do not display fees\""
TAGS = ["p0", "event_and_ticket_and_redeemed_ticket_created_and_setting", "suite:lury"]
PRIORITY = 0


CASE_ID = 8662408
ENV_NAME = "Release"

# --- step 1: delete cart ---
# --- step 2: buy now ticket with custom fee ---
# post[customScript]: pm.test("Check buy now", function () {
# post:     var res = JSON.parse(responseBody);
# post:     var orderNumber = res['data']['orderNumber']
# post:     var orderId = res['data']['orderId']
# post:     pm.environment.set("orderNumber",orderNumber);
# post:     pm.environment.set("orderId",orderId);
# post:     var lineItems = res['data']['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["promoterVariantId"]).to.eql("d5e8d02e-6038-4603-90a0-769012f620d5");
# post:         pm.expect(line_item["hideFees"]).to.eql(true);
# post:         pm.expect(line_item["ticketFees"]).to.eql(0);
# post:         pm.expect(line_item["subtotalTicketFees"]).to.eql(0);
# post:     }
# post: });
# --- step 3: create Order ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(201);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalTopay']).to.eql(14.28);
# post:     var lineItems = res['data']["confirmation"]['lineItems'];
# post:     for (var line_item of lineItems){
# post:         pm.expect(line_item["merchantProductId"]).to.eql("b0ce090f-1d6f-4962-bdce-3f2f1cbfa1d5");
# post:         pm.expect(line_item["hideFees"]).to.eql(true);
# post:         pm.expect(line_item["ticketFees"]).to.eql(0);
# post:     }
# post: });
# --- step 4: get consumer order detail ---
# post[customScript]: pm.test("Check total contains taxes for consumer order", function () {
# post:     pm.response.to.have.status(200);
# post:     var res = JSON.parse(responseBody);
# post:     pm.expect(res['data']['totalLineItemPrice']).to.eql(14.28);
# post:     var line_item_list = res['data']['lineItems'];
# post:     for (var line_item of line_item_list){
# post:         pm.expect(line_item["merchantProductId"]).to.eql("b0ce090f-1d6f-4962-bdce-3f2f1cbfa1d5");
# post:         pm.expect(line_item["hideFees"]).to.eql(true);
# post:         pm.expect(line_item["ticketFees"]).to.eql(0);
# post:     }
# post: });




from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_t5408_verify_fee_is_not_displayed_if_ticekt_set_do_not_display_fees(ctx: "Context"):
    """Apifox case #8662408: Lury_T5408_Verify_fee_is_not_displayed_if_ticekt_set_Do_not_display_fees"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: delete cart
    _resp1 = ctx.api.cart.delete()
    # step 2: buy now ticket with custom fee
    _resp2 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "885eaa07-e64b-4eff-90aa-d5b1582034e9",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "d5e8d02e-6038-4603-90a0-769012f620d5",
                "price": 14.28,
                "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "5c622faf-26eb-4833-905b-ece92ed1f45e",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/mcc/post/lury-automation-test-check-in-expiration",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "d5e8d02e-6038-4603-90a0-769012f620d5",
                "postId": "885eaa07-e64b-4eff-90aa-d5b1582034e9",
                "price": 14.28,
                "customFields": [],
            },
        ],
    })
    # extractor: orderNumber = orderNumber
    ctx.extract('orderNumber', _resp2, 'orderNumber')
    # extractor: orderId = orderId
    ctx.extract('orderId', _resp2, 'orderId')
    # step 3: create Order
    _resp3 = ctx.api.orders.create(body={
        "id": "{{orderId}}",
        "contact": {
            "email": "dian.yuhong.ext+19@1m.app",
            "phoneNumber": "+17404630034",
        },
        "shippingAddressId": "41ef3748-0466-4e91-95c2-a7983d14e151",
        "paymentInfo": {
            "paymentMethodId": "{{pay_method_id}}",
        },
        "fbAdParams": {
            "eventID": "af93500c-e7f0-43b3-b88a-5cc461f20494",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/checkout?postId=446662ad-cac4-4837-9b1f-3358eddf169a",
        },
    })
    # step 4: get consumer order detail
    _resp4 = ctx.api.orders.consumer_detail_by_order_number()
