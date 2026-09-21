"""merchants —— 商户。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 仅类型检查期导入：避免 api ↔ core 运行期循环依赖
    from core.response import ApiResponse

from api.base import BaseApi, _pv


class MerchantsApi(BaseApi):
    """商户。"""

    domain = "merchants"

    def by_merchant_id(
        self, *,
        merchantId: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        catalog_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /merchant/822a3e59-fdf3-4d9b-be57-f8f0b3af1023/sync-shopify-shipping"""
        return self._call(
            "POST", '/merchant/822a3e59-fdf3-4d9b-be57-f8f0b3af1023/sync-shopify-shipping',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    # --- UI Automation Data Pre-configuration 专用接口 ---------------

    def shipping_options_by_merchant_id(
        self, *,
        merchant_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /merchants/{{merchant_id}}/shipping-options"""
        return self._call(
            "GET", '/merchants/{{merchant_id}}/shipping-options',
            path_vars=_pv(("merchant_id", merchant_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def shipping_options_update(
        self, *,
        merchant_id: str | None = None,
        shipping_option_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /merchants/{{merchant_id}}/shipping-options/{{shipping_option_id}}"""
        return self._call(
            "PUT", '/merchants/{{merchant_id}}/shipping-options/{{shipping_option_id}}',
            path_vars=_pv(("merchant_id", merchant_id), ("shipping_option_id", shipping_option_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
