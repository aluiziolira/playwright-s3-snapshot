"""Shared pytest fixtures and configuration.

This module provides essential fixtures for the test suite including:
- Temporary directories for file operations
- Mock AWS services and Lambda events
- Basic test data structures
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests.

    Yields:
        Temporary directory path that is automatically cleaned up.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def lambda_event() -> Dict[str, Any]:
    """Create a basic Lambda event for testing.

    Returns:
        Dictionary containing standard Lambda event structure.
    """
    return {
        "url": "https://example.com",
        "bucket": "test-bucket",
        "prefix": "screenshots/",
        "width": 1920,
        "height": 1080,
        "timeout": 30000,
        "region": "us-east-1"
    }


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Create a sample configuration for testing.

    Returns:
        Dictionary containing standard configuration options.
    """
    return {
        "bucket": "test-bucket",
        "prefix": "screenshots/",
        "width": 1920,
        "height": 1080,
        "timeout": 30000,
        "region": "us-east-1",
        "parallel": True
    }


@pytest.fixture
def config_file(temp_dir: str, sample_config: Dict[str, Any]) -> str:
    """Create a temporary configuration file.

    Args:
        temp_dir: Temporary directory path.
        sample_config: Configuration data to write.

    Returns:
        Path to the created configuration file.
    """
    config_path = Path(temp_dir) / "config.json"
    config_path.write_text(json.dumps(sample_config, indent=2))
    return str(config_path)


@pytest.fixture
def s3_upload_result() -> Dict[str, Any]:
    """Create a successful S3 upload result for testing.

    Returns:
        Dictionary containing standard S3 upload response structure.
    """
    return {
        "success": True,
        "s3_url": "https://test-bucket.s3.amazonaws.com/screenshot.png",
        "key": "screenshot.png",
        "file_size": 12345,
        "timestamp": "2025-07-16T12:00:00Z"
    }


@pytest.fixture
def screenshot_result(temp_dir: str) -> str:
    """Create a mock screenshot file for testing.

    Args:
        temp_dir: Temporary directory path.

    Returns:
        Path to the created screenshot file.
    """
    screenshot_path = Path(temp_dir) / "screenshot.png"
    screenshot_path.write_bytes(b"mock screenshot data")
    return str(screenshot_path)