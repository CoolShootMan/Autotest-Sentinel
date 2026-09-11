"""Migrated from Apifox case #7511246. Source folder: Event and ticket and redeemed/Event created and setting."""
# Apifox Case ID: 7511246  (traceability only — not needed to run)
NAME = "Verify add a new tab Lineup when create an event"
TAGS = ["p1", "event_and_ticket_and_redeemed_event_created_and_setting", "suite:linda"]
PRIORITY = 1


CASE_ID = 7511246
ENV_NAME = "Release"

def _gen_lineup_random():
    # pre script (original pm.environment.set) was dropped during migration.
    # Rebuild the 3-digit random suffix here so the title is non-empty.
    return f"API Test T4440 lineup by linda {random.randint(100, 999)}"

# --- step 1: 0b81a3c3-02fc-48b3-822d-d9eaf49b2a3a ---
# --- step 2: a288f139-84e6-463e-a20d-7aa171f9b7cb ---
# pre: // 假设这是之前定义的生成三位随机数的函数
# pre: function generateThreeDigitRandomNumber() {
# pre:     return Math.floor(Math.random() * 900) + 100;
# pre: }
# pre: 
# pre: const lineup_random = `API Test T4440 lineup by linda ${generateThreeDigitRandomNumber()}`;
# pre: console.log(lineup_random);
# pre: 
# pre: 
# pre: 
# pre: pm.environment.set("lineup_random", lineup_random);
# post[assertion]: {"name": "meassage", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "linda zhou automation test introduction", "path": "$.data.introduction", "multipleValue": [], "extractSettings": {"expression": "$.data.introduction", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import random
from core.assertions import expect

def test_linda_t4440_verify_add_a_new_tab_lineup_when_create_an_event(ctx):
    """Apifox case #7511246: Linda_T4440_Verify_add_a_new_tab_Lineup_when_create_an_event"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # Restore pre-script generated var that was dropped during migration.
    vars['lineup_random'] = _gen_lineup_random()
    # The migrated URL still holds the literal {event_id} placeholder; bind it to
    # the same eventId used in the request body so the path resolves.
    vars['event_id'] = '79ec6803-9f10-4937-9fde-823468e0e543'
    # === Steps ===
    # step 1: 0b81a3c3-02fc-48b3-822d-d9eaf49b2a3a
    _resp1 = ctx.api.promoters.product_image_url(body='{"contentType":"image/jpeg"}', token='linda01_token')
    # step 2: a288f139-84e6-463e-a20d-7aa171f9b7cb
    _resp2 = ctx.api.events.lineup(body='{\r\n    "eventId": "79ec6803-9f10-4937-9fde-823468e0e543",\r\n    "poster": {\r\n        "width": 160,\r\n        "height": 160,\r\n        "file": {},\r\n        "base64": "blob:https://release.pear.us/5ec24efe-5468-45a0-8003-2f1f22f1cf79",\r\n        "source": "UPLOAD",\r\n        "src": "https://res.cloudinary.com/dr9io1zjv/v1762926629/uploaded_images/bnd8lqb9habur8lbsvux.jpg",\r\n        "mediaType": "IMAGE"\r\n    },\r\n    "posterBackend": [\r\n        {\r\n            "width": 160,\r\n            "height": 160,\r\n            "file": {},\r\n            "base64": "blob:https://release.pear.us/5ec24efe-5468-45a0-8003-2f1f22f1cf79",\r\n            "source": "UPLOAD",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762926629/uploaded_images/bnd8lqb9habur8lbsvux.jpg",\r\n            "mediaType": "IMAGE"\r\n        }\r\n    ],\r\n    "title": "{{lineup_random}}",\r\n    "introduction": "linda zhou automation test introduction"\r\n}', token='linda01_token')
    # assertion 2.meassage: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # assertion 2.assertion: responseJson equal linda zhou automation test introduction
    expect(_resp2).json('$.data.introduction').equals('linda zhou automation test introduction')
