"""
Google Gemini AI provider implementation
"""
import os
from typing import Dict, Any, Optional, List
from .base import BaseAIProvider
from ..models import AIPreset, AIAnalysisResponse

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Gemini provider"""
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.model_name = config.get('model', 'gemini-1.5-pro')
        self._client = None
        
    async def initialize(self) -> bool:
        """Initialize Gemini client"""
        if not genai:
            return False
            
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
            else:
                # Try to get from environment
                api_key = os.getenv('GOOGLE_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                else:
                    return False
            
            # Test with a simple model list
            models = genai.list_models()
            self._client = genai
            return True
        except Exception as e:
            print(f"Failed to initialize Gemini: {e}")
            return False
    
    async def analyze(self, preset: AIPreset, content: str, context: Optional[Dict[str, Any]] = None) -> AIAnalysisResponse:
        """Analyze content using Gemini"""
        if not self._client:
            return AIAnalysisResponse(
                success=False,
                content="",
                provider=self.name,
                model=preset.model,
                error="Provider not initialized"
            )
        
        try:
            # Build the prompt
            prompt = self._build_prompt(preset, content, context)
            
            # Get the model
            model = genai.GenerativeModel(preset.model)
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Extract content
            result_content = response.text if response.text else "No response generated"
            
            return AIAnalysisResponse(
                success=True,
                content=result_content,
                provider=self.name,
                model=preset.model,
                usage={"tokens": len(prompt) + len(result_content)}
            )
            
        except Exception as e:
            return AIAnalysisResponse(
                success=False,
                content="",
                provider=self.name,
                model=preset.model,
                error=str(e)
            )
    
    async def test_connection(self) -> bool:
        """Test Gemini connection"""
        if not self._client:
            return False
            
        try:
            # Try to list models
            models = genai.list_models()
            return True
        except Exception:
            return False
    
    async def get_models(self) -> List[str]:
        """Get available Gemini models"""
        if not self._client:
            return []
            
        try:
            models = genai.list_models()
            return [model.name for model in models if 'gemini' in model.name.lower()]
        except Exception:
            return ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
    
    def _build_prompt(self, preset: AIPreset, content: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the prompt for analysis"""
        prompt_parts = [preset.system_prompt]
        
        if context:
            context_str = "Context: " + ", ".join([f"{k}: {v}" for k, v in context.items()])
            prompt_parts.append(context_str)
        
        prompt_parts.append(f"Content to analyze: {content}")
        prompt_parts.append("Please provide a detailed analysis based on the above content and context.")
        
        return "\n\n".join(prompt_parts)
    
    async def _cleanup(self):
        """Cleanup Gemini resources"""
        # Gemini doesn't require explicit cleanup
        pass
