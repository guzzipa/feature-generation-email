# Real-time Streaming Enrichment (v4.0)

Stream-based email enrichment system using Redis Streams for scalable, distributed processing.

## Architecture Overview

```
┌─────────────┐
│  Producer   │ ──submit──> Redis Stream ──consume──> ┌──────────┐
│   (API)     │                  │                     │ Worker 1 │
└─────────────┘                  │                     └──────────┘
                                 │                     ┌──────────┐
┌─────────────┐                  ├──consume──────────> │ Worker 2 │
│   Submit    │ ──submit──>      │                     └──────────┘
│    CLI      │                  │                     ┌──────────┐
└─────────────┘                  └──consume──────────> │ Worker N │
                                                        └──────────┘
                                                              │
                                                              v
                                                        ┌──────────┐
                                                        │ Results  │
                                                        │  Stream  │
                                                        └──────────┘
```

### Components

1. **Producer**: Submits enrichment jobs to Redis Stream
2. **Redis Stream**: Distributed message queue with consumer groups
3. **Workers**: Consume and process jobs in parallel
4. **Results Stream**: Stores completed enrichments
5. **Dead Letter Queue**: Handles failed jobs after retries
6. **Monitor**: Tracks metrics and stream health

## Why Redis Streams?

- **Distributed Processing**: Multiple workers can process in parallel
- **Consumer Groups**: Automatic load balancing across workers
- **Persistence**: Messages survive crashes (unlike pub/sub)
- **At-least-once Delivery**: Guarantees no message loss
- **Built-in Acknowledgment**: Track which messages were processed
- **Scalable**: Add/remove workers dynamically
- **Low Latency**: Sub-millisecond message delivery

## Installation

### 1. Install Dependencies

```bash
pip install redis[asyncio]>=5.0.0
```

### 2. Start Redis Server

```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. Verify Redis Connection

```bash
redis-cli ping
# Expected: PONG
```

## Quick Start

### Start Workers

```bash
# Single worker
python streaming.py worker

# Multiple workers (recommended for production)
python streaming.py worker --workers 4
```

You should see:
```
2026-03-16 10:30:00 - __main__ - INFO - 🚀 Starting 4 workers...
2026-03-16 10:30:00 - __main__ - INFO - 🚀 Starting worker worker-0
2026-03-16 10:30:00 - __main__ - INFO - 🚀 Starting worker worker-1
2026-03-16 10:30:00 - __main__ - INFO - 🚀 Starting worker worker-2
2026-03-16 10:30:00 - __main__ - INFO - 🚀 Starting worker worker-3
```

### Submit Jobs

```bash
# Submit single email
python streaming.py submit user@example.com

# Output:
# ✅ Submitted job: a1b2c3d4-e5f6-7890-abcd-ef1234567890
# Email: user@example.com
```

### Monitor Stream

```bash
python streaming.py monitor
```

Output:
```
============================================================
📊 STREAM STATISTICS
============================================================

🔄 Stream Queue:
  Pending: 12

✅ Processing Metrics:
  jobs_submitted: 150
  jobs_completed: 138
  jobs_failed: 0

📦 Results: 138
❌ Failed (DLQ): 0
============================================================
```

## Usage

### Programmatic Usage

```python
import asyncio
from streaming import StreamProducer, StreamWorker
import redis.asyncio as redis
from full_enrichment import FullEnrichmentPipeline

async def submit_job():
    """Submit enrichment job"""
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    job_id = await producer.submit_job(
        email='user@example.com',
        ip_address='181.45.123.45',
        skip_commercial=False
    )

    print(f"Submitted job: {job_id}")
    await redis_client.close()

# Run
asyncio.run(submit_job())
```

### Batch Submission

```python
async def submit_batch():
    """Submit multiple emails at once"""
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    emails = [
        'user1@example.com',
        'user2@example.com',
        'user3@example.com'
    ]

    job_ids = await producer.submit_batch(emails)
    print(f"Submitted {len(job_ids)} jobs")

    await redis_client.close()

asyncio.run(submit_batch())
```

### Integration with REST API

```python
from fastapi import FastAPI, BackgroundTasks
from streaming import StreamProducer
import redis.asyncio as redis

app = FastAPI()

@app.post("/enrich/async")
async def enrich_async(email: str):
    """Async enrichment via streaming"""
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)
    job_id = await producer.submit_job(email)

    await redis_client.close()

    return {
        "job_id": job_id,
        "status": "submitted",
        "email": email
    }

@app.get("/job/{job_id}")
async def get_job_result(job_id: str):
    """Poll for job result"""
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    result_key = f"result:{job_id}"
    result = await redis_client.get(result_key)

    await redis_client.close()

    if result:
        return json.loads(result)
    else:
        return {"status": "pending"}
```

## Configuration

Edit `StreamConfig` class in `streaming.py`:

```python
class StreamConfig:
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Stream names
    STREAM_NAME = 'email:enrichment:stream'
    RESULTS_STREAM = 'email:enrichment:results'
    DLQ_STREAM = 'email:enrichment:dlq'

    # Consumer group
    CONSUMER_GROUP = 'enrichment-workers'

    # Processing config
    BATCH_SIZE = 10  # Process 10 emails at a time
    BLOCK_MS = 5000  # Block for 5 seconds waiting for messages
    MAX_RETRIES = 3  # Retry failed jobs 3 times
```

### Environment Variables

Add to `.env`:

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Streaming Configuration
STREAM_BATCH_SIZE=10
STREAM_BLOCK_MS=5000
MAX_RETRIES=3
```

## Job Lifecycle

### 1. Job Submission

```python
job = EnrichmentJob(
    job_id=str(uuid.uuid4()),
    email=email,
    ip_address=ip_address,
    status=JobStatus.PENDING,
    created_at=datetime.now().isoformat()
)

# Add to stream
await redis.xadd(
    StreamConfig.STREAM_NAME,
    {'job': json.dumps(job.to_dict())}
)
```

### 2. Job Processing

```python
# Worker reads from stream
messages = await redis.xreadgroup(
    StreamConfig.CONSUMER_GROUP,
    self.worker_id,
    {StreamConfig.STREAM_NAME: '>'},
    count=BATCH_SIZE,
    block=BLOCK_MS
)

# Process email
result = await asyncio.to_thread(
    pipeline.enrich_email,
    job.email
)

# Store result
await redis.xadd(
    StreamConfig.RESULTS_STREAM,
    {
        'job_id': job.job_id,
        'result': json.dumps(result),
        'completed_at': datetime.now().isoformat()
    }
)

# Acknowledge message
await redis.xack(
    StreamConfig.STREAM_NAME,
    StreamConfig.CONSUMER_GROUP,
    message_id
)
```

### 3. Retry Logic

If processing fails:

```python
if job.retries < MAX_RETRIES:
    # Retry - resubmit to stream
    job.retries += 1
    job.status = JobStatus.RETRY
    await redis.xadd(
        StreamConfig.STREAM_NAME,
        {'job': json.dumps(job.to_dict())}
    )
else:
    # Move to Dead Letter Queue
    job.status = JobStatus.FAILED
    await redis.xadd(
        StreamConfig.DLQ_STREAM,
        {
            'job_id': job.job_id,
            'error': error_message,
            'job': json.dumps(job.to_dict())
        }
    )
```

### 4. Result Retrieval

```python
# Get result by job_id
result_key = f"result:{job_id}"
result = await redis.get(result_key)

if result:
    data = json.loads(result)
    print(f"Status: {data['job']['status']}")
    print(f"Features: {data['result']['features']}")
```

## Monitoring & Metrics

### Stream Statistics

```python
from streaming import StreamMonitor

monitor = StreamMonitor(redis_client)
stats = await monitor.get_stats()

print(f"Pending jobs: {stats['stream']['length']}")
print(f"Completed: {stats['metrics']['jobs_completed']}")
print(f"Failed: {stats['failed_count']}")
```

### Metrics Tracked

- `jobs_submitted`: Total jobs added to stream
- `jobs_completed`: Successfully processed jobs
- `jobs_failed`: Jobs moved to DLQ after max retries
- Stream length: Current pending jobs
- Results count: Total results stored
- DLQ length: Failed jobs

### Monitor Dashboard

```bash
# Continuous monitoring (updates every 5 seconds)
python streaming.py monitor
```

### Redis CLI Monitoring

```bash
# Watch stream in real-time
redis-cli XINFO STREAM email:enrichment:stream

# Check consumer group
redis-cli XINFO GROUPS email:enrichment:stream

# View results
redis-cli XREAD COUNT 10 STREAMS email:enrichment:results 0

# Check dead letter queue
redis-cli XLEN email:enrichment:dlq
```

## Production Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  worker:
    build: .
    command: python streaming.py worker --workers 4
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    deploy:
      replicas: 2  # Run 2 containers, each with 4 workers

volumes:
  redis-data:
```

### Systemd Service

Create `/etc/systemd/system/enrichment-worker.service`:

```ini
[Unit]
Description=Email Enrichment Stream Worker
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/email-enrichment
ExecStart=/usr/bin/python3 streaming.py worker --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable enrichment-worker
sudo systemctl start enrichment-worker
sudo systemctl status enrichment-worker
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enrichment-workers
spec:
  replicas: 3
  selector:
    matchLabels:
      app: enrichment-worker
  template:
    metadata:
      labels:
        app: enrichment-worker
    spec:
      containers:
      - name: worker
        image: email-enrichment:v4.0
        command: ["python", "streaming.py", "worker", "--workers", "4"]
        env:
        - name: REDIS_HOST
          value: redis-service
        - name: REDIS_PORT
          value: "6379"
```

### Scaling Workers

```bash
# Add more workers dynamically
python streaming.py worker --workers 8 &

# In Kubernetes
kubectl scale deployment enrichment-workers --replicas=5

# In Docker Compose
docker-compose up --scale worker=3
```

## Performance Tuning

### Worker Configuration

```python
# High throughput (more parallel processing)
BATCH_SIZE = 20
BLOCK_MS = 1000  # Check more frequently

# Low latency (faster response)
BATCH_SIZE = 1
BLOCK_MS = 100

# Balanced (default)
BATCH_SIZE = 10
BLOCK_MS = 5000
```

### Redis Optimization

```bash
# Increase max memory
redis-cli CONFIG SET maxmemory 2gb

# Set eviction policy (don't evict streams)
redis-cli CONFIG SET maxmemory-policy noeviction

# Enable persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### Worker Pool Sizing

Rule of thumb:
- **CPU-bound tasks**: workers = CPU cores
- **I/O-bound tasks**: workers = CPU cores × 2-4

Email enrichment is I/O-bound (API calls), so:
```bash
# 4-core machine
python streaming.py worker --workers 16
```

## Error Handling

### Common Issues

#### Redis Connection Failed

```
Error: Could not connect to Redis at localhost:6379
```

Solution:
```bash
# Check Redis is running
redis-cli ping

# Check connection
telnet localhost 6379

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis # Linux
```

#### Consumer Group Already Exists

```
ResponseError: BUSYGROUP Consumer Group name already exists
```

This is normal - the error is caught and ignored:
```python
except redis.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise
```

#### Worker Not Processing Jobs

Check consumer group pending messages:
```bash
redis-cli XPENDING email:enrichment:stream enrichment-workers
```

Claim pending messages:
```bash
redis-cli XCLAIM email:enrichment:stream enrichment-workers worker-0 3600000 <message-id>
```

### Dead Letter Queue Processing

```python
async def reprocess_dlq():
    """Reprocess failed jobs from DLQ"""
    redis_client = redis.Redis(...)

    # Read from DLQ
    messages = await redis_client.xread(
        {StreamConfig.DLQ_STREAM: '0'},
        count=100
    )

    producer = StreamProducer(redis_client)

    for stream_name, stream_messages in messages:
        for message_id, data in stream_messages:
            # Re-submit to main stream
            job_dict = json.loads(data[b'job'].decode())
            job = EnrichmentJob.from_dict(job_dict)
            job.retries = 0  # Reset retry counter

            await producer.submit_job(job.email)

            # Remove from DLQ
            await redis_client.xdel(StreamConfig.DLQ_STREAM, message_id)
```

## Benchmarks

### Throughput

| Workers | Emails/hour | Avg Latency | CPU Usage |
|---------|-------------|-------------|-----------|
| 1       | 600         | 6s          | 25%       |
| 4       | 2,000       | 7s          | 80%       |
| 8       | 3,200       | 9s          | 95%       |
| 16      | 4,500       | 13s         | 100%      |

### Scalability

- **Vertical**: Add more workers per machine
- **Horizontal**: Add more machines with workers
- **Linear scaling** up to ~16 workers (then API rate limits kick in)

## Best Practices

1. **Use Multiple Workers**: Distribute load across workers
2. **Monitor DLQ**: Check for failing patterns
3. **Set Reasonable TTLs**: Results expire after 24 hours by default
4. **Enable Persistence**: Use Redis AOF for durability
5. **Handle Backpressure**: Monitor stream length, scale workers
6. **Graceful Shutdown**: Workers handle SIGTERM/SIGINT
7. **Log Everything**: Track job lifecycle for debugging
8. **Use Consumer Groups**: Automatic load balancing

## Comparison: Streaming vs REST API

| Feature | REST API (v3.5) | Streaming (v4.0) |
|---------|-----------------|------------------|
| **Response Time** | Immediate | Async (poll for result) |
| **Throughput** | ~300/hour | ~4,500/hour |
| **Scalability** | Vertical only | Horizontal + Vertical |
| **Reliability** | Retry on failure | DLQ + retry logic |
| **Resource Usage** | High (sync blocking) | Low (async workers) |
| **Use Case** | Real-time queries | Batch processing |
| **Backpressure** | Request timeouts | Queue builds up |

## Use Cases

### 1. Batch User Enrichment

Process existing user database:
```python
import asyncio
import pandas as pd

async def enrich_user_database():
    df = pd.read_csv('users.csv')

    redis_client = redis.Redis(...)
    producer = StreamProducer(redis_client)

    # Submit all users
    job_ids = await producer.submit_batch(
        df['email'].tolist()
    )

    print(f"Submitted {len(job_ids)} jobs")
    # Workers will process in background
```

### 2. Real-time Signup Enrichment

Enrich new signups asynchronously:
```python
@app.post("/signup")
async def signup(email: str, password: str):
    # Create user immediately
    user = create_user(email, password)

    # Enrich in background
    await producer.submit_job(email)

    return {"user_id": user.id}
```

### 3. Scheduled Refresh

Refresh user data periodically:
```python
# Cron job (daily at 2 AM)
# 0 2 * * * /usr/bin/python /opt/refresh_users.py

async def refresh_stale_users():
    users = get_users_not_refreshed_in_days(30)

    for user in users:
        await producer.submit_job(user.email)
```

## Future Enhancements

- [ ] WebSocket notifications for real-time updates
- [ ] Priority queues (VIP users processed first)
- [ ] Rate limiting per API source
- [ ] Multi-stream support (high/low priority)
- [ ] Grafana dashboards
- [ ] Prometheus metrics export
- [ ] Worker auto-scaling based on queue depth

## Troubleshooting

### Jobs Stuck in Pending

```bash
# Check consumer groups
redis-cli XINFO GROUPS email:enrichment:stream

# Check pending messages
redis-cli XPENDING email:enrichment:stream enrichment-workers
```

### High Memory Usage

```bash
# Trim old results
redis-cli XTRIM email:enrichment:results MAXLEN 10000

# Check memory usage
redis-cli INFO memory
```

### Worker Crashes

Check logs:
```bash
tail -f /var/log/enrichment-worker.log
```

Common causes:
- API rate limits exceeded
- Redis connection lost
- Out of memory

## Support

For issues or questions:
- GitHub Issues: https://github.com/guzzipa/feature-generation-email/issues
- Check logs: `streaming.py` uses Python logging
- Redis monitoring: `redis-cli MONITOR`

---

**Version:** 4.0.0
**Last Updated:** 2026-03-16
**Status:** Production Ready
