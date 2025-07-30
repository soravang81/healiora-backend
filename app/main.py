from fastapi import FastAPI
from app.api.v1 import (
    credential,
    medical_record,
    hospital,
    patient  # ✅ import the patient router
)

app = FastAPI(title="Healiora API", version="1.0.0")

# Routers
app.include_router(credential.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(medical_record.router, prefix="/api/v1/medical-records", tags=["Medical Records"]) 
app.include_router(hospital.router, prefix="/api/v1/hospitals", tags=["Hospitals"])
app.include_router(patient.router, prefix="/api/v1/patients", tags=["Patients"])  # ✅ added patient router

@app.get("/")
def read_root():
    return {"message": "Healiora API is running!"}
