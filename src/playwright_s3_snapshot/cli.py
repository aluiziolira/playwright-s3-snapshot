"""Command-line interface for Playwright S3 Snapshot."""

import argparse
import os
import sys
import re
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from .screenshot import take_screenshot_sync
from .snapshot import take_snapshot_to_s3_sync
from .config import load_config, create_sample_config_file


def validate_url(url: str) -> str:
    """Validate and normalize URL."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    if not parsed.netloc:
        raise argparse.ArgumentTypeError(f"Invalid URL: {url}")
    
    return url


def validate_s3_bucket_name(bucket: str) -> str:
    """Validate S3 bucket name according to AWS rules."""
    if len(bucket) < 3 or len(bucket) > 63:
        raise argparse.ArgumentTypeError("S3 bucket name must be between 3 and 63 characters")
    
    if not re.match(r'^[a-z0-9][a-z0-9\-]*[a-z0-9]$', bucket):
        raise argparse.ArgumentTypeError(
            "S3 bucket name must start/end with lowercase letter or number, "
            "contain only lowercase letters, numbers, and hyphens"
        )
    
    if '..' in bucket or '.-' in bucket or '-.' in bucket:
        raise argparse.ArgumentTypeError("S3 bucket name cannot contain consecutive periods or period-hyphen combinations")
    
    return bucket


def validate_positive_int(value: str) -> int:
    """Validate positive integer."""
    try:
        int_value = int(value)
        if int_value <= 0:
            raise argparse.ArgumentTypeError(f"Value must be positive, got: {int_value}")
        return int_value
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer: {value}")


def parse_urls_from_file(file_path: str) -> List[str]:
    """Parse URLs from a file (one per line)."""
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return [validate_url(url) for url in urls]
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f"URL file not found: {file_path}")
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Error reading URL file: {e}")


def main() -> int:
    """Enhanced CLI with comprehensive validation and features."""
    # Load configuration first
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description="Take screenshots with Playwright and optionally upload to S3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --output screenshot.png
  %(prog)s https://example.com --bucket my-bucket --prefix qa/
  %(prog)s --url-file urls.txt --bucket my-bucket
  %(prog)s https://example.com --width 1280 --height 720 --timeout 60000
  %(prog)s --create-config  # Create sample config file

Configuration:
  Settings can be loaded from:
  - playwright-s3-snapshot.json (current directory)
  - .playwright-s3-snapshot.json (current directory)  
  - ~/.playwright-s3-snapshot.json (home directory)
  - Environment variables (PS3S_BUCKET, PS3S_PREFIX, etc.)
        """
    )
    
    # Special commands
    parser.add_argument("--create-config", action="store_true",
                       help="Create sample configuration file and exit")
    
    # URL input (mutually exclusive)
    url_group = parser.add_mutually_exclusive_group(required=False)
    url_group.add_argument("url", nargs="?", type=validate_url, help="URL to screenshot")
    url_group.add_argument("--url-file", type=parse_urls_from_file, metavar="FILE", 
                          help="File containing URLs (one per line)")
    
    # S3 configuration
    s3_group = parser.add_argument_group("S3 options")
    s3_group.add_argument("--bucket", type=validate_s3_bucket_name, 
                         default=config.get("bucket"),
                         help="S3 bucket name (enables S3 upload)")
    s3_group.add_argument("--prefix", 
                         default=config.get("prefix", ""),
                         help="S3 key prefix (default: empty)")
    s3_group.add_argument("--region", 
                         default=config.get("region", "us-east-1"),
                         help="AWS region (default: us-east-1)")
    
    # Output configuration
    output_group = parser.add_argument_group("Output options")
    output_group.add_argument("--output", metavar="PATH",
                             help="Local output path (ignored if --bucket specified)")
    output_group.add_argument("--verbose", "-v", action="store_true",
                             default=config.get("verbose", False),
                             help="Enable verbose output")
    output_group.add_argument("--quiet", "-q", action="store_true",
                             default=config.get("quiet", False),
                             help="Suppress non-error output")
    
    # Browser configuration
    browser_group = parser.add_argument_group("Browser options")
    browser_group.add_argument("--width", type=validate_positive_int, 
                              default=config.get("width", 1920),
                              help="Viewport width in pixels (default: 1920)")
    browser_group.add_argument("--height", type=validate_positive_int, 
                              default=config.get("height", 1080),
                              help="Viewport height in pixels (default: 1080)")
    browser_group.add_argument("--timeout", type=validate_positive_int, 
                              default=config.get("timeout", 30000),
                              help="Page load timeout in milliseconds (default: 30000)")
    
    # Advanced options
    advanced_group = parser.add_argument_group("Advanced options")
    advanced_group.add_argument("--retries", type=validate_positive_int, 
                               default=config.get("retries", 1),
                               help="Number of retry attempts on failure (default: 1)")
    advanced_group.add_argument("--parallel", type=validate_positive_int, 
                               default=config.get("parallel", 1),
                               help="Number of parallel processes for batch jobs (default: 1)")
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.create_config:
        try:
            config_path = create_sample_config_file()
            print(f"✅ Sample configuration file created: {config_path}")
            print("Edit this file to set your default values.")
            return 0
        except Exception as e:
            print(f"❌ Error creating config file: {e}", file=sys.stderr)
            return 1
    
    # Validate that we have a URL if not creating config
    if not args.url and not args.url_file:
        parser.error("URL is required (or use --create-config)")
    
    # Validate argument combinations
    if args.quiet and args.verbose:
        parser.error("--quiet and --verbose are mutually exclusive")
    
    # Set up output level
    def log_info(msg: str):
        if not args.quiet:
            print(msg)
    
    def log_verbose(msg: str):
        if args.verbose:
            print(f"[VERBOSE] {msg}")
    
    def log_error(msg: str):
        print(f"❌ Error: {msg}", file=sys.stderr)
    
    try:
        # Get URLs to process
        urls = []
        if args.url:
            urls = [args.url]
        elif args.url_file:
            urls = args.url_file
            log_verbose(f"Loaded {len(urls)} URLs from file")
        
        if not urls:
            parser.error("No URLs specified")
        
        success_count = 0
        total_urls = len(urls)
        
        for i, url in enumerate(urls, 1):
            if total_urls > 1:
                log_info(f"\n[{i}/{total_urls}] Processing: {url}")
            
            retry_count = 0
            success = False
            
            while retry_count < args.retries and not success:
                try:
                    if args.bucket:
                        # S3 upload mode
                        if retry_count == 0:
                            log_info(f"Taking screenshot of: {url}")
                            log_verbose(f"Uploading to S3 bucket: {args.bucket}")
                        else:
                            log_info(f"Retry {retry_count}/{args.retries - 1}: {url}")
                        
                        result = take_snapshot_to_s3_sync(
                            url=url,
                            bucket_name=args.bucket,
                            key_prefix=args.prefix,
                            viewport_width=args.width,
                            viewport_height=args.height,
                            wait_timeout=args.timeout,
                            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                            region_name=args.region,
                        )
                        
                        log_info(f"✅ Screenshot uploaded successfully!")
                        if args.verbose or total_urls == 1:
                            log_info(f"S3 URL: {result['s3_url']}")
                            log_info(f"File size: {result['file_size']:,} bytes")
                            log_verbose(f"Timestamp: {result['timestamp']}")
                        
                    else:
                        # Local file mode
                        if retry_count == 0:
                            log_info(f"Taking screenshot of: {url}")
                        else:
                            log_info(f"Retry {retry_count}/{args.retries - 1}: {url}")
                        
                        # Generate output path for batch processing
                        output_path = args.output
                        if total_urls > 1 and not output_path:
                            from datetime import datetime
                            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                            output_path = f"screenshot_{i}_{timestamp}.png"
                        
                        result_path = take_screenshot_sync(
                            url=url,
                            output_path=output_path,
                            viewport_width=args.width,
                            viewport_height=args.height,
                            wait_timeout=args.timeout,
                        )
                        
                        log_info(f"Screenshot saved to: {result_path}")
                        
                        if Path(result_path).exists():
                            file_size = Path(result_path).stat().st_size
                            log_verbose(f"File size: {file_size:,} bytes")
                            log_info(f"✅ Screenshot file created successfully!")
                        else:
                            raise Exception("Screenshot file not found after creation")
                    
                    success = True
                    success_count += 1
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count < args.retries:
                        log_verbose(f"Attempt {retry_count} failed: {e}")
                        log_info(f"Retrying in 2 seconds...")
                        import time
                        time.sleep(2)
                    else:
                        log_error(f"Failed after {args.retries} attempts: {e}")
        
        # Summary for batch jobs
        if total_urls > 1:
            log_info(f"\n📊 Summary: {success_count}/{total_urls} screenshots completed successfully")
            if success_count < total_urls:
                return 1
        
        return 0 if success_count > 0 else 1
        
    except KeyboardInterrupt:
        log_error("Operation interrupted by user")
        return 130
    except Exception as e:
        log_error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())