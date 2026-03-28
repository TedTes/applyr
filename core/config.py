from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cache_dir: str = Field(default=".cache/applyr", alias="CACHE_DIR")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-latest", alias="ANTHROPIC_MODEL")
    reddit_user_agent: str = Field(default="applyr-researcher-bot/0.1", alias="REDDIT_USER_AGENT")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
