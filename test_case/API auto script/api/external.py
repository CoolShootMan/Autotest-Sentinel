"""external —— 外部依赖（Stripe 等，仅联调）。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class ExternalApi(BaseApi):
    """外部依赖（Stripe 等，仅联调）。"""

    domain = "external"

    def demi_release_post_538yja(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET https://release.notip.com.cn/demi-release/post/538yja

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://release.notip.com.cn/demi-release/post/538yja',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def lindazhou_curator(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET https://release.notip.com.cn/lindazhouCurator

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://release.notip.com.cn/lindazhouCurator',
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
        """GET https://release.notip.com.cn/

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://release.notip.com.cn/',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v1_setup_intents_confirm(
        self, *,
        Stripeid=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST https://api.stripe.com/v1/setup_intents/{{Stripeid}}/confirm

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "POST", 'https://api.stripe.com/v1/setup_intents/{{Stripeid}}/confirm',
            path_vars=_pv(("Stripeid", Stripeid), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_1129(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET https://demi0214.notip.com.cn/1129

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://demi0214.notip.com.cn/1129',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_1129_2(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET https://release.notip.com.cn/1129

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://release.notip.com.cn/1129',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
