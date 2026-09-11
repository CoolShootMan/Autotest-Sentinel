"""merchants —— 商户。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class MerchantsApi(BaseApi):
    """商户。"""

    domain = "merchants"

    def by_merchant_id(
        self, *,
        merchantId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /merchant/{{merchantId}}"""
        return self._call(
            "DELETE", '/merchant/{{merchantId}}',
            path_vars=_pv(("merchantId", merchantId), extra=path_vars),
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
        """POST /merchant"""
        return self._call(
            "POST", '/merchant',
            path_vars=path_vars,
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
        """GET /merchant/list"""
        return self._call(
            "GET", '/merchant/list',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def shipping_options(
        self, *,
        catalog_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /merchants/{{catalog_id}}/shipping-options  （用例中出现 2 次）"""
        return self._call(
            "GET", '/merchants/{{catalog_id}}/shipping-options',
            path_vars=_pv(("catalog_id", catalog_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_7c2db5d2_92f0_4090_a1ef_55a811b12a6f_subscription_plan_693b2288_c958_4312_92a9_910b948bb6c3(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /merchants/7c2db5d2-92f0-4090-a1ef-55a811b12a6f/subscription-plan/693b2288-c958-4312-92a9-910b948bb6c3"""
        return self._call(
            "PUT", '/merchants/7c2db5d2-92f0-4090-a1ef-55a811b12a6f/subscription-plan/693b2288-c958-4312-92a9-910b948bb6c3',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_822a3e59_fdf3_4d9b_be57_f8f0b3af1023_sync_shopify_shipping(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /merchant/822a3e59-fdf3-4d9b-be57-f8f0b3af1023/sync-shopify-shipping"""
        return self._call(
            "POST", '/merchant/822a3e59-fdf3-4d9b-be57-f8f0b3af1023/sync-shopify-shipping',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
