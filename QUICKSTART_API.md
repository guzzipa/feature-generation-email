# 🚀 REST API Quick Start Guide

Get the API running in 2 minutes!

---

## 1️⃣ Install Dependencies

```bash
# Install FastAPI and Uvicorn
pip install fastapi uvicorn pydantic python-multipart

# Or install all requirements
pip install -r requirements.txt
```

---

## 2️⃣ Start the API Server

```bash
# Development mode (with auto-reload)
uvicorn api:app --reload --port 8000

# Server will start at http://localhost:8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     🚀 Starting Email Intelligence API v3.5
INFO:     ✅ Pipeline initialized (cache: True)
```

---

## 3️⃣ View Interactive Documentation

Open your browser:

**Swagger UI**: http://localhost:8000/docs

**ReDoc**: http://localhost:8000/redoc

Try the interactive examples right in your browser!

---

## 4️⃣ Test with cURL

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "3.5.0",
  "cache_enabled": true,
  "cache_connected": true,
  "features_available": 291
}
```

### Enrich Single Email
```bash
curl -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Enrich with IP
```bash
curl -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "ip_address": "181.45.123.45"
  }'
```

### Batch Enrichment
```bash
curl -X POST http://localhost:8000/enrich/batch \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      "user1@example.com",
      "user2@example.com",
      "user3@example.com"
    ]
  }'
```

---

## 5️⃣ Test with Python

```python
import requests

# Enrich email
response = requests.post(
    'http://localhost:8000/enrich',
    json={'email': 'user@example.com'}
)

result = response.json()

# Print summary
print(f"Email: {result['email']}")
print(f"Trust Score: {result['summary']['trust_score']}")
print(f"Features: {result['features']['feature_count']}")
```

---

## 6️⃣ Test with JavaScript

```javascript
// Fetch API
fetch('http://localhost:8000/enrich', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com'
  })
})
.then(response => response.json())
.then(result => {
  console.log('Trust Score:', result.summary.trust_score);
  console.log('Features:', result.features.feature_count);
});
```

---

## 7️⃣ Run Example Client

```bash
# Run the example client
python examples/api_client_example.py
```

This will:
1. Check API health
2. Enrich a test email
3. Show extracted features
4. Demonstrate batch processing

---

## 🎯 Next Steps

### Production Deployment

```bash
# Multiple workers for production
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Enable API Key Authentication

1. Add to `.env`:
   ```bash
   API_KEY=your_secret_key_here
   ```

2. Restart server

3. Include key in requests:
   ```bash
   curl -H "X-API-Key: your_secret_key_here" \
     http://localhost:8000/enrich/user@example.com
   ```

### Enable Redis Caching

1. Install and start Redis:
   ```bash
   brew install redis          # macOS
   brew services start redis
   ```

2. Caching is auto-enabled (configured in `.env`)

3. Verify:
   ```bash
   curl http://localhost:8000/health | jq .cache_connected
   # true
   ```

### Docker Deployment

```bash
# Build
docker build -t email-intelligence-api .

# Run
docker run -p 8000:8000 --env-file .env email-intelligence-api
```

---

## 📚 Full Documentation

- **API Reference**: [API.md](API.md)
- **Streaming Guide**: [STREAMING.md](STREAMING.md) - Real-time streaming enrichment (v4.0)
- **Use Cases**: [USE_CASES.md](USE_CASES.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **Caching Guide**: [REDIS_CACHE.md](REDIS_CACHE.md)

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"

```bash
pip install fastapi uvicorn pydantic
```

### "Address already in use"

```bash
# Use different port
uvicorn api:app --reload --port 8001

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### "Redis connection failed"

```bash
# Start Redis
brew services start redis  # macOS
sudo systemctl start redis # Linux

# Or disable cache
ENABLE_CACHE=false uvicorn api:app --reload
```

### API returns 401 Unauthorized

API key authentication is enabled. Either:
1. Disable it by removing `API_KEY` from `.env`
2. Include key in requests: `-H "X-API-Key: your_key"`

---

## ⚡ Performance Tips

1. **Enable Redis caching** - 10-50x speedup
2. **Use batch endpoint** for multiple emails
3. **Skip commercial APIs** if not needed
4. **Run multiple workers** in production
5. **Deploy behind Nginx** for load balancing

---

**You're now running Email Intelligence API v3.5!** 🎉

Visit http://localhost:8000/docs to explore all endpoints.
