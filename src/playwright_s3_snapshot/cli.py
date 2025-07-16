"""Command-line interface for Playwright S3 Snapshot."""

import sys
from pathlib import Path

from .screenshot import take_screenshot_sync


def main() -> int:
    """Simple CLI entry point for Phase 1 testing."""
    if len(sys.argv) < 2:
        print("Usage: python -m playwright_s3_snapshot.cli <url>")
        return 1
    
    url = sys.argv[1]
    
    try:
        print(f"Taking screenshot of: {url}")
        output_path = take_screenshot_sync(url)
        print(f"Screenshot saved to: {output_path}")
        
        if Path(output_path).exists():
            print("✅ Screenshot file created successfully!")
            return 0
        else:
            print("❌ Screenshot file not found!")
            return 1
            
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())