#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : conftest.py
Description      : Root conftest with dynamic YAML loading & per-test emulation
Time             : 2023/12/14 14:24:12
Author           : AllenLuo
Version          : 2.2
'''
import os
import shutil
from loguru import logger
import warnings
from typing import Any, Callable, Dict, Generator, List, Optional
import allure
import yaml
import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Error,
    Page,
    Playwright,
    sync_playwright,
)
from slugify import slugify
import re
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 加载项目根目录的 .env 文件（不覆盖已存在的环境变量）
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _resolve_base_url():
    """
    获取 BASE_URL，优先级：系统环境变量 > .env 文件 > 默认值
    默认值: https://release.pear.us
    """
    return os.environ.get("BASE_URL", "https://release.pear.us")


def _replace_placeholders(obj, base_url):
    """递归替换字典/列表/字符串中所有 {BASE_URL} 占位符"""
    if isinstance(obj, str):
        return obj.replace("{BASE_URL}", base_url)
    elif isinstance(obj, dict):
        return {k: _replace_placeholders(v, base_url) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_placeholders(item, base_url) for item in obj]
    return obj


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Default to the trimmed small video to prevent OOM
    y4m_name = "Ticket_Small.y4m"
    
    # Fallback to Ticket_C.y4m if small one doesn't exist
    if not os.path.exists(os.path.join(BASE_DIR, "data", y4m_name)):
        y4m_name = "Ticket_C.y4m"
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    if worker_id != "master":
        # Extract index from 'gw0', 'gw1' etc.
        try:
            worker_idx = int(re.sub(r'\D', '', worker_id)) + 1
            worker_y4m = f"Ticket_{worker_idx}.y4m"
            if os.path.exists(os.path.join(BASE_DIR, "data", worker_y4m)):
                y4m_name = worker_y4m
                logger.info(f"WORKER_ISOLATION: Worker {worker_id} using dedicated video: {y4m_name}")
        except Exception as e:
            logger.warning(f"Failed to determine worker-specific video: {e}")

    y4m_path = os.path.join(BASE_DIR, "data", y4m_name).replace("\\", "/")
    logger.info(f"Y4M_LOAD_PATH: {y4m_path}")

    return {
        **browser_type_launch_args,
        "args": [
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            f"--use-file-for-fake-video-capture={y4m_path}",
            "--window-size=600,1100",
            "--start-maximized",
            "--disable-translate",
            "--disable-features=Translate",
            "--disable-gpu",
            "--no-sandbox"
        ],
    }

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    if rep.when == "call":
        try:
            smokecases1 = item.funcargs.get('smokecases1')
            if smokecases1:
                test_case_name = list(smokecases1.keys())[0]
                test_case_data = list(smokecases1.values())[0]
                match = re.search(r'T\d+', test_case_name)
                if match:
                    # 获取 YAML 文件名用于日志追踪
                    yaml_path = test_case_data.get("__yaml_path__", "")
                    yaml_name = os.path.basename(yaml_path) if yaml_path else "unknown"
                    logger.info(f"TEST_STATUS: [{yaml_name}] {match.group(0)} - {'passed' if rep.passed else 'failed'}")
        except Exception:
            pass

def pytest_addoption(parser):
    try:
        parser.addoption("--storage-state", action="store", default=None, help="Path to the storage state file")
    except ValueError:
        pass
    try:
        parser.addoption("--yaml", action="store", default=None, help="Specific YAML file to load test cases from")
    except ValueError:
        pass

@pytest.fixture()
def browser_context_args(browser_context_args, playwright, request):
    """
    Root level dynamic device emulation.
    """
    is_mobile = False
    try:
        if "smokecases1" in request.fixturenames:
            smokecases1 = request.getfixturevalue("smokecases1")
            v = list(smokecases1.values())[0]
            is_mobile = v.get("is_mobile", False)
    except Exception:
        pass

    if is_mobile:
        iphone_14 = playwright.devices['iPhone 14 Pro Max']
        logger.info("ROOT_EMULATION: Enabled (iPhone 14 Pro Max)")
        return {
            **browser_context_args,
            **iphone_14,
            "permissions": ["camera", "microphone"],
        }
    else:
        logger.info("ROOT_EMULATION: Disabled (Desktop)")
        return {
            **browser_context_args,
            "permissions": ["camera", "microphone"],
        }

@pytest.fixture()
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page

def _build_artifact_test_folder(
    pytestconfig: Any, request: pytest.FixtureRequest, folder_or_file_name: str
) -> str:
    output_dir = pytestconfig.getoption("--output")
    return os.path.join(output_dir, slugify(request.node.nodeid), folder_or_file_name)

@pytest.fixture()
def context(
    browser: Browser,
    browser_context_args: Dict,
    pytestconfig: Any,
    request: pytest.FixtureRequest,
) -> Generator[BrowserContext, None, None]:
    pages: List[Page] = []
    storage_state = pytestconfig.getoption("--storage-state")
    
    is_guest = False
    try:
        if "smokecases1" in request.fixturenames:
            val = request.getfixturevalue("smokecases1")
            is_guest = list(val.values())[0].get("guest", False)
    except Exception:
        pass

    if is_guest:
        logger.info("GUEST MODE detected in fixture override: Bypassing cookie loading for pure context")
        context = browser.new_context(**browser_context_args)
    elif storage_state:
        context = browser.new_context(storage_state=storage_state, **browser_context_args)
    else:
        # Check if local conftest defined a default cookie_release.json
        local_cookie = os.path.join(BASE_DIR, "test_case", "UI", "Test_Katana", "cookie_release.json")
        if os.path.exists(local_cookie):
            context = browser.new_context(storage_state=local_cookie, **browser_context_args)
        else:
            context = browser.new_context(**browser_context_args)
            
    context.on("page", lambda page: pages.append(page))
    
    yield context
    context.close()

# --- THE DYNAMIC ENGINE ---
def pytest_generate_tests(metafunc):
    if "smokecases1" in metafunc.fixturenames:
        yaml_files = metafunc.config.getoption("--yaml")
        if not yaml_files:
            yaml_files = "Storefront_module.yaml"
        
        # 支持逗号分隔的多个 yaml
        yaml_file_list = [f.strip() for f in yaml_files.split(",")]
        
        all_argvalues = []
        all_ids = []
        
        for yaml_file in yaml_file_list:
            # 使用 os.sep 确保路径分隔符正确
            yaml_path = os.path.join(BASE_DIR, "test_case", "UI", "Test_Katana", yaml_file.replace('/', os.sep).replace('\\', os.sep))
            
            if os.path.exists(yaml_path):
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if data:
                    # 运行时替换 {BASE_URL} 占位符
                    base_url = _resolve_base_url()
                    data = _replace_placeholders(data, base_url)
                    for k, v in data.items():
                        if isinstance(v, dict):
                            v["__yaml_path__"] = yaml_path
                            all_argvalues.append({k: v})
                            # 加上 yaml 前缀避免 id 冲突
                            all_ids.append(f"{yaml_file}::{k}")
            else:
                logger.error(f"YAML file not found at: {yaml_path}")
        
        if all_argvalues:
            metafunc.parametrize("smokecases1", all_argvalues, ids=all_ids)