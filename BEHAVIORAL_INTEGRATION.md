# 🎯 Platform Behavioral Data Integration Guide

## Overview

**Platform behavioral data is THE MOST VALUABLE source for credit scoring:**
- ✅ **Free** - You already have this data
- ✅ **Unique** - Impossible to fake
- ✅ **Predictive** - Real user behavior correlates with creditworthiness
- ✅ **40+ features** - Rich signal

---

## 📊 Features Extracted (40 total)

### 1. Account & Temporal (3 features)
```python
{
    "platform_account_age_days": 45,
    "platform_account_age_weeks": 6,
    "platform_account_age_months": 1
}
```

### 2. Session Patterns (9 features)
```python
{
    "sessions_total": 12,
    "sessions_last_30_days": 8,
    "sessions_last_7_days": 3,
    "session_duration_avg_seconds": 245,
    "session_duration_median_seconds": 220,
    "session_duration_max_seconds": 890,
    "sessions_per_week": 2.5,
    "days_since_last_session": 2,
    "sessions_consistency_score": 0.85  # High = regular user
}
```

### 3. Engagement (7 features)
```python
{
    "total_events": 234,
    "events_per_session": 19.5,
    "clicks_total": 156,
    "pages_viewed": 234,
    "time_on_platform_minutes": 892,
    "engagement_rate": 0.67,  # clicks / pageviews
    "bounce_rate": 0.12
}
```

### 4. Device & Tech (6 features)
```python
{
    "unique_devices_count": 2,
    "device_type_primary": "mobile",
    "unique_browsers_count": 2,
    "unique_os_count": 2,
    "uses_mobile": 1,
    "uses_desktop": 1
}
```

### 5. Geographic Consistency (5 features)
```python
{
    "unique_ips_count": 3,
    "unique_countries_count": 1,
    "unique_cities_count": 2,
    "ip_country_changes": 0,  # RED FLAG if > 2
    "geo_consistency_score": 0.95  # Always same country = high
}
```

### 6. Form Completion (4 features)
```python
{
    "forms_submitted": 8,
    "forms_abandoned": 2,
    "form_completion_rate": 0.80,
    "avg_form_completion_time_seconds": 340
}
```

### 7. Temporal Patterns (4 features)
```python
{
    "login_hour_most_common": 19,  # 7pm - after work hours
    "weekday_activity_ratio": 0.75,  # More on weekdays = employed?
    "night_activity_ratio": 0.08,  # Low = normal patterns
    "weekend_activity_ratio": 0.25
}
```

---

## 🔌 Integration Options

### Option A: Database Query (Recommended)

**If you have PostgreSQL/MySQL:**

```python
from platform_behavioral import PlatformBehavioralEnricher
import psycopg2  # or pymysql

def get_user_behavioral_data(email: str) -> dict:
    """Query your database for user behavioral data."""

    conn = psycopg2.connect("your_connection_string")
    cursor = conn.cursor()

    # 1. Get user account info
    cursor.execute("""
        SELECT id, email, created_at
        FROM users
        WHERE email = %s
    """, (email,))
    user = cursor.fetchone()

    if not user:
        return None

    user_id = user[0]

    # 2. Get sessions
    cursor.execute("""
        SELECT timestamp, EXTRACT(EPOCH FROM duration) as duration_seconds
        FROM sessions
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 100
    """, (user_id,))
    sessions = [
        {'timestamp': row[0].isoformat(), 'duration_seconds': row[1]}
        for row in cursor.fetchall()
    ]

    # 3. Get events
    cursor.execute("""
        SELECT type, timestamp
        FROM events
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 1000
    """, (user_id,))
    events = [
        {'type': row[0], 'timestamp': row[1].isoformat()}
        for row in cursor.fetchall()
    ]

    # 4. Get devices
    cursor.execute("""
        SELECT DISTINCT device_fingerprint, device_type, browser, os
        FROM sessions
        WHERE user_id = %s
    """, (user_id,))
    devices = [
        {
            'fingerprint': row[0],
            'type': row[1],
            'browser': row[2],
            'os': row[3]
        }
        for row in cursor.fetchall()
    ]

    # 5. Get IPs
    cursor.execute("""
        SELECT DISTINCT ip_address, ip_country, ip_city
        FROM sessions
        WHERE user_id = %s
    """, (user_id,))
    ips = [
        {
            'address': row[0],
            'country': row[1],
            'city': row[2]
        }
        for row in cursor.fetchall()
    ]

    # 6. Get forms
    cursor.execute("""
        SELECT status, EXTRACT(EPOCH FROM completion_time) as completion_time_seconds
        FROM form_submissions
        WHERE user_id = %s
    """, (user_id,))
    forms = [
        {'status': row[0], 'completion_time_seconds': row[1]}
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        'user_id': str(user_id),
        'email': email,
        'created_at': user[2].isoformat(),
        'sessions': sessions,
        'events': events,
        'devices': devices,
        'ips': ips,
        'forms': forms,
    }


# Usage
enricher = PlatformBehavioralEnricher()
user_data = get_user_behavioral_data("user@example.com")
behavioral_features = enricher.enrich_user(user_data)

print(f"Generated {len(behavioral_features)} behavioral features")
```

---

### Option B: Analytics Integration (Mixpanel, Segment, etc)

**If you use Mixpanel:**

```python
from mixpanel import Mixpanel
from platform_behavioral import PlatformBehavioralEnricher

mp = Mixpanel("YOUR_API_SECRET")

def get_mixpanel_data(email: str) -> dict:
    """Fetch behavioral data from Mixpanel."""

    # Get user profile
    user = mp.people.query_engagement(email)

    # Get events
    events_data = mp.request(['export'], {
        'where': f'properties["$email"] == "{email}"',
        'from_date': '2024-01-01',
        'to_date': '2026-12-31',
    })

    # Transform to our format
    sessions = []
    events = []
    devices = set()

    for event in events_data:
        if event['event'] == 'Session Start':
            sessions.append({
                'timestamp': event['properties']['time'],
                'duration_seconds': event['properties'].get('session_length', 0)
            })

        events.append({
            'type': event['event'],
            'timestamp': event['properties']['time']
        })

        # Track devices
        devices.add((
            event['properties'].get('$device_id'),
            event['properties'].get('$device'),
            event['properties'].get('$browser'),
            event['properties'].get('$os')
        ))

    return {
        'user_id': email,
        'email': email,
        'created_at': user.get('$created'),
        'sessions': sessions,
        'events': events,
        'devices': [
            {'fingerprint': d[0], 'type': d[1], 'browser': d[2], 'os': d[3]}
            for d in devices
        ],
        'ips': [],  # May not be available
        'forms': [],  # May not be available
    }
```

---

### Option C: Google Analytics

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

def get_ga_data(email: str, property_id: str) -> dict:
    """Fetch behavioral data from Google Analytics 4."""

    client = BetaAnalyticsDataClient()

    # Query for user sessions
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            {"name": "sessionId"},
            {"name": "date"},
            {"name": "deviceCategory"},
        ],
        metrics=[
            {"name": "sessions"},
            {"name": "engagementRate"},
            {"name": "averageSessionDuration"},
        ],
        dimension_filter={
            "filter": {
                "field_name": "userEmail",
                "string_filter": {"value": email}
            }
        }
    )

    response = client.run_report(request)

    # Transform to our format
    sessions = []
    for row in response.rows:
        sessions.append({
            'timestamp': row.dimension_values[1].value,
            'duration_seconds': float(row.metric_values[2].value)
        })

    return {
        'user_id': email,
        'email': email,
        'sessions': sessions,
        'events': [],
        'devices': [],
        'ips': [],
        'forms': [],
    }
```

---

## 🚀 Integration into Full Pipeline

Update `full_enrichment.py` to include behavioral data:

```python
from platform_behavioral import PlatformBehavioralEnricher

# In FullEnrichmentPipeline class:

def enrich_email(self, email: str, user_behavioral_data: dict = None) -> dict:
    """
    Args:
        email: Email address
        user_behavioral_data: Optional dict with platform behavioral data
    """

    # ... existing OSINT, commercial, additional, free sources ...

    # NEW: Step 6 - Platform Behavioral Data
    behavioral_data = None
    if user_behavioral_data:
        logger.info("📊 Step 6/6: Extracting platform behavioral features...")
        behavioral_enricher = PlatformBehavioralEnricher()
        behavioral_data = behavioral_enricher.enrich_user(user_behavioral_data)

    # Add to results
    results = {
        'data_sources': {
            # ... existing ...
            'behavioral': behavioral_data if behavioral_data else {},
        }
    }
```

---

## 📈 Value for Credit Scoring

| Feature Group | Credit Scoring Value | Why |
|---------------|---------------------|-----|
| **Session Consistency** | ⭐⭐⭐⭐⭐ | Regular users = stable lifestyle |
| **Engagement Rate** | ⭐⭐⭐⭐ | High engagement = serious user |
| **Geographic Consistency** | ⭐⭐⭐⭐⭐ | Changing countries = red flag |
| **Device Count** | ⭐⭐⭐ | Too many devices = suspicious |
| **Form Completion** | ⭐⭐⭐⭐ | Completes forms = serious intent |
| **Account Age** | ⭐⭐⭐⭐⭐ | Older accounts = more trustworthy |
| **Temporal Patterns** | ⭐⭐⭐⭐ | Normal hours = employed person |

---

## ⚠️ Red Flags to Watch

```python
# EXAMPLE: Automated red flag detection
def calculate_behavioral_risk(features: dict) -> dict:
    """Calculate risk based on behavioral patterns."""

    risk_flags = []

    # Too many IP changes
    if features.get('ip_country_changes', 0) > 2:
        risk_flags.append("MULTIPLE_COUNTRIES")

    # Very short session durations
    if features.get('session_duration_avg_seconds', 0) < 30:
        risk_flags.append("SHORT_SESSIONS")

    # Too many devices
    if features.get('unique_devices_count', 0) > 5:
        risk_flags.append("MANY_DEVICES")

    # Low engagement
    if features.get('engagement_rate', 0) < 0.1:
        risk_flags.append("LOW_ENGAGEMENT")

    # Inconsistent activity
    if features.get('sessions_consistency_score', 0) < 0.3:
        risk_flags.append("SPORADIC_ACTIVITY")

    # High night activity (bots?)
    if features.get('night_activity_ratio', 0) > 0.5:
        risk_flags.append("UNUSUAL_HOURS")

    return {
        'risk_flags': risk_flags,
        'risk_count': len(risk_flags),
        'behavioral_risk_score': len(risk_flags) / 6.0  # 0-1 scale
    }
```

---

## 💡 Pro Tips

1. **Cache behavioral features**: Recalculate only weekly, not per request
2. **Track changes over time**: Sudden pattern changes = red flag
3. **Combine with email features**: Behavioral + OSINT = powerful signal
4. **Use for continuous monitoring**: Not just at signup

---

## 🔧 Testing

```bash
# Test with sample data
python platform_behavioral.py test@example.com

# Test with real data (create integration script)
python your_integration_script.py user@example.com
```

---

## 📝 Next Steps

1. Identify which analytics/database you use
2. Write SQL queries or API calls to fetch the data
3. Format into the structure shown in `create_sample_user_data()`
4. Integrate into your enrichment pipeline
5. Train model with behavioral features included

**This will likely be your HIGHEST-VALUE feature source for credit scoring!**

---

**Version:** 3.3.0
**Cost:** $0 (uses your existing data)
**Setup Time:** 1-2 hours
**Value:** ⭐⭐⭐⭐⭐ CRITICAL
