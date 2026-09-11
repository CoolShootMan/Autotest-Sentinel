"""storefront —— 店铺装修。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class StorefrontApi(BaseApi):
    """店铺装修。"""

    domain = "storefront"

    def module(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /store-front/module"""
        return self._call(
            "POST", '/store-front/module',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def module_by_dynamic_music_link_id(
        self, *,
        dynamicMusicLinkId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /store-front/module/{{dynamicMusicLinkId}}"""
        return self._call(
            "DELETE", '/store-front/module/{{dynamicMusicLinkId}}',
            path_vars=_pv(("dynamicMusicLinkId", dynamicMusicLinkId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def module_item_by_dynamic_music_link_id(
        self, *,
        dynamicMusicLinkId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /store-front/module-item/{{dynamicMusicLinkId}}"""
        return self._call(
            "PUT", '/store-front/module-item/{{dynamicMusicLinkId}}',
            path_vars=_pv(("dynamicMusicLinkId", dynamicMusicLinkId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
