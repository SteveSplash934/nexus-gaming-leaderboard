import asyncio
import httpx
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import http_exception_handler, validation_exception_handler
from app.routers import players, scores, leaderboard

app = FastAPI(
    title="Nexus API Gateway",
    description="Secure entry point and circuit breaker for the Nexus Gaming Leaderboard System.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(players.router, prefix="/api/v1")
app.include_router(scores.router, prefix="/api/v1")
app.include_router(leaderboard.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Dynamic Gateway Health Aggregator
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    # Map all services we eventually want to monitor
    services = {
        "player_engine": f"{settings.PLAYER_ENGINE_URL}/health",
        "match_engine": f"{settings.MATCH_ENGINE_URL}/health",
        "leaderboard_engine": f"{settings.LEADERBOARD_ENGINE_URL}/health",
        "ai_engine": f"{settings.AI_ENGINE_URL}/health",
    }

    async def ping_service(name: str, url: str):
        async with httpx.AsyncClient() as client:
            try:
                # 1.5 seconds timeout to keep the check snappy
                response = await client.get(url, timeout=1.5)
                if response.status_code == 200:
                    return name, {"status": "healthy", "details": response.json()}
                return name, {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                }
            except Exception:
                return name, {"status": "offline", "error": "Unreachable or timed out"}

    # Ping all services concurrently
    tasks = [ping_service(name, url) for name, url in services.items()]
    results = await asyncio.gather(*tasks)
    health_results = dict(results)

    # Determine gateway status based on the availability of currently active critical services
    critical_services = ["player_engine", "match_engine"]
    all_critical_healthy = all(
        health_results[srv]["status"] == "healthy" for srv in critical_services
    )

    return {
        "success": True,
        "gateway_status": "operational" if all_critical_healthy else "degraded",
        "services": health_results,
    }
