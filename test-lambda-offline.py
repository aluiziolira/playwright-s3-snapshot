#!/usr/bin/env python3
"""Offline testing script for Lambda functions (no S3 upload)."""

import json
import os
import sys
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Mock the S3 upload to test screenshot functionality without AWS
import unittest.mock


def mock_upload_to_s3(*args, **kwargs):
    """Mock S3 upload for offline testing."""
    return "https://test-bucket.s3.amazonaws.com/test-key.png"


# Apply the mock
with unittest.mock.patch(
    "playwright_s3_snapshot.snapshot.upload_to_s3", side_effect=mock_upload_to_s3
):
    from playwright_s3_snapshot.lambda_handler import lambda_handler, batch_handler


class MockContext:
    """Mock Lambda context for local testing."""

    def __init__(self):
        self.function_name = "test-function"
        self.function_version = "1"
        self.aws_request_id = "test-request-id"
        self.memory_limit_in_mb = "3008"
        self.remaining_time_in_millis = lambda: 300000


def test_screenshot_functionality():
    """Test screenshot functionality without S3 upload."""
    print("🧪 Testing Lambda screenshot functionality (offline mode)...")

    event = {
        "url": "https://example.com",
        "bucket": "test-bucket",
        "prefix": "test/",
        "width": 1280,
        "height": 720,
    }

    print(f"Event: {json.dumps(event, indent=2)}")

    try:
        result = lambda_handler(event, MockContext())
        print(f"✅ Result: {json.dumps(result, indent=2)}")

        # Check if screenshot was taken successfully
        if result["statusCode"] == 200:
            body = json.loads(result["body"])
            return body["success"] and "s3_url" in body["result"]

        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_error_validation():
    """Test input validation."""
    print("\n🧪 Testing input validation...")

    # Test missing URL
    event = {"bucket": "test-bucket"}

    try:
        result = lambda_handler(event, MockContext())
        print(f"Expected validation error: {json.dumps(result, indent=2)}")

        if result["statusCode"] == 500:
            body = json.loads(result["body"])
            return not body["success"] and "URL is required" in body["error"]

        return False
    except Exception as e:
        print(f"Unexpected exception: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Offline Lambda Testing")
    print("=" * 50)

    success_count = 0
    total_tests = 2

    # Run tests
    if test_screenshot_functionality():
        success_count += 1

    if test_error_validation():
        success_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} passed")

    if success_count == total_tests:
        print("✅ All tests passed! Lambda functions are working correctly.")
        print("💡 S3 upload will work when deployed with proper AWS credentials.")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
