from fastapi import FastAPI
from app.api.v1 import (
    credential,
    medical_record,
    hospital,
    patient,
    doctor,
    ambulance
      # ✅ import the patient router
)
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import socketio

app = FastAPI(title="Healiora API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend URL like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(credential.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(medical_record.router, prefix="/api/v1/medical-records", tags=["Medical Records"]) 
app.include_router(hospital.router, prefix="/api/v1/hospitals", tags=["Hospitals"])
app.include_router(patient.router, prefix="/api/v1/patients", tags=["Patients"]) 
app.include_router(doctor.router, prefix="/api/v1/doctors", tags=["Doctors"])
app.include_router(ambulance.router, prefix="/api/v1/ambulances", tags=["Ambulances"])
 # ✅ added patient router

@app.get("/")
def read_root():
    return {"message": "Healiora API is running!"}

# Socket.IO Setup
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000"],  # Match your frontend URL
    logger=True,
    engineio_logger=True
)

# Wrap with ASGI application
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app
)
app.mount("/socket.io", socket_app)

# Socket.IO Events
@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid}")
    # You can access query parameters from environ
    query_string = environ.get('QUERY_STRING', '')
    print(f"Query params: {query_string}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def chat_message(sid, data):
    print(f"Message from {sid}: {data}")
    await sio.emit('chat_message', data, room=sid)

@sio.on('message')
async def handle_message(sid, data):
    print(f"Received message: {data}")
    await sio.emit('response', {'status': 'received'}, room=sid)

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)