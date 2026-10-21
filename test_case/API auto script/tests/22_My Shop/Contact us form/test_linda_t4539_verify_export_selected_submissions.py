"""ONES case: Verify Export data button appears after selecting submissions"""
NAME = "Verify Export data button appears after selecting submissions"
TAGS = ['p0', 'contact_us_form', 'suite:linda']
PRIORITY = 0
CASE_ID = "PdbNzxEB"
ENV_NAME = "Release"

from typing import TYPE_CHECKING
from core.assertions import expect
if TYPE_CHECKING:
    from core.context import Context


def test_linda_t4539_verify_export_selected_submissions(ctx: "Context"):
    """ONES case #PdbNzxEB: Verify Export data button appears after selecting submissions"""
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
    ctx.extract('t4539_form_id', _create, '$.data.id')
    f_name = _create.path('$.data.formFields[0].id')

    _sub = ctx.api.forms.submit(body={
        "contactId": vars['t4539_form_id'],
        "emailMessage": [
            {"title": "Name", "field": "SHORT_ANSWER", "fieldId": f_name, "value": "ExportMe"},
        ],
    })
    expect(_sub).json('$.data.success').equals(True)

    _list = ctx.api.forms.list_inquiry(token='linda997_token', params={'formId': vars['t4539_form_id']})
    ctx.extract('t4539_inq_id', _list, '$.data.items[0].id')

    # export only the selected inquiry (binary zip stream)
    _ex = ctx.api.forms.export_inquiry(body={
        "formId": vars['t4539_form_id'],
        "ids": [vars['t4539_inq_id']],
        "exportAll": False,
    }, token='linda997_token')
    expect(_ex).status().is_ok()

    ctx.api.forms.delete_inquiries(body={"ids": [vars['t4539_inq_id']]}, token='linda997_token')
    _del = ctx.api.forms.delete_by_id(id=vars['t4539_form_id'], token='linda997_token')
    expect(_del).json('$.code').equals('200')

