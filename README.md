# 🔍 Email Intelligence & Feature Extraction

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: clean](https://img.shields.io/badge/code%20style-clean-brightgreen.svg)](https://github.com/guzzipa/feature-generation-email)

Comprehensive email intelligence system that extracts 291+ structured features from email addresses using OSINT data, commercial APIs, and behavioral analysis. Turn an email into rich, actionable data for ML models.

> ⚡ **v3.5**: 291 features from 11+ data sources with Redis caching + REST API service

## 🎯 What It Does

Extract comprehensive, structured features from email addresses by combining public data (OSINT), commercial APIs, and behavioral patterns. Use cases include:

- **User profiling and segmentation**
- **Identity verification and validation**
- **Fraud detection and security**
- **Lead scoring and enrichment**
- **User research and analytics**
- **ML model training (any domain)**

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/guzzipa/feature-generation-email.git
cd feature-generation-email

# Install dependencies
pip install -r requirements.txt

# Optional: Install Redis for caching
brew install redis  # macOS
# or: sudo apt install redis-server  # Linux
```

### Basic Usage

```bash
# Enrich single email (all free sources)
python full_enrichment.py user@example.com

# With IP address for geolocation
python full_enrichment.py user@example.com --ip 181.45.123.45

# Skip commercial APIs (100% free)
python full_enrichment.py user@example.com --skip-commercial

# Force refresh (bypass cache)
python full_enrichment.py user@example.com --force-refresh
```

### Programmatic Usage

```python
from full_enrichment import FullEnrichmentPipeline

# Initialize pipeline
pipeline = FullEnrichmentPipeline(
    output_dir='results',
    enable_cache=True
)

# Enrich email
results = pipeline.enrich_email('user@example.com')

# Access features
features = results['features']['all_features']
ml_ready = results['features']['ml_ready']

print(f"Trust Score: {features['overall_trust_score']}")
print(f"Identity Strength: {features['identity_strength_score']}")
print(f"GitHub Repos: {features.get('github_repos', 0)}")
```

## 📂 Estructura del Proyecto

```
feature-generation-email/
├── osint_email_enrichment.py       # Recolección de datos públicos
├── commercial_apis.py              # Integración Hunter.io, EmailRep, Clearbit
├── advanced_feature_engineering.py # Feature engineering avanzado (103+ features)
├── batch_processing.py             # Procesamiento batch de múltiples usuarios
├── requirements.txt                # Dependencias Python
├── .env.example                    # Template variables de entorno
├── CLAUDE.md                       # Contexto del proyecto
└── examples/
    ├── sample_users.csv           # CSV de ejemplo
    └── example_output.json        # Output de ejemplo
```

## 📊 Features Extracted (291 total)

### 🌐 Data Sources

#### Free Sources (204 features - $0/month)
1. **OSINT Core** (78 features)
   - GitHub: Profile, repos, activity, followers
   - Gravatar: Avatar and public profile
   - HIBP: Data breach information
   - Email validation and pattern analysis

2. **IP Intelligence** (15 features)
   - Geolocation (country, city, timezone)
   - ISP and connection type
   - VPN/proxy detection

3. **Email Pattern Analysis** (20 features)
   - Name extraction
   - Professional pattern detection
   - Entropy and randomness analysis
   - Year extraction and age calculation

4. **Username Search** (10 features)
   - Presence across 8 social platforms
   - Instagram, TikTok, Pinterest, Reddit, etc.

5. **Domain Analysis** (13 features)
   - WHOIS data and domain age
   - DNS records and security
   - Registrar information

6. **Platform Behavioral** (40 features - requires your data)
   - Session patterns and consistency
   - Engagement metrics
   - Device fingerprinting
   - Geographic consistency
   - Form completion behavior

7. **Additional Sources** (28 features)
   - IPQualityScore fraud detection (5K/month free)
   - Google search presence
   - StackOverflow, LinkedIn placeholders

#### Commercial APIs (Optional - 87 features)
- **Hunter.io** (13 features) - Email verification - $49/month
- **EmailRep.io** (15 features) - Reputation scoring
- **Clearbit** (12 features) - Company enrichment
- **Twitter API** (13 features) - Social presence

### 📋 Feature Categories

#### Identity & Validation (45 features)
- Email format, provider, domain analysis
- Name extraction and professional patterns
- Digital footprint across platforms
- Account age and history

#### Social & Professional (60 features)
- GitHub activity and contributions
- Social media presence
- Professional bio, location, company
- Online reputation signals

#### Security & Quality (35 features)
- Data breach history
- Disposable/temporary email detection
- Spam trap and honeypot flags
- IP reputation and connection type

#### Behavioral Patterns (40 features)
- Session frequency and duration
- Engagement and interaction metrics
- Device diversity and fingerprinting
- Temporal activity patterns

#### Technical & Geolocation (30 features)
- IP geolocation and timezone
- Browser, OS, device detection
- Domain DNS and WHOIS
- Connection type classification

#### Derived Scores (25 features)
- Overall trust score (0-1)
- Identity strength (0-1)
- Security risk score (0-1)
- Activity engagement (0-1)
- Data quality metrics

## 📈 Output Format

### Complete Enrichment Results

```json
{
  "email": "user@example.com",
  "pipeline_version": "3.4.0",
  "enrichment_timestamp": "2026-03-16T10:30:00",

  "data_sources": {
    "osint": { /* GitHub, Gravatar, HIBP data */ },
    "commercial": { /* Hunter.io, EmailRep, Clearbit */ },
    "additional": { /* WHOIS, IPQS, social platforms */ },
    "free_sources": { /* IP intel, patterns, username search */ }
  },

  "features": {
    "all_features": { /* 291 features */ },
    "ml_ready": {
      "numerical": [ /* normalized 0-1 values */ ],
      "categorical": [ /* encoded categories */ ]
    },
    "feature_count": 291
  },

  "summary": {
    "trust_score": 0.812,
    "identity_strength": 0.900,
    "security_risk": 0.040,
    "activity_engagement": 0.756,
    "data_quality": 0.890
  }
}
```

### ML-Ready Features

```python
# Numerical features (ready for sklearn, tensorflow, etc)
numerical_features = results['features']['ml_ready']['numerical']
# [0.812, 0.900, 0.040, 11.76, 16, 0, ...]

# Categorical features (encoded)
categorical_features = results['features']['ml_ready']['categorical']
# ['gmail', 'AR', 'full', 'residential', ...]

# Use directly in ML models
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(X_train, y_train)
predictions = model.predict(numerical_features)
```

## 🎓 ML Integration Examples

### Scikit-learn

```python
from full_enrichment import FullEnrichmentPipeline
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Enrich multiple users
pipeline = FullEnrichmentPipeline(enable_cache=True)
emails = ['user1@example.com', 'user2@example.com', ...]

# Extract features
features_list = []
for email in emails:
    result = pipeline.enrich_email(email)
    features_list.append(result['features']['ml_ready']['numerical'])

X = np.array(features_list)

# Train your model (example: user conversion prediction)
model = RandomForestClassifier()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

### Feature Importance

Features are ranked by information value across multiple domains:

**High Impact Features** (general purpose):
- `account_age_years` - Digital footprint age
- `overall_trust_score` - Composite trust metric
- `identity_strength_score` - Profile completeness
- `github_repos` - Technical activity signal
- `digital_footprint_count` - Platform presence

**Domain-Specific Features**:
- `is_disposable_email` - Quality filtering
- `is_corporate_email` - B2B segmentation
- `security_risk_score` - Security applications
- `activity_engagement_score` - User engagement
- `breach_count` - Security awareness

## 📊 Real Example

```bash
$ python full_enrichment.py john.doe@example.com

# OUTPUT:
{
  "email": "john.doe@example.com",
  "summary": {
    "trust_score": 0.812,
    "identity_strength": 0.900,
    "security_risk": 0.040,
    "activity_engagement": 0.756
  },
  "features": {
    "account_age_years": 11.8,
    "github_repos": 16,
    "has_gravatar": true,
    "breach_count": 0,
    "is_corporate_email": false,
    "digital_footprint_count": 5,
    "location_country": "AR"
  }
}

# ✅ Strong digital identity (11.8 years)
# ✅ Active on GitHub (16 repos)
# ✅ Present on 5 platforms
# ✅ No security breaches
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# APIs Públicas (opcional - mejoran rate limits)
GITHUB_TOKEN=ghp_your_token_here        # 60 → 5000 req/hora
HIBP_API_KEY=your_hibp_key_here         # Requerido para producción

# APIs Comerciales (requeridas para v3.0)
HUNTER_API_KEY=your_hunter_key          # hunter.io
EMAILREP_API_KEY=your_emailrep_key      # emailrep.io
CLEARBIT_API_KEY=your_clearbit_key      # clearbit.com

# Configuración
CACHE_TTL_DAYS=30
MAX_RETRIES=3
REQUEST_TIMEOUT=10
```

## 🚀 Batch Processing

Process multiple emails efficiently with built-in caching:

```python
from full_enrichment import FullEnrichmentPipeline
import pandas as pd

# Load email list
df = pd.read_csv('users.csv')
emails = df['email'].tolist()

# Initialize pipeline with caching
pipeline = FullEnrichmentPipeline(enable_cache=True)

# Process batch
results = []
for email in emails:
    result = pipeline.enrich_email(email)
    results.append({
        'email': email,
        'trust_score': result['summary']['trust_score'],
        'github_repos': result['features']['all_features'].get('github_repos', 0),
        'digital_footprint': result['features']['all_features'].get('digital_footprint_count', 0)
    })

# Save to CSV
pd.DataFrame(results).to_csv('enrichment_results.csv', index=False)
```

### Performance

- **First run**: ~3-5 seconds per email (API calls)
- **Cached**: <100ms per email (⚡ 30-50x faster)
- **Recommended**: Enable Redis caching for production
- **Throughput**: 1000+ emails/hour with caching

## ⚠️ Consideraciones de Producción

### Rate Limits
- **GitHub API**: 60 req/hora (sin token) → 5000/hora (con token)
- **HIBP**: Requiere API key ($) para producción
- **Gravatar**: Sin límites conocidos

### Performance
- **Tiempo por email**: ~2-3 segundos
- **Batch recomendado**: 2.5s entre requests (rate limiting)
- **Procesamiento**: Asíncrono/batch, NO en tiempo real

### Caching
- **TTL recomendado**: 30-90 días para datos estáticos
- **TTL breach check**: 7 días
- **Storage**: Redis, DynamoDB, o similar

### Privacidad & Compliance
- ✅ Solo datos públicamente disponibles
- ✅ Respetar GDPR/CCPA
- ✅ Informar a usuarios sobre enriquecimiento
- ✅ Permitir opt-out
- ❌ No almacenar datos sensibles sin consentimiento

## 🔐 Privacy & Security

- ✅ Uses only publicly available data
- ✅ GDPR/CCPA compliant (no PII storage)
- ✅ Configurable data sources
- ✅ Opt-out support
- ✅ Rate limiting and retry logic
- ✅ Secure API key management (.env)

### Security Flags

The system automatically detects:
- Disposable/temporary emails
- Data breach history
- VPN/proxy usage
- Suspicious patterns
- Anomalous behavior

## 📚 Documentation

- [REDIS_CACHE.md](REDIS_CACHE.md) - Redis caching setup and optimization
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete feature breakdown (291 features)
- [BEHAVIORAL_INTEGRATION.md](BEHAVIORAL_INTEGRATION.md) - Platform behavioral data integration
- [ADDITIONAL_SOURCES.md](ADDITIONAL_SOURCES.md) - Extra data sources guide

## 🌐 REST API Service (NEW in v3.5)

Deploy as HTTP API service for easy integration:

```bash
# Start API server
uvicorn api:app --reload --port 8000

# Visit http://localhost:8000/docs for interactive API documentation
```

### API Examples

```bash
# Enrich email via REST API
curl -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Batch enrichment (up to 100 emails)
curl -X POST http://localhost:8000/enrich/batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["user1@example.com", "user2@example.com"]}'
```

**Full API Documentation**: [API.md](API.md)

## Real-time Streaming Enrichment (NEW in v4.0)

Process emails at scale using Redis Streams for distributed, async enrichment:

```bash
# Start workers (distributed processing)
python streaming.py worker --workers 4

# Submit jobs
python streaming.py submit user@example.com

# Monitor stream
python streaming.py monitor
```

### Architecture

```
Producer → Redis Stream → Consumer Group → Workers → Results
                                    ↓
                               Metrics & DLQ
```

### Key Features

- **Distributed Processing**: Multiple workers process jobs in parallel
- **Consumer Groups**: Automatic load balancing
- **Dead Letter Queue**: Failed jobs handling with retry logic
- **Metrics Tracking**: Real-time monitoring of throughput and errors
- **Horizontal Scaling**: Add workers dynamically
- **High Throughput**: Process 4,500+ emails/hour

### Use Cases

- Batch enrichment of existing user databases
- Async enrichment on user signup (non-blocking)
- Scheduled refresh of stale user data
- High-volume lead processing

**Full Streaming Documentation**: [STREAMING.md](STREAMING.md)

---

## 🎯 Feast Feature Store Integration (NEW in v4.1)

Push enriched features to [Feast](https://feast.dev/) for ML model training and real-time serving:

```bash
# Initialize Feast repository
cd feature_repo && feast apply

# Enrich and push to Feast
python feast_integration.py push user@example.com

# Get online features for real-time prediction
python feast_integration.py get user@example.com
```

### Architecture

```
Email → Enrichment → 291 Features → Feast
                                      ├─ Online Store (Redis)
                                      └─ Offline Store (Parquet)
                                           ↓
                              ML Training & Real-Time Serving
```

### Key Features

- **7 Feature Views**: Identity, Social, Security, Behavioral, Technical, Commercial, Derived
- **Online Serving**: Low-latency feature retrieval for predictions (< 10ms)
- **Offline Training**: Point-in-time correct historical features
- **Smart TTLs**: 1-90 days based on feature stability
- **Feature Versioning**: Track lineage and changes
- **ML Framework Integration**: Works with scikit-learn, PyTorch, TensorFlow

### Use Cases

- Train fraud detection models with historical features
- Real-time lead scoring with online features
- A/B testing with feature flags
- Point-in-time correct training datasets
- Feature reuse across ML models

**Full Feast Documentation**: [FEAST.md](FEAST.md)

---

## 📊 Interactive Dashboard (NEW in v4.2)

Web-based dashboard for visual email analysis and system monitoring:

```bash
# Install dashboard dependencies
pip install streamlit plotly pandas

# Launch dashboard
streamlit run streamlit_app.py
```

Opens automatically at `http://localhost:8501`

### Dashboard Features

**Main Page: Email Analysis**
- Real-time email enrichment with progress indicators
- Summary metrics with color-coded scores
- Interactive radar charts
- Feature breakdown by category (7 tabs)
- GitHub profile integration
- Security analysis dashboard
- JSON export functionality

**System Monitor Page**
- Redis cache statistics and hit rates
- Streaming worker metrics and health
- Job queue monitoring
- Cache management tools
- Real-time auto-refresh

**Feature Explorer Page**
- Browse all 291 features
- Search and filter capabilities
- Feature type distribution
- Use case templates (Fraud, Lead Scoring, Segmentation)
- Export feature catalog as CSV

### Key Capabilities

- **Email Comparison**: Side-by-side analysis of two emails
- **History Tracking**: Timeline of analyzed emails with trends
- **Mobile Responsive**: Works on phones and tablets
- **Export Options**: JSON, CSV, metrics data
- **Production Ready**: Docker deployment, Streamlit Cloud compatible

**Full Dashboard Documentation**: [DASHBOARD.md](DASHBOARD.md)

---

## 🤖 Auto-Improvement System (NEW in v5.0)

**Living System**: Self-maintaining and auto-improving project that discovers new data sources, optimizes performance, and suggests features automatically.

```bash
# Run auto-improvement tasks
python auto_improve.py discover    # Find new APIs and data sources
python auto_improve.py health      # Check system health
python auto_improve.py optimize    # Get optimization suggestions
python auto_improve.py analyze     # Discover new features from data

# Start local scheduler (runs tasks automatically)
python scheduler.py start          # Daemon mode
python scheduler.py run-now        # Run all tasks immediately
```

### Automated Capabilities

**🔍 Source Discovery**
- Searches GitHub for relevant open-source projects (weekly)
- Discovers new APIs from directories (ProgrammableWeb, RapidAPI)
- Identifies feature opportunities from new sources
- Auto-creates GitHub issues with discoveries

**🏥 Health Monitoring**
- Checks all API endpoints daily
- Monitors response times and success rates
- Alerts on degraded or failed APIs
- Tracks dependency updates

**⚡ Optimization Engine**
- Analyzes cache performance
- Suggests code optimizations
- Identifies performance bottlenecks
- Recommends architecture improvements

**📊 Feature Analysis**
- Analyzes enrichment data patterns
- Suggests new derived features
- Identifies low-coverage features
- Proposes feature correlations

### GitHub Actions (Automatic)

Runs every **Monday at 9 AM UTC**:

1. ✅ Discovers new data sources
2. ✅ Checks API health
3. ✅ Analyzes performance
4. ✅ Creates GitHub issues/PRs with findings
5. ✅ Updates documentation

### Local Scheduler (Manual)

Alternative to GitHub Actions for local development:

```bash
# Configure schedule
python scheduler.py start

# Schedule:
# • Daily 09:00 - Health Check
# • Monday 09:00 - Source Discovery
# • Monday 10:00 - Optimization Analysis
# • Monthly - Feature Analysis
```

**Full Maintenance Guide**: [MAINTENANCE.md](MAINTENANCE.md)

---

## 🛠️ Roadmap

- ✅ **v1.0**: OSINT core (78 features)
- ✅ **v3.0**: Commercial APIs (Hunter.io, EmailRep, Clearbit)
- ✅ **v3.1**: Additional sources (WHOIS, IPQS, Twitter)
- ✅ **v3.2**: Free sources (IP Intel, patterns, username search)
- ✅ **v3.3**: Platform behavioral data (40 features)
- ✅ **v3.4**: Redis caching layer
- ✅ **v3.5**: REST API service
- ✅ **v4.0**: Real-time streaming enrichment
- ✅ **v4.1**: Feature store integration (Feast)
- ✅ **v4.2**: Interactive dashboard (Streamlit)
- ✅ **v5.0**: Auto-improvement system (Living Project)
- 🔲 AI-powered code improvements (Claude Code integration)
- 🔲 GraphQL API
- 🔲 Webhooks for async notifications
- 🔲 Mobile app (React Native)

## 📄 License

MIT License - Feel free to use for commercial or personal projects.

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Additional data sources
- Performance optimizations
- New feature engineering techniques
- Documentation improvements

## ⭐ Star History

If you find this useful, please star the repository!

---

**Built with Python 3.8+ | Powered by OSINT & ML**
