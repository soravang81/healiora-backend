#!/usr/bin/env python3
"""
Script to add dummy doctors and ambulances to the hospital for testing purposes.
Run this script to populate the database with test data.
"""

import sys
import os
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.hospital import Hospital
from app.db.models.doctor import Doctor
from app.db.models.ambulance import Ambulance
from app.db.models.credential import Credential
from app.db.models.socket_log import SocketLog
from app.core.security import hash_password
import secrets
import string

def generate_password(length: int = 12) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)):
            return password

def add_dummy_doctors(db: Session, hospital_id: int):
    """Add dummy doctors to the hospital."""
    doctors_data = [
        {
            "name": "Dr. Sarah Johnson",
            "phone_number": "9876543210",
            "email": "sarah.johnson@hospital.com",
            "address": "123 Medical Center Dr, Kharar",
            "education": "MBBS, MD - Emergency Medicine",
            "specialization": "Emergency Medicine",
            "years_of_experience": 8.5
        },
        {
            "name": "Dr. Michael Chen",
            "phone_number": "9876543211",
            "email": "michael.chen@hospital.com",
            "address": "456 Health Plaza, Kharar",
            "education": "MBBS, MS - General Surgery",
            "specialization": "General Surgery",
            "years_of_experience": 12.0
        },
        {
            "name": "Dr. Priya Sharma",
            "phone_number": "9876543212",
            "email": "priya.sharma@hospital.com",
            "address": "789 Care Street, Kharar",
            "education": "MBBS, MD - Cardiology",
            "specialization": "Cardiology",
            "years_of_experience": 15.5
        },
        {
            "name": "Dr. Rajesh Kumar",
            "phone_number": "9876543213",
            "email": "rajesh.kumar@hospital.com",
            "address": "321 Emergency Lane, Kharar",
            "education": "MBBS, MD - Trauma Surgery",
            "specialization": "Trauma Surgery",
            "years_of_experience": 10.0
        }
    ]
    
    for doctor_data in doctors_data:
        # Check if doctor already exists
        existing_doctor = db.query(Doctor).filter(
            Doctor.email == doctor_data["email"]
        ).first()
        
        if existing_doctor:
            print(f"Doctor {doctor_data['name']} already exists, skipping...")
            continue
        
        # Generate password and create credential
        password = generate_password()
        hashed_password = hash_password(password)
        
        credential = Credential(
            email=doctor_data["email"],
            password=hashed_password,
            phone_number=doctor_data["phone_number"],
            role="doctor",
            is_active=True
        )
        db.add(credential)
        db.commit()
        db.refresh(credential)
        
        # Create doctor
        doctor = Doctor(
            credential_id=credential.id,
            hospital_id=hospital_id,
            name=doctor_data["name"],
            phone_number=doctor_data["phone_number"],
            email=doctor_data["email"],
            address=doctor_data["address"],
            education=doctor_data["education"],
            specialization=doctor_data["specialization"],
            years_of_experience=doctor_data["years_of_experience"]
        )
        db.add(doctor)
        db.commit()
        
        print(f"✅ Added doctor: {doctor_data['name']} (Email: {doctor_data['email']}, Password: {password})")

def add_dummy_ambulances(db: Session, hospital_id: int):
    """Add dummy ambulances to the hospital."""
    ambulances_data = [
        {
            "ambulance_number": "AMB001",
            "driver_name": "Amit Singh",
            "driver_phone": "9876543220",
            "driver_email": "amit.singh@hospital.com",
            "vehicle_type": "Basic Life Support (BLS)"
        },
        {
            "ambulance_number": "AMB002",
            "driver_name": "Kavita Patel",
            "driver_phone": "9876543221",
            "driver_email": "kavita.patel@hospital.com",
            "vehicle_type": "Advanced Life Support (ALS)"
        },
        {
            "ambulance_number": "AMB003",
            "driver_name": "Rahul Verma",
            "driver_phone": "9876543222",
            "driver_email": "rahul.verma@hospital.com",
            "vehicle_type": "Basic Life Support (BLS)"
        },
        {
            "ambulance_number": "AMB004",
            "driver_name": "Sunita Devi",
            "driver_phone": "9876543223",
            "driver_email": "sunita.devi@hospital.com",
            "vehicle_type": "Advanced Life Support (ALS)"
        }
    ]
    
    for ambulance_data in ambulances_data:
        # Check if ambulance already exists
        existing_ambulance = db.query(Ambulance).filter(
            Ambulance.ambulance_number == ambulance_data["ambulance_number"]
        ).first()
        
        if existing_ambulance:
            print(f"Ambulance {ambulance_data['ambulance_number']} already exists, skipping...")
            continue
        
        # Generate password and create credential
        password = generate_password()
        hashed_password = hash_password(password)
        
        credential = Credential(
            email=ambulance_data["driver_email"],
            password=hashed_password,
            phone_number=ambulance_data["driver_phone"],
            role="ambulance",
            is_active=True
        )
        db.add(credential)
        db.commit()
        db.refresh(credential)
        
        # Create ambulance
        ambulance = Ambulance(
            credential_id=credential.id,
            hospital_id=hospital_id,
            ambulance_number=ambulance_data["ambulance_number"],
            driver_name=ambulance_data["driver_name"],
            driver_phone=ambulance_data["driver_phone"],
            driver_email=ambulance_data["driver_email"],
            vehicle_type=ambulance_data["vehicle_type"]
        )
        db.add(ambulance)
        db.commit()
        
        print(f"✅ Added ambulance: {ambulance_data['ambulance_number']} - {ambulance_data['driver_name']} (Email: {ambulance_data['driver_email']}, Password: {password})")

def main():
    """Main function to add dummy data."""
    print("🚑 Adding dummy doctors and ambulances to the hospital...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Find the hospital (assuming it's the one with credential_id = 19)
        hospital = db.query(Hospital).filter(Hospital.credential_id == 19).first()
        
        if not hospital:
            print("❌ Hospital not found! Please check the credential_id.")
            return
        
        print(f"🏥 Found hospital: {hospital.name} (ID: {hospital.id})")
        
        # Add dummy doctors
        print("\n👨‍⚕️ Adding dummy doctors...")
        add_dummy_doctors(db, hospital.id)
        
        # Add dummy ambulances
        print("\n🚑 Adding dummy ambulances...")
        add_dummy_ambulances(db, hospital.id)
        
        print("\n✅ Successfully added dummy data!")
        print("\n📋 Summary:")
        print("- 4 doctors added")
        print("- 4 ambulances added")
        print("\n🔑 Login credentials have been printed above for each user.")
        print("💡 You can use these credentials to test the system.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 