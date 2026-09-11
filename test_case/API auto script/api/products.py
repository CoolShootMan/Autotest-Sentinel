"""products —— 商品。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class ProductsApi(BaseApi):
    """商品。"""

    domain = "products"

    def batch(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /v2/products/batch"""
        return self._call(
            "POST", '/v2/products/batch',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def by_newticketid(
        self, *,
        newticketid=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /v2/products/{{newticketid}}  （用例中出现 3 次）"""
        return self._call(
            "DELETE", '/v2/products/{{newticketid}}',
            path_vars=_pv(("newticketid", newticketid), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def by_product_id(
        self, *,
        productId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /merchant/product/{{productId}}  （用例中出现 2 次）"""
        return self._call(
            "DELETE", '/merchant/product/{{productId}}',
            path_vars=_pv(("productId", productId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def by_product_id_2(
        self, *,
        productId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /merchant/product/{{productId}}"""
        return self._call(
            "GET", '/merchant/product/{{productId}}',
            path_vars=_pv(("productId", productId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def by_product_id_general_admission_02(
        self, *,
        productId_General_Admission_02=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /v2/products/{{productId_General_Admission_02}}  （用例中出现 5 次）"""
        return self._call(
            "PUT", '/v2/products/{{productId_General_Admission_02}}',
            path_vars=_pv(("productId_General_Admission_02", productId_General_Admission_02), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def calculate_ticket_batch(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /merchant/product/calculate/ticket/batch  （用例中出现 4 次）"""
        return self._call(
            "POST", '/merchant/product/calculate/ticket/batch',
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
        """POST /v2/products  （用例中出现 8 次）"""
        return self._call(
            "POST", '/v2/products',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def exist_product(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /merchant/product/exist-product"""
        return self._call(
            "GET", '/merchant/product/exist-product',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def f0a91cf5_c585_45d9_8b08_f59a6941e6d8(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /v2/products/f0a91cf5-c585-45d9-8b08-f59a6941e6d8  （用例中出现 2 次）"""
        return self._call(
            "PUT", '/v2/products/f0a91cf5-c585-45d9-8b08-f59a6941e6d8',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def list(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /merchant/product/list"""
        return self._call(
            "GET", '/merchant/product/list',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_2efee169_7e73_4d20_8d56_d99d7f4ab699(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /v2/products/2efee169-7e73-4d20-8d56-d99d7f4ab699  （用例中出现 2 次）"""
        return self._call(
            "PUT", '/v2/products/2efee169-7e73-4d20-8d56-d99d7f4ab699',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_50cfb015_c43d_463e_8357_4556d592bf26(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /v2/products/50cfb015-c43d-463e-8357-4556d592bf26"""
        return self._call(
            "PUT", '/v2/products/50cfb015-c43d-463e-8357-4556d592bf26',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def v_5589beae_d2ca_40fc_b361_03122952beb2(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /v2/products/5589beae-d2ca-40fc-b361-03122952beb2  （用例中出现 2 次）"""
        return self._call(
            "PUT", '/v2/products/5589beae-d2ca-40fc-b361-03122952beb2',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
