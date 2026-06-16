from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import http_exception_handler, validation_exception_handler
from app.routers import players, scores, leaderboard

# Initialize FastAPI App
app = FastAPI(
    title="Nexus API Gateway",
    description="Secure entry point and circuit breaker for the Nexus Gaming Leaderboard System.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware (Configure for production domains later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Custom Exception Handlers to enforce API Contracts
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Register Routers
app.include_router(players.router, prefix="/api/v1")
app.include_router(scores.router, prefix="/api/v1")
app.include_router(leaderboard.router, prefix="/api/v1")

# Gateway Health Check
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "success": True,
        "message": "API Gateway Engine is fully operational."
    }