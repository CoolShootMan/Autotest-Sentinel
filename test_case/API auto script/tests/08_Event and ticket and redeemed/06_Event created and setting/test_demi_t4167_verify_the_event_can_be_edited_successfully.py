"""Migrated from Apifox case #7570770. Source folder: Event and ticket and redeemed/Event created and setting."""
# Apifox Case ID: 7570770  (traceability only — not needed to run)
NAME = "Verify the event can be edited successfully"
TAGS = ["p0", "event_and_ticket_and_redeemed_event_created_and_setting", "suite:linda"]
PRIORITY = 0


CASE_ID = 7570770
ENV_NAME = "Release"

# --- step 1: Get Partner xuan22 token ---
# post[extractor]: {"variableName": "xuan22_token", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.token", "extractSettings": {"expression": "$.data.token", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 2: List events ---
# post[customScript]: // 配置项：抽离匹配关键词，便于后续修改
# post: const MATCH_TITLE = "demi test event auto";
# post: const MATCH_STATUS = "UPCOMING";
# post: 
# post: // 1. 安全解析JSON响应体（防止解析失败导致脚本崩溃）
# post: let responseData = {};
# post: try {
# post:     responseData = pm.response.json();
# post: } catch (parseError) {
# post:     console.error("❌ 响应体解析失败（非合法JSON）：", parseError.message);
# post:     pm.environment.unset("targetEventId"); // 清空旧变量
# post:     return; // 终止脚本
# post: }
# post: 
# post: // 2. 安全获取items数组（多层可选链，兼容接口返回结构变化）
# post: const eventItems = responseData?.data?.items || [];
# post: console.log(`📥 接口返回事件总数：${eventItems.length}`);
# post: 
# post: // 3. 筛选逻辑：title包含指定字符串 + status严格等于UPCOMING
# post: // 用find高效查找第一个匹配项，同时兼容title/status字段不存在的情况
# post: const targetItem = eventItems.find(item => {
# post:     // 标题包含关键词（非严格匹配）+ 状态严格匹配UPCOMING
# post:     const isTitleMatch = item?.title?.includes(MATCH_TITLE);
# post:     const isStatusMatch = item?.status === MATCH_STATUS;
# post:     return isTitleMatch && isStatusMatch;
# post: });
# post: 
# post: // 4. 结果处理：日志反馈 + 环境变量管理
# post: if (targetItem) {
# post:     const targetEventId = targetItem.id;
# post:     console.log(`✅ 找到符合条件的事件：`);
# post:     console.log(`   - ID：${targetEventId}`);
# post:     console.log(`   - 标题：${targetItem.title}`);
# post:     console.log(`   - 状态：${targetItem.status}`);
# post:     pm.environment.set("targetEventId", targetEventId); // 存入环境变量
# post: } else {
# post:     console.log(`❌ 未找到符合条件的事件（title包含"${MATCH_TITLE}" 且 status="${MATCH_STATUS}"）`);
# post:     // 可选：输出所有事件的title/status，便于调试
# post:     console.log(`💡 所有事件的title/status列表：`);
# post:     eventItems.forEach((item, index) => {
# post:         console.log(`   [${index+1}] 标题：${item?.title || "无"} | 状态：${item?.status || "无"}`);
# post:     });
# post:     pm.environment.unset("targetEventId"); // 清空旧的无效ID
# post: }
# --- step 3: 4d1e7107-3451-4dda-9f87-39a9782188e2 ---
# pre: // 1. 定义基础标题（你当前的title值）
# pre: const baseTitle = "demi test event auto update";
# pre: 
# pre: // 2. 生成随机数（示例：4位固定长度，避免长度不一致）
# pre: function getRandomNum(length = 4) {
# pre:   const random = Math.floor(Math.random() * Math.pow(10, length));
# pre:   return random.toString().padStart(length, "0"); // 补零，比如生成5→0005
# pre: }
# pre: 
# pre: // 3. 拼接带随机数的完整标题
# pre: const randomNum = getRandomNum();
# pre: const updatedTitle = `${baseTitle} ${randomNum}`;
# pre: 
# pre: // 4. 存入环境变量（后续请求Body直接引用这个变量）
# pre: pm.environment.set("updatedEventTitle", updatedTitle);
# pre: 
# pre: // 日志打印（调试用）
# pre: console.log(`✅ 生成带随机数的标题：${updatedTitle}`);
# --- step 4: Check the event details updated ---
# post[customScript]: // ========== 后置脚本：动态验证随机生成的title更新成功 ==========
# post: try {
# post:     // 1. 读取前置脚本生成的环境变量（动态获取目标title）
# post:     const targetTitle = pm.environment.get("updatedEventTitle");
# post:     
# post:     // 校验环境变量是否存在（避免前置脚本未执行/生成失败）
# post:     if (!targetTitle) {
# post:         throw new Error(`环境变量 "updatedEventTitle" 未找到！请检查前置脚本是否正常执行`);
# post:     }
# post:     console.log(`📌 开始验证目标title：${targetTitle}`);
# post: 
# post:     // 2. 安全解析接口响应数据
# post:     const responseData = pm.response.json();
# post:     console.log("✅ 响应数据解析成功，共返回事件数：", responseData?.data?.items?.length || 0);
# post: 
# post:     // 3. 核心断言：分步骤校验响应合法性
# post:     // 3.1 校验响应状态码
# post:     pm.test("接口响应状态码为200", () => {
# post:         pm.response.to.have.status(200);
# post:     });
# post: 
# post:     // 3.2 校验响应结构完整性
# post:     pm.test("响应结构符合预期（包含data.items数组）", () => {
# post:         pm.expect(responseData).to.have.property("data");
# post:         pm.expect(responseData.data).to.have.property("items");
# post:         pm.expect(responseData.data.items).to.be.an("array");
# post:     });
# post: 
# post:     // 3.3 校验目标title是否存在于响应中
# post:     const eventItems = responseData.data.items || [];
# post:     const matchedItem = eventItems.find(item => item?.title === targetTitle); // 精确匹配title
# post: 
# post:     pm.test(`验证随机生成的title【${targetTitle}】更新成功`, () => {
# post:         pm.expect(matchedItem).to.not.be.undefined; // 断言找到匹配项
# post:     });
# post: 
# post:     // 4. 输出详细验证结果（便于调试）
# post:     if (matchedItem) {
# post:         console.log(`✅ 验证成功！`);
# post:         console.log(`   - 目标title：${targetTitle}`);
# post:         console.log(`   - 对应事件ID：${matchedItem.id}`);
# post:         console.log(`   - 事件状态：${matchedItem.status}`);
# post:         // 可选：将匹配到的事件ID存入环境变量，供后续接口使用
# post:         pm.environment.set("matchedEventId", matchedItem.id);
# post:     }
# post: 
# post: } catch (error) {
# post:     // 异常捕获：统一处理脚本执行错误/环境变量缺失
# post:     console.error(`❌ 验证失败：${error.message}`);
# post:     // 断言失败，让接口运行结果标红提示
# post:     pm.test("脚本执行正常且验证通过", () => {
# post:         pm.expect(error).to.be.undefined;
# post:     });
# post: }




import json

from core.assertions import expect

def test_demi_t4167_verify_the_event_can_be_edited_successfully(ctx):
    """Apifox case #7570770: Demi_T4167_Verify_the_event_can_be_edited_successfully"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Get Partner xuan22 token
    _resp1 = ctx.api.auth.sign_in(body={
        "email": "xuan.ext+22@1m.app",
        "password": "fB5A002Dc16AbF5Cd096dA6Aa66F3050",
    })
    # extractor: xuan22_token = $.data.token
    ctx.extract('xuan22_token', _resp1, '$.data.token')
    # step 2: List events
    _resp2 = ctx.api.events.list(params={'pageNumber': 1, 'pageSize': 50}, app_headers=False, token='xuan22_token')
    # === 断言/提取（由Apifox customScript翻译）===
    _j = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    assert _resp2.status_code == 200, f"step2 status != 200, got {_resp2.status_code}"
    _items2 = (_j.get('data') or {}).get('items') or []
    _target2 = next((it for it in _items2 if 'demi test event auto' in (it.get('title') or '') and it.get('status') == 'UPCOMING'), None)
    assert _target2 is not None, "未找到 title 包含 'demi test event auto' 且 status=UPCOMING 的事件"
    vars['targetEventId'] = _target2['id']
    # === pre-script（由Apifox customScript翻译）：生成随机 updatedEventTitle ===
    import random as _rnd
    _rand_num = str(_rnd.randint(0, 9999)).zfill(4)
    vars['updatedEventTitle'] = 'demi test event auto update ' + _rand_num
    # step 3: 4d1e7107-3451-4dda-9f87-39a9782188e2
    _resp3 = ctx.api.events.by_dup_event_id(body={
    'id': '{{targetEventId}}',
    'title': '{{updatedEventTitle}}',
    'curatorId': '9d0083c6-dd34-4679-8780-73b8c5c46441',
    'description': '',
    'descriptionBodyJson': '{"root":{"children":[{"children":[],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":"","style":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
    'startDate': '2026-12-05T11:05:00.000Z',
    'endDate': None,
    'venue': 'london',
    'location': 'Canada Line - SkyTrain, Metro Vancouver, BC, Canada',
    'status': 'UPCOMING',
    'isTaxEnabled': False,
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
    'allowAutoComplete': True,
    'startDateDisplay': '2026-12-05 03:05',
    'note': '',
    'timezone': {
        'timeZoneId': 'America/Vancouver',
        'timeZoneName': 'Pacific Standard Time',
        'dstOffset': 0,
        'rawOffset': -28800,
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
        'line1': 'Canada Line - SkyTrain',
        'city': '',
        'state': 'British Columbia',
        'stateName': 'British Columbia',
        'zipcode': '',
        'country': 'Canada',
        'placeId': 'EjNDYW5hZGEgTGluZSAtIFNreVRyYWluLCBNZXRybyBWYW5jb3V2ZXIsIEJDLCBDYW5hZGEiLiosChQKEgl7kAKs3XSGVBHQ0p4DNxpJ8RIUChIJpd_5BZDOYlQRpvz0npdsnM4',
    },
    'country': 'US',
    'state': 'CA',
    'autoReplace': False,
    'lineupTransactionId': None,
    'lineupTransactionStatus': None,
    'medias': [],
    'tickets': [
        {
            'id': 'b142ff3c-60b6-407f-a37c-cd678a3182ad',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': 'bf678663-3624-46c3-862e-e65b346ba22b',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': 'b142ff3c-60b6-407f-a37c-cd678a3182ad',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': 'c3688784-fc22-4f5d-8c5b-c8042b2367e7',
                    'remote_id': None,
                    'productId': 'b142ff3c-60b6-407f-a37c-cd678a3182ad',
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
                    'id': 'e5bface9-695a-4034-a872-90b744d4938f',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': 'b142ff3c-60b6-407f-a37c-cd678a3182ad',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.386Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 'cmnu3n',
            'copyFromId': 'b142ff3c-60b6-407f-a37c-cd678a3182ad',
        },
        {
            'id': '12574b1d-fc29-42eb-9021-5dfcd4857c30',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': 'ebcae8d4-97fa-4c92-9ed3-220f1e0eb6ae',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': '12574b1d-fc29-42eb-9021-5dfcd4857c30',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': 'e120472c-4205-4f02-b32c-5037ed99f86d',
                    'remote_id': None,
                    'productId': '12574b1d-fc29-42eb-9021-5dfcd4857c30',
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
                    'id': '9353cc0c-e8ce-40fb-a3ba-896fc32eb603',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '12574b1d-fc29-42eb-9021-5dfcd4857c30',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.385Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 'pbmy2w',
            'copyFromId': '12574b1d-fc29-42eb-9021-5dfcd4857c30',
        },
        {
            'id': '842b23b9-a13e-474f-9fab-3080d52020de',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': '057367cb-4753-468e-a70c-5c5560bdaa14',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': '842b23b9-a13e-474f-9fab-3080d52020de',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': '3f816fa3-b139-4fc8-a40a-87db88e4fd7f',
                    'remote_id': None,
                    'productId': '842b23b9-a13e-474f-9fab-3080d52020de',
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
                    'id': 'c0b87efd-a7c7-4eaa-a373-133afcfe4441',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '842b23b9-a13e-474f-9fab-3080d52020de',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.384Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 'n0zo4o',
            'copyFromId': '842b23b9-a13e-474f-9fab-3080d52020de',
        },
        {
            'id': '23acc0d0-ea31-48ab-99e4-40d2efff1772',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': '80be2962-bf0a-414a-8a1e-965b2f5d7a23',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': '23acc0d0-ea31-48ab-99e4-40d2efff1772',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': '91e84ed3-70fd-4ca4-bd8f-525a009198f7',
                    'remote_id': None,
                    'productId': '23acc0d0-ea31-48ab-99e4-40d2efff1772',
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
                    'id': '13852e04-c2bb-4777-88a7-2b2dc4435fe7',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '23acc0d0-ea31-48ab-99e4-40d2efff1772',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.383Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 't55f7a',
            'copyFromId': '23acc0d0-ea31-48ab-99e4-40d2efff1772',
        },
        {
            'id': 'c54d5fa5-f2ae-40e7-8b2e-ba50cc5b69de',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': '69d2b7b0-b2c6-4efa-8c9d-b86edeb8fb71',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': 'c54d5fa5-f2ae-40e7-8b2e-ba50cc5b69de',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': '2832c6a1-0734-4d2c-a91e-b85e6076df25',
                    'remote_id': None,
                    'productId': 'c54d5fa5-f2ae-40e7-8b2e-ba50cc5b69de',
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
                    'id': '72e60a75-67ac-4497-a95e-abb4b20c55e2',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': 'c54d5fa5-f2ae-40e7-8b2e-ba50cc5b69de',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.382Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 'lrjrkx',
            'copyFromId': 'c54d5fa5-f2ae-40e7-8b2e-ba50cc5b69de',
        },
        {
            'id': '3f389745-d0b0-4293-988e-44434de31fae',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': 'e5984b0f-c748-4076-b5ef-23d0f178bfbf',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': '3f389745-d0b0-4293-988e-44434de31fae',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': '987307bb-a226-4fa8-891f-6b0f8cf9e0ee',
                    'remote_id': None,
                    'productId': '3f389745-d0b0-4293-988e-44434de31fae',
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
                    'id': '76cfcbbc-85f2-42b8-9e0c-37d3a9ebcb0d',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': '3f389745-d0b0-4293-988e-44434de31fae',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.381Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 'ij6om5',
            'copyFromId': '3f389745-d0b0-4293-988e-44434de31fae',
        },
        {
            'id': 'ed9d1556-c1ca-4a82-a3d4-212664fb14fd',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': '7c0ca2d7-a983-4c1b-b215-f93aad9fe79a',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': 'ed9d1556-c1ca-4a82-a3d4-212664fb14fd',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': '404c4717-1327-47d5-99a6-8a958a97493f',
                    'remote_id': None,
                    'productId': 'ed9d1556-c1ca-4a82-a3d4-212664fb14fd',
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
                    'id': '5222cb70-3fb7-4b1c-96ee-5144a71d6e25',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': 'ed9d1556-c1ca-4a82-a3d4-212664fb14fd',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.380Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 'cs3nga',
            'copyFromId': 'ed9d1556-c1ca-4a82-a3d4-212664fb14fd',
        },
        {
            'id': 'c0652bb7-9eeb-4c42-8b01-40b6e284b193',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': '20b9fafc-f7f2-4ef6-8c40-afb6a541674b',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': 'c0652bb7-9eeb-4c42-8b01-40b6e284b193',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': '25398242-7501-4942-bd6d-ee4344cdd85e',
                    'remote_id': None,
                    'productId': 'c0652bb7-9eeb-4c42-8b01-40b6e284b193',
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
                    'id': 'd9eb9344-6bbe-49f8-a24c-bbd9e7e39184',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': 'c0652bb7-9eeb-4c42-8b01-40b6e284b193',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.379Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 'c30ntw',
            'copyFromId': 'c0652bb7-9eeb-4c42-8b01-40b6e284b193',
        },
        {
            'id': 'c302a977-dcef-4b9f-87be-db14cce945a2',
            'title': '5654',
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
            'inventoryQuantity': 1,
            'soldQuantity': 0,
            'priceMin': 0,
            'priceMax': 0,
            'bodyJson': '{"root":{"children":[{"children":[{"detail":0,"format":0,"mode":"normal","style":"","text":"456","type":"extended-text","version":1}],"direction":"ltr","format":"","indent":0,"type":"katana-paragraph","version":1,"textFormat":0,"textStyle":""}],"direction":null,"format":"","indent":0,"type":"root","version":1}}',
            'bodyHtml': '<p class="katana__paragraph katana__paragraph--align-left" dir="ltr"><span style="white-space: pre-wrap;">456</span></p>',
            'images': [
                {
                    'id': '2258554d-e2fe-4abc-a4a5-c7056b52fb09',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'height': 2048,
                    'width': 3072,
                    'position': 1,
                    'productId': 'c302a977-dcef-4b9f-87be-db14cce945a2',
                    'src': 'https://res.cloudinary.com/dr9io1zjv/v1762842604/uploaded_images/s47jfs33fgz3do4wvrxz.png',
                    'variantIds': [],
                    'mediaType': 'IMAGE',
                    'mediaSrc': None,
                    'mediaDuration': 0,
                    'contributedBy': 3,
                    'contributorId': None,
                    'productImageType': 'PRODUCT',
                    'source': 'EVENT',
                },
            ],
            'options': [
                {
                    'id': 'b93b8c81-402a-4018-b51e-efd6357d296e',
                    'remote_id': None,
                    'productId': 'c302a977-dcef-4b9f-87be-db14cce945a2',
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
                    'id': 'cdcf8f64-6c86-4061-a3ab-2765157fa78e',
                    'remote_id': None,
                    'createdAt': '2026-01-30T04:02:06.574Z',
                    'updatedAt': '2026-01-30T04:02:06.574Z',
                    'compareAtPrice': None,
                    'fulfillmentService': 'manual',
                    'grams': 0,
                    'imageId': None,
                    'imageIds': [],
                    'inventoryItemId': None,
                    'inventoryManagement': 'Pear',
                    'inventoryPolicy': 'DENY',
                    'inventoryQuantity': 1,
                    'inventoryQuantityOriginal': 1,
                    'soldQuantity': 0,
                    'option': {
                        'option1': 'Default Title',
                    },
                    'position': 1,
                    'price': '0',
                    'priceAnchor': '0',
                    'priceImported': '0.00',
                    'productId': 'c302a977-dcef-4b9f-87be-db14cce945a2',
                    'sku': '',
                    'taxCode': None,
                    'taxable': True,
                    'title': 'Default Title',
                    'weight': None,
                    'weightUnit': None,
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
                },
            ],
            'merchantId': '2476af1f-8d82-49c9-961b-48faba3b3d26',
            'createdAt': '2026-01-30T04:02:06.378Z',
            'lifecycleStatus': 'LIFECYCLE_STATUS_NORMAL',
            'stopSellingAfterDisplay': '',
            'deliveryMethod': 'QR_CODE',
            'isMultipleDaysPassEnabled': False,
            'multipleDaysPass': None,
            'overrideEventTax': False,
            'customTaxRate': None,
            'thirdPartyDeliveryMessage': None,
            'excludeFromPostSync': False,
            'isExpirationEnabled': False,
            'expirationTime': None,
            'expirationTimeDisplay': None,
            'urlAlias': 'zxv0tx',
            'copyFromId': 'c302a977-dcef-4b9f-87be-db14cce945a2',
        },
    ],
    'lineup': [],
    'eventProducts': [],
    'statistics': {
        'totalAvailableTickets': 9,
        'totalSoldTickets': 0,
        'totalRedeemedTickets': 0,
    },
    'hasPaidSales': False,
    'accessType': 'OWNER',
    'ignoreStartTime': False,
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
}, token='xuan22_token', path_vars={'dup_event_id': '{{targetEventId}}'})
    # step 4: Check the event details updated
    _resp4 = ctx.api.events.list(params={'pageNumber': 1, 'pageSize': 50}, app_headers=False, token='xuan22_token')
    # === 断言（由Apifox customScript翻译）===
    assert _resp4.status_code == 200, f"step4 status != 200, got {_resp4.status_code}"
    _j4 = _resp4.json() if _resp4.headers.get('content-type','').startswith('application/json') else {}
    assert 'data' in _j4, "响应缺少 data"
    _items4 = (_j4.get('data') or {}).get('items')
    assert isinstance(_items4, list), "data.items 不是数组"
    _matched4 = next((it for it in _items4 if it.get('title') == vars['updatedEventTitle']), None)
    assert _matched4 is not None, "未找到 title 为 [{}] 的事件".format(vars['updatedEventTitle'])
    vars['matchedEventId'] = _matched4['id']
