"""
Async Performance Optimizer
Provides optimized async patterns and performance utilities for blocking operations
"""

import asyncio
import logging
import random
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Performance optimization levels"""
    AGGRESSIVE = "aggressive"  # Maximum performance, minimal delays
    BALANCED = "balanced"      # Balanced performance and reliability
    CONSERVATIVE = "conservative"  # Maximum reliability, some delays


@dataclass
class PerformanceConfig:
    """Configuration for performance optimizations"""
    
    # Optimization level
    level: OptimizationLevel = OptimizationLevel.BALANCED
    
    # Timeout settings
    default_timeout: float = 30.0
    page_load_timeout: float = 10.0
    element_wait_timeout: float = 5.0
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # Anti-bot detection settings
    min_human_delay: float = 0.1
    max_human_delay: float = 0.5
    randomize_delays: bool = True
    
    # Queue processing settings
    queue_poll_interval: float = 0.05  # 50ms for responsive processing
    batch_size: int = 10
    
    # ProducerAI specific settings
    producer_check_interval: float = 0.5
    producer_max_checks: int = 60  # 30 seconds total
    page_refresh_delay: float = 1.0


class AsyncOptimizer:
    """Optimized async operations and performance utilities"""
    
    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()
        self._setup_optimizations()
    
    def _setup_optimizations(self):
        """Setup optimization parameters based on level"""
        if self.config.level == OptimizationLevel.AGGRESSIVE:
            self.config.queue_poll_interval = 0.01  # 10ms
            self.config.min_human_delay = 0.05
            self.config.max_human_delay = 0.2
            self.config.producer_check_interval = 0.2
        elif self.config.level == OptimizationLevel.CONSERVATIVE:
            self.config.queue_poll_interval = 0.1  # 100ms
            self.config.min_human_delay = 0.2
            self.config.max_human_delay = 1.0
            self.config.producer_check_interval = 1.0
    
    async def smart_sleep(self, duration: float, reason: str = "waiting") -> None:
        """
        Smart sleep with optimization based on context
        
        Args:
            duration: Sleep duration in seconds
            reason: Reason for sleeping (for logging and optimization)
        """
        if duration <= 0:
            return
        
        # Optimize sleep duration based on context and level
        optimized_duration = self._optimize_sleep_duration(duration, reason)
        
        if optimized_duration < duration:
            logger.debug(f"Optimized sleep from {duration}s to {optimized_duration}s for {reason}")
        
        await asyncio.sleep(optimized_duration)
    
    def _optimize_sleep_duration(self, duration: float, reason: str) -> float:
        """Optimize sleep duration based on context"""
        # Anti-bot detection delays should not be optimized
        if "anti-bot" in reason.lower() or "human" in reason.lower():
            return duration
        
        # Page load delays can be optimized
        if "page" in reason.lower() or "load" in reason.lower():
            if self.config.level == OptimizationLevel.AGGRESSIVE:
                return min(duration, 2.0)
            elif self.config.level == OptimizationLevel.BALANCED:
                return min(duration, 3.0)
        
        # Queue processing can be very fast
        if "queue" in reason.lower() or "processing" in reason.lower():
            return min(duration, self.config.queue_poll_interval)
        
        # Default optimization
        if self.config.level == OptimizationLevel.AGGRESSIVE:
            return duration * 0.5
        elif self.config.level == OptimizationLevel.BALANCED:
            return duration * 0.7
        
        return duration
    
    async def human_like_delay(self, min_seconds: float = None, max_seconds: float = None) -> None:
        """
        Human-like delay with randomization for anti-bot detection
        
        Args:
            min_seconds: Minimum delay (uses config default if None)
            max_seconds: Maximum delay (uses config default if None)
        """
        min_delay = min_seconds or self.config.min_human_delay
        max_delay = max_seconds or self.config.max_human_delay
        
        if self.config.randomize_delays:
            delay = random.uniform(min_delay, max_delay)
        else:
            delay = (min_delay + max_delay) / 2
        
        await asyncio.sleep(delay)
    
    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        max_retries: Optional[int] = None,
        delay: Optional[float] = None,
        exponential_backoff: Optional[bool] = None,
        **kwargs
    ) -> Any:
        """
        Retry function with exponential backoff
        
        Args:
            func: Function to retry
            *args: Function arguments
            max_retries: Maximum retry attempts
            delay: Initial delay between retries
            exponential_backoff: Whether to use exponential backoff
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries fail
        """
        max_retries = max_retries or self.config.max_retries
        delay = delay or self.config.retry_delay
        exponential_backoff = exponential_backoff if exponential_backoff is not None else self.config.exponential_backoff
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    current_delay = delay
                    if exponential_backoff:
                        current_delay = delay * (2 ** attempt)
                    
                    logger.debug(f"Retry attempt {attempt + 1}/{max_retries} failed: {e}, retrying in {current_delay}s")
                    await asyncio.sleep(current_delay)
                else:
                    logger.error(f"All {max_retries + 1} retry attempts failed for {func.__name__}")
        
        raise last_exception
    
    async def batch_process(
        self,
        items: List[Any],
        process_func: Callable,
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[Any]:
        """
        Process items in batches for better performance
        
        Args:
            items: List of items to process
            process_func: Function to process each item
            batch_size: Size of each batch
            **kwargs: Additional arguments for process_func
            
        Returns:
            List of processed results
        """
        batch_size = batch_size or self.config.batch_size
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for item in batch:
                if asyncio.iscoroutinefunction(process_func):
                    tasks.append(process_func(item, **kwargs))
                else:
                    tasks.append(asyncio.create_task(asyncio.to_thread(process_func, item, **kwargs)))
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Small delay between batches to prevent overwhelming
            if i + batch_size < len(items):
                await self.smart_sleep(0.01, "batch processing")
        
        return results
    
    async def wait_for_condition(
        self,
        condition_func: Callable,
        timeout: Optional[float] = None,
        check_interval: float = 0.1,
        *args,
        **kwargs
    ) -> bool:
        """
        Wait for a condition to be true with timeout
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait
            check_interval: How often to check the condition
            *args: Arguments for condition_func
            **kwargs: Keyword arguments for condition_func
            
        Returns:
            True if condition was met, False if timeout
        """
        timeout = timeout or self.config.default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if asyncio.iscoroutinefunction(condition_func):
                    result = await condition_func(*args, **kwargs)
                else:
                    result = condition_func(*args, **kwargs)
                
                if result:
                    return True
            except Exception as e:
                logger.debug(f"Condition check failed: {e}")
            
            await asyncio.sleep(check_interval)
        
        return False
    
    @asynccontextmanager
    async def timeout_context(self, timeout: float, operation_name: str = "operation"):
        """
        Context manager for operations with timeout
        
        Args:
            timeout: Timeout in seconds
            operation_name: Name of operation for logging
        """
        try:
            async with asyncio.timeout(timeout):
                yield
        except asyncio.TimeoutError:
            logger.error(f"Operation '{operation_name}' timed out after {timeout}s")
            raise
    
    async def parallel_execute(
        self,
        tasks: List[Callable],
        max_concurrent: int = 5,
        **kwargs
    ) -> List[Any]:
        """
        Execute tasks in parallel with concurrency limit
        
        Args:
            tasks: List of tasks to execute
            max_concurrent: Maximum concurrent executions
            **kwargs: Additional arguments for tasks
            
        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                if asyncio.iscoroutinefunction(task):
                    return await task(**kwargs)
                else:
                    return await asyncio.to_thread(task, **kwargs)
        
        return await asyncio.gather(*[execute_with_semaphore(task) for task in tasks])


# Performance decorators
def optimize_async(optimizer: AsyncOptimizer = None):
    """Decorator to optimize async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            opt = optimizer or AsyncOptimizer()
            
            # Add performance monitoring
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator


def with_retry(max_retries: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """Decorator to add retry logic to functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            optimizer = AsyncOptimizer()
            return await optimizer.retry_with_backoff(
                func, *args, max_retries=max_retries, delay=delay, 
                exponential_backoff=exponential_backoff, **kwargs
            )
        return wrapper
    return decorator


def with_timeout(timeout: float, operation_name: str = None):
    """Decorator to add timeout to functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            optimizer = AsyncOptimizer()
            async with optimizer.timeout_context(timeout, name):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


# Global optimizer instances
aggressive_optimizer = AsyncOptimizer(PerformanceConfig(level=OptimizationLevel.AGGRESSIVE))
balanced_optimizer = AsyncOptimizer(PerformanceConfig(level=OptimizationLevel.BALANCED))
conservative_optimizer = AsyncOptimizer(PerformanceConfig(level=OptimizationLevel.CONSERVATIVE))

# Default optimizer
default_optimizer = balanced_optimizer


# Utility functions
async def smart_sleep(duration: float, reason: str = "waiting", optimizer: AsyncOptimizer = None) -> None:
    """Smart sleep utility function"""
    opt = optimizer or default_optimizer
    await opt.smart_sleep(duration, reason)


async def human_delay(min_seconds: float = 0.1, max_seconds: float = 0.5, optimizer: AsyncOptimizer = None) -> None:
    """Human-like delay utility function"""
    opt = optimizer or default_optimizer
    await opt.human_like_delay(min_seconds, max_seconds)


async def retry_operation(
    func: Callable,
    *args,
    max_retries: int = 3,
    delay: float = 1.0,
    exponential_backoff: bool = True,
    optimizer: AsyncOptimizer = None,
    **kwargs
) -> Any:
    """Retry operation utility function"""
    opt = optimizer or default_optimizer
    return await opt.retry_with_backoff(
        func, *args, max_retries=max_retries, delay=delay,
        exponential_backoff=exponential_backoff, **kwargs
    )
