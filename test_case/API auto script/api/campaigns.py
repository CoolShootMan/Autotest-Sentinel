"""campaigns —— 营销活动。

由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**
（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class CampaignsApi(BaseApi):
    """营销活动。"""

    domain = "campaigns"

    def by_campaign_id(
        self, *,
        campaignId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """PUT /campaigns/{{campaignId}}  （用例中出现 6 次）"""
        return self._call(
            "PUT", '/campaigns/{{campaignId}}',
            path_vars=_pv(("campaignId", campaignId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def by_campaign_id_2(
        self, *,
        campaignId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """GET /campaigns/{{campaignId}}  （用例中出现 2 次）"""
        return self._call(
            "GET", '/campaigns/{{campaignId}}',
            path_vars=_pv(("campaignId", campaignId), extra=path_vars),
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def by_random_linda_automation_id(
        self, *,
        randomLindaAutomationId=None,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """DELETE /campaigns/{{randomLindaAutomationId}}"""
        return self._call(
            "DELETE", '/campaigns/{{randomLindaAutomationId}}',
            path_vars=_pv(("randomLindaAutomationId", randomLindaAutomationId), extra=path_vars),
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
        """POST /campaigns  （用例中出现 7 次）"""
        return self._call(
            "POST", '/campaigns',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def duplicate(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /campaigns/duplicate  （用例中出现 2 次）"""
        return self._call(
            "POST", '/campaigns/duplicate',
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
        """GET /campaigns  （用例中出现 3 次）"""
        return self._call(
            "GET", '/campaigns',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def save_recipients(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /campaigns/save-recipients  （用例中出现 7 次）"""
        return self._call(
            "POST", '/campaigns/save-recipients',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def send_campaign(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /campaigns/send-campaign  （用例中出现 3 次）"""
        return self._call(
            "POST", '/campaigns/send-campaign',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def test_email(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /campaigns/test/email"""
        return self._call(
            "POST", '/campaigns/test/email',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )

    def test_sms(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /campaigns/test/sms"""
        return self._call(
            "POST", '/campaigns/test/sms',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
