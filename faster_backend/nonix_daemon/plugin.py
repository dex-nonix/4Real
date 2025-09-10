from typing import Dict, Any

from nonix_di import NxInject, injectables
from nonix_plugin import BasePlugin
from .manager import NxDaemonManager


@injectables([
    NxDaemonManager
])
class NxDaemonPlugin(BasePlugin):
    daemon_manager: NxDaemonManager = NxInject(NxDaemonManager)

    def _startup(self, config: Dict[str, Any]):
        self.daemon_manager.start_all()

    def _shutdown(self, config: Dict[str, Any]):
        self.daemon_manager.stop_all()
