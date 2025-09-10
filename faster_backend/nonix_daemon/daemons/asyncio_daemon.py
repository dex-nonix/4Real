
from abc import ABC, abstractmethod
from asyncio import CancelledError, create_task

from ..base import NxBaseDaemon


class NxAsyncioDaemon(NxBaseDaemon, ABC):
    """
    Abstract base class for daemons that run as asyncio tasks.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._task = None

    async def _start(self):
        if not self._task:
            self._task = create_task(self._run())

    async def _stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except CancelledError:
                pass
            self._task = None

    @abstractmethod
    async def _run(self):
        """
        Abstract method to be implemented by concrete subclasses.
        """
        pass
