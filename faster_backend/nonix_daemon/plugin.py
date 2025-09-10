from typing import Dict, Any, TYPE_CHECKING

from nonix_daemon.manager import NxDaemonManager
from nonix_web.plugin.base_plugin import BasePlugin, services
from nonix_di import NxInject

if TYPE_CHECKING:
    from nonix_web.server import NxWebServer


@services([
    NxDaemonManager
])
class NxDaemonPlugin(BasePlugin):
    daemon_manager: NxDaemonManager = NxInject(NxDaemonManager)

    def _startup(self, server: "NxWebServer", config: Dict[str, Any]):
        self.daemon_manager.start_all()

    def _shutdown(self, server: "NxWebServer", config: Dict[str, Any]):
        self.daemon_manager.stop_all()
