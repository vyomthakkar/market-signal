"""
Retry logic with exponential backoff and jitter.

Provides decorators and utilities for retrying failed operations
with intelligent backoff strategies.
"""
import asyncio
import random
import logging
from typing import Callable, Type, Tuple, Optional
from functools import wraps

from .exceptions import ScraperException, RateLimitException

logger = logging.getLogger(__name__)


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Attempt number (0-indexed)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential growth (2 = double each time)
        jitter: Add random jitter to prevent thundering herd
    
    Returns:
        Delay in seconds
    
    Example:
        Attempt 0: ~1s
        Attempt 1: ~2s
        Attempt 2: ~4s
        Attempt 3: ~8s
        Attempt 4: ~16s (but capped at max_delay)
    """
    delay = min(base_delay * (exponential_base ** attempt), max_delay)
    
    if jitter:
        # Add ±25% jitter
        delay = delay * (0.75 + random.random() * 0.5)
    
    return delay


def retry_async(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for async functions with exponential backoff retry.
    
    Args:
        max_attempts: Maximum retry attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exception types to retry on
        on_retry: Optional callback called on each retry(attempt, exception)
    
    Example:
        @retry_async(max_attempts=3, base_delay=2.0)
        async def fetch_data():
            response = await make_request()
            return response
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Don't retry on last attempt
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts",
                            exc_info=True
                        )
                        raise
                    
                    # Calculate backoff delay
                    delay = exponential_backoff(
                        attempt=attempt,
                        base_delay=base_delay,
                        max_delay=max_delay,
                        exponential_base=exponential_base
                    )
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}). "
                        f"Retrying in {delay:.2f}s. Error: {str(e)}"
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt, e)
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing if service recovered, allow one request
    
    Prevents cascading failures by failing fast when service is down.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again (half-open)
            expected_exception: Exception type that counts as failure
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should try transitioning to HALF_OPEN"""
        import time
        if self.state == "OPEN" and self.last_failure_time:
            elapsed = time.time() - self.last_failure_time
            return elapsed >= self.recovery_timeout
        return False
    
    async def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to call
            *args, **kwargs: Arguments to pass to function
        
        Raises:
            Exception: If circuit is OPEN or function fails
        """
        # Check if we should attempt recovery
        if self._should_attempt_reset():
            self.state = "HALF_OPEN"
            logger.info("Circuit breaker transitioning to HALF_OPEN (testing recovery)")
        
        # Fail fast if circuit is OPEN
        if self.state == "OPEN":
            raise ScraperException(
                f"Circuit breaker is OPEN. Service is likely down. "
                f"Retry after {self.recovery_timeout}s"
            )
        
        try:
            result = await func(*args, **kwargs)
            
            # Success! Reset circuit breaker
            if self.state == "HALF_OPEN":
                logger.info("Circuit breaker transitioning to CLOSED (service recovered)")
            
            self.failure_count = 0
            self.state = "CLOSED"
            return result
            
        except self.expected_exception as e:
            import time
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(
                    f"Circuit breaker OPEN after {self.failure_count} failures. "
                    f"Will retry after {self.recovery_timeout}s"
                )
            
            raise
    
    def reset(self):
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None
        logger.info("Circuit breaker manually reset to CLOSED")
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout
        }

