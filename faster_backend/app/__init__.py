import os
from contextlib import asynccontextmanager
from inspect import isclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.health import router as health_router
from .api.upload import router as upload_router
from .config import settings
from .database import init_db, close_db
from .services.service_registration import ALL_SERVICES
from .websocket.handlers import handle_websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup/shutdown events."""

    await init_db()
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    yield

    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    for service in ALL_SERVICES:
        if not isclass(service) and  callable(service):
            router = service(app)
        else:
            router = service.to_router()

        app.include_router(router, prefix="/api")

    # app.include_router(health_router, prefix="/api", tags=["health"])
    # app.include_router(upload_router, prefix="/api", tags=["upload"])

    @app.websocket(settings.WEBSOCKET_PATH)
    async def websocket_endpoint(websocket):
        await handle_websocket(websocket)

    @app.get("/")
    async def root():
        return {
            "message": "4Real FastAPI Backend",
            "version": "1.0.0",
            "docs": "/docs",
            "websocket": settings.WEBSOCKET_PATH,
            "api": "/api"
        }

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"}
        )

    return app
