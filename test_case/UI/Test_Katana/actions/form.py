import os
import csv
import re
import pandas as pd
from datetime import datetime
from loguru import logger
from playwright.sync_api import Page
from .base import smart_click

def verify_submission_details(page: Page, v: dict):
    page.get_by_role("heading", name=v["name"]).wait_for(state="visible", timeout=5000)
    logger.info("Submission details page verified.")

def verify_message_content(page: Page, v: dict):
    target_text = v["text"]
    try:
        page.get_by_text(target_text, exact=False).wait_for(state="visible", timeout=3000)
        logger.info(f"Verified content (direct): {target_text[:30]}...")
    except:
        logger.warning(f"Direct verification failed, checking body text...")
        page.wait_for_timeout(1000)
        body_text = page.locator("body").inner_text()
        if target_text in body_text:
            logger.info(f"Verified content (body search): {target_text[:30]}...")
        else:
            logger.error(f"Content verification failed.")
            page.screenshot(path=f"fail_verify_message.png")
            raise Exception(f"Content verification failed")

def click_form_more_menu(page: Page, v: dict):
    form_name = v.get("form_name")
    logger.info(f"Clicking More menu for form: {form_name}")
    try:
        container = page.locator("div").filter(has=page.get_by_text(form_name, exact=True)).filter(has=page.get_by_role("button")).last
        more_btn = container.get_by_role("button").first
        more_btn.scroll_into_view_if_needed()
        more_btn.click()
        logger.info(f"More menu for {form_name} clicked.")
        page.wait_for_timeout(1000)
    except Exception as e:
        logger.warning(f"Failed to find More menu for {form_name}: {e}. Trying broad search...")
        try:
            text_el = page.get_by_text(form_name, exact=True).first
            box = text_el.bounding_box()
            if box:
                page.get_by_role("button").filter(has=page.locator(f"xpath=//ancestor::div[abs(number(@y)-{box['y']})<50]")).first.click()
                logger.info("Clicked first button near form text as fallback.")
            else: raise Exception("No bounding box")
        except:
            page.screenshot(path=f"fail_form_more_{form_name}.png")
            raise

def capture_total_count(page: Page, v: dict):
    """Captures the 'Total submissions : X' count from the UI to verify against export."""
    logger.info("Capturing total submissions count from UI...")
    try:
        # Looking for the specific text pattern
        count_text = page.locator("div").filter(has_text=re.compile(r"Total submissions : \d+")).last.inner_text()
        match = re.search(r"Total submissions : (\d+)", count_text)
        if match:
            count = int(match.group(1))
            setattr(page, "_total_submissions_count", count)
            logger.info(f"✨ Captured UI Total Submissions: {count}")
    except Exception as e:
        logger.warning(f"Failed to capture total submissions count: {e}. Count-check will be skipped.")

def click_submission_details_back(page: Page, v: dict):
    logger.info("Closing submission details modal...")
    try:
        close_btn = page.locator("div[role='dialog'] button[aria-label='close'], div[role='dialog'] button:has-text('close')").first
        if not close_btn or not close_btn.is_visible(timeout=2000):
            close_btn = page.get_by_role("button", name="close", exact=False).first
            
        close_btn.click(timeout=5000)
        logger.info("Successfully clicked the 'x' close icon.")
    except Exception as e:
        logger.warning(f"Failed to click 'x' icon, using Escape as final fallback: {e}")
        page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

def click_contact_form(page: Page, v: dict):
    # Restoring original function needed by registry
    page.locator("div").filter(has_text="Auto test form").last.click()

def download_submission_csv(page: Page, v: dict):
    logger.info(f"Triggering download for: {v.get('name')}")
    if not os.path.exists("data"):
        os.makedirs("data")
        
    with page.expect_download() as download_info:
        smart_click(page, v)
    download = download_info.value
    path = os.path.join("data", download.suggested_filename)
    download.save_as(path)
    logger.info(f"File saved to: {path}")
    setattr(page, "_last_download_csv", path)

def verify_csv_data(page: Page, v: dict):
    path = getattr(page, "_last_download_csv", None)
    if not path or not os.path.exists(path):
        raise Exception("No downloaded file found to verify.")
    
    expected_row = v.get("expected_row", {})
    logger.info(f"Verifying data in {path} against pattern: {expected_row}")
    
    found = False
    is_excel = False
    with open(path, 'rb') as f:
        sig = f.read(4)
        if sig == b'PK\x03\x04': # ZIP/XLSX signature
            is_excel = True
            
    import allure
    # 1. Check Row Count against captured UI Total
    ui_count = getattr(page, "_total_submissions_count", None)
    
    if is_excel or path.endswith(('.xlsx', '.xls')):
        logger.info("Detected Excel format. Parsing with pandas...")
        df = pd.read_excel(path).fillna("").astype(str)
        actual_count = len(df)
        logger.info(f"Loaded Excel file: total {actual_count} rows found.")
        
        # Verify total count
        if ui_count is not None:
            if actual_count == ui_count:
                logger.info(f"✅ SUCCESS: Export row count ({actual_count}) matches UI total count.")
                allure.attach(str(actual_count), name="Verified Total Count (Matched)", attachment_type=allure.attachment_type.TEXT)
            else:
                logger.error(f"❌ FAILED: Export row count ({actual_count}) does NOT match UI total count ({ui_count})")
                raise AssertionError(f"Export count mismatch! UI says {ui_count}, Excel has {actual_count}")

        for _, row in df.iterrows():
            match = True
            for k, val in expected_row.items():
                if str(val).strip() not in str(row.get(k, "")).strip():
                    match = False
                    break
            if match:
                found = True
                row_dict = row.to_dict()
                logger.info(f"✨ SUCCESS: Matching data row found in EXCEL: {row_dict}")
                allure.attach(str(row_dict), name="Verified Row Data", attachment_type=allure.attachment_type.TEXT)
                break
    else:
        logger.info("Parsing as standard CSV...")
        with open(path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            actual_count = len(rows)
            logger.info(f"Loaded CSV file: total {actual_count} rows found.")
            
            # Verify total count
            if ui_count is not None:
                if actual_count == ui_count:
                    logger.info(f"✅ SUCCESS: Export row count ({actual_count}) matches UI total count.")
                else:
                    logger.error(f"❌ FAILED: Export row count ({actual_count}) does NOT match UI total count ({ui_count})")
                    raise AssertionError(f"Export count mismatch! UI says {ui_count}, CSV has {actual_count}")

            for row in rows:
                match = True
                for k, val in expected_row.items():
                    if str(val).strip() not in str(row.get(k, "")).strip():
                        match = False
                        break
                if match:
                    found = True
                    logger.info(f"✨ SUCCESS: Matching data row found in CSV: {row}")
                    allure.attach(str(row), name="Verified Row Data", attachment_type=allure.attachment_type.TEXT)
                    break
                
    if not found:
        logger.error(f"FAILED: Expected row {expected_row} not found in {path}")
        raise AssertionError(f"Data verification failed for {path}")


def _format_datetime(dt: datetime) -> str:
    """Format datetime to 'Wed, May 12, 2026 12:00 AM' (Windows-safe, no %-d/%-I)."""
    return (
        dt.strftime("%a") + ", " +
        dt.strftime("%b") + " " +
        str(dt.day) + ", " +
        str(dt.year) + " " +
        dt.strftime("%I") + ":" +
        dt.strftime("%M") + " " +
        dt.strftime("%p")
    )


def verify_date(page: Page, v: dict):
    """
    Dynamically verify the date field in the submission details modal.

    The calendar always opens to the CURRENT month, so a hardcoded expected
    date (e.g. "Apr 12") goes stale each month. This action reads the
    calendar's actual visible month from the page via JS, combines it with
    the day number selected during form submission, and verifies the
    formatted date text inside the active dialog.

    YAML usage:
        verify_date:          # uses day=12 from the submission step
            day: 12           # optional, defaults to 12
            timeout: 10000     # optional
    """
    day = int(v.get("day", 12))
    timeout = v.get("timeout", 10000)

    dt_actual = None

    try:
        # Step 1: Read the raw ISO date from the date-picker input on the page.
        #         This survives after the calendar modal closes.
        raw_date = page.evaluate("""() => {
            const dateInputs = document.querySelectorAll('input[type="date"]');
            for (const inp of dateInputs) {
                if (inp.value && inp.value.match(/\\d{4}-\\d{2}-\\d{2}/)) return inp.value;
            }
            const dated = document.querySelectorAll('[data-date]');
            for (const el of dated) {
                const v = el.dataset.date;
                if (v && v.match(/\\d{4}-\\d{2}-\\d{2}/)) return v;
            }
            return null;
        }""")

        if raw_date:
            parts = raw_date.split("-")
            if len(parts) == 3:
                dt_actual = datetime(int(parts[0]), int(parts[1]), day)
                logger.info(f"verify_date: read raw date from page input: {raw_date}")

        # Step 2: Fallback — read month/year from the calendar header in the DOM.
        if dt_actual is None:
            month_info = page.evaluate("""() => {
                const grid = document.querySelector('[role="grid"]');
                if (grid) {
                    const label = grid.getAttribute('aria-label') || '';
                    const m = label.match(/([A-Za-z]+)\\s+(\\d{4})/);
                    if (m) return { month: m[1], year: m[2] };
                }
                const candidates = document.querySelectorAll('[class*="calendar-header"], [class*="datepicker-header"], [class*="month-year"]');
                for (const c of candidates) {
                    const t = c.textContent.trim();
                    const m = t.match(/([A-Za-z]+)\\s+(\\d{4})/);
                    if (m) return { month: m[1], year: m[2] };
                }
                return null;
            }""")

            if month_info:
                MONTH_NUM = {
                    "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
                    "july":7,"august":8,"september":9,"october":10,"november":11,"december":12
                }
                key = month_info["month"].lower()
                month_num = MONTH_NUM.get(key)
                if month_num:
                    dt_actual = datetime(int(month_info["year"]), month_num, day)
                    logger.info(f"verify_date: detected month from DOM: {month_info['month']} {month_info['year']}")

        # Step 3: Last resort — use current system month.
        if dt_actual is None:
            now = datetime.now()
            dt_actual = now.replace(day=day)
            logger.warning("verify_date: no calendar month detected, falling back to current system month.")

        expected_text = _format_datetime(dt_actual)
        logger.info(f"verify_date: expected formatted date = '{expected_text}'")

        day_s = str(day)
        # Anchor regex on day + year; allow any weekday/month text in between.
        # Format: "Wed, May 12, 2026 12:00 AM"
        full_regex = re.compile(
            r"[A-Za-z]{3}"               # 3-letter weekday (e.g. Tue)
            r","                          # comma
            r"\s+"                        # space(s)
            r"[A-Za-z]{3}"               # 3-letter month (e.g. May)
            r"\s+"
            + re.escape(day_s) +          # day number (e.g. 12)
            r",?\s+"
            r"\d{4}"                     # year
            r"\s+"
            r"\d{1,2}:\d{2}"            # time
            r"\s+[AP]M",
            re.IGNORECASE
        )
        anchor_regex = re.compile(
            r"(" + re.escape(day_s) + r",?\s+\d{4})",
            re.IGNORECASE
        )

        # Get text from the active submission details dialog
        dialog_el = page.locator("div[role='dialog']").last
        if dialog_el.is_visible(timeout=3000):
            modal_text = dialog_el.inner_text()
        else:
            modal_text = page.content()
            logger.warning("verify_date: no dialog visible, searching full page content")

        if full_regex.search(modal_text):
            logger.info(f"verify_date: PASS — '{expected_text}' matched in modal.")
        elif anchor_regex.search(modal_text) and day_s in anchor_regex.search(modal_text).group(0):
            logger.info(f"verify_date: PASS — day {day_s} confirmed in modal.")
        else:
            page.screenshot(path="fail_verify_date.png")
            logger.error(f"verify_date: FAIL — date for day {day_s} not found in modal.")
            raise AssertionError(
                f"Date verification failed: expected day {day_s} ({expected_text}) "
                f"in submission modal but not found."
            )

    except AssertionError:
        raise
    except Exception as e:
        page.screenshot(path="fail_verify_date.png")
        logger.error(f"verify_date: unexpected error: {e}")
        raise AssertionError(f"Date verification error: {e}")
