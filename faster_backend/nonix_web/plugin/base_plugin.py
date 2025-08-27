import logging
from abc import ABC
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import NxWebServer


class BasePlugin(ABC):
    api_services = []

    def __init__(self, config: Dict[str, Any]):
        self.name: str = "Unnamed Plugin"
        self.version: str = "0.0.0"
        self.config = config
        self._logger = logging.getLogger(self.__class__.__name__)

    async def configure(self, server: "NxWebServer", config: Dict[str, Any]):
        for routed_service in self.api_services:
            server.include_router(routed_service.to_router(server), prefix="/api")

    async def startup(self, server: "NxWebServer", config: Dict[str, Any]):
        ...

    async def shutdown(self, server: "NxWebServer", config: Dict[str, Any]):
        ...
