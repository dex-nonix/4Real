"""
ConfigManager for managing STT configurations.
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path

from talki.core.stt_engine import STTConfig
from talki.config.logging_config import logger
from talki.utils.constants import CONFIGS_DIR


class ConfigManager:
    """Manages STT configuration files."""

    def __init__(self, config_dir: str = CONFIGS_DIR):
        """Initialize config manager."""
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, STTConfig] = {}
        self.current_config_name: Optional[str] = None

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load all configurations
        self._load_all_configs()

        # Set default if no configs exist
        if not self.configs:
            self._create_default_config()

        logger.info(f"🎛️  ConfigManager initialized with {len(self.configs)} configurations")

    def _load_all_configs(self):
        """Load all configuration files from config directory."""
        try:
            for config_file in self.config_dir.glob("*.json"):
                try:
                    config_name = config_file.stem
                    config = STTConfig.from_json(str(config_file))
                    self.configs[config_name] = config
                    logger.debug(f"📄 Loaded config: {config_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load config {config_file}: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to load configs from {self.config_dir}: {e}")

    def _create_default_config(self):
        """Create and save default configuration."""
        try:
            default_config = STTConfig(
                name="default-speech",
                version="1.0.0"
            )

            # Save to file
            config_path = self.config_dir / "default-speech.json"
            default_config.save_config(str(config_path))

            # Add to loaded configs
            self.configs["default-speech"] = default_config
            self.current_config_name = "default-speech"

            logger.info("✅ Created default configuration")
        except Exception as e:
            logger.error(f"❌ Failed to create default config: {e}")

    def get_config_names(self) -> List[str]:
        """Get list of available configuration names."""
        return list(self.configs.keys())

    def get_config(self, name: str) -> Optional[STTConfig]:
        """Get configuration by name."""
        return self.configs.get(name)

    def get_current_config(self) -> Optional[STTConfig]:
        """Get currently selected configuration."""
        if self.current_config_name:
            return self.configs.get(self.current_config_name)
        return None

    def set_current_config(self, name: str) -> bool:
        """Set the current configuration by name."""
        if name in self.configs:
            self.current_config_name = name
            logger.info(f"🔄 Switched to config: {name}")
            return True
        else:
            logger.error(f"❌ Config not found: {name}")
            return False

    def save_config(self, config: STTConfig) -> bool:
        """Save configuration to file."""
        try:
            config_path = self.config_dir / f"{config.name}.json"
            config.save_config(str(config_path))

            # Update in memory
            self.configs[config.name] = config

            logger.info(f"💾 Saved config: {config.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save config {config.name}: {e}")
            return False

    def delete_config(self, name: str) -> bool:
        """Delete configuration."""
        if name not in self.configs:
            logger.error(f"❌ Config not found: {name}")
            return False

        if name == "default-speech":
            logger.error("❌ Cannot delete default configuration")
            return False

        try:
            # Remove file
            config_path = self.config_dir / f"{name}.json"
            if config_path.exists():
                config_path.unlink()

            # Remove from memory
            del self.configs[name]

            # Switch to default if this was current
            if self.current_config_name == name:
                self.current_config_name = "default-speech"

            logger.info(f"🗑️  Deleted config: {name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete config {name}: {e}")
            return False

    def create_config(self, name: str, base_config: Optional[STTConfig] = None) -> Optional[STTConfig]:
        """Create new configuration."""
        if name in self.configs:
            logger.error(f"❌ Config already exists: {name}")
            return None

        try:
            # Create from base config or default
            if base_config:
                new_config = STTConfig.from_dict(base_config.to_dict())
            else:
                new_config = STTConfig()

            new_config.name = name

            # Save and add to memory
            if self.save_config(new_config):
                return new_config
            else:
                return None
        except Exception as e:
            logger.error(f"❌ Failed to create config {name}: {e}")
            return None

    def duplicate_config(self, source_name: str, new_name: str) -> Optional[STTConfig]:
        """Duplicate existing configuration."""
        source_config = self.get_config(source_name)
        if not source_config:
            logger.error(f"❌ Source config not found: {source_name}")
            return None

        return self.create_config(new_name, source_config)

    def get_current_config_name(self) -> Optional[str]:
        """Get name of currently selected configuration."""
        return self.current_config_name

    def reload_configs(self):
        """Reload all configurations from disk."""
        self.configs.clear()
        self._load_all_configs()

        # Ensure we have a current config
        if not self.current_config_name or self.current_config_name not in self.configs:
            self.current_config_name = "default-speech" if "default-speech" in self.configs else None

        logger.info(f"🔄 Reloaded {len(self.configs)} configurations")

    def get_config_path(self, name: str) -> Optional[Path]:
        """Get file path for configuration."""
        if name in self.configs:
            return self.config_dir / f"{name}.json"
        return None
