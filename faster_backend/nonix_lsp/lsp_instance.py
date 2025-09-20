import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Union

# LSP Client imports
from sansio_lsp_client import Client as SansIOLSPClient
from sansio_lsp_client import structs

# Component imports
from .components import (
    LSPFileManager,
    LSPCodeIntelligence,
    LSPNavigation,
    LSPFormatting,
    LSPRefactoring,
    LSPAdvanced
)


class LSPInstanceError(Exception):
    """Base exception for LSP instance errors"""
    pass


class LSPInstanceConnectionError(LSPInstanceError):
    """Raised when connection to LSP server fails"""
    pass


class LSPInstanceTimeoutError(LSPInstanceError):
    """Raised when LSP operation times out"""
    pass


class LSPInstance:
    """
    Language Server Protocol Instance Manager
    
    Provides a clean interface to interact with language servers through the LSP protocol.
    Handles server lifecycle, file management, and all standard LSP operations.
    
    Example:
        lsp = LSPInstance({"port": 19998, "workspace_path": "/path/to/project"})
        lsp.start()
        lsp.initialize("/path/to/project")
        # Use various methods...
        lsp.stop()
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LSP instance with configuration
        
        Args:
            config: Configuration dictionary containing:
                - port: Port for LSP server (required)
                - workspace_path: Path to workspace root (required)
                - lsp_cmd: Command to start LSP server (optional, defaults to ['pylsp'])
                - timeout: Operation timeout in seconds (optional, defaults to 30)
                - log_level: Logging level (optional, defaults to 'INFO')
        """
        self.logger = logging.getLogger(__name__)

        # Required configuration
        if 'port' not in config:
            raise ValueError("port is required in config")
        if 'workspace_path' not in config:
            raise ValueError("workspace_path is required in config")

        self.port = config['port']
        self.workspace_path = Path(config['workspace_path']).resolve()
        self.lsp_cmd = config.get('lsp_cmd', ['pylsp'])
        self.timeout = config.get('timeout', 30)
        self.log_level = config.get('log_level', 'INFO')

        # Internal state
        self.process = None
        self.lsp_client = None
        self.is_running = False
        self.is_initialized = False
        self.server_capabilities = None
        self.open_files = {}

        # Configure logging
        self.logger.setLevel(getattr(logging, self.log_level.upper()))

        # Initialize component properties
        self._file_manager = LSPFileManager(self)
        self._code_intelligence = LSPCodeIntelligence(self)
        self._navigation = LSPNavigation(self)
        self._formatting = LSPFormatting(self)
        self._refactoring = LSPRefactoring(self)
        self._advanced = LSPAdvanced(self)

    def start(self) -> None:
        """
        Start the LSP server process and establish connection

        Raises:
            LSPInstanceConnectionError: If server fails to start or connect
        """
        if self.is_running:
            self.logger.warning("LSP server is already running")
            return

        try:
            self.logger.info(f"Starting LSP server on port {self.port}")

            # Start the language server process
            self.process = subprocess.Popen(
                self.lsp_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.workspace_path
            )

            # Initialize Sans-IO LSP Client
            workspace_uri = f"file://{self.workspace_path}"
            self.lsp_client = SansIOLSPClient(
                process_id=os.getpid(),
                root_uri=workspace_uri,
                trace='off'
            )

            self.is_running = True
            self.logger.info("LSP server started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start LSP server: {e}")
            self._cleanup()
            raise LSPInstanceConnectionError(f"Failed to start LSP server: {e}") from e

    def stop(self) -> None:
        """
        Stop the LSP server and cleanup resources
        """
        if not self.is_running:
            self.logger.warning("LSP server is not running")
            return

        try:
            self.logger.info("Stopping LSP server")

            # Shutdown gracefully if initialized
            if self.is_initialized:
                self.lsp_client.shutdown()
                self.lsp_client.exit()
                self._send_pending_requests()

            # Kill process if still running
            if self.process and self.process.poll() is None:
                self.process.terminate()
                # Wait up to 5 seconds for graceful termination
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

            self.logger.info("LSP server stopped")

        except Exception as e:
            self.logger.error(f"Error during LSP server shutdown: {e}")
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """Internal cleanup of resources"""
        self.is_running = False
        self.is_initialized = False
        self.server_capabilities = None
        self.lsp_client = None
        self.open_files.clear()

        if self.process:
            try:
                if self.process.poll() is None:
                    self.process.kill()
            except Exception:
                pass  # Process might already be dead
            self.process = None

    def _send_request(self, method_name: str, *args):
        """Send a request to the LSP server"""
        if not self.lsp_client or not self.process:
            raise LSPInstanceConnectionError("LSP client not initialized")

        try:
            # Call the method on the client
            method = getattr(self.lsp_client, method_name)
            method(*args)

            # Send the request data
            data = self.lsp_client.send()
            if data:
                self.process.stdin.write(data)
                self.process.stdin.flush()

        except Exception as e:
            self.logger.error(f"Failed to send {method_name} request: {e}")
            raise LSPInstanceError(f"Request failed: {method_name} - {e}") from e

    def _read_response(self):
        """Read response data from the LSP server"""
        if not self.process:
            return None

        try:
            import select
            if select.select([self.process.stdout], [], [], 0.1)[0]:
                return self.process.stdout.read(8192)
            return None
        except Exception as e:
            self.logger.error(f"Failed to read response: {e}")
            return None

    def _make_request(self, method_name: str, *args):
        """Make a request to the LSP server and return a basic response"""
        if not self.is_initialized:
            raise LSPInstanceConnectionError("LSP server not initialized")

        try:
            self.logger.debug(f"Making LSP request: {method_name}")

            # Send the request
            self._send_request(method_name, *args)

            # Read response data
            response_data = self._read_response()

            if response_data:
                # Process the response data through the client
                events = list(self.lsp_client.recv(response_data))
                if events:
                    # Return the first event as a basic response
                    return events[0]

            return None

        except Exception as e:
            self.logger.error(f"LSP request failed: {method_name} - {e}")
            raise LSPInstanceError(f"Request failed: {method_name} - {e}") from e

    def initialize(self, workspace_path: Union[str, Path] = None) -> None:
        """
        Initialize the LSP connection with workspace

        Args:
            workspace_path: Optional path to workspace root (uses configured path if None)

        Raises:
            LSPInstanceConnectionError: If initialization fails
        """
        if not self.is_running:
            raise LSPInstanceConnectionError("LSP server is not running")

        try:
            self.logger.info("Initializing LSP connection")

            # Send initialization request
            request_id = self.lsp_client.initialize()
            self._send_pending_requests()

            # Wait for initialization response
            self._wait_for_response(request_id)

            # Mark as initialized
            self.is_initialized = True
            self.logger.info("LSP initialization completed")

        except Exception as e:
            self.logger.error(f"LSP initialization failed: {e}")
            raise LSPInstanceConnectionError(f"Initialization failed: {e}") from e

    # Component Properties

    @property
    def file(self) -> LSPFileManager:
        """Access to file operations"""
        return self._file_manager

    @property
    def code(self) -> LSPCodeIntelligence:
        """Access to code intelligence operations"""
        return self._code_intelligence

    @property
    def navigation(self) -> LSPNavigation:
        """Access to navigation operations"""
        return self._navigation

    @property
    def formatting(self) -> LSPFormatting:
        """Access to formatting operations"""
        return self._formatting

    @property
    def refactoring(self) -> LSPRefactoring:
        """Access to refactoring operations"""
        return self._refactoring

    @property
    def advanced(self) -> LSPAdvanced:
        """Access to advanced operations"""
        return self._advanced

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
