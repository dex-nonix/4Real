from nonix_di.resolve import di_resolve
from nonix_plugin import add_configure_callback
from .server import NxWebServer


def web_routers(classes, prefix="/api"):
    def _add_router(plugin, config):
        ws: NxWebServer = di_resolve(NxWebServer)
        include_router = ws.app.include_router
        for router_class in classes:
            include_router(router_class.to_router(), prefix=prefix)

    return lambda cls: add_configure_callback(cls, _add_router)
