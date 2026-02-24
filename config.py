"""
Configuration module for the Nagios Passive Receiver.
Loads settings from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Dict, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    nagios_cmd_path: str = "/var/nagios/rw/nagios.cmd"
    api_keys: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    tls_cert_file: Optional[str] = None
    tls_key_file: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_api_keys_dict(self) -> Dict[str, str]:
        """
        Parse API_KEYS environment variable into a dictionary.
        Format: apikey1:plugin1,apikey2:plugin2
        Returns: {apikey1: plugin1, apikey2: plugin2}
        """
        if not self.api_keys:
            return {}

        api_keys_dict = {}
        for pair in self.api_keys.split(","):
            pair = pair.strip()
            if ":" in pair:
                key, name = pair.split(":", 1)
                api_keys_dict[key.strip()] = name.strip()

        return api_keys_dict


# Global settings instance
settings = Settings()
