#!/usr/bin/env python3
"""
Debug script to check SOS data in the database.
"""

from sqlalchemy import text
from app.db.session import get_db

def debug_sos_data():
    """Debug SOS data in the database."""
    print("🔍 Debugging SOS data in the database...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check all socket logs
        print("\n📊 All Socket Logs:")
        result = db.execute(text("""
            SELECT id, event_type, user_id, hospital_id, sos_status, status, created_at 
            FROM socket_logs 
            ORDER BY created_at DESC 
            LIMIT 10
        """))
        logs = result.fetchall()
        
        for log in logs:
            print(f"  ID: {log[0]}, Event: {log[1]}, User: {log[2]}, Hospital: {log[3]}, SOS Status: {log[4]}, Status: {log[5]}, Created: {log[6]}")
        
        # Check ambulance requests specifically
        print("\n🚑 Ambulance Requests:")
        result = db.execute(text("""
            SELECT id, user_id, hospital_id, sos_status, status, response_data, created_at 
            FROM socket_logs 
            WHERE event_type = 'ambulance_request'
            ORDER BY created_at DESC 
            LIMIT 10
        """))
        ambulance_logs = result.fetchall()
        
        for log in ambulance_logs:
            print(f"  ID: {log[0]}, User: {log[1]}, Hospital: {log[2]}, SOS Status: {log[3]}, Status: {log[4]}, Created: {log[5]}")
        
        # Check hospital data
        print("\n🏥 Hospital Data:")
        result = db.execute(text("SELECT id, name, credential_id FROM hospitals WHERE credential_id = 19"))
        hospital = result.fetchone()
        if hospital:
            print(f"  Hospital ID: {hospital[0]}, Name: {hospital[1]}, Credential ID: {hospital[2]}")
        
        # Count SOS requests by status for hospital 7
        print("\n📈 SOS Counts for Hospital 7:")
        result = db.execute(text("""
            SELECT sos_status, COUNT(*) as count 
            FROM socket_logs 
            WHERE event_type = 'ambulance_request' AND hospital_id = 7
            GROUP BY sos_status
        """))
        counts = result.fetchall()
        
        for count in counts:
            print(f"  {count[0] or 'NULL'}: {count[1]}")
        
        # Check pending requests
        print("\n⏳ Pending SOS Requests for Hospital 7:")
        result = db.execute(text("""
            SELECT id, user_id, response_data, created_at 
            FROM socket_logs 
            WHERE event_type = 'ambulance_request' AND hospital_id = 7 AND sos_status = 'pending'
            ORDER BY created_at DESC
        """))
        pending = result.fetchall()
        
        for req in pending:
            print(f"  ID: {req[0]}, User: {req[1]}, Created: {req[3]}")
            if req[2]:
                print(f"    Response Data: {req[2]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_sos_data() 