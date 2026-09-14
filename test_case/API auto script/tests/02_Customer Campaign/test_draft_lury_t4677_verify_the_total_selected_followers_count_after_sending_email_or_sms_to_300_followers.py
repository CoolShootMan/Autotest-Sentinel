"""Migrated from Apifox case #7887702. Source folder: Customer Campaign ."""
# Apifox Case ID: 7887702  (traceability only — not needed to run)
NAME = "Draft (Lury) T4677 Verify the total selected followers count after sending email or sms to 300 followers"
TAGS = ["p0", "customer_campaign"]
PRIORITY = 0


CASE_ID = 7887702
ENV_NAME = "Release"

# --- step 5: View campaign details ---
# --- step 9: View campaign details ---


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

def test_draft_lury_t4677_verify_the_total_selected_followers_count_after_sending_email_or_sms_to_300_followers(ctx):
    """Apifox case #7887702: Draft_Lury_T4677_Verify_the_total_selected_followers_count_after_sending_email_o"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['account_email_curator'] = 'linda.zhou.ext+01@1m.app'
    # step 1: Merchant login
    _resp1 = ctx.api.auth.sign_in(
        body={"email": "{{merchant_email}}", "password": "{{merchant_password}}"},
        app_headers=True,
    )
    # assertion 1.code: responseJson equal 200
    expect(_resp1).json('$.code').equals('200')
    # extractor: token = $.data.token
    ctx.extract('token', _resp1, '$.data.token')
    # assertion 1.message: responseJson equal success
    expect(_resp1).json('$.message').equals('success')
    # step 2: Create SMS campaign
    _resp2 = ctx.api.campaigns.create(
        body={
            "channel": "SMS",
            "name": "Automation by Lury SMS",
            "content": "This is test SMS message from Lury, It will don't send to any one",
        },
        token='token',
    )
    # assertion 2.assertion: responseJson equal 200
    expect(_resp2).json('$.code').equals('200')
    # assertion 2.assertion: responseJson equal success
    expect(_resp2).json('$.message').equals('success')
    # extractor: campaignId = $.data.id
    ctx.extract('campaignId', _resp2, '$.data.id')
    # step 3: Save recipients (selectAll) for SMS
    _resp3 = ctx.api.campaigns.save_recipients(
        body={
            "campaignId": "{{campaignId}}",
            "channel": "SMS",
            "isSelectAll": True,
            "followerIds": [],
            "excludeFollowers": [],
            "searchKey": "",
        },
        token='token',
    )
    # assertion 3.assertion: responseJson equal 200
    expect(_resp3).json('$.code').equals('200')
    # assertion 3.assertion: responseJson equal success
    expect(_resp3).json('$.message').equals('success')
    # extractor: selected_count_sms = $.data.totalSelectedCount
    ctx.extract('selected_count_sms', _resp3, '$.data.totalSelectedCount')
    # assertion 3.Check number of segment: responseJson equal 1
    expect(_resp3).json('$.data.segmentsPerMessage').equals('1')
    # assertion 3.Check unit price for SMS: responseJson equal 0.01
    expect(_resp3).json('$.data.unitPrice').equals('0.01')
    # assertion 3.Check sms fixed fee: responseJson equal 2
    expect(_resp3).json('$.data.fixedFee').equals('2')
    # extractor: total_fee = $.data.totalToPay
    ctx.extract('total_fee', _resp3, '$.data.totalToPay')
    # step 4: Send SMS campaign
    _resp4 = ctx.api.campaigns.send_campaign(
        body={
            "campaignId": "{{campaignId}}",
            "channel": "SMS",
            "paymentBreakdown": {"CAMPAIGN": 0, "PAYOUT": "{{total_fee}}"},
        },
        token='token',
    )
    # step 5: View campaign details
    _resp5 = ctx.api.campaigns.by_campaign_id_2(token='token')
    # assertion 5.Verify total selected count: responseJson equal {{selected_count_sms}}
    expect(_resp5).json('$.data.totalSelectedCount').equals(ctx.render_text('{{selected_count_sms}}'))
    # step 6: Create EMAIL campaign
    _resp6 = ctx.api.campaigns.create(
        body={
            "channel": "EMAIL",
            "name": "Automation by Lury campaign Email",
            "subject": "Don\u2019t Miss Out! ",
            "content": _EMAIL_HTML_CONTENT,
        },
        token='token',
    )
    # assertion 6.assertion: responseJson equal 200
    expect(_resp6).json('$.code').equals('200')
    # assertion 6.assertion: responseJson equal success
    expect(_resp6).json('$.message').equals('success')
    # extractor: campaignEmailId = $.data.id
    ctx.extract('campaignEmailId', _resp6, '$.data.id')
    # assertion 6.assertion: responseJson equal 0
    expect(_resp6).json('$.data.totalSelectedCount').equals('0')
    # step 7: Save recipients (selectAll) for EMAIL
    _resp7 = ctx.api.campaigns.save_recipients(
        body={
            "campaignId": "{{campaignEmailId}}",
            "channel": "EMAIL",
            "isSelectAll": True,
            "followerIds": [],
            "searchKey": "",
        },
        token='token',
    )
    # assertion 7.assertion: responseJson equal 200
    expect(_resp7).json('$.code').equals('200')
    # assertion 7.assertion: responseJson equal success
    expect(_resp7).json('$.message').equals('success')
    # assertion 7.assertion: responseJson equal 0
    expect(_resp7).json('$.data.deleted').equals('0')
    # extractor: selected_count_email = $.data.created
    ctx.extract('selected_count_email', _resp7, '$.data.created')
    # step 8: Send EMAIL campaign
    _resp8 = ctx.api.campaigns.send_campaign(
        body={"campaignId": "{{campaignEmailId}}", "channel": "EMAIL"},
        token='token',
    )
    # assertion 8.assertion: responseJson equal 200
    expect(_resp8).json('$.code').equals('200')
    # assertion 8.assertion: responseJson equal true
    expect(_resp8).json('$.data.success').equals('true')
    # step 9: View campaign details
    _resp9 = ctx.api.campaigns.by_campaign_id_2(token='token', path_vars={'campaignId': '{{campaignEmailId}}'})
    # assertion 9.Verify select followers count: responseJson equal {{selected_count_email}}
    expect(_resp9).json('$.data.totalSelectedCount').equals(ctx.render_text('{{selected_count_email}}'))
