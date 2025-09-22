from fastapi import Request
from nonix_web.router.web_server_router import NxWebServerRouter
from nonix_web.router.decorators import router, route
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ..services.vscode_workspace_service import VscodeWorkspaceService


@router("/vscode-workspaces", tags=["VSCode Workspaces"])
class VscodeWorkspaceRouter(NxWebServerCrudRouter):
    service: VscodeWorkspaceService = NxInject(VscodeWorkspaceService)

    @route('/{workspace_id}/start', methods=['POST'])
    async def start_workspace(self, req: Request, workspace_id: int):
        return await self.service_call_and_respond(
            self.service.start_workspace,
            service_args=(workspace_id,),
            response_converter=lambda r: r
        )

    @route('/{workspace_id}/stop', methods=['POST'])
    async def stop_workspace(self, req: Request, workspace_id: int):
        return await self.service_call_and_respond(
            self.service.stop_workspace,
            service_args=(workspace_id,),
            response_converter=lambda r: r
        )

    @route('/{workspace_id}/status', methods=['GET'])
    async def get_workspace_status(self, req: Request, workspace_id: int):
        return await self.service_call_and_respond(
            self.service.get_workspace_status,
            service_args=(workspace_id,),
            response_converter=lambda r: r
        )
