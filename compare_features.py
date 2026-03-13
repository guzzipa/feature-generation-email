#!/usr/bin/env python3
"""
Compara features v1.0 (básico) vs v2.0 (avanzado) lado a lado
Muestra mejoras y nuevos insights para scoring crediticio
"""

import json
import sys
from pathlib import Path


def load_features(file_path: str) -> dict:
    """Carga archivo de features"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def compare_features(v1_file: str, v2_file: str):
    """Compara ambas versiones"""

    v1_data = load_features(v1_file)
    v2_data = load_features(v2_file)

    v1_features = v1_data.get('ml_ready', {}).get('numerical_features', {})
    v2_features = v2_data.get('ml_ready', {}).get('numerical_features', {})

    print("\n" + "="*80)
    print("COMPARACIÓN DE FEATURES: v1.0 (Básico) vs v2.0 (Avanzado)")
    print("="*80)

    # Count
    print(f"\n📊 CONTEO:")
    print(f"   v1.0 Numerical: {len(v1_features)}")
    print(f"   v2.0 Numerical: {len(v2_features)}")
    print(f"   Nuevos features: +{len(v2_features) - len(v1_features)} ({(len(v2_features) / len(v1_features) - 1) * 100:.0f}% más)")

    # Compare common features
    print(f"\n🔄 FEATURES COMUNES (valores diferentes):")
    common_keys = set(v1_features.keys()) & set(v2_features.keys())

    differences = []
    for key in sorted(common_keys):
        v1_val = v1_features[key]
        v2_val = v2_features[key]

        if v1_val != v2_val:
            diff_pct = ((v2_val - v1_val) / v1_val * 100) if v1_val != 0 else 0
            differences.append((key, v1_val, v2_val, diff_pct))

    for key, v1_val, v2_val, diff_pct in differences[:10]:
        arrow = "📈" if diff_pct > 0 else "📉"
        print(f"   {arrow} {key}:")
        print(f"      v1.0: {v1_val:.3f} → v2.0: {v2_val:.3f} ({diff_pct:+.1f}%)")

    # New features
    print(f"\n✨ FEATURES NUEVOS EN v2.0 (muestra de 20):")
    new_features = set(v2_features.keys()) - set(v1_features.keys())

    categories = {
        'temporal': ['days_since', 'is_active', 'velocity', 'recency', 'monthly', 'age_weeks', 'age_months'],
        'email': ['username', 'entropy', 'structure', 'subaddr', 'role'],
        'ratios': ['_to_', 'ratio', '_per_'],
        'nlp': ['bio_', 'location_', 'company_'],
        'anomaly': ['outlier', 'suspicious', 'anomaly', 'inconsistency'],
        'quality': ['quality', 'completeness', 'missing']
    }

    for category, keywords in categories.items():
        category_features = [f for f in new_features if any(k in f for k in keywords)]
        if category_features:
            print(f"\n   📁 {category.upper()}:")
            for feat in sorted(category_features)[:5]:
                val = v2_features.get(feat, 0)
                print(f"      • {feat}: {val}")

    # Score comparison
    print(f"\n🎯 COMPARACIÓN DE SCORES CRÍTICOS:")

    score_comparison = [
        ('overall_trust_score', 'Trust Global'),
        ('identity_strength_score', 'Fortaleza Identidad'),
        ('activity_engagement_score', 'Engagement'),
        ('security_risk_score', 'Riesgo Seguridad'),
    ]

    for key, label in score_comparison:
        v1_val = v1_features.get(key, 0)
        v2_val = v2_features.get(key, 0)
        diff = v2_val - v1_val
        pct = (diff / v1_val * 100) if v1_val != 0 else 0

        trend = "🔴" if diff < -0.1 else "🟢" if diff > 0.1 else "⚪"
        print(f"   {trend} {label}:")
        print(f"      v1.0: {v1_val:.3f} | v2.0: {v2_val:.3f} | Δ: {diff:+.3f} ({pct:+.1f}%)")

    # New scores only in v2
    new_scores = [
        ('data_quality_score', 'Calidad de Datos'),
        ('recency_score', 'Score de Recencia'),
        ('professional_signal_score', 'Señal Profesional'),
        ('anomaly_score', 'Score de Anomalías'),
    ]

    print(f"\n✨ NUEVOS SCORES EN v2.0:")
    for key, label in new_scores:
        val = v2_features.get(key, None)
        if val is not None:
            emoji = "✅" if val > 0.5 else "⚠️" if val > 0.3 else "🔴"
            print(f"   {emoji} {label}: {val:.3f}")

    # Categorical comparison
    v1_cat = v1_data.get('ml_ready', {}).get('categorical_features', {})
    v2_cat = v2_data.get('ml_ready', {}).get('categorical_features', {})

    print(f"\n📋 FEATURES CATEGÓRICOS:")
    print(f"   v1.0: {len(v1_cat)} features")
    for key, val in v1_cat.items():
        print(f"      • {key}: {val}")

    print(f"\n   v2.0: {len(v2_cat)} features")
    for key, val in v2_cat.items():
        v1_val = v1_cat.get(key)
        if v1_val == val:
            print(f"      • {key}: {val}")
        elif v1_val is None:
            print(f"      ✨ {key}: {val} (NUEVO)")
        else:
            print(f"      🔄 {key}: {v1_val} → {val}")

    # Analysis
    print(f"\n" + "="*80)
    print("🔍 ANÁLISIS DE MEJORAS")
    print("="*80)

    # Temporal
    days_since = v2_features.get('days_since_last_github_update', 0)
    if days_since > 365:
        print(f"\n⚠️  ALERTA: Inactividad detectada ({days_since} días)")
        print(f"   v1.0 NO detectaba esto")
        print(f"   v2.0 penaliza en trust score")

    # Email quality
    entropy = v2_features.get('username_entropy', 0)
    structure = v2_cat.get('email_structure_type', 'unknown')
    print(f"\n📧 EMAIL ANALYSIS:")
    print(f"   Estructura: {structure}")
    print(f"   Entropía: {entropy:.3f}")
    if entropy > 4.0:
        print(f"   ⚠️  Alta entropía = posible email random (fraude)")
    elif structure == 'professional':
        print(f"   ✅ Email profesional detectado")

    # Anomalies
    anomaly = v2_features.get('anomaly_score', 0)
    print(f"\n🚨 ANOMALÍAS:")
    print(f"   Score: {anomaly:.3f}")
    if anomaly > 0.5:
        print(f"   ⚠️  Patrones sospechosos detectados")
    else:
        print(f"   ✅ Sin anomalías detectadas")

    # Data quality
    completeness = v2_features.get('data_completeness_ratio', 0)
    missing = v2_features.get('missing_critical_fields', 0)
    print(f"\n📊 CALIDAD DE DATOS:")
    print(f"   Completitud: {completeness:.1%}")
    print(f"   Campos faltantes: {missing}")
    if completeness < 0.5:
        print(f"   ⚠️  Perfil incompleto - revisar")

    # Recommendations
    print(f"\n" + "="*80)
    print("💡 RECOMENDACIONES PARA MODELO ML")
    print("="*80)

    v2_trust = v2_features.get('overall_trust_score', 0)

    print(f"\n🎯 DECISIÓN DE CRÉDITO (basado en features v2.0):")
    if v2_trust >= 0.8:
        print(f"   ✅ APROBAR - Trust score alto ({v2_trust:.3f})")
        print(f"   Límite sugerido: Alto")
    elif v2_trust >= 0.6:
        print(f"   ⚪ REVISAR - Trust score medio ({v2_trust:.3f})")
        print(f"   Límite sugerido: Medio, verificar ingresos")
    elif v2_trust >= 0.4:
        print(f"   ⚠️  PRECAUCIÓN - Trust score bajo ({v2_trust:.3f})")
        print(f"   Límite sugerido: Bajo, verificación adicional")
    else:
        print(f"   🔴 RECHAZAR - Trust score muy bajo ({v2_trust:.3f})")
        print(f"   Riesgo alto de default")

    print(f"\n📈 TOP 10 FEATURES PARA TU MODELO:")
    important_features = [
        'overall_trust_score',
        'monthly_activity_score',
        'days_since_last_github_update',
        'username_entropy',
        'data_completeness_ratio',
        'anomaly_score',
        'recency_score',
        'professional_signal_score',
        'account_age_years',
        'followers_to_following_ratio'
    ]

    for i, feat in enumerate(important_features, 1):
        val = v2_features.get(feat, v2_cat.get(feat, 'N/A'))
        print(f"   {i:2d}. {feat}: {val}")

    print(f"\n" + "="*80)


def main():
    if len(sys.argv) < 3:
        print("Uso: python compare_features.py <v1_ml_features.json> <v2_advanced_features.json>")
        return

    v1_file = sys.argv[1]
    v2_file = sys.argv[2]

    if not Path(v1_file).exists():
        print(f"❌ Archivo v1.0 no encontrado: {v1_file}")
        return

    if not Path(v2_file).exists():
        print(f"❌ Archivo v2.0 no encontrado: {v2_file}")
        return

    compare_features(v1_file, v2_file)


if __name__ == "__main__":
    main()
