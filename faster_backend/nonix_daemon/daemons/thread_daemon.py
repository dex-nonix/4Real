import asyncio
from abc import ABC, abstractmethod
from threading import Thread, Event

from ..base import NxBaseDaemon


class NxThreadDaemon(NxBaseDaemon, ABC):
    """
    Abstract base class for daemons that run in a separate thread.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._thread = None
        self._stop_event = Event()

    async def _start(self):
        if not self._thread:
            self._stop_event.clear()
            self._thread = Thread(target=lambda: asyncio.run(self._run()))
            self._thread.start()

    async def _stop(self):
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            self._thread = None

    @abstractmethod
    async def _run(self):
        """
        Abstract method to be implemented by concrete subclasses.
        """
        pass
