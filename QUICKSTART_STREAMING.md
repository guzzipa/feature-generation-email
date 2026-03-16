# 🚀 Streaming Quick Start Guide

Get the streaming system running in 3 minutes!

---

## What is Streaming Enrichment?

Instead of processing emails synchronously (wait for response), streaming allows you to:
- **Submit jobs** to a queue
- **Workers** process jobs in parallel
- **Poll for results** when ready
- **Scale horizontally** by adding more workers

**Perfect for**: Batch processing, async enrichment, high-volume workloads

---

## 1️⃣ Install Dependencies

```bash
# Install Redis async support
pip install redis[asyncio]>=5.0.0

# Or install all requirements
pip install -r requirements.txt
```

---

## 2️⃣ Start Redis

```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:7-alpine

# Verify
redis-cli ping
# Expected: PONG
```

---

## 3️⃣ Start Workers

Open a terminal and start workers:

```bash
# Start 4 workers (recommended)
python streaming.py worker --workers 4
```

You should see:
```
INFO - 🚀 Starting 4 workers...
INFO - 🚀 Starting worker worker-0
INFO - 🚀 Starting worker worker-1
INFO - 🚀 Starting worker worker-2
INFO - 🚀 Starting worker worker-3
```

**Leave this terminal running!** Workers will process jobs in the background.

---

## 4️⃣ Submit Jobs

Open a **new terminal** and submit emails:

```bash
# Submit single email
python streaming.py submit user@example.com

# Output:
# ✅ Submitted job: a1b2c3d4-e5f6-7890-abcd-ef1234567890
# Email: user@example.com
```

Check the workers terminal - you should see:
```
INFO - 📧 Processing user@example.com (job a1b2c3d4-...)
INFO - ✅ Completed user@example.com (job a1b2c3d4-...)
```

---

## 5️⃣ Monitor Stream

Open a **third terminal** to monitor:

```bash
python streaming.py monitor
```

Output:
```
============================================================
📊 STREAM STATISTICS
============================================================

🔄 Stream Queue:
  Pending: 3

✅ Processing Metrics:
  jobs_submitted: 15
  jobs_completed: 12
  jobs_failed: 0

📦 Results: 12
❌ Failed (DLQ): 0
============================================================
```

Press `Ctrl+C` to stop monitoring.

---

## 6️⃣ Programmatic Usage

### Submit Jobs from Python

```python
import asyncio
import redis.asyncio as redis
from streaming import StreamProducer

async def submit_job():
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    job_id = await producer.submit_job(
        email='user@example.com',
        ip_address='181.45.123.45'
    )

    print(f"Submitted: {job_id}")
    await redis_client.close()

# Run
asyncio.run(submit_job())
```

### Submit Batch

```python
async def submit_batch():
    redis_client = redis.Redis(...)
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

### Get Results

```python
import json

async def get_result(job_id):
    redis_client = redis.Redis(...)

    result_key = f"result:{job_id}"
    result = await redis_client.get(result_key)

    if result:
        data = json.loads(result)
        print(f"Status: {data['job']['status']}")
        print(f"Trust Score: {data['result']['summary']['trust_score']}")
    else:
        print("Result not ready yet")

    await redis_client.close()

asyncio.run(get_result('a1b2c3d4-e5f6-7890-abcd-ef1234567890'))
```

---

## 7️⃣ Integration with REST API

Combine streaming with your API for async enrichment:

```python
from fastapi import FastAPI
from streaming import StreamProducer
import redis.asyncio as redis

app = FastAPI()

@app.post("/enrich/async")
async def enrich_async(email: str):
    """Submit job for async enrichment"""
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
        "poll_url": f"/job/{job_id}"
    }

@app.get("/job/{job_id}")
async def get_job(job_id: str):
    """Poll for job result"""
    redis_client = redis.Redis(...)

    result_key = f"result:{job_id}"
    result = await redis_client.get(result_key)

    await redis_client.close()

    if result:
        return json.loads(result)
    else:
        return {"status": "pending"}
```

Start API:
```bash
uvicorn api_streaming:app --reload --port 8000
```

Test:
```bash
# Submit job
curl -X POST http://localhost:8000/enrich/async?email=user@example.com

# Output:
# {
#   "job_id": "a1b2c3d4-...",
#   "status": "submitted",
#   "poll_url": "/job/a1b2c3d4-..."
# }

# Poll for result (wait a few seconds)
curl http://localhost:8000/job/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## 🎯 Next Steps

### Scale Workers

```bash
# Add more workers dynamically
python streaming.py worker --workers 8
```

### Docker Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  worker:
    build: .
    command: python streaming.py worker --workers 4
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
    deploy:
      replicas: 2
```

Run:
```bash
docker-compose up -d
docker-compose scale worker=4
```

### Production Configuration

Add to `.env`:

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Streaming config
STREAM_BATCH_SIZE=10
STREAM_BLOCK_MS=5000
MAX_RETRIES=3
```

---

## 📊 Performance Comparison

| Metric | REST API (v3.5) | Streaming (v4.0) |
|--------|-----------------|------------------|
| **Throughput** | ~300/hour | ~4,500/hour |
| **Response Time** | 2-5s (blocking) | Async (non-blocking) |
| **Scalability** | Vertical only | Horizontal + Vertical |
| **Best For** | Real-time queries | Batch processing |

---

## 🐛 Troubleshooting

### "Could not connect to Redis"

```bash
# Check Redis is running
redis-cli ping

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis # Linux
```

### Workers not processing jobs

```bash
# Check stream
redis-cli XINFO STREAM email:enrichment:stream

# Check workers
ps aux | grep streaming.py

# Restart workers
pkill -f "streaming.py worker"
python streaming.py worker --workers 4
```

### Jobs stuck in queue

```bash
# Check consumer group
redis-cli XINFO GROUPS email:enrichment:stream

# Check pending messages
redis-cli XPENDING email:enrichment:stream enrichment-workers
```

---

## 📚 Full Documentation

- **Complete Guide**: [STREAMING.md](STREAMING.md)
- **API Reference**: [API.md](API.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**You're now running Real-time Streaming Enrichment v4.0!** 🎉

Start workers, submit jobs, and scale horizontally for massive throughput.

**Throughput**: Process up to 4,500 emails/hour with distributed workers
