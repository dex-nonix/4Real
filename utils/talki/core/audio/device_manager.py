"""
Audio device management and microphone enumeration.
"""

import sounddevice as sd
from typing import List, Tuple, Optional
from talki.config.logging_config import logger
from talki.utils.constants import AUDIO_DEVICE_DEFAULT_NAME


class AudioDeviceManager:
    """
    Manages audio device enumeration and selection.
    """

    def __init__(self):
        self.devices = []
        self._enumerate_devices()

    def _enumerate_devices(self):
        """Enumerate all available audio input devices."""
        try:
            logger.debug("🎤 Querying available audio devices...")
            all_devices = sd.query_devices()
            self.devices = []

            for i, device in enumerate(all_devices):
                if device['max_input_channels'] > 0:
                    logger.debug(f"📱 Found input device: {device['name']} (index: {i})")
                    self.devices.append((i, device))

        except Exception as e:
            logger.error(f"❌ Could not enumerate audio devices: {e}")
            self.devices = []

    def get_devices(self) -> List[Tuple[int, dict]]:
        """
        Get list of available input devices.

        Returns:
            List of (device_index, device_info) tuples
        """
        return self.devices.copy()

    def get_device_names(self) -> List[str]:
        """
        Get list of device names for UI display.

        Returns:
            List of device names
        """
        return [device['name'] for _, device in self.devices]

    def find_default_device_index(self) -> Optional[int]:
        """
        Find the default system microphone device index.

        Returns:
            Device index of default device, or None if not found
        """
        for device_index, device in self.devices:
            if device['name'].lower() == AUDIO_DEVICE_DEFAULT_NAME:
                logger.info(f"🎯 Found system default microphone: {device['name']}")
                return device_index
        return None

    def get_first_device_index(self) -> Optional[int]:
        """
        Get the index of the first available device.

        Returns:
            Device index of first device, or None if no devices available
        """
        if self.devices:
            return self.devices[0][0]
        return None

    def get_recommended_device_index(self) -> Optional[int]:
        """
        Get the recommended device index (default if available, otherwise first).

        Returns:
            Recommended device index, or None if no devices available
        """
        default_device = self.find_default_device_index()
        if default_device is not None:
            return default_device

        first_device = self.get_first_device_index()
        if first_device is not None:
            logger.info("✅ Using first available microphone device")
            return first_device

        logger.warning("⚠️  No microphone devices found")
        return None

    def get_device_info(self, device_index: int) -> Optional[dict]:
        """
        Get detailed information for a specific device.

        Args:
            device_index: Index of the device

        Returns:
            Device information dict, or None if not found
        """
        for idx, device in self.devices:
            if idx == device_index:
                return device.copy()
        return None

    def refresh_devices(self):
        """Refresh the device list."""
        logger.debug("🔄 Refreshing audio device list...")
        self._enumerate_devices()
