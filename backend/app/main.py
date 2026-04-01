from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, domain

app = FastAPI(title="Requirements AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(domain.router)

@app.get("/")
def root():
    return {"message": "Requirements AI API is running"}