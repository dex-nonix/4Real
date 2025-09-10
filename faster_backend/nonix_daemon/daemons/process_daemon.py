
from abc import ABC, abstractmethod
from asyncio import run
from multiprocessing import Process

from ..base import NxBaseDaemon


class NxProcessDaemon(NxBaseDaemon, ABC):
    """
    Abstract base class for daemons that run in a separate process.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._process = None

    async def _start(self):
        if not self._process:
            self._process = Process(target=lambda: run(self._run()))
            self._process.start()

    async def _stop(self):
        if self._process:
            self._process.terminate()
            self._process.join()
            self._process = None

    @abstractmethod
    async def _run(self):
        """
        Abstract method to be implemented by concrete subclasses.
        """
        pass
