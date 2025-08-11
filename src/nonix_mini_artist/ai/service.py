"""
Main AI service for managing providers and analysis
"""
import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from .models import AIPreset, AIProviderConfig, AIAnalysisRequest, AIAnalysisResponse
from .providers.base import BaseAIProvider
from .providers.gemini_provider import GeminiProvider
from .providers.vertex_provider import VertexAIProvider

class AIService:
    """Main AI service for music analysis"""
    
    def __init__(self, config_path: str = "config/ai_config.json"):
        """Initialize AI service"""
        self.config_path = Path(config_path)
        self.providers: Dict[str, BaseAIProvider] = {}
        self.presets: Dict[str, AIPreset] = {}
        self.default_provider = "gemini"
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_config()
        
        # Initialize default presets
        self._init_default_presets()
    
    def _load_config(self):
        """Load AI configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                # Load providers
                for provider_config in config.get('providers', []):
                    self._add_provider(provider_config)
                
                # Load presets
                for preset_config in config.get('presets', []):
                    preset = AIPreset(**preset_config)
                    self.presets[preset.name] = preset
                    
            except Exception as e:
                print(f"Failed to load AI config: {e}")
        
        # Initialize default providers if none exist
        if not self.providers:
            self._init_default_providers()
    
    def _save_config(self):
        """Save AI configuration to file"""
        try:
            config = {
                'providers': [
                    provider.get_config() for provider in self.providers.values()
                ],
                'presets': [
                    preset.dict() for preset in self.presets.values()
                ]
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save AI config: {e}")
    
    def _init_default_providers(self):
        """Initialize default AI providers"""
        # Try to get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY', '')
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', '')
        
        # Add Gemini provider
        gemini_config = {
            'name': 'gemini',
            'api_key': api_key,
            'enabled': bool(api_key)
        }
        self._add_provider(gemini_config)
        
        # Add Vertex AI provider if project ID is available
        if project_id:
            vertex_config = {
                'name': 'vertex',
                'project_id': project_id,
                'location': 'us-central1',
                'enabled': True
            }
            self._add_provider(vertex_config)
    
    def _init_default_presets(self):
        """Initialize default AI presets"""
        default_presets = [
            AIPreset(
                name="lyrics_analyzer",
                provider="gemini",
                model="gemini-1.5-pro",
                system_prompt="You are a music analyst specializing in dancehall and reggae music. Analyze lyrics for themes, cultural references, musical style, and provide insights about the artist's message and cultural context.",
                temperature=0.7,
                max_tokens=1000
            ),
            AIPreset(
                name="style_classifier",
                provider="gemini",
                model="gemini-1.5-pro",
                system_prompt="You are a music genre and style classifier. Analyze the given content and classify it into appropriate musical styles, genres, and subgenres. Provide confidence levels and reasoning for your classifications.",
                temperature=0.3,
                max_tokens=500
            ),
            AIPreset(
                name="content_generator",
                provider="gemini",
                model="gemini-1.5-pro",
                system_prompt="You are a music content writer. Generate engaging descriptions, artist bios, and track summaries based on the provided information. Use appropriate tone and style for the music genre.",
                temperature=0.8,
                max_tokens=800
            )
        ]
        
        for preset in default_presets:
            if preset.name not in self.presets:
                self.presets[preset.name] = preset
    
    def _add_provider(self, config: Dict[str, Any]):
        """Add a new AI provider"""
        provider_name = config.get('name', '').lower()
        
        if provider_name == 'gemini':
            provider = GeminiProvider(config)
        elif provider_name == 'vertex':
            provider = VertexAIProvider(config)
        else:
            print(f"Unknown provider: {provider_name}")
            return
        
        self.providers[provider_name] = provider
    
    async def initialize_providers(self):
        """Initialize all enabled providers"""
        for provider in self.providers.values():
            if provider.is_enabled():
                await provider.initialize()
    
    async def analyze(self, request: AIAnalysisRequest) -> AIAnalysisResponse:
        """Analyze content using AI"""
        if request.preset_name not in self.presets:
            return AIAnalysisResponse(
                success=False,
                content="",
                provider="unknown",
                model="unknown",
                error=f"Preset '{request.preset_name}' not found"
            )
        
        preset = self.presets[request.preset_name]
        provider_name = preset.provider.lower()
        
        if provider_name not in self.providers:
            return AIAnalysisResponse(
                success=False,
                content="",
                provider=provider_name,
                model=preset.model,
                error=f"Provider '{provider_name}' not available"
            )
        
        provider = self.providers[provider_name]
        if not provider.is_enabled():
            return AIAnalysisResponse(
                success=False,
                content="",
                provider=provider_name,
                model=preset.model,
                error=f"Provider '{provider_name}' is disabled"
            )
        
        return await provider.analyze(preset, request.content, request.context)
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers"""
        return [
            {
                'name': provider.get_name(),
                'enabled': provider.is_enabled(),
                'config': provider.get_config()
            }
            for provider in self.providers.values()
        ]
    
    def get_presets(self) -> List[AIPreset]:
        """Get list of available presets"""
        return list(self.presets.values())
    
    def add_preset(self, preset: AIPreset):
        """Add a new preset"""
        self.presets[preset.name] = preset
        self._save_config()
    
    def update_preset(self, name: str, **kwargs):
        """Update an existing preset"""
        if name in self.presets:
            preset = self.presets[name]
            for key, value in kwargs.items():
                if hasattr(preset, key):
                    setattr(preset, key, value)
            self._save_config()
    
    def delete_preset(self, name: str):
        """Delete a preset"""
        if name in self.presets:
            del self.presets[name]
            self._save_config()
    
    def add_provider(self, config: Dict[str, Any]):
        """Add a new provider"""
        self._add_provider(config)
        self._save_config()
    
    def update_provider(self, name: str, **kwargs):
        """Update provider configuration"""
        if name in self.providers:
            provider = self.providers[name]
            for key, value in kwargs.items():
                if hasattr(provider, key):
                    setattr(provider, key, value)
            self._save_config()
    
    async def test_provider(self, name: str) -> bool:
        """Test a provider connection"""
        if name in self.providers:
            provider = self.providers[name]
            return await provider.test_connection()
        return False
    
    async def close(self):
        """Close all provider connections"""
        for provider in self.providers.values():
            await provider.close()
