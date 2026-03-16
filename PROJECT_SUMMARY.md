# 📊 Email Intelligence System - Complete Feature Breakdown

## 🎯 Project Status: v4.0 - Production Ready + Real-time Streaming

**Total Features Available: 291**
**Deployment Options**: CLI, Python Library, REST API, Streaming Workers

---

## 📦 Data Sources Overview

| Source | Features | Cost | Status | Use Case | Documentation |
|--------|----------|------|--------|----------|---------------|
| **OSINT Core** | 78 | $0 | ✅ Active | Identity, presence | README.md |
| **Hunter.io** | 13 | $49/month | ✅ Active | Email verification | commercial_apis.py |
| **IPQualityScore** | 20 | 5K/month free | ✅ Active | Fraud detection | ADDITIONAL_SOURCES.md |
| **Free Sources** | 53 | $0 | ✅ Active | Patterns, IP intel | free_sources.py |
| **Platform Behavioral** | 40 | $0* | ✅ Ready | Engagement patterns | BEHAVIORAL_INTEGRATION.md |
| **WHOIS/DNS** | 13 | $0 | ⚠️ Partial | Domain intelligence | ADDITIONAL_SOURCES.md |
| **Redis Cache** | - | $0-20/month | ✅ Active | Performance | REDIS_CACHE.md |
| **Twitter** | 13 | $100+/month | ❌ Paid | Social presence | - |
| **EmailRep** | 15 | Pending | ❌ Requires approval | Reputation | - |
| **Clearbit** | 12 | $99-499/month | ❌ Expensive | B2B enrichment | - |
| **LinkedIn** | 15 | TBD | ⚠️ Placeholder | Professional | ADDITIONAL_SOURCES.md |
| **StackOverflow** | 11 | $0 | ⚠️ Placeholder | Technical profile | ADDITIONAL_SOURCES.md |

*Requires your own platform data

---

## ✅ Active Sources (204 features, 100% free)

### 1. OSINT Core (78 features) - **$0/month**

Extracts comprehensive data from public sources:

- **GitHub**: Profile, repositories, followers, contributions, activity history
- **Gravatar**: Avatar presence and public profile
- **Email Validation**: Format checking, provider detection, disposable detection
- **HIBP**: Data breach history checking
- **Domain Analysis**: Provider type, risk scoring
- **Temporal Patterns**: Account age, activity velocity, engagement metrics
- **NLP Analysis**: Bio text, location extraction, company detection
- **Anomaly Detection**: Suspicious patterns, outlier detection
- **Derived Scores**: Trust, identity strength, security risk

**Setup:** No API key needed (GitHub token optional for higher rate limits)
**Documentation:** [README.md](README.md)

---

### 2. IPQualityScore (20 features) - **5K/mes gratis**
- Fraud score (0-100)
- Email validation
- Leaked credentials detection ⚠️
- Spam trap detection
- Disposable email detection
- Domain velocity
- SMTP validation
- Overall quality score

**Setup:** [https://www.ipqualityscore.com/create-account](https://www.ipqualityscore.com/create-account)  
**Documentation:** [ADDITIONAL_SOURCES.md](ADDITIONAL_SOURCES.md)

---

### 3. Free Sources (53 features) - **$0/mes**

#### IP Intelligence (15 features)
- Country, city, region
- ISP, ASN, timezone
- Connection type (datacenter/mobile/vpn/residential)
- EU flag, continent

**API:** ipapi.co (30K/mes gratis)

#### Email Pattern Analysis (20 features)
- Name extraction
- Professional pattern detection
- Shannon entropy (randomness)
- Year extraction and age calculation
- Separator detection
- Numeric ratio
- Readability score

**Cost:** $0 (pure code)

#### Username Search (10 features)
- Instagram, TikTok, Pinterest, Reddit
- YouTube, Medium, Spotify, Twitch
- Platforms found count

**Cost:** $0 (HTTP checks)

#### Google Search Presence (5 features)
- Email mentions
- LinkedIn/GitHub/Twitter presence
- Search count

**Cost:** $0 (scraping)

**Documentation:** [free_sources.py](free_sources.py)

---

### 4. Platform Behavioral (40 features) - **$0/month**

**HIGHEST VALUE SOURCE** - Extracts behavioral patterns from your platform data

#### Account & Temporal (3)
- Account age (days, weeks, months)

#### Session Patterns (9)
- Total sessions, recent activity (7/30 days)
- Duration statistics (avg, median, max)
- Sessions per week
- Days since last session
- Consistency score (regularity metric)

#### Engagement (7)
- Total events, clicks, pageviews
- Time on platform
- Engagement rate
- Bounce rate

#### Device & Tech (6)
- Unique devices count
- Primary device type
- Browser/OS diversity
- Mobile/desktop usage patterns

#### Geographic Consistency (5)
- Unique IPs, countries, cities
- Country changes (mobility indicator)
- Geo consistency score

#### Form Completion (4)
- Forms submitted/abandoned
- Completion rate
- Average completion time

#### Temporal Patterns (4)
- Most common login hour
- Weekday/weekend activity ratio
- Night activity ratio

**Value:** Behavioral data is unique per user, impossible to fake, and highly predictive
**Setup:** 1-2 hours (requires database/analytics integration)
**Documentation:** [BEHAVIORAL_INTEGRATION.md](BEHAVIORAL_INTEGRATION.md)

---

## 💰 Optional Commercial APIs (+13-47 features)

### Hunter.io - **$49/month** (13 features)
- Email deliverability verification
- SMTP validation
- Corporate email detection
- Email sources count
- Domain information

**Status:** ✅ Active
**Use Case:** B2B lead validation, email verification
**Value:** ⭐⭐⭐ Recommended for B2B applications

---

## 🚀 Usage

### Basic (OSINT only - 78 features)
```bash
python full_enrichment.py usuario@ejemplo.com --skip-commercial --skip-additional
```

### Recommended (All free sources - 204 features)
```bash
python full_enrichment.py usuario@ejemplo.com --ip 181.45.123.45
```

### With Behavioral Data (244 features)
```python
from full_enrichment import FullEnrichmentPipeline
from platform_behavioral import PlatformBehavioralEnricher

# Get behavioral data from your platform
behavioral_data = get_user_behavioral_data(email)  # Your function

# Run full pipeline
pipeline = FullEnrichmentPipeline(ip_address=user_ip)
results = pipeline.enrich_email(email)

# Add behavioral features
behavioral_enricher = PlatformBehavioralEnricher()
behavioral_features = behavioral_enricher.enrich_user(behavioral_data)

# Combine for ML
all_features = {
    **results['features']['all_features'],
    **behavioral_features
}
```

---

## 📈 Feature Breakdown by Category

### Identity & Validation (45 features)
- Email format, provider, domain analysis
- Name extraction from email
- Professional pattern detection
- Gravatar presence
- Digital footprint count

### Security & Risk (35 features)
- IPQS fraud score
- Leaked credentials
- Spam trap/honeypot detection
- Breach count (HIBP)
- Geographic consistency
- IP connection type

### Social & Professional Presence (60 features)
- GitHub activity (repos, followers, contributions)
- Username presence (8 platforms)
- Google search mentions
- Domain age and DNS security

### Engagement & Behavior (40 features)
- Session patterns
- Click/pageview metrics
- Form completion behavior
- Temporal activity patterns
- Device diversity

### Technical & Geolocation (30 features)
- IP geolocation (country, city, timezone)
- Device fingerprinting
- Browser/OS detection
- Connection type classification

### Derived Scores (25 features)
- Trust score
- Identity strength
- Security risk
- Activity engagement
- Data quality
- Professional signal
- Anomaly score

### Commercial API (56 features - optional)
- Hunter.io verification (13)
- EmailRep reputation (15) - pending
- Clearbit person/company (12) - expensive
- Additional sources (16) - Twitter/LinkedIn/etc

---

## 🎯 Recommended Configurations

### Free Tier - 164 features, $0/month
```
✅ OSINT Core (78)
✅ IPQualityScore (20) - 5K requests/month free
✅ Free Sources (53) - IP intel, patterns, username search
✅ WHOIS/DNS (13)
```
**Use Case:** Personal projects, MVPs, low-volume applications

### Recommended - 204 features, $0/month*
```
✅ Free Tier (164)
✅ Platform Behavioral (40) - your own data
```
**Use Case:** Production applications with user base
*Requires integration with your platform data (1-2 hours setup)

### Commercial - 217 features, $49/month
```
✅ Recommended (204)
✅ Hunter.io (13) - email verification
```
**Use Case:** B2B applications, lead verification, high-quality needs

### Enterprise - 244+ features, $150+/month
```
✅ Commercial (217)
✅ EmailRep (15) - pending approval
✅ Twitter (13) - $100+/month
```
**Use Case:** Full enrichment, social intelligence, comprehensive profiling

---

## 💡 Integration Checklist

- [x] OSINT Core - Active
- [x] IPQualityScore API key configured
- [x] Free Sources implemented
- [ ] Behavioral data integration (1-2 hours)
  - [ ] Identify data source (database/analytics)
  - [ ] Write query/API integration
  - [ ] Test with sample users
  - [ ] Integrate into pipeline
- [ ] Optional: Hunter.io ($49/mes)
- [ ] Optional: HIBP API ($3.50/mes)

---

## 📊 Expected Coverage & Quality

With **204 free features** (OSINT + IPQS + Free Sources + Behavioral):

- **Coverage:** 85-90% of users will have 150+ features populated
- **Data Quality:** High (combines multiple independent sources)
- **Cost:** $0-3.50/month (optional HIBP API)
- **Setup Time:** 2-4 hours (including behavioral integration)

**Key Feature Insights:**
- **Behavioral data**: User-specific, impossible to fake, highly predictive for engagement models
- **Email patterns**: Entropy and professional patterns correlate with user quality
- **Session consistency**: Regular activity indicates genuine user engagement
- **Geographic consistency**: Stable location patterns vs. suspicious mobility
- **Security flags**: Breach history, leaked credentials, disposable emails

---

## 🔧 Technical Architecture

```
┌─────────────────────────────────────────────────┐
│      Full Enrichment Pipeline (v3.4)            │
│         + Redis Caching Layer                   │
└─────────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────┐
        │            │            │          │
    ┌───▼───┐   ┌───▼───┐   ┌───▼───┐  ┌──▼───┐
    │ OSINT │   │ Free  │   │ IPQS  │  │Behav.│
    │  (78) │   │  (53) │   │  (20) │  │ (40) │
    └───┬───┘   └───┬───┘   └───┬───┘  └──┬───┘
        │            │            │         │
        └────────────┴────────────┴─────────┘
                     │
              ┌──────▼──────┐
              │  Enhanced   │
              │   Feature   │
              │  Engineer   │
              │   (291)     │
              └─────────────┘
                     │
              ┌──────▼──────┐
              │   Output    │
              │ • JSON      │
              │ • ML-ready  │
              │ • Summary   │
              └─────────────┘
```

---

## 📝 Getting Started

### Quick Start (5 minutes)

1. **Clone and install**
   ```bash
   git clone https://github.com/guzzipa/feature-generation-email.git
   cd feature-generation-email
   pip install -r requirements.txt
   ```

2. **Basic enrichment** (100% free)
   ```bash
   python full_enrichment.py user@example.com
   ```

3. **Enable caching** (optional, 10x faster)
   ```bash
   brew install redis  # macOS
   brew services start redis
   python full_enrichment.py user@example.com  # auto-detects Redis
   ```

### Next Steps

1. ✅ **Try the examples** - Run with test emails
2. 🔄 **Integrate behavioral data** (if you have platform users)
3. 📊 **Use in your ML pipeline** - Extract features for your models
4. 📈 **Monitor performance** - Enable Redis caching for production
5. 💰 **Add commercial APIs** (optional, if needed for your use case)

---

## 🎉 Project Status

**Status:** ✅ Production Ready (v4.0)
**Total Features:** 291 (204 free + 40 behavioral + 47 optional commercial)
**Cost:** $0-150/month (depending on configuration)
**Performance:** 2-10x faster with Redis caching, 4,500+ emails/hour with streaming
**Deployment:** CLI, Python Library, REST API, Real-time Streaming (NEW)
**Use Cases:** User profiling, identity verification, fraud detection, lead scoring, ML training

**Repository:** [https://github.com/guzzipa/feature-generation-email](https://github.com/guzzipa/feature-generation-email)

---

## 🚀 Deployment Options

### 1. Command Line Interface
```bash
python full_enrichment.py user@example.com
```

### 2. Python Library
```python
from full_enrichment import FullEnrichmentPipeline
pipeline = FullEnrichmentPipeline()
results = pipeline.enrich_email('user@example.com')
```

### 3. REST API Service (v3.5)
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```
**API Documentation**: http://localhost:8000/docs

### 4. Real-time Streaming (NEW in v4.0)
```bash
# Start workers
python streaming.py worker --workers 4

# Submit jobs
python streaming.py submit user@example.com

# Monitor
python streaming.py monitor
```
**Streaming Documentation**: [STREAMING.md](STREAMING.md)
**Throughput**: 4,500+ emails/hour with horizontal scaling

---

**Version:** 4.0.0
**Last Updated:** 2026-03-16
**License:** MIT
