#!/bin/bash

# Test script for Azure Function MCP endpoints
# Usage: ./test_endpoints.sh <function-app-url> <function-key>

if [ $# -lt 2 ]; then
    echo "Usage: $0 <function-app-url> <function-key>"
    echo "Example: $0 https://pichat-dev-func.azurewebsites.net abcd1234=="
    exit 1
fi

FUNCTION_URL=$1
FUNCTION_KEY=$2

echo "Testing MCP Endpoints..."
echo "========================"
echo ""

# Test GetTelemetry endpoint
echo "1. Testing GetTelemetry endpoint..."
TELEMETRY_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "${FUNCTION_URL}/api/GetTelemetry?code=${FUNCTION_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "SensorKey": "sensor-001",
    "StartDate": "2025-01-01T00:00:00Z",
    "EndDate": "2025-01-02T00:00:00Z"
  }')

HTTP_CODE=$(echo "$TELEMETRY_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$TELEMETRY_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
    echo "✓ GetTelemetry test PASSED"
    echo "  Response: $RESPONSE_BODY"
else
    echo "✗ GetTelemetry test FAILED (HTTP $HTTP_CODE)"
    echo "  Response: $RESPONSE_BODY"
fi

echo ""

# Test SendAction endpoint
echo "2. Testing SendAction endpoint..."
ACTION_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "${FUNCTION_URL}/api/SendAction?code=${FUNCTION_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "ActionType": "turn_on",
    "ActionSpec": "{\"device\": \"led\", \"pin\": 17}"
  }')

HTTP_CODE=$(echo "$ACTION_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$ACTION_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
    echo "✓ SendAction test PASSED"
    echo "  Response: $RESPONSE_BODY"
else
    echo "✗ SendAction test FAILED (HTTP $HTTP_CODE)"
    echo "  Response: $RESPONSE_BODY"
fi

echo ""
echo "Testing complete!"
