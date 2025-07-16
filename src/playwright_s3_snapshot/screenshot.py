"""Core screenshot functionality using Playwright."""

from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright


async def take_screenshot(
    url: str,
    output_path: str | None = None,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    wait_timeout: int = 30000,
) -> str:
    """
    Take a full-page screenshot of the given URL.

    Args:
        url: The URL to screenshot
        output_path: Optional path to save the screenshot. If None, generates timestamp-based name.
        viewport_width: Browser viewport width in pixels
        viewport_height: Browser viewport height in pixels
        wait_timeout: Maximum time to wait for page load in milliseconds

    Returns:
        Path to the saved screenshot file

    Raises:
        Exception: If screenshot fails
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = f"screenshot_{timestamp}.png"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # Configure browser for Lambda environment
        browser_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-dev-tools",
            "--disable-setuid-sandbox",
            "--no-first-run",
            "--no-zygote",
            "--single-process",
            "--disable-background-timer-throttling",
            "--disable-background-networking",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
        ]

        browser = await p.chromium.launch(headless=True, args=browser_args)

        try:
            page = await browser.new_page(
                viewport={"width": viewport_width, "height": viewport_height}
            )

            await page.goto(url, wait_until="networkidle", timeout=wait_timeout)

            await page.screenshot(path=str(output_path), full_page=True, type="png")

            return str(output_path)

        finally:
            await browser.close()


def take_screenshot_sync(
    url: str,
    output_path: str | None = None,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    wait_timeout: int = 30000,
) -> str:
    """
    Synchronous wrapper for take_screenshot.

    Args:
        url: The URL to screenshot
        output_path: Optional path to save the screenshot
        viewport_width: Browser viewport width in pixels
        viewport_height: Browser viewport height in pixels
        wait_timeout: Maximum time to wait for page load in milliseconds

    Returns:
        Path to the saved screenshot file
    """
    import asyncio

    return asyncio.run(
        take_screenshot(url, output_path, viewport_width, viewport_height, wait_timeout)
    )
