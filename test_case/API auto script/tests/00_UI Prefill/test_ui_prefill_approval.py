"""UI Automation Prefill -- Require approval to purchase (before / after posts).

**只做审批这一段**：不删用户、不跑其它预制步骤，可以单独执行：

    cd "test_case/API auto script"
    python -m pytest "tests/00_UI Prefill/test_ui_prefill_approval.py" -v -s

产出（同一个 event 下两个 post，UI 的 Post 标签页用下拉切换）：

    post-setting-require-approval-to-purchase-before  -> "Before approval" 模式
    post-setting-require-approval-to-purchase-after   -> "After approval"  模式

依赖：环境里已存在 source event "12061 phase2 auto event"（大 prefill 的 step 142 建的），
本文件会自己按标题查最新的那一个。

注意（踩过的坑）：
  * 改 post 的 urlAlias 必须用 ``PATCH /posts/curator/{postId}/url-alias``；
    admin 的 ``PATCH /post/{postId}`` 对 create-from-event 出来的 post **不生效**
    （返回 200/success，但 urlAlias 没变，UI 上还是自动生成的旧别名）。
  * 复制 post（``POST /posts/curator/event/{eventId}/duplicate/posts``）出来的 post
    **不带 relatedProducts**（票全丢），所以第二个 post 用
    ``POST /posts/curator/create-from-event`` 建（票会带上），再把座位图 CTA 的
    bodyJson 复制过去。
"""
NAME = "UI Automation Prefill - Require approval to purchase (before/after posts)"
TAGS = ["p0", "prefill", "suite:linda", "folder_00_ui_prefill"]
PRIORITY = 0

CASE_ID = None  # manually migrated, no Apifox Case ID
ENV_NAME = "Release"

import json as _json
import os
from typing import TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 IDE 能把 ctx.api.<域>.<方法>() 跳到 api/ 定义
    from core.context import Context

SOURCE_EVENT_TITLE = "12061 phase2 auto event"
APPROVAL_EVENT_TITLE = "post setting require approval to purchase"
ALIAS_BEFORE = "post-setting-require-approval-to-purchase-before"
ALIAS_AFTER = "post-setting-require-approval-to-purchase-after"


def _find_source_event(ctx: "Context") -> str:
    """按标题找 source event（取最新的一个）。"""
    _resp = ctx.api.events.list(
        params={"keyword": SOURCE_EVENT_TITLE, "pageSize": 50, "pageNumber": 1},
        token="token")
    expect(_resp).json('$.code').equals('200')
    _items = (_resp.json().get("data") or {}).get("items") or []
    _hits = [i for i in _items if i.get("title") == SOURCE_EVENT_TITLE]
    if not _hits:
        raise AssertionError(
            f"找不到 source event '{SOURCE_EVENT_TITLE}'，请先跑一次完整 prefill 创建它")
    return _hits[0]["id"]


def test_ui_prefill_approval(ctx: "Context"):
    """Pre-create the approval event with its two posts (before / after mode)."""
    vars = ctx  # 与大 prefill 一致：ctx 本身就是 vars 映射层（支持 .get / []）

    # --- step 0: Partner 999 login（只登录，**不删用户**）---
    # 需要一个新鲜的 JWT（寿命 120s）以及 user_id（模板 {{user_id}} 依赖它）。
    _resp_login = ctx.api.auth.sign_in(body="""{
    "email": "{{UIauto_partner_email}}",
    "password": "{{password}}"
}""", app_headers=True, token="token")
    expect(_resp_login).json('$.code').equals('200')
    ctx.extract("user_id", _resp_login, "$.data.id")
    ctx.extract("token", _resp_login, "$.data.token")

    # --- step 1: 清掉上一轮遗留的审批 event ---
    # 它们的 post 占着**全局唯一**的 urlAlias（-before / -after），新 post 改别名会
    # 报 400 "A post with the same urlAlias already exists"，UI 上就还是自动生成的旧别名。
    # ⚠️ 只删本测试自己建的 event（标题完全等于审批 event 标题），**绝不碰用户**
    #    （删用户会让 UI 侧保存的登录态失效）。
    _resp_old = ctx.api.events.list(
        params={"keyword": APPROVAL_EVENT_TITLE, "pageSize": 50, "pageNumber": 1},
        token="token")
    _old_items = (_resp_old.json().get("data") or {}).get("items") or []
    for _ev in _old_items:
        if _ev.get("title") != APPROVAL_EVENT_TITLE:
            continue
        _resp_old_posts = ctx.api.posts.curator_event_posts(event_id=_ev.get("id"), token="token")
        _old_data = _resp_old_posts.json().get("data")
        _old_posts = _old_data if isinstance(_old_data, list) else ((_old_data or {}).get("items") or [])
        for _p in _old_posts:
            _resp_del_post = ctx.api.posts.curator_by_post_id_2(post_id=_p.get("id"), token="token")
            print(f"  删除旧 post {_p.get('id')} ({_p.get('urlAlias')}) -> {_resp_del_post.status_code}")
        _resp_del_ev = ctx.api.events.by_event_id(event_id=_ev.get("id"), token="token")
        print(f"  删除旧审批 event {_ev.get('id')} -> {_resp_del_ev.status_code}")

    _source_event_id = _find_source_event(ctx)

    # --- step 151c: duplicate 12061 event -> "post setting require approval to purchase" ---
    # source event 由本文件自己查（不依赖大 prefill 的 vars）
    _body_151c = r"""{
    "title": "post setting require approval to purchase",
    "curatorId": "{{user_id}}",
    "description": "",
    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "startDate": "2053-04-17T05:00:00.000Z",
    "endDate": null,
    "venue": "Instagram Live, Zoom, In-person",
    "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",
    "status": "UPCOMING",
    "isTaxEnabled": false,
    "taxConfig": null,
    "mediaTextConfig": {
        "headline": "Missed our last event?",
        "subtitle": "Here's a lil recap of our last event👇",
        "align": "center"
    },
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
    "allowAutoComplete": true,
    "startDateDisplay": "2053-04-17",
    "note": "linda note",
    "timezone": {
        "timeZoneId": "America/Chicago",
        "timeZoneName": "Central Daylight Time",
        "dstOffset": 3600,
        "rawOffset": -21600
    },
    "isAddressRevealEnabled": false,
    "messageInfo": {
        "smsMaxLimit": 3,
        "emailMaxLimit": 5,
        "cooldownMinutes": 15
    },
    "platform": "PEAR",
    "creationStep": "COMPLETED",
    "extraInfo": null,
    "locationDetails": {
        "city": "Chicago",
        "line1": "789 River East Art Center Promenade",
        "line2": null,
        "state": "IL",
        "country": "US",
        "placeId": null,
        "zipcode": null,
        "stateName": "Illinois",
        "stripeLocationId": null
    },
    "country": "US",
    "state": "IL",
    "autoReplace": false,
    "lineupTransactionId": null,
    "lineupTransactionStatus": null,
    "autoPayLineupStatus": "PENDING",
    "medias": [],
    "lineup": [],
    "eventProducts": [],
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "duplicateEventId": "{_source_event_id}",
    "posterBackend": [
        {
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "width": 3072,
            "height": 2048,
            "position": 0,
            "mediaType": "IMAGE",
            "mediaDuration": 0
        }
    ],
    "styleSettings": {
        "fontFamily": "Inter",
        "color": "#FFFFFF",
        "backgroundColor": "#000000",
        "borderColor": "#000000",
        "dividerColor": "#FFFFFF",
        "secondaryTextColor": "#E0E0E0",
        "title": {"color": "#F6CA7C", "fontFamily": "Inter", "fontSize": 24, "fontWeight": 700},
        "columnTitle": {"fontFamily": "Inter", "fontSize": 20, "fontWeight": 700, "color": "#FFFFFF"},
        "subtitle": {"fontFamily": "Inter", "fontSize": 20, "fontWeight": 400, "color": "#FFFFFF"},
        "button": {"backgroundColor": "#F6CA7C", "color": "#000000", "borderColor": "#000000", "borderRadius": 12, "boxShadow": "none", "fontSize": 16, "fontWeight": 700},
        "secondaryButton": {"fontSize": 16, "fontWeight": 700, "color": "#FFFFFF", "borderColor": "#F6CA7C", "borderRadius": 12, "boxShadow": "none"},
        "textButton": {"fontSize": 16, "fontWeight": 700, "color": "#FFFFFF"},
        "selectButton": {"borderColor": "#000000"},
        "relatedLink": {"borderRadius": 99, "color": "#FFFFFF ", "borderColor": "#0000", "backgroundColor": "#FAFAFA"},
        "featuredProducts": {"borderRadius": 16, "backgroundColor": "#000000", "color": "#FFFFFF", "secondaryTextColor": "#E0E0E0", "title": {"fontFamily": "Inter", "fontSize": 14, "fontWeight": 400, "color": "#FFFFFF"}},
        "product": {"backgroundColor": "#000000", "borderRadius": 8, "color": "#FFFFFF", "secondaryTextColor": "#E0E0E0"},
        "discount": {"backgroundColor": "#D32A09", "color": "#FFFFFF", "priceColor": "#FFFFFF"},
        "freeShipping": {"backgroundColor": "#EBF5EF", "color": "#268E46"},
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {"title": {"fontFamily": "Inter", "fontSize": 16, "fontWeight": 700, "color": "#FFFFFF"}, "color": "#FFFFFF", "secondaryTextColor": "#E0E0E0", "button": {"backgroundColor": "#F6CA7C", "color": "#000000"}},
        "lineupBanner": {"titleText": "#FFFFFF", "descriptionText": "#E0E0E0"},
        "eventInfoBanner": {"text": "#FFFFFF", "secondaryTextColor": "#E0E0E0"},
        "eventDescription": {"text": "#E0E0E0", "title": "#FFFFFF"}
    }
}"""
    _body_151c = _body_151c.replace("{_source_event_id}", _source_event_id)
    _resp151c = ctx.api.events.v2_duplicate(body=_body_151c, app_headers=True, token="token")
    expect(_resp151c).json('$.code').equals('200')
    expect(_resp151c).json('$.message').equals('success')
    ctx.extract("approval_post_id", _resp151c, "$.data.posts[0].id")
    ctx.extract("approval_event_id", _resp151c, "$.data.id")
    expect(_resp151c).json('$.data.posts').is_array()
    expect(_resp151c).json('$.data.posts').is_not_empty()

    # --- step 151c2: create tickets on the duplicated event (duplicateEventId does NOT copy tickets) ---
    _approval_event_id = vars.get("approval_event_id", "")
    _resp151c2 = ctx.api.events.ticket_batch_v2(path_vars={"created_event_id": _approval_event_id}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072, "height": 2048, "position": 0, "mediaType": "IMAGE", "mediaDuration": 0
    },
    "listingType": "TICKET",
    "isTaxEnabled": false,
    "autoReplace": false,
    "tickets": [
        {
            "listingType": "TICKET", "ticketType": "TICKET_TYPE_STANDARD", "title": "test v", "bodyJson": "",
            "options": [{"name": "Title", "values": ["Default Title"], "images": []}],
            "variants": [{"inventoryQuantity": 20, "ticketPrice": 0, "price": "0", "fees": 0, "priceAnchor": "0", "option": {"option1": "Default Title"}, "transactionFee": {"platformFee": 0, "customFee": 0, "customFeeBreakdown": {"TAX": {"title": "Taxes", "unitFixedFee": 0, "unitPercentageFee": 0, "index": 0, "itemFee": 0}}, "transactionItemFee": 0}}]
        },
        {
            "listingType": "TICKET", "ticketType": "TICKET_TYPE_STANDARD", "title": "inside seat with 80", "bodyJson": "",
            "images": [{"src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png", "width": 3072, "height": 2048, "position": 0, "mediaType": "IMAGE", "mediaDuration": 0}],
            "options": [{"name": "Title", "values": ["Default Title"], "images": []}],
            "variants": [{"inventoryQuantity": 4, "ticketPrice": 71, "price": "80", "fees": 9, "priceAnchor": "0", "option": {"option1": "Default Title"}, "transactionFee": {"platformFee": 9, "customFee": 0, "customFeeBreakdown": {"TAX": {"title": "Taxes", "unitFixedFee": 0, "unitPercentageFee": 0, "index": 0, "itemFee": 0}}, "transactionItemFee": 9}}]
        },
        {
            "listingType": "TICKET", "ticketType": "TICKET_TYPE_STANDARD", "title": "inside seat with 100", "bodyJson": "",
            "images": [{"src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png", "width": 3072, "height": 2048, "position": 0, "mediaType": "IMAGE", "mediaDuration": 0}],
            "options": [{"name": "Title", "values": ["Default Title"], "images": []}],
            "variants": [{"inventoryQuantity": 43, "ticketPrice": 89, "price": "100", "fees": 11, "priceAnchor": "0", "option": {"option1": "Default Title"}, "transactionFee": {"platformFee": 11, "customFee": 0, "customFeeBreakdown": {"TAX": {"title": "Taxes", "unitFixedFee": 0, "unitPercentageFee": 0, "index": 0, "itemFee": 0}}, "transactionItemFee": 11}}]
        },
        {
            "listingType": "TICKET", "ticketType": "TICKET_TYPE_STANDARD", "title": "outside seat", "bodyJson": "",
            "images": [{"src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png", "width": 3072, "height": 2048, "position": 0, "mediaType": "IMAGE", "mediaDuration": 0}],
            "options": [{"name": "Day", "values": ["Saturday", "Sunday"], "images": [{"value": "Saturday", "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png"}, {"value": "Sunday", "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png"}]}],
            "variants": [
                {"inventoryQuantity": 20, "ticketPrice": 44, "price": "50", "fees": 6, "priceAnchor": "0", "imageIds": [], "imageId": null, "option": {"option1": "Saturday"}, "transactionFee": {"platformFee": 6, "customFee": 0, "customFeeBreakdown": {"TAX": {"title": "Taxes", "unitFixedFee": 0, "unitPercentageFee": 0, "index": 0, "itemFee": 0}}, "transactionItemFee": 6}},
                {"inventoryQuantity": 15, "ticketPrice": 44, "price": "50", "fees": 6, "priceAnchor": "0", "imageIds": [], "imageId": null, "option": {"option1": "Sunday"}, "transactionFee": {"platformFee": 6, "customFee": 0, "customFeeBreakdown": {"TAX": {"title": "Taxes", "unitFixedFee": 0, "unitPercentageFee": 0, "index": 0, "itemFee": 0}}, "transactionItemFee": 6}}
            ]
        }
    ],
    "coSellingCommissionRate": 0,
    "customFeeConfig": {"isEnabled": false, "items": []}
    }""", app_headers=True, token="token")
    expect(_resp151c2).json('$.code').equals('200')
    _approval_products = _resp151c2.json()["data"]["tickets"]
    vars["pid_approval_outside"] = _approval_products[3]["id"]
    vars["pid_approval_inside_100"] = _approval_products[2]["id"]
    vars["pid_approval_inside_80"] = _approval_products[1]["id"]

    # --- step 151c3: save + publish venue map on the duplicated event ---
    _approval_venue_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "fixtures", "venue_map_12061.json")
    with open(_approval_venue_path) as _f:
        _approval_venue_body = _f.read()
    _resp151c3 = ctx.api.admin.events_venue_map_create(
        venue_map_event_id=_approval_event_id,
        body=_approval_venue_body, token="admin_token", app_headers=True)
    expect(_resp151c3).json('$.code').equals('200')
    _resp151c4 = ctx.api.admin.events_venue_map_publish(
        venue_map_event_id=_approval_event_id,
        body=_approval_venue_body, token="admin_token", app_headers=True)
    expect(_resp151c4).json('$.code').equals('200')

    # --- step 151c5: bind categories to products ---
    _approval_assoc = _json.dumps({"associations": [
        {"categoryId": "dd69f2bd-23dc-49a6-9cb7-2b0a7c59f086", "productId": vars["pid_approval_outside"]},
        {"categoryId": "e27d924e-1848-4f1d-a891-9be07f24aece", "productId": vars["pid_approval_inside_100"]},
        {"categoryId": "ee8fdf1a-0de6-44a8-9666-dcafe68afd7a", "productId": vars["pid_approval_inside_80"]},
    ]})
    _resp151c5 = ctx.api.admin.events_venue_map_associations(
        venue_map_event_id=_approval_event_id,
        body=_approval_assoc, token="admin_token", app_headers=True)
    expect(_resp151c5).json('$.code').equals('200')


    # --- step 151d: set post URL alias (this post = "Before approval" mode) ---
    # ⚠️ 改 urlAlias 必须用 PATCH /posts/curator/{postId}/url-alias：
    #    admin 的 PATCH /post/{postId} 对 create-from-event 出来的 post 不生效
    #    （返回 200/success，但 urlAlias 根本没变，UI 上还是自动生成的旧别名）。
    _resp151d = ctx.api.admin.post_by_post_id(
        path_vars={"post_id": vars.get("approval_post_id", "")},
        body="""{
    "headline": "post setting require approval to purchase",
    "title": "post setting require approval to purchase",
    "subTitle": "",
    "links": [],
    "creatorId": "{{user_id}}",
    "baseSold": 0,
    "baseViewed": 0,
    "expiredAt": null,
    "hideInStore": false,
    "checkoutInPost": true,
    "status": "ACTIVE"
}""", token="admin_token", app_headers=True)
    expect(_resp151d).json('$.code').equals('200')
    expect(_resp151d).json('$.message').equals('success')
    _resp151d_alias = ctx.api.posts.curator_url_alias(
        post_id=vars.get("approval_post_id", ""),
        body={"urlAlias": ALIAS_BEFORE}, token="token", app_headers=True)
    expect(_resp151d_alias).json('$.code').equals('200')


    # --- step 151e: fix CTA eventId in duplicated post (duplicate copies old eventId) ---
    _approval_post_id = vars.get("approval_post_id", "")
    _approval_event_id = vars.get("approval_event_id", "")
    _resp151e = ctx.api.posts.curator_edit_by_post_id(
        post_id=_approval_post_id, token="token", app_headers=True)
    expect(_resp151e).json('$.code').equals('200')
    _approval_post_data = _resp151e.json()["data"]
    _approval_body = _json.loads(_approval_post_data["bodyJson"]) if isinstance(_approval_post_data.get("bodyJson"), str) else _approval_post_data.get("bodyJson", {})
    _approval_children = _approval_body.get("root", {}).get("children", [])
    _has_cta = False
    for _child in _approval_children:
        if _child.get("action") == "show-venue-map":
            _child["eventId"] = _approval_event_id
            _has_cta = True
    if not _has_cta:
        # source post 上没有座位图 CTA 时自己补一个（保证本文件自包含）
        import uuid as _uuid
        _approval_children.insert(0, {
            "id": str(_uuid.uuid4()),
            "label": "Show venue map drawer",
            "height": "42px",
            "type": "cta-button",
            "version": 2,
            "width": "100%",
            "action": "show-venue-map",
            "eventId": _approval_event_id,
        })
    _approval_body["root"]["children"] = _approval_children
    _patch_approval = dict(_approval_post_data)
    _patch_approval["bodyJson"] = _json.dumps(_approval_body)
    _resp151f = ctx.api.posts.update_curator_content(
        venue_map_post_id=_approval_post_id,
        body=_json.dumps(_patch_approval), token="token", app_headers=True)
    expect(_resp151f).json('$.code').equals('200')


    # --- step 151g: create the second post of the same event ("After approval" mode) ---
    # 同一个 event 下要放两个 post，UI 的 Post 标签页用下拉（DownLineIcon）切换。
    # ⚠️ 不要用 POST /posts/curator/event/{eventId}/duplicate/posts（复制 post）：
    #    复制出来的 post **不会带 relatedProducts**（票全丢，hasTicketProducts=false），
    #    而 Event 类型的票又不能直接 PATCH 上去（"Cannot add Event products directly.
    #    Event products are managed through Event sync."），
    #    POST /posts/curator/toggle-sync 还会 500（numSold 只读）。
    #    => 用 create-from-event：内容/媒体/样式从 event 继承，票也会带上。
    _resp151g = ctx.api.posts.curator_create_from_event(
        body={"eventId": _approval_event_id, "allowPromotersResell": True},
        token="token", app_headers=True)
    expect(_resp151g).json('$.code').equals('200')
    # ⚠️ expect() 只能接 ApiResponse，直接对 str 断言会抛
    #    "expect() 需要 ApiResponse，实际收到 str"。
    expect(_resp151g).json('$.data.id').is_not_empty()
    _after_post_id = _resp151g.json()["data"]["id"]

    # --- step 151h: give the new post the same venue-map CTA body ---
    # create-from-event 建出来的 post 默认是 ticket-all 区块，没有 "Show venue map drawer" CTA，
    # 这里直接复用 before post 的 bodyJson（同一个 event，CTA/eventId 一致）。
    _resp151h = ctx.api.posts.curator_edit_by_post_id(
        post_id=_after_post_id, token="token", app_headers=True)
    expect(_resp151h).json('$.code').equals('200')
    _after_post_data = _resp151h.json()["data"]
    _patch_after = dict(_after_post_data)
    _patch_after["bodyJson"] = _json.dumps(_approval_body)
    _resp151i = ctx.api.posts.update_curator_content(
        venue_map_post_id=_after_post_id,
        body=_json.dumps(_patch_after), token="token", app_headers=True)
    expect(_resp151i).json('$.code').equals('200')

    # --- step 151j: rename the new post -> ...-after (After approval mode) ---
    _resp151j = ctx.api.admin.post_by_post_id(
        post_id=_after_post_id,
        body="""{
    "headline": "post setting require approval to purchase after",
    "title": "post setting require approval to purchase after",
    "subTitle": "",
    "links": [],
    "creatorId": "{{user_id}}",
    "baseSold": 0,
    "baseViewed": 0,
    "expiredAt": null,
    "hideInStore": false,
    "checkoutInPost": true,
    "status": "ACTIVE"
}""", token="admin_token", app_headers=True)
    expect(_resp151j).json('$.code').equals('200')
    expect(_resp151j).json('$.message').equals('success')
    _resp151j_alias = ctx.api.posts.curator_url_alias(
        post_id=_after_post_id, body={"urlAlias": ALIAS_AFTER}, token="token", app_headers=True)
    expect(_resp151j_alias).json('$.code').equals('200')

    # --- step 151k: verify both posts exist and carry the tickets ---
    # ⚠️ expect() 只接受 ApiResponse，断言必须挂在响应上（不能直接对 str/list 断言）。
    _resp151k = ctx.api.posts.curator_event_posts(
        event_id=_approval_event_id, token="token", app_headers=True)
    expect(_resp151k).json('$.code').equals('200')
    expect(_resp151k).json('$.data.items').is_array()
    # ⚠️ 不要用递归路径 `..urlAlias`：它会命中 post 里嵌套的 event.posts[] 的别名，
    #    即使顶层别名没改对也会"通过"。这里用过滤谓词精确取顶层那条。
    expect(_resp151k).json(f'$.data.items[?(@.urlAlias == "{ALIAS_BEFORE}")].id').exists()
    expect(_resp151k).json(f'$.data.items[?(@.urlAlias == "{ALIAS_AFTER}")].id').exists()
    # 这个 event 上只有这两个 post
    expect(_resp151k).json('$.data.items[0].urlAlias').exists()
    expect(_resp151k).json('$.data.items[1].urlAlias').exists()
    expect(_resp151k).json('$.data.items[2].urlAlias').not_exists()
    # 两个 post 都带着 event 的票（copy post 会丢票，create-from-event 才带得上）
    _resp151k1 = ctx.api.posts.curator_edit_by_post_id(
        post_id=_approval_post_id, token="token", app_headers=True)
    expect(_resp151k1).json('$.data.hasTicketProducts').equals(True)
    _resp151k2 = ctx.api.posts.curator_edit_by_post_id(
        post_id=_after_post_id, token="token", app_headers=True)
    expect(_resp151k2).json('$.data.hasTicketProducts').equals(True)

    # --- 收尾：打印最终状态，肉眼可直接核对两个 post 的 URL ---
    _resp_final = ctx.api.posts.curator_event_posts(
        event_id=_approval_event_id, token="token", app_headers=True)
    _fd = _resp_final.json().get("data")
    _final_posts = _fd if isinstance(_fd, list) else ((_fd or {}).get("items") or [])
    print(f"[approval prefill] event={_approval_event_id} posts={len(_final_posts)}")
    for _p in _final_posts:
        print(f"    urlAlias={_p.get('urlAlias')!r}  title={_p.get('title')!r}")


    # ================================================================
    # Prefill event: lury-ui-automation-testing (for linda999)
    # ================================================================

