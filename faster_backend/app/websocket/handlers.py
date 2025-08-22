import json
import uuid
import logging
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from .manager import manager

logger = logging.getLogger(__name__)

async def handle_websocket(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    
    try:
        await manager.connect(websocket, client_id)
        
        await manager.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "message": "Connected to 4Real FastAPI Backend"
        }, client_id)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_message(client_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, client_id)
            except Exception as e:
                logger.error(f"Error handling message from {client_id}: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Internal server error: {str(e)}"
                }, client_id)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {client_id}")
    except Exception as e:
        logger.error(f"Unexpected error for client {client_id}: {e}")
    finally:
        manager.disconnect(client_id)

async def handle_message(client_id: str, message: Dict[str, Any]):
    message_type = message.get("type")
    
    if message_type == "join_room":
        room = message.get("room")
        if room:
            await manager.join_room(client_id, room)
    
    elif message_type == "leave_room":
        room = message.get("room")
        if room:
            await manager.leave_room(client_id, room)
    
    elif message_type == "chat_message":
        room = message.get("room")
        content = message.get("content")
        if room and content:
            await manager.broadcast_to_room({
                "type": "chat_message",
                "client_id": client_id,
                "room": room,
                "content": content,
                "timestamp": message.get("timestamp")
            }, room, exclude_client=client_id)
    
    elif message_type == "system_message":
        room = message.get("room")
        content = message.get("content")
        if room and content:
            await manager.broadcast_to_room({
                "type": "system_message",
                "room": room,
                "content": content,
                "timestamp": message.get("timestamp")
            }, room)
    
    elif message_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, client_id)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }, client_id)
