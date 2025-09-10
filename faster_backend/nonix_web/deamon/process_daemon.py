import asyncio
import multiprocessing

from .base_daemon import BaseDaemon


class ProcessDaemon(BaseDaemon):
    """
    A daemon that runs in a separate process.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._process = None

    async def _start(self):
        if not self._process:
            self._process = multiprocessing.Process(target=lambda: asyncio.run(self._run()))
            self._process.start()

    async def _stop(self):
        if self._process:
            self._process.terminate()
            self._process.join()
            self._process = None

    async def _run(self):
        self.logger.info(f"ProcessDaemon '{self.name}' started.")
        try:
            while True:
                self.logger.info(f"ProcessDaemon '{self.name}' is running.")
                await asyncio.sleep(5)
        except (KeyboardInterrupt, SystemExit):
            self.logger.info(f"ProcessDaemon '{self.name}' is stopping.")
