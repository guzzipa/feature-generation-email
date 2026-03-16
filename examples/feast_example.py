#!/usr/bin/env python3
"""
Feast Feature Store Integration Examples
Complete workflows for training and serving with Feast

Run:
    python examples/feast_example.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, timedelta
from feast_integration import FeastFeatureStore


def example_1_basic_enrichment():
    """Example 1: Basic email enrichment and push to Feast"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Email Enrichment and Push to Feast")
    print("="*60)

    feast = FeastFeatureStore(repo_path="./feature_repo")

    # Enrich single email
    print("\n📧 Enriching email...")
    df = feast.enrich_to_dataframe(
        emails=["test@example.com"],
        skip_commercial=True  # Use free sources only
    )

    print(f"\n✅ Generated {len(df.columns)} features")
    print("\nSample features:")
    print(df[["email", "is_valid_format", "is_free_provider", "has_github"]].to_string())

    # Push to Feast
    print("\n📤 Pushing to Feast...")
    feast.push_features(df)
    print("✅ Features pushed to online and offline stores")


def example_2_batch_enrichment():
    """Example 2: Batch email enrichment for training data"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Enrichment for Training Dataset")
    print("="*60)

    feast = FeastFeatureStore()

    # Batch of emails
    emails = [
        "john.doe@example.com",
        "jane.smith@company.com",
        "developer@startup.io",
        "admin@tech.org"
    ]

    print(f"\n📧 Enriching {len(emails)} emails...")
    df = feast.enrich_to_dataframe(
        emails=emails,
        skip_commercial=True
    )

    print(f"\n✅ Enriched {len(df)} emails")
    print(f"📊 Total features: {len(df.columns)}")

    # Show summary statistics
    print("\n📈 Feature Statistics:")
    print(df[["has_github", "github_followers", "github_repos"]].describe())

    # Push to Feast
    print("\n📤 Pushing batch to Feast...")
    feast.push_features(df)
    print("✅ Batch pushed successfully")


def example_3_online_serving():
    """Example 3: Get features from online store for real-time prediction"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Online Feature Serving (Real-Time)")
    print("="*60)

    feast = FeastFeatureStore()

    # Emails to score
    emails = ["test@example.com", "john.doe@example.com"]

    print(f"\n🔍 Fetching online features for {len(emails)} emails...")

    # Get specific features for fraud detection
    features_df = feast.get_online_features(
        emails=emails,
        features=[
            "identity_features:is_valid_format",
            "identity_features:is_disposable",
            "security_features:has_breaches",
            "security_features:spam_score",
            "derived_scores:trust_score",
            "derived_scores:fraud_risk_score"
        ]
    )

    print("\n📊 Online Features Retrieved:")
    print(features_df.to_string())

    # Make simple fraud decision
    print("\n🎯 Fraud Detection Results:")
    for _, row in features_df.iterrows():
        fraud_risk = row.get("fraud_risk_score", 0)
        trust = row.get("trust_score", 0)

        if fraud_risk > 0.7:
            decision = "🚫 REJECT"
        elif fraud_risk > 0.4:
            decision = "⚠️  REVIEW"
        else:
            decision = "✅ APPROVE"

        print(f"{row['email']}: {decision} (fraud_risk={fraud_risk:.2f}, trust={trust:.2f})")


def example_4_historical_features():
    """Example 4: Get historical features for ML training"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Historical Features for ML Training")
    print("="*60)

    feast = FeastFeatureStore()

    # Simulate historical data with timestamps
    entity_df = pd.DataFrame({
        "email": [
            "test@example.com",
            "john.doe@example.com",
            "jane.smith@company.com"
        ],
        "event_timestamp": [
            datetime.utcnow() - timedelta(days=10),
            datetime.utcnow() - timedelta(days=5),
            datetime.utcnow() - timedelta(days=1)
        ],
        "label": [0, 1, 0]  # Example: 1=fraud, 0=legitimate
    })

    print("\n📅 Entity DataFrame (with timestamps):")
    print(entity_df.to_string())

    # Get point-in-time correct features
    print("\n🔍 Fetching historical features...")
    training_df = feast.get_historical_features(
        entity_df=entity_df,
        features=[
            "identity_features:is_valid_format",
            "security_features:has_breaches",
            "social_features:has_github",
            "derived_scores:trust_score",
            "derived_scores:fraud_risk_score"
        ]
    )

    print("\n📊 Training Dataset:")
    print(training_df.to_string())

    # Prepare for ML
    X = training_df.drop(columns=["email", "event_timestamp", "label"])
    y = training_df["label"]

    print(f"\n✅ Training data ready: X.shape={X.shape}, y.shape={y.shape}")


def example_5_ml_pipeline():
    """Example 5: Complete ML pipeline with Feast"""
    print("\n" + "="*60)
    print("EXAMPLE 5: End-to-End ML Pipeline with Feast")
    print("="*60)

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report
    except ImportError:
        print("⚠️  scikit-learn not installed. Run: pip install scikit-learn")
        return

    feast = FeastFeatureStore()

    # 1. Simulate labeled data
    print("\n📝 Step 1: Preparing training data...")
    emails = [
        "legit1@company.com",
        "legit2@startup.io",
        "fraud1@disposable.com",
        "fraud2@tempmail.net",
        "test@example.com"
    ]
    labels = [0, 0, 1, 1, 0]  # 0=legit, 1=fraud

    # 2. Enrich emails
    print("📧 Step 2: Enriching emails...")
    df = feast.enrich_to_dataframe(emails, skip_commercial=True)

    # 3. Add labels
    df["label"] = labels

    # 4. Select features for training
    print("🔧 Step 3: Feature engineering...")
    feature_cols = [
        "is_valid_format",
        "is_free_provider",
        "is_disposable",
        "has_github",
        "github_followers",
        "has_breaches",
        "trust_score",
        "fraud_risk_score"
    ]

    # Convert boolean to int
    for col in feature_cols:
        if df[col].dtype == bool:
            df[col] = df[col].astype(int)

    X = df[feature_cols].fillna(0)
    y = df["label"]

    # 5. Train model
    print("🤖 Step 4: Training model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 6. Evaluate
    print("📊 Step 5: Evaluating model...")
    predictions = model.predict(X_test)

    print("\n📈 Classification Report:")
    print(classification_report(y_test, predictions, target_names=["Legitimate", "Fraud"]))

    # 7. Feature importance
    print("\n🎯 Top 5 Most Important Features:")
    feature_importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    print(feature_importance.head().to_string(index=False))

    print("\n✅ ML pipeline completed successfully!")


def example_6_real_time_scoring():
    """Example 6: Real-time scoring with Feast + ML model"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Real-Time Fraud Scoring API")
    print("="*60)

    feast = FeastFeatureStore()

    # Simulate new user signup
    new_emails = [
        "prospect@newcompany.com",
        "suspicious@tempmail.net",
        "developer@github.com"
    ]

    print(f"\n🆕 Scoring {len(new_emails)} new signups...")

    for email in new_emails:
        # 1. Get features from online store
        features = feast.get_online_features(
            emails=[email],
            features=[
                "identity_features:is_disposable",
                "security_features:has_breaches",
                "derived_scores:trust_score",
                "derived_scores:fraud_risk_score"
            ]
        )

        # 2. Simple rule-based scoring
        row = features.iloc[0]
        is_disposable = row.get("is_disposable", False)
        has_breaches = row.get("has_breaches", False)
        trust_score = row.get("trust_score", 0)
        fraud_risk = row.get("fraud_risk_score", 0)

        # 3. Decision logic
        if is_disposable or fraud_risk > 0.7:
            decision = "🚫 REJECT"
            action = "Block signup"
        elif has_breaches or fraud_risk > 0.4:
            decision = "⚠️  REVIEW"
            action = "Manual review"
        else:
            decision = "✅ APPROVE"
            action = "Auto-approve"

        print(f"\n{email}:")
        print(f"  Decision: {decision}")
        print(f"  Action: {action}")
        print(f"  Trust: {trust_score:.2f}, Fraud Risk: {fraud_risk:.2f}")


def example_7_materialization():
    """Example 7: Feature materialization workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Feature Materialization Workflow")
    print("="*60)

    feast = FeastFeatureStore()

    print("\n🔄 Running incremental materialization...")
    print("This updates the online store with latest offline features")

    try:
        feast.materialize_incremental()
        print("✅ Materialization completed successfully")
        print("\nℹ️  Run this periodically (hourly/daily) to keep online features fresh")
        print("   Example cron: 0 * * * * python -c 'from feast_integration import FeastFeatureStore; FeastFeatureStore().materialize_incremental()'")

    except Exception as e:
        print(f"⚠️  Materialization failed: {e}")
        print("   This is normal if no offline features exist yet")


# ========== Main ==========

def main():
    """Run all examples"""
    print("\n🎓 FEAST FEATURE STORE INTEGRATION EXAMPLES")
    print("=" * 60)

    examples = [
        ("Basic Enrichment", example_1_basic_enrichment),
        ("Batch Enrichment", example_2_batch_enrichment),
        ("Online Serving", example_3_online_serving),
        ("Historical Features", example_4_historical_features),
        ("ML Pipeline", example_5_ml_pipeline),
        ("Real-Time Scoring", example_6_real_time_scoring),
        ("Materialization", example_7_materialization),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...")
    print("(Press Ctrl+C to skip)\n")

    for name, func in examples:
        try:
            func()
            input("\n⏸  Press Enter to continue to next example...")
        except KeyboardInterrupt:
            print("\n\n⏭  Skipping to next example...")
            continue
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            continue

    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
