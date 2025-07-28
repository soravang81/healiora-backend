from fastapi import FastAPI
from app.api.v1 import users, medical_record, hospital  # ✅ import the new router

app = FastAPI(title="Healiora API", version="1.0.0")

# Routers
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(medical_record.router, prefix="/api/v1/medical-records", tags=["Medical Records"]) 
app.include_router(hospital.router, prefix="/api/v1/hospitals", tags=["Hospitals"]) # ✅ add this

@app.get("/")
def read_root():
    return {"message": "Healiora API is running!"}
