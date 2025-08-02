#!/usr/bin/env python3
"""
Test script for ambulance socket functionality with real user IDs
This version uses actual user IDs from the database
"""

import socketio
import time
import json
from datetime import datetime

# Create socket client (synchronous version)
sio = socketio.Client()

# Test data - using real user IDs from database
TEST_PATIENT_ID = "5"  # Real patient ID from database
TEST_HOSPITAL_ID = "3"  # Real hospital ID from database (City Hospital)
TEST_LATITUDE = 12.9716  # Bangalore
TEST_LONGITUDE = 77.5946

# Patient socket handlers
@sio.event
def connect():
    print("✅ Patient connected to socket server")

@sio.event
def disconnect():
    print("❌ Patient disconnected from socket server")

@sio.event
def ambulance_request_confirmed(data):
    print(f"✅ Ambulance request confirmed: {data}")

@sio.event
def ambulance_request_error(data):
    print(f"❌ Ambulance request error: {data}")

@sio.event
def ambulance_accepted(data):
    print(f"🎉 Ambulance accepted: {data}")

@sio.event
def ambulance_rejected(data):
    print(f"😞 Ambulance rejected: {data}")

@sio.event
def location_updated(data):
    print(f"📍 Location updated: {data}")

# Hospital socket handlers
@sio.event
def AMBULANCE_ALERT(data):
    print(f"🚑 AMBULANCE ALERT RECEIVED:")
    print(f"   Patient: {data.get('patient_name')}")
    print(f"   Age: {data.get('patient_age')}")
    print(f"   Phone: {data.get('patient_phone')}")
    print(f"   Distance: {data.get('distance_km')} km")
    print(f"   Symptoms: {data.get('emergency_details', {}).get('symptoms')}")
    
    # Simulate hospital response after 2 seconds
    time.sleep(2)
    
    # Accept the request
    sio.emit('hospital_response', {
        'patient_id': data.get('patient_id'),
        'hospital_id': data.get('hospital_id'),
        'response': 'accepted',
        'details': {
            'ambulance_id': 'AMB001',
            'estimated_arrival': '15 minutes',
            'driver_phone': '+1234567890',
            'driver_name': 'John Doe'
        }
    })
    print("✅ Hospital accepted ambulance request")

def create_test_token(user_id):
    """Create a test JWT token"""
    from app.utils.jwt import create_access_token
    return create_access_token(user_id=user_id)

def test_patient_flow():
    """Test the patient side of ambulance requests"""
    print("\n🧪 Testing Patient Flow...")
    
    try:
        # Create JWT token for patient
        patient_token = create_test_token(int(TEST_PATIENT_ID))
        print(f"🔑 Patient token created for user {TEST_PATIENT_ID}: {patient_token[:50]}...")
        
        # Connect as patient with JWT token
        sio.connect('http://localhost:8000', {
            'token': patient_token,
            'role': 'patient'
        })
        
        time.sleep(1)
        
        # Update location
        print("📍 Updating patient location...")
        sio.emit('update_location', {
            'patient_id': TEST_PATIENT_ID,
            'latitude': TEST_LATITUDE,
            'longitude': TEST_LONGITUDE
        })
        
        time.sleep(1)
        
        # Send ambulance request
        print("🚑 Sending ambulance request...")
        sio.emit('ambulance_request', {
            'patient_id': TEST_PATIENT_ID,
            'latitude': TEST_LATITUDE,
            'longitude': TEST_LONGITUDE,
            'emergency_details': {
                'symptoms': 'Chest pain, difficulty breathing',
                'severity': 'high',
                'notes': 'Patient is conscious but in severe pain'
            },
            'timestamp': datetime.now().isoformat()
        })
        
        # Wait for response
        time.sleep(5)
        
        # Disconnect
        sio.disconnect()
        
    except Exception as e:
        print(f"❌ Error in patient flow: {e}")

def test_hospital_flow():
    """Test the hospital side of ambulance requests"""
    print("\n🏥 Testing Hospital Flow...")
    
    try:
        # Create JWT token for hospital
        hospital_token = create_test_token(int(TEST_HOSPITAL_ID))
        print(f"🔑 Hospital token created for user {TEST_HOSPITAL_ID}: {hospital_token[:50]}...")
        
        # Connect as hospital with JWT token
        sio.connect('http://localhost:8000', {
            'token': hospital_token,
            'role': 'hospital'
        })
        
        time.sleep(1)
        
        # Wait for ambulance alerts
        print("🏥 Hospital waiting for ambulance alerts...")
        time.sleep(10)
        
        # Disconnect
        sio.disconnect()
        
    except Exception as e:
        print(f"❌ Error in hospital flow: {e}")

def test_ambulance_request_flow():
    """Test complete ambulance request flow"""
    print("\n🚑 Testing Complete Ambulance Request Flow...")
    
    try:
        # First, connect hospital
        hospital_token = create_test_token(int(TEST_HOSPITAL_ID))
        print(f"🔑 Hospital token created for user {TEST_HOSPITAL_ID}: {hospital_token[:50]}...")
        
        # Connect as hospital
        sio.connect('http://localhost:8000', {
            'token': hospital_token,
            'role': 'hospital'
        })
        
        time.sleep(2)
        
        # Disconnect hospital
        sio.disconnect()
        time.sleep(1)
        
        # Now connect patient and send request
        patient_token = create_test_token(int(TEST_PATIENT_ID))
        print(f"🔑 Patient token created for user {TEST_PATIENT_ID}: {patient_token[:50]}...")
        
        # Connect as patient
        sio.connect('http://localhost:8000', {
            'token': patient_token,
            'role': 'patient'
        })
        
        time.sleep(1)
        
        # Send ambulance request
        print("🚑 Sending ambulance request...")
        sio.emit('ambulance_request', {
            'patient_id': TEST_PATIENT_ID,
            'latitude': TEST_LATITUDE,
            'longitude': TEST_LONGITUDE,
            'emergency_details': {
                'symptoms': 'Chest pain, difficulty breathing',
                'severity': 'high',
                'notes': 'Patient is conscious but in severe pain'
            },
            'timestamp': datetime.now().isoformat()
        })
        
        # Wait for response
        time.sleep(5)
        
        # Disconnect patient
        sio.disconnect()
        
    except Exception as e:
        print(f"❌ Error in ambulance request flow: {e}")

def main():
    """Main test function"""
    print("🚑 Ambulance Socket Service Test (Real Users)")
    print("=" * 50)
    print(f"Using Patient ID: {TEST_PATIENT_ID}")
    print(f"Using Hospital ID: {TEST_HOSPITAL_ID}")
    print("=" * 50)
    
    # Test patient flow
    test_patient_flow()
    
    # Wait a bit
    time.sleep(2)
    
    # Test hospital flow
    test_hospital_flow()
    
    # Wait a bit
    time.sleep(2)
    
    # Test complete flow
    test_ambulance_request_flow()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    print("Starting real user ambulance socket test...")
    print("Make sure the socket server is running on http://localhost:8000")
    print("Press Ctrl+C to stop the test")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        print("Test finished") 