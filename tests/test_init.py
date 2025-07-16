"""Tests for package initialization functionality.

This module tests the package initialization and import functionality:
- Package and module import validation
- Function availability verification
- Package structure validation
- Import error handling
"""

from typing import Any, Callable, Dict, List, Optional

import pytest


class TestPackageInit:
    """Tests for package initialization and imports."""

    def test_package_imports(self) -> None:
        """Test that all main modules can be imported.
        
        Verifies that the main package and all its submodules
        can be imported without errors and are properly initialized.
        """
        # Test importing the main package
        import playwright_s3_snapshot

        assert playwright_s3_snapshot is not None

        # Test importing individual modules
        from playwright_s3_snapshot import screenshot
        from playwright_s3_snapshot import s3_upload
        from playwright_s3_snapshot import snapshot
        from playwright_s3_snapshot import lambda_handler
        from playwright_s3_snapshot import cli
        from playwright_s3_snapshot import config

        # Verify modules are not None
        assert screenshot is not None
        assert s3_upload is not None
        assert snapshot is not None
        assert lambda_handler is not None
        assert cli is not None
        assert config is not None

    def test_main_functions_exist(self) -> None:
        """Test that main functions are available.
        
        Verifies that all expected public functions are accessible
        from their respective modules and are callable objects.
        """
        from playwright_s3_snapshot.screenshot import (
            take_screenshot,
            take_screenshot_sync,
        )
        from playwright_s3_snapshot.s3_upload import upload_to_s3, S3Uploader
        from playwright_s3_snapshot.snapshot import (
            take_snapshot_to_s3,
            take_snapshot_to_s3_sync,
        )
        from playwright_s3_snapshot.lambda_handler import lambda_handler, batch_handler
        from playwright_s3_snapshot.cli import main
        from playwright_s3_snapshot.config import load_config, merge_config

        # Verify functions are callable
        assert callable(take_screenshot)
        assert callable(take_screenshot_sync)
        assert callable(upload_to_s3)
        assert callable(S3Uploader)
        assert callable(take_snapshot_to_s3)
        assert callable(take_snapshot_to_s3_sync)
        assert callable(lambda_handler)
        assert callable(batch_handler)
        assert callable(main)
        assert callable(load_config)
        assert callable(merge_config)

    def test_no_import_errors(self) -> None:
        """Test that there are no import errors in any module.
        
        Verifies that all modules can be imported without
        raising ImportError or other import-related exceptions.
        """
        try:
            import playwright_s3_snapshot.screenshot
            import playwright_s3_snapshot.s3_upload
            import playwright_s3_snapshot.snapshot
            import playwright_s3_snapshot.lambda_handler
            import playwright_s3_snapshot.cli
            import playwright_s3_snapshot.config
        except ImportError as e:
            pytest.fail(f"Import error: {e}")

    def test_package_structure(self) -> None:
        """Test package structure and attributes.
        
        Verifies that the package has the expected structure
        with proper __name__, __file__, and __path__ attributes.
        """
        import playwright_s3_snapshot

        # Test that __name__ is set correctly
        assert playwright_s3_snapshot.__name__ == "playwright_s3_snapshot"

        # Test that the package has expected attributes
        assert hasattr(playwright_s3_snapshot, "__file__")
        assert hasattr(playwright_s3_snapshot, "__path__")
