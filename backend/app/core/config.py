from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Another Worldline"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost:5432/another_worldline"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Claude API
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # Story Settings
    FREE_PULLS_PER_DAY: int = 3
    STORY_RESET_HOUR_KST: int = 0  # UTC+9 midnight

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
