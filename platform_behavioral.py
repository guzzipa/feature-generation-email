#!/usr/bin/env python3
"""
Platform Behavioral Data Enrichment
Extract features from user behavior on YOUR platform

Features extracted: +40
- Session patterns (duration, frequency, recency)
- Engagement metrics (clicks, pages, time on site)
- Device/Tech fingerprinting
- Temporal patterns (login times, activity patterns)
- Form completion behavior
- Geographic consistency

Cost: $0 (uses YOUR existing data)
Value: ⭐⭐⭐⭐⭐ CRITICAL for credit scoring

Version: 3.3.0
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import Counter
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlatformBehavioralEnricher:
    """
    Extract behavioral features from platform data.

    This is THE MOST VALUABLE source for credit scoring because:
    - It's unique to each user
    - It's impossible to fake
    - It shows real engagement patterns
    - It's 100% FREE (you already have the data)
    """

    def __init__(self):
        pass

    def enrich_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate behavioral features from platform user data.

        Args:
            user_data: Dictionary containing user's platform behavior
                {
                    'user_id': 'abc123',
                    'email': 'user@example.com',
                    'created_at': '2023-01-15T10:30:00Z',
                    'sessions': [...],  # List of session objects
                    'events': [...],    # List of event/click objects
                    'forms': [...],     # List of form submissions
                    'devices': [...],   # List of device fingerprints
                    'ips': [...],       # List of IP addresses used
                }

        Returns:
            Dictionary with 40+ behavioral features
        """
        logger.info(f"[Behavioral] Extracting features for user: {user_data.get('user_id', 'unknown')}")

        features = {
            'email': user_data.get('email'),
            'enrichment_timestamp': datetime.now().isoformat(),
        }

        # 1. Account & Temporal Features
        account_features = self._extract_account_features(user_data)
        features.update(account_features)

        # 2. Session Features
        session_features = self._extract_session_features(user_data.get('sessions', []))
        features.update(session_features)

        # 3. Engagement Features
        engagement_features = self._extract_engagement_features(user_data.get('events', []))
        features.update(engagement_features)

        # 4. Device & Tech Features
        device_features = self._extract_device_features(user_data.get('devices', []))
        features.update(device_features)

        # 5. Geographic Features
        geo_features = self._extract_geographic_features(user_data.get('ips', []))
        features.update(geo_features)

        # 6. Form Completion Features
        form_features = self._extract_form_features(user_data.get('forms', []))
        features.update(form_features)

        # 7. Temporal Pattern Features
        temporal_features = self._extract_temporal_patterns(user_data.get('sessions', []))
        features.update(temporal_features)

        logger.info(f"[Behavioral] Extracted {len(features)} behavioral features")
        return features

    def _extract_account_features(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract account-level features."""
        created_at = user_data.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

            account_age_days = (datetime.now() - created_at.replace(tzinfo=None)).days
        else:
            account_age_days = 0

        return {
            'platform_account_age_days': account_age_days,
            'platform_account_age_weeks': account_age_days // 7,
            'platform_account_age_months': account_age_days // 30,
        }

    def _extract_session_features(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract session-based features."""
        if not sessions:
            return {
                'sessions_total': 0,
                'sessions_last_30_days': 0,
                'sessions_last_7_days': 0,
                'session_duration_avg_seconds': 0,
                'session_duration_median_seconds': 0,
                'session_duration_max_seconds': 0,
                'sessions_per_week': 0.0,
                'days_since_last_session': None,
                'sessions_consistency_score': 0.0,
            }

        now = datetime.now()

        # Parse session times and durations
        session_times = []
        durations = []

        for session in sessions:
            if 'timestamp' in session:
                ts = session['timestamp']
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                session_times.append(ts.replace(tzinfo=None))

            if 'duration_seconds' in session:
                durations.append(session['duration_seconds'])

        # Count recent sessions
        sessions_last_30 = sum(1 for ts in session_times if (now - ts).days <= 30)
        sessions_last_7 = sum(1 for ts in session_times if (now - ts).days <= 7)

        # Days since last session
        days_since_last = (now - max(session_times)).days if session_times else None

        # Session duration stats
        avg_duration = statistics.mean(durations) if durations else 0
        median_duration = statistics.median(durations) if durations else 0
        max_duration = max(durations) if durations else 0

        # Sessions per week
        if session_times:
            days_active = (max(session_times) - min(session_times)).days or 1
            sessions_per_week = (len(sessions) / days_active) * 7
        else:
            sessions_per_week = 0.0

        # Consistency score (regular activity vs sporadic)
        consistency_score = self._calculate_consistency(session_times)

        return {
            'sessions_total': len(sessions),
            'sessions_last_30_days': sessions_last_30,
            'sessions_last_7_days': sessions_last_7,
            'session_duration_avg_seconds': round(avg_duration, 1),
            'session_duration_median_seconds': round(median_duration, 1),
            'session_duration_max_seconds': max_duration,
            'sessions_per_week': round(sessions_per_week, 2),
            'days_since_last_session': days_since_last,
            'sessions_consistency_score': round(consistency_score, 3),
        }

    def _extract_engagement_features(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract engagement/interaction features."""
        if not events:
            return {
                'total_events': 0,
                'events_per_session': 0.0,
                'clicks_total': 0,
                'pages_viewed': 0,
                'time_on_platform_minutes': 0,
                'engagement_rate': 0.0,
                'bounce_rate': 0.0,
            }

        # Count event types
        event_types = Counter(e.get('type', 'unknown') for e in events)

        clicks = event_types.get('click', 0)
        page_views = event_types.get('pageview', 0)

        # Time on platform (sum of session durations if available)
        total_time = sum(e.get('duration_seconds', 0) for e in events)

        # Engagement rate (clicks / pageviews)
        engagement_rate = clicks / page_views if page_views > 0 else 0

        # Bounce rate (sessions with only 1 pageview)
        # This would need session grouping - simplified here
        bounce_rate = 0.0  # Placeholder

        return {
            'total_events': len(events),
            'events_per_session': 0.0,  # Would need session count
            'clicks_total': clicks,
            'pages_viewed': page_views,
            'time_on_platform_minutes': round(total_time / 60, 1),
            'engagement_rate': round(engagement_rate, 3),
            'bounce_rate': round(bounce_rate, 3),
        }

    def _extract_device_features(self, devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract device/tech features."""
        if not devices:
            return {
                'unique_devices_count': 0,
                'device_type_primary': 'unknown',
                'unique_browsers_count': 0,
                'unique_os_count': 0,
                'uses_mobile': 0,
                'uses_desktop': 0,
            }

        # Count unique devices
        unique_devices = len(set(d.get('fingerprint', i) for i, d in enumerate(devices)))

        # Device types
        device_types = Counter(d.get('type', 'unknown') for d in devices)
        primary_device = device_types.most_common(1)[0][0] if device_types else 'unknown'

        # Browsers and OS
        browsers = set(d.get('browser', 'unknown') for d in devices)
        oses = set(d.get('os', 'unknown') for d in devices)

        return {
            'unique_devices_count': unique_devices,
            'device_type_primary': primary_device,
            'unique_browsers_count': len(browsers),
            'unique_os_count': len(oses),
            'uses_mobile': 1 if 'mobile' in device_types else 0,
            'uses_desktop': 1 if 'desktop' in device_types else 0,
        }

    def _extract_geographic_features(self, ips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract geographic consistency features."""
        if not ips:
            return {
                'unique_ips_count': 0,
                'unique_countries_count': 0,
                'unique_cities_count': 0,
                'ip_country_changes': 0,
                'geo_consistency_score': 0.0,
            }

        # Count unique locations
        unique_ips = len(set(ip.get('address', i) for i, ip in enumerate(ips)))

        countries = [ip.get('country') for ip in ips if ip.get('country')]
        cities = [ip.get('city') for ip in ips if ip.get('city')]

        unique_countries = len(set(countries))
        unique_cities = len(set(cities))

        # Country changes (red flag if too many)
        country_changes = len(countries) - 1 if len(countries) > 1 else 0

        # Geo consistency (1.0 = always same location, 0.0 = very inconsistent)
        geo_consistency = 1.0 - (country_changes / len(countries)) if countries else 0.0

        return {
            'unique_ips_count': unique_ips,
            'unique_countries_count': unique_countries,
            'unique_cities_count': unique_cities,
            'ip_country_changes': country_changes,
            'geo_consistency_score': round(geo_consistency, 3),
        }

    def _extract_form_features(self, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract form completion behavior."""
        if not forms:
            return {
                'forms_submitted': 0,
                'forms_abandoned': 0,
                'form_completion_rate': 0.0,
                'avg_form_completion_time_seconds': 0,
            }

        submitted = sum(1 for f in forms if f.get('status') == 'submitted')
        abandoned = sum(1 for f in forms if f.get('status') == 'abandoned')

        completion_rate = submitted / len(forms) if forms else 0.0

        # Completion times
        completion_times = [f.get('completion_time_seconds', 0) for f in forms if f.get('status') == 'submitted']
        avg_completion_time = statistics.mean(completion_times) if completion_times else 0

        return {
            'forms_submitted': submitted,
            'forms_abandoned': abandoned,
            'form_completion_rate': round(completion_rate, 3),
            'avg_form_completion_time_seconds': round(avg_completion_time, 1),
        }

    def _extract_temporal_patterns(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract temporal activity patterns."""
        if not sessions:
            return {
                'login_hour_most_common': None,
                'weekday_activity_ratio': 0.0,
                'night_activity_ratio': 0.0,
                'weekend_activity_ratio': 0.0,
            }

        # Parse session timestamps
        timestamps = []
        for session in sessions:
            if 'timestamp' in session:
                ts = session['timestamp']
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                timestamps.append(ts.replace(tzinfo=None))

        if not timestamps:
            return {
                'login_hour_most_common': None,
                'weekday_activity_ratio': 0.0,
                'night_activity_ratio': 0.0,
                'weekend_activity_ratio': 0.0,
            }

        # Most common login hour
        hours = Counter(ts.hour for ts in timestamps)
        most_common_hour = hours.most_common(1)[0][0] if hours else None

        # Weekday vs weekend
        weekday_count = sum(1 for ts in timestamps if ts.weekday() < 5)
        weekend_count = len(timestamps) - weekday_count
        weekday_ratio = weekday_count / len(timestamps)
        weekend_ratio = weekend_count / len(timestamps)

        # Night activity (10pm - 6am)
        night_count = sum(1 for ts in timestamps if ts.hour >= 22 or ts.hour < 6)
        night_ratio = night_count / len(timestamps)

        return {
            'login_hour_most_common': most_common_hour,
            'weekday_activity_ratio': round(weekday_ratio, 3),
            'night_activity_ratio': round(night_ratio, 3),
            'weekend_activity_ratio': round(weekend_ratio, 3),
        }

    def _calculate_consistency(self, timestamps: List[datetime]) -> float:
        """Calculate consistency score based on session regularity."""
        if len(timestamps) < 2:
            return 0.0

        # Calculate gaps between sessions
        sorted_ts = sorted(timestamps)
        gaps = [(sorted_ts[i+1] - sorted_ts[i]).days for i in range(len(sorted_ts)-1)]

        if not gaps:
            return 0.0

        # Low variance in gaps = high consistency
        mean_gap = statistics.mean(gaps)
        variance = statistics.variance(gaps) if len(gaps) > 1 else 0

        # Normalize: regular weekly activity = 1.0, very sporadic = 0.0
        consistency = 1.0 / (1.0 + variance / (mean_gap + 1))

        return consistency


def create_sample_user_data(email: str) -> Dict[str, Any]:
    """
    Create sample user data structure.

    This shows you how to format YOUR platform data for enrichment.
    Replace with real data from your database.
    """
    now = datetime.now()

    return {
        'user_id': 'sample_user_123',
        'email': email,
        'created_at': (now - timedelta(days=45)).isoformat(),

        'sessions': [
            {'timestamp': (now - timedelta(days=1)).isoformat(), 'duration_seconds': 245},
            {'timestamp': (now - timedelta(days=3)).isoformat(), 'duration_seconds': 180},
            {'timestamp': (now - timedelta(days=7)).isoformat(), 'duration_seconds': 420},
            {'timestamp': (now - timedelta(days=10)).isoformat(), 'duration_seconds': 310},
            {'timestamp': (now - timedelta(days=14)).isoformat(), 'duration_seconds': 290},
        ],

        'events': [
            {'type': 'pageview', 'timestamp': (now - timedelta(days=1)).isoformat()},
            {'type': 'click', 'timestamp': (now - timedelta(days=1)).isoformat()},
            {'type': 'pageview', 'timestamp': (now - timedelta(days=1)).isoformat()},
        ],

        'devices': [
            {'fingerprint': 'device_abc123', 'type': 'mobile', 'browser': 'Safari', 'os': 'iOS'},
            {'fingerprint': 'device_xyz789', 'type': 'desktop', 'browser': 'Chrome', 'os': 'macOS'},
        ],

        'ips': [
            {'address': '181.45.123.45', 'country': 'Argentina', 'city': 'Buenos Aires'},
            {'address': '181.45.123.46', 'country': 'Argentina', 'city': 'Buenos Aires'},
        ],

        'forms': [
            {'status': 'submitted', 'completion_time_seconds': 340},
            {'status': 'submitted', 'completion_time_seconds': 280},
            {'status': 'abandoned', 'completion_time_seconds': 120},
        ],
    }


def main():
    """CLI for testing."""
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python platform_behavioral.py <email>")
        print("\nThis will use SAMPLE data. Replace with real platform data in production.")
        sys.exit(1)

    email = sys.argv[1]

    # Create sample data (replace with real data from your database)
    user_data = create_sample_user_data(email)

    # Enrich
    enricher = PlatformBehavioralEnricher()
    results = enricher.enrich_user(user_data)

    # Save results
    filename = f"behavioral_{email.replace('@', '_at_')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"PLATFORM BEHAVIORAL ENRICHMENT RESULTS")
    print(f"{'='*60}\n")
    print(json.dumps(results, indent=2))
    print(f"\n{'='*60}")
    print(f"Results saved to: {filename}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
