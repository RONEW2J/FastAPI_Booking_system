from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://booking_user:booking_pass@localhost:5432/booking_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://booking_user:booking_pass@localhost:5672/"
    
    # JWT
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    
    # App settings
    app_name: str = "Booking System"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()