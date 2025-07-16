"""AWS Lambda handler for Playwright S3 Snapshot."""

import json
import os
import logging
from typing import Dict, Any, Optional

from .snapshot import take_snapshot_to_s3_sync

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for taking screenshots and uploading to S3.
    
    Expected event structure:
    {
        "url": "https://example.com",
        "bucket": "my-bucket",
        "prefix": "screenshots/",
        "width": 1920,
        "height": 1080,
        "timeout": 30000,
        "region": "us-east-1"
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {
            "success": true,
            "result": {
                "url": "https://example.com",
                "s3_url": "https://bucket.s3.amazonaws.com/key",
                "s3_key": "screenshots/2025-07-15_143022.png",
                "timestamp": "2025-07-15T14:30:22",
                "file_size": 55531
            }
        }
    }
    """
    try:
        logger.info(f"Processing screenshot request: {json.dumps(event, default=str)}")
        
        # Extract parameters from event
        url = event.get("url")
        if not url:
            raise ValueError("URL is required")
        
        bucket_name = event.get("bucket") or os.getenv("BUCKET_NAME")
        if not bucket_name:
            raise ValueError("Bucket name is required (via event.bucket or BUCKET_NAME env var)")
        
        # Optional parameters with defaults
        key_prefix = event.get("prefix", os.getenv("KEY_PREFIX", ""))
        viewport_width = int(event.get("width", os.getenv("VIEWPORT_WIDTH", 1920)))
        viewport_height = int(event.get("height", os.getenv("VIEWPORT_HEIGHT", 1080)))
        wait_timeout = int(event.get("timeout", os.getenv("WAIT_TIMEOUT", 30000)))
        region_name = event.get("region", os.getenv("AWS_REGION", "us-east-1"))
        
        logger.info(f"Taking screenshot: url={url}, bucket={bucket_name}, prefix={key_prefix}")
        
        # Take screenshot and upload to S3
        result = take_snapshot_to_s3_sync(
            url=url,
            bucket_name=bucket_name,
            key_prefix=key_prefix,
            temp_dir="/tmp",  # Lambda temp directory
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            wait_timeout=wait_timeout,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region_name,
            cleanup_local=True,  # Always cleanup in Lambda
        )
        
        logger.info(f"Screenshot completed successfully: {result['s3_url']}")
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({
                "success": True,
                "result": result,
            })
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing screenshot request: {error_msg}")
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "success": False,
                "error": error_msg,
                "type": type(e).__name__,
            })
        }


def batch_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for batch screenshot processing.
    
    Expected event structure:
    {
        "urls": ["https://example.com", "https://google.com"],
        "bucket": "my-bucket", 
        "prefix": "batch-screenshots/",
        "parallel": false
    }
    
    Returns summary of batch processing results.
    """
    try:
        logger.info(f"Processing batch screenshot request: {json.dumps(event, default=str)}")
        
        urls = event.get("urls", [])
        if not urls:
            raise ValueError("URLs list is required")
        
        bucket_name = event.get("bucket") or os.getenv("BUCKET_NAME")
        if not bucket_name:
            raise ValueError("Bucket name is required")
        
        key_prefix = event.get("prefix", os.getenv("KEY_PREFIX", ""))
        
        results = []
        errors = []
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"Processing URL {i}/{len(urls)}: {url}")
                
                # Create individual event for each URL
                individual_event = {
                    **event,
                    "url": url,
                    "prefix": f"{key_prefix}batch-{i:03d}-" if key_prefix else f"batch-{i:03d}-"
                }
                
                # Process individual screenshot
                response = lambda_handler(individual_event, context)
                
                if response["statusCode"] == 200:
                    response_data = json.loads(response["body"])
                    results.append(response_data["result"])
                else:
                    error_data = json.loads(response["body"])
                    errors.append({
                        "url": url,
                        "error": error_data.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                errors.append({
                    "url": url,
                    "error": str(e)
                })
        
        success_count = len(results)
        total_count = len(urls)
        
        logger.info(f"Batch processing completed: {success_count}/{total_count} successful")
        
        return {
            "statusCode": 200 if success_count > 0 else 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "success": success_count > 0,
                "summary": {
                    "total_urls": total_count,
                    "successful": success_count,
                    "failed": len(errors),
                },
                "results": results,
                "errors": errors,
            })
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing batch request: {error_msg}")
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "success": False,
                "error": error_msg,
                "type": type(e).__name__,
            })
        }


# For local testing
if __name__ == "__main__":
    import sys
    
    # Test event
    test_event = {
        "url": "https://example.com",
        "bucket": "test-bucket",
        "prefix": "test/",
    }
    
    class MockContext:
        def __init__(self):
            self.function_name = "test-function"
            self.function_version = "1"
            self.aws_request_id = "test-request-id"
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))