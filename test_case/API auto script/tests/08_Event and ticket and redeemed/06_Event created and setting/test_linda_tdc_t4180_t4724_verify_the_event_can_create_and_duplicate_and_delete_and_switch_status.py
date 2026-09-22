# Folder: 
# Case: (Linda)(TDC)T4180&T4724 Verify the Event can create and duplicate and delete and switch status
# Priority: P1
# Created: 2026-09-21T09:54:59.000Z
# Updated: 2026-09-21T07:42:12.000Z


CASE_ID = 8709247
ENV_NAME = "Release"



import json

from typing import TYPE_CHECKING, Callable, TypeVar

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context

_T = TypeVar("_T")

def _pick_first(items: list[_T], predicate: Callable[[_T], bool]) -> _T | None:
    """返回 items 中第一个满足 predicate 的元素；未命中返回 None。"""
    return next((i for i in items if predicate(i)), None)


def _product_has_stock(product: dict) -> bool:
    """原 post-script 的库存判定：优先 ``variants[0].inventoryQuantity``，
    回退 ``product.inventoryQuantity``，> 0 视为有货。"""
    variants = product.get('variants') or []
    inv = variants[0].get('inventoryQuantity') if variants else None
    if inv is None:
        inv = product.get('inventoryQuantity')
    try:
        return float(inv or 0) > 0
    except (TypeError, ValueError):
        return False


def _apply_related_product(ctx: "Context", product: dict) -> None:
    """把「库存 > 0 的关联产品」的字段写入上下文。

    一律写空串/0 而非 None —— ``templating.render_text`` 会**跳过 None** 的值，
    占位符就不会被替换而原样残留进 request body。
    """
    variants = product.get('variants') or []
    variant0 = variants[0] if variants else {}
    assert isinstance(variant0, dict), "variants 元素应为 dict"
    hub = (product.get('extraInfo') or {}).get('ticketHubInfo') or {}
    sections = hub.get('sectionOptions') or []
    section0 = sections[0] if sections else {}
    assert isinstance(section0, dict), "sectionOptions 元素应为 dict"
    try:
        quantity = int(float(section0.get('availableQuantity') or 0))
    except (TypeError, ValueError):
        quantity = 0
    ctx.set('ticket_title', (product.get('title') or '').strip())
    ctx.set('productId', product.get('merchantProductId')
            or (product.get('shippingView') or {}).get('productId') or '')
    ctx.set('promoterProductId', product.get('promoterProductId') or '')
    ctx.set('merchantProductVariantId', variant0.get('merchantProductVariantId') or '')
    ctx.set('displayVariantId', variant0.get('displayVariantId')
            or product.get('displayVariantId') or '')
    ctx.set('ticketHubInfo_id', hub.get('ticketHandle') or '')
    ctx.set('ticketHandle', section0.get('ticketHandle') or '')
    ctx.set('availableQuantity', quantity)
    ctx.set('sectionIds', section0.get('label') or '')
    # 源 section 自带 isGeneralAdmission（GA 票为 True、有座区如 BALCRT 为 False）。
    # 迁移时下游 step7 的复制 body 把它写死成 True，与源数据不一致，故按源值透传。
    ctx.set('isGeneralAdmission', bool(section0.get('isGeneralAdmission', True)))


def test__8709247__Linda_TDC_T4180_T4724_Verify_the_Event_can_create_and_duplicate_and_delete_and_switch_status(ctx: "Context"):
    from core.compat import get_path as _get_path
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    vars['__uuid_0'] = str(__import__('uuid').uuid4())
    # === Steps ===
    # step 1: GET Partner Get the Event id
    _resp1 = ctx.api.events.list(body=None, params={'keyword': '', 'pageSize': '50', 'pageNumber': '1'}, token='yuxiao999_token')
    # 取 id/title 写入 event_id/event_title，并取 tickets[0].id 写入 copyFromId。
    # 注意：/product-event/list 按时间倒序，本用例自己复制出来的事件（标题以 "Duplicate "
    # 开头、票已 0 库存）会排在真正源事件前面，直接取首个 TDC 会选中上一轮跑出的副本，
    # 导致 step4 取不到可售产品。故先排除自身副本，再取首个 TDC 事件。
    _items1 = (_resp1.json().get('data') or {}).get('items') or []
    _candidates1 = [i for i in _items1
                    if i.get('platform') == 'TDC'
                    and not str(i.get('title') or '').startswith('Duplicate ')]
    assert _candidates1, (f"step1 事件列表中未找到可用的 platform=TDC 源事件"
                          f"（items={len(_items1)}，已排除 title 以 'Duplicate ' 开头的副本）")
    _tdc_event = _candidates1[0]
    vars['event_id'] = _tdc_event.get('id') or ''
    vars['event_title'] = _tdc_event.get('title') or ''
    _tickets1 = _tdc_event.get('tickets') or []
    vars['copyFromId'] = (_tickets1[0].get('id') or '') if _tickets1 else ''
    # step 2: GET get the event catalog id
    _resp2 = ctx.api.events.default_catalog(body=None, token='yuxiao999_token')
    ctx.extract('catalog_id', _resp2, '$.data.id')
    # step 3: GET get the event post id
    _resp3 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token')
    _post0id_val = _get_path(_resp3.json(), ['data', 'items', 0, 'id'])
    vars['post0_id'] = _post0id_val if _post0id_val is not None else ''
    # step 4: GET Catch the ProductId and promoterProductId
    _resp4 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    _rels4: list[dict] = (_resp4.json().get('data') or {}).get('relatedProducts') or []
    _prod4 = _pick_first(_rels4, _product_has_stock)
    assert _prod4, f"step4 未找到库存 > 0 的关联产品（relatedProducts={len(_rels4)}）"
    _apply_related_product(ctx, _prod4)
    # step 5: GET get the original ticket's form information
    _resp5 = ctx.api.products.by_product_id_2(body=None, token='yuxiao999_token')
    # 实测该接口（GET /merchant/product/{id}）响应里并没有 productForm 字段
    # 源头不可复现 → 取不到就为 None。
    # 下游只有 step7 复制事件的 body 消费它，而服务端要求 isProductFormEnabled=True 时
    # productForm 必须是 object/array（字符串/null 均 400：
    # `tickets.0.nested property productForm must be either object or array`），
    # 故该 body 用 `isProductFormEnabled = bool(productForm)` 保持自洽；
    # 与同目录同场景的 test_linda_t4180_t4724_*.py（已完整迁移版，值为 False/None）一致。
    vars['productForm'] = (_get_path(_resp5.json(), ['data', 'product', 'productForm'])
                           or _get_path(_resp5.json(), ['data', 'productForm']))
    # step 6: POST Admin search partner 999
    _resp6 = ctx.api.admin.users_search(body={
        "query": "{{UIauto_partner_email}}",
        "filter": {
            "userRoles": [
                "PROMOTER",
                "BUSINESS_PARTNER",
            ],
            "userType": "ALL",
        },
        "pageSize": 100,
        "pageNumber": 1,
    }, token='admin_token')
    _items6 = (_resp6.json().get('data') or {}).get('items') or []
    vars['user_id'] = (_items6[0].get('id') or '') if _items6 else ''
    vars['dul_event_title'] = 'Duplicate Verify the TDC Event can create and duplicate and delete success'
    # step 7: POST duplicate the event
    vars['dul_event_title'] = "Duplicate Verify the TDC Event can create and duplicate and delete success"

    _resp7 = ctx.api.events.v2_duplicate(body={
    'title': '{{dul_event_title}}',
    'curatorId': '{{user_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"This event has a tiered pricing structure in the General Admission area. All General Admission tiers have the same access. Once a price level sells out it may no longer be visible or available for selection. *Please note: multiple GA price levels may be available at the same time The event organizer has decided that ticket transfer will be delayed for this event. Ticket transfer will be available on or about three weeks prior to the event. Please review the terms of TDC’s Purchase Agreement for more information.","type":"extended-text","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2027-11-07T02:00:00.000Z',
    'endDate': '2027-12-01T05:15:00.000Z',
    'venue': 'Agora Theatre',
    'location': 'Cleveland, OH, United States',
    'status': 'UPCOMING',
    'isTaxEnabled': False,
    'taxConfig': None,
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap. Make sure you buy, tickets SOLD OUT last event!",
        'align': 'center',
    },
    'poster': {
        'src': 'https://images.discovery-prod.tdc.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
        'width': 1200,
        'height': 630,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2027-11-06 21:00',
    'endDateDisplay': '2027-12-01 00:15',
    'note': '{{dul_event_title}',
    'timezone': {
        'timeZoneId': 'America/New_York',
        'timeZoneName': 'Eastern Standard Time',
        'dstOffset': 0,
        'rawOffset': -18000,
    },
    'isAddressRevealEnabled': False,
    'isAddressHidden': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'TDC',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Cleveland',
        'line1': None,
        'line2': None,
        'state': 'OH',
        'country': 'United States',
        'placeId': None,
        'zipcode': None,
        'stateName': 'OH',
        'stripeLocationId': None,
    },
    'country': 'United States',
    'state': 'OH',
    'autoReplace': False,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'excludeOnsiteSalesFromReport': False,
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'venueMapId': None,
    'ticketHubInfo': {
        'contextId': '517840254',
        'contextDesc': 'AEG Great Lakes',
        'eventHandle': 'eyJwbGF0Zm9ybSI6IkFYUyIsImh1YklkIjoiYy1wS2o5Ujk1d0Z1bWl0RmNUYXFIb283dVNCcHktaXlRTmdNTFNGZnNybyJ9',
    },
    'readOnlyFields': [
        'tax',
        'customFees',
        'duplicateTicket',
        'addTicket',
        'addMerch',
        'duplicateMerch',
    ],
    'medias': [],
    'tickets': [
        {
            'id': '{{productId}}',
            'remote_id': None,
            'platform': 'TDC',
            'createdAt': '2026-09-03T09:44:42.495Z',
            'updatedAt': '2026-09-04T09:28:40.780Z',
            'merchantId': 'e1229bad-fb18-44b2-ac23-c4c3c1b5c3c3',
            'title': 'General Admission — Pear.US',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'originalBodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'isBodyHtmlOverridden': False,
            'bodyText': '\n',
            'handle': None,
            'productType': '',
            'publishedAt': '2026-09-03T09:44:42.508Z',
            'publishedScope': '',
            'status': 'ACTIVE',
            'externalStatus': 'ACTIVE',
            'followExternalStatus': False,
            'tags': [],
            'templateSuffix': None,
            'vendor': 'Pear',
            'syncAt': None,
            'deletedAt': None,
            'delisted': False,
            'excludedByImportingTag': False,
            'isFeatured': False,
            'featuredScore': None,
            'inventoryQuantity': '{{availableQuantity}}',
            'inventoryQuantityOriginal': '{{availableQuantity}}',
            'soldQuantity': 0,
            'priceDisplay': 55.88,
            'priceDisplayAnchor': 0,
            'priceMin': 55.88,
            'priceMinAnchor': 0,
            'priceMax': 55.88,
            'priceMaxAnchor': 0,
            'priceImportedMin': 0,
            'priceImportedMax': 0,
            'imageCount': 1,
            'isUsed': 'NWT',
            'shippingType': 'NO_SHIPPING_REQUIRED',
            'additionalShippingFee': 0,
            'deliveryTime': [
                0,
                5,
            ],
            'returnPolicyApplied': True,
            'isAvailable': True,
            'commissionRate': 0,
            'textForShare': None,
            'priceSyncImported': False,
            'coverImage': {
                'src': 'https://images.discovery-prod.tdc.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
                'width': 1200,
                'height': 630,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'useEventPosterAsCover': True,
            'reviewCount': None,
            'reviewOverallScore': None,
            'reviewAggregate': None,
            'displayReviews': True,
            'links': None,
            'taxEnable': False,
            'taxJarCategory': '',
            'overrideEventTax': False,
            'customTaxRate': None,
            'subscriptionPlanId': None,
            'reviewRedirectProductId': None,
            'reviewSummary': None,
            'customFieldsInfo': None,
            'listingType': 'TICKET',
            'ticketType': 'TICKET_TYPE_STANDARD',
            'extraInfo': {
                'date': 'Fri Nov 6, 2026 9PM - Tue Dec 1, 12:15AM EST',
                'event': 'Zack Fox (DJ Set)',
                'venue': 'Agora Theatre',
                'lineup': [],
                'poster': {
                    'src': 'https://images.discovery-prod.tdc.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
                    'width': 1200,
                    'height': 630,
                    'position': 0,
                    'mediaType': 'IMAGE',
                    'mediaDuration': 0,
                },
                'status': 'UPCOMING',
                'endDate': '2026-12-01T05:15:00.000Z',
                'location': 'Cleveland, OH, United States',
                'eventNote': '',
                'startDate': '2026-11-07T02:00:00.000Z',
                'timeZoneId': 'America/New_York',
                'isAddressHidden': False,
                'addressRevealConfig': None,
            },
            'ticketHubInfo': {
                'ticketHandle': '{{ticketHubInfo_id}}',
                'priceSyncedAt': '2026-09-03T09:44:42.350Z',
                'sectionOptions': [
                    {
                        'label': 'GeneralAdmission',
                        'price': {
                            'amount': 4930,
                            'currency': 'USD',
                        },
                        'quantityRule': {
                            'max': 4,
                            'min': 1,
                            'step': 1,
                        },
                        'ticketHandle': '{{ticketHandle}}',
                        'availableQuantity': '{{availableQuantity}}',
                        'isGeneralAdmission': vars['isGeneralAdmission'],
                    },
                ],
            },
            'customizedFields': [],
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'shippingOptions': [],
            'shippingNote': None,
            'autoFulfill': True,
            'eventId': '{{event_id}}',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'copyFromId': '{{productId}}',
            'stopSellingAfter': None,
            'stopSellingAfterDisplay': None,
            'deliveryMethod': 'THIRD_PARTY_ISSUED',
            'thirdPartyDeliveryMessage': 'Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.',
            'isMultipleDaysPassEnabled': False,
            'isVenueUnitEnabled': False,
            'venueUnitCategoryId': None,
            'multipleDaysPass': None,
            'isPickupEtaEnabled': None,
            'eventMatchingRules': None,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'allowAtDoorSales': False,
            'isProductFormEnabled': bool(vars['productForm']),
            'isVariantPriceDisplayEnabled': False,
            'isTipEnabled': False,
            'hideFees': False,
            'isPlatformFeeConfigCustomized': False,
            'isVariantPlatformFeeConfigCustomized': False,
            'transactionFeeConfig': {
                'baseConfig': {
                    'unitFixedFee': 1,
                    'unitPercentageFee': 0.1,
                },
            },
            'transactionFeeRebateConfig': {
                'baseConfig': {
                    'unitFixedFee': 0,
                    'unitPercentageFee': 0,
                },
            },
            'transactionCustomFeeConfig': None,
            'overrideEventCustomFee': False,
            'isInclusionsEnabled': False,
            'images': [
                {
                    'id': '7b9ef5e8-a5ff-4d9b-95fc-7f75872008a9',
                    'remote_id': None,
                    'createdAt': '2026-09-03T09:44:42.518Z',
                    'updatedAt': '2026-09-03T09:44:42.518Z',
                    'height': 1000,
                    'width': 1000,
                    'position': 1,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'name': 'Title',
                    'images': [
                        {
                            'value': 'Default Title',
                            'image': None,
                        },
                    ],
                },
            ],
            'variants': [
                {
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-09-03T09:44:42.518Z',
                    'updatedAt': '2026-09-03T09:44:42.518Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': '{{availableQuantity}}',
                    'inventoryQuantityOriginal': '{{availableQuantity}}',
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '55.88',
                    'priceAnchor': '0.00',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 6.58,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 6.58,
                        'customFeeBreakdown': {
                            'TAX': {
                                'index': 0,
                                'title': 'Taxes',
                                'itemFee': 0,
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0,
                            },
                        },
                        'transactionItemFee': 6.58,
                    },
                    'ticketPrice': 49.3,
                    'isMinPurchaseQuantityEnabled': True,
                    'minPurchaseQuantity': 1,
                    'isMaxPurchaseQuantityEnabled': True,
                    'maxPurchaseQuantity': 4,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                    'image': None,
                },
            ],
            'inclusions': [],
            'productForm': vars['productForm'],
        },
    ],
    'lineup': [],
    'eventProducts': [],
    'ignoreStartTime': False,
    'ignoreEndTime': False,
    'duplicateEventId': '{{event_id}}',
    'posterBackend': [
        {
            'src': 'https://images.discovery-prod.tdc.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
            'width': 1200,
            'height': 630,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': None,
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'MidnightGlow',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'version': 'v2',
        'backgroundColor': '#000000',
        'title': {
            'color': '#F6CA7C',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 700,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'dividerColor': '#5D5D5D',
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderRadius': 0,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'fontWeight': 400,
        },
        'product': {
            'borderRadius': 0,
        },
        'featuredProducts': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'relatedLink': {
            'backgroundColor': '#FAFAFA',
            'color': '#000000 ',
            'borderRadius': 0,
        },
        'announcementCarousel': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#7132F4',
            '#FFFFFF',
        ],
    },
}, token='yuxiao999_token')
    # 复制失败会让 dup_event_id 落空 → 下游 URL 变成 /posts/curator/event//posts (404)，
    # 报错信息完全指不到真正原因，故在此显式断言并带出服务端错误体。
    assert _resp7.status_code in (200, 201), f"step7 复制事件失败：{_resp7.describe()}"
    _dupeventid_val = _get_path(_resp7.json(), ['data', 'id'])
    vars['dup_event_id'] = _dupeventid_val if _dupeventid_val is not None else ''
    _lineupid_val = _get_path(_resp7.json(), ['data', 'lineup', 0, 'id'])
    vars['lineup_id'] = _lineupid_val if _lineupid_val is not None else ''
    # step 8: GET get the event post id
    _resp8 = ctx.api.posts.curator_event_posts(body=None, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
    _items8: list[dict] = (_resp8.json().get('data') or {}).get('items') or []
    _post0id_val = _get_path(_resp8.json(), ['data', 'items', 0, 'id'])
    vars['post0_id'] = _post0id_val if _post0id_val is not None else ''
    # post0_id 是 step4/9/11 的**路径变量**（GET /post/v2/{{post0_id}}/relate-products）。
    # 而下游 buy-now / checkout-express 的 body 消费 {{postId}}，原迁移漏赋值 → 空串 →
    # 400 `id must be a UUID`。复刻事件自动生成的 post 有时把新标题只落在 headline 上，
    # 故先按 dul_event_title 匹配 title，再退 headline，最后退「列表唯一项」，并显式断言。
    _target8 = (_pick_first(_items8, lambda i: i.get('title') == vars.get('dul_event_title'))
                or _pick_first(_items8, lambda i: i.get('headline') == vars.get('dul_event_title'))
                or (_items8[0] if len(_items8) == 1 else None))
    assert _target8, (f"step8 未能在事件 {vars.get('dup_event_id')} 的 posts 中找到目标 post"
                      f"（items={len(_items8)}）")
    vars['postId'] = _target8.get('id') or ''
    # step 9: GET Catch the ProductId and promoterProductId
    _resp9 = ctx.api.admin.post_v2_relate_products(body=None, token='admin_token')
    _rels9: list[dict] = (_resp9.json().get('data') or {}).get('relatedProducts') or []
    _prod9 = _pick_first(_rels9, _product_has_stock)
    assert _prod9, f"step9 未找到库存 > 0 的关联产品（relatedProducts={len(_rels9)}）"
    _apply_related_product(ctx, _prod9)
    # step 10: PUT setting the event status as Hold
    _resp10 = ctx.api.events.by_dup_event_id(body={
    'id': '{{dup_event_id}}',
    'title': '{{dul_event_title}}',
    'curatorId': '{{user_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"This event has a tiered pricing structure in the General Admission area. All General Admission tiers have the same access. Once a price level sells out it may no longer be visible or available for selection. *Please note: multiple GA price levels may be available at the same time The event organizer has decided that ticket transfer will be delayed for this event. Ticket transfer will be available on or about three weeks prior to the event. Please review the terms of TDC’s Purchase Agreement for more information.","type":"extended-text","version":1}],"direction":null,"format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2027-11-07T01:00:00.000Z',
    'endDate': '2027-12-01T05:15:00.000Z',
    'venue': 'Agora Theatre',
    'location': 'Cleveland, OH, United States',
    'status': 'ON_HOLD',
    'isTaxEnabled': False,
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap. Make sure you buy, tickets SOLD OUT last event!",
        'align': 'center',
    },
    'poster': {
        'height': 630,
        'mediaDuration': 0,
        'mediaType': 'IMAGE',
        'position': 0,
        'src': 'https://images.discovery-prod.tdc.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
        'width': 1200,
    },
    'startDateDisplay': '2027-11-06 21:00',
    'endDateDisplay': '2027-12-01 00:15',
    'note': '{{dul_event_title}}',
    'timezone': {
        'timeZoneId': 'America/New_York',
        'timeZoneName': 'Eastern Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -18000,
    },
    'isAddressRevealEnabled': False,
    'isAddressHidden': False,
    'messageInfo': {
        'cooldownMinutes': 15,
        'emailMaxLimit': 5,
        'smsMaxLimit': 3,
    },
    'platform': 'TDC',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Cleveland',
        'country': 'United States',
        'line1': None,
        'line2': None,
        'placeId': None,
        'state': 'OH',
        'stateName': 'OH',
        'stripeLocationId': None,
        'zipcode': None,
    },
    'country': 'United States',
    'state': 'OH',
    'autoReplace': False,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'ticketHubInfo': {
        'contextDesc': 'AEG Great Lakes',
        'contextId': '517840254',
        'eventHandle': 'eyJwbGF0Zm9ybSI6IkFYUyIsImh1YklkIjoiYy1wS2o5Ujk1d0Z1bWl0RmNUYXFIb283dVNCcHktaXlRTmdNTFNGZnNybyJ9',
    },
    'readOnlyFields': [
        'tax',
        'customFees',
        'duplicateTicket',
        'addTicket',
        'addMerch',
        'duplicateMerch',
    ],
    'medias': [],
    'tickets': [
        {
            'id': '{{productId}}',
            'title': 'General Admission — Pear.US',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'height': 630,
                'mediaDuration': 0,
                'mediaType': 'IMAGE',
                'position': 0,
                'src': 'https://images.discovery-prod.tdc.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
                'width': 1200,
            },
            'inventoryQuantity': 82,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 55.88,
            'priceMax': 55.88,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'contributedBy': 3,
                    'contributorId': None,
                    'createdAt': '2026-09-07T03:49:37.677Z',
                    'height': 1000,
                    'id': '6ca3d3dc-34f3-4898-84ca-e8a7776a757c',
                    'mediaDuration': 0,
                    'mediaSrc': None,
                    'mediaType': 'IMAGE',
                    'position': 1,
                    'productId': '{{productId}}',
                    'productImageType': 'PRODUCT',
                    'remote_id': None,
                    'source': None,
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png',
                    'updatedAt': '2026-09-07T03:49:37.677Z',
                    'variantIds': [],
                    'width': 1000,
                },
            ],
            'options': [
                {
                    'id': 'e3e6d794-4549-45f7-82a3-9d289715eedf',
                    'images': [
                        {
                            'imageId': None,
                            'value': 'Default Title',
                        },
                    ],
                    'name': 'Title',
                    'position': 1,
                    'productId': '{{productId}}',
                    'remote_id': None,
                    'values': [
                        'Default Title',
                    ],
                },
            ],
            'variants': [
                {
                    'compareAtPrice': None,
                    'createdAt': '2026-09-07T03:49:37.677Z',
                    'fees': 6.58,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'id': '{{merchantProductVariantId}}',
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 82,
                    'inventoryQuantityOriginal': 82,
                    'isInventoryQuantityUnlimited': False,
                    'isMaxPurchaseQuantityEnabled': True,
                    'isMinPurchaseQuantityEnabled': True,
                    'isPackSizeEnabled': False,
                    'maxPurchaseQuantity': 4,
                    'minPurchaseQuantity': 1,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'packSize': None,
                    'platform': None,
                    'position': 1,
                    'price': '55.88',
                    'priceAnchor': '0.00',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'remote_id': None,
                    'sku': '',
                    'soldQuantity': 0,
                    'taxCode': None,
                    'taxable': True,
                    'ticketPrice': 49.3,
                    'title': 'Default Title',
                    'transactionFee': {
                        'customFee': 0,
                        'customFeeBreakdown': {
                            'TAX': {
                                'index': 0,
                                'itemFee': 0,
                                'title': 'Taxes',
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0,
                            },
                        },
                        'platformFee': 6.58,
                        'transactionItemFee': 6.58,
                    },
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                    'updatedAt': '2026-09-07T03:49:37.677Z',
                    'weight': None,
                    'weightUnit': 'lb',
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-09-07T03:49:37.653Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': None,
            'deliveryMethod': 'THIRD_PARTY_ISSUED',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': 'Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.',
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '34z3as',
            'taxEnable': False,
            'taxJarCategory': '',
            'productFormId': '7dbd799d-032b-4333-9376-9a157c8ac31b',
            'isPlatformFeeConfigOutdated': False,
            'copyFromId': '{{productId}}',
        },
    ],
    'lineup': [],
    'eventProducts': [],
    'products': [
        {
            'id': '{{productId}}',
            'title': 'General Admission — Pear.US',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'height': 630,
                'mediaDuration': 0,
                'mediaType': 'IMAGE',
                'position': 0,
                'src': 'https://images.discovery-prod.tdc.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
                'width': 1200,
            },
            'inventoryQuantity': 82,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 55.88,
            'priceMax': 55.88,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'contributedBy': 3,
                    'contributorId': None,
                    'createdAt': '2026-09-07T03:49:37.677Z',
                    'height': 1000,
                    'id': '6ca3d3dc-34f3-4898-84ca-e8a7776a757c',
                    'mediaDuration': 0,
                    'mediaSrc': None,
                    'mediaType': 'IMAGE',
                    'position': 1,
                    'productId': '{{productId}}',
                    'productImageType': 'PRODUCT',
                    'remote_id': None,
                    'source': None,
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1782457065/uploaded_images/w2ozhgihovoqxegk9vf8.png',
                    'updatedAt': '2026-09-07T03:49:37.677Z',
                    'variantIds': [],
                    'width': 1000,
                },
            ],
            'options': [
                {
                    'id': 'e3e6d794-4549-45f7-82a3-9d289715eedf',
                    'images': [
                        {
                            'imageId': None,
                            'value': 'Default Title',
                        },
                    ],
                    'name': 'Title',
                    'position': 1,
                    'productId': '{{productId}}',
                    'remote_id': None,
                    'values': [
                        'Default Title',
                    ],
                },
            ],
            'variants': [
                {
                    'compareAtPrice': None,
                    'createdAt': '2026-09-07T03:49:37.677Z',
                    'fees': 6.58,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'id': '{{merchantProductVariantId}}',
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 82,
                    'inventoryQuantityOriginal': 82,
                    'isInventoryQuantityUnlimited': False,
                    'isMaxPurchaseQuantityEnabled': True,
                    'isMinPurchaseQuantityEnabled': True,
                    'isPackSizeEnabled': False,
                    'maxPurchaseQuantity': 4,
                    'minPurchaseQuantity': 1,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'packSize': None,
                    'platform': None,
                    'position': 1,
                    'price': '55.88',
                    'priceAnchor': '0.00',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'remote_id': None,
                    'sku': '',
                    'soldQuantity': 0,
                    'taxCode': None,
                    'taxable': True,
                    'ticketPrice': 49.3,
                    'title': 'Default Title',
                    'transactionFee': {
                        'customFee': 0,
                        'customFeeBreakdown': {
                            'TAX': {
                                'index': 0,
                                'itemFee': 0,
                                'title': 'Taxes',
                                'unitFixedFee': 0,
                                'unitPercentageFee': 0,
                            },
                        },
                        'platformFee': 6.58,
                        'transactionItemFee': 6.58,
                    },
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                    'updatedAt': '2026-09-07T03:49:37.677Z',
                    'weight': None,
                    'weightUnit': 'lb',
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-09-07T03:49:37.653Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': None,
            'deliveryMethod': 'THIRD_PARTY_ISSUED',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': 'Tickets will be delivered in a separate email closer to the event date to ensure accuracy and a smooth entry on show day.',
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '34z3as',
            'taxEnable': False,
            'taxJarCategory': '',
            'productFormId': '7dbd799d-032b-4333-9376-9a157c8ac31b',
            'isPlatformFeeConfigOutdated': False,
        },
    ],
    'statistics': {
        'totalAvailableTickets': 82,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
        'totalTickets': 82,
        'totalMerch': 0,
        'totalSoldMerch': 0,
        'totalAvailableMerch': 0,
        'totalRedeemedMerch': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': False,
    'ignoreEndTime': False,
    'posterBackend': [
        {
            'height': 630,
            'mediaDuration': 0,
            'mediaType': 'IMAGE',
            'position': 0,
            'src': 'https://images.discovery-prod.tdc.com/2026/06/zack-fox-dj-set-tickets_11-06-26_1_6a3ae524110f2.jpg',
            'width': 1200,
        },
    ],
    'customFeeConfig': {
        'isEnabled': False,
        'items': [],
    },
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'MidnightGlow',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'version': 'v2',
        'backgroundColor': '#000000',
        'title': {
            'color': '#F6CA7C',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 700,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'dividerColor': '#5D5D5D',
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderRadius': 0,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'fontWeight': 400,
        },
        'product': {
            'borderRadius': 0,
        },
        'featuredProducts': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'relatedLink': {
            'backgroundColor': '#FAFAFA',
            'color': '#000000 ',
            'borderRadius': 0,
        },
        'announcementCarousel': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#7132F4',
            '#FFFFFF',
        ],
    },
}, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # assertion 10.assertion: responseJson equal 200
    expect(_resp10).json('$.code').equals('200')
    # assertion 10.assertion: event status is ON_HOLD
    expect(_resp10).json('$.data.status').equals('ON_HOLD')
    # step15/18 期望报 "The product(ticket on hold)is not available." 的来源。
    # 单独跑本用例时这两个变量为空，buy-now 会落到复制出来的 TDC 外链票上，被 ticket hub
    # 以 "These tickets are not on sale right now." 拒掉（外部票无法在本环境转售），
    # 于是 orderId 取不到 → step24 的 body 残留 "{{orderId}}" → 400 id must be a UUID。
    # 故这里把那张票补建出来，让用例自洽。
    _resp10b = ctx.api.products.create(body={
    'merchantId': '{{catalog_id}}',
    'shippingType': 'NO_SHIPPING_REQUIRED',
    'isFeatured': False,
    'commissionRate': 0,
    'priceSyncImported': False,
    'additionalShippingFee': 0,
    'returnPolicyApplied': True,
    'title': 'ticket on hold',
    'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
    'status': 'ACTIVE',
    'isUsed': 'NWT',
    'taxJarCategory': '',
    'platform': 'PEAR',
    'autoFulfill': True,
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
            'price': 0,
            'priceAnchor': 0,
            'option': {
                'option1': 'Default Title',
            },
            'fees': 0,
            'ticketPrice': 0,
            'transactionFee': {
                'platformFee': 0,
                'customFee': 0,
                'customFeeBreakdown': {},
                'transactionItemFee': 0,
            },
            'minPriceForCheckFees': 0,
            'weightUnit': 'lb',
        },
    ],
    'listingType': 'TICKET',
    'ticketType': 'TICKET_TYPE_STANDARD',
    'soldQuantity': 0,
    'excludeFromPostSync': False,
    'isTipEnabled': False,
    'useEventPosterAsCover': True,
    'catalogCommissionRate': 0,
    'deliveryMethod': 'QR_CODE',
    'thirdPartyDeliveryMessage': '',
    'taxEnable': True,
    'customTaxRate': None,
    'earliestTime': '2026-08-12T09:32:07.963Z',
    'styleSettings': {
        'recentUsedColors': [
            '#110921',
            '#ECA416',
            '#FFEEBE',
            '#0000',
            '#0D0D14',
            '#2D2108',
            '#5D5D5D',
            '#CBBE9C',
            '#000000',
            '#EDA415',
            '#FFFFFF',
            '#CFCFCF',
            '#ABABAB',
            '#C1C1C3',
            '#858585',
            '#F6CA7C',
            '#E0E0E0',
        ],
    },
    'isInclusionsEnabled': False,
    'inclusions': [],
    'isVariantPriceDisplayEnabled': False,
    'stopSellingAfterDisplay': '',
    'extraInfo': {
        'businessTimezone': 'America/Los_Angeles',
    },
    'overrideEventTax': False,
    'overrideEventCustomFee': False,
    'hideFees': False,
    'transactionCustomFeeConfig': None,
    'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'images': [
        {
            'height': 2048,
            'mediaDuration': 0,
            'mediaType': 'IMAGE',
            'position': 0,
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
        },
    ],
    'eventId': '{{dup_event_id}}',
    'isExpirationEnabled': False,
}, token='yuxiao999_token')
    assert _resp10b.status_code in (200, 201), f"补建 ticket on hold 票失败：{_resp10b.describe()}"
    _d_hold = _resp10b.json().get('data') or {}
    vars['on_hold_productId'] = _d_hold.get('id') or ''
    _hold_variants = _d_hold.get('variants') or []
    vars['on_hold_displayVariantId'] = ((_hold_variants[0].get('displayVariantId')
                                     or _hold_variants[0].get('id')) or '') if _hold_variants else ''
    vars['on_hold_merchantVariantId'] = ((_hold_variants[0].get('merchantProductVariantId')
                                      or _hold_variants[0].get('id')) or '') if _hold_variants else ''
    # show-in-post：把新票挂到复制出来的 post 上（与兄弟用例 step12 一致），
    # 这样 step11 的 post/v2/{{postId}}/relate-products 能查到它。
    _resp10c = ctx.api.events.v2_show_in_post(body={
        "productIds": [
            "{{on_hold_productId}}",
        ],
        "posts": [
            {
                "postId": "{{postId}}",
                "isVisible": True,
            },
        ],
    }, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
    assert _resp10c.status_code in (200, 201), f"补建票 show-in-post 失败：{_resp10c.describe()}"
    # step 11: GET Catch the promoterProductvariantId and merchantProductVariantId
    _resp11 = ctx.api.admin.post_v2_relate_products(
        body=None, token='admin_token', path_vars={'post0_id': '{{postId}}'})
    # 实测本用例数据里并没有该标题的产品：源事件 DANNA 的票是 GA Standing Floor /
    # Reserved Balcony / GA Standing Balcony，复制后只剩一张 "General Admission — Pear.US"。
    # 本用例下游（step14 buy-now、step15/18 checkout-express）只把该变量当作
    # 「复制事件那张票的变体 id」用，且 step15/18 迁移后并未保留标题相关断言，
    # 故按标题优先命中、否则取首个带 displayVariantId 的关联产品。
    _rels11: list[dict] = (_resp11.json().get('data') or {}).get('relatedProducts') or []
    _tp11 = (_pick_first(_rels11, lambda p: p.get('title') == 'ticket on hold')
             or _pick_first(_rels11, lambda p: p.get('id') == vars.get('on_hold_productId')))
    vars['promoterProductId'] = ((_tp11 or {}).get('displayVariantId')
                                 or vars.get('on_hold_displayVariantId') or '')
    assert vars['promoterProductId'], (f"step11 未取到可买变体"
                                      f"（relatedProducts={len(_rels11)}）")
    # step 12: POST guest login
    _resp12 = ctx.api.auth.guest_login(body={
        "consumerId": "{{__uuid_0}}",
    })
    vars['access_token'] = (_resp12.json() if _resp12.headers.get('content-type', '').startswith('application/json') else {}).get('data', '')
    # step 13: DELETE Clean Cart
    _resp13 = ctx.api.cart.delete(body={}, app_headers=True, token='access_token')
    # assertion 13.assertion: responseJson equal 200
    expect(_resp13).json('$.code').equals('200')
    # assertion 13.assertion: responseJson equal success
    expect(_resp13).json('$.message').equals('success')
    # step 14: POST buy now
    _resp14 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "{{postId}}",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 2,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "{{event_id}}",
            "pixelId": [
                "test",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "{{promoterProductId}}",
                "postId": "{{postId}}",
                "price": 2,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='access_token')
    # extractor: orderId = $.data.orderId
    # 注意：此处 buy-now 预期失败（step10 已把事件置为 ON_HOLD，票不可售），
    # orderId 取不到是正常的；真正的 orderId 由 step23 提供（那时事件已回到 UPCOMING）。
    ctx.extract('orderId', _resp14, '$.data.orderId')
    # step 15: POST check the "Hold" post is unable to checkout
    _resp15 = ctx.api.orders.checkout_express(body={
        "items": [
            {
                "quantity": 3,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 8.57,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "{{dup_event_id}}",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1786526453224.334258892692108835",
            "externalId": "b0b0ed9c-8bc8-426f-b590-9a97f10dcd24",
            "eventSourceUrl": "https://release.pear.us/autotestshop/post/duplicate-verify-the-event-can-create-and-duplicate-and-delete-success",
        },
        "subdomainVanityUrl": "",
    }, app_headers=True, token='access_token')
    # step 16: GET get shipping-options
    _resp16 = ctx.api.merchants.shipping_options(body=None, token='yuxiao999_token')
    _items16 = (_resp16.json().get('data') or {}).get('items') or []
    assert _items16, 'step16 未取到 shipping options，下游 body 需要 {{shipping_option_id}}'
    vars['shipping_option_id'] = _items16[0].get('id') or ''
    # step 17: PUT setting the event status as Cancelled
    _resp17 = ctx.api.events.by_dup_event_id(body={
    'id': '{{dup_event_id}}',
    'title': '{{event_title}}',
    'curatorId': '{{catalog_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2053-04-17T05:00:00.000Z',
    'endDate': None,
    'venue': 'Instagram Live, Zoom, In-person',
    'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
    'status': 'CANCELED',
    'isTaxEnabled': True,
    'taxConfig': {
        'customTaxRate': 10,
        'calculationType': 'CUSTOM',
        'configUpdatedAt': '2026-08-14T02:04:30.036Z',
    },
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap of our last event👇",
        'align': 'center',
    },
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2053-04-17',
    'note': 'linda note',
    'timezone': {
        'timeZoneId': 'America/Chicago',
        'timeZoneName': 'Central Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -21600,
    },
    'isAddressRevealEnabled': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'PEAR',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Chicago',
        'line1': '789 River East Art Center Promenade',
        'line2': None,
        'state': 'IL',
        'country': 'US',
        'placeId': None,
        'zipcode': None,
        'stateName': 'Illinois',
        'stripeLocationId': None,
    },
    'country': 'US',
    'state': 'IL',
    'autoReplace': True,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'venueMapId': None,
    'ticketHubInfo': None,
    'readOnlyFields': [],
    'medias': [],
    # post-script 覆盖成**复制出来的 TDC 外链票** id。PUT /product-event 的 tickets
    # 是整体替换语义：用它会把事件票列表替换成那张外部票，我们在上一步补建的 PEAR
    # 票会被挤出事件（同时掉落 post 的 relatedProducts），step23 的 buy-now 随即
    # 落到外部票上被 ticket hub 拒绝（These tickets are not on sale right now.）。
    # 本 body 的标题是 'ticket on hold' + deliveryMethod QR_CODE，语义上指向的正是
    # 补建的那张 PEAR 票，故改为 '{{on_hold_productId}}'。
    'tickets': [
        {
            'id': '{{on_hold_productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
                    'name': 'Title',
                    'position': 1,
                    'values': [
                        'Default Title',
                    ],
                    'images': [
                        {
                            'value': 'Default Title',
                            'imageId': None,
                        },
                    ],
                },
            ],
            'variants': [
                {
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_ON_HOLD',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
            'copyFromId': '{{productId}}',
        },
    ],
    'lineup': [
        {
            'title': 'lineup',
            'introduction': '001',
            'poster': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf',
                'width': 160,
                'height': 160,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'isHeadliner': False,
            'order': 0,
            'isPaymentAfterEventEnabled': False,
            'id': 'ae6d0a8a-221b-4bec-8ada-f2fea16b4443',
        },
    ],
    'eventProducts': [],
    'products': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
                    'name': 'Title',
                    'position': 1,
                    'values': [
                        'Default Title',
                    ],
                    'images': [
                        {
                            'value': 'Default Title',
                            'imageId': None,
                        },
                    ],
                },
            ],
            'variants': [
                {
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_ON_HOLD',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
        },
    ],
    'statistics': {
        'totalAvailableTickets': 10,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
        'totalTickets': 10,
        'totalMerch': 0,
        'totalSoldMerch': 0,
        'totalAvailableMerch': 0,
        'totalRedeemedMerch': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': True,
    'ignoreEndTime': True,
    'posterBackend': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
            'height': 2048,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': {
        'isEnabled': True,
        'items': [
            {
                'title': 'custom fee',
                'unitFixedFee': 0,
                'unitPercentageFee': 0.1,
            },
        ],
    },
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'MidnightGlow',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'dividerColor': '#5D5D5D',
        'secondaryTextColor': '#E0E0E0',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 700,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'subtitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 400,
            'color': '#FFFFFF',
        },
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderColor': '#000000',
            'borderRadius': 0,
            'boxShadow': 'none',
            'fontSize': 16,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'fontSize': 16,
            'fontWeight': 400,
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'boxShadow': 'none',
        },
        'textButton': {
            'fontSize': 16,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'selectButton': {
            'borderColor': '#000000',
        },
        'relatedLink': {
            'borderRadius': 0,
            'color': '#000000 ',
            'borderColor': '#0000',
            'backgroundColor': '#FAFAFA',
        },
        'featuredProducts': {
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'product': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
        },
        'discount': {
            'backgroundColor': '#D32A09',
            'color': '#FFFFFF',
            'priceColor': '#FFFFFF',
        },
        'freeShipping': {
            'backgroundColor': '#EBF5EF',
            'color': '#268E46',
        },
        'starRatingColor': '#FAAF03',
        'layoutFeatureCard': {
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 16,
                'fontWeight': 700,
                'color': '#FFFFFF',
            },
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'button': {
                'backgroundColor': '#F6CA7C',
                'color': '#000000',
            },
        },
        'lineupBanner': {
            'titleText': '#FFFFFF',
            'descriptionText': '#E0E0E0',
        },
        'eventInfoBanner': {
            'text': '#FFFFFF',
            'secondaryText': '#E0E0E0',
        },
        'eventDescription': {
            'text': '#E0E0E0',
            'title': '#FFFFFF',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#ffffff',
        ],
    },
}, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # assertion 17.assertion: responseJson equal 200
    expect(_resp17).json('$.code').equals('200')
    # assertion 17.assertion: event status is CANCELED
    expect(_resp17).json('$.data.status').equals('CANCELED')
    # step 18: POST check the "cancelled" post is unable to checkout
    _resp18 = ctx.api.orders.checkout_express(body={
        "items": [
            {
                "quantity": 3,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 8.57,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "{{dup_event_id}}",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1786526453224.334258892692108835",
            "externalId": "b0b0ed9c-8bc8-426f-b590-9a97f10dcd24",
            "eventSourceUrl": "https://release.pear.us/autotestshop/post/duplicate-verify-the-event-can-create-and-duplicate-and-delete-success",
        },
        "subdomainVanityUrl": "",
    }, app_headers=True, token='access_token')
    # step 19: PUT setting the event status as Completed
    _resp19 = ctx.api.events.by_dup_event_id(body={
    'id': '{{dup_event_id}}',
    'title': '{{event_title}}',
    'curatorId': '{{catalog_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2053-04-17T05:00:00.000Z',
    'endDate': None,
    'venue': 'Instagram Live, Zoom, In-person',
    'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
    'status': 'COMPLETED',
    'isTaxEnabled': True,
    'taxConfig': {
        'customTaxRate': 10,
        'calculationType': 'CUSTOM',
        'configUpdatedAt': '2026-08-14T02:04:30.036Z',
    },
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap of our last event👇",
        'align': 'center',
    },
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2053-04-17',
    'note': 'linda note',
    'timezone': {
        'timeZoneId': 'America/Chicago',
        'timeZoneName': 'Central Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -21600,
    },
    'isAddressRevealEnabled': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'PEAR',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Chicago',
        'line1': '789 River East Art Center Promenade',
        'line2': None,
        'state': 'IL',
        'country': 'US',
        'placeId': None,
        'zipcode': None,
        'stateName': 'Illinois',
        'stripeLocationId': None,
    },
    'country': 'US',
    'state': 'IL',
    'autoReplace': True,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'venueMapId': None,
    'ticketHubInfo': None,
    'readOnlyFields': [],
    'medias': [],
    # post-script 覆盖成**复制出来的 TDC 外链票** id。PUT /product-event 的 tickets
    # 是整体替换语义：用它会把事件票列表替换成那张外部票，我们在上一步补建的 PEAR
    # 票会被挤出事件（同时掉落 post 的 relatedProducts），step23 的 buy-now 随即
    # 落到外部票上被 ticket hub 拒绝（These tickets are not on sale right now.）。
    # 本 body 的标题是 'ticket on hold' + deliveryMethod QR_CODE，语义上指向的正是
    # 补建的那张 PEAR 票，故改为 '{{on_hold_productId}}'。
    'tickets': [
        {
            'id': '{{on_hold_productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
                    'name': 'Title',
                    'position': 1,
                    'values': [
                        'Default Title',
                    ],
                    'images': [
                        {
                            'value': 'Default Title',
                            'imageId': None,
                        },
                    ],
                },
            ],
            'variants': [
                {
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_CANCELED',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
            'copyFromId': '{{productId}}',
        },
    ],
    'lineup': [
        {
            'title': 'lineup',
            'introduction': '001',
            'poster': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf',
                'width': 160,
                'height': 160,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'isHeadliner': False,
            'order': 0,
            'isPaymentAfterEventEnabled': False,
            'id': 'ae6d0a8a-221b-4bec-8ada-f2fea16b4443',
        },
    ],
    'eventProducts': [],
    'products': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
                    'name': 'Title',
                    'position': 1,
                    'values': [
                        'Default Title',
                    ],
                    'images': [
                        {
                            'value': 'Default Title',
                            'imageId': None,
                        },
                    ],
                },
            ],
            'variants': [
                {
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_CANCELED',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
        },
    ],
    'statistics': {
        'totalAvailableTickets': 10,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
        'totalTickets': 10,
        'totalMerch': 0,
        'totalSoldMerch': 0,
        'totalAvailableMerch': 0,
        'totalRedeemedMerch': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': True,
    'ignoreEndTime': True,
    'posterBackend': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
            'height': 2048,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': {
        'isEnabled': True,
        'items': [
            {
                'title': 'custom fee',
                'unitFixedFee': 0,
                'unitPercentageFee': 0.1,
            },
        ],
    },
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'MidnightGlow',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'dividerColor': '#5D5D5D',
        'secondaryTextColor': '#E0E0E0',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 700,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'subtitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 400,
            'color': '#FFFFFF',
        },
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderColor': '#000000',
            'borderRadius': 0,
            'boxShadow': 'none',
            'fontSize': 16,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'fontSize': 16,
            'fontWeight': 400,
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'boxShadow': 'none',
        },
        'textButton': {
            'fontSize': 16,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'selectButton': {
            'borderColor': '#000000',
        },
        'relatedLink': {
            'borderRadius': 0,
            'color': '#000000 ',
            'borderColor': '#0000',
            'backgroundColor': '#FAFAFA',
        },
        'featuredProducts': {
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'product': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
        },
        'discount': {
            'backgroundColor': '#D32A09',
            'color': '#FFFFFF',
            'priceColor': '#FFFFFF',
        },
        'freeShipping': {
            'backgroundColor': '#EBF5EF',
            'color': '#268E46',
        },
        'starRatingColor': '#FAAF03',
        'layoutFeatureCard': {
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 16,
                'fontWeight': 700,
                'color': '#FFFFFF',
            },
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'button': {
                'backgroundColor': '#F6CA7C',
                'color': '#000000',
            },
        },
        'lineupBanner': {
            'titleText': '#FFFFFF',
            'descriptionText': '#E0E0E0',
        },
        'eventInfoBanner': {
            'text': '#FFFFFF',
            'secondaryText': '#E0E0E0',
        },
        'eventDescription': {
            'text': '#E0E0E0',
            'title': '#FFFFFF',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#ffffff',
        ],
    },
}, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # assertion 19.assertion: responseJson equal 200
    expect(_resp19).json('$.code').equals('200')
    # assertion 19.assertion: event status is COMPLETED
    expect(_resp19).json('$.data.status').equals('COMPLETED')
    # step 20: PATCH admin update the event status from complete to upcoming
    _resp20 = ctx.api.admin.events_by_dup_event_id(body={
        "status": "UPCOMING",
    }, token='admin_token')
    # assertion 20.assertion: responseJson equal 200
    expect(_resp20).json('$.code').equals('200')
    # assertion 20.assertion: responseJson equal success
    expect(_resp20).json('$.message').equals('success')
    # assertion 20.assertion: event status is UPCOMING (admin PATCH 不返回 event 对象，重新 GET 校验)
    _resp20b = ctx.api.events._call("GET", '/product-event/{{dup_event_id}}', token='yuxiao999_token', app_headers=True)
    expect(_resp20b).json('$.data.status').equals('UPCOMING')
    # step 22: DELETE Clean Cart
    _resp22 = ctx.api.cart.delete(body={}, app_headers=True, token='access_token')
    # assertion 22.assertion: responseJson equal 200
    expect(_resp22).json('$.code').equals('200')
    # assertion 22.assertion: responseJson equal success
    expect(_resp22).json('$.message').equals('success')
    # step11 取到的 displayVariantId 在 step17/19 的 PUT 之后已失效（PUT 会重排事件票），
    # 直接拿来 buy-now 会 400 `relatedProduct Not Found`。故买之前重新取一次关联产品，
    # 按**变体 id** 精确匹配上一步补建的那张 PEAR 票，避免命中同名的其它票。
    _rels23 = ctx.api.admin.post_v2_relate_products(
        body=None, token='admin_token', path_vars={'post0_id': '{{postId}}'})
    _list23: list[dict] = (_rels23.json().get('data') or {}).get('relatedProducts') or []
    _tp23 = _pick_first(
        _list23,
        lambda p: any(v.get('merchantProductVariantId') == vars.get('on_hold_merchantVariantId')
                      for v in (p.get('variants') or [])))
    assert _tp23, (f"step23 关联产品中未找到补建的 ticket on hold 票"
                   f"（on_hold_merchantVariantId={vars.get('on_hold_merchantVariantId')}，"
                   f"relatedProducts={len(_list23)}）")
    vars['promoterProductId'] = _tp23.get('displayVariantId') or ''
    # step 23: POST buy now
    _resp23 = ctx.api.orders.buy_now(body={
        "postIdForFilter": "{{postId}}",
        "updateCartItems": [
            {
                "quantity": 1,
                "promoterProductVariantId": "{{promoterProductId}}",
                "price": 2,
                "postId": "{{postId}}",
                "selected": True,
                "customFields": [],
            },
        ],
        "fbAdParams": {
            "eventID": "{{event_id}}",
            "pixelId": [
                "test",
            ],
            "fbBrowserId": "fb.1.1756981422832.790136385853196461",
            "externalId": "986eb96d-be5a-4a52-8379-eeddddc6df56",
            "eventSourceUrl": "https://release.pear.us/yu-xiao/post/zileb8",
        },
        "currentUpdateCartItems": [
            {
                "quantity": 1,
                "id": "{{promoterProductId}}",
                "postId": "{{postId}}",
                "price": 2,
                "customFields": [],
            },
        ],
    }, app_headers=True, token='access_token')
    # extractor: orderId = $.data.orderId
    # orderId 是 step24 下单（POST /order）的 body 入参。这一步 buy-now 必须成功：
    # 失败时 ctx.extract 会把 orderId 写成 None，而 render_text 跳过 None 值，
    # 下游 body 就会带着未渲染的 "{{orderId}}" 发出去 → 400 `id must be a UUID`，
    # 报错完全指不到真正原因，故在此断言并带出服务端错误体。
    assert _resp23.status_code in (200, 201), f"step23 buy-now 失败：{_resp23.describe()}"
    ctx.extract('orderId', _resp23, '$.data.orderId')
    # step 24: POST place order
    _resp24 = ctx.api.orders.create(body={
        "inviterCampaign": {},
        "id": "{{orderId}}",
        "contact": {
            "email": "{{$internet.email(locale='en')}}",
            "firstName": "test",
            "lastName": "linda",
            "phoneNumber": "+16502396646",
        },
        "fbAdParams": {
            "eventID": "586718a7-e342-4210-88b9-280e6cb3a836",
            "pixelId": [
                "268933192948110",
            ],
            "fbBrowserId": "fb.1.1769653368885.141808310869967644",
            "externalId": "b7090865-489e-4861-9aa3-d7760e80ee16",
            "eventSourceUrl": "https://hui.staging.pear.us/lury-merchant/post/300-orders-automation",
        },
    }, skip_notifications=False, token='access_token')
    # assertion 24.assertion: responseJson equal success
    expect(_resp24).json('$.message').equals('success')
    # step 25: PUT setting the event status as Completed
    _resp25 = ctx.api.events.by_dup_event_id(body={
    'id': '{{dup_event_id}}',
    'title': '{{event_title}}',
    'curatorId': '{{catalog_id}}',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2053-04-17T05:00:00.000Z',
    'endDate': None,
    'venue': 'Instagram Live, Zoom, In-person',
    'location': '789 River East Art Center Promenade, Chicago, Illinois, USA',
    'status': 'COMPLETED',
    'isTaxEnabled': True,
    'taxConfig': {
        'customTaxRate': 10,
        'calculationType': 'CUSTOM',
        'configUpdatedAt': '2026-08-14T02:04:30.036Z',
    },
    'mediaTextConfig': {
        'headline': 'Missed our last event?',
        'subtitle': "Here's a lil recap of our last event👇",
        'align': 'center',
    },
    'poster': {
        'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
        'width': 3072,
        'height': 2048,
        'position': 0,
        'mediaType': 'IMAGE',
        'mediaDuration': 0,
    },
    'startDateDisplay': '2053-04-17',
    'note': 'linda note',
    'timezone': {
        'timeZoneId': 'America/Chicago',
        'timeZoneName': 'Central Daylight Time',
        'dstOffset': 3600,
        'rawOffset': -21600,
    },
    'isAddressRevealEnabled': False,
    'messageInfo': {
        'smsMaxLimit': 3,
        'emailMaxLimit': 5,
        'cooldownMinutes': 15,
    },
    'platform': 'PEAR',
    'creationStep': 'COMPLETED',
    'extraInfo': None,
    'locationDetails': {
        'city': 'Chicago',
        'line1': '789 River East Art Center Promenade',
        'line2': None,
        'state': 'IL',
        'country': 'US',
        'placeId': None,
        'zipcode': None,
        'stateName': 'Illinois',
        'stripeLocationId': None,
    },
    'country': 'US',
    'state': 'IL',
    'autoReplace': True,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'autoPayLineupStatus': 'PENDING',
    'showFeesBreakdown': False,
    'showBuyerInfoOnVenueMap': False,
    'venueMapId': None,
    'ticketHubInfo': None,
    'readOnlyFields': [],
    'medias': [],
    'tickets': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
                    'name': 'Title',
                    'position': 1,
                    'values': [
                        'Default Title',
                    ],
                    'images': [
                        {
                            'value': 'Default Title',
                            'imageId': None,
                        },
                    ],
                },
            ],
            'variants': [
                {
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_CANCELED',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
            'copyFromId': '{{productId}}',
        },
    ],
    'lineup': [
        {
            'title': 'lineup',
            'introduction': '001',
            'poster': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762935019/uploaded_images/wc8wuj2boch4k7bccjgf',
                'width': 160,
                'height': 160,
                'position': 0,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'isHeadliner': False,
            'order': 0,
            'isPaymentAfterEventEnabled': False,
            'id': 'ae6d0a8a-221b-4bec-8ada-f2fea16b4443',
        },
    ],
    'eventProducts': [],
    'products': [
        {
            'id': '{{productId}}',
            'title': 'ticket on hold',
            'listingType': 'TICKET',
            'status': 'ACTIVE',
            'coverImage': {
                'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                'width': 3072,
                'height': 2048,
                'mediaSrc': None,
                'mediaType': 'IMAGE',
                'mediaDuration': 0,
            },
            'inventoryQuantity': 10,
            'soldQuantity': 0,
            'isInventoryQuantityUnlimited': False,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><br></p>',
            'images': [
                {
                    'id': 'c46b0869-dd26-44b4-af2f-1208626a74a9',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 0,
                    'productId': '{{productId}}',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': None,
                },
            ],
            'options': [
                {
                    'id': '{{shipping_option_id}}',
                    'remote_id': None,
                    'productId': '{{productId}}',
                    'name': 'Title',
                    'position': 1,
                    'values': [
                        'Default Title',
                    ],
                    'images': [
                        {
                            'value': 'Default Title',
                            'imageId': None,
                        },
                    ],
                },
            ],
            'variants': [
                {
                    'id': '{{merchantProductVariantId}}',
                    'remote_id': None,
                    'createdAt': '2026-08-14T02:04:30.452Z',
                    'updatedAt': '2026-08-14T02:04:30.452Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'isInventoryQuantityUnlimited': False,
                    'inventoryQuantity': 10,
                    'inventoryQuantityOriginal': 10,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '{{productId}}',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': 'lb',
                    'platform': None,
                    'fees': 0,
                    'transactionFee': {
                        'customFee': 0,
                        'platformFee': 0,
                        'customFeeBreakdown': {},
                        'transactionItemFee': 0,
                    },
                    'ticketPrice': 0,
                    'isMinPurchaseQuantityEnabled': False,
                    'minPurchaseQuantity': None,
                    'isMaxPurchaseQuantityEnabled': False,
                    'maxPurchaseQuantity': None,
                    'isPackSizeEnabled': False,
                    'packSize': None,
                    'transactionFeeConfig': None,
                    'transactionFeeRebateConfig': None,
                },
            ],
            'merchantId': '{{catalog_id}}',
            'createdAt': '2026-08-14T02:04:30.452Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_CANCELED',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'overrideEventCustomFee': False,
            'transactionCustomFeeConfig': None,
            'thirdPartyDeliveryMessage': None,
            'ticketType': 'TICKET_TYPE_STANDARD',
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'isVenueUnitEnabled': False,
            'useEventPosterAsCover': True,
            'readOnlyFields': [],
            'urlAlias': '7vwa9v',
            'taxEnable': True,
            'taxJarCategory': '',
            'productFormId': None,
            'isPlatformFeeConfigOutdated': False,
        },
    ],
    'statistics': {
        'totalAvailableTickets': 10,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
        'totalTickets': 10,
        'totalMerch': 0,
        'totalSoldMerch': 0,
        'totalAvailableMerch': 0,
        'totalRedeemedMerch': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': True,
    'ignoreEndTime': True,
    'posterBackend': [
        {
            'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
            'width': 3072,
            'height': 2048,
            'position': 0,
            'mediaType': 'IMAGE',
            'mediaDuration': 0,
        },
    ],
    'customFeeConfig': {
        'isEnabled': True,
        'items': [
            {
                'title': 'custom fee',
                'unitFixedFee': 0,
                'unitPercentageFee': 0.1,
            },
        ],
    },
    'allowAutoComplete': True,
    'styleSettings': {
        'template': 'ClearSky',
        'themeName': 'MidnightGlow',
        'layout': {
            'pageHeader': {
                'style': 'DEDICATED_HEADER_BAR',
                'displayText': 'SHOP_NAME',
                'height': 'MEDIUM',
            },
            'productBanner': {
                'ctaButton': 'VIEW_PRODUCT',
                'display': 'HIDE',
            },
        },
        'fontFamily': 'Inter',
        'color': '#FFFFFF',
        'backgroundColor': '#000000',
        'borderColor': '#000000',
        'dividerColor': '#5D5D5D',
        'secondaryTextColor': '#E0E0E0',
        'announcementCarousel': {
            'color': '#000000',
            'backgroundColor': '#F6CA7C',
        },
        'title': {
            'color': '#F6CA7C',
            'fontFamily': 'Inter',
            'fontSize': 24,
            'fontWeight': 700,
        },
        'columnTitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'subtitle': {
            'fontFamily': 'Inter',
            'fontSize': 20,
            'fontWeight': 400,
            'color': '#FFFFFF',
        },
        'button': {
            'backgroundColor': '#F6CA7C',
            'color': '#000000',
            'borderColor': '#000000',
            'borderRadius': 0,
            'boxShadow': 'none',
            'fontSize': 16,
            'fontWeight': 400,
        },
        'secondaryButton': {
            'fontSize': 16,
            'fontWeight': 400,
            'color': '#FFFFFF',
            'borderColor': '#F6CA7C',
            'borderRadius': 0,
            'boxShadow': 'none',
        },
        'textButton': {
            'fontSize': 16,
            'fontWeight': 700,
            'color': '#FFFFFF',
        },
        'selectButton': {
            'borderColor': '#000000',
        },
        'relatedLink': {
            'borderRadius': 0,
            'color': '#000000 ',
            'borderColor': '#0000',
            'backgroundColor': '#FAFAFA',
        },
        'featuredProducts': {
            'borderRadius': 0,
            'backgroundColor': '#000000',
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 14,
                'fontWeight': 400,
                'color': '#FFFFFF',
            },
        },
        'product': {
            'backgroundColor': '#000000',
            'borderRadius': 0,
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
        },
        'discount': {
            'backgroundColor': '#D32A09',
            'color': '#FFFFFF',
            'priceColor': '#FFFFFF',
        },
        'freeShipping': {
            'backgroundColor': '#EBF5EF',
            'color': '#268E46',
        },
        'starRatingColor': '#FAAF03',
        'layoutFeatureCard': {
            'title': {
                'fontFamily': 'Inter',
                'fontSize': 16,
                'fontWeight': 700,
                'color': '#FFFFFF',
            },
            'color': '#FFFFFF',
            'secondaryTextColor': '#E0E0E0',
            'button': {
                'backgroundColor': '#F6CA7C',
                'color': '#000000',
            },
        },
        'lineupBanner': {
            'titleText': '#FFFFFF',
            'descriptionText': '#E0E0E0',
        },
        'eventInfoBanner': {
            'text': '#FFFFFF',
            'secondaryText': '#E0E0E0',
        },
        'eventDescription': {
            'text': '#E0E0E0',
            'title': '#FFFFFF',
        },
        'featuredProduct': {
            'cover': {
                'borderRadius': 0,
            },
        },
        'recentUsedColors': [
            '#ffffff',
        ],
    },
}, params={'skipFeesCheck': 'true'}, token='yuxiao999_token')
    # assertion 25.assertion: responseJson equal COMPLETED
    expect(_resp25).json('$.data.status').equals('COMPLETED')
    # step 26: PATCH admin update the event status from complete to upcoming failed if exist order
    _resp26 = ctx.api.admin.events_by_dup_event_id(body={
        "status": "UPCOMING",
    }, token='admin_token')
    # assertion 26.assertion: responseJson equal 400
    expect(_resp26).json('$.code').equals('400')
    # assertion 26.assertion: responseJson equal Cannot revert an event that has sales.
    expect(_resp26).json('$.message').equals('Cannot revert an event that has sales.')
    # step 27: DELETE delete the event
    _resp27 = ctx.api.events.by_event_id(body=None, token='yuxiao999_token', path_vars={'event_id': '{{dup_event_id}}'})
