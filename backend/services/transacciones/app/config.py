from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT (Nombres corregidos para coincidir con docker-compose)
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # RabbitMQ (Default corregido al nombre del servicio)
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/" 
    
    # App
    APP_NAME: str = "Transaccion Service"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()