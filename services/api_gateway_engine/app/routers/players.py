from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.config import settings
from app.services.circuit_breaker import forward_request

router = APIRouter(prefix="/players", tags=["Players"])


class RegisterPlayerRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=15)


@router.post("/register")
async def register_player(request: RegisterPlayerRequest):
    # Route traffic to the internal player engine
    url = f"{settings.PLAYER_ENGINE_URL}/api/v1/players/register"
    return await forward_request("POST", url, payload={"username": request.username})
