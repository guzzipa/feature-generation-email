#!/usr/bin/env python3
"""
Feast Feature Store Integration
Pushes email intelligence features to Feast for ML model serving

This module converts enrichment results into Feast-compatible format
and manages feature materialization to online/offline stores.

Version: 4.1.0
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import asdict

from full_enrichment import EmailEnrichmentPipeline
from enhanced_feature_engineering import EnhancedFeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeastFeatureStore:
    """
    Feast Feature Store integration for email intelligence features.

    Pushes enriched email features to Feast for:
    - Online serving (real-time predictions)
    - Offline serving (training datasets)
    - Feature versioning and lineage
    - Point-in-time correct joins
    """

    def __init__(self, repo_path: str = "./feature_repo"):
        """
        Initialize Feast feature store.

        Args:
            repo_path: Path to Feast repository
        """
        self.repo_path = repo_path
        self._store = None

    def get_store(self):
        """Get Feast FeatureStore instance (lazy loading)."""
        if self._store is None:
            try:
                from feast import FeatureStore
                self._store = FeatureStore(repo_path=self.repo_path)
                logger.info(f"✅ Connected to Feast repository: {self.repo_path}")
            except ImportError:
                logger.error("❌ Feast not installed. Run: pip install feast")
                raise
            except Exception as e:
                logger.error(f"❌ Error connecting to Feast: {e}")
                raise
        return self._store

    def enrich_to_dataframe(
        self,
        emails: List[str],
        ip_addresses: Optional[List[str]] = None,
        skip_commercial: bool = False
    ) -> pd.DataFrame:
        """
        Enrich multiple emails and convert to Feast-compatible DataFrame.

        Args:
            emails: List of email addresses
            ip_addresses: Optional list of IP addresses (parallel to emails)
            skip_commercial: Skip commercial APIs

        Returns:
            DataFrame with email, event_timestamp, and all features
        """
        logger.info(f"🚀 Enriching {len(emails)} emails for Feast...")

        pipeline = EmailEnrichmentPipeline()
        engineer = EnhancedFeatureEngineer()

        results = []
        for i, email in enumerate(emails):
            ip = ip_addresses[i] if ip_addresses and i < len(ip_addresses) else None

            try:
                # Enrich email
                enrichment_data = pipeline.enrich_email(
                    email=email,
                    ip_address=ip,
                    skip_commercial=skip_commercial
                )

                # Generate features
                features = engineer.generate_features(enrichment_data)

                # Convert to dict
                feature_dict = asdict(features)

                # Add entity and timestamp
                feature_dict['email'] = email
                feature_dict['event_timestamp'] = datetime.utcnow()

                results.append(feature_dict)
                logger.info(f"   ✅ {email} enriched successfully")

            except Exception as e:
                logger.error(f"   ❌ Error enriching {email}: {e}")
                continue

        if not results:
            raise ValueError("No emails were successfully enriched")

        df = pd.DataFrame(results)
        logger.info(f"✅ Created DataFrame with {len(df)} rows and {len(df.columns)} columns")

        return df

    def push_features(
        self,
        df: pd.DataFrame,
        feature_view_name: str = "email_features"
    ) -> None:
        """
        Push features to Feast online store.

        Args:
            df: DataFrame with features (must have 'email' and 'event_timestamp')
            feature_view_name: Name of feature view to push to
        """
        store = self.get_store()

        logger.info(f"📤 Pushing {len(df)} feature rows to Feast online store...")

        try:
            # Write to offline store (parquet)
            store.write_to_offline_store(
                feature_view_name=feature_view_name,
                df=df,
                allow_registry_cache=True
            )
            logger.info(f"   ✅ Written to offline store")

            # Materialize to online store
            store.materialize(
                start_date=datetime.utcnow() - timedelta(days=1),
                end_date=datetime.utcnow()
            )
            logger.info(f"   ✅ Materialized to online store (Redis)")

            logger.info(f"✅ Successfully pushed features to Feast")

        except Exception as e:
            logger.error(f"❌ Error pushing to Feast: {e}")
            raise

    def get_online_features(
        self,
        emails: List[str],
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get features from online store for real-time prediction.

        Args:
            emails: List of email addresses
            features: List of feature names to retrieve (None = all)

        Returns:
            DataFrame with requested features
        """
        store = self.get_store()

        if features is None:
            # Get all features from email_features view
            features = [
                "email_features:is_valid_format",
                "email_features:is_free_provider",
                "email_features:has_github",
                "email_features:github_followers",
                "email_features:github_repos",
                "email_features:has_breaches",
                "email_features:identity_strength_score",
                "email_features:trust_score",
                "email_features:security_risk_score",
                # Add more features as needed
            ]

        logger.info(f"🔍 Fetching online features for {len(emails)} emails...")

        try:
            # Prepare entity dataframe
            entity_df = pd.DataFrame({
                "email": emails
            })

            # Get features from online store
            feature_vector = store.get_online_features(
                features=features,
                entity_rows=entity_df.to_dict('records')
            ).to_df()

            logger.info(f"✅ Retrieved {len(feature_vector)} rows with {len(feature_vector.columns)} features")
            return feature_vector

        except Exception as e:
            logger.error(f"❌ Error fetching online features: {e}")
            raise

    def get_historical_features(
        self,
        entity_df: pd.DataFrame,
        features: List[str],
        full_feature_names: bool = True
    ) -> pd.DataFrame:
        """
        Get historical features for training dataset (point-in-time correct).

        Args:
            entity_df: DataFrame with 'email' and 'event_timestamp' columns
            features: List of feature view:feature names
            full_feature_names: Include feature view prefix in column names

        Returns:
            DataFrame with historical features joined to entity_df
        """
        store = self.get_store()

        logger.info(f"📚 Fetching historical features for {len(entity_df)} records...")

        try:
            training_df = store.get_historical_features(
                entity_df=entity_df,
                features=features,
                full_feature_names=full_feature_names
            ).to_df()

            logger.info(f"✅ Retrieved historical features: {training_df.shape}")
            return training_df

        except Exception as e:
            logger.error(f"❌ Error fetching historical features: {e}")
            raise

    def materialize_incremental(self) -> None:
        """
        Materialize new features to online store (incremental update).
        Run this periodically (e.g., every hour) to keep online store fresh.
        """
        store = self.get_store()

        logger.info("🔄 Running incremental materialization...")

        try:
            store.materialize_incremental(
                end_date=datetime.utcnow()
            )
            logger.info("✅ Incremental materialization completed")

        except Exception as e:
            logger.error(f"❌ Error in materialization: {e}")
            raise


# ========== CLI Interface ==========

def main():
    """CLI for Feast integration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Feast Feature Store Integration for Email Intelligence"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Push command
    push_parser = subparsers.add_parser('push', help='Enrich emails and push to Feast')
    push_parser.add_argument('emails', nargs='+', help='Email addresses to enrich')
    push_parser.add_argument('--skip-commercial', action='store_true',
                            help='Skip commercial APIs')
    push_parser.add_argument('--repo', default='./feature_repo',
                            help='Feast repository path')

    # Get command
    get_parser = subparsers.add_parser('get', help='Get features from online store')
    get_parser.add_argument('emails', nargs='+', help='Email addresses')
    get_parser.add_argument('--repo', default='./feature_repo',
                           help='Feast repository path')

    # Materialize command
    mat_parser = subparsers.add_parser('materialize', help='Materialize features to online store')
    mat_parser.add_argument('--repo', default='./feature_repo',
                           help='Feast repository path')

    args = parser.parse_args()

    feast = FeastFeatureStore(repo_path=args.repo)

    if args.command == 'push':
        # Enrich and push
        df = feast.enrich_to_dataframe(
            emails=args.emails,
            skip_commercial=args.skip_commercial
        )
        feast.push_features(df)
        print(f"\n✅ Pushed {len(df)} email features to Feast")

    elif args.command == 'get':
        # Get online features
        features_df = feast.get_online_features(emails=args.emails)
        print("\n📊 Online Features:")
        print(features_df.to_string())

    elif args.command == 'materialize':
        # Materialize to online store
        feast.materialize_incremental()
        print("\n✅ Materialization completed")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
