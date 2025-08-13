#!/usr/bin/env python3
"""
Simple script to add dummy doctors and ambulances to the hospital.
This script directly inserts data into the database.
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
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

def hash_password_simple(password: str) -> str:
    """Simple password hashing (you should use proper hashing in production)."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def add_dummy_data():
    """Add dummy doctors and ambulances to the hospital."""
    print("🚑 Adding dummy doctors and ambulances to the hospital...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Find the hospital (credential_id = 19)
        result = db.execute(text("SELECT id, name FROM hospitals WHERE credential_id = 19"))
        hospital = result.fetchone()
        
        if not hospital:
            print("❌ Hospital not found! Please check the credential_id.")
            return
        
        hospital_id = hospital[0]
        hospital_name = hospital[1]
        print(f"🏥 Found hospital: {hospital_name} (ID: {hospital_id})")
        
        # Add dummy doctors
        print("\n👨‍⚕️ Adding dummy doctors...")
        doctors_data = [
            ("Dr. Sarah Johnson", "9876543210", "sarah.johnson@hospital.com", "Emergency Medicine", 8.5),
            ("Dr. Michael Chen", "9876543214", "michael.chen@hospital.com", "General Surgery", 12.0),
            ("Dr. Priya Sharma", "9876543215", "priya.sharma@hospital.com", "Cardiology", 15.5),
            ("Dr. Rajesh Kumar", "9876543216", "rajesh.kumar@hospital.com", "Trauma Surgery", 10.0)
        ]
        
        for name, phone, email, specialization, experience in doctors_data:
            # Check if doctor already exists
            result = db.execute(text("SELECT id FROM doctors WHERE email = :email"), {"email": email})
            if result.fetchone():
                print(f"Doctor {name} already exists, skipping...")
                continue
            
            # Generate password
            password = generate_password()
            hashed_password = hash_password_simple(password)
            
            # Create credential
            result = db.execute(
                text("""
                    INSERT INTO credentials (email, password, phone_number, role, is_active)
                    VALUES (:email, :password, :phone, 'doctor', true)
                    RETURNING id
                """),
                {"email": email, "password": hashed_password, "phone": phone}
            )
            credential_id = result.fetchone()[0]
            
            # Create doctor
            db.execute(
                text("""
                    INSERT INTO doctors (credential_id, hospital_id, name, phone_number, email, 
                                       address, education, specialization, years_of_experience)
                    VALUES (:credential_id, :hospital_id, :name, :phone, :email, 
                           :address, :education, :specialization, :experience)
                """),
                {
                    "credential_id": credential_id,
                    "hospital_id": hospital_id,
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "address": f"123 Medical Center Dr, Kharar",
                    "education": f"MBBS, MD - {specialization}",
                    "specialization": specialization,
                    "experience": experience
                }
            )
            
            print(f"✅ Added doctor: {name} (Email: {email}, Password: {password})")
        
        # Add dummy ambulances
        print("\n🚑 Adding dummy ambulances...")
        ambulances_data = [
            ("AMB001", "Amit Singh", "9876543220", "amit.singh@hospital.com", "Basic Life Support (BLS)"),
            ("AMB002", "Kavita Patel", "9876543224", "kavita.patel@hospital.com", "Advanced Life Support (ALS)"),
            ("AMB003", "Rahul Verma", "9876543225", "rahul.verma@hospital.com", "Basic Life Support (BLS)"),
            ("AMB004", "Sunita Devi", "9876543226", "sunita.devi@hospital.com", "Advanced Life Support (ALS)")
        ]
        
        for ambulance_number, driver_name, driver_phone, driver_email, vehicle_type in ambulances_data:
            # Check if ambulance already exists
            result = db.execute(text("SELECT id FROM ambulances WHERE ambulance_number = :number"), {"number": ambulance_number})
            if result.fetchone():
                print(f"Ambulance {ambulance_number} already exists, skipping...")
                continue
            
            # Generate password
            password = generate_password()
            hashed_password = hash_password_simple(password)
            
            # Create credential
            result = db.execute(
                text("""
                    INSERT INTO credentials (email, password, phone_number, role, is_active)
                    VALUES (:email, :password, :phone, 'ambulance', true)
                    RETURNING id
                """),
                {"email": driver_email, "password": hashed_password, "phone": driver_phone}
            )
            credential_id = result.fetchone()[0]
            
            # Create ambulance
            db.execute(
                text("""
                    INSERT INTO ambulances (credential_id, hospital_id, ambulance_number, driver_name, 
                                          driver_phone, driver_email, vehicle_type)
                    VALUES (:credential_id, :hospital_id, :ambulance_number, :driver_name, 
                           :driver_phone, :driver_email, :vehicle_type)
                """),
                {
                    "credential_id": credential_id,
                    "hospital_id": hospital_id,
                    "ambulance_number": ambulance_number,
                    "driver_name": driver_name,
                    "driver_phone": driver_phone,
                    "driver_email": driver_email,
                    "vehicle_type": vehicle_type
                }
            )
            
            print(f"✅ Added ambulance: {ambulance_number} - {driver_name} (Email: {driver_email}, Password: {password})")
        
        # Commit all changes
        db.commit()
        
        print("\n✅ Successfully added dummy data!")
        print("\n📋 Summary:")
        print("- 4 doctors added")
        print("- 4 ambulances added")
        print("\n🔑 Login credentials have been printed above for each user.")
        print("💡 You can use these credentials to test the system.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_dummy_data() 