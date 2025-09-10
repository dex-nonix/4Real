import logging
from typing import Dict
from pyee import asyncio as pyee_asyncio

from .base_daemon import BaseDaemon
from .daemon_events import DaemonEvents


class DaemonManager:
    """
    Manages a collection of daemons, providing a simple interface to start,
    stop, add, and remove them. It also listens to events from the daemons.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.daemons: Dict[str, BaseDaemon] = {}
        self.emitter = pyee_asyncio.AsyncIOEventEmitter()

    def add_daemon(self, daemon: BaseDaemon):
        """
        Adds a daemon to the manager.
        """
        if daemon.name in self.daemons:
            raise ValueError(f"Daemon with name '{daemon.name}' already exists.")
        self.daemons[daemon.name] = daemon
        self._register_daemon_events(daemon)
        self.emitter.emit(DaemonEvents.DAEMON_ADDED.value, daemon)

    def remove_daemon(self, name: str):
        """
        Removes a daemon from the manager.
        """
        if name in self.daemons:
            daemon = self.daemons.pop(name)
            self.emitter.emit(DaemonEvents.DAEMON_REMOVED.value, daemon)

    def _register_daemon_events(self, daemon: BaseDaemon):
        """
        Forwards events from a daemon to the manager's emitter.
        """
        for event in DaemonEvents:
            if event not in [DaemonEvents.DAEMON_ADDED, DaemonEvents.DAEMON_REMOVED]:
                daemon.emitter.on(event.value, lambda *args, **kwargs: self.emitter.emit(event.value, *args, **kwargs))

    async def start_all(self):
        """
        Starts all managed daemons.
        """
        for daemon in self.daemons.values():
            await daemon.start()

    async def stop_all(self):
        """
        Stops all managed daemons.
        """
        for daemon in self.daemons.values():
            await daemon.stop()
