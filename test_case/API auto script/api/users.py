"""users —— 用户与账户。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class UsersApi(BaseApi):
    """用户与账户。"""

    domain = "users"

    def me_earning_share_configs(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
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
        config_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        contractId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
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
        contractId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        contractId=None, contractOrderId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /users/self/contracts/{{contractId}}/contract-orders/{{contractOrderId}}"""
        return self._call(
            "PUT", '/users/self/contracts/{{contractId}}/contract-orders/{{contractOrderId}}',
            path_vars=_pv(("contractId", contractId), ("contractOrderId", contractOrderId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
