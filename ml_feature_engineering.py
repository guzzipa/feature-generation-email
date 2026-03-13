#!/usr/bin/env python3
"""
ML Feature Engineering for Credit Scoring
Transforma datos OSINT en features estructurados para algoritmos de ML
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict


@dataclass
class MLFeatures:
    """Estructura de features para ML - todos tipados y documentados"""

    # === IDENTITY FEATURES (Identidad Digital) ===
    account_age_days: int                    # Antigüedad de cuenta más antigua en días
    account_age_years: float                 # Antigüedad en años (decimal)
    has_github: int                          # Binario: tiene perfil GitHub
    has_gravatar: int                        # Binario: tiene Gravatar
    digital_footprint_count: int             # Cantidad de plataformas con presencia

    # === ACTIVITY FEATURES (Actividad Online) ===
    github_repos: int                        # Cantidad de repositorios públicos
    github_followers: int                    # Cantidad de seguidores
    github_activity_ratio: float             # Repos por año de cuenta (proxy de actividad)
    has_professional_bio: int                # Binario: tiene bio profesional
    has_location: int                        # Binario: declaró ubicación
    has_company: int                         # Binario: declaró empresa

    # === EMAIL FEATURES (Tipo y Calidad de Email) ===
    email_valid: int                         # Binario: email válido
    is_free_email: int                       # Binario: proveedor gratuito (Gmail, Yahoo, etc)
    is_corporate_email: int                  # Binario: email corporativo
    is_disposable_email: int                 # Binario: email temporal/desechable
    email_provider_risk: float               # Score de riesgo del proveedor (0=bajo, 1=alto)

    # === SECURITY FEATURES (Seguridad) ===
    has_known_breaches: int                  # Binario: aparece en brechas de datos
    breach_count: int                        # Cantidad de brechas conocidas
    breach_severity_score: float             # Score de severidad (0=sin brechas, 1=alto riesgo)

    # === DERIVED SCORES (Scores Compuestos) ===
    identity_strength_score: float           # Score de fortaleza de identidad (0-1)
    activity_engagement_score: float         # Score de engagement/actividad (0-1)
    security_risk_score: float               # Score de riesgo de seguridad (0-1)
    overall_trust_score: float               # Score de confianza general (0-1)

    # === CATEGORICAL FEATURES (Para encoding posterior) ===
    email_provider_type: str                 # Categoría: 'gmail', 'corporate', 'other', etc
    location_country: str                    # País declarado (o 'unknown')
    profile_completeness: str                # Categoría: 'full', 'partial', 'minimal', 'none'

    # === METADATA ===
    enrichment_timestamp: str                # ISO timestamp del enriquecimiento
    feature_version: str                     # Versión del esquema de features


class CreditScoringFeatureEngineer:
    """Transforma datos OSINT en features para scoring crediticio"""

    FEATURE_VERSION = "1.0.0"

    # Categorías de proveedores de email por riesgo
    PROVIDER_RISK_MAP = {
        'gmail': 0.2,      # Bajo riesgo
        'outlook': 0.2,
        'yahoo': 0.3,
        'icloud': 0.2,
        'corporate': 0.1,  # Muy bajo riesgo
        'disposable': 1.0, # Alto riesgo
        'unknown': 0.5     # Riesgo medio
    }

    def __init__(self, osint_data: Dict[str, Any]):
        """
        Args:
            osint_data: Output del EmailOSINT.enrich()
        """
        self.raw_data = osint_data
        self.features = None

    def _calculate_account_age(self) -> tuple[int, float]:
        """Calcula antigüedad de cuenta en días y años"""
        github_created = self.raw_data.get('github', {}).get('created_at')

        if not github_created:
            return 0, 0.0

        # Parse GitHub date format: "2014-06-06T16:28:48Z"
        created_date = datetime.fromisoformat(github_created.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        age_days = (now - created_date).days
        age_years = age_days / 365.25

        return age_days, round(age_years, 2)

    def _calculate_activity_ratio(self, repos: int, age_years: float) -> float:
        """Calcula ratio de actividad (repos por año)"""
        if age_years == 0:
            return 0.0

        ratio = repos / age_years
        # Normalizar: 3+ repos/año = 1.0
        return min(ratio / 3.0, 1.0)

    def _calculate_digital_footprint(self) -> int:
        """Cuenta cantidad de plataformas con presencia"""
        count = 0
        if self.raw_data.get('gravatar', {}).get('has_gravatar'):
            count += 1
        if self.raw_data.get('github', {}).get('github_found'):
            count += 1
        # Aquí se pueden agregar más plataformas
        return count

    def _has_professional_bio(self) -> int:
        """Detecta si tiene bio profesional"""
        bio = self.raw_data.get('github', {}).get('bio', '')
        # Bio con mínimo 10 caracteres se considera profesional
        return 1 if bio and len(bio) >= 10 else 0

    def _get_email_provider_risk(self) -> float:
        """Calcula score de riesgo del proveedor de email"""
        provider = self.raw_data.get('validation', {}).get('provider_type', 'unknown')

        if self.raw_data.get('domain_analysis', {}).get('is_disposable'):
            return self.PROVIDER_RISK_MAP['disposable']

        return self.PROVIDER_RISK_MAP.get(provider, 0.5)

    def _calculate_identity_strength(self) -> float:
        """
        Score de fortaleza de identidad digital
        Combina: antigüedad, presencia en plataformas, completitud de perfil
        """
        github = self.raw_data.get('github', {})

        # Componentes
        has_github = 1.0 if github.get('github_found') else 0.0
        has_gravatar = 1.0 if self.raw_data.get('gravatar', {}).get('has_gravatar') else 0.0
        has_bio = 1.0 if github.get('bio') else 0.0
        has_location = 1.0 if github.get('location') else 0.0
        has_company = 1.0 if github.get('company') else 0.0

        # Antigüedad normalizada (10+ años = 1.0)
        _, age_years = self._calculate_account_age()
        age_score = min(age_years / 10.0, 1.0)

        # Peso ponderado
        score = (
            has_github * 0.25 +
            has_gravatar * 0.15 +
            age_score * 0.30 +
            has_bio * 0.10 +
            has_location * 0.10 +
            has_company * 0.10
        )

        return round(score, 3)

    def _calculate_activity_engagement(self) -> float:
        """
        Score de engagement/actividad
        Combina: repos, followers, ratio de actividad
        """
        github = self.raw_data.get('github', {})
        repos = github.get('public_repos', 0) or 0
        followers = github.get('followers', 0) or 0

        # Normalización
        repos_score = min(repos / 20.0, 1.0)      # 20+ repos = 1.0
        followers_score = min(followers / 10.0, 1.0)  # 10+ followers = 1.0

        _, age_years = self._calculate_account_age()
        activity_ratio = self._calculate_activity_ratio(repos, age_years)

        score = (
            repos_score * 0.4 +
            followers_score * 0.3 +
            activity_ratio * 0.3
        )

        return round(score, 3)

    def _calculate_security_risk(self) -> float:
        """
        Score de riesgo de seguridad (0=bajo riesgo, 1=alto riesgo)
        Combina: brechas, email temporal, provider risk
        """
        breach_count = self.raw_data.get('breach_check', {}).get('breach_count', 0) or 0
        is_disposable = self.raw_data.get('domain_analysis', {}).get('is_disposable', False)
        provider_risk = self._get_email_provider_risk()

        # Normalización
        breach_score = min(breach_count / 3.0, 1.0)  # 3+ brechas = máximo riesgo
        disposable_score = 1.0 if is_disposable else 0.0

        risk_score = (
            breach_score * 0.4 +
            disposable_score * 0.4 +
            provider_risk * 0.2
        )

        return round(risk_score, 3)

    def _calculate_overall_trust(self) -> float:
        """
        Score de confianza general para scoring crediticio
        Combina todos los componentes
        """
        identity = self._calculate_identity_strength()
        activity = self._calculate_activity_engagement()
        security_risk = self._calculate_security_risk()

        # Trust es inverso al riesgo
        security_trust = 1.0 - security_risk

        trust_score = (
            identity * 0.40 +
            activity * 0.30 +
            security_trust * 0.30
        )

        return round(trust_score, 3)

    def _get_profile_completeness(self) -> str:
        """Clasifica completitud del perfil"""
        github = self.raw_data.get('github', {})

        if not github.get('github_found'):
            return 'none'

        score = sum([
            bool(github.get('bio')),
            bool(github.get('location')),
            bool(github.get('company')),
            github.get('public_repos', 0) > 0,
            github.get('followers', 0) > 0
        ])

        if score >= 4:
            return 'full'
        elif score >= 2:
            return 'partial'
        else:
            return 'minimal'

    def _extract_location_country(self) -> str:
        """Extrae país de la ubicación declarada"""
        location = self.raw_data.get('github', {}).get('location', '')

        if not location:
            return 'unknown'

        # Normalizar países comunes (puede expandirse)
        location_lower = location.lower()

        country_map = {
            'argentina': 'AR',
            'brazil': 'BR',
            'mexico': 'MX',
            'usa': 'US',
            'united states': 'US',
            'spain': 'ES',
            'colombia': 'CO',
            'chile': 'CL',
        }

        for country, code in country_map.items():
            if country in location_lower:
                return code

        return 'OTHER'

    def generate_features(self) -> MLFeatures:
        """Genera el vector completo de features estructurados"""

        # Extraer datos base
        validation = self.raw_data.get('validation', {})
        github = self.raw_data.get('github', {})
        gravatar = self.raw_data.get('gravatar', {})
        breach = self.raw_data.get('breach_check', {})
        domain = self.raw_data.get('domain_analysis', {})

        # Calcular features derivados
        age_days, age_years = self._calculate_account_age()
        repos = github.get('public_repos', 0) or 0

        # Construir objeto de features
        self.features = MLFeatures(
            # Identity
            account_age_days=age_days,
            account_age_years=age_years,
            has_github=int(github.get('github_found', False)),
            has_gravatar=int(gravatar.get('has_gravatar', False)),
            digital_footprint_count=self._calculate_digital_footprint(),

            # Activity
            github_repos=repos,
            github_followers=github.get('followers', 0) or 0,
            github_activity_ratio=round(self._calculate_activity_ratio(repos, age_years), 3),
            has_professional_bio=self._has_professional_bio(),
            has_location=int(bool(github.get('location'))),
            has_company=int(bool(github.get('company'))),

            # Email
            email_valid=int(validation.get('is_valid_format', False)),
            is_free_email=int(validation.get('is_free_provider', False)),
            is_corporate_email=int(domain.get('likely_corporate', False)),
            is_disposable_email=int(domain.get('is_disposable', False)),
            email_provider_risk=self._get_email_provider_risk(),

            # Security
            has_known_breaches=int(breach.get('has_breaches', False) or False),
            breach_count=breach.get('breach_count', 0) or 0,
            breach_severity_score=min((breach.get('breach_count', 0) or 0) / 3.0, 1.0),

            # Derived scores
            identity_strength_score=self._calculate_identity_strength(),
            activity_engagement_score=self._calculate_activity_engagement(),
            security_risk_score=self._calculate_security_risk(),
            overall_trust_score=self._calculate_overall_trust(),

            # Categorical
            email_provider_type=validation.get('provider_type', 'unknown'),
            location_country=self._extract_location_country(),
            profile_completeness=self._get_profile_completeness(),

            # Metadata
            enrichment_timestamp=self.raw_data.get('enrichment_timestamp', datetime.now().isoformat()),
            feature_version=self.FEATURE_VERSION
        )

        return self.features

    def to_dict(self) -> Dict[str, Any]:
        """Convierte features a diccionario"""
        if not self.features:
            self.generate_features()
        return asdict(self.features)

    def to_ml_ready(self) -> Dict[str, Any]:
        """
        Retorna features en formato listo para ML
        Separa numéricos y categóricos para facilitar el preprocessing
        """
        if not self.features:
            self.generate_features()

        feature_dict = asdict(self.features)

        # Separar features por tipo
        numerical_features = {}
        categorical_features = {}
        metadata = {}

        numerical_keys = [
            'account_age_days', 'account_age_years', 'has_github', 'has_gravatar',
            'digital_footprint_count', 'github_repos', 'github_followers',
            'github_activity_ratio', 'has_professional_bio', 'has_location',
            'has_company', 'email_valid', 'is_free_email', 'is_corporate_email',
            'is_disposable_email', 'email_provider_risk', 'has_known_breaches',
            'breach_count', 'breach_severity_score', 'identity_strength_score',
            'activity_engagement_score', 'security_risk_score', 'overall_trust_score'
        ]

        categorical_keys = [
            'email_provider_type', 'location_country', 'profile_completeness'
        ]

        for key in numerical_keys:
            numerical_features[key] = feature_dict[key]

        for key in categorical_keys:
            categorical_features[key] = feature_dict[key]

        metadata['enrichment_timestamp'] = feature_dict['enrichment_timestamp']
        metadata['feature_version'] = feature_dict['feature_version']

        return {
            'numerical_features': numerical_features,
            'categorical_features': categorical_features,
            'metadata': metadata
        }

    def get_feature_importance_guide(self) -> Dict[str, str]:
        """
        Guía de importancia de features para modelos de scoring crediticio
        """
        return {
            'CRITICAL (Alta importancia para scoring)': [
                'account_age_years',
                'overall_trust_score',
                'is_disposable_email',
                'has_known_breaches',
                'identity_strength_score'
            ],
            'IMPORTANT (Media importancia)': [
                'is_corporate_email',
                'security_risk_score',
                'activity_engagement_score',
                'profile_completeness',
                'email_provider_risk'
            ],
            'CONTEXTUAL (Baja importancia, pero útil)': [
                'github_repos',
                'github_followers',
                'location_country',
                'has_professional_bio',
                'digital_footprint_count'
            ]
        }


def main():
    """Demo: genera features ML desde archivo OSINT"""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python ml_feature_engineering.py <osint_results.json>")
        return

    # Leer archivo de resultados OSINT
    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Extraer full_data
    osint_data = data.get('full_data', data)

    # Generar features ML
    print("\n" + "="*60)
    print("ML FEATURE ENGINEERING - Credit Scoring")
    print("="*60)

    engineer = CreditScoringFeatureEngineer(osint_data)
    features = engineer.generate_features()

    # Mostrar features
    print("\n📊 FEATURES GENERADOS:\n")
    feature_dict = asdict(features)

    print("🔵 IDENTITY FEATURES:")
    print(f"  • Antigüedad cuenta: {features.account_age_years} años ({features.account_age_days} días)")
    print(f"  • Digital footprint: {features.digital_footprint_count} plataformas")
    print(f"  • Identity strength: {features.identity_strength_score}")

    print("\n🟢 ACTIVITY FEATURES:")
    print(f"  • GitHub repos: {features.github_repos}")
    print(f"  • GitHub followers: {features.github_followers}")
    print(f"  • Activity ratio: {features.github_activity_ratio}")
    print(f"  • Activity engagement: {features.activity_engagement_score}")

    print("\n🟡 EMAIL FEATURES:")
    print(f"  • Provider type: {features.email_provider_type}")
    print(f"  • Is corporate: {bool(features.is_corporate_email)}")
    print(f"  • Is disposable: {bool(features.is_disposable_email)}")
    print(f"  • Provider risk: {features.email_provider_risk}")

    print("\n🔴 SECURITY FEATURES:")
    print(f"  • Breach count: {features.breach_count}")
    print(f"  • Security risk: {features.security_risk_score}")

    print("\n⭐ SCORING FEATURES:")
    print(f"  • Overall trust score: {features.overall_trust_score}")
    print(f"  • Profile completeness: {features.profile_completeness}")
    print(f"  • Location: {features.location_country}")

    # Exportar
    output_file = input_file.replace('.json', '_ml_features.json')
    ml_ready = engineer.to_ml_ready()

    with open(output_file, 'w') as f:
        json.dump({
            'all_features': feature_dict,
            'ml_ready': ml_ready,
            'feature_importance_guide': engineer.get_feature_importance_guide()
        }, f, indent=2)

    print(f"\n💾 Features ML guardados en: {output_file}")

    # Guía de importancia
    print("\n" + "="*60)
    print("GUÍA DE IMPORTANCIA DE FEATURES")
    print("="*60)
    guide = engineer.get_feature_importance_guide()
    for category, features in guide.items():
        print(f"\n{category}:")
        for feat in features:
            print(f"  • {feat}")


if __name__ == "__main__":
    main()
