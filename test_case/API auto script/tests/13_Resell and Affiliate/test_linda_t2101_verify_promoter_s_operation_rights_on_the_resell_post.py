"""Migrated from Apifox case #7898307. Source folder: Resell and Affiliate."""
# Apifox Case ID: 7898307  (traceability only — not needed to run)
NAME = "Verify Promoter's operation rights on the resell-post"
TAGS = ["p1", "resell_and_affiliate", "suite:linda"]
PRIORITY = 1


CASE_ID = 7898307
ENV_NAME = "Release"

# --- step 1: 4498daf7-3269-4208-817a-6463c7cff775 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "DRAFT", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[extractor]: {"variableName": "resell_post_id", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: 0389ebb4-f10a-4c5f-b075-f7f55c495f25 ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "ACTIVE", "path": "$.data.status", "multipleValue": [], "extractSettings": {"expression": "$.data.status", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 4da12903-d431-4211-895b-4d2c3f383bff ---
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "200", "path": "$.code", "multipleValue": [], "extractSettings": {"expression": "$.code", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "success", "path": "$.message", "multipleValue": [], "extractSettings": {"expression": "$.message", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# post[assertion]: {"name": "", "subject": "responseJson", "comparison": "equal", "value": "{{resell_post_id}}", "path": "$.data.id", "multipleValue": [], "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}




import json
import uuid as _uuid

from core.assertions import expect

from core.compat import get_path as _get_path

def test_linda_t2101_verify_promoter_s_operation_rights_on_the_resell_post(ctx):
    """Apifox case #7898307: Linda_T2101_Verify_Promoter_s_operation_rights_on_the_resell_post"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: 4498daf7-3269-4208-817a-6463c7cff775
    _resp1 = ctx.api.posts.promoter_resale(body='{"postId":"84b3d58a-964a-49ef-961e-62e885463410","status":"DRAFT"}', token='linda05_token')
    # === 断言（由Apifox assertion翻译）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    assert _j1.get('code') == 200, f"step1 code != 200, got {_j1.get('code')}"
    assert _j1.get('message') == 'success', f"step1 message != success, got {_j1.get('message')}"
    assert (_j1.get('data') or {}).get('status') == 'DRAFT', f"step1 data.status != DRAFT, got {(_j1.get('data') or {}).get('status')}"
    _rid = _get_path(_j1, ["data", "id"])
    assert _rid, "step1 resell_post_id 提取失败"
    vars['resell_post_id'] = _rid
    # step 2: 0389ebb4-f10a-4c5f-b075-f7f55c495f25
    # --- 人工补丁：名称唯一化 ---
    # Apifox 原文 PUT 的 urlAlias/title 与它「复制来源」的 post 同名，而服务端对同一商户
    # 做名称唯一校验 → 重复执行必然 400（Release 已累积 14 篇同名遗留 DRAFT，
    # 因为失败发生在清理步骤之前）。断言只检查 id/status，附加唯一后缀不改变语义，
    # 且能让末尾的 DELETE 真正被执行到。
    _uniq = _uuid.uuid4().hex[:8]
    _body2 = '{\r\n    "id": "{{resell_post_id}}",\r\n    "createFromEventId": null,\r\n    "urlAlias": "linda-t4652-t4653-t4654-verify-partner-can-set-update-disable-tax-rate-on-events-settings-1",\r\n    "headline": "(Linda) T4652 & T4653 & T4654 Verify partner can set & update & disable tax rate on events settings",\r\n    "title": "(Linda) T4652 & T4653 & T4654 Verify partner can set & update & disable tax rate on events settings",\r\n    "subTitle": "",\r\n    "media": [\r\n        {\r\n            "id": "6255834a-c9d9-4bf0-aded-e18d7cb07ae4",\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n            "selected": true,\r\n            "type": "IMAGE",\r\n            "height": 2048,\r\n            "width": 3072,\r\n            "mediaDuration": 0,\r\n            "mediaSrc": null,\r\n            "mediaType": "IMAGE",\r\n            "inherited": true,\r\n            "position": 0,\r\n            "referenceId": null,\r\n            "source": "POST",\r\n            "setThumbnail": false\r\n        }\r\n    ],\r\n    "status": "ACTIVE",\r\n    "styleSettings": {\r\n        "recentUsedColors": [\r\n            "#B7E2E0FF",\r\n            "#ECA416FF",\r\n            "#757575FF",\r\n            "#FFFFFFFF",\r\n            "#110921FF",\r\n            "#FFCDD2FF",\r\n            "#CB135BFF",\r\n            "#FF9800",\r\n            "#1B5E20",\r\n            "#FFF59D",\r\n            "#F57C00",\r\n            "#7986CBFF",\r\n            "#FFEEBEFF",\r\n            "#7132F4FF",\r\n            "#616161FF",\r\n            "#0B99FFFF",\r\n            "#E0E0E0FF"\r\n        ],\r\n        "fontFamily": "Inter",\r\n        "color": "#FFFFFF",\r\n        "backgroundColor": "#000000",\r\n        "borderColor": "#000000",\r\n        "secondaryTextColor": "#E0E0E0FF",\r\n        "announcementCarousel": {\r\n            "color": "#000000",\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "title": {\r\n            "color": "#F6CA7C",\r\n            "fontSize": 30,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "columnTitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 700\r\n        },\r\n        "subtitle": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 20,\r\n            "fontFamily": "Inter",\r\n            "fontWeight": 400\r\n        },\r\n        "button": {\r\n            "color": "#000000",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#F6CA7C"\r\n        },\r\n        "secondaryButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "boxShadow": "none",\r\n            "fontWeight": 400,\r\n            "borderColor": "#F6CA7C",\r\n            "borderRadius": 0\r\n        },\r\n        "textButton": {\r\n            "color": "#FFFFFF",\r\n            "fontSize": 16,\r\n            "fontWeight": 700\r\n        },\r\n        "selectButton": {\r\n            "borderColor": "#000000"\r\n        },\r\n        "relatedLink": {\r\n            "color": "#000000 ",\r\n            "borderColor": "#0000",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#FFFFFF80"\r\n        },\r\n        "featuredProducts": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 14,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 400\r\n            },\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "product": {\r\n            "color": "#FFFFFF",\r\n            "borderRadius": 0,\r\n            "backgroundColor": "#000000",\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "discount": {\r\n            "color": "#FFFFFF",\r\n            "priceColor": "#FFFFFF",\r\n            "backgroundColor": "#D32A09"\r\n        },\r\n        "freeShipping": {\r\n            "color": "#268E46",\r\n            "backgroundColor": "#EBF5EF"\r\n        },\r\n        "starRatingColor": "#FAAF03",\r\n        "layoutFeatureCard": {\r\n            "color": "#FFFFFF",\r\n            "title": {\r\n                "color": "#FFFFFF",\r\n                "fontSize": 16,\r\n                "fontFamily": "Inter",\r\n                "fontWeight": 700\r\n            },\r\n            "button": {\r\n                "color": "#000000",\r\n                "backgroundColor": "#F6CA7C"\r\n            },\r\n            "secondaryTextColor": "#E0E0E0FF"\r\n        },\r\n        "lineupBanner": {\r\n            "titleText": "#FFFFFF",\r\n            "descriptionText": "#F6CA7C"\r\n        },\r\n        "eventInfoBanner": {\r\n            "text": "#FFFFFF",\r\n            "secondaryText": "#ABABAB"\r\n        },\r\n        "eventDescription": {\r\n            "text": "#E0E0E0FF",\r\n            "title": "#FFFFFF"\r\n        },\r\n        "layout": {\r\n            "pageHeader": {\r\n                "style": "DEDICATED_HEADER_BAR",\r\n                "height": "MEDIUM",\r\n                "displayText": "SHOP_NAME"\r\n            },\r\n            "productBanner": {\r\n                "display": "HIDE",\r\n                "ctaButton": "VIEW_PRODUCT"\r\n            }\r\n        },\r\n        "template": "ClearSky",\r\n        "featuredProduct": {\r\n            "cover": {\r\n                "borderRadius": 0\r\n            }\r\n        }\r\n    },\r\n    "coverImages": [\r\n        {\r\n            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",\r\n            "width": 3072,\r\n            "height": 2048,\r\n            "mediaSrc": null,\r\n            "position": 1,\r\n            "mediaType": "IMAGE",\r\n            "mediaDuration": 0,\r\n            "inherited": true,\r\n            "selected": false\r\n        }\r\n    ],\r\n    "syncEnabled": true,\r\n    "cardCustomizeCoverImages": null,\r\n    "timeKey": 1770196355119\r\n}'
    _body2 = _body2.replace(
        "linda-t4652-t4653-t4654-verify-partner-can-set-update-disable-tax-rate-on-events-settings-1",
        f"linda-t4652-t4653-t4654-verify-partner-can-set-update-disable-tax-rate-on-events-settings-1-{_uniq}",
    ).replace(
        "(Linda) T4652 & T4653 & T4654 Verify partner can set & update & disable tax rate on events settings",
        f"(Linda) T4652 & T4653 & T4654 Verify partner can set & update & disable tax rate on events settings {_uniq}",
    )
    _resp2 = ctx.api.posts.curator_resell_by_resell_post_id(body=_body2, token='linda05_token')
    # === 断言（由Apifox assertion翻译）===
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"step2 code != 200, got {_j2.get('code')}"
    assert _j2.get('message') == 'success', f"step2 message != success, got {_j2.get('message')}"
    assert (_j2.get('data') or {}).get('status') == 'ACTIVE', f"step2 data.status != ACTIVE, got {(_j2.get('data') or {}).get('status')}"
    # step 3: 4da12903-d431-4211-895b-4d2c3f383bff
    _resp3 = ctx.api.posts.curator_by_post_id_2(body=None, token='linda05_token', path_vars={'post_id': '{{resell_post_id}}'})
    # === 断言（由Apifox assertion翻译）===
    _j3 = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
    assert _j3.get('code') == 200, f"step3 code != 200, got {_j3.get('code')}"
    assert _j3.get('message') == 'success', f"step3 message != success, got {_j3.get('message')}"
    _expectId3 = vars.get('resell_post_id')
    assert _expectId3, "未找到 resell_post_id"
    assert (_j3.get('data') or {}).get('id') == _expectId3, f"step3 data.id != {_expectId3}, got {(_j3.get('data') or {}).get('id')}"
