import os
from contextlib import asynccontextmanager
from inspect import isclass
from typing import Optional, List

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi_socketio import SocketManager

from .config import settings
from .database import init_db, close_db
from .services.service_registration import ALL_SERVICES
# from .websocket import socket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup/shutdown events."""

    await init_db()
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    yield

    # Shutdown
    await close_db()


def create_nx_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    # app.socket_manager = SocketManager(app, cors_allowed_origins=settings.CORS_ORIGINS, mount_location="/ws")
    #
    app.mount("/static", StaticFiles(directory="static"), name="static")

    for service in ALL_SERVICES:
        app.include_router(service.to_router(app), prefix="/api")

    # app.include_router(health_router, prefix="/api", tags=["health"])
    # app.include_router(upload_router, prefix="/api", tags=["upload"])

    def custom_openapi(tags: Optional[List[str]] = None):
        print(f"🔍 DEBUG: custom_openapi called with tags: {tags}")
        
        # Don't cache when filtering by tags
        if tags:
            all_routes = app.routes
            print(f"🔍 DEBUG: Total routes: {len(all_routes)}")
            
            filtered_routes = []
            for route in all_routes:
                print(f"🔍 DEBUG: Route {route.path} has tags: {getattr(route, 'tags', 'NO_TAGS')}")
                if hasattr(route, 'tags') and route.tags:
                    route_tags = [str(tag).lower() for tag in route.tags]
                    print(f"🔍 DEBUG: Route {route.path} route_tags: {route_tags}")
                    if any(tag.lower() in route_tags for tag in tags):
                        filtered_routes.append(route)
                        print(f"🔍 DEBUG: Route {route.path} MATCHED!")
            all_routes = filtered_routes
            print(f"🔍 DEBUG: Filtered routes: {len(all_routes)}")
            
            return get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=all_routes,
                tags=app.openapi_tags,
                servers=app.servers,
            )
        
        # Cache only for unfiltered requests
        if not app.openapi_schema:
            app.openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
                tags=app.openapi_tags,
                servers=app.servers,
            )
        return app.openapi_schema

    app.openapi = custom_openapi

    def create_swagger_ui_html(tags: str = None):
        openapi_url = f"/openapi.json?tags={tags}" if tags else "/openapi.json"
        title_suffix = f" - {tags}" if tags else ""
        
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=f"{app.title} - API Documentation{title_suffix}",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get("/openapi.json")
    async def openapi_spec(request: Request):
        tags = request.query_params.get("tags")
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            return custom_openapi(tags=tag_list)
        return custom_openapi()

    @app.get("/docs")
    @app.get("/docs/{tags}")
    async def docs(tags: str = None):
        return create_swagger_ui_html(tags)


    @app.get("/")
    async def root():
        return {
            "message": "4Real FastAPI Backend",
            "version": "1.0.0",
            "docs": "/docs",
            "api": "/api"
        }

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"}
        )

    return app
