"""Tests for configuration functionality.

This module tests the configuration system including:
- JSON file loading and validation
- Configuration merging
- Error handling for malformed configs
"""

import json
from pathlib import Path
from typing import Dict, Any

import pytest

from playwright_s3_snapshot.config import load_config, merge_config


class TestConfigLoading:
    """Tests for configuration file loading."""

    def test_load_config_success(self, temp_dir: str) -> None:
        """Test successful configuration loading."""
        config_file = Path(temp_dir) / "config.json"
        config_data = {
            "bucket": "test-bucket",
            "prefix": "screenshots/",
            "width": 1920,
            "height": 1080,
            "timeout": 30000,
            "region": "us-east-1"
        }
        config_file.write_text(json.dumps(config_data))

        result = load_config(str(config_file))
        assert result == config_data

    def test_load_config_file_not_found(self) -> None:
        """Test handling of missing configuration file."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.json")

    def test_load_config_invalid_json(self, temp_dir: str) -> None:
        """Test handling of invalid JSON configuration."""
        config_file = Path(temp_dir) / "invalid.json"
        config_file.write_text("invalid json content")

        with pytest.raises(json.JSONDecodeError):
            load_config(str(config_file))

    def test_load_config_empty_file(self, temp_dir: str) -> None:
        """Test handling of empty configuration file."""
        config_file = Path(temp_dir) / "empty.json"
        config_file.write_text("{}")

        result = load_config(str(config_file))
        assert result == {}


class TestConfigMerging:
    """Tests for configuration merging."""

    def test_merge_config_basic(self) -> None:
        """Test basic configuration merging."""
        file_config = {"bucket": "file-bucket", "timeout": 5000}
        cli_config = {"bucket": "cli-bucket", "prefix": "cli/"}

        result = merge_config(file_config, cli_config)
        
        assert result["bucket"] == "cli-bucket"  # CLI overrides file
        assert result["timeout"] == 5000  # From file
        assert result["prefix"] == "cli/"  # From CLI

    def test_merge_config_empty_configs(self) -> None:
        """Test merging with empty configurations."""
        result = merge_config({}, {})
        assert result == {}

        result = merge_config({"bucket": "test"}, {})
        assert result == {"bucket": "test"}

        result = merge_config({}, {"bucket": "test"})
        assert result == {"bucket": "test"}