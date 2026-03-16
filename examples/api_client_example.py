#!/usr/bin/env python3
"""
Email Intelligence API Client Examples

Demonstrates how to use the REST API for email enrichment.

Requirements:
    pip install requests

Usage:
    python examples/api_client_example.py
"""

import requests
import json
from typing import List, Dict, Any


class EmailIntelligenceClient:
    """
    Python client for Email Intelligence API
    """

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        """
        Initialize API client

        Args:
            base_url: API base URL
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}

        if api_key:
            self.headers['X-API-Key'] = api_key

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def enrich_email(
        self,
        email: str,
        ip_address: str = None,
        skip_commercial: bool = False,
        skip_additional: bool = False,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich single email

        Args:
            email: Email address to enrich
            ip_address: Optional IP for geolocation
            skip_commercial: Skip commercial APIs
            skip_additional: Skip additional sources
            force_refresh: Force cache refresh

        Returns:
            Enrichment result dictionary
        """
        payload = {
            'email': email,
            'skip_commercial': skip_commercial,
            'skip_additional': skip_additional,
            'force_refresh': force_refresh
        }

        if ip_address:
            payload['ip_address'] = ip_address

        response = requests.post(
            f"{self.base_url}/enrich",
            headers=self.headers,
            json=payload
        )

        response.raise_for_status()
        return response.json()

    def enrich_batch(
        self,
        emails: List[str],
        ip_address: str = None,
        skip_commercial: bool = False,
        skip_additional: bool = False,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich multiple emails in batch

        Args:
            emails: List of email addresses (max 100)
            ip_address: Optional IP for geolocation
            skip_commercial: Skip commercial APIs
            skip_additional: Skip additional sources
            force_refresh: Force cache refresh

        Returns:
            Batch enrichment result
        """
        if len(emails) > 100:
            raise ValueError("Maximum 100 emails per batch")

        payload = {
            'emails': emails,
            'skip_commercial': skip_commercial,
            'skip_additional': skip_additional,
            'force_refresh': force_refresh
        }

        if ip_address:
            payload['ip_address'] = ip_address

        response = requests.post(
            f"{self.base_url}/enrich/batch",
            headers=self.headers,
            json=payload
        )

        response.raise_for_status()
        return response.json()

    def invalidate_cache(self, email: str) -> Dict[str, Any]:
        """Invalidate cache for specific email"""
        response = requests.delete(
            f"{self.base_url}/cache/{email}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


# ============================================================================
# Examples
# ============================================================================

def example_1_basic_enrichment():
    """Example 1: Basic email enrichment"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Email Enrichment")
    print("=" * 60 + "\n")

    client = EmailIntelligenceClient()

    # Enrich email
    result = client.enrich_email('user@example.com')

    # Display results
    print(f"Email: {result['email']}")
    print(f"Cached: {result['cached']}")
    print(f"\nSummary:")
    for key, value in result['summary'].items():
        print(f"  {key}: {value}")

    print(f"\nFeatures generated: {result['features']['feature_count']}")


def example_2_with_ip():
    """Example 2: Enrichment with IP geolocation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: With IP Geolocation")
    print("=" * 60 + "\n")

    client = EmailIntelligenceClient()

    # Enrich with IP address
    result = client.enrich_email(
        email='user@example.com',
        ip_address='181.45.123.45'
    )

    # Display IP intelligence
    free_sources = result['data_sources'].get('free_sources', {})
    print(f"IP Country: {free_sources.get('ip_country')}")
    print(f"IP City: {free_sources.get('ip_city')}")
    print(f"IP ISP: {free_sources.get('ip_isp')}")
    print(f"Connection Type: {free_sources.get('ip_connection_type')}")


def example_3_batch_enrichment():
    """Example 3: Batch enrichment"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Batch Enrichment")
    print("=" * 60 + "\n")

    client = EmailIntelligenceClient()

    emails = [
        'user1@example.com',
        'user2@example.com',
        'user3@example.com'
    ]

    # Enrich batch
    result = client.enrich_batch(emails)

    print(f"Total: {result['total']}")
    print(f"Success: {result['success']}")
    print(f"Failed: {result['failed']}")

    print("\nResults:")
    for item in result['results']:
        if item['success']:
            summary = item['summary']
            print(f"  {item['email']}: trust={summary['trust_score']:.3f}")
        else:
            print(f"  {item['email']}: ERROR - {item['error']}")


def example_4_free_only():
    """Example 4: Free sources only (skip commercial APIs)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Free Sources Only")
    print("=" * 60 + "\n")

    client = EmailIntelligenceClient()

    # Skip commercial APIs
    result = client.enrich_email(
        email='user@example.com',
        skip_commercial=True
    )

    print(f"Email: {result['email']}")
    print(f"Sources used:")
    for source, data in result['data_sources'].items():
        if data:
            print(f"  ✓ {source}")
        else:
            print(f"  ✗ {source} (skipped)")


def example_5_extract_specific_features():
    """Example 5: Extract specific features"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Extract Specific Features")
    print("=" * 60 + "\n")

    client = EmailIntelligenceClient()

    result = client.enrich_email('user@example.com')
    features = result['features']['all_features']

    # Extract features of interest
    print("Security Features:")
    print(f"  Breach Count: {features.get('breach_count', 0)}")
    print(f"  Disposable Email: {features.get('is_disposable_email', False)}")
    print(f"  Security Risk: {features.get('security_risk_score', 0):.3f}")

    print("\nIdentity Features:")
    print(f"  Account Age: {features.get('account_age_years', 0):.1f} years")
    print(f"  Has GitHub: {features.get('has_github', False)}")
    print(f"  GitHub Repos: {features.get('github_repos', 0)}")
    print(f"  Digital Footprint: {features.get('digital_footprint_count', 0)} platforms")

    print("\nEmail Features:")
    print(f"  Corporate Email: {features.get('is_corporate_email', False)}")
    print(f"  Provider Type: {features.get('email_provider_type', 'unknown')}")
    print(f"  Professional Pattern: {features.get('email_is_professional_pattern', False)}")


def example_6_ml_ready_features():
    """Example 6: ML-ready features for model training"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: ML-Ready Features")
    print("=" * 60 + "\n")

    client = EmailIntelligenceClient()

    result = client.enrich_email('user@example.com')
    ml_ready = result['features']['ml_ready']

    # Get feature vectors
    numerical = ml_ready['numerical']
    categorical = ml_ready['categorical']

    print(f"Numerical features: {len(numerical)} values")
    print(f"First 10: {numerical[:10]}")

    print(f"\nCategorical features: {len(categorical)} values")
    print(f"Values: {categorical}")

    print("\nReady for:")
    print("  - scikit-learn: X = np.array(numerical)")
    print("  - TensorFlow: tf.constant(numerical)")
    print("  - PyTorch: torch.tensor(numerical)")


def example_7_error_handling():
    """Example 7: Error handling"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Error Handling")
    print("=" * 60 + "\n")

    client = EmailIntelligenceClient()

    try:
        # Invalid email
        result = client.enrich_email('invalid_email')
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTPError: {e}")
        print(f"   Status Code: {e.response.status_code}")
        print(f"   Response: {e.response.json()}")

    try:
        # Batch with too many emails
        emails = [f"user{i}@example.com" for i in range(101)]
        result = client.enrich_batch(emails)
    except ValueError as e:
        print(f"❌ ValueError: {e}")


def example_8_cache_management():
    """Example 8: Cache management"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Cache Management")
    print("=" * 60 + "\n")

    client = EmailIntelligenceClient(api_key='your_api_key')  # Requires API key

    email = 'user@example.com'

    # First call (cold)
    print("First call (cold)...")
    result1 = client.enrich_email(email)
    print(f"Cached: {result1['cached']}")

    # Second call (cached)
    print("\nSecond call (warm)...")
    result2 = client.enrich_email(email)
    print(f"Cached: {result2['cached']}")

    # Invalidate cache
    print("\nInvalidating cache...")
    client.invalidate_cache(email)

    # Third call (cold again)
    print("\nThird call (cold)...")
    result3 = client.enrich_email(email)
    print(f"Cached: {result3['cached']}")


def main():
    """Run all examples"""
    print("\n🚀 EMAIL INTELLIGENCE API - CLIENT EXAMPLES\n")

    try:
        # Check if API is running
        client = EmailIntelligenceClient()
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
        print(f"   Version: {health['version']}")
        print(f"   Cache: {'Enabled' if health['cache_enabled'] else 'Disabled'}")

        # Run examples
        example_1_basic_enrichment()
        # example_2_with_ip()
        # example_3_batch_enrichment()
        # example_4_free_only()
        # example_5_extract_specific_features()
        # example_6_ml_ready_features()
        # example_7_error_handling()
        # example_8_cache_management()  # Requires API key

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60 + "\n")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("   Make sure the API is running:")
        print("   uvicorn api:app --reload --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
