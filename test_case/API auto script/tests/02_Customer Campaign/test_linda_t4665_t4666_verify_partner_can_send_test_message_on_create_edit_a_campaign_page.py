"""Migrated from Apifox case #7627466. Source folder: Customer Campaign ."""
# Apifox Case ID: 7627466  (traceability only — not needed to run)
NAME = "&T4666 Verify partner can send test message on create/edit a campaign page"
TAGS = ["p0", "customer_campaign", "suite:linda"]
PRIORITY = 0


CASE_ID = 7627466
ENV_NAME = "Release"


import json
import re

from core.assertions import expect

# --- 可复用的 HTML 邮件内容（消除源码中的深层转义）---
_EMAIL_HTML_CONTENT = (
    '<p class="katana__paragraph katana__paragraph--align-start" dir="ltr" style="text-align: start;">'
    '<b><strong class="katana__textBold" style="color: rgb(0, 0, 0); font-size: 16px; line-height: 28px; white-space: pre-wrap;">'
    'Subject: Don\u2019t Miss Out! Live Concert 2026 \u2013 Early Bird Tickets Now On Sale</strong></b></p>'
    '<p class="katana__paragraph katana__paragraph--align-start" dir="ltr" style="text-align: start;">'
    '<span style="white-space: pre-wrap;">Dear Music Lover,</span></p>'
    '<p class="katana__paragraph katana__paragraph--align-start" dir="ltr" style="text-align: start;">'
    '<span style="white-space: pre-wrap;">We\u2019re thrilled to announce that global superstar [Artist Name] is hitting the stage in your city this summer! '
    'The \u201cStellar Nights Tour\u201d will light up [Venue Name] on [Date, Time], featuring hit songs from their latest album and classic fan favorites'
    '\u2014plus exclusive stage visuals you won\u2019t want to miss.</span></p>'
    '<p class="katana__paragraph katana__paragraph--align-start" dir="ltr" style="text-align: start;">'
    '<span style="white-space: pre-wrap;">Secure your spot before prices rise: early bird tickets are 20% off until [Deadline]! '
    'Grab yours here: bit.ly/StellarNights2025. Limited VIP packages include meet-and-greets and backstage access'
    '\u2014perfect for die-hard fans.</span></p>'
    '<p class="katana__paragraph katana__paragraph--align-start" dir="ltr" style="text-align: start;">'
    '<span style="white-space: pre-wrap;">Hurry, tickets sell out fast for [Artist Name]\u2019s tours! For group bookings or questions, email </span>'
    '<a href="mailto:support@concertpro.com" class="katana__link" dir="ltr">'
    '<span style="white-space: pre-wrap;">support@concertpro.com</span></a>'
    '<span style="white-space: pre-wrap;"> or call +1-800-567-8901.</span></p>'
    '<p class="katana__paragraph katana__paragraph--align-start" dir="ltr" style="text-align: start;">'
    '<span style="white-space: pre-wrap;">Don\u2019t let this unforgettable night slip away\u2014see you at the show!</span></p>'
    '<p class="katana__paragraph katana__paragraph--align-start" dir="ltr" style="text-align: start;">'
    '<span style="white-space: pre-wrap;">Best regards,The ConcertPro TeamYour Go-To for Unforgettable Live Music Experiences</span></p>'
)

def test_linda_t4665_t4666_verify_partner_can_send_test_message_on_create_edit_a_campaign_page(ctx):
    """Apifox case #7627466: Linda_T4665_T4666_Verify_partner_can_send_test_message_on_create_edit_a_campaign"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    # step 1: Create SMS campaign
    _resp1 = ctx.api.campaigns.create(
        body={
            "channel": "SMS",
            "name": "automation by linda SMS",
            "content": "Subject: Your Order #7892 Has Shipped!",
        },
        token='linda01_token',
    )
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # extractor: campaignId = $.data.id
    ctx.extract('campaignId', _resp1, '$.data.id')
    # step 2: Test SMS
    _resp2 = ctx.api.campaigns.test_sms(
        body={
            "phones": ["+16502396646"],
            "message": "Subject: Your Order #7892 Has Shipped!",
        },
        token='linda01_token',
    )
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j2 = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert (_j2.get('data') or {}).get('success') is True, f"data.success应为true，实际={(_j2.get('data') or {}).get('success')!r}"
    assert (_j2.get('data') or {}).get('message') == "Test SMS sent to 1 recipients", f"data.message不匹配：{(_j2.get('data') or {}).get('message')!r}"
    # step 3: Save recipients for SMS campaign
    _resp3 = ctx.api.campaigns.save_recipients(
        body={
            "campaignId": "{{campaignId}}",
            "channel": "SMS",
            "isSelectAll": False,
            "followerIds": ["bbf4a1ee-d93d-4e92-9e73-53ba168d7a66"],
            "searchKey": "",
        },
        token='linda01_token',
    )
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # assertion 3.assertion: responseJson equal DRAFT
    expect(_resp3).json('$.data.status').equals('DRAFT')
    # assertion 3.assertion: responseJson equal UNPAID
    expect(_resp3).json('$.data.paymentStatus').equals('UNPAID')
    # step 4: Verify SMS campaign details
    _resp4 = ctx.api.campaigns.by_campaign_id(
        body={
            "id": "{{campaignId}}",
            "name": "automation by linda SMS",
            "status": "DRAFT",
            "paymentStatus": "UNPAID",
            "channel": "SMS",
            "content": "Subject: Your Order #7892 Has Shipped!",
            "selectAll": False,
            "totalSelectedCount": 1,
            "totalSegments": 1,
            "fixedFee": 2,
            "unitPrice": 0.01,
            "totalToPay": 2.01,
            "usageFee": 0.01,
            "paymentBreakdown": {"PAYOUT": 2.01, "DEPOSIT": 0, "CAMPAIGN": 0},
        },
        token='linda01_token',
    )
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j4 = _resp4.json() if _resp4.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp4.status_code == 200, f"HTTP状态码应为200，实际={_resp4.status_code}"
    assert _j4.get('code') == 200, f"业务code应为200，实际={_j4.get('code')!r}"
    assert _j4.get('message') == 'success', f"message应为success，实际={_j4.get('message')!r}"
    assert isinstance(_j4.get('request_id'), str) and _j4.get('request_id'), f"request_id应为非空字符串，实际={_j4.get('request_id')!r}"
    _d4 = _j4.get('data') or {}
    # 核心业务字段断言（固定配置和状态）
    assert _d4.get('name') == "automation by linda SMS", f"data.name不匹配：{_d4.get('name')!r}"
    assert _d4.get('channel') == "SMS", f"data.channel应为SMS，实际={_d4.get('channel')!r}"
    assert _d4.get('status') == "DRAFT", f"data.status应为DRAFT，实际={_d4.get('status')!r}"
    assert _d4.get('paymentStatus') == "UNPAID", f"data.paymentStatus应为UNPAID，实际={_d4.get('paymentStatus')!r}"
    assert _d4.get('sentStatus') == "NOT_STARTED", f"data.sentStatus应为NOT_STARTED，实际={_d4.get('sentStatus')!r}"
    assert _d4.get('smsEncoding') == "GSM_7", f"data.smsEncoding应为GSM_7，实际={_d4.get('smsEncoding')!r}"
    # 短信条数与费用计算逻辑
    assert _d4.get('totalSelectedCount') == 1, f"totalSelectedCount应为1，实际={_d4.get('totalSelectedCount')!r}"
    assert _d4.get('segmentsPerMessage') == 1, f"segmentsPerMessage应为1，实际={_d4.get('segmentsPerMessage')!r}"
    assert _d4.get('totalSegments') == 1, f"totalSegments应为1，实际={_d4.get('totalSegments')!r}"
    assert _d4.get('unitPrice') == 0.01, f"unitPrice应为0.01，实际={_d4.get('unitPrice')!r}"
    assert _d4.get('fixedFee') == 2, f"fixedFee应为2，实际={_d4.get('fixedFee')!r}"
    assert _d4.get('usageFee') == 0.01, f"usageFee应为0.01，实际={_d4.get('usageFee')!r}"
    assert _d4.get('totalToPay') == 2.01, f"totalToPay应为2.01，实际={_d4.get('totalToPay')!r}"
    assert _d4.get('totalToPay') == (_d4.get('fixedFee') or 0) + (_d4.get('usageFee') or 0), f"应付金额应=固定费+使用费，实际totalToPay={_d4.get('totalToPay')!r}"
    assert (_d4.get('paymentBreakdown') or {}).get('PAYOUT') == _d4.get('totalToPay'), f"paymentBreakdown.PAYOUT应等于totalToPay，实际={(_d4.get('paymentBreakdown') or {}).get('PAYOUT')!r}"
    # 动态数据：只校验类型、非空和格式
    assert isinstance(_d4.get('id'), str) and _d4.get('id'), f"data.id应为非空字符串，实际={_d4.get('id')!r}"
    assert isinstance(_d4.get('userId'), str) and _d4.get('userId'), f"data.userId应为非空字符串，实际={_d4.get('userId')!r}"
    _iso_re = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')
    assert _iso_re.match(str(_d4.get('createdAt') or '')), f"createdAt格式不正确：{_d4.get('createdAt')!r}"
    assert _iso_re.match(str(_d4.get('updatedAt') or '')), f"updatedAt格式不正确：{_d4.get('updatedAt')!r}"
    # step 5: Create EMAIL campaign
    _resp5 = ctx.api.campaigns.create(
        body={
            "channel": "EMAIL",
            "name": "automation by linda Email",
            "subject": "Don\u2019t Miss Out! ",
            "content": _EMAIL_HTML_CONTENT,
        },
        token='linda01_token',
    )
    # assertion 5.assertion: responseJson equal 200
    expect(_resp5).json('$.code').equals('200')
    # assertion 5.assertion: responseJson equal success
    expect(_resp5).json('$.message').equals('success')
    # extractor: campaignEmailId = $.data.id
    ctx.extract('campaignEmailId', _resp5, '$.data.id')
    # assertion 5.assertion: responseJson equal 0
    expect(_resp5).json('$.data.totalSelectedCount').equals('0')
    # step 6: Test email
    _resp6 = ctx.api.campaigns.test_email(
        body={
            "emails": ["linda.zhou.ext@1m.app"],
            "subject": "Don\u2019t Miss Out! ",
            "content": _EMAIL_HTML_CONTENT,
        },
        token='linda01_token',
    )
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j6 = _resp6.json() if _resp6.headers.get('content-type', '').startswith('application/json') else {}
    assert (_j6.get('data') or {}).get('success') is True, f"data.success应为true，实际={(_j6.get('data') or {}).get('success')!r}"
    assert (_j6.get('data') or {}).get('message') == "Test email sent to 1 recipients", f"data.message不匹配：{(_j6.get('data') or {}).get('message')!r}"
    # step 7: Save recipients for EMAIL campaign
    _resp7 = ctx.api.campaigns.save_recipients(
        body={
            "campaignId": "{{campaignEmailId}}",
            "channel": "EMAIL",
            "isSelectAll": False,
            "followerIds": ["5617efb6-1b25-4b22-af65-5a76ca51dcea"],
            "searchKey": "",
        },
        token='linda01_token',
    )
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal success
    expect(_resp7).json('$.message').equals('success')
    # assertion 7.assertion: responseJson equal DRAFT
    expect(_resp7).json('$.data.status').equals('DRAFT')
    # assertion 7.assertion: responseJson equal UNPAID
    expect(_resp7).json('$.data.paymentStatus').equals('UNPAID')
    # step 8: Verify EMAIL campaign details
    _resp8 = ctx.api.campaigns.by_campaign_id(
        body={
            "id": "{{campaignEmailId}}",
            "name": "automation by linda Email",
            "status": "DRAFT",
            "paymentStatus": "UNPAID",
            "channel": "Email",
            "subject": None,
            "content": "Subject: Your Order #7892 Has Shipped!",
            "selectAll": False,
            "totalSelectedCount": 1,
            "totalSegments": 1,
            "fixedFee": 2,
            "unitPrice": 0.01,
            "totalToPay": 2.01,
            "usageFee": 0.01,
            "paymentBreakdown": {"PAYOUT": 2.01, "DEPOSIT": 0, "CAMPAIGN": 0},
        },
        token='linda01_token',
        path_vars={'campaignId': '{{campaignEmailId}}'},
    )
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j8 = _resp8.json() if _resp8.headers.get('content-type', '').startswith('application/json') else {}
    assert _resp8.status_code == 200, f"响应状态码为200，实际={_resp8.status_code}"
    assert _j8.get('code') == 200, f"业务code应为200，实际={_j8.get('code')!r}"
    assert _j8.get('message') == 'success', f"message应为success，实际={_j8.get('message')!r}"
    _d8 = _j8.get('data') or {}
    # 核心业务数据断言
    assert _d8.get('status') == "DRAFT", f"data.status应为DRAFT，实际={_d8.get('status')!r}"
    assert _d8.get('paymentStatus') == "UNPAID", f"data.paymentStatus应为UNPAID，实际={_d8.get('paymentStatus')!r}"
    assert _d8.get('sentStatus') == "NOT_STARTED", f"data.sentStatus应为NOT_STARTED，实际={_d8.get('sentStatus')!r}"
    assert _d8.get('name') == "automation by linda Email", f"data.name不匹配：{_d8.get('name')!r}"
    assert _d8.get('channel') == "EMAIL", f"data.channel应为EMAIL，实际={_d8.get('channel')!r}"
    assert isinstance(_d8.get('id'), str) and _d8.get('id'), f"data.id应为非空字符串，实际={_d8.get('id')!r}"
    # 费用与计算逻辑断言
    assert _d8.get('unitPrice') == 0.001, f"unitPrice应为0.001，实际={_d8.get('unitPrice')!r}"
    assert _d8.get('totalToPay') == 1, f"totalToPay应为1，实际={_d8.get('totalToPay')!r}"
    assert (_d8.get('paymentBreakdown') or {}).get('PAYOUT') == 1, f"paymentBreakdown.PAYOUT应为1，实际={(_d8.get('paymentBreakdown') or {}).get('PAYOUT')!r}"
