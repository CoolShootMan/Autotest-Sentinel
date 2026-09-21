"""users —— 用户与账户。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 仅类型检查期导入：避免 api ↔ core 运行期循环依赖
    from core.response import ApiResponse

from api.base import BaseApi, _pv


class UsersApi(BaseApi):
    """用户与账户。"""

    domain = "users"

    def me_earning_share_configs(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /users/me/earning-share-configs"""
        return self._call(
            "POST", '/users/me/earning-share-configs',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def me_earning_share_configs_by_config_id(
        self, *,
        config_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """DELETE /users/me/earning-share-configs/{{config_id}}"""
        return self._call(
            "DELETE", '/users/me/earning-share-configs/{{config_id}}',
            path_vars=_pv(("config_id", config_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def me_recipient_earning_shares(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /users/me/recipient-earning-shares"""
        return self._call(
            "GET", '/users/me/recipient-earning-shares',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def self_contracts(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /users/self/contracts/  （用例中出现 5 次）"""
        return self._call(
            "GET", '/users/self/contracts/',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def self_contracts_by_contract_id(
        self, *,
        contractId: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /users/self/contracts/{{contractId}}  （用例中出现 6 次）"""
        return self._call(
            "PUT", '/users/self/contracts/{{contractId}}',
            path_vars=_pv(("contractId", contractId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def self_contracts_by_contract_id_2(
        self, *,
        contractId: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /users/self/contracts/{{contractId}}  （用例中出现 5 次）"""
        return self._call(
            "GET", '/users/self/contracts/{{contractId}}',
            path_vars=_pv(("contractId", contractId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def self_contracts_contract_orders_by_contract_order_id(
        self, *,
        contractId: str | None = None, contractOrderId: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /users/self/contracts/{{contractId}}/contract-orders/{{contractOrderId}}"""
        return self._call(
            "PUT", '/users/self/contracts/{{contractId}}/contract-orders/{{contractOrderId}}',
            path_vars=_pv(("contractId", contractId), ("contractOrderId", contractOrderId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    # --- UI Automation Data Pre-configuration 专用接口 ---------------

    def delete_by_user_id(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """DELETE /users/{{user_id}}"""
        return self._call(
            "DELETE", '/users/{{user_id}}',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def set_password(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /users/{{user_id}}/password"""
        return self._call(
            "PUT", '/users/{{user_id}}/password',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def external_user_import_partner(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /users/tool/external-user-import/partner"""
        return self._call(
            "POST", '/users/tool/external-user-import/partner',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def external_user_import_promoter(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /users/tool/external-user-import/promoter"""
        return self._call(
            "POST", '/users/tool/external-user-import/promoter',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter_associations_connect(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /users/promoter-associations/connect/{{user_id}}"""
        return self._call(
            "POST", '/users/promoter-associations/connect/{{user_id}}',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def update_feature_flags(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH /users/tool/feature-flags"""
        return self._call(
            "PATCH", '/users/tool/feature-flags',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def update_by_user_id(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH /users/{{user_id}}"""
        return self._call(
            "PATCH", '/users/{{user_id}}',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def search(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /users/search"""
        return self._call(
            "POST", '/users/search',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def set_api_platform_credentials(
        self, *,
        user_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /users/{{user_id}}/api-platform-credentials"""
        return self._call(
            "PUT", '/users/{{user_id}}/api-platform-credentials',
            path_vars=_pv(("user_id", user_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
