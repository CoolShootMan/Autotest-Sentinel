# author: Lury
# time: 2026/10/21 10:30

NAME = "Verify the location id for event address is not missing"
TAGS = ["p0", "event_address_location_id", "suite:linda"]
PRIORITY = 0

ENV_NAME = "Release"

# --- step 1: Create event ---
from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_lury_t6036_verify_the_event_address_location_id(ctx: "Context"):
    """Verify the location id is not missing for event address"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Create event
    _resp1 = ctx.api.events.v2(body={
        "ignoreStartTime": True,
        "ignoreEndTime": True,
        "isTimeUnspecified": False,
        "allowAutoComplete": True,
        "description": "",
        "note": "Lury test event address location id is not missing",
        "location": "261 Driggs Ave, Brooklyn, NY 11222, United States",
        "status": "UPCOMING",
        "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
        "isTaxEnabled": True,
        "isAddressRevealEnabled": False,
        "title": "Lury api auto testing T6036",
        "venue": "This is venue",
        "timezone": {
            "timeZoneId": "America/New_York",
            "timeZoneName": "Eastern Daylight Time",
            "dstOffset": 3600,
            "rawOffset": -18000,
        },
        "poster": {
            "height": 2048,
            "width": 3072,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "mediaType": "IMAGE",
        },
        "startDateDisplay": "2056-04-01",
        "placeId": "ChIJUUKzekVZwokRx9H7oppFep8",
        "taxConfig": {
            "customTaxRate": 1,
            "calculationType": "CUSTOM",
        },
    }, token='M1_access_token')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # extract created event id (orig: pm.environment.set("created_event_id", resJson.data.id))
    ctx.extract('created_event_id_lury', _resp1, '$.data.id')
    # step 2: POST Create event next step
    _resp2 = ctx.api.events.v2_ticket_batch_v2(body={
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
        'customTaxRate': 1,
        'calculationType': 'CUSTOM',
        'configUpdatedAt': '2026-03-25T07:16:01.387Z',
    },
    'autoReplace': False,
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
            'title': 'General Admission',
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
                    'inventoryQuantity': 10,
                    'ticketPrice': 0,
                    'price': 0,
                    'fees': 0,
                    'priceAnchor': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                },
            ],
        },
    ],
    'coSellingCommissionRate': 24,
}, token='M1_access_token', path_vars={'event_id': '{{created_event_id_lury}}'})
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3: Check event details
    _resp3 = ctx.api.events.v2_config(token='M1_access_token', params={'pageSize': '30', 'pageNumber': '1'})
    _resp4 = ctx.api.events.create_staff_id_for_single_event(token='M1_access_token', params={"role":"OPERATOR","staffId":"111","eventIds":["{{created_event_id_lury}}"]})
    expect(_resp4).json('$.code').equals('200')
    _resp5 = ctx.api.events.v2_config(token='M1_access_token', path_vars={'event_id': '{{created_event_id_lury}}'})
    expect(_resp5).json('$.code').equals('200')
    expect(_resp5).json('$.data.locationDetails.stripeLocationId').is_not_empty
    # step 6: DELETE delete the event and recover the data
    _resp6 = ctx.api.events.by_event_id(body=None, token='M1_access_token', path_vars={'event_id': '{{created_event_id_lury}}'})
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
