"""Migrated from Apifox case #8698068. Source folder: Post validation/(Linda)KAT-11814 Verify Require approval to purchase."""
# Apifox Case ID: 8698068  (traceability only — not needed to run)
NAME = "test"
TAGS = ["p2", "post_validation_linda_kat_11814_verify_require_approval_to_purchase"]
PRIORITY = 2


CASE_ID = 8698068
ENV_NAME = "Release"

# --- step 1: 22b39deb-e976-49a4-a94b-246d0015eae9 ---
# post[customScript]: if (pm.response.to.have.status(201)){
# post:     var res = JSON.parse(responseBody);
# post:     pm.environment.set("access_token",res['data']);
# post: }
# post: 
# --- step 2: c2c7d898-eb0e-4f49-9f2f-e364b14259b3 ---
# --- step 3: 9a94d50a-3c6e-4b36-9795-d0c9a4094c7b ---
# pre: // 1. 随机生成名字 (firstName & lastName)
# pre: const firstNames = ["linda", "james", "alex", "emma", "michael", "sophia", "david", "olivia"];
# pre: const lastNames = ["zhou", "smith", "johnson", "wang", "brown", "lee", "chen", "taylor"];
# pre: 
# pre: const randomFirstName = firstNames[Math.floor(Math.random() * firstNames.length)];
# pre: const randomLastName = lastNames[Math.floor(Math.random() * lastNames.length)];
# pre: 
# pre: // 2. 固定 linda.zhou 格式，只生成 1 ~ 999 之间的随机数字
# pre: const randomNumber = Math.floor(Math.random() * 999) + 1;
# pre: const randomEmail = `linda.zhou.ext+${randomNumber}@1m.app`;
# pre: 
# pre: // 3. 设置变量
# pre: pm.variables.set("randomFirstName", randomFirstName);
# pre: pm.variables.set("randomLastName", randomLastName);
# pre: pm.variables.set("randomEmail", randomEmail);




import random
import uuid
import string
from core.assertions import expect

def test_test(ctx):
    """Apifox case #8698068: test"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    vars['__uuid_1'] = str(__import__('uuid').uuid4())
    # 生成 Apifox 动态变量 {{__uuid_0}}（原 Apifox 内置，迁移后需显式生成）
    vars['$string.uuid'] = str(uuid.uuid4())
    # === Steps ===
    # step 1: 22b39deb-e976-49a4-a94b-246d0015eae9
    _resp1 = ctx.api.auth.guest_login(body='{\r\n    "consumerId": "{{__uuid_1}}"\r\n}')
    # extractor: access_token = $.data
    ctx.extract('access_token', _resp1, '$.data')
    # step 2: c2c7d898-eb0e-4f49-9f2f-e364b14259b3
    _resp2 = ctx.api.cart.update(body='{\n    "fbAdParams": {\n        "eventID": "0bc21151-180e-47cc-877b-4e65e98f3818",\n        "pixelId": [\n            "268933192948110"\n        ],\n        "fbBrowserId": "fb.1.1788334482977.794598099244596576",\n        "externalId": "ce119dc8-4bd9-4759-89b5-c000d8b27e9a",\n        "eventSourceUrl": "https://release.pear.us/resident/post/mexico-vs-ecuador-0630-1"\n    },\n    "items": [\n        {\n            "quantity": 1,\n            "promoterProductVariantId": "b6def878-7d7a-4336-b3a2-74be1f44b788",\n            "price": 25.2,\n            "postId": "250c6120-735e-4c13-8afb-736d56e9cb25",\n            "customFields": []\n        }\n    ],\n    "lite": true,\n    "subdomainVanityUrl": ""\n}', app_headers=True, token='access_token')
    _firstNames = ["linda","james","alex","emma","michael","sophia","david","olivia"]
    vars['randomFirstName'] = random.choice(_firstNames)
    _lastNames = ["zhou","smith","johnson","wang","brown","lee","chen","taylor"]
    vars['randomLastName'] = random.choice(_lastNames)
    vars['randomNumber'] = str(random.randint(1, 999))
    vars['randomEmail'] = f"linda.zhou.ext+{vars['randomNumber']}@1m.app"
    # step 3: 9a94d50a-3c6e-4b36-9795-d0c9a4094c7b
    _resp3 = ctx.api.approvals.create(body='{\n    "postId": "250c6120-735e-4c13-8afb-736d56e9cb25",\n    "firstName": "{{randomFirstName}}",\n    "lastName": "{{randomLastName}}",\n    "email": "{{randomEmail}}"\n}\n\n', token='access_token')
    # --- assertions: no fake-green (non-4xx/5xx) ---
    assert _resp1.status_code < 400, f"step1 got HTTP {_resp1.status_code}: {_resp1.text[:200]}"
    assert _resp2.status_code < 400, f"step2 got HTTP {_resp2.status_code}: {_resp2.text[:200]}"
    assert _resp3.status_code < 400, f"step3 got HTTP {_resp3.status_code}: {_resp3.text[:200]}"
