"""
Configuration management for Finnish NLP Toolkit
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False

    # Feature flags for advanced NLP
    USE_VOIKKO: bool = False
    USE_UDPIPE: bool = False
    USE_SPACY: bool = False
    USE_TRANSFORMERS: bool = False
    USE_REDIS: bool = False

    # Model paths
    UDPIPE_MODEL_PATH: str = "data/models/finnish-tdt-ud-2.5-191206.udpipe"
    TOXICITY_MODEL_PATH: Optional[str] = None

    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
