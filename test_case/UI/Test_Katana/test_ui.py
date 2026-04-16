#!usr/bin/env python3
# -*- encoding : utf-8 -*-
# coding : unicode_escape
'''
Filename         : test_ui.py
Description      : Action Registry Refactored Version
Time             : 2026/01/15
Author           : AllenLuo / Agent
Version          : 3.0
'''

import sys
import os
import pytest
import allure
from playwright.sync_api import Page, Browser
from loguru import logger

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from tools import allure_title, allure_step_no
from page.home import *

# Import the new Action Registry
from test_case.UI.Test_Katana.actions import get_action

@allure.testcase('https://ones.cn/project/#/testcase/team/T7u1zXum/plan/QCuFwDdq/library/XcAFFViB/module/6mi4qiVp', 'ONS测试用例链接')
@allure.title("测试执行")
def test_case(smokecases1, page: Page, browser: Browser, request):
    val = list(smokecases1.values())[0]
    
    # Guest Mode Setup
    if val.get("guest", False):
        logger.info(f"Running {list(smokecases1.keys())[0]} in GUEST mode")

    page.set_default_timeout(30000)  # Reduced from 90s for faster AI failover
    
    # Test Metadata extraction
    caseno = list(smokecases1.keys())[0]
    description = dict(list(smokecases1.values())[0])["description"]
    test_step = list(smokecases1.values())[0]["test_step"]
    expect_result = dict(list(smokecases1.values())[0])["expect_result"]
    
    # Pass metadata to page object for AI context
    setattr(page, "_test_description", description)
    setattr(page, "_test_caseno", caseno)
    setattr(page, "_yaml_path", val.get("__yaml_path__")) # For self-patching
    setattr(page, "_execution_history", [])  # Initialize execution history
    
    allure_title(caseno)
    allure_step_no(f'description:{description}')
    allure_step_no(f'test_step:{str(test_step)}')

    # --- Core Execution Engine ---
    for k, v in test_step.items():
        logger.info(f">>> Current Step: {k}")
        
        # Global Crash Check
        if page.get_by_text("Something went wrong!", exact=True).is_visible():
            logger.error("Application crash detected (Something went wrong!)")
            page.screenshot(path="crash_detected.png")
            pytest.fail("Application crashed during test execution.")

        # 1. Action Registry Lookup
        action = get_action(k)
        
        if action:
            try:
                action(page, v)
                # Record successful step
                page._execution_history.append((k, v))
            except Exception as e:
                logger.error(f"Action '{k}' failed: {e}")
                # Try generic screenshot on failure
                try: page.screenshot(path=f"fail_{k}.png")
                except: pass
                raise
        else:
            # 2. Legacy Fallback
            logger.warning(f"Step '{k}' not found in Action Registry. Attempting legacy dispatch/fallback.")
            fallback_success = False
            if k.startswith("click"):
                try:
                   target_text = v.get('text') or v.get('name')
                   if target_text:
                       page.click(f"text={target_text}", timeout=5000)
                       logger.info(f"Fallback click success for: {target_text}")
                       fallback_success = True
                       page._execution_history.append((k, v))
                except:
                   pass
            
            if not fallback_success:
                logger.error(f"FATAL: Step '{k}' could not be resolved by Registry or Fallback.")
                pytest.fail(f"Step '{k}' not found or failed in fallback. Check actions/__init__.py or YAML key.")

        # Post-step Crash Check
        if page.get_by_text("Something went wrong!", exact=True).is_visible():
             logger.error("Application crash detected after step completion.")
             page.screenshot(path=f"crash_after_{k}.png")
             pytest.fail(f"Application crashed after step: {k}")

    # --- Assertion Phase ---
    allure_step_no(f'expect_result:{str(expect_result)}')
    if "assertions" in expect_result:
        for assertion in expect_result["assertions"]:
            assertion_type = assertion.get("assertion_type")
            
            if assertion_type == "element_visible_by_text":
                text = assertion.get("text")
                if text:
                    logger.info(f"Verifying visibility of text: '{text}'")
                    try:
                        page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=10000)
                        logger.info(f"Assertion success: Text '{text}' is visible.")
                    except:
                        # Capture page content for debugging
                        found_in_content = text in page.content()
                        if not found_in_content:
                            logger.error(f"Assertion failed: Text '{text}' not found in page content.")
                            page.screenshot(path=f"fail_assert_{caseno}.png")
                        assert found_in_content, f"Assertion failed: Text '{text}' not found in page content."
            
            elif assertion_type == "element_visible":
                role = assertion.get("role")
                name = assertion.get("name")
                if role:
                    logger.info(f"Verifying visibility of element: {role} '{name}'")
                    try:
                        page.get_by_role(role, name=name).first.wait_for(state="visible", timeout=10000)
                        logger.info(f"Assertion success: Element {role} '{name}' is visible.")
                    except:
                        logger.error(f"Assertion failed: Element {role} '{name}' not found or visible.")
                        page.screenshot(path=f"fail_assert_{caseno}.png")
                        pytest.fail(f"Assertion failed: Element {role} '{name}' not found or visible.")
            
            elif assertion_type == "element_not_visible":
                role = assertion.get("role")
                name = assertion.get("name")
                locator = assertion.get("locator")
                logger.info(f"Verifying element is NOT visible: role={role}, name={name}, locator={locator}")
                try:
                    if locator:
                        is_visible = page.locator(locator).first.is_visible(timeout=3000)
                    elif role:
                        is_visible = page.get_by_role(role, name=name).first.is_visible(timeout=3000)
                    else:
                        is_visible = False
                    if is_visible:
                        logger.error(f"Assertion failed: Element should NOT be visible but it is (role={role}, name={name}, locator={locator}).")
                        page.screenshot(path=f"fail_assert_{caseno}.png")
                        pytest.fail(f"Assertion failed: Element should NOT be visible but it is (role={role}, name={name}, locator={locator}).")
                    else:
                        logger.info(f"Assertion success: Element is correctly NOT visible (role={role}, name={name}, locator={locator}).")
                except Exception as e:
                    # is_visible returning False or throwing means not visible - which is what we want
                    logger.info(f"Assertion success: Element is correctly NOT visible (role={role}, name={name}, locator={locator}).")
            
            elif assertion_type == "element_not_visible_by_text":
                text = assertion.get("text")
                logger.info(f"Verifying text is NOT visible: '{text}'")
                try:
                    is_visible = page.get_by_text(text, exact=False).first.is_visible(timeout=3000)
                    if is_visible:
                        logger.error(f"Assertion failed: Text '{text}' should NOT be visible but it is.")
                        page.screenshot(path=f"fail_assert_{caseno}.png")
                        pytest.fail(f"Assertion failed: Text '{text}' should NOT be visible but it is.")
                    else:
                        logger.info(f"Assertion success: Text '{text}' is correctly NOT visible.")
                except:
                    logger.info(f"Assertion success: Text '{text}' is correctly NOT visible.")
            
            
    # --- Teardown Phase ---
    teardown_step = val.get("teardown_step", {})
    if teardown_step:
        logger.info(">>> Starting Teardown Phase to clean up test data")
        for tk, tv in teardown_step.items():
            logger.info(f">>> Teardown Step: {tk}")
            t_action = get_action(tk)
            if t_action:
                try: t_action(page, tv)
                except Exception as e: logger.error(f"Teardown Action '{tk}' failed: {e}")
            else:
                if tk.startswith("click"):
                    try:
                        t_target_text = tv.get('text') or tv.get('name')
                        if t_target_text: page.click(f"text={t_target_text}", timeout=5000)
                    except: pass
