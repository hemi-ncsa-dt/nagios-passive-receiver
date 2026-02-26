#!/usr/bin/env python3
"""
Example script demonstrating how to send a host check to the Nagios receiver.
"""

import requests
import sys

# Configuration
API_URL = "http://localhost:8000/api/v1/passive-check"
API_KEY = "your-secret-key-1"  # Replace with your actual API key


def send_host_check(host_name, host_status, plugin_output):
    """
    Send a host check result to the Nagios receiver.

    Args:
        host_name: Name of the host in Nagios
        host_status: 0=UP, 1=DOWN, 2=UNREACHABLE
        plugin_output: Output message from the host check
    """
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    payload = {
        "host_name": host_name,
        "host_status": host_status,
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
    # Example 1: UP status
    print("Example 1: Sending UP status...")
    send_host_check(
        host_name="maxima",
        host_status=0,
        plugin_output="PING OK - Packet loss = 0%, RTA = 1.23 ms",
    )
    exit()

    print("\nExample 2: Sending DOWN status...")
    send_host_check(
        host_name="maxima",
        host_status=1,
        plugin_output="PING CRITICAL - Host unreachable",
    )

    #print("\nExample 3: Sending UNREACHABLE status...")
    #send_host_check(
    #    host_name="appserver01",
    #    host_status=2,
    #    plugin_output="PING UNREACHABLE - No route to host",
    #)
