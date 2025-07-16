"""Tests for CLI functionality.

This module tests the command-line interface including:
- URL validation
- Main execution flow
- Error handling and exit codes
"""

import sys
from unittest.mock import patch
import argparse

import pytest

from playwright_s3_snapshot.cli import main, validate_url


class TestURLValidation:
    """Tests for URL validation."""

    def test_validate_url_valid_https(self) -> None:
        """Test validation of valid HTTPS URL."""
        result = validate_url("https://example.com")
        assert result == "https://example.com"

    def test_validate_url_valid_http(self) -> None:
        """Test validation of valid HTTP URL."""
        result = validate_url("http://example.com")
        assert result == "http://example.com"

    def test_validate_url_no_scheme_adds_https(self) -> None:
        """Test validation of URL without scheme adds https."""
        result = validate_url("example.com")
        assert result == "https://example.com"

    def test_validate_url_invalid_format(self) -> None:
        """Test validation of invalid URL format."""
        with pytest.raises(argparse.ArgumentTypeError):
            validate_url("https://")


class TestCLIMainExecution:
    """Tests for main CLI execution."""

    def test_main_no_arguments(self) -> None:
        """Test main function with no arguments."""
        test_argv = ["snapshot"]
        
        with patch.object(sys, 'argv', test_argv):
            exit_code = main()
            assert exit_code == 1

    @patch("playwright_s3_snapshot.cli.take_snapshot_to_s3_sync")
    def test_main_s3_upload_success(self, mock_snapshot: None) -> None:
        """Test successful S3 upload execution."""
        mock_snapshot.return_value = {
            "success": True,
            "url": "https://example.com",
            "s3_url": "https://test-bucket.s3.amazonaws.com/screenshot.png"
        }
        
        test_argv = [
            "snapshot",
            "https://example.com",
            "--bucket", "test-bucket"
        ]
        
        with patch.object(sys, 'argv', test_argv):
            exit_code = main()
            assert exit_code == 0

    @patch("playwright_s3_snapshot.cli.take_screenshot_sync")
    def test_main_local_file_success(self, mock_screenshot: None, temp_dir: str) -> None:
        """Test successful local file execution."""
        from pathlib import Path
        
        output_path = str(Path(temp_dir) / "screenshot.png")
        mock_screenshot.return_value = output_path
        
        # Create the file to simulate screenshot success
        Path(output_path).write_bytes(b"test screenshot data")
        
        test_argv = [
            "snapshot",
            "https://example.com",
            "--output", output_path
        ]
        
        with patch.object(sys, 'argv', test_argv):
            exit_code = main()
            assert exit_code == 0

    def test_main_invalid_url(self) -> None:
        """Test execution with invalid URL."""
        test_argv = [
            "snapshot",
            "not-a-url"
        ]
        
        with patch.object(sys, 'argv', test_argv):
            exit_code = main()
            assert exit_code == 1