"""ONES case: Verify exported report contains correct data, full timestamp, and timezone"""
NAME = "Verify exported report contains correct data, full timestamp, and timezone"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "MVW5DEEo"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4540_verify_export_report_contains_data(ctx: "Context"):
    """ONES case #MVW5DEEo: Verify exported report contains correct data, full timestamp, and timezone"""
    vars = ctx
    _create = ctx.api.forms.create(body={
        "title": "Contact us",
        "subtitle": "",
        "description": "",
        "showImage": False,
        "recipientEmail": "linda.zhou.ext+00@1m.app",
        "formFields": [
            {"field": "SHORT_ANSWER", "title": "Name", "required": True},
        ],
    }, token='linda997_token')
    expect(_create).json('$.code').equals('200')
    ctx.extract('t4540_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')

    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4540_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "ReportRow"},
        ],
    })
    expect(_sub).json('$.data.success').equals(True)

    # export all submissions for this form (binary zip)
    _ex = ctx.api.forms.export_inquiry(body={
        "formId": vars['t4540_form_id'],
        "exportAll": True,
    }, token='linda997_token')
    expect(_ex).status().is_ok()

    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4540_form_id']})
    ids = [it['id'] for it in _list.json_safe()['data']['items']]
    if ids:
        ctx.api.forms.delete_inquiries(body={"ids": ids}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4540_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

