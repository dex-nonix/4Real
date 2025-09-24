"""
Base audio source classes and interfaces.
"""

from abc import ABC, abstractmethod
import queue
import numpy as np


class AudioSource(ABC):
    """Abstract base class for audio input sources."""

    def __init__(self):
        self.audio_queue = queue.Queue(maxsize=100)
        self._is_active = False

    @abstractmethod
    def start(self) -> None:
        """Start the audio source."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the audio source."""
        pass

    @property
    def is_active(self) -> bool:
        """Check if the audio source is active."""
        return self._is_active
