from typing import Dict, Any
from datetime import datetime
import logging

from socketio import AsyncServer
from nonix_web.utils.di import Inject


class WebSocketService:
    """
    WebSocket service that provides send_ws_message method.
    Injects the server to enable WebSocket functionality.
    """

    # Inject the Socket.IO server instance
    sio: AsyncServer = Inject(AsyncServer)

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    async def send_ws_message(self, room: str, message: dict):
        """
        Send WebSocket message to a room.
        This is the method that services expect to have available.
        """
        try:
            event = message.get('event') if isinstance(message, dict) else None
            data = message.get('data') if isinstance(message, dict) else None
            if not event or data is None:
                self._logger.error(f"Invalid WS payload for room {room}: missing 'event' or 'data'")
                return
            await self.sio.emit(event, data, room=room)
        except Exception as e:
            self._logger.error(f"Failed to send message to room {room}: {e}")
