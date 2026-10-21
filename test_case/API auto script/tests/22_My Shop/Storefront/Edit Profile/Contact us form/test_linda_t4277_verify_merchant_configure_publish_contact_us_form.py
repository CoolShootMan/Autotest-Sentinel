"""ONES case: Verify Merchant can configure and publish the Contact us form"""
NAME = "Verify Merchant can configure and publish the Contact us form"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "8N87Xddf"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4277_verify_merchant_configure_publish_contact_us_form(ctx: "Context"):
    """ONES case #8N87Xddf: Verify Merchant can configure and publish the Contact us form"""
    vars = ctx
    # step 1: create the contact us form with basic info + required fields
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "We are here to help",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
            {"field": "EMAIL_ADDRESS", "title": "Email", "required": True},
            {"field": "PARAGRAPH", "title": "Message", "required": True},
        ],
        "confirmationMessage": {
            "title": "You have successfully submitted the information!",
            "body": "We will reply within three to four working days",
        },
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    expect(_create).json('$.data.title').equals("Contact us")
    expect(_create).json('$.data.subtitle').equals("We are here to help")
    expect(_create).json('$.data.formFields').length(3)
    ctx.extract('t4277_form_id', _create, '$.data.id')

    # step 2: fetch merchant-side form detail, basic info must be persisted
    _get = ctx.api.forms.by_id(id=vars['t4277_form_id'], token='linda997_token')
    expect(_get).json('$.code').equals('200')
    expect(_get).json('$.data.title').equals("Contact us")
    expect(_get).json('$.data.confirmationMessage.title').equals("You have successfully submitted the information!")

    # step 3: visitor-side public form exposes title / subtitle / fields
    _pub = ctx.api.forms.public_by_id(id=vars['t4277_form_id'])
    expect(_pub).json('$.code').equals('200')
    expect(_pub).json('$.data.title').equals("Contact us")
    expect(_pub).json('$.data.subtitle').equals("We are here to help")

    # teardown: delete the form
    _del = ctx.api.forms.delete_by_id(id=vars['t4277_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

