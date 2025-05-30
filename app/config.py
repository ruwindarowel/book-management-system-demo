from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXP_DELTA_SECONDS: int
    REFRESH_TOKEN_EXPIRY: int
    REDIS_HOST: str
    REDIS_PORT: int = "localhost"
    REDIS_DB: int = 6379

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env", extra="ignore"  # app/.env
    )


Config = Settings()
