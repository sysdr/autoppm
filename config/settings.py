"""
AutoPPM Configuration Settings
Centralized configuration management for the application
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    app_name: str = Field(default="AutoPPM", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    secret_key: str = Field(env="SECRET_KEY")
    
    # Zerodha Kite Connect Configuration
    zerodha_api_key: str = Field(env="ZERODHA_API_KEY")
    zerodha_api_secret: str = Field(env="ZERODHA_API_SECRET")
    zerodha_redirect_uri: str = Field(env="ZERODHA_REDIRECT_URI")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./autoppm.db", env="DATABASE_URL")
    
    # Security Settings
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/autoppm.log", env="LOG_FILE")
    
    # CORS Settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # Session Settings
    session_timeout_minutes: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings


def validate_required_settings():
    """Validate that all required settings are present"""
    required_fields = [
        "secret_key",
        "zerodha_api_key", 
        "zerodha_api_secret",
        "jwt_secret_key"
    ]
    
    missing_fields = []
    for field in required_fields:
        if not getattr(settings, field, None):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
    
    return True
