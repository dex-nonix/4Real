from fastapi import APIRouter
from .service_router.service_router import ServiceRouter

api_router = APIRouter(prefix="/api")

# Create service router instance
service_router = ServiceRouter()

__all__ = ["api_router", "service_router"]
