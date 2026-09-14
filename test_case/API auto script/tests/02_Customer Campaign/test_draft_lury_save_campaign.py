"""Migrated from Apifox case #8620149. Source folder: Customer Campaign ."""
# Apifox Case ID: 8620149  (traceability only — not needed to run)
NAME = "Draft (Lury) save campaign"
TAGS = ["p0", "customer_campaign"]
PRIORITY = 0


CASE_ID = 8620149
ENV_NAME = "Release"


from core.assertions import expect

def test_draft_lury_save_campaign(ctx):
    """Apifox case #8620149: Draft_Lury_save_campaign"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # === Steps ===
    vars['account_email_curator'] = 'linda.zhou.ext+01@1m.app'
    # step 1:
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
    # step 2:
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
    # step 3:
    _resp3 = ctx.api.campaigns.save_recipients(
        body={
            "campaignId": "{{campaignId}}",
            "channel": "SMS",
            "isSelectAll": False,
            "followerIds": ["d3435d0a-d6df-4f80-a9b2-f5da77b368fe"],
            "excludeFollowers": [],
            "searchKey": "6502469802",
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
