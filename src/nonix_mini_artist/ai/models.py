"""
AI configuration models for presets and settings
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class AIPreset(BaseModel):
    """AI analysis preset configuration"""
    name: str = Field(..., description="Name of the preset")
    provider: str = Field(..., description="AI provider to use")
    model: str = Field(..., description="Model name/version")
    system_prompt: str = Field(..., description="System prompt for the AI")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="AI creativity level")
    max_tokens: int = Field(default=1000, ge=1, le=10000, description="Maximum response length")
    enabled: bool = Field(default=True, description="Whether this preset is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "lyrics_analyzer",
                "provider": "gemini",
                "model": "gemini-1.5-pro",
                "system_prompt": "You are a music analyst specializing in dancehall and reggae music. Analyze lyrics for themes, cultural references, and musical style.",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }

class AIProviderConfig(BaseModel):
    """AI provider configuration"""
    name: str = Field(..., description="Provider name")
    api_key: str = Field(..., description="API key for the provider")
    project_id: Optional[str] = Field(None, description="Google Cloud project ID")
    location: Optional[str] = Field(default="us-central1", description="Google Cloud location")
    enabled: bool = Field(default=True, description="Whether this provider is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "gemini",
                "api_key": "your-api-key-here",
                "enabled": True
            }
        }

class AIAnalysisRequest(BaseModel):
    """Request for AI analysis"""
    preset_name: str = Field(..., description="Name of the preset to use")
    content: str = Field(..., description="Content to analyze")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "preset_name": "lyrics_analyzer",
                "content": "Twelve... Di number of di beast reborn...",
                "context": {"genre": "dancehall", "artist": "TRC"}
            }
        }

class AIAnalysisResponse(BaseModel):
    """Response from AI analysis"""
    success: bool = Field(..., description="Whether the analysis was successful")
    content: str = Field(..., description="Analysis result content")
    provider: str = Field(..., description="Provider used for analysis")
    model: str = Field(..., description="Model used for analysis")
    usage: Optional[Dict[str, Any]] = Field(default=None, description="Usage statistics")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "content": "This dancehall track features strong Jamaican patois...",
                "provider": "gemini",
                "model": "gemini-1.5-pro",
                "usage": {"tokens": 150, "cost": 0.001}
            }
        }
