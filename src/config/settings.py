from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    app_name: str = "AI Council API"
    debug: bool = False

    # Gemini Configuration
    gemini_api_key: str
    council_gemini_model: str = "gemini-2.0-flash-exp"
    dev_team_gemini_model: str = "gemini-2.0-flash-exp"

    # GitHub Publishing (Dev Team)
    github_user: Optional[str] = None
    github_token: Optional[str] = None
    git_user_email: Optional[str] = None
    git_user_name: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
