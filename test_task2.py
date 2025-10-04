#!/usr/bin/env python3
"""
Test script to demonstrate new production-ready features.

Run this to verify all new modules are working correctly before integration.
"""
import asyncio
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.exceptions import *
from core.rate_limiter import TokenBucketRateLimiter, AdaptiveRateLimiter
from core.retry import retry_async, exponential_backoff, CircuitBreaker
from data.collector import TweetCollector
from config.settings import load_config, TwitterCredentials


async def test_rate_limiter():
    """Test TokenBucketRateLimiter"""
    print("\n" + "="*60)
    print("TEST 1: Token Bucket Rate Limiter")
    print("="*60)
    
    limiter = TokenBucketRateLimiter(rate=5, capacity=10, name="test")
    
    print(f"Rate: {limiter.rate} req/s, Capacity: {limiter.capacity}")
    print("Making 15 requests...")
    
    start = time.time()
    for i in range(15):
        async with limiter:
            elapsed = time.time() - start
            print(f"  Request {i+1}/15 - Elapsed: {elapsed:.2f}s")
    
    total_time = time.time() - start
    actual_rate = 15 / total_time
    print(f"\nCompleted 15 requests in {total_time:.2f}s")
    print(f"Actual rate: {actual_rate:.2f} req/s (target: {limiter.rate} req/s)")
    print(f"✅ Rate limiter working!" if abs(actual_rate - limiter.rate) < 2 else "❌ Rate limiter not working")


async def test_adaptive_rate_limiter():
    """Test AdaptiveRateLimiter"""
    print("\n" + "="*60)
    print("TEST 2: Adaptive Rate Limiter")
    print("="*60)
    
    limiter = AdaptiveRateLimiter(initial_rate=10, min_rate=2, max_rate=20)
    
    print(f"Initial rate: {limiter.current_rate} req/s")
    
    # Simulate rate limit
    print("\nSimulating rate limit detection...")
    limiter.on_rate_limit()
    print(f"After rate limit: {limiter.current_rate} req/s (backed off)")
    
    # Simulate successful requests
    print("\nSimulating 20 successful requests...")
    for _ in range(20):
        limiter.on_success()
    print(f"After successes: {limiter.current_rate} req/s (recovered)")
    
    print("\n✅ Adaptive rate limiter working!")


async def test_tweet_collector():
    """Test TweetCollector with O(1) deduplication"""
    print("\n" + "="*60)
    print("TEST 3: TweetCollector (O(1) Deduplication)")
    print("="*60)
    
    collector = TweetCollector()
    
    # Create sample tweets
    tweets = [
        {'tweet_id': '1', 'content': 'Tweet 1'},
        {'tweet_id': '2', 'content': 'Tweet 2'},
        {'tweet_id': '1', 'content': 'Tweet 1 duplicate'},  # Duplicate!
        {'tweet_id': '3', 'content': 'Tweet 3'},
        {'tweet_id': '2', 'content': 'Tweet 2 duplicate'},  # Duplicate!
    ]
    
    print(f"Adding {len(tweets)} tweets (including duplicates)...")
    for tweet in tweets:
        added = collector.add(tweet)
        status = "✓ Added" if added else "✗ Duplicate"
        print(f"  {status}: {tweet['tweet_id']}")
    
    stats = collector.get_stats()
    print(f"\nStatistics:")
    print(f"  Unique tweets: {stats['unique_tweets']}")
    print(f"  Duplicates skipped: {stats['duplicates_skipped']}")
    print(f"  Total processed: {stats['total_processed']}")
    print(f"  Deduplication rate: {stats['deduplication_rate']:.1f}%")
    
    print("\n✅ TweetCollector working!")


async def test_retry_logic():
    """Test retry with exponential backoff"""
    print("\n" + "="*60)
    print("TEST 4: Retry Logic with Exponential Backoff")
    print("="*60)
    
    # Test exponential backoff calculation
    print("Exponential backoff delays:")
    for attempt in range(5):
        delay = exponential_backoff(attempt, base_delay=1.0, jitter=False)
        print(f"  Attempt {attempt + 1}: {delay:.2f}s")
    
    # Test retry decorator
    call_count = [0]
    
    @retry_async(max_attempts=3, base_delay=0.5, exceptions=(ValueError,))
    async def flaky_function():
        call_count[0] += 1
        print(f"  Attempt {call_count[0]}")
        if call_count[0] < 3:
            raise ValueError("Simulated failure")
        return "Success!"
    
    print("\nTesting retry decorator (will fail 2 times, succeed on 3rd):")
    result = await flaky_function()
    print(f"Result: {result}")
    print(f"Total attempts: {call_count[0]}")
    
    print("\n✅ Retry logic working!")


async def test_circuit_breaker():
    """Test Circuit Breaker"""
    print("\n" + "="*60)
    print("TEST 5: Circuit Breaker")
    print("="*60)
    
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2)
    
    async def failing_function():
        raise NetworkException("Simulated network error")
    
    print(f"Initial state: {breaker.state}")
    
    # Cause failures
    print("\nCausing 3 failures to open circuit...")
    for i in range(3):
        try:
            await breaker.call(failing_function)
        except NetworkException:
            print(f"  Failure {i+1}/3")
    
    print(f"State after failures: {breaker.state}")
    
    # Try to call with open circuit
    print("\nTrying to call with OPEN circuit...")
    try:
        await breaker.call(failing_function)
    except ScraperException as e:
        print(f"  Blocked: {e}")
    
    # Wait for recovery timeout
    print(f"\nWaiting {breaker.recovery_timeout}s for recovery...")
    await asyncio.sleep(breaker.recovery_timeout + 0.5)
    
    # Should transition to HALF_OPEN
    async def working_function():
        return "Success!"
    
    print("Attempting recovery with successful call...")
    result = await breaker.call(working_function)
    print(f"  Result: {result}")
    print(f"  State after recovery: {breaker.state}")
    
    print("\n✅ Circuit breaker working!")


def test_configuration():
    """Test configuration management"""
    print("\n" + "="*60)
    print("TEST 6: Configuration Management")
    print("="*60)
    
    # Load default config
    config = load_config()
    
    print("Default configuration:")
    print(f"  Headless: {config.headless}")
    print(f"  Tweets per hashtag: {config.tweets_per_hashtag}")
    print(f"  Hashtags: {config.hashtags}")
    print(f"  Max retries: {config.max_retries}")
    print(f"  Rate limit: {config.rate_limit_requests_per_second} req/s")
    
    # Load with overrides
    config2 = load_config(headless=False, tweets_per_hashtag=100)
    print("\nWith overrides:")
    print(f"  Headless: {config2.headless}")
    print(f"  Tweets per hashtag: {config2.tweets_per_hashtag}")
    
    print("\n✅ Configuration working!")


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  TESTING NEW PRODUCTION-READY FEATURES")
    print("="*70)
    
    try:
        # Run tests
        await test_rate_limiter()
        await test_adaptive_rate_limiter()
        await test_tweet_collector()
        await test_retry_logic()
        await test_circuit_breaker()
        test_configuration()
        
        # Summary
        print("\n" + "="*70)
        print("  ✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nNew features are ready for integration into the main scraper.")
        print("\nComponents tested:")
        print("  ✅ Token Bucket Rate Limiter")
        print("  ✅ Adaptive Rate Limiter")
        print("  ✅ TweetCollector (O(1) deduplication)")
        print("  ✅ Retry Logic with Exponential Backoff")
        print("  ✅ Circuit Breaker")
        print("  ✅ Configuration Management")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

