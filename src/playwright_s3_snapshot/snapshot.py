"""Main snapshot functionality combining screenshot and S3 upload."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from .screenshot import take_screenshot
from .s3_upload import upload_to_s3


async def take_snapshot_to_s3(
    url: str,
    bucket_name: str,
    key_prefix: str = "",
    temp_dir: str = "/tmp",
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    wait_timeout: int = 30000,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: str = "us-east-1",
    cleanup_local: bool = True,
) -> dict:
    """
    Take a screenshot and upload it directly to S3.
    
    Args:
        url: The URL to screenshot
        bucket_name: S3 bucket name
        key_prefix: Optional prefix for S3 key
        temp_dir: Directory for temporary files
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height
        wait_timeout: Page load timeout in milliseconds
        aws_access_key_id: AWS access key (optional)
        aws_secret_access_key: AWS secret key (optional)
        region_name: AWS region
        cleanup_local: Whether to delete local file after upload
        
    Returns:
        Dictionary with screenshot info:
        {
            "url": "https://example.com",
            "s3_url": "https://bucket.s3.amazonaws.com/prefix/2025-07-15_143022.png",
            "s3_key": "prefix/2025-07-15_143022.png", 
            "timestamp": "2025-07-15T14:30:22",
            "file_size": 55531
        }
        
    Raises:
        Exception: If screenshot or upload fails
    """
    timestamp = datetime.now()
    
    # Generate temporary file path
    timestamp_str = timestamp.strftime("%Y-%m-%d_%H%M%S")
    temp_file = Path(temp_dir) / f"screenshot_{timestamp_str}.png"
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Take screenshot
        local_path = await take_screenshot(
            url=url,
            output_path=str(temp_file),
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            wait_timeout=wait_timeout,
        )
        
        # Get file size
        file_size = Path(local_path).stat().st_size
        
        # Upload to S3
        s3_url = upload_to_s3(
            file_path=local_path,
            bucket_name=bucket_name,
            key_prefix=key_prefix,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        
        # Generate S3 key for response
        if key_prefix:
            key_prefix = key_prefix.rstrip("/") + "/"
        s3_key = f"{key_prefix}{timestamp_str}.png"
        
        # Cleanup local file if requested
        if cleanup_local:
            Path(local_path).unlink(missing_ok=True)
        
        return {
            "url": url,
            "s3_url": s3_url,
            "s3_key": s3_key,
            "timestamp": timestamp.isoformat(),
            "file_size": file_size,
        }
        
    except Exception:
        # Cleanup temp file on error
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)
        raise


def take_snapshot_to_s3_sync(
    url: str,
    bucket_name: str,
    key_prefix: str = "",
    temp_dir: str = "/tmp",
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    wait_timeout: int = 30000,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: str = "us-east-1",
    cleanup_local: bool = True,
) -> dict:
    """
    Synchronous wrapper for take_snapshot_to_s3.
    
    Args: Same as take_snapshot_to_s3
    
    Returns: Same as take_snapshot_to_s3
    """
    import asyncio
    
    return asyncio.run(
        take_snapshot_to_s3(
            url=url,
            bucket_name=bucket_name,
            key_prefix=key_prefix,
            temp_dir=temp_dir,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            wait_timeout=wait_timeout,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            cleanup_local=cleanup_local,
        )
    )