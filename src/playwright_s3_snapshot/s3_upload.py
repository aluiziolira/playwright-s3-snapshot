"""S3 upload functionality for screenshots."""

from datetime import datetime
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class S3Uploader:
    """Handles uploading files to S3 with proper error handling."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str = "us-east-1",
    ):
        """
        Initialize S3 uploader.

        Args:
            bucket_name: Name of the S3 bucket
            aws_access_key_id: AWS access key (optional, can use env vars)
            aws_secret_access_key: AWS secret key (optional, can use env vars)
            region_name: AWS region name
        """
        self.bucket_name = bucket_name

        session_kwargs = {"region_name": region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update(
                {
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                }
            )

        session = boto3.Session(**session_kwargs)
        self.s3_client = session.client("s3")

    def upload_file(
        self,
        file_path: str,
        key_prefix: str = "",
        timestamp: datetime | None = None,
    ) -> str:
        """
        Upload a file to S3 with timestamped naming.

        Args:
            file_path: Path to the file to upload
            key_prefix: Optional prefix for the S3 key
            timestamp: Optional timestamp (defaults to now)

        Returns:
            S3 URL of the uploaded file

        Raises:
            FileNotFoundError: If file doesn't exist
            NoCredentialsError: If AWS credentials not found
            ClientError: If S3 upload fails
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if timestamp is None:
            timestamp = datetime.now()

        # Generate timestamped key
        timestamp_str = timestamp.strftime("%Y-%m-%d_%H%M%S")
        file_extension = file_path.suffix

        if key_prefix:
            key_prefix = key_prefix.rstrip("/") + "/"

        s3_key = f"{key_prefix}{timestamp_str}{file_extension}"

        try:
            # Upload file
            self.s3_client.upload_file(
                str(file_path),
                self.bucket_name,
                s3_key,
                ExtraArgs={"ContentType": self._get_content_type(file_extension)},
            )

            # Return S3 URL
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"

        except NoCredentialsError as e:
            raise NoCredentialsError() from None
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                raise ClientError(
                    {
                        "Error": {
                            "Code": "NoSuchBucket",
                            "Message": f"Bucket '{self.bucket_name}' does not exist",
                        }
                    },
                    "upload_file",
                ) from None
            raise

    def _get_content_type(self, file_extension: str) -> str:
        """Get appropriate content type for file extension."""
        content_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".pdf": "application/pdf",
            ".html": "text/html",
        }
        return content_types.get(file_extension.lower(), "application/octet-stream")


def upload_to_s3(
    file_path: str,
    bucket_name: str,
    key_prefix: str = "",
    aws_access_key_id: str | None = None,
    aws_secret_access_key: str | None = None,
    region_name: str = "us-east-1",
) -> str:
    """
    Convenience function to upload a file to S3.

    Args:
        file_path: Path to the file to upload
        bucket_name: Name of the S3 bucket
        key_prefix: Optional prefix for the S3 key
        aws_access_key_id: AWS access key (optional)
        aws_secret_access_key: AWS secret key (optional)
        region_name: AWS region name

    Returns:
        S3 URL of the uploaded file
    """
    uploader = S3Uploader(
        bucket_name=bucket_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )

    return uploader.upload_file(file_path, key_prefix)
