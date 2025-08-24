import re
from abc import ABC
from typing import Dict, Any, List, Callable

from app.websocket.manager import manager


class BaseService(ABC):
    """Base class for all API services with FastAPI WebSocket support."""

    def __init__(self):
        """Initialize service."""
        self._logger = None  # Will be set by subclasses
        self._service_router = None  # Will be set by ServiceRouter during registration

    def set_service_router(self, service_router):
        """Set reference to the service router for FastAPI WebSocket support - REQUIRED!"""
        if service_router is None:
            raise ValueError("Service router cannot be None - WebSocket communication requires it!")
        self._service_router = service_router

    @property
    def service_router(self):
        """Get the service router - guaranteed to be available after registration."""
        if self._service_router is None:
            raise RuntimeError("Service router not set! Call set_service_router() during registration.")
        return self._service_router

    async def send_message(self, room: str, message: dict):
        try:
            await manager.broadcast_to_room(message, room)
        except Exception as e:
            self._logger.error(f"Failed to send message to room {room}: {e}")

    def get_exposed_methods(self) -> List[Dict[str, Any]]:
        exposed_methods = []
        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, '_exposed'):
                method_info = {
                    'method': method,
                    'name': attr_name,
                    'path': getattr(method, '_path'),
                    'methods': getattr(method, '_methods', ['GET']),
                    'summary': getattr(method, '_summary'),
                    'description': getattr(method, '_description'),
                    'tags': getattr(method, '_tags', []),
                    'status_codes': getattr(method, '_status_codes', {}),
                    'request_schema': getattr(method, '_request_schema'),
                    'response_schema': getattr(method, '_response_schema')
                }
                exposed_methods.append(method_info)
        return exposed_methods





