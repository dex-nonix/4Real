"""
Configuration management for the application
"""
import os
from pathlib import Path
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_path: str = "data/music.db"
    
    # App
    app_title: str = "Nonix Mini Artist Manager"
    app_version: str = "0.1.0"
    
    # UI
    theme: str = "dark"
    sidebar_width: int = 250
    
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
