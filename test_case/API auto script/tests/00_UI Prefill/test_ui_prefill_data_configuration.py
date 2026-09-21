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
TAGS = ["p0", "prefill", "suite:linda"]
PRIORITY = 0

CASE_ID = None  # manually migrated, no Apifox Case ID
ENV_NAME = "Release"

from core.assertions import expect

# UI 自动化共用的三个账号（+999/+997/+998）口令统一为明文 Happy123，全仓库多处硬编码它的 md5。
# 见 tools/get_all_cookies.py、tests/01_Login flow/test_linda_t2302_*.py 等。
MD5_HAPPY123 = "7EbE8F4BdE4A38768AcF9C2833aF2Db5"


def test_ui_prefill_data_configuration(ctx):
    """UI automation data pre-configuration: create/cleanup users, events, products, stores."""
    vars = ctx

    # ======================================================================
    # step_0
    # ======================================================================
    # --- step 1: admin login (POST /auth/login) ---
    _resp1 = ctx.api.auth.login(body="""{
    "email": "{{UIauto_admin_email}}",
    "password": "{{adminpassword}}"
}""", app_headers=True, token="admin_token")

    # --- step 2: Admin search partner 999 (POST /users/search) ---
    _resp2 = ctx.api.users.search(body="""{
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
    ctx.extract("user_id", _resp2, "$.data.userId")

    # --- step 3: Admin search partner 997 (POST /users/search) ---
    _resp3 = ctx.api.users.search(body="""{
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
    ctx.extract("user_partner997_id", _resp3, "$.data.userId")

    # --- step 4: Admin search coseller 998 (POST /users/search) ---
    _resp4 = ctx.api.users.search(body="""{
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
    ctx.extract("user_coseller_id", _resp4, "$.data.userId")

    if vars.get("user_id"):
        # --- step 6: delete the users and check the user delete success (DELETE /users/{{user_id}}) ---
        _resp6 = ctx.api.users.delete_by_user_id(body="""{"deleteOrders":true}""", path_vars={"user_id": vars.get("user_id", "")}, app_headers=True, token="admin_token")

    if vars.get("user_coseller_id"):
        # --- step 9: delete the users and check the user delete success (DELETE /users/{{user_coseller_id}}) ---
        _resp9 = ctx.api.users.delete_by_user_id(body="""{"deleteOrders":true}""", path_vars={"user_id": vars.get("user_coseller_id", "")}, app_headers=True, token="admin_token")

    if vars.get("user_partner997_id"):
        # --- step 12: delete the users and check the user delete success (DELETE /users/{{user_partner997_id}}) ---
        _resp12 = ctx.api.users.delete_by_user_id(body="""{"deleteOrders":true}""", path_vars={"user_id": vars.get("user_partner997_id", "")}, app_headers=True, token="admin_token")

    # --- step 14: Create partner999 on admin tools (POST /users/tool/external-user-import/partner) ---
    _resp14 = ctx.api.users.external_user_import_partner(body="""{
    "allowSyncResalePosts": true,
    "defaultModuleName": "Upcoming Events",
    "email": "{{UIauto_partner_email}}"
}""", app_headers=True, token="admin_token")
    ctx.extract("password", _resp14, "$.data.md5Password")

    # --- step 15: Admin search partner 999 (POST /users/search) ---
    _resp15 = ctx.api.users.search(body="""{
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
    ctx.extract("user_id", _resp15, "$.data.userId")

    # --- step 16: set partner999 password to Happy123 (PUT /users/{{user_id}}/password) ---
    _resp16 = ctx.api.users.set_password(body="""{"password":"{{password}}"}""", path_vars={"user_id": vars.get("user_id", "")}, app_headers=True, token="admin_token")

    # --- step 17: Create partner997 on admin tools (POST /users/tool/external-user-import/partner) ---
    _resp17 = ctx.api.users.external_user_import_partner(body="""{
    "allowSyncResalePosts": true,
    "defaultModuleName": "Upcoming Events",
    "email": "{{UIauto_partner997_email}}"
}""", app_headers=True, token="admin_token")
    ctx.extract("password", _resp17, "$.data.password")

    # --- step 18: Admin search partner 997 (POST /users/search) ---
    _resp18 = ctx.api.users.search(body="""{
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
    ctx.extract("user_partner997_id", _resp18, "$.data.userId")

    # --- step 19: set partner997 password (PUT /users/{{user_partner997_id}}/password) ---
    _resp19 = ctx.api.users.set_password(body="""{"password":"{{password}}"}""", path_vars={"user_id": vars.get("user_partner997_id", "")}, app_headers=True, token="admin_token")

    # --- step 20: delay 3.0s ---
    # NOTE: original Apifox collection had a 3.0s delay here; removed per framework style (no time.sleep).
    # --- step 21: delay 3.0s ---
    # NOTE: original Apifox collection had a 3.0s delay here; removed per framework style (no time.sleep).
    # --- step 22: delay 3.0s ---
    # NOTE: original Apifox collection had a 3.0s delay here; removed per framework style (no time.sleep).
    # --- step 23: Connect 999 and 997  (POST /users/promoter-associations/connect/{{user_id}}) ---
    _resp23 = ctx.api.users.promoter_associations_connect(body="""{"promoterInfo":"{{UIauto_partner997_email}}"}""", path_vars={"user_id": vars.get("user_id", "")}, app_headers=True, token="admin_token")

    # --- step 24: Partner 999 login (POST /auth/sign-in) ---
    _resp24 = ctx.api.auth.sign_in(body="""{
    "email": "{{UIauto_partner_email}}",
    "password": "{{password}}"

}""", app_headers=True, token="token")
    ctx.extract("user_id", _resp24, "$.data.id")
    ctx.extract("user_coseller_id", _resp24, "$.data.id")
    ctx.extract("user_partner997_id", _resp24, "$.data.id")
    ctx.extract("token", _resp24, "$.data.token")

    # --- step 25: update the partner999's store shop url to autoshop (PUT /store-front) ---
    _resp25 = ctx.api.storefront.update(body="""{
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

    # --- step 26: get partner 999's uncoming module id (GET /store-front/shop/{{partner_vanityUrl}}) ---
    _resp26 = ctx.api.storefront.shop(path_vars={"partner_vanityUrl": vars.get("partner_vanityUrl", "")}, app_headers=True, token="token")
    ctx.extract("module_id", _resp26, "$.data.targetModule.id")

    # --- step 27: delay 3.0s ---
    # NOTE: original Apifox collection had a 3.0s delay here; removed per framework style (no time.sleep).
    # --- step 28: Partner Create event (POST /product-event/v2) ---
    _resp28 = ctx.api.events.create_v2(body="""{
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
    ctx.extract("created_event_id", _resp28, "$.data.eventId")

    # --- step 29: Partner999 Create event media next step  (POST /product-event/v2/{{created_event_id}}/media/batch/create) ---
    _resp29 = ctx.api.events.media_batch_create(body="""{
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
}""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")

    # --- step 30: Partner999 Create event ticket next step (POST /product-event/v2/{{created_event_id}}/ticket/batch/v2) ---
    _resp30 = ctx.api.events.ticket_batch_v2(body="""{
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
}""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")

    # --- step 31: Partner999 Create event lineup next step (POST /product-event/v2/{{created_event_id}}/lineup/batch) ---
    _resp31 = ctx.api.events.lineup_batch(body="""{"lineup":[]}""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    ctx.extract("ticket_id", _resp31, "$.data.ticketId")
    ctx.extract("variant_id", _resp31, "$.data.variantId")

    # --- step 32: get the event post id (GET /posts/curator/event/{{created_event_id}}/posts) ---
    _resp32 = ctx.api.posts.curator_event_posts(path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    ctx.extract("post0_id", _resp32, "$.data.postId")

    # --- step 33: Partner999 sync to module (POST /store-front/sync-post-to-module) ---
    _resp33 = ctx.api.storefront.sync_post_to_module(body="""{
    "postId": "{{post0_id}}",
    "moduleIds": [
        "{{module_id}}"
    ]
}""", app_headers=True, token="token")

    # --- step 34: duplicate event for yuxiao (POST /product-event/v2/duplicate) ---
    _resp34 = ctx.api.events.duplicate(body="""{
    "title": "verify-post-shipping_fee",
    "curatorId": "{{user_id}}}",
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
    ctx.extract("neweventid", _resp34, "$.data.eventId")
    ctx.extract("shipping_fee_postsId", _resp34, "$.data.postId")

    # --- step 35: update the post title to verify-post-shipping-fee (PATCH /post/{{shipping_fee_postsId}}) ---
    _resp35 = ctx.api.posts.patch_by_id(body="""{
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
}""", path_vars={"post_id": vars.get("shipping_fee_postsId", "")}, app_headers=True, token="token")

    # --- step 36: duplicate event for form (POST /product-event/v2/duplicate) ---
    _resp36 = ctx.api.events.duplicate(body="""{
    "title": "event-for-rte-insert-form",
    "curatorId": "{{user_id}}}",
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
    ctx.extract("post_id", _resp36, "$.data.postId")
    ctx.extract("createFromEventId", _resp36, "$.data.eventId")
    ctx.extract("ticketsid", _resp36, "$.data.ticketId")
    ctx.extract("variantsid", _resp36, "$.data.variantId")

    # --- step 37: syncEnabled false form (POST /posts/curator/toggle-sync) ---
    _resp37 = ctx.api.call("POST", "/posts/curator/toggle-sync", body="""{
    "syncEnabled": false,
    "postId": "{{post_id}}",
    "eventId": "{{createFromEventId}}",
    "additionalContentPosition": "aboveTickets",
    "dryRun": true
}""", token="token", app_headers=True)

    # --- step 38: update the post auto sync false form (PUT /posts/curator/{{post_id}}) ---
    _resp38 = ctx.api.call("PUT", "/posts/curator/{{post_id}}", body="""{
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

    # --- step 39: duplicate event for auto coupon apply (POST /product-event/v2/duplicate) ---
    _resp39 = ctx.api.events.duplicate(body="""{
    "title": "verify auto coupon apply",
    "curatorId": "{{user_id}}}",
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
    ctx.extract("post_id", _resp39, "$.data.postId")
    ctx.extract("createFromEventId", _resp39, "$.data.eventId")
    ctx.extract("ticketsid", _resp39, "$.data.ticketId")
    ctx.extract("variantsid", _resp39, "$.data.variantId")
    ctx.extract("neweventid", _resp39, "$.data.eventId")
    ctx.extract("auto_coupon_postsId", _resp39, "$.data.postId")

    # --- step 40: update the post title to verify-post-auto-coupon (PATCH /post/{{auto_coupon_postsId}}) ---
    _resp40 = ctx.api.call("PATCH", "/post/{{auto_coupon_postsId}}", body="""{
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
}""", token="token", app_headers=True)

    # --- step 41: duplicate event for demi (POST /product-event/v2/duplicate) ---
    _resp41 = ctx.api.events.duplicate(body="""{
    "title": "test event with two tickets",
    "curatorId": "{{user_id}}}",
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
    ctx.extract("post_id", _resp41, "$.data.postId")
    ctx.extract("createFromEventId", _resp41, "$.data.eventId")
    ctx.extract("ticketsid", _resp41, "$.data.ticketId")
    ctx.extract("variantsid", _resp41, "$.data.variantId")
    ctx.extract("neweventid", _resp41, "$.data.eventId")
    ctx.extract("two_tickets_postsid", _resp41, "$.data.postId")

    # --- step 42: update the post title to verify post with two tickets (PATCH /post/{{two_tickets_postsid}}) ---
    _resp42 = ctx.api.call("PATCH", "/post/{{two_tickets_postsid}}", body="""{
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
}""", token="token", app_headers=True)

    # --- step 43: enable co-selling-defaults (PATCH /catalog/event/co-selling-defaults) ---
    _resp43 = ctx.api.call("PATCH", "/catalog/event/co-selling-defaults", body="""{
    "commissionRate": 0,
    "enableEventCoSellingCommission": true
}""", token="token", app_headers=True)

    # --- step 44: update the ticket price to 0 (PUT /v2/products/{{ticketsid}}) ---
    _resp44 = ctx.api.call("PUT", "/v2/products/{{ticketsid}}", body="""{
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

    # --- step 45: Add ticket 002 (POST /v2/products) ---
    _resp45 = ctx.api.products.create_v2(body="""{
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

    # --- step 46: Partner999 sync the post to the coseller's 997 shop (POST /posts/curator/{{post0_id}}/promoters/sync) ---
    _resp46 = ctx.api.posts.curator_sync_promoters(body="""{
    "postId": "{{post0_id}}",
    "promoterIds": [
        "{{user_partner997_id}}"
    ]
}""", path_vars={"post0_id": vars.get("post0_id", "")}, app_headers=True, token="token")

    # --- step 47: Partner 997 login (POST /auth/sign-in) ---
    _resp47 = ctx.api.auth.sign_in(body="""{
    "email": "{{UIauto_partner997_email}}",
    "password": "{{password}}"

}""", app_headers=True, token="token")

    # --- step 48: update the partner997's store shop url to autoshop (PUT /store-front) ---
    _resp48 = ctx.api.storefront.update(body="""{
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
}""", app_headers=True, token="token")

    # --- step 49: Partner997 create expired module (POST /store-front/module) ---
    _resp49 = ctx.api.storefront.module(body="""{
    "type": "POST",
    "direction": "VERTICAL",
    "title": "Expired events",
    "linkType": null,
    "visible": true
}""", app_headers=True, token="token")
    ctx.extract("cosellermodule_id", _resp49, "$.data.moduleId")

    # --- step 50: get the coseller's resell post id (GET /post/{{post0_id}}/children) ---
    _resp50 = ctx.api.call("GET", "/post/{{post0_id}}/children", token="token", app_headers=True)
    ctx.extract("cosellpost_id", _resp50, "$.data.cosellId")

    # --- step 51: get the event post id (GET /posts/curator/event/{{created_event_id}}/posts) ---
    _resp51 = ctx.api.posts.curator_event_posts(path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    ctx.extract("post0_id", _resp51, "$.data.postId")

    # --- step 52: Add the coseller997's post to the module (PUT /store-front/module-item/{{cosellermodule_id}}) ---
    _resp52 = ctx.api.call("PUT", "/store-front/module-item/{{cosellermodule_id}}", body="""{
    "id": "{{module_id}}",
    "items": [
        {
            "itemId": "{{cosellpost_id}}",
            "position": 1
        }
    ]
}""", token="token", app_headers=True)

    # --- step 53: Partner Create event T1742 (POST /product-event/v2) ---
    _resp53 = ctx.api.events.create_v2(body="""{
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
    ctx.extract("created_event_id", _resp53, "$.data.eventId")

    # --- step 54: Partner Create event media next step T1742  (POST /product-event/v2/{{created_event_id}}/media/batch/create) ---
    _resp54 = ctx.api.events.media_batch_create(body="""{
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
}""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")

    # --- step 55: Partner Create event ticket next step T1742 (POST /product-event/v2/{{created_event_id}}/ticket/batch/v2) ---
    _resp55 = ctx.api.events.ticket_batch_v2(body="""{
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
""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")

    # --- step 56: Partner Create event lineup next step  T1742 (POST /product-event/v2/{{created_event_id}}/lineup/batch) ---
    _resp56 = ctx.api.events.lineup_batch(body="""{"lineup":[]}""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")

    # --- step 57: Partner Check event details T1742 (GET /product-event/v2/{{created_event_id}}/config) ---
    _resp57 = ctx.api.call("GET", "/product-event/v2/{{created_event_id}}/config", token="token", app_headers=True)

    # --- step 58: get the event post id (GET /posts/curator/event/{{created_event_id}}/posts) ---
    _resp58 = ctx.api.posts.curator_event_posts(path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    ctx.extract("post0_id", _resp58, "$.data.postId")

    # --- step 59: Admin update the partner's the t1742 post  url (PATCH /post/{{post0_id}}) ---
    _resp59 = ctx.api.posts.patch_by_id(body="""{
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
}""", path_vars={"post_id": vars.get("post0_id", "")}, app_headers=True, token="token")

    # --- step 60: Partner Create event T2830 (POST /product-event/v2) ---
    _resp60 = ctx.api.events.create_v2(body="""{
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
    ctx.extract("created_event_id", _resp60, "$.data.eventId")
    ctx.extract("autoCreatedPostId", _resp60, "$.data.autoCreatedPostId")

    # --- step 61: Partner Create event media next step T2830  (POST /product-event/v2/{{created_event_id}}/media/batch/create) ---
    _resp61 = ctx.api.events.media_batch_create(body="""{
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
}""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")

    # --- step 62: Partner Create event ticket next step T2830 (POST /product-event/v2/{{created_event_id}}/ticket/batch/v2) ---
    _resp62 = ctx.api.events.ticket_batch_v2(body="""{
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
""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")

    # --- step 63: Partner Create event lineup next step  T2830 (POST /product-event/v2/{{created_event_id}}/lineup/batch) ---
    _resp63 = ctx.api.events.lineup_batch(body="""{"lineup":[]}""", path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")

    # --- step 64: Partner Check event details (GET /product-event/v2/{{created_event_id}}/config) ---
    _resp64 = ctx.api.call("GET", "/product-event/v2/{{created_event_id}}/config", token="token", app_headers=True)
    ctx.extract("ticket_id", _resp64, "$.data.firstTicketId")

    # --- step 65: update the ticket variant and price to 0 (PUT /v2/products/{{ticket_id}}) ---
    _resp65 = ctx.api.call("PUT", "/v2/products/{{ticket_id}}", body="""{
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
    ctx.extract("current_product_id", _resp65, "$.data.productId")
    ctx.extract("current_variants_json", _resp65, "$.data.JSON.stringify(variants)")

    # --- step 66: Add merch001 (POST /v2/products) ---
    _resp66 = ctx.api.products.create_v2(body="""{
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

    # --- step 67: Add merch002 (POST /v2/products) ---
    _resp67 = ctx.api.products.create_v2(body="""{
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

    # --- step 68: get the event post id (GET /posts/curator/event/{{created_event_id}}/posts) ---
    _resp68 = ctx.api.posts.curator_event_posts(path_vars={"created_event_id": vars.get("created_event_id", "")}, app_headers=True, token="token")
    ctx.extract("post0_id", _resp68, "$.data.postId")

    # --- step 69: Admin update the partner's the t2830 post  url (PATCH /post/{{post0_id}}) ---
    _resp69 = ctx.api.posts.patch_by_id(body="""{
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
}""", path_vars={"post_id": vars.get("post0_id", "")}, app_headers=True, token="token")

    # --- step 70: Create event with no ticket (POST /product-event/v2) ---
    _resp70 = ctx.api.events.create_v2(body="""{
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
    ctx.extract("created_event_id02", _resp70, "$.data.eventId")

    # --- step 71: Create event media next step (POST /product-event/v2/{{created_event_id02}}/media/batch/create) ---
    _resp71 = ctx.api.call("POST", "/product-event/v2/{{created_event_id02}}/media/batch/create", body="""{
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

    # --- step 72: Create event ticket next step (POST /product-event/v2/{{created_event_id02}}/ticket/batch/v2) ---
    _resp72 = ctx.api.call("POST", "/product-event/v2/{{created_event_id02}}/ticket/batch/v2", body="""{
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

    # --- step 73: Partner Create event lineup next step (POST /product-event/v2/{{created_event_id02}}/lineup/batch) ---
    _resp73 = ctx.api.call("POST", "/product-event/v2/{{created_event_id02}}/lineup/batch", body="""{"lineup":[]}""", token="token", app_headers=True)

    # --- step 74: Create Catalog (POST /merchant) ---
    _resp74 = ctx.api.merchants.create(body="""{
    "commissionRate": 25,
    "storeName": "auto test",
    "isVisible": true
}""", app_headers=True, token="token")
    ctx.extract("merchant_id_autotest", _resp74, "$.data.merchantId")

    # --- step 75: get shipping-options (GET /merchants/{{merchant_id_autotest}}/shipping-options) ---
    _resp75 = ctx.api.merchants.shipping_options_by_merchant_id(path_vars={"merchant_id": vars.get("merchant_id_autotest", "")}, app_headers=True, token="token")
    ctx.extract("shipping_option_id", _resp75, "$.data.shippingId")

    # --- step 76: create general product and setting the shipping option is flat shipping (POST /v2/products) ---
    _resp76 = ctx.api.products.create_v2(body="""{
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

    # --- step 77: Partner 999 update shipping options (PUT /merchants/{{merchant_id_autotest}}/shipping-options/{{shipping_option_id}}) ---
    _resp77 = ctx.api.merchants.shipping_options_update(body="""{
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
}""", path_vars={"merchant_id": vars.get("merchant_id_autotest", ""), "shipping_option_id": vars.get("shipping_option_id", "")}, app_headers=True, token="token")

    # --- step 78: create product and update alias (POST /v2/products) ---
    _resp78 = ctx.api.products.create_v2(body="""{
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

    # --- step 79: get the two products url allias (GET /merchant/product/list) ---
    _resp79 = ctx.api.products.merchant_product_list(app_headers=True, token="token")
    ctx.extract("alias0", _resp79, "$.data.item.alias")
    ctx.extract("alias1", _resp79, "$.data.item.alias")

    # --- step 80: get partner 999 promoter ProductId0 (GET /promoter/product/public/{{alias0}}/product-detail) ---
    _resp80 = ctx.api.promoters.product_public_detail(path_vars={"alias": vars.get("alias0", "")}, app_headers=True, token="token")
    ctx.extract("ProductVariantId0", _resp80, "$.data.variantId")

    # --- step 81: get partner 999 promoter ProductId1 (GET /promoter/product/public/{{alias1}}/product-detail) ---
    _resp81 = ctx.api.promoters.product_public_detail(path_vars={"alias": vars.get("alias1", "")}, app_headers=True, token="token")
    ctx.extract("ProductVariantId1", _resp81, "$.data.variantId")

    # --- step 82: Partner999 create general post with 2 products  (POST /posts/curator) ---
    _resp82 = ctx.api.posts.curator(body="""{
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

    # --- step 83: Partner999 sync the post t3788 to the coseller's 997 shop (POST /posts/curator/{{post0_id}}/promoters/sync) ---
    _resp83 = ctx.api.posts.curator_sync_promoters(body="""{
    "postId": "{{post0_id}}",
    "promoterIds": [
        "{{user_partner997_id}}"
    ]
}""", path_vars={"post0_id": vars.get("post0_id", "")}, app_headers=True, token="token")

    # --- step 84: Set the Partner all tabs are visible  (PUT /store-front/layout) ---
    _resp84 = ctx.api.storefront.layout(body="""{
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
    ctx.extract("is_products_tab_enabled", _resp84, "$.data.productsTab.checked")

    # --- step 85: Set the Partner997 all tabs are visible  (PUT /store-front/layout) ---
    _resp85 = ctx.api.storefront.layout(body="""{
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
    ctx.extract("is_products_tab_enabled", _resp85, "$.data.productsTab.checked")

    # --- step 86: Add MyForm module (POST /store-front/module) ---
    _resp86 = ctx.api.storefront.module(body="""{
    "type": "FORM",
    "direction": "VERTICAL",
    "title": "MyForm",
    "linkType": null,
    "visible": true
}""", app_headers=True, token="token")
    ctx.extract("form_id", _resp86, "$.data.data.id")
    ctx.extract("user_id", _resp86, "$.data.data.userId")

    # --- step 87: create media form (POST /form) ---
    _resp87 = ctx.api.forms.create(body="""{
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
    ctx.extract("itemId", _resp87, "$.data.idValue")

    # --- step 88: import the media form to the module (PUT /store-front/module-item/{{form_id}}) ---
    _resp88 = ctx.api.storefront.module_item_by_dynamic_music_link_id(body="""{
    "id": "{{form_id}}",
    "items": [
        {
            "itemId": "{{itemId}}",
            "position": 1
        }
    ]
}""", path_vars={"dynamicMusicLinkId": vars.get("form_id", "")}, app_headers=True, token="token")

    # --- step 89: Partner997 Create Catalog (POST /merchant) ---
    _resp89 = ctx.api.merchants.create(body="""{
    "commissionRate": 25,
    "storeName": "auto test",
    "isVisible": true
}""", app_headers=True, token="token")
    ctx.extract("merchant_id", _resp89, "$.data.merchantId")

    # --- step 90: Partner997 get shipping-options (GET /merchants/{{merchant_id}}/shipping-options) ---
    _resp90 = ctx.api.merchants.shipping_options_by_merchant_id(path_vars={"merchant_id": vars.get("merchant_id", "")}, app_headers=True, token="token")
    ctx.extract("shipping_option_id", _resp90, "$.data.shippingId")

    # --- step 91: Patner 997create general product and setting no shipping (POST /v2/products) ---
    _resp91 = ctx.api.products.create_v2(body="""{
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
}""", app_headers=True, token="token")

    # --- step 92: Create coseller 998 on admin tools (POST /users/tool/external-user-import/promoter) ---
    _resp92 = ctx.api.users.external_user_import_promoter(body="""{
  "allowSyncResalePosts": true,
  "email": "{{UIauto_coseller_email}}",
  "partnerId": "{{user_id}}"
}""", app_headers=True, token="admin_token")
    # promoter import 返回的 $.data.password 是当场生成的随机口令，step 94 会把它写成 +998 的新口令；
    # 这里覆盖成与 +999/+997 一致的统一口令，否则 get_all_cookies.py 等处会 403。
    vars["password"] = MD5_HAPPY123

    # --- step 93: Admin search coseller 998 (POST /users/search) ---
    _resp93 = ctx.api.users.search(body="""{
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
    ctx.extract("user_coseller_id", _resp93, "$.data.userId")

    # --- step 94: set coseller998 password (PUT /users/{{user_coseller_id}}/password) ---
    _resp94 = ctx.api.users.set_password(body="""{"password":"{{password}}"}""", path_vars={"user_id": vars.get("user_coseller_id", "")}, app_headers=True, token="admin_token")

    # --- step 95: Coseller 998 login (POST /auth/sign-in) ---
    _resp95 = ctx.api.auth.sign_in(body="""{
    "email": "{{UIauto_coseller_email}}",
    "password": "{{password}}"

}""", app_headers=True, token="admin_token")

    # --- step 96: update the coseller 998's store shop url to autoshop (PUT /store-front) ---
    _resp96 = ctx.api.storefront.update(body="""{
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
}""", app_headers=True, token="admin_token")

    # --- step 97: Set the Coseller all tabs are visible  (PUT /store-front/layout) ---
    _resp97 = ctx.api.storefront.layout(body="""{
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
}""", app_headers=True, token="admin_token")

    # --- step 98: Authorize Product 999 to 998 (PUT /promote-invitation/{{user_coseller_id}}) ---
    _resp98 = ctx.api.promoters.authorize_product(body="""[
    {
        "merchantId": "{{merchant_id_autotest}}",
        "merchantStoreName": "auto test",
        "defaultCommissionRate": 25,
        "merchantPlatform": "PEAR",
        "hasAccess": true,
        "isSetCommission": false,
        "commissionRate": null
    }
]""", path_vars={"target_user_id": vars.get("user_coseller_id", "")}, app_headers=True, token="admin_token")

    # --- step 99: Authorize Product 999 to 997 (PUT /promote-invitation/{{user_partner997_id}}) ---
    _resp99 = ctx.api.promoters.authorize_product(body="""[
    {
        "merchantId": "{{merchant_id_autotest}}",
        "merchantStoreName": "auto test",
        "defaultCommissionRate": 25,
        "merchantPlatform": "PEAR",
        "hasAccess": true,
        "isSetCommission": false,
        "commissionRate": null
    }
]""", path_vars={"target_user_id": vars.get("user_partner997_id", "")}, app_headers=True, token="admin_token")

    # ======================================================================
    # step_100
    # ======================================================================