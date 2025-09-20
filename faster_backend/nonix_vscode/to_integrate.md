# @nonix_vscode Plugin - Complete Implementation Guide

## Overview
This document provides complete implementation details for the @nonix_vscode plugin that integrates VSCode/code-server instances with the nonix framework. The plugin follows the established nonix patterns for unified routers consuming specialized services.

**🏗️ ARCHITECTURE HIGHLIGHT**: Mirrors the chat router pattern - unified router consuming services that handle all business logic including process management.

## Architecture
- **Unified router pattern** like ChatRouter - consumes multiple services
- **Specialized service layer** with BaseCrudService inheritance + domain logic
- **No controllers** - services handle all business logic
- **Daemon consumes services** instead of direct database access
- **Pydantic schemas** for request/response validation

## Directory Structure
```
faster_backend/nonix_vscode/
├── plugin.json              # Plugin configuration
├── plugin.py                # Main plugin class
├── __init__.py              # Package initialization
├── models/
│   ├── __init__.py
│   └── vscode_workspace.py  # VscodeWorkspace database model
├── services/
│   ├── __init__.py
│   └── vscode_workspace_service.py    # Workspace service (CRUD + process management)
├── daemons/
│   ├── __init__.py
│   └── vscode_daemon.py     # Daemon managing code-server processes
└── routers/
    ├── __init__.py
    ├── vscode_router.py         # Main business logic router (start/stop/status)
    ├── vscode_workspace_router.py # CRUD router for workspaces
    └── vscode_schemas.py        # Pydantic schemas
```

## File Implementations

### 1. plugin.json
```json
{
  "name": "vscode",
  "version": "0.1.0",
  "class": "NxVscodePlugin",
  "dependencies": ["db"],
  "config": {}
}
```

### 2. plugin.py
```python
from nonix_di.decorator import injectables
from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from nonix_daemon.decorator import daemons
from .routers.vscode_router import VscodeRouter
from .routers.vscode_workspace_router import VscodeWorkspaceRouter
from .services.vscode_workspace_service import VscodeWorkspaceService
from .daemons.vscode_daemon import VscodeDaemon

@web_routers([
    VscodeRouter,           # Main business logic router (start/stop/status)
    VscodeWorkspaceRouter   # CRUD router for workspaces
])
@injectables([
    VscodeWorkspaceService
])
@daemons([
    VscodeDaemon
])
class NxVscodePlugin(BasePlugin):
    pass
```

### 3. __init__.py
```python
# NxVscodePlugin
```

### 4. models/__init__.py
```python
# Models for nonix_vscode plugin
```

### 5. models/vscode_workspace.py
```python
from __future__ import annotations
from sqlalchemy import Column, String, Text, Integer, Boolean, JSON, DateTime
from nonix_web_db import BaseModel

class VscodeWorkspace(BaseModel):
    """VSCode workspace database model"""
    __tablename__ = 'vscode_workspaces'

    name = Column(String(255), unique=True, nullable=False)
    workspace_path = Column(Text, nullable=False)
    port = Column(Integer, nullable=False)
    host = Column(String(255), default="localhost")  # Can be remote server
    status = Column(String(50), default="stopped")  # VscodeStatus StrEnum: IDLE, RUNNING, STOPPED, CRASHED, UNHEALTHY, UNREACHABLE
    config = Column(JSON, default={})

    # Process management settings
    auto_restart = Column(Boolean, default=True)  # Auto-restart on crash
    max_restarts = Column(Integer, default=3)     # Max restart attempts
    restart_count = Column(Integer, default=0)    # Current restart count
    last_crash = Column(String(500))              # Last crash reason
    crash_time = Column(DateTime)                 # When last crash occurred
    started_at = Column(DateTime)                 # When workspace was started

    def __repr__(self) -> str:
        return f"<VscodeWorkspace id={self.id} name={self.name!r}>"
```

### 6. services/__init__.py
```python
# Services for nonix_vscode plugin
```

### 7. services/vscode_workspace_service.py
```python
import asyncio
import logging
from typing import Dict, Any, Optional
import aiohttp

from nonix_di.resolve import NxInject
from nonix_daemon.manager import NxDaemonManager
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, BaseCrudService
from nonix_web_db import AsyncSessionLocal
from ..routers.vscode_schemas import VscodeWorkspaceCreate, VscodeWorkspaceUpdate, VscodeWorkspaceInDbModel, VscodeStatus
from ..models.vscode_workspace import VscodeWorkspace

class VscodeWorkspaceService(BaseCrudService):
    """Workspace service - handles all VSCode workspace operations (CRUD + process management)"""

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
        """Initialize service with configuration"""
        self.code_server_cmd = config.get("code_server_cmd", "code-server")

        # Initialize HTTP session for health checks
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )

        self.logger.info("VSCode workspace service initialized")

    async def start_workspace(self, workspace_id: int):
        """Start VSCode workspace - handles all logic including daemon coordination"""
        try:
            # Get workspace from database
            async with AsyncSessionLocal() as session:
                workspace = await session.get(VscodeWorkspace, workspace_id)
                if not workspace:
                    return {"success": False, "message": "Workspace not found"}

                # Get daemon and start workspace
                daemon = self.daemon_manager.daemons.get("vscode-daemon")
                if not daemon:
                    return {"success": False, "message": "VSCode daemon not found"}

                # Start the workspace through daemon
                result = await daemon.start_workspace(workspace)
                if result["success"]:
                    # Update database status
                    workspace.status = VscodeStatus.RUNNING
                    await session.commit()

                return result

        except Exception as e:
            self.logger.error(f"Failed to start workspace {workspace_id}: {e}")
            return {"success": False, "message": str(e)}

    async def stop_workspace(self, workspace_id: int):
        """Stop VSCode workspace - handles all logic including daemon coordination"""
        try:
            # Get workspace from database
            async with AsyncSessionLocal() as session:
                workspace = await session.get(VscodeWorkspace, workspace_id)
                if not workspace:
                    return {"success": False, "message": "Workspace not found"}

                # Get daemon and stop workspace
                daemon = self.daemon_manager.daemons.get("vscode-daemon")
                if not daemon:
                    return {"success": False, "message": "VSCode daemon not found"}

                # Stop the workspace through daemon
                result = await daemon.stop_workspace(workspace)
                if result["success"]:
                    # Update database status
                    workspace.status = VscodeStatus.STOPPED
                    await session.commit()

                return result

        except Exception as e:
            self.logger.error(f"Failed to stop workspace {workspace_id}: {e}")
            return {"success": False, "message": str(e)}

    async def get_workspace_status(self, workspace_id: int):
        """Get workspace health status"""
        try:
            # Get workspace from database
            async with AsyncSessionLocal() as session:
                workspace = await session.get(VscodeWorkspace, workspace_id)
                if not workspace:
                    return {"status": "error", "message": "Workspace not found"}

                if workspace.status == VscodeStatus.STOPPED:
                    return self._create_status_response(workspace)

                # Check health using host and port
                if self.session and workspace.port is not None:
                    try:
                        url = f"{workspace.host}:{workspace.port}"
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
                    # Port not assigned or session not available
                    await session.commit()
                    return self._create_status_response(workspace)

        except Exception as e:
            self.logger.error(f"Failed to get workspace status {workspace_id}: {e}")
            return {"status": "error"}

    # pyee Event Handler Methods - called by daemon events
    async def handle_process_crashed(self, workspace_id: int, exit_code: int):
        """Handle process crashed event from daemon using pyee"""
        async with AsyncSessionLocal() as session:
            workspace = await session.get(VscodeWorkspace, workspace_id)
            if workspace:
                workspace.status = VscodeStatus.CRASHED
                workspace.last_crash = f"Process exited with code {exit_code}"
                workspace.crash_time = datetime.utcnow()
                await session.commit()

    async def handle_process_restarted(self, workspace_id: int, attempt_count: int):
        """Handle process restarted event from daemon using pyee"""
        async with AsyncSessionLocal() as session:
            workspace = await session.get(VscodeWorkspace, workspace_id)
            if workspace:
                workspace.status = VscodeStatus.RUNNING
                workspace.restart_count = attempt_count
                workspace.started_at = datetime.utcnow()
                await session.commit()

    async def handle_max_restarts_exceeded(self, workspace_id: int, attempt_count: int):
        """Handle max restarts exceeded event from daemon using pyee"""
        async with AsyncSessionLocal() as session:
            workspace = await session.get(VscodeWorkspace, workspace_id)
            if workspace:
                workspace.status = VscodeStatus.CRASHED
                workspace.last_crash = f"Max restart attempts ({workspace.max_restarts}) exceeded after {attempt_count} attempts"
                workspace.crash_time = datetime.utcnow()
                await session.commit()

    async def handle_restart_failed(self, workspace_id: int, attempt_count: int, error_msg: str):
        """Handle restart failed event from daemon using pyee"""
        async with AsyncSessionLocal() as session:
            workspace = await session.get(VscodeWorkspace, workspace_id)
            if workspace:
                workspace.status = VscodeStatus.CRASHED
                workspace.last_crash = f"Restart attempt {attempt_count} failed: {error_msg}"
                workspace.crash_time = datetime.utcnow()
                await session.commit()

    async def get_workspace_by_id(self, workspace_id: int) -> Optional[VscodeWorkspace]:
        """Get workspace by ID for daemon use with pyee events"""
        async with AsyncSessionLocal() as session:
            return await session.get(VscodeWorkspace, workspace_id)

    def _create_status_response(self, workspace: VscodeWorkspace):
        """Create standardized status response"""
        return {
            "status": workspace.status,
            "host": workspace.host,
            "port": workspace.port
        }
```

### 8. daemons/__init__.py
```python
# Daemons for nonix_vscode plugin
```

### 9. daemons/vscode_daemon.py
```python
import asyncio
import subprocess
import logging
import time
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from pyee import AsyncIOEventEmitter  # Standard event library

from nonix_daemon.daemons.asyncio_daemon import NxAsyncioDaemon
from nonix_di.resolve import NxInject
from ..models.vscode_workspace import VscodeWorkspace, VscodeStatus
from ..services.vscode_workspace_service import VscodeWorkspaceService

class VscodeDaemon(NxAsyncioDaemon):
    """Daemon managing VSCode/code-server processes"""

    workspace_service: VscodeWorkspaceService = NxInject(VscodeWorkspaceService)

    def __init__(self, config: Dict[str, Any]):
        super().__init__("vscode-daemon")
        self.config = config
        self.code_server_cmd = config.get("code_server_cmd", "code-server")
        self.running_processes: Dict[int, subprocess.Popen] = {}
        self.restart_counts: Dict[int, int] = {}
        self.events = AsyncIOEventEmitter()  # pyee event emitter
        self.logger = logging.getLogger(__name__)

        # Set up event handlers using pyee
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Set up pyee event handlers"""
        # Service subscribes to daemon events
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
        """Main daemon loop - monitor VSCode processes"""
        while True:
            try:
                # Check health of all running processes
                for workspace_id, process in list(self.running_processes.items()):
                    if process.poll() is not None:  # Process died
                        await self._handle_process_death(workspace_id, process)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Daemon loop error: {e}")
                await asyncio.sleep(10)

    async def _handle_process_death(self, workspace_id: int, process: subprocess.Popen):
        """Handle process death using pyee events"""
        self.logger.warning(f"VSCode process for workspace {workspace_id} died with code {process.returncode}")

        # Clean up process
        del self.running_processes[workspace_id]

        # Emit event using pyee - service will handle via event subscription
        await self.events.emit('process_crashed', workspace_id, process.returncode)

        # Get workspace and check restart policy
        try:
            workspace = await self.workspace_service.get_workspace_by_id(workspace_id)
            if not workspace:
                return

            current_attempts = self.restart_counts.get(workspace_id, 0)

            if workspace.auto_restart and current_attempts < workspace.max_restarts:
                # Schedule restart
                delay = min(2 ** current_attempts, 300)
                asyncio.create_task(self._perform_restart(workspace, current_attempts + 1, delay))
            else:
                # Max restarts exceeded
                await self.events.emit('max_restarts_exceeded', workspace_id, current_attempts)

        except Exception as e:
            self.logger.error(f"Error handling process death: {e}")

    async def _perform_restart(self, workspace: VscodeWorkspace, attempt_count: int, delay: float):
        """Perform restart with pyee event communication"""
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
        """Start a VSCode workspace process"""
        try:
            # Check if already running
            if workspace.id in self.running_processes:
                process = self.running_processes[workspace.id]
                if process.poll() is None:  # Still running
                    host = workspace.host or "localhost"
                    return {
                        "success": True,
                        "message": f"Workspace {workspace.name} already running",
                        "url": f"http://{host}:{workspace.port}"
                    }

            # Start code-server process
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

            # Store process reference
            self.running_processes[workspace.id] = process

            # Wait for startup
            await asyncio.sleep(3)

            # Verify process is still running
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
            # Clean up if process was started
            if workspace.id in self.running_processes:
                del self.running_processes[workspace.id]
            return {
                "success": False,
                "message": str(e)
            }

    async def stop_workspace(self, workspace: VscodeWorkspace) -> Dict[str, Any]:
        """Stop a VSCode workspace process"""
        try:
            if workspace.id not in self.running_processes:
                return {
                    "success": True,
                    "message": f"Workspace {workspace.name} not running"
                }

            process = self.running_processes[workspace.id]

            # Terminate process
            if process.poll() is None:  # Still running
                self.logger.info(f"Stopping VSCode workspace: {workspace.name}")
                process.terminate()
                await asyncio.sleep(1)

                if process.poll() is None:
                    process.kill()
                    await asyncio.sleep(0.5)

            # Clean up
            del self.running_processes[workspace.id]
            self.logger.info(f"VSCode workspace {workspace.name} stopped")

            return {
                "success": True,
                "message": f"Stopped workspace {workspace.name}"
            }

        except Exception as e:
            self.logger.error(f"Failed to stop workspace {workspace.name}: {e}")
            # Clean up anyway
            if workspace.id in self.running_processes:
                del self.running_processes[workspace.id]
            return {
                "success": False,
                "message": str(e)
            }

    async def _cleanup_all_processes(self):
        """Clean up all running processes on shutdown"""
        for workspace_id, process in list(self.running_processes.items()):
            try:
                if process.poll() is None:
                    process.kill()
            except:
                pass
        self.running_processes.clear()
```

### 10. routers/__init__.py
```python
# Empty - routers imported directly in plugin.py
```

### 10. routers/vscode_router.py
```python
from fastapi import Request

from nonix_web.router.web_server_router import NxWebServerRouter
from nonix_web.router.decorators import router, route
from nonix_di.resolve import NxInject
from ..services.vscode_workspace_service import VscodeWorkspaceService

@router("/vscode", tags=["VSCode"])
class VscodeRouter(NxWebServerRouter):
    """Main VSCode business logic router - mirrors ChatRouter pattern (NO CRUD, only business operations)"""

    workspace_service: VscodeWorkspaceService = NxInject(VscodeWorkspaceService)

    # ==========================================
    # WORKSPACE MANAGEMENT ENDPOINTS (Business Logic)
    # ==========================================
    # NOTE: NO CRUD operations here - those are in VscodeWorkspaceRouter

    @route('/workspaces/{workspace_id}/start', methods=['POST'])
    async def start_workspace(self, req: Request, workspace_id: int):
        """Start VSCode workspace"""
        return await self.service_call_and_respond(
            self.workspace_service.start_workspace,
            service_args=(workspace_id,)
        )

    @route('/workspaces/{workspace_id}/stop', methods=['POST'])
    async def stop_workspace(self, req: Request, workspace_id: int):
        """Stop VSCode workspace"""
        return await self.service_call_and_respond(
            self.workspace_service.stop_workspace,
            service_args=(workspace_id,)
        )

    @route('/workspaces/{workspace_id}/status', methods=['GET'])
    async def get_workspace_status(self, req: Request, workspace_id: int):
        """Get workspace health status"""
        return await self.service_call_and_respond(
            self.workspace_service.get_workspace_status,
            service_args=(workspace_id,)
        )
```

### 11. routers/vscode_workspace_router.py
```python
from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ..services.vscode_workspace_service import VscodeWorkspaceService

@router("/vscode-workspaces", tags=["VSCode Workspaces"])
class VscodeWorkspaceRouter(NxWebServerCrudRouter):
    """VSCode Workspace CRUD router - mirrors ChatSessionRouter pattern"""

    service: VscodeWorkspaceService = NxInject(VscodeWorkspaceService)

    # CRUD endpoints are automatically generated by NxWebServerCrudRouter:
    # GET /vscode-workspaces - List workspaces
    # POST /vscode-workspaces - Create workspace
    # GET /vscode-workspaces/{id} - Get workspace
    # PUT /vscode-workspaces/{id} - Update workspace
    # DELETE /vscode-workspaces/{id} - Delete workspace
```

### 12. routers/vscode_schemas.py
```python
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class VscodeStatus(StrEnum):
    """Workspace status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    CRASHED = "crashed"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"

class VscodeWorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    workspace_path: str = Field(..., min_length=1)
    port: int = Field(..., gt=0, le=65535)
    host: Optional[str] = Field("localhost", max_length=255)  # Host without protocol
    status: VscodeStatus = Field(VscodeStatus.STOPPED)  # StrEnum with valid status values
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    auto_restart: Optional[bool] = Field(True)
    max_restarts: Optional[int] = Field(3, ge=0)

class VscodeWorkspaceCreate(VscodeWorkspaceBase):
    pass

class VscodeWorkspaceUpdate(BaseUpdateModel, base_model=VscodeWorkspaceBase):
    pass

class VscodeWorkspaceInDbModel(VscodeWorkspaceBase, BaseDbModelMixin):
    pass
```

## Endpoints

### Business Logic Endpoints (VscodeRouter)
```
POST   /vscode/workspaces/{id}/start   # Start code-server instance
POST   /vscode/workspaces/{id}/stop    # Stop code-server instance
GET    /vscode/workspaces/{id}/status  # Get health status, host and port
```

### CRUD Endpoints (VscodeWorkspaceRouter)
```
GET    /vscode-workspaces        # List all workspaces
POST   /vscode-workspaces        # Create workspace
GET    /vscode-workspaces/{id}   # Get workspace by ID
PUT    /vscode-workspaces/{id}   # Update workspace
DELETE /vscode-workspaces/{id}   # Delete workspace
```

## Configuration

### Add to settings.py
```python
settings.PLUGINS = [
    # ... existing plugins ...
    {"name": "vscode", "config": {}}
]
```

### Plugin Dependencies
- `db` - For database operations
- Inherits from BasePlugin automatically


## Implementation Notes

### 1. Process Management
- Current implementation is simplified
- In production, track PIDs in database
- Add proper process cleanup on shutdown
- Handle port conflicts

### 2. Health Monitoring
- Basic health check implemented
- Could be enhanced with more detailed checks
- Add automatic restart on failure

### 3. Security
- Currently uses `--auth none` for development
- Add proper authentication for production
- Validate workspace paths
- Add user permissions

### 4. Error Handling
- Basic error handling in place
- Add more specific error types
- Log errors properly
- Return meaningful error messages

### 5. Configuration
- Plugin config is minimal (empty)
- All configuration stored in database
- Could add global VSCode settings

## Testing

### CRUD Operations (VscodeWorkspaceRouter)
```bash
# Create workspace (host is just hostname, no protocol)
curl -X POST http://localhost:5000/vscode-workspaces \
  -H "Content-Type: application/json" \
  -d '{"name":"test","workspace_path":"/tmp","host":"localhost","port":8080}'

# List all workspaces
curl http://localhost:5000/vscode-workspaces

# Get specific workspace
curl http://localhost:5000/vscode-workspaces/1

# Update workspace
curl -X PUT http://localhost:5000/vscode-workspaces/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"updated-test","port":8081}'

# Delete workspace
curl -X DELETE http://localhost:5000/vscode-workspaces/1
```

### Business Logic Operations (VscodeRouter)
```bash
# Start workspace
curl -X POST http://localhost:5000/vscode/workspaces/1/start

# Get workspace status (shows current status, host and port)
curl http://localhost:5000/vscode/workspaces/1/status
# Response: {"status": "running", "host": "localhost", "port": 8080}

# Stop workspace
curl -X POST http://localhost:5000/vscode/workspaces/1/stop
```



## Dependencies
- code-server (system dependency)
- pyee (Python Event Emitter library for event-driven communication)

## Key Integration Points
- **Dual Router Pattern**: Mirrors chat system with separate routers for different concerns
- **VscodeRouter**: Business logic router (like `ChatRouter`) - handles start/stop/status operations
- **VscodeWorkspaceRouter**: CRUD router (like `ChatSessionRouter`) - handles basic CRUD operations
- **Single Service Architecture**: `VscodeWorkspaceService` handles all workspace operations (CRUD + process management) like `ChatSessionService`
- **No Controllers**: Business logic lives in services, not separate controller layer
- **pyee Event-Driven Communication**: Daemon uses `AsyncIOEventEmitter` to publish events, service subscribes via `@events.on()` decorators
- **Autonomous Daemon**: Makes restart decisions based on workspace configuration, publishes events for service to handle database updates
- **Event Types**: `process_crashed`, `process_restarted`, `max_restarts_exceeded`, `restart_failed`
- **Status Field as Single Source of Truth**: `status` field uses `VscodeStatus` StrEnum (idle, running, stopped, crashed, unhealthy, unreachable)
- **Separated Endpoints**: `/vscode/*` for business operations, `/vscode-workspaces/*` for CRUD

