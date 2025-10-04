"""
Token Bucket Rate Limiter

Implements a production-grade rate limiter using the token bucket algorithm.
Allows bursts when tokens are available, then smooths to steady rate.

Key Features:
- Async support
- Thread-safe
- Configurable rate and burst size
- Adaptive backoff
"""
import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token Bucket algorithm for rate limiting.
    
    Tokens are added at a steady rate. Each request consumes a token.
    If no tokens available, request waits until tokens are added.
    
    Example:
        limiter = TokenBucketRateLimiter(rate=10, capacity=20)
        
        # Will pass immediately if tokens available
        async with limiter:
            await make_request()
    """
    
    def __init__(
        self, 
        rate: float = 10.0,  # Tokens per second
        capacity: int = 20,  # Max tokens (burst size)
        name: str = "default"
    ):
        """
        Args:
            rate: Tokens added per second (requests/second)
            capacity: Maximum tokens in bucket (max burst)
            name: Identifier for this limiter (for logging)
        """
        self.rate = rate
        self.capacity = capacity
        self.name = name
        
        self.tokens = float(capacity)  # Start with full bucket
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _add_tokens(self):
        """Add tokens based on elapsed time"""
        now = time.monotonic()
        elapsed = now - self.last_update
        
        # Add tokens based on elapsed time
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, waiting if necessary.
        
        Args:
            tokens: Number of tokens to consume
        
        Returns:
            Time waited in seconds
        """
        async with self._lock:
            wait_time = 0.0
            
            while True:
                await self._add_tokens()
                
                if self.tokens >= tokens:
                    # Enough tokens available
                    self.tokens -= tokens
                    return wait_time
                
                # Not enough tokens, calculate wait time
                tokens_needed = tokens - self.tokens
                sleep_time = tokens_needed / self.rate
                
                # Sleep and retry
                await asyncio.sleep(sleep_time)
                wait_time += sleep_time
    
    async def __aenter__(self):
        """Context manager support: async with limiter:"""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        pass
    
    def get_stats(self) -> dict:
        """Get current limiter statistics"""
        return {
            'name': self.name,
            'rate': self.rate,
            'capacity': self.capacity,
            'current_tokens': self.tokens,
            'utilization': (1 - self.tokens / self.capacity) * 100
        }


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts based on detected rate limits.
    
    Starts with initial rate, backs off when rate limits detected,
    gradually increases when successful.
    """
    
    def __init__(
        self,
        initial_rate: float = 10.0,
        min_rate: float = 1.0,
        max_rate: float = 20.0,
        backoff_factor: float = 0.5,
        recovery_factor: float = 1.1
    ):
        """
        Args:
            initial_rate: Starting requests per second
            min_rate: Minimum rate (after backoff)
            max_rate: Maximum rate (after recovery)
            backoff_factor: Multiply rate by this on rate limit (0.5 = half speed)
            recovery_factor: Multiply rate by this on success (1.1 = 10% faster)
        """
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.backoff_factor = backoff_factor
        self.recovery_factor = recovery_factor
        
        self.limiter = TokenBucketRateLimiter(
            rate=initial_rate,
            capacity=int(initial_rate * 2)
        )
        
        self.rate_limit_count = 0
        self.success_count = 0
    
    async def acquire(self):
        """Acquire with current rate"""
        await self.limiter.acquire()
    
    def on_rate_limit(self):
        """Called when rate limit is detected"""
        self.rate_limit_count += 1
        self.success_count = 0  # Reset success counter
        
        # Back off
        new_rate = max(self.min_rate, self.current_rate * self.backoff_factor)
        if new_rate != self.current_rate:
            self.current_rate = new_rate
            self._update_limiter()
    
    def on_success(self):
        """Called on successful request"""
        self.success_count += 1
        
        # After N successful requests, try increasing rate
        if self.success_count >= 20:
            new_rate = min(self.max_rate, self.current_rate * self.recovery_factor)
            if new_rate != self.current_rate:
                self.current_rate = new_rate
                self._update_limiter()
            self.success_count = 0
    
    def _update_limiter(self):
        """Update underlying rate limiter"""
        self.limiter.rate = self.current_rate
        self.limiter.capacity = int(self.current_rate * 2)
    
    def get_stats(self) -> dict:
        """Get statistics"""
        return {
            'current_rate': self.current_rate,
            'min_rate': self.min_rate,
            'max_rate': self.max_rate,
            'rate_limit_count': self.rate_limit_count,
            'success_count': self.success_count,
            **self.limiter.get_stats()
        }
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.on_success()
        return False

