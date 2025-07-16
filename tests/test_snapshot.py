"""Tests for snapshot functionality.

This module tests the snapshot system including:
- End-to-end screenshot and upload workflow
- Integration between screenshot and S3 upload
- Error handling and retry logic
- Result formatting and validation
"""

from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

import pytest
import boto3
from moto import mock_aws

from playwright_s3_snapshot.snapshot import take_snapshot_to_s3_sync


class TestSnapshotIntegration:
    """Tests for the integrated snapshot functionality."""

    @patch("playwright_s3_snapshot.snapshot.take_screenshot_sync")
    @mock_aws
    def test_take_snapshot_to_s3_success(self, mock_screenshot: Mock, temp_dir: str) -> None:
        """Test successful screenshot and upload workflow."""
        # Setup test file
        test_file = Path(temp_dir) / "screenshot.png"
        test_file.write_bytes(b"test screenshot data")
        mock_screenshot.return_value = str(test_file)
        
        # Setup S3 bucket
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        
        # Test the workflow
        result = take_snapshot_to_s3_sync(
            url="https://example.com",
            bucket_name="test-bucket",
            key_prefix="screenshots/",
            viewport_width=1920,
            viewport_height=1080,
            wait_timeout=30000,
            region_name="us-east-1"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["url"] == "https://example.com"
        assert result["bucket"] == "test-bucket"
        assert "screenshots/" in result["key"]
        assert result["s3_url"] == f"https://test-bucket.s3.amazonaws.com/{result['key']}"

    @patch("playwright_s3_snapshot.snapshot.take_screenshot_sync")
    def test_take_snapshot_to_s3_screenshot_failure(self, mock_screenshot: Mock) -> None:
        """Test workflow with screenshot failure."""
        mock_screenshot.side_effect = Exception("Screenshot failed")
        
        result = take_snapshot_to_s3_sync(
            url="https://example.com",
            bucket_name="test-bucket",
            region_name="us-east-1"
        )
        
        assert result["success"] is False
        assert "Screenshot failed" in result["error"]

    @patch("playwright_s3_snapshot.snapshot.take_screenshot_sync")
    def test_take_snapshot_to_s3_s3_failure(self, mock_screenshot: Mock, temp_dir: str) -> None:
        """Test workflow with S3 upload failure."""
        # Setup test file
        test_file = Path(temp_dir) / "screenshot.png"
        test_file.write_bytes(b"test screenshot data")
        mock_screenshot.return_value = str(test_file)
        
        # Test with non-existent bucket (no moto mock)
        result = take_snapshot_to_s3_sync(
            url="https://example.com",
            bucket_name="nonexistent-bucket",
            region_name="us-east-1"
        )
        
        assert result["success"] is False
        assert "error" in result

    @patch("playwright_s3_snapshot.snapshot.take_screenshot_sync")
    @mock_aws
    def test_take_snapshot_to_s3_custom_dimensions(self, mock_screenshot: Mock, temp_dir: str) -> None:
        """Test workflow with custom viewport dimensions."""
        # Setup test file
        test_file = Path(temp_dir) / "screenshot.png"
        test_file.write_bytes(b"test screenshot data")
        mock_screenshot.return_value = str(test_file)
        
        # Setup S3 bucket
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        
        # Test with custom dimensions
        result = take_snapshot_to_s3_sync(
            url="https://example.com",
            bucket_name="test-bucket",
            viewport_width=1366,
            viewport_height=768,
            wait_timeout=60000,
            region_name="us-east-1"
        )
        
        assert result["success"] is True
        
        # Verify screenshot was called with custom dimensions
        mock_screenshot.assert_called_once_with(
            url="https://example.com",
            output_path=mock_screenshot.call_args[1]["output_path"],
            viewport_width=1366,
            viewport_height=768,
            wait_timeout=60000
        )