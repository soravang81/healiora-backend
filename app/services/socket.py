import socketio
import math
from typing import Dict, List, Optional
import urllib.parse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.hospital import get_all_hospitals
from app.services.patient import get_patient_by_credential_id
from app.utils.jwt import verify_token
from app.services.socket_log import create_socket_log, update_socket_log
from datetime import datetime

# mgr = socketio.AsyncRedisManager(url="redis://localhost:6379/0") 
sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=[]
)

# Store connected users: {user_id: {socket_id: str, role: str}}
connected_users: Dict[str, Dict] = {}

# Store patient locations: {patient_id: {latitude: float, longitude: float, timestamp: str}}
patient_locations: Dict[str, Dict] = {}

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def update_patient_location(patient_id: str, latitude: float, longitude: float):
    """
    Update patient's current location
    """
    from datetime import datetime
    patient_locations[patient_id] = {
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": datetime.utcnow().isoformat()
    }
    print(f"📍 Updated location for patient {patient_id}: {latitude}, {longitude}")

def get_patient_location(patient_id: str) -> Optional[Dict]:
    """
    Get patient's current location
    """
    return patient_locations.get(patient_id)

def find_nearest_hospital(patient_lat: float, patient_lon: float, db: Session) -> Optional[Dict]:
    """
    Find the nearest hospital with available capacity
    """
    try:
        hospitals = get_all_hospitals(db)
        
        if not hospitals:
            return None
        
        # Filter hospitals with coordinates and calculate distances
        hospitals_with_distance = []
        for hospital in hospitals:
            if hospital.latitude is not None and hospital.longitude is not None:
                distance = calculate_distance(
                    patient_lat, patient_lon, 
                    hospital.latitude, hospital.longitude
                )
                hospitals_with_distance.append({
                    'id': hospital.id,
                    'name': hospital.name,
                    'address': hospital.address,
                    'latitude': hospital.latitude,
                    'longitude': hospital.longitude,
                    'phone': hospital.phone,
                    'distance': distance
                })
        
        if not hospitals_with_distance:
            return None
        
        # Sort by distance and return the nearest
        nearest_hospital = min(hospitals_with_distance, key=lambda x: x['distance'])
        return nearest_hospital
        
    except Exception as e:
        print(f"Error finding nearest hospital: {e}")
        return None

@sio.event
async def connect(sid, environ):
    try:
        # Extract user_id and role from token or query parameters
        # For now, we'll assume they're passed in the query string
        # print(f"✅ Client connected: {sid}") 
        query_params = environ.get("QUERY_STRING", "")
        print(f"✅ Query params: {query_params}")
        params = {}
        # Parse query params robustly (handle both & and ? in the string)

        if query_params:
            # Remove leading '?' if present
            qp = query_params[1:] if query_params.startswith("?") else query_params
            # Parse query string into dict
            params = dict(urllib.parse.parse_qsl(qp))
        else:
            params = {}

        role = params.get("role")
        token = params.get("token")

        user_id = None
        if token:
            try:
                # Decode JWT manually to extract user_id
                payload = verify_token(token)
                print(f"✅ Token payload: {payload}")
                user_id = payload.get("user_id")
            except Exception as e:
                print(f"❌ Error decoding token: {e}")
                user_id = None

        print(f"✅ Client connected: {sid} with token {token} and role {role} and user_id {user_id}")
        
        if user_id and role:
            connected_users[user_id] = {
                "socket_id": sid,
                "role": role
            }
            print(f"✅ User {user_id} ({role}) connected with socket {sid}")
            print(f"✅ Connected users: {connected_users}")
            
            # Log connection event
            # try:
            #     db = next(get_db())
            #     create_socket_log(
            #         db=db,
            #         event_type="connect",
            #         socket_id=sid,
            #         user_id=user_id,
            #         user_role=role,
            #         event_data={"connected_users_count": len(connected_users)},
            #         status="success"
            #     )
            # except Exception as e:
            #     print(f"❌ Error logging connection: {e}")
        else:
            print(f"⚠️ Missing userId or role for socket {sid}")
            
    except Exception as e:
        print(f"❌ Error in connect: {e}")

@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")
    
    # Find user and log disconnect
    disconnected_user = None
    for user_id, user_data in list(connected_users.items()):
        if user_data["socket_id"] == sid:
            disconnected_user = {"user_id": user_id, "role": user_data["role"]}
            del connected_users[user_id]
            print(f"✅ Removed user {user_id} from connected users")
            break
    
    # Log disconnect event
    # if disconnected_user:
    #     try:
    #         db = next(get_db())
    #         create_socket_log(
    #             db=db,
    #             event_type="disconnect",
    #             socket_id=sid,
    #             user_id=disconnected_user["user_id"],
    #             user_role=disconnected_user["role"],
    #             event_data={"connected_users_count": len(connected_users)},
    #             status="success"
    #         )
    #     except Exception as e:
    #         print(f"❌ Error logging disconnect: {e}")

@sio.event
async def update_location(sid, data):
    """
    Update patient's current location
    data should contain: {patient_id, latitude, longitude}
    """
    try:
        patient_id = data.get("patient_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        if patient_id and latitude is not None and longitude is not None:
            update_patient_location(str(patient_id), latitude, longitude)
            await sio.emit("location_updated", {"message": "Location updated successfully"}, to=sid)
            print(f"📍 Location updated for patient {patient_id}")
            
            # Log location update
            try:
                db = next(get_db())
                create_socket_log(
                    db=db,
                    event_type="update_location",
                    socket_id=sid,
                    user_id=str(patient_id),
                    user_role="patient",
                    event_data=data,
                    patient_latitude=str(latitude),
                    patient_longitude=str(longitude),
                    status="success"
                )
            except Exception as e:
                print(f"❌ Error logging location update: {e}")
        else:
            await sio.emit("location_error", {"error": "Missing location data"}, to=sid)
            
    except Exception as e:
        print(f"❌ Error updating location: {e}")
        await sio.emit("location_error", {"error": "Failed to update location"}, to=sid)

@sio.event
async def ambulance_request(sid, data):
    """
    Handle ambulance request from patient
    data should contain: {patient_id, latitude, longitude, emergency_details}
    """
    start_time = datetime.utcnow()
    log_id = None
    
    try:
        print(f"🚑 Ambulance request received from {sid}: {data}")
        
        patient_id = data.get("patient_id")
        patient_lat = data.get("latitude")
        patient_lon = data.get("longitude")
        emergency_details = data.get("emergency_details", {})
        
        if not patient_id:
            print("❌ Missing patient_id in ambulance request")
            await sio.emit("ambulance_request_error", {"error": "Missing patient_id"}, to=sid)
            return
        
        # Get database session
        db = next(get_db())
        
        # Log ambulance request
        try:
            socket_log = create_socket_log(
                db=db,
                event_type="ambulance_request",
                socket_id=sid,
                user_id=str(patient_id),
                user_role="patient",
                event_data=data,
                request_data=emergency_details,
                patient_latitude=str(patient_lat) if patient_lat else None,
                patient_longitude=str(patient_lon) if patient_lon else None,
                status="pending"
            )
            log_id = socket_log.id
        except Exception as e:
            print(f"❌ Error logging ambulance request: {e}")
        
        try:
            # Get patient details
            patient = get_patient_by_credential_id(db, int(patient_id))
            print(f"📋 Patient found: {patient.full_name}")
            
            # Get patient location - first from request, then from stored location, then default
            if patient_lat is None or patient_lon is None:
                stored_location = get_patient_location(str(patient_id))
                if stored_location:
                    patient_lat = stored_location["latitude"]
                    patient_lon = stored_location["longitude"]
                    print(f"📍 Using stored location for patient: {patient_lat}, {patient_lon}")
                else:
                    # Default to a central location (you can modify this)
                    patient_lat = 12.9716  # Default latitude (e.g., Bangalore)
                    patient_lon = 77.5946  # Default longitude
                    print(f"⚠️ Using default coordinates for patient: {patient_lat}, {patient_lon}")
            
            # Find nearest hospital
            nearest_hospital = find_nearest_hospital(patient_lat, patient_lon, db)
            
            if not nearest_hospital:
                print("❌ No hospitals found")
                await sio.emit("ambulance_request_error", {"error": "No hospitals available"}, to=sid)
                
                # Update log with error
                if log_id:
                    update_socket_log(db, log_id, status="failed", error_message="No hospitals available")
                return
            
            print(f"🏥 Nearest hospital: {nearest_hospital['name']} ({nearest_hospital['distance']:.2f} km)")
            
            # Check if hospital is connected
            hospital_user_id = str(nearest_hospital['id'])
            if hospital_user_id not in connected_users:
                print(f"⚠️ Hospital {nearest_hospital['name']} is not connected")
                await sio.emit("ambulance_request_error", {"error": "Nearest hospital is not available"}, to=sid)
                
                # Update log with error
                if log_id:
                    update_socket_log(db, log_id, status="failed", error_message="Nearest hospital not connected")
                return
            
            hospital_socket_data = connected_users[hospital_user_id]
            if hospital_socket_data["role"] != "hospital":
                print(f"⚠️ User {hospital_user_id} is not a hospital")
                await sio.emit("ambulance_request_error", {"error": "Hospital not available"}, to=sid)
                
                # Update log with error
                if log_id:
                    update_socket_log(db, log_id, status="failed", error_message="User is not a hospital")
                return
            
            # Prepare ambulance alert data
            ambulance_alert_data = {
                "patient_id": patient_id,
                "patient_name": patient.full_name,
                "patient_phone": patient.phone_number,
                "patient_age": patient.age,
                "patient_gender": patient.gender,
                "emergency_contact": patient.emergency_contact,
                "patient_latitude": patient_lat,
                "patient_longitude": patient_lon,
                "hospital_id": nearest_hospital['id'],
                "hospital_name": nearest_hospital['name'],
                "distance_km": round(nearest_hospital['distance'], 2),
                "emergency_details": emergency_details,
                "request_timestamp": data.get("timestamp")
            }
            
            # Send ambulance alert to hospital
            await sio.emit("AMBULANCE_ALERT", ambulance_alert_data, to=hospital_socket_data["socket_id"])
            print(f"✅ Ambulance alert sent to hospital {nearest_hospital['name']}")
            
            # Send confirmation to patient
            await sio.emit("ambulance_request_confirmed", {
                "message": f"Ambulance request sent to {nearest_hospital['name']}",
                "hospital_name": nearest_hospital['name'],
                "distance_km": round(nearest_hospital['distance'], 2),
                "estimated_time": f"{int(nearest_hospital['distance'] * 2)} minutes"
            }, to=sid)
            
            # Update log with success
            if log_id:
                response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                update_socket_log(
                    db, log_id, 
                    status="success", 
                    response_data=ambulance_alert_data,
                    hospital_id=nearest_hospital['id'],
                    hospital_name=nearest_hospital['name'],
                    distance_km=str(round(nearest_hospital['distance'], 2)),
                    response_time_ms=response_time
                )
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error processing ambulance request: {e}")
        await sio.emit("ambulance_request_error", {"error": "Internal server error"}, to=sid)
        
        # Update log with error
        if log_id:
            try:
                db = next(get_db())
                update_socket_log(db, log_id, status="failed", error_message=str(e))
            except Exception as log_error:
                print(f"❌ Error updating log: {log_error}")

@sio.event
async def hospital_response(sid, data):
    """
    Handle hospital response to ambulance request
    data should contain: {patient_id, hospital_id, response: 'accepted'|'rejected', details}
    """
    start_time = datetime.utcnow()
    log_id = None
    
    try:
        print(f"🏥 Hospital response received from {sid}: {data}")
        
        patient_id = data.get("patient_id")
        hospital_id = data.get("hospital_id")
        response = data.get("response")  # 'accepted' or 'rejected'
        details = data.get("details", {})
        
        if not patient_id or not response:
            print("❌ Missing patient_id or response in hospital response")
            return
        
        # Get database session and log hospital response
        db = next(get_db())
        try:
            socket_log = create_socket_log(
                db=db,
                event_type="hospital_response",
                socket_id=sid,
                user_id=str(hospital_id) if hospital_id else None,
                user_role="hospital",
                event_data=data,
                response_data=details,
                hospital_id=hospital_id,
                status="pending"
            )
            log_id = socket_log.id
        except Exception as e:
            print(f"❌ Error logging hospital response: {e}")
        
        # Find patient's socket
        patient_user_id = str(patient_id)
        if patient_user_id not in connected_users:
            print(f"⚠️ Patient {patient_id} is not connected")
            
            # Update log with error
            if log_id:
                update_socket_log(db, log_id, status="failed", error_message="Patient not connected")
            return
        
        patient_socket_data = connected_users[patient_user_id]
        if patient_socket_data["role"] != "patient":
            print(f"⚠️ User {patient_id} is not a patient")
            
            # Update log with error
            if log_id:
                update_socket_log(db, log_id, status="failed", error_message="User is not a patient")
            return
        
        # Send response to patient
        if response == "accepted":
            await sio.emit("ambulance_accepted", {
                "message": "Ambulance request accepted! Help is on the way.",
                "details": details
            }, to=patient_socket_data["socket_id"])
            print(f"✅ Ambulance accepted notification sent to patient {patient_id}")
        else:
            await sio.emit("ambulance_rejected", {
                "message": "Ambulance request could not be fulfilled.",
                "details": details
            }, to=patient_socket_data["socket_id"])
            print(f"❌ Ambulance rejected notification sent to patient {patient_id}")
        
        # Update log with success
        if log_id:
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            update_socket_log(
                db, log_id, 
                status="success", 
                response_time_ms=response_time
            )
            
    except Exception as e:
        print(f"❌ Error processing hospital response: {e}")
        
        # Update log with error
        if log_id:
            try:
                db = next(get_db())
                update_socket_log(db, log_id, status="failed", error_message=str(e))
            except Exception as log_error:
                print(f"❌ Error updating log: {log_error}")

@sio.event
async def my_event(sid, data):
    print(f"📦 Received data from {sid}: {data}")
    await sio.emit("response", {"data": "Message received!"}, to=sid)