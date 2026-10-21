"""ONES case: Verify Form Social Field Configuration with Auto-Complete URL Generation"""
NAME = "Verify Form Social Field Configuration with Auto-Complete URL Generation"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "2c3QWELc"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4972_verify_social_field_config(ctx: "Context"):
    """ONES case #2c3QWELc: Verify Form Social Field Configuration with Auto-Complete URL Generation"""
    vars = ctx
    # step 1: merchant adds a required Social (Instagram) field
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
            {"field": "SOCIAL", "title": "Find us on Instagram", "required": True},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4972_form_id', _create, '$.data.id')

    # step 2: social field persists as SOCIAL type with the custom title
    _get = ctx.api.forms.by_id(id=vars['t4972_form_id'], token='linda997_token')
    expect(_get).json('$.data.formFields[1].field').equals("SOCIAL")
    expect(_get).json('$.data.formFields[1].title').equals("Find us on Instagram")
    expect(_get).json('$.data.formFields[1].required').equals(True)

    # step 3: public form exposes the social field to visitors
    _pub = ctx.api.forms.public_by_id(id=vars['t4972_form_id'])
    expect(_pub).json('$.data.formFields..field').includes("SOCIAL")

    _del = ctx.api.forms.delete_by_id(id=vars['t4972_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

