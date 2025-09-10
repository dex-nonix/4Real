import logging
from typing import Dict
from pyee import asyncio as pyee_asyncio

from .base_daemon import BaseDaemon
from .daemon_events import DaemonEvents, DaemonManagerEvents


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
        try:
            if daemon.name in self.daemons:
                raise ValueError(f"Daemon with name '{daemon.name}' already exists.")
            self.daemons[daemon.name] = daemon
            self._register_daemon_events(daemon)
            self.emitter.emit(DaemonManagerEvents.DAEMON_ADDED.value, daemon)
        except Exception as e:
            self.logger.error(f"Error adding daemon '{daemon.name}': {e}")
            self.emitter.emit(DaemonManagerEvents.MANAGER_ERROR.value, self, e)

    def remove_daemon(self, name: str):
        """
        Removes a daemon from the manager.
        """
        try:
            if name in self.daemons:
                daemon = self.daemons.pop(name)
                self.emitter.emit(DaemonManagerEvents.DAEMON_REMOVED.value, daemon)
        except Exception as e:
            self.logger.error(f"Error removing daemon '{name}': {e}")
            self.emitter.emit(DaemonManagerEvents.MANAGER_ERROR.value, self, e)

    def _register_daemon_events(self, daemon: BaseDaemon):
        """
        Forwards events from a daemon to the manager's emitter.
        """
        # Forward all daemon events to manager's emitter
        for event in DaemonEvents:
            daemon.emitter.on(event.value, lambda *args, **kwargs: self.emitter.emit(event.value, *args, **kwargs))

    async def start_all(self):
        """
        Starts all managed daemons.
        """
        try:
            self.emitter.emit(DaemonManagerEvents.BEFORE_START_ALL.value, self)
            for daemon in self.daemons.values():
                await daemon.start()
            self.emitter.emit(DaemonManagerEvents.AFTER_START_ALL.value, self)
        except Exception as e:
            self.logger.error(f"Error starting all daemons: {e}")
            self.emitter.emit(DaemonManagerEvents.MANAGER_ERROR.value, self, e)

    async def stop_all(self):
        """
        Stops all managed daemons.
        """
        try:
            self.emitter.emit(DaemonManagerEvents.BEFORE_STOP_ALL.value, self)
            for daemon in self.daemons.values():
                await daemon.stop()
            self.emitter.emit(DaemonManagerEvents.AFTER_STOP_ALL.value, self)
        except Exception as e:
            self.logger.error(f"Error stopping all daemons: {e}")
            self.emitter.emit(DaemonManagerEvents.MANAGER_ERROR.value, self, e)
