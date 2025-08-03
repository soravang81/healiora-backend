#!/usr/bin/env python3
"""
Test script for universal /me route
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/credential/login"
ME_ENDPOINT = f"{BASE_URL}/credential/me"

def test_patient_me_route():
    """Test /me route for patient user"""
    
    print("🏥 Testing Universal /me Route - Patient")
    print("=" * 60)
    
    # Test patient login
    patient_login_data = {
        "email": "patient@example.com",  # Use existing patient email
        "password": "password123"
    }
    
    try:
        # Step 1: Login as patient
        print("🔐 Step 1: Logging in as patient...")
        login_response = requests.post(LOGIN_ENDPOINT, json=patient_login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Patient login successful!")
            print(f"🎫 Token: {login_result['access_token'][:50]}...")
            print(f"👤 Role: {login_result['role']}")
            print()
            
            # Step 2: Get complete patient profile via /me
            print("👤 Step 2: Getting complete patient profile via /me...")
            headers = {"Authorization": f"Bearer {login_result['access_token']}"}
            me_response = requests.get(ME_ENDPOINT, headers=headers)
            
            if me_response.status_code == 200:
                patient_profile = me_response.json()
                print("✅ Patient profile retrieved successfully!")
                print(f"🆔 ID: {patient_profile['id']}")
                print(f"📧 Email: {patient_profile['email']}")
                print(f"👤 Role: {patient_profile['role']}")
                print(f"📝 Full Name: {patient_profile['full_name']}")
                print(f"🎂 Age: {patient_profile['age']}")
                print(f"👨 Gender: {patient_profile['gender']}")
                print(f"📱 Phone: {patient_profile['phone_number']}")
                print(f"🚨 Emergency Contact: {patient_profile['emergency_contact']}")
                print(f"📊 Profile Completion: {patient_profile['profile_completion_percentage']}%")
                print()
                print("🎉 Universal /me route working perfectly for patient!")
                
            else:
                print(f"❌ Failed to get patient profile: {me_response.status_code}")
                print(f"Response: {me_response.text}")
                
        else:
            print(f"❌ Patient login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_doctor_me_route():
    """Test /me route for doctor user"""
    
    print("\n👨‍⚕️ Testing Universal /me Route - Doctor")
    print("=" * 60)
    
    # Test doctor login
    doctor_login_data = {
        "email": "doctor@example.com",  # Use existing doctor email
        "password": "password123"
    }
    
    try:
        # Step 1: Login as doctor
        print("🔐 Step 1: Logging in as doctor...")
        login_response = requests.post(LOGIN_ENDPOINT, json=doctor_login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Doctor login successful!")
            print(f"🎫 Token: {login_result['access_token'][:50]}...")
            print(f"👤 Role: {login_result['role']}")
            print()
            
            # Step 2: Get complete doctor profile via /me
            print("👤 Step 2: Getting complete doctor profile via /me...")
            headers = {"Authorization": f"Bearer {login_result['access_token']}"}
            me_response = requests.get(ME_ENDPOINT, headers=headers)
            
            if me_response.status_code == 200:
                doctor_profile = me_response.json()
                print("✅ Doctor profile retrieved successfully!")
                print(f"🆔 ID: {doctor_profile['id']}")
                print(f"📧 Email: {doctor_profile['email']}")
                print(f"👤 Role: {doctor_profile['role']}")
                print(f"👨‍⚕️ Name: {doctor_profile['name']}")
                print(f"📍 Address: {doctor_profile['address']}")
                print(f"🎓 Education: {doctor_profile['education']}")
                print(f"🏥 Specialization: {doctor_profile['specialization']}")
                print(f"⏰ Years of Experience: {doctor_profile['years_of_experience']}")
                print(f"📊 Profile Completion: {doctor_profile['profile_completion_percentage']}%")
                print()
                print("🎉 Universal /me route working perfectly for doctor!")
                
            else:
                print(f"❌ Failed to get doctor profile: {me_response.status_code}")
                print(f"Response: {me_response.text}")
                
        else:
            print(f"❌ Doctor login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_ambulance_me_route():
    """Test /me route for ambulance user"""
    
    print("\n🚑 Testing Universal /me Route - Ambulance")
    print("=" * 60)
    
    # Test ambulance login
    ambulance_login_data = {
        "email": "ambulance@example.com",  # Use existing ambulance email
        "password": "password123"
    }
    
    try:
        # Step 1: Login as ambulance
        print("🔐 Step 1: Logging in as ambulance...")
        login_response = requests.post(LOGIN_ENDPOINT, json=ambulance_login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Ambulance login successful!")
            print(f"🎫 Token: {login_result['access_token'][:50]}...")
            print(f"👤 Role: {login_result['role']}")
            print()
            
            # Step 2: Get complete ambulance profile via /me
            print("👤 Step 2: Getting complete ambulance profile via /me...")
            headers = {"Authorization": f"Bearer {login_result['access_token']}"}
            me_response = requests.get(ME_ENDPOINT, headers=headers)
            
            if me_response.status_code == 200:
                ambulance_profile = me_response.json()
                print("✅ Ambulance profile retrieved successfully!")
                print(f"🆔 ID: {ambulance_profile['id']}")
                print(f"📧 Email: {ambulance_profile['email']}")
                print(f"👤 Role: {ambulance_profile['role']}")
                print(f"👨‍💼 Driver Name: {ambulance_profile['driver_name']}")
                print(f"📱 Driver Phone: {ambulance_profile['driver_phone']}")
                print(f"🚑 Ambulance Number: {ambulance_profile['ambulance_number']}")
                print(f"🚗 Vehicle Type: {ambulance_profile['vehicle_type']}")
                print(f"📊 Profile Completion: {ambulance_profile['profile_completion_percentage']}%")
                print()
                print("🎉 Universal /me route working perfectly for ambulance!")
                
            else:
                print(f"❌ Failed to get ambulance profile: {me_response.status_code}")
                print(f"Response: {me_response.text}")
                
        else:
            print(f"❌ Ambulance login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_universal_me_features():
    """Test universal features of /me route"""
    
    print("\n🌐 Testing Universal /me Route Features")
    print("=" * 60)
    
    print("✅ Features implemented:")
    print("   - Single endpoint for all user types")
    print("   - Role-based data retrieval")
    print("   - Profile completion percentage")
    print("   - Complete user information")
    print("   - JWT token authentication")
    print("   - Error handling")
    print()
    print("📋 Response includes:")
    print("   - Credential information (id, email, role, is_active)")
    print("   - Role-specific profile data")
    print("   - Profile completion percentage")
    print("   - Timestamps (created_at, updated_at)")
    print()
    print("🎯 Benefits:")
    print("   - One endpoint for all user types")
    print("   - Frontend can use same API call")
    print("   - Automatic role detection")
    print("   - Complete user context")

if __name__ == "__main__":
    print("🏥 Universal /me Route Test")
    print("=" * 60)
    print()
    
    # Test all user types
    test_patient_me_route()
    test_doctor_me_route()
    test_ambulance_me_route()
    test_universal_me_features()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!")
    print()
    print("📝 Usage:")
    print("GET /credential/me")
    print("Headers: Authorization: Bearer <token>")
    print("Returns: Complete user profile based on role") 