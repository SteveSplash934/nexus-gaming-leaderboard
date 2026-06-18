import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)  # Added SettingsConfigDict
from langchain_ollama import OllamaLLM


class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "gemma4:31b-cloud"

    # Strict Pydantic v2 environment loading configuration
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

app = FastAPI(
    title="Nexus AI Engine",
    description="Microservice interfacing with local Ollama to generate gamer hype commentary using langchain-ollama.",
    version="1.0.0",
)

# Initialize the official langchain-ollama integration
llm = OllamaLLM(
    base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL, temperature=0.7
)


class HypeRequest(BaseModel):
    username: str
    high_score: int = Field(..., ge=0)


@app.post("/internal/generate/hype")
async def generate_hype(request: HypeRequest):
    prompt = (
        f"You are a hyperactive, excited Esports announcer. "
        f"Write a short, thrilling, single-sentence hype message for the player '{request.username}' "
        f"who just achieved a high score of {request.high_score} in our retro-arcade grid game 'Nexus'. "
        f"Keep it under 20 words, do not use hashtags, do not use emojis, and make it punchy."
    )

    try:
        # Asynchronously invoke the LLM wrapper using langchain-ollama
        hype_message = await llm.ainvoke(prompt)
        hype_message = hype_message.strip()

        # Clean up enclosing quotes
        if hype_message.startswith('"') and hype_message.endswith('"'):
            hype_message = hype_message[1:-1]

        return {"success": True, "data": {"hype_message": hype_message}}

    except Exception:
        # Defensive Fallback: If Ollama is offline or model is missing
        return {
            "success": True,
            "data": {
                "hype_message": f"{request.username} is absolutely destroying the leaderboards with a massive score of {request.high_score}!"
            },
        }


@app.get("/health")
async def health_check():
    # Ping the local Ollama backend to report connection health to the Gateway
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(settings.OLLAMA_BASE_URL, timeout=1.0)
            ollama_status = (
                "connected" if response.status_code == 200 else "unreachable"
            )
        except Exception:
            ollama_status = "disconnected"

    return {
        "success": True,
        "service": "ai_engine",
        "status": "healthy",
        "ollama_connection_status": ollama_status,
    }
