import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp

from nonix_di.resolve import NxInject
from nonix_daemon.manager import NxDaemonManager
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, BaseCrudService
from nonix_web_db import AsyncSessionLocal
from ..routers.vscode_schemas import VscodeWorkspaceCreate, VscodeWorkspaceUpdate, VscodeWorkspaceInDbModel, VscodeStatus
from ..models.vscode_workspace import VscodeWorkspace


class VscodeWorkspaceService(BaseCrudService):
    daemon_manager: NxDaemonManager = NxInject(NxDaemonManager)

    config = CRUDConfig(
        model=VscodeWorkspace,
        create_schema=VscodeWorkspaceCreate,
        update_schema=VscodeWorkspaceUpdate,
        response_schema=VscodeWorkspaceInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'status', 'port']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at', 'port']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name']
        )
    )

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.code_server_cmd: str = "code-server"
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self, config: Dict[str, Any]):
        self.code_server_cmd = config.get("code_server_cmd", "code-server")
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )

    async def start_workspace(self, workspace_id: int):
        try:
            async with AsyncSessionLocal() as session:
                workspace = await session.get(VscodeWorkspace, workspace_id)
                if not workspace:
                    return {"success": False, "message": "Workspace not found"}

                daemon = self.daemon_manager.daemons.get("vscode-daemon")
                if not daemon:
                    return {"success": False, "message": "VSCode daemon not found"}

                result = await daemon.start_workspace(workspace)
                if result["success"]:
                    workspace.status = VscodeStatus.RUNNING
                    await session.commit()

                return result

        except Exception as e:
            self.logger.error(f"Failed to start workspace {workspace_id}: {e}")
            return {"success": False, "message": str(e)}

    async def stop_workspace(self, workspace_id: int):
        try:
            async with AsyncSessionLocal() as session:
                workspace = await session.get(VscodeWorkspace, workspace_id)
                if not workspace:
                    return {"success": False, "message": "Workspace not found"}

                daemon = self.daemon_manager.daemons.get("vscode-daemon")
                if not daemon:
                    return {"success": False, "message": "VSCode daemon not found"}

                result = await daemon.stop_workspace(workspace)
                if result["success"]:
                    workspace.status = VscodeStatus.STOPPED
                    await session.commit()

                return result

        except Exception as e:
            self.logger.error(f"Failed to stop workspace {workspace_id}: {e}")
            return {"success": False, "message": str(e)}

    async def get_workspace_status(self, workspace_id: int):
        try:
            async with AsyncSessionLocal() as session:
                workspace = await session.get(VscodeWorkspace, workspace_id)
                if not workspace:
                    return {"status": "error", "message": "Workspace not found"}

                if workspace.status == VscodeStatus.STOPPED:
                    return self._create_status_response(workspace)

                if self.session and workspace.port is not None:
                    try:
                        host = workspace.host or "localhost"
                        url = f"http://{host}:{workspace.port}/"
                        async with self.session.get(url, timeout=5) as response:
                            if response.status == 200:
                                workspace.status = VscodeStatus.RUNNING
                                await session.commit()
                                return self._create_status_response(workspace)
                            else:
                                workspace.status = VscodeStatus.UNHEALTHY
                                await session.commit()
                                return self._create_status_response(workspace)
                    except:
                        workspace.status = VscodeStatus.UNREACHABLE
                        await session.commit()
                        return self._create_status_response(workspace)
                else:
                    await session.commit()
                    return self._create_status_response(workspace)

        except Exception as e:
            self.logger.error(f"Failed to get workspace status {workspace_id}: {e}")
            return {"status": "error"}

    async def handle_process_crashed(self, workspace_id: int, exit_code: int):
        async with AsyncSessionLocal() as session:
            workspace = await session.get(VscodeWorkspace, workspace_id)
            if workspace:
                workspace.status = VscodeStatus.CRASHED
                workspace.last_crash = f"Process exited with code {exit_code}"
                workspace.crash_time = datetime.utcnow()
                await session.commit()

    async def handle_process_restarted(self, workspace_id: int, attempt_count: int):
        async with AsyncSessionLocal() as session:
            workspace = await session.get(VscodeWorkspace, workspace_id)
            if workspace:
                workspace.status = VscodeStatus.RUNNING
                workspace.restart_count = attempt_count
                workspace.started_at = datetime.utcnow()
                await session.commit()

    async def handle_max_restarts_exceeded(self, workspace_id: int, attempt_count: int):
        async with AsyncSessionLocal() as session:
            workspace = await session.get(VscodeWorkspace, workspace_id)
            if workspace:
                workspace.status = VscodeStatus.CRASHED
                workspace.last_crash = f"Max restart attempts ({workspace.max_restarts}) exceeded after {attempt_count} attempts"
                workspace.crash_time = datetime.utcnow()
                await session.commit()

    async def handle_restart_failed(self, workspace_id: int, attempt_count: int, error_msg: str):
        async with AsyncSessionLocal() as session:
            workspace = await session.get(VscodeWorkspace, workspace_id)
            if workspace:
                workspace.status = VscodeStatus.CRASHED
                workspace.last_crash = f"Restart attempt {attempt_count} failed: {error_msg}"
                workspace.crash_time = datetime.utcnow()
                await session.commit()

    async def get_workspace_by_id(self, workspace_id: int) -> Optional[VscodeWorkspace]:
        async with AsyncSessionLocal() as session:
            return await session.get(VscodeWorkspace, workspace_id)

    def _create_status_response(self, workspace: VscodeWorkspace):
        return {
            "status": workspace.status,
            "host": workspace.host,
            "port": workspace.port
        }
