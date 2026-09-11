"""业务服务层（被测系统的接口语义）。

用例通过 ``ctx.api`` 访问各业务域，例如::

    ctx.api.auth.sign_in(body=..., token=None)
    ctx.api.orders.promoter_detail(promoterOrderId=ctx["P1_OrderId"])

本层只描述**接口**，场景留在 ``tests/`` 里。
"""
from __future__ import annotations

from api.base import BaseApi
from api.address import AddressApi
from api.admin import AdminApi
from api.analytics import AnalyticsApi
from api.approvals import ApprovalsApi
from api.auth import AuthApi
from api.campaigns import CampaignsApi
from api.cart import CartApi
from api.earnings import EarningsApi
from api.events import EventsApi
from api.external import ExternalApi
from api.links import LinksApi
from api.merchants import MerchantsApi
from api.misc import MiscApi
from api.orders import OrdersApi
from api.payments import PaymentsApi
from api.posts import PostsApi
from api.products import ProductsApi
from api.promoters import PromotersApi
from api.storefront import StorefrontApi
from api.users import UsersApi

__all__ = [
    "Api",
    "BaseApi",
    "AddressApi",
    "AdminApi",
    "AnalyticsApi",
    "ApprovalsApi",
    "AuthApi",
    "CampaignsApi",
    "CartApi",
    "EarningsApi",
    "EventsApi",
    "ExternalApi",
    "LinksApi",
    "MerchantsApi",
    "MiscApi",
    "OrdersApi",
    "PaymentsApi",
    "PostsApi",
    "ProductsApi",
    "PromotersApi",
    "StorefrontApi",
    "UsersApi",
]


class Api:
    """业务服务门面：``ctx.api.<domain>.<method>()``。"""

    def __init__(self, client, ctx):
        self._client = client
        self._ctx = ctx
        self._cache = {}

    def _svc(self, key, cls):
        if key not in self._cache:
            self._cache[key] = cls(self._client, self._ctx)
        return self._cache[key]

    @property
    def address(self) -> AddressApi:
        """收货地址（3 个接口）。"""
        return self._svc("address", AddressApi)

    @property
    def admin(self) -> AdminApi:
        """管理后台接口（{{adminurl}}）（11 个接口）。"""
        return self._svc("admin", AdminApi)

    @property
    def analytics(self) -> AnalyticsApi:
        """埋点与统计（1 个接口）。"""
        return self._svc("analytics", AnalyticsApi)

    @property
    def approvals(self) -> ApprovalsApi:
        """采购审批（1 个接口）。"""
        return self._svc("approvals", ApprovalsApi)

    @property
    def auth(self) -> AuthApi:
        """鉴权（登录 / 注册 / 验证码）（6 个接口）。"""
        return self._svc("auth", AuthApi)

    @property
    def campaigns(self) -> CampaignsApi:
        """营销活动（10 个接口）。"""
        return self._svc("campaigns", CampaignsApi)

    @property
    def cart(self) -> CartApi:
        """购物车（3 个接口）。"""
        return self._svc("cart", CartApi)

    @property
    def earnings(self) -> EarningsApi:
        """收益与结算（6 个接口）。"""
        return self._svc("earnings", EarningsApi)

    @property
    def events(self) -> EventsApi:
        """活动与票务（37 个接口）。"""
        return self._svc("events", EventsApi)

    @property
    def external(self) -> ExternalApi:
        """外部依赖（Stripe 等，仅联调）（6 个接口）。"""
        return self._svc("external", ExternalApi)

    @property
    def links(self) -> LinksApi:
        """短链与用户链接（2 个接口）。"""
        return self._svc("links", LinksApi)

    @property
    def merchants(self) -> MerchantsApi:
        """商户（6 个接口）。"""
        return self._svc("merchants", MerchantsApi)

    @property
    def misc(self) -> MiscApi:
        """其它（7 个接口）。"""
        return self._svc("misc", MiscApi)

    @property
    def orders(self) -> OrdersApi:
        """订单（下单 / 结算 / 履约 / 退款）（21 个接口）。"""
        return self._svc("orders", OrdersApi)

    @property
    def payments(self) -> PaymentsApi:
        """支付方式（4 个接口）。"""
        return self._svc("payments", PaymentsApi)

    @property
    def posts(self) -> PostsApi:
        """帖子（策展人 / 消费者 / 推广者）（26 个接口）。"""
        return self._svc("posts", PostsApi)

    @property
    def products(self) -> ProductsApi:
        """商品（13 个接口）。"""
        return self._svc("products", ProductsApi)

    @property
    def promoters(self) -> PromotersApi:
        """推广者与分销（9 个接口）。"""
        return self._svc("promoters", PromotersApi)

    @property
    def storefront(self) -> StorefrontApi:
        """店铺装修（3 个接口）。"""
        return self._svc("storefront", StorefrontApi)

    @property
    def users(self) -> UsersApi:
        """用户与账户（7 个接口）。"""
        return self._svc("users", UsersApi)

    # --- 逃生口 ---------------------------------------------------
    def call(self, method: str, path: str, **kw):
        """直接调用未封装接口（新增接口请优先补进对应业务域模块）。"""
        return self._client.request(method, path, **kw)
