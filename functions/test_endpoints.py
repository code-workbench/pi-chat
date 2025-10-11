#!/usr/bin/env python3
"""
Test script for Azure Function MCP endpoints
Usage: python test_endpoints.py <function-app-url> <function-key>
Example: python test_endpoints.py https://pichat-dev-func.azurewebsites.net abcd1234==
"""

import sys
import json
import requests
from datetime import datetime, timedelta


def test_get_telemetry(base_url: str, function_key: str) -> bool:
    """Test the GetTelemetry endpoint"""
    url = f"{base_url}/api/GetTelemetry?code={function_key}"
    
    # Create test payload
    payload = {
        "SensorKey": "sensor-001",
        "StartDate": (datetime.now() - timedelta(days=1)).isoformat() + "Z",
        "EndDate": datetime.now().isoformat() + "Z"
    }
    
    print("Testing GetTelemetry endpoint...")
    print(f"  URL: {url}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ GetTelemetry test PASSED")
            return True
        else:
            print("✗ GetTelemetry test FAILED")
            return False
    except Exception as e:
        print(f"✗ GetTelemetry test FAILED with exception: {str(e)}")
        return False


def test_send_action(base_url: str, function_key: str) -> bool:
    """Test the SendAction endpoint"""
    url = f"{base_url}/api/SendAction?code={function_key}"
    
    # Create test payload
    payload = {
        "ActionType": "turn_on",
        "ActionSpec": json.dumps({"device": "led", "pin": 17})
    }
    
    print("\nTesting SendAction endpoint...")
    print(f"  URL: {url}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ SendAction test PASSED")
            return True
        else:
            print("✗ SendAction test FAILED")
            return False
    except Exception as e:
        print(f"✗ SendAction test FAILED with exception: {str(e)}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python test_endpoints.py <function-app-url> <function-key>")
        print("Example: python test_endpoints.py https://pichat-dev-func.azurewebsites.net abcd1234==")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    function_key = sys.argv[2]
    
    print("Testing MCP Endpoints...")
    print("=" * 50)
    print()
    
    # Run tests
    test1_passed = test_get_telemetry(base_url, function_key)
    test2_passed = test_send_action(base_url, function_key)
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  GetTelemetry: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"  SendAction: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✓ All tests PASSED")
        sys.exit(0)
    else:
        print("\n✗ Some tests FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
