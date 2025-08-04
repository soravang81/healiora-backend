#!/usr/bin/env python3
"""
Test script for admin login functionality.
This script demonstrates how to use the admin login API.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_LOGIN_URL = f"{BASE_URL}/api/v1/admin/login"
ADMIN_ME_URL = f"{BASE_URL}/api/v1/admin/me"
ADMIN_VERIFY_URL = f"{BASE_URL}/api/v1/admin/verify"

def test_admin_login():
    """Test admin login functionality"""
    
    # Test case 1: Valid admin login
    print("=== Test Case 1: Valid Admin Login ===")
    admin_credentials = {
        "email": "admin@healiora.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(ADMIN_LOGIN_URL, json=admin_credentials)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Admin login successful! Token: {token[:50]}...")
            
            # Test accessing admin profile
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(ADMIN_ME_URL, headers=headers)
            print(f"\n=== Admin Profile ===")
            print(f"Status Code: {me_response.status_code}")
            print(f"Profile: {me_response.json()}")
            
            # Test admin verification
            verify_response = requests.get(ADMIN_VERIFY_URL, headers=headers)
            print(f"\n=== Admin Verification ===")
            print(f"Status Code: {verify_response.status_code}")
            print(f"Verification: {verify_response.json()}")
            
        else:
            print("❌ Admin login failed")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test case 2: Non-admin user trying to login
    print("=== Test Case 2: Non-Admin User Login ===")
    non_admin_credentials = {
        "email": "patient@healiora.com",
        "password": "patient123"
    }
    
    try:
        response = requests.post(ADMIN_LOGIN_URL, json=non_admin_credentials)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 403:
            print("✅ Correctly rejected non-admin user")
        else:
            print("❌ Should have rejected non-admin user")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test case 3: Invalid credentials
    print("=== Test Case 3: Invalid Credentials ===")
    invalid_credentials = {
        "email": "nonexistent@healiora.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(ADMIN_LOGIN_URL, json=invalid_credentials)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid credentials")
        else:
            print("❌ Should have rejected invalid credentials")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Admin Login System")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("="*50)
    
    test_admin_login()
    
    print("\n📋 API Endpoints Created:")
    print("POST /api/v1/admin/login - Admin login")
    print("GET  /api/v1/admin/me - Get admin profile")
    print("GET  /api/v1/admin/verify - Verify admin status")
    
    print("\n🔐 Security Features:")
    print("- Only users with role='admin' can login")
    print("- Password verification using bcrypt")
    print("- JWT token generation with role information")
    print("- Account status verification (is_active)")
    print("- Role-based access control for all admin endpoints") 