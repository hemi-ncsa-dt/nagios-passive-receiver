"""
Main FastAPI application for Nagios Passive Receiver.
"""

from fastapi import FastAPI, HTTPException, Security, Depends, status
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from config import settings, api_key_config
from models import (
    PassiveCheckRequest,
    PassiveCheckResponse,
    HealthResponse,
    HostCheckRequest,
)
from nagios_writer import NagiosCommandWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nagios Passive Receiver",
    description="HTTP API for receiving passive check results for Nagios",
    version="1.0.0",
)

# Initialize Nagios command writer
nagios_writer = NagiosCommandWriter(settings.nagios_cmd_path)

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from the request header.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        Plugin name associated with the API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        logger.warning("Request without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key"
        )

    # Get valid API keys
    valid_keys = api_key_config.get_api_keys_dict()

    if not valid_keys:
        logger.error("No API keys configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
        )

    # Verify the key
    if api_key not in valid_keys:
        logger.warning(f"Invalid API key attempted: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    plugin_name = valid_keys[api_key]
    logger.info(f"Authenticated request from: {plugin_name}")
    return plugin_name


@app.get("/", response_model=dict)
async def root():
    """Root endpoint providing API information."""
    return {
        "service": "Nagios Passive Receiver",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "submit_check": "/api/v1/passive-check (POST)",
            "submit_host_check": "/api/v1/host-check (POST)",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running
    and can write to nagios.cmd.
    """
    is_writable = nagios_writer.is_writable()

    return HealthResponse(
        status="healthy" if is_writable else "degraded",
        nagios_cmd_writable=is_writable,
        timestamp=datetime.utcnow(),
        nagios_cmd_path=settings.nagios_cmd_path,
    )


@app.post("/api/v1/passive-check", response_model=PassiveCheckResponse)
async def submit_passive_check(
    check: PassiveCheckRequest, plugin_name: str = Depends(verify_api_key)
):
    """
    Submit a passive check result to Nagios.

    Args:
        check: Passive check data including host, service, return code, and output
        plugin_name: Authenticated plugin name (injected by dependency)

    Returns:
        PassiveCheckResponse indicating success or failure
    """
    logger.info(
        f"Received passive check from {plugin_name}: "
        f"host={check.host_name}, service={check.service_description}, "
        f"code={check.return_code}"
    )

    # Check if nagios.cmd is writable
    if not nagios_writer.is_writable():
        logger.error("Cannot write to nagios.cmd file")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot write to Nagios command file",
        )

    # Write the passive check
    success = nagios_writer.write_passive_check(check)

    if success:
        return PassiveCheckResponse(
            status="success",
            message=f"Passive check result submitted for {check.host_name}/{check.service_description}",
            timestamp=datetime.utcnow(),
        )
    else:
        logger.error("Failed to write passive check")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to write passive check result",
        )


@app.post("/api/v1/host-check", response_model=PassiveCheckResponse)
async def submit_host_check(
    check: HostCheckRequest, plugin_name: str = Depends(verify_api_key)
):
    """
    Submit a host check result to Nagios.

    Args:
        check: Host check data including host name, host status, and output
        plugin_name: Authenticated plugin name (injected by dependency)

    Returns:
        PassiveCheckResponse indicating success or failure
    """
    logger.info(
        f"Received host check from {plugin_name}: "
        f"host={check.host_name}, status={check.host_status}"
    )

    # Check if nagios.cmd is writable
    if not nagios_writer.is_writable():
        logger.error("Cannot write to nagios.cmd file")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot write to Nagios command file",
        )

    # Write the host check
    success = nagios_writer.write_host_check(check)

    if success:
        return PassiveCheckResponse(
            status="success",
            message=f"Host check result submitted for {check.host_name}",
            timestamp=datetime.utcnow(),
        )
    else:
        logger.error("Failed to write host check")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to write host check result",
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    # Determine if using TLS
    use_tls = settings.tls_cert_file and settings.tls_key_file

    if use_tls:
        logger.info(f"Starting server with TLS on {settings.host}:{settings.port}")
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            ssl_certfile=settings.tls_cert_file,
            ssl_keyfile=settings.tls_key_file,
            log_level="info",
        )
    else:
        logger.info(f"Starting server without TLS on {settings.host}:{settings.port}")
        logger.warning("TLS is not configured. Consider enabling TLS in production.")
        uvicorn.run(
            "main:app", host=settings.host, port=settings.port, log_level="info"
        )
