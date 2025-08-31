import logging
from abc import ABC
from functools import partial
from typing import Dict, Any, TYPE_CHECKING, final, Type, List, Callable

if TYPE_CHECKING:
    from ..server import NxWebServer


def api_services(services, prefix="/api"):
    def _add_services(plugin, server, config):
        include_router = server.app.include_router
        for routed_service in services:
            include_router(routed_service.to_router(), prefix=prefix)

    return lambda cls: add_configure_callback(cls, _add_services)


class BasePlugin(ABC):
    api_services = []
    _configure_callbacks: List = None  # assigned by decorator
    _startup_callbacks: List = None  # assigned by decorator
    _shutdown_callbacks: List = None  # assigned by decorator

    def __init__(self, config: Dict[str, Any]):
        self.name: str = "Unnamed Plugin"
        self.version: str = "0.0.0"
        self.config = config
        self._logger = logging.getLogger(self.__class__.__name__)

    @final
    def configure(self, server: "NxWebServer", config: Dict[str, Any]):
        self._configure(server, config)

        for callback in self._configure_callbacks:
            callback(self, server, config)

        for routed_service in self.api_services:
            server.app.include_router(routed_service.to_router(), prefix="/api")

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


def _add_callback(cls, attr_name, callback, args, kwargs):
    callbacks = getattr(cls, attr_name, None)
    if callbacks is None:
        callbacks = []
        setattr(cls, attr_name, callbacks)
    callbacks.append(partial(callback, *(args or []), **(kwargs or {})))
    return cls


def add_configure_callback(plugin_class: Type[BasePlugin], callback: Callable, args=None, kwargs=None):
    return _add_callback(plugin_class, "_configure_callbacks", callback, args, kwargs)


def add_startup_callback(plugin_class: Type[BasePlugin], callback: Callable, args=None, kwargs=None):
    return _add_callback(plugin_class, "_startup_callbacks", callback, args, kwargs)


def add_shutdown_callback(plugin_class: Type[BasePlugin], callback: Callable, args=None, kwargs=None):
    return _add_callback(plugin_class, "_shutdown_callbacks", callback, args, kwargs)


def register_llm_tools(*tools: List[Dict[str, Any]]):
    def _(cls):
        setattr(cls, "llm_tools", tools)
        return cls

    return _
