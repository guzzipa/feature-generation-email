# 🔍 OSINT Feature Engineering for Credit Scoring

Sistema completo de enriquecimiento OSINT y feature engineering para scoring crediticio usando emails como punto de partida.

## 🎯 Objetivo

Generar features estructurados de ML para scoring crediticio basados en información pública (OSINT) obtenida a partir del email del usuario. Útil para:

- **Scoring crediticio automatizado**
- **Evaluación de riesgo**
- **Detección de fraude**
- **Verificación de identidad**
- **Modelos de ML para aprobación de créditos**

## 🚀 Quick Start

### 1. Análisis Individual

```bash
# Paso 1: Enriquecimiento OSINT básico
python osint_email_enrichment.py usuario@ejemplo.com

# Paso 2: Generar features ML estructurados
python ml_feature_engineering.py osint_results_usuario_at_ejemplo.com.json

# Paso 3: Generar reporte de scoring crediticio
python example_ml_integration.py osint_results_usuario_at_ejemplo.com_ml_features.json
```

### 2. Procesamiento Batch

```bash
# Desde CSV
python batch_processing.py usuarios.csv --email-col email --id-col user_id

# Lista de emails
python batch_processing.py email1@test.com email2@test.com email3@test.com
```

## 📂 Estructura del Proyecto

```
features-osint/
├── osint_email_enrichment.py       # Recolección OSINT de datos públicos
├── ml_feature_engineering.py       # Feature engineering para ML
├── example_ml_integration.py       # Integración ML y scoring crediticio
├── batch_processing.py             # Procesamiento batch de múltiples usuarios
├── requirements.txt                # Dependencias Python
├── .env.example                    # Template variables de entorno
├── CLAUDE.md                       # Contexto del proyecto
└── examples/
    ├── sample_users.csv           # CSV de ejemplo
    └── example_output.json        # Output de ejemplo
```

## 📊 Features ML Generados (30+ features)

### 🔵 Identity Features
- `account_age_days` / `account_age_years` - Antigüedad de cuenta digital
- `has_github` / `has_gravatar` - Presencia en plataformas
- `digital_footprint_count` - Cantidad de plataformas
- `identity_strength_score` - Score compuesto de identidad (0-1)

### 🟢 Activity Features
- `github_repos` / `github_followers` - Actividad en GitHub
- `github_activity_ratio` - Repos por año (proxy de actividad sostenida)
- `has_professional_bio` / `has_location` / `has_company` - Completitud de perfil
- `activity_engagement_score` - Score de engagement (0-1)

### 🟡 Email Features
- `email_valid` / `is_free_email` / `is_corporate_email` - Tipo de email
- `is_disposable_email` - Detector de emails temporales
- `email_provider_risk` - Score de riesgo del proveedor (0-1)
- `email_provider_type` - Categoría del proveedor

### 🔴 Security Features
- `has_known_breaches` / `breach_count` - Brechas de datos conocidas
- `breach_severity_score` - Severidad de brechas (0-1)
- `security_risk_score` - Score compuesto de riesgo (0-1)

### ⭐ Derived Scores
- `overall_trust_score` - Score principal de confianza (0-1)
- `profile_completeness` - Categoría: full/partial/minimal/none
- `location_country` - País extraído (códigos ISO)

## 📈 Output del Sistema

### Formato ML-Ready

```json
{
  "numerical_features": {
    "account_age_years": 11.76,
    "overall_trust_score": 0.812,
    "identity_strength_score": 0.90,
    "security_risk_score": 0.04,
    "github_repos": 16,
    "breach_count": 0,
    ...
  },
  "categorical_features": {
    "email_provider_type": "gmail",
    "location_country": "AR",
    "profile_completeness": "full"
  }
}
```

### Reporte Crediticio

```json
{
  "risk_assessment": {
    "risk_category": "BAJO RIESGO",
    "recommendation": "APROBACIÓN RECOMENDADA",
    "interest_tier": "Tier 1 (tasa preferencial)",
    "trust_score": 0.812
  },
  "suggested_credit_limit_usd": 39884,
  "key_scores": {
    "overall_trust": 0.812,
    "identity_strength": 0.900,
    "security_risk": 0.040
  }
}
```

## 🎓 Integración con Modelos ML

### Scikit-learn

```python
from ml_feature_engineering import CreditScoringFeatureEngineer
from sklearn.ensemble import RandomForestClassifier

# Cargar datos OSINT
engineer = CreditScoringFeatureEngineer(osint_data)
ml_ready = engineer.to_ml_ready()

# Features listos para entrenar
X = ml_ready['numerical_features']  # 23 features numéricos
y = labels  # [1, 0, 1, ...]  # 1=buen pagador, 0=mal pagador

# Entrenar modelo
model = RandomForestClassifier()
model.fit(X_scaled, y)
```

### Importancia de Features

**CRÍTICO** (alta importancia para scoring):
- `account_age_years`
- `overall_trust_score`
- `is_disposable_email`
- `identity_strength_score`

**IMPORTANTE** (media importancia):
- `is_corporate_email`
- `security_risk_score`
- `activity_engagement_score`

**CONTEXTUAL** (útil para enriquecer):
- `github_repos`, `location_country`, etc.

## 📊 Ejemplo Real

```bash
$ python osint_email_enrichment.py guzzipa@gmail.com
# → Genera: osint_results_guzzipa_at_gmail.com.json

$ python ml_feature_engineering.py osint_results_guzzipa_at_gmail.com.json
# → Genera: osint_results_guzzipa_at_gmail.com_ml_features.json

$ python example_ml_integration.py osint_results_guzzipa_at_gmail.com_ml_features.json

# OUTPUT:
# 🎯 EVALUACIÓN: BAJO RIESGO
# 💰 LÍMITE SUGERIDO: $39,884 USD
# ⭐ TRUST SCORE: 0.812
# ✅ Antigüedad digital: 11.8 años
# ✅ Perfil completo
# ⚠️  Email gratuito (no corporativo)
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# APIs opcionales (mejoran rate limits)
GITHUB_TOKEN=ghp_your_token_here        # 60 → 5000 req/hora
HIBP_API_KEY=your_hibp_key_here         # Requerido para producción

# Configuración
CACHE_TTL_DAYS=30
MAX_RETRIES=3
REQUEST_TIMEOUT=10
```

## 🚀 Procesamiento Batch

### Desde CSV

```bash
python batch_processing.py users.csv --email-col email --id-col user_id
```

**Output generado:**
- `batch_results_YYYYMMDD_HHMMSS.json` - Resultados completos
- `batch_summary_YYYYMMDD_HHMMSS.csv` - Resumen para análisis
- `batch_errors_YYYYMMDD_HHMMSS.csv` - Errores (si los hay)

### Estadísticas Automáticas

```json
{
  "total_processed": 100,
  "successful": 98,
  "errors": 2,
  "trust_score": {
    "mean": 0.67,
    "min": 0.12,
    "max": 0.95
  },
  "risk_distribution": {
    "BAJO RIESGO": 45,
    "RIESGO MEDIO": 35,
    "ALTO RIESGO": 18
  }
}
```

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

## 🔐 Seguridad

- Email temporales/desechables → **Rechazo automático**
- Múltiples brechas (>3) → **Verificación adicional requerida**
- Sin identidad digital → **Revisión manual**

## 📚 Documentación Adicional

- [CLAUDE.md](CLAUDE.md) - Contexto completo del proyecto
- [examples/](examples/) - Ejemplos de uso y outputs

## 🛠️ Próximos Pasos

1. ✅ Sistema base de enriquecimiento OSINT
2. ✅ Feature engineering para ML
3. ✅ Integración con scoring crediticio
4. ✅ Procesamiento batch
5. 🔲 Agregar más fuentes: Hunter.io, Clearbit, EmailRep
6. 🔲 Implementar caching con Redis
7. 🔲 API REST para servir features
8. 🔲 Integración con feature stores (Feast, Tecton)
9. 🔲 Dashboard de métricas

## 📄 Licencia

Proyecto de evaluación/POC para scoring crediticio basado en OSINT.
