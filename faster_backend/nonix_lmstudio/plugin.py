from typing import Dict, Any

from nonix_di.decorator import injectables
from nonix_di.resolve import NxInject
from nonix_daemon.decorator import daemons
from nonix_plugin.base import BasePlugin

from .services.lmstudio_service import LMStudioService
from .daemons.lmstudio_daemon import LMStudioDaemon


@injectables([
    LMStudioService      # Register service for injection
])
@daemons([
    LMStudioDaemon       # Register daemon for background management
])
class NxLMStudioPlugin(BasePlugin):
    """LM Studio plugin - handles lifecycle management of its components."""

    service: LMStudioService = NxInject(LMStudioService)

    async def _configure(self, config: Dict[str, Any]):
        """SETUP: Initialize service with configuration."""
        try:
            await self.service.initialize(config)
            self.logger.info("LM Studio service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LM Studio service: {e}")
            raise

    async def _startup(self, config: Dict[str, Any]):
        """STARTUP: Plugin startup complete."""
        self.logger.info("LM Studio plugin startup complete")

    async def _shutdown(self, config: Dict[str, Any]):
        """TEARDOWN: Clean up service resources."""
        try:
            # Clean up controller resources
            await self.service.controller.cleanup()
            self.logger.info("LM Studio plugin shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during LM Studio plugin shutdown: {e}")
