"""Migrated from Apifox case #7635562. Source folder: Module."""
# Apifox Case ID: 7635562  (traceability only — not needed to run)
NAME = "Verify adding music link types in the storefront modules"
TAGS = ["p0", "module", "suite:linda"]
PRIORITY = 0


CASE_ID = 7635562
ENV_NAME = "Release"

# --- step 1: 7f06967e-944b-45ca-a527-386b2b8319fa ---
# pre: // 1. 生成动态title（Automation music + 5位随机数）
# pre: const randomNum = Math.floor(Math.random() * 90000) + 10000;
# pre: const dynamicMusicTitle = `Automation music ${randomNum}`;
# pre: 
# pre: // 2. 强制存储到环境变量（确保作用域是当前环境）
# pre: pm.environment.set("dynamicMusicTitle", dynamicMusicTitle);
# pre: console.log("【前置脚本】已生成环境变量：dynamicMusicTitle =", dynamicMusicTitle);
# pre: 
# pre: // 3. 主动更新请求体的title（避免APIFOX变量解析延迟）
# pre: let requestBody = JSON.parse(pm.request.body.raw);
# pre: requestBody.title = dynamicMusicTitle; // 直接赋值（也可保留{{变量}}，但这里强制替换确保生效）
# pre: pm.request.body.raw = JSON.stringify(requestBody, null, 2);
# pre: console.log("【前置脚本】请求体已更新title：", requestBody.title);
# post[customScript]: // ========== 1. 配置校验基准（可根据需求调整） ==========
# post: const verifyConfig = {
# post:     expectedCode: 200,
# post:     expectedMessage: "success",
# post:     expectedType: "LINK",
# post:     // expectedLinkType: "null",
# post:     titlePrefix: "Automation music ", // 动态title的固定前缀
# post:     envVarIdName: "dynamicMusicLinkId" // 存储ID的环境变量名
# post: };
# post: 
# post: // ========== 2. 解析响应数据 & 基础断言 ==========
# post: const responseData = pm.response.json();
# post: console.log("【原始响应】返回数据:\n", JSON.stringify(responseData, null, 2));
# post: 
# post: // 断言1：接口响应状态码为200（核心成功标志）
# post: pm.test("接口响应状态码为200", function () {
# post:     pm.expect(responseData.code).to.equal(verifyConfig.expectedCode, `期望code=${verifyConfig.expectedCode}，实际=${responseData.code}`);
# post: });
# post: 
# post: // 断言2：接口业务状态为success
# post: pm.test("接口业务状态为success", function () {
# post:     pm.expect(responseData.message).to.equal(verifyConfig.expectedMessage, `期望message=${verifyConfig.expectedMessage}，实际=${responseData.message}`);
# post: });
# post: 
# post: // ========== 3. 校验核心字段结构 & 取值 ==========
# post: // 断言3：响应包含有效data字段
# post: pm.test("响应包含核心data字段", function () {
# post:     pm.expect(responseData.data).to.exist.and.not.be.empty, "响应缺少data字段或data为空";
# post: });
# post: 
# post: const data = responseData.data;
# post: if (data) {
# post:     // 断言4：type等于LINK
# post:     pm.test("type字段值为LINK", function () {
# post:         pm.expect(data.type).to.equal(verifyConfig.expectedType, `期望type=${verifyConfig.expectedType}，实际=${data.type}`);
# post:     });
# post: 
# post:     // // 断言5：linkType等于MUSIC
# post:     // pm.test("linkType字段值为MUSIC", function () {
# post:     //     pm.expect(data.linkType).to.equal(verifyConfig.expectedLinkType, `期望linkType=${verifyConfig.expectedLinkType}，实际=${data.linkType}`);
# post:     // });
# post: 
# post:     // 断言6：title是动态生成的有效格式（Automation music + 随机数）
# post:     pm.test("title为动态生成的有效格式（Automation music + 随机数）", function () {
# post:         // 正则匹配：以"Automation music "开头，后跟1个及以上数字（匹配随机数）
# post:         const titleRegex = new RegExp(`^${verifyConfig.titlePrefix}\\d+$`);
# post:         pm.expect(data.title).to.match(titleRegex, `title格式错误，期望以"${verifyConfig.titlePrefix}"开头且后跟数字，实际=${data.title}`);
# post:     });
# post: 
# post:     // ========== 4. 提取并存储data.id到环境变量 ==========
# post:     pm.test("提取data.id并存储到环境变量", function () {
# post:         pm.expect(data.id).to.exist.and.not.be.empty, "data.id为空或不存在，无法存储";
# post:         pm.environment.set(verifyConfig.envVarIdName, data.id);
# post:         console.log(`【环境变量已设置】${verifyConfig.envVarIdName} = ${pm.environment.get(verifyConfig.envVarIdName)}`);
# post:     });
# post: }
# post: 
# post: // ========== 5. 结构化日志输出（便于调试） ==========
# post: console.log(`
# post: =====================================================
# post:             音乐链接配置校验 & ID提取总结
# post: =====================================================
# post: ✅ 接口基础断言：code=${responseData.code}，message=${responseData.message}
# post: ✅ type校验：${data?.type === verifyConfig.expectedType ? "通过" : "失败"}
# post: ✅ linkType校验：${data?.linkType === verifyConfig.expectedLinkType ? "通过" : "失败"}
# post: ✅ title格式校验：${data?.title?.startsWith(verifyConfig.titlePrefix) && /\\d+$/.test(data?.title) ? "通过" : "失败"}
# post: 📌 提取的ID（${verifyConfig.envVarIdName}）：${pm.environment.get(verifyConfig.envVarIdName) || "无"}
# post: =====================================================
# post: `);
# --- step 2: 4ad69ccd-e26c-42a6-b635-ee54c1498ef5 ---
# pre: // ========== 1. 动态生成核心变量（贴合传参格式） ==========
# pre: // 动态title：music + 随机数（确保唯一，匹配示例格式）
# pre: const randomNum = Math.floor(Math.random() * 90000) + 10000;
# pre: const dynamicTitle = `music_${randomNum}`; 
# pre: 
# pre: // 动态timeKey：当前时间戳（毫秒，匹配示例格式）
# pre: const dynamicTimeKey = Date.now(); 
# pre: 
# pre: // 热门歌手（选用当前流媒体平台热度TOP的独立音乐人，匹配真实场景）
# pre: const hotArtist = "Leanna Firestone"; 
# pre: 
# pre: // ========== 2. 扩充全量音乐平台的真实热门链接（规范platform命名+有效src） ==========
# pre: // platform遵循「大写+下划线」规范，src为各平台真实热门歌曲链接，position递增
# pre: const musicServices = [
# pre:   {
# pre:     "platform": "APPLE_MUSIC",
# pre:     "src": "https://music.apple.com/us/album/cruel-summer/1640383474?i=1640383500",
# pre:     "position": 1
# pre:   },
# pre:   {
# pre:     "platform": "ANGHAMI",
# pre:     "src": "https://play.anghami.com/song/177824714",
# pre:     "position": 2
# pre:   },
# pre:   {
# pre:     "platform": "AUDIOMACK",
# pre:     "src": "https://audiomack.com/leanna-firestone/song/samson",
# pre:     "position": 3
# pre:   },
# pre:   {
# pre:     "platform": "BANDCAMP",
# pre:     "src": "https://leannafirestone.bandcamp.com/track/samson",
# pre:     "position": 4
# pre:   },
# pre:   {
# pre:     "platform": "BEATPORT",
# pre:     "src": "https://www.beatport.com/track/cruel-summer/17892345",
# pre:     "position": 5
# pre:   },
# pre:   {
# pre:     "platform": "DEEZER",
# pre:     "src": "https://www.deezer.com/track/1889456789",
# pre:     "position": 6
# pre:   },
# pre:   {
# pre:     "platform": "GAANA",
# pre:     "src": "https://gaana.com/song/samson-12",
# pre:     "position": 7
# pre:   },
# pre:   {
# pre:     "platform": "IHEARTRADIO",
# pre:     "src": "https://www.iheart.com/artist/leanna-firestone-123456/cruel-summer-32145678/",
# pre:     "position": 8
# pre:   },
# pre:   {
# pre:     "platform": "NAPSTER",
# pre:     "src": "https://us.napster.com/song/leanna-firestone/samson",
# pre:     "position": 9
# pre:   },
# pre:   {
# pre:     "platform": "PANDORA",
# pre:     "src": "https://www.pandora.com/artist/leanna-firestone/samson/AL123456789",
# pre:     "position": 10
# pre:   },
# pre:   {
# pre:     "platform": "QOBUZ",
# pre:     "src": "https://www.qobuz.com/us-en/track/samson/1234567890123",
# pre:     "position": 11
# pre:   },
# pre:   {
# pre:     "platform": "SPOTIFY",
# pre:     "src": "https://open.spotify.com/track/3hgl7EQwYP7y9A557Rj9p3",
# pre:     "position": 12
# pre:   },
# pre:   {
# pre:     "platform": "TIDAL",
# pre:     "src": "https://tidal.com/track/123456789",
# pre:     "position": 13
# pre:   },
# pre:   {
# pre:     "platform": "YOUTUBE_MUSIC",
# pre:     "src": "https://music.youtube.com/watch?v=eJ9R3xQ98c0",
# pre:     "position": 14
# pre:   }
# pre: ];
# pre: 
# pre: // ========== 3. 组装完整请求体（严格匹配传参格式） ==========
# pre: const requestBody = {
# pre:   "position": 0, // 固定值，匹配示例
# pre:   "type": "MUSIC", // 固定值，匹配示例
# pre:   "timeKey": dynamicTimeKey, // 动态时间戳
# pre:   "additionalInfo": {
# pre:     "services": musicServices, // 扩充后的全量平台链接
# pre:     "artist": hotArtist // 热门歌手
# pre:   },
# pre:   "title": dynamicTitle, // 动态title
# pre:   "mediaSrc": "https://res.cloudinary.com/dr9io1zjv/v1765509128/uploaded_images/vqesoltctfxgyufqun0t.jpg", // 示例图片链接（可替换为真实封面）
# pre:   "showBelowTitle": false // 固定值，匹配示例
# pre: };
# pre: 
# pre: // ========== 4. 替换请求体（确保格式&值完全生效） ==========
# pre: pm.request.body.raw = JSON.stringify(requestBody, null, 2);
# pre: 
# pre: // ========== 5. 日志输出（便于调试） ==========
# pre: console.log(`【参数填充完成】
# pre: - 动态Title：${dynamicTitle}
# pre: - 动态TimeKey：${dynamicTimeKey}
# pre: - 歌手：${hotArtist}
# pre: - 已扩充${musicServices.length}个音乐平台的真实热门链接
# pre: - 传参格式完全匹配示例结构`);
# post[customScript]: // ========== 1. Configure verification benchmarks ==========
# post: const verifyConfig = {
# post:     expectedCode: 200,
# post:     expectedMessage: "success",
# post:     expectedType: "MUSIC",
# post:     expectedArtist: "Leanna Firestone",
# post:     expectedShowBelowTitle: false,
# post:     expectedPosition: 0,
# post:     minServicesCount: 14,
# post:     titleRegex: /^music_\d+$/,
# post:     envVarIdName: "musicLinkConfigId"
# post: };
# post: 
# post: // ========== 2. Parse response data ==========
# post: const responseData = pm.response.json();
# post: console.log("【Raw Response】Data:\n", JSON.stringify(responseData, null, 2));
# post: const data = responseData.data || {};
# post: const additionalInfo = data.additionalInfo || {};
# post: const services = additionalInfo.services || [];
# post: 
# post: // ========== 3. Core assertions (fixed syntax) ==========
# post: // Assertion 1: Response code is 200
# post: pm.test("Response code is 200 (request successful)", function () {
# post:     pm.expect(responseData.code).to.equal(verifyConfig.expectedCode, 
# post:         `Expected code=${verifyConfig.expectedCode}, actual=${responseData.code}`);
# post: });
# post: 
# post: // Assertion 2: Business status is success
# post: pm.test("Business status is success", function () {
# post:     pm.expect(responseData.message).to.equal(verifyConfig.expectedMessage, 
# post:         `Expected message=${verifyConfig.expectedMessage}, actual=${responseData.message}`);
# post: });
# post: 
# post: 
# post: // Assertion 6: Title format is correct
# post: pm.test("Title format is 'music_+number' (e.g. music_51107)", function () {
# post:     pm.expect(data.title).to.match(verifyConfig.titleRegex, 
# post:         `Title format error: expected ${verifyConfig.titleRegex}, actual=${data.title}`);
# post: });
# post: 
# post: // Assertion 7: Type equals MUSIC
# post: pm.test("Type field is MUSIC", function () {
# post:     pm.expect(data.type).to.equal(verifyConfig.expectedType, 
# post:         `Expected type=${verifyConfig.expectedType}, actual=${data.type}`);
# post: });
# post: 
# post: // Assertion 8: showBelowTitle is false
# post: pm.test("showBelowTitle field is false", function () {
# post:     pm.expect(data.showBelowTitle).to.equal(verifyConfig.expectedShowBelowTitle, 
# post:         `Expected showBelowTitle=${verifyConfig.expectedShowBelowTitle}, actual=${data.showBelowTitle}`);
# post: });
# post: 
# post: // Assertion 9: Position is 0
# post: pm.test("Position field is 0", function () {
# post:     pm.expect(data.position).to.equal(verifyConfig.expectedPosition, 
# post:         `Expected position=${verifyConfig.expectedPosition}, actual=${data.position}`);
# post: });
# post: 
# post: 
# post: 
# post: // Assertion 12: services array length ≥14
# post: pm.test(`services array length ≥${verifyConfig.minServicesCount} (all platforms returned)`, function () {
# post:     pm.expect(services).to.be.an("array").and.have.lengthOf.at.least(verifyConfig.minServicesCount, 
# post:         `services length insufficient: expected ≥${verifyConfig.minServicesCount}, actual=${services.length}`);
# post: });
# post: 
# post: 
# post: 
# post: 
# post: // ========== 4. Structured log ==========
# post: console.log(`
# post: =====================================================
# post:             MUSIC Link Configuration Assertion Summary
# post: =====================================================
# post: ✅ Basic Response: code=${responseData.code}, message=${responseData.message}
# post: ✅ Title Format: ${data.title} (matches 'music_+number')
# post: ✅ Type: ${data.type} (expected MUSIC)
# post: ✅ Artist: ${additionalInfo.artist} (expected Leanna Firestone)
# post: ✅ Services Count: ${services.length} (≥${verifyConfig.minServicesCount})
# post: 📌 Extracted ID (${verifyConfig.envVarIdName}): ${pm.environment.get(verifyConfig.envVarIdName)}
# post: =====================================================
# post: `);
# post[extractor]: {"variableName": "moduleContentId", "variableType": "environment", "subject": "responseJson", "template": "", "expression": "$.data.id", "extractSettings": {"expression": "$.data.id", "continueExtractorSettings": {"isContinueExtractValue": false, "JsonArrayValueIndexValue": ""}}}
# --- step 3: 02b3432c-17c6-4bce-8fc9-01d250e4c238 ---
# post[customScript]: // ========== 1. 配置校验基准（全英文符号） ==========
# post: const verifyConfig = {
# post:     expectedCode: 200,
# post:     expectedMessage: "success",
# post:     expectedOuterType: "LINK",
# post:     expectedLinkType: "MUSIC",
# post:     expectedDirection: "VERTICAL",
# post:     expectedVisible: true,
# post:     outerTitleRegex: /^Automation music \d+$/,
# post:     expectedInnerType: "MUSIC",
# post:     expectedArtist: "Leanna Firestone",
# post:     expectedShowBelowTitle: false,
# post:     expectedInnerPosition: 0,
# post:     envVarOuterIdName: "linkMusicConfigOuterId",
# post:     envVarInnerItemIdName: "linkMusicConfigInnerItemId"
# post: };
# post: 
# post: // ========== 2. 解析响应数据 ==========
# post: const responseData = pm.response.json();
# post: const outerData = responseData.data || {};
# post: const items = outerData.items || [];
# post: const innerItem = items[0] || {};
# post: const innerAdditionalInfo = innerItem.additionalInfo || {};
# post: const innerServices = innerAdditionalInfo.services || [];
# post: 
# post: // ========== 3. 基础响应断言 ==========
# post: // 断言1：响应码200
# post: pm.test("Response code is 200", function () {
# post:     pm.expect(responseData.code).to.equal(verifyConfig.expectedCode, 
# post:         `Expected code=${verifyConfig.expectedCode}, actual=${responseData.code}`);
# post: });
# post: 
# post: // 断言2：业务状态success
# post: pm.test("Business status is success", function () {
# post:     pm.expect(responseData.message).to.equal(verifyConfig.expectedMessage, 
# post:         `Expected message=${verifyConfig.expectedMessage}, actual=${responseData.message}`);
# post: });
# post: 
# post: 
# post: 
# post: // 断言：外层title格式
# post: pm.test("Outer title format is correct", function () {
# post:     pm.expect(outerData.title).to.match(verifyConfig.outerTitleRegex, 
# post:         `Title format error, actual=${outerData.title}`);
# post: });
# post: 
# post: // // 断言：外层type/linkType
# post: // pm.test("Outer type=LINK and linkType=MUSIC", function () {
# post: //     pm.expect(outerData.type).to.equal(verifyConfig.expectedOuterType);
# post: //     pm.expect(outerData.linkType).to.equal(verifyConfig.expectedLinkType);
# post: // });
# post: 
# post: // 断言：外层direction/visible
# post: pm.test("Outer direction=VERTICAL and visible=true", function () {
# post:     pm.expect(outerData.direction).to.equal(verifyConfig.expectedDirection);
# post:     pm.expect(outerData.visible).to.equal(verifyConfig.expectedVisible);
# post: });
# post: 
# post: // ========== 5. items数组断言 ==========
# post: pm.test("Items array has at least 1 element", function () {
# post:     pm.expect(items).to.be.an("array").and.have.lengthOf.at.least(1);
# post: });
# post: 
# post: // // 断言：内层item字段
# post: // pm.test("Inner item fields are valid", function () {
# post: //     pm.expect(innerItem.id).to.exist.and.not.be.empty;
# post: //     pm.expect(innerItem.type).to.equal(verifyConfig.expectedInnerType);
# post: //     pm.expect(innerItem.showBelowTitle).to.equal(verifyConfig.expectedShowBelowTitle);
# post: //     pm.expect(innerItem.position).to.equal(verifyConfig.expectedInnerPosition);
# post: //     pm.environment.set(verifyConfig.envVarInnerItemIdName, innerItem.id);
# post: // });
# post: 
# post: // ========== 6. additionalInfo断言 ==========
# post: pm.test("additionalInfo and artist are valid", function () {
# post:     pm.expect(innerAdditionalInfo).to.exist.and.not.be.empty;
# post:     pm.expect(innerAdditionalInfo.artist).to.equal(verifyConfig.expectedArtist);
# post: });
# post: 
# post: // 断言：services数组
# post: pm.test("Services array elements are valid", function () {
# post:     pm.expect(innerServices).to.be.an("array").and.not.be.empty;
# post:     innerServices.forEach((s, i) => {
# post:         pm.expect(s.platform).to.exist;
# post:         pm.expect(s.src).to.exist;
# post:         pm.expect(s.position).to.be.a("number");
# post:     });
# post: });
# --- step 4: 73a7f755-a3eb-400c-bb7a-15ad1eb9d79a ---




import random
import json
import re

from core.assertions import expect

def test_linda_t4658_verify_adding_music_link_types_in_the_storefront_modules(ctx):
    """Apifox case #7635562: Linda_T4658_Verify_adding_music_link_types_in_the_storefront_modules"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # 动态生成 music title（对应原 Apifox pre-script: Automation music + 5位随机数）
    vars['dynamicTitle'] = 'Automation music ' + str(random.randint(10000, 99999))
    # === Steps ===
    # step 1: 7f06967e-944b-45ca-a527-386b2b8319fa
    _resp1 = ctx.api.storefront.module(body='{\r\n    "type": "LINK",\r\n    "direction": "VERTICAL",\r\n    "linkType": "MUSIC",\r\n    "title": "{{dynamicTitle}}",\r\n    "visible": true\r\n}', token='linda01_token')
    # === 断言/提取（由Apifox customScript翻译）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type','').startswith('application/json') else {}
    assert _j1.get('code') == 200, f"step1 code != 200, got {_j1.get('code')}"
    assert _j1.get('message') == 'success', f"step1 message != success, got {_j1.get('message')}"
    _d1 = _j1.get('data') or {}
    assert _d1, "step1 data 为空"
    assert _d1.get('type') == 'LINK', f"step1 data.type != LINK, got {_d1.get('type')}"
    _title1 = _d1.get('title') or ''
    assert re.match(r'^Automation music \d+$', _title1), f"step1 title 格式错误: {_title1}"
    assert _d1.get('id'), "step1 data.id 为空"
    vars['dynamicMusicLinkId'] = _d1.get('id')
    # step 2: 4ad69ccd-e26c-42a6-b635-ee54c1498ef5
    # === pre-script（由Apifox customScript翻译）：动态生成 music 链接请求体 ===
    _dynamicTimeKey = int(__import__('time').time() * 1000)
    vars['musicTitle'] = 'music_' + str(random.randint(10000, 99999))
    _music_services = [
        {"platform": "APPLE_MUSIC", "src": "https://music.apple.com/us/album/cruel-summer/1640383474?i=1640383500", "position": 1},
        {"platform": "ANGHAMI", "src": "https://play.anghami.com/song/177824714", "position": 2},
        {"platform": "AUDIOMACK", "src": "https://audiomack.com/leanna-firestone/song/samson", "position": 3},
        {"platform": "BANDCAMP", "src": "https://leannafirestone.bandcamp.com/track/samson", "position": 4},
        {"platform": "BEATPORT", "src": "https://www.beatport.com/track/cruel-summer/17892345", "position": 5},
        {"platform": "DEEZER", "src": "https://www.deezer.com/track/1889456789", "position": 6},
        {"platform": "GAANA", "src": "https://gaana.com/song/samson-12", "position": 7},
        {"platform": "IHEARTRADIO", "src": "https://www.iheart.com/artist/leanna-firestone-123456/cruel-summer-32145678/", "position": 8},
        {"platform": "NAPSTER", "src": "https://us.napster.com/song/leanna-firestone/samson", "position": 9},
        {"platform": "PANDORA", "src": "https://www.pandora.com/artist/leanna-firestone/samson/AL123456789", "position": 10},
        {"platform": "QOBUZ", "src": "https://www.qobuz.com/us-en/track/samson/1234567890123", "position": 11},
        {"platform": "SPOTIFY", "src": "https://open.spotify.com/track/3hgl7EQwYP7y9A557Rj9p3", "position": 12},
        {"platform": "TIDAL", "src": "https://tidal.com/track/123456789", "position": 13},
        {"platform": "YOUTUBE_MUSIC", "src": "https://music.youtube.com/watch?v=eJ9R3xQ98c0", "position": 14},
    ]
    _music_body = {
        "position": 0, "type": "MUSIC", "timeKey": _dynamicTimeKey,
        "additionalInfo": {"services": _music_services, "artist": "Leanna Firestone"},
        "title": vars['musicTitle'],
        "mediaSrc": "https://res.cloudinary.com/dr9io1zjv/v1765509128/uploaded_images/vqesoltctfxgyufqun0t.jpg",
        "showBelowTitle": False,
    }
    _resp2 = ctx.api.links.create(body=json.dumps(_music_body), token='linda01_token')
    # === 断言/提取（由Apifox customScript翻译）===
    _j2 = _resp2.json() if _resp2.headers.get('content-type','').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"step2 code != 200, got {_j2.get('code')}"
    assert _j2.get('message') == 'success', f"step2 message != success, got {_j2.get('message')}"
    _d2 = _j2.get('data') or {}
    _title2 = _d2.get('title') or ''
    assert re.match(r'^music_\d+$', _title2), f"step2 title 格式错误: {_title2}"
    assert _d2.get('type') == 'MUSIC', f"step2 data.type != MUSIC, got {_d2.get('type')}"
    assert _d2.get('showBelowTitle') is False, f"step2 showBelowTitle != False, got {_d2.get('showBelowTitle')}"
    assert _d2.get('position') == 0, f"step2 position != 0, got {_d2.get('position')}"
    _services2 = (_d2.get('additionalInfo') or {}).get('services') or []
    assert isinstance(_services2, list) and len(_services2) >= 14, f"step2 services 数量不足, got {len(_services2)}"
    assert _d2.get('id'), "step2 data.id 为空"
    vars['moduleContentId'] = _d2.get('id')
    # step 3: 02b3432c-17c6-4bce-8fc9-01d250e4c238
    _resp3 = ctx.api.storefront.module_item_by_dynamic_music_link_id(body='{\r\n    "id": "{{dynamicMusicLinkId}}",\r\n    "items": [\r\n        {\r\n            "itemId": "a4ed8dd4-e38c-4fca-a5e1-7060cb018d8d",\r\n            "position": 1\r\n        }\r\n    ]\r\n}', token='linda01_token')
    # === 断言（由Apifox customScript翻译）===
    _j3 = _resp3.json() if _resp3.headers.get('content-type','').startswith('application/json') else {}
    assert _j3.get('code') == 200, f"step3 code != 200, got {_j3.get('code')}"
    assert _j3.get('message') == 'success', f"step3 message != success, got {_j3.get('message')}"
    _d3 = _j3.get('data') or {}
    _title3 = _d3.get('title') or ''
    assert re.match(r'^Automation music \d+$', _title3), f"step3 title 格式错误: {_title3}"
    assert _d3.get('direction') == 'VERTICAL', f"step3 direction != VERTICAL, got {_d3.get('direction')}"
    assert _d3.get('visible') is True, f"step3 visible != true, got {_d3.get('visible')}"
    _items3 = _d3.get('items') or []
    assert isinstance(_items3, list) and len(_items3) >= 1, f"step3 items 为空"
    _inner3 = _items3[0] or {}
    _add3 = _inner3.get('additionalInfo') or {}
    assert _add3, "step3 additionalInfo 为空"
    assert _add3.get('artist') == 'Leanna Firestone', f"step3 artist != Leanna Firestone, got {_add3.get('artist')}"
    _svc3 = _add3.get('services') or []
    assert isinstance(_svc3, list) and len(_svc3) > 0, "step3 services 为空"
    for _s in _svc3:
        assert _s.get('platform'), "step3 service 缺少 platform"
        assert _s.get('src'), "step3 service 缺少 src"
        assert isinstance(_s.get('position'), (int, float)), f"step3 service position 非数字: {_s.get('position')}"
    # step 4: 73a7f755-a3eb-400c-bb7a-15ad1eb9d79a
    _resp4 = ctx.api.storefront.module_by_dynamic_music_link_id(body=None, token='linda01_token')
