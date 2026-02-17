import asyncio
from abc import ABC, abstractmethod

import numpy as np


class AudioSource(ABC):
    """
    Abstract base class for providing audio chunks.
    Defines the interface for different audio input methods like microphones or files.
    """

    def __init__(self):
        self._queue = asyncio.Queue()
        self._is_active = False

    @property
    def is_active(self) -> bool:
        """Returns True if the source is currently running."""
        return self._is_active

    async def read(self) -> np.ndarray | None:
        """
        Asynchronously reads the next available audio chunk from the source.
        Returns a NumPy array, or None if the stream is finished.
        """
        return await self._queue.get()

    @abstractmethod
    async def start(self):
        """Starts the audio source, which should begin populating the internal queue."""
        pass

    @abstractmethod
    async def stop(self):
        """Stops the audio source and signals the end by putting None into the queue."""
        pass
