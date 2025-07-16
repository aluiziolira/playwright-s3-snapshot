"""Tests for S3 upload functionality.

This module tests the S3 upload system including:
- Basic upload operations
- Error handling and retries
- Convenience functions
- File validation
"""

from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

import pytest
import boto3
from moto import mock_aws

from playwright_s3_snapshot.s3_upload import S3Uploader, upload_to_s3


class TestS3Uploader:
    """Tests for S3Uploader class."""

    @mock_aws
    def test_upload_success(self, temp_dir: str) -> None:
        """Test successful file upload to S3."""
        # Create test file
        test_file = Path(temp_dir) / "test.png"
        test_file.write_bytes(b"test image data")
        
        # Create S3 bucket
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        
        # Test upload
        uploader = S3Uploader(
            bucket_name="test-bucket",
            region_name="us-east-1"
        )
        
        result = uploader.upload(str(test_file), "test.png")
        
        assert result["success"] is True
        assert result["s3_url"] == "https://test-bucket.s3.amazonaws.com/test.png"
        assert result["key"] == "test.png"

    @mock_aws
    def test_upload_with_prefix(self, temp_dir: str) -> None:
        """Test upload with key prefix."""
        test_file = Path(temp_dir) / "test.png"
        test_file.write_bytes(b"test image data")
        
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        
        uploader = S3Uploader(
            bucket_name="test-bucket",
            key_prefix="screenshots/",
            region_name="us-east-1"
        )
        
        result = uploader.upload(str(test_file), "test.png")
        
        assert result["key"] == "screenshots/test.png"
        assert "screenshots/test.png" in result["s3_url"]

    def test_upload_file_not_found(self) -> None:
        """Test upload with missing file."""
        uploader = S3Uploader(
            bucket_name="test-bucket",
            region_name="us-east-1"
        )
        
        result = uploader.upload("nonexistent.png", "test.png")
        
        assert result["success"] is False
        assert "error" in result

    @mock_aws
    def test_upload_invalid_bucket(self, temp_dir: str) -> None:
        """Test upload to non-existent bucket."""
        test_file = Path(temp_dir) / "test.png"
        test_file.write_bytes(b"test image data")
        
        uploader = S3Uploader(
            bucket_name="nonexistent-bucket",
            region_name="us-east-1"
        )
        
        result = uploader.upload(str(test_file), "test.png")
        
        assert result["success"] is False
        assert "error" in result


class TestS3ConvenienceFunctions:
    """Tests for S3 convenience functions."""

    @mock_aws
    def test_upload_to_s3_success(self, temp_dir: str) -> None:
        """Test convenience function for S3 upload."""
        test_file = Path(temp_dir) / "test.png"
        test_file.write_bytes(b"test image data")
        
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        
        result = upload_to_s3(
            file_path=str(test_file),
            bucket_name="test-bucket",
            key="test.png",
            region_name="us-east-1"
        )
        
        assert result["success"] is True
        assert result["s3_url"] == "https://test-bucket.s3.amazonaws.com/test.png"

    def test_upload_to_s3_missing_file(self) -> None:
        """Test convenience function with missing file."""
        result = upload_to_s3(
            file_path="nonexistent.png",
            bucket_name="test-bucket",
            key="test.png",
            region_name="us-east-1"
        )
        
        assert result["success"] is False
        assert "error" in result

    @mock_aws
    def test_upload_to_s3_with_metadata(self, temp_dir: str) -> None:
        """Test upload with custom metadata."""
        test_file = Path(temp_dir) / "test.png"
        test_file.write_bytes(b"test image data")
        
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        
        metadata = {"Content-Type": "image/png", "Cache-Control": "max-age=3600"}
        
        result = upload_to_s3(
            file_path=str(test_file),
            bucket_name="test-bucket",
            key="test.png",
            region_name="us-east-1",
            metadata=metadata
        )
        
        assert result["success"] is True
        
        # Verify metadata was set
        response = s3_client.head_object(Bucket="test-bucket", Key="test.png")
        assert response["ContentType"] == "image/png"
        assert response["CacheControl"] == "max-age=3600"