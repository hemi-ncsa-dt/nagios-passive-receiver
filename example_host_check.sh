#!/bin/bash
# Example bash script to send host checks using curl

API_URL="http://localhost:8000/api/v1/host-check"
API_KEY="your-secret-key-1"

# Function to send a host check
send_host_check() {
    local host=$1
    local status=$2
    local output=$3
    
    curl -X POST "$API_URL" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"host_name\": \"$host\",
            \"host_status\": $status,
            \"plugin_output\": \"$output\"
        }"
    
    echo ""
}

# Example usage
echo "Sending UP status..."
send_host_check "webserver01" 0 "PING OK - Packet loss = 0%, RTA = 1.23 ms"

echo "Sending DOWN status..."
send_host_check "dbserver01" 1 "PING CRITICAL - Host unreachable"

echo "Sending UNREACHABLE status..."
send_host_check "appserver01" 2 "PING UNREACHABLE - No route to host"
