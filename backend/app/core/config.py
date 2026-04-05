from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    QDRANT_URL: str
    QDRANT_API_KEY: str
    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()