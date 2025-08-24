"""
Async Task Manager for FastAPI Chat Service
Provides production-grade async task management for message processing.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable, Any, Dict, List


@dataclass
class TaskStats:
    """Task statistics for monitoring."""
    active_tasks: int
    max_concurrent_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_submissions: int
    last_activity: datetime


class ChatTaskManager:
    """
    Production-grade async task manager for FastAPI chat service.
    
    Features:
    - Async task execution with configurable concurrency limits
    - Task tracking and monitoring
    - Health monitoring and metrics
    - Graceful shutdown procedures
    - Comprehensive error handling
    """
    def __init__(
            self,
            max_concurrent_tasks: int = 20,
            monitoring_interval: int = 30
    ):

        self._max_concurrent_tasks = max_concurrent_tasks
        self._monitoring_interval = monitoring_interval

        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._active_tasks: List[asyncio.Task] = []
        self._completed_tasks = 0
        self._failed_tasks = 0
        self._total_submissions = 0
        self._last_activity = datetime.utcnow()
        self._shutdown_event = asyncio.Event()
        self._logger = logging.getLogger(__name__)
        self._monitor_task = asyncio.create_task(self._monitor_tasks())
        self._logger.debug(f"ChatTaskManager initialized with {max_concurrent_tasks} max concurrent tasks")

    async def submit_task(self, func: Callable, *args, **kwargs) -> asyncio.Task:
        """
        Submit a task for async execution.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Task object representing the execution
            
        Raises:
            RuntimeError: If task manager is shutdown
        """
        if self._shutdown_event.is_set():
            error_msg = "Task manager is shutdown"
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            # Create and start the task
            task = asyncio.create_task(self._execute_task(func, *args, **kwargs))

            # Track task
            self._active_tasks.append(task)
            self._total_submissions += 1
            self._last_activity = datetime.utcnow()

            # Add completion callback
            task.add_done_callback(self._task_completed_callback)

            # Log successful submission
            func_name = getattr(func, '__name__', str(func))
            self._logger.info(f"Task submitted successfully: {func_name} (args: {len(args)}, kwargs: {len(kwargs)})")
            return task

        except Exception as e:
            func_name = getattr(func, '__name__', str(func))
            self._logger.error(f"Failed to submit task {func_name}: {type(e).__name__}: {e}", exc_info=True)
            raise

    async def _execute_task(self, func: Callable, *args, **kwargs):
        """Execute a task with concurrency control."""
        async with self._semaphore:
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    # Run sync functions in executor
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, func, *args, **kwargs)
                return result
            except Exception as e:
                self._logger.error(f"Task execution failed: {e}", exc_info=True)
                raise

    def _task_completed_callback(self, task: asyncio.Task):
        """Callback executed when a task completes."""
        try:
            # Remove from active tasks
            if task in self._active_tasks:
                self._active_tasks.remove(task)

            self._completed_tasks += 1
            self._last_activity = datetime.utcnow()

            # Check for exceptions
            if task.exception():
                self._failed_tasks += 1
                exc = task.exception()
                self._logger.error(f"Task failed with exception: {type(exc).__name__}: {exc}", exc_info=True)
            else:
                self._logger.debug("Task completed successfully")

        except Exception as e:
            self._logger.error(f"Critical error in task completion callback: {e}", exc_info=True)

    async def _monitor_tasks(self):
        """Monitor task health and performance."""
        while not self._shutdown_event.is_set():
            try:
                # Get current stats
                stats = self.get_stats()

                # Log metrics
                self._logger.debug(f"Task monitoring - Active: {stats.active_tasks}/{stats.max_concurrent_tasks}, "
                                   f"Completed: {stats.completed_tasks}, Failed: {stats.failed_tasks}, "
                                   f"Total: {stats.total_submissions}")

                # Alert if high utilization
                utilization = stats.active_tasks / stats.max_concurrent_tasks
                if utilization > 0.8:
                    self._logger.warning(
                        f"High task utilization: {utilization:.1%} "
                        f"({stats.active_tasks}/{stats.max_concurrent_tasks})"
                    )

                # Alert if many failed tasks
                if stats.failed_tasks > 0 and stats.completed_tasks > 0:
                    failure_rate = stats.failed_tasks / (stats.completed_tasks + stats.failed_tasks)
                    if failure_rate > 0.1:  # 10% failure rate
                        self._logger.error(f"High task failure rate: {failure_rate:.1%} - "
                                           f"Failed: {stats.failed_tasks}, Completed: {stats.completed_tasks}")

                # Wait for next check
                await asyncio.sleep(self._monitoring_interval)

            except Exception as e:
                self._logger.error(f"Critical error in task monitor: {e}", exc_info=True)
                # Sleep longer on error to prevent spam
                await asyncio.sleep(60)

    def get_stats(self) -> TaskStats:
        """Get current task statistics."""
        return TaskStats(
            active_tasks=len(self._active_tasks),
            max_concurrent_tasks=self._max_concurrent_tasks,
            completed_tasks=self._completed_tasks,
            failed_tasks=self._failed_tasks,
            total_submissions=self._total_submissions,
            last_activity=self._last_activity
        )

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring endpoints."""
        try:
            stats = self.get_stats()

            # Calculate health metrics
            utilization = stats.active_tasks / stats.max_concurrent_tasks if stats.max_concurrent_tasks > 0 else 0
            failure_rate = stats.failed_tasks / max(stats.completed_tasks + stats.failed_tasks, 1)

            # Determine overall health
            if utilization > 0.9:
                health_status = "overloaded"
                self._logger.warning(f"Task manager health: {health_status} - Utilization: {utilization:.1%}")
            elif failure_rate > 0.2:
                health_status = "degraded"
                self._logger.error(f"Task manager health: {health_status} - Failure rate: {failure_rate:.1%}")
            elif utilization > 0.7:
                health_status = "busy"
                self._logger.info(f"Task manager health: {health_status} - Utilization: {utilization:.1%}")
            else:
                health_status = "healthy"
                self._logger.debug(f"Task manager health: {health_status} - Utilization: {utilization:.1%}")

            return {
                "status": health_status,
                "timestamp": datetime.utcnow().isoformat(),
                "stats": {
                    "active_tasks": stats.active_tasks,
                    "max_concurrent_tasks": stats.max_concurrent_tasks,
                    "utilization": f"{utilization:.1%}",
                    "failure_rate": f"{failure_rate:.1%}",
                    "total_submissions": stats.total_submissions,
                    "last_activity": stats.last_activity.isoformat()
                }
            }

        except Exception as e:
            self._logger.error(f"Failed to get health status: {type(e).__name__}: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"{type(e).__name__}: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def shutdown(self, wait: bool = True, timeout: Optional[float] = None):
        """Graceful shutdown of task manager."""
        self._logger.info("Shutting down ChatTaskManager...")

        # Signal shutdown
        self._shutdown_event.set()

        try:
            # Cancel all active tasks
            for task in self._active_tasks.copy():
                task.cancel()

            # Wait for tasks to complete if requested
            if wait and self._active_tasks:
                await asyncio.wait_for(
                    asyncio.gather(*self._active_tasks, return_exceptions=True),
                    timeout=timeout
                )

            # Cancel monitoring task
            if self._monitor_task and not self._monitor_task.done():
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass

            self._logger.info("ChatTaskManager shutdown complete")

        except Exception as e:
            self._logger.error(f"Error during task manager shutdown: {e}", exc_info=True)
