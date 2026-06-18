from fastapi import APIRouter
from pydantic import BaseModel, UUID4, Field
from app.core.config import settings
from app.services.circuit_breaker import forward_request

router = APIRouter(prefix="/scores", tags=["Scores"])


class SubmitScoreRequest(BaseModel):
    player_id: UUID4
    score: int = Field(..., ge=0)  # Score must be greater than or equal to 0


@router.post("")
async def submit_score(request: SubmitScoreRequest):
    url = f"{settings.MATCH_ENGINE_URL}/api/v1/scores"

    # Convert UUID4 to string for JSON serialization
    payload = {"player_id": str(request.player_id), "score": request.score}

    return await forward_request("POST", url, payload=payload)
