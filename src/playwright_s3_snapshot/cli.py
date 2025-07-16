"""Command-line interface for Playwright S3 Snapshot."""

import argparse
import os
import sys
from pathlib import Path

from .screenshot import take_screenshot_sync
from .snapshot import take_snapshot_to_s3_sync


def main() -> int:
    """Enhanced CLI with S3 support."""
    parser = argparse.ArgumentParser(
        description="Take screenshots with Playwright and optionally upload to S3"
    )
    
    parser.add_argument("url", help="URL to screenshot")
    parser.add_argument("--bucket", help="S3 bucket name (enables S3 upload)")
    parser.add_argument("--prefix", default="", help="S3 key prefix (default: empty)")
    parser.add_argument("--output", help="Local output path (ignored if --bucket specified)")
    parser.add_argument("--width", type=int, default=1920, help="Viewport width (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height (default: 1080)")
    parser.add_argument("--timeout", type=int, default=30000, help="Page load timeout in ms (default: 30000)")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")
    
    args = parser.parse_args()
    
    try:
        if args.bucket:
            # S3 upload mode
            print(f"Taking screenshot of: {args.url}")
            print(f"Uploading to S3 bucket: {args.bucket}")
            
            result = take_snapshot_to_s3_sync(
                url=args.url,
                bucket_name=args.bucket,
                key_prefix=args.prefix,
                viewport_width=args.width,
                viewport_height=args.height,
                wait_timeout=args.timeout,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=args.region,
            )
            
            print(f"✅ Screenshot uploaded successfully!")
            print(f"S3 URL: {result['s3_url']}")
            print(f"File size: {result['file_size']:,} bytes")
            print(f"Timestamp: {result['timestamp']}")
            
        else:
            # Local file mode
            print(f"Taking screenshot of: {args.url}")
            output_path = take_screenshot_sync(
                url=args.url,
                output_path=args.output,
                viewport_width=args.width,
                viewport_height=args.height,
                wait_timeout=args.timeout,
            )
            
            print(f"Screenshot saved to: {output_path}")
            
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                print(f"✅ Screenshot file created successfully! ({file_size:,} bytes)")
            else:
                print("❌ Screenshot file not found!")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())