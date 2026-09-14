"""Migrated from Apifox case #7555786. Source folder: Event and ticket and redeemed/Event created and setting."""
# Apifox Case ID: 7555786  (traceability only — not needed to run)
NAME = "Verify the event can be created successfully"
TAGS = ["p0", "event_and_ticket_and_redeemed_event_created_and_setting", "suite:linda"]
PRIORITY = 0


CASE_ID = 7555786
ENV_NAME = "Release"

# --- step 1: Create event ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[customScript]: const resJson = pm.response.json();
# post: 
# post: pm.test("活动创建成功，响应包含合法ID", function () {
# post: // 断言状态码和业务响应正常
# post: pm.response.to.have.status(201);
# post: pm.expect(resJson.code).to.eql(200); // 响应体中code字段为200（按实际业务码调整）
# post: pm.expect(resJson.message).to.eql("success");
# post:   
# post: // 核心断言：确保 data 存在且包含 id 字段
# post: pm.expect(resJson.data).to.exist.and.to.be.an("object", "响应体缺少 data 字段");
# post: pm.expect(resJson.data.id).to.exist.and.to.be.a("string", "data 字段中缺少 id（活动ID）");
# post: });
# post: 
# post: const eventId = resJson.data.id;
# post: pm.environment.set("created_event_id", eventId);
# post: 
# post: console.log("✅ 已成功提取活动ID：", eventId);
# post: console.log("✅ 环境变量 created_event_id 已更新为：", pm.environment.get("created_event_id"));
# --- step 2: 9d87a6e4-0a90-42ed-a88b-7831049d3fdb ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: Check event details ---
# post[customScript]: // 1. Parse the response JSON
# post: const response = pm.response.json();
# post: const data = response.data || {};
# post: 
# post: // --- Assertion for the Title ---
# post: pm.test("Verify the event title is correct", function () {
# post:     // Assert that the title strictly matches "API auto test T4166"
# post:     pm.expect(data.title).to.eql("API auto test T4166");
# post: });
# --- step 4: e4581991-2e26-4034-999f-7f05de16bdfd ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




from core.assertions import expect

def test_demi_t4166_verify_the_event_can_be_created_successfully(ctx):
    """Apifox case #7555786: Demi_T4166_Verify_the_event_can_be_created_successfully"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Create event
    _resp1 = ctx.api.events.v2(body={
        "ignoreStartTime": True,
        "ignoreEndTime": True,
        "isTimeUnspecified": False,
        "allowAutoComplete": True,
        "description": "",
        "note": "21+ refunds by linda",
        "location": "Canada Line - SkyTrain, Metro Vancouver, BC, Canada",
        "status": "UPCOMING",
        "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
        "isTaxEnabled": True,
        "isAddressRevealEnabled": False,
        "title": "API auto test T4166",
        "venue": "Instagram Live, Zoom, In-person",
        "timezone": {
            "timeZoneId": "America/Vancouver",
            "timeZoneName": "Pacific Daylight Time",
            "dstOffset": 3600,
            "rawOffset": -28800,
        },
        "poster": {
            "height": 2048,
            "width": 3072,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "mediaType": "IMAGE",
        },
        "startDateDisplay": "2056-04-01",
        "locationDetails": {
            "line1": "Canada Line - SkyTrain",
            "city": "",
            "state": "British Columbia",
            "stateName": "British Columbia",
            "zipcode": "",
            "country": "Canada",
            "placeId": "EjNDYW5hZGEgTGluZSAtIFNreVRyYWluLCBNZXRybyBWYW5jb3V2ZXIsIEJDLCBDYW5hZGEiLiosChQKEgl7kAKs3XSGVBHQ0p4DNxpJ8RIUChIJpd_5BZDOYlQRpvz0npdsnM4",
        },
        "taxConfig": {
            "customTaxRate": 10,
            "calculationType": "CUSTOM",
        },
    }, token='xuan22_token')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # extract created event id (orig: pm.environment.set("created_event_id", resJson.data.id))
    ctx.extract('created_event_id', _resp1, '$.data.id')
    # step 2: 9d87a6e4-0a90-42ed-a88b-7831049d3fdb
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
        'customTaxRate': 10,
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
}, token='xuan22_token', path_vars={'event_id': '{{created_event_id}}'})
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # step 3: Check event details
    _resp3 = ctx.api.events.v2_config(token='xuan22_token', params={'pageSize': '30', 'pageNumber': '1'})
    # step 4: e4581991-2e26-4034-999f-7f05de16bdfd
    _resp4 = ctx.api.events.by_event_id(body=None, token='xuan22_token', path_vars={'event_id': '{{created_event_id}}'})
    # assertion 4.assertion: responseJson equal 200
    expect(_resp4).json('$.code').equals('200')
    # assertion 4.assertion: responseJson equal success
    expect(_resp4).json('$.message').equals('success')
