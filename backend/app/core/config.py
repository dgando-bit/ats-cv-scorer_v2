from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "ATS CV Scorer"
    model_name: str = "oksomu/resume-ner"
    max_file_size_mb: int = 10

    france_travail_client_id: str | None = None
    france_travail_client_secret: str | None = None
    france_travail_scope: str = "api_offresdemploiv2 o2dsoffre"

    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-20b"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()