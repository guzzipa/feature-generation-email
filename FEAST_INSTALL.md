# Feast Installation Guide

Due to dependency conflicts between Feast and other libraries in this project, you may need to install Feast in a separate virtual environment.

## Option 1: Separate Virtual Environment (Recommended)

```bash
# Create new virtual environment for Feast
python -m venv feast_env
source feast_env/bin/activate

# Install Feast dependencies
pip install feast pandas pyarrow redis

# Install email intelligence deps
pip install requests python-dotenv python-whois dnspython

# Run enrichment and push to Feast
python feast_integration.py push user@example.com
```

## Option 2: Fix Dependency Conflicts

If you need everything in one environment:

```bash
# Downgrade pandas to resolve conflicts
pip install 'pandas<2.0' 'numpy>=2.0'

# Or use a fresh Python 3.11+ environment
```

## Option 3: Use Docker

We provide a Dockerfile with all dependencies pre-configured:

```bash
docker build -t email-feast .
docker run -it email-feast bash

# Inside container
python feast_integration.py push user@example.com
```

## Verification

Once installed, verify Feast is working:

```bash
cd feature_repo
feast version
feast apply
```

You should see output like:
```
Created entity email
Created feature view identity_features
Created feature view social_features
...
```

## Troubleshooting

### NumPy Version Conflicts

```bash
# Feast requires numpy>=2.0, but scipy requires numpy<2
# Solution: Use separate environments or wait for scipy update
pip install scipy --upgrade
```

### Redis Connection Error

Ensure Redis is running:
```bash
brew services start redis
redis-cli ping  # Should return PONG
```

### Feature Store Not Found

Initialize the repository:
```bash
cd feature_repo
feast apply
```

## Production Deployment

For production, use containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN cd feature_repo && feast apply

CMD ["python", "feast_integration.py", "worker"]
```
