#!/usr/bin/env python3
"""
Redis Cache Usage Examples

Shows how to use the caching system in your application.
"""

import sys
sys.path.insert(0, '..')

from cache_manager import get_cache_manager
from full_enrichment import FullEnrichmentPipeline


def example_1_basic_usage():
    """Example 1: Basic cache usage"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Cache Usage")
    print("=" * 60 + "\n")

    # Run enrichment with cache enabled (default)
    pipeline = FullEnrichmentPipeline(
        output_dir='results',
        enable_cache=True
    )

    email = "test@example.com"

    # First run - fetches from APIs
    print("First run (cold cache):")
    results1 = pipeline.enrich_email(email)
    print(f"✓ Enriched {email}")

    # Second run - uses cache
    print("\nSecond run (warm cache):")
    results2 = pipeline.enrich_email(email)
    print(f"✓ Enriched {email} (from cache)")


def example_2_force_refresh():
    """Example 2: Force refresh to bypass cache"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Force Refresh")
    print("=" * 60 + "\n")

    # Force fresh data (bypass cache)
    pipeline = FullEnrichmentPipeline(
        output_dir='results',
        force_refresh=True
    )

    email = "test@example.com"
    results = pipeline.enrich_email(email)
    print(f"✓ Forced fresh data for {email}")


def example_3_cache_management():
    """Example 3: Direct cache management"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Cache Management")
    print("=" * 60 + "\n")

    cache = get_cache_manager(enabled=True)

    email = "test@example.com"

    # Manually set cache
    test_data = {
        'email': email,
        'github_username': 'testuser',
        'has_github': True
    }

    print("Setting cache manually...")
    cache.set(email, 'osint', test_data)

    # Get from cache
    cached = cache.get(email, 'osint')
    print(f"Retrieved from cache: {cached}")

    # Invalidate cache
    print("\nInvalidating cache...")
    cache.invalidate(email, 'osint')

    # Try to get (should be None now)
    cached = cache.get(email, 'osint')
    print(f"After invalidation: {cached}")


def example_4_cache_stats():
    """Example 4: View cache statistics"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Cache Statistics")
    print("=" * 60 + "\n")

    cache = get_cache_manager(enabled=True)

    stats = cache.get_stats()

    if stats.get('enabled'):
        print("Cache Status: ✓ ENABLED")
        print(f"Total Keys: {stats.get('total_keys', 0)}")
        print(f"Memory Used: {stats.get('memory_used', 'N/A')}")
        print("\nKeys by source:")
        for source, count in stats.get('source_counts', {}).items():
            print(f"  {source}: {count} keys")
    else:
        print("Cache Status: ✗ DISABLED")
        print(f"Reason: {stats.get('reason', 'Unknown')}")


def example_5_custom_ttl():
    """Example 5: Custom TTL for specific use case"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Custom TTL")
    print("=" * 60 + "\n")

    cache = get_cache_manager(enabled=True)

    email = "vip_user@example.com"

    # VIP user - cache for only 1 hour (fresher data)
    vip_data = {
        'email': email,
        'tier': 'VIP',
        'needs_fresh_data': True
    }

    ttl_1_hour = 3600  # 1 hour in seconds
    cache.set(email, 'osint', vip_data, ttl=ttl_1_hour)
    print(f"Cached VIP user data with 1-hour TTL")


def example_6_batch_with_cache():
    """Example 6: Batch processing with cache"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Batch Processing")
    print("=" * 60 + "\n")

    pipeline = FullEnrichmentPipeline(
        output_dir='results',
        enable_cache=True
    )

    emails = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ]

    print(f"Processing {len(emails)} emails...")

    for i, email in enumerate(emails, 1):
        print(f"\n[{i}/{len(emails)}] Processing: {email}")
        results = pipeline.enrich_email(email)
        print(f"  ✓ Completed")

    print("\n✓ Batch processing complete!")
    print("Note: Subsequent runs will be much faster due to caching")


def main():
    """Run all examples"""
    import argparse

    parser = argparse.ArgumentParser(description='Redis Cache Examples')
    parser.add_argument(
        '--example',
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help='Run specific example (1-6)'
    )

    args = parser.parse_args()

    examples = {
        1: example_1_basic_usage,
        2: example_2_force_refresh,
        3: example_3_cache_management,
        4: example_4_cache_stats,
        5: example_5_custom_ttl,
        6: example_6_batch_with_cache,
    }

    if args.example:
        examples[args.example]()
    else:
        # Run all examples
        print("\n" + "🚀 RUNNING ALL EXAMPLES " + "=" * 38)
        for example_func in examples.values():
            try:
                example_func()
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("(This is expected if Redis is not running)")


if __name__ == "__main__":
    main()
