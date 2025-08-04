from fastapi import FastAPI
from app.api.v1 import (
    credential,
    medical_record,
    hospital,
    patient,
    doctor,
    ambulance,
    socket_log
)
from fastapi.middleware.cors import CORSMiddleware
import socketio
from app.services.socket import sio
import os

app = FastAPI(title="Healiora API", version="1.0.0" , debug=True)

sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)

app.mount("/socket.io/", sio_asgi_app, name="socket.io")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary for development
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(credential.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(medical_record.router, prefix="/api/v1/medical-records", tags=["Medical Records"]) 
app.include_router(hospital.router, prefix="/api/v1/hospitals", tags=["Hospitals"])
app.include_router(patient.router, prefix="/api/v1/patients", tags=["Patients"]) 
app.include_router(doctor.router, prefix="/api/v1/doctors", tags=["Doctors"])
app.include_router(ambulance.router, prefix="/api/v1/ambulances", tags=["Ambulances"])
app.include_router(socket_log.router, prefix="/api/v1/socket-logs", tags=["Socket Logs"])

@app.get("/")
def read_root():
    return {"message": "Healiora API is running!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )