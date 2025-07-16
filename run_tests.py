#!/usr/bin/env python3
"""Test runner script for the playwright-s3-snapshot project."""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run the test suite with coverage analysis."""
    project_root = Path(__file__).parent

    print("🧪 Running Playwright S3 Snapshot Test Suite")
    print("=" * 50)

    # Change to project directory
    original_dir = Path.cwd()
    try:
        import os

        os.chdir(project_root)

        # Install test dependencies if needed
        print("📦 Installing test dependencies...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return 1

        # Run tests with coverage
        print("\n🏃 Running tests with coverage...")
        test_cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--cov=src/playwright_s3_snapshot",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=90",
            "-v",
            "tests/",
        ]

        result = subprocess.run(test_cmd)

        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("📊 Coverage report generated in htmlcov/")
            print("🌐 Open htmlcov/index.html to view detailed coverage")
        else:
            print("\n❌ Some tests failed or coverage is below 90%")

        return result.returncode

    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    sys.exit(run_tests())
