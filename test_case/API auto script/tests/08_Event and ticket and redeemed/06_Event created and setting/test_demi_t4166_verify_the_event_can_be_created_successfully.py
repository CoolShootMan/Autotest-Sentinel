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
    _resp1 = ctx.api.events.v2(body='{\n    "ignoreStartTime": true,\n    "ignoreEndTime": true,\n    "isTimeUnspecified": false,\n    "allowAutoComplete": true,\n    "description": "",\n    "note": "21+ refunds by linda",\n    "location": "Canada Line - SkyTrain, Metro Vancouver, BC, Canada",\n    "status": "UPCOMING",\n    "descriptionBodyJson": "{\\"root\\":{\\"children\\":[{\\"children\\":[],\\"direction\\":\\"ltr\\",\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"katana-paragraph\\",\\"version\\":1,\\"textFormat\\":0,\\"textStyle\\":\\"\\",\\"style\\":\\"\\"}],\\"direction\\":null,\\"format\\":\\"\\",\\"indent\\":0,\\"type\\":\\"root\\",\\"version\\":1}}",\n    "isTaxEnabled": true,\n    "isAddressRevealEnabled": false,\n    "title": "API auto test T4166",\n    "venue": "Instagram Live, Zoom, In-person",\n    "timezone": {\n        "timeZoneId": "America/Vancouver",\n        "timeZoneName": "Pacific Daylight Time",\n        "dstOffset": 3600,\n        "rawOffset": -28800\n    },\n    "poster": {\n        "height": 2048,\n        "width": 3072,\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\n        "mediaType": "IMAGE"\n    },\n    "startDateDisplay": "2056-04-01",\n    "locationDetails": {\n        "line1": "Canada Line - SkyTrain",\n        "city": "",\n        "state": "British Columbia",\n        "stateName": "British Columbia",\n        "zipcode": "",\n        "country": "Canada",\n        "placeId": "EjNDYW5hZGEgTGluZSAtIFNreVRyYWluLCBNZXRybyBWYW5jb3V2ZXIsIEJDLCBDYW5hZGEiLiosChQKEgl7kAKs3XSGVBHQ0p4DNxpJ8RIUChIJpd_5BZDOYlQRpvz0npdsnM4"\n    },\n    "taxConfig": {\n        "customTaxRate": 10,\n        "calculationType": "CUSTOM"\n    }\n}', token='xuan22_token')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # extract created event id (orig: pm.environment.set("created_event_id", resJson.data.id))
    ctx.extract('created_event_id', _resp1, '$.data.id')
    # step 2: 9d87a6e4-0a90-42ed-a88b-7831049d3fdb
    _resp2 = ctx.api.events.v2_ticket_batch_v2(body='{\r\n    "poster": {\r\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n        "width": 3072,\r\n        "height": 2048,\r\n        "position": 0,\r\n        "mediaType": "IMAGE",\r\n        "mediaDuration": 0\r\n    },\r\n    "listingType": "TICKET",\r\n    "isTaxEnabled": true,\r\n    "taxConfig": {\r\n        "customTaxRate": 10,\r\n        "calculationType": "CUSTOM",\r\n        "configUpdatedAt": "2026-03-25T07:16:01.387Z"\r\n    },\r\n    "autoReplace": false,\r\n    "tickets": [\r\n        {\r\n            "listingType": "TICKET",\r\n            "images": [\r\n                {\r\n                    "id": "80f43627-4bef-49b0-934b-cd63d49f8787",\r\n                    "height": 1000,\r\n                    "width": 1000,\r\n                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",\r\n                    "mediaType": "IMAGE"\r\n                }\r\n            ],\r\n            "title": "General Admission",\r\n            "bodyJson": "",\r\n            "options": [\r\n                {\r\n                    "name": "Title",\r\n                    "values": [\r\n                        "Default Title"\r\n                    ],\r\n                    "images": []\r\n                }\r\n            ],\r\n            "variants": [\r\n                {\r\n                    "inventoryQuantity": 10,\r\n                    "ticketPrice": 0,\r\n                    "price": 0,\r\n                    "fees": 0,\r\n                    "priceAnchor": 0,\r\n                    "option": {\r\n                        "option1": "Default Title"\r\n                    }\r\n                }\r\n            ]\r\n        }\r\n    ],\r\n    "coSellingCommissionRate": 24\r\n}', token='xuan22_token', path_vars={'event_id': '{{created_event_id}}'})
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
