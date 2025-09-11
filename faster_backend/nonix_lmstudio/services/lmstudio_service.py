from typing import Dict, Any, Optional, List
from ..controllers.lmstudio_controller import LMStudioController


class LMStudioService:
    """
    Service layer for LM Studio operations.
    Provides high-level API for other plugins and components.
    """

    def __init__(self):
        self.controller = LMStudioController()

    async def initialize(self, config: Dict[str, Any]):
        """Initialize the service with configuration."""
        await self.controller.initialize(config)

    async def start_daemon(self) -> bool:
        """Start the LM Studio daemon process."""
        return await self.controller.start_lmstudio()

    async def stop_daemon(self) -> bool:
        """Stop the LM Studio daemon process."""
        return await self.controller.stop_lmstudio()

    async def restart_daemon(self) -> bool:
        """Restart the LM Studio daemon process."""
        stopped = await self.stop_daemon()
        if stopped:
            return await self.start_daemon()
        return False

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        models = await self.controller.get_models()
        return [
            {
                "name": model.get("id", ""),
                "size": model.get("size", 0),
                "format": model.get("format", ""),
                "quantization": model.get("quantization", ""),
                "modified": model.get("modified_at", ""),
            }
            for model in models
        ]

    async def load_model(self, model_name: str) -> bool:
        """Load a specific model."""
        return await self.controller.load_model(model_name)

    async def unload_model(self, model_name: str) -> bool:
        """Unload a specific model."""
        return await self.controller.unload_model(model_name)

    async def generate_response(self, prompt: str, model: str = None, **kwargs) -> Optional[str]:
        """Generate AI response for a given prompt."""
        return await self.controller.generate_text(prompt, model, **kwargs)

    async def chat_completion(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> Optional[str]:
        """Perform chat completion with message history."""
        # Convert messages to a single prompt for LM Studio
        conversation = ""
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                conversation += f"System: {content}\n"
            elif role == "user":
                conversation += f"User: {content}\n"
            elif role == "assistant":
                conversation += f"Assistant: {content}\n"

        conversation += "Assistant: "

        return await self.generate_response(conversation, model, **kwargs)

    async def get_server_status(self) -> Dict[str, Any]:
        """Get LM Studio server status."""
        server_info = await self.controller.get_server_info()
        controller_status = self.controller.get_status()

        return {
            "server": server_info,
            "controller": controller_status,
            "service_ready": controller_status["is_running"]
        }

    async def health_check(self) -> bool:
        """Check if LM Studio service is healthy."""
        status = await self.get_server_status()
        return status.get("service_ready", False)

    def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "name": "LM Studio Service",
            "version": "0.1.0",
            "capabilities": [
                "text_generation",
                "model_management",
                "chat_completion"
            ],
            "supported_models": ["Any model supported by LM Studio"],
            "api_version": "OpenAI-compatible"
        }
