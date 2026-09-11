"""promoters —— 推广者与分销。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class PromotersApi(BaseApi):
    """推广者与分销。"""

    domain = "promoters"

    def affiliate_link_notification_batch(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /promoter-association/affiliate-link/notification/batch  （用例中出现 2 次）"""
        return self._call(
            "POST", '/promoter-association/affiliate-link/notification/batch',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def affiliate_promoters(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /promoter-association/affiliate-promoters"""
        return self._call(
            "GET", '/promoter-association/affiliate-promoters',
            path_vars=path_vars,
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
        """POST /promoter-subscription  （用例中出现 2 次）"""
        return self._call(
            "POST", '/promoter-subscription',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_affiliate_link(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /promoter-association/curator/affiliate-link  （用例中出现 2 次）"""
        return self._call(
            "POST", '/promoter-association/curator/affiliate-link',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def invitation_link(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /promoter-invitation-link/invitation-link  （用例中出现 2 次）"""
        return self._call(
            "GET", '/promoter-invitation-link/invitation-link',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def invitation_link_2(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /promoter-invitation-link/invitation-link"""
        return self._call(
            "POST", '/promoter-invitation-link/invitation-link',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def invitation_link_by_new_invitation_link(
        self, *,
        new_invitation_link=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /promoter-invitation-link/invitation-link/{{new_invitation_link}}"""
        return self._call(
            "DELETE", '/promoter-invitation-link/invitation-link/{{new_invitation_link}}',
            path_vars=_pv(("new_invitation_link", new_invitation_link), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def product_image_url(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /promoter/product/image-url"""
        return self._call(
            "POST", '/promoter/product/image-url',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PATCH /promote-invitation/promoter"""
        return self._call(
            "PATCH", '/promote-invitation/promoter',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
