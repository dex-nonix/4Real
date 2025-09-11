from typing import Dict, Any

from nonix_di.decorator import injectables
from nonix_di.resolve import NxInject
from nonix_daemon.decorator import daemons
from nonix_plugin.base import BasePlugin

from .controllers.lmstudio_controller import LMStudioController
from .services.lmstudio_service import LMStudioService
from .daemons.lmstudio_daemon import LMStudioDaemon


@injectables([
    LMStudioController,  # Register controller for injection
    LMStudioService      # Register service for injection
])
@daemons([
    LMStudioDaemon       # Register daemon for background management
])
class NxLMStudioPlugin(BasePlugin):
    """
    LM Studio plugin with injectable controller.

    Provides:
    - LMStudioController: Main control interface for LM Studio operations
    - LMStudioService: High-level service API for AI operations
    - LMStudioDaemon: Background process management for LM Studio

    Features:
    - Automatic path detection across platforms (Windows, macOS, Linux)
    - Background process monitoring and restart
    - OpenAI-compatible API integration
    - Model loading and management
    - Text generation and chat completion
    - Runtime configuration and environment variable support
    """

    # Inject controller and service for direct access within the plugin
    controller: LMStudioController = NxInject(LMStudioController)
    service: LMStudioService = NxInject(LMStudioService)

    async def _configure(self, config: Dict[str, Any]):
        """Plugin configuration phase - setup controller and pass config to daemon."""
        try:
            # Initialize controller with configuration
            await self.controller.initialize(config)

            # Store resolved path for daemon (will be passed during daemon creation)
            config["resolved_lmstudio_path"] = self.controller.lmstudio_path

            self.logger.info("LM Studio plugin configured successfully")
            self.logger.info(f"Using LM Studio at: {self.controller.lmstudio_path}")

        except Exception as e:
            self.logger.error(f"Failed to configure LM Studio plugin: {e}")
            raise

    async def _startup(self, config: Dict[str, Any]):
        """Plugin startup phase - daemon manager will handle daemon startup."""
        self.logger.info("LM Studio plugin startup complete")
        # Note: The daemon will be started by the daemon manager during plugin startup

    async def _shutdown(self, config: Dict[str, Any]):
        """Plugin shutdown phase - cleanup resources."""
        try:
            await self.controller.cleanup()
            self.logger.info("LM Studio plugin shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during LM Studio plugin shutdown: {e}")

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive plugin status."""
        try:
            server_status = await self.service.get_server_status()
            service_info = self.service.get_service_info()

            return {
                "plugin": {
                    "name": "lmstudio",
                    "version": "0.1.0",
                    "status": "active"
                },
                "controller": self.controller.get_status(),
                "service": service_info,
                "server": server_status
            }
        except Exception as e:
            return {
                "plugin": {
                    "name": "lmstudio",
                    "version": "0.1.0",
                    "status": "error"
                },
                "error": str(e)
            }

    async def start_lmstudio(self) -> bool:
        """Convenience method to start LM Studio."""
        return await self.service.start_service()

    async def stop_lmstudio(self) -> bool:
        """Convenience method to stop LM Studio."""
        return await self.service.stop_service()

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Convenience method for text generation."""
        result = await self.service.generate_response(prompt, **kwargs)
        return result or "Error: Failed to generate response"
