#!/usr/bin/env python3
"""
Example script demonstrating how to send a passive check to the Nagios receiver.
"""

import requests
import json
import sys

# Configuration
API_URL = "http://localhost:8000/api/v1/passive-check"
API_KEY = "your-secret-key-1"  # Replace with your actual API key


def send_passive_check(host_name, service_description, return_code, plugin_output):
    """
    Send a passive check result to the Nagios receiver.

    Args:
        host_name: Name of the host in Nagios
        service_description: Description of the service
        return_code: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN
        plugin_output: Output message from the check
    """
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    payload = {
        "host_name": host_name,
        "service_description": service_description,
        "return_code": return_code,
        "plugin_output": plugin_output,
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        print(f"✓ Success: {result['message']}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Example 1: OK status
    print("Example 1: Sending OK status...")
    send_passive_check(
        host_name="webserver01",
        service_description="HTTP Check",
        return_code=0,
        plugin_output="HTTP OK - Response time: 0.234s",
    )

    print("\nExample 2: Sending WARNING status...")
    send_passive_check(
        host_name="dbserver01",
        service_description="Disk Usage",
        return_code=1,
        plugin_output="WARNING - Disk usage at 85%",
    )

    print("\nExample 3: Sending CRITICAL status...")
    send_passive_check(
        host_name="appserver01",
        service_description="Memory Usage",
        return_code=2,
        plugin_output="CRITICAL - Memory usage at 95%",
    )

    print("\nExample 4: Sending UNKNOWN status...")
    send_passive_check(
        host_name="testserver01",
        service_description="Custom Check",
        return_code=3,
        plugin_output="UNKNOWN - Unable to determine status",
    )
