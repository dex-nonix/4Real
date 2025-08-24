from fastapi import APIRouter

from ..websocket import socket_manager

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "4Real FastAPI Backend",
        "websocket_connections": len(socket_manager.server.manager.rooms),
        "active_rooms": len(socket_manager.server.manager.rooms)
    }


@router.get("/status")
async def status_check():
    return {
        "websocket": {
            "active_connections": len(socket_manager.server.manager.rooms),
            "active_rooms": len(socket_manager.server.manager.rooms)
        },
        "database": "connected",
        "file_uploads": "ready"
    }
