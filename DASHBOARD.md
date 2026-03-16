# Email Intelligence Dashboard

Interactive Streamlit web dashboard for email enrichment visualization and exploration.

## 🚀 Quick Start

```bash
# Install dependencies
pip install streamlit plotly pandas

# Run dashboard
streamlit run streamlit_app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## 📱 Features

### 1. Single Email Analysis

Comprehensive analysis of individual emails with interactive visualizations:

- **Summary Scores**: Trust, Identity Strength, Security Risk, Engagement
- **Radar Charts**: Visual representation of key metrics
- **Feature Breakdown**: All 291 features organized by category
- **GitHub Integration**: Full GitHub profile statistics and activity
- **Security Analysis**: Breach detection, disposable email checks, IP analysis
- **Raw Data Export**: Download complete enrichment results as JSON

### 2. Email Comparison

Side-by-side comparison of two email addresses:

- Compare trust scores and key metrics
- Identify differences in security profiles
- Evaluate relative lead quality
- Useful for A/B testing and validation

### 3. System Monitor

Real-time monitoring of system health and performance:

- **Redis Cache Stats**: Hit rate, memory usage, connected clients
- **Streaming Workers**: Job queue status, success rates, worker health
- **Cache Management**: View cached keys, clear cache, export metrics
- **System Information**: Pipeline version, feature count, connection status

### 4. Feature Explorer

Browse and understand all 291 available features:

- **7 Feature Categories**: Identity, Social, Security, Behavioral, Technical, Commercial, Derived
- **Search & Filter**: Find features by name or description
- **Type Distribution**: Breakdown of boolean, numeric, and string features
- **Use Case Templates**: Pre-defined feature sets for common scenarios
- **Export Feature List**: Download complete feature catalog as CSV

### 5. Enrichment History

Track and analyze enrichment history over time:

- Timeline of analyzed emails
- Trust score trends
- Historical data export
- Performance analytics

## 🎯 Use Cases

### Fraud Detection

```python
# Use the dashboard to:
1. Analyze suspicious email
2. Check trust_score, fraud_risk_score
3. Review security flags (breaches, disposable, proxy)
4. Make approval/rejection decision
```

### Lead Scoring

```python
# Evaluate lead quality:
1. Input lead email
2. Review lead_score, conversion_probability
3. Check professionalism_score, has_github
4. Prioritize high-quality leads
```

### User Research

```python
# Understand your users:
1. Batch analyze user base
2. View distribution of features
3. Identify patterns and segments
4. Export insights
```

## 📊 Dashboard Pages

### Main Page: Single Email Analysis

**Input:**
- Email address (required)
- IP address (optional)
- Skip commercial APIs checkbox

**Output Tabs:**
1. **Overview** - Summary metrics and radar chart
2. **Features** - Detailed feature breakdown by category
3. **GitHub** - GitHub profile and activity stats
4. **Security** - Security analysis and risk factors
5. **Raw Data** - Complete JSON export

### Page 1: System Monitor

Real-time monitoring dashboard:

**Cache Metrics:**
- Total keys cached
- Memory usage
- Hit/miss ratio
- Connected clients
- Cache efficiency chart

**Streaming Metrics:**
- Jobs submitted/completed/failed
- Queue status
- Success rate
- Worker health alerts

**Actions:**
- Clear cache
- Export metrics
- Manual refresh

### Page 2: Feature Explorer

Interactive feature catalog:

**Features:**
- Browse 291 features across 7 categories
- Search and filter
- View feature types and descriptions
- See TTL strategies
- Export feature list

**Statistics:**
- Feature type distribution
- Category breakdown
- Use case templates

## ⚙️ Configuration

### Sidebar Settings

- **Mode**: Single Email, Batch Analysis, Compare Emails, History
- **Skip Commercial APIs**: Use only free sources
- **Enable Cache**: Use Redis caching
- **Stats**: Emails analyzed count
- **Clear History**: Reset session

### Auto-Refresh (System Monitor)

Enable 5-second auto-refresh for real-time monitoring:

```python
auto_refresh = st.checkbox("Auto Refresh (5s)", value=False)
```

## 🎨 Customization

### Custom CSS

The dashboard uses custom CSS for styling:

```css
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
}
.score-high { color: #28a745; }
.score-medium { color: #ffc107; }
.score-low { color: #dc3545; }
```

### Color Coding

**Score Ranges:**
- **High** (0.7-1.0): Green ✅
- **Medium** (0.4-0.7): Yellow ⚠️
- **Low** (0.0-0.4): Red ❌

## 📈 Data Visualization

### Charts Available

1. **Radar Chart**: 6-dimensional score visualization
2. **Line Chart**: Trust score over time
3. **Bar Chart**: Cache hit/miss distribution
4. **Metrics Cards**: Key performance indicators

### Interactive Features

- Hover tooltips
- Zoom and pan
- Export as PNG
- Responsive layout

## 🔧 Advanced Usage

### Programmatic Access

Access enrichment pipeline directly:

```python
from full_enrichment import EmailEnrichmentPipeline

pipeline = EmailEnrichmentPipeline()
results = pipeline.enrich_email('user@example.com')
```

### Batch Processing

For batch analysis, use the streaming API:

```bash
# Start workers
python streaming.py worker --workers 4

# Submit batch
cat emails.txt | xargs -I {} python streaming.py submit {}
```

Then view results in the dashboard's History page.

### Export Results

Multiple export options:

1. **JSON**: Raw enrichment data
2. **CSV**: Feature list and values
3. **Metrics**: System performance data

## 🚀 Production Deployment

### Deploy with Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t email-intelligence-dashboard .
docker run -p 8501:8501 email-intelligence-dashboard
```

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from repository
4. Configure secrets for API keys

### Environment Variables

Set in Streamlit Cloud or `.streamlit/secrets.toml`:

```toml
[api_keys]
GITHUB_TOKEN = "ghp_your_token"
HIBP_API_KEY = "your_hibp_key"
HUNTER_API_KEY = "your_hunter_key"

[redis]
REDIS_HOST = "localhost"
REDIS_PORT = 6379
```

## 📱 Mobile Support

The dashboard is responsive and works on mobile devices:

- Adaptive layout
- Touch-friendly controls
- Optimized charts
- Mobile-first design

## 🔒 Security

### Best Practices

1. **Never commit API keys** - Use secrets management
2. **Rate limiting** - Implement on production
3. **Authentication** - Add user login for public deployments
4. **HTTPS** - Always use SSL in production

### Authentication (Optional)

Add basic auth:

```python
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Show dashboard
    main()
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

## 🐛 Troubleshooting

### Dashboard Won't Start

```bash
# Check Streamlit installation
pip install streamlit --upgrade

# Check for port conflicts
lsof -i :8501

# Run on different port
streamlit run streamlit_app.py --server.port=8502
```

### Redis Connection Error

```bash
# Ensure Redis is running
redis-cli ping
# Should return: PONG

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Missing Dependencies

```bash
# Install all dashboard dependencies
pip install streamlit plotly pandas

# Or full requirements
pip install -r requirements.txt
```

### Slow Performance

1. **Enable Redis caching** - 2-10x speedup
2. **Skip commercial APIs** - Faster enrichment
3. **Reduce auto-refresh frequency**
4. **Use streaming for batch processing**

## 📊 Performance

### Metrics

- **Cold start**: ~2-5 seconds (first enrichment)
- **Cached**: ~100-500ms (with Redis)
- **Dashboard load**: ~1-2 seconds
- **Concurrent users**: 10-50 (single instance)

### Optimization Tips

1. Enable Redis caching
2. Use CDN for static assets
3. Compress images
4. Lazy load charts
5. Implement pagination for large datasets

## 🎓 Examples

### Example 1: Fraud Detection Workflow

```python
1. Open dashboard
2. Input suspicious email
3. Review security tab:
   - Has breaches? ❌
   - Disposable email? ✅
   - Proxy/VPN? ✅
4. Check trust_score: 0.15 (LOW)
5. Decision: REJECT
```

### Example 2: Lead Qualification

```python
1. Input lead email
2. Check overview:
   - lead_score: 0.82 (HIGH)
   - has_github: ✅
   - is_corporate: ✅
3. Review GitHub tab:
   - 45 repos, 230 followers
   - Active contributor
4. Decision: PRIORITY LEAD
```

### Example 3: Monitoring Workers

```python
1. Go to System Monitor page
2. Check streaming stats:
   - 1,245 jobs submitted
   - 1,240 completed (99.6%)
   - 0 in DLQ
3. Cache performance:
   - Hit rate: 87%
   - Memory: 125MB
4. System: HEALTHY ✅
```

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Charts](https://plotly.com/python/)
- [Email Intelligence README](README.md)
- [Feature Catalog](pages/2_🔬_Feature_Explorer.py)

## 🤝 Contributing

Suggestions for dashboard improvements:

1. Add more chart types
2. Implement batch upload UI
3. Create custom widgets
4. Add export formats
5. Improve mobile UX

## 📄 License

MIT License - Same as parent project

---

**Version**: 4.2.0
**Last Updated**: 2026-03-16
**Requires**: Streamlit >= 1.28.0, Plotly >= 5.17.0
