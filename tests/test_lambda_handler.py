"""Tests for AWS Lambda handler functionality.

This module tests the Lambda handler including:
- Event processing and validation
- Error handling and responses
- Lambda-specific functionality
"""

import json
from typing import Dict, Any
from unittest.mock import Mock, patch

import pytest

from playwright_s3_snapshot.lambda_handler import lambda_handler


class TestLambdaHandler:
    """Tests for the main Lambda handler function."""

    @patch("playwright_s3_snapshot.lambda_handler.take_snapshot_to_s3_sync")
    def test_lambda_handler_success(self, mock_snapshot: Mock, lambda_event: Dict[str, Any]) -> None:
        """Test successful Lambda handler execution."""
        mock_snapshot.return_value = {
            "success": True,
            "s3_url": "https://test-bucket.s3.amazonaws.com/screenshot.png",
            "key": "screenshot.png",
            "file_size": 12345,
            "timestamp": "2025-07-16T12:00:00Z"
        }
        
        result = lambda_handler(lambda_event, {})
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["success"] is True
        assert body["s3_url"] == "https://test-bucket.s3.amazonaws.com/screenshot.png"

    def test_lambda_handler_missing_url(self) -> None:
        """Test Lambda handler with missing URL."""
        invalid_event = {"bucket": "test-bucket"}
        
        result = lambda_handler(invalid_event, {})
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["success"] is False
        assert "error" in body

    def test_lambda_handler_missing_bucket(self) -> None:
        """Test Lambda handler with missing bucket."""
        invalid_event = {"url": "https://example.com"}
        
        result = lambda_handler(invalid_event, {})
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["success"] is False
        assert "error" in body

    @patch("playwright_s3_snapshot.lambda_handler.take_snapshot_to_s3_sync")
    def test_lambda_handler_screenshot_failure(self, mock_snapshot: Mock, lambda_event: Dict[str, Any]) -> None:
        """Test Lambda handler with screenshot failure."""
        mock_snapshot.return_value = {
            "success": False,
            "error": "Failed to take screenshot"
        }
        
        result = lambda_handler(lambda_event, {})
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["success"] is False
        assert body["error"] == "Failed to take screenshot"

    @patch("playwright_s3_snapshot.lambda_handler.take_snapshot_to_s3_sync")
    def test_lambda_handler_exception(self, mock_snapshot: Mock, lambda_event: Dict[str, Any]) -> None:
        """Test Lambda handler with unexpected exception."""
        mock_snapshot.side_effect = Exception("Unexpected error")
        
        result = lambda_handler(lambda_event, {})
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["success"] is False
        assert "Unexpected error" in body["error"]