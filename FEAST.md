# Feast Feature Store Integration

Integration with [Feast](https://feast.dev/) - open source feature store for machine learning.

## 📋 Overview

Feast provides:
- **Online Store** (Redis) - Low-latency feature serving for real-time predictions
- **Offline Store** (Parquet) - Historical features for training datasets
- **Feature Registry** - Centralized feature definitions and metadata
- **Point-in-Time Joins** - Time-travel correct feature retrieval
- **Feature Versioning** - Track feature lineage and changes

## 🏗️ Architecture

```
Email Intelligence Pipeline
         ↓
   291 Features Generated
         ↓
    Feast Integration
    /              \
Online Store      Offline Store
(Redis)           (Parquet)
   ↓                  ↓
Real-time         Training
Predictions       Datasets
```

## 🚀 Quick Start

### 1. Install Feast

**⚠️ IMPORTANT**: Feast has dependency conflicts with some packages in this repo (scipy, tts). We recommend installing in a separate virtual environment:

```bash
# Create separate environment for Feast
python -m venv feast_env
source feast_env/bin/activate  # On Windows: feast_env\Scripts\activate

# Install Feast
pip install feast pandas pyarrow redis

# Install minimal dependencies for enrichment
pip install requests python-dotenv python-whois dnspython
```

Alternatively, see [FEAST_INSTALL.md](FEAST_INSTALL.md) for Docker and other installation options.

### 2. Initialize Feature Repository

The feature repository is already configured in `feature_repo/`:

```
feature_repo/
├── feature_store.yaml    # Feast configuration
├── features.py           # Feature definitions (291 features)
└── data/                 # Parquet files (auto-generated)
```

### 3. Apply Feature Definitions

```bash
cd feature_repo
feast apply
```

This registers all 291 features in Feast registry.

### 4. Enrich Emails and Push to Feast

```bash
# Enrich single email and push to Feast
python feast_integration.py push user@example.com

# Enrich multiple emails
python feast_integration.py push user1@example.com user2@company.com user3@startup.io

# Skip commercial APIs (100% free)
python feast_integration.py push test@example.com --skip-commercial
```

### 5. Get Features for Real-Time Prediction

```bash
# Fetch online features
python feast_integration.py get user@example.com
```

## 📊 Feature Views

Features are organized into 7 views for better management:

### 1. Identity Features (25 features)
- Email validation and format
- Name extraction
- Domain analysis
- TTL: 90 days

### 2. Social Features (35 features)
- GitHub activity
- Gravatar profile
- Social media presence
- TTL: 30 days

### 3. Security Features (25 features)
- Data breaches
- Email reputation
- Spam/fraud detection
- TTL: 7 days

### 4. Behavioral Features (25 features)
- Activity patterns
- Device fingerprinting
- Engagement metrics
- TTL: 1 day

### 5. Technical Features (20 features)
- IP geolocation
- Network intelligence
- Connection analysis
- TTL: 7 days

### 6. Commercial Features (40 features)
- Hunter.io verification
- EmailRep reputation
- Clearbit enrichment
- TTL: 7 days

### 7. Derived Scores (25 features)
- Trust score
- Fraud risk
- Lead score
- Engagement level
- TTL: 7 days

## 🐍 Python SDK Usage

### Online Features (Real-Time Serving)

```python
from feast_integration import FeastFeatureStore

# Initialize
feast = FeastFeatureStore(repo_path="./feature_repo")

# Get features for prediction
features_df = feast.get_online_features(
    emails=["user@example.com"],
    features=[
        "identity_features:is_valid_format",
        "security_features:trust_score",
        "derived_scores:fraud_risk_score",
        "social_features:github_followers"
    ]
)

print(features_df)
# Output:
#              email  is_valid_format  trust_score  fraud_risk_score  github_followers
# 0  user@example.com             True         0.85              0.12               342
```

### Historical Features (Training Data)

```python
import pandas as pd
from datetime import datetime

# Prepare training data
entity_df = pd.DataFrame({
    "email": ["user1@example.com", "user2@startup.io"],
    "event_timestamp": [
        datetime(2024, 1, 15),
        datetime(2024, 1, 20)
    ]
})

# Get point-in-time correct features
training_df = feast.get_historical_features(
    entity_df=entity_df,
    features=[
        "security_features:trust_score",
        "derived_scores:fraud_risk_score",
        "behavioral_features:engagement_score"
    ]
)

# Use for ML training
X = training_df.drop(columns=["label"])
y = training_df["label"]
```

### Batch Enrichment and Push

```python
from feast_integration import FeastFeatureStore

feast = FeastFeatureStore()

# Enrich batch of emails
emails = [
    "user1@example.com",
    "user2@company.com",
    "user3@startup.io"
]

# Enrich and convert to DataFrame
df = feast.enrich_to_dataframe(emails)

# Push to Feast (offline + online stores)
feast.push_features(df)

print(f"✅ Pushed {len(df)} records to Feast")
```

### Incremental Materialization

```python
# Update online store with latest data
feast.materialize_incremental()
```

Run this periodically (cron job) to keep online features fresh:

```bash
# Every hour
0 * * * * cd /path/to/project && python -c "from feast_integration import FeastFeatureStore; FeastFeatureStore().materialize_incremental()"
```

## 🔄 Feature Serving Workflow

### Training Pipeline

```python
# 1. Enrich historical emails
emails_df = pd.read_csv("historical_emails.csv")  # email, event_timestamp, label
emails = emails_df["email"].tolist()

# 2. Enrich with pipeline
feast = FeastFeatureStore()
enriched_df = feast.enrich_to_dataframe(emails)

# 3. Push to offline store
feast.push_features(enriched_df)

# 4. Get training features (point-in-time correct)
training_df = feast.get_historical_features(
    entity_df=emails_df[["email", "event_timestamp"]],
    features=feast.get_store().list_all_feature_views()
)

# 5. Train model
from sklearn.ensemble import RandomForestClassifier
X = training_df.select_dtypes(include=[float, int])
y = emails_df["label"]
model = RandomForestClassifier().fit(X, y)
```

### Prediction Pipeline

```python
# 1. Get fresh features from online store
new_emails = ["prospect@newcompany.com"]

features_df = feast.get_online_features(
    emails=new_emails,
    features=["security_features:trust_score", "derived_scores:fraud_risk_score"]
)

# 2. Make prediction
prediction = model.predict(features_df)
```

## 🏭 Production Deployment

### Configuration

Edit `feature_repo/feature_store.yaml` for production:

```yaml
project: email_intelligence
registry: s3://your-bucket/feast/registry.db  # S3 for distributed access
provider: aws

online_store:
  type: redis
  connection_string: redis.production.com:6379
  ssl: true
  password: ${REDIS_PASSWORD}

offline_store:
  type: snowflake  # or BigQuery, Redshift
  account: your_account
  database: feast
  schema: email_features
```

### Materialization Schedule

Use Airflow/Prefect to schedule:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta

def materialize_features():
    from feast_integration import FeastFeatureStore
    feast = FeastFeatureStore(repo_path="/opt/feast/repo")
    feast.materialize_incremental()

with DAG(
    "feast_materialization",
    schedule_interval=timedelta(hours=1),
    catchup=False
) as dag:

    materialize = PythonOperator(
        task_id="materialize_features",
        python_callable=materialize_features
    )
```

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

  feast-server:
    image: feastdev/feature-server:latest
    ports:
      - "6566:6566"
    environment:
      - FEAST_REPO_PATH=/feast/repo
    volumes:
      - ./feature_repo:/feast/repo
    depends_on:
      - redis

  enrichment-worker:
    build: .
    command: python streaming.py worker --workers 4
    environment:
      - REDIS_HOST=redis
      - FEAST_REPO_PATH=/feast/repo
    volumes:
      - ./feature_repo:/feast/repo
    depends_on:
      - redis
      - feast-server

volumes:
  redis-data:
```

## 📈 Monitoring

### Feature Statistics

```python
from feast import FeatureStore

store = FeatureStore(repo_path="./feature_repo")

# Get feature view info
fv = store.get_feature_view("security_features")
print(f"Features: {len(fv.schema)}")
print(f"TTL: {fv.ttl}")
print(f"Tags: {fv.tags}")

# List all features
for fv in store.list_feature_views():
    print(f"{fv.name}: {len(fv.schema)} features")
```

### Data Quality Checks

```python
# Check feature freshness
import pandas as pd

df = feast.get_online_features(
    emails=["test@example.com"],
    features=["derived_scores:data_freshness_score"]
)

freshness = df["data_freshness_score"].iloc[0]
if freshness < 0.7:
    print("⚠️ Features are stale, running enrichment...")
```

## 🔗 Integration with ML Frameworks

### Scikit-learn

```python
from feast_integration import FeastFeatureStore
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

class FeastTransformer:
    def __init__(self):
        self.feast = FeastFeatureStore()

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # X is DataFrame with 'email' column
        features_df = self.feast.get_online_features(
            emails=X["email"].tolist()
        )
        return features_df

pipeline = Pipeline([
    ("feast", FeastTransformer()),
    ("clf", RandomForestClassifier())
])

pipeline.fit(train_df, train_labels)
predictions = pipeline.predict(test_df)
```

### PyTorch

```python
import torch
from torch.utils.data import Dataset

class EmailFeaturesDataset(Dataset):
    def __init__(self, emails, labels):
        self.feast = FeastFeatureStore()
        self.features = self.feast.get_online_features(emails)
        self.labels = torch.tensor(labels)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        features = torch.tensor(
            self.features.iloc[idx].values,
            dtype=torch.float32
        )
        return features, self.labels[idx]
```

## 📚 Best Practices

1. **TTL Strategy**
   - Identity features: 90 days (stable)
   - Social features: 30 days (semi-stable)
   - Security features: 7 days (dynamic)
   - Behavioral features: 1 day (real-time)

2. **Batch Enrichment**
   - Enrich in batches of 100-1000 emails
   - Use streaming pipeline for continuous updates
   - Run materialization every 1-6 hours

3. **Feature Selection**
   - Start with derived_scores (25 high-level features)
   - Add domain-specific features as needed
   - Monitor feature importance in models

4. **Data Freshness**
   - Monitor `data_freshness_score` feature
   - Set up alerts for stale features
   - Re-enrich if freshness < 0.7

5. **Cost Optimization**
   - Use `skip_commercial=True` for free tier
   - Cache aggressively (90-day TTL for stable features)
   - Batch API calls to reduce cost

## 🆘 Troubleshooting

### Registry Not Found

```bash
cd feature_repo
feast apply
```

### Redis Connection Error

Check Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Features Not Found

Ensure features are materialized:
```python
feast.materialize_incremental()
```

### Parquet File Issues

Clear and regenerate:
```bash
rm -rf feature_repo/data/*.parquet
python feast_integration.py push user@example.com
```

## 📖 Learn More

- [Feast Documentation](https://docs.feast.dev/)
- [Feast GitHub](https://github.com/feast-dev/feast)
- [Feast Examples](https://github.com/feast-dev/feast/tree/master/examples)
- [Feature Store Concepts](https://www.featurestore.org/)

## 🎯 Next Steps

1. **Experiment**: Enrich sample emails and explore features
2. **Train Models**: Use historical features for ML training
3. **Deploy**: Set up production materialization pipeline
4. **Monitor**: Track feature quality and model performance
5. **Optimize**: Tune TTLs and feature selection for your use case
