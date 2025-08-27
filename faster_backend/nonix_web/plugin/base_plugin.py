import logging
from abc import ABC
from typing import Dict, Any, TYPE_CHECKING, final

if TYPE_CHECKING:
    from ..server import NxWebServer


class BasePlugin(ABC):
    api_services = []

    def __init__(self, config: Dict[str, Any]):
        self.name: str = "Unnamed Plugin"
        self.version: str = "0.0.0"
        self.config = config
        self._logger = logging.getLogger(self.__class__.__name__)

    @final
    def configure(self, server: "NxWebServer", config: Dict[str, Any]):
        """Configure app structure: middleware, routes, static files"""
        for routed_service in self.api_services:
            server.include_router(routed_service.to_router(server), prefix="/api")
        return self._configure(server, config)

    @final
    async def startup(self, server: "NxWebServer", config: Dict[str, Any]):
        """Runtime startup: database connections, async initialization"""
        return await self._startup(server, config)

    @final
    async def shutdown(self, server: "NxWebServer", config: Dict[str, Any]):
        """Cleanup: close connections, dispose resources"""
        return await self._shutdown(server, config)

    def _configure(self, server: "NxWebServer", config: Dict[str, Any]):
        """Override this method to configure your plugin"""
        pass

    async def _startup(self, server: "NxWebServer", config: Dict[str, Any]):
        """Override this method to handle startup"""
        pass

    async def _shutdown(self, server: "NxWebServer", config: Dict[str, Any]):
        """Override this method to handle shutdown"""
        pass
