"""
Performance optimization and monitoring for the chat system
"""
import time
import asyncio
from functools import wraps
from typing import Dict, Any, Optional, Callable
from collections import OrderedDict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics = {
            'database_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': 0,
            'response_times': []
        }
        self.start_time = time.time()
    
    def record_query(self, query_time: float):
        """Record database query performance"""
        self.metrics['database_queries'] += 1
        self.metrics['response_times'].append(query_time)
        
        if query_time > 1.0:  # Log slow queries
            logger.warning(f"Slow database query detected: {query_time:.2f}s")
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics['cache_misses'] += 1
    
    def record_api_call(self, call_time: float):
        """Record API call performance"""
        self.metrics['api_calls'] += 1
        self.metrics['response_times'].append(call_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total_time = time.time() - self.start_time
        avg_response_time = (
            sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            if self.metrics['response_times'] else 0
        )
        
        cache_efficiency = (
            self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
            if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
        )
        
        return {
            'uptime_seconds': total_time,
            'total_queries': self.metrics['database_queries'],
            'total_api_calls': self.metrics['api_calls'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_efficiency': f"{cache_efficiency:.2%}",
            'average_response_time': f"{avg_response_time:.3f}s",
            'queries_per_second': self.metrics['database_queries'] / total_time if total_time > 0 else 0
        }

class Cache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """Initialize cache"""
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            # Check if expired
            if time.time() - self.timestamps[key] > self.default_ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
            
            # Move to end (LRU)
            value = self.cache.pop(key)
            self.cache[key] = value
            self.timestamps[key] = time.time()
            return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_select_query(fields: list, table: str, conditions: Dict[str, Any] = None) -> str:
        """Generate optimized SELECT query"""
        # Only select needed fields
        field_list = ', '.join(fields) if fields else '*'
        
        query = f"SELECT {field_list} FROM {table}"
        
        if conditions:
            where_clauses = []
            for field, value in conditions.items():
                if value is not None:
                    where_clauses.append(f"{field} = ?")
            
            if where_clauses:
                query += f" WHERE {' AND '.join(where_clauses)}"
        
        return query
    
    @staticmethod
    def add_index_hints(table: str, index_name: str) -> str:
        """Add index hints to queries"""
        return f"SELECT * FROM {table} USE INDEX ({index_name})"
    
    @staticmethod
    def limit_results(limit: int = 100, offset: int = 0) -> str:
        """Add LIMIT and OFFSET to queries"""
        return f" LIMIT {limit} OFFSET {offset}"

def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log performance
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

def cache_result(ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                performance_monitor.record_cache_hit()
                return cached_result
            
            # Execute function and cache result
            performance_monitor.record_cache_miss()
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Global instances
performance_monitor = PerformanceMonitor()
cache = Cache()

# Performance monitoring utilities
def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics"""
    return performance_monitor.get_stats()

def clear_cache():
    """Clear all cached data"""
    cache.clear()

def optimize_database_connection():
    """Optimize database connection settings"""
    # This would contain database-specific optimization code
    # For SQLite, we could set pragmas for better performance
    pass
