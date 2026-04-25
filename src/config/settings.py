"""
Centralized settings management for the test framework.
Loads configuration from YAML and environment variables.
"""
import os
import yaml
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Singleton settings manager for test framework configuration."""

    _instance: Optional['Settings'] = None
    _config: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from YAML file and environment variables."""
        config_paths = [
            Path("src/config/config.yaml"),
            Path("config/config.yaml"),
            Path("config.yaml"),
        ]

        for config_path in config_paths:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
                break

        # Override with environment variables
        self._config['environment']['base_url'] = os.getenv(
            'BASE_URL',
            self._config.get('environment', {}).get('base_url', 'http://localhost:8000')
        )

    def get(self, *keys: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation keys."""
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def environment(self) -> dict:
        return self._config.get('environment', {})

    @property
    def logging(self) -> dict:
        return self._config.get('logging', {})

    @property
    def reporting(self) -> dict:
        return self._config.get('reporting', {})

    @property
    def execution(self) -> dict:
        return self._config.get('execution', {})

    @property
    def categories(self) -> dict:
        return self._config.get('categories', {})


# Global settings instance
settings = Settings()