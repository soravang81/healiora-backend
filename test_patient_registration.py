#!/usr/bin/env python3
"""
Test script for patient registration with automatic login
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = f"{BASE_URL}/register-complete"
LOGIN_ENDPOINT = f"{BASE_URL}/login"
ME_ENDPOINT = f"{BASE_URL}/me"

def test_patient_registration_with_auto_login():
    """Test the complete patient registration with automatic login"""
    
    # Test data for patient registration
    patient_data = {
        "email": f"patient_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "password": "securepassword123",
        "full_name": "John Doe",
        "age": 35,
        "phone_number": "+1234567890",
        "emergency_contact": "+1987654321",
        "gender": "male"
    }
    
    print("🚀 Testing Patient Registration with Automatic Login")
    print("=" * 60)
    print(f"📧 Email: {patient_data['email']}")
    print(f"👤 Name: {patient_data['full_name']}")
    print(f"📱 Phone: {patient_data['phone_number']}")
    print(f"🚨 Emergency: {patient_data['emergency_contact']}")
    print(f"👨 Gender: {patient_data['gender']}")
    print(f"🎂 Age: {patient_data['age']}")
    print()
    
    try:
        # Step 1: Register patient with complete details
        print("📝 Step 1: Registering patient with complete details...")
        response = requests.post(REGISTER_ENDPOINT, json=patient_data)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Registration successful!")
            print(f"🆔 Patient ID: {result['patient']['id']}")
            print(f"🔑 Access Token: {result['access_token'][:50]}...")
            print(f"🎫 Token Type: {result['token_type']}")
            print()
            
            # Step 2: Use the returned token to access protected endpoints
            print("🔐 Step 2: Testing automatic login with returned token...")
            headers = {"Authorization": f"Bearer {result['access_token']}"}
            
            # Test accessing patient profile
            me_response = requests.get(ME_ENDPOINT, headers=headers)
            
            if me_response.status_code == 200:
                patient_profile = me_response.json()
                print("✅ Automatic login successful!")
                print(f"👤 Retrieved Profile: {patient_profile['full_name']}")
                print(f"📧 Email: {patient_profile['email']}")
                print(f"📱 Phone: {patient_profile['phone_number']}")
                print(f"🚨 Emergency: {patient_profile['emergency_contact']}")
                print(f"👨 Gender: {patient_profile['gender']}")
                print(f"🎂 Age: {patient_profile['age']}")
                print()
                print("🎉 Complete registration and automatic login working perfectly!")
                
            else:
                print(f"❌ Failed to access profile: {me_response.status_code}")
                print(f"Response: {me_response.text}")
                
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_traditional_login_after_registration():
    """Test traditional login after registration"""
    
    # Test data
    patient_data = {
        "email": f"patient_login_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "password": "securepassword123",
        "full_name": "Jane Smith",
        "age": 28,
        "phone_number": "+1555123456",
        "emergency_contact": "+1555987654",
        "gender": "female"
    }
    
    print("\n🔄 Testing Traditional Login After Registration")
    print("=" * 60)
    
    try:
        # Step 1: Register patient
        print("📝 Step 1: Registering patient...")
        response = requests.post(REGISTER_ENDPOINT, json=patient_data)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Registration successful!")
            print()
            
            # Step 2: Traditional login
            print("🔐 Step 2: Testing traditional login...")
            login_data = {
                "email": patient_data["email"],
                "password": patient_data["password"]
            }
            
            login_response = requests.post(LOGIN_ENDPOINT, json=login_data)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ Traditional login successful!")
                print(f"🔑 Login Token: {login_result['access_token'][:50]}...")
                print()
                
                # Step 3: Access profile with login token
                print("👤 Step 3: Accessing profile with login token...")
                headers = {"Authorization": f"Bearer {login_result['access_token']}"}
                me_response = requests.get(ME_ENDPOINT, headers=headers)
                
                if me_response.status_code == 200:
                    patient_profile = me_response.json()
                    print("✅ Profile access successful!")
                    print(f"👤 Name: {patient_profile['full_name']}")
                    print(f"📧 Email: {patient_profile['email']}")
                    print("🎉 Traditional login flow working perfectly!")
                else:
                    print(f"❌ Failed to access profile: {me_response.status_code}")
                    
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🏥 Patient Registration System Test")
    print("=" * 60)
    print()
    
    # Test 1: Complete registration with auto-login
    test_patient_registration_with_auto_login()
    
    # Test 2: Traditional login after registration
    test_traditional_login_after_registration()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!") 