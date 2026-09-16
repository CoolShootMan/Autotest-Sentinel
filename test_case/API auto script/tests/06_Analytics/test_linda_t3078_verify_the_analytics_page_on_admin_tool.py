"""Migrated from Apifox case #7750601. Source folder: Analytics ."""
# Apifox Case ID: 7750601  (traceability only — not needed to run)
NAME = "Verify the Analytics page on admin tool"
TAGS = ["p0", "analytics", "suite:linda"]
PRIORITY = 0


CASE_ID = 7750601
ENV_NAME = "Release"


import datetime
import json

from typing import Any, TYPE_CHECKING

from core.assertions import expect

if TYPE_CHECKING:  # 仅类型检查期导入：让 ctx.api.<域>.<方法>() 能跳到 api/ 定义
    from core.context import Context


def test_linda_t3078_verify_the_analytics_page_on_admin_tool(ctx: "Context"):
    """Apifox case #7750601: Linda_T3078_Verify_the_Analytics_page_on_admin_tool"""
    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用
    # 动态生成日期范围（对应原 Apifox pre-script 的 formatDate / yesterday 计算）
    _today = datetime.datetime.now()
    _fmt = lambda d: d.strftime('%Y-%m-%d')
    vars['startTime'] = _fmt(_today - datetime.timedelta(days=8))
    vars['endTime'] = _fmt(_today - datetime.timedelta(days=1))
    vars['Yesterday'] = _fmt(_today - datetime.timedelta(days=1))
    vars['dayBeforeYesterday'] = _fmt(_today - datetime.timedelta(days=2))
    vars['threeDaysAgo'] = _fmt(_today - datetime.timedelta(days=3))
    # === Steps ===
    # step 1:
    _resp1 = ctx.api.admin.tracking_post_activities(
        body={
            "postId": ["5972f262-ba27-44fc-91cd-cf1054d632a9"],
            "timeRanges": [{"startTime": "{{startTime}}", "endTime": "{{endTime}}"}],
        },
        token='admin_token',
    )
    # step 2:
    _resp2 = ctx.api.admin.tracking_post_activities(
        body={
            "postString": [
                "https://release.pear.us/lindazhoucurator/post/automation-test-event-with-in-person-delivery-t4251"
            ],
            "timeRanges": [
                {"startTime": "{{Yesterday}}", "endTime": "{{Yesterday}}"},
                {"startTime": "{{dayBeforeYesterday}}", "endTime": "{{dayBeforeYesterday}}"},
                {"startTime": "{{threeDaysAgo}}", "endTime": "{{threeDaysAgo}}"},
            ],
        },
        token='admin_token',
    )
    # === 断言（由 Apifox customScript 翻译，原校验逻辑见文件头注释）===
    # ---- step1: postId 查询 ----
    _j1: dict[str, Any] = _resp1.json() if _resp1.headers.get('content-type', '').startswith('application/json') else {}
    assert _j1.get('code') == 200, f"code应为200，实际={_j1.get('code')!r}"
    assert _j1.get('message') == 'success', f"message应为success，实际={_j1.get('message')!r}"
    _d1: dict[str, Any] = _j1.get('data') or {}
    assert _d1.get('totalCount') == 1, f"totalCount应为1，实际={_d1.get('totalCount')!r}"
    _items1: list[Any] = _d1.get('items') or []
    assert len(_items1) > 0, "data.items 为空数组"
    _det1: dict[str, Any] = _items1[0].get('detail') or {}
    assert _det1.get('title') == 'Automation test Event with In-person delivery', f"title不符，实际={_det1.get('title')!r}"
    assert _det1.get('vanityUrl') == 'lindazhoucurator', f"vanityUrl不符，实际={_det1.get('vanityUrl')!r}"
    assert _det1.get('alias') == 'automation-test-event-with-in-person-delivery-t4251', f"alias不符，实际={_det1.get('alias')!r}"
    _ms1 = (_items1[0].get('mutiStatistics') or [{}])[0]
    _uv1: dict[str, Any] = (_ms1.get('visitors') or {}).get('Total Unique Visitors') or {}
    assert _uv1.get('total') == 0, f"Total Unique Visitors.total 应为0，实际={_uv1.get('total')!r}"
    # ---- step2: postString 查询 ----
    _j2: dict[str, Any] = _resp2.json() if _resp2.headers.get('content-type', '').startswith('application/json') else {}
    assert _j2.get('code') == 200, f"code应为200，实际={_j2.get('code')!r}"
    assert _j2.get('message') == 'success', f"message应为success，实际={_j2.get('message')!r}"
    _d2: dict[str, Any] = _j2.get('data') or {}
    assert isinstance(_d2.get('totalCount'), (int, float)) and _d2.get('totalCount') >= 0, f"totalCount应为非负数字，实际={_d2.get('totalCount')!r}"
    _items2: list[Any] = _d2.get('items') or []
    assert len(_items2) > 0, "data.items 为空数组"
    _it2 = _items2[0]
    assert _it2.get('detail') is not None, "第一个item的detail字段缺失"
    _ms2: list[Any] = _it2.get('mutiStatistics') or []
    assert len(_ms2) == 3, f"mutiStatistics 长度应为3，实际={len(_ms2)}"
    _det2: dict[str, Any] = _it2.get('detail') or {}
    assert _det2.get('title') == 'Automation test Event with In-person delivery', f"title不符，实际={_det2.get('title')!r}"
    assert _det2.get('vanityUrl') == 'lindazhoucurator', f"vanityUrl不符，实际={_det2.get('vanityUrl')!r}"
    assert _det2.get('alias') == 'automation-test-event-with-in-person-delivery-t4251', f"alias不符，实际={_det2.get('alias')!r}"
    for _i, _stat in enumerate(_ms2):
        _vis: dict[str, Any] = (_stat.get('visitors') or {}).get('Total Unique Visitors') or {}
        assert isinstance(_vis.get('total'), (int, float)) and _vis.get('total') >= 0, f"第{_i+1}组访客总数非法：{_vis.get('total')!r}"
        for _dn, _dv in (_stat.get('devices') or {}).items():
            _dt = (_dv or {}).get('total')
            assert isinstance(_dt, (int, float)) and _dt >= 0, f"第{_i+1}组devices[{_dn}].total非法：{_dt!r}"
        for _pn, _pv in (_stat.get('platforms') or {}).items():
            _pt = (_pv or {}).get('total')
            assert isinstance(_pt, (int, float)) and _pt >= 0, f"第{_i+1}组platforms[{_pn}].total非法：{_pt!r}"
        assert _stat.get('orderQuantity') == 0, f"第{_i+1}组orderQuantity应为0，实际={_stat.get('orderQuantity')!r}"
