"""cart —— 购物车。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class CartApi(BaseApi):
    """购物车。"""

    domain = "cart"

    def delete(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /cart  （用例中出现 81 次）"""
        return self._call(
            "DELETE", '/cart',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def list(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /cart  （用例中出现 6 次）"""
        return self._call(
            "GET", '/cart',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def update(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /cart  （用例中出现 15 次）"""
        return self._call(
            "PUT", '/cart',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
