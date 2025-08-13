#!/usr/bin/env python3
"""
Simple test to check API response structure
"""

import requests
import json

def test_api_structure():
    """Test the API structure without authentication"""
    
    try:
        # Test if the server is responding
        response = requests.get("http://localhost:8000/docs")
        print(f"✅ Server is running: {response.status_code}")
        
        # Test the comprehensive dashboard endpoint (will fail due to auth, but we can see the structure)
        response = requests.get("http://localhost:8000/api/v1/socket-logs/comprehensive-dashboard")
        print(f"📊 Comprehensive dashboard response: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ API endpoint exists (requires authentication)")
        else:
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_structure() 