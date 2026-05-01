import logging
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.routers import auth, domain, upload, requirements, crosscheck, srs, usecases, admin, profile
from app.core.config import settings
from app.core.limiter import limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("requirements_ai")

app = FastAPI(title="Requirements AI", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

allowed_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    correlation_id = str(uuid.uuid4())
    logger.error(
        "Unhandled exception | correlation_id=%s | %s %s",
        correlation_id,
        request.method,
        request.url,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "correlation_id": correlation_id},
    )


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
