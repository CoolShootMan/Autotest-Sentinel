"""posts —— 帖子（策展人 / 消费者 / 推广者）。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 仅类型检查期导入：避免 api ↔ core 运行期循环依赖
    from core.response import ApiResponse

from api.base import BaseApi, _pv


class PostsApi(BaseApi):
    """帖子（策展人 / 消费者 / 推广者）。"""

    domain = "posts"

    def consumer_detail(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /posts/consumer/detail  （用例中出现 26 次）"""
        return self._call(
            "GET", '/posts/consumer/detail',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /posts/curator"""
        return self._call(
            "POST", '/posts/curator',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_by_post_id(
        self, *,
        postId: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /posts/curator/{{postId}}  （用例中出现 6 次）"""
        return self._call(
            "PUT", '/posts/curator/{{postId}}',
            path_vars=_pv(("postId", postId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_by_post_id_2(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """DELETE /posts/curator/{{post_id}}  （用例中出现 3 次）"""
        return self._call(
            "DELETE", '/posts/curator/{{post_id}}',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_event_posts(
        self, *,
        event_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /posts/curator/event/{{event_id}}/posts  （用例中出现 12 次）"""
        return self._call(
            "GET", '/posts/curator/event/{{event_id}}/posts',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_edit_by_post_id(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /posts/curator/edit/{{post_id}}"""
        return self._call(
            "GET", '/posts/curator/edit/{{post_id}}',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    # --- UI Automation Data Pre-configuration 专用接口 ---------------
    # 注意：方法名不要与上面的 PUT /posts/curator/{{postId}} 重名
    # （curator_by_post_id）。同名会被后面的定义覆盖，导致 PUT 版失效，
    # 调用方传 postId= 时报 TypeError，不传时渲染出空 id 的
    # PATCH /posts/curator/ → 404。见 T2747 / T2810 / T4955。

    def curator_patch_by_post_id(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH /posts/curator/{{post_id}}"""
        return self._call(
            "PATCH", '/posts/curator/{{post_id}}',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_sync_promoters(
        self, *,
        post0_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /posts/curator/{{post0_id}}/promoters/sync"""
        return self._call(
            "POST", '/posts/curator/{{post0_id}}/promoters/sync',
            path_vars=_pv(("post0_id", post0_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_from_event(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /posts/curator/from-event"""
        return self._call(
            "POST", '/posts/curator/from-event',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_resell_by_resell_post_id(
        self, *,
        resell_post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /posts/curator/resell/{{resell_post_id}}"""
        return self._call(
            "PUT", '/posts/curator/resell/{{resell_post_id}}',
            path_vars=_pv(("resell_post_id", resell_post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_shop(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /posts/curator/shop  （用例中出现 3 次）"""
        return self._call(
            "GET", '/posts/curator/shop',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter_detail(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /posts/promoter/detail  （用例中出现 3 次）"""
        return self._call(
            "GET", '/posts/promoter/detail',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter_resale(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /posts/promoter/resale"""
        return self._call(
            "POST", '/posts/promoter/resale',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def promoter_simplify_list(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /posts/promoter/simplify/list"""
        return self._call(
            "GET", '/posts/promoter/simplify/list',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def simplify_shop_linda(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /post/simplify/shop/linda"""
        return self._call(
            "GET", '/post/simplify/shop/linda',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def tiubyg(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = False, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET https://mehost.cn/post/tiubyg

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://mehost.cn/post/tiubyg',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def relate_products(
        self, *,
        venue_map_post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /post/v2/{{venue_map_post_id}}/relate-products"""
        return self._call(
            "GET", '/post/v2/{{venue_map_post_id}}/relate-products',
            path_vars=_pv(("venue_map_post_id", venue_map_post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def children(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """GET /post/{{post_id}}/children"""
        return self._call(
            "GET", '/post/{{post_id}}/children',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def patch_by_id(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH /post/{{post_id}}"""
        return self._call(
            "PATCH", '/post/{{post_id}}',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def update_curator_content(
        self, *,
        venue_map_post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH /posts/curator/{{venue_map_post_id}}/content"""
        return self._call(
            "PATCH", '/posts/curator/{{venue_map_post_id}}/content',
            path_vars=_pv(("venue_map_post_id", venue_map_post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def posts_curator_toggle_sync(
        self, *,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """POST /posts/curator/toggle-sync"""
        return self._call(
            "POST", '/posts/curator/toggle-sync',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_update(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PUT /posts/curator/{{post_id}}"""
        return self._call(
            "PUT", '/posts/curator/{{post_id}}',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_promotions_update(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH /posts/curator/{{post_id}}/promotions

        专用「为帖子添加 / 更新 coupon / promotion」子端点。

        .. note:: 与整帖 ``PUT /posts/curator/{{post_id}}`` 不同，本端点只处理
           ``promotions``，不会触发 ``katana-promotion`` 的
           ``/api/promotions-by-promoter`` 微服务（该路径在 Release 环境偶发 500 →
           整帖 PUT 503）。手动 curl 验证稳定成功的就是这条路径，故 coupon 添加
           统一走这里。

           请求体形如::

               {"announcements": [], "promotions": [...], "hideCouponBox": false}
        """
        return self._call(
            "PATCH", '/posts/curator/{{post_id}}/promotions',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_co_selling_update(
        self, *,
        post_id: str | None = None,
        body: Any = None, token: str | None = None,
        params: dict[str, Any] | None = None, headers: dict[str, Any] | None = None,
        app_headers: bool = True, skip_notifications: bool = False,
        path_vars: dict[str, Any] | None = None,
    ) -> "ApiResponse":
        """PATCH /posts/curator/{{post_id}}/co-selling"""
        return self._call(
            "PATCH", '/posts/curator/{{post_id}}/co-selling',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
