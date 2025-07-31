from fastapi import FastAPI
from app.api.v1 import (
    credential,
    medical_record,
    hospital,
    patient  # ✅ import the patient router
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

app.include_router(credential.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(medical_record.router, prefix="/api/v1/medical-records", tags=["Medical Records"]) 
app.include_router(hospital.router, prefix="/api/v1/hospitals", tags=["Hospitals"])
app.include_router(patient.router, prefix="/api/v1/patients", tags=["Patients"])

@app.get("/")
def read_root():
    return {"message": "Healiora API is running!"}

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*"
)

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio)

# Mount the Socket.IO app
app.mount("/socket.io", socket_app)

# Your FastAPI routes
@app.get("/")
async def root():
    return {"message": "FastAPI + Socket.IO"}

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def chat_message(sid, data):
    # Broadcast to all clients
    await sio.emit('chat_message', data)
    print("chat_msg"+data)

@sio.on("message")
async def handleMessage(sid, data):
    print("from msg"+data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)