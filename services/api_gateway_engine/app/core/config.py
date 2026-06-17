from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PLAYER_ENGINE_URL: str = "http://player_engine:8001"
    MATCH_ENGINE_URL: str = "http://match_engine:8002"
    LEADERBOARD_ENGINE_URL: str = "http://leaderboard_engine:8003"
    AI_ENGINE_URL: str = "http://ai_engine:8004"
    
    class Config:
        env_file = ".env"

settings = Settings()