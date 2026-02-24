"""
Nagios command writer module.
Handles writing passive check results to nagios.cmd file.
"""

import os
import time
import logging
from pathlib import Path
from models import PassiveCheckRequest

logger = logging.getLogger(__name__)


class NagiosCommandWriter:
    """Handles writing passive check results to Nagios command file."""

    def __init__(self, cmd_path: str):
        """
        Initialize the Nagios command writer.

        Args:
            cmd_path: Path to the nagios.cmd file
        """
        self.cmd_path = Path(cmd_path)
        logger.info(f"Initialized NagiosCommandWriter with path: {self.cmd_path}")

    def is_writable(self) -> bool:
        """
        Check if the nagios.cmd file is writable.

        Returns:
            True if the file exists and is writable, False otherwise
        """
        try:
            # Check if parent directory exists
            if not self.cmd_path.parent.exists():
                logger.warning(
                    f"Parent directory does not exist: {self.cmd_path.parent}"
                )
                return False

            # Check if file exists and is writable, or if we can create it
            if self.cmd_path.exists():
                return os.access(self.cmd_path, os.W_OK)
            else:
                # Check if we can write to the parent directory
                return os.access(self.cmd_path.parent, os.W_OK)
        except Exception as e:
            logger.error(f"Error checking writability: {e}")
            return False

    def write_passive_check(self, check: PassiveCheckRequest) -> bool:
        """
        Write a passive check result to the nagios.cmd file.

        The format for passive service checks in Nagios is:
        [<timestamp>] PROCESS_SERVICE_CHECK_RESULT;<host_name>;<service_description>;<return_code>;<plugin_output>

        Args:
            check: PassiveCheckRequest object containing check data

        Returns:
            True if write was successful, False otherwise
        """
        try:
            # Get current timestamp
            timestamp = int(time.time())

            # Format the command according to Nagios external command format
            command = (
                f"[{timestamp}] PROCESS_SERVICE_CHECK_RESULT;"
                f"{check.host_name};"
                f"{check.service_description};"
                f"{check.return_code};"
                f"{check.plugin_output}\n"
            )

            logger.info(f"Writing command to {self.cmd_path}: {command.strip()}")

            # Write to the nagios.cmd file
            # Using append mode and ensuring atomic write
            with open(self.cmd_path, "a") as f:
                f.write(command)
                f.flush()
                os.fsync(f.fileno())

            logger.info("Successfully wrote passive check result")
            return True

        except Exception as e:
            logger.error(f"Error writing to nagios.cmd: {e}", exc_info=True)
            return False
