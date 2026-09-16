"""misc —— 其它。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 仅类型检查期导入：避免 api ↔ core 运行期循环依赖
    from core.response import ApiResponse

from api.base import BaseApi, _pv


class MiscApi(BaseApi):
    """其它。"""

    domain = "misc"

    def earnings_merchant_orders(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /earnings-merchant-orders  （用例中出现 3 次）"""
        return self._call(
            "GET", '/earnings-merchant-orders',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def earnings_promoter_orders(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /earnings-promoter-orders  （用例中出现 2 次）"""
        return self._call(
            "GET", '/earnings-promoter-orders',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def invitation_profile(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST https://release.pear.us/invitation/profile

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "POST", 'https://release.pear.us/invitation/profile',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def linda_post_lindapromoter(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET https://release.pear.us/linda/post/lindapromoter

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://release.pear.us/linda/post/lindapromoter',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def list(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET https://mehost.cn/

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://mehost.cn/',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def submit(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /user-contact-form/submit"""
        return self._call(
            "POST", '/user-contact-form/submit',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def user_business_operation(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /user/business-operation  （用例中出现 4 次）"""
        return self._call(
            "PUT", '/user/business-operation',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
