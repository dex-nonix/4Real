from fastapi import APIRouter

from ..websocket import manager

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "4Real FastAPI Backend",
        "websocket_connections": manager.get_connection_count(),
        "active_rooms": len(manager.room_connections)
    }


@router.get("/status")
async def status_check():
    return {
        "websocket": {
            "active_connections": manager.get_connection_count(),
            "active_rooms": len(manager.room_connections)
        },
        "database": "connected",
        "file_uploads": "ready"
    }
