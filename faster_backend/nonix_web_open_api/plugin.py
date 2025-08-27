from typing import Dict, Any, Optional, List

from fastapi import Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from nonix_web.plugin.base_plugin import BasePlugin
from nonix_web.server import NxWebServer


class NxWebOpenApiPlugin(BasePlugin):
    openapi_schema = None

    def _configure(self, server: NxWebServer, config: Dict[str, Any]):
        openapi_route = config.get("openapi_route", "/openapi.json")
        docs_route = config.get("docs_route", "/docs")

        @server.get(openapi_route)
        async def openapi_spec(request: Request):
            tags = request.query_params.get("tags")
            if tags:
                tags = [t.strip() for t in tags.split(",")]
            return self.custom_openapi(server, tags=tags)

        @server.get(docs_route)
        @server.get(docs_route + "/{tags}")
        async def docs(tags: str = None):
            return self.create_swagger_ui_html(openapi_route, server.title, tags)

    def custom_openapi(self, server, tags: Optional[List[str]] = None):
        logger = self._logger
        logger.info(f"🔍 custom_openapi called with tags: {tags}")

        # Don't cache when filtering by tags
        if tags:
            all_routes = server.routes
            logger.debug(f"🔍 Total routes: {len(all_routes)}")

            filtered_routes = []
            for route in all_routes: # what the fuck is the plus???
                logger.debug(f"🔍 Route {route.path} has tags: {getattr(route, 'tags', 'NO_TAGS')}")
                if hasattr(route, 'tags') and route.tags:
                    route_tags = [str(tag).lower() for tag in route.tags]
                    logger.debug(f"🔍 Route {route.path} route_tags: {route_tags}")
                    if any(tag.lower() in route_tags for tag in tags):
                        filtered_routes.append(route)
                        logger.debug(f"🔍 Route {route.path} MATCHED!")
            all_routes = filtered_routes
            logger.debug(f"🔍 Filtered routes: {len(all_routes)}")

            return get_openapi(
                title=server.title,
                version=server.version,
                openapi_version=server.openapi_version,
                description=server.description,
                routes=all_routes,
                tags=server.openapi_tags,
                servers=server.servers,
            )

        if not self.openapi_schema:
            server.openapi_schema = get_openapi(
                title=server.title,
                version=server.version,
                openapi_version=server.openapi_version,
                description=server.description,
                routes=server.routes,
                tags=server.openapi_tags,
                servers=server.servers,
            )
        return self.openapi_schema

    def create_swagger_ui_html(self, file_path, title, tags: str = None):
        openapi_url = f"/{file_path}?tags={tags}" if tags else f"/{file_path}"
        title_suffix = f" - {tags}" if tags else ""

        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=f"{title} - API Documentation{title_suffix}",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        )
