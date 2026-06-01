from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://bookstore_user:bookstore_pass@db:5432/bookstore_db"
    SECRET_KEY: str = "dev-secret-key-replace-in-production-at-least-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PAYMENT_MOCK_URL: str = "http://payment_mock:8001"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
