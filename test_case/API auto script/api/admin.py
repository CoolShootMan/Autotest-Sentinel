"""admin —— 管理后台接口（{{adminurl}}）。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class AdminApi(BaseApi):
    """管理后台接口（{{adminurl}}）。"""

    domain = "admin"

    def auth_login(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST {{adminurl}}/auth/login  （用例中出现 5 次）"""
        return self._call(
            "POST", '{{adminurl}}/auth/login',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def events_by_dup_event_id(
        self, *,
        dup_event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PATCH {{adminurl}}/events/{{dup_event_id}}  （用例中出现 5 次）"""
        return self._call(
            "PATCH", '{{adminurl}}/events/{{dup_event_id}}',
            path_vars=_pv(("dup_event_id", dup_event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def events_search(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST {{adminurl}}/events/search"""
        return self._call(
            "POST", '{{adminurl}}/events/search',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def merchant_product_by_product_id(
        self, *,
        productId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PATCH {{adminurl}}/merchant/product/{{productId}}"""
        return self._call(
            "PATCH", '{{adminurl}}/merchant/product/{{productId}}',
            path_vars=_pv(("productId", productId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def orders_refunds(
        self, *,
        admin_orderId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST {{adminurl}}/orders/{{admin_orderId}}/refunds  （用例中出现 8 次）"""
        return self._call(
            "POST", '{{adminurl}}/orders/{{admin_orderId}}/refunds',
            path_vars=_pv(("admin_orderId", admin_orderId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def orders_search(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST {{adminurl}}/orders/search  （用例中出现 5 次）"""
        return self._call(
            "POST", '{{adminurl}}/orders/search',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def post_v2_relate_products(
        self, *,
        post0_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET {{adminurl}}/post/v2/{{post0_id}}/relate-products  （用例中出现 12 次）"""
        return self._call(
            "GET", '{{adminurl}}/post/v2/{{post0_id}}/relate-products',
            path_vars=_pv(("post0_id", post0_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoters_reward(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST {{adminurl}}/promoters/reward"""
        return self._call(
            "POST", '{{adminurl}}/promoters/reward',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoters_reward_by_promoter_id(
        self, *,
        promoterId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET {{adminurl}}/promoters/reward/{{promoterId}}"""
        return self._call(
            "GET", '{{adminurl}}/promoters/reward/{{promoterId}}',
            path_vars=_pv(("promoterId", promoterId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def tracking_post_activities(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST {{adminurl}}/tracking/post/activities  （用例中出现 2 次）"""
        return self._call(
            "POST", '{{adminurl}}/tracking/post/activities',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_search(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST {{adminurl}}/users/search"""
        return self._call(
            "POST", '{{adminurl}}/users/search',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
