#!/usr/bin/env python3
"""
Test script for user settings API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_settings_api():
    print("Testing User Settings API...")
    
    # Test 1: Get settings (requires authentication)
    print("\n1. Testing GET /api/v1/user-settings/me")
    try:
        # This will fail without proper auth, but we can test the endpoint exists
        response = requests.get(f"{BASE_URL}/api/v1/user-settings/me")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Endpoint exists (authentication required)")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Check if API is running
    print("\n2. Testing API health")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ API not running: {e}")
    
    # Test 3: Check API docs
    print("\n3. Testing API documentation")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ API documentation available")
        else:
            print("❌ API documentation not available")
    except Exception as e:
        print(f"❌ Error accessing docs: {e}")

if __name__ == "__main__":
    test_settings_api()
