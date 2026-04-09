#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : conftest.py
Description      :
Time             : 2023/12/14 14:24:12
Author           : AllenLuo
Version          : 2.0
'''
import os
os.environ["AI_DISABLED"] = "True"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(BASE_DIR, "test_case")) and BASE_DIR != os.path.dirname(BASE_DIR):
    BASE_DIR = os.path.dirname(BASE_DIR)

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

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)

    if rep.when == "call":
        try:
            smokecases1 = item.funcargs['smokecases1']
            test_case_name = list(smokecases1.keys())[0] # e.g., testT3370
            match = re.search(r'T\d+', test_case_name)
            if not match:
                return
            test_case_id = match.group(0)

            status = "skipped" # Default status
            if rep.passed:
                status = "passed"
            elif rep.failed:
                status = "failed"
            
            logger.info(f"TEST_STATUS: {test_case_id} - {status}")
        except Exception:
            pass # Ignore errors if the fixture is not present



def pytest_addoption(parser):
    try:
        parser.addoption("--env", action="store", default="release", help="Test environment: release, staging, or local")
    except ValueError:
        pass
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
    Dynamic device emulation based on YAML 'is_mobile' flag.
    """
    is_mobile = False
    try:
        if "smokecases1" in request.fixturenames:
            smokecases1 = request.getfixturevalue("smokecases1")
            v = list(smokecases1.values())[0]
            is_mobile = v.get("is_mobile", False)
    except Exception:
        pass

    # Base arguments for all contexts
    base_args = {
        **browser_context_args,
        "permissions": ["camera", "microphone"],
        "ignore_https_errors": True,
    }

    if is_mobile:
        iphone_14 = playwright.devices['iPhone 14 Pro Max']
        res = {
            **base_args,
            **iphone_14,
        }
        logger.info("MOBILE_EMULATION: Enabled (iPhone 14 Pro Max)")
        return res
    else:
        logger.info("MOBILE_EMULATION: Disabled (Desktop)")
        return base_args


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
    if not storage_state:
        # Optimize: automatically load the default cookie state if it exists
        default_cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookie_release.json")
        if os.path.exists(default_cookie_path):
            storage_state = default_cookie_path
            
    is_guest = False
    try:
        if "smokecases1" in request.fixturenames:
            smokecases1 = request.getfixturevalue("smokecases1")
            is_guest = list(smokecases1.values())[0].get("guest", False)
    except Exception:
        pass

    # Only use storage-state if authenticated and NOT a guest
    if storage_state and not is_guest:
        context = browser.new_context(storage_state=storage_state, **browser_context_args)
    else:
        # Use full mobile emulation args even for guests as requested
        context = browser.new_context(**browser_context_args)

    # Force grant permissions even if storage_state has restricted ones
    try:
        context.grant_permissions(["camera", "microphone"])
    except Exception as e:
        logger.warning(f"Failed to grant preset permissions: {e}")

    # --- KEY FIX: Patch getUserMedia to relax 'exact' constraints ---
    # The web app requests facingMode:{exact:"environment"} and deviceId:{exact:...}
    # which fails because Chromium's fake device doesn't declare a facing mode.
    # We intercept and change 'exact' to 'ideal' so the fake device can pass the check.
    context.add_init_script("""
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            const _original = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
            navigator.mediaDevices.getUserMedia = function(constraints) {
                if (constraints && constraints.video && typeof constraints.video === 'object') {
                    const v = JSON.parse(JSON.stringify(constraints.video));
                    // Relax facingMode: {exact: 'environment'} -> {ideal: 'environment'}
                    if (v.facingMode && v.facingMode.exact) {
                        v.facingMode = { ideal: v.facingMode.exact };
                    }
                    // Remove deviceId exact constraint (fake device has no real deviceId)
                    if (v.deviceId && v.deviceId.exact) {
                        delete v.deviceId;
                    }
                    // Delete width/height constraints so the fake camera ignores 16:9 
                    // requirements and doesn't crop or stretch 1:1 videos like Ticket_C.y4m
                    if (v.width) delete v.width;
                    if (v.height) delete v.height;
                    constraints = { ...constraints, video: v };
                }
                return _original(constraints);
            };
        }
    """)
    logger.info("CAMERA_PATCH: getUserMedia constraint relaxation injected.")

    context.on("page", lambda page: pages.append(page))
    tracing_option = pytestconfig.getoption("--tracing")
    capture_trace = tracing_option in ["on", "retain-on-failure"]
    if capture_trace:
        context.tracing.start(
            name=slugify(request.node.nodeid),
            screenshots=True,
            snapshots=True,
            sources=True,
        )

    yield context
    failed = request.node.rep_setup.failed or request.node.rep_call.failed if hasattr(request.node, 'rep_setup') and hasattr(request.node, 'rep_call') else True

    if capture_trace:
        retain_trace = tracing_option == "on" or (
            failed and tracing_option == "retain-on-failure"
        )
        if retain_trace:
            trace_path = _build_artifact_test_folder(pytestconfig, request, "trace.zip")
            context.tracing.stop(path=trace_path)
        else:
            context.tracing.stop()

    screenshot_option = pytestconfig.getoption("--screenshot")
    capture_screenshot = screenshot_option == "on" or (
        failed and screenshot_option == "only-on-failure"
    )
    if capture_screenshot:
        for i, page in enumerate(pages):
            screenshot_path = _build_artifact_test_folder(
                pytestconfig, request, f"screenshot-{i}.png"
            )
            try:
                page.screenshot(path=screenshot_path)
                allure.attach.file(
                    screenshot_path,
                    name=f"Screenshot {i}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass

    # --- Video Attachment Fix ---
    # CRITICAL: video.path() must be called BEFORE context.close().
    # context.close() triggers Playwright to finalize and write the video file to disk.
    # After close(), we can safely read and attach the file to Allure.
    video_option = pytestconfig.getoption("--video")
    capture_video = video_option == "on" or (
        failed and video_option == "retain-on-failure"
    )
    video_paths = []
    if capture_video:
        for i, page in enumerate(pages):
            video = page.video
            if video:
                try:
                    # Record path BEFORE context.close() finalizes the file
                    video_paths.append((i, video.path()))
                except Exception as e:
                    logger.warning(f"Could not get video path for page {i}: {e}")

    # Close context: this is when Playwright writes the video to disk
    context.close()

    # Now attach the finalized video files to Allure
    for i, video_path in video_paths:
        try:
            if os.path.exists(video_path):
                allure.attach.file(
                    video_path,
                    name=f"Video {i}",
                    attachment_type=allure.attachment_type.WEBM,
                )
                logger.info(f"Video {i} attached to Allure: {video_path}")
            else:
                logger.warning(f"Video file not found after context close: {video_path}")
        except Exception as e:
            logger.warning(f"Failed to attach video {i} to Allure: {e}")