import asyncio
import threading

from .base_daemon import BaseDaemon


class ThreadDaemon(BaseDaemon):
    """
    A daemon that runs in a separate thread.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._thread = None
        self._stop_event = threading.Event()

    async def _start(self):
        if not self._thread:
            self._stop_event.clear()
            self._thread = threading.Thread(target=lambda: asyncio.run(self._run()))
            self._thread.start()

    async def _stop(self):
        if self._thread:
            self._stop_event.set()
            self._thread.join()
            self._thread = None

    async def _run(self):
        self.logger.info(f"ThreadDaemon '{self.name}' started.")
        while not self._stop_event.is_set():
            self.logger.info(f"ThreadDaemon '{self.name}' is running.")
            await asyncio.sleep(5)
        self.logger.info(f"ThreadDaemon '{self.name}' stopped.")
