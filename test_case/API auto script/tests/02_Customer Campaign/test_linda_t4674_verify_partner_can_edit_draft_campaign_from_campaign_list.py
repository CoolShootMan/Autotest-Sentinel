"""Migrated from Apifox case #7631803. Source folder: Customer Campaign ."""
# Apifox Case ID: 7631803  (traceability only — not needed to run)
NAME = "Verify partner can edit draft campaign from campaign list"
TAGS = ["p1", "customer_campaign", "suite:linda"]
PRIORITY = 1


CASE_ID = 7631803
ENV_NAME = "Release"


def _gen_random_sms_name():
    """对应原 Apifox pre-script 的 generateRandomSMSName()"""
    prefixes = ["SMS_Promo_", "Order_Alert_", "Sale_Reminder_", "Event_Notify_", "Coupon_SMS_"]
    suffixes = [
        f"{datetime.datetime.now().month}_{random.randint(0, 29)}",
        str(random.randint(0, 999)),
        f"{random.choice(['AM', 'PM'])}{random.randint(0, 11)}",
    ]
    name = random.choice(prefixes) + random.choice(suffixes)
    if len(name) > 20:
        name = name[:20]
    return name

def _gen_random_sms_content():
    """对应原 Apifox pre-script 的 generateRandomSMSContent()（模板内占位符全部填充）"""
    templates = [
        "Your Order #{{orderNo}} Has Shipped! \U0001f4e6 Track: {{trackNo}}. Delivery in {{days}} business days. Thank you!",
        "Exclusive Offer! {{discount}}% OFF on {{product}} \u2013 Valid till {{date}}. Use code: {{code}}. Reply STOP to unsubscribe.",
        "Reminder: {{event}} on {{date}} at {{time}}! Don\u2019t miss out \u2013 confirm via {{link}}. Reply YES to confirm.",
        "Free {{amount}} Coupon! Redeem at {{store}} till {{date}}. Code: {{code}}. Limited stock \u2013 act fast!"
    ]
    t = random.choice(templates)
    content = (t
        .replace("{{orderNo}}", str(random.randint(10000, 99999)))
        .replace("{{trackNo}}", "TRK" + str(random.randint(100000, 999999)))
        .replace("{{days}}", str(random.randint(1, 5)))
        .replace("{{discount}}", str(random.choice([5, 10, 15, 20, 25])))
        .replace("{{product}}", random.choice(["Electronics", "Clothing", "Groceries", "Beauty"]))
        .replace("{{date}}", f"{datetime.datetime.now().month}/{random.randint(1, 28)}")
        .replace("{{code}}", ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)).upper())
        .replace("{{event}}", random.choice(["Concert", "Workshop", "Sale Event", "Webinar"]))
        .replace("{{time}}", f"{random.randint(0, 11)}:{random.choice(['00', '15', '30', '45'])}")
        .replace("{{link}}", "bit.ly/" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)))
        .replace("{{amount}}", random.choice(["$5", "$10", "$15", "$20"]))
        .replace("{{store}}", random.choice(["Our Store", "Online Shop", "Retail Outlet"])))
    if len(content) > 160:
        content = content[:160]
    return content

import datetime
import random
import string
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

def test_linda_t4674_verify_partner_can_edit_draft_campaign_from_campaign_list(ctx):
    """Apifox case #7631803: Linda_T4674_Verify_partner_can_edit_draft_campaign_from_campaign_list"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # 动态生成 SMS name/content（对应原 Apifox pre-script 的 generateRandomSMSName / generateRandomSMSContent）
    vars['randomName'] = _gen_random_sms_name()
    vars['randomContent'] = _gen_random_sms_content()
    # === Steps ===
    # step 1: Create SMS campaign
    _resp1 = ctx.api.campaigns.create(
        body={
            "channel": "SMS",
            "name": "automation by linda SMS",
            "content": "Subject: Your Order #7892 Has Shipped! ",
        },
        token='linda01_token',
    )
    # assertion 1.assertion: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # assertion 1.assertion: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # extractor: campaignId = $.data.id
    ctx.extract('campaignId', _resp1, '$.data.id')
    # step 2: Edit SMS campaign
    _resp2 = ctx.api.campaigns.by_campaign_id(
        body={
            "id": "{{campaignId}}",
            "name": "{{randomName}}",
            "channel": "SMS",
            "status": "DRAFT",
            "content": "{{randomContent}}",
            "selectAll": False,
            "totalSelectedCount": 1,
        },
        token='linda01_token',
    )
    vars['smsCampaignGenerateVerifyResult'] = 'verifyPass ? "success" : "failed"'
    vars['smsCampaignGenerateVerifyLogs'] = 'JSON.stringify(verifyLogs'
    # step 3: Create EMAIL campaign
    _resp3 = ctx.api.campaigns.create(
        body={
            "channel": "EMAIL",
            "name": "automation by linda Email",
            "subject": "Don\u2019t Miss Out! ",
            "content": _EMAIL_HTML_CONTENT,
        },
        token='linda01_token',
    )
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # extractor: campaignEmailId = $.data.id
    ctx.extract('campaignEmailId', _resp3, '$.data.id')
    # assertion 3.assertion: responseJson equal 0
    expect(_resp3).json('$.data.totalSelectedCount').equals('0')
    # step 4: Edit EMAIL campaign
    _resp4 = ctx.api.campaigns.by_campaign_id(
        body={
            "id": "{{campaignEmailId}}",
            "name": "{{randomName}}",
            "channel": "EMAIL",
            "status": "DRAFT",
            "subject": "Don\u2019t Miss Out! ",
            "content": "{{randomContent}}",
            "selectAll": False,
            "totalSelectedCount": 1,
        },
        token='linda01_token',
        path_vars={'campaignId': '{{campaignEmailId}}'},
    )
    vars['emailCampaignGenerateVerifyResult'] = 'verifyPass ? "success" : "failed"'
    vars['emailCampaignGenerateVerifyLogs'] = 'JSON.stringify(verifyLogs'
