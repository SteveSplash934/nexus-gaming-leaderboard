from fastapi import APIRouter
from app.core.config import settings
from app.services.circuit_breaker import forward_request

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("")
async def get_leaderboard():
    url = f"{settings.LEADERBOARD_ENGINE_URL}/api/v1/leaderboard"

    # Allow 4 seconds for the Leaderboard Engine (and subsequent AI processing)
    return await forward_request("GET", url, timeout=4.0)
