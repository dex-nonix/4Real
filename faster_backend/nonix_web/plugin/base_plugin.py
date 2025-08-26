import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from nonix_web.server import NxWebServer


class BasePlugin(ABC):
    api_services = []

    def __init__(self, config: Dict[str, Any]):
        self.name: str = "Unnamed Plugin"
        self.version: str = "0.0.0"
        self.config = config
        self._logger = logging.getLogger(self.__class__.__name__)

    async def load_plugin(self, server: NxWebServer, config: Dict[str, Any]):
        for routed_service in self.api_services:
            server.include_router(routed_service.to_router(server), prefix="/api")
        return self._load_plugin(server, config)

    @abstractmethod
    async def _load_plugin(self, server: NxWebServer, config: Dict[str, Any]):
        self._logger.warning(f"Default _load_plugin called for {self.name}. "
                             "Consider overriding this method in your plugin.")
