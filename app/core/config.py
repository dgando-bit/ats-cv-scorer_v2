from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ATS CV Scorer"
    model_name: str = "oksomu/resume-ner"
    max_file_size_mb: int = 10

    class Config:
        env_file = ".env"


settings = Settings()