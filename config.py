"""
Configuration module for the Nagios Passive Receiver.
Loads settings from environment variables and API keys from JSON file.
"""

import json
import logging
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class APIKeyConfig:
    """Manages API key configuration from JSON file."""

    def __init__(self, config_path: str):
        """Initialize API key config from JSON file."""
        self.config_path = Path(config_path)
        self._api_keys: Dict[str, str] = {}
        self.load_api_keys()

    def load_api_keys(self) -> None:
        """Load API keys from JSON file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"API keys file not found: {self.config_path}")
                return

            with open(self.config_path, "r") as f:
                data = json.load(f)

            self._api_keys = {}
            for entry in data.get("api_keys", []):
                if entry.get("enabled", True):
                    key = entry.get("key")
                    name = entry.get("name")
                    if key and name:
                        self._api_keys[key] = name

            logger.info(
                f"Loaded {len(self._api_keys)} API key(s) from {self.config_path}"
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in API keys file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            raise

    def get_api_keys_dict(self) -> Dict[str, str]:
        """Get dictionary of valid API keys."""
        return self._api_keys

    def reload(self) -> None:
        """Reload API keys from file."""
        logger.info("Reloading API keys...")
        self.load_api_keys()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    nagios_cmd_path: str = "/var/nagios/rw/nagios.cmd"
    api_keys_file: str = "api_keys.json"
    host: str = "0.0.0.0"
    port: int = 8000
    tls_cert_file: Optional[str] = None
    tls_key_file: Optional[str] = None


# Global settings instance
settings = Settings()

# Global API keys configuration
api_key_config = APIKeyConfig(settings.api_keys_file)
