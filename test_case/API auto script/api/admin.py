"""admin —— 管理后台接口（{{adminurl}}）。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 仅类型检查期导入：避免 api ↔ core 运行期循环依赖
    from core.response import ApiResponse

from api.base import BaseApi, _pv


class AdminApi(BaseApi):
    """管理后台接口（{{adminurl}}）。"""

    domain = "admin"

    def auth_login(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        dup_event_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        productId: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH {{adminurl}}/merchant/product/{{productId}}"""
        return self._call(
            "PATCH", '{{adminurl}}/merchant/product/{{productId}}',
            path_vars=_pv(("productId", productId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def merchant_product_search(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET {{adminurl}}/merchant/product/search?pageSize=&eventId=

        注意：该接口只存在于 admin 域——base 域带 admin_token 返回 401、
        带 {{token}}(999) 返回 500（Inconsistent column data: Error creating UUID，
        因为缺少 eventId 时后端拿不到合法 UUID）。需 admin_token。
        """
        return self._call(
            "GET", '{{adminurl}}/merchant/product/search',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def orders_refunds(
        self, *,
        admin_orderId: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/orders/search  （用例中出现 5 次）"""
        return self._call(
            "POST", '{{adminurl}}/orders/search',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def post_by_post_id(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH {{adminurl}}/post/{{post_id}}"""
        return self._call(
            "PATCH", '{{adminurl}}/post/{{post_id}}',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def post_children(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET {{adminurl}}/post/{{post_id}}/children"""
        return self._call(
            "GET", '{{adminurl}}/post/{{post_id}}/children',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def post_v2_relate_products(
        self, *,
        post0_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        promoterId: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
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
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/tracking/post/activities  （用例中出现 2 次）"""
        return self._call(
            "POST", '{{adminurl}}/tracking/post/activities',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_by_user_id(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """DELETE {{adminurl}}/users/{{user_id}}"""
        return self._call(
            "DELETE", '{{adminurl}}/users/{{user_id}}',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_password(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT {{adminurl}}/users/{{user_id}}/password"""
        return self._call(
            "PUT", '{{adminurl}}/users/{{user_id}}/password',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_promoter_associations_connect_by_user_id(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/users/promoter-associations/connect/{{user_id}}"""
        return self._call(
            "POST", '{{adminurl}}/users/promoter-associations/connect/{{user_id}}',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_search(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/users/search"""
        return self._call(
            "POST", '{{adminurl}}/users/search',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_tool_external_user_import_partner(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/users/tool/external-user-import/partner"""
        return self._call(
            "POST", '{{adminurl}}/users/tool/external-user-import/partner',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_tool_external_user_import_promoter(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/users/tool/external-user-import/promoter"""
        return self._call(
            "POST", '{{adminurl}}/users/tool/external-user-import/promoter',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_tool_feature_flags(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH {{adminurl}}/users/tool/feature-flags?userId=...

        注意：该接口只存在于 admin 域（base 域 PATCH /users/tool/feature-flags 返回
        404 Cannot PATCH），且 **必须** 带 ?userId=，缺失时后端 500
        （Inconsistent column data: Error creating UUID）。调用方需传
        params={"userId": <用户 id>}，并使用 admin_token。
        """
        return self._call(
            "PATCH", '{{adminurl}}/users/tool/feature-flags',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    # ------------------------------------------------------------------
    # venue-map 系列（管理后台侧）
    #
    # 注意：这三个接口只存在于 admin 域。base 域 POST /events/{{id}}/venue-map
    # 返回 404（Cannot POST），带 {{token}}(999) 走 admin 域返回 401。
    # 只有 admin 域 + admin_token 返回 201/200，因此统一放在 admin 门面下。
    # 调用方需传 path_vars={"venue_map_event_id": <event id>} 或关键字参数。
    # ------------------------------------------------------------------

    def events_venue_map_create(
        self, *,
        venue_map_event_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/events/{{venue_map_event_id}}/venue-map（需 admin_token）"""
        return self._call(
            "POST", '{{adminurl}}/events/{{venue_map_event_id}}/venue-map',
            path_vars=_pv(("venue_map_event_id", venue_map_event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def events_venue_map_associations(
        self, *,
        venue_map_event_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/events/{{venue_map_event_id}}/venue-map/associations（需 admin_token）"""
        return self._call(
            "POST", '{{adminurl}}/events/{{venue_map_event_id}}/venue-map/associations',
            path_vars=_pv(("venue_map_event_id", venue_map_event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def events_venue_map_publish(
        self, *,
        venue_map_event_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/events/{{venue_map_event_id}}/venue-map/publish（需 admin_token）"""
        return self._call(
            "POST", '{{adminurl}}/events/{{venue_map_event_id}}/venue-map/publish',
            path_vars=_pv(("venue_map_event_id", venue_map_event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    # ------------------------------------------------------------------
    # 用户管理 + ticket-hub（TDC / AXS）系列
    #
    # 实测（Release 环境，用 SUPER_ADMIN 的 admin_token 逐一探测）：
    #   - PATCH {{adminurl}}/users/{id}                          → 200
    #     （base 域同路径 → 404 Cannot PATCH）
    #   - PUT   {{adminurl}}/users/{id}/api-platform-credentials → 400/200
    #     （base 域 → 404 Cannot PUT，说明路由只在 admin 域）
    #   - GET   {{adminurl}}/events/ticket-hub/discovery         → 503/200
    #     （base 域 → 404 Cannot GET）
    #   - POST  {{adminurl}}/events/ticket-hub/check-imported    → 201
    #   - POST  {{adminurl}}/events/ticket-hub/import            → 200/500
    #     （base 域 → 404 Cannot POST）
    # 即：这五个接口都只在 admin 域存在，且都需要 admin_token。
    # discovery 必须带 ?userId=<用户>&platform=TDC|AXS，否则后端 503。
    # ------------------------------------------------------------------

    def users_update_by_user_id(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH {{adminurl}}/users/{{user_id}}（需 admin_token）"""
        return self._call(
            "PATCH", '{{adminurl}}/users/{{user_id}}',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def users_api_platform_credentials(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT {{adminurl}}/users/{{user_id}}/api-platform-credentials（需 admin_token）"""
        return self._call(
            "PUT", '{{adminurl}}/users/{{user_id}}/api-platform-credentials',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def events_ticket_hub_discovery(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET {{adminurl}}/events/ticket-hub/discovery?userId=&platform=（需 admin_token）"""
        return self._call(
            "GET", '{{adminurl}}/events/ticket-hub/discovery',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def events_ticket_hub_check_imported(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/events/ticket-hub/check-imported（需 admin_token，HTTP 201）"""
        return self._call(
            "POST", '{{adminurl}}/events/ticket-hub/check-imported',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def events_ticket_hub_import(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST {{adminurl}}/events/ticket-hub/import（需 admin_token）"""
        return self._call(
            "POST", '{{adminurl}}/events/ticket-hub/import',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
