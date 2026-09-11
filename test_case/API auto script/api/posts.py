"""posts —— 帖子（策展人 / 消费者 / 推广者）。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class PostsApi(BaseApi):
    """帖子（策展人 / 消费者 / 推广者）。"""

    domain = "posts"

    def consumer_detail(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /posts/curator"""
        return self._call(
            "POST", '/posts/curator',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_1a6bf2bd_f228_40f2_ba24_e0128b88bccd(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/1a6bf2bd-f228-40f2-ba24-e0128b88bccd"""
        return self._call(
            "PUT", '/posts/curator/1a6bf2bd-f228-40f2-ba24-e0128b88bccd',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_24232e2c_b3af_4517_be24_4dfddb1ca79f(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/24232e2c-b3af-4517-be24-4dfddb1ca79f"""
        return self._call(
            "PUT", '/posts/curator/24232e2c-b3af-4517-be24-4dfddb1ca79f',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_397367e3_1140_4a14_9ba1_26f92bd7f24a(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/397367e3-1140-4a14-9ba1-26f92bd7f24a"""
        return self._call(
            "PUT", '/posts/curator/397367e3-1140-4a14-9ba1-26f92bd7f24a',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_504d5e2a_d2e9_4782_9333_536a696b9669(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/504d5e2a-d2e9-4782-9333-536a696b9669"""
        return self._call(
            "PUT", '/posts/curator/504d5e2a-d2e9-4782-9333-536a696b9669',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_7dd8e66d_7d42_4715_ab73_3cf8d7c03632(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/7dd8e66d-7d42-4715-ab73-3cf8d7c03632"""
        return self._call(
            "PUT", '/posts/curator/7dd8e66d-7d42-4715-ab73-3cf8d7c03632',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_907f5bec_0233_4778_8f46_7820e8b2eb7c(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/907f5bec-0233-4778-8f46-7820e8b2eb7c"""
        return self._call(
            "PUT", '/posts/curator/907f5bec-0233-4778-8f46-7820e8b2eb7c',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_9fd62b45_6f4a_4bca_ac59_778e44c2813b(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/9fd62b45-6f4a-4bca-ac59-778e44c2813b"""
        return self._call(
            "PUT", '/posts/curator/9fd62b45-6f4a-4bca-ac59-778e44c2813b',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_by_post_id(
        self, *,
        postId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        post_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /posts/curator/{{post_id}}  （用例中出现 3 次）"""
        return self._call(
            "DELETE", '/posts/curator/{{post_id}}',
            path_vars=_pv(("post_id", post_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_de6f0abd_c8f8_41e5_b2d1_1eb2ba05f839(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/de6f0abd-c8f8-41e5-b2d1-1eb2ba05f839"""
        return self._call(
            "PUT", '/posts/curator/de6f0abd-c8f8-41e5-b2d1-1eb2ba05f839',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_ed73ae71_ad44_4391_8b69_02e5a21982e9(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/ed73ae71-ad44-4391-8b69-02e5a21982e9"""
        return self._call(
            "PUT", '/posts/curator/ed73ae71-ad44-4391-8b69-02e5a21982e9',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_edit_ac273ab5_3f9a_4f89_8e07_72d19c463b18(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /posts/curator/edit/ac273ab5-3f9a-4f89-8e07-72d19c463b18"""
        return self._call(
            "GET", '/posts/curator/edit/ac273ab5-3f9a-4f89-8e07-72d19c463b18',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_event_0fe6623e_a3ba_40fb_815d_3d6f444775c3_posts(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /posts/curator/event/0fe6623e-a3ba-40fb-815d-3d6f444775c3/posts  （用例中出现 3 次）"""
        return self._call(
            "GET", '/posts/curator/event/0fe6623e-a3ba-40fb-815d-3d6f444775c3/posts',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_event_posts(
        self, *,
        event_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /posts/curator/event/{{event_id}}/posts  （用例中出现 12 次）"""
        return self._call(
            "GET", '/posts/curator/event/{{event_id}}/posts',
            path_vars=_pv(("event_id", event_id), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_fe26aba1_17b9_4e04_872e_3759ce5fc842(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/fe26aba1-17b9-4e04-872e-3759ce5fc842"""
        return self._call(
            "PUT", '/posts/curator/fe26aba1-17b9-4e04-872e-3759ce5fc842',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_ff9274b0_b4b1_442c_b9ea_afcaf67912ae(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /posts/curator/ff9274b0-b4b1-442c-b9ea-afcaf67912ae"""
        return self._call(
            "PUT", '/posts/curator/ff9274b0-b4b1-442c-b9ea-afcaf67912ae',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def curator_from_event(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        resell_post_id=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
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
        body=None, token=None, params=None, headers=None,
        app_headers=False, skip_notifications=False,
        path_vars=None,
    ):
        """GET https://mehost.cn/post/tiubyg

        .. warning:: 该接口的域名写死在路径里（迁移遗留），切换环境时需要一并修改；建议后续改为环境变量。"""
        return self._call(
            "GET", 'https://mehost.cn/post/tiubyg',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
