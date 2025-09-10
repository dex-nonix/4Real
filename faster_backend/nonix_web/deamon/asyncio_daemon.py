import asyncio
from abc import ABC, abstractmethod

from .base_daemon import BaseDaemon


class AsyncioDaemon(BaseDaemon, ABC):
    """
    Abstract base class for daemons that run as asyncio tasks.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._task = None

    async def _start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run())

    async def _stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    @abstractmethod
    async def _run(self):
        """
        Abstract method to be implemented by concrete subclasses.
        """
        pass
