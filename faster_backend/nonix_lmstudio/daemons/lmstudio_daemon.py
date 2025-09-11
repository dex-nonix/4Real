import asyncio
import os
import signal
import subprocess
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any

from nonix_daemon.daemons.asyncio_daemon import NxAsyncioDaemon


class LMStudioDaemon(NxAsyncioDaemon):
    """
    Daemon for managing LM Studio background process.
    Handles starting, monitoring, and stopping the LM Studio application.
    """

    def __init__(self, lmstudio_path: str, config: Dict[str, Any]):
        super().__init__("lmstudio-daemon")
        self.lmstudio_path = lmstudio_path
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.api_base_url = config["api_base_url"]
        self.api_timeout = config["api_timeout"]
        self.is_process_running = False

    async def _run(self):
        """
        Main daemon loop - monitors LM Studio process and API availability.
        """
        while True:
            try:
                # Check if process is still running
                if self.process and self.process.poll() is not None:
                    self.logger.warning("LM Studio process terminated unexpectedly")
                    self.is_process_running = False

                    # Attempt to restart
                    await self._restart_process()
                else:
                    # Process is running, check API health
                    await self._check_api_health()

                # Wait before next check
                await asyncio.sleep(5)

            except Exception as e:
                self.logger.error(f"Daemon loop error: {e}")
                await asyncio.sleep(10)

    async def _start(self):
        """Start the LM Studio process."""
        if not Path(self.lmstudio_path).exists():
            raise FileNotFoundError(f"LM Studio executable not found: {self.lmstudio_path}")

        try:
            self.logger.info(f"Starting LM Studio from: {self.lmstudio_path}")

            # Start LM Studio process
            if self._is_windows():
                # Windows specific startup
                self.process = subprocess.Popen(
                    [self.lmstudio_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                # Unix-like systems
                self.process = subprocess.Popen(
                    [self.lmstudio_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid  # Create new process group
                )

            self.is_process_running = True
            self.logger.info("LM Studio process started successfully")

            # Wait for API to be ready
            await self._wait_for_api_ready()

        except Exception as e:
            self.logger.error(f"Failed to start LM Studio process: {e}")
            raise

    async def _stop(self):
        """Stop the LM Studio process."""
        if self.process and self.is_process_running:
            try:
                self.logger.info("Stopping LM Studio process...")

                if self._is_windows():
                    # Windows - use taskkill
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(self.process.pid)],
                        capture_output=True
                    )
                else:
                    # Unix-like - send SIGTERM to process group
                    try:
                        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                        # Wait a bit, then force kill if still running
                        await asyncio.sleep(2)
                        if self.process.poll() is None:
                            os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    except ProcessLookupError:
                        # Process already terminated
                        pass

                # Wait for process to terminate
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning("LM Studio process did not terminate gracefully")
                    self.process.kill()
                    self.process.wait()

                self.is_process_running = False
                self.logger.info("LM Studio process stopped")

            except Exception as e:
                self.logger.error(f"Error stopping LM Studio process: {e}")
            finally:
                self.process = None

    async def _restart_process(self):
        """Restart the LM Studio process after unexpected termination."""
        self.logger.info("Attempting to restart LM Studio process...")

        try:
            await self._stop()  # Clean up any existing process
            await asyncio.sleep(2)  # Brief pause
            await self._start()
            self.logger.info("LM Studio process restarted successfully")
        except Exception as e:
            self.logger.error(f"Failed to restart LM Studio process: {e}")
            # Don't raise exception here to keep daemon running

    async def _wait_for_api_ready(self):
        """Wait for LM Studio API to become available."""
        timeout = self.api_timeout
        for i in range(timeout):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.api_base_url}/v1/models", timeout=5) as response:
                        if response.status == 200:
                            self.logger.info("LM Studio API is ready")
                            return
            except Exception:
                pass

            if i < timeout - 1:  # Don't sleep on last iteration
                await asyncio.sleep(1)

        raise TimeoutError(f"LM Studio API not ready within {timeout} seconds")

    async def _check_api_health(self):
        """Check if LM Studio API is responding."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/v1/models", timeout=5) as response:
                    if response.status != 200:
                        self.logger.warning(f"LM Studio API health check failed: HTTP {response.status}")

        except Exception as e:
            self.logger.warning(f"LM Studio API health check failed: {e}")

    def _is_windows(self) -> bool:
        """Check if running on Windows."""
        return os.name == 'nt'

    def get_process_info(self) -> Dict[str, Any]:
        """Get information about the running process."""
        if not self.process:
            return {"running": False}

        return {
            "running": self.is_process_running,
            "pid": self.process.pid if self.process else None,
            "returncode": self.process.returncode if self.process else None,
            "lmstudio_path": self.lmstudio_path,
            "api_url": self.api_base_url
        }
