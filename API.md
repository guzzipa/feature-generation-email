# 🚀 Email Intelligence REST API (v3.5)

Fast, async REST API for email enrichment. Extract 291+ features from email addresses via HTTP endpoints.

---

## 📋 Features

- ⚡ **Async/Await** - High performance with async processing
- 📚 **Auto Documentation** - Swagger UI and ReDoc
- 🔄 **Redis Caching** - Built-in caching support
- 🔐 **API Key Auth** - Optional authentication
- 📦 **Batch Processing** - Enrich up to 100 emails per request
- 🎯 **CORS Enabled** - Ready for web applications
- 📊 **Health Checks** - Monitoring endpoints

---

## 🏁 Quick Start

### Installation

```bash
# Install API dependencies
pip install fastapi uvicorn pydantic python-multipart

# Or update requirements
pip install -r requirements.txt
```

### Run Development Server

```bash
# Start API server
uvicorn api:app --reload --port 8000

# Server will start at http://localhost:8000
```

### Run Production Server

```bash
# Multiple workers for production
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# With gunicorn (recommended)
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📖 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔑 Authentication (Optional)

Set API key in `.env`:

```bash
API_KEY=your_secret_key_here
```

Include in requests:

```bash
curl -H "X-API-Key: your_secret_key_here" \
  http://localhost:8000/enrich/user@example.com
```

---

## 📡 Endpoints

### General

#### `GET /`
Root endpoint with API information

```bash
curl http://localhost:8000/
```

Response:
```json
{
  "name": "Email Intelligence API",
  "version": "3.5.0",
  "description": "Extract 291+ features from email addresses",
  "docs": "/docs",
  "health": "/health"
}
```

#### `GET /health`
Health check endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "3.5.0",
  "timestamp": "2026-03-16T15:30:00",
  "cache_enabled": true,
  "cache_connected": true,
  "features_available": 291
}
```

#### `GET /stats`
API statistics (requires API key)

```bash
curl -H "X-API-Key: your_key" http://localhost:8000/stats
```

---

### Email Enrichment

#### `POST /enrich`
Enrich single email

**Request:**
```bash
curl -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "ip_address": "181.45.123.45",
    "skip_commercial": false,
    "force_refresh": false
  }'
```

**Request Body:**
```json
{
  "email": "user@example.com",           // Required
  "ip_address": "181.45.123.45",         // Optional
  "skip_commercial": false,               // Optional (default: false)
  "skip_additional": false,               // Optional (default: false)
  "force_refresh": false                  // Optional (default: false)
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "pipeline_version": "3.4.0",
  "enrichment_timestamp": "2026-03-16T15:30:00",
  "cached": false,
  "data_sources": {
    "osint": { /* GitHub, Gravatar, HIBP data */ },
    "commercial": { /* Hunter.io data */ },
    "additional": { /* WHOIS, IPQS data */ },
    "free_sources": { /* IP intel, patterns */ }
  },
  "features": {
    "all_features": {
      "overall_trust_score": 0.812,
      "identity_strength_score": 0.900,
      "github_repos": 16,
      // ... 288 more features
    },
    "ml_ready": {
      "numerical": [0.812, 0.900, ...],
      "categorical": ["gmail", "AR", ...]
    },
    "feature_count": 291
  },
  "summary": {
    "trust_score": 0.812,
    "identity_strength": 0.900,
    "security_risk": 0.040,
    "activity_engagement": 0.756
  }
}
```

#### `GET /enrich/{email}`
Enrich email via GET request

**Request:**
```bash
curl "http://localhost:8000/enrich/user@example.com?ip_address=181.45.123.45&skip_commercial=false"
```

**Query Parameters:**
- `ip_address` (optional) - IP address for geolocation
- `skip_commercial` (optional) - Skip commercial APIs (default: false)
- `skip_additional` (optional) - Skip additional sources (default: false)
- `force_refresh` (optional) - Bypass cache (default: false)

**Response:** Same as POST /enrich

---

#### `POST /enrich/batch`
Enrich multiple emails (max 100 per request)

**Request:**
```bash
curl -X POST http://localhost:8000/enrich/batch \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      "user1@example.com",
      "user2@example.com",
      "user3@example.com"
    ],
    "skip_commercial": false
  }'
```

**Request Body:**
```json
{
  "emails": [
    "user1@example.com",
    "user2@example.com"
  ],                              // Required (max 100)
  "ip_address": "181.45.123.45",  // Optional
  "skip_commercial": false,        // Optional
  "skip_additional": false,        // Optional
  "force_refresh": false           // Optional
}
```

**Response:**
```json
{
  "total": 3,
  "success": 3,
  "failed": 0,
  "results": [
    {
      "email": "user1@example.com",
      "pipeline_version": "3.4.0",
      "features": { /* ... */ },
      "summary": { /* ... */ },
      "success": true
    },
    {
      "email": "user2@example.com",
      "features": { /* ... */ },
      "success": true
    },
    // ... more results
  ]
}
```

---

### Cache Management

#### `DELETE /cache/{email}`
Invalidate cache for specific email (requires API key)

```bash
curl -X DELETE \
  -H "X-API-Key: your_key" \
  http://localhost:8000/cache/user@example.com
```

Response:
```json
{
  "email": "user@example.com",
  "deleted_keys": 4,
  "message": "Cache invalidated for user@example.com"
}
```

#### `DELETE /cache?confirm=true`
Flush all cache (requires API key and confirmation)

```bash
curl -X DELETE \
  -H "X-API-Key: your_key" \
  "http://localhost:8000/cache?confirm=true"
```

⚠️ **WARNING**: This deletes ALL cached data!

---

## 🐍 Python Client Examples

### Basic Usage

```python
import requests

# Enrich single email
response = requests.post(
    'http://localhost:8000/enrich',
    json={
        'email': 'user@example.com',
        'ip_address': '181.45.123.45'
    }
)

result = response.json()
print(f"Trust Score: {result['summary']['trust_score']}")
print(f"GitHub Repos: {result['features']['all_features']['github_repos']}")
```

### Batch Enrichment

```python
import requests

# Enrich multiple emails
response = requests.post(
    'http://localhost:8000/enrich/batch',
    json={
        'emails': [
            'user1@example.com',
            'user2@example.com',
            'user3@example.com'
        ],
        'skip_commercial': False
    }
)

batch_result = response.json()
print(f"Processed: {batch_result['total']}")
print(f"Success: {batch_result['success']}")

for result in batch_result['results']:
    if result['success']:
        print(f"{result['email']}: {result['summary']['trust_score']}")
```

### With API Key

```python
import requests

headers = {
    'X-API-Key': 'your_secret_key_here'
}

response = requests.post(
    'http://localhost:8000/enrich',
    headers=headers,
    json={'email': 'user@example.com'}
)

result = response.json()
```

---

## 🌐 JavaScript/TypeScript Examples

### Fetch API

```javascript
// Enrich email
const enrichEmail = async (email) => {
  const response = await fetch('http://localhost:8000/enrich', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your_key'  // If authentication enabled
    },
    body: JSON.stringify({
      email: email,
      skip_commercial: false
    })
  });

  const result = await response.json();
  return result;
};

// Usage
enrichEmail('user@example.com')
  .then(result => {
    console.log('Trust Score:', result.summary.trust_score);
    console.log('GitHub Repos:', result.features.all_features.github_repos);
  });
```

### Axios

```javascript
const axios = require('axios');

const enrichEmail = async (email) => {
  try {
    const response = await axios.post(
      'http://localhost:8000/enrich',
      {
        email: email,
        ip_address: '181.45.123.45'
      },
      {
        headers: {
          'X-API-Key': 'your_key'
        }
      }
    );

    return response.data;
  } catch (error) {
    console.error('Enrichment error:', error.response.data);
  }
};
```

---

## 📊 Performance

### Single Email
- **Cold (no cache)**: ~3-5 seconds
- **Warm (cached)**: ~50-100ms
- **Throughput**: 200-400 requests/second (cached)

### Batch Requests
- **100 emails (cold)**: ~10-15 seconds (parallel processing)
- **100 emails (cached)**: ~2-3 seconds

### Optimization Tips
1. **Enable Redis caching** for 10-50x speedup
2. **Use batch endpoint** for multiple emails
3. **Skip commercial APIs** if not needed (`skip_commercial=true`)
4. **Deploy multiple workers** for high traffic

---

## 🚀 Production Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and run:
```bash
docker build -t email-intelligence-api .
docker run -p 8000:8000 --env-file .env email-intelligence-api
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENABLE_CACHE=true
      - REDIS_HOST=redis
      - API_KEY=${API_KEY}
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

Run:
```bash
docker-compose up -d
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## ⚙️ Configuration

Environment variables (`.env`):

```bash
# API Configuration
API_KEY=your_secret_key_here     # Optional API key authentication

# Redis Cache
ENABLE_CACHE=true                 # Enable caching
REDIS_HOST=localhost              # Redis host
REDIS_PORT=6379                   # Redis port
REDIS_DB=0                        # Redis database
REDIS_PASSWORD=                   # Redis password (optional)

# Data Sources (same as full_enrichment.py)
HUNTER_API_KEY=your_key           # Hunter.io
IPQS_API_KEY=your_key             # IPQualityScore
# ... other API keys
```

---

## 🔒 Security Best Practices

1. **Enable API Key Authentication**
   ```bash
   API_KEY=strong_random_key_here
   ```

2. **Use HTTPS in Production**
   - Deploy behind Nginx with SSL/TLS
   - Use Let's Encrypt for free certificates

3. **Rate Limiting**
   - Consider adding rate limiting middleware
   - Use services like Cloudflare or AWS API Gateway

4. **Input Validation**
   - Already implemented via Pydantic models
   - Validates email format, limits batch size, etc.

5. **CORS Configuration**
   - Update `allow_origins` in production to specific domains

---

## 📈 Monitoring

### Health Checks

```bash
# Simple health check
curl http://localhost:8000/health

# Automated monitoring
watch -n 30 'curl -s http://localhost:8000/health | jq .status'
```

### Logging

API logs include:
- Request timestamps
- Email being processed
- Cache hits/misses
- Errors and exceptions

View logs:
```bash
# Docker
docker logs -f email-intelligence-api

# Systemd
journalctl -u email-api -f
```

---

## 🐛 Troubleshooting

### API won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install fastapi uvicorn pydantic
```

### Redis connection error

**Error:** `Redis connection failed`

**Solution:**
```bash
# Start Redis
brew services start redis  # macOS
sudo systemctl start redis # Linux

# Or disable cache
ENABLE_CACHE=false
```

### Slow responses

**Solutions:**
1. Enable Redis caching: `ENABLE_CACHE=true`
2. Skip commercial APIs: `skip_commercial=true`
3. Increase workers: `--workers 4`
4. Use batch endpoint for multiple emails

---

## 📝 Changelog

**v3.5.0** (2026-03-16)
- Initial REST API release
- Async/await support
- Batch enrichment endpoint
- Redis caching integration
- API key authentication
- Auto-generated documentation

---

## 🤝 Contributing

API improvements welcome:
- Additional endpoints
- Performance optimizations
- Better error handling
- Rate limiting implementation
- WebSocket support

---

**Version:** 3.5.0
**License:** MIT
**Documentation:** http://localhost:8000/docs
