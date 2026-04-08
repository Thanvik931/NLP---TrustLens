"""
Application settings loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql://trustlens:trustlens@localhost:5433/trustlens"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # JWT
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_32_CHARS_MIN"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # Upload paths
    UPLOAD_DIR: str = "./uploads"
    MODEL_DIR: str = "./uploads/models"
    DATASET_DIR: str = "./uploads/datasets"
    REPORT_DIR: str = "./uploads/reports"

    # App
    APP_NAME: str = "TrustLens AI"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["*"]  # Flexible for production subdomains


settings = Settings()
