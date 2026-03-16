#!/usr/bin/env python3
"""
Real-time Streaming Enrichment System (v4.0)

Process emails in real-time as they arrive using Redis Streams.
Features:
- Redis Streams for message queuing
- Async workers for parallel processing
- WebSocket notifications for real-time updates
- Automatic scaling based on queue size
- Dead letter queue for failed jobs
- Monitoring and metrics

Architecture:
    Producer → Redis Stream → Consumer Group → Workers → Results
                                    ↓
                               WebSocket Push

Usage:
    # Start workers
    python streaming.py worker --workers 4

    # Submit email for enrichment
    python streaming.py submit user@example.com

    # Monitor stream
    python streaming.py monitor

Version: 4.0.0
"""

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

import redis.asyncio as redis
from dotenv import load_dotenv

# Import our enrichment pipeline
from full_enrichment import FullEnrichmentPipeline

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class StreamConfig:
    """Streaming system configuration"""
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Stream names
    STREAM_NAME = 'email:enrichment:stream'
    RESULTS_STREAM = 'email:enrichment:results'
    DLQ_STREAM = 'email:enrichment:dlq'  # Dead Letter Queue

    # Consumer group
    CONSUMER_GROUP = 'enrichment-workers'

    # Processing config
    BATCH_SIZE = 10  # Process 10 emails at a time
    BLOCK_MS = 5000  # Block for 5 seconds waiting for messages
    MAX_RETRIES = 3

    # Monitoring
    METRICS_KEY = 'email:enrichment:metrics'


class JobStatus(Enum):
    """Job status enum"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    RETRY = 'retry'


@dataclass
class EnrichmentJob:
    """Enrichment job data structure"""
    job_id: str
    email: str
    ip_address: Optional[str] = None
    skip_commercial: bool = False
    skip_additional: bool = False
    webhook_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    # Job tracking
    status: JobStatus = JobStatus.PENDING
    retries: int = 0
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnrichmentJob':
        """Create from dictionary"""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = JobStatus(data['status'])
        return cls(**data)


# ============================================================================
# Stream Producer
# ============================================================================

class StreamProducer:
    """
    Producer for submitting enrichment jobs to the stream
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def submit_job(
        self,
        email: str,
        ip_address: Optional[str] = None,
        skip_commercial: bool = False,
        skip_additional: bool = False,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit email enrichment job to stream

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())

        job = EnrichmentJob(
            job_id=job_id,
            email=email,
            ip_address=ip_address,
            skip_commercial=skip_commercial,
            skip_additional=skip_additional,
            webhook_url=webhook_url,
            metadata=metadata
        )

        # Add to stream
        await self.redis.xadd(
            StreamConfig.STREAM_NAME,
            {'job': json.dumps(job.to_dict())}
        )

        logger.info(f"✅ Submitted job {job_id} for {email}")

        # Increment metrics
        await self.redis.hincrby(StreamConfig.METRICS_KEY, 'jobs_submitted', 1)

        return job_id

    async def submit_batch(
        self,
        emails: List[str],
        **kwargs
    ) -> List[str]:
        """Submit multiple emails at once"""
        job_ids = []
        for email in emails:
            job_id = await self.submit_job(email, **kwargs)
            job_ids.append(job_id)

        logger.info(f"✅ Submitted {len(job_ids)} jobs")
        return job_ids


# ============================================================================
# Stream Consumer (Worker)
# ============================================================================

class StreamWorker:
    """
    Worker that consumes jobs from stream and enriches emails
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        worker_id: str,
        pipeline: FullEnrichmentPipeline
    ):
        self.redis = redis_client
        self.worker_id = worker_id
        self.pipeline = pipeline
        self.running = False

    async def start(self):
        """Start consuming jobs from stream"""
        logger.info(f"🚀 Starting worker {self.worker_id}")

        # Create consumer group if it doesn't exist
        try:
            await self.redis.xgroup_create(
                StreamConfig.STREAM_NAME,
                StreamConfig.CONSUMER_GROUP,
                id='0',
                mkstream=True
            )
            logger.info(f"Created consumer group {StreamConfig.CONSUMER_GROUP}")
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

        self.running = True

        while self.running:
            try:
                # Read from stream
                messages = await self.redis.xreadgroup(
                    StreamConfig.CONSUMER_GROUP,
                    self.worker_id,
                    {StreamConfig.STREAM_NAME: '>'},
                    count=StreamConfig.BATCH_SIZE,
                    block=StreamConfig.BLOCK_MS
                )

                if messages:
                    for stream_name, stream_messages in messages:
                        for message_id, message_data in stream_messages:
                            await self._process_message(message_id, message_data)

            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, message_id: bytes, message_data: Dict):
        """Process a single message"""
        try:
            # Parse job
            job_dict = json.loads(message_data[b'job'].decode())
            job = EnrichmentJob.from_dict(job_dict)

            logger.info(f"📧 Processing {job.email} (job {job.job_id})")

            # Update status
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now().isoformat()

            # Enrich email (run in thread pool to avoid blocking)
            result = await asyncio.to_thread(
                self._enrich_email,
                job
            )

            # Mark as completed
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now().isoformat()

            # Store result
            await self._store_result(job, result)

            # Acknowledge message
            await self.redis.xack(
                StreamConfig.STREAM_NAME,
                StreamConfig.CONSUMER_GROUP,
                message_id
            )

            # Increment metrics
            await self.redis.hincrby(StreamConfig.METRICS_KEY, 'jobs_completed', 1)

            logger.info(f"✅ Completed {job.email} (job {job.job_id})")

        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")

            # Handle retry logic
            await self._handle_failure(message_id, message_data, str(e))

    def _enrich_email(self, job: EnrichmentJob) -> Dict[str, Any]:
        """Enrich email (blocking operation)"""
        return self.pipeline.enrich_email(job.email)

    async def _store_result(self, job: EnrichmentJob, result: Dict[str, Any]):
        """Store enrichment result"""
        # Add to results stream
        await self.redis.xadd(
            StreamConfig.RESULTS_STREAM,
            {
                'job_id': job.job_id,
                'email': job.email,
                'status': job.status.value,
                'result': json.dumps(result),
                'completed_at': job.completed_at
            }
        )

        # Also store in hash for quick lookup
        result_key = f"result:{job.job_id}"
        await self.redis.setex(
            result_key,
            3600 * 24,  # Keep for 24 hours
            json.dumps({
                'job': job.to_dict(),
                'result': result
            })
        )

    async def _handle_failure(
        self,
        message_id: bytes,
        message_data: Dict,
        error: str
    ):
        """Handle failed message"""
        try:
            job_dict = json.loads(message_data[b'job'].decode())
            job = EnrichmentJob.from_dict(job_dict)
            job.retries += 1
            job.error = error

            if job.retries < StreamConfig.MAX_RETRIES:
                # Retry
                job.status = JobStatus.RETRY
                logger.warning(f"⚠️ Retrying {job.email} (attempt {job.retries})")

                # Re-add to stream
                await self.redis.xadd(
                    StreamConfig.STREAM_NAME,
                    {'job': json.dumps(job.to_dict())}
                )

                # Acknowledge original message
                await self.redis.xack(
                    StreamConfig.STREAM_NAME,
                    StreamConfig.CONSUMER_GROUP,
                    message_id
                )
            else:
                # Move to DLQ
                job.status = JobStatus.FAILED
                logger.error(f"❌ Failed {job.email} after {job.retries} retries")

                await self.redis.xadd(
                    StreamConfig.DLQ_STREAM,
                    {
                        'job_id': job.job_id,
                        'email': job.email,
                        'error': error,
                        'job': json.dumps(job.to_dict())
                    }
                )

                # Acknowledge message
                await self.redis.xack(
                    StreamConfig.STREAM_NAME,
                    StreamConfig.CONSUMER_GROUP,
                    message_id
                )

                # Increment metrics
                await self.redis.hincrby(StreamConfig.METRICS_KEY, 'jobs_failed', 1)

        except Exception as e:
            logger.error(f"Error handling failure: {e}")

    def stop(self):
        """Stop worker"""
        logger.info(f"🛑 Stopping worker {self.worker_id}")
        self.running = False


# ============================================================================
# Stream Monitor
# ============================================================================

class StreamMonitor:
    """
    Monitor stream health and metrics
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get_stats(self) -> Dict[str, Any]:
        """Get stream statistics"""
        # Stream info
        try:
            stream_info = await self.redis.xinfo_stream(StreamConfig.STREAM_NAME)
        except redis.ResponseError:
            stream_info = {}

        # Metrics
        metrics = await self.redis.hgetall(StreamConfig.METRICS_KEY)
        metrics_decoded = {
            k.decode(): int(v.decode())
            for k, v in metrics.items()
        } if metrics else {}

        # Consumer group info
        try:
            groups = await self.redis.xinfo_groups(StreamConfig.STREAM_NAME)
        except redis.ResponseError:
            groups = []

        # Results stream length
        try:
            results_len = await self.redis.xlen(StreamConfig.RESULTS_STREAM)
        except redis.ResponseError:
            results_len = 0

        # DLQ length
        try:
            dlq_len = await self.redis.xlen(StreamConfig.DLQ_STREAM)
        except redis.ResponseError:
            dlq_len = 0

        return {
            'stream': {
                'length': stream_info.get(b'length', 0),
                'first_entry': stream_info.get(b'first-entry'),
                'last_entry': stream_info.get(b'last-entry'),
            },
            'metrics': metrics_decoded,
            'consumer_groups': len(groups),
            'results_count': results_len,
            'failed_count': dlq_len,
            'timestamp': datetime.now().isoformat()
        }

    async def print_stats(self):
        """Print statistics to console"""
        stats = await self.get_stats()

        print("\n" + "=" * 60)
        print("📊 STREAM STATISTICS")
        print("=" * 60)
        print(f"\n🔄 Stream Queue:")
        print(f"  Pending: {stats['stream']['length']}")
        print(f"\n✅ Processing Metrics:")
        for key, value in stats['metrics'].items():
            print(f"  {key}: {value}")
        print(f"\n📦 Results: {stats['results_count']}")
        print(f"❌ Failed (DLQ): {stats['failed_count']}")
        print("=" * 60 + "\n")


# ============================================================================
# CLI Interface
# ============================================================================

async def run_worker(worker_id: str):
    """Run a single worker"""
    redis_client = redis.Redis(
        host=StreamConfig.REDIS_HOST,
        port=StreamConfig.REDIS_PORT,
        db=StreamConfig.REDIS_DB,
        decode_responses=False
    )

    pipeline = FullEnrichmentPipeline(enable_cache=True)
    worker = StreamWorker(redis_client, worker_id, pipeline)

    try:
        await worker.start()
    except KeyboardInterrupt:
        worker.stop()
    finally:
        await redis_client.close()


async def run_multiple_workers(num_workers: int = 4):
    """Run multiple workers in parallel"""
    logger.info(f"🚀 Starting {num_workers} workers...")

    workers = [
        run_worker(f"worker-{i}")
        for i in range(num_workers)
    ]

    await asyncio.gather(*workers)


async def submit_email(
    email: str,
    ip_address: Optional[str] = None,
    skip_commercial: bool = False
):
    """Submit email for enrichment"""
    redis_client = redis.Redis(
        host=StreamConfig.REDIS_HOST,
        port=StreamConfig.REDIS_PORT,
        db=StreamConfig.REDIS_DB,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    try:
        job_id = await producer.submit_job(
            email=email,
            ip_address=ip_address,
            skip_commercial=skip_commercial
        )
        print(f"\n✅ Submitted job: {job_id}")
        print(f"Email: {email}\n")
    finally:
        await redis_client.close()


async def monitor_stream():
    """Monitor stream continuously"""
    redis_client = redis.Redis(
        host=StreamConfig.REDIS_HOST,
        port=StreamConfig.REDIS_PORT,
        db=StreamConfig.REDIS_DB,
        decode_responses=False
    )

    monitor = StreamMonitor(redis_client)

    try:
        while True:
            await monitor.print_stats()
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        await redis_client.close()


def main():
    """CLI entry point"""
    import sys

    if len(sys.argv) < 2:
        print("""
Real-time Streaming Enrichment System (v4.0)

Usage:
    python streaming.py worker [--workers N]    # Start worker(s)
    python streaming.py submit <email>          # Submit email
    python streaming.py monitor                 # Monitor stream

Examples:
    # Start 4 workers
    python streaming.py worker --workers 4

    # Submit email for enrichment
    python streaming.py submit user@example.com

    # Monitor stream
    python streaming.py monitor
""")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'worker':
        num_workers = 1
        if '--workers' in sys.argv:
            idx = sys.argv.index('--workers')
            num_workers = int(sys.argv[idx + 1])

        asyncio.run(run_multiple_workers(num_workers))

    elif command == 'submit':
        if len(sys.argv) < 3:
            print("❌ Error: Email required")
            print("Usage: python streaming.py submit <email>")
            sys.exit(1)

        email = sys.argv[2]
        asyncio.run(submit_email(email))

    elif command == 'monitor':
        asyncio.run(monitor_stream())

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
