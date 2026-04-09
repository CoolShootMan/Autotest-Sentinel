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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Now that the path is space-free (monster_test), we can use simple normalization
    y4m_path = os.path.join(BASE_DIR, "data", "Ticket_C.y4m").replace("\\", "/")
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
                match = re.search(r'T\d+', test_case_name)
                if match:
                    logger.info(f"TEST_STATUS: {match.group(0)} - {'passed' if rep.passed else 'failed'}")
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
        yaml_file = metafunc.config.getoption("--yaml")
        if not yaml_file:
            yaml_file = "Storefront_module.yaml"
            
        yaml_path = os.path.join(BASE_DIR, "test_case", "UI", "Test_Katana", yaml_file)
        
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data:
                argvalues = []
                ids = []
                for k, v in data.items():
                    if isinstance(v, dict):
                        v["__yaml_path__"] = yaml_path
                        argvalues.append({k: v})
                        ids.append(k)
                metafunc.parametrize("smokecases1", argvalues, ids=ids)
        else:
            logger.error(f"YAML file not found at: {yaml_path}")