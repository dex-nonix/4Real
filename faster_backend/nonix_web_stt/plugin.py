from typing import Dict, Any

from nonix_di.decorator import injectables
from nonix_di.resolve import NxInject
from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from .routers.stt_router import NxSttRouter
from .services.stt_service import NxSttService


@injectables([
    NxSttService
])
@web_routers([
    NxSttRouter
])
class NxWebSttPlugin(BasePlugin):
    pass
