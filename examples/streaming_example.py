#!/usr/bin/env python3
"""
Streaming Enrichment Example

Demonstrates how to use the real-time streaming enrichment system (v4.0)
"""

import asyncio
import json
import time
import redis.asyncio as redis
from streaming import StreamProducer, StreamMonitor


async def example_1_submit_single_job():
    """Example 1: Submit a single enrichment job"""
    print("\n" + "=" * 60)
    print("Example 1: Submit Single Job")
    print("=" * 60)

    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    # Submit job
    job_id = await producer.submit_job(
        email='user@example.com',
        ip_address='181.45.123.45'
    )

    print(f"\n✅ Submitted job: {job_id}")
    print(f"Email: user@example.com")
    print(f"\nNow workers will process this job in the background.")

    await redis_client.close()


async def example_2_submit_batch():
    """Example 2: Submit multiple emails at once"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Submission")
    print("=" * 60)

    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    # Submit batch
    emails = [
        'john.doe@example.com',
        'jane.smith@company.com',
        'developer@startup.io',
        'ceo@enterprise.com',
        'support@service.net'
    ]

    print(f"\nSubmitting {len(emails)} emails...")

    job_ids = await producer.submit_batch(emails)

    print(f"\n✅ Submitted {len(job_ids)} jobs:")
    for i, (email, job_id) in enumerate(zip(emails, job_ids), 1):
        print(f"  {i}. {email}: {job_id[:8]}...")

    await redis_client.close()


async def example_3_check_results():
    """Example 3: Check job results"""
    print("\n" + "=" * 60)
    print("Example 3: Check Job Results")
    print("=" * 60)

    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    # Submit a job
    email = 'test@example.com'
    job_id = await producer.submit_job(email)

    print(f"\n✅ Submitted: {email}")
    print(f"Job ID: {job_id}")
    print(f"\nWaiting for result (polling every 2 seconds)...")

    # Poll for result
    result_key = f"result:{job_id}"

    for attempt in range(30):  # Try for up to 60 seconds
        result = await redis_client.get(result_key)

        if result:
            data = json.loads(result)
            print(f"\n✅ Result ready!")
            print(f"\nJob Status: {data['job']['status']}")
            print(f"Trust Score: {data['result']['summary']['trust_score']}")
            print(f"Features Extracted: {data['result']['features']['feature_count']}")
            print(f"\nTop Features:")
            features = data['result']['features']['all_features']
            print(f"  - GitHub Repos: {features.get('github_repos', 0)}")
            print(f"  - Has Gravatar: {features.get('has_gravatar', False)}")
            print(f"  - Digital Footprint: {features.get('digital_footprint_count', 0)}")
            break
        else:
            print(f"  Attempt {attempt + 1}/30: Still processing...")
            await asyncio.sleep(2)
    else:
        print("\n⚠️ Result not ready after 60 seconds")

    await redis_client.close()


async def example_4_monitor_stream():
    """Example 4: Monitor stream statistics"""
    print("\n" + "=" * 60)
    print("Example 4: Monitor Stream")
    print("=" * 60)

    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    monitor = StreamMonitor(redis_client)

    print("\nFetching stream statistics...")

    stats = await monitor.get_stats()

    print(f"\n📊 Stream Statistics:")
    print(f"  Pending Jobs: {stats['stream']['length']}")
    print(f"\n✅ Processing Metrics:")
    for key, value in stats['metrics'].items():
        print(f"  {key}: {value}")
    print(f"\n📦 Results Stored: {stats['results_count']}")
    print(f"❌ Failed (DLQ): {stats['failed_count']}")

    await redis_client.close()


async def example_5_integration_workflow():
    """Example 5: Complete integration workflow"""
    print("\n" + "=" * 60)
    print("Example 5: Complete Integration Workflow")
    print("=" * 60)

    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    # Simulate user signup
    print("\n1. User signs up")
    new_user_email = 'newuser@startup.com'
    print(f"   Email: {new_user_email}")

    # Submit enrichment job (async, non-blocking)
    print("\n2. Submit enrichment job (async)")
    job_id = await producer.submit_job(new_user_email)
    print(f"   Job ID: {job_id}")
    print("   ✅ User can continue using the app")

    # Later: Check if enrichment is done
    print("\n3. Poll for enrichment result")
    result_key = f"result:{job_id}"

    for i in range(5):
        await asyncio.sleep(1)
        result = await redis_client.get(result_key)

        if result:
            data = json.loads(result)
            print(f"   ✅ Enrichment complete!")

            # Use enrichment data
            trust_score = data['result']['summary']['trust_score']
            features = data['result']['features']['all_features']

            print(f"\n4. Use enrichment data for personalization")
            print(f"   Trust Score: {trust_score}")

            if trust_score > 0.7:
                print("   → Action: Enable premium features")
            elif trust_score > 0.4:
                print("   → Action: Standard onboarding")
            else:
                print("   → Action: Enhanced verification required")

            if features.get('github_repos', 0) > 10:
                print("   → Action: Show developer-focused content")

            break
        else:
            print(f"   Attempt {i+1}/5: Still processing...")
    else:
        print("   ⚠️ Result not ready yet (continue in background)")

    await redis_client.close()


async def example_6_batch_user_enrichment():
    """Example 6: Batch enrichment of existing users"""
    print("\n" + "=" * 60)
    print("Example 6: Batch User Enrichment")
    print("=" * 60)

    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=False
    )

    producer = StreamProducer(redis_client)

    # Simulate database of users
    users_from_database = [
        {'id': 1, 'email': 'user1@example.com'},
        {'id': 2, 'email': 'user2@startup.io'},
        {'id': 3, 'email': 'user3@company.com'},
        {'id': 4, 'email': 'user4@service.net'},
        {'id': 5, 'email': 'user5@enterprise.org'},
    ]

    print(f"\nEnriching {len(users_from_database)} users from database...")

    # Submit all jobs
    job_mapping = {}
    for user in users_from_database:
        job_id = await producer.submit_job(
            email=user['email'],
            metadata={'user_id': user['id']}
        )
        job_mapping[job_id] = user
        print(f"  ✅ Submitted: {user['email']} (user_id: {user['id']})")

    print(f"\n✅ All {len(job_mapping)} jobs submitted!")
    print("Workers will process these in parallel.")

    await redis_client.close()


def main():
    """Run all examples"""
    print("=" * 60)
    print("Real-time Streaming Enrichment Examples")
    print("=" * 60)

    print("\nIMPORTANT: Make sure you have:")
    print("  1. Redis running: redis-cli ping")
    print("  2. Workers started: python streaming.py worker --workers 4")
    print("\nPress Enter to continue...")
    input()

    # Run examples
    asyncio.run(example_1_submit_single_job())
    time.sleep(1)

    asyncio.run(example_2_submit_batch())
    time.sleep(1)

    asyncio.run(example_4_monitor_stream())
    time.sleep(1)

    asyncio.run(example_5_integration_workflow())
    time.sleep(1)

    asyncio.run(example_6_batch_user_enrichment())

    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)

    print("\nNext Steps:")
    print("  1. Check worker logs to see processing")
    print("  2. Run: python streaming.py monitor")
    print("  3. Try example_3_check_results() to see a specific result")

    print("\nTo run individual examples:")
    print("  python -c 'from examples.streaming_example import example_3_check_results; import asyncio; asyncio.run(example_3_check_results())'")


if __name__ == "__main__":
    main()
