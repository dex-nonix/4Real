# Nonix Daemon System - Usage Guide

## Overview

The Nonix Daemon System provides a powerful background processing framework that extends your application with long-running tasks, scheduled jobs, and concurrent processing capabilities. It handles daemon lifecycle management, event-driven architecture, and multi-threading/multi-processing support automatically.

**⚠️ Important Philosophy**: Daemons are background loaders that provide continuous processing capabilities. They are registered and managed through the plugin system, following the same loader pattern where daemons expose background functionality rather than being directly injected.

## Dependencies

### Core Daemon System (Requires DI + Plugin System)
- Plugin system for daemon registration and lifecycle
- DI system for daemon manager injection
- Event system for daemon communication

### Daemon Types
- **Asyncio Daemons**: For async background tasks within the same process
- **Thread Daemons**: For CPU-bound tasks in separate threads
- **Process Daemons**: For heavy computation in separate processes

## Quick Start

### 1. Create Your First Daemon

Create a daemon class that extends one of the base daemon types:

```python
from nonix_daemon import NxAsyncioDaemon

class MyBackgroundDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("my-background-daemon")

    async def _run(self):
        while True:
            # Your background logic here
            print("Background task running...")
            await asyncio.sleep(60)  # Run every minute
```

### 2. Register Your Daemon

Use the `@daemons` decorator in a plugin to register your daemon:

```python
from nonix_daemon import daemons
from nonix_plugin import BasePlugin

@daemons([MyBackgroundDaemon])
class BackgroundPlugin(BasePlugin):
    def _configure(self, config):
        # Daemon is automatically registered with the daemon manager
        pass
```

### 3. Enable the Daemon System

Add the daemon plugin to your application:

```python
settings.PLUGINS = [
    {"name": "daemon"},  # This enables the daemon system
    {"name": "background-plugin"},  # Your plugin with daemons
    # ... other plugins
]
```

That's it! Your daemon will automatically start when the application starts and stop when it shuts down.

## Daemon Types

### Asyncio Daemon (Most Common)

Best for I/O-bound background tasks that can run concurrently:

```python
from nonix_daemon import NxAsyncioDaemon

class DataSyncDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("data-sync")

    async def _run(self):
        while True:
            try:
                # Sync data from external APIs
                await self.sync_external_data()
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Sync failed: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
```

### Thread Daemon

Best for CPU-bound tasks that would block the event loop:

```python
from nonix_daemon import NxThreadDaemon

class HeavyComputationDaemon(NxThreadDaemon):
    def __init__(self):
        super().__init__("heavy-computation")

    async def _run(self):
        while True:
            try:
                # CPU-intensive calculations
                result = self.perform_heavy_calculation()
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"Calculation failed: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes
```

### Process Daemon

Best for memory-intensive tasks or tasks requiring complete isolation:

```python
from nonix_daemon import NxProcessDaemon

class MemoryIntensiveDaemon(NxProcessDaemon):
    def __init__(self):
        super().__init__("memory-intensive")

    async def _run(self):
        while True:
            try:
                # Process large datasets
                await self.process_large_dataset()
                await asyncio.sleep(7200)  # Every 2 hours
            except Exception as e:
                self.logger.error(f"Processing failed: {e}")
                await asyncio.sleep(600)  # Retry in 10 minutes
```

## Daemon Lifecycle

### Configuration Phase
- Daemons are registered with the daemon manager
- Happens during plugin configuration

### Startup Phase
- All daemons start automatically when the daemon plugin starts
- Daemons emit `BEFORE_START` and `AFTER_START` events

### Runtime Phase
- Daemons run their `_run()` method continuously
- Event system allows communication between daemons
- Error handling prevents one daemon from crashing others

### Shutdown Phase
- All daemons stop automatically when the application shuts down
- Daemons emit `BEFORE_STOP` and `AFTER_STOP` events
- Clean shutdown prevents resource leaks

## Event System

### Daemon Events

Daemons emit events for lifecycle monitoring:

```python
from nonix_daemon import NxDaemonEvents

daemon.emitter.on(NxDaemonEvents.AFTER_START.value, lambda d: print(f"Started: {d.name}"))
daemon.emitter.on(NxDaemonEvents.ERROR.value, lambda d, e: print(f"Error in {d.name}: {e}"))
```

Available daemon events:
- `BEFORE_START`: Before daemon starts
- `AFTER_START`: After daemon starts successfully
- `BEFORE_STOP`: Before daemon stops
- `AFTER_STOP`: After daemon stops successfully
- `ERROR`: When daemon encounters an error

### Daemon Manager Events

Monitor all daemons collectively:

```python
from nonix_daemon import NxDaemonManagerEvents

daemon_manager.emitter.on(NxDaemonManagerEvents.AFTER_START_ALL.value,
                         lambda dm: print("All daemons started"))
```

Available manager events:
- `DAEMON_ADDED`: When a daemon is added
- `DAEMON_REMOVED`: When a daemon is removed
- `BEFORE_START_ALL`: Before starting all daemons
- `AFTER_START_ALL`: After all daemons start
- `BEFORE_STOP_ALL`: Before stopping all daemons
- `AFTER_STOP_ALL`: After all daemons stop
- `MANAGER_ERROR`: When manager encounters an error

## Accessing Daemon Manager

### Direct Access (Advanced Usage)

For advanced scenarios, you can access the daemon manager directly:

```python
from nonix_di.resolve import NxInject
from nonix_daemon import NxDaemonManager

class AdvancedPlugin(BasePlugin):
    daemon_manager: NxDaemonManager = NxInject(NxDaemonManager)

    def _configure(self, config):
        # Access daemon manager for advanced operations
        daemon_count = len(self.daemon_manager.daemons)
        print(f"Total daemons registered: {daemon_count}")

    async def custom_operation(self):
        # Custom daemon management logic
        await self.daemon_manager.start_all()
```

### Event-Based Communication

Use events to communicate between daemons and other parts of the application:

```python
class MonitoringDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("monitor")
        self.setup_event_listeners()

    def setup_event_listeners(self):
        # Listen to other daemon events
        from nonix_di.resolve import di_resolve
        from nonix_daemon import NxDaemonManagerEvents

        dm = di_resolve(NxDaemonManager)
        dm.emitter.on(NxDaemonManagerEvents.DAEMON_ADDED.value,
                     lambda d: print(f"New daemon: {d.name}"))

    async def _run(self):
        while True:
            # Monitor other daemons
            await asyncio.sleep(30)
```

## Common Usage Patterns

### Scheduled Task Daemon

```python
class ScheduledTaskDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("scheduler")

    async def _run(self):
        while True:
            now = datetime.now()

            # Run daily tasks at midnight
            if now.hour == 0 and now.minute == 0:
                await self.run_daily_tasks()

            # Run hourly tasks
            if now.minute == 0:
                await self.run_hourly_tasks()

            await asyncio.sleep(60)  # Check every minute
```

### Queue Processing Daemon

```python
class QueueProcessorDaemon(NxAsyncioDaemon):
    def __init__(self, queue_service):
        super().__init__("queue-processor")
        self.queue = queue_service

    async def _run(self):
        while True:
            try:
                # Process queue items
                item = await self.queue.pop()
                if item:
                    await self.process_item(item)
                else:
                    await asyncio.sleep(1)  # Queue empty, wait
            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(5)  # Back off on error
```

### Health Monitoring Daemon

```python
class HealthMonitorDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("health-monitor")

    async def _run(self):
        while True:
            try:
                # Check system health
                await self.check_database_connection()
                await self.check_external_services()
                await self.send_health_report()
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")

            await asyncio.sleep(300)  # Every 5 minutes
```

### Data Synchronization Daemon

```python
class DataSyncDaemon(NxAsyncioDaemon):
    def __init__(self, api_client, database):
        super().__init__("data-sync")
        self.api = api_client
        self.db = database

    async def _run(self):
        while True:
            try:
                # Incremental sync
                last_sync = await self.get_last_sync_time()
                new_data = await self.api.fetch_updates(since=last_sync)

                for item in new_data:
                    await self.db.save(item)

                await self.update_last_sync_time()
                await asyncio.sleep(600)  # Every 10 minutes

            except Exception as e:
                self.logger.error(f"Sync failed: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
```

## Error Handling

### Daemon-Level Error Handling

Daemons should handle their own errors gracefully:

```python
class RobustDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("robust-daemon")
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5

    async def _run(self):
        while True:
            try:
                await self.perform_operation()
                self.consecutive_failures = 0  # Reset on success
                await asyncio.sleep(60)

            except TemporaryError as e:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.max_consecutive_failures:
                    self.logger.error("Too many consecutive failures, stopping daemon")
                    break
                await asyncio.sleep(30)  # Shorter retry

            except PermanentError as e:
                self.logger.error(f"Permanent error: {e}")
                break  # Stop daemon on permanent errors

            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(300)  # Long retry for unknown errors
```

### Event-Based Error Monitoring

Monitor daemon errors across the system:

```python
from nonix_daemon import NxDaemonEvents, NxDaemonManager

class ErrorMonitor:
    def __init__(self):
        self.setup_error_monitoring()

    def setup_error_monitoring(self):
        dm = di_resolve(NxDaemonManager)

        # Listen to all daemon errors
        dm.emitter.on(NxDaemonEvents.ERROR.value,
                     lambda daemon, error: self.handle_daemon_error(daemon, error))

    def handle_daemon_error(self, daemon, error):
        self.logger.error(f"Daemon {daemon.name} error: {error}")
        # Send alerts, log to monitoring system, etc.
```

## Best Practices

### 1. Choose the Right Daemon Type

```python
# ✅ Use Asyncio for I/O-bound tasks
class ApiPollerDaemon(NxAsyncioDaemon): pass

# ✅ Use Thread for CPU-bound tasks
class ImageProcessorDaemon(NxThreadDaemon): pass

# ✅ Use Process for memory-heavy tasks
class DataAnalyzerDaemon(NxProcessDaemon): pass
```

### 2. Implement Proper Error Handling

```python
# ✅ Handle errors gracefully
async def _run(self):
    while True:
        try:
            await self.do_work()
        except Exception as e:
            self.logger.error(f"Error: {e}")
            await asyncio.sleep(60)  # Don't crash, retry
```

### 3. Use Events for Communication

```python
# ✅ Use events instead of direct coupling
class ProducerDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("producer")
        self.emitter.emit("data_ready", data)

class ConsumerDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("consumer")
        producer.emitter.on("data_ready", self.handle_data)
```

### 4. Resource Management

```python
# ✅ Clean up resources properly
class DatabaseDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("db-daemon")
        self.connection = None

    async def _start(self):
        self.connection = await create_connection()

    async def _stop(self):
        if self.connection:
            await self.connection.close()
```

### 5. Logging and Monitoring

```python
# ✅ Log important events
async def _run(self):
    self.logger.info(f"{self.name} starting work")
    # ... work ...
    self.logger.info(f"{self.name} completed work")
```

## Choosing the Right Pattern

### For Simple Background Tasks
Use **Asyncio Daemon** with basic error handling:

```python
@daemons([SimpleAsyncioDaemon])
class SimplePlugin(BasePlugin): pass
```

### For Complex Background Processing
Use **Thread/Process Daemons** with event communication:

```python
@daemons([WorkerDaemon, MonitorDaemon])
class ComplexPlugin(BasePlugin): pass
```

### For System-Level Services
Use **multiple daemon types** with comprehensive error handling:

```python
@daemons([WebScraperDaemon, DataProcessorDaemon, HealthCheckDaemon])
class SystemPlugin(BasePlugin): pass
```

## Complete Integration Example

Here's how the daemon system integrates with the plugin architecture:

```python
import asyncio
from nonix_di.decorator import injectables
from nonix_daemon import daemons, NxAsyncioDaemon, NxThreadDaemon, NxDaemonManager
from nonix_di.resolve import NxInject
from nonix_plugin import BasePlugin

# Background data processing daemon
class DataProcessorDaemon(NxThreadDaemon):
    def __init__(self):
        super().__init__("data-processor")

    async def _run(self):
        while True:
            try:
                # Process pending data in background
                await self.process_pending_data()
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Data processing error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute

# System health monitoring daemon
class SystemMonitorDaemon(NxAsyncioDaemon):
    def __init__(self):
        super().__init__("system-monitor")

    async def _run(self):
        while True:
            try:
                # Monitor system health
                await self.check_system_health()
                await asyncio.sleep(60)  # Every minute
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)  # Retry in 30 seconds

# Service that provides daemon control interface
class DaemonControlService:
    def __init__(self):
        self.daemon_manager = NxInject(NxDaemonManager)

    def get_daemon_status(self):
        """Get status of all registered daemons"""
        return {name: "running" for name in self.daemon_manager.daemons.keys()}

    async def restart_daemon(self, name: str):
        """Restart a specific daemon"""
        if name in self.daemon_manager.daemons:
            daemon = self.daemon_manager.daemons[name]
            await daemon.stop()
            await daemon.start()
            return True
        return False

# Plugin that registers daemons and services
@injectables([DaemonControlService])
@daemons([DataProcessorDaemon, SystemMonitorDaemon])
class DaemonSystemPlugin(BasePlugin):
    # Inject daemon manager for monitoring
    daemon_manager: NxDaemonManager = NxInject(NxDaemonManager)

    def _configure(self, config):
        # Daemon manager is available for monitoring
        print(f"Registered {len(self.daemon_manager.daemons)} daemons")

    async def _startup(self, config):
        print("Daemon system loaded with background processing")
        # Daemons start automatically through daemon plugin lifecycle

## Key Principles

### Daemons vs Services
- **Daemons** = Background loaders that provide continuous processing
- **Services** = Functionality that gets injected by type
- **Plugins** = Registration mechanism for both

### When to Use What
- **NxAsyncioDaemon**: Most common - async background tasks
- **NxThreadDaemon**: CPU-bound background work
- **NxProcessDaemon**: Heavy processing requiring isolation
- **Event System**: Communication between daemons and application

### The Flow
1. **Plugin loads** → Registers daemons with manager
2. **Application starts** → Daemon manager starts all daemons
3. **Daemons run** → Continuous background processing with events
4. **Application stops** → Daemon manager stops all daemons

**Remember**: Daemons are background loaders that provide continuous processing capabilities. They expose functionality through the DI system and communicate via events, not direct injection.

## Daemon Development Workflow

1. **Design** - Choose daemon type (Asyncio/Thread/Process) based on task requirements
2. **Create** - Implement daemon class with `_run()` method
3. **Register** - Use `@daemons` decorator in a plugin
4. **Configure** - Set up event listeners and error handling
5. **Test** - Verify daemon starts/stops properly and handles errors
6. **Monitor** - Use events to monitor daemon health and performance

The daemon system provides a robust foundation for background processing, allowing your application to handle continuous tasks, scheduled jobs, and concurrent processing while maintaining clean separation through the plugin architecture.
