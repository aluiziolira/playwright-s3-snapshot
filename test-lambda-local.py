#!/usr/bin/env python3
"""Local testing script for Lambda functions."""

import json
import os
import sys
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from playwright_s3_snapshot.lambda_handler import lambda_handler, batch_handler


class MockContext:
    """Mock Lambda context for local testing."""

    def __init__(self):
        self.function_name = "test-function"
        self.function_version = "1"
        self.aws_request_id = "test-request-id"
        self.memory_limit_in_mb = "3008"
        self.remaining_time_in_millis = lambda: 300000


def test_single_screenshot():
    """Test single screenshot Lambda function."""
    print("🧪 Testing single screenshot Lambda function...")

    event = {
        "url": "https://example.com",
        "bucket": os.getenv("TEST_BUCKET", "test-bucket"),
        "prefix": "test-lambda/",
        "width": 1280,
        "height": 720,
    }

    print(f"Event: {json.dumps(event, indent=2)}")

    try:
        result = lambda_handler(event, MockContext())
        print(f"✅ Result: {json.dumps(result, indent=2)}")
        return result["statusCode"] == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_batch_screenshots():
    """Test batch screenshot Lambda function."""
    print("\n🧪 Testing batch screenshot Lambda function...")

    event = {
        "urls": ["https://example.com", "https://httpbin.org/html"],
        "bucket": os.getenv("TEST_BUCKET", "test-bucket"),
        "prefix": "test-batch/",
    }

    print(f"Event: {json.dumps(event, indent=2)}")

    try:
        result = batch_handler(event, MockContext())
        print(f"✅ Result: {json.dumps(result, indent=2)}")
        return result["statusCode"] == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_error_handling():
    """Test error handling."""
    print("\n🧪 Testing error handling...")

    # Test missing URL
    event = {"bucket": "test-bucket"}

    try:
        result = lambda_handler(event, MockContext())
        print(f"Expected error result: {json.dumps(result, indent=2)}")
        return result["statusCode"] == 500
    except Exception as e:
        print(f"Unexpected exception: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Local Lambda Testing")
    print("=" * 50)

    # Set test environment variables
    os.environ.setdefault("AWS_REGION", "us-east-1")

    success_count = 0
    total_tests = 3

    # Run tests
    if test_single_screenshot():
        success_count += 1

    if test_batch_screenshots():
        success_count += 1

    if test_error_handling():
        success_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} passed")

    if success_count == total_tests:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
