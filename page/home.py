#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : home.py
Description      : 
Time             : 2023/12/29 10:29:01
Author           : Xiao
Version          : 2.0
'''

from playwright.sync_api import Page, expect
import allure
from loguru import logger


def page_element_click(page: Page, selector, index=0):
    """ Page click event (Demo)
        selector: element selector
        index: index of matched selector, default is first (0)
    """
    with allure.step(f'Clicked element - {selector}'):
        logger.info(f'Clicked element - {selector}')
    page.locator(selector=selector).nth(index).click()

def page_element_role_click(page: Page, role, name, index=None, exact=False, force=False):
    """ Page click event
        role: built-in locator, better accuracy than selector
    """
    with allure.step(f'Clicked element - {role}, visible text - {name}'):
        logger.info(f'Clicked element - {role}, visible text - {name}')
    with allure.step(f'Clicked element - {role}, visible text - {name}'):
        logger.info(f'Clicked element - {role}, visible text - {name}')
    if index is not None:
        locator = page.get_by_role(role=role, name=name, exact=exact).nth(index=index)
        # locator.scroll_into_view_if_needed()
        locator.click(force=force, timeout=15000)
    else:
        locator = page.get_by_role(role=role, name=name, exact=exact).first
        # locator.scroll_into_view_if_needed()
        locator.click(force=force, timeout=15000)

def page_element_label_click(page: Page, text, index=0):
    """ Page click event
        label: label locator, better accuracy than selector
    """
    with allure.step(f'Clicked element - {text}'):
        logger.info(f'Clicked element - {text}')
    page.get_by_label(text=text).nth(index).click(timeout=15000)

def page_element_input_fill(page: Page, selector, value):
    """ Fill text input (Demo) """
    with allure.step(f'Element - {selector}, fill text - {value}'):
        logger.info(f'Element - {selector}, fill text - {value}')
    page.locator(selector=selector).fill(value=value)

def page_element_input_role_fill(page: Page, role, name, value, exact=False):
    """ Fill text input """
    with allure.step(f'Element - {role} ({name}), fill text - {value}'):
        logger.info(f'Element - {role} ({name}), fill text - {value}')
    page.get_by_role(role=role, name=name, exact=exact).fill(value=value)

def page_element_input_placeholder_fill(page: Page, placeholder, value):
    """ Fill text input """
    with allure.step(f'Element - {placeholder}, fill text - {value}'):
        logger.info(f'Element - {placeholder}, fill text - {value}')
    page.get_by_placeholder(placeholder).fill(value=value)

def page_element_input_by_placeholder_and_locator_fill(page: Page, placeholder, locator, value):
    """ Fill text input """
    with allure.step(f'Element - {placeholder}, fill text - {value}'):
        logger.info(f'Element - {placeholder}, fill text - {value}')
    page.get_by_placeholder(placeholder).click()
    page.locator(locator).fill(value=value)


def page_swipe(page: Page, x, y):
    """ Page scroll method """
    with allure.step(f'Scroll/swipe element, coordinates - {x, y}'):
        logger.info(f'Scroll/swipe element, coordinates - {x, y}')
    page.mouse.wheel(delta_x=x, delta_y=y)

def page_element_input_role_press(page: Page, role, key):
    """ Page keyboard press method """
    with allure.step(f'Key pressed on element - {role}'):
        logger.info(f'Key pressed on element - {role}')
    page.get_by_role(role=role).press(key=key)

def page_open(page: Page, url):
    """ Open page method """
    with allure.step(f'Opening - {url}'):
        logger.info(f'Opening - {url}')
    page.goto(url=url, wait_until="load", timeout=120000)
    
    # DEBUG: Proof of cookies for user
    cookies = page.context.cookies()
    logger.debug(f"Authentication state check - Cookies count: {len(cookies)}")
    if len(cookies) > 0:
        logger.debug(f"Sample Cookie (session): {[c['name'] for c in cookies]}")
    else:
        logger.warning("No cookies found in context! Storage state may not be loaded.")

        
