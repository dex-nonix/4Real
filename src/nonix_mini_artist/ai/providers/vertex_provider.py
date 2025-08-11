"""
Google Vertex AI provider implementation
"""
import os
from typing import Dict, Any, Optional, List
from .base import BaseAIProvider
from ..models import AIPreset, AIAnalysisResponse

try:
    from google.cloud import aiplatform
    from vertexai.language_models import TextGenerationModel
except ImportError:
    aiplatform = None
    TextGenerationModel = None

class VertexAIProvider(BaseAIProvider):
    """Google Vertex AI provider"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Vertex AI provider"""
        super().__init__(config)
        self.project_id = config.get('project_id', '')
        self.location = config.get('location', 'us-central1')
        self._client = None
        
    async def initialize(self) -> bool:
        """Initialize Vertex AI client"""
        if not aiplatform or not TextGenerationModel:
            return False
            
        try:
            # Set project and location
            if self.project_id:
                aiplatform.init(project=self.project_id, location=self.location)
            else:
                # Try to get from environment
                project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
                if project_id:
                    aiplatform.init(project=project_id, location=self.location)
                else:
                    return False
            
            self._client = aiplatform
            return True
        except Exception as e:
            print(f"Failed to initialize Vertex AI: {e}")
            return False
    
    async def analyze(self, preset: AIPreset, content: str, context: Optional[Dict[str, Any]] = None) -> AIAnalysisResponse:
        """Analyze content using Vertex AI"""
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
            model = TextGenerationModel.from_pretrained(preset.model)
            
            # Generate response
            response = model.predict(
                prompt,
                temperature=preset.temperature,
                max_output_tokens=preset.max_tokens
            )
            
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
        """Test Vertex AI connection"""
        if not self._client:
            return False
            
        try:
            # Try to list models
            models = aiplatform.Model.list()
            return True
        except Exception:
            return False
    
    async def get_models(self) -> List[str]:
        """Get available Vertex AI models"""
        if not self._client:
            return []
            
        try:
            models = aiplatform.Model.list()
            return [model.display_name for model in models if 'text' in model.display_name.lower()]
        except Exception:
            return ['text-bison', 'text-unicorn', 'chat-bison']
    
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
        """Cleanup Vertex AI resources"""
        # Vertex AI doesn't require explicit cleanup
        pass
