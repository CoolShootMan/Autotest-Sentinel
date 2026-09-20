"""UI Automation Data Pre-configuration -- migrated from Apifox CLI collection.

Original collection: "UI Automation Data Pre-configuration staging & release env - no sql"
Migrated to pytest style using ctx.api facade calls.

This test pre-configures test data before UI automation runs:
  - Admin login, search/cleanup/create partner 999/997/998 users
  - Partner 999/997 login, create event/ticket/lineup/media
  - Create general product, post, catalog, form, shipping options
  - Sync post to coseller, authorize products, setup store tabs

Original Apifox collection and prefill_runner.py are in tools/prefill/.
"""
NAME = "UI Automation Data Pre-configuration (staging & release, no SQL)"
TAGS = ["p0", "prefill", "suite:linda", "folder_00_ui_prefill"]
PRIORITY = 0

CASE_ID = None  # manually migrated, no Apifox Case ID
ENV_NAME = "Release"

import datetime as _dt  # step 106/116 需要动态生成事件起止日期
import logging
import time  # step 107/117 重试 relate-products 的空窗抖动用
from typing import TYPE_CHECKING

from core.assertions import expect

_logger = logging.getLogger("api.framework")  # 与 core/context.py 同一日志通道

if TYPE_CHECKING:  # 仅类型检查期导入：让 IDE 能把 ctx.api.<域>.<方法>() 跳到 api/ 定义
    from core.context import Context


def test_ui_prefill_data_configuration(ctx: "Context"):
    """UI automation data pre-configuration: create/cleanup users, events, products, stores."""
    vars = ctx

    # ======================================================================
    # step_0
    # ======================================================================
    # --- step 1: admin login (POST {{adminurl}}/auth/login) ---
    # NOTE: 管理后台登录在 admin 域（{{adminurl}} = https://release.admin.katana-api.1m.app）。
    # 迁移时误写成 ctx.api.auth.login -> 打到 base 域 /auth/login，后端直接 404
    # "Cannot POST /auth/login"，导致第 1 步就挂、后面 136 步全部没机会跑。
    _resp1 = ctx.api.admin.auth_login(body="""{
    "email": "{{UIauto_admin_email}}",
    "password": "{{adminpassword}}"
}""", app_headers=True, token="admin_token")
    expect(_resp1).json('$.code').equals('200')
    expect(_resp1).json('$.message').equals('success')



    # --- step 2: Admin search partner 999 (POST /users/search) ---
    _resp2 = ctx.api.admin.users_search(body="""{
    "query": "{{UIauto_partner_email}}",
    "filter": {
        "userRoles": [
            "PROMOTER",
            "BUSINESS_PARTNER",
            "CONSUMER"
        ],
        "userType": "ALL"
    },
    "pageSize": 100,
    "pageNumber": 1
}


""", app_headers=True, token="admin_token")
    expect(_resp2).json('$.code').equals('200')
    expect(_resp2).json('$.message').equals('success')
    ctx.extract("user_id", _resp2, "$.data.items[0].id")



    # --- step 3: Admin search partner 997 (POST /users/search) ---
    _resp3 = ctx.api.admin.users_search(body="""{
    "query": "{{UIauto_partner997_email}}",
    "filter": {
        "userRoles": [
            "PROMOTER",
            "BUSINESS_PARTNER",
            "CONSUMER"
        ],
        "userType": "ALL"
    },
    "pageSize": 100,
    "pageNumber": 1
}""", app_headers=True, token="admin_token")
    expect(_resp3).json('$.code').equals('200')
    expect(_resp3).json('$.message').equals('success')
    ctx.extract("user_partner997_id", _resp3, "$.data.items[0].id")



    # --- step 4: Admin search coseller 998 (POST /users/search) ---
    _resp4 = ctx.api.admin.users_search(body="""{
    "query": "{{UIauto_coseller_email}}",
    "filter": {
        "userRoles": [
            "PROMOTER",
            "BUSINESS_PARTNER",
            "CONSUMER"
        ],
        "userType": "ALL"
    },
    "pageSize": 100,
    "pageNumber": 1
}""", app_headers=True, token="admin_token")
    expect(_resp4).json('$.code').equals('200')
    expect(_resp4).json('$.message').equals('success')
    ctx.extract("user_coseller_id", _resp4, "$.data.items[0].id")

    if vars.get("user_id"):


        # --- step 5: delete the users and check the user delete success (DELETE /users/{{user_id}}) ---
        _resp5 = ctx.api.admin.users_by_user_id(params={"deleteOrders": "true"}, path_vars={"user_id": vars.get("user_id", "")}, body="""{"deleteOrders":true}""", app_headers=True, token="admin_token")
        expect(_resp5).json('$.code').equals('200')
        expect(_resp5).json('$.message').equals('success')
        expect(_resp5).json('$.data.status').equals('ok')

    if vars.get("user_coseller_id"):


        # --- step 6: delete the users and check the user delete success (DELETE /users/{{user_coseller_id}}) ---
        _resp6 = ctx.api.admin.users_by_user_id(params={"deleteOrders": "true"}, path_vars={"user_id": vars.get("user_coseller_id", "")}, body="""{"deleteOrders":true}""", app_headers=True, token="admin_token")
        expect(_resp6).json('$.code').equals('200')
        expect(_resp6).json('$.message').equals('success')
        expect(_resp6).json('$.data.status').equals('ok')

    if vars.get("user_partner997_id"):


        # --- step 7: delete the users and check the user delete success (DELETE /users/{{user_partner997_id}}) ---
        _resp7 = ctx.api.admin.users_by_user_id(params={"deleteOrders": "true"}, path_vars={"user_id": vars.get("user_partner997_id", "")}, body="""{"deleteOrders":true}""", app_headers=True, token="admin_token")
        expect(_resp7).json('$.code').equals('200')
        expect(_resp7).json('$.message').equals('success')
        expect(_resp7).json('$.data.status').equals('ok')



    # --- step 8: Create partner999 on admin tools (POST /users/tool/external-user-import/partner) ---
    _resp8 = ctx.api.admin.users_tool_external_user_import_partner(body="""{
    "allowSyncResalePosts": true,
    "defaultModuleName": "Upcoming Events",
    "email": "{{UIauto_partner_email}}"
}""", app_headers=True, token="admin_token")
    expect(_resp8).json('$.code').equals('200')
    expect(_resp8).json('$.message').equals('success')
    # 注意: 原始集合此处 pm.environment.set("password", MD5(res.data.password)) 属于**死写**——
    # 后续所有「设置密码 / 登录」节点用的都是字面量 7EbE8F4BdE4A38768AcF9C2833aF2Db5
    # （= MD5("Happy123")，即环境变量 {{password}} 的取值），从不读这个被覆盖的 password。
    # 迁移时误写成 extract("password", resp, "$.data.md5Password")：该字段不存在，
    # 会把 {{password}} 清空 -> PUT /users/{id}/password 500 PasswordStrengthError。
    # 故此处**不得**再覆盖 {{password}}。



    # --- step 9: Admin search partner 999 (POST /users/search) ---
    _resp9 = ctx.api.admin.users_search(body="""{
    "query": "{{UIauto_partner_email}}",
    "filter": {
        "userRoles": [
            "PROMOTER",
            "BUSINESS_PARTNER"
        ],
        "userType": "ALL"
    },
    "pageSize": 100,
    "pageNumber": 1
}""", app_headers=True, token="admin_token")
    expect(_resp9).json('$.code').equals('200')
    expect(_resp9).json('$.message').equals('success')
    ctx.extract("user_id", _resp9, "$.data.items[0].id")



    # --- step 10: set partner999 password to Happy123 (PUT /users/{{user_id}}/password) ---
    _resp10 = ctx.api.admin.users_password(path_vars={"user_id": vars.get("user_id", "")}, body="""{"password":"{{password}}"}""", app_headers=True, token="admin_token")
    expect(_resp10).json('$.code').equals('200')
    expect(_resp10).json('$.message').equals('success')



    # --- step 11: Create partner997 on admin tools (POST /users/tool/external-user-import/partner) ---
    _resp11 = ctx.api.admin.users_tool_external_user_import_partner(body="""{
    "allowSyncResalePosts": true,
    "defaultModuleName": "Upcoming Events",
    "email": "{{UIauto_partner997_email}}"
}""", app_headers=True, token="admin_token")
    expect(_resp11).json('$.code').equals('200')
    expect(_resp11).json('$.message').equals('success')
    # 注意: 同 step 8 —— 原始集合的 pm.environment.set("password", res.data.password)
    # 是死写（这里是明文随机密码，后端要求的是 MD5），后续节点用的是字面量。
    # 覆盖 {{password}} 会让后续 PUT 设为弱口令 / 登录失败，故此处不提取。
    expect(_resp11).status().is_(201)
    expect(_resp11).json('$.data.password').is_string()
    expect(_resp11).json('$.data.password').is_not_empty()



    # --- step 12: Admin search partner 997 (POST /users/search) ---
    _resp12 = ctx.api.admin.users_search(body="""{
    "query": "{{UIauto_partner997_email}}",
    "filter": {
        "userRoles": [
            "PROMOTER",
            "BUSINESS_PARTNER"
        ],
        "userType": "ALL"
    },
    "pageSize": 100,
    "pageNumber": 1
}""", app_headers=True, token="admin_token")
    expect(_resp12).json('$.code').equals('200')
    expect(_resp12).json('$.message').equals('success')
    ctx.extract("user_partner997_id", _resp12, "$.data.items[0].id")



    # --- step 13: set partner997 password (PUT /users/{{user_partner997_id}}/password) ---
    _resp13 = ctx.api.admin.users_password(path_vars={"user_id": vars.get("user_partner997_id", "")}, body="""{"password":"{{password}}"}""", app_headers=True, token="admin_token")
    expect(_resp13).json('$.code').equals('200')
    expect(_resp13).json('$.message').equals('success')



    # --- step 14: delay 3.0s ---
    # NOTE: original Apifox collection had a 3.0s delay here; removed per framework style (no time.sleep).


    # --- step 15: delay 3.0s ---
    # NOTE: original Apifox collection had a 3.0s delay here; removed per framework style (no time.sleep).


    # --- step 16: delay 3.0s ---
    # NOTE: original Apifox collection had a 3.0s delay here; removed per framework style (no time.sleep).


    # --- step 17: Connect 999 and 997  (POST /users/promoter-associations/connect/{{user_id}}) ---
    _resp17 = ctx.api.admin.users_promoter_associations_connect_by_user_id(path_vars={"user_id": vars.get("user_id", "")}, body="""{"promoterInfo":"{{UIauto_partner997_email}}"}""", app_headers=True, token="admin_token")
    expect(_resp17).json('$.code').equals('200')
    expect(_resp17).json('$.message').equals('success')



    # --- step 18: Partner 999 login (POST /auth/sign-in) ---
    _resp18 = ctx.api.auth.sign_in(body="""{
    "email": "{{UIauto_partner_email}}",
    "password": "{{password}}"

}""", app_headers=True, token="token")
    expect(_resp18).json('$.code').equals('200')
    expect(_resp18).json('$.message').equals('success')
    ctx.extract("user_id", _resp18, "$.data.id")
    # 原始集合 node「Partner 999 login」的 syncUserVariable() 按“当前登录邮箱”分流：
    #   邮箱 == UIauto_partner_email    -> set user_id
    #   邮箱 == UIauto_coseller_email   -> set user_coseller_id
    #   邮箱 == UIauto_partner997_email -> set user_partner997_id
    # 本步登录的是 999，因此【只能】写 user_id。
    # 绝不能把登录响应的 data.id 写进 user_coseller_id / user_partner997_id：
    # 那会把 997 的 id（来自前面 admin users/search）覆盖成 999 自己的 id，
    # 导致后续 posts/curator/{post0_id}/promoters/sync 把帖子同步给 999 自己，
    # 从而不产生 resell 子帖，GET /post/{post0_id}/children 返回 items:[]。
    ctx.extract("token", _resp18, "$.data.token")



    # --- step 19: update the partner999's store shop url to autoshop (PUT /store-front) ---
    _resp19 = ctx.api.storefront.update(body="""{
    "userInfo": {
        "storeName": "{{partner_storeName}}",
        "logo": null,
        "backgroundSource": {
            "width": 375,
            "height": 375,
            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1764821680/setting/wrbmwobccxtbsy1e79h0.webp"
        },
        "description": "",
        "subTitle": "",
        "socialMedias": [],
        "storeFront": {
            "storeTabs": [
                {
                    "name": "Posts",
                    "checked": false
                },
                {
                    "name": "Links",
                    "checked": false
                },
                {
                    "name": "Products",
                    "checked": false
                },
                {
                    "name": "Forms",
                    "checked": false
                }
            ]
        },
        "vanityUrl": "{{partner_vanityUrl}}"
    }
}""", app_headers=True, token="token")
    expect(_resp19).json('$.code').equals('200')
    expect(_resp19).json('$.message').equals('success')



    # --- step 20: get partner 999's uncoming module id (GET store-front/shop/autotestshop) ---
    _resp20 = ctx.api.storefront.shop(path_vars={"partner_vanityUrl": 'autotestshop'}, params={"public": "false"}, token="token", app_headers=True)
    expect(_resp20).json('$.code').equals('200')
    expect(_resp20).json('$.message').equals('success')
    ctx.extract("module_id", _resp20, '$.data.shopModules[?(@.title=="Upcoming Events")].id')


    # --- step 21: get partner 999's uncoming module id (GET /store-front/shop/{{partner_vanityUrl}}) ---
    _resp21 = ctx.api.storefront.shop(path_vars={"partner_vanityUrl": vars.get("partner_vanityUrl", "")}, params={"public": "false"}, app_headers=True, token="token")
    expect(_resp21).json('$.code').equals('200')
    expect(_resp21).json('$.message').equals('success')
    ctx.extract("module_id", _resp21, '$.data.shopModules[?(@.title=="Upcoming Events")].id')



    # --- step 22: delay 3.0s ---
    # NOTE: original Apifox collection had a 3.0s delay here; removed per framework style (no time.sleep).


    # --- step 23: Partner Create event (POST /product-event/v2) ---
    _resp23 = ctx.api.events.create_v2(body=r"""{
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "isTimeUnspecified": false,
    "allowAutoComplete": true,
    "description": "",
    "note": "linda note",
    "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",
    "status": "UPCOMING",
    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "isTaxEnabled": false,
    "isAddressRevealEnabled": false,
    "title": "verify-co-seller-auto-archive",
    "venue": "Instagram Live, Zoom, In-person",
    "timezone": {
        "timeZoneId": "America/Chicago",
        "timeZoneName": "Central Daylight Time",
        "dstOffset": 3600,
        "rawOffset": -21600
    },
    "poster": {
        "height": 2048,
        "width": 3072,
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "mediaType": "IMAGE"
    },
    "startDateDisplay": "2053-04-17",
    "styleSettings": {
        "fontFamily": "Inter",
        "color": "#FFFFFF",
        "backgroundColor": "#000000",
        "borderColor": "#000000",
        "dividerColor": "#FFFFFF",
        "secondaryTextColor": "#E0E0E0",
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 700
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 400,
            "color": "#FFFFFF"
        },
        "button": {
            "backgroundColor": "#F6CA7C",
            "color": "#000000",
            "borderColor": "#000000",
            "borderRadius": 12,
            "boxShadow": "none",
            "fontSize": 16,
            "fontWeight": 700
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF",
            "borderColor": "#F6CA7C",
            "borderRadius": 12,
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "borderRadius": 99,
            "color": "#000000 ",
            "borderColor": "#0000",
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "borderRadius": 16,
            "backgroundColor": "#000000",
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#FFFFFF"
            }
        },
        "product": {
            "backgroundColor": "#000000",
            "borderRadius": 8,
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "backgroundColor": "#D32A09",
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        }
    }
}""", app_headers=True, token="token")
    expect(_resp23).json('$.code').equals('200')
    expect(_resp23).json('$.message').equals('success')
    ctx.extract("created_event_id", _resp23, "$.data.id")
    expect(_resp23).status().is_(201)
    expect(_resp23).json('$.data').exists()
    expect(_resp23).json('$.data.id').exists()



    # --- step 24: Partner999 Create event media next step  (POST /product-event/v2/{{created_event_id}}/media/batch/create) ---
    _resp24 = ctx.api.events.media_batch_create(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
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
    "medias": [],
    "mediaTextConfig": {
        "headline": "Missed our last event?",
        "subtitle": "Here's a lil recap of our last event👇",
        "align": "center"
    }
}""", app_headers=True, token="token")
    expect(_resp24).json('$.code').equals('200')
    expect(_resp24).json('$.message').equals('success')



    # --- step 25: Partner999 Create event ticket next step (POST /product-event/v2/{{created_event_id}}/ticket/batch/v2) ---
    _resp25 = ctx.api.events.ticket_batch_v2(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
    "listingType": "TICKET",
    "isTaxEnabled": false,
    "autoReplace": false,
    "tickets": [
        {
            "listingType": "TICKET",
            "ticketType": "TICKET_TYPE_STANDARD",
            "images": [
                {
                    "id": "80f43627-4bef-49b0-934b-cd63d49f8787",
                    "height": 1000,
                    "width": 1000,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "mediaType": "IMAGE"
                }
            ],
            "title": "General Admission",
            "bodyJson": "",
            "options": [
                {
                    "name": "Title",
                    "values": [
                        "Default Title"
                    ],
                    "images": []
                }
            ],
            "variants": [
                {
                    "inventoryQuantity": 1000,
                    "ticketPrice": 22,
                    "price": 25.55,
                    "fees": 3.55,
                    "priceAnchor": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "transactionFee": {
                        "platformFee": 3.5,
                        "customFee": 0,
                        "customFeeBreakdown": {
                            "TAX": {
                                "title": "Taxes",
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0,
                                "index": 0,
                                "itemFee": 0
                            }
                        },
                        "transactionItemFee": 3.55
                    }
                }
            ]
        }
    ],
    "coSellingCommissionRate": 0,
    "customFeeConfig": {
        "isEnabled": false,
        "items": []
    }
}""", app_headers=True, token="token")
    expect(_resp25).json('$.code').equals('200')
    expect(_resp25).json('$.message').equals('success')



    # --- step 26: Partner999 Create event lineup next step (POST /product-event/v2/{{created_event_id}}/lineup/batch) ---
    _resp26 = ctx.api.events.lineup_batch(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{"lineup":[]}""", app_headers=True, token="token")
    expect(_resp26).json('$.code').equals('200')
    expect(_resp26).json('$.message').equals('success')
    ctx.extract("ticket_id", _resp26, "$.data.tickets[0].id")
    ctx.extract("variant_id", _resp26, "$.data.tickets[0].variants[0].id")
    expect(_resp26).json('$.data.title').equals('verify-co-seller-auto-archive')
    expect(_resp26).json('$.data.tickets[0].id').is_string()
    expect(_resp26).json('$.data.tickets[0].id').is_not_empty()
    expect(_resp26).json('$.data.tickets[0].variants[0].id').is_string()
    expect(_resp26).json('$.data.tickets[0].variants[0].id').is_not_empty()



    # --- step 27: get the event post id (GET /posts/curator/event/{{created_event_id}}/posts) ---
    _resp27 = ctx.api.posts.curator_event_posts(path_vars={"event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    expect(_resp27).json('$.code').equals('200')
    expect(_resp27).json('$.message').equals('success')
    ctx.extract("post0_id", _resp27, "$.data.items[0].id")
    expect(_resp27).json('$.data.items[0].id').is_string()
    expect(_resp27).json('$.data.items[0].id').is_not_empty()



    # --- step 28: Partner999 sync to module (POST /store-front/sync-post-to-module) ---
    _resp28 = ctx.api.storefront.sync_post_to_module(body="""{
    "postId": "{{post0_id}}",
    "moduleIds": [
        "{{module_id}}"
    ]
}""", app_headers=True, token="token")
    expect(_resp28).json('$.code').equals('200')
    expect(_resp28).json('$.message').equals('success')



    # --- step 29: duplicate event for yuxiao (POST /product-event/v2/duplicate) ---
    _resp29 = ctx.api.events.v2_duplicate(body=r"""{
    "title": "verify-post-shipping_fee",
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
    "tickets": [
        {
            "id": "{{ticket_id}}",
            "remote_id": null,
            "platform": "PEAR",
            "createdAt": "2026-04-22T07:08:00.363Z",
            "updatedAt": "2026-04-22T08:09:37.162Z",
            "merchantId": "{{eventcatalog_id}}",
            "title": "General Admission",
            "bodyHtml": "",
            "originalBodyHtml": "",
            "isBodyHtmlOverridden": false,
            "bodyText": "",
            "handle": null,
            "productType": "",
            "publishedAt": "2026-04-22T07:08:00.374Z",
            "publishedScope": "",
            "status": "ACTIVE",
            "externalStatus": "ACTIVE",
            "followExternalStatus": false,
            "tags": [],
            "templateSuffix": null,
            "vendor": "Pear",
            "syncAt": null,
            "deletedAt": null,
            "delisted": false,
            "excludedByImportingTag": false,
            "isFeatured": false,
            "featuredScore": null,
            "inventoryQuantity": 1000,
            "inventoryQuantityOriginal": 1000,
            "soldQuantity": 0,
            "priceDisplay": 25.56,
            "priceDisplayAnchor": 0,
            "priceMin": 25.56,
            "priceMinAnchor": 0,
            "priceMax": 25.56,
            "priceMaxAnchor": 0,
            "priceImportedMin": 0,
            "priceImportedMax": 0,
            "imageCount": 1,
            "isUsed": "NWT",
            "shippingType": "NO_SHIPPING_REQUIRED",
            "additionalShippingFee": 0,
            "deliveryTime": [
                0,
                5
            ],
            "returnPolicyApplied": true,
            "isAvailable": false,
            "commissionRate": 10,
            "textForShare": null,
            "priceSyncImported": false,
            "coverImage": {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                "width": 1000,
                "height": 1000,
                "mediaSrc": null,
                "mediaType": "IMAGE",
                "mediaDuration": 0
            },
            "reviewCount": null,
            "reviewOverallScore": null,
            "reviewAggregate": null,
            "displayReviews": true,
            "links": null,
            "taxEnable": false,
            "taxJarCategory": null,
            "overrideEventTax": false,
            "customTaxRate": null,
            "subscriptionPlanId": null,
            "reviewRedirectProductId": null,
            "reviewSummary": null,
            "customFieldsInfo": null,
            "listingType": "TICKET",
            "extraInfo": {
                "date": "Thu, Apr 17, 2053 (CDT)",
                "event": "verify-post-shipping_fee",
                "venue": "Instagram Live, Zoom, In-person",
                "lineup": [],
                "poster": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "status": "COMPLETED",
                "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",
                "eventNote": "linda note",
                "startDate": "2053-04-17T05:00:00.000Z",
                "timeZoneId": "America/Chicago",
                "isAddressHidden": false,
                "addressRevealConfig": null
            },
            "bodyJson": null,
            "shippingOptions": null,
            "shippingNote": null,
            "autoFulfill": true,
            "eventId": "{{created_event_id}}",
            "lifecycleStatus": "LIFECYCLE_STATUS_ARCHIVED",
            "copyFromId": "{{ticket_id}}",
            "stopSellingAfter": null,
            "stopSellingAfterDisplay": null,
            "deliveryMethod": "QR_CODE",
            "thirdPartyDeliveryMessage": null,
            "isMultipleDaysPassEnabled": false,
            "multipleDaysPass": null,
            "isPickupEtaEnabled": null,
            "eventMatchingRules": null,
            "excludeFromPostSync": false,
            "isExpirationEnabled": false,
            "expirationTime": null,
            "expirationTimeDisplay": null,
            "allowAtDoorSales": false,
            "isProductFormEnabled": false,
            "isVariantPriceDisplayEnabled": false,
            "isTipEnabled": false,
            "images": [
                {
                    "id": "b471bc6e-a872-4253-ab7a-41fa0cf51c2d",
                    "remote_id": null,
                    "createdAt": "2026-04-22T07:08:00.377Z",
                    "updatedAt": "2026-04-22T07:08:00.377Z",
                    "height": 1000,
                    "width": 1000,
                    "position": 1,
                    "productId": "{{ticket_id}}",
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "variantIds": [],
                    "mediaType": "IMAGE",
                    "mediaSrc": null,
                    "mediaDuration": 0,
                    "contributedBy": 3,
                    "contributorId": null,
                    "productImageType": "PRODUCT",
                    "source": null
                }
            ],
            "options": [
                {
                    "name": "Title",
                    "images": [
                        {
                            "value": "Default Title",
                            "image": null
                        }
                    ]
                }
            ],
            "variants": [
                {
                    "id": "{{variant_id}}",
                    "remote_id": null,
                    "createdAt": "2026-04-22T07:08:00.377Z",
                    "updatedAt": "2026-04-22T07:08:00.377Z",
                    "compareAtPrice": null,
                    "fulfillmentService": "manual",
                    "grams": 0,
                    "imageId": null,
                    "imageIds": [],
                    "inventoryItemId": null,
                    "inventoryManagement": "Pear",
                    "inventoryPolicy": "DENY",
                    "inventoryQuantity": 1000,
                    "inventoryQuantityOriginal": 1000,
                    "soldQuantity": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "position": 1,
                    "price": "25.56",
                    "priceAnchor": "0",
                    "priceImported": "0.00",
                    "productId": "{{ticket_id}}",
                    "sku": "",
                    "taxCode": null,
                    "taxable": true,
                    "title": "Default Title",
                    "weight": null,
                    "weightUnit": null,
                    "platform": null,
                    "fees": 3.56,
                    "transactionFee": {
                        "customFee": 0,
                        "platformFee": 3.56,
                        "customFeeBreakdown": {
                            "TAX": {
                                "itemFee": 0,
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0
                            }
                        },
                        "transactionItemFee": 3.56
                    },
                    "ticketPrice": 22,
                    "isMinPurchaseQuantityEnabled": false,
                    "minPurchaseQuantity": 0,
                    "isMaxPurchaseQuantityEnabled": false,
                    "maxPurchaseQuantity": 0,
                    "isPackSizeEnabled": false,
                    "packSize": null,
                    "image": null
                }
            ],
            "productForm": null
        }
    ],
    "lineup": [],
    "eventProducts": [],
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "duplicateEventId": "{{created_event_id}}",
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
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 700
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 400,
            "color": "#FFFFFF"
        },
        "button": {
            "backgroundColor": "#F6CA7C",
            "color": "#000000",
            "borderColor": "#000000",
            "borderRadius": 12,
            "boxShadow": "none",
            "fontSize": 16,
            "fontWeight": 700
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF",
            "borderColor": "#F6CA7C",
            "borderRadius": 12,
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "borderRadius": 99,
            "color": "#000000 ",
            "borderColor": "#0000",
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "borderRadius": 16,
            "backgroundColor": "#000000",
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#FFFFFF"
            }
        },
        "product": {
            "backgroundColor": "#000000",
            "borderRadius": 8,
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "backgroundColor": "#D32A09",
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        }
    }
}""", app_headers=True, token="token")
    expect(_resp29).json('$.code').equals('200')
    expect(_resp29).json('$.message').equals('success')
    ctx.extract("neweventid", _resp29, "$.data.id")
    ctx.extract("shipping_fee_postsId", _resp29, "$.data.posts[0].id")



    # --- step 30: update the post title to verify-post-shipping-fee (PATCH /post/{{shipping_fee_postsId}}) ---
    _resp30 = ctx.api.admin.post_by_post_id(path_vars={"post_id": vars.get("shipping_fee_postsId", "")}, body="""{
    "urlAlias": "verify-post-shipping-fee",
    "headline": "verify-post-shipping-fee",
    "title": "verify-post-shipping_fee",
    "subTitle": "",
    "links": [],
    "creatorId": "{{user_id}}",
    "baseSold": 0,
    "baseViewed": 0,
    "expiredAt": null,
    "hideInStore": false,
    "checkoutInPost": true,
    "status": "ACTIVE"
}""", app_headers=True, token="admin_token")
    expect(_resp30).json('$.code').equals('200')
    expect(_resp30).json('$.message').equals('success')



    # --- step 31: duplicate event for form (POST /product-event/v2/duplicate) ---
    _resp31 = ctx.api.events.v2_duplicate(body=r"""{
    "title": "event-for-rte-insert-form",
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
    "tickets": [
        {
            "id": "{{ticket_id}}",
            "remote_id": null,
            "platform": "PEAR",
            "createdAt": "2026-04-22T07:08:00.363Z",
            "updatedAt": "2026-04-22T08:09:37.162Z",
            "merchantId": "{{eventcatalog_id}}",
            "title": "General Admission",
            "bodyHtml": "",
            "originalBodyHtml": "",
            "isBodyHtmlOverridden": false,
            "bodyText": "",
            "handle": null,
            "productType": "",
            "publishedAt": "2026-04-22T07:08:00.374Z",
            "publishedScope": "",
            "status": "ACTIVE",
            "externalStatus": "ACTIVE",
            "followExternalStatus": false,
            "tags": [],
            "templateSuffix": null,
            "vendor": "Pear",
            "syncAt": null,
            "deletedAt": null,
            "delisted": false,
            "excludedByImportingTag": false,
            "isFeatured": false,
            "featuredScore": null,
            "inventoryQuantity": 1000,
            "inventoryQuantityOriginal": 1000,
            "soldQuantity": 0,
            "priceDisplay": 25.56,
            "priceDisplayAnchor": 0,
            "priceMin": 25.56,
            "priceMinAnchor": 0,
            "priceMax": 25.56,
            "priceMaxAnchor": 0,
            "priceImportedMin": 0,
            "priceImportedMax": 0,
            "imageCount": 1,
            "isUsed": "NWT",
            "shippingType": "NO_SHIPPING_REQUIRED",
            "additionalShippingFee": 0,
            "deliveryTime": [
                0,
                5
            ],
            "returnPolicyApplied": true,
            "isAvailable": false,
            "commissionRate": 10,
            "textForShare": null,
            "priceSyncImported": false,
            "coverImage": {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                "width": 1000,
                "height": 1000,
                "mediaSrc": null,
                "mediaType": "IMAGE",
                "mediaDuration": 0
            },
            "reviewCount": null,
            "reviewOverallScore": null,
            "reviewAggregate": null,
            "displayReviews": true,
            "links": null,
            "taxEnable": false,
            "taxJarCategory": null,
            "overrideEventTax": false,
            "customTaxRate": null,
            "subscriptionPlanId": null,
            "reviewRedirectProductId": null,
            "reviewSummary": null,
            "customFieldsInfo": null,
            "listingType": "TICKET",
            "extraInfo": {
                "date": "Thu, Apr 17, 2053 (CDT)",
                "event": "verify-co-seller-auto-archive",
                "venue": "Instagram Live, Zoom, In-person",
                "lineup": [],
                "poster": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "status": "COMPLETED",
                "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",
                "eventNote": "linda note",
                "startDate": "2053-04-17T05:00:00.000Z",
                "timeZoneId": "America/Chicago",
                "isAddressHidden": false,
                "addressRevealConfig": null
            },
            "bodyJson": null,
            "shippingOptions": null,
            "shippingNote": null,
            "autoFulfill": true,
            "eventId": "{{created_event_id}}",
            "lifecycleStatus": "LIFECYCLE_STATUS_ARCHIVED",
            "copyFromId": "{{ticket_id}}",
            "stopSellingAfter": null,
            "stopSellingAfterDisplay": null,
            "deliveryMethod": "QR_CODE",
            "thirdPartyDeliveryMessage": null,
            "isMultipleDaysPassEnabled": false,
            "multipleDaysPass": null,
            "isPickupEtaEnabled": null,
            "eventMatchingRules": null,
            "excludeFromPostSync": false,
            "isExpirationEnabled": false,
            "expirationTime": null,
            "expirationTimeDisplay": null,
            "allowAtDoorSales": false,
            "isProductFormEnabled": false,
            "isVariantPriceDisplayEnabled": false,
            "isTipEnabled": false,
            "images": [
                {
                    "id": "b471bc6e-a872-4253-ab7a-41fa0cf51c2d",
                    "remote_id": null,
                    "createdAt": "2026-04-22T07:08:00.377Z",
                    "updatedAt": "2026-04-22T07:08:00.377Z",
                    "height": 1000,
                    "width": 1000,
                    "position": 1,
                    "productId": "{{ticket_id}}",
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "variantIds": [],
                    "mediaType": "IMAGE",
                    "mediaSrc": null,
                    "mediaDuration": 0,
                    "contributedBy": 3,
                    "contributorId": null,
                    "productImageType": "PRODUCT",
                    "source": null
                }
            ],
            "options": [
                {
                    "name": "Title",
                    "images": [
                        {
                            "value": "Default Title",
                            "image": null
                        }
                    ]
                }
            ],
            "variants": [
                {
                    "id": "{{variant_id}}",
                    "remote_id": null,
                    "createdAt": "2026-04-22T07:08:00.377Z",
                    "updatedAt": "2026-04-22T07:08:00.377Z",
                    "compareAtPrice": null,
                    "fulfillmentService": "manual",
                    "grams": 0,
                    "imageId": null,
                    "imageIds": [],
                    "inventoryItemId": null,
                    "inventoryManagement": "Pear",
                    "inventoryPolicy": "DENY",
                    "inventoryQuantity": 1000,
                    "inventoryQuantityOriginal": 1000,
                    "soldQuantity": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "position": 1,
                    "price": "25.56",
                    "priceAnchor": "0",
                    "priceImported": "0.00",
                    "productId": "{{ticket_id}}",
                    "sku": "",
                    "taxCode": null,
                    "taxable": true,
                    "title": "Default Title",
                    "weight": null,
                    "weightUnit": null,
                    "platform": null,
                    "fees": 3.56,
                    "transactionFee": {
                        "customFee": 0,
                        "platformFee": 3.56,
                        "customFeeBreakdown": {
                            "TAX": {
                                "itemFee": 0,
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0
                            }
                        },
                        "transactionItemFee": 3.56
                    },
                    "ticketPrice": 22,
                    "isMinPurchaseQuantityEnabled": false,
                    "minPurchaseQuantity": 0,
                    "isMaxPurchaseQuantityEnabled": false,
                    "maxPurchaseQuantity": 0,
                    "isPackSizeEnabled": false,
                    "packSize": null,
                    "image": null
                }
            ],
            "productForm": null
        }
    ],
    "lineup": [],
    "eventProducts": [],
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "duplicateEventId": "{{created_event_id}}",
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
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 700
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 400,
            "color": "#FFFFFF"
        },
        "button": {
            "backgroundColor": "#F6CA7C",
            "color": "#000000",
            "borderColor": "#000000",
            "borderRadius": 12,
            "boxShadow": "none",
            "fontSize": 16,
            "fontWeight": 700
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF",
            "borderColor": "#F6CA7C",
            "borderRadius": 12,
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "borderRadius": 99,
            "color": "#000000 ",
            "borderColor": "#0000",
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "borderRadius": 16,
            "backgroundColor": "#000000",
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#FFFFFF"
            }
        },
        "product": {
            "backgroundColor": "#000000",
            "borderRadius": 8,
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "backgroundColor": "#D32A09",
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        }
    }
}""", app_headers=True, token="token")
    expect(_resp31).json('$.code').equals('200')
    expect(_resp31).json('$.message').equals('success')
    ctx.extract("post_id", _resp31, "$.data.posts[0].id")
    ctx.extract("createFromEventId", _resp31, "$.data.id")
    ctx.extract("ticketsid", _resp31, "$.data.tickets[0].id")
    ctx.extract("variantsid", _resp31, "$.data.tickets[0].variants[0].id")



    # --- step 32: syncEnabled false form (POST /posts/curator/toggle-sync) ---
    _resp32 = ctx.api.posts.posts_curator_toggle_sync(body="""{
    "syncEnabled": false,
    "postId": "{{post_id}}",
    "eventId": "{{createFromEventId}}",
    "additionalContentPosition": "aboveTickets",
    "dryRun": true
}""", token="token", app_headers=True)
    expect(_resp32).json('$.code').equals('200')
    expect(_resp32).json('$.message').equals('success')



    # --- step 33: update the post auto sync false form (PUT /posts/curator/{{post_id}}) ---
    _resp33 = ctx.api.posts.curator_update(body=r"""{
    "id": "{{post_id}}",
    "announcements": null,
    "createFromEventId": "{{createFromEventId}}",
    "title": "event-for-rte-insert-form",
    "subTitle": "",
    "links": [],
    "allowPromotersResell": true,
    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",
    "financeMode": "FINANCE_MODE_COMMISSION",
    "status": "ACTIVE",
    "allowPromotersHideProducts": true,
    "allowPromotersCustomizeMedia": true,
    "allowPromotersCreateCoupon": true,
    "promotions": [],
    "isPurchaseQuantityLimited": false,
    "purchaseQuantityLimit": 0,
    "isAccessRestricted": false,
    "allowPromotersAccess": false,
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ],
        "fontFamily": "Inter",
        "color": "#FFFFFF",
        "backgroundColor": "#000000",
        "borderColor": "#000000",
        "dividerColor": "#FFFFFF",
        "secondaryTextColor": "#E0E0E0",
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontSize": 24,
            "fontFamily": "Inter",
            "fontWeight": 700
        },
        "columnTitle": {
            "color": "#FFFFFF",
            "fontSize": 20,
            "fontFamily": "Inter",
            "fontWeight": 700
        },
        "subtitle": {
            "color": "#FFFFFF",
            "fontSize": 20,
            "fontFamily": "Inter",
            "fontWeight": 400
        },
        "button": {
            "color": "#000000",
            "fontSize": 16,
            "boxShadow": "none",
            "fontWeight": 700,
            "borderColor": "#000000",
            "borderRadius": 12,
            "backgroundColor": "#F6CA7C"
        },
        "secondaryButton": {
            "color": "#FFFFFF",
            "fontSize": 16,
            "boxShadow": "none",
            "fontWeight": 700,
            "borderColor": "#F6CA7C",
            "borderRadius": 12
        },
        "textButton": {
            "color": "#FFFFFF",
            "fontSize": 16,
            "fontWeight": 700
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "color": "#000000 ",
            "borderColor": "#0000",
            "borderRadius": 99,
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "color": "#FFFFFF",
            "title": {
                "color": "#FFFFFF",
                "fontSize": 14,
                "fontFamily": "Inter",
                "fontWeight": 400
            },
            "borderRadius": 16,
            "backgroundColor": "#000000",
            "secondaryTextColor": "#E0E0E0"
        },
        "product": {
            "color": "#FFFFFF",
            "borderRadius": 8,
            "backgroundColor": "#000000",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF",
            "backgroundColor": "#D32A09"
        },
        "freeShipping": {
            "color": "#268E46",
            "backgroundColor": "#EBF5EF"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "color": "#FFFFFF",
            "title": {
                "color": "#FFFFFF",
                "fontSize": 16,
                "fontFamily": "Inter",
                "fontWeight": 700
            },
            "button": {
                "color": "#000000",
                "backgroundColor": "#F6CA7C"
            },
            "secondaryTextColor": "#E0E0E0"
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        },
        "layout": {
            "pageHeader": {
                "style": "DEDICATED_HEADER_BAR",
                "height": "MEDIUM",
                "displayText": "SHOP_NAME"
            },
            "productBanner": {
                "display": "HIDE",
                "ctaButton": "VIEW_PRODUCT"
            }
        },
        "template": "ClearSky",
        "featuredProduct": {
            "cover": {
                "borderRadius": 0
            }
        }
    },
    "hideInStore": false,
    "recommendationSectionTitle": "",
    "coverImages": [
        {
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "width": 3072,
            "height": 2048,
            "mediaSrc": null,
            "position": 1,
            "mediaType": "IMAGE",
            "mediaDuration": 0
        }
    ],
    "checkoutInPost": true,
    "allowAffiliateSharingOnly": false,
    "abTestingSettings": [],
    "enableAbTesting": false,
    "isOrderConfirmationNoteEnabled": false,
    "hideCouponBox": false,
    "allowCustomizeDisplayPrices": true,
    "customizeDisplayPrices": {
        "price": "Instagram Live, Zoom, In-person | Thu, Apr 17 (CDT)",
        "priceColor": "",
        "titleColor": "",
        "discountPercent": "Get Tickets",
        "discountPercentColor": ""
    },
    "canSetPrice": false,
    "downlineNoteBodyHtml": null,
    "downlineNoteBodyJson": null,
    "featuredSectionTitle": "",
    "enableRedirectUrl": false,
    "redirectUrl": "",
    "redirectDestinationName": "",
    "additionalContentPosition": "aboveTickets",
    "bodyHtml": "",
    "currentDate": "2026-04-23T01:54:37.572Z",
    "relatedProducts": [
        {
            "type": "PRODUCT",
            "merchantProductId": "{{ticketsid}}",
            "isVisible": true,
            "isPurchaseQuantityLimited": false,
            "isRecommendation": false,
            "hasDependentProducts": false,
            "dependentProductIds": [],
            "isFreeShipping": false,
            "isDefaultToSubscription": false,
            "toReplaceMerchantProductIds": null,
            "isCtaCustomized": false,
            "ctaConfig": {
                "type": "BUY_NOW"
            },
            "syncWithCatalogPrice": true,
            "purchaseQuantityLimit": 1,
            "variants": [
                {
                    "wholesalePriceForPromoters": 23,
                    "price": 25.56,
                    "costPrice": 0,
                    "isExcluded": false,
                    "isDefault": false,
                    "priceAnchor": 0,
                    "merchantProductVariantId": "{{variantsid}}",
                    "commissionRateForPromoters": 10
                }
            ]
        }
    ],
    "accessSpecificUser": [],
    "featuredSectionEnable": false,
    "tab": {
        "value": "Content",
        "label": "Content",
        "mappingControl": [
            "media",
            "coverImages",
            "title",
            "headline",
            "urlAlias"
        ]
    },
    "timeKey": 1776909277572,
    "originEnablePaymentRestriction": false,
    "syncEnabled": false,
    "postType": "EVENT",
    "bodyJson": "{\"root\":{\"children\":[{\"id\":\"fc942a8e-eca9-47ee-a19c-53f31f779df8\",\"eventId\":\"{{createFromEventId}}\",\"width\":\"100%\",\"type\":\"event-info-banner\",\"version\":2},{\"id\":\"bd30a550-128e-4507-b685-6cef75868d52\",\"eventId\":\"{{createFromEventId}}\",\"productId\":\"{{ticketsid}}\",\"width\":\"100%\",\"height\":\"\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"thumbnailDisplay\":\"showThumbnail\",\"eventNotesDisplay\":\"showEventNotes\",\"type\":\"ticket-banner\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
    "needRefreshHTML": true,
    "additionalContent": "{}",
    "showAdditionalContent": false,
    "media": [
        {
            "id": "636ef332-537d-4134-90fd-00a11e2e9d9f",
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "selected": true,
            "type": "IMAGE",
            "height": 2048,
            "width": 3072,
            "mediaDuration": 0,
            "mediaSrc": null,
            "mediaType": "IMAGE",
            "inherited": true,
            "position": 1,
            "referenceId": null,
            "source": null,
            "setThumbnail": false
        }
    ],
    "othersCanCopy": false,
    "enableDownlineNote": false,
    "expiredAt": null,
    "urlAlias": "event-for-rte-insert-form",
    "headline": "event-for-rte-insert-form",
    "isPaymentRestrictionEnabled": false
}""", token="token", app_headers=True)
    expect(_resp33).json('$.code').equals('200')
    expect(_resp33).json('$.message').equals('success')



    # --- step 34: duplicate event for auto coupon apply (POST /product-event/v2/duplicate) ---
    _resp34 = ctx.api.events.v2_duplicate(body=r"""{
    "title": "verify auto coupon apply",
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
    "tickets": [
        {
            "id": "{{ticket_id}}",
            "remote_id": null,
            "platform": "PEAR",
            "createdAt": "2026-04-22T07:08:00.363Z",
            "updatedAt": "2026-04-22T08:09:37.162Z",
            "merchantId": "{{eventcatalog_id}}",
            "title": "General Admission",
            "bodyHtml": "",
            "originalBodyHtml": "",
            "isBodyHtmlOverridden": false,
            "bodyText": "",
            "handle": null,
            "productType": "",
            "publishedAt": "2026-04-22T07:08:00.374Z",
            "publishedScope": "",
            "status": "ACTIVE",
            "externalStatus": "ACTIVE",
            "followExternalStatus": false,
            "tags": [],
            "templateSuffix": null,
            "vendor": "Pear",
            "syncAt": null,
            "deletedAt": null,
            "delisted": false,
            "excludedByImportingTag": false,
            "isFeatured": false,
            "featuredScore": null,
            "inventoryQuantity": 1000,
            "inventoryQuantityOriginal": 1000,
            "soldQuantity": 0,
            "priceDisplay": 25.56,
            "priceDisplayAnchor": 0,
            "priceMin": 25.56,
            "priceMinAnchor": 0,
            "priceMax": 25.56,
            "priceMaxAnchor": 0,
            "priceImportedMin": 0,
            "priceImportedMax": 0,
            "imageCount": 1,
            "isUsed": "NWT",
            "shippingType": "NO_SHIPPING_REQUIRED",
            "additionalShippingFee": 0,
            "deliveryTime": [
                0,
                5
            ],
            "returnPolicyApplied": true,
            "isAvailable": false,
            "commissionRate": 10,
            "textForShare": null,
            "priceSyncImported": false,
            "coverImage": {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                "width": 1000,
                "height": 1000,
                "mediaSrc": null,
                "mediaType": "IMAGE",
                "mediaDuration": 0
            },
            "reviewCount": null,
            "reviewOverallScore": null,
            "reviewAggregate": null,
            "displayReviews": true,
            "links": null,
            "taxEnable": false,
            "taxJarCategory": null,
            "overrideEventTax": false,
            "customTaxRate": null,
            "subscriptionPlanId": null,
            "reviewRedirectProductId": null,
            "reviewSummary": null,
            "customFieldsInfo": null,
            "listingType": "TICKET",
            "extraInfo": {
                "date": "Thu, Apr 17, 2053 (CDT)",
                "event": "verify-co-seller-auto-archive",
                "venue": "Instagram Live, Zoom, In-person",
                "lineup": [],
                "poster": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "status": "COMPLETED",
                "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",
                "eventNote": "linda note",
                "startDate": "2053-04-17T05:00:00.000Z",
                "timeZoneId": "America/Chicago",
                "isAddressHidden": false,
                "addressRevealConfig": null
            },
            "bodyJson": null,
            "shippingOptions": null,
            "shippingNote": null,
            "autoFulfill": true,
            "eventId": "{{created_event_id}}",
            "lifecycleStatus": "LIFECYCLE_STATUS_ARCHIVED",
            "copyFromId": "{{ticket_id}}",
            "stopSellingAfter": null,
            "stopSellingAfterDisplay": null,
            "deliveryMethod": "QR_CODE",
            "thirdPartyDeliveryMessage": null,
            "isMultipleDaysPassEnabled": false,
            "multipleDaysPass": null,
            "isPickupEtaEnabled": null,
            "eventMatchingRules": null,
            "excludeFromPostSync": false,
            "isExpirationEnabled": false,
            "expirationTime": null,
            "expirationTimeDisplay": null,
            "allowAtDoorSales": false,
            "isProductFormEnabled": false,
            "isVariantPriceDisplayEnabled": false,
            "isTipEnabled": false,
            "images": [
                {
                    "id": "b471bc6e-a872-4253-ab7a-41fa0cf51c2d",
                    "remote_id": null,
                    "createdAt": "2026-04-22T07:08:00.377Z",
                    "updatedAt": "2026-04-22T07:08:00.377Z",
                    "height": 1000,
                    "width": 1000,
                    "position": 1,
                    "productId": "{{ticket_id}}",
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "variantIds": [],
                    "mediaType": "IMAGE",
                    "mediaSrc": null,
                    "mediaDuration": 0,
                    "contributedBy": 3,
                    "contributorId": null,
                    "productImageType": "PRODUCT",
                    "source": null
                }
            ],
            "options": [
                {
                    "name": "Title",
                    "images": [
                        {
                            "value": "Default Title",
                            "image": null
                        }
                    ]
                }
            ],
            "variants": [
                {
                    "id": "{{variant_id}}",
                    "remote_id": null,
                    "createdAt": "2026-04-22T07:08:00.377Z",
                    "updatedAt": "2026-04-22T07:08:00.377Z",
                    "compareAtPrice": null,
                    "fulfillmentService": "manual",
                    "grams": 0,
                    "imageId": null,
                    "imageIds": [],
                    "inventoryItemId": null,
                    "inventoryManagement": "Pear",
                    "inventoryPolicy": "DENY",
                    "inventoryQuantity": 1000,
                    "inventoryQuantityOriginal": 1000,
                    "soldQuantity": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "position": 1,
                    "price": "25.56",
                    "priceAnchor": "0",
                    "priceImported": "0.00",
                    "productId": "{{ticket_id}}",
                    "sku": "",
                    "taxCode": null,
                    "taxable": true,
                    "title": "Default Title",
                    "weight": null,
                    "weightUnit": null,
                    "platform": null,
                    "fees": 3.56,
                    "transactionFee": {
                        "customFee": 0,
                        "platformFee": 3.56,
                        "customFeeBreakdown": {
                            "TAX": {
                                "itemFee": 0,
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0
                            }
                        },
                        "transactionItemFee": 3.56
                    },
                    "ticketPrice": 22,
                    "isMinPurchaseQuantityEnabled": false,
                    "minPurchaseQuantity": 0,
                    "isMaxPurchaseQuantityEnabled": false,
                    "maxPurchaseQuantity": 0,
                    "isPackSizeEnabled": false,
                    "packSize": null,
                    "image": null
                }
            ],
            "productForm": null
        }
    ],
    "lineup": [],
    "eventProducts": [],
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "duplicateEventId": "{{created_event_id}}",
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
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 700
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 400,
            "color": "#FFFFFF"
        },
        "button": {
            "backgroundColor": "#F6CA7C",
            "color": "#000000",
            "borderColor": "#000000",
            "borderRadius": 12,
            "boxShadow": "none",
            "fontSize": 16,
            "fontWeight": 700
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF",
            "borderColor": "#F6CA7C",
            "borderRadius": 12,
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "borderRadius": 99,
            "color": "#000000 ",
            "borderColor": "#0000",
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "borderRadius": 16,
            "backgroundColor": "#000000",
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#FFFFFF"
            }
        },
        "product": {
            "backgroundColor": "#000000",
            "borderRadius": 8,
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "backgroundColor": "#D32A09",
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        }
    }
}""", app_headers=True, token="token")
    expect(_resp34).json('$.code').equals('200')
    expect(_resp34).json('$.message').equals('success')
    ctx.extract("post_id", _resp34, "$.data.posts[0].id")
    ctx.extract("createFromEventId", _resp34, "$.data.id")
    ctx.extract("ticketsid", _resp34, "$.data.tickets[0].id")
    ctx.extract("variantsid", _resp34, "$.data.tickets[0].variants[0].id")
    ctx.extract("neweventid", _resp34, "$.data.id")
    ctx.extract("auto_coupon_postsId", _resp34, "$.data.posts[0].id")
    expect(_resp34).json('$.data.posts').is_array()
    expect(_resp34).json('$.data.posts').is_not_empty()
    expect(_resp34).json('$.data.tickets').is_array()
    expect(_resp34).json('$.data.tickets').is_not_empty()
    expect(_resp34).json('$.data.tickets[0].variants').is_array()
    expect(_resp34).json('$.data.tickets[0].variants').is_not_empty()



    # --- step 35: update the post title to verify-post-auto-coupon (PATCH /post/{{auto_coupon_postsId}}) ---
    _resp35 = ctx.api.admin.post_by_post_id(path_vars={"post_id": "{{auto_coupon_postsId}}"}, body="""{
    "urlAlias": "verify-auto-coupon-apply",
    "headline": "verify auto coupon apply",
    "title": "verify auto coupon apply",
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
    expect(_resp35).json('$.code').equals('200')
    expect(_resp35).json('$.message').equals('success')



    # --- step 36: duplicate event for demi (POST /product-event/v2/duplicate) ---
    _resp36 = ctx.api.events.v2_duplicate(body=r"""{
    "title": "test event with two tickets",
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
    "tickets": [
        {
            "id": "{{ticket_id}}",
            "remote_id": null,
            "platform": "PEAR",
            "createdAt": "2026-04-22T07:08:00.363Z",
            "updatedAt": "2026-04-22T08:09:37.162Z",
            "merchantId": "{{eventcatalog_id}}",
            "title": "General Admission",
            "bodyHtml": "",
            "originalBodyHtml": "",
            "isBodyHtmlOverridden": false,
            "bodyText": "",
            "handle": null,
            "productType": "",
            "publishedAt": "2026-04-22T07:08:00.374Z",
            "publishedScope": "",
            "status": "ACTIVE",
            "externalStatus": "ACTIVE",
            "followExternalStatus": false,
            "tags": [],
            "templateSuffix": null,
            "vendor": "Pear",
            "syncAt": null,
            "deletedAt": null,
            "delisted": false,
            "excludedByImportingTag": false,
            "isFeatured": false,
            "featuredScore": null,
            "inventoryQuantity": 1000,
            "inventoryQuantityOriginal": 1000,
            "soldQuantity": 0,
            "priceDisplay": 25.56,
            "priceDisplayAnchor": 0,
            "priceMin": 25.56,
            "priceMinAnchor": 0,
            "priceMax": 25.56,
            "priceMaxAnchor": 0,
            "priceImportedMin": 0,
            "priceImportedMax": 0,
            "imageCount": 1,
            "isUsed": "NWT",
            "shippingType": "NO_SHIPPING_REQUIRED",
            "additionalShippingFee": 0,
            "deliveryTime": [
                0,
                5
            ],
            "returnPolicyApplied": true,
            "isAvailable": false,
            "commissionRate": 10,
            "textForShare": null,
            "priceSyncImported": false,
            "coverImage": {
                "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                "width": 1000,
                "height": 1000,
                "mediaSrc": null,
                "mediaType": "IMAGE",
                "mediaDuration": 0
            },
            "reviewCount": null,
            "reviewOverallScore": null,
            "reviewAggregate": null,
            "displayReviews": true,
            "links": null,
            "taxEnable": false,
            "taxJarCategory": null,
            "overrideEventTax": false,
            "customTaxRate": null,
            "subscriptionPlanId": null,
            "reviewRedirectProductId": null,
            "reviewSummary": null,
            "customFieldsInfo": null,
            "listingType": "TICKET",
            "extraInfo": {
                "date": "Thu, Apr 17, 2053 (CDT)",
                "event": "verify-co-seller-auto-archive",
                "venue": "Instagram Live, Zoom, In-person",
                "lineup": [],
                "poster": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "status": "COMPLETED",
                "location": "789 River East Art Center Promenade, Chicago, Illinois, USA",
                "eventNote": "linda note",
                "startDate": "2053-04-17T05:00:00.000Z",
                "timeZoneId": "America/Chicago",
                "isAddressHidden": false,
                "addressRevealConfig": null
            },
            "bodyJson": null,
            "shippingOptions": null,
            "shippingNote": null,
            "autoFulfill": true,
            "eventId": "{{created_event_id}}",
            "lifecycleStatus": "LIFECYCLE_STATUS_ARCHIVED",
            "copyFromId": "{{ticket_id}}",
            "stopSellingAfter": null,
            "stopSellingAfterDisplay": null,
            "deliveryMethod": "QR_CODE",
            "thirdPartyDeliveryMessage": null,
            "isMultipleDaysPassEnabled": false,
            "multipleDaysPass": null,
            "isPickupEtaEnabled": null,
            "eventMatchingRules": null,
            "excludeFromPostSync": false,
            "isExpirationEnabled": false,
            "expirationTime": null,
            "expirationTimeDisplay": null,
            "allowAtDoorSales": false,
            "isProductFormEnabled": false,
            "isVariantPriceDisplayEnabled": false,
            "isTipEnabled": false,
            "images": [
                {
                    "id": "b471bc6e-a872-4253-ab7a-41fa0cf51c2d",
                    "remote_id": null,
                    "createdAt": "2026-04-22T07:08:00.377Z",
                    "updatedAt": "2026-04-22T07:08:00.377Z",
                    "height": 1000,
                    "width": 1000,
                    "position": 1,
                    "productId": "{{ticket_id}}",
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "variantIds": [],
                    "mediaType": "IMAGE",
                    "mediaSrc": null,
                    "mediaDuration": 0,
                    "contributedBy": 3,
                    "contributorId": null,
                    "productImageType": "PRODUCT",
                    "source": null
                }
            ],
            "options": [
                {
                    "name": "Title",
                    "images": [
                        {
                            "value": "Default Title",
                            "image": null
                        }
                    ]
                }
            ],
            "variants": [
                {
                    "id": "{{variant_id}}",
                    "remote_id": null,
                    "createdAt": "2026-04-22T07:08:00.377Z",
                    "updatedAt": "2026-04-22T07:08:00.377Z",
                    "compareAtPrice": null,
                    "fulfillmentService": "manual",
                    "grams": 0,
                    "imageId": null,
                    "imageIds": [],
                    "inventoryItemId": null,
                    "inventoryManagement": "Pear",
                    "inventoryPolicy": "DENY",
                    "inventoryQuantity": 1000,
                    "inventoryQuantityOriginal": 1000,
                    "soldQuantity": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "position": 1,
                    "price": "25.56",
                    "priceAnchor": "0",
                    "priceImported": "0.00",
                    "productId": "{{ticket_id}}",
                    "sku": "",
                    "taxCode": null,
                    "taxable": true,
                    "title": "Default Title",
                    "weight": null,
                    "weightUnit": null,
                    "platform": null,
                    "fees": 3.56,
                    "transactionFee": {
                        "customFee": 0,
                        "platformFee": 3.56,
                        "customFeeBreakdown": {
                            "TAX": {
                                "itemFee": 0,
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0
                            }
                        },
                        "transactionItemFee": 3.56
                    },
                    "ticketPrice": 22,
                    "isMinPurchaseQuantityEnabled": false,
                    "minPurchaseQuantity": 0,
                    "isMaxPurchaseQuantityEnabled": false,
                    "maxPurchaseQuantity": 0,
                    "isPackSizeEnabled": false,
                    "packSize": null,
                    "image": null
                }
            ],
            "productForm": null
        }
    ],
    "lineup": [],
    "eventProducts": [],
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "duplicateEventId": "{{created_event_id}}",
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
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 700
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 400,
            "color": "#FFFFFF"
        },
        "button": {
            "backgroundColor": "#F6CA7C",
            "color": "#000000",
            "borderColor": "#000000",
            "borderRadius": 12,
            "boxShadow": "none",
            "fontSize": 16,
            "fontWeight": 700
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF",
            "borderColor": "#F6CA7C",
            "borderRadius": 12,
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "borderRadius": 99,
            "color": "#000000 ",
            "borderColor": "#0000",
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "borderRadius": 16,
            "backgroundColor": "#000000",
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#FFFFFF"
            }
        },
        "product": {
            "backgroundColor": "#000000",
            "borderRadius": 8,
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "backgroundColor": "#D32A09",
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        }
    }
}""", app_headers=True, token="token")
    expect(_resp36).json('$.code').equals('200')
    expect(_resp36).json('$.message').equals('success')
    ctx.extract("post_id", _resp36, "$.data.posts[0].id")
    ctx.extract("createFromEventId", _resp36, "$.data.id")
    ctx.extract("ticketsid", _resp36, "$.data.tickets[0].id")
    ctx.extract("variantsid", _resp36, "$.data.tickets[0].variants[0].id")
    ctx.extract("neweventid", _resp36, "$.data.id")
    ctx.extract("two_tickets_postsid", _resp36, "$.data.posts[0].id")
    expect(_resp36).json('$.data.posts').is_array()
    expect(_resp36).json('$.data.posts').is_not_empty()
    expect(_resp36).json('$.data.tickets').is_array()
    expect(_resp36).json('$.data.tickets').is_not_empty()
    expect(_resp36).json('$.data.tickets[0].variants').is_array()
    expect(_resp36).json('$.data.tickets[0].variants').is_not_empty()



    # --- step 37: update the post title to verify post with two tickets (PATCH /post/{{two_tickets_postsid}}) ---
    _resp37 = ctx.api.admin.post_by_post_id(path_vars={"post_id": "{{two_tickets_postsid}}"}, body="""{
    "urlAlias": "test-event-with-two-tickets",
    "headline": "test event with two tickets",
    "title": "test event with two tickets",
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
    expect(_resp37).json('$.code').equals('200')
    expect(_resp37).json('$.message').equals('success')



    # --- step 38: enable co-selling-defaults (PATCH /catalog/event/co-selling-defaults) ---
    _resp38 = ctx.api.events.event_co_selling_defaults(body="""{
    "commissionRate": 0,
    "enableEventCoSellingCommission": true
}""", token="token", app_headers=True)
    expect(_resp38).json('$.code').equals('200')
    expect(_resp38).json('$.message').equals('success')



    # --- step 39: update the ticket price to 0 (PUT /v2/products/{{ticketsid}}) ---
    _resp39 = ctx.api.products.update_v2(path_vars={"ticket_id": "{{ticketsid}}"}, body=r"""{
    "id": "{{ticketsid}}",
    "remote_id": null,
    "platform": "PEAR",
    "createdAt": "2026-04-23T08:30:45.619Z",
    "updatedAt": "2026-04-23T08:30:45.632Z",
    "merchantId": "82b25033-61c9-4498-88ac-ca6c03731c4b",
    "title": "General Admission 001",
    "bodyHtml": "<p class=\"katana__paragraph katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "originalBodyHtml": "",
    "isBodyHtmlOverridden": false,
    "bodyText": "",
    "handle": null,
    "productType": "",
    "publishedAt": "2026-04-23T08:30:45.628Z",
    "publishedScope": "",
    "status": "ACTIVE",
    "externalStatus": "ACTIVE",
    "followExternalStatus": false,
    "tags": [],
    "templateSuffix": null,
    "vendor": "Pear",
    "syncAt": null,
    "deletedAt": null,
    "delisted": false,
    "excludedByImportingTag": false,
    "isFeatured": false,
    "featuredScore": null,
    "inventoryQuantity": 1000,
    "inventoryQuantityOriginal": 1000,
    "soldQuantity": 0,
    "priceDisplay": 25.56,
    "priceDisplayAnchor": 0,
    "priceMin": 25.56,
    "priceMinAnchor": 0,
    "priceMax": 25.56,
    "priceMaxAnchor": 0,
    "priceImportedMin": 0,
    "priceImportedMax": 0,
    "imageCount": 1,
    "isUsed": "NWT",
    "shippingType": "NO_SHIPPING_REQUIRED",
    "additionalShippingFee": 0,
    "deliveryTime": [
        0,
        5
    ],
    "returnPolicyApplied": true,
    "isAvailable": true,
    "commissionRate": 10,
    "textForShare": null,
    "priceSyncImported": false,
    "coverImage": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
        "width": 1000,
        "height": 1000,
        "mediaSrc": null,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
    "reviewCount": null,
    "reviewOverallScore": null,
    "reviewAggregate": null,
    "displayReviews": true,
    "links": null,
    "taxEnable": false,
    "taxJarCategory": "",
    "customTaxRate": null,
    "subscriptionPlanId": null,
    "reviewRedirectProductId": null,
    "reviewSummary": null,
    "customFieldsInfo": null,
    "listingType": "TICKET",
    "shippingOptions": [],
    "shippingNote": null,
    "autoFulfill": true,
    "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",
    "copyFromId": "{{createFromEventId}}",
    "stopSellingAfter": null,
    "deliveryMethod": "QR_CODE",
    "thirdPartyDeliveryMessage": "",
    "isMultipleDaysPassEnabled": false,
    "multipleDaysPass": null,
    "isPickupEtaEnabled": null,
    "eventMatchingRules": null,
    "excludeFromPostSync": false,
    "expirationTime": null,
    "allowAtDoorSales": false,
    "isTipEnabled": false,
    "options": [
        {
            "remote_id": null,
            "productId": "{{ticketsid}}",
            "name": "Title",
            "position": 1,
            "values": [
                "Default Title"
            ],
            "images": [
                {
                    "value": "Default Title",
                    "imageId": null
                }
            ]
        }
    ],
    "variants": [
        {
            "id": "{{variantsid}}",
            "remote_id": null,
            "createdAt": "2026-04-23T08:30:45.632Z",
            "updatedAt": "2026-04-23T08:30:45.632Z",
            "compareAtPrice": null,
            "fulfillmentService": "manual",
            "grams": 0,
            "imageIds": [],
            "inventoryItemId": null,
            "inventoryManagement": "Pear",
            "inventoryPolicy": "DENY",
            "inventoryQuantity": 1000,
            "inventoryQuantityOriginal": 1000,
            "soldQuantity": 0,
            "option": {
                "option1": "Default Title"
            },
            "position": 1,
            "price": "0",
            "priceAnchor": "0",
            "priceImported": "0.00",
            "productId": "{{ticketsid}}",
            "sku": "",
            "taxCode": null,
            "taxable": true,
            "title": "Default Title",
            "weight": null,
            "weightUnit": null,
            "platform": null,
            "fees": 0,
            "transactionFee": {
                "platformFee": 0,
                "customFee": 0,
                "customFeeBreakdown": {},
                "transactionItemFee": 0
            },
            "ticketPrice": "0",
            "isMinPurchaseQuantityEnabled": false,
            "minPurchaseQuantity": null,
            "isMaxPurchaseQuantityEnabled": false,
            "maxPurchaseQuantity": null,
            "isPackSizeEnabled": false,
            "packSize": null
        }
    ],
    "catalogCommissionRate": 0,
    "earliestTime": "2026-04-23T08:30:45.619Z",
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "isProductFormEnabled": false,
    "isVariantPriceDisplayEnabled": false,
    "stopSellingAfterDisplay": "",
    "overrideEventTax": false,
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "images": [
        {
            "id": "fb2c0429-d3b7-4c82-b0e2-39a541cda1e6",
            "remote_id": null,
            "createdAt": "2026-04-23T08:30:45.632Z",
            "updatedAt": "2026-04-23T08:30:45.632Z",
            "height": 1000,
            "width": 1000,
            "position": 1,
            "productId": "{{ticketsid}}",
            "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
            "variantIds": [],
            "mediaType": "IMAGE",
            "mediaSrc": null,
            "mediaDuration": 0,
            "contributedBy": 3,
            "contributorId": null,
            "productImageType": "PRODUCT",
            "source": null
        }
    ],
    "eventId": "{{createFromEventId}}",
    "isExpirationEnabled": false
}""", token="token", app_headers=True)
    expect(_resp39).json('$.code').equals('200')
    expect(_resp39).json('$.message').equals('success')



    # --- step 40: Add ticket 002 (POST /v2/products) ---
    _resp40 = ctx.api.products.create_v2(body=r"""{
    "merchantId": "{{eventcatalog_id}}",
    "shippingType": "NO_SHIPPING_REQUIRED",
    "isFeatured": false,
    "commissionRate": 0,
    "priceSyncImported": false,
    "additionalShippingFee": 0,
    "returnPolicyApplied": true,
    "title": "General Admission 002",
    "bodyHtml": "<p class=\"katana__paragraph katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "status": "ACTIVE",
    "isUsed": "NWT",
    "taxJarCategory": "",
    "platform": "PEAR",
    "autoFulfill": true,
    "options": [
        {
            "name": "Title",
            "values": [
                "Default Title"
            ],
            "images": []
        }
    ],
    "variants": [
        {
            "inventoryQuantity": 10000,
            "price": "0",
            "priceAnchor": 0,
            "option": {
                "option1": "Default Title"
            },
            "ticketPrice": "0",
            "fees": 0,
            "transactionFee": {
                "platformFee": 0,
                "customFee": 0,
                "customFeeBreakdown": {},
                "transactionItemFee": 0
            }
        }
    ],
    "listingType": "TICKET",
    "excludeFromPostSync": false,
    "isTipEnabled": false,
    "catalogCommissionRate": 0,
    "shippingOptions": [],
    "deliveryMethod": "QR_CODE",
    "thirdPartyDeliveryMessage": "",
    "taxEnable": false,
    "customTaxRate": null,
    "earliestTime": "2026-04-23T08:35:58.929Z",
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "isVariantPriceDisplayEnabled": false,
    "stopSellingAfterDisplay": "",
    "extraInfo": {
        "businessTimezone": "America/Los_Angeles"
    },
    "overrideEventTax": false,
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "images": [
        {
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "width": 3072,
            "height": 2048,
            "position": 1,
            "mediaType": "IMAGE",
            "mediaDuration": 0,
            "source": "EVENT",
            "setThumbnail": true,
            "origin": {
                "id": "defaultEventMediaId",
                "width": 3072,
                "height": 2048,
                "position": 1
            },
            "productImageType": "PRODUCT"
        }
    ],
    "eventId": "{{createFromEventId}}",
    "isExpirationEnabled": false
}""", app_headers=True, token="token")
    expect(_resp40).json('$.code').equals('200')
    expect(_resp40).json('$.message').equals('success')



    # --- step 41: Partner999 sync the post to the coseller's 997 shop (POST /posts/curator/{{post0_id}}/promoters/sync) ---
    _resp41 = ctx.api.posts.curator_sync_promoters(path_vars={"post0_id": vars.get("post0_id", "")}, body="""{
    "postId": "{{post0_id}}",
    "promoterIds": [
        "{{user_partner997_id}}"
    ]
}""", app_headers=True, token="token")
    expect(_resp41).json('$.code').equals('200')
    expect(_resp41).json('$.message').equals('success')



    # --- step 42: Partner 997 login (POST /auth/sign-in) ---
    _resp42 = ctx.api.auth.sign_in(body="""{
    "email": "{{UIauto_partner997_email}}",
    "password": "{{password}}"

}""", app_headers=True, token="token")
    expect(_resp42).json('$.code').equals('200')
    expect(_resp42).json('$.message').equals('success')
    ctx.extract("partner997_auth_token", _resp42, "$.data.token")



    # --- step 43: update the partner997's store shop url to autoshop (PUT /store-front) ---
    _resp43 = ctx.api.storefront.update(body="""{
    "userInfo": {
        "storeName": "{{partner997_storeName}}",
        "logo": null,
        "backgroundSource": {
            "width": 375,
            "height": 375,
            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1764821680/setting/wrbmwobccxtbsy1e79h0.webp"
        },
        "description": "",
        "subTitle": "",
        "socialMedias": [],
        "storeFront": {
            "storeTabs": [
                {
                    "name": "Posts",
                    "checked": false
                },
                {
                    "name": "Links",
                    "checked": false
                },
                {
                    "name": "Products",
                    "checked": false
                },
                {
                    "name": "Forms",
                    "checked": false
                }
            ]
        },
        "vanityUrl": "{{partner997_vanityUrl}}"
    }
}""", app_headers=True, token="partner997_auth_token")
    expect(_resp43).json('$.code').equals('200')
    expect(_resp43).json('$.message').equals('success')



    # --- step 44: Partner997 create expired module (POST /store-front/module) ---
    _resp44 = ctx.api.storefront.module(body="""{
    "type": "POST",
    "direction": "VERTICAL",
    "title": "Expired events",
    "linkType": null,
    "visible": true
}""", app_headers=True, token="partner997_auth_token")
    expect(_resp44).json('$.code').equals('200')
    expect(_resp44).json('$.message').equals('success')
    ctx.extract("cosellermodule_id", _resp44, "$.data.id")
    expect(_resp44).status().is_(201)
    expect(_resp44).json('$.data.id').is_string()
    expect(_resp44).json('$.data.id').is_not_empty()
    expect(_resp44).json('$.data.type').equals('POST')
    expect(_resp44).json('$.data.visible').equals(True)



    # --- step 45: get the coseller's resell post id (GET /post/{{post0_id}}/children) ---
    _resp45 = ctx.api.admin.post_children(params={"pageNumber": "1", "pageSize": "20", "includeFinancialInfo": "false"}, path_vars={"post_id": "{{post0_id}}"}, token="admin_token", app_headers=True)
    expect(_resp45).json('$.code').equals('200')
    expect(_resp45).json('$.message').equals('success')
    ctx.extract("cosellpost_id", _resp45, "$.data.items[0].id")
    expect(_resp45).json('$.data.items[0].id').is_string()
    expect(_resp45).json('$.data.items[0].id').is_not_empty()



    # --- step 46: get the event post id (GET /posts/curator/event/{{created_event_id}}/posts) ---
    _resp46 = ctx.api.posts.curator_event_posts(path_vars={"event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    expect(_resp46).json('$.code').equals('200')
    expect(_resp46).json('$.message').equals('success')
    ctx.extract("post0_id", _resp46, "$.data.items[0].id")
    expect(_resp46).json('$.data.items[0].id').is_string()
    expect(_resp46).json('$.data.items[0].id').is_not_empty()



    # --- step 47: Add the coseller997's post to the module (PUT /store-front/module-item/{{cosellermodule_id}}) ---
    _resp47 = ctx.api.storefront.update_module_item(path_vars={"module_item_id": "{{cosellermodule_id}}"}, body="""{
    "id": "{{module_id}}",
    "items": [
        {
            "itemId": "{{cosellpost_id}}",
            "position": 1
        }
    ]
}""", token="partner997_auth_token", app_headers=True)
    expect(_resp47).json('$.code').equals('200')
    expect(_resp47).json('$.message').equals('success')
    expect(_resp47).status().is_(200)
    expect(_resp47).json('$.data.title').equals('Expired events')
    expect(_resp47).json('$.data.type').equals('POST')
    expect(_resp47).json('$.data.items[0]').is_object()
    expect(_resp47).json('$.data.items[0].postType').equals('EVENT')
    expect(_resp47).json('$.data.items[0].status').equals('ACTIVE')
    expect(_resp47).json('$.data.items[0].event.status').equals('UPCOMING')
    expect(_resp47).json('$.data.items[0].id').is_string()
    expect(_resp47).json('$.data.items[0].id').is_not_empty()
    expect(_resp47).json('$.data.items[0].event.status').equals('UPCOMING')



    # --- step 48: Partner Create event T1742 (POST /product-event/v2) ---
    _resp48 = ctx.api.events.create_v2(body=r"""{
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "isTimeUnspecified": false,
    "allowAutoComplete": true,
    "description": "",
    "note": "auto test",
    "location": "Test venue · West Mound Street, Columbus, OH",
    "status": "UPCOMING",
    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "isTaxEnabled": false,
    "isAddressRevealEnabled": false,
    "title": "Auto-Test-post-setting",
    "venue": "Test venue · West Mound Street, Columbus, OH",
    "timezone": {
        "timeZoneId": "America/New_York",
        "timeZoneName": "Eastern Daylight Time",
        "dstOffset": 3600,
        "rawOffset": -18000
    },
    "poster": {
        "height": 2048,
        "width": 3072,
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "mediaType": "IMAGE"
    },
    "startDateDisplay": "2032-04-24",
    "styleSettings": {
        "fontFamily": "Inter",
        "color": "#FFFFFF",
        "backgroundColor": "#000000",
        "borderColor": "#000000",
        "dividerColor": "#FFFFFF",
        "secondaryTextColor": "#E0E0E0",
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 700
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 400,
            "color": "#FFFFFF"
        },
        "button": {
            "backgroundColor": "#F6CA7C",
            "color": "#000000",
            "borderColor": "#000000",
            "borderRadius": 12,
            "boxShadow": "none",
            "fontSize": 16,
            "fontWeight": 700
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF",
            "borderColor": "#F6CA7C",
            "borderRadius": 12,
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "borderRadius": 99,
            "color": "#000000 ",
            "borderColor": "#0000",
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "borderRadius": 16,
            "backgroundColor": "#000000",
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#FFFFFF"
            }
        },
        "product": {
            "backgroundColor": "#000000",
            "borderRadius": 8,
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "backgroundColor": "#D32A09",
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        }
    }
}""", app_headers=True, token="token")
    expect(_resp48).json('$.code').equals('200')
    expect(_resp48).json('$.message').equals('success')
    ctx.extract("created_event_id", _resp48, "$.data.id")
    expect(_resp48).status().is_(201)
    expect(_resp48).json('$.data').exists()
    expect(_resp48).json('$.data.id').exists()



    # --- step 49: Partner Create event media next step T1742  (POST /product-event/v2/{{created_event_id}}/media/batch/create) ---
    _resp49 = ctx.api.events.media_batch_create(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
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
    "medias": [],
    "mediaTextConfig": {
        "headline": "Missed our last event?",
        "subtitle": "Here's a lil recap of our last event👇",
        "align": "center"
    }
}""", app_headers=True, token="token")
    expect(_resp49).json('$.code').equals('200')
    expect(_resp49).json('$.message').equals('success')



    # --- step 50: Partner Create event ticket next step T1742 (POST /product-event/v2/{{created_event_id}}/ticket/batch/v2) ---
    _resp50 = ctx.api.events.ticket_batch_v2(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
    "listingType": "TICKET",
    "isTaxEnabled": false,
    "autoReplace": false,
    "tickets": [
        {
            "listingType": "TICKET",
            "ticketType": "TICKET_TYPE_STANDARD",
            "images": [
                {
                    "id": "80f43627-4bef-49b0-934b-cd63d49f8787",
                    "height": 1000,
                    "width": 1000,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "mediaType": "IMAGE"
                }
            ],
            "title": "General Admission 02",
            "bodyJson": "",
            "options": [
                {
                    "name": "Title",
                    "values": [
                        "Default Title"
                    ],
                    "images": []
                }
            ],
            "variants": [
                {
                    "inventoryQuantity": 10000,
                    "ticketPrice": 100,
                    "price": 112.22,
                    "fees": 12.22,
                    "priceAnchor": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "transactionFee": {
                        "platformFee": 12.22,
                        "customFee": 0,
                        "customFeeBreakdown": {
                            "TAX": {
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0,
                                "itemFee": 0
                            }
                        },
                        "transactionItemFee": 12.22
                    }
                }
            ]
        },
        {
            "listingType": "TICKET",
            "ticketType": "TICKET_TYPE_STANDARD",
            "images": [
                {
                    "id": "80f43627-4bef-49b0-934b-cd63d49f8787",
                    "height": 1000,
                    "width": 1000,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "mediaType": "IMAGE"
                }
            ],
            "title": "General Admission 01",
            "bodyJson": "",
            "options": [
                {
                    "name": "Title",
                    "values": [
                        "Default Title"
                    ],
                    "images": []
                }
            ],
            "variants": [
                {
                    "inventoryQuantity": 10000,
                    "ticketPrice": 60,
                    "price": 67.77,
                    "fees": 7.77,
                    "priceAnchor": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "transactionFee": {
                        "platformFee": 7.77,
                        "customFee": 0,
                        "customFeeBreakdown": {
                            "TAX": {
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0,
                                "itemFee": 0
                            }
                        },
                        "transactionItemFee": 7.77
                    }
                }
            ]
        },
        {
            "listingType": "TICKET",
            "ticketType": "TICKET_TYPE_STANDARD",
            "images": [
                {
                    "id": "80f43627-4bef-49b0-934b-cd63d49f8787",
                    "height": 1000,
                    "width": 1000,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "mediaType": "IMAGE"
                }
            ],
            "title": "General Admission",
            "bodyJson": "",
            "options": [
                {
                    "name": "Title",
                    "values": [
                        "Default Title"
                    ],
                    "images": []
                }
            ],
            "variants": [
                {
                    "inventoryQuantity": 10000,
                    "ticketPrice": 82,
                    "price": 92.22,
                    "fees": 10.22,
                    "priceAnchor": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "transactionFee": {
                        "platformFee": 10.22,
                        "customFee": 0,
                        "customFeeBreakdown": {
                            "TAX": {
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0,
                                "itemFee": 0
                            }
                        },
                        "transactionItemFee": 10.22
                    }
                }
            ]
        }
    ],
    "coSellingCommissionRate": 7
}
""", app_headers=True, token="token")
    expect(_resp50).json('$.code').equals('200')
    expect(_resp50).json('$.message').equals('success')
    # 原 Apifox 在该请求的 test script 里按 ticket.title 匹配写入 3 组变量
    # （ticket_id_* / variant_id_* / productId_*）。迁移只实现了 variant_id_*，
    # 另两组被误标成「由 step 106/107 的循环写入」——但 step 106 的**请求体自身**
    # 就引用了 tickets[].id / tickets[].copyFromId = {{ticket_id_General_Admission*}}，
    # 用「step 106 的响应」当来源是自引用死局（响应还没产生就要求值），
    # 因此这里必须按原始脚本补齐 ticket_id_*（来源=本次 ticket/batch 响应里对应 title 的票）。
    for _t50_title, _t50_sfx in (
        ("General Admission 02", "_General_Admission_02"),
        ("General Admission 01", "_General_Admission_01"),
        ("General Admission", "_General_Admission"),
    ):
        ctx.extract("variant_id" + _t50_sfx, _resp50,
                    '$.data.tickets[?(@.title=="%s")].variants[0].id' % _t50_title)
        ctx.extract("ticket_id" + _t50_sfx, _resp50,
                    '$.data.tickets[?(@.title=="%s")].id' % _t50_title)



    # --- step 51: Partner Create event lineup next step  T1742 (POST /product-event/v2/{{created_event_id}}/lineup/batch) ---
    _resp51 = ctx.api.events.lineup_batch(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{"lineup":[]}""", app_headers=True, token="token")
    expect(_resp51).json('$.code').equals('200')
    expect(_resp51).json('$.message').equals('success')



    # --- step 52: Partner Check event details T1742 (GET /product-event/v2/{{created_event_id}}/config) ---
    _resp52 = ctx.api.events.v2_config(params={"keyword": "", "pageSize": "30", "pageNumber": "1"}, token="token", app_headers=True)
    expect(_resp52).json('$.code').equals('200')
    expect(_resp52).json('$.message').equals('success')
    expect(_resp52).json('$.data.title').equals('Auto-Test-post-setting')



    # --- step 53: get the event post id (GET /posts/curator/event/{{created_event_id}}/posts) ---
    _resp53 = ctx.api.posts.curator_event_posts(path_vars={"event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    expect(_resp53).json('$.code').equals('200')
    expect(_resp53).json('$.message').equals('success')
    ctx.extract("post0_id", _resp53, "$.data.items[0].id")
    expect(_resp53).json('$.data.items[0].id').is_string()
    expect(_resp53).json('$.data.items[0].id').is_not_empty()



    # --- step 54: Admin update the partner's the t1742 post  url (PATCH /post/{{post0_id}}) ---
    _resp54 = ctx.api.admin.post_by_post_id(path_vars={"post_id": vars.get("post0_id", "")}, body="""{
    "urlAlias": "auto-test-post-setting-t1742",
    "headline": "Auto-Test-post-setting ",
    "title": "Auto-Test-post-setting ",
    "subTitle": "",
    "links": [],
    "creatorId": "{{user_id}}",
    "baseSold": 0,
    "baseViewed": 0,
    "expiredAt": null,
    "hideInStore": false,
    "checkoutInPost": true,
    "status": "ACTIVE"
}""", app_headers=True, token="admin_token")
    expect(_resp54).json('$.code').equals('200')
    expect(_resp54).json('$.message').equals('success')
    expect(_resp54).status().is_one_of([200,201])
    # 注：常量 expectedAlias
    expect(_resp54).json('$.data.post.urlAlias').equals('auto-test-post-setting-t1742')
    expect(_resp54).json('$.data.post.status').equals('ACTIVE')



    # --- step 55: Get the Upcoming Events sections id (GET store-front/shop/autotestshop) ---
    _resp55 = ctx.api.storefront.shop(path_vars={"partner_vanityUrl": 'autotestshop'}, params={"public": "false"}, token="token", app_headers=True)
    expect(_resp55).json('$.code').equals('200')
    expect(_resp55).json('$.message').equals('success')
    ctx.extract("section", _resp55, '$.data.shopModules[?(@.title=="Upcoming Events")].id')


    # --- step 56: Add to the post to module to add to shop (POST store-front/add-items-to-modules) ---
    _resp56 = ctx.api.storefront.add_items_to_modules(body="""{
    "items": [
        {
            "itemId": "{{post0_id}}"
        }
    ],
    "moduleIds": [
        "{{section}}"
    ]
}""", token="token", app_headers=True)
    expect(_resp56).json('$.code').equals('200')
    expect(_resp56).json('$.message').equals('success')


    # --- step 57: Partner Create event T2830 (POST /product-event/v2) ---
    _resp57 = ctx.api.events.create_v2(body=r"""{
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "isTimeUnspecified": false,
    "allowAutoComplete": true,
    "description": "",
    "note": "auto test",
    "location": "Test venue · West Mound Street, Columbus, OH",
    "status": "UPCOMING",
    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "isTaxEnabled": false,
    "isAddressRevealEnabled": false,
    "title": "Test event post variant settings",
    "venue": "Test venue · West Mound Street, Columbus, OH",
    "timezone": {
        "timeZoneId": "America/New_York",
        "timeZoneName": "Eastern Daylight Time",
        "dstOffset": 3600,
        "rawOffset": -18000
    },
    "poster": {
        "height": 2048,
        "width": 3072,
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "mediaType": "IMAGE"
    },
    "startDateDisplay": "2032-04-24",
    "styleSettings": {
        "fontFamily": "Inter",
        "color": "#FFFFFF",
        "backgroundColor": "#000000",
        "borderColor": "#000000",
        "dividerColor": "#FFFFFF",
        "secondaryTextColor": "#E0E0E0",
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 700
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 400,
            "color": "#FFFFFF"
        },
        "button": {
            "backgroundColor": "#F6CA7C",
            "color": "#000000",
            "borderColor": "#000000",
            "borderRadius": 12,
            "boxShadow": "none",
            "fontSize": 16,
            "fontWeight": 700
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF",
            "borderColor": "#F6CA7C",
            "borderRadius": 12,
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "borderRadius": 99,
            "color": "#000000 ",
            "borderColor": "#0000",
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "borderRadius": 16,
            "backgroundColor": "#000000",
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#FFFFFF"
            }
        },
        "product": {
            "backgroundColor": "#000000",
            "borderRadius": 8,
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "backgroundColor": "#D32A09",
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        }
    }
}""", app_headers=True, token="token")
    expect(_resp57).json('$.code').equals('200')
    expect(_resp57).json('$.message').equals('success')
    ctx.extract("created_event_id", _resp57, "$.data.id")
    ctx.extract("autoCreatedPostId", _resp57, "$.data.autoCreatedPostId")
    expect(_resp57).json('$.data').exists()
    expect(_resp57).json('$.data.id').exists()
    expect(_resp57).json('$.data.autoCreatedPostId').exists()



    # --- step 58: Partner Create event media next step T2830  (POST /product-event/v2/{{created_event_id}}/media/batch/create) ---
    _resp58 = ctx.api.events.media_batch_create(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
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
    "medias": [],
    "mediaTextConfig": {
        "headline": "Missed our last event?",
        "subtitle": "Here's a lil recap of our last event👇",
        "align": "center"
    }
}""", app_headers=True, token="token")
    expect(_resp58).json('$.code').equals('200')
    expect(_resp58).json('$.message').equals('success')



    # --- step 59: Partner Create event ticket next step T2830 (POST /product-event/v2/{{created_event_id}}/ticket/batch/v2) ---
    _resp59 = ctx.api.events.ticket_batch_v2(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
    "listingType": "TICKET",
    "isTaxEnabled": false,
    "autoReplace": false,
    "tickets": [
        {
            "listingType": "TICKET",
            "ticketType": "TICKET_TYPE_STANDARD",
            "images": [
                {
                    "id": "80f43627-4bef-49b0-934b-cd63d49f8787",
                    "height": 1000,
                    "width": 1000,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                    "mediaType": "IMAGE"
                }
            ],
            "title": "General Admission",
            "bodyJson": "",
            "options": [
                {
                    "name": "Title",
                    "values": [
                        "Default Title"
                    ],
                    "images": []
                }
            ],
            "variants": [
                {
                    "inventoryQuantity": 1000,
                    "ticketPrice": 22,
                    "price": 25.55,
                    "fees": 3.55,
                    "priceAnchor": 0,
                    "option": {
                        "option1": "Default Title"
                    },
                    "transactionFee": {
                        "platformFee": 3.55,
                        "customFee": 0,
                        "customFeeBreakdown": {
                            "TAX": {
                                "unitFixedFee": 0,
                                "unitPercentageFee": 0,
                                "itemFee": 0
                            }
                        },
                        "transactionItemFee": 3.55
                    }
                }
            ]
        }
    ],
    "coSellingCommissionRate": 10
}
""", app_headers=True, token="token")
    expect(_resp59).json('$.code').equals('200')
    expect(_resp59).json('$.message').equals('success')



    # --- step 60: Partner Create event lineup next step  T2830 (POST /product-event/v2/{{created_event_id}}/lineup/batch) ---
    _resp60 = ctx.api.events.lineup_batch(path_vars={"created_event_id": vars.get("created_event_id", "")}, body="""{"lineup":[]}""", app_headers=True, token="token")
    expect(_resp60).json('$.code').equals('200')
    expect(_resp60).json('$.message').equals('success')



    # --- step 61: Partner Check event details (GET /product-event/v2/{{created_event_id}}/config) ---
    _resp61 = ctx.api.events.v2_config(params={"keyword": "", "pageSize": "30", "pageNumber": "1"}, token="token", app_headers=True)
    expect(_resp61).json('$.code').equals('200')
    expect(_resp61).json('$.message').equals('success')
    ctx.extract("ticket_id", _resp61, "$.data.tickets[0].id")
    expect(_resp61).status().is_(200)
    expect(_resp61).json('$.data.title').equals('Test event post variant settings')
    expect(_resp61).json('$.data.tickets').is_array()
    expect(_resp61).json('$.data.tickets').is_not_empty()
    expect(_resp61).json('$.data.tickets[0].id').is_string()
    expect(_resp61).json('$.data.tickets[0].id').is_not_empty()
    expect(_resp61).json('$.data.status').equals('UPCOMING')



    # --- step 62: update the ticket variant and price to 0 (PUT /v2/products/{{ticket_id}}) ---
    _resp62 = ctx.api.products.update_v2(body=r"""{
    "id": "{{ticket_id}}",
    "remote_id": null,
    "platform": "PEAR",
    "createdAt": "2026-04-20T07:41:49.560Z",
    "updatedAt": "2026-04-20T07:41:49.588Z",
    "title": "General Admission",
    "bodyHtml": "<p class=\"katana__paragraph katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "originalBodyHtml": "",
    "isBodyHtmlOverridden": false,
    "bodyText": "",
    "handle": null,
    "productType": "",
    "publishedAt": "2026-04-20T07:41:49.582Z",
    "publishedScope": "",
    "status": "ACTIVE",
    "externalStatus": "ACTIVE",
    "followExternalStatus": false,
    "tags": [],
    "templateSuffix": null,
    "vendor": "Pear",
    "syncAt": null,
    "deletedAt": null,
    "delisted": false,
    "excludedByImportingTag": false,
    "isFeatured": false,
    "featuredScore": null,
    "inventoryQuantity": 1000,
    "inventoryQuantityOriginal": 1000,
    "soldQuantity": 0,
    "priceDisplay": 25.56,
    "priceDisplayAnchor": 0,
    "priceMin": 25.56,
    "priceMinAnchor": 0,
    "priceMax": 25.56,
    "priceMaxAnchor": 0,
    "priceImportedMin": 0,
    "priceImportedMax": 0,
    "imageCount": 1,
    "isUsed": "NWT",
    "shippingType": "NO_SHIPPING_REQUIRED",
    "additionalShippingFee": 0,
    "deliveryTime": [
        0,
        5
    ],
    "returnPolicyApplied": true,
    "isAvailable": true,
    "commissionRate": 10,
    "textForShare": null,
    "priceSyncImported": false,
    "coverImage": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
        "width": 1000,
        "height": 1000,
        "mediaSrc": null,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
    "reviewCount": null,
    "reviewOverallScore": null,
    "reviewAggregate": null,
    "displayReviews": true,
    "links": null,
    "taxEnable": false,
    "taxJarCategory": "",
    "customTaxRate": null,
    "subscriptionPlanId": null,
    "reviewRedirectProductId": null,
    "reviewSummary": null,
    "customFieldsInfo": null,
    "listingType": "TICKET",
    "shippingOptions": [],
    "shippingNote": null,
    "autoFulfill": true,
    "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",
    "copyFromId": null,
    "stopSellingAfter": null,
    "deliveryMethod": "QR_CODE",
    "thirdPartyDeliveryMessage": "",
    "isMultipleDaysPassEnabled": false,
    "multipleDaysPass": null,
    "isPickupEtaEnabled": null,
    "eventMatchingRules": null,
    "excludeFromPostSync": false,
    "expirationTime": null,
    "allowAtDoorSales": false,
    "options": [
        {
            "name": "Time",
            "values": [
                "5 people",
                "7 people",
                "9 people"
            ],
            "position": 1
        }
    ],
    "variants": [
        {
            "title": "5 people",
            "option": {
                "option1": "5 people"
            },
            "price": 0,
            "ticketPrice": 0,
            "fees": 0,
            "transactionFee": {
                "platformFee": 0,
                "customFee": 0,
                "customFeeBreakdown": {},
                "transactionItemFee": 0
            },
            "image": null,
            "priceAnchor": "0",
            "inventoryQuantity": 1000
        },
        {
            "title": "7 people",
            "option": {
                "option1": "7 people"
            },
            "price": 0,
            "ticketPrice": 0,
            "fees": 0,
            "transactionFee": {
                "platformFee": 0,
                "customFee": 0,
                "customFeeBreakdown": {},
                "transactionItemFee": 0
            },
            "image": null,
            "priceAnchor": "0",
            "inventoryQuantity": 1000
        },
        {
            "title": "9 people",
            "option": {
                "option1": "9 people"
            },
            "price": 0,
            "ticketPrice": 0,
            "fees": 0,
            "transactionFee": {
                "platformFee": 0,
                "customFee": 0,
                "customFeeBreakdown": {},
                "transactionItemFee": 0
            },
            "image": null,
            "priceAnchor": "0",
            "inventoryQuantity": 1000
        }
    ],
    "catalogCommissionRate": 25,
    "earliestTime": "2026-04-20T07:41:49.560Z",
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "isProductFormEnabled": false,
    "isVariantPriceDisplayEnabled": false,
    "stopSellingAfterDisplay": "",
    "overrideEventTax": false,
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "images": [
        {
            "id": "c47ca31e-2e09-4b59-8f52-27d3570ab653",
            "remote_id": null,
            "createdAt": "2026-04-20T07:41:49.588Z",
            "updatedAt": "2026-04-20T07:41:49.588Z",
            "height": 1000,
            "width": 1000,
            "position": 1,
            "productId": "{{ticket_id}}",
            "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
            "variantIds": [],
            "mediaType": "IMAGE",
            "mediaSrc": null,
            "mediaDuration": 0,
            "contributedBy": 3,
            "contributorId": null,
            "productImageType": "PRODUCT",
            "source": null
        }
    ],
    "eventId": "{{created_event_id}}",
    "isExpirationEnabled": false
}""", token="token", app_headers=True)
    expect(_resp62).json('$.code').equals('200')
    expect(_resp62).json('$.message').equals('success')
    ctx.extract("current_product_id", _resp62, "$.data.id")
    ctx.extract("current_variants_json", _resp62, "$.data.variants")
    expect(_resp62).status().is_(200)



    # --- step 63: Add merch001 (POST /v2/products) ---
    _resp63 = ctx.api.products.create_v2(body=r"""{
    "merchantId": "{{eventcatalog_id}}",
    "shippingType": "NO_SHIPPING_REQUIRED",
    "isFeatured": false,
    "commissionRate": 0,
    "priceSyncImported": false,
    "additionalShippingFee": 0,
    "returnPolicyApplied": true,
    "title": "merch 001",
    "bodyHtml": "<p class=\"katana__paragraph katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "status": "ACTIVE",
    "isUsed": "NWT",
    "taxJarCategory": "",
    "platform": "PEAR",
    "autoFulfill": true,
    "options": [
        {
            "name": "Title",
            "values": [
                "Default Title"
            ],
            "images": []
        }
    ],
    "variants": [
        {
            "inventoryQuantity": 1,
            "price": 100,
            "priceAnchor": 0,
            "option": {
                "option1": "Default Title"
            },
            "weightUnit": "lb"
        }
    ],
    "listingType": "EVENT_PRODUCT",
    "soldQuantity": 0,
    "excludeFromPostSync": false,
    "isTipEnabled": false,
    "catalogCommissionRate": 0,
    "shippingOptions": [],
    "deliveryMethod": "QR_CODE",
    "thirdPartyDeliveryMessage": "",
    "taxEnable": false,
    "customTaxRate": null,
    "earliestTime": "2026-07-15T07:26:10.057Z",
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "isInclusionsEnabled": false,
    "inclusions": [],
    "isVariantPriceDisplayEnabled": false,
    "stopSellingAfterDisplay": "",
    "extraInfo": {
        "businessTimezone": "Asia/Shanghai"
    },
    "overrideEventTax": false,
    "overrideEventCustomFee": false,
    "hideFees": false,
    "transactionCustomFeeConfig": null,
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "images": [
        {
            "mediaType": "IMAGE",
            "mediaSrc": null,
            "mediaDuration": 0,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762141834/uploaded_images/vdcheuqxljhmyl4oqbnx.webp",
            "height": 1350,
            "width": 1080,
            "source": "UPLOAD",
            "position": 1,
            "setThumbnail": true,
            "origin": {
                "width": 1080,
                "height": 1350,
                "position": 1
            },
            "productImageType": "PRODUCT"
        }
    ],
    "isMultipleDaysPassEnabled": false,
    "eventId": "{{created_event_id}}",
    "isExpirationEnabled": false
}""", app_headers=True, token="token")
    expect(_resp63).json('$.code').equals('200')
    expect(_resp63).json('$.message').equals('success')



    # --- step 64: Add merch002 (POST /v2/products) ---
    _resp64 = ctx.api.products.create_v2(body=r"""{
    "merchantId": "{{eventcatalog_id}}",
    "shippingType": "NO_SHIPPING_REQUIRED",
    "isFeatured": false,
    "commissionRate": 0,
    "priceSyncImported": false,
    "additionalShippingFee": 0,
    "returnPolicyApplied": true,
    "title": "merch 002",
    "bodyHtml": "<p class=\"katana__paragraph katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "status": "ACTIVE",
    "isUsed": "NWT",
    "taxJarCategory": "",
    "platform": "PEAR",
    "autoFulfill": true,
    "options": [
        {
            "name": "Title",
            "values": [
                "Default Title"
            ],
            "images": []
        }
    ],
    "variants": [
        {
            "inventoryQuantity": 1,
            "price": 100,
            "priceAnchor": 0,
            "option": {
                "option1": "Default Title"
            },
            "weightUnit": "lb"
        }
    ],
    "listingType": "EVENT_PRODUCT",
    "soldQuantity": 0,
    "excludeFromPostSync": false,
    "isTipEnabled": false,
    "catalogCommissionRate": 0,
    "shippingOptions": [],
    "deliveryMethod": "QR_CODE",
    "thirdPartyDeliveryMessage": "",
    "taxEnable": false,
    "customTaxRate": null,
    "earliestTime": "2026-07-15T07:26:10.057Z",
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "isInclusionsEnabled": false,
    "inclusions": [],
    "isVariantPriceDisplayEnabled": false,
    "stopSellingAfterDisplay": "",
    "extraInfo": {
        "businessTimezone": "Asia/Shanghai"
    },
    "overrideEventTax": false,
    "overrideEventCustomFee": false,
    "hideFees": false,
    "transactionCustomFeeConfig": null,
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "images": [
        {
            "mediaType": "IMAGE",
            "mediaSrc": null,
            "mediaDuration": 0,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762141834/uploaded_images/vdcheuqxljhmyl4oqbnx.webp",
            "height": 1350,
            "width": 1080,
            "source": "UPLOAD",
            "position": 1,
            "setThumbnail": true,
            "origin": {
                "width": 1080,
                "height": 1350,
                "position": 1
            },
            "productImageType": "PRODUCT"
        }
    ],
    "isMultipleDaysPassEnabled": false,
    "eventId": "{{created_event_id}}",
    "isExpirationEnabled": false
}""", app_headers=True, token="token")
    expect(_resp64).json('$.code').equals('200')
    expect(_resp64).json('$.message').equals('success')



    # --- step 65: get the event post id (GET /posts/curator/event/{{created_event_id}}/posts) ---
    _resp65 = ctx.api.posts.curator_event_posts(path_vars={"event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    expect(_resp65).json('$.code').equals('200')
    expect(_resp65).json('$.message').equals('success')
    ctx.extract("post0_id", _resp65, "$.data.items[0].id")
    expect(_resp65).json('$.data.items[0].id').is_string()
    expect(_resp65).json('$.data.items[0].id').is_not_empty()



    # --- step 66: Add to the post to module to add to shop (POST store-front/add-items-to-modules) ---
    _resp66 = ctx.api.storefront.add_items_to_modules(body="""{
    "items": [
        {
            "itemId": "{{post0_id}}"
        }
    ],
    "moduleIds": [
        "{{section}}"
    ]
}""", token="token", app_headers=True)
    expect(_resp66).json('$.code').equals('200')
    expect(_resp66).json('$.message').equals('success')


    # --- step 67: Admin update the partner's the t2830 post  url (PATCH /post/{{post0_id}}) ---
    _resp67 = ctx.api.admin.post_by_post_id(path_vars={"post_id": vars.get("post0_id", "")}, body="""{
    "urlAlias": "test-event-post-variant-settings",
    "headline": "test-event-post-variant-settings ",
    "title": "test-event-post-variant-settings ",
    "subTitle": "",
    "links": [],
    "creatorId": "{{user_id}}",
    "baseSold": 0,
    "baseViewed": 0,
    "expiredAt": null,
    "hideInStore": false,
    "checkoutInPost": true,
    "status": "ACTIVE"
}""", app_headers=True, token="admin_token")
    expect(_resp67).json('$.code').equals('200')
    expect(_resp67).json('$.message').equals('success')
    expect(_resp67).status().is_one_of([200,201])
    # 注：常量 expectedAlias
    expect(_resp67).json('$.data.post.urlAlias').equals('test-event-post-variant-settings')
    expect(_resp67).json('$.data.post.status').equals('ACTIVE')



    # --- step 68: Create event with no ticket (POST /product-event/v2) ---
    _resp68 = ctx.api.events.create_v2(body=r"""{
    "ignoreStartTime": true,
    "ignoreEndTime": true,
    "isTimeUnspecified": false,
    "allowAutoComplete": true,
    "description": "",
    "note": "",
    "location": "Teston Road, Maple, ON, Canada",
    "status": "UPCOMING",
    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "isTaxEnabled": false,
    "isAddressRevealEnabled": false,
    "title": "event with no ticket",
    "venue": "3rd Street Promenade",
    "timezone": {
        "timeZoneId": "America/Toronto",
        "timeZoneName": "Eastern Daylight Time",
        "dstOffset": 3600,
        "rawOffset": -18000
    },
    "poster": {
        "height": 2048,
        "width": 3072,
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "mediaType": "IMAGE"
    },
    "startDateDisplay": "2032-07-15",
    "locationDetails": {
        "line1": "Teston Road",
        "city": "Vaughan",
        "state": "Ontario",
        "stateName": "Ontario",
        "zipcode": "",
        "country": "Canada",
        "placeId": "Eh5UZXN0b24gUm9hZCwgTWFwbGUsIE9OLCBDYW5hZGEiLiosChQKEgnZKxgAlCgriBFZxtVPBhJGQxIUChIJnViAXQMpK4gR_d4duheew-k"
    },
    "styleSettings": {
        "template": "ClearSky",
        "layout": {
            "pageHeader": {
                "style": "DEDICATED_HEADER_BAR",
                "displayText": "SHOP_NAME",
                "height": "MEDIUM"
            },
            "productBanner": {
                "ctaButton": "VIEW_PRODUCT",
                "display": "HIDE"
            }
        },
        "fontFamily": "Inter",
        "color": "#FFFFFF",
        "backgroundColor": "#000000",
        "borderColor": "#000000",
        "dividerColor": "#FFFFFF",
        "secondaryTextColor": "#E0E0E0",
        "announcementCarousel": {
            "color": "#000000",
            "backgroundColor": "#F6CA7C"
        },
        "title": {
            "color": "#F6CA7C",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 700
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 400,
            "color": "#FFFFFF"
        },
        "button": {
            "backgroundColor": "#F6CA7C",
            "color": "#000000",
            "borderColor": "#000000",
            "borderRadius": 0,
            "boxShadow": "none",
            "fontSize": 16,
            "fontWeight": 400
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 400,
            "color": "#FFFFFF",
            "borderColor": "#F6CA7C",
            "borderRadius": 0,
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF"
        },
        "selectButton": {
            "borderColor": "#000000"
        },
        "relatedLink": {
            "borderRadius": 0,
            "color": "#000000 ",
            "borderColor": "#0000",
            "backgroundColor": "#FAFAFA"
        },
        "featuredProducts": {
            "borderRadius": 0,
            "backgroundColor": "#000000",
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#FFFFFF"
            }
        },
        "product": {
            "backgroundColor": "#000000",
            "borderRadius": 0,
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0"
        },
        "discount": {
            "backgroundColor": "#D32A09",
            "color": "#FFFFFF",
            "priceColor": "#FFFFFF"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF03",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#FFFFFF",
            "descriptionText": "#E0E0E0"
        },
        "eventInfoBanner": {
            "text": "#FFFFFF",
            "secondaryText": "#E0E0E0"
        },
        "eventDescription": {
            "text": "#E0E0E0",
            "title": "#FFFFFF"
        },
        "featuredProduct": {
            "cover": {
                "borderRadius": 0
            }
        },
        "recentUsedColors": [
            "#ffffff"
        ]
    }
}""", app_headers=True, token="token")
    expect(_resp68).json('$.code').equals('200')
    expect(_resp68).json('$.message').equals('success')
    ctx.extract("created_event_id02", _resp68, "$.data.id")
    expect(_resp68).status().is_(201)
    expect(_resp68).json('$.data').exists()
    expect(_resp68).json('$.data.id').exists()



    # --- step 69: Create event media next step (POST /product-event/v2/{{created_event_id02}}/media/batch/create) ---
    _resp69 = ctx.api.events.media_batch_create(path_vars={"created_event_id": "{{created_event_id02}}"}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
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
    "medias": [],
    "mediaTextConfig": {
        "headline": "Missed our last event?",
        "subtitle": "Here's a lil recap of our last event👇",
        "align": "center"
    }
}""", token="token", app_headers=True)
    expect(_resp69).json('$.code').equals('200')
    expect(_resp69).json('$.message').equals('success')



    # --- step 70: Create event ticket next step (POST /product-event/v2/{{created_event_id02}}/ticket/batch/v2) ---
    _resp70 = ctx.api.events.ticket_batch_v2(path_vars={"created_event_id": "{{created_event_id02}}"}, body="""{
    "poster": {
        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
        "width": 3072,
        "height": 2048,
        "position": 0,
        "mediaType": "IMAGE",
        "mediaDuration": 0
    },
    "listingType": "TICKET",
    "isTaxEnabled": false,
    "autoReplace": false,
    "tickets": [],
    "customFeeConfig": {
        "isEnabled": false,
        "items": []
    }
}""", token="token", app_headers=True)
    expect(_resp70).json('$.code').equals('200')
    expect(_resp70).json('$.message').equals('success')



    # --- step 71: Partner Create event lineup next step (POST /product-event/v2/{{created_event_id02}}/lineup/batch) ---
    _resp71 = ctx.api.events.lineup_batch(path_vars={"created_event_id": "{{created_event_id02}}"}, body="""{"lineup":[]}""", token="token", app_headers=True)
    expect(_resp71).json('$.code').equals('200')
    expect(_resp71).json('$.message').equals('success')



    # --- step 72: Create Catalog (POST /merchant) ---
    _resp72 = ctx.api.merchants.create(body="""{
    "commissionRate": 25,
    "storeName": "auto test",
    "isVisible": true
}""", app_headers=True, token="token")
    expect(_resp72).json('$.code').equals('200')
    expect(_resp72).json('$.message').equals('success')
    ctx.extract("merchant_id_autotest", _resp72, "$.data.id")
    expect(_resp72).status().is_(201)
    expect(_resp72).json('$.data.storeName').equals('auto test')
    expect(_resp72).json('$.data.commissionRate').equals(25)
    expect(_resp72).json('$.data.id').is_string()
    expect(_resp72).json('$.data.id').is_not_empty()



    # --- step 73: get shipping-options (GET /merchants/{{merchant_id_autotest}}/shipping-options) ---
    _resp73 = ctx.api.merchants.shipping_options_by_merchant_id(path_vars={"merchant_id": vars.get("merchant_id_autotest", "")}, app_headers=True, token="token")
    expect(_resp73).json('$.code').equals('200')
    expect(_resp73).json('$.message').equals('success')
    ctx.extract("shipping_option_id", _resp73, "$.data.items[0].id")
    expect(_resp73).status().is_(200)
    expect(_resp73).json('$.data.items').is_array()
    expect(_resp73).json('$.data.items').is_not_empty()
    expect(_resp73).json('$.data.totalCount').at_least(1)
    expect(_resp73).json('$.data.items[0].title').equals('Flat Shipping')
    expect(_resp73).json('$.data.items[0].shippingFee').equals(4.99)
    expect(_resp73).json('$.data.items[0].isDefault').equals(True)
    expect(_resp73).json('$.data.items[0].id').is_string()
    expect(_resp73).json('$.data.items[0].id').is_not_empty()



    # --- step 74: create general product and setting the shipping option is flat shipping (POST /v2/products) ---
    _resp74 = ctx.api.products.create_v2(body=r"""{
    "merchantId": "{{merchant_id_autotest}}",
    "shippingType": "INHERIT_SHIPPING",
    "isFeatured": false,
    "commissionRate": null,
    "priceSyncImported": false,
    "additionalShippingFee": 0,
    "returnPolicyApplied": true,
    "title": "test_general_products",
    "bodyHtml": "<p class=\"katana__paragraph katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "status": "ACTIVE",
    "isUsed": "NWT",
    "taxJarCategory": "",
    "platform": "PEAR",
    "autoFulfill": false,
    "options": [
        {
            "name": "Title",
            "values": [
                "Default Title"
            ],
            "images": []
        }
    ],
    "variants": [
        {
            "inventoryQuantity": 1000,
            "price": 0,
            "priceAnchor": 0,
            "option": {
                "option1": "Default Title"
            },
			"weight": 1,
            "weightUnit": "lb"
        }
    ],
    "excludeFromPostSync": false,
    "listingType": "REGULAR",
    "catalogCommissionRate": 25,
    "shippingOptions": [
        {
            "id": "{{shipping_option_id}}",
            "catalogId": "{{merchant_id_autotest}}",
            "title": "Flat Shipping",
            "shippingFee": 4.99,
            "deliveryTime": [
                0,
                5
            ],
            "enableFreeShippingThreshold": false,
            "freeShippingThreshold": 0,
            "note": null,
            "isDefault": true,
            "weightBasedShippingRates": [
        {
          "to": 2,
          "from": 0,
          "price": 0
        },
        {
          "to": 5,
          "from": 3,
          "price": 5
        }
      ],
            "enableWeightBasedShippingRates": true,
            "priceBasedShippingRates": null,
            "enablePriceBasedShippingRates": false,
            "profileName": null,
            "from": "PEAR",
            "additionalShippingFee": 0,
            "enableAdditionalShippingFee": false
        }
    ],
    "deliveryMethod": "SHIPPING",
    "isReturnPolicyAllowed": false,
    "thirdPartyDeliveryMessage": "",
    "taxEnable": false,
    "customTaxRate": null,
    "earliestTime": "2026-04-20T08:19:01.799Z",
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "isVariantPriceDisplayEnabled": false,
    "stopSellingAfterDisplay": "",
    "extraInfo": {
        "businessTimezone": "America/Los_Angeles"
    },
    "overrideEventTax": false,
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "images": [
        {
            "mediaType": "IMAGE",
            "mediaSrc": null,
            "mediaDuration": 0,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762141834/uploaded_images/vdcheuqxljhmyl4oqbnx.webp",
            "height": 1350,
            "width": 1080,
            "source": "UPLOAD",
            "position": 1,
            "setThumbnail": true,
            "origin": {
                "width": 1080,
                "height": 1350,
                "position": 1
            },
            "productImageType": "PRODUCT"
        }
    ],
    "isMultipleDaysPassEnabled": false
}""", app_headers=True, token="token")
    expect(_resp74).json('$.code').equals('200')
    expect(_resp74).json('$.message').equals('success')
    expect(_resp74).json('$.data.title').equals('test_general_products')
    # 原始集合 node「create general product and setting the shipping option is flat shipping」
    # 把响应 $.data.id 存为 productId0（下游 shipping-options PUT 与 POST /posts/curator 依赖它）
    ctx.extract("productId0", _resp74, "$.data.id")



    # --- step 75: Partner 999 update shipping options (PUT /merchants/{{merchant_id_autotest}}/shipping-options/{{shipping_option_id}}) ---
    _resp75 = ctx.api.merchants.shipping_options_update(path_vars={"merchant_id": vars.get("merchant_id_autotest", ""), "shipping_option_id": vars.get("shipping_option_id", "")}, body="""{
    "deliveryTime": [
        0,
        5
    ],
    "id": "{{productId0}}",
    "catalogId": "{{merchant_id_autotest}}",
    "title": "Flat Shipping",
    "shippingFee": 5,
    "enableFreeShippingThreshold": false,
    "freeShippingThreshold": 0,
    "note": null,
    "isDefault": true,
    "weightBasedShippingRates": [
        {
            "from": 0,
            "to": 2,
            "price": 0
        },
        {
            "from": 3,
            "to": 5,
            "price": 5
        }
    ],
    "enableWeightBasedShippingRates": true,
    "priceBasedShippingRates": null,
    "enablePriceBasedShippingRates": false,
    "profileName": null,
    "from": "PEAR"
}""", app_headers=True, token="token")
    expect(_resp75).json('$.code').equals('200')
    expect(_resp75).json('$.message').equals('success')



    # --- step 76: create product and update alias (POST /v2/products) ---
    _resp76 = ctx.api.products.create_v2(body=r"""{
    "merchantId": "{{merchant_id_autotest}}",
    "shippingType": "INHERIT_SHIPPING",
    "isFeatured": false,
    "commissionRate": null,
    "priceSyncImported": false,
    "additionalShippingFee": 0,
    "returnPolicyApplied": true,
    "title": "autotest product title - do not delete",
    "bodyHtml": "<p class=\"katana__paragraph katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "status": "ACTIVE",
    "isUsed": "NWT",
    "taxJarCategory": "",
    "platform": "PEAR",
    "autoFulfill": false,
    "options": [
        {
            "name": "Title",
            "values": [
                "Default Title"
            ],
            "images": []
        }
    ],
    "variants": [
        {
            "inventoryQuantity": 100,
            "price": 0,
            "priceAnchor": 0,
            "option": {
                "option1": "Default Title"
            },
			"weight": 1,
            "weightUnit": "lb"
        }
    ],
    "excludeFromPostSync": false,
    "listingType": "REGULAR",
    "catalogCommissionRate": 25,
    "shippingOptions": [
        {
            "id": "{{shipping_option_id}}",
            "catalogId": "{{merchant_id_autotest}}",
            "title": "Flat Shipping",
            "shippingFee": 4.99,
            "deliveryTime": [
                0,
                5
            ],
            "enableFreeShippingThreshold": false,
            "freeShippingThreshold": 0,
            "note": null,
            "isDefault": true,
            "weightBasedShippingRates": [
        {
          "to": 2,
          "from": 0,
          "price": 0
        },
        {
          "to": 5,
          "from": 3,
          "price": 5
        }
      ],
            "enableWeightBasedShippingRates": true,
            "priceBasedShippingRates": null,
            "enablePriceBasedShippingRates": false,
            "profileName": null,
            "from": "PEAR",
            "additionalShippingFee": 0,
            "enableAdditionalShippingFee": false
        }
    ],
    "deliveryMethod": "SHIPPING",
    "isReturnPolicyAllowed": false,
    "thirdPartyDeliveryMessage": "",
    "taxEnable": false,
    "customTaxRate": null,
    "earliestTime": "2026-04-20T08:19:01.799Z",
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "isVariantPriceDisplayEnabled": false,
    "stopSellingAfterDisplay": "",
    "extraInfo": {
        "businessTimezone": "America/Los_Angeles"
    },
    "overrideEventTax": false,
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "images": [
        {
            "mediaType": "IMAGE",
            "mediaSrc": null,
            "mediaDuration": 0,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762141834/uploaded_images/vdcheuqxljhmyl4oqbnx.webp",
            "height": 1350,
            "width": 1080,
            "source": "UPLOAD",
            "position": 1,
            "setThumbnail": true,
            "origin": {
                "width": 1080,
                "height": 1350,
                "position": 1
            },
            "productImageType": "PRODUCT"
        }
    ],
    "isMultipleDaysPassEnabled": false
}""", app_headers=True, token="token")
    expect(_resp76).json('$.code').equals('200')
    expect(_resp76).json('$.message').equals('success')
    expect(_resp76).json('$.data.title').equals('autotest product title - do not delete')
    # 原始集合 node「create product and update alias」把响应 $.data.id 存为 productId1
    # （下游 POST /posts/curator 的 relatedProducts[1].merchantProductId 依赖它，缺失会 400）
    ctx.extract("productId1", _resp76, "$.data.id")

    # --- step 76 附带的 database 处理器：update alias ---
    # 原 Apifox 集合 node「create product and update alias」除 POST /v2/products 外，
    # 还挂了一个 type="database" 处理器（connectionId=112809 = Release_new）：
    #   UPDATE "PromoterProduct" SET alias = 'bxasz9' WHERE merchant_product_id = '{{productId1}}'
    # 作用是把这个商品在 promoter 侧登记为 alias=bxasz9，使店铺短链
    # /{{partner_vanityUrl}}/p/bxasz9 可解析 —— UI 用例 T5007 / T3690 打开的正是该短链
    # （迁移时整个 database 处理器被丢弃，用例名也因此带 "no SQL"，于是短链 404、
    #  商品页渲染不出 [data-cta-action="add-to-cart"]）。
    # 必须用 run_db_write：run_db / db.query 只读，事务在连接关闭时会被回滚，
    # UPDATE 会「看似成功、库里没改」。
    _sql76 = "UPDATE \"PromoterProduct\" SET alias = 'bxasz9' WHERE merchant_product_id = '{{productId1}}'"
    _affected76 = 0
    try:
        # PromoterProduct 行由建商品时的后端逻辑写入，理论上紧随 Product，但可能异步
        # 落地（实测两者相差 ~15ms）。这里最多重试 5 次、每次间隔 2s，避免「行还没建
        # 好 -> UPDATE 影响 0 行 -> alias 没落库 -> 短链 404」这种时序性假失败。
        for _try76 in range(1, 6):
            _affected76 = ctx.run_db_write(112809, _sql76)
            if _affected76:
                break
            time.sleep(2)
        _logger.info(
            "[step 76][db] UPDATE PromoterProduct SET alias='bxasz9' "
            "WHERE merchant_product_id=%s -> affected_rows=%s (尝试 %s 次)",
            vars.get("productId1"), _affected76, _try76,
        )
        if _affected76 == 0:
            # 如实记录、不阻断：0 行说明该商品在 PromoterProduct 里没有对应记录，
            # alias 未落库，短链 bxasz9 会 404（T5007 / T3690 将如实报失败）。
            _logger.warning(
                "[step 76][db] 重试后仍 0 行：productId1=%s 在 PromoterProduct 中无对应行，"
                "alias 未设置 -> 短链 bxasz9 会 404",
                vars.get("productId1"),
            )
    except Exception as _exc76:  # noqa: BLE001
        # DB 不可达（如 CI 网络/安全组限制）不应让整轮预制中断，但必须如实记录，
        # 以便区分「SQL 没跑成」与「UI 用例真失败」。
        _logger.warning("[step 76][db] SQL 执行失败（未阻断执行）-> %s", _exc76)



    # --- step 77: get the two products url allias (GET /merchant/product/list) ---
    # 原始集合带了完整查询串（缺 merchantId 会 400 "merchantId must be a UUID"）：
    #   keyword=&sortCreatedAt=desc&merchantId={{merchant_id_autotest}}
    #   &status[]=ACTIVE&status[]=DRAFT
    #   &lifecycleStatus[]=LIFECYCLE_STATUS_NORMAL&lifecycleStatus[]=LIFECYCLE_STATUS_ON_HOLD
    #   &pageSize=50&pageNumber=1
    # 重复键（status[] / lifecycleStatus[]）用 list 值表达，requests 会展开成重复参数。
    _resp77 = ctx.api.products.merchant_product_list(
        params={
            "keyword": "",
            "sortCreatedAt": "desc",
            "merchantId": "{{merchant_id_autotest}}",
            "status[]": ["ACTIVE", "DRAFT"],
            "lifecycleStatus[]": ["LIFECYCLE_STATUS_NORMAL", "LIFECYCLE_STATUS_ON_HOLD"],
            "pageSize": "50",
            "pageNumber": "1",
        },
        app_headers=True, token="token")
    expect(_resp77).json('$.code').equals('200')
    expect(_resp77).json('$.message').equals('success')
    # 原 Apifox 遍历 response.data.items，按 title 匹配后取 alias：
    #   alias0 <- title == "test_general_products"
    #   alias1 <- title == "autotest product title - do not delete"
    ctx.extract("alias0", _resp77, '$.data.items[?(@.title=="test_general_products")].alias')
    ctx.extract("alias1", _resp77, '$.data.items[?(@.title=="autotest product title - do not delete")].alias')
    assert vars.get('alias0') is not None, "环境变量 alias0 未设置"
    assert vars.get('alias1') is not None, "环境变量 alias1 未设置"



    # --- step 78: get partner 999 promoter ProductId0 (GET /promoter/product/public/{{alias0}}/product-detail) ---
    _resp78 = ctx.api.promoters.product_public_detail(path_vars={"alias": vars.get("alias0", "")}, params={"vanityUrl": "{{partner_vanityUrl}}"}, app_headers=True, token="token")
    expect(_resp78).json('$.code').equals('200')
    expect(_resp78).json('$.message').equals('success')
    ctx.extract("ProductVariantId0", _resp78, "$.data.product.variants[0].merchantProductVariantId")
    expect(_resp78).json('$.data.product.variants[0].merchantProductVariantId').is_string()
    expect(_resp78).json('$.data.product.variants[0].merchantProductVariantId').is_not_empty()



    # --- step 79: get partner 999 promoter ProductId1 (GET /promoter/product/public/{{alias1}}/product-detail) ---
    _resp79 = ctx.api.promoters.product_public_detail(path_vars={"alias": vars.get("alias1", "")}, params={"vanityUrl": "{{partner_vanityUrl}}"}, app_headers=True, token="token")
    expect(_resp79).json('$.code').equals('200')
    expect(_resp79).json('$.message').equals('success')
    ctx.extract("ProductVariantId1", _resp79, "$.data.product.variants[0].merchantProductVariantId")
    expect(_resp79).json('$.data.product.variants[0].merchantProductVariantId').is_string()
    expect(_resp79).json('$.data.product.variants[0].merchantProductVariantId').is_not_empty()



    # --- step 80: Partner999 create general post with 2 products  (POST /posts/curator) ---
    _resp80 = ctx.api.posts.curator(body=r"""{
    "title": "auto test T3788",
    "links": [],
    "allowPromotersResell": true,
    "financeModeForPromoters": "FINANCE_MODE_COMMISSION",
    "status": "ACTIVE",
    "allowPromotersHideProducts": true,
    "allowPromotersCustomizeMedia": true,
    "isPurchaseQuantityLimited": false,
    "purchaseQuantityLimit": 1,
    "styleSettings": {
        "template": "TwilightChic",
        "layout": {
            "pageHeader": {
                "style": "DEDICATED_HEADER_BAR",
                "displayText": "NOTHING",
                "height": "MEDIUM"
            },
            "productBanner": {
                "ctaButton": "VIEW_PRODUCT",
                "display": "SHRINK"
            }
        },
        "fontFamily": "Inter",
        "color": "#000000",
        "backgroundColor": "#FFFFFF",
        "borderColor": "#CFCFCF",
        "dividerColor": "#CFCFCF",
        "secondaryTextColor": "#5D5D5D",
        "announcementCarousel": {
            "color": "#FFFFFF",
            "backgroundColor": "#0D0D14"
        },
        "title": {
            "color": "#000000",
            "fontFamily": "Inter",
            "fontSize": 24,
            "fontWeight": 800
        },
        "columnTitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#000000"
        },
        "subtitle": {
            "fontFamily": "Inter",
            "fontSize": 20,
            "fontWeight": 700,
            "color": "#000000"
        },
        "button": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#FFFFFF",
            "backgroundColor": "#0D0D14",
            "borderRadius": 12,
            "borderColor": "#0000",
            "boxShadow": "none"
        },
        "secondaryButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#0D0D14",
            "borderRadius": 12,
            "borderColor": "#0D0D14",
            "boxShadow": "none"
        },
        "textButton": {
            "fontSize": 16,
            "fontWeight": 700,
            "color": "#0D0D14"
        },
        "selectButton": {
            "borderColor": "#C1C1C3"
        },
        "relatedLink": {
            "backgroundColor": "#F2F2F6",
            "borderColor": "#0000",
            "color": "#2D2D33",
            "borderRadius": 99
        },
        "featuredProducts": {
            "borderRadius": 16,
            "backgroundColor": "#F2F2F6",
            "color": "#000000",
            "secondaryTextColor": "#5D5D5D",
            "title": {
                "fontFamily": "Inter",
                "fontSize": 14,
                "fontWeight": 400,
                "color": "#000000"
            }
        },
        "product": {
            "backgroundColor": "#FFFFFF",
            "borderRadius": 8,
            "color": "#000000",
            "secondaryTextColor": "#5D5D5D"
        },
        "discount": {
            "backgroundColor": "#D32A08",
            "color": "#FFFFFF",
            "priceColor": "#D32A08"
        },
        "freeShipping": {
            "backgroundColor": "#EBF5EF",
            "color": "#268E46"
        },
        "starRatingColor": "#FAAF00",
        "layoutFeatureCard": {
            "title": {
                "fontFamily": "Inter",
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "color": "#FFFFFF",
            "secondaryTextColor": "#5D5D5D",
            "button": {
                "backgroundColor": "#FFFFFF",
                "color": "#000000"
            }
        },
        "lineupBanner": {
            "titleText": "#000000",
            "descriptionText": "#000000"
        },
        "eventInfoBanner": {
            "text": "#000000",
            "secondaryText": "#5D5D5D"
        },
        "eventDescription": {
            "text": "#000000",
            "title": "#000000"
        },
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "variantSelectorType": "FULL_PAGE",
    "abTestingSettings": [],
    "enableAbTesting": false,
    "featuredSectionTitle": "Featured products",
    "canSetPrice": false,
    "additionalContentPosition": "aboveTickets",
    "bodyHtml": "<p class=\"katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "currentDate": "2026-04-22T09:15:13.108Z",
    "relatedProducts": [
        {
            "merchantProductId": "{{productId0}}",
            "isVisible": true,
            "isPurchaseQuantityLimited": false,
            "isRecommendation": false,
            "isDefaultToSubscription": false,
            "isCtaCustomized": false,
            "syncWithCatalogPrice": true,
            "purchaseQuantityLimit": 1,
            "variants": [
                {
                    "wholesalePriceForPromoters": 0,
                    "price": 0,
                    "costPrice": 0,
                    "priceAnchor": 0,
                    "merchantProductVariantId": "{{ProductVariantId0}}",
                    "commissionRateForPromoters": 25
                }
            ]
        },
        {
            "merchantProductId": "{{productId1}}",
            "isVisible": true,
            "isPurchaseQuantityLimited": false,
            "isRecommendation": false,
            "isDefaultToSubscription": false,
            "isCtaCustomized": false,
            "syncWithCatalogPrice": true,
            "purchaseQuantityLimit": 1,
            "variants": [
                {
                    "wholesalePriceForPromoters": 0,
                    "price": 0,
                    "costPrice": 0,
                    "priceAnchor": 0,
                    "merchantProductVariantId": "{{ProductVariantId1}}",
                    "commissionRateForPromoters": 25
                }
            ]
        }
    ],
    "promotions": [],
    "accessSpecificUser": [],
    "allowPromotersCreateCoupon": true,
    "featuredSectionEnable": true,
    "allowAffiliateSharingOnly": false,
    "hideCouponBox": false,
    "checkoutInPost": true,
    "tab": {
        "value": "Commerce",
        "label": "Commerce",
        "mappingControl": []
    },
    "timeKey": 1776849313108,
    "allowCustomizeDisplayPrices": true,
    "redirectUrl": "",
    "redirectDestinationName": "",
    "originEnablePaymentRestriction": false,
    "syncEnabled": false,
    "postType": "STANDARD",
    "recommendationSectionTitle": "",
    "subTitle": "auto test T3788",
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"\",\"editorClassName\":\"\"}",
    "needRefreshHTML": true,
    "additionalContent": "{}",
    "showAdditionalContent": false,
    "media": [],
    "othersCanCopy": false,
    "enableDownlineNote": false,
    "allowVisitorCreateAffiliateLink": false,
    "coverImages": [],
    "expiredAt": null,
    "urlAlias": "{{$word.noun(locale='en')}}",
    "headline": "auto test T3788",
    "isPaymentRestrictionEnabled": false
}""", app_headers=True, token="token")
    expect(_resp80).json('$.code').equals('200')
    expect(_resp80).json('$.message').equals('success')



    # --- step 81: Partner999 sync the post t3788 to the coseller's 997 shop (POST /posts/curator/{{post0_id}}/promoters/sync) ---
    _resp81 = ctx.api.posts.curator_sync_promoters(path_vars={"post0_id": vars.get("post0_id", "")}, body="""{
    "postId": "{{post0_id}}",
    "promoterIds": [
        "{{user_partner997_id}}"
    ]
}""", app_headers=True, token="token")
    expect(_resp81).json('$.code').equals('200')
    expect(_resp81).json('$.message').equals('success')



    # --- step 82: Set the Partner all tabs are visible  (PUT /store-front/layout) ---
    _resp82 = ctx.api.storefront.layout(body="""{
    "storeTabs": [
        {
            "name": "Posts",
            "checked": true
        },
        {
            "name": "Links",
            "checked": true
        },
        {
            "name": "Products",
            "checked": true
        },
        {
            "name": "Forms",
            "checked": true
        }
    ]
}""", app_headers=True, token="token")
    expect(_resp82).json('$.code').equals('200')
    expect(_resp82).json('$.message').equals('success')
    ctx.extract("is_products_tab_enabled", _resp82, '$.data.storeTabs[?(@.name=="Products")].checked')
    expect(_resp82).status().is_(200)
    expect(_resp82).json('$.data.storeTabs').is_array()
    expect(_resp82).json('$.data.storeTabs.length').equals(4)
    expect(_resp82).json('$.data..storeTabs..name').includes('Posts')
    expect(_resp82).json('$.data..storeTabs..name').includes('Links')
    expect(_resp82).json('$.data..storeTabs..name').includes('Products')
    expect(_resp82).json('$.data..storeTabs..name').includes('Forms')
    expect(_resp82).json('$.data.storeTabs[?(@.name=="Posts")].checked').equals(True)



    # --- step 83: Set the Partner997 all tabs are visible  (PUT /store-front/layout) ---
    _resp83 = ctx.api.storefront.layout(body="""{
    "storeTabs": [
        {
            "name": "Posts",
            "checked": true
        },
        {
            "name": "Links",
            "checked": true
        },
        {
            "name": "Products",
            "checked": true
        },
        {
            "name": "Forms",
            "checked": true
        }
    ]
}""", app_headers=True, token="partner997_auth_token")
    expect(_resp83).json('$.code').equals('200')
    expect(_resp83).json('$.message').equals('success')
    ctx.extract("is_products_tab_enabled", _resp83, '$.data.storeTabs[?(@.name=="Products")].checked')
    expect(_resp83).status().is_(200)
    expect(_resp83).json('$.data.storeTabs').is_array()
    expect(_resp83).json('$.data.storeTabs.length').equals(4)
    expect(_resp83).json('$.data..storeTabs..name').includes('Posts')
    expect(_resp83).json('$.data..storeTabs..name').includes('Links')
    expect(_resp83).json('$.data..storeTabs..name').includes('Products')
    expect(_resp83).json('$.data..storeTabs..name').includes('Forms')
    expect(_resp83).json('$.data.storeTabs[?(@.name=="Posts")].checked').equals(True)



    # --- step 84: Add MyForm module (POST /store-front/module) ---
    _resp84 = ctx.api.storefront.module(body="""{
    "type": "FORM",
    "direction": "VERTICAL",
    "title": "MyForm",
    "linkType": null,
    "visible": true
}""", app_headers=True, token="token")
    expect(_resp84).json('$.code').equals('200')
    expect(_resp84).json('$.message').equals('success')
    ctx.extract("form_id", _resp84, "$.data.id")
    ctx.extract("user_id", _resp84, "$.data.userId")
    expect(_resp84).json('$.data.title').equals('MyForm')
    expect(_resp84).json('$.data.type').equals('FORM')
    expect(_resp84).json('$.data.direction').equals('VERTICAL')
    expect(_resp84).json('$.data.visible').equals(True)
    expect(_resp84).json('$.data.items').is_array()
    expect(_resp84).json('$.data.items.length').equals(0)
    expect(_resp84).json('$.data.createdAt').is_string()
    expect(_resp84).json('$.data.createdAt').is_not_empty()
    expect(_resp84).json('$.data.updatedAt').is_string()
    expect(_resp84).json('$.data.updatedAt').is_not_empty()



    # --- step 85: create media form (POST /form) ---
    _resp85 = ctx.api.forms.create(body="""{
    "title": "10 images uploaded case",
    "subtitle": "",
    "description": "",
    "confirmationMessage": {
        "title": "Thanks for your submission!",
        "body": "We've received your information and will follow up soon."
    },
    "recipientEmail": "{{UIauto_recipient_email}}",
    "showImage": true,
    "formFields": [
        {
            "timeKey": 1776911693659,
            "title": "media",
            "tooltip": "",
            "description": "",
            "field": "ATTACHMENT",
            "required": true,
            "extensions": {
                "maxUploadCount": 10
            },
            "position": 1
        }
    ]
}



""", app_headers=True, token="token")
    expect(_resp85).json('$.code').equals('200')
    expect(_resp85).json('$.message').equals('success')
    ctx.extract("itemId", _resp85, "$.data.id")
    expect(_resp85).json('$.data').is_object()
    expect(_resp85).json('$.data.title').equals('10 images uploaded case')
    expect(_resp85).json('$.data.id').is_string()
    expect(_resp85).json('$.data.id').is_not_empty()



    # --- step 86: import the media form to the module (PUT /store-front/module-item/{{form_id}}) ---
    _resp86 = ctx.api.storefront.update_module_item(path_vars={"module_item_id": vars.get("form_id", "")}, body="""{
    "id": "{{form_id}}",
    "items": [
        {
            "itemId": "{{itemId}}",
            "position": 1
        }
    ]
}""", app_headers=True, token="token")
    expect(_resp86).json('$.code').equals('200')
    expect(_resp86).json('$.message').equals('success')
    expect(_resp86).json('$.data.title').equals('MyForm')
    expect(_resp86).json('$.data.type').equals('FORM')
    expect(_resp86).json('$.data').is_object()
    expect(_resp86).json('$.data.id').exists()



    # --- step 87: Partner997 Create Catalog (POST /merchant) ---
    _resp87 = ctx.api.merchants.create(body="""{
    "commissionRate": 25,
    "storeName": "auto test",
    "isVisible": true
}""", app_headers=True, token="partner997_auth_token")
    expect(_resp87).json('$.code').equals('200')
    expect(_resp87).json('$.message').equals('success')
    ctx.extract("merchant_id", _resp87, "$.data.id")
    expect(_resp87).status().is_(201)
    expect(_resp87).json('$.data.storeName').equals('auto test')
    expect(_resp87).json('$.data.commissionRate').equals(25)
    expect(_resp87).json('$.data.id').is_string()
    expect(_resp87).json('$.data.id').is_not_empty()



    # --- step 88: Partner997 get shipping-options (GET /merchants/{{merchant_id}}/shipping-options) ---
    _resp88 = ctx.api.merchants.shipping_options_by_merchant_id(path_vars={"merchant_id": vars.get("merchant_id", "")}, app_headers=True, token="partner997_auth_token")
    expect(_resp88).json('$.code').equals('200')
    expect(_resp88).json('$.message').equals('success')
    ctx.extract("shipping_option_id", _resp88, "$.data.items[0].id")
    expect(_resp88).status().is_(200)
    expect(_resp88).json('$.data.items').is_array()
    expect(_resp88).json('$.data.items').is_not_empty()
    expect(_resp88).json('$.data.totalCount').at_least(1)
    expect(_resp88).json('$.data.items[0].title').equals('Flat Shipping')
    expect(_resp88).json('$.data.items[0].shippingFee').equals(4.99)
    expect(_resp88).json('$.data.items[0].isDefault').equals(True)
    expect(_resp88).json('$.data.items[0].id').is_string()
    expect(_resp88).json('$.data.items[0].id').is_not_empty()



    # --- step 89: Patner 997create general product and setting no shipping (POST /v2/products) ---
    _resp89 = ctx.api.products.create_v2(body=r"""{
    "merchantId": "{{merchant_id}}",
    "shippingType": "NO_SHIPPING_REQUIRED",
    "isFeatured": false,
    "commissionRate": null,
    "priceSyncImported": false,
    "additionalShippingFee": 0,
    "returnPolicyApplied": true,
    "title": "auto-test-997-default-product",
    "bodyHtml": "<p class=\"katana__paragraph katana__paragraph--align-left\" dir=\"ltr\"><br></p>",
    "status": "ACTIVE",
    "isUsed": "NWT",
    "taxJarCategory": "",
    "platform": "PEAR",
    "autoFulfill": false,
    "options": [
        {
            "name": "Title",
            "values": [
                "Default Title"
            ],
            "images": []
        }
    ],
    "variants": [
        {
            "inventoryQuantity": 10000,
            "price": 0,
            "priceAnchor": 0,
            "option": {
                "option1": "Default Title"
            },
            "weightUnit": "lb"
        }
    ],
    "excludeFromPostSync": false,
    "isTipEnabled": false,
    "listingType": "REGULAR",
    "catalogCommissionRate": 25,
    "shippingOptions": [
        {
            "id": "{{shipping_option_id}}",
            "catalogId": "{{merchant_id}}",
            "title": "Flat Shipping",
            "shippingFee": 0,
            "deliveryTime": [
                0,
                5
            ],
            "enableFreeShippingThreshold": false,
            "freeShippingThreshold": 0,
            "note": null,
            "isDefault": true,
            "weightBasedShippingRates": null,
            "enableWeightBasedShippingRates": false,
            "priceBasedShippingRates": null,
            "enablePriceBasedShippingRates": false,
            "profileName": null,
            "from": "PEAR",
            "additionalShippingFee": 0,
            "enableAdditionalShippingFee": false
        }
    ],
    "deliveryMethod": "SHIPPING",
    "isReturnPolicyAllowed": false,
    "thirdPartyDeliveryMessage": "",
    "taxEnable": false,
    "customTaxRate": null,
    "earliestTime": "2026-04-22T10:14:22.527Z",
    "styleSettings": {
        "recentUsedColors": [
            "#ffffff"
        ]
    },
    "isVariantPriceDisplayEnabled": false,
    "stopSellingAfterDisplay": "",
    "extraInfo": {
        "businessTimezone": "America/Los_Angeles"
    },
    "overrideEventTax": false,
    "bodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
    "images": [
        {
            "mediaType": "IMAGE",
            "mediaSrc": null,
            "mediaDuration": 0,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1776850213/uploaded_images/z7whekb6m8ycqyswvuzt.jpg",
            "height": 855,
            "width": 1280,
            "source": "UPLOAD",
            "position": 1,
            "setThumbnail": true,
            "origin": {
                "width": 1280,
                "height": 855,
                "position": 1
            },
            "productImageType": "PRODUCT"
        }
    ],
    "isMultipleDaysPassEnabled": false
}""", app_headers=True, token="partner997_auth_token")
    expect(_resp89).json('$.code').equals('200')
    expect(_resp89).json('$.message').equals('success')
    expect(_resp89).json('$.data.title').equals('auto-test-997-default-product')



    # --- step 90: Create coseller 998 on admin tools (POST /users/tool/external-user-import/promoter) ---
    _resp90 = ctx.api.admin.users_tool_external_user_import_promoter(body="""{
  "allowSyncResalePosts": true,
  "email": "{{UIauto_coseller_email}}",
  "partnerId": "{{user_id}}"
}""", app_headers=True, token="admin_token")
    expect(_resp90).json('$.code').equals('200')
    expect(_resp90).json('$.message').equals('success')
    # 注意: 同 step 8 / 11 —— 原始集合的 pm.environment.set("password", res.data.password)
    # 是死写，后续节点用字面量 MD5("Happy123")。不要覆盖 {{password}}。
    expect(_resp90).status().is_(201)
    expect(_resp90).json('$.data.password').is_string()
    expect(_resp90).json('$.data.password').is_not_empty()



    # --- step 91: Admin search coseller 998 (POST /users/search) ---
    _resp91 = ctx.api.admin.users_search(body="""{
    "query": "{{UIauto_coseller_email}}",
    "filter": {
        "userRoles": [
            "PROMOTER",
            "BUSINESS_PARTNER"
        ],
        "userType": "ALL"
    },
    "pageSize": 100,
    "pageNumber": 1
}""", app_headers=True, token="admin_token")
    expect(_resp91).json('$.code').equals('200')
    expect(_resp91).json('$.message').equals('success')
    ctx.extract("user_coseller_id", _resp91, "$.data.items[0].id")



    # --- step 92: set coseller998 password (PUT /users/{{user_coseller_id}}/password) ---
    _resp92 = ctx.api.admin.users_password(path_vars={"user_id": vars.get("user_coseller_id", "")}, body="""{"password":"{{password}}"}""", app_headers=True, token="admin_token")
    expect(_resp92).json('$.code').equals('200')
    expect(_resp92).json('$.message').equals('success')



    # --- step 93: Coseller 998 login (POST /auth/sign-in) ---
    _resp93 = ctx.api.auth.sign_in(body="""{
    "email": "{{UIauto_coseller_email}}",
    "password": "{{password}}"

}""", app_headers=True, token="token")
    expect(_resp93).json('$.code').equals('200')
    expect(_resp93).json('$.message').equals('success')
    ctx.extract("coseller_auth_token", _resp93, "$.data.token")



    # --- step 94: update the coseller 998's store shop url to autoshop (PUT /store-front) ---
    _resp94 = ctx.api.storefront.update(body="""{
    "userInfo": {
        "storeName": "{{coseller_storeName}}",
        "logo": null,
        "backgroundSource": {
            "width": 375,
            "height": 375,
            "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1764821680/setting/wrbmwobccxtbsy1e79h0.webp"
        },
        "description": "",
        "subTitle": "",
        "socialMedias": [],
        "storeFront": {
            "storeTabs": [
                {
                    "name": "Posts",
                    "checked": false
                },
                {
                    "name": "Links",
                    "checked": false
                },
                {
                    "name": "Products",
                    "checked": false
                },
                {
                    "name": "Forms",
                    "checked": false
                }
            ]
        },
        "vanityUrl": "{{coseller_vanityUrl}}"
    }
}""", app_headers=True, token="coseller_auth_token")
    expect(_resp94).json('$.code').equals('200')
    expect(_resp94).json('$.message').equals('success')



    # --- step 95: Set the Coseller all tabs are visible  (PUT /store-front/layout) ---
    _resp95 = ctx.api.storefront.layout(body="""{
    "storeTabs": [
        {
            "name": "Posts",
            "checked": true
        },
        {
            "name": "Links",
            "checked": true
        },
        {
            "name": "Forms",
            "checked": true
        }
    ]
}""", app_headers=True, token="coseller_auth_token")
    expect(_resp95).json('$.code').equals('200')
    expect(_resp95).json('$.message').equals('success')
    # 注：循环 tabName='Posts'
    expect(_resp95).json('$.data.storeTabs[?(@.name=="Posts")]').exists()
    # 注：循环 tabName='Links'
    expect(_resp95).json('$.data.storeTabs[?(@.name=="Links")]').exists()
    # 注：循环 tabName='Forms'
    expect(_resp95).json('$.data.storeTabs[?(@.name=="Forms")]').exists()
    # 注：循环 tabName='Posts'
    expect(_resp95).json('$.data.storeTabs[?(@.name=="Posts")].checked').equals(True)
    # 注：循环 tabName='Links'
    expect(_resp95).json('$.data.storeTabs[?(@.name=="Links")].checked').equals(True)
    # 注：循环 tabName='Forms'
    expect(_resp95).json('$.data.storeTabs[?(@.name=="Forms")].checked').equals(True)



    # --- step 96: Authorize Product 999 to 998 (PUT /promote-invitation/{{user_coseller_id}}) ---
    _resp96 = ctx.api.promoters.authorize_product(path_vars={"target_user_id": vars.get("user_coseller_id", "")}, body="""[
    {
        "merchantId": "{{merchant_id_autotest}}",
        "merchantStoreName": "auto test",
        "defaultCommissionRate": 25,
        "merchantPlatform": "PEAR",
        "hasAccess": true,
        "isSetCommission": false,
        "commissionRate": null
    }
]""", app_headers=True, token="token")
    expect(_resp96).json('$.code').equals('200')
    expect(_resp96).json('$.message').equals('success')



    # --- step 97: Authorize Product 999 to 997 (PUT /promote-invitation/{{user_partner997_id}}) ---
    _resp97 = ctx.api.promoters.authorize_product(path_vars={"target_user_id": vars.get("user_partner997_id", "")}, body="""[
    {
        "merchantId": "{{merchant_id_autotest}}",
        "merchantStoreName": "auto test",
        "defaultCommissionRate": 25,
        "merchantPlatform": "PEAR",
        "hasAccess": true,
        "isSetCommission": false,
        "commissionRate": null
    }
]""", app_headers=True, token="token")
    expect(_resp97).json('$.code').equals('200')
    expect(_resp97).json('$.message').equals('success')

    # ======================================================================
    # MISSING STEPS MIGRATED FROM APIFOX (items 100-137)
    # ======================================================================



    # --- step 98: set coseller998 password (PUT users/{{user_coseller_id}}/password) ---
    # NOTE: steps 100-105 duplicate the coseller-998 setup already performed at steps 92-99 in the source Apifox collection; kept for 1:1 fidelity. Password uses the existing {{password}} placeholder (no literal).
    _resp98 = ctx.api.admin.users_password(path_vars={"user_id": "{{user_coseller_id}}"}, body="""{"password":"{{password}}"}""", token="admin_token", app_headers=True)
    expect(_resp98).json('$.code').equals('200')
    expect(_resp98).json('$.message').equals('success')



    # --- step 99: Coseller 998 login (POST auth/sign-in) ---
    # NOTE: Password uses the existing {{password}} placeholder (no literal).
    _resp99 = ctx.api.auth.sign_in(body="""{
        "email": "{{UIauto_coseller_email}}",
        "password": "{{password}}"
    
    }""", app_headers=True)
    expect(_resp99).json('$.code').equals('200')
    expect(_resp99).json('$.message').equals('success')
    # ⚠️ 不要在此提取 "token"：原始集合里 `token` 只在「Partner 999 login」(node[25]) 设过一次，
    #    998 登录（node[96]）只写 `coseller_auth_token`。迁移器多写的这一句会把 999 的
    #    token 覆盖成 998 的，导致后续以 {{token}} 发出的请求（Authorize Product 999 to 998/997、
    #    GET /product-event/default-catalog 等）实际以 998 身份执行——default-catalog 会因此
    #    返回 998 的默认 catalog，而不是 999 的。已按集合语义移除此提取。
    ctx.extract("coseller_auth_token", _resp99, "$.data.token")



    # --- step 100: update the coseller 998's store shop url to autoshop (PUT store-front) ---
    # NOTE: Uses the dedicated {{coseller_auth_token}} variable (set during the coseller-998 login at step 101), not the generic `token`.
    _resp100 = ctx.api.storefront.update(body="""{
        "userInfo": {
            "storeName": "{{coseller_storeName}}",
            "logo": null,
            "backgroundSource": {
                "width": 375,
                "height": 375,
                "src": "https://res.cloudinary.com/dr9io1zjv/image/upload/v1764821680/setting/wrbmwobccxtbsy1e79h0.webp"
            },
            "description": "",
            "subTitle": "",
            "socialMedias": [],
            "storeFront": {
                "storeTabs": [
                    {
                        "name": "Posts",
                        "checked": false
                    },
                    {
                        "name": "Links",
                        "checked": false
                    },
                    {
                        "name": "Products",
                        "checked": false
                    },
                    {
                        "name": "Forms",
                        "checked": false
                    }
                ]
            },
            "vanityUrl": "{{coseller_vanityUrl}}"
        }
    }""", token="coseller_auth_token", app_headers=True)
    expect(_resp100).json('$.code').equals('200')
    expect(_resp100).json('$.message').equals('success')



    # --- step 101: Set the Coseller all tabs are visible  (PUT store-front/layout) ---
    # NOTE: Uses the dedicated {{coseller_auth_token}} variable (set during the coseller-998 login at step 101).
    _resp101 = ctx.api.storefront.layout(body="""{
        "storeTabs": [
            {
                "name": "Posts",
                "checked": true
            },
            {
                "name": "Links",
                "checked": true
            },
            {
                "name": "Forms",
                "checked": true
            }
        ]
    }""", token="coseller_auth_token", app_headers=True)
    expect(_resp101).json('$.code').equals('200')
    expect(_resp101).json('$.message').equals('success')
    expect(_resp101).status().is_(200)
    expect(_resp101).json('$.data.storeTabs').is_array()
    expect(_resp101).json('$.data.storeTabs.length').equals(4)
    expect(_resp101).json('$.data..storeTabs..name').includes('Posts')
    expect(_resp101).json('$.data..storeTabs..name').includes('Links')
    expect(_resp101).json('$.data..storeTabs..name').includes('Products')
    expect(_resp101).json('$.data..storeTabs..name').includes('Forms')
    expect(_resp101).json('$.data.storeTabs[?(@.name=="Posts")].checked').equals(True)



    # --- step 102: Authorize Product 999 to 998 (PUT promote-invitation/{{user_coseller_id}}) ---
    _resp102 = ctx.api.promoters.authorize_product(path_vars={"target_user_id": "{{user_coseller_id}}"}, body="""[
        {
            "merchantId": "{{merchant_id_autotest}}",
            "merchantStoreName": "auto test",
            "defaultCommissionRate": 25,
            "merchantPlatform": "PEAR",
            "hasAccess": true,
            "isSetCommission": false,
            "commissionRate": null
        }
    ]""", token="token", app_headers=True)
    expect(_resp102).json('$.code').equals('200')
    expect(_resp102).json('$.message').equals('success')



    # --- step 103: Authorize Product 999 to 997 (PUT promote-invitation/{{user_partner997_id}}) ---
    _resp103 = ctx.api.promoters.authorize_product(path_vars={"target_user_id": "{{user_partner997_id}}"}, body="""[
        {
            "merchantId": "{{merchant_id_autotest}}",
            "merchantStoreName": "auto test",
            "defaultCommissionRate": 25,
            "merchantPlatform": "PEAR",
            "hasAccess": true,
            "isSetCommission": false,
            "commissionRate": null
        }
    ]""", token="token", app_headers=True)
    expect(_resp103).json('$.code').equals('200')
    expect(_resp103).json('$.message').equals('success')



    # --- step 104: delay (no-op, framework style) ---
    # NOTE: original Apifox collection had a delay here; removed per framework style (no time.sleep).



    # --- step 105: get the event catalog id (GET product-event/default-catalog) ---
    _resp105 = ctx.api.events.default_catalog(token="token", app_headers=True)
    expect(_resp105).json('$.code').equals('200')
    expect(_resp105).json('$.message').equals('success')
    # ⚠️ 响应里没有 curatorId 这个字段（实测 200 响应为 id/storeName/description/logo/bio/
    #    commissionRate/shippingFee/type/returnPolicy/returnPolicyTag/tier/**userId**/...），
    #    原路径 $.data.curatorId 恒为 None → {{curator_id}} 渲染成空/字面量。
    #    curator_id 的用途是 PATCH users/tool/feature-flags?userId={{curator_id}} 与
    #    productOwnerId，需要一个「用户 id」，即 $.data.userId（默认 catalog 的属主）。
    ctx.extract("curator_id", _resp105, "$.data.userId")
    ctx.extract("catalog_id", _resp105, "$.data.id")
    # 原 Apifox 工程里 eventcatalog_id 由一条 SQL（database）步骤产出：
    #   select id from "Merchant" where user_id='{{user_id}}' and catalog_type='EVENT'
    # 本集合是「- no sql」导出，该步骤被整体剪掉，所以 eventcatalog_id 在 vars.yaml 里
    # 只是个空串槽位（body 里 7 处 merchantId / id 引用它 → 全部渲染成空）。
    # 经用户确认，改用本请求的响应取值：GET /product-event/default-catalog 的 $.data.id。
    # （Apifox 原始后置脚本同样是把 responseData.data.id 写入环境变量。）
    ctx.extract("eventcatalog_id", _resp105, "$.data.id")
    expect(_resp105).json('$.data').is_object()
    expect(_resp105).json('$.data.id').is_string()
    expect(_resp105).json('$.data.id').is_not_empty()



    # --- pre-step 106: 重新生成事件日期与标题（原 Apifox 该请求的 prerequest 脚本） ---
    # 原 JS 用 new Date() 计算：current_iso_date = toISOString()（UTC）、
    # startDateDisplay = 本地今天（YYYY-MM-DD）、event_title = 固定标题。
    # 不设置时这些占位符会渲染成空串（Release.yaml 中为 ''），导致 duplicate 请求报错。
    _now106 = _dt.datetime.now()
    _utc106 = _dt.datetime.now(_dt.timezone.utc)
    vars["current_iso_date"] = _utc106.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    vars["startDateDisplay"] = _now106.strftime("%Y-%m-%d")
    vars["event_title"] = "event-for-ui-auto-venue-map"

    # --- step 106: duplicate event for venue map (POST product-event/v2/duplicate) ---
    # NOTE: eventcatalog_id 已由 step 105（GET /product-event/default-catalog 的 $.data.id）产出。
    #       仍未解决：body 里 tickets[].copyFromId 引用的 ticket_id_General_Admission*,
    #       venue_map_variant_id_General_Admission* / venue_map_productId_* /
    #       venue_map_promoterProductId_* / categoryId_General_Admission* ——
    #       这些变量在本仓库全文件无任何生产方（既无 ctx.extract 也无 vars[...] 赋值），
    #       来源是另一份 Apifox 集合，需补源后才能修。
    _resp106 = ctx.api.events.v2_duplicate(body=r"""{
        "title": "{{event_title}}",
        "curatorId": "{{catalog_id}}",
        "description": "",
        "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
        "startDate": "{{current_iso_date}}",
        "endDate": null,
        "venue": "Test venue · West Mound Street, Columbus, OH",
        "location": "Test venue · West Mound Street, Columbus, OH",
        "status": "UPCOMING",
        "isTaxEnabled": false,
        "taxConfig": null,
        "mediaTextConfig": {
            "headline": "Missed our last event?",
            "subtitle": "Here's a lil recap of our last event👇",
            "align": "center"
        },
        "poster": {
            "height": 2048,
            "mediaDuration": 0,
            "mediaType": "IMAGE",
            "position": 0,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "width": 3072
        },
        "startDateDisplay": "{{startDateDisplay}}",
        "note": "auto test",
        "timezone": {
            "timeZoneId": "America/New_York",
            "timeZoneName": "Eastern Daylight Time",
            "dstOffset": 3600,
            "rawOffset": -18000
        },
        "isAddressRevealEnabled": false,
        "isAddressHidden": false,
        "messageInfo": {
            "cooldownMinutes": 15,
            "emailMaxLimit": 5,
            "smsMaxLimit": 3
        },
        "platform": "PEAR",
        "creationStep": "COMPLETED",
        "extraInfo": null,
        "locationDetails": {
            "city": "Columbus",
            "country": "US",
            "line1": "Test venue · West Mound Street",
            "line2": "",
            "placeId": null,
            "state": "OH",
            "stateName": "Ohio",
            "stripeLocationId": null,
            "zipcode": null
        },
        "country": "US",
        "state": "OH",
        "autoReplace": false,
        "lineupTransactionId": null,
        "lineupTransactionStatus": null,
        "autoPayLineupStatus": "PENDING",
        "excludeOnsiteSalesFromReport": false,
        "showFeesBreakdown": false,
        "showBuyerInfoOnVenueMap": false,
        "venueMapId": null,
        "ticketHubInfo": null,
        "readOnlyFields": [],
        "medias": [],
        "tickets": [
            {
                "id": "{{ticket_id_General_Admission_02}}",
                "remote_id": null,
                "platform": "PEAR",
                "createdAt": "2026-08-21T08:59:12.986Z",
                "updatedAt": "2026-08-21T08:59:13.052Z",
                "merchantId": "{{eventcatalog_id}}",
                "title": "General Admission 02",
                "bodyHtml": "",
                "originalBodyHtml": "",
                "isBodyHtmlOverridden": false,
                "bodyText": "",
                "handle": null,
                "productType": "",
                "publishedAt": "2026-08-21T08:59:13.025Z",
                "publishedScope": "",
                "status": "ACTIVE",
                "externalStatus": "ACTIVE",
                "followExternalStatus": false,
                "tags": [],
                "templateSuffix": null,
                "vendor": "Pear",
                "syncAt": null,
                "deletedAt": null,
                "delisted": false,
                "excludedByImportingTag": false,
                "isFeatured": false,
                "featuredScore": null,
                "inventoryQuantity": 10000,
                "inventoryQuantityOriginal": 10000,
                "soldQuantity": 0,
                "priceDisplay": 112.22,
                "priceDisplayAnchor": 0,
                "priceMin": 112.22,
                "priceMinAnchor": 0,
                "priceMax": 112.22,
                "priceMaxAnchor": 0,
                "priceImportedMin": 0,
                "priceImportedMax": 0,
                "imageCount": 1,
                "isUsed": "NWT",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "deliveryTime": [
                    0,
                    5
                ],
                "returnPolicyApplied": true,
                "isAvailable": true,
                "commissionRate": 7,
                "textForShare": null,
                "priceSyncImported": false,
                "coverImage": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "useEventPosterAsCover": true,
                "reviewCount": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "displayReviews": true,
                "links": null,
                "taxEnable": false,
                "taxJarCategory": null,
                "overrideEventTax": false,
                "customTaxRate": null,
                "subscriptionPlanId": null,
                "reviewRedirectProductId": null,
                "reviewSummary": null,
                "customFieldsInfo": null,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "date": "Sat Apr 24, 2032 EDT",
                    "event": "Auto-Test-post-setting",
                    "venue": "Test venue · West Mound Street, Columbus, OH",
                    "lineup": [],
                    "poster": {
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072,
                        "height": 2048,
                        "position": 0,
                        "mediaType": "IMAGE",
                        "mediaDuration": 0
                    },
                    "status": "UPCOMING",
                    "location": "Test venue · West Mound Street, Columbus, OH",
                    "eventNote": "auto test",
                    "startDate": "2032-04-24T04:00:00.000Z",
                    "timeZoneId": "America/New_York",
                    "isAddressHidden": false,
                    "addressRevealConfig": null
                },
                "ticketHubInfo": null,
                "customizedFields": [],
                "bodyJson": null,
                "shippingOptions": null,
                "shippingNote": null,
                "autoFulfill": true,
                "eventId": "{{created_event_id}}",
                "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",
                "copyFromId": "{{ticket_id_General_Admission_02}}",
                "stopSellingAfter": null,
                "stopSellingAfterDisplay": null,
                "deliveryMethod": "QR_CODE",
                "thirdPartyDeliveryMessage": null,
                "isMultipleDaysPassEnabled": false,
                "isVenueUnitEnabled": false,
                "venueUnitCategoryId": null,
                "multipleDaysPass": null,
                "isPickupEtaEnabled": null,
                "eventMatchingRules": null,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "allowAtDoorSales": false,
                "isProductFormEnabled": false,
                "isVariantPriceDisplayEnabled": false,
                "isTipEnabled": false,
                "hideFees": false,
                "isPlatformFeeConfigCustomized": false,
                "isVariantPlatformFeeConfigCustomized": false,
                "transactionFeeConfig": {
                    "baseConfig": {
                        "unitFixedFee": 1,
                        "unitPercentageFee": 0.1
                    }
                },
                "transactionFeeRebateConfig": {
                    "baseConfig": {
                        "unitFixedFee": 0,
                        "unitPercentageFee": 0
                    }
                },
                "transactionCustomFeeConfig": null,
                "overrideEventCustomFee": false,
                "isInclusionsEnabled": false,
                "images": [
                    {
                        "id": "95ed387c-1f0c-43f9-ab26-29c61ca31176",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.052Z",
                        "updatedAt": "2026-08-21T08:59:13.052Z",
                        "height": 1000,
                        "width": 1000,
                        "position": 1,
                        "productId": "{{ticket_id_General_Admission_02}}",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "variantIds": [],
                        "mediaType": "IMAGE",
                        "mediaSrc": null,
                        "mediaDuration": 0,
                        "contributedBy": 3,
                        "contributorId": null,
                        "productImageType": "PRODUCT",
                        "source": null
                    }
                ],
                "options": [
                    {
                        "name": "Title",
                        "images": [
                            {
                                "value": "Default Title",
                                "image": null
                            }
                        ]
                    }
                ],
                "variants": [
                    {
                        "id": "{{variant_id_General_Admission_02}}",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.052Z",
                        "updatedAt": "2026-08-21T08:59:13.052Z",
                        "compareAtPrice": null,
                        "fulfillmentService": "manual",
                        "grams": 0,
                        "imageId": null,
                        "imageIds": [],
                        "inventoryItemId": null,
                        "inventoryManagement": "Pear",
                        "inventoryPolicy": "DENY",
                        "isInventoryQuantityUnlimited": false,
                        "inventoryQuantity": 10000,
                        "inventoryQuantityOriginal": 10000,
                        "soldQuantity": 0,
                        "option": {
                            "option1": "Default Title"
                        },
                        "position": 1,
                        "price": "112.22",
                        "priceAnchor": "0",
                        "priceImported": "0.00",
                        "productId": "{{ticket_id_General_Admission_02}}",
                        "sku": "",
                        "taxCode": null,
                        "taxable": true,
                        "title": "Default Title",
                        "weight": null,
                        "weightUnit": null,
                        "platform": null,
                        "fees": 12.22,
                        "transactionFee": {
                            "customFee": 0,
                            "platformFee": 12.22,
                            "customFeeBreakdown": {
                                "TAX": {
                                    "index": 0,
                                    "title": "Taxes",
                                    "itemFee": 0,
                                    "unitFixedFee": 0,
                                    "unitPercentageFee": 0
                                }
                            },
                            "transactionItemFee": 12.22
                        },
                        "ticketPrice": 100,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": 0,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": 0,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "transactionFeeConfig": null,
                        "transactionFeeRebateConfig": null,
                        "image": null
                    }
                ],
                "inclusions": [],
                "productForm": null
            },
            {
                "id": "{{ticket_id_General_Admission_01}}",
                "remote_id": null,
                "platform": "PEAR",
                "createdAt": "2026-08-21T08:59:12.985Z",
                "updatedAt": "2026-08-21T08:59:13.080Z",
                "merchantId": "{{eventcatalog_id}}",
                "title": "General Admission 01",
                "bodyHtml": "",
                "originalBodyHtml": "",
                "isBodyHtmlOverridden": false,
                "bodyText": "",
                "handle": null,
                "productType": "",
                "publishedAt": "2026-08-21T08:59:13.032Z",
                "publishedScope": "",
                "status": "ACTIVE",
                "externalStatus": "ACTIVE",
                "followExternalStatus": false,
                "tags": [],
                "templateSuffix": null,
                "vendor": "Pear",
                "syncAt": null,
                "deletedAt": null,
                "delisted": false,
                "excludedByImportingTag": false,
                "isFeatured": false,
                "featuredScore": null,
                "inventoryQuantity": 10000,
                "inventoryQuantityOriginal": 10000,
                "soldQuantity": 0,
                "priceDisplay": 67.77,
                "priceDisplayAnchor": 0,
                "priceMin": 67.77,
                "priceMinAnchor": 0,
                "priceMax": 67.77,
                "priceMaxAnchor": 0,
                "priceImportedMin": 0,
                "priceImportedMax": 0,
                "imageCount": 1,
                "isUsed": "NWT",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "deliveryTime": [
                    0,
                    5
                ],
                "returnPolicyApplied": true,
                "isAvailable": true,
                "commissionRate": 7,
                "textForShare": null,
                "priceSyncImported": false,
                "coverImage": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "useEventPosterAsCover": true,
                "reviewCount": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "displayReviews": true,
                "links": null,
                "taxEnable": false,
                "taxJarCategory": null,
                "overrideEventTax": false,
                "customTaxRate": null,
                "subscriptionPlanId": null,
                "reviewRedirectProductId": null,
                "reviewSummary": null,
                "customFieldsInfo": null,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "date": "Sat Apr 24, 2032 EDT",
                    "event": "Auto-Test-post-setting",
                    "venue": "Test venue · West Mound Street, Columbus, OH",
                    "lineup": [],
                    "poster": {
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072,
                        "height": 2048,
                        "position": 0,
                        "mediaType": "IMAGE",
                        "mediaDuration": 0
                    },
                    "status": "UPCOMING",
                    "location": "Test venue · West Mound Street, Columbus, OH",
                    "eventNote": "auto test",
                    "startDate": "2032-04-24T04:00:00.000Z",
                    "timeZoneId": "America/New_York",
                    "isAddressHidden": false,
                    "addressRevealConfig": null
                },
                "ticketHubInfo": null,
                "customizedFields": [],
                "bodyJson": null,
                "shippingOptions": null,
                "shippingNote": null,
                "autoFulfill": true,
                "eventId": "{{created_event_id}}",
                "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",
                "copyFromId": "{{ticket_id_General_Admission_01}}",
                "stopSellingAfter": null,
                "stopSellingAfterDisplay": null,
                "deliveryMethod": "QR_CODE",
                "thirdPartyDeliveryMessage": null,
                "isMultipleDaysPassEnabled": false,
                "isVenueUnitEnabled": false,
                "venueUnitCategoryId": null,
                "multipleDaysPass": null,
                "isPickupEtaEnabled": null,
                "eventMatchingRules": null,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "allowAtDoorSales": false,
                "isProductFormEnabled": false,
                "isVariantPriceDisplayEnabled": false,
                "isTipEnabled": false,
                "hideFees": false,
                "isPlatformFeeConfigCustomized": false,
                "isVariantPlatformFeeConfigCustomized": false,
                "transactionFeeConfig": {
                    "baseConfig": {
                        "unitFixedFee": 1,
                        "unitPercentageFee": 0.1
                    }
                },
                "transactionFeeRebateConfig": {
                    "baseConfig": {
                        "unitFixedFee": 0,
                        "unitPercentageFee": 0
                    }
                },
                "transactionCustomFeeConfig": null,
                "overrideEventCustomFee": false,
                "isInclusionsEnabled": false,
                "images": [
                    {
                        "id": "c3711955-0d20-460b-8f65-d30fc691b6c8",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.080Z",
                        "updatedAt": "2026-08-21T08:59:13.080Z",
                        "height": 1000,
                        "width": 1000,
                        "position": 1,
                        "productId": "{{ticket_id_General_Admission_01}}",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "variantIds": [],
                        "mediaType": "IMAGE",
                        "mediaSrc": null,
                        "mediaDuration": 0,
                        "contributedBy": 3,
                        "contributorId": null,
                        "productImageType": "PRODUCT",
                        "source": null
                    }
                ],
                "options": [
                    {
                        "name": "Title",
                        "images": [
                            {
                                "value": "Default Title",
                                "image": null
                            }
                        ]
                    }
                ],
                "variants": [
                    {
                        "id": "{{variant_id_General_Admission_01}}",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.080Z",
                        "updatedAt": "2026-08-21T08:59:13.080Z",
                        "compareAtPrice": null,
                        "fulfillmentService": "manual",
                        "grams": 0,
                        "imageId": null,
                        "imageIds": [],
                        "inventoryItemId": null,
                        "inventoryManagement": "Pear",
                        "inventoryPolicy": "DENY",
                        "isInventoryQuantityUnlimited": false,
                        "inventoryQuantity": 10000,
                        "inventoryQuantityOriginal": 10000,
                        "soldQuantity": 0,
                        "option": {
                            "option1": "Default Title"
                        },
                        "position": 1,
                        "price": "67.77",
                        "priceAnchor": "0",
                        "priceImported": "0.00",
                        "productId": "{{ticket_id_General_Admission_01}}",
                        "sku": "",
                        "taxCode": null,
                        "taxable": true,
                        "title": "Default Title",
                        "weight": null,
                        "weightUnit": null,
                        "platform": null,
                        "fees": 7.77,
                        "transactionFee": {
                            "customFee": 0,
                            "platformFee": 7.77,
                            "customFeeBreakdown": {
                                "TAX": {
                                    "index": 0,
                                    "title": "Taxes",
                                    "itemFee": 0,
                                    "unitFixedFee": 0,
                                    "unitPercentageFee": 0
                                }
                            },
                            "transactionItemFee": 7.77
                        },
                        "ticketPrice": 60,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": 0,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": 0,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "transactionFeeConfig": null,
                        "transactionFeeRebateConfig": null,
                        "image": null
                    }
                ],
                "inclusions": [],
                "productForm": null
            },
            {
                "id": "{{ticket_id_General_Admission}}",
                "remote_id": null,
                "platform": "PEAR",
                "createdAt": "2026-08-21T08:59:12.984Z",
                "updatedAt": "2026-08-21T08:59:13.103Z",
                "merchantId": "{{eventcatalog_id}}",
                "title": "General Admission",
                "bodyHtml": "",
                "originalBodyHtml": "",
                "isBodyHtmlOverridden": false,
                "bodyText": "",
                "handle": null,
                "productType": "",
                "publishedAt": "2026-08-21T08:59:13.037Z",
                "publishedScope": "",
                "status": "ACTIVE",
                "externalStatus": "ACTIVE",
                "followExternalStatus": false,
                "tags": [],
                "templateSuffix": null,
                "vendor": "Pear",
                "syncAt": null,
                "deletedAt": null,
                "delisted": false,
                "excludedByImportingTag": false,
                "isFeatured": false,
                "featuredScore": null,
                "inventoryQuantity": 3000,
                "inventoryQuantityOriginal": 3000,
                "soldQuantity": 0,
                "priceDisplay": 0,
                "priceDisplayAnchor": 0,
                "priceMin": 0,
                "priceMinAnchor": 0,
                "priceMax": 0,
                "priceMaxAnchor": 0,
                "priceImportedMin": 0,
                "priceImportedMax": 0,
                "imageCount": 1,
                "isUsed": "NWT",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "deliveryTime": [
                    0,
                    5
                ],
                "returnPolicyApplied": true,
                "isAvailable": true,
                "commissionRate": 7,
                "textForShare": null,
                "priceSyncImported": false,
                "coverImage": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "useEventPosterAsCover": true,
                "reviewCount": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "displayReviews": true,
                "links": null,
                "taxEnable": false,
                "taxJarCategory": null,
                "overrideEventTax": false,
                "customTaxRate": null,
                "subscriptionPlanId": null,
                "reviewRedirectProductId": null,
                "reviewSummary": null,
                "customFieldsInfo": null,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "date": "Sat Apr 24, 2032 EDT",
                    "event": "Auto-Test-post-setting",
                    "venue": "Test venue · West Mound Street, Columbus, OH",
                    "lineup": [],
                    "poster": {
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072,
                        "height": 2048,
                        "position": 0,
                        "mediaType": "IMAGE",
                        "mediaDuration": 0
                    },
                    "status": "UPCOMING",
                    "location": "Test venue · West Mound Street, Columbus, OH",
                    "eventNote": "auto test",
                    "startDate": "2032-04-24T04:00:00.000Z",
                    "timeZoneId": "America/New_York",
                    "isAddressHidden": false,
                    "addressRevealConfig": null
                },
                "ticketHubInfo": null,
                "customizedFields": [],
                "bodyJson": null,
                "shippingOptions": null,
                "shippingNote": null,
                "autoFulfill": true,
                "eventId": "{{created_event_id}}",
                "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",
                "copyFromId": "{{ticket_id_General_Admission}}",
                "stopSellingAfter": null,
                "stopSellingAfterDisplay": null,
                "deliveryMethod": "QR_CODE",
                "thirdPartyDeliveryMessage": null,
                "isMultipleDaysPassEnabled": false,
                "isVenueUnitEnabled": false,
                "venueUnitCategoryId": null,
                "multipleDaysPass": null,
                "isPickupEtaEnabled": null,
                "eventMatchingRules": null,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "allowAtDoorSales": false,
                "isProductFormEnabled": false,
                "isVariantPriceDisplayEnabled": false,
                "isTipEnabled": false,
                "hideFees": false,
                "isPlatformFeeConfigCustomized": false,
                "isVariantPlatformFeeConfigCustomized": false,
                "transactionFeeConfig": {
                    "baseConfig": {
                        "unitFixedFee": 1,
                        "unitPercentageFee": 0.1
                    }
                },
                "transactionFeeRebateConfig": {
                    "baseConfig": {
                        "unitFixedFee": 0,
                        "unitPercentageFee": 0
                    }
                },
                "transactionCustomFeeConfig": null,
                "overrideEventCustomFee": false,
                "isInclusionsEnabled": false,
                "images": [
                    {
                        "id": "9564cc3d-78cc-4c92-90bb-df92227b92fb",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.103Z",
                        "updatedAt": "2026-08-21T08:59:13.103Z",
                        "height": 1000,
                        "width": 1000,
                        "position": 1,
                        "productId": "{{ticket_id_General_Admission}}",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "variantIds": [],
                        "mediaType": "IMAGE",
                        "mediaSrc": null,
                        "mediaDuration": 0,
                        "contributedBy": 3,
                        "contributorId": null,
                        "productImageType": "PRODUCT",
                        "source": null
                    }
                ],
                "options": [
                    {
                        "name": "Time",
                        "images": [
                            {
                                "value": "5 people",
                                "image": null
                            },
                            {
                                "value": "7 people",
                                "image": null
                            },
                            {
                                "value": "9 people",
                                "image": null
                            }
                        ]
                    }
                ],
                "variants": [
                    {
                        "id": "{{variant_id_General_Admission}}",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.103Z",
                        "updatedAt": "2026-08-21T08:59:13.103Z",
                        "compareAtPrice": null,
                        "fulfillmentService": "manual",
                        "grams": 0,
                        "imageId": null,
                        "imageIds": [],
                        "inventoryItemId": null,
                        "inventoryManagement": "Pear",
                        "inventoryPolicy": "DENY",
                        "isInventoryQuantityUnlimited": false,
                        "inventoryQuantity": 1000,
                        "inventoryQuantityOriginal": 1000,
                        "soldQuantity": 0,
                        "option": {
                            "option1": "5 people"
                        },
                        "position": 1,
                        "price": 0,
                        "priceAnchor": "0",
                        "priceImported": "0.00",
                        "productId": "{{ticket_id_General_Admission}}",
                        "sku": "",
                        "taxCode": null,
                        "taxable": true,
                        "title": "5 people",
                        "weight": null,
                        "weightUnit": null,
                        "platform": null,
                        "fees": 0,
                        "transactionFee": {
                            "customFee": 0,
                            "platformFee": 0,
                            "customFeeBreakdown": {},
                            "transactionItemFee": 0
                        },
                        "ticketPrice": 0,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": 0,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": 0,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "transactionFeeConfig": null,
                        "transactionFeeRebateConfig": null,
                        "image": null
                    },
                    {
                        "id": null,
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.103Z",
                        "updatedAt": "2026-08-21T08:59:13.103Z",
                        "compareAtPrice": null,
                        "fulfillmentService": "manual",
                        "grams": 0,
                        "imageId": null,
                        "imageIds": [],
                        "inventoryItemId": null,
                        "inventoryManagement": "Pear",
                        "inventoryPolicy": "DENY",
                        "isInventoryQuantityUnlimited": false,
                        "inventoryQuantity": 1000,
                        "inventoryQuantityOriginal": 1000,
                        "soldQuantity": 0,
                        "option": {
                            "option1": "7 people"
                        },
                        "position": 2,
                        "price": 0,
                        "priceAnchor": "0",
                        "priceImported": "0.00",
                        "productId": "{{ticket_id_General_Admission}}",
                        "sku": "",
                        "taxCode": null,
                        "taxable": true,
                        "title": "7 people",
                        "weight": null,
                        "weightUnit": null,
                        "platform": null,
                        "fees": 0,
                        "transactionFee": {
                            "customFee": 0,
                            "platformFee": 0,
                            "customFeeBreakdown": {},
                            "transactionItemFee": 0
                        },
                        "ticketPrice": 0,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": 0,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": 0,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "transactionFeeConfig": null,
                        "transactionFeeRebateConfig": null,
                        "image": null
                    },
                    {
                        "id": null,
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.103Z",
                        "updatedAt": "2026-08-21T08:59:13.103Z",
                        "compareAtPrice": null,
                        "fulfillmentService": "manual",
                        "grams": 0,
                        "imageId": null,
                        "imageIds": [],
                        "inventoryItemId": null,
                        "inventoryManagement": "Pear",
                        "inventoryPolicy": "DENY",
                        "isInventoryQuantityUnlimited": false,
                        "inventoryQuantity": 1000,
                        "inventoryQuantityOriginal": 1000,
                        "soldQuantity": 0,
                        "option": {
                            "option1": "9 people"
                        },
                        "position": 3,
                        "price": 0,
                        "priceAnchor": "0",
                        "priceImported": "0.00",
                        "productId": "{{ticket_id_General_Admission}}",
                        "sku": "",
                        "taxCode": null,
                        "taxable": true,
                        "title": "9 people",
                        "weight": null,
                        "weightUnit": null,
                        "platform": null,
                        "fees": 0,
                        "transactionFee": {
                            "customFee": 0,
                            "platformFee": 0,
                            "customFeeBreakdown": {},
                            "transactionItemFee": 0
                        },
                        "ticketPrice": 0,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": 0,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": 0,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "transactionFeeConfig": null,
                        "transactionFeeRebateConfig": null,
                        "image": null
                    }
                ],
                "inclusions": [],
                "productForm": null
            }
        ],
        "lineup": [],
        "eventProducts": [],
        "ignoreStartTime": true,
        "ignoreEndTime": true,
        "duplicateEventId": "{{created_event_id}}",
        "posterBackend": [
            {
                "height": 2048,
                "mediaDuration": 0,
                "mediaType": "IMAGE",
                "position": 0,
                "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                "width": 3072
            }
        ],
        "customFeeConfig": null,
        "allowAutoComplete": true,
        "styleSettings": {
            "template": "ClearSky",
            "themeName": "MidnightGlow",
            "layout": {
                "pageHeader": {
                    "style": "DEDICATED_HEADER_BAR",
                    "displayText": "SHOP_NAME",
                    "height": "MEDIUM"
                },
                "productBanner": {
                    "ctaButton": "VIEW_PRODUCT",
                    "display": "HIDE"
                }
            },
            "fontFamily": "Inter",
            "color": "#FFFFFF",
            "backgroundColor": "#000000",
            "borderColor": "#000000",
            "dividerColor": "#5D5D5D",
            "secondaryTextColor": "#E0E0E0",
            "announcementCarousel": {
                "color": "#000000",
                "backgroundColor": "#F6CA7C"
            },
            "title": {
                "color": "#F6CA7C",
                "fontFamily": "Inter",
                "fontSize": 24,
                "fontWeight": 700
            },
            "columnTitle": {
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "subtitle": {
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 400,
                "color": "#FFFFFF"
            },
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000",
                "borderColor": "#000000",
                "borderRadius": 0,
                "boxShadow": "none",
                "fontSize": 16,
                "fontWeight": 400
            },
            "secondaryButton": {
                "fontSize": 16,
                "fontWeight": 400,
                "color": "#FFFFFF",
                "borderColor": "#F6CA7C",
                "borderRadius": 0,
                "boxShadow": "none"
            },
            "textButton": {
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "selectButton": {
                "borderColor": "#000000"
            },
            "relatedLink": {
                "borderRadius": 0,
                "color": "#000000 ",
                "borderColor": "#0000",
                "backgroundColor": "#FAFAFA"
            },
            "featuredProducts": {
                "borderRadius": 0,
                "backgroundColor": "#000000",
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 14,
                    "fontWeight": 400,
                    "color": "#FFFFFF"
                }
            },
            "product": {
                "backgroundColor": "#000000",
                "borderRadius": 0,
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0"
            },
            "discount": {
                "backgroundColor": "#D32A09",
                "color": "#FFFFFF",
                "priceColor": "#FFFFFF"
            },
            "freeShipping": {
                "backgroundColor": "#EBF5EF",
                "color": "#268E46"
            },
            "starRatingColor": "#FAAF03",
            "layoutFeatureCard": {
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 16,
                    "fontWeight": 700,
                    "color": "#FFFFFF"
                },
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "button": {
                    "backgroundColor": "#F6CA7C",
                    "color": "#000000"
                }
            },
            "lineupBanner": {
                "titleText": "#FFFFFF",
                "descriptionText": "#E0E0E0"
            },
            "eventInfoBanner": {
                "text": "#FFFFFF",
                "secondaryText": "#E0E0E0"
            },
            "eventDescription": {
                "text": "#E0E0E0",
                "title": "#FFFFFF"
            },
            "featuredProduct": {
                "cover": {
                    "borderRadius": 0
                }
            },
            "recentUsedColors": [
                "#ffffff"
            ]
        }
    }""", token="token", app_headers=True)
    expect(_resp106).json('$.code').equals('200')
    expect(_resp106).json('$.message').equals('success')
    # ⚠️ 该响应里没有 eventId / postId 字段（实测 201 响应的 data 为事件对象：
    #    id / title / curatorId / ... / tickets[3] / posts[1] / storeFrontModules[1]）。
    #    新事件 id 取 data.id，新建的帖子取 data.posts[0].id —— 原路径会恒为 None，
    #    导致 URL/PATCH body 里的 {{venue_map_event_id}} / {{venue_map_post_id}} 渲染不出。
    ctx.extract("venue_map_event_id", _resp106, "$.data.id")
    ctx.extract("venue_map_post_id", _resp106, "$.data.posts[0].id")
    # 按票种标题提取 venue map 所需的 ticket / product / variant id
    # （原 Apifox 在该请求的 test script 里用 JS 循环 pm.environment.set 完成）
    for _vm_title, _vm_sfx in (
        ("General Admission 02", "_General_Admission_02"),
        ("General Admission 01", "_General_Admission_01"),
        ("General Admission", "_General_Admission"),
    ):
        _vm_ticket = '$.data.tickets[?(@.title=="%s")]' % _vm_title
        ctx.extract("venue_map_ticket_id" + _vm_sfx, _resp106, _vm_ticket + ".id")
        ctx.extract("venue_map_productId" + _vm_sfx, _resp106, _vm_ticket + ".id")
        ctx.extract("venue_map_variant_id" + _vm_sfx, _resp106, _vm_ticket + ".variants[0].id")
        ctx.extract("ticket_id" + _vm_sfx, _resp106, _vm_ticket + ".id")
        # GA 票现在是 3 个 variant（5/7/9 people，见本 step 的 body）；step 109 的 post 商品
        # 快照要按 variant 逐个写 merchantProductVariantId —— variants[0] 已由上面的循环写入
        # venue_map_variant_id_General_Admission，这里补 variants[1] / variants[2]。
        _vm_ga = '$.data.tickets[?(@.title=="General Admission")]'
        ctx.extract("venue_map_variant_id_General_Admission_7p", _resp106, _vm_ga + ".variants[1].id")
        ctx.extract("venue_map_variant_id_General_Admission_9p", _resp106, _vm_ga + ".variants[2].id")



    # --- step 107: Catch the ProductId promoterProductId merchantProductVariantId (GET post/v2/{{venue_map_post_id}}/relate-products) ---
    # NOTE: 原 Apifox 用 JS 循环提取 productId / promoterProductId / merchantProductVariantId；
    #       下方按票种标题过滤提取（core.jsonpath 支持 [?(@.field=="value")] 谓词）。
    #       未命中时写入 None，渲染器跳过 None（占位符保持字面量），与迁移前行为一致。
    # ⚠️ 该接口只在 admin 域存在：实测 base 域 → 404（Cannot GET），
    #    admin 域 + {{token}}(999) → 401，admin 域 + {{admin_token}} → 200。
    # 🔁 重试：relate-products 的 relatedProducts 由「事件 → 帖子」产品关联异步落地
    #    （eventually-consistent）。CI 多次 run 实测 09-18 为空、09-19 非空，属时序抖动，
    #    不是数据真缺失。这里最多重试 5 次、每次间隔 3s，仍为空才视为真实失败。
    #    （code/message != 200 是真实失败，不重试，直接抛出。）
    _resp107 = None
    for _rp_try in range(5):
        _resp107 = ctx.api.admin.post_v2_relate_products(
            path_vars={"post0_id": vars.get("venue_map_post_id", "")},
            token="admin_token", app_headers=True)
        expect(_resp107).json('$.code').equals('200')
        expect(_resp107).json('$.message').equals('success')
        try:
            expect(_resp107).json('$.data.relatedProducts').is_not_empty()
        except Exception:
            if _rp_try < 4:
                time.sleep(3)
                continue
            raise
        else:
            break
    for _vm_title, _vm_sfx in (
        ("General Admission 02", "_General_Admission_02"),
        ("General Admission 01", "_General_Admission_01"),
        ("General Admission", "_General_Admission"),
    ):
        _vm_prod = '$.data.relatedProducts[?(@.title=="%s")]' % _vm_title
        ctx.extract("productId" + _vm_sfx, _resp107, _vm_prod + ".merchantProductId")
        ctx.extract("venue_map_promoterProductId" + _vm_sfx, _resp107, _vm_prod + ".promoterProductId")
        ctx.extract("merchantProductVariantId" + _vm_sfx, _resp107,
                    _vm_prod + ".variants[0].merchantProductVariantId")
    expect(_resp107).json('$.data.relatedProducts').is_array()
    expect(_resp107).json('$.data.relatedProducts').is_not_empty()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp107).json('$.data.relatedProducts[0].merchantProductId').is_string()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp107).json('$.data.relatedProducts[0].merchantProductId').is_not_empty()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp107).json('$.data.relatedProducts[0].promoterProductId').is_string()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp107).json('$.data.relatedProducts[0].promoterProductId').is_not_empty()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp107).json('$.data.relatedProducts[0].variants[0].merchantProductVariantId').is_string()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp107).json('$.data.relatedProducts[0].variants[0].merchantProductVariantId').is_not_empty()



    # --- step 108: enable venue map (PATCH users/tool/feature-flags?userId={{curator_id}}) ---
    _resp108 = ctx.api.admin.users_tool_feature_flags(
        params={"userId": vars.get("curator_id", "")}, body="""{"name":"enableVenueMap","enabled":true}""", token="admin_token", app_headers=True)
    expect(_resp108).json('$.code').equals('200')
    expect(_resp108).json('$.message').equals('success')



    # --- step 109: Insert all tickets and all merch section (PATCH posts/curator/{{venue_map_post_id}}/content) ---
    _resp109 = ctx.api.posts.update_curator_content(body=r"""{
        "id": "{{venue_map_post_id}}",
        "createFromEventId": "{{venue_map_event_id}}",
        "headline": "{{event_title}}",
        "title": "{{event_title}}",
        "subTitle": "",
        "links": [],
        "bodyHtml": "",
        "syncEnabled": true,
        "postType": "EVENT",
        "products": [
            {
                "type": "PRODUCT",
                "originalCommissionRate": 100,
                "priceDisplayCost": 0,
                "displayVariantId": "{{venue_map_variant_id_General_Admission_02}}",
                "options": [
                    {
                        "name": "Title",
                        "values": [
                            "Default Title"
                        ],
                        "position": 1
                    }
                ],
                "inStock": true,
                "alias": "bzusuh",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "merchantProductImages": [
                    {
                        "id": "900a8d96-d912-4896-903b-adcc11bf543a",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "type": "IMAGE",
                        "height": 1000,
                        "width": 1000,
                        "mediaDuration": 0,
                        "mediaSrc": null,
                        "mediaType": "IMAGE",
                        "position": 1,
                        "productImageType": "PRODUCT"
                    }
                ],
                "promoterProductImages": [],
                "shippingInfo": {
                    "merchantName": "Events",
                    "returnPolicy": "No return accepted",
                    "shippingFee": "No shipping fee",
                    "deliveryTime": "0-0 business days",
                    "shippingPolicy": null,
                    "realShippingFee": 0
                },
                "shippingView": {
                    "productId": "{{venue_map_productId_General_Admission_02}}",
                    "shippingType": "NO_SHIPPING_REQUIRED",
                    "shippingNote": "",
                    "realShippingFee": 0,
                    "returnPolicy": "No return accepted",
                    "configCatalogShippingOptionId": null,
                    "shippingOptions": []
                },
                "merchant": {
                    "id": "{{eventcatalog_id}}",
                    "shopUrl": null
                },
                "discountPercent": 0,
                "isUsed": "NWT",
                "platform": "PEAR",
                "publishedAt": "2026-08-24T02:46:11.249Z",
                "merchantAvatar": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "reviewSummary": null,
                "status": "ACTIVE",
                "customFieldsInfo": null,
                "reviewCount": null,
                "title": "General Admission 02",
                "bodyHtml": "",
                "bodyText": "",
                "promoterProductId": "{{venue_map_promoterProductId_General_Admission_02}}",
                "productOwnerId": "{{curator_id}}",
                "priceMin": 112.22,
                "priceMax": 112.22,
                "priceDisplay": 112.22,
                "priceDisplayAnchor": 0,
                "priceMinAnchor": 0,
                "maxDiscountPercent": 0,
                "commissionRate": 100,
                "isVisible": true,
                "purchaseQuantityLimit": 1,
                "isPurchaseQuantityLimited": false,
                "isDefaultToSubscription": false,
                "syncWithCatalogPrice": true,
                "variants": [
                    {
                        "defaultCommissionRateForPromoters": 7,
                        "defaultWholesalePriceForPromoters": 104.36,
                        "isExcluded": false,
                        "isDefault": false,
                        "priceImported": "0.00",
                        "compareAtPrice": null,
                        "title": "Default Title",
                        "catalogPrice": 112.22,
                        "catalogPriceAnchor": 0,
                        "id": "{{venue_map_variant_id_General_Admission_02}}",
                        "position": 1,
                        "imageId": null,
                        "inventoryQuantity": 10000,
                        "isInventoryQuantityUnlimited": false,
                        "option": {
                            "option1": "Default Title"
                        },
                        "merchantProductVariantId": "{{venue_map_variant_id_General_Admission_02}}",
                        "inventoryItemId": null,
                        "inventoryPolicy": "DENY",
                        "commissionRateForPromoters": 7,
                        "commissionRateForMe": 100,
                        "costPrice": 0,
                        "wholesalePriceForPromoters": 0,
                        "price": 112.22,
                        "priceAnchor": 0,
                        "imageIds": [],
                        "inPost": true,
                        "discountPercent": 0,
                        "subscriptionPlanOptionPrices": [],
                        "fees": 12.22,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": null,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": null,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "weight": null,
                        "weightUnit": null
                    }
                ],
                "isFreeShipping": false,
                "hasDependentProducts": false,
                "dependentProductIds": [],
                "isRecommendation": false,
                "coverImage": {
                    "height": 2048,
                    "mediaDuration": 0,
                    "mediaType": "IMAGE",
                    "position": 0,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072
                },
                "isAvailable": true,
                "isNotAvailableReason": null,
                "isMyCatalog": true,
                "links": null,
                "merchantId": "{{eventcatalog_id}}",
                "merchantName": "Events",
                "merchantProductId": "{{venue_map_ticket_id_General_Admission_02}}",
                "canSetPrice": true,
                "subscriptionPlanId": null,
                "hasSubscriptionPlan": false,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "addressRevealConfig": null,
                    "date": "Mon Aug 24, 2026 EDT",
                    "event": "{{event_title}}",
                    "eventNote": "auto test",
                    "isAddressHidden": false,
                    "lineup": [],
                    "location": "Test venue 路 West Mound Street, Columbus, OH",
                    "poster": {
                        "height": 2048,
                        "mediaDuration": 0,
                        "mediaType": "IMAGE",
                        "position": 0,
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072
                    },
                    "startDate": "2026-08-24T04:00:00.000Z",
                    "status": "UPCOMING",
                    "timeZoneId": "America/New_York",
                    "venue": "Test venue 路 West Mound Street, Columbus, OH"
                },
                "feesDisplay": 12.22,
                "hideFees": false,
                "toReplaceMerchantProductIds": null,
                "event": {
                    "id": "{{venue_map_event_id}}",
                    "description": "",
                    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
                    "showFeesBreakdown": false
                },
                "eventId": "{{venue_map_event_id}}",
                "isCtaCustomized": false,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "isVenueUnitEnabled": false,
                "isAddedByPromoter": false,
                "id": "{{venue_map_ticket_id_General_Admission_02}}",
                "isCustomizePurchase": false,
                "hasReplaceProduct": false,
                "setCustomizePrice": false,
                "ctaConfig": {
                    "type": "BUY_NOW"
                }
            },
            {
                "type": "PRODUCT",
                "originalCommissionRate": 100,
                "priceDisplayCost": 0,
                "displayVariantId": "{{venue_map_variant_id_General_Admission_01}}",
                "options": [
                    {
                        "name": "Title",
                        "values": [
                            "Default Title"
                        ],
                        "position": 1
                    }
                ],
                "inStock": true,
                "alias": "er782n",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "merchantProductImages": [
                    {
                        "id": "0f9d5493-c44a-479e-96c0-a3f2eee06cb9",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "type": "IMAGE",
                        "height": 1000,
                        "width": 1000,
                        "mediaDuration": 0,
                        "mediaSrc": null,
                        "mediaType": "IMAGE",
                        "position": 1,
                        "productImageType": "PRODUCT"
                    }
                ],
                "promoterProductImages": [],
                "shippingInfo": {
                    "merchantName": "Events",
                    "returnPolicy": "No return accepted",
                    "shippingFee": "No shipping fee",
                    "deliveryTime": "0-0 business days",
                    "shippingPolicy": null,
                    "realShippingFee": 0
                },
                "shippingView": {
                    "productId": "{{venue_map_productId_General_Admission_01}}",
                    "shippingType": "NO_SHIPPING_REQUIRED",
                    "shippingNote": "",
                    "realShippingFee": 0,
                    "returnPolicy": "No return accepted",
                    "configCatalogShippingOptionId": null,
                    "shippingOptions": []
                },
                "merchant": {
                    "id": "{{eventcatalog_id}}",
                    "shopUrl": null
                },
                "discountPercent": 0,
                "isUsed": "NWT",
                "platform": "PEAR",
                "publishedAt": "2026-08-24T02:46:11.255Z",
                "merchantAvatar": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "reviewSummary": null,
                "status": "ACTIVE",
                "customFieldsInfo": null,
                "reviewCount": null,
                "title": "General Admission 01",
                "bodyHtml": "",
                "bodyText": "",
                "promoterProductId": "{{venue_map_promoterProductId_General_Admission_01}}",
                "productOwnerId": "{{curator_id}}",
                "priceMin": 67.77,
                "priceMax": 67.77,
                "priceDisplay": 67.77,
                "priceDisplayAnchor": 0,
                "priceMinAnchor": 0,
                "maxDiscountPercent": 0,
                "commissionRate": 100,
                "isVisible": true,
                "purchaseQuantityLimit": 1,
                "isPurchaseQuantityLimited": false,
                "isDefaultToSubscription": false,
                "syncWithCatalogPrice": true,
                "variants": [
                    {
                        "defaultCommissionRateForPromoters": 7,
                        "defaultWholesalePriceForPromoters": 63.03,
                        "isExcluded": false,
                        "isDefault": false,
                        "priceImported": "0.00",
                        "compareAtPrice": null,
                        "title": "Default Title",
                        "catalogPrice": 67.77,
                        "catalogPriceAnchor": 0,
                        "id": "{{venue_map_variant_id_General_Admission_01}}",
                        "position": 1,
                        "imageId": null,
                        "inventoryQuantity": 10000,
                        "isInventoryQuantityUnlimited": false,
                        "option": {
                            "option1": "Default Title"
                        },
                        "merchantProductVariantId": "{{venue_map_variant_id_General_Admission_01}}",
                        "inventoryItemId": null,
                        "inventoryPolicy": "DENY",
                        "commissionRateForPromoters": 7,
                        "commissionRateForMe": 100,
                        "costPrice": 0,
                        "wholesalePriceForPromoters": 0,
                        "price": 67.77,
                        "priceAnchor": 0,
                        "imageIds": [],
                        "inPost": true,
                        "discountPercent": 0,
                        "subscriptionPlanOptionPrices": [],
                        "fees": 7.77,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": null,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": null,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "weight": null,
                        "weightUnit": null
                    }
                ],
                "isFreeShipping": false,
                "hasDependentProducts": false,
                "dependentProductIds": [],
                "isRecommendation": false,
                "coverImage": {
                    "height": 2048,
                    "mediaDuration": 0,
                    "mediaType": "IMAGE",
                    "position": 0,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072
                },
                "isAvailable": true,
                "isNotAvailableReason": null,
                "isMyCatalog": true,
                "links": null,
                "merchantId": "{{eventcatalog_id}}",
                "merchantName": "Events",
                "merchantProductId": "{{venue_map_ticket_id_General_Admission_01}}",
                "canSetPrice": true,
                "subscriptionPlanId": null,
                "hasSubscriptionPlan": false,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "addressRevealConfig": null,
                    "date": "Mon Aug 24, 2026 EDT",
                    "event": "{{event_title}}",
                    "eventNote": "auto test",
                    "isAddressHidden": false,
                    "lineup": [],
                    "location": "Test venue 路 West Mound Street, Columbus, OH",
                    "poster": {
                        "height": 2048,
                        "mediaDuration": 0,
                        "mediaType": "IMAGE",
                        "position": 0,
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072
                    },
                    "startDate": "2026-08-24T04:00:00.000Z",
                    "status": "UPCOMING",
                    "timeZoneId": "America/New_York",
                    "venue": "Test venue 路 West Mound Street, Columbus, OH"
                },
                "feesDisplay": 7.77,
                "hideFees": false,
                "toReplaceMerchantProductIds": null,
                "event": {
                    "id": "{{venue_map_event_id}}",
                    "description": "",
                    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
                    "showFeesBreakdown": false
                },
                "eventId": "{{venue_map_event_id}}",
                "isCtaCustomized": false,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "isVenueUnitEnabled": true,
                "isAddedByPromoter": false,
                "id": "{{venue_map_ticket_id_General_Admission_01}}",
                "isCustomizePurchase": false,
                "hasReplaceProduct": false,
                "setCustomizePrice": false,
                "ctaConfig": {
                    "type": "BUY_NOW"
                }
            },
            {
                "type": "PRODUCT",
                "originalCommissionRate": 100,
                "priceDisplayCost": 0,
                "displayVariantId": "{{venue_map_variant_id_General_Admission}}",
                "options": [
                    {
                        "name": "Time",
                        "values": [
                            "5 people",
                            "7 people",
                            "9 people"
                        ],
                        "position": 1
                    }
                ],
                "inStock": true,
                "alias": "a0kvr3",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "merchantProductImages": [
                    {
                        "id": "c988917d-f11f-4ef4-a62c-20f5263b3ff6",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "type": "IMAGE",
                        "height": 1000,
                        "width": 1000,
                        "mediaDuration": 0,
                        "mediaSrc": null,
                        "mediaType": "IMAGE",
                        "position": 1,
                        "productImageType": "PRODUCT"
                    }
                ],
                "promoterProductImages": [],
                "shippingInfo": {
                    "merchantName": "Events",
                    "returnPolicy": "No return accepted",
                    "shippingFee": "No shipping fee",
                    "deliveryTime": "0-0 business days",
                    "shippingPolicy": null,
                    "realShippingFee": 0
                },
                "shippingView": {
                    "productId": "{{venue_map_productId_General_Admission}}",
                    "shippingType": "NO_SHIPPING_REQUIRED",
                    "shippingNote": "",
                    "realShippingFee": 0,
                    "returnPolicy": "No return accepted",
                    "configCatalogShippingOptionId": null,
                    "shippingOptions": []
                },
                "merchant": {
                    "id": "{{eventcatalog_id}}",
                    "shopUrl": null
                },
                "discountPercent": 0,
                "isUsed": "NWT",
                "platform": "PEAR",
                "publishedAt": "2026-08-24T02:46:11.261Z",
                "merchantAvatar": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "reviewSummary": null,
                "status": "ACTIVE",
                "customFieldsInfo": null,
                "reviewCount": null,
                "title": "General Admission",
                "bodyHtml": "",
                "bodyText": "",
                "promoterProductId": "{{venue_map_promoterProductId_General_Admission}}",
                "productOwnerId": "{{curator_id}}",
                "priceMin": 0,
                "priceMax": 0,
                "priceDisplay": 0,
                "priceDisplayAnchor": 0,
                "priceMinAnchor": 0,
                "maxDiscountPercent": 0,
                "commissionRate": 100,
                "isVisible": true,
                "purchaseQuantityLimit": 1,
                "isPurchaseQuantityLimited": false,
                "isDefaultToSubscription": false,
                "syncWithCatalogPrice": true,
                "variants": [
                    {
                        "defaultCommissionRateForPromoters": 7,
                        "defaultWholesalePriceForPromoters": 0,
                        "isExcluded": false,
                        "isDefault": false,
                        "priceImported": "0.00",
                        "compareAtPrice": null,
                        "title": "5 people",
                        "catalogPrice": 0,
                        "catalogPriceAnchor": 0,
                        "id": "{{venue_map_variant_id_General_Admission}}",
                        "position": 1,
                        "imageId": null,
                        "inventoryQuantity": 1000,
                        "isInventoryQuantityUnlimited": false,
                        "option": {
                            "option1": "5 people"
                        },
                        "merchantProductVariantId": "{{venue_map_variant_id_General_Admission}}",
                        "inventoryItemId": null,
                        "inventoryPolicy": "DENY",
                        "commissionRateForPromoters": 7,
                        "commissionRateForMe": 100,
                        "costPrice": 0,
                        "wholesalePriceForPromoters": 0,
                        "price": 0,
                        "priceAnchor": 0,
                        "imageIds": [],
                        "inPost": true,
                        "discountPercent": 0,
                        "subscriptionPlanOptionPrices": [],
                        "fees": 0,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": null,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": null,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "weight": null,
                        "weightUnit": null
                    },
                    {
                        "defaultCommissionRateForPromoters": 7,
                        "defaultWholesalePriceForPromoters": 0,
                        "isExcluded": false,
                        "isDefault": false,
                        "priceImported": "0.00",
                        "compareAtPrice": null,
                        "title": "7 people",
                        "catalogPrice": 0,
                        "catalogPriceAnchor": 0,
                        "id": "{{venue_map_variant_id_General_Admission_7p}}",
                        "position": 2,
                        "imageId": null,
                        "inventoryQuantity": 1000,
                        "isInventoryQuantityUnlimited": false,
                        "option": {
                            "option1": "7 people"
                        },
                        "merchantProductVariantId": "{{venue_map_variant_id_General_Admission_7p}}",
                        "inventoryItemId": null,
                        "inventoryPolicy": "DENY",
                        "commissionRateForPromoters": 7,
                        "commissionRateForMe": 100,
                        "costPrice": 0,
                        "wholesalePriceForPromoters": 0,
                        "price": 0,
                        "priceAnchor": 0,
                        "imageIds": [],
                        "inPost": true,
                        "discountPercent": 0,
                        "subscriptionPlanOptionPrices": [],
                        "fees": 0,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": null,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": null,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "weight": null,
                        "weightUnit": null
                    },
                    {
                        "defaultCommissionRateForPromoters": 7,
                        "defaultWholesalePriceForPromoters": 0,
                        "isExcluded": false,
                        "isDefault": false,
                        "priceImported": "0.00",
                        "compareAtPrice": null,
                        "title": "9 people",
                        "catalogPrice": 0,
                        "catalogPriceAnchor": 0,
                        "id": "{{venue_map_variant_id_General_Admission_9p}}",
                        "position": 3,
                        "imageId": null,
                        "inventoryQuantity": 1000,
                        "isInventoryQuantityUnlimited": false,
                        "option": {
                            "option1": "9 people"
                        },
                        "merchantProductVariantId": "{{venue_map_variant_id_General_Admission_9p}}",
                        "inventoryItemId": null,
                        "inventoryPolicy": "DENY",
                        "commissionRateForPromoters": 7,
                        "commissionRateForMe": 100,
                        "costPrice": 0,
                        "wholesalePriceForPromoters": 0,
                        "price": 0,
                        "priceAnchor": 0,
                        "imageIds": [],
                        "inPost": true,
                        "discountPercent": 0,
                        "subscriptionPlanOptionPrices": [],
                        "fees": 0,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": null,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": null,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "weight": null,
                        "weightUnit": null
                    }
                ],
                "isFreeShipping": false,
                "hasDependentProducts": false,
                "dependentProductIds": [],
                "isRecommendation": false,
                "coverImage": {
                    "height": 2048,
                    "mediaDuration": 0,
                    "mediaType": "IMAGE",
                    "position": 0,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072
                },
                "isAvailable": true,
                "isNotAvailableReason": null,
                "isMyCatalog": true,
                "links": null,
                "merchantId": "{{eventcatalog_id}}",
                "merchantName": "Events",
                "merchantProductId": "{{venue_map_ticket_id_General_Admission}}",
                "canSetPrice": true,
                "subscriptionPlanId": null,
                "hasSubscriptionPlan": false,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "addressRevealConfig": null,
                    "date": "Mon Aug 24, 2026 EDT",
                    "event": "{{event_title}}",
                    "eventNote": "auto test",
                    "isAddressHidden": false,
                    "lineup": [],
                    "location": "Test venue 路 West Mound Street, Columbus, OH",
                    "poster": {
                        "height": 2048,
                        "mediaDuration": 0,
                        "mediaType": "IMAGE",
                        "position": 0,
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072
                    },
                    "startDate": "2026-08-24T04:00:00.000Z",
                    "status": "UPCOMING",
                    "timeZoneId": "America/New_York",
                    "venue": "Test venue 路 West Mound Street, Columbus, OH"
                },
                "feesDisplay": 0,
                "hideFees": false,
                "toReplaceMerchantProductIds": null,
                "event": {
                    "id": "{{venue_map_event_id}}",
                    "description": "",
                    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
                    "showFeesBreakdown": false
                },
                "eventId": "{{venue_map_event_id}}",
                "isCtaCustomized": false,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "isVenueUnitEnabled": false,
                "isAddedByPromoter": false,
                "id": "{{venue_map_ticket_id_General_Admission}}",
                "isCustomizePurchase": false,
                "hasReplaceProduct": false,
                "setCustomizePrice": false,
                "ctaConfig": {
                    "type": "BUY_NOW"
                }
            }
        ],
        "styleSettings": {
            "recentUsedColors": [
                "#ffffff"
            ],
            "fontFamily": "Inter",
            "color": "#FFFFFF",
            "backgroundColor": "#000000",
            "borderColor": "#000000",
            "dividerColor": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "announcementCarousel": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            },
            "title": {
                "color": "#F6CA7C",
                "fontFamily": "Inter",
                "fontSize": 24,
                "fontWeight": 700
            },
            "columnTitle": {
                "color": "#FFFFFF",
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 700
            },
            "subtitle": {
                "color": "#FFFFFF",
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 400
            },
            "button": {
                "backgroundColor": "#F6CA7C",
                "borderColor": "#000000",
                "borderRadius": 12,
                "boxShadow": "none",
                "color": "#000000",
                "fontSize": 16,
                "fontWeight": 700
            },
            "secondaryButton": {
                "borderColor": "#F6CA7C",
                "borderRadius": 12,
                "boxShadow": "none",
                "color": "#FFFFFF",
                "fontSize": 16,
                "fontWeight": 700
            },
            "textButton": {
                "color": "#FFFFFF",
                "fontSize": 16,
                "fontWeight": 700
            },
            "selectButton": {
                "borderColor": "#000000"
            },
            "relatedLink": {
                "backgroundColor": "#FAFAFA",
                "borderColor": "#0000",
                "borderRadius": 99,
                "color": "#000000 "
            },
            "featuredProducts": {
                "backgroundColor": "#000000",
                "borderRadius": 16,
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "title": {
                    "color": "#FFFFFF",
                    "fontFamily": "Inter",
                    "fontSize": 14,
                    "fontWeight": 400
                }
            },
            "product": {
                "backgroundColor": "#000000",
                "borderRadius": 8,
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0"
            },
            "discount": {
                "backgroundColor": "#D32A09",
                "color": "#FFFFFF",
                "priceColor": "#FFFFFF"
            },
            "freeShipping": {
                "backgroundColor": "#EBF5EF",
                "color": "#268E46"
            },
            "starRatingColor": "#FAAF03",
            "layoutFeatureCard": {
                "button": {
                    "backgroundColor": "#F6CA7C",
                    "color": "#000000"
                },
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "title": {
                    "color": "#FFFFFF",
                    "fontFamily": "Inter",
                    "fontSize": 16,
                    "fontWeight": 700
                }
            },
            "lineupBanner": {
                "descriptionText": "#E0E0E0",
                "titleText": "#FFFFFF"
            },
            "eventInfoBanner": {
                "secondaryText": "#E0E0E0",
                "text": "#FFFFFF"
            },
            "eventDescription": {
                "text": "#E0E0E0",
                "title": "#FFFFFF"
            },
            "featuredProduct": {
                "cover": {
                    "borderRadius": 0
                }
            },
            "layout": {
                "pageHeader": {
                    "displayText": "SHOP_NAME",
                    "height": "MEDIUM",
                    "style": "DEDICATED_HEADER_BAR"
                },
                "productBanner": {
                    "ctaButton": "VIEW_PRODUCT",
                    "display": "HIDE"
                }
            },
            "template": "ClearSky"
        },
        "featuredSectionEnable": false,
        "featuredSectionTitle": "",
        "recommendationSectionTitle": "",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"2d77f532-fadd-4825-a8b5-9a4cc18d183d\",\"allTickets\":[{\"eventId\":\"{{venue_map_event_id}}\",\"productId\":\"{{venue_map_productId_General_Admission_01}}\",\"variantId\":\"{{venue_map_variant_id_General_Admission_01}}\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"thumbnailDisplay\":\"showThumbnail\",\"eventNotesDisplay\":\"showEventNotes\",\"position\":0,\"isVisible\":true,\"applyToAll\":false},{\"eventId\":\"{{venue_map_event_id}}\",\"productId\":\"{{venue_map_productId_General_Admission}}\",\"variantId\":\"{{venue_map_variant_id_General_Admission}}\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"thumbnailDisplay\":\"showThumbnail\",\"eventNotesDisplay\":\"showEventNotes\",\"position\":1,\"isVisible\":true,\"applyToAll\":false},{\"eventId\":\"{{venue_map_event_id}}\",\"productId\":\"{{venue_map_productId_General_Admission_02}}\",\"variantId\":\"{{venue_map_variant_id_General_Admission_02}}\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"thumbnailDisplay\":\"showThumbnail\",\"eventNotesDisplay\":\"showEventNotes\",\"position\":2,\"isVisible\":true,\"applyToAll\":false}],\"width\":\"100%\",\"height\":\"\",\"showDivider\":true,\"orderingMode\":\"auto\",\"type\":\"ticket-all\",\"version\":1},{\"id\":\"8804bb99-8aa9-4ab6-b5e8-dd340c842e7f\",\"allMerchandise\":[],\"width\":\"100%\",\"height\":\"\",\"showDivider\":true,\"type\":\"merchandise-all\",\"version\":1},{\"id\":\"03e9c4b2-6f24-4233-bee0-1518f4e164fa\",\"eventId\":\"{{venue_map_event_id}}\",\"width\":\"100%\",\"showDivider\":true,\"type\":\"event-info-banner\",\"version\":2},{\"children\":[],\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"},{\"children\":[],\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"},{\"id\":\"09de8dbb-c76a-4750-999b-b1a2bbe7e924\",\"eventId\":\"{{venue_map_event_id}}\",\"allMedia\":[],\"width\":\"100%\",\"height\":\"\",\"title\":\"Missed our last event?\",\"subtitle\":\"Here's a lil recap of our last event馃憞\",\"align\":\"center\",\"showDivider\":true,\"type\":\"event-media\",\"version\":1},{\"children\":[],\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"},{\"id\":\"b7f278d3-4ef4-40d3-8f97-e22170502153\",\"eventId\":\"{{venue_map_event_id}}\",\"width\":\"100%\",\"showDivider\":true,\"type\":\"post-event-description\",\"version\":2},{\"children\":[],\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"katana-t8777m\"}",
        "status": "ACTIVE",
        "media": [
            {
                "id": "15ba8a6b-08b1-4508-8540-81cc81524e72",
                "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                "selected": true,
                "type": "IMAGE",
                "height": 2048,
                "width": 3072,
                "mediaDuration": 0,
                "mediaSrc": null,
                "mediaType": "IMAGE",
                "inherited": true,
                "position": 1,
                "referenceId": null,
                "source": null,
                "setThumbnail": false
            }
        ],
        "needRefreshHTML": true,
        "urlAlias": "{{event_title}}"
    }""", token="token", app_headers=True)
    expect(_resp109).json('$.code').equals('200')
    expect(_resp109).json('$.message').equals('success')



    # --- step 110: search the category id (GET merchant/product/search?pageSize=100&eventId={{venue_map_event_id}}) ---
    # NOTE: 原 Apifox 用 JS 循环从 $.data.items 提取 ticket_id / categoryId / venueUnitCategoryId；
    #       下方按票种标题过滤提取（categoryId 缺失时回退 venueCategoryId，与 JS 的 `||` 一致）。
    # ⚠️ 该接口只在 admin 域存在（base 域：带 admin_token → 401，带 {{token}} → 500），
    #    且必须带 ?pageSize=&eventId=，需 admin_token。
    _resp110 = ctx.api.admin.merchant_product_search(
        params={"pageSize": "100", "eventId": vars.get("venue_map_event_id", "")},
        token="admin_token", app_headers=True)
    expect(_resp110).json('$.code').equals('200')
    expect(_resp110).json('$.message').equals('success')
    for _vm_title, _vm_sfx in (
        ("General Admission 02", "_General_Admission_02"),
        ("General Admission 01", "_General_Admission_01"),
        ("General Admission", "_General_Admission"),
    ):
        _vm_item = '$.data.items[?(@.title=="%s")]' % _vm_title
        ctx.extract("ticket_id" + _vm_sfx, _resp110, _vm_item + ".id")
        ctx.extract("venueUnitCategoryId" + _vm_sfx, _resp110, _vm_item + ".venueUnitCategoryId")
        _vm_cat = ctx.extract("categoryId" + _vm_sfx, _resp110, _vm_item + ".categoryId")
        if _vm_cat is None:
            ctx.extract("categoryId" + _vm_sfx, _resp110, _vm_item + ".venueCategoryId")
    expect(_resp110).json('$.data.items.length').at_least(1)



    # --- step 111: Create Venue map (POST events/{{venue_map_event_id}}/venue-map) ---
    # ⚠️ 该接口只存在于 admin 域（base 域 404 Cannot POST；admin 域 + {{token}}(999) → 401），
    #    需 admin_token + 路径参数 venue_map_event_id。
    _resp111 = ctx.api.admin.events_venue_map_create(
        path_vars={"venue_map_event_id": vars.get("venue_map_event_id", "")},
        body="""{
        "venueData": {
            "version": 1,
            "mode": "SECTION",
            "sections": [],
            "rows": [
                {
                    "id": "84743235-32b0-4a91-a8c2-b4ff48781e87",
                    "chairSpacing": 20,
                    "seatLabeling": {
                        "algorithm": "NUMBERS",
                        "startAtIndex": 0,
                        "inverted": false,
                        "useEndAt": false
                    },
                    "seats": [
                        {
                            "id": "6034d01c-a994-40af-982d-75c8cd61083b",
                            "x": 200,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "1",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "0ada37a5-2711-4b58-ba43-e45c3aef617b",
                            "x": 221,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "2",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "179778d0-fdcb-408f-9a44-6d973bcdef0a",
                            "x": 242,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "3",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "8aac52a3-1713-4d45-9974-dd6a290c7016",
                            "x": 263,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "4",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "0cfed81c-3f29-4f40-916e-694c73495c75",
                            "x": 284,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "5",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "8062527d-acbc-4709-a51b-c4b3b9658c75",
                            "x": 305,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "6",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "bc510ab4-457f-4b0c-90fa-fb8d566c7d4b",
                            "x": 326,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "7",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "5c8bd617-4677-4b55-9035-1f998d0eb0b0",
                            "x": 347,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "8",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "795ca6b1-75c8-4c9b-a0d7-cd6fb6e8d9fa",
                            "x": 368,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "9",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "c8d285dc-1e37-4f7f-a0e0-b8a414bcaf77",
                            "x": 389,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "10",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "28f9ee6c-ec08-4c76-aa65-18821b14f3f8",
                            "x": 410,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "11",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "b2244c31-d5eb-47dc-aba9-d34ddaf82fa5",
                            "x": 431,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "12",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "18eaa71a-0090-4488-b7d5-ffcd011b1bbc",
                            "x": 452,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "13",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "3d0fa510-a654-49a3-82e6-a73c163504b9",
                            "x": 473,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "14",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "a3b164bc-bbfd-49ad-93fb-3290d1f54681",
                            "x": 494,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "15",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        }
                    ],
                    "label": null,
                    "displayLabel": null,
                    "sectionLabel": null,
                    "sectionDisplayedLabel": null,
                    "curve": 0,
                    "rotationAngle": 0,
                    "smooth": false,
                    "smoothness": 50,
                    "rowLabelDisabled": false,
                    "displayObjectType": "row",
                    "viewFromYourSeatImage": null,
                    "entrance": null,
                    "published": false,
                    "points": null,
                    "objectType": "row",
                    "verticalRowLabelDirection": "BASELINE_LEFT"
                },
                {
                    "id": "f7bd43cd-5acd-47a9-8008-a9e3e5385a71",
                    "chairSpacing": 20,
                    "seatLabeling": {
                        "algorithm": "NUMBERS",
                        "startAtIndex": 0,
                        "inverted": false,
                        "useEndAt": false
                    },
                    "seats": [
                        {
                            "id": "4c4ee7e4-5848-44f2-8f02-4a6282a2f194",
                            "x": 200,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "1",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "8435be0f-1d1a-4408-9aa8-02e0e090299f",
                            "x": 221,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "2",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "e1772c5b-3d3d-45b6-90da-5859798add14",
                            "x": 242,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "3",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "da54cca9-a861-402a-b319-395502ed03cc",
                            "x": 263,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "4",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "667f4c4c-1092-4d2f-a0cd-535842fce60d",
                            "x": 284,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "5",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "bb6bf47d-62f6-4a8b-9ab8-4ad2010165a4",
                            "x": 305,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "6",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "0267e056-7c83-4512-9b52-5b5a2399ab45",
                            "x": 326,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "7",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "93f9e77d-145c-46fd-ad70-1f10e817d936",
                            "x": 347,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "8",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "f5bb72fc-9c79-40d4-b67f-36d2756637f4",
                            "x": 368,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "9",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "c51e4e5d-1609-4942-9017-8c3d3f143a91",
                            "x": 389,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "10",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "5a61d28c-7858-4298-ab04-39a6919bfb76",
                            "x": 410,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "11",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "85edb5dd-9252-4b90-840b-81518a385ebd",
                            "x": 431,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "12",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "b6326aeb-7e2e-42c5-bc56-e5009ecbee3b",
                            "x": 452,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "13",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "471c7972-6a75-444e-a5be-388a1a86ec6f",
                            "x": 473,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "14",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "e7eb390c-57a0-47c4-8e3e-f19e8ca2aa46",
                            "x": 494,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "15",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        }
                    ],
                    "label": null,
                    "displayLabel": null,
                    "sectionLabel": null,
                    "sectionDisplayedLabel": null,
                    "curve": 0,
                    "rotationAngle": 0,
                    "smooth": false,
                    "smoothness": 50,
                    "rowLabelDisabled": false,
                    "displayObjectType": "row",
                    "viewFromYourSeatImage": null,
                    "entrance": null,
                    "published": false,
                    "points": null,
                    "objectType": "row",
                    "verticalRowLabelDirection": "BASELINE_LEFT"
                },
                {
                    "id": "95d63e15-56f5-486b-b47c-c750c53c629d",
                    "chairSpacing": 20,
                    "seatLabeling": {
                        "algorithm": "NUMBERS",
                        "startAtIndex": 0,
                        "inverted": false,
                        "useEndAt": false
                    },
                    "seats": [
                        {
                            "id": "831ad517-2f81-4c76-9bea-6c6109f85e43",
                            "x": 200,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "1",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "15696971-367b-4d3e-90df-0d3d6eefb132",
                            "x": 221,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "2",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "79c277ed-41de-4f9c-88cf-246880ae9b50",
                            "x": 242,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "3",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "df47bc60-0023-4586-9f0c-0e07028039b8",
                            "x": 263,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "4",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "43248efa-a96d-43eb-95d9-c529b82b288e",
                            "x": 284,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "5",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "558ed673-181e-4585-b8b7-7608a3306f42",
                            "x": 305,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "6",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "b0b28a67-5be0-41b4-aa37-9ff232c9e4e6",
                            "x": 326,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "7",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "44463d8b-4a76-4d55-ab49-090c32d7f7d7",
                            "x": 347,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "8",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "f231471d-23a6-44fb-9dc0-e968bd16504c",
                            "x": 368,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "9",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "62c4d181-75aa-45a4-b3e7-703a81bd8984",
                            "x": 389,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "10",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "1494d66f-36ef-4451-b0d5-3ea955c1d7e3",
                            "x": 410,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "11",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "4a2f7a90-b68b-430c-a5c0-51172cb63484",
                            "x": 431,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "12",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "5fe47f91-16d5-4ee7-9564-542520f07ff9",
                            "x": 452,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "13",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "d8fcbb55-db47-4a51-b8bb-a833f0718edf",
                            "x": 473,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "14",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "894630a1-ba52-485d-9409-1791943868c3",
                            "x": 494,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "15",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        }
                    ],
                    "label": null,
                    "displayLabel": null,
                    "sectionLabel": null,
                    "sectionDisplayedLabel": null,
                    "curve": 0,
                    "rotationAngle": 0,
                    "smooth": false,
                    "smoothness": 50,
                    "rowLabelDisabled": false,
                    "displayObjectType": "row",
                    "viewFromYourSeatImage": null,
                    "entrance": null,
                    "published": false,
                    "points": null,
                    "objectType": "row",
                    "verticalRowLabelDirection": "BASELINE_LEFT"
                }
            ],
            "shapes": [],
            "gaAreas": [],
            "texts": [],
            "icons": [],
            "images": [],
            "tables": [],
            "booths": [],
            "categories": [
                {
                    "id": "{{categoryId_General_Admission_02}}",
                    "key": 1,
                    "label": "General Admission 02",
                    "color": "#992C4E",
                    "accessible": false
                },
                {
                    "id": "{{categoryId_General_Admission_01}}",
                    "key": 2,
                    "label": "General Admission 01",
                    "color": "#CD254A",
                    "accessible": false
                },
                {
                    "id": "{{categoryId_General_Admission}}",
                    "key": 3,
                    "label": "General Admission",
                    "color": "#E9803D",
                    "accessible": false
                }
            ],
            "maxCategoryKey": 3,
            "focalPoint": null,
            "background": null
        }
    }""", token="admin_token", app_headers=True)
    expect(_resp111).json('$.code').equals('200')
    expect(_resp111).json('$.message').equals('success')
    ctx.extract("venueMapId", _resp111, "$.data.id")
    expect(_resp111).json('$.data.id').exists()
    expect(_resp111).json('$.data.venueDataDraft.rows[0].seats[0]').is_object()
    expect(_resp111).json('$.data.venueDataDraft.rows[0].seats[0].categoryId').is_string()
    expect(_resp111).json('$.data.venueDataDraft.rows[0].seats[0].categoryId').is_not_empty()



    # --- step 112: delay (no-op, framework style) ---
    # NOTE: original Apifox collection had a delay here; removed per framework style (no time.sleep).



    # --- step 113: publish the seat (POST events/{{venue_map_event_id}}/venue-map/publish) ---
    # ⚠️ 同 step 111：仅 admin 域 + admin_token。
    _resp113 = ctx.api.admin.events_venue_map_publish(
        path_vars={"venue_map_event_id": vars.get("venue_map_event_id", "")},
        token="admin_token", app_headers=True)
    expect(_resp113).json('$.code').equals('200')
    expect(_resp113).json('$.message').equals('success')



    # --- step 114: delay (no-op, framework style) ---
    # NOTE: original Apifox collection had a delay here; removed per framework style (no time.sleep).



    # --- step 115: Bind the seat to the product (POST events/{{venue_map_event_id}}/venue-map/associations) ---
    # ⚠️ 同 step 111：仅 admin 域 + admin_token。
    _resp115 = ctx.api.admin.events_venue_map_associations(
        path_vars={"venue_map_event_id": vars.get("venue_map_event_id", "")},
        body="""{
        "associations": [
            {
                "categoryId": "{{categoryId_General_Admission_02}}",
                "productId": "{{productId_General_Admission_02}}"
            },
            {
                "categoryId": "{{categoryId_General_Admission_01}}",
                "productId": "{{productId_General_Admission_01}}"
            },
            {
                "categoryId": "{{categoryId_General_Admission}}",
                "productId": "{{productId_General_Admission}}"
            }
        ]
    }""", token="admin_token", app_headers=True)
    expect(_resp115).json('$.code').equals('200')
    expect(_resp115).json('$.message').equals('success')
    expect(_resp115).json('$.data').is_object()
    expect(_resp115).json('$.data.created').equals(45)
    expect(_resp115).json('$.data.updated').equals(0)
    expect(_resp115).json('$.data.deleted').equals(0)
    expect(_resp115).json('$.data.linked').equals(3)



    # --- pre-step 116: 重新生成事件日期与标题（原 Apifox 该请求的 prerequest 脚本） ---
    # 第二个 duplicate 的 prerequest 额外生成 endDateDisplay（本地今天 + 7 天）。
    _now116 = _dt.datetime.now()
    _utc116 = _dt.datetime.now(_dt.timezone.utc)
    vars["current_iso_date"] = _utc116.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    vars["startDateDisplay"] = _now116.strftime("%Y-%m-%d")
    vars["endDateDisplay"] = (_now116 + _dt.timedelta(days=7)).strftime("%Y-%m-%d")
    vars["event_title"] = "event-for-api-auto-venue-map"

    # --- step 116: duplicate event for venue map (POST product-event/v2/duplicate) ---
    _resp116 = ctx.api.events.v2_duplicate(body=r"""{
        "title": "{{event_title}}",
        "curatorId": "{{catalog_id}}",
        "description": "",
        "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
        "startDate": "{{current_iso_date}}",
        "endDate": null,
        "venue": "Test venue · West Mound Street, Columbus, OH",
        "location": "Test venue · West Mound Street, Columbus, OH",
        "status": "UPCOMING",
        "isTaxEnabled": false,
        "taxConfig": null,
        "mediaTextConfig": {
            "headline": "Missed our last event?",
            "subtitle": "Here's a lil recap of our last event👇",
            "align": "center"
        },
        "poster": {
            "height": 2048,
            "mediaDuration": 0,
            "mediaType": "IMAGE",
            "position": 0,
            "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
            "width": 3072
        },
        "startDateDisplay": "{{startDateDisplay}}",
        "endDateDisplay": "{{endDateDisplay}}",
        "note": "auto test",
        "timezone": {
            "timeZoneId": "America/New_York",
            "timeZoneName": "Eastern Daylight Time",
            "dstOffset": 3600,
            "rawOffset": -18000
        },
        "isAddressRevealEnabled": false,
        "isAddressHidden": false,
        "messageInfo": {
            "cooldownMinutes": 15,
            "emailMaxLimit": 5,
            "smsMaxLimit": 3
        },
        "platform": "PEAR",
        "creationStep": "COMPLETED",
        "extraInfo": null,
        "locationDetails": {
            "city": "Columbus",
            "country": "US",
            "line1": "Test venue · West Mound Street",
            "line2": "",
            "placeId": null,
            "state": "OH",
            "stateName": "Ohio",
            "stripeLocationId": null,
            "zipcode": null
        },
        "country": "US",
        "state": "OH",
        "autoReplace": false,
        "lineupTransactionId": null,
        "lineupTransactionStatus": null,
        "autoPayLineupStatus": "PENDING",
        "excludeOnsiteSalesFromReport": false,
        "showFeesBreakdown": false,
        "showBuyerInfoOnVenueMap": false,
        "venueMapId": null,
        "ticketHubInfo": null,
        "readOnlyFields": [],
        "medias": [],
        "tickets": [
            {
                "id": "{{ticket_id_General_Admission_02}}",
                "remote_id": null,
                "platform": "PEAR",
                "createdAt": "2026-08-21T08:59:12.986Z",
                "updatedAt": "2026-08-21T08:59:13.052Z",
                "merchantId": "{{eventcatalog_id}}",
                "title": "General Admission 02",
                "bodyHtml": "",
                "originalBodyHtml": "",
                "isBodyHtmlOverridden": false,
                "bodyText": "",
                "handle": null,
                "productType": "",
                "publishedAt": "2026-08-21T08:59:13.025Z",
                "publishedScope": "",
                "status": "ACTIVE",
                "externalStatus": "ACTIVE",
                "followExternalStatus": false,
                "tags": [],
                "templateSuffix": null,
                "vendor": "Pear",
                "syncAt": null,
                "deletedAt": null,
                "delisted": false,
                "excludedByImportingTag": false,
                "isFeatured": false,
                "featuredScore": null,
                "inventoryQuantity": 10000,
                "inventoryQuantityOriginal": 10000,
                "soldQuantity": 0,
                "priceDisplay": 112.22,
                "priceDisplayAnchor": 0,
                "priceMin": 112.22,
                "priceMinAnchor": 0,
                "priceMax": 112.22,
                "priceMaxAnchor": 0,
                "priceImportedMin": 0,
                "priceImportedMax": 0,
                "imageCount": 1,
                "isUsed": "NWT",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "deliveryTime": [
                    0,
                    5
                ],
                "returnPolicyApplied": true,
                "isAvailable": true,
                "commissionRate": 7,
                "textForShare": null,
                "priceSyncImported": false,
                "coverImage": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "useEventPosterAsCover": true,
                "reviewCount": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "displayReviews": true,
                "links": null,
                "taxEnable": false,
                "taxJarCategory": null,
                "overrideEventTax": false,
                "customTaxRate": null,
                "subscriptionPlanId": null,
                "reviewRedirectProductId": null,
                "reviewSummary": null,
                "customFieldsInfo": null,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "date": "Sat Apr 24, 2032 EDT",
                    "event": "Auto-Test-post-setting",
                    "venue": "Test venue · West Mound Street, Columbus, OH",
                    "lineup": [],
                    "poster": {
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072,
                        "height": 2048,
                        "position": 0,
                        "mediaType": "IMAGE",
                        "mediaDuration": 0
                    },
                    "status": "UPCOMING",
                    "location": "Test venue · West Mound Street, Columbus, OH",
                    "eventNote": "auto test",
                    "startDate": "2032-04-24T04:00:00.000Z",
                    "timeZoneId": "America/New_York",
                    "isAddressHidden": false,
                    "addressRevealConfig": null
                },
                "ticketHubInfo": null,
                "customizedFields": [],
                "bodyJson": null,
                "shippingOptions": null,
                "shippingNote": null,
                "autoFulfill": true,
                "eventId": "{{created_event_id}}",
                "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",
                "copyFromId": "{{ticket_id_General_Admission_02}}",
                "stopSellingAfter": null,
                "stopSellingAfterDisplay": null,
                "deliveryMethod": "QR_CODE",
                "thirdPartyDeliveryMessage": null,
                "isMultipleDaysPassEnabled": false,
                "isVenueUnitEnabled": false,
                "venueUnitCategoryId": null,
                "multipleDaysPass": null,
                "isPickupEtaEnabled": null,
                "eventMatchingRules": null,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "allowAtDoorSales": false,
                "isProductFormEnabled": false,
                "isVariantPriceDisplayEnabled": false,
                "isTipEnabled": false,
                "hideFees": false,
                "isPlatformFeeConfigCustomized": false,
                "isVariantPlatformFeeConfigCustomized": false,
                "transactionFeeConfig": {
                    "baseConfig": {
                        "unitFixedFee": 1,
                        "unitPercentageFee": 0.1
                    }
                },
                "transactionFeeRebateConfig": {
                    "baseConfig": {
                        "unitFixedFee": 0,
                        "unitPercentageFee": 0
                    }
                },
                "transactionCustomFeeConfig": null,
                "overrideEventCustomFee": false,
                "isInclusionsEnabled": false,
                "images": [
                    {
                        "id": "95ed387c-1f0c-43f9-ab26-29c61ca31176",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.052Z",
                        "updatedAt": "2026-08-21T08:59:13.052Z",
                        "height": 1000,
                        "width": 1000,
                        "position": 1,
                        "productId": "{{ticket_id_General_Admission_02}}",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "variantIds": [],
                        "mediaType": "IMAGE",
                        "mediaSrc": null,
                        "mediaDuration": 0,
                        "contributedBy": 3,
                        "contributorId": null,
                        "productImageType": "PRODUCT",
                        "source": null
                    }
                ],
                "options": [
                    {
                        "name": "Title",
                        "images": [
                            {
                                "value": "Default Title",
                                "image": null
                            }
                        ]
                    }
                ],
                "variants": [
                    {
                        "id": "{{variant_id_General_Admission_02}}",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.052Z",
                        "updatedAt": "2026-08-21T08:59:13.052Z",
                        "compareAtPrice": null,
                        "fulfillmentService": "manual",
                        "grams": 0,
                        "imageId": null,
                        "imageIds": [],
                        "inventoryItemId": null,
                        "inventoryManagement": "Pear",
                        "inventoryPolicy": "DENY",
                        "isInventoryQuantityUnlimited": false,
                        "inventoryQuantity": 10000,
                        "inventoryQuantityOriginal": 10000,
                        "soldQuantity": 0,
                        "option": {
                            "option1": "Default Title"
                        },
                        "position": 1,
                        "price": "112.22",
                        "priceAnchor": "0",
                        "priceImported": "0.00",
                        "productId": "{{ticket_id_General_Admission_02}}",
                        "sku": "",
                        "taxCode": null,
                        "taxable": true,
                        "title": "Default Title",
                        "weight": null,
                        "weightUnit": null,
                        "platform": null,
                        "fees": 12.22,
                        "transactionFee": {
                            "customFee": 0,
                            "platformFee": 12.22,
                            "customFeeBreakdown": {
                                "TAX": {
                                    "index": 0,
                                    "title": "Taxes",
                                    "itemFee": 0,
                                    "unitFixedFee": 0,
                                    "unitPercentageFee": 0
                                }
                            },
                            "transactionItemFee": 12.22
                        },
                        "ticketPrice": 100,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": 0,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": 0,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "transactionFeeConfig": null,
                        "transactionFeeRebateConfig": null,
                        "image": null
                    }
                ],
                "inclusions": [],
                "productForm": null
            },
            {
                "id": "{{ticket_id_General_Admission_01}}",
                "remote_id": null,
                "platform": "PEAR",
                "createdAt": "2026-08-21T08:59:12.985Z",
                "updatedAt": "2026-08-21T08:59:13.080Z",
                "merchantId": "{{eventcatalog_id}}",
                "title": "General Admission 01",
                "bodyHtml": "",
                "originalBodyHtml": "",
                "isBodyHtmlOverridden": false,
                "bodyText": "",
                "handle": null,
                "productType": "",
                "publishedAt": "2026-08-21T08:59:13.032Z",
                "publishedScope": "",
                "status": "ACTIVE",
                "externalStatus": "ACTIVE",
                "followExternalStatus": false,
                "tags": [],
                "templateSuffix": null,
                "vendor": "Pear",
                "syncAt": null,
                "deletedAt": null,
                "delisted": false,
                "excludedByImportingTag": false,
                "isFeatured": false,
                "featuredScore": null,
                "inventoryQuantity": 10000,
                "inventoryQuantityOriginal": 10000,
                "soldQuantity": 0,
                "priceDisplay": 67.77,
                "priceDisplayAnchor": 0,
                "priceMin": 67.77,
                "priceMinAnchor": 0,
                "priceMax": 67.77,
                "priceMaxAnchor": 0,
                "priceImportedMin": 0,
                "priceImportedMax": 0,
                "imageCount": 1,
                "isUsed": "NWT",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "deliveryTime": [
                    0,
                    5
                ],
                "returnPolicyApplied": true,
                "isAvailable": true,
                "commissionRate": 7,
                "textForShare": null,
                "priceSyncImported": false,
                "coverImage": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "useEventPosterAsCover": true,
                "reviewCount": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "displayReviews": true,
                "links": null,
                "taxEnable": false,
                "taxJarCategory": null,
                "overrideEventTax": false,
                "customTaxRate": null,
                "subscriptionPlanId": null,
                "reviewRedirectProductId": null,
                "reviewSummary": null,
                "customFieldsInfo": null,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "date": "Sat Apr 24, 2032 EDT",
                    "event": "Auto-Test-post-setting",
                    "venue": "Test venue · West Mound Street, Columbus, OH",
                    "lineup": [],
                    "poster": {
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072,
                        "height": 2048,
                        "position": 0,
                        "mediaType": "IMAGE",
                        "mediaDuration": 0
                    },
                    "status": "UPCOMING",
                    "location": "Test venue · West Mound Street, Columbus, OH",
                    "eventNote": "auto test",
                    "startDate": "2032-04-24T04:00:00.000Z",
                    "timeZoneId": "America/New_York",
                    "isAddressHidden": false,
                    "addressRevealConfig": null
                },
                "ticketHubInfo": null,
                "customizedFields": [],
                "bodyJson": null,
                "shippingOptions": null,
                "shippingNote": null,
                "autoFulfill": true,
                "eventId": "{{created_event_id}}",
                "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",
                "copyFromId": "{{ticket_id_General_Admission_01}}",
                "stopSellingAfter": null,
                "stopSellingAfterDisplay": null,
                "deliveryMethod": "QR_CODE",
                "thirdPartyDeliveryMessage": null,
                "isMultipleDaysPassEnabled": false,
                "isVenueUnitEnabled": false,
                "venueUnitCategoryId": null,
                "multipleDaysPass": null,
                "isPickupEtaEnabled": null,
                "eventMatchingRules": null,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "allowAtDoorSales": false,
                "isProductFormEnabled": false,
                "isVariantPriceDisplayEnabled": false,
                "isTipEnabled": false,
                "hideFees": false,
                "isPlatformFeeConfigCustomized": false,
                "isVariantPlatformFeeConfigCustomized": false,
                "transactionFeeConfig": {
                    "baseConfig": {
                        "unitFixedFee": 1,
                        "unitPercentageFee": 0.1
                    }
                },
                "transactionFeeRebateConfig": {
                    "baseConfig": {
                        "unitFixedFee": 0,
                        "unitPercentageFee": 0
                    }
                },
                "transactionCustomFeeConfig": null,
                "overrideEventCustomFee": false,
                "isInclusionsEnabled": false,
                "images": [
                    {
                        "id": "c3711955-0d20-460b-8f65-d30fc691b6c8",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.080Z",
                        "updatedAt": "2026-08-21T08:59:13.080Z",
                        "height": 1000,
                        "width": 1000,
                        "position": 1,
                        "productId": "{{ticket_id_General_Admission_01}}",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "variantIds": [],
                        "mediaType": "IMAGE",
                        "mediaSrc": null,
                        "mediaDuration": 0,
                        "contributedBy": 3,
                        "contributorId": null,
                        "productImageType": "PRODUCT",
                        "source": null
                    }
                ],
                "options": [
                    {
                        "name": "Title",
                        "images": [
                            {
                                "value": "Default Title",
                                "image": null
                            }
                        ]
                    }
                ],
                "variants": [
                    {
                        "id": "{{variant_id_General_Admission_01}}",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.080Z",
                        "updatedAt": "2026-08-21T08:59:13.080Z",
                        "compareAtPrice": null,
                        "fulfillmentService": "manual",
                        "grams": 0,
                        "imageId": null,
                        "imageIds": [],
                        "inventoryItemId": null,
                        "inventoryManagement": "Pear",
                        "inventoryPolicy": "DENY",
                        "isInventoryQuantityUnlimited": false,
                        "inventoryQuantity": 10000,
                        "inventoryQuantityOriginal": 10000,
                        "soldQuantity": 0,
                        "option": {
                            "option1": "Default Title"
                        },
                        "position": 1,
                        "price": "67.77",
                        "priceAnchor": "0",
                        "priceImported": "0.00",
                        "productId": "{{ticket_id_General_Admission_01}}",
                        "sku": "",
                        "taxCode": null,
                        "taxable": true,
                        "title": "Default Title",
                        "weight": null,
                        "weightUnit": null,
                        "platform": null,
                        "fees": 7.77,
                        "transactionFee": {
                            "customFee": 0,
                            "platformFee": 7.77,
                            "customFeeBreakdown": {
                                "TAX": {
                                    "index": 0,
                                    "title": "Taxes",
                                    "itemFee": 0,
                                    "unitFixedFee": 0,
                                    "unitPercentageFee": 0
                                }
                            },
                            "transactionItemFee": 7.77
                        },
                        "ticketPrice": 60,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": 0,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": 0,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "transactionFeeConfig": null,
                        "transactionFeeRebateConfig": null,
                        "image": null
                    }
                ],
                "inclusions": [],
                "productForm": null
            },
            {
                "id": "{{ticket_id_General_Admission}}",
                "remote_id": null,
                "platform": "PEAR",
                "createdAt": "2026-08-21T08:59:12.984Z",
                "updatedAt": "2026-08-21T08:59:13.103Z",
                "merchantId": "{{eventcatalog_id}}",
                "title": "General Admission",
                "bodyHtml": "",
                "originalBodyHtml": "",
                "isBodyHtmlOverridden": false,
                "bodyText": "",
                "handle": null,
                "productType": "",
                "publishedAt": "2026-08-21T08:59:13.037Z",
                "publishedScope": "",
                "status": "ACTIVE",
                "externalStatus": "ACTIVE",
                "followExternalStatus": false,
                "tags": [],
                "templateSuffix": null,
                "vendor": "Pear",
                "syncAt": null,
                "deletedAt": null,
                "delisted": false,
                "excludedByImportingTag": false,
                "isFeatured": false,
                "featuredScore": null,
                "inventoryQuantity": 10000,
                "inventoryQuantityOriginal": 10000,
                "soldQuantity": 0,
                "priceDisplay": 92.22,
                "priceDisplayAnchor": 0,
                "priceMin": 92.22,
                "priceMinAnchor": 0,
                "priceMax": 92.22,
                "priceMaxAnchor": 0,
                "priceImportedMin": 0,
                "priceImportedMax": 0,
                "imageCount": 1,
                "isUsed": "NWT",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "deliveryTime": [
                    0,
                    5
                ],
                "returnPolicyApplied": true,
                "isAvailable": true,
                "commissionRate": 7,
                "textForShare": null,
                "priceSyncImported": false,
                "coverImage": {
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072,
                    "height": 2048,
                    "position": 0,
                    "mediaType": "IMAGE",
                    "mediaDuration": 0
                },
                "useEventPosterAsCover": true,
                "reviewCount": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "displayReviews": true,
                "links": null,
                "taxEnable": false,
                "taxJarCategory": null,
                "overrideEventTax": false,
                "customTaxRate": null,
                "subscriptionPlanId": null,
                "reviewRedirectProductId": null,
                "reviewSummary": null,
                "customFieldsInfo": null,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "date": "Sat Apr 24, 2032 EDT",
                    "event": "Auto-Test-post-setting",
                    "venue": "Test venue · West Mound Street, Columbus, OH",
                    "lineup": [],
                    "poster": {
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072,
                        "height": 2048,
                        "position": 0,
                        "mediaType": "IMAGE",
                        "mediaDuration": 0
                    },
                    "status": "UPCOMING",
                    "location": "Test venue · West Mound Street, Columbus, OH",
                    "eventNote": "auto test",
                    "startDate": "2032-04-24T04:00:00.000Z",
                    "timeZoneId": "America/New_York",
                    "isAddressHidden": false,
                    "addressRevealConfig": null
                },
                "ticketHubInfo": null,
                "customizedFields": [],
                "bodyJson": null,
                "shippingOptions": null,
                "shippingNote": null,
                "autoFulfill": true,
                "eventId": "{{created_event_id}}",
                "lifecycleStatus": "LIFECYCLE_STATUS_NORMAL",
                "copyFromId": "{{ticket_id_General_Admission}}",
                "stopSellingAfter": null,
                "stopSellingAfterDisplay": null,
                "deliveryMethod": "QR_CODE",
                "thirdPartyDeliveryMessage": null,
                "isMultipleDaysPassEnabled": false,
                "isVenueUnitEnabled": false,
                "venueUnitCategoryId": null,
                "multipleDaysPass": null,
                "isPickupEtaEnabled": null,
                "eventMatchingRules": null,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "allowAtDoorSales": false,
                "isProductFormEnabled": false,
                "isVariantPriceDisplayEnabled": false,
                "isTipEnabled": false,
                "hideFees": false,
                "isPlatformFeeConfigCustomized": false,
                "isVariantPlatformFeeConfigCustomized": false,
                "transactionFeeConfig": {
                    "baseConfig": {
                        "unitFixedFee": 1,
                        "unitPercentageFee": 0.1
                    }
                },
                "transactionFeeRebateConfig": {
                    "baseConfig": {
                        "unitFixedFee": 0,
                        "unitPercentageFee": 0
                    }
                },
                "transactionCustomFeeConfig": null,
                "overrideEventCustomFee": false,
                "isInclusionsEnabled": false,
                "images": [
                    {
                        "id": "9564cc3d-78cc-4c92-90bb-df92227b92fb",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.103Z",
                        "updatedAt": "2026-08-21T08:59:13.103Z",
                        "height": 1000,
                        "width": 1000,
                        "position": 1,
                        "productId": "{{ticket_id_General_Admission}}",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "variantIds": [],
                        "mediaType": "IMAGE",
                        "mediaSrc": null,
                        "mediaDuration": 0,
                        "contributedBy": 3,
                        "contributorId": null,
                        "productImageType": "PRODUCT",
                        "source": null
                    }
                ],
                "options": [
                    {
                        "name": "Title",
                        "images": [
                            {
                                "value": "Default Title",
                                "image": null
                            }
                        ]
                    }
                ],
                "variants": [
                    {
                        "id": "{{variant_id_General_Admission}}",
                        "remote_id": null,
                        "createdAt": "2026-08-21T08:59:13.103Z",
                        "updatedAt": "2026-08-21T08:59:13.103Z",
                        "compareAtPrice": null,
                        "fulfillmentService": "manual",
                        "grams": 0,
                        "imageId": null,
                        "imageIds": [],
                        "inventoryItemId": null,
                        "inventoryManagement": "Pear",
                        "inventoryPolicy": "DENY",
                        "isInventoryQuantityUnlimited": false,
                        "inventoryQuantity": 10000,
                        "inventoryQuantityOriginal": 10000,
                        "soldQuantity": 0,
                        "option": {
                            "option1": "Default Title"
                        },
                        "position": 1,
                        "price": "92.22",
                        "priceAnchor": "0",
                        "priceImported": "0.00",
                        "productId": "{{ticket_id_General_Admission}}",
                        "sku": "",
                        "taxCode": null,
                        "taxable": true,
                        "title": "Default Title",
                        "weight": null,
                        "weightUnit": null,
                        "platform": null,
                        "fees": 10.22,
                        "transactionFee": {
                            "customFee": 0,
                            "platformFee": 10.22,
                            "customFeeBreakdown": {
                                "TAX": {
                                    "index": 0,
                                    "title": "Taxes",
                                    "itemFee": 0,
                                    "unitFixedFee": 0,
                                    "unitPercentageFee": 0
                                }
                            },
                            "transactionItemFee": 10.22
                        },
                        "ticketPrice": 82,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": 0,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": 0,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "transactionFeeConfig": null,
                        "transactionFeeRebateConfig": null,
                        "image": null
                    }
                ],
                "inclusions": [],
                "productForm": null
            }
        ],
        "lineup": [],
        "eventProducts": [],
        "ignoreStartTime": true,
        "ignoreEndTime": true,
        "duplicateEventId": "{{created_event_id}}",
        "posterBackend": [
            {
                "height": 2048,
                "mediaDuration": 0,
                "mediaType": "IMAGE",
                "position": 0,
                "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                "width": 3072
            }
        ],
        "customFeeConfig": null,
        "allowAutoComplete": true,
        "styleSettings": {
            "template": "ClearSky",
            "themeName": "MidnightGlow",
            "layout": {
                "pageHeader": {
                    "style": "DEDICATED_HEADER_BAR",
                    "displayText": "SHOP_NAME",
                    "height": "MEDIUM"
                },
                "productBanner": {
                    "ctaButton": "VIEW_PRODUCT",
                    "display": "HIDE"
                }
            },
            "fontFamily": "Inter",
            "color": "#FFFFFF",
            "backgroundColor": "#000000",
            "borderColor": "#000000",
            "dividerColor": "#5D5D5D",
            "secondaryTextColor": "#E0E0E0",
            "announcementCarousel": {
                "color": "#000000",
                "backgroundColor": "#F6CA7C"
            },
            "title": {
                "color": "#F6CA7C",
                "fontFamily": "Inter",
                "fontSize": 24,
                "fontWeight": 700
            },
            "columnTitle": {
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "subtitle": {
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 400,
                "color": "#FFFFFF"
            },
            "button": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000",
                "borderColor": "#000000",
                "borderRadius": 0,
                "boxShadow": "none",
                "fontSize": 16,
                "fontWeight": 400
            },
            "secondaryButton": {
                "fontSize": 16,
                "fontWeight": 400,
                "color": "#FFFFFF",
                "borderColor": "#F6CA7C",
                "borderRadius": 0,
                "boxShadow": "none"
            },
            "textButton": {
                "fontSize": 16,
                "fontWeight": 700,
                "color": "#FFFFFF"
            },
            "selectButton": {
                "borderColor": "#000000"
            },
            "relatedLink": {
                "borderRadius": 0,
                "color": "#000000 ",
                "borderColor": "#0000",
                "backgroundColor": "#FAFAFA"
            },
            "featuredProducts": {
                "borderRadius": 0,
                "backgroundColor": "#000000",
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 14,
                    "fontWeight": 400,
                    "color": "#FFFFFF"
                }
            },
            "product": {
                "backgroundColor": "#000000",
                "borderRadius": 0,
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0"
            },
            "discount": {
                "backgroundColor": "#D32A09",
                "color": "#FFFFFF",
                "priceColor": "#FFFFFF"
            },
            "freeShipping": {
                "backgroundColor": "#EBF5EF",
                "color": "#268E46"
            },
            "starRatingColor": "#FAAF03",
            "layoutFeatureCard": {
                "title": {
                    "fontFamily": "Inter",
                    "fontSize": 16,
                    "fontWeight": 700,
                    "color": "#FFFFFF"
                },
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "button": {
                    "backgroundColor": "#F6CA7C",
                    "color": "#000000"
                }
            },
            "lineupBanner": {
                "titleText": "#FFFFFF",
                "descriptionText": "#E0E0E0"
            },
            "eventInfoBanner": {
                "text": "#FFFFFF",
                "secondaryText": "#E0E0E0"
            },
            "eventDescription": {
                "text": "#E0E0E0",
                "title": "#FFFFFF"
            },
            "featuredProduct": {
                "cover": {
                    "borderRadius": 0
                }
            },
            "recentUsedColors": [
                "#ffffff"
            ]
        }
    }""", token="token", app_headers=True)
    expect(_resp116).json('$.code').equals('200')
    expect(_resp116).json('$.message').equals('success')
    # 同 step 106：响应为事件对象，无 eventId/postId 字段（事件 id=data.id，帖子=data.posts[0].id）
    ctx.extract("venue_map_event_id", _resp116, "$.data.id")
    ctx.extract("venue_map_post_id", _resp116, "$.data.posts[0].id")



    # --- step 117: Catch the ProductId promoterProductId merchantProductVariantId (GET post/v2/{{venue_map_post_id}}/relate-products) ---
    # NOTE: Same per-product JS-loop extraction as step 109 (second venue-map flow).
    # 同 step 107：接口仅在 admin 域存在，需 admin_token（base 域 404）。
    # 🔁 重试：同 step 107（relate-products 异步落地，偶发为空）。最多 5 次、间隔 3s。
    _resp117 = None
    for _rp_try in range(5):
        _resp117 = ctx.api.admin.post_v2_relate_products(
            path_vars={"post0_id": vars.get("venue_map_post_id", "")},
            token="admin_token", app_headers=True)
        expect(_resp117).json('$.code').equals('200')
        expect(_resp117).json('$.message').equals('success')
        try:
            expect(_resp117).json('$.data.relatedProducts').is_not_empty()
        except Exception:
            if _rp_try < 4:
                time.sleep(3)
                continue
            raise
        else:
            break
    # NOTE: 迁移时本段漏了提取（只有断言），导致 step 122 的 productId 仍沿用上一段
    #       （属于另一个 event）的 merchantProductId，后端报
    #       "Product <id> is not a ticket of this event"。此处按 step 107 的同一
    #       过滤规则补回提取，用本段 relate-products 的结果覆盖。
    for _vm_title, _vm_sfx in (
        ("General Admission 02", "_General_Admission_02"),
        ("General Admission 01", "_General_Admission_01"),
        ("General Admission", "_General_Admission"),
    ):
        _vm_prod = '$.data.relatedProducts[?(@.title=="%s")]' % _vm_title
        ctx.extract("productId" + _vm_sfx, _resp117, _vm_prod + ".merchantProductId")
        ctx.extract("venue_map_promoterProductId" + _vm_sfx, _resp117, _vm_prod + ".promoterProductId")
        ctx.extract("merchantProductVariantId" + _vm_sfx, _resp117,
                    _vm_prod + ".variants[0].merchantProductVariantId")
    expect(_resp117).json('$.data.relatedProducts').is_array()
    expect(_resp117).json('$.data.relatedProducts').is_not_empty()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp117).json('$.data.relatedProducts[0].merchantProductId').is_string()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp117).json('$.data.relatedProducts[0].merchantProductId').is_not_empty()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp117).json('$.data.relatedProducts[0].promoterProductId').is_string()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp117).json('$.data.relatedProducts[0].promoterProductId').is_not_empty()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp117).json('$.data.relatedProducts[0].variants[0].merchantProductVariantId').is_string()
    # 注：源为循环变量 product（脚本外定义），此处取数组 relatedProducts 的第 0 个元素
    expect(_resp117).json('$.data.relatedProducts[0].variants[0].merchantProductVariantId').is_not_empty()



    # --- step 118: Insert all tickets and all merch section (PATCH posts/curator/{{venue_map_post_id}}/content) ---
    _resp118 = ctx.api.posts.update_curator_content(body=r"""{
        "id": "{{venue_map_post_id}}",
        "createFromEventId": "{{venue_map_event_id}}",
        "headline": "{{event_title}}",
        "title": "{{event_title}}",
        "subTitle": "",
        "links": [],
        "bodyHtml": "",
        "syncEnabled": true,
        "postType": "EVENT",
        "products": [
            {
                "type": "PRODUCT",
                "originalCommissionRate": 100,
                "priceDisplayCost": 0,
                "displayVariantId": "{{venue_map_variant_id_General_Admission_02}}",
                "options": [
                    {
                        "name": "Title",
                        "values": [
                            "Default Title"
                        ],
                        "position": 1
                    }
                ],
                "inStock": true,
                "alias": "bzusuh",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "merchantProductImages": [
                    {
                        "id": "900a8d96-d912-4896-903b-adcc11bf543a",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "type": "IMAGE",
                        "height": 1000,
                        "width": 1000,
                        "mediaDuration": 0,
                        "mediaSrc": null,
                        "mediaType": "IMAGE",
                        "position": 1,
                        "productImageType": "PRODUCT"
                    }
                ],
                "promoterProductImages": [],
                "shippingInfo": {
                    "merchantName": "Events",
                    "returnPolicy": "No return accepted",
                    "shippingFee": "No shipping fee",
                    "deliveryTime": "0-0 business days",
                    "shippingPolicy": null,
                    "realShippingFee": 0
                },
                "shippingView": {
                    "productId": "{{venue_map_productId_General_Admission_02}}",
                    "shippingType": "NO_SHIPPING_REQUIRED",
                    "shippingNote": "",
                    "realShippingFee": 0,
                    "returnPolicy": "No return accepted",
                    "configCatalogShippingOptionId": null,
                    "shippingOptions": []
                },
                "merchant": {
                    "id": "{{eventcatalog_id}}",
                    "shopUrl": null
                },
                "discountPercent": 0,
                "isUsed": "NWT",
                "platform": "PEAR",
                "publishedAt": "2026-08-24T02:46:11.249Z",
                "merchantAvatar": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "reviewSummary": null,
                "status": "ACTIVE",
                "customFieldsInfo": null,
                "reviewCount": null,
                "title": "General Admission 02",
                "bodyHtml": "",
                "bodyText": "",
                "promoterProductId": "{{venue_map_promoterProductId_General_Admission_02}}",
                "productOwnerId": "{{curator_id}}",
                "priceMin": 112.22,
                "priceMax": 112.22,
                "priceDisplay": 112.22,
                "priceDisplayAnchor": 0,
                "priceMinAnchor": 0,
                "maxDiscountPercent": 0,
                "commissionRate": 100,
                "isVisible": true,
                "purchaseQuantityLimit": 1,
                "isPurchaseQuantityLimited": false,
                "isDefaultToSubscription": false,
                "syncWithCatalogPrice": true,
                "variants": [
                    {
                        "defaultCommissionRateForPromoters": 7,
                        "defaultWholesalePriceForPromoters": 104.36,
                        "isExcluded": false,
                        "isDefault": false,
                        "priceImported": "0.00",
                        "compareAtPrice": null,
                        "title": "Default Title",
                        "catalogPrice": 112.22,
                        "catalogPriceAnchor": 0,
                        "id": "{{venue_map_variant_id_General_Admission_02}}",
                        "position": 1,
                        "imageId": null,
                        "inventoryQuantity": 10000,
                        "isInventoryQuantityUnlimited": false,
                        "option": {
                            "option1": "Default Title"
                        },
                        "merchantProductVariantId": "{{venue_map_variant_id_General_Admission_02}}",
                        "inventoryItemId": null,
                        "inventoryPolicy": "DENY",
                        "commissionRateForPromoters": 7,
                        "commissionRateForMe": 100,
                        "costPrice": 0,
                        "wholesalePriceForPromoters": 0,
                        "price": 112.22,
                        "priceAnchor": 0,
                        "imageIds": [],
                        "inPost": true,
                        "discountPercent": 0,
                        "subscriptionPlanOptionPrices": [],
                        "fees": 12.22,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": null,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": null,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "weight": null,
                        "weightUnit": null
                    }
                ],
                "isFreeShipping": false,
                "hasDependentProducts": false,
                "dependentProductIds": [],
                "isRecommendation": false,
                "coverImage": {
                    "height": 2048,
                    "mediaDuration": 0,
                    "mediaType": "IMAGE",
                    "position": 0,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072
                },
                "isAvailable": true,
                "isNotAvailableReason": null,
                "isMyCatalog": true,
                "links": null,
                "merchantId": "{{eventcatalog_id}}",
                "merchantName": "Events",
                "merchantProductId": "{{venue_map_ticket_id_General_Admission_02}}",
                "canSetPrice": true,
                "subscriptionPlanId": null,
                "hasSubscriptionPlan": false,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "addressRevealConfig": null,
                    "date": "Mon Aug 24, 2026 EDT",
                    "event": "{{event_title}}",
                    "eventNote": "auto test",
                    "isAddressHidden": false,
                    "lineup": [],
                    "location": "Test venue 路 West Mound Street, Columbus, OH",
                    "poster": {
                        "height": 2048,
                        "mediaDuration": 0,
                        "mediaType": "IMAGE",
                        "position": 0,
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072
                    },
                    "startDate": "2026-08-24T04:00:00.000Z",
                    "status": "UPCOMING",
                    "timeZoneId": "America/New_York",
                    "venue": "Test venue 路 West Mound Street, Columbus, OH"
                },
                "feesDisplay": 12.22,
                "hideFees": false,
                "toReplaceMerchantProductIds": null,
                "event": {
                    "id": "{{venue_map_event_id}}",
                    "description": "",
                    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
                    "showFeesBreakdown": false
                },
                "eventId": "{{venue_map_event_id}}",
                "isCtaCustomized": false,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "isVenueUnitEnabled": false,
                "isAddedByPromoter": false,
                "id": "{{venue_map_ticket_id_General_Admission_02}}",
                "isCustomizePurchase": false,
                "hasReplaceProduct": false,
                "setCustomizePrice": false,
                "ctaConfig": {
                    "type": "BUY_NOW"
                }
            },
            {
                "type": "PRODUCT",
                "originalCommissionRate": 100,
                "priceDisplayCost": 0,
                "displayVariantId": "{{venue_map_variant_id_General_Admission_01}}",
                "options": [
                    {
                        "name": "Title",
                        "values": [
                            "Default Title"
                        ],
                        "position": 1
                    }
                ],
                "inStock": true,
                "alias": "er782n",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "merchantProductImages": [
                    {
                        "id": "0f9d5493-c44a-479e-96c0-a3f2eee06cb9",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "type": "IMAGE",
                        "height": 1000,
                        "width": 1000,
                        "mediaDuration": 0,
                        "mediaSrc": null,
                        "mediaType": "IMAGE",
                        "position": 1,
                        "productImageType": "PRODUCT"
                    }
                ],
                "promoterProductImages": [],
                "shippingInfo": {
                    "merchantName": "Events",
                    "returnPolicy": "No return accepted",
                    "shippingFee": "No shipping fee",
                    "deliveryTime": "0-0 business days",
                    "shippingPolicy": null,
                    "realShippingFee": 0
                },
                "shippingView": {
                    "productId": "{{venue_map_productId_General_Admission_01}}",
                    "shippingType": "NO_SHIPPING_REQUIRED",
                    "shippingNote": "",
                    "realShippingFee": 0,
                    "returnPolicy": "No return accepted",
                    "configCatalogShippingOptionId": null,
                    "shippingOptions": []
                },
                "merchant": {
                    "id": "{{eventcatalog_id}}",
                    "shopUrl": null
                },
                "discountPercent": 0,
                "isUsed": "NWT",
                "platform": "PEAR",
                "publishedAt": "2026-08-24T02:46:11.255Z",
                "merchantAvatar": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "reviewSummary": null,
                "status": "ACTIVE",
                "customFieldsInfo": null,
                "reviewCount": null,
                "title": "General Admission 01",
                "bodyHtml": "",
                "bodyText": "",
                "promoterProductId": "{{venue_map_promoterProductId_General_Admission_01}}",
                "productOwnerId": "{{curator_id}}",
                "priceMin": 67.77,
                "priceMax": 67.77,
                "priceDisplay": 67.77,
                "priceDisplayAnchor": 0,
                "priceMinAnchor": 0,
                "maxDiscountPercent": 0,
                "commissionRate": 100,
                "isVisible": true,
                "purchaseQuantityLimit": 1,
                "isPurchaseQuantityLimited": false,
                "isDefaultToSubscription": false,
                "syncWithCatalogPrice": true,
                "variants": [
                    {
                        "defaultCommissionRateForPromoters": 7,
                        "defaultWholesalePriceForPromoters": 63.03,
                        "isExcluded": false,
                        "isDefault": false,
                        "priceImported": "0.00",
                        "compareAtPrice": null,
                        "title": "Default Title",
                        "catalogPrice": 67.77,
                        "catalogPriceAnchor": 0,
                        "id": "{{venue_map_variant_id_General_Admission_01}}",
                        "position": 1,
                        "imageId": null,
                        "inventoryQuantity": 10000,
                        "isInventoryQuantityUnlimited": false,
                        "option": {
                            "option1": "Default Title"
                        },
                        "merchantProductVariantId": "{{venue_map_variant_id_General_Admission_01}}",
                        "inventoryItemId": null,
                        "inventoryPolicy": "DENY",
                        "commissionRateForPromoters": 7,
                        "commissionRateForMe": 100,
                        "costPrice": 0,
                        "wholesalePriceForPromoters": 0,
                        "price": 67.77,
                        "priceAnchor": 0,
                        "imageIds": [],
                        "inPost": true,
                        "discountPercent": 0,
                        "subscriptionPlanOptionPrices": [],
                        "fees": 7.77,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": null,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": null,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "weight": null,
                        "weightUnit": null
                    }
                ],
                "isFreeShipping": false,
                "hasDependentProducts": false,
                "dependentProductIds": [],
                "isRecommendation": false,
                "coverImage": {
                    "height": 2048,
                    "mediaDuration": 0,
                    "mediaType": "IMAGE",
                    "position": 0,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072
                },
                "isAvailable": true,
                "isNotAvailableReason": null,
                "isMyCatalog": true,
                "links": null,
                "merchantId": "{{eventcatalog_id}}",
                "merchantName": "Events",
                "merchantProductId": "{{venue_map_ticket_id_General_Admission_01}}",
                "canSetPrice": true,
                "subscriptionPlanId": null,
                "hasSubscriptionPlan": false,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "addressRevealConfig": null,
                    "date": "Mon Aug 24, 2026 EDT",
                    "event": "{{event_title}}",
                    "eventNote": "auto test",
                    "isAddressHidden": false,
                    "lineup": [],
                    "location": "Test venue 路 West Mound Street, Columbus, OH",
                    "poster": {
                        "height": 2048,
                        "mediaDuration": 0,
                        "mediaType": "IMAGE",
                        "position": 0,
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072
                    },
                    "startDate": "2026-08-24T04:00:00.000Z",
                    "status": "UPCOMING",
                    "timeZoneId": "America/New_York",
                    "venue": "Test venue 路 West Mound Street, Columbus, OH"
                },
                "feesDisplay": 7.77,
                "hideFees": false,
                "toReplaceMerchantProductIds": null,
                "event": {
                    "id": "{{venue_map_event_id}}",
                    "description": "",
                    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
                    "showFeesBreakdown": false
                },
                "eventId": "{{venue_map_event_id}}",
                "isCtaCustomized": false,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "isVenueUnitEnabled": true,
                "isAddedByPromoter": false,
                "id": "{{venue_map_ticket_id_General_Admission_01}}",
                "isCustomizePurchase": false,
                "hasReplaceProduct": false,
                "setCustomizePrice": false,
                "ctaConfig": {
                    "type": "BUY_NOW"
                }
            },
            {
                "type": "PRODUCT",
                "originalCommissionRate": 100,
                "priceDisplayCost": 0,
                "displayVariantId": "{{venue_map_variant_id_General_Admission}}",
                "options": [
                    {
                        "name": "Title",
                        "values": [
                            "Default Title"
                        ],
                        "position": 1
                    }
                ],
                "inStock": true,
                "alias": "a0kvr3",
                "shippingType": "NO_SHIPPING_REQUIRED",
                "additionalShippingFee": 0,
                "merchantProductImages": [
                    {
                        "id": "c988917d-f11f-4ef4-a62c-20f5263b3ff6",
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1755656006/uploaded_images/pt4zctae8zwv8jrljrf7.png",
                        "type": "IMAGE",
                        "height": 1000,
                        "width": 1000,
                        "mediaDuration": 0,
                        "mediaSrc": null,
                        "mediaType": "IMAGE",
                        "position": 1,
                        "productImageType": "PRODUCT"
                    }
                ],
                "promoterProductImages": [],
                "shippingInfo": {
                    "merchantName": "Events",
                    "returnPolicy": "No return accepted",
                    "shippingFee": "No shipping fee",
                    "deliveryTime": "0-0 business days",
                    "shippingPolicy": null,
                    "realShippingFee": 0
                },
                "shippingView": {
                    "productId": "{{venue_map_productId_General_Admission}}",
                    "shippingType": "NO_SHIPPING_REQUIRED",
                    "shippingNote": "",
                    "realShippingFee": 0,
                    "returnPolicy": "No return accepted",
                    "configCatalogShippingOptionId": null,
                    "shippingOptions": []
                },
                "merchant": {
                    "id": "{{eventcatalog_id}}",
                    "shopUrl": null
                },
                "discountPercent": 0,
                "isUsed": "NWT",
                "platform": "PEAR",
                "publishedAt": "2026-08-24T02:46:11.261Z",
                "merchantAvatar": null,
                "reviewOverallScore": null,
                "reviewAggregate": null,
                "reviewSummary": null,
                "status": "ACTIVE",
                "customFieldsInfo": null,
                "reviewCount": null,
                "title": "General Admission",
                "bodyHtml": "",
                "bodyText": "",
                "promoterProductId": "{{venue_map_promoterProductId_General_Admission}}",
                "productOwnerId": "{{curator_id}}",
                "priceMin": 92.22,
                "priceMax": 92.22,
                "priceDisplay": 92.22,
                "priceDisplayAnchor": 0,
                "priceMinAnchor": 0,
                "maxDiscountPercent": 0,
                "commissionRate": 100,
                "isVisible": true,
                "purchaseQuantityLimit": 1,
                "isPurchaseQuantityLimited": false,
                "isDefaultToSubscription": false,
                "syncWithCatalogPrice": true,
                "variants": [
                    {
                        "defaultCommissionRateForPromoters": 7,
                        "defaultWholesalePriceForPromoters": 85.76,
                        "isExcluded": false,
                        "isDefault": false,
                        "priceImported": "0.00",
                        "compareAtPrice": null,
                        "title": "Default Title",
                        "catalogPrice": 92.22,
                        "catalogPriceAnchor": 0,
                        "id": "{{venue_map_variant_id_General_Admission}}",
                        "position": 1,
                        "imageId": null,
                        "inventoryQuantity": 10000,
                        "isInventoryQuantityUnlimited": false,
                        "option": {
                            "option1": "Default Title"
                        },
                        "merchantProductVariantId": "{{venue_map_variant_id_General_Admission}}",
                        "inventoryItemId": null,
                        "inventoryPolicy": "DENY",
                        "commissionRateForPromoters": 7,
                        "commissionRateForMe": 100,
                        "costPrice": 0,
                        "wholesalePriceForPromoters": 0,
                        "price": 92.22,
                        "priceAnchor": 0,
                        "imageIds": [],
                        "inPost": true,
                        "discountPercent": 0,
                        "subscriptionPlanOptionPrices": [],
                        "fees": 10.22,
                        "isMinPurchaseQuantityEnabled": false,
                        "minPurchaseQuantity": null,
                        "isMaxPurchaseQuantityEnabled": false,
                        "maxPurchaseQuantity": null,
                        "isPackSizeEnabled": false,
                        "packSize": null,
                        "weight": null,
                        "weightUnit": null
                    }
                ],
                "isFreeShipping": false,
                "hasDependentProducts": false,
                "dependentProductIds": [],
                "isRecommendation": false,
                "coverImage": {
                    "height": 2048,
                    "mediaDuration": 0,
                    "mediaType": "IMAGE",
                    "position": 0,
                    "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                    "width": 3072
                },
                "isAvailable": true,
                "isNotAvailableReason": null,
                "isMyCatalog": true,
                "links": null,
                "merchantId": "{{eventcatalog_id}}",
                "merchantName": "Events",
                "merchantProductId": "{{venue_map_ticket_id_General_Admission}}",
                "canSetPrice": true,
                "subscriptionPlanId": null,
                "hasSubscriptionPlan": false,
                "listingType": "TICKET",
                "ticketType": "TICKET_TYPE_STANDARD",
                "extraInfo": {
                    "addressRevealConfig": null,
                    "date": "Mon Aug 24, 2026 EDT",
                    "event": "{{event_title}}",
                    "eventNote": "auto test",
                    "isAddressHidden": false,
                    "lineup": [],
                    "location": "Test venue 路 West Mound Street, Columbus, OH",
                    "poster": {
                        "height": 2048,
                        "mediaDuration": 0,
                        "mediaType": "IMAGE",
                        "position": 0,
                        "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                        "width": 3072
                    },
                    "startDate": "2026-08-24T04:00:00.000Z",
                    "status": "UPCOMING",
                    "timeZoneId": "America/New_York",
                    "venue": "Test venue 路 West Mound Street, Columbus, OH"
                },
                "feesDisplay": 10.22,
                "hideFees": false,
                "toReplaceMerchantProductIds": null,
                "event": {
                    "id": "{{venue_map_event_id}}",
                    "description": "",
                    "descriptionBodyJson": "{\"root\":{\"children\":[{\"children\":[],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":null,\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
                    "showFeesBreakdown": false
                },
                "eventId": "{{venue_map_event_id}}",
                "isCtaCustomized": false,
                "isExpirationEnabled": false,
                "expirationTime": null,
                "expirationTimeDisplay": null,
                "isVenueUnitEnabled": false,
                "isAddedByPromoter": false,
                "id": "{{venue_map_ticket_id_General_Admission}}",
                "isCustomizePurchase": false,
                "hasReplaceProduct": false,
                "setCustomizePrice": false,
                "ctaConfig": {
                    "type": "BUY_NOW"
                }
            }
        ],
        "styleSettings": {
            "recentUsedColors": [
                "#ffffff"
            ],
            "fontFamily": "Inter",
            "color": "#FFFFFF",
            "backgroundColor": "#000000",
            "borderColor": "#000000",
            "dividerColor": "#FFFFFF",
            "secondaryTextColor": "#E0E0E0",
            "announcementCarousel": {
                "backgroundColor": "#F6CA7C",
                "color": "#000000"
            },
            "title": {
                "color": "#F6CA7C",
                "fontFamily": "Inter",
                "fontSize": 24,
                "fontWeight": 700
            },
            "columnTitle": {
                "color": "#FFFFFF",
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 700
            },
            "subtitle": {
                "color": "#FFFFFF",
                "fontFamily": "Inter",
                "fontSize": 20,
                "fontWeight": 400
            },
            "button": {
                "backgroundColor": "#F6CA7C",
                "borderColor": "#000000",
                "borderRadius": 12,
                "boxShadow": "none",
                "color": "#000000",
                "fontSize": 16,
                "fontWeight": 700
            },
            "secondaryButton": {
                "borderColor": "#F6CA7C",
                "borderRadius": 12,
                "boxShadow": "none",
                "color": "#FFFFFF",
                "fontSize": 16,
                "fontWeight": 700
            },
            "textButton": {
                "color": "#FFFFFF",
                "fontSize": 16,
                "fontWeight": 700
            },
            "selectButton": {
                "borderColor": "#000000"
            },
            "relatedLink": {
                "backgroundColor": "#FAFAFA",
                "borderColor": "#0000",
                "borderRadius": 99,
                "color": "#000000 "
            },
            "featuredProducts": {
                "backgroundColor": "#000000",
                "borderRadius": 16,
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "title": {
                    "color": "#FFFFFF",
                    "fontFamily": "Inter",
                    "fontSize": 14,
                    "fontWeight": 400
                }
            },
            "product": {
                "backgroundColor": "#000000",
                "borderRadius": 8,
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0"
            },
            "discount": {
                "backgroundColor": "#D32A09",
                "color": "#FFFFFF",
                "priceColor": "#FFFFFF"
            },
            "freeShipping": {
                "backgroundColor": "#EBF5EF",
                "color": "#268E46"
            },
            "starRatingColor": "#FAAF03",
            "layoutFeatureCard": {
                "button": {
                    "backgroundColor": "#F6CA7C",
                    "color": "#000000"
                },
                "color": "#FFFFFF",
                "secondaryTextColor": "#E0E0E0",
                "title": {
                    "color": "#FFFFFF",
                    "fontFamily": "Inter",
                    "fontSize": 16,
                    "fontWeight": 700
                }
            },
            "lineupBanner": {
                "descriptionText": "#E0E0E0",
                "titleText": "#FFFFFF"
            },
            "eventInfoBanner": {
                "secondaryText": "#E0E0E0",
                "text": "#FFFFFF"
            },
            "eventDescription": {
                "text": "#E0E0E0",
                "title": "#FFFFFF"
            },
            "featuredProduct": {
                "cover": {
                    "borderRadius": 0
                }
            },
            "layout": {
                "pageHeader": {
                    "displayText": "SHOP_NAME",
                    "height": "MEDIUM",
                    "style": "DEDICATED_HEADER_BAR"
                },
                "productBanner": {
                    "ctaButton": "VIEW_PRODUCT",
                    "display": "HIDE"
                }
            },
            "template": "ClearSky"
        },
        "featuredSectionEnable": false,
        "featuredSectionTitle": "",
        "recommendationSectionTitle": "",
        "bodyJson": "{\"root\":{\"children\":[{\"id\":\"2d77f532-fadd-4825-a8b5-9a4cc18d183d\",\"allTickets\":[{\"eventId\":\"{{venue_map_event_id}}\",\"productId\":\"{{venue_map_productId_General_Admission_01}}\",\"variantId\":\"{{venue_map_variant_id_General_Admission_01}}\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"thumbnailDisplay\":\"showThumbnail\",\"eventNotesDisplay\":\"showEventNotes\",\"position\":0,\"isVisible\":true,\"applyToAll\":false},{\"eventId\":\"{{venue_map_event_id}}\",\"productId\":\"{{venue_map_productId_General_Admission}}\",\"variantId\":\"{{venue_map_variant_id_General_Admission}}\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"thumbnailDisplay\":\"showThumbnail\",\"eventNotesDisplay\":\"showEventNotes\",\"position\":1,\"isVisible\":true,\"applyToAll\":false},{\"eventId\":\"{{venue_map_event_id}}\",\"productId\":\"{{venue_map_productId_General_Admission_02}}\",\"variantId\":\"{{venue_map_variant_id_General_Admission_02}}\",\"ctaLabel\":\"Buy Ticket\",\"action\":\"buy-now\",\"layout\":\"vertical\",\"thumbnailDisplay\":\"showThumbnail\",\"eventNotesDisplay\":\"showEventNotes\",\"position\":2,\"isVisible\":true,\"applyToAll\":false}],\"width\":\"100%\",\"height\":\"\",\"showDivider\":true,\"orderingMode\":\"auto\",\"type\":\"ticket-all\",\"version\":1},{\"id\":\"8804bb99-8aa9-4ab6-b5e8-dd340c842e7f\",\"allMerchandise\":[],\"width\":\"100%\",\"height\":\"\",\"showDivider\":true,\"type\":\"merchandise-all\",\"version\":1},{\"id\":\"03e9c4b2-6f24-4233-bee0-1518f4e164fa\",\"eventId\":\"{{venue_map_event_id}}\",\"width\":\"100%\",\"showDivider\":true,\"type\":\"event-info-banner\",\"version\":2},{\"children\":[],\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"},{\"children\":[],\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"},{\"id\":\"09de8dbb-c76a-4750-999b-b1a2bbe7e924\",\"eventId\":\"{{venue_map_event_id}}\",\"allMedia\":[],\"width\":\"100%\",\"height\":\"\",\"title\":\"Missed our last event?\",\"subtitle\":\"Here's a lil recap of our last event馃憞\",\"align\":\"center\",\"showDivider\":true,\"type\":\"event-media\",\"version\":1},{\"children\":[],\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"},{\"id\":\"b7f278d3-4ef4-40d3-8f97-e22170502153\",\"eventId\":\"{{venue_map_event_id}}\",\"width\":\"100%\",\"showDivider\":true,\"type\":\"post-event-description\",\"version\":2},{\"children\":[],\"format\":\"\",\"indent\":0,\"type\":\"katana-paragraph\",\"version\":1,\"textFormat\":0,\"textStyle\":\"\",\"style\":\"\"}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1},\"containerClassName\":\"katana-t8777m\"}",
        "status": "ACTIVE",
        "media": [
            {
                "id": "15ba8a6b-08b1-4508-8540-81cc81524e72",
                "src": "https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png",
                "selected": true,
                "type": "IMAGE",
                "height": 2048,
                "width": 3072,
                "mediaDuration": 0,
                "mediaSrc": null,
                "mediaType": "IMAGE",
                "inherited": true,
                "position": 1,
                "referenceId": null,
                "source": null,
                "setThumbnail": false
            }
        ],
        "needRefreshHTML": true,
        "urlAlias": "{{event_title}}"
    }""", token="token", app_headers=True)
    expect(_resp118).json('$.code').equals('200')
    expect(_resp118).json('$.message').equals('success')



    # --- step 119: search the category id (GET merchant/product/search?pageSize=100&eventId={{venue_map_event_id}}) ---
    # NOTE: Same search-id JS-loop extraction as step 112 (second venue-map flow).
    # 同 step 110：接口仅在 admin 域存在，且需 ?pageSize=&eventId= 与 admin_token。
    _resp119 = ctx.api.admin.merchant_product_search(
        params={"pageSize": "100", "eventId": vars.get("venue_map_event_id", "")},
        token="admin_token", app_headers=True)
    expect(_resp119).json('$.code').equals('200')
    expect(_resp119).json('$.message').equals('success')
    # NOTE: 迁移时本段漏了提取（只有长度断言），导致 step 120/122 的
    #       {{categoryId_*}} 渲染成字面量、venue-map 建图与绑定的类目全空。
    #       按 step 110 的同一规则补回提取（categoryId 缺失时回退 venueCategoryId）。
    for _vm_title, _vm_sfx in (
        ("General Admission 02", "_General_Admission_02"),
        ("General Admission 01", "_General_Admission_01"),
        ("General Admission", "_General_Admission"),
    ):
        _vm_item = '$.data.items[?(@.title=="%s")]' % _vm_title
        ctx.extract("ticket_id" + _vm_sfx, _resp119, _vm_item + ".id")
        ctx.extract("venueUnitCategoryId" + _vm_sfx, _resp119, _vm_item + ".venueUnitCategoryId")
        _vm_cat = ctx.extract("categoryId" + _vm_sfx, _resp119, _vm_item + ".categoryId")
        if _vm_cat is None:
            ctx.extract("categoryId" + _vm_sfx, _resp119, _vm_item + ".venueCategoryId")
    expect(_resp119).json('$.data.items.length').at_least(1)



    # --- step 120: Create Venue map (POST events/{{venue_map_event_id}}/venue-map) ---
    # ⚠️ 同 step 111：仅 admin 域 + admin_token。
    _resp120 = ctx.api.admin.events_venue_map_create(
        path_vars={"venue_map_event_id": vars.get("venue_map_event_id", "")},
        body="""{
        "venueData": {
            "version": 1,
            "mode": "SECTION",
            "sections": [],
            "rows": [
                {
                    "id": "84743235-32b0-4a91-a8c2-b4ff48781e87",
                    "chairSpacing": 20,
                    "seatLabeling": {
                        "algorithm": "NUMBERS",
                        "startAtIndex": 0,
                        "inverted": false,
                        "useEndAt": false
                    },
                    "seats": [
                        {
                            "id": "6034d01c-a994-40af-982d-75c8cd61083b",
                            "x": 200,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "1",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "0ada37a5-2711-4b58-ba43-e45c3aef617b",
                            "x": 221,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "2",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "179778d0-fdcb-408f-9a44-6d973bcdef0a",
                            "x": 242,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "3",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "8aac52a3-1713-4d45-9974-dd6a290c7016",
                            "x": 263,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "4",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "0cfed81c-3f29-4f40-916e-694c73495c75",
                            "x": 284,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "5",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "8062527d-acbc-4709-a51b-c4b3b9658c75",
                            "x": 305,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "6",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "bc510ab4-457f-4b0c-90fa-fb8d566c7d4b",
                            "x": 326,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "7",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "5c8bd617-4677-4b55-9035-1f998d0eb0b0",
                            "x": 347,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "8",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "795ca6b1-75c8-4c9b-a0d7-cd6fb6e8d9fa",
                            "x": 368,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "9",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "c8d285dc-1e37-4f7f-a0e0-b8a414bcaf77",
                            "x": 389,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "10",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "28f9ee6c-ec08-4c76-aa65-18821b14f3f8",
                            "x": 410,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "11",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "b2244c31-d5eb-47dc-aba9-d34ddaf82fa5",
                            "x": 431,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "12",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "18eaa71a-0090-4488-b7d5-ffcd011b1bbc",
                            "x": 452,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "13",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "3d0fa510-a654-49a3-82e6-a73c163504b9",
                            "x": 473,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "14",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "a3b164bc-bbfd-49ad-93fb-3290d1f54681",
                            "x": 494,
                            "y": 0,
                            "categoryId": "{{categoryId_General_Admission_02}}",
                            "categoryKey": 1,
                            "categoryLabel": "General Admission 02",
                            "categoryAccessible": false,
                            "label": "15",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        }
                    ],
                    "label": null,
                    "displayLabel": null,
                    "sectionLabel": null,
                    "sectionDisplayedLabel": null,
                    "curve": 0,
                    "rotationAngle": 0,
                    "smooth": false,
                    "smoothness": 50,
                    "rowLabelDisabled": false,
                    "displayObjectType": "row",
                    "viewFromYourSeatImage": null,
                    "entrance": null,
                    "published": false,
                    "points": null,
                    "objectType": "row",
                    "verticalRowLabelDirection": "BASELINE_LEFT"
                },
                {
                    "id": "f7bd43cd-5acd-47a9-8008-a9e3e5385a71",
                    "chairSpacing": 20,
                    "seatLabeling": {
                        "algorithm": "NUMBERS",
                        "startAtIndex": 0,
                        "inverted": false,
                        "useEndAt": false
                    },
                    "seats": [
                        {
                            "id": "4c4ee7e4-5848-44f2-8f02-4a6282a2f194",
                            "x": 200,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "1",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "8435be0f-1d1a-4408-9aa8-02e0e090299f",
                            "x": 221,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "2",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "e1772c5b-3d3d-45b6-90da-5859798add14",
                            "x": 242,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "3",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "da54cca9-a861-402a-b319-395502ed03cc",
                            "x": 263,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "4",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "667f4c4c-1092-4d2f-a0cd-535842fce60d",
                            "x": 284,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "5",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "bb6bf47d-62f6-4a8b-9ab8-4ad2010165a4",
                            "x": 305,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "6",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "0267e056-7c83-4512-9b52-5b5a2399ab45",
                            "x": 326,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "7",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "93f9e77d-145c-46fd-ad70-1f10e817d936",
                            "x": 347,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "8",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "f5bb72fc-9c79-40d4-b67f-36d2756637f4",
                            "x": 368,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "9",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "c51e4e5d-1609-4942-9017-8c3d3f143a91",
                            "x": 389,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "10",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "5a61d28c-7858-4298-ab04-39a6919bfb76",
                            "x": 410,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "11",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "85edb5dd-9252-4b90-840b-81518a385ebd",
                            "x": 431,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "12",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "b6326aeb-7e2e-42c5-bc56-e5009ecbee3b",
                            "x": 452,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "13",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "471c7972-6a75-444e-a5be-388a1a86ec6f",
                            "x": 473,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "14",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "e7eb390c-57a0-47c4-8e3e-f19e8ca2aa46",
                            "x": 494,
                            "y": 30,
                            "categoryId": "{{categoryId_General_Admission_01}}",
                            "categoryKey": 2,
                            "categoryLabel": "General Admission 01",
                            "categoryAccessible": false,
                            "label": "15",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        }
                    ],
                    "label": null,
                    "displayLabel": null,
                    "sectionLabel": null,
                    "sectionDisplayedLabel": null,
                    "curve": 0,
                    "rotationAngle": 0,
                    "smooth": false,
                    "smoothness": 50,
                    "rowLabelDisabled": false,
                    "displayObjectType": "row",
                    "viewFromYourSeatImage": null,
                    "entrance": null,
                    "published": false,
                    "points": null,
                    "objectType": "row",
                    "verticalRowLabelDirection": "BASELINE_LEFT"
                },
                {
                    "id": "95d63e15-56f5-486b-b47c-c750c53c629d",
                    "chairSpacing": 20,
                    "seatLabeling": {
                        "algorithm": "NUMBERS",
                        "startAtIndex": 0,
                        "inverted": false,
                        "useEndAt": false
                    },
                    "seats": [
                        {
                            "id": "831ad517-2f81-4c76-9bea-6c6109f85e43",
                            "x": 200,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "1",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "15696971-367b-4d3e-90df-0d3d6eefb132",
                            "x": 221,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "2",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "79c277ed-41de-4f9c-88cf-246880ae9b50",
                            "x": 242,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "3",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "df47bc60-0023-4586-9f0c-0e07028039b8",
                            "x": 263,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "4",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "43248efa-a96d-43eb-95d9-c529b82b288e",
                            "x": 284,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "5",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "558ed673-181e-4585-b8b7-7608a3306f42",
                            "x": 305,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "6",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "b0b28a67-5be0-41b4-aa37-9ff232c9e4e6",
                            "x": 326,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "7",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "44463d8b-4a76-4d55-ab49-090c32d7f7d7",
                            "x": 347,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "8",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "f231471d-23a6-44fb-9dc0-e968bd16504c",
                            "x": 368,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "9",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "62c4d181-75aa-45a4-b3e7-703a81bd8984",
                            "x": 389,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "10",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "1494d66f-36ef-4451-b0d5-3ea955c1d7e3",
                            "x": 410,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "11",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "4a2f7a90-b68b-430c-a5c0-51172cb63484",
                            "x": 431,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "12",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "5fe47f91-16d5-4ee7-9564-542520f07ff9",
                            "x": 452,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "13",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "d8fcbb55-db47-4a51-b8bb-a833f0718edf",
                            "x": 473,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "14",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        },
                        {
                            "id": "894630a1-ba52-485d-9409-1791943868c3",
                            "x": 494,
                            "y": 60,
                            "categoryId": "{{categoryId_General_Admission}}",
                            "categoryKey": 3,
                            "categoryLabel": "General Admission",
                            "categoryAccessible": false,
                            "label": "15",
                            "displayLabel": null,
                            "displayObjectType": "seat",
                            "restrictedView": false,
                            "hearingImpaired": false,
                            "signLanguageInterpretation": false,
                            "cartServices": false,
                            "liftUpArmrests": false,
                            "accessible": false,
                            "companionSeat": false,
                            "semiAmbulatorySeat": false,
                            "plusSize": false,
                            "wheelchairSpaceType": null,
                            "disabledBySocialDistancingRules": false,
                            "viewFromYourSeatImage": null,
                            "entrance": null,
                            "published": false
                        }
                    ],
                    "label": null,
                    "displayLabel": null,
                    "sectionLabel": null,
                    "sectionDisplayedLabel": null,
                    "curve": 0,
                    "rotationAngle": 0,
                    "smooth": false,
                    "smoothness": 50,
                    "rowLabelDisabled": false,
                    "displayObjectType": "row",
                    "viewFromYourSeatImage": null,
                    "entrance": null,
                    "published": false,
                    "points": null,
                    "objectType": "row",
                    "verticalRowLabelDirection": "BASELINE_LEFT"
                }
            ],
            "shapes": [],
            "gaAreas": [],
            "texts": [],
            "icons": [],
            "images": [],
            "tables": [],
            "booths": [],
            "categories": [
                {
                    "id": "{{categoryId_General_Admission_02}}",
                    "key": 1,
                    "label": "General Admission 02",
                    "color": "#992C4E",
                    "accessible": false
                },
                {
                    "id": "{{categoryId_General_Admission_01}}",
                    "key": 2,
                    "label": "General Admission 01",
                    "color": "#CD254A",
                    "accessible": false
                },
                {
                    "id": "{{categoryId_General_Admission}}",
                    "key": 3,
                    "label": "General Admission",
                    "color": "#E9803D",
                    "accessible": false
                }
            ],
            "maxCategoryKey": 3,
            "focalPoint": null,
            "background": null
        }
    }""", token="admin_token", app_headers=True)
    expect(_resp120).json('$.code').equals('200')
    expect(_resp120).json('$.message').equals('success')
    expect(_resp120).json('$.data.id').exists()
    expect(_resp120).json('$.data.venueDataDraft.rows[0].seats[0]').is_object()
    expect(_resp120).json('$.data.venueDataDraft.rows[0].seats[0].categoryId').is_string()
    expect(_resp120).json('$.data.venueDataDraft.rows[0].seats[0].categoryId').is_not_empty()



    # --- step 121: publish the seat (POST events/{{venue_map_event_id}}/venue-map/publish) ---
    # ⚠️ 同 step 111：仅 admin 域 + admin_token。
    _resp121 = ctx.api.admin.events_venue_map_publish(
        path_vars={"venue_map_event_id": vars.get("venue_map_event_id", "")},
        token="admin_token", app_headers=True)
    expect(_resp121).json('$.code').equals('200')
    expect(_resp121).json('$.message').equals('success')



    # --- step 122: Bind the seat to the product (POST events/{{venue_map_event_id}}/venue-map/associations) ---
    # ⚠️ 同 step 111：仅 admin 域 + admin_token。
    _resp122 = ctx.api.admin.events_venue_map_associations(
        path_vars={"venue_map_event_id": vars.get("venue_map_event_id", "")},
        body="""{
        "associations": [
            {
                "categoryId": "{{categoryId_General_Admission_02}}",
                "productId": "{{productId_General_Admission_02}}"
            },
            {
                "categoryId": "{{categoryId_General_Admission_01}}",
                "productId": "{{productId_General_Admission_01}}"
            },
            {
                "categoryId": "{{categoryId_General_Admission}}",
                "productId": "{{productId_General_Admission}}"
            }
        ]
    }""", token="admin_token", app_headers=True)
    expect(_resp122).json('$.code').equals('200')
    expect(_resp122).json('$.message').equals('success')
    expect(_resp122).json('$.data').is_object()
    expect(_resp122).json('$.data.created').equals(45)
    expect(_resp122).json('$.data.updated').equals(0)
    expect(_resp122).json('$.data.deleted').equals(0)
    expect(_resp122).json('$.data.linked').equals(3)



    # --- step 123: setting the partner 999 is testing user (PATCH users/{{user_id}}) ---
    # ⚠️ base 域 PATCH /users/{id} → 404 Cannot PATCH；仅 admin 域 + admin_token → 200。
    _resp123 = ctx.api.admin.users_update_by_user_id(
        path_vars={"user_id": vars.get("user_id", "")},
        body="""{"phoneNumber":"","testing":true}""", token="admin_token", app_headers=True)
    expect(_resp123).json('$.code').equals('200')
    expect(_resp123).json('$.message').equals('success')



    # --- step 124: enable TDC API Credentials (PATCH users/tool/feature-flags?userId={{curator_id}}) ---
    _resp124 = ctx.api.admin.users_tool_feature_flags(
        params={"userId": vars.get("curator_id", "")}, body="""{"name":"enablePlatformTDC","enabled":true}""", token="admin_token", app_headers=True)
    expect(_resp124).json('$.code').equals('200')
    expect(_resp124).json('$.message').equals('success')



    # --- step 125: setting TDC API (PUT users/{{user_id}}/api-platform-credentials) ---
    # NOTE: Credential values (clientSecret/accessToken/apiKey/clientId) use {{tdc_*}} placeholders; supply them via .vars.yaml / environment, never commit literals.
    # ⚠️ base 域 PUT → 404 Cannot PUT；仅 admin 域 + admin_token 有效（缺 apiCredentials 时 400）。
    _resp125 = ctx.api.admin.users_api_platform_credentials(
        path_vars={"user_id": vars.get("user_id", "")}, body=r"""{
        "apiPlatform": "TDC",
        "apiCredentials": {
            "baseUrl": "https://sandbox.pvapi.provenue.com",
            "clientId": "{{tdc_clientId}}",
            "clientSecret": "{{tdc_clientSecret}}",
            "appId": "us.pear.web",
            "userAgent": "{{tdc_userAgent}}",
            "deliveryMethodId": 3683,
            "paymentMethodId": 3289,
            "ticket": {
                "linkTemplate": "https://mpvsb.tickets.com/?agency=MLBM_MYTIXX&orgid=48650&supp_oid=44135946",
                "messageTemplate": "You're all set — tickets confirmed! Tickets typically show up in 1–2\nhours, and will be available before the event.\n\nClick View Tickets and log in with your\nMLB.com username ({{email}}) and password to view your tickets."
            }
        }
    }""", token="admin_token", app_headers=True)
    expect(_resp125).json('$.code').equals('200')
    expect(_resp125).json('$.message').equals('success')
    expect(_resp125).status().is_(200)
    expect(_resp125).json('$.data').is_object()
    expect(_resp125).json('$.data.apiPlatform').equals('TDC')
    expect(_resp125).json('$.data.userId').is_string()
    expect(_resp125).json('$.data.userId').is_not_empty()
    expect(_resp125).json('$.data.apiCredentials').is_object()
    expect(_resp125).json('$.data.apiCredentials.appId').equals('us.pear.web')
    expect(_resp125).json('$.data.apiCredentials.baseUrl').equals('https://sandbox.pvapi.provenue.com')
    expect(_resp125).json('$.data.apiCredentials.clientId').is_string()
    expect(_resp125).json('$.data.apiCredentials.clientId').is_not_empty()
    expect(_resp125).json('$.data.apiCredentials.clientSecret').is_string()
    expect(_resp125).json('$.data.apiCredentials.clientSecret').is_not_empty()
    expect(_resp125).json('$.data.apiCredentials.paymentMethodId').equals(3289)
    expect(_resp125).json('$.data.apiCredentials.deliveryMethodId').equals(3683)
    expect(_resp125).json('$.data.apiCredentials.ticket').is_object()
    expect(_resp125).json('$.data.apiCredentials.ticket.linkTemplate').contains('https://mpvsb.tickets.com/?agency=MLBM_MYTIXX')
    expect(_resp125).json('$.data.apiCredentials.ticket.messageTemplate').contains("You're all set — tickets confirmed!")
    expect(_resp125).json('$.data.createdAt').is_string()
    expect(_resp125).json('$.data.createdAt').is_not_empty()
    expect(_resp125).json('$.data.updatedAt').is_string()
    expect(_resp125).json('$.data.updatedAt').is_not_empty()



    # --- step 126: discovery the TDC event data (GET events/ticket-hub/discovery?userId={{user_id}}&platform=TDC) ---
    # ⚠️ base 域 → 404 Cannot GET；仅 admin 域 + admin_token。
    #    且必须带 ?userId= 与 ?platform=，否则后端拿不到该用户的 TDC 凭据 → 503。
    _resp126 = ctx.api.admin.events_ticket_hub_discovery(
        params={"userId": vars.get("user_id", ""), "platform": "TDC"},
        token="admin_token", app_headers=True)
    expect(_resp126).json('$.code').equals('200')
    expect(_resp126).json('$.message').equals('success')
    # NOTE: 迁移时提取路径误写成 "$.data.events[i].handle"（该字段不存在 → 提取为 None →
    #       占位符保持字面量，后续 check-imported 会拿字面量比对而「假通过」）。
    #       同段断言用的是 events[i].eventHandle，据此改正。
    ctx.extract("TDC_eventHandle1", _resp126, "$.data.events[0].eventHandle")
    ctx.extract("TDC_eventHandle2", _resp126, "$.data.events[1].eventHandle")
    expect(_resp126).status().is_(200)
    expect(_resp126).json('$.data.events').is_array()
    expect(_resp126).json('$.data.events.length').at_least(2)
    expect(_resp126).json('$.data.events[0].eventHandle').is_string()
    expect(_resp126).json('$.data.events[0].eventHandle').is_not_empty()
    expect(_resp126).json('$.data.events[1].eventHandle').is_string()
    expect(_resp126).json('$.data.events[1].eventHandle').is_not_empty()



    # --- step 127: Check Imported TDC event (POST events/ticket-hub/check-imported) ---
    # ⚠️ base 域 → 404；仅 admin 域 + admin_token（返回 HTTP 201）。
    _resp127 = ctx.api.admin.events_ticket_hub_check_imported(body="""{
        "eventHandles": [
            "{{TDC_eventHandle1}}"
        ],
        "curatorId": "{{user_id}}"
    }""", token="admin_token", app_headers=True)
    expect(_resp127).json('$.code').equals('200')
    expect(_resp127).json('$.message').equals('success')
    expect(_resp127).status().is_(201)
    assert isinstance(vars.get('TDC_eventHandle1'), str) and vars.get('TDC_eventHandle1'), "环境变量 TDC_eventHandle1 未设置或为空"
    expect(_resp127).json('$.data.notImported').is_array()
    # 注：环境变量 targetHandle
    expect(_resp127).json('$.data.notImported').includes(vars.get('TDC_eventHandle1'))



    # --- step 128: Import TDC event 01 (POST events/ticket-hub/import) ---
    # ⚠️ base 域 → 404；仅 admin 域 + admin_token。
    _resp128 = ctx.api.admin.events_ticket_hub_import(body="""{
        "eventHandle": "{{TDC_eventHandle1}}",
        "curatorId": "{{user_id}}",
        "platform": "TDC"
    }""", token="admin_token", app_headers=True)
    expect(_resp128).json('$.code').equals('200')
    expect(_resp128).json('$.message').equals('success')
    expect(_resp128).json('$.data').is_object()
    expect(_resp128).json('$.data.queued').equals(True)



    # --- step 129: Import TDC event 02 (POST events/ticket-hub/import) ---
    # ⚠️ base 域 → 404；仅 admin 域 + admin_token。
    _resp129 = ctx.api.admin.events_ticket_hub_import(body="""{
        "eventHandle": "{{TDC_eventHandle2}}",
        "curatorId": "{{user_id}}",
        "platform": "TDC"
    }""", token="admin_token", app_headers=True)
    expect(_resp129).json('$.code').equals('200')
    expect(_resp129).json('$.message').equals('success')
    expect(_resp129).json('$.data').is_object()
    expect(_resp129).json('$.data.queued').equals(True)



    # --- step 130: enable AXS API Credentials (PATCH users/tool/feature-flags?userId={{curator_id}}) ---
    _resp130 = ctx.api.admin.users_tool_feature_flags(
        params={"userId": vars.get("curator_id", "")}, body="""{"name":"enablePlatformAXS","enabled":true}""", token="admin_token", app_headers=True)
    expect(_resp130).json('$.code').equals('200')
    expect(_resp130).json('$.message').equals('success')



    # --- step 131: setting AXS API (PUT users/{{user_id}}/api-platform-credentials) ---
    # NOTE: Credential values (clientSecret/accessToken/apiKey/clientId) use {{axs_*}} placeholders; supply them via .vars.yaml / environment, never commit literals.
    # ⚠️ 同 step 125：仅 admin 域 + admin_token。
    _resp131 = ctx.api.admin.users_api_platform_credentials(
        path_vars={"user_id": vars.get("user_id", "")}, body="""{
        "apiPlatform": "AXS",
        "apiCredentials": {
            "accessToken": "{{axs_accessToken}}",
            "siteId": "1",
            "apiKey": "{{axs_apiKey}}",
            "apiBaseUrl": "https://api.axs.com",
            "appBaseUrl": "https://app.axs.com",
            "ticketerId": "22",
            "outletId": "99947",
            "paymentTypeId": "90043",
            "ticket": {
                "linkTemplate": "https://axs.page.link/mobile",
                "messageTemplate": "Click View Tickets and log in with your AXS account ({{email}}) and password to view your tickets."
            }
        }
    }""", token="admin_token", app_headers=True)
    expect(_resp131).json('$.code').equals('200')
    expect(_resp131).json('$.message').equals('success')
    expect(_resp131).status().is_(200)
    expect(_resp131).json('$.data').is_object()
    expect(_resp131).json('$.data.apiPlatform').equals('AXS')
    expect(_resp131).json('$.data.userId').is_string()
    expect(_resp131).json('$.data.userId').is_not_empty()
    expect(_resp131).json('$.data.apiCredentials').is_object()
    expect(_resp131).json('$.data.apiCredentials.apiKey').is_string()
    expect(_resp131).json('$.data.apiCredentials.apiKey').is_not_empty()
    expect(_resp131).json('$.data.apiCredentials.siteId').equals('1')
    expect(_resp131).json('$.data.apiCredentials.outletId').equals('99947')
    expect(_resp131).json('$.data.apiCredentials.ticketerId').equals('22')
    expect(_resp131).json('$.data.apiCredentials.paymentTypeId').equals('90043')
    expect(_resp131).json('$.data.apiCredentials.apiBaseUrl').equals('https://api.axs.com')
    expect(_resp131).json('$.data.apiCredentials.appBaseUrl').equals('https://app.axs.com')
    expect(_resp131).json('$.data.apiCredentials.accessToken').is_string()
    expect(_resp131).json('$.data.apiCredentials.accessToken').is_not_empty()
    expect(_resp131).json('$.data.apiCredentials.ticket').is_object()
    expect(_resp131).json('$.data.apiCredentials.ticket.linkTemplate').equals('https://axs.page.link/mobile')
    expect(_resp131).json('$.data.apiCredentials.ticket.messageTemplate').contains('log in with your AXS account')
    expect(_resp131).json('$.data.createdAt').is_string()
    expect(_resp131).json('$.data.createdAt').is_not_empty()
    expect(_resp131).json('$.data.updatedAt').is_string()
    expect(_resp131).json('$.data.updatedAt').is_not_empty()



    # --- step 132: discovery the AXS event data (GET events/ticket-hub/discovery?userId={{user_id}}&platform=AXS) ---
    # ⚠️ 同 step 126：仅 admin 域 + admin_token，且必须带 userId 与 platform。
    _resp132 = ctx.api.admin.events_ticket_hub_discovery(
        params={"userId": vars.get("user_id", ""), "platform": "AXS"},
        token="admin_token", app_headers=True)
    expect(_resp132).json('$.code').equals('200')
    expect(_resp132).json('$.message').equals('success')
    # NOTE: 同 step 126，原提取路径 $.data.events[i].handle 不存在，改为 eventHandle。
    ctx.extract("AXS_eventHandle1", _resp132, "$.data.events[0].eventHandle")
    ctx.extract("AXS_eventHandle2", _resp132, "$.data.events[1].eventHandle")
    expect(_resp132).status().is_(200)
    expect(_resp132).json('$.data.events').is_array()
    expect(_resp132).json('$.data.events.length').at_least(2)
    expect(_resp132).json('$.data.events[0].eventHandle').is_string()
    expect(_resp132).json('$.data.events[0].eventHandle').is_not_empty()
    expect(_resp132).json('$.data.events[1].eventHandle').is_string()
    expect(_resp132).json('$.data.events[1].eventHandle').is_not_empty()



    # --- step 133: Check Imported AXS event (POST events/ticket-hub/check-imported) ---
    # ⚠️ 同 step 127：仅 admin 域 + admin_token。
    _resp133 = ctx.api.admin.events_ticket_hub_check_imported(body="""{
        "eventHandles": [
            "{{AXS_eventHandle1}}"
        ],
        "curatorId": "{{user_id}}"
    }""", token="admin_token", app_headers=True)
    expect(_resp133).json('$.code').equals('200')
    expect(_resp133).json('$.message').equals('success')
    expect(_resp133).status().is_(201)
    assert isinstance(vars.get('AXS_eventHandle1'), str) and vars.get('AXS_eventHandle1'), "环境变量 AXS_eventHandle1 未设置或为空"
    expect(_resp133).json('$.data.notImported').is_array()
    # 注：环境变量 targetHandle
    expect(_resp133).json('$.data.notImported').includes(vars.get('AXS_eventHandle1'))



    # --- step 134: Import AXS event 01 (POST events/ticket-hub/import) ---
    # ⚠️ 同 step 128：仅 admin 域 + admin_token。
    _resp134 = ctx.api.admin.events_ticket_hub_import(body="""{
        "eventHandle": "{{AXS_eventHandle1}}",
        "curatorId": "{{user_id}}",
        "platform": "AXS"
    }""", token="admin_token", app_headers=True)
    expect(_resp134).json('$.code').equals('200')
    expect(_resp134).json('$.message').equals('success')
    expect(_resp134).json('$.data').is_object()
    expect(_resp134).json('$.data.queued').equals(True)



    # --- step 135: Import AXS event 02 (POST events/ticket-hub/import) ---
    # ⚠️ 同 step 128：仅 admin 域 + admin_token。
    _resp135 = ctx.api.admin.events_ticket_hub_import(body="""{
        "eventHandle": "{{AXS_eventHandle2}}",
        "curatorId": "{{user_id}}",
        "platform": "AXS"
    }""", token="admin_token", app_headers=True)
    expect(_resp135).json('$.code').equals('200')
    expect(_resp135).json('$.message').equals('success')
    expect(_resp135).json('$.data').is_object()
    expect(_resp135).json('$.data.queued').equals(True)



    # --- step 136: delay (no-op, framework style) ---
    # NOTE: original Apifox collection had a delay here; removed per framework style (no time.sleep).
