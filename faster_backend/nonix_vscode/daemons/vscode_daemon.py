import asyncio
import subprocess
import logging
from typing import Dict, Any
from pyee import asyncio as pyee_asyncio

from nonix_daemon.daemons.asyncio_daemon import NxAsyncioDaemon
from nonix_di.resolve import NxInject
from ..models.vscode_workspace import VscodeWorkspace
from ..services.vscode_workspace_service import VscodeWorkspaceService


class VscodeDaemon(NxAsyncioDaemon):
    workspace_service: VscodeWorkspaceService = NxInject(VscodeWorkspaceService)

    def __init__(self, config: Dict[str, Any]):
        super().__init__("vscode-daemon")
        self.config = config
        self.code_server_cmd = config.get("code_server_cmd", "code-server")
        self.running_processes: Dict[int, subprocess.Popen] = {}
        self.restart_counts: Dict[int, int] = {}
        self.events = pyee_asyncio.AsyncIOEventEmitter()
        self.logger = logging.getLogger(__name__)
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        @self.events.on('process_crashed')
        async def handle_process_crashed(workspace_id, exit_code):
            await self.workspace_service.handle_process_crashed(workspace_id, exit_code)

        @self.events.on('process_restarted')
        async def handle_process_restarted(workspace_id, attempt_count):
            await self.workspace_service.handle_process_restarted(workspace_id, attempt_count)

        @self.events.on('max_restarts_exceeded')
        async def handle_max_restarts_exceeded(workspace_id, attempt_count):
            await self.workspace_service.handle_max_restarts_exceeded(workspace_id, attempt_count)

        @self.events.on('restart_failed')
        async def handle_restart_failed(workspace_id, attempt_count, error_msg):
            await self.workspace_service.handle_restart_failed(workspace_id, attempt_count, error_msg)

    async def _run(self):
        while True:
            try:
                for workspace_id, process in list(self.running_processes.items()):
                    if process.poll() is not None:
                        await self._handle_process_death(workspace_id, process)

                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Daemon loop error: {e}")
                await asyncio.sleep(10)

    async def _handle_process_death(self, workspace_id: int, process: subprocess.Popen):
        self.logger.warning(f"VSCode process for workspace {workspace_id} died with code {process.returncode}")
        del self.running_processes[workspace_id]
        await self.events.emit('process_crashed', workspace_id, process.returncode)

        try:
            workspace = await self.workspace_service.get_workspace_by_id(workspace_id)
            if not workspace:
                return

            current_attempts = self.restart_counts.get(workspace_id, 0)

            if workspace.auto_restart and current_attempts < workspace.max_restarts:
                delay = min(2 ** current_attempts, 300)
                asyncio.create_task(self._perform_restart(workspace, current_attempts + 1, delay))
            else:
                await self.events.emit('max_restarts_exceeded', workspace_id, current_attempts)

        except Exception as e:
            self.logger.error(f"Error handling process death: {e}")

    async def _perform_restart(self, workspace: VscodeWorkspace, attempt_count: int, delay: float):
        await asyncio.sleep(delay)

        try:
            result = await self.start_workspace(workspace)

            if result["success"]:
                self.restart_counts[workspace.id] = attempt_count
                await self.events.emit('process_restarted', workspace.id, attempt_count)
            else:
                await self.events.emit('restart_failed', workspace.id, attempt_count, result.get("message", "Unknown error"))

        except Exception as e:
            self.logger.error(f"Restart error for workspace {workspace.name}: {e}")
            await self.events.emit('restart_failed', workspace.id, attempt_count, str(e))

    async def start_workspace(self, workspace: VscodeWorkspace) -> Dict[str, Any]:
        try:
            if workspace.id in self.running_processes:
                process = self.running_processes[workspace.id]
                if process.poll() is None:
                    host = workspace.host or "localhost"
                    return {
                        "success": True,
                        "message": f"Workspace {workspace.name} already running",
                        "url": f"http://{host}:{workspace.port}"
                    }

            cmd = [
                self.code_server_cmd,
                "--bind-addr", f"0.0.0.0:{workspace.port}",
                "--auth", "none",
                workspace.workspace_path
            ]

            host = workspace.host or "localhost"
            self.logger.info(f"Starting VSCode workspace: {workspace.name} on {host}:{workspace.port}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.running_processes[workspace.id] = process
            await asyncio.sleep(3)

            if process.poll() is None:
                url = f"http://{host}:{workspace.port}"
                self.logger.info(f"VSCode workspace {workspace.name} started successfully")
                return {
                    "success": True,
                    "message": f"Started workspace {workspace.name}",
                    "url": url
                }
            else:
                self.logger.error(f"VSCode process for {workspace.name} failed to start")
                return {
                    "success": False,
                    "message": "Process failed to start"
                }

        except Exception as e:
            self.logger.error(f"Failed to start workspace {workspace.name}: {e}")
            if workspace.id in self.running_processes:
                del self.running_processes[workspace.id]
            return {
                "success": False,
                "message": str(e)
            }

    async def stop_workspace(self, workspace: VscodeWorkspace) -> Dict[str, Any]:
        try:
            if workspace.id not in self.running_processes:
                return {
                    "success": True,
                    "message": f"Workspace {workspace.name} not running"
                }

            process = self.running_processes[workspace.id]

            if process.poll() is None:
                self.logger.info(f"Stopping VSCode workspace: {workspace.name}")
                process.terminate()
                await asyncio.sleep(1)

                if process.poll() is None:
                    process.kill()
                    await asyncio.sleep(0.5)

            del self.running_processes[workspace.id]
            self.logger.info(f"VSCode workspace {workspace.name} stopped")

            return {
                "success": True,
                "message": f"Stopped workspace {workspace.name}"
            }

        except Exception as e:
            self.logger.error(f"Failed to stop workspace {workspace.name}: {e}")
            if workspace.id in self.running_processes:
                del self.running_processes[workspace.id]
            return {
                "success": False,
                "message": str(e)
            }

    async def _cleanup_all_processes(self):
        for workspace_id, process in list(self.running_processes.items()):
            try:
                if process.poll() is None:
                    process.kill()
            except:
                pass
        self.running_processes.clear()
