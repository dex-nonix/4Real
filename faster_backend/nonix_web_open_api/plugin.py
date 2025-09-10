from typing import Dict, Any, Optional, List

from fastapi import Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from nonix_di.resolve import NxInject
from nonix_plugin.base import BasePlugin
from nonix_web.server import NxWebServer


def create_swagger_ui_html(file_path, title, tags: str = None):
    openapi_url = f"{file_path}?tags={tags}" if tags else f"{file_path}"
    title_suffix = f" - {tags}" if tags else ""

    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=f"{title} - API Documentation{title_suffix}",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


class NxWebOpenApiPlugin(BasePlugin):
    openapi_schema = None
    web_server: NxWebServer = NxInject(NxWebServer)

    def _configure(self, config: Dict[str, Any]):
        openapi_route = config.get("openapi_route", "/openapi.json")
        docs_route = config.get("docs_route", "/docs")
        server = self.web_server
        @server.app.get(openapi_route, include_in_schema=False)
        async def openapi_spec(request: Request):
            tags = request.query_params.get("tags")
            if tags:
                tags = [t.strip() for t in tags.split(",")]
            return self.custom_openapi(server.app, tags=tags)

        @server.app.get(docs_route, include_in_schema=False)
        @server.app.get(docs_route + "/{tags}", include_in_schema=False)
        async def docs(tags: str = None):
            return create_swagger_ui_html(openapi_route, server.app.title, tags)

    def custom_openapi(self, fast_api, tags: Optional[List[str]] = None):

        logger = self._logger
        logger.info(f"🔍 custom_openapi called with tags: {tags}")

        # Don't cache when filtering by tags
        if tags:
            all_routes = fast_api.routes
            logger.debug(f"🔍 Total routes: {len(all_routes)}")

            filtered_routes = []
            for route in all_routes:
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
                title=fast_api.title,
                version=fast_api.version,
                openapi_version=fast_api.openapi_version,
                description=fast_api.description,
                routes=all_routes,
                tags=fast_api.openapi_tags,
                servers=fast_api.servers,
            )

        if not self.openapi_schema:
            self.openapi_schema = get_openapi(
                title=fast_api.title,
                version=fast_api.version,
                openapi_version=fast_api.openapi_version,
                description=fast_api.description,
                routes=fast_api.routes,
                tags=fast_api.openapi_tags,
                servers=fast_api.servers,
            )
        return self.openapi_schema

