"""Migrated from Apifox case #7631212. Source folder: Customer Campaign ."""
# Apifox Case ID: 7631212  (traceability only — not needed to run)
NAME = "Verify partner can search campaign on campaign list"
TAGS = ["p1", "customer_campaign", "suite:linda"]
PRIORITY = 1


CASE_ID = 7631212
ENV_NAME = "Release"


def test_linda_t4673_verify_partner_can_search_campaign_on_campaign_list(ctx):
    """Apifox case #7631212: Linda_T4673_Verify_partner_can_search_campaign_on_campaign_list"""
    # === Steps ===
    # step 1:
    _resp1 = ctx.api.campaigns.list(body=None, params={'search': 'automation', 'pageSize': '30', 'pageNumber': '1'}, token='linda01_token')
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    _j1 = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    # 校验1: code 与 message
    assert _j1.get('code') == 200, f"响应code错误：期望200，实际={_j1.get('code')!r}"
    assert _j1.get('message') == 'success', f"响应message错误：期望success，实际={_j1.get('message')!r}"
    # 校验2: data 结构（items 数组 + 分页字段数字类型）
    _d1 = _j1.get('data')
    assert _d1 is not None, "响应缺少data字段"
    assert isinstance(_d1.get('items'), list), f"data.items不是数组格式，实际类型={type(_d1.get('items')).__name__}"
    assert isinstance(_d1.get('totalCount'), (int, float)), f"data.totalCount不是数字，实际={_d1.get('totalCount')!r}"
    assert isinstance(_d1.get('pageSize'), (int, float)), f"data.pageSize不是数字，实际={_d1.get('pageSize')!r}"
    assert isinstance(_d1.get('pageNumber'), (int, float)), f"data.pageNumber不是数字，实际={_d1.get('pageNumber')!r}"
    # 校验3: 核心——所有 items.name 包含搜索关键词 automation
    _items = _d1.get('items') or []
    assert len(_items) > 0, "data.items为空数组，无数据可校验"
    for _i, _task in enumerate(_items):
        _name = _task.get('name') or ''
        assert 'automation' in _name, f"第{_i+1}条任务name不包含automation：{_name}（ID:{_task.get('id') or '无'}）"
    # 校验4: 分页数量一致性（pageNumber=1 且 pageSize>=totalCount 时 items 长度应等于 totalCount）
    if _d1.get('pageNumber') == 1 and _d1.get('pageSize') >= _d1.get('totalCount'):
        assert len(_items) == _d1.get('totalCount'), f"当前页数据量不匹配：期望{_d1.get('totalCount')}条，实际{len(_items)}条"
