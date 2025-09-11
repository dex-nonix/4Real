import asyncio
import logging
from typing import Dict, Any, Optional, List
import aiohttp

from nonix_di.resolve import NxInject
from nonix_daemon.manager import NxDaemonManager


class LMStudioController:
    """
    Main controller for LM Studio operations.
    Manages LM Studio process, API communication, and model lifecycle.
    """

    daemon_manager: NxDaemonManager = NxInject(NxDaemonManager)

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.lmstudio_path: Optional[str] = None
        self.api_base_url: str = ""
        self.session: Optional[aiohttp.ClientSession] = None
        self.models: List[Dict[str, Any]] = []
        self.is_running: bool = False
        self.api_timeout: int = 0

    async def initialize(self, config: Dict[str, Any]):
        """Initialize controller with configuration."""
        self.lmstudio_path = self._resolve_path(config)
        self.api_base_url = config["api_base_url"]
        self.api_timeout = config["api_timeout"]

        if not self.lmstudio_path:
            raise ValueError("LM Studio installation not found. Please check your configuration.")

        # Initialize HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.api_timeout)
        )

        self.logger.info(f"LM Studio controller initialized with path: {self.lmstudio_path}")

    async def start_lmstudio(self) -> bool:
        """Start LM Studio process through daemon."""
        try:
            daemon = self.daemon_manager.daemons.get("lmstudio-daemon")
            if not daemon:
                self.logger.error("LM Studio daemon not found in daemon manager")
                return False

            await daemon.start()
            self.is_running = True

            # Wait for API to be ready
            await self._wait_for_api()

            # Load available models
            await self._load_models()

            self.logger.info("LM Studio started and ready")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start LM Studio: {e}")
            self.is_running = False
            return False

    async def stop_lmstudio(self) -> bool:
        """Stop LM Studio process through daemon."""
        try:
            daemon = self.daemon_manager.daemons.get("lmstudio-daemon")
            if daemon:
                await daemon.stop()

            self.is_running = False
            self.logger.info("LM Studio stopped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop LM Studio: {e}")
            return False

    async def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from LM Studio API."""
        if not self.is_running or not self.session:
            return []

        try:
            async with self.session.get(f"{self.api_base_url}/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    self.logger.warning(f"Failed to get models: HTTP {response.status}")

        except Exception as e:
            self.logger.error(f"Failed to get models: {e}")

        return []

    async def load_model(self, model_name: str) -> bool:
        """Load a specific model in LM Studio."""
        if not self.is_running or not self.session:
            return False

        try:
            payload = {"model": model_name}
            async with self.session.post(
                f"{self.api_base_url}/v1/models/load",
                json=payload
            ) as response:
                if response.status == 200:
                    self.logger.info(f"Model '{model_name}' loaded successfully")
                    return True
                else:
                    self.logger.warning(f"Failed to load model '{model_name}': HTTP {response.status}")

        except Exception as e:
            self.logger.error(f"Failed to load model '{model_name}': {e}")

        return False

    async def unload_model(self, model_name: str) -> bool:
        """Unload a specific model from LM Studio."""
        if not self.is_running or not self.session:
            return False

        try:
            payload = {"model": model_name}
            async with self.session.post(
                f"{self.api_base_url}/v1/models/unload",
                json=payload
            ) as response:
                if response.status == 200:
                    self.logger.info(f"Model '{model_name}' unloaded successfully")
                    return True
                else:
                    self.logger.warning(f"Failed to unload model '{model_name}': HTTP {response.status}")

        except Exception as e:
            self.logger.error(f"Failed to unload model '{model_name}': {e}")

        return False

    async def generate_text(self, prompt: str, model: str = None, **kwargs) -> Optional[str]:
        """Generate text using the loaded model."""
        if not self.is_running or not self.session:
            return None

        try:
            payload = {
                "prompt": prompt,
                "model": model,
                "max_tokens": kwargs.get("max_tokens", 100),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
                "stop": kwargs.get("stop", []),
            }

            async with self.session.post(
                f"{self.api_base_url}/v1/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("choices", [{}])[0].get("text")
                else:
                    self.logger.warning(f"Failed to generate text: HTTP {response.status}")

        except Exception as e:
            self.logger.error(f"Failed to generate text: {e}")

        return None

    async def get_server_info(self) -> Optional[Dict[str, Any]]:
        """Get LM Studio server information."""
        if not self.is_running or not self.session:
            return None

        try:
            async with self.session.get(f"{self.api_base_url}/v1/server/info") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.warning(f"Failed to get server info: HTTP {response.status}")

        except Exception as e:
            self.logger.error(f"Failed to get server info: {e}")

        return None

    def get_status(self) -> Dict[str, Any]:
        """Get current status of LM Studio controller."""
        return {
            "is_running": self.is_running,
            "lmstudio_path": self.lmstudio_path,
            "api_base_url": self.api_base_url,
            "models_count": len(self.models),
            "models": self.models
        }

    async def _wait_for_api(self):
        """Wait for LM Studio API to be ready."""
        for i in range(self.api_timeout):
            try:
                async with self.session.get(f"{self.api_base_url}/v1/models", timeout=5) as response:
                    if response.status == 200:
                        self.logger.info("LM Studio API is ready")
                        return
            except Exception:
                pass

            if i < self.api_timeout - 1:  # Don't sleep on last iteration
                await asyncio.sleep(1)

        raise TimeoutError(f"LM Studio API not ready within {self.api_timeout} seconds")

    async def _load_models(self):
        """Load and cache available models."""
        self.models = await self.get_models()
        self.logger.info(f"Loaded {len(self.models)} models from LM Studio")

    def _resolve_path(self, config: Dict[str, Any]) -> Optional[str]:
        """Resolve LM Studio installation path from various sources."""
        import os

        # Priority: env var > config > auto-detect > fallback paths
        path = os.getenv("LMSTUDIO_PATH") or config.get("lmstudio_path")

        if path and self.path_detector.validate_path(path):
            return path

        # Auto-detect if enabled
        if config.get("auto_detect", True):
            detected = self.path_detector.find_lmstudio_path()
            if detected:
                return detected

        # Try fallback paths
        for fallback_path in config.get("fallback_paths", []):
            if self.path_detector.validate_path(fallback_path):
                return fallback_path

        return None

    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
            self.session = None

        self.models = []
        self.logger.info("LM Studio controller cleaned up")
