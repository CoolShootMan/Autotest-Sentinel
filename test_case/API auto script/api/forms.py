"""forms —— 表单模块（UI Automation Data Pre-configuration 专用）。

由 Apifox 预配置用例引入，用于创建媒体表单并导入到店铺模块。
新增或调整接口请直接编辑本文件。
"""
from __future__ import annotations

from api.base import BaseApi, _pv


class FormsApi(BaseApi):
    """表单（媒体表单创建）。"""

    domain = "forms"

    def create(
        self, *,
        body=None, token=None, params=None, headers=None,
        app_headers=True, skip_notifications=False,
        path_vars=None,
    ):
        """POST /form"""
        return self._call(
            "POST", '/form',
            path_vars=path_vars,
            params=params,
            body=body, token=token, headers=headers,
            app_headers=app_headers, skip_notifications=skip_notifications,
        )
