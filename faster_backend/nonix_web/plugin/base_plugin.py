import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from nonix_web.server import NxWebServer


class BasePlugin(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.name: str = "Unnamed Plugin"
        self.version: str = "0.0.0"
        self.config = config
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def load_plugin(self, server: NxWebServer, config: Dict[str, Any]):
        self._logger.warning(f"Default load_plugin called for {self.name}. "
                             "Consider overriding this method in your plugin.")
