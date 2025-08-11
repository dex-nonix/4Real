"""
Abstract base class for AI providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models import AIPreset, AIAnalysisResponse

class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize provider with configuration"""
        self.config = config
        self.name = config.get('name', 'unknown')
        self.enabled = config.get('enabled', True)
        self._client = None
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider client"""
        pass
    
    @abstractmethod
    async def analyze(self, preset: AIPreset, content: str, context: Optional[Dict[str, Any]] = None) -> AIAnalysisResponse:
        """Analyze content using the specified preset"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the provider connection is working"""
        pass
    
    @abstractmethod
    async def get_models(self) -> list:
        """Get available models for this provider"""
        pass
    
    def is_enabled(self) -> bool:
        """Check if provider is enabled"""
        return self.enabled
    
    def get_name(self) -> str:
        """Get provider name"""
        return self.name
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration"""
        return self.config.copy()
    
    async def close(self):
        """Close provider connections"""
        if self._client:
            try:
                # Provider-specific cleanup
                await self._cleanup()
            except Exception:
                pass
            self._client = None
    
    @abstractmethod
    async def _cleanup(self):
        """Provider-specific cleanup"""
        pass
