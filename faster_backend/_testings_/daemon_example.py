import asyncio
import logging

from nonix_web.deamon import ProcessDaemon, ThreadDaemon, AsyncioDaemon, DaemonManagerEvents, DaemonEvents, \
    DaemonManager

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    async def main():
        manager = DaemonManager()

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
        for event in DaemonEvents:
            manager.emitter.on(event.value, log_daemon_event(event.name))

        # Listen to manager-specific events
        for event in DaemonManagerEvents:
            manager.emitter.on(event.value, log_manager_event(event.name))

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
