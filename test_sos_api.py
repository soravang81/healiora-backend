#!/usr/bin/env python3
"""
Test script for SOS API endpoints.
This script demonstrates how to use the new SOS tracking API endpoints.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1/socket-logs"

# Test credentials (you'll need to create these users in your database)
ADMIN_TOKEN = None
HOSPITAL_TOKEN = None

def login_admin():
    """Login as admin user"""
    global ADMIN_TOKEN
    
    login_data = {
        "email": "admin@healiora.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/admin/login", json=login_data)
    
    if response.status_code == 200:
        ADMIN_TOKEN = response.json()["access_token"]
        print("✅ Admin login successful")
        return True
    else:
        print(f"❌ Admin login failed: {response.json()}")
        return False

def login_hospital():
    """Login as hospital user"""
    global HOSPITAL_TOKEN
    
    login_data = {
        "email": "hospital@healiora.com",
        "password": "hospital123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/users/login", json=login_data)
    
    if response.status_code == 200:
        HOSPITAL_TOKEN = response.json()["access_token"]
        print("✅ Hospital login successful")
        return True
    else:
        print(f"❌ Hospital login failed: {response.json()}")
        return False

def get_headers(token):
    """Get headers with authentication token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_sos_endpoints():
    """Test SOS API endpoints"""
    
    print("🚀 Testing SOS API Endpoints")
    print("="*50)
    
    # Login as admin and hospital
    if not login_admin():
        print("Skipping admin tests - admin login failed")
        return
    
    if not login_hospital():
        print("Skipping hospital tests - hospital login failed")
        return
    
    # Test 1: Get SOS Statistics (Admin only)
    print("\n=== Test 1: Get SOS Statistics (Admin) ===")
    try:
        response = requests.get(
            f"{API_BASE}/sos/statistics",
            headers=get_headers(ADMIN_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ SOS Statistics: {stats}")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get Pending SOS Requests (Admin only)
    print("\n=== Test 2: Get Pending SOS Requests (Admin) ===")
    try:
        response = requests.get(
            f"{API_BASE}/sos/pending",
            headers=get_headers(ADMIN_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            pending = response.json()
            print(f"✅ Pending SOS Requests: {len(pending)} found")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get SOS Requests by Status (Admin only)
    print("\n=== Test 3: Get SOS Requests by Status (Admin) ===")
    try:
        response = requests.get(
            f"{API_BASE}/sos/by-status/accepted",
            headers=get_headers(ADMIN_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            accepted = response.json()
            print(f"✅ Accepted SOS Requests: {len(accepted)} found")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Get Hospital-specific SOS Requests (Hospital user)
    print("\n=== Test 4: Get My Hospital SOS Requests (Hospital) ===")
    try:
        response = requests.get(
            f"{API_BASE}/sos/my-hospital",
            headers=get_headers(HOSPITAL_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            hospital_sos = response.json()
            print(f"✅ Hospital SOS Requests: {len(hospital_sos)} found")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Get SOS Dashboard Data (Admin)
    print("\n=== Test 5: Get SOS Dashboard Data (Admin) ===")
    try:
        response = requests.get(
            f"{API_BASE}/sos/dashboard",
            headers=get_headers(ADMIN_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            dashboard = response.json()
            print(f"✅ Dashboard Data: {dashboard}")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Get SOS Dashboard Data (Hospital)
    print("\n=== Test 6: Get SOS Dashboard Data (Hospital) ===")
    try:
        response = requests.get(
            f"{API_BASE}/sos/dashboard",
            headers=get_headers(HOSPITAL_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            dashboard = response.json()
            print(f"✅ Hospital Dashboard Data: {dashboard}")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_sos_accept_reject():
    """Test SOS accept/reject functionality"""
    
    print("\n🔄 Testing SOS Accept/Reject Functionality")
    print("="*50)
    
    if not HOSPITAL_TOKEN:
        print("❌ Hospital token not available - skipping accept/reject tests")
        return
    
    # Note: These tests require existing SOS requests in the database
    # You would need to create some test SOS requests first
    
    # Test Accept SOS Request
    print("\n=== Test Accept SOS Request ===")
    accept_data = {
        "socket_log_id": 1,  # This should be a real SOS request ID
        "hospital_id": 1,
        "hospital_name": "Test Hospital",
        "acceptance_note": "Ambulance dispatched within 5 minutes"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/sos/accept",
            json=accept_data,
            headers=get_headers(HOSPITAL_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SOS Accepted: {result}")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test Reject SOS Request
    print("\n=== Test Reject SOS Request ===")
    reject_data = {
        "socket_log_id": 2,  # This should be a real SOS request ID
        "hospital_id": 1,
        "hospital_name": "Test Hospital",
        "rejection_reason": "No available ambulances at this time"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/sos/reject",
            json=reject_data,
            headers=get_headers(HOSPITAL_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SOS Rejected: {result}")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_error_cases():
    """Test error cases and validation"""
    
    print("\n⚠️ Testing Error Cases")
    print("="*50)
    
    # Test 1: Access denied for non-hospital user
    print("\n=== Test 1: Access Denied for Non-Hospital User ===")
    try:
        response = requests.get(
            f"{API_BASE}/sos/my-hospital",
            headers=get_headers(ADMIN_TOKEN)  # Admin trying to access hospital endpoint
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 403:
            print("✅ Correctly denied access to non-hospital user")
        else:
            print(f"❌ Should have denied access: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Invalid SOS status
    print("\n=== Test 2: Invalid SOS Status ===")
    try:
        response = requests.get(
            f"{API_BASE}/sos/by-status/invalid_status",
            headers=get_headers(ADMIN_TOKEN)
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected invalid SOS status")
        else:
            print(f"❌ Should have rejected invalid status: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing SOS API System")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("Make sure you have admin and hospital users in your database")
    print("="*50)
    
    test_sos_endpoints()
    test_sos_accept_reject()
    test_error_cases()
    
    print("\n📋 SOS API Endpoints Created:")
    print("POST /api/v1/socket-logs/sos/accept - Accept SOS request")
    print("POST /api/v1/socket-logs/sos/reject - Reject SOS request")
    print("POST /api/v1/socket-logs/sos/expire/{id} - Expire SOS request")
    print("GET  /api/v1/socket-logs/sos/statistics - Get SOS statistics")
    print("GET  /api/v1/socket-logs/sos/pending - Get pending SOS requests")
    print("GET  /api/v1/socket-logs/sos/by-status/{status} - Get SOS by status")
    print("GET  /api/v1/socket-logs/sos/by-hospital/{id} - Get SOS by hospital")
    print("GET  /api/v1/socket-logs/sos/my-hospital - Get my hospital SOS")
    print("GET  /api/v1/socket-logs/sos/my-hospital/pending - Get my pending SOS")
    print("GET  /api/v1/socket-logs/sos/dashboard - Get SOS dashboard data")
    
    print("\n🔐 Security Features:")
    print("- Role-based access control (Admin/Hospital only)")
    print("- Hospital users can only access their own hospital data")
    print("- Input validation for SOS status")
    print("- Proper error handling and responses") 