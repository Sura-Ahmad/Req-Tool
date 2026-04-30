import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import auth, domain, upload, requirements, crosscheck, srs, usecases, admin, profile

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Requirements AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(domain.router)
app.include_router(upload.router)
app.include_router(requirements.router)
app.include_router(crosscheck.router)
app.include_router(srs.router)
app.include_router(usecases.router)
app.include_router(admin.router)
app.include_router(profile.router)

@app.get("/")
def root():
    return {"message": "Requirements AI API is running"}
