from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PLAYER_ENGINE_URL: str = "http://player-engine:8001"
    MATCH_ENGINE_URL: str = "http://match-engine:8002"
    LEADERBOARD_ENGINE_URL: str = "http://leaderboard-engine:8003"
    AI_ENGINE_URL: str = "http://ai-engine:8004"

    class Config:
        env_file = ".env"


settings = Settings()
