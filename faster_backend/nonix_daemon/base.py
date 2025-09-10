import logging
from abc import ABC, abstractmethod
from pyee import asyncio as pyee_asyncio

from .events import NxDaemonEvents


class NxBaseDaemon(ABC):
    """
    An abstract base class for creating daemons.

    This class provides the basic structure for daemons, including event emitting
    capabilities for key lifecycle events. The public methods `start` and `stop`
    are wrappers that handle event emission and error handling, while the
    protected methods `_start` and `_stop` should be implemented by subclasses
    to contain the actual logic.
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.emitter = pyee_asyncio.AsyncIOEventEmitter()

    async def start(self):
        """
        Starts the daemon, emitting before and after start events.
        """
        try:
            self.emitter.emit(NxDaemonEvents.BEFORE_START.value, self)
            await self._start()
            self.emitter.emit(NxDaemonEvents.AFTER_START.value, self)
        except Exception as e:
            self.logger.error(f"Error starting daemon {self.name}: {e}")
            self.emitter.emit(NxDaemonEvents.ERROR.value, self, e)

    async def stop(self):
        """
        Stops the daemon, emitting before and after stop events.
        """
        try:
            self.emitter.emit(NxDaemonEvents.BEFORE_STOP.value, self)
            await self._stop()
            self.emitter.emit(NxDaemonEvents.AFTER_STOP.value, self)
        except Exception as e:
            self.logger.error(f"Error stopping daemon {self.name}: {e}")
            self.emitter.emit(NxDaemonEvents.ERROR.value, self, e)

    @abstractmethod
    async def _start(self):
        """
        The actual implementation of the daemon's start logic. This method
        should be overridden by subclasses.
        """
        ...

    @abstractmethod
    async def _stop(self):
        """
        The actual implementation of the daemon's stop logic. This method
        should be overridden by subclasses.
        """
        ...

    @abstractmethod
    async def _run(self):
        """
        The main logic of the daemon that runs in the background.
        """
        ...
