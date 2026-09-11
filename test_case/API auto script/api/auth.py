"""auth —— 鉴权（登录 / 注册 / 验证码）。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class AuthApi(BaseApi):
    """鉴权（登录 / 注册 / 验证码）。"""

    domain = "auth"

    def code(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /auth/code  （用例中出现 2 次）"""
        return self._call(
            "POST", '/auth/code',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def guest_login(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /auth/guest-login  （用例中出现 28 次）"""
        return self._call(
            "POST", '/auth/guest-login',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def merchant_login(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /auth/merchant-login"""
        return self._call(
            "POST", '/auth/merchant-login',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter_login(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /auth/promoter-login  （用例中出现 2 次）"""
        return self._call(
            "POST", '/auth/promoter-login',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter_signup(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /auth/promoter-signup  （用例中出现 2 次）"""
        return self._call(
            "POST", '/auth/promoter-signup',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def sign_in(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """POST /auth/sign-in  （用例中出现 188 次）"""
        return self._call(
            "POST", '/auth/sign-in',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
