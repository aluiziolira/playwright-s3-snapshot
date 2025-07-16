"""Configuration file support for Playwright S3 Snapshot."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager supporting multiple formats."""
    
    def __init__(self):
        self.data = {}
        self._load_from_files()
        self._load_from_env()
    
    def _load_from_files(self):
        """Load configuration from files in order of preference."""
        config_files = [
            "playwright-s3-snapshot.json",
            ".playwright-s3-snapshot.json",
            os.path.expanduser("~/.playwright-s3-snapshot.json"),
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                        self.data.update(file_config)
                        break
                except (json.JSONDecodeError, IOError):
                    continue
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mapping = {
            'PS3S_BUCKET': 'bucket',
            'PS3S_PREFIX': 'prefix',
            'PS3S_REGION': 'region',
            'PS3S_WIDTH': 'width',
            'PS3S_HEIGHT': 'height',
            'PS3S_TIMEOUT': 'timeout',
            'PS3S_RETRIES': 'retries',
            'PS3S_VERBOSE': 'verbose',
            'PS3S_QUIET': 'quiet',
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_key in ['width', 'height', 'timeout', 'retries']:
                    try:
                        self.data[config_key] = int(value)
                    except ValueError:
                        continue
                elif config_key in ['verbose', 'quiet']:
                    self.data[config_key] = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    self.data[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.data.get(key, default)
    
    def set_defaults(self, parser_defaults: Dict[str, Any]):
        """Set argparse defaults from configuration."""
        for key, value in self.data.items():
            if key in parser_defaults:
                parser_defaults[key] = value


def load_config() -> Config:
    """Load configuration from files and environment."""
    return Config()


def create_sample_config_file(path: str = "playwright-s3-snapshot.json"):
    """Create a sample configuration file."""
    sample_config = {
        "bucket": "my-screenshots-bucket", 
        "prefix": "qa-screenshots",
        "region": "us-east-1",
        "width": 1920,
        "height": 1080,
        "timeout": 30000,
        "retries": 3,
        "verbose": False
    }
    
    with open(path, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    return path