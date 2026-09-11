"""events —— 活动与票务。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class EventsApi(BaseApi):
    """活动与票务。"""

    domain = "events"

    def bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_orders_summary(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/orders/summary  （用例中出现 2 次）"""
        return self._call(
            "GET", '/product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/orders/summary',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_staff(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/staff"""
        return self._call(
            "GET", '/product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/staff',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_staff_summary(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/staff-summary"""
        return self._call(
            "GET", '/product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/staff-summary',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_summary(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/summary"""
        return self._call(
            "GET", '/product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/summary',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def bdc4f6e7_8f5d_4dae_8c2b_d7ae1b43b320_metrics_tipped_orders(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/tipped-orders"""
        return self._call(
            "GET", '/product-event/bdc4f6e7-8f5d-4dae-8c2b-d7ae1b43b320/metrics/tipped-orders',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def bea4cfb9_a9a6_4a1f_a1a8_96f7e9418d03_metrics_promoters(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/bea4cfb9-a9a6-4a1f-a1a8-96f7e9418d03/metrics/promoters"""
        return self._call(
            "GET", '/product-event/bea4cfb9-a9a6-4a1f-a1a8-96f7e9418d03/metrics/promoters',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def bea4cfb9_a9a6_4a1f_a1a8_96f7e9418d03_metrics_summary(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/bea4cfb9-a9a6-4a1f-a1a8-96f7e9418d03/metrics/summary"""
        return self._call(
            "GET", '/product-event/bea4cfb9-a9a6-4a1f-a1a8-96f7e9418d03/metrics/summary',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def by_co_hostid(
        self, *,
        co_hostid=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /event-collaborators/{{co-hostid}}  （用例中出现 3 次）"""
        return self._call(
            "DELETE", '/event-collaborators/{{co-hostid}}',
            path_vars=_pv(("co-hostid", co_hostid), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def collaborators(
        self, *,
        eventId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /event-collaborators?eventId={{eventId}}  （人工补充）

        未出现在 Apifox 用例里 —— 原始用例不需要（当时环境干净）。补它的目的：
        「先增后删」的协办人用例一旦中途失败就会永久遗留记录，此后 POST 恒返回
        409 且不回传已存在记录的 id，用例无法自愈。有了列表端点才能先清理。
        """
        merged = dict(params or {})
        if eventId is not None:
            merged.setdefault("eventId", eventId)
        return self._call(
            "GET", '/event-collaborators',
            params=merged or None,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
            path_vars=path_vars,
        )

    def by_dup_event_id(
        self, *,
        dup_event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /product-event/{{dup_event_id}}  （用例中出现 9 次）"""
        return self._call(
            "PUT", '/product-event/{{dup_event_id}}',
            path_vars=_pv(("dup_event_id", dup_event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def by_event_id(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /product-event/{{event_id}}  （用例中出现 6 次）"""
        return self._call(
            "DELETE", '/product-event/{{event_id}}',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def create(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /event-collaborators  （用例中出现 3 次）"""
        return self._call(
            "POST", '/event-collaborators',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def dad4b563_4eaf_47cd_a825_e63d61e48de1_metrics_discount_orders(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/dad4b563-4eaf-47cd-a825-e63d61e48de1/metrics/discount-orders"""
        return self._call(
            "GET", '/product-event/dad4b563-4eaf-47cd-a825-e63d61e48de1/metrics/discount-orders',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def dad4b563_4eaf_47cd_a825_e63d61e48de1_metrics_orders_summary(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/dad4b563-4eaf-47cd-a825-e63d61e48de1/metrics/orders/summary"""
        return self._call(
            "GET", '/product-event/dad4b563-4eaf-47cd-a825-e63d61e48de1/metrics/orders/summary',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def dad4b563_4eaf_47cd_a825_e63d61e48de1_metrics_summary(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/dad4b563-4eaf-47cd-a825-e63d61e48de1/metrics/summary"""
        return self._call(
            "GET", '/product-event/dad4b563-4eaf-47cd-a825-e63d61e48de1/metrics/summary',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def default_catalog(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/default-catalog  （用例中出现 10 次）"""
        return self._call(
            "GET", '/product-event/default-catalog',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def fb5df095_b68d_45f6_adc0_2211428d0a8c_metrics_summary(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/fb5df095-b68d-45f6-adc0-2211428d0a8c/metrics/summary  （用例中出现 2 次）"""
        return self._call(
            "GET", '/product-event/fb5df095-b68d-45f6-adc0-2211428d0a8c/metrics/summary',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def guests(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /event/guests  （用例中出现 3 次）"""
        return self._call(
            "POST", '/event/guests',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def guests_batch(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /event/{{event_id}}/guests/batch  （用例中出现 3 次）"""
        return self._call(
            "DELETE", '/event/{{event_id}}/guests/batch',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def lineup(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/{{event_id}}/lineup"""
        return self._call(
            "POST", '/product-event/{{event_id}}/lineup',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def lineup_by_lineup_id(
        self, *,
        event_id=None, lineup_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /product-event/{{event_id}}/lineup/{{lineup_id}}  （用例中出现 2 次）"""
        return self._call(
            "PUT", '/product-event/{{event_id}}/lineup/{{lineup_id}}',
            path_vars=_pv(("event_id", event_id), ("lineup_id", lineup_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def lineup_l_lineup_id(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /product-event/{{event_id}}/lineup/{l{lineup_id}}

        .. warning:: 路径含畸形占位符（迁移遗留），已原样保留。"""
        return self._call(
            "DELETE", '/product-event/{{event_id}}/lineup/{l{lineup_id}}',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def lineup_transactions(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/{{event_id}}/lineup-transactions"""
        return self._call(
            "POST", '/product-event/{{event_id}}/lineup-transactions',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def list(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/list  （用例中出现 23 次）"""
        return self._call(
            "GET", '/product-event/list',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def metrics_summary(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/{{event_id}}/metrics/summary  （用例中出现 2 次）"""
        return self._call(
            "GET", '/product-event/{{event_id}}/metrics/summary',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def tickets_venue_units(
        self, *,
        productId_General_Admission_02=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/tickets/{{productId_General_Admission_02}}/venue-units  （用例中出现 4 次）"""
        return self._call(
            "GET", '/product-event/tickets/{{productId_General_Admission_02}}/venue-units',
            path_vars=_pv(("productId_General_Admission_02", productId_General_Admission_02), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2  （用例中出现 5 次）"""
        return self._call(
            "POST", '/product-event/v2',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_1a2e22e6_076a_4176_949b_7ab63a149b3f_lineup_batch(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2/1a2e22e6-076a-4176-949b-7ab63a149b3f/lineup/batch"""
        return self._call(
            "POST", '/product-event/v2/1a2e22e6-076a-4176-949b-7ab63a149b3f/lineup/batch',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_1a2e22e6_076a_4176_949b_7ab63a149b3f_media_batch_operate(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2/1a2e22e6-076a-4176-949b-7ab63a149b3f/media/batch/operate"""
        return self._call(
            "POST", '/product-event/v2/1a2e22e6-076a-4176-949b-7ab63a149b3f/media/batch/operate',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_config(
        self, *,
        created_event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/v2/{{created_event_id}}/config"""
        return self._call(
            "GET", '/product-event/v2/{{created_event_id}}/config',
            path_vars=_pv(("created_event_id", created_event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_duplicate(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2/duplicate  （用例中出现 2 次）"""
        return self._call(
            "POST", '/product-event/v2/duplicate',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_lineup_batch(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2/{{event_id}}/lineup/batch  （用例中出现 4 次）"""
        return self._call(
            "POST", '/product-event/v2/{{event_id}}/lineup/batch',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_media_batch_create(
        self, *,
        created_event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2/{{created_event_id}}/media/batch/create"""
        return self._call(
            "POST", '/product-event/v2/{{created_event_id}}/media/batch/create',
            path_vars=_pv(("created_event_id", created_event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_media_batch_operate(
        self, *,
        newMediaId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2/{{newMediaId}}/media/batch/operate"""
        return self._call(
            "POST", '/product-event/v2/{{newMediaId}}/media/batch/operate',
            path_vars=_pv(("newMediaId", newMediaId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_show_in_post(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2/{{event_id}}/show-in-post  （用例中出现 4 次）"""
        return self._call(
            "POST", '/product-event/v2/{{event_id}}/show-in-post',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v2_ticket_batch_v2(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /product-event/v2/{{event_id}}/ticket/batch/v2  （用例中出现 5 次）"""
        return self._call(
            "POST", '/product-event/v2/{{event_id}}/ticket/batch/v2',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_1a2e22e6_076a_4176_949b_7ab63a149b3f_lineup_by_lineup_id(
        self, *,
        lineup_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /product-event/1a2e22e6-076a-4176-949b-7ab63a149b3f/lineup/{{lineup_id}}"""
        return self._call(
            "DELETE", '/product-event/1a2e22e6-076a-4176-949b-7ab63a149b3f/lineup/{{lineup_id}}',
            path_vars=_pv(("lineup_id", lineup_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_39014a10_14e7_4cfa_993b_485f5c5485ac_metrics_summary(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /product-event/39014a10-14e7-4cfa-993b-485f5c5485ac/metrics/summary"""
        return self._call(
            "GET", '/product-event/39014a10-14e7-4cfa-993b-485f5c5485ac/metrics/summary',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
