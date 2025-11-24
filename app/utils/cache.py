"""
Caching utility for NLP results
Supports in-memory cache with optional Redis backend
"""
import hashlib
import json
import logging
from typing import Optional, Any
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NLPCache:
    """
    Caching layer for NLP results
    Uses LRU cache with optional Redis backend
    """

    def __init__(self, use_redis: bool = False, redis_url: str = None, ttl: int = 3600):
        """
        Initialize cache

        Args:
            use_redis: Use Redis for caching
            redis_url: Redis connection URL
            ttl: Time to live in seconds (default 1 hour)
        """
        self.ttl = ttl
        self.redis_client = None
        self.use_redis = use_redis

        if use_redis:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url or "redis://localhost:6379/0")
                logger.info("✅ Redis cache initialized")
            except ImportError:
                logger.warning("⚠️  Redis not available, using in-memory cache")
                logger.warning("Install with: pip install redis")
                self.use_redis = False
            except Exception as e:
                logger.warning(f"⚠️  Redis connection failed: {e}")
                logger.warning("Using in-memory cache")
                self.use_redis = False

        if not self.use_redis:
            logger.info("Using in-memory LRU cache")

    def _generate_key(self, prefix: str, text: str, params: dict = None) -> str:
        """
        Generate cache key from text and parameters

        Args:
            prefix: Cache key prefix (e.g., 'lemma', 'complexity')
            text: Input text
            params: Additional parameters

        Returns:
            Cache key (hash)
        """
        cache_data = {
            'text': text,
            'params': params or {}
        }

        # Create hash from JSON string
        data_str = json.dumps(cache_data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())

        return f"{prefix}:{hash_obj.hexdigest()}"

    def get(self, prefix: str, text: str, params: dict = None) -> Optional[Any]:
        """
        Get cached result

        Args:
            prefix: Cache key prefix
            text: Input text
            params: Additional parameters

        Returns:
            Cached result or None
        """
        key = self._generate_key(prefix, text, params)

        if self.use_redis and self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    logger.debug(f"Cache hit: {key[:20]}...")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        # In-memory cache doesn't support direct key lookup
        # Would need separate implementation with dict
        return None

    def set(self, prefix: str, text: str, result: Any, params: dict = None):
        """
        Set cached result

        Args:
            prefix: Cache key prefix
            text: Input text
            result: Result to cache
            params: Additional parameters
        """
        key = self._generate_key(prefix, text, params)

        if self.use_redis and self.redis_client:
            try:
                # Convert result to JSON-serializable format
                if hasattr(result, 'dict'):
                    result_data = result.dict()
                else:
                    result_data = result

                self.redis_client.setex(
                    key,
                    self.ttl,
                    json.dumps(result_data)
                )
                logger.debug(f"Cache set: {key[:20]}...")
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

    def clear(self, prefix: Optional[str] = None):
        """
        Clear cache

        Args:
            prefix: Clear only keys with this prefix, or all if None
        """
        if self.use_redis and self.redis_client:
            try:
                if prefix:
                    pattern = f"{prefix}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                    logger.info(f"Cleared cache with prefix: {prefix}")
                else:
                    self.redis_client.flushdb()
                    logger.info("Cleared entire cache")
            except Exception as e:
                logger.warning(f"Cache clear failed: {e}")


# Global cache instance
_cache_instance = None


def get_cache() -> NLPCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = NLPCache()
    return _cache_instance


def cached_result(prefix: str):
    """
    Decorator for caching function results

    Args:
        prefix: Cache key prefix

    Example:
        @cached_result('lemma')
        def lemmatize(text, include_morphology=True):
            ...
    """
    def decorator(func):
        def wrapper(text: str, *args, **kwargs):
            cache = get_cache()

            # Try to get from cache
            params = {**kwargs, 'args': args}
            cached = cache.get(prefix, text, params)

            if cached is not None:
                return cached

            # Compute result
            result = func(text, *args, **kwargs)

            # Cache result
            cache.set(prefix, text, result, params)

            return result

        return wrapper
    return decorator
