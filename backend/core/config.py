from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = 'AI Orchestration Platform'
    POSTGRES_URL: str = 'postgresql://postgres:postgres@db:5432/aiplatform'
    REDIS_URL: str = 'redis://redis:6379/0'
    SECRET_KEY: str = 'change_me'

settings = Settings()
