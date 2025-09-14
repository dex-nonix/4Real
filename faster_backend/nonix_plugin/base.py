import logging
from abc import ABC
from typing import Dict, Any, final, List


class BasePlugin(ABC):
    _configure_callbacks: List = None  # assigned by decorator
    _startup_callbacks: List = None  # assigned by decorator
    _shutdown_callbacks: List = None  # assigned by decorator

    def __init__(self, config: Dict[str, Any]):
        self.name: str = "Unnamed Plugin"
        self.version: str = "0.0.0"
        self.config = config
        self._logger = logging.getLogger(self.__class__.__name__)

    @final
    def configure(self, config: Dict[str, Any]):

        if configure_callbacks := self._configure_callbacks:
            for callback in configure_callbacks:
                callback(self, config)

        self._configure(config)

    @final
    async def startup(self, config: Dict[str, Any]):
        """Runtime startup: database connections, async initialization"""
        await self._startup(config)

        if not (startup_callbacks := self._startup_callbacks):
            return

        for callback in startup_callbacks:
            await callback(self, config)

    @final
    async def shutdown(self, config: Dict[str, Any]):
        """Cleanup: close connections, dispose resources"""
        await self._shutdown(config)

        if not (shutdown_callbacks := self._shutdown_callbacks):
            return

        for callback in shutdown_callbacks:
            await callback(self, config)

    def _configure(self, config: Dict[str, Any]):
        """Override this method to configure your plugin"""
        pass

    async def _startup(self, config: Dict[str, Any]):
        """Override this method to handle startup"""
        pass

    async def _shutdown(self, config: Dict[str, Any]):
        """Override this method to handle shutdown"""
        pass
