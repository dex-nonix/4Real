import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from ..config import settings

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.room_connections: Dict[str, Set[str]] = {}
        self.connection_rooms: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
        if client_id in self.connection_rooms:
            for room in self.connection_rooms[client_id]:
                if room in self.room_connections:
                    self.room_connections[room].discard(client_id)
                    if not self.room_connections[room]:
                        del self.room_connections[room]
            del self.connection_rooms[client_id]
        
        logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def join_room(self, client_id: str, room: str):
        if room not in self.room_connections:
            self.room_connections[room] = set()
        
        if client_id not in self.connection_rooms:
            self.connection_rooms[client_id] = set()
        
        self.room_connections[room].add(client_id)
        self.connection_rooms[client_id].add(room)
        
        await self.send_personal_message(
            {"type": "room_joined", "room": room}, 
            client_id
        )
        logger.info(f"Client {client_id} joined room {room}")
    
    async def leave_room(self, client_id: str, room: str):
        if room in self.room_connections:
            self.room_connections[room].discard(client_id)
            if not self.room_connections[room]:
                del self.room_connections[room]
        
        if client_id in self.connection_rooms:
            self.connection_rooms[client_id].discard(room)
            if not self.connection_rooms[client_id]:
                del self.connection_rooms[client_id]
        
        await self.send_personal_message(
            {"type": "room_left", "room": room}, 
            client_id
        )
        logger.info(f"Client {client_id} left room {room}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_room(self, message: Dict[str, Any], room: str, exclude_client: str = None):
        if room in self.room_connections:
            for client_id in self.room_connections[room]:
                if client_id != exclude_client:
                    await self.send_personal_message(message, client_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any], exclude_client: str = None):
        for client_id in self.active_connections:
            if client_id != exclude_client:
                await self.send_personal_message(message, client_id)
    
    def get_connection_count(self) -> int:
        return len(self.active_connections)
    
    def get_room_count(self, room: str) -> int:
        return len(self.room_connections.get(room, set()))

manager = ConnectionManager()
