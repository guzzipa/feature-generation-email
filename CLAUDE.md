# Email Intelligence & Feature Extraction

## Project Description

Email intelligence system that extracts 291+ structured features from email addresses. Combines public data (OSINT), commercial APIs, and behavioral analysis to generate comprehensive user profiles for ML applications, user research, identity verification, and data enrichment.

## Project Structure

```
feature-generation-email/
├── full_enrichment.py              # Main enrichment pipeline (v3.4)
├── osint_email_enrichment.py       # OSINT data collection (GitHub, Gravatar, HIBP)
├── commercial_apis.py              # Commercial API integration (Hunter, EmailRep, Clearbit)
├── additional_sources.py           # Extra sources (WHOIS, IPQS, Twitter, etc)
├── free_sources.py                 # 100% free sources (IP intel, patterns, username search)
├── platform_behavioral.py          # Platform behavioral data extraction
├── enhanced_feature_engineering.py # Feature engineering (291 features)
├── cache_manager.py                # Redis caching layer
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not committed)
└── examples/                       # Usage examples
```

## Fuentes de Datos

### Datos Públicos (OSINT) - Implementados
1. **Validación de Email** - Formato, tipo de proveedor, dominio
2. **Gravatar** - Avatar y perfil público
3. **GitHub** - Perfil, repos, actividad
4. **Have I Been Pwned** - Brechas de seguridad
5. **Domain Analysis** - Tipo de dominio, disposable detection

### APIs Comerciales - v3.0
1. **Hunter.io** - Verificación deliverability, riesgo, datos corporativos
2. **EmailRep.io** - Reputación, flags maliciosos, credential leaks
3. **Clearbit** - Enriquecimiento empresa (funding, size, tech stack) y persona (role, seniority)

### Por Implementar (futuro)
- FullContact - Perfil social agregado
- Lookup de redes sociales (LinkedIn, Twitter vía scraping)
- Domain WHOIS age analysis

## Features Generated

The system generates 291 features across multiple categories:

- **Identity & Validation** (45): Email format, provider, domain analysis, name extraction, professional patterns
- **Social & Professional** (60): GitHub activity, social presence, bio/location/company, reputation signals
- **Security & Quality** (35): Data breaches, disposable detection, spam flags, IP reputation
- **Behavioral Patterns** (40): Session patterns, engagement metrics, device fingerprinting, temporal activity
- **Technical & Geo** (30): IP geolocation, browser/OS/device, domain WHOIS, connection type
- **Derived Scores** (25): Trust score, identity strength, security risk, engagement, data quality
- **Commercial APIs** (56): Hunter verification, EmailRep reputation, Clearbit enrichment (optional)

## Consideraciones de Producción

### Rate Limits
- GitHub API: 60 req/hora (sin auth), 5000/hora (con token)
- HIBP: Requiere API key para producción
- Gravatar: Sin límites conocidos

### Caching
- TTL recomendado: 30-90 días para datos estáticos (Gravatar, GitHub profile)
- TTL recomendado: 7 días para breach checks

### Privacidad y Compliance
- Solo usar datos públicamente disponibles
- Respetar GDPR/CCPA - informar a usuarios sobre enriquecimiento
- No almacenar datos sensibles
- Permitir opt-out

### Arquitectura para Escala
- Ejecutar en batch asíncrono (Celery, Airflow, etc)
- No ejecutar en tiempo real de registro
- Usar queue system para procesamiento
- Implementar retry logic con exponential backoff

## Instrucciones para Claude

### Estilo de Código
- Python 3.8+
- Type hints donde sea relevante
- Docstrings para funciones públicas
- Manejo de errores graceful (no fallar por una API caída)
- Logging estructurado

### Testing
- Crear unit tests para cada fuente de datos
- Mock APIs externas en tests
- Test cases para emails válidos/inválidos
- Test error handling

### Seguridad
- Nunca hardcodear API keys
- Usar .env para configuración sensible
- Rate limiting local para evitar bans
- Timeout en todas las requests HTTP

### Próximos Pasos Sugeridos
1. Agregar más fuentes de datos (Hunter.io, EmailRep)
2. Implementar sistema de caching (Redis)
3. Crear API REST para servir features
4. Integración con feature stores populares (Feast, Tecton)
5. Dashboard de métricas y coverage

## Variables de Entorno

```bash
# APIs Públicas (opcional - mejoran rate limits)
GITHUB_TOKEN=          # Token de GitHub para mayor rate limit
HIBP_API_KEY=          # API key de Have I Been Pwned

# APIs Comerciales (v3.0 - requeridas para features completos)
HUNTER_API_KEY=        # API key de Hunter.io
EMAILREP_API_KEY=      # API key de EmailRep.io
CLEARBIT_API_KEY=      # API key de Clearbit

# Configuración
CACHE_TTL_DAYS=30      # TTL para cache de resultados
MAX_RETRIES=3          # Reintentos en caso de fallo
REQUEST_TIMEOUT=10     # Timeout de requests en segundos
```

## Usage

```bash
# Single email enrichment
python full_enrichment.py user@example.com

# With IP geolocation
python full_enrichment.py user@example.com --ip 181.45.123.45

# Skip commercial APIs (100% free)
python full_enrichment.py user@example.com --skip-commercial

# Force refresh (bypass cache)
python full_enrichment.py user@example.com --force-refresh
```

## Production Recommendations

- **Enable Redis caching** for performance (2-10x speedup)
- **Use batch processing** for multiple emails
- **Monitor API rate limits** (especially free tiers)
- **Implement retry logic** with exponential backoff
- **Consider costs** before scaling commercial APIs
- **Respect privacy** and comply with GDPR/CCPA
