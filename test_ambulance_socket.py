#!/usr/bin/env python3
"""
Test script for ambulance socket functionality
Run this script to test the ambulance request system
"""

import asyncio
import socketio
import json
from datetime import datetime

# Create socket client
sio = socketio.AsyncClient()

# Test data
TEST_PATIENT_ID = "12"
TEST_HOSPITAL_ID = "19"
TEST_LATITUDE = 12.9716  # Bangalore
TEST_LONGITUDE = 77.5946

# Patient socket handlers
@sio.event
async def connect():
    print("✅ Patient connected to socket server")

@sio.event
async def disconnect():
    print("❌ Patient disconnected from socket server")

@sio.event
async def ambulance_request_confirmed(data):
    print(f"✅ Ambulance request confirmed: {data}")

@sio.event
async def ambulance_request_error(data):
    print(f"❌ Ambulance request error: {data}")

@sio.event
async def ambulance_accepted(data):
    print(f"🎉 Ambulance accepted: {data}")

@sio.event
async def ambulance_rejected(data):
    print(f"😞 Ambulance rejected: {data}")

@sio.event
async def location_updated(data):
    print(f"📍 Location updated: {data}")

# Hospital socket handlers
@sio.event
async def AMBULANCE_ALERT(data):
    print(f"🚑 AMBULANCE ALERT RECEIVED:")
    print(f"   Patient: {data.get('patient_name')}")
    print(f"   Age: {data.get('patient_age')}")
    print(f"   Phone: {data.get('patient_phone')}")
    print(f"   Distance: {data.get('distance_km')} km")
    print(f"   Symptoms: {data.get('emergency_details', {}).get('symptoms')}")
    
    # Simulate hospital response after 2 seconds
    await asyncio.sleep(2)
    
    # Accept the request
    await sio.emit('hospital_response', {
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

async def test_patient_flow():
    """Test the patient side of ambulance requests"""
    print("\n🧪 Testing Patient Flow...")
    
    # Connect as patient
    await sio.connect('http://localhost:8000', {
        'token': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0MSwiZXhwIjoxNzU0NzMwOTk3fQ.yrqb4QfK03SywQRfnkeSHlYijp1c_dtT_GFKWoMH1kw",
        'role': 'patient'
    })
    
    await asyncio.sleep(1)
    
    # Update location
    print("📍 Updating patient location...")
    await sio.emit('update_location', {
        'patient_id': TEST_PATIENT_ID,
        'latitude': TEST_LATITUDE,
        'longitude': TEST_LONGITUDE
    })
    
    await asyncio.sleep(1)
    
    # Send ambulance request
    print("🚑 Sending ambulance request...")
    await sio.emit('ambulance_request', {
        'patient_id': TEST_PATIENT_ID,
        'latitude': TEST_LATITUDE,
        'longitude': TEST_LONGITUDE,
        'emergency_details': {
            'symptoms': 'Chest pain, difficulty breathing',
            'severity': 'high',
            'notes': 'Patient is conscious but in severe pain'
        },
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Wait for response
    await asyncio.sleep(5)
    
    # Disconnect
    await sio.disconnect()

async def test_hospital_flow():
    """Test the hospital side of ambulance requests"""
    print("\n🏥 Testing Hospital Flow...")
    
    # Connect as hospital
    await sio.connect('http://localhost:8000', {
        'userId': TEST_HOSPITAL_ID,
        'role': 'hospital'
    })
    
    await asyncio.sleep(1)
    
    # Wait for ambulance alerts
    print("🏥 Hospital waiting for ambulance alerts...")
    await asyncio.sleep(10)
    
    # Disconnect
    await sio.disconnect()

async def main():
    """Main test function"""
    print("🚑 Ambulance Socket Service Test")
    print("=" * 40)
    
    # Test patient flow
    await test_patient_flow()
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Test hospital flow
    await test_hospital_flow()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    print("Starting ambulance socket test...")
    print("Make sure the socket server is running on http://localhost:8000")
    print("Press Ctrl+C to stop the test")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        print("Test finished") 