"""
Thread Pool Manager for Chat Service
Provides production-grade thread pool management for async message processing.
"""

import concurrent.futures
import threading
import logging
import time
import asyncio
from typing import Optional, Callable, Any, Dict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ThreadPoolStats:
    """Thread pool statistics for monitoring."""
    active_tasks: int
    thread_pool_size: int
    queue_size: int
    completed_tasks: int
    failed_tasks: int
    total_submissions: int
    last_activity: datetime


class ChatThreadPoolManager:
    """
    Production-grade thread pool manager for chat service.
    
    Features:
    - Persistent thread pool with configurable workers
    - Task tracking and monitoring
    - Health monitoring and metrics
    - Graceful shutdown procedures
    - Comprehensive error handling
    """
    
    def __init__(self, 
                 max_workers: int = 20, 
                 thread_name_prefix: str = "ChatWorker",
                 monitoring_interval: int = 30,
                 log_level: str = "INFO"):
        """
        Initialize the thread pool manager.
        
        Args:
            max_workers: Maximum number of worker threads
            thread_name_prefix: Prefix for thread names
            monitoring_interval: Monitoring check interval in seconds
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self._max_workers = max_workers
        self._thread_name_prefix = thread_name_prefix
        self._monitoring_interval = monitoring_interval
        
        # Thread pool
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix
        )
        
        # State management
        self._lock = threading.RLock()
        self._active_tasks = set()
        self._completed_tasks = 0
        self._failed_tasks = 0
        self._total_submissions = 0
        self._last_activity = datetime.utcnow()
        self._shutdown_event = threading.Event()
        
        # Logging setup with configurable level
        self._logger = logging.getLogger(__name__)
        self._setup_logging(log_level)
        
        # Start monitoring thread
        self._monitor_thread = threading.Thread(
            target=self._monitor_thread_pool,
            daemon=True,
            name="ThreadPoolMonitor"
        )
        self._monitor_thread.start()
        
        self._logger.info(f"ChatThreadPoolManager initialized with {max_workers} workers, log level: {log_level}")
    
    def _setup_logging(self, log_level: str):
        """Setup logging with configurable level."""
        try:
            # Convert string to logging level
            numeric_level = getattr(logging, log_level.upper(), logging.INFO)
            self._logger.setLevel(numeric_level)
            
            # Create formatter with detailed information
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            
            # Add handler if none exists
            if not self._logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(formatter)
                self._logger.addHandler(handler)
            
            self._logger.debug(f"Logging configured with level: {log_level} ({numeric_level})")
            
        except Exception as e:
            # Fallback to basic logging if setup fails
            print(f"Warning: Failed to setup logging: {e}")
            self._logger.setLevel(logging.INFO)
    
    def submit_task(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """
        Submit a task to the thread pool.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Future object representing the task
            
        Raises:
            RuntimeError: If thread pool is shutdown
        """
        if self._shutdown_event.is_set():
            error_msg = "Thread pool manager is shutdown"
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            # Submit to thread pool
            future = self._executor.submit(func, *args, **kwargs)
            
            # Track task
            with self._lock:
                self._active_tasks.add(future)
                self._total_submissions += 1
                self._last_activity = datetime.utcnow()
            
            # Add completion callback
            future.add_done_callback(self._task_completed_callback)
            
            # Log successful submission with function details
            func_name = getattr(func, '__name__', str(func))
            self._logger.info(f"Task submitted successfully: {func_name} (args: {len(args)}, kwargs: {len(kwargs)})")
            return future
            
        except Exception as e:
            # Log detailed error with stack trace
            func_name = getattr(func, '__name__', str(func))
            self._logger.error(f"Failed to submit task {func_name}: {type(e).__name__}: {e}", exc_info=True)
            
            # Log additional context
            self._logger.error(f"Task submission context - Args: {args}, Kwargs: {kwargs}")
            raise

    def submit_async_task(self, async_func, *args, **kwargs) -> concurrent.futures.Future:
        """
        Submit an async function to the thread pool with event loop management.
        
        Args:
            async_func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Future object representing the task
            
        Raises:
            RuntimeError: If thread pool is shutdown
        """
        if self._shutdown_event.is_set():
            error_msg = "Thread pool manager is shutdown"
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        def run_async_in_thread():
            """Run async function in a new thread with its own event loop."""
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the async function and ensure it's properly awaited
                result = loop.run_until_complete(async_func(*args, **kwargs))
                return result
            except Exception as e:
                # Log any errors that occur during async execution
                self._logger.error(f"Async function execution failed: {e}", exc_info=True)
                raise
            finally:
                # Ensure the loop is properly closed
                try:
                    # Cancel any pending tasks
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    
                    # Wait for cancellation to complete
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass
                finally:
                    loop.close()
        
        try:
            # Submit the wrapper function to thread pool
            future = self._executor.submit(run_async_in_thread)
            
            # Track task
            with self._lock:
                self._active_tasks.add(future)
                self._total_submissions += 1
                self._last_activity = datetime.utcnow()
            
            # Add completion callback
            future.add_done_callback(self._task_completed_callback)
            
            # Log successful submission
            func_name = getattr(async_func, '__name__', str(async_func))
            self._logger.info(f"Async task submitted successfully: {func_name} (args: {len(args)}, kwargs: {len(kwargs)})")
            return future
            
        except Exception as e:
            # Log detailed error
            func_name = getattr(async_func, '__name__', str(async_func))
            self._logger.error(f"Failed to submit async task {func_name}: {type(e).__name__}: {e}", exc_info=True)
            raise
    
    def _task_completed_callback(self, future: concurrent.futures.Future):
        """Callback executed when a task completes."""
        try:
            # Remove from active tasks
            with self._lock:
                self._active_tasks.discard(future)
                self._completed_tasks += 1
                self._last_activity = datetime.utcnow()
            
            # Check for exceptions with full stack trace
            if future.exception():
                with self._lock:
                    self._failed_tasks += 1
                
                # Log the exception with full details
                exc = future.exception()
                self._logger.error(f"Task failed with exception: {type(exc).__name__}: {exc}", exc_info=True)
                
                # Additional context for debugging
                if hasattr(future, '_thread_name'):
                    self._logger.error(f"Task failed in thread: {future._thread_name}")
                
            else:
                self._logger.debug("Task completed successfully")
                
        except Exception as e:
            self._logger.error(f"Critical error in task completion callback: {e}", exc_info=True)
            # This is a meta-error - log it but don't crash the callback
    
    def _monitor_thread_pool(self):
        """Monitor thread pool health and performance."""
        while not self._shutdown_event.is_set():
            try:
                # Get current stats
                stats = self.get_stats()
                
                # Log metrics with detailed info
                self._logger.info(f"Thread pool monitoring - Active: {stats.active_tasks}/{stats.thread_pool_size}, "
                                f"Completed: {stats.completed_tasks}, Failed: {stats.failed_tasks}, "
                                f"Total: {stats.total_submissions}")
                
                # Alert if high utilization
                utilization = stats.active_tasks / stats.thread_pool_size
                if utilization > 0.8:
                    self._logger.warning(
                        f"High thread pool utilization: {utilization:.1%} "
                        f"({stats.active_tasks}/{stats.thread_pool_size})"
                    )
                
                # Alert if many failed tasks
                if stats.failed_tasks > 0 and stats.completed_tasks > 0:
                    failure_rate = stats.failed_tasks / (stats.completed_tasks + stats.failed_tasks)
                    if failure_rate > 0.1:  # 10% failure rate
                        self._logger.error(f"High task failure rate: {failure_rate:.1%} - "
                                         f"Failed: {stats.failed_tasks}, Completed: {stats.completed_tasks}")
                
                # Wait for next check
                self._shutdown_event.wait(self._monitoring_interval)
                
            except Exception as e:
                self._logger.error(f"Critical error in thread pool monitor: {e}", exc_info=True)
                # Sleep longer on error to prevent spam
                self._shutdown_event.wait(60)
    
    def get_stats(self) -> ThreadPoolStats:
        """Get current thread pool statistics."""
        with self._lock:
            return ThreadPoolStats(
                active_tasks=len(self._active_tasks),
                thread_pool_size=self._max_workers,
                queue_size=getattr(self._executor, '_work_queue', None).qsize() if hasattr(self._executor, '_work_queue') else 0,
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
            utilization = stats.active_tasks / stats.thread_pool_size if stats.thread_pool_size > 0 else 0
            failure_rate = stats.failed_tasks / max(stats.completed_tasks + stats.failed_tasks, 1)
            
            # Determine overall health
            if utilization > 0.9:
                health_status = "overloaded"
                self._logger.warning(f"Thread pool health: {health_status} - Utilization: {utilization:.1%}")
            elif failure_rate > 0.2:
                health_status = "degraded"
                self._logger.error(f"Thread pool health: {health_status} - Failure rate: {failure_rate:.1%}")
            elif utilization > 0.7:
                health_status = "busy"
                self._logger.info(f"Thread pool health: {health_status} - Utilization: {utilization:.1%}")
            else:
                health_status = "healthy"
                self._logger.debug(f"Thread pool health: {health_status} - Utilization: {utilization:.1%}")
            
            return {
                "status": health_status,
                "timestamp": datetime.utcnow().isoformat(),
                "stats": {
                    "active_tasks": stats.active_tasks,
                    "thread_pool_size": stats.thread_pool_size,
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
    
    @contextmanager
    def get_executor_context(self):
        """Context manager for safe thread pool access."""
        if self._shutdown_event.is_set():
            raise RuntimeError("Thread pool manager is shutdown")
        
        try:
            yield self._executor
        except Exception as e:
            self._logger.error(f"Error in executor context: {e}", exc_info=True)
            raise
    
    def shutdown(self, wait: bool = True, timeout: Optional[float] = None):
        """Graceful shutdown of thread pool manager."""
        self._logger.info("Shutting down ChatThreadPoolManager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        try:
            # Cancel all pending tasks
            with self._lock:
                for future in self._active_tasks.copy():
                    future.cancel()
            
            # Shutdown executor
            self._executor.shutdown(wait=wait, timeout=timeout)
            
            self._logger.info("ChatThreadPoolManager shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during thread pool shutdown: {e}", exc_info=True)
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.shutdown(wait=False)
        except:
            pass  # Ignore errors during cleanup


# Global instance for easy access
_thread_pool_manager: Optional[ChatThreadPoolManager] = None


def get_thread_pool_manager() -> ChatThreadPoolManager:
    """Get the global thread pool manager instance."""
    global _thread_pool_manager
    if _thread_pool_manager is None:
        _thread_pool_manager = ChatThreadPoolManager()
    return _thread_pool_manager


def initialize_thread_pool_manager(max_workers: int = 20, 
                                  thread_name_prefix: str = "ChatWorker",
                                  monitoring_interval: int = 30,
                                  log_level: str = "INFO") -> ChatThreadPoolManager:
    """Initialize the global thread pool manager with custom settings."""
    global _thread_pool_manager
    if _thread_pool_manager is not None:
        _thread_pool_manager.shutdown()
    
    _thread_pool_manager = ChatThreadPoolManager(
        max_workers=max_workers,
        thread_name_prefix=thread_name_prefix,
        monitoring_interval=monitoring_interval,
        log_level=log_level
    )
    return _thread_pool_manager


def shutdown_thread_pool_manager():
    """Shutdown the global thread pool manager."""
    global _thread_pool_manager
    if _thread_pool_manager is not None:
        _thread_pool_manager.shutdown()
        _thread_pool_manager = None
