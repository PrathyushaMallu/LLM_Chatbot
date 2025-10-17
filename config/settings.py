"""
Configuration settings for the Chatbot application.
This module contains all configuration variables and settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # App Configuration
    app_name: str = "LLM Chatbot"
    version: str = "1.0.0"
    description: str = "A Streamlit + FastAPI chatbot application"
    debug: bool = False
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Streamlit Configuration
    streamlit_port: int = 8501
    streamlit_host: str = "localhost"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"  # Updated to current available model
    default_llm_provider: str = "gemini"  # "openai" or "gemini"
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # Database Configuration (for chat history)
    database_url: str = "sqlite:///./chatbot.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: list = ["http://localhost:8501", "http://127.0.0.1:8501"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/chatbot.log"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()