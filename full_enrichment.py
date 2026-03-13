#!/usr/bin/env python3
"""
Full End-to-End Email Enrichment Pipeline (v3.1)

Combines:
1. OSINT data collection (GitHub, Gravatar, HIBP)
2. Commercial API enrichment (Hunter.io, EmailRep.io, Clearbit)
3. Additional sources (WHOIS, IPQualityScore, Twitter, LinkedIn, StackOverflow)
4. Enhanced feature engineering (202 features)

Usage:
    python full_enrichment.py email@example.com
    python full_enrichment.py email@example.com --skip-commercial  # OSINT only
    python full_enrichment.py email@example.com --skip-additional  # Skip WHOIS/IPQS/etc
    python full_enrichment.py email@example.com --output results/

Author: Feature Generation Email
Version: 3.1.0
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Import our modules
try:
    from osint_email_enrichment import EmailOSINT
    from commercial_apis import CommercialAPIsEnricher
    from additional_sources import AdditionalSourcesEnricher
    from enhanced_feature_engineering import EnhancedFeatureEngineer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FullEnrichmentPipeline:
    """
    Complete enrichment pipeline combining all data sources.
    """

    VERSION = "3.1.0"

    def __init__(self, output_dir: str = "results", skip_commercial: bool = False, skip_additional: bool = False):
        """
        Initialize pipeline.

        Args:
            output_dir: Directory to save results
            skip_commercial: Skip commercial APIs (Hunter, EmailRep, Clearbit)
            skip_additional: Skip additional sources (WHOIS, IPQS, Twitter, etc)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.skip_commercial = skip_commercial
        self.skip_additional = skip_additional

        if not skip_commercial:
            self.commercial = CommercialAPIsEnricher()
        else:
            self.commercial = None
            logger.warning("Commercial APIs disabled - will use OSINT data only")

        if not skip_additional:
            self.additional = AdditionalSourcesEnricher()
        else:
            self.additional = None
            logger.warning("Additional sources disabled")

    def enrich_email(self, email: str) -> dict:
        """
        Run full enrichment pipeline for an email.

        Args:
            email: Email address to enrich

        Returns:
            Dictionary with all enrichment data and features
        """
        logger.info(f"🚀 Starting full enrichment for: {email}")

        # Step 1: OSINT Data Collection
        logger.info("📊 Step 1/4: Collecting OSINT data...")
        osint_enricher = EmailOSINT(email)
        osint_data = osint_enricher.enrich()

        # Step 2: Commercial API Enrichment (optional)
        commercial_data = None
        if not self.skip_commercial and self.commercial:
            logger.info("💼 Step 2/4: Enriching with commercial APIs...")
            try:
                commercial_data = self.commercial.enrich_email(email)
            except Exception as e:
                logger.error(f"Commercial API error: {e}")
                logger.warning("Continuing with OSINT data only")

        # Step 3: Additional Sources (optional)
        additional_data = None
        if not self.skip_additional and self.additional:
            logger.info("🌐 Step 3/4: Enriching with additional sources...")
            try:
                additional_data = self.additional.enrich_email(email)
            except Exception as e:
                logger.error(f"Additional sources error: {e}")
                logger.warning("Continuing without additional sources")

        # Step 4: Feature Engineering
        logger.info("🔬 Step 4/4: Generating enhanced features...")
        engineer = EnhancedFeatureEngineer(osint_data, commercial_data, additional_data)
        features = engineer.generate_all_features()
        ml_ready = engineer.to_ml_ready()

        # Compile results
        results = {
            'email': email,
            'pipeline_version': self.VERSION,
            'enrichment_timestamp': datetime.now().isoformat(),
            'data_sources': {
                'osint': osint_data,
                'commercial': commercial_data if commercial_data else {},
                'additional': additional_data if additional_data else {},
            },
            'features': {
                'all_features': features.__dict__,
                'ml_ready': ml_ready,
                'feature_count': len(features.__dict__),
            },
            'summary': self._generate_summary(features, additional_data),
        }

        logger.info("✅ Enrichment completed successfully")
        return results

    def _generate_summary(self, features, additional_data=None) -> dict:
        """Generate human-readable summary of key metrics."""
        summary = {
            'trust_score': features.overall_trust_score,
            'identity_strength': features.identity_strength_score,
            'security_risk': features.security_risk_score,
            'activity_engagement': features.activity_engagement_score,
            'data_quality': features.data_quality_score,
        }

        # Add commercial scores if available
        if hasattr(features, 'hunter_score'):
            summary['hunter_verification'] = features.hunter_score / 100.0
            summary['emailrep_reputation'] = features.emailrep_reputation_score
            summary['clearbit_person_quality'] = features.clearbit_person_score
            summary['clearbit_company_quality'] = features.clearbit_company_score

        # Add additional sources scores if available
        if additional_data:
            summary['domain_age_years'] = additional_data.get('domain_age_years')
            summary['ipqs_fraud_score'] = additional_data.get('ipqs_fraud_score', 0)
            summary['ipqs_overall_score'] = additional_data.get('ipqs_overall_score', 0)
            summary['twitter_followers'] = additional_data.get('twitter_followers_count', 0)
            summary['linkedin_profile_exists'] = additional_data.get('linkedin_profile_exists', False)
            summary['stackoverflow_reputation'] = additional_data.get('stackoverflow_reputation', 0)

        # Risk classification
        trust = features.overall_trust_score
        if trust >= 0.75:
            risk_level = "LOW RISK"
            recommendation = "APPROVE"
        elif trust >= 0.50:
            risk_level = "MEDIUM RISK"
            recommendation = "REVIEW"
        else:
            risk_level = "HIGH RISK"
            recommendation = "REJECT"

        summary['risk_classification'] = {
            'level': risk_level,
            'recommendation': recommendation,
            'trust_score': trust,
        }

        return summary

    def save_results(self, email: str, results: dict) -> str:
        """
        Save results to JSON file.

        Args:
            email: Email address
            results: Enrichment results

        Returns:
            Path to saved file
        """
        filename = f"full_enrichment_{email.replace('@', '_at_')}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"💾 Results saved to: {filepath}")
        return str(filepath)

    def print_summary(self, results: dict):
        """Print human-readable summary to console."""
        email = results['email']
        summary = results['summary']
        features = results['features']['all_features']

        print("\n" + "=" * 60)
        print(f"📧 EMAIL: {email}")
        print("=" * 60)

        # Risk classification
        risk = summary['risk_classification']
        print(f"\n🎯 RISK ASSESSMENT: {risk['level']}")
        print(f"   Recommendation: {risk['recommendation']}")
        print(f"   Trust Score: {risk['trust_score']:.3f}")

        # Core scores
        print(f"\n📊 CORE SCORES:")
        print(f"   Identity Strength:    {summary['identity_strength']:.3f}")
        print(f"   Security Risk:        {summary['security_risk']:.3f}")
        print(f"   Activity Engagement:  {summary['activity_engagement']:.3f}")
        print(f"   Data Quality:         {summary['data_quality']:.3f}")

        # Commercial API scores (if available)
        if 'hunter_verification' in summary:
            print(f"\n💼 COMMERCIAL API SCORES:")
            print(f"   Hunter Verification:  {summary['hunter_verification']:.3f}")
            print(f"   EmailRep Reputation:  {summary['emailrep_reputation']:.3f}")
            print(f"   Clearbit Person:      {summary['clearbit_person_quality']:.3f}")
            print(f"   Clearbit Company:     {summary['clearbit_company_quality']:.3f}")

        # Key indicators
        print(f"\n🔍 KEY INDICATORS:")
        print(f"   Account Age: {features.get('account_age_years', 0):.1f} years")
        print(f"   GitHub Repos: {features.get('github_repos', 0)}")
        print(f"   Digital Footprint: {features.get('digital_footprint_count', 0)} platforms")
        print(f"   Known Breaches: {features.get('breach_count', 0)}")

        if features.get('clearbit_company_name'):
            print(f"   Company: {features['clearbit_company_name']}")
            if features.get('clearbit_person_title'):
                print(f"   Job Title: {features['clearbit_person_title']}")

        print(f"\n📈 TOTAL FEATURES GENERATED: {results['features']['feature_count']}")
        print("=" * 60 + "\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Full email enrichment pipeline (OSINT + Commercial APIs + Features)'
    )
    parser.add_argument('email', help='Email address to enrich')
    parser.add_argument(
        '--output',
        default='results',
        help='Output directory for results (default: results/)'
    )
    parser.add_argument(
        '--skip-commercial',
        action='store_true',
        help='Skip commercial APIs (OSINT only)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress summary output'
    )

    args = parser.parse_args()

    # Validate email
    if '@' not in args.email:
        print(f"❌ Invalid email format: {args.email}")
        sys.exit(1)

    # Run pipeline
    try:
        pipeline = FullEnrichmentPipeline(
            output_dir=args.output,
            skip_commercial=args.skip_commercial
        )

        results = pipeline.enrich_email(args.email)
        filepath = pipeline.save_results(args.email, results)

        if not args.quiet:
            pipeline.print_summary(results)

        print(f"\n✅ Success! Full results saved to: {filepath}\n")

    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Pipeline error")
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
