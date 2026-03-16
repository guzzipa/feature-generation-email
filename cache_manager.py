#!/usr/bin/env python3
"""
Redis Cache Manager for Email Enrichment Pipeline

Caches API responses to:
- Reduce API calls (save rate limits)
- Improve response time
- Reduce costs (commercial APIs)

Cache Strategy:
- OSINT data: 30 days (stable, rarely changes)
- Commercial APIs: 7 days (moderate TTL)
- Additional sources: 14 days
- Free sources: 30 days
- Behavioral data: 1 day (frequent updates)

Version: 3.4.0
"""

import os
import json
import logging
import hashlib
from typing import Dict, Any, Optional
from datetime import timedelta
from dotenv import load_dotenv

# Try to import Redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

load_dotenv()
logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis-based cache manager with intelligent TTL strategies.

    Falls back gracefully if Redis is not available.
    """

    # Cache TTL in seconds
    TTL_STRATEGIES = {
        'osint': int(timedelta(days=30).total_seconds()),      # GitHub, Gravatar, HIBP
        'commercial': int(timedelta(days=7).total_seconds()),  # Hunter, EmailRep, Clearbit
        'additional': int(timedelta(days=14).total_seconds()), # WHOIS, IPQS, Twitter
        'free': int(timedelta(days=30).total_seconds()),       # IP Intel, patterns
        'behavioral': int(timedelta(days=1).total_seconds()),  # Platform behavior
        'features': int(timedelta(days=7).total_seconds()),    # Engineered features
    }

    def __init__(
        self,
        enabled: bool = True,
        host: str = None,
        port: int = None,
        db: int = None,
        password: str = None,
        prefix: str = "email_enrich"
    ):
        """
        Initialize cache manager.

        Args:
            enabled: Enable/disable caching
            host: Redis host (default from env or localhost)
            port: Redis port (default from env or 6379)
            db: Redis database number (default 0)
            password: Redis password (optional)
            prefix: Cache key prefix
        """
        self.enabled = enabled and REDIS_AVAILABLE
        self.prefix = prefix
        self.redis_client = None

        if not REDIS_AVAILABLE:
            logger.warning("Redis not installed. Caching disabled. Install with: pip install redis")
            self.enabled = False
            return

        if not self.enabled:
            logger.info("Cache disabled by configuration")
            return

        # Load Redis configuration
        host = host or os.getenv('REDIS_HOST', 'localhost')
        port = port or int(os.getenv('REDIS_PORT', 6379))
        db = db or int(os.getenv('REDIS_DB', 0))
        password = password or os.getenv('REDIS_PASSWORD')

        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,  # Automatically decode bytes to strings
                socket_timeout=5,
                socket_connect_timeout=5,
            )

            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Redis cache connected: {host}:{port}")

        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
            self.redis_client = None

    def _make_key(self, email: str, source: str, suffix: str = "") -> str:
        """
        Generate cache key.

        Args:
            email: Email address
            source: Data source (osint, commercial, etc)
            suffix: Additional suffix (optional)

        Returns:
            Cache key string
        """
        # Hash email for privacy (don't store raw emails in keys)
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:16]

        key_parts = [self.prefix, source, email_hash]
        if suffix:
            key_parts.append(suffix)

        return ":".join(key_parts)

    def get(self, email: str, source: str, suffix: str = "") -> Optional[Dict[str, Any]]:
        """
        Get cached data.

        Args:
            email: Email address
            source: Data source type
            suffix: Additional suffix

        Returns:
            Cached data or None if not found
        """
        if not self.enabled or not self.redis_client:
            return None

        try:
            key = self._make_key(email, source, suffix)
            cached = self.redis_client.get(key)

            if cached:
                logger.debug(f"[Cache HIT] {source} for {email[:10]}...")
                return json.loads(cached)
            else:
                logger.debug(f"[Cache MISS] {source} for {email[:10]}...")
                return None

        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return None

    def set(
        self,
        email: str,
        source: str,
        data: Dict[str, Any],
        ttl: int = None,
        suffix: str = ""
    ) -> bool:
        """
        Cache data.

        Args:
            email: Email address
            source: Data source type
            data: Data to cache
            ttl: Time to live in seconds (uses default if not specified)
            suffix: Additional suffix

        Returns:
            True if cached successfully
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            key = self._make_key(email, source, suffix)

            # Use default TTL for source if not specified
            if ttl is None:
                ttl = self.TTL_STRATEGIES.get(source, self.TTL_STRATEGIES['features'])

            # Serialize and cache
            serialized = json.dumps(data, default=str)
            self.redis_client.setex(key, ttl, serialized)

            logger.debug(f"[Cache SET] {source} for {email[:10]}... (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False

    def invalidate(self, email: str, source: str = None, suffix: str = "") -> int:
        """
        Invalidate cache for email.

        Args:
            email: Email address
            source: Data source (if None, invalidates all sources for email)
            suffix: Additional suffix

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis_client:
            return 0

        try:
            if source:
                # Invalidate specific source
                key = self._make_key(email, source, suffix)
                deleted = self.redis_client.delete(key)
                logger.info(f"[Cache INVALIDATE] {source} for {email}")
                return deleted
            else:
                # Invalidate all sources for email
                email_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:16]
                pattern = f"{self.prefix}:*:{email_hash}*"

                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"[Cache INVALIDATE] All sources for {email} ({deleted} keys)")
                    return deleted
                return 0

        except Exception as e:
            logger.error(f"Cache INVALIDATE error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled or not self.redis_client:
            return {
                'enabled': False,
                'available': REDIS_AVAILABLE,
                'reason': 'Redis not available' if not REDIS_AVAILABLE else 'Cache disabled'
            }

        try:
            info = self.redis_client.info()

            # Count keys by source
            source_counts = {}
            for source in self.TTL_STRATEGIES.keys():
                pattern = f"{self.prefix}:{source}:*"
                keys = self.redis_client.keys(pattern)
                source_counts[source] = len(keys)

            return {
                'enabled': True,
                'connected': True,
                'total_keys': info.get('db0', {}).get('keys', 0),
                'memory_used': info.get('used_memory_human'),
                'uptime_days': info.get('uptime_in_days'),
                'source_counts': source_counts,
                'ttl_strategies': self.TTL_STRATEGIES,
            }

        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {
                'enabled': True,
                'connected': False,
                'error': str(e)
            }

    def flush_all(self, confirm: bool = False) -> bool:
        """
        Flush all cache data (DANGEROUS).

        Args:
            confirm: Must be True to actually flush

        Returns:
            True if flushed successfully
        """
        if not confirm:
            logger.warning("flush_all() called without confirm=True. Ignoring.")
            return False

        if not self.enabled or not self.redis_client:
            return False

        try:
            # Only flush keys with our prefix
            pattern = f"{self.prefix}:*"
            keys = self.redis_client.keys(pattern)

            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.warning(f"[Cache FLUSH] Deleted {deleted} keys")
                return True
            return False

        except Exception as e:
            logger.error(f"Cache FLUSH error: {e}")
            return False


# Singleton instance
_cache_instance = None


def get_cache_manager(
    enabled: bool = None,
    **kwargs
) -> CacheManager:
    """
    Get or create cache manager singleton.

    Args:
        enabled: Enable/disable caching (defaults to env ENABLE_CACHE)
        **kwargs: Additional arguments for CacheManager

    Returns:
        CacheManager instance
    """
    global _cache_instance

    if _cache_instance is None:
        # Default to enabled if not specified
        if enabled is None:
            enabled = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'

        _cache_instance = CacheManager(enabled=enabled, **kwargs)

    return _cache_instance


def main():
    """CLI for testing cache."""
    import sys

    cache = get_cache_manager(enabled=True)

    if len(sys.argv) < 2:
        print("Cache Manager CLI")
        print("\nCommands:")
        print("  stats                    - Show cache statistics")
        print("  test <email>             - Test cache with email")
        print("  invalidate <email>       - Invalidate cache for email")
        print("  flush                    - Flush all cache (requires confirmation)")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stats":
        stats = cache.get_stats()
        print("\n" + "=" * 60)
        print("CACHE STATISTICS")
        print("=" * 60)
        print(json.dumps(stats, indent=2))
        print("=" * 60 + "\n")

    elif command == "test" and len(sys.argv) >= 3:
        email = sys.argv[2]

        # Test SET
        test_data = {
            'email': email,
            'test': True,
            'timestamp': 'now'
        }

        print(f"\n[TEST] Caching test data for: {email}")
        cache.set(email, 'osint', test_data)

        # Test GET
        cached = cache.get(email, 'osint')
        if cached:
            print(f"[TEST] ✅ Retrieved from cache:")
            print(json.dumps(cached, indent=2))
        else:
            print(f"[TEST] ❌ Failed to retrieve from cache")

    elif command == "invalidate" and len(sys.argv) >= 3:
        email = sys.argv[2]
        deleted = cache.invalidate(email)
        print(f"\n[INVALIDATE] Deleted {deleted} keys for: {email}\n")

    elif command == "flush":
        print("\n⚠️  WARNING: This will delete ALL cached data!")
        confirm = input("Type 'yes' to confirm: ")

        if confirm.lower() == 'yes':
            cache.flush_all(confirm=True)
            print("✅ Cache flushed\n")
        else:
            print("❌ Cancelled\n")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
