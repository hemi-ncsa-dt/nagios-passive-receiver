"""
Data models for the Nagios Passive Receiver API.
"""

from pydantic import BaseModel, Field, validator
from typing import Literal
from datetime import datetime


class PassiveCheckRequest(BaseModel):
    """Model for passive check submission request."""

    host_name: str = Field(..., description="Name of the host in Nagios")
    service_description: str = Field(
        ..., description="Description of the service in Nagios"
    )
    return_code: int = Field(
        ...,
        ge=0,
        le=3,
        description="Service state: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN",
    )
    plugin_output: str = Field(
        ..., description="Output text from the monitoring plugin"
    )

    @validator("host_name", "service_description")
    def validate_no_special_chars(cls, v):
        """Ensure no special characters that could break nagios.cmd format."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")

        # Disallow characters that could cause issues in nagios.cmd
        forbidden_chars = ["\n", "\r", "\t", ";", "|"]
        for char in forbidden_chars:
            if char in v:
                raise ValueError(f"Field contains forbidden character: {repr(char)}")

        return v.strip()

    @validator("plugin_output")
    def validate_output(cls, v):
        """Ensure plugin output doesn't contain newlines."""
        if "\n" in v or "\r" in v:
            raise ValueError("Plugin output cannot contain newlines")
        return v


class HostCheckRequest(BaseModel):
    """Model for host check submission request."""

    host_name: str = Field(..., description="Name of the host in Nagios")
    host_status: int = Field(
        ...,
        ge=0,
        le=2,
        description="Host state: 0=UP, 1=DOWN, 2=UNREACHABLE",
    )
    plugin_output: str = Field(..., description="Output text from the host check")

    @validator("host_name")
    def validate_no_special_chars(cls, v):
        """Ensure no special characters that could break nagios.cmd format."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")

        # Disallow characters that could cause issues in nagios.cmd
        forbidden_chars = ["\n", "\r", "\t", ";", "|"]
        for char in forbidden_chars:
            if char in v:
                raise ValueError(f"Field contains forbidden character: {repr(char)}")

        return v.strip()

    @validator("plugin_output")
    def validate_output(cls, v):
        """Ensure plugin output doesn't contain newlines."""
        if "\n" in v or "\r" in v:
            raise ValueError("Plugin output cannot contain newlines")
        return v


class PassiveCheckResponse(BaseModel):
    """Response model for passive check submission."""

    status: Literal["success", "error"] = Field(
        ..., description="Status of the submission"
    )
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Health status")
    nagios_cmd_writable: bool = Field(..., description="Whether nagios.cmd is writable")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    nagios_cmd_path: str = Field(..., description="Path to nagios.cmd file")
