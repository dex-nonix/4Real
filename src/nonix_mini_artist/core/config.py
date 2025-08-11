"""
Configuration management for the application
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_path: str = "data/music.db"
    
    # App
    app_title: str = "Nonix Mini Artist Manager"
    app_version: str = "0.2.0"
    
    # UI
    theme: str = "dark"
    sidebar_width: int = 250
    
    # Google AI Configuration
    google_api_key: str = ""
    google_project_id: str = ""
    google_location: str = "us-central1"
    
    # AI Provider Settings
    default_ai_provider: str = "gemini"
    ai_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure data directory exists
def ensure_data_dir():
    """Ensure the data directory exists"""
    data_dir = Path(settings.database_path).parent
    data_dir.mkdir(parents=True, exist_ok=True)

# Initialize on import
ensure_data_dir()
