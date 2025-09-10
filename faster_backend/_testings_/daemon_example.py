"""
Nx Daemon Example with Abstract Base Classes

This example demonstrates:
1. Nx-prefixed abstract daemon base classes (NxAsyncioDaemon, NxThreadDaemon, NxProcessDaemon)
2. Example-prefixed concrete implementations that inherit from the abstract classes
3. NxDaemonManager with its own event system
4. Proper separation of daemon events vs manager events
"""

import asyncio
import logging

from nonix_daemon import NxProcessDaemon, NxThreadDaemon, NxAsyncioDaemon, NxDaemonManagerEvents, NxDaemonEvents, \
    NxDaemonManager

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Concrete implementations of abstract daemon classes
class ExampleAsyncioDaemon(NxAsyncioDaemon):
    """Concrete implementation of AsyncioDaemon."""

    async def _run(self):
        self.logger.info(f"ExampleAsyncioDaemon '{self.name}' started.")
        try:
            while True:
                self.logger.info(f"ExampleAsyncioDaemon '{self.name}' is processing data...")
                await asyncio.sleep(3)  # Process every 3 seconds
        except asyncio.CancelledError:
            self.logger.info(f"ExampleAsyncioDaemon '{self.name}' is stopping.")


class ExampleThreadDaemon(NxThreadDaemon):
    """Concrete implementation of ThreadDaemon."""

    async def _run(self):
        self.logger.info(f"ExampleThreadDaemon '{self.name}' started.")
        while not self._stop_event.is_set():
            self.logger.info(f"ExampleThreadDaemon '{self.name}' is monitoring files...")
            await asyncio.sleep(4)  # Monitor every 4 seconds
        self.logger.info(f"ExampleThreadDaemon '{self.name}' stopped.")


class ExampleProcessDaemon(NxProcessDaemon):
    """Concrete implementation of ProcessDaemon."""

    async def _run(self):
        self.logger.info(f"ExampleProcessDaemon '{self.name}' started.")
        try:
            while True:
                self.logger.info(f"ExampleProcessDaemon '{self.name}' is computing heavy tasks...")
                await asyncio.sleep(6)  # Heavy computation every 6 seconds
        except (KeyboardInterrupt, SystemExit):
            self.logger.info(f"ExampleProcessDaemon '{self.name}' is stopping.")

if __name__ == '__main__':
    async def main():
        manager = NxDaemonManager()

        # --- Event Listeners ---
        def log_daemon_event(name):
            def handler(*args, **kwargs):
                daemon_name = args[0].name if args else ''
                logging.info(f"DAEMON EVENT: {name} - Daemon: {daemon_name} - Args: {args} - Kwargs: {kwargs}")
            return handler

        def log_manager_event(name):
            def handler(*args, **kwargs):
                manager_name = args[0].__class__.__name__ if args else ''
                logging.info(f"MANAGER EVENT: {name} - Manager: {manager_name} - Args: {args} - Kwargs: {kwargs}")
            return handler

        # Listen to daemon events (forwarded from individual daemons)
        for event in NxDaemonEvents:
            manager.emitter.on(event.value, log_daemon_event(event.name))

        # Listen to manager-specific events
        for event in NxDaemonManagerEvents:
            manager.emitter.on(event.value, log_manager_event(event.name))

        # --- Create and Add Daemons ---
        async_daemon = ExampleAsyncioDaemon("async-data-processor")
        thread_daemon = ExampleThreadDaemon("thread-file-monitor")
        process_daemon = ExampleProcessDaemon("process-heavy-compute")

        manager.add_daemon(async_daemon)
        manager.add_daemon(thread_daemon)
        manager.add_daemon(process_daemon)

        # --- Start Daemons ---
        await manager.start_all()

        # --- Run for a while ---
        try:
            await asyncio.sleep(15)
        finally:
            # --- Stop Daemons ---
            await manager.stop_all()

    asyncio.run(main())
