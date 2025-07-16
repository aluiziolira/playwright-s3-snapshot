"""Tests for screenshot functionality.

This module tests the screenshot system including:
- Playwright screenshot capture
- Async and sync screenshot functions
- Error handling and retries
- File output validation
"""

import asyncio
from pathlib import Path
from typing import Optional
from unittest.mock import Mock, patch, AsyncMock

import pytest

from playwright_s3_snapshot.screenshot import take_screenshot, take_screenshot_sync


class TestScreenshotCapture:
    """Tests for screenshot capture functionality."""

    @patch("playwright_s3_snapshot.screenshot.async_playwright")
    @pytest.mark.asyncio
    async def test_take_screenshot_success(self, mock_playwright: Mock, temp_dir: str) -> None:
        """Test successful screenshot capture."""
        output_path = str(Path(temp_dir) / "screenshot.png")
        
        # Mock playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance
        
        # Test screenshot
        result = await take_screenshot(
            url="https://example.com",
            output_path=output_path,
            viewport_width=1920,
            viewport_height=1080,
            wait_timeout=30000
        )
        
        assert result == output_path
        
        # Verify calls
        mock_playwright_instance.chromium.launch.assert_called_once()
        mock_browser.new_context.assert_called_once_with(
            viewport={"width": 1920, "height": 1080}
        )
        mock_page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="networkidle",
            timeout=30000
        )
        mock_page.screenshot.assert_called_once_with(
            path=output_path,
            full_page=True
        )

    @patch("playwright_s3_snapshot.screenshot.async_playwright")
    @pytest.mark.asyncio
    async def test_take_screenshot_navigation_error(self, mock_playwright: Mock, temp_dir: str) -> None:
        """Test screenshot with navigation error."""
        output_path = str(Path(temp_dir) / "screenshot.png")
        
        # Mock playwright to raise navigation error
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.goto.side_effect = Exception("Navigation timeout")
        mock_context = AsyncMock()
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance
        
        # Test screenshot failure
        with pytest.raises(Exception, match="Navigation timeout"):
            await take_screenshot(
                url="https://example.com",
                output_path=output_path
            )

    @patch("playwright_s3_snapshot.screenshot.async_playwright")
    @pytest.mark.asyncio
    async def test_take_screenshot_custom_viewport(self, mock_playwright: Mock, temp_dir: str) -> None:
        """Test screenshot with custom viewport dimensions."""
        output_path = str(Path(temp_dir) / "screenshot.png")
        
        # Mock playwright components
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        
        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance
        
        # Test with custom dimensions
        await take_screenshot(
            url="https://example.com",
            output_path=output_path,
            viewport_width=1366,
            viewport_height=768,
            wait_timeout=60000
        )
        
        # Verify custom viewport was used
        mock_browser.new_context.assert_called_once_with(
            viewport={"width": 1366, "height": 768}
        )
        mock_page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="networkidle",
            timeout=60000
        )


class TestSynchronousScreenshot:
    """Tests for synchronous screenshot functions."""

    @patch("playwright_s3_snapshot.screenshot.asyncio.run")
    @patch("playwright_s3_snapshot.screenshot.take_screenshot")
    def test_take_screenshot_sync_success(self, mock_take_screenshot: Mock, mock_asyncio_run: Mock, temp_dir: str) -> None:
        """Test synchronous screenshot wrapper."""
        output_path = str(Path(temp_dir) / "screenshot.png")
        mock_take_screenshot.return_value = output_path
        mock_asyncio_run.return_value = output_path
        
        result = take_screenshot_sync(
            url="https://example.com",
            output_path=output_path,
            viewport_width=1920,
            viewport_height=1080,
            wait_timeout=30000
        )
        
        assert result == output_path
        mock_asyncio_run.assert_called_once()

    @patch("playwright_s3_snapshot.screenshot.asyncio.run")
    @patch("playwright_s3_snapshot.screenshot.take_screenshot")
    def test_take_screenshot_sync_error(self, mock_take_screenshot: Mock, mock_asyncio_run: Mock, temp_dir: str) -> None:
        """Test synchronous screenshot wrapper with error."""
        output_path = str(Path(temp_dir) / "screenshot.png")
        mock_asyncio_run.side_effect = Exception("Screenshot failed")
        
        with pytest.raises(Exception, match="Screenshot failed"):
            take_screenshot_sync(
                url="https://example.com",
                output_path=output_path
            )

    @patch("playwright_s3_snapshot.screenshot.asyncio.run")
    @patch("playwright_s3_snapshot.screenshot.take_screenshot")
    def test_take_screenshot_sync_default_params(self, mock_take_screenshot: Mock, mock_asyncio_run: Mock, temp_dir: str) -> None:
        """Test synchronous screenshot with default parameters."""
        output_path = str(Path(temp_dir) / "screenshot.png")
        mock_asyncio_run.return_value = output_path
        
        result = take_screenshot_sync(
            url="https://example.com",
            output_path=output_path
        )
        
        assert result == output_path
        # Verify asyncio.run was called with the coroutine
        mock_asyncio_run.assert_called_once()
        args, kwargs = mock_asyncio_run.call_args
        # The first argument should be the coroutine from take_screenshot
        assert asyncio.iscoroutine(args[0])