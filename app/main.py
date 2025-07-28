from fastapi import FastAPI
from app.api.v1 import users

app = FastAPI(title="Healiora API", version="1.0.0")

# Routers
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "Healiora API is running!"}
