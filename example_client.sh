#!/bin/bash
# Example bash script to send passive checks using curl

API_URL="http://localhost:8000/api/v1/passive-check"
API_KEY="your-secret-key-1"

# Function to send a passive check
send_check() {
    local host=$1
    local service=$2
    local code=$3
    local output=$4
    
    curl -X POST "$API_URL" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"host_name\": \"$host\",
            \"service_description\": \"$service\",
            \"return_code\": $code,
            \"plugin_output\": \"$output\"
        }"
    
    echo ""
}

# Example usage
echo "Sending OK status..."
send_check "webserver01" "HTTP Check" 0 "HTTP OK - Response time: 0.234s"

echo "Sending WARNING status..."
send_check "dbserver01" "Disk Usage" 1 "WARNING - Disk usage at 85%"

echo "Sending CRITICAL status..."
send_check "appserver01" "Memory Usage" 2 "CRITICAL - Memory usage at 95%"
