from typing import Dict, Any

from nonix_di.decorator import injectables
from nonix_di.resolve import NxInject
from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from nonix_daemon.manager import NxDaemonManager

from .routers.vscode_workspace_router import VscodeWorkspaceRouter
from .services.vscode_workspace_service import VscodeWorkspaceService
from .daemons.vscode_daemon import VscodeDaemon


@web_routers([
    VscodeWorkspaceRouter
])
@injectables([
    VscodeWorkspaceService
])
class NxVscodePlugin(BasePlugin):
    workspace_service: VscodeWorkspaceService = NxInject(VscodeWorkspaceService)
    daemon_manager: NxDaemonManager = NxInject(NxDaemonManager)

    async def _configure(self, config: Dict[str, Any]):
        await self.workspace_service.initialize(config)
        daemon = VscodeDaemon(config)
        self.daemon_manager.add_daemon(daemon)

    async def _shutdown(self, config: Dict[str, Any]):
        if getattr(self.workspace_service, "session", None):
            await self.workspace_service.session.close()
