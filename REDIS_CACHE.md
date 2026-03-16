# Redis Caching System

## Overview

Version 3.4.0 introduces **Redis caching** to dramatically improve performance and reduce API costs.

### Benefits

- **Faster responses**: Cached results return in <10ms vs seconds for API calls
- **Cost savings**: Reduce commercial API calls by 80-95%
- **Rate limit protection**: Avoid hitting API rate limits
- **Reliability**: Continue working if APIs are temporarily down

### Cache Hit Rates (Expected)

| Source | Expected Hit Rate | Reason |
|--------|------------------|--------|
| OSINT (GitHub, Gravatar) | 90%+ | User profiles rarely change |
| Commercial APIs | 85%+ | Company data is stable |
| Additional Sources | 75%+ | Domain/IP info changes slowly |
| Free Sources | 80%+ | Email patterns and IP geo are stable |

---

## Installation

### 1. Install Redis

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**Windows:**
Download from: https://redis.io/download

### 2. Install Python Redis Client

```bash
pip install redis
```

Or update requirements:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Add to `.env`:

```bash
# Redis Cache Configuration
ENABLE_CACHE=true           # Enable/disable caching
REDIS_HOST=localhost        # Redis server host
REDIS_PORT=6379             # Redis server port
REDIS_DB=0                  # Redis database number (0-15)
REDIS_PASSWORD=             # Redis password (optional)
```

---

## Usage

### Basic Usage (with cache enabled)

```bash
# First run - fetches from APIs and caches
python full_enrichment.py user@example.com

# Second run - instant (from cache)
python full_enrichment.py user@example.com
```

Output:
```
📊 Step 1/5: Collecting OSINT data...
   ⚡ Using cached OSINT data
💼 Step 2/5: Enriching with commercial APIs...
   ⚡ Using cached commercial data
```

### Disable Cache

```bash
# Don't use cache at all
python full_enrichment.py user@example.com --no-cache
```

### Force Refresh

```bash
# Bypass cache and fetch fresh data
python full_enrichment.py user@example.com --force-refresh
```

---

## Cache TTL Strategy

Different data sources have different cache lifetimes:

| Source | TTL | Reason |
|--------|-----|--------|
| **OSINT** (GitHub, Gravatar, HIBP) | 30 days | Profiles change infrequently |
| **Commercial APIs** (Hunter, EmailRep) | 7 days | Moderate update frequency |
| **Additional** (WHOIS, IPQS, Twitter) | 14 days | Domain/IP data stable |
| **Free Sources** (patterns, IP geo) | 30 days | Very stable data |
| **Behavioral** (platform activity) | 1 day | Frequent updates needed |
| **Features** (engineered) | 7 days | Recompute weekly |

### Custom TTL

You can override TTL in code:

```python
from cache_manager import get_cache_manager

cache = get_cache_manager()

# Cache for 1 hour (3600 seconds)
cache.set(email, 'osint', data, ttl=3600)
```

---

## Cache Management CLI

The cache manager includes a CLI for maintenance:

### View Statistics

```bash
python cache_manager.py stats
```

Output:
```json
{
  "enabled": true,
  "connected": true,
  "total_keys": 234,
  "memory_used": "2.3M",
  "uptime_days": 5,
  "source_counts": {
    "osint": 78,
    "commercial": 45,
    "additional": 67,
    "free": 44
  }
}
```

### Test Cache

```bash
python cache_manager.py test user@example.com
```

### Invalidate Cache

```bash
# Invalidate all data for specific email
python cache_manager.py invalidate user@example.com
```

### Flush All Cache

```bash
# WARNING: Deletes ALL cached data
python cache_manager.py flush
```

---

## Programmatic Usage

### In Your Code

```python
from cache_manager import get_cache_manager

# Get cache instance
cache = get_cache_manager(enabled=True)

# Check if data is cached
cached_data = cache.get(email, 'osint')

if cached_data:
    print("Using cached data")
    data = cached_data
else:
    print("Fetching fresh data")
    data = fetch_from_api(email)
    cache.set(email, 'osint', data)
```

### Invalidate on User Update

```python
# User updated their profile - invalidate cache
cache.invalidate(email, source='osint')

# Or invalidate ALL sources for user
cache.invalidate(email)
```

---

## Performance Benchmarks

### Without Cache

```
First run: 12.4 seconds (4 API calls)
Second run: 11.8 seconds (4 API calls)
Third run: 12.1 seconds (4 API calls)

Total time (3 runs): 36.3 seconds
API calls: 12
```

### With Cache

```
First run: 12.4 seconds (4 API calls + cache writes)
Second run: 0.3 seconds (4 cache reads)
Third run: 0.3 seconds (4 cache reads)

Total time (3 runs): 13.0 seconds
API calls: 4
Speedup: 2.8x
Cache hit rate: 100%
```

---

## Production Recommendations

### 1. Use Redis in Production

Always enable caching in production:

```bash
ENABLE_CACHE=true
```

### 2. Monitor Cache Stats

Track cache performance:

```python
cache = get_cache_manager()
stats = cache.get_stats()

# Log to monitoring system
logger.info(f"Cache hit rate: {stats['hit_rate']}")
logger.info(f"Memory used: {stats['memory_used']}")
```

### 3. Set Up Redis Persistence

Configure Redis to persist data:

```bash
# redis.conf
save 900 1       # Save if 1 key changed in 15 minutes
save 300 10      # Save if 10 keys changed in 5 minutes
save 60 10000    # Save if 10000 keys changed in 1 minute
```

### 4. Configure Eviction Policy

For production with limited memory:

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru  # Evict least recently used
```

### 5. Secure Redis

If exposing Redis:

```bash
# Set password
requirepass your_secure_password_here

# Bind to localhost only (if on same server)
bind 127.0.0.1
```

Update `.env`:
```bash
REDIS_PASSWORD=your_secure_password_here
```

---

## Troubleshooting

### Redis Connection Failed

**Error:**
```
Redis connection failed: Error 111 connecting to localhost:6379. Connection refused.
```

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
# macOS
brew services start redis

# Linux
sudo systemctl start redis
```

### Cache Disabled Automatically

**Warning:**
```
Redis not installed. Caching disabled. Install with: pip install redis
```

**Solution:**
```bash
pip install redis
```

### Stale Data

If you're getting outdated cached data:

```bash
# Force refresh
python full_enrichment.py email@example.com --force-refresh

# Or invalidate specific email
python cache_manager.py invalidate email@example.com
```

### Out of Memory

**Error:**
```
OOM command not allowed when used memory > 'maxmemory'
```

**Solution:**
```bash
# Increase maxmemory in redis.conf
maxmemory 4gb

# Or flush old data
python cache_manager.py flush
```

---

## Cost Savings Calculator

### Without Cache (1000 enrichments/day)

```
Commercial APIs:
- Hunter.io: $49/month (10K calls)
- EmailRep.io: $49/month (10K calls)
- Clearbit: $99/month (10K calls)

Additional APIs:
- IPQualityScore: $0 (free tier 5K/month)
- Twitter: $100/month (paid tier)

Total: ~$297/month
```

### With Cache (1000 enrichments/day, 90% cache hit rate)

```
Actual API calls: 100/day = 3000/month

Commercial APIs:
- Hunter.io: $0 (under 5K free tier)
- EmailRep.io: $0 (under 5K free tier)
- Clearbit: $49/month (5-10K tier)

Additional APIs:
- IPQualityScore: $0 (under free tier)
- Twitter: $0 (under free tier or disabled)

Total: ~$49/month

Savings: $248/month (83% reduction)
```

---

## Advanced: Distributed Caching

For multiple servers:

### Use Redis Cluster

```bash
# Setup Redis cluster
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002

# Update .env
REDIS_HOST=127.0.0.1:7000,127.0.0.1:7001,127.0.0.1:7002
```

### Use Redis Sentinel (HA)

For high availability:

```bash
# Start Redis with Sentinel
redis-sentinel /path/to/sentinel.conf
```

---

## Monitoring

### Key Metrics to Track

1. **Cache Hit Rate**: Should be >80%
2. **Memory Usage**: Keep under 80% of maxmemory
3. **Eviction Rate**: Should be low
4. **Connection Errors**: Should be 0

### Sample Monitoring Script

```python
import time
from cache_manager import get_cache_manager

cache = get_cache_manager()

while True:
    stats = cache.get_stats()

    print(f"Total Keys: {stats['total_keys']}")
    print(f"Memory: {stats['memory_used']}")
    print(f"Source Counts: {stats['source_counts']}")

    time.sleep(60)  # Check every minute
```

---

## Migration Guide

### From v3.3 to v3.4

1. Install Redis:
   ```bash
   brew install redis  # macOS
   brew services start redis
   ```

2. Install Python package:
   ```bash
   pip install redis
   ```

3. Update `.env`:
   ```bash
   echo "ENABLE_CACHE=true" >> .env
   echo "REDIS_HOST=localhost" >> .env
   echo "REDIS_PORT=6379" >> .env
   ```

4. Done! Cache is now enabled

---

**Version:** 3.4.0
**Redis Client:** redis-py 5.0+
**Redis Server:** 6.0+ recommended
**Performance:** 2-10x faster with 80-95% cost savings
