"""orders —— 订单（下单 / 结算 / 履约 / 退款）。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class OrdersApi(BaseApi):
    """订单（下单 / 结算 / 履约 / 退款）。"""

    domain = "orders"

    def buy_now(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """POST /order/buy-now  （用例中出现 75 次）"""
        return self._call(
            "POST", '/order/buy-now',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def checkout(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """POST /order/checkout  （用例中出现 7 次）"""
        return self._call(
            "POST", '/order/checkout',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def checkout_2(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/checkout"""
        return self._call(
            "GET", '/order/checkout',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def checkout_express(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """POST /order/checkout/express  （用例中出现 21 次）"""
        return self._call(
            "POST", '/order/checkout/express',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def consumer(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/consumer  （用例中出现 2 次）"""
        return self._call(
            "GET", '/order/consumer',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def consumer_detail_by_order_number(
        self, *,
        orderNumber=None,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/consumer/detail/{{orderNumber}}  （用例中出现 18 次）"""
        return self._call(
            "GET", '/order/consumer/detail/{{orderNumber}}',
            path_vars=_pv(("orderNumber", orderNumber), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def create(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=True,
        path_vars=None,
    ):
        """POST /order  （用例中出现 77 次）"""
        return self._call(
            "POST", '/order',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def fulfillment_merchant_by_order_number(
        self, *,
        merchantId=None, orderNumber=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /orders/fulfillment/merchant/{{merchantId}}/{{orderNumber}}  （用例中出现 3 次）"""
        return self._call(
            "POST", '/orders/fulfillment/merchant/{{merchantId}}/{{orderNumber}}',
            path_vars=_pv(("merchantId", merchantId), ("orderNumber", orderNumber), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def merchant(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/merchant  （用例中出现 19 次）"""
        return self._call(
            "GET", '/order/merchant',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def merchant_bed7b1d8_16d8_4d27_ab1a_dc4a8f19e0c6_detail_v2(
        self, *,
        orderNumber=None,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/merchant/bed7b1d8-16d8-4d27-ab1a-dc4a8f19e0c6/detail/{{orderNumber}}/v2  （用例中出现 3 次）"""
        return self._call(
            "GET", '/order/merchant/bed7b1d8-16d8-4d27-ab1a-dc4a8f19e0c6/detail/{{orderNumber}}/v2',
            path_vars=_pv(("orderNumber", orderNumber), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def merchant_detail_by_order_number(
        self, *,
        merchantId=None, orderNumber=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/merchant/{{merchantId}}/detail/{{orderNumber}}  （用例中出现 2 次）"""
        return self._call(
            "GET", '/order/merchant/{{merchantId}}/detail/{{orderNumber}}',
            path_vars=_pv(("merchantId", merchantId), ("orderNumber", orderNumber), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def merchant_detail_v2(
        self, *,
        merchantId=None, orderNumber=None,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/merchant/{{merchantId}}/detail/{{orderNumber}}/v2  （用例中出现 65 次）"""
        return self._call(
            "GET", '/order/merchant/{{merchantId}}/detail/{{orderNumber}}/v2',
            path_vars=_pv(("merchantId", merchantId), ("orderNumber", orderNumber), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def points_and_promotions(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /order/points-and-promotions"""
        return self._call(
            "POST", '/order/points-and-promotions',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/promoter  （用例中出现 51 次）"""
        return self._call(
            "GET", '/order/promoter',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter_detail_v2(
        self, *,
        merchantOrderId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/promoter/detail/{{merchantOrderId}}/v2  （用例中出现 57 次）"""
        return self._call(
            "GET", '/order/promoter/detail/{{merchantOrderId}}/v2',
            path_vars=_pv(("merchantOrderId", merchantOrderId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def refunds(
        self, *,
        refund_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """POST /merchant-orders/{{refund_id}}/refunds  （用例中出现 5 次）"""
        return self._call(
            "POST", '/merchant-orders/{{refund_id}}/refunds',
            path_vars=_pv(("refund_id", refund_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def ticket_status(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /order/ticket/status"""
        return self._call(
            "POST", '/order/ticket/status',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def update_promotions(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """POST /order/update-promotions  （用例中出现 13 次）"""
        return self._call(
            "POST", '/order/update-promotions',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def verification(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /order/verification  （用例中出现 2 次）"""
        return self._call(
            "POST", '/order/verification',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def verification_search(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/verification/search  （用例中出现 2 次）"""
        return self._call(
            "GET", '/order/verification/search',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def verification_ticket_statistics(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /order/verification/ticket/statistics"""
        return self._call(
            "GET", '/order/verification/ticket/statistics',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
