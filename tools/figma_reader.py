#!/usr/bin/env python3
"""Figma design screenshot tool.

Usage:
    python tools/figma_reader.py "<figma_url>" [--output <path>] [--zoom 55] [--debug]
    python tools/figma_reader.py "<figma_url>" -i [--zoom 55]   # interactive mode

The tool launches Chrome, navigates to the Figma URL, waits for the canvas to load,
and takes a screenshot. Interactive mode pauses before capture so you can manually
select the right frame/node if the URL node-id does not reveal it.
"""
import argparse
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def parse_args():
    parser = argparse.ArgumentParser(description="Screenshot a Figma design frame/node.")
    parser.add_argument("url", help="Figma URL (supports node-id)")
    parser.add_argument("-o", "--output", help="Output screenshot path")
    parser.add_argument("-z", "--zoom", type=int, default=55, help="Zoom percentage (default 55)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Pause for manual selection before screenshot")
    parser.add_argument("--debug", action="store_true", help="Run headed with slow mo")
    parser.add_argument("--width", type=int, default=1920, help="Viewport width")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height")
    parser.add_argument("--wait", type=int, default=10, help="Seconds to wait for canvas load")
    return parser.parse_args()


def build_figma_url(url: str, zoom: int) -> str:
    """Ensure zoom parameter is present in the URL."""
    parsed = re.sub(r"[?&]zoom-scale=\d+", "", url)
    sep = "&" if "?" in parsed else "?"
    return f"{parsed}{sep}zoom-scale={zoom}"


def main():
    args = parse_args()
    output = args.output or f"figma_screenshot_{int(time.time())}.png"
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figma_url = build_figma_url(args.url, args.zoom)
    print(f"Opening Figma: {figma_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not args.interactive and not args.debug,
            slow_mo=300 if args.debug else None,
            channel="chrome",
        )
        context = browser.new_context(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=2,
        )
        page = context.new_page()

        page.goto(figma_url, wait_until="domcontentloaded", timeout=120000)

        # Wait for Figma canvas to be present
        try:
            page.wait_for_selector("[data-testid='canvas']", timeout=args.wait * 1000)
        except Exception:
            print("Canvas selector not found, continuing with generic wait...")

        page.wait_for_timeout(5000)

        if args.interactive:
            print("\nInteractive mode: please select the correct frame/node in the browser.")
            input("Press ENTER when ready to capture the screenshot...")
        else:
            # Give the canvas a bit more time to render in auto mode
            page.wait_for_timeout(args.wait * 1000)

        page.screenshot(path=str(output_path), full_page=False)
        print(f"Screenshot saved: {output_path.resolve()}")

        browser.close()


if __name__ == "__main__":
    main()
