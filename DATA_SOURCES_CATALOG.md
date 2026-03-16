# Email Intelligence Data Sources - Complete Catalog

Catálogo exhaustivo de TODAS las fuentes de datos disponibles para enriquecimiento de emails, organizadas por categoría.

## 📊 Categorías de Fuentes

### 1. Identity Verification & KYC
**Objetivo**: Verificar identidad real, prevenir fraude

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Onfido** | Face verification, document check, liveness | $2-5/check | Global | 🔲 |
| **Jumio** | ID verification, biometrics, AML | $1-3/check | Global | 🔲 |
| **Trulioo** | Global ID verification, 5B+ records | $0.50-2/check | 195 countries | 🔲 |
| **Persona** | Identity verification, KYC/AML | $1-4/check | Global | 🔲 |
| **Vouched** | ID + selfie verification | $1.50/check | US/Canada | 🔲 |
| **Veriff** | Document + biometric verification | $2-4/check | Global | 🔲 |

**Features potenciales**: ~20 (ID verified, face match score, document type, liveness check, AML risk, PEP screening)

---

### 2. Phone Number Intelligence
**Objetivo**: Vincular email con teléfono, validar contacto

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Twilio Lookup** | Carrier, caller name, SMS capable | $0.005-0.01/lookup | Global | 🔲 |
| **Numverify** | Type, carrier, location, validity | Free-$50/month | Global | 🔲 |
| **Telesign** | Phone verification, risk score | $0.02-0.05/check | Global | 🔲 |
| **Vonage Verify** | 2FA, phone validation | $0.06-0.15/verify | Global | 🔲 |
| **Phone Validator** | Line type, carrier, location | $0.01-0.03/lookup | US/Canada | 🔲 |

**Features potenciales**: ~15 (phone_linked, phone_type, carrier_name, phone_country, sms_capable, phone_risk_score)

---

### 3. Address & Geolocation Data
**Objetivo**: Datos de dirección física, verificación postal

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **SmartyStreets** | Address validation, geocoding | $0.35-1.10/1000 | US/International | 🔲 |
| **Melissa Data** | Address verify, phone append | $25-100/month | Global | 🔲 |
| **Loqate** | Address autocomplete, verification | Custom | Global | 🔲 |
| **Google Maps Geocoding** | Lat/long, address components | $5/1000 | Global | 🔲 |
| **HERE Geocoding** | Location data, routing | Free tier | Global | 🔲 |

**Features potenciales**: ~12 (address_verified, lat, lng, address_type, postal_code, address_complete)

---

### 4. Financial & Credit Data
**Objetivo**: Creditworthiness, financial profile

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Experian** | Credit score, history, tradelines | Enterprise | US/UK | 🔲 |
| **Equifax** | Credit report, risk models | Enterprise | US/UK/Canada | 🔲 |
| **TransUnion** | Credit score, fraud detection | Enterprise | US | 🔲 |
| **Plaid** | Bank account, transactions, balance | $0.20-0.60/user | US/Canada/UK | 🔲 |
| **Yodlee** | Financial aggregation, transactions | Enterprise | US | 🔲 |
| **Stripe Identity** | Payment history, chargeback risk | Included | Global | 🔲 |

**Features potenciales**: ~25 (credit_score, credit_tier, bank_linked, account_balance_range, payment_history)

---

### 5. Employment & Income Verification
**Objetivo**: Verificar empleo, ingresos, estabilidad laboral

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Argyle** | Employment, income verification | $3-10/verification | US/Canada | 🔲 |
| **Truework** | VOE, VOI, instant verification | $25-40/verification | US | 🔲 |
| **Equifax TWN** | The Work Number, employment data | Enterprise | US | 🔲 |
| **Pinwheel** | Payroll connectivity, income | $2-5/user | US | 🔲 |
| **Atomic** | Payroll data, income streams | $3-8/user | US | 🔲 |

**Features potenciales**: ~18 (employer_name, job_title, employment_status, income_range, tenure_months)

---

### 6. Education & Academic Verification
**Objetivo**: Verificar educación, instituciones, grados

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **National Student Clearinghouse** | Degree verification, enrollment | $3-5/verification | US | 🔲 |
| **Credentials Inc** | Degree verification, transcripts | $15-30/verification | US | 🔲 |
| **HireRight** | Education background check | $10-25/check | US/International | 🔲 |
| **Verifile** | Academic verification | £10-20/check | UK | 🔲 |

**Features potenciales**: ~10 (education_verified, degree_type, institution, graduation_year, major)

---

### 7. Device Intelligence & Fingerprinting
**Objetivo**: Device data, behavior patterns, bot detection

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Fingerprint.js** | Device fingerprinting, visitor ID | $0-200/month | Global | 🔲 |
| **DeviceAtlas** | Device detection, properties | $99-499/month | Global | 🔲 |
| **51Degrees** | Device detection | Free-Enterprise | Global | 🔲 |
| **Seon** | Digital footprint, device fingerprinting | $299+/month | Global | 🔲 |
| **Iovation** | Device intelligence, fraud prevention | Enterprise | Global | 🔲 |

**Features potenciales**: ~20 (device_id, device_trust_score, bot_probability, emulator_detected, vpn_usage)

---

### 8. Behavioral Analytics & CDP
**Objetivo**: User behavior, engagement, journey data

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Segment** | Customer data platform, events | $120+/month | Global | 🔲 |
| **Mixpanel** | Product analytics, user behavior | Free-Enterprise | Global | 🔲 |
| **Amplitude** | Product analytics, cohorts | Free-Enterprise | Global | 🔲 |
| **Heap** | Auto-capture events, user journeys | $0-Enterprise | Global | 🔲 |
| **FullStory** | Session replay, user behavior | $199+/month | Global | 🔲 |

**Features potenciales**: ~30 (session_count, events_triggered, feature_usage, user_journey_stage, engagement_score)

---

### 9. CRM & Marketing Automation Data
**Objetivo**: Marketing data, lead scoring, campaign engagement

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **HubSpot** | Contacts, deals, email engagement | Free-Enterprise | Global | 🔲 |
| **Salesforce** | CRM data, opportunity pipeline | $25-300/user/month | Global | 🔲 |
| **Marketo** | Marketing automation, lead scoring | Enterprise | Global | 🔲 |
| **Mailchimp** | Email engagement, campaign data | Free-$350/month | Global | 🔲 |
| **Intercom** | Customer messaging, conversations | $74+/month | Global | 🔲 |

**Features potenciales**: ~25 (crm_lead_score, email_open_rate, deals_in_pipeline, last_interaction_days)

---

### 10. Alternative Data & Consumer Behavior
**Objetivo**: Purchase patterns, interests, lifestyle data

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Factual** | Location data, consumer visits | Enterprise | US | 🔲 |
| **Placed** | Location insights, foot traffic | Enterprise | US | 🔲 |
| **Foursquare** | Location intelligence, visits | Custom | Global | 🔲 |
| **LiveRamp** | Identity resolution, segments | Enterprise | US | 🔲 |
| **Acxiom** | Consumer data, demographics | Enterprise | US | 🔲 |
| **Experian Marketing** | Consumer segments, propensity | Enterprise | US/UK | 🔲 |

**Features potenciales**: ~30 (purchase_frequency, favorite_brands, spending_tier, lifestyle_segment)

---

### 11. Telecommunications Data
**Objetivo**: Carrier info, mobile behavior, telco intelligence

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **GSMA Mobile Connect** | Mobile identity, authentication | Enterprise | Global | 🔲 |
| **Mobilewalla** | Mobile app usage, device data | Enterprise | Global | 🔲 |
| **OpenSignal** | Network performance, coverage | API access | Global | 🔲 |

**Features potenciales**: ~12 (mobile_carrier, data_plan_type, roaming_patterns, app_usage_categories)

---

### 12. Identity Graphs & Cross-Device Tracking
**Objetivo**: Unificar identidades across devices/channels

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **LiveRamp IdentityLink** | Cross-device identity graph | Enterprise | US | 🔲 |
| **Tapad** | Cross-device graph, household data | Enterprise | Global | 🔲 |
| **Drawbridge** | Cross-device matching | Enterprise | Global | 🔲 |
| **Neustar** | Identity resolution, OneID | Enterprise | US | 🔲 |

**Features potenciales**: ~15 (devices_linked, household_id, cross_device_score, household_size)

---

### 13. Fraud Prevention & Risk Scoring
**Objetivo**: Fraud detection, risk assessment, AML

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Sift** | Fraud detection, chargeback prevention | $500+/month | Global | 🔲 |
| **Kount** | Fraud prevention, risk scoring | Enterprise | Global | 🔲 |
| **Forter** | E-commerce fraud prevention | Enterprise | Global | 🔲 |
| **Riskified** | Chargeback guarantee, fraud detection | Enterprise | Global | 🔲 |
| **Signifyd** | Commerce protection, fraud prevention | Enterprise | Global | 🔲 |
| **ComplyAdvantage** | AML, sanctions screening | $1,000+/month | Global | 🔲 |

**Features potenciales**: ~20 (fraud_score, chargeback_risk, aml_risk, sanctions_match, pep_match)

---

### 14. Payment & Transaction Data
**Objetivo**: Payment methods, transaction history, wallet data

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Stripe** | Payment history, customer LTV | % of transactions | Global | 🔲 |
| **PayPal** | Transaction data, buyer reputation | % of transactions | Global | 🔲 |
| **Adyen** | Payment data, risk signals | % of transactions | Global | 🔲 |
| **Venmo** | P2P transactions, social graph | N/A (closed) | US | ❌ |

**Features potenciales**: ~18 (payment_methods_count, avg_transaction_value, payment_success_rate, ltv)

---

### 15. Social Login & OAuth Data
**Objetivo**: Data from social auth providers

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Google Sign-In** | Profile, email verified, photo | Free | Global | 🔲 |
| **Facebook Login** | Profile, friends count, interests | Free | Global | 🔲 |
| **Apple Sign In** | Email (private relay), verified | Free | Global | 🔲 |
| **LinkedIn OAuth** | Profile, connections, experience | Free | Global | 🔲 |
| **GitHub OAuth** | Profile, repos, contributions | Free | Global | ✅ |

**Features potenciales**: ~12 (oauth_provider, profile_verified, oauth_email_match, friends_count)

---

### 16. Public Records & Government Data
**Objetivo**: Legal records, property, business registrations

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **LexisNexis** | Public records, background checks | Enterprise | US | 🔲 |
| **Thomson Reuters CLEAR** | Identity, assets, associates | Enterprise | US | 🔲 |
| **BeenVerified** | Background check, public records | $26/month | US | 🔲 |
| **Intelius** | Background check, reverse lookup | $20/month | US | 🔲 |
| **SEC EDGAR** | Company filings, insider trading | Free | US companies | 🔲 |

**Features potenciales**: ~15 (property_owner, business_owner, court_records, registered_voter)

---

### 17. App Usage & Mobile Intelligence
**Objetivo**: App install data, mobile behavior

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Adjust** | App attribution, user behavior | Free-Enterprise | Global | 🔲 |
| **AppsFlyer** | Mobile attribution, user value | Free-Enterprise | Global | 🔲 |
| **Branch** | Deep linking, attribution | Free-Enterprise | Global | 🔲 |
| **App Annie** | App market data, competitor intel | $850+/month | Global | 🔲 |

**Features potenciales**: ~12 (apps_installed, app_categories, last_app_launch, mobile_engagement)

---

### 18. Web3 & Blockchain Data
**Objetivo**: Crypto wallets, NFTs, DeFi activity

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Etherscan** | Ethereum transactions, balance | Free API | Ethereum | 🔲 |
| **Alchemy** | Blockchain data, NFT API | Free-$299/month | Multi-chain | 🔲 |
| **Moralis** | Web3 data, wallet tracking | Free-$249/month | Multi-chain | 🔲 |
| **Covalent** | Blockchain analytics | Free-$999/month | 100+ chains | 🔲 |
| **Dune Analytics** | On-chain data queries | Free-$390/month | Multi-chain | 🔲 |

**Features potenciales**: ~20 (crypto_wallet_linked, nft_count, defi_user, eth_balance, transaction_count)

---

### 19. Professional Networks & Recruitment
**Objetivo**: Professional profile, skills, job search

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **LinkedIn API** | Profile, connections, experience | Restricted | Global | ⚠️ |
| **AngelList** | Startup profiles, investments | Limited API | Global | 🔲 |
| **Crunchbase** | Company data, funding rounds | $29-999/month | Global | 🔲 |
| **PitchBook** | Private market data, valuations | Enterprise | Global | 🔲 |

**Features potenciales**: ~18 (job_titles, companies_worked, skills_endorsed, job_seeking)

---

### 20. E-commerce & Marketplace Data
**Objetivo**: Purchase behavior, product reviews

| Fuente | Features | Costo | Cobertura | Status |
|--------|----------|-------|-----------|--------|
| **Amazon** | Purchase history (user consent) | N/A | Global | 🔲 |
| **eBay** | Seller ratings, purchase history | Limited API | Global | 🔲 |
| **Etsy** | Shop owner, product reviews | Public API | Global | 🔲 |
| **Shopify** | Customer data (merchant) | Included | Global | 🔲 |

**Features potenciales**: ~15 (ecommerce_purchases, seller_rating, product_categories, purchase_frequency)

---

## 📊 Resumen por Valor/Costo

### Alto Valor, Bajo Costo (Quick Wins)
- ✅ Social OAuth data (Free)
- ✅ Dev.to API (Free)
- ✅ HackerNews API (Free)
- ⭐ Numverify phone validation (Free tier)
- ⭐ Twilio Lookup ($0.005/lookup)
- ⭐ Google Geocoding ($5/1000)

### Alto Valor, Costo Medio (Worth It)
- ⭐⭐ Plaid financial data ($0.20-0.60/user)
- ⭐⭐ Fingerprint.js ($0-200/month)
- ⭐⭐ Trulioo ID verification ($0.50-2/check)
- ⭐⭐ Argyle employment ($3-10/verification)

### Alto Valor, Alto Costo (Enterprise)
- 💎 Credit bureaus (Experian, Equifax, TransUnion)
- 💎 LiveRamp identity graph
- 💎 Sift fraud prevention
- 💎 LexisNexis public records

### Features Potenciales Totales
- **OSINT actual**: 291 features
- **Phone intelligence**: +15 features
- **Financial data**: +25 features
- **Employment data**: +18 features
- **Device intelligence**: +20 features
- **Behavioral analytics**: +30 features
- **Web3/Crypto**: +20 features
- **Fraud/Risk scoring**: +20 features

**TOTAL POTENCIAL: ~450-500 features**

---

## 🎯 Recomendaciones de Implementación

### Fase 1: Quick Wins (Gratis o < $50/month)
1. ✅ Twilio Lookup - Phone validation ($0.005/lookup)
2. ✅ Google Sign-In OAuth - Profile data (Free)
3. ✅ HackerNews API - Developer profile (Free)
4. ✅ Numverify - Phone intelligence (Free tier)
5. ✅ HERE Geocoding - Location (Free tier)

**Costo mensual**: $0-50
**Features agregados**: ~30
**Tiempo implementación**: 1-2 semanas

### Fase 2: Moderate Investment ($50-500/month)
1. ⭐ Plaid - Financial connectivity ($0.20-0.60/user)
2. ⭐ Fingerprint.js - Device intelligence ($100-200/month)
3. ⭐ SmartyStreets - Address validation ($0.35/1000)
4. ⭐ Segment - Behavioral data ($120/month)
5. ⭐ Alchemy - Web3 data ($0-299/month)

**Costo mensual**: $200-500
**Features agregados**: ~60
**Tiempo implementación**: 1 mes

### Fase 3: Enterprise Value (Custom pricing)
1. 💎 Trulioo - ID verification (Enterprise)
2. 💎 Argyle - Employment verification (Enterprise)
3. 💎 Credit bureaus (Experian/Equifax)
4. 💎 Sift - Fraud prevention (Enterprise)
5. 💎 LiveRamp - Identity resolution (Enterprise)

**Costo mensual**: $2,000-10,000+
**Features agregados**: ~100
**ROI**: Alto para use cases específicos

---

## 💡 Próximos Pasos

1. **Priorizar por use case**:
   - Fraud detection → Sift, Fingerprint.js, Seon
   - Lead scoring → Clearbit, Plaid, Argyle
   - Identity verification → Trulioo, Onfido, Jumio
   - Developer profiling → GitHub (✅), HackerNews (✅), StackOverflow

2. **Evaluar ROI**:
   - Calcular valor por feature
   - Estimar cobertura (% de emails con data)
   - Medir impacto en modelo ML

3. **Implementación incremental**:
   - Empezar con APIs gratis/baratas
   - Medir performance
   - Escalar a enterprise si vale la pena

4. **Compliance check**:
   - GDPR compliance
   - Consent requirements
   - Data retention policies
   - Privacy regulations por país

---

¿Cuál de estas categorías te interesa más explorar?
