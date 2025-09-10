import asyncio
import logging

from .daemon_events import DaemonEvents
from .daemon_manager import DaemonManager
from .asyncio_daemon import AsyncioDaemon
from .thread_daemon import ThreadDaemon
from .process_daemon import ProcessDaemon

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    async def main():
        manager = DaemonManager()

        # --- Event Listeners ---
        def log_event(name):
            def handler(*args, **kwargs):
                daemon_name = args[0].name if args else ''
                logging.info(f"EVENT: {name} - Daemon: {daemon_name} - Args: {args} - Kwargs: {kwargs}")
            return handler

        for event in DaemonEvents:
            manager.emitter.on(event.value, log_event(event.name))

        # --- Create and Add Daemons ---
        async_daemon = AsyncioDaemon("async-worker-1")
        thread_daemon = ThreadDaemon("thread-worker-1")
        process_daemon = ProcessDaemon("process-worker-1")

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
