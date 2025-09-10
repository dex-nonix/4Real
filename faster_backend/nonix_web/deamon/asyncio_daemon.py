import asyncio

from .base_daemon import BaseDaemon


class AsyncioDaemon(BaseDaemon):
    """
    A daemon that runs as an asyncio task.
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

    async def _run(self):
        self.logger.info(f"AsyncioDaemon '{self.name}' started.")
        try:
            while True:
                self.logger.info(f"AsyncioDaemon '{self.name}' is running.")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            self.logger.info(f"AsyncioDaemon '{self.name}' is stopping.")
