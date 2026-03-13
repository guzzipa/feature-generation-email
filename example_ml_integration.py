#!/usr/bin/env python3
"""
Ejemplo de integración de features OSINT con modelos de ML
Demuestra cómo usar los features estructurados en un pipeline de scikit-learn
"""

import json
import numpy as np
from typing import List, Dict, Any


def load_ml_features(json_file: str) -> Dict[str, Any]:
    """Carga features desde archivo JSON"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data['ml_ready']


def prepare_feature_vector(ml_ready: Dict[str, Any]) -> tuple:
    """
    Prepara vector de features listo para modelo

    Returns:
        (feature_vector, feature_names, categorical_dict)
    """
    numerical = ml_ready['numerical_features']
    categorical = ml_ready['categorical_features']

    # Vector de features numéricas
    feature_names = list(numerical.keys())
    feature_vector = np.array([numerical[k] for k in feature_names])

    return feature_vector, feature_names, categorical


def get_credit_score_interpretation(trust_score: float) -> Dict[str, str]:
    """
    Interpreta el trust score como categoría de riesgo crediticio

    Args:
        trust_score: Overall trust score (0-1)

    Returns:
        Diccionario con interpretación de riesgo
    """
    if trust_score >= 0.8:
        category = "BAJO RIESGO"
        recommendation = "APROBACIÓN RECOMENDADA"
        interest_tier = "Tier 1 (tasa preferencial)"
    elif trust_score >= 0.6:
        category = "RIESGO MEDIO"
        recommendation = "APROBACIÓN CONDICIONAL"
        interest_tier = "Tier 2 (tasa estándar)"
    elif trust_score >= 0.4:
        category = "RIESGO MEDIO-ALTO"
        recommendation = "REVISIÓN MANUAL REQUERIDA"
        interest_tier = "Tier 3 (tasa elevada)"
    else:
        category = "ALTO RIESGO"
        recommendation = "RECHAZO RECOMENDADO"
        interest_tier = "No elegible"

    return {
        "risk_category": category,
        "recommendation": recommendation,
        "interest_tier": interest_tier,
        "trust_score": trust_score
    }


def calculate_credit_limit_suggestion(features: Dict[str, Any]) -> int:
    """
    Sugiere límite de crédito basado en features OSINT

    Esta es una heurística simplificada. En producción usarías un modelo entrenado.
    """
    trust = features.get('overall_trust_score', 0)
    identity = features.get('identity_strength_score', 0)
    activity = features.get('activity_engagement_score', 0)
    account_age = features.get('account_age_years', 0)

    # Base amount
    base_limit = 5000  # USD/moneda local

    # Multiplicadores
    trust_multiplier = 1 + (trust * 2)          # 1.0 - 3.0x
    identity_multiplier = 1 + (identity * 1)     # 1.0 - 2.0x
    age_multiplier = 1 + min(account_age / 10, 1.0)  # 1.0 - 2.0x

    # Penalizaciones
    if features.get('is_disposable_email', 0) == 1:
        return 0  # No otorgar crédito

    if features.get('breach_count', 0) > 2:
        trust_multiplier *= 0.5  # Reducir 50%

    if features.get('is_free_email', 0) == 1 and features.get('is_corporate_email', 0) == 0:
        base_limit *= 0.8  # Reducir 20% si no es email corporativo

    suggested_limit = int(base_limit * trust_multiplier * identity_multiplier * age_multiplier)

    # Caps
    suggested_limit = max(500, min(suggested_limit, 50000))

    return suggested_limit


# EJEMPLO DE USO CON SKLEARN (pseudo-código, requiere instalar scikit-learn)
SKLEARN_EXAMPLE = """
# ===================================================================
# EJEMPLO: Integración con scikit-learn
# ===================================================================
# Descomentar si tienes scikit-learn instalado

# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import StandardScaler, LabelEncoder
# import pandas as pd

# def train_credit_model(feature_files: List[str], labels: List[int]):
#     '''
#     Entrena un modelo de clasificación para scoring crediticio
#
#     Args:
#         feature_files: Lista de archivos JSON con features
#         labels: Lista de labels (1=buen pagador, 0=mal pagador)
#     '''
#     # Cargar features
#     X_numerical = []
#     X_categorical = []
#
#     for file in feature_files:
#         ml_ready = load_ml_features(file)
#
#         # Numéricas
#         num_feats = ml_ready['numerical_features']
#         X_numerical.append(list(num_feats.values()))
#
#         # Categóricas (one-hot encoding después)
#         cat_feats = ml_ready['categorical_features']
#         X_categorical.append(cat_feats)
#
#     # Convertir a arrays
#     X_num = np.array(X_numerical)
#     y = np.array(labels)
#
#     # Normalizar features numéricas
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X_num)
#
#     # Entrenar modelo
#     model = RandomForestClassifier(
#         n_estimators=100,
#         max_depth=10,
#         random_state=42
#     )
#     model.fit(X_scaled, y)
#
#     # Feature importance
#     feature_names = list(ml_ready['numerical_features'].keys())
#     importances = model.feature_importances_
#
#     print("\\nTop 10 Features más importantes:")
#     for idx in np.argsort(importances)[::-1][:10]:
#         print(f"  {feature_names[idx]}: {importances[idx]:.4f}")
#
#     return model, scaler
#
# # Predicción
# def predict_credit_risk(model, scaler, feature_file: str):
#     ml_ready = load_ml_features(feature_file)
#     X = np.array([list(ml_ready['numerical_features'].values())])
#     X_scaled = scaler.transform(X)
#
#     prediction = model.predict(X_scaled)[0]
#     probability = model.predict_proba(X_scaled)[0]
#
#     return {
#         'prediction': 'APROBADO' if prediction == 1 else 'RECHAZADO',
#         'probability_good': probability[1],
#         'probability_bad': probability[0]
#     }
"""


def generate_credit_report(ml_features_file: str) -> Dict[str, Any]:
    """
    Genera un reporte completo de análisis crediticio
    """
    ml_ready = load_ml_features(ml_features_file)
    numerical = ml_ready['numerical_features']
    categorical = ml_ready['categorical_features']

    # Interpretación de riesgo
    trust_score = numerical['overall_trust_score']
    risk_interp = get_credit_score_interpretation(trust_score)

    # Sugerencia de límite
    credit_limit = calculate_credit_limit_suggestion(numerical)

    # Factores de riesgo
    risk_factors = []
    positive_factors = []

    # Análisis de factores
    if numerical['is_disposable_email'] == 1:
        risk_factors.append("❌ Email temporal/desechable (CRÍTICO)")

    if numerical['breach_count'] > 0:
        risk_factors.append(f"⚠️  {numerical['breach_count']} brechas de datos conocidas")

    if numerical['account_age_years'] < 1:
        risk_factors.append("⚠️  Cuenta digital muy nueva (<1 año)")

    if numerical['is_free_email'] == 1 and numerical['is_corporate_email'] == 0:
        risk_factors.append("⚠️  Email gratuito (no corporativo)")

    # Factores positivos
    if numerical['account_age_years'] >= 5:
        positive_factors.append(f"✅ Identidad digital establecida ({numerical['account_age_years']:.1f} años)")

    if numerical['identity_strength_score'] >= 0.7:
        positive_factors.append(f"✅ Identidad verificable (score: {numerical['identity_strength_score']:.2f})")

    if categorical['profile_completeness'] == 'full':
        positive_factors.append("✅ Perfil digital completo")

    if numerical['has_known_breaches'] == 0:
        positive_factors.append("✅ Sin brechas de seguridad conocidas")

    if numerical['digital_footprint_count'] >= 2:
        positive_factors.append(f"✅ Presencia en {numerical['digital_footprint_count']} plataformas")

    # Construir reporte
    report = {
        "risk_assessment": risk_interp,
        "suggested_credit_limit_usd": credit_limit,
        "key_scores": {
            "overall_trust": numerical['overall_trust_score'],
            "identity_strength": numerical['identity_strength_score'],
            "activity_engagement": numerical['activity_engagement_score'],
            "security_risk": numerical['security_risk_score']
        },
        "risk_factors": risk_factors if risk_factors else ["Sin factores de riesgo críticos"],
        "positive_factors": positive_factors,
        "profile_summary": {
            "account_age_years": numerical['account_age_years'],
            "location": categorical['location_country'],
            "email_type": categorical['email_provider_type'],
            "profile_completeness": categorical['profile_completeness']
        },
        "recommendations": _generate_recommendations(numerical, categorical, risk_interp)
    }

    return report


def _generate_recommendations(numerical: Dict, categorical: Dict, risk_interp: Dict) -> List[str]:
    """Genera recomendaciones operativas"""
    recommendations = []

    trust = numerical['overall_trust_score']

    if trust >= 0.8:
        recommendations.append("Procesar aprobación automática")
        recommendations.append("Ofrecer productos premium")
    elif trust >= 0.6:
        recommendations.append("Aprobación con verificación de ingresos")
        recommendations.append("Límite inicial conservador con revisión a 6 meses")
    elif trust >= 0.4:
        recommendations.append("Requiere revisión manual del analista de crédito")
        recommendations.append("Solicitar documentación adicional")
        recommendations.append("Considerar producto asegurado/garantizado")
    else:
        recommendations.append("Rechazar solicitud o requerir co-deudor")
        recommendations.append("Ofrecer productos alternativos (cuenta sin crédito)")

    # Recomendaciones específicas
    if numerical['is_disposable_email'] == 1:
        recommendations.append("BLOQUEAR: Email desechable detectado")

    if numerical['breach_count'] > 3:
        recommendations.append("Requiere verificación de identidad reforzada (2FA/biométrica)")

    if categorical['profile_completeness'] == 'none':
        recommendations.append("Solicitar información adicional para verificación")

    return recommendations


def print_credit_report(report: Dict[str, Any]):
    """Imprime reporte formateado"""
    print("\n" + "="*70)
    print("REPORTE DE ANÁLISIS CREDITICIO OSINT")
    print("="*70)

    # Risk Assessment
    risk = report['risk_assessment']
    print(f"\n🎯 EVALUACIÓN DE RIESGO: {risk['risk_category']}")
    print(f"   Trust Score: {risk['trust_score']:.3f}")
    print(f"   Recomendación: {risk['recommendation']}")
    print(f"   Tier de Interés: {risk['interest_tier']}")

    # Credit Limit
    print(f"\n💰 LÍMITE DE CRÉDITO SUGERIDO: ${report['suggested_credit_limit_usd']:,} USD")

    # Key Scores
    print("\n📊 SCORES CLAVE:")
    scores = report['key_scores']
    print(f"   • Overall Trust:        {scores['overall_trust']:.3f}")
    print(f"   • Identity Strength:    {scores['identity_strength']:.3f}")
    print(f"   • Activity Engagement:  {scores['activity_engagement']:.3f}")
    print(f"   • Security Risk:        {scores['security_risk']:.3f}")

    # Profile Summary
    print("\n👤 PERFIL:")
    profile = report['profile_summary']
    print(f"   • Antigüedad digital: {profile['account_age_years']:.1f} años")
    print(f"   • Ubicación: {profile['location']}")
    print(f"   • Tipo email: {profile['email_type']}")
    print(f"   • Completitud: {profile['profile_completeness']}")

    # Positive Factors
    print("\n✅ FACTORES POSITIVOS:")
    for factor in report['positive_factors']:
        print(f"   {factor}")

    # Risk Factors
    print("\n⚠️  FACTORES DE RIESGO:")
    for factor in report['risk_factors']:
        print(f"   {factor}")

    # Recommendations
    print("\n💡 RECOMENDACIONES:")
    for rec in report['recommendations']:
        print(f"   • {rec}")

    print("\n" + "="*70)


def main():
    """Demo del reporte crediticio"""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python example_ml_integration.py <ml_features.json>")
        return

    features_file = sys.argv[1]

    # Generar reporte
    report = generate_credit_report(features_file)

    # Mostrar reporte
    print_credit_report(report)

    # Guardar reporte
    output_file = features_file.replace('.json', '_credit_report.json')
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Reporte guardado en: {output_file}")

    # Mostrar ejemplo de sklearn
    print("\n" + "="*70)
    print("INTEGRACIÓN CON SCIKIT-LEARN")
    print("="*70)
    print(SKLEARN_EXAMPLE)


if __name__ == "__main__":
    main()
