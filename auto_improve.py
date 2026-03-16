#!/usr/bin/env python3
"""
Auto-Improvement System
Continuously monitors, discovers, and improves the email intelligence pipeline

This system:
1. Discovers new data sources and APIs
2. Analyzes enrichment data to find new feature opportunities
3. Monitors API health and changes
4. Suggests improvements and optimizations
5. Auto-updates documentation

Run:
    python auto_improve.py discover    # Find new sources
    python auto_improve.py analyze     # Analyze data for patterns
    python auto_improve.py health      # Check system health
    python auto_improve.py optimize    # Suggest optimizations

Version: 5.0.0
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceDiscovery:
    """
    Discover new data sources and APIs that could enrich email data.
    """

    DISCOVERY_SOURCES = {
        "api_directories": [
            "https://www.programmableweb.com/category/email/api",
            "https://rapidapi.com/search/email",
            "https://apilist.fun/api-search?q=email",
        ],
        "github_topics": [
            "email-verification",
            "email-validation",
            "osint-tools",
            "threat-intelligence",
        ],
        "categories": [
            "email_verification",
            "reputation_apis",
            "social_media_apis",
            "data_enrichment",
            "fraud_detection",
        ]
    }

    def __init__(self):
        self.discovered_sources = []
        self.report_path = "discoveries/sources_report.json"

    def discover_github_projects(self, topic: str) -> List[Dict[str, Any]]:
        """
        Search GitHub for relevant open-source projects.
        """
        logger.info(f"🔍 Searching GitHub for topic: {topic}")

        try:
            url = f"https://api.github.com/search/repositories"
            params = {
                "q": f"topic:{topic} language:python stars:>50",
                "sort": "stars",
                "order": "desc",
                "per_page": 10
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            repos = response.json().get('items', [])

            discoveries = []
            for repo in repos:
                discoveries.append({
                    "name": repo['name'],
                    "url": repo['html_url'],
                    "description": repo['description'],
                    "stars": repo['stargazers_count'],
                    "updated_at": repo['updated_at'],
                    "topics": repo.get('topics', []),
                    "language": repo['language'],
                    "type": "github_repo"
                })

            logger.info(f"   Found {len(discoveries)} relevant repositories")
            return discoveries

        except Exception as e:
            logger.error(f"   Error discovering GitHub projects: {e}")
            return []

    def discover_new_apis(self) -> List[Dict[str, Any]]:
        """
        Discover new APIs that could be integrated.
        """
        logger.info("🔍 Discovering new APIs...")

        # In production, this would scrape API directories
        # For now, return known candidates

        api_candidates = [
            {
                "name": "FullContact",
                "url": "https://www.fullcontact.com/developer/",
                "category": "identity_resolution",
                "features_potential": ["social_profiles", "demographics", "employer"],
                "cost": "$99/month",
                "status": "candidate"
            },
            {
                "name": "Pipl",
                "url": "https://pipl.com/api/",
                "category": "identity_search",
                "features_potential": ["phone", "address", "work_history"],
                "cost": "$0.10/query",
                "status": "candidate"
            },
            {
                "name": "Have I Been Pwned (Pwned Passwords)",
                "url": "https://haveibeenpwned.com/API/v3",
                "category": "security",
                "features_potential": ["password_hash_check", "domain_breach_search"],
                "cost": "$3.50/month",
                "status": "candidate"
            },
            {
                "name": "EmailListVerify",
                "url": "https://www.emaillistverify.com/",
                "category": "verification",
                "features_potential": ["catch_all_detection", "role_account"],
                "cost": "$4/1000 verifications",
                "status": "candidate"
            },
            {
                "name": "Abstract API",
                "url": "https://www.abstractapi.com/email-validation-api",
                "category": "validation",
                "features_potential": ["smtp_check", "quality_score"],
                "cost": "100/month free",
                "status": "candidate"
            }
        ]

        return api_candidates

    def run_discovery(self) -> Dict[str, Any]:
        """
        Run full discovery process.
        """
        logger.info("🚀 Starting source discovery process...")

        discoveries = {
            "timestamp": datetime.now().isoformat(),
            "github_repos": [],
            "api_candidates": [],
            "summary": {}
        }

        # Discover GitHub projects
        for topic in self.DISCOVERY_SOURCES["github_topics"]:
            repos = self.discover_github_projects(topic)
            discoveries["github_repos"].extend(repos)

        # Discover new APIs
        apis = self.discover_new_apis()
        discoveries["api_candidates"] = apis

        # Generate summary
        discoveries["summary"] = {
            "total_github_repos": len(discoveries["github_repos"]),
            "total_api_candidates": len(discoveries["api_candidates"]),
            "free_apis": len([a for a in apis if "free" in a.get("cost", "").lower()]),
            "potential_new_features": sum(
                len(a.get("features_potential", [])) for a in apis
            )
        }

        # Save report
        self._save_report(discoveries)

        return discoveries

    def _save_report(self, discoveries: Dict[str, Any]):
        """Save discovery report to file."""
        import os
        os.makedirs("discoveries", exist_ok=True)

        with open(self.report_path, 'w') as f:
            json.dump(discoveries, f, indent=2)

        logger.info(f"✅ Discovery report saved to {self.report_path}")


class FeatureAnalyzer:
    """
    Analyze enrichment data to discover new feature opportunities.
    """

    def __init__(self):
        self.analysis_results = {}

    def analyze_data_patterns(self, enrichment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze enrichment results to find patterns and opportunities.
        """
        logger.info("📊 Analyzing enrichment data for patterns...")

        if not enrichment_results:
            logger.warning("No enrichment data provided")
            return {}

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "sample_size": len(enrichment_results),
            "patterns": {},
            "feature_opportunities": [],
            "data_quality": {}
        }

        # Analyze feature coverage
        feature_coverage = {}
        for result in enrichment_results:
            features = result.get('features', {}).get('all_features', {})
            for key, value in features.items():
                if key not in feature_coverage:
                    feature_coverage[key] = {"populated": 0, "null": 0, "total": 0}

                feature_coverage[key]["total"] += 1
                if value is not None and value != "" and value != 0:
                    feature_coverage[key]["populated"] += 1
                else:
                    feature_coverage[key]["null"] += 1

        # Calculate coverage percentages
        for feature, stats in feature_coverage.items():
            stats["coverage_pct"] = (stats["populated"] / stats["total"]) * 100

        # Find low-coverage features (opportunities for improvement)
        low_coverage = {
            k: v for k, v in feature_coverage.items()
            if v["coverage_pct"] < 50
        }

        analysis["data_quality"]["feature_coverage"] = feature_coverage
        analysis["data_quality"]["low_coverage_features"] = len(low_coverage)

        # Suggest new derived features
        analysis["feature_opportunities"] = self._suggest_derived_features(enrichment_results)

        return analysis

    def _suggest_derived_features(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Suggest new derived features based on existing data.
        """
        suggestions = []

        # Example: If we have github_repos and github_followers, suggest influence ratio
        suggestions.append({
            "name": "github_influence_ratio",
            "formula": "github_followers / (github_repos + 1)",
            "description": "Ratio of followers to repositories (influence metric)",
            "category": "derived_social"
        })

        suggestions.append({
            "name": "email_age_risk_score",
            "formula": "breach_count * (1 / account_age_years)",
            "description": "Risk score combining breaches and account age",
            "category": "derived_security"
        })

        suggestions.append({
            "name": "professional_consistency_score",
            "formula": "avg(is_corporate, is_professional_format, has_linkedin, !is_free_provider)",
            "description": "Composite professional email indicator",
            "category": "derived_identity"
        })

        suggestions.append({
            "name": "bot_likelihood_composite",
            "formula": "avg(is_disposable, !has_github, !has_gravatar, suspicious)",
            "description": "Combined bot detection score",
            "category": "derived_security"
        })

        return suggestions

    def find_correlation_opportunities(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find features that could be correlated to create new insights.
        """
        logger.info("🔗 Finding correlation opportunities...")

        # This would analyze correlations between features
        # For example: trust_score vs github_repos correlation

        opportunities = [
            {
                "feature_a": "github_repos",
                "feature_b": "trust_score",
                "hypothesis": "More repos → Higher trust",
                "suggested_action": "Create 'developer_trust_boost' feature"
            },
            {
                "feature_a": "breach_count",
                "feature_b": "engagement_score",
                "hypothesis": "Breached users may have lower engagement",
                "suggested_action": "Flag for re-engagement campaign"
            }
        ]

        return opportunities


class HealthMonitor:
    """
    Monitor system health and API status.
    """

    def __init__(self):
        self.health_report = {}

    def check_api_health(self) -> Dict[str, Any]:
        """
        Check health of all integrated APIs.
        """
        logger.info("🏥 Checking API health...")

        apis_to_check = [
            {
                "name": "GitHub API",
                "endpoint": "https://api.github.com/rate_limit",
                "expected_status": 200
            },
            {
                "name": "HIBP API",
                "endpoint": "https://haveibeenpwned.com/api/v3/breachedaccount/test@example.com",
                "expected_status": [200, 404, 401]  # 401 = needs API key (but API is up)
            },
            {
                "name": "IP API",
                "endpoint": "https://ipapi.co/json/",
                "expected_status": 200
            }
        ]

        health_status = []

        for api in apis_to_check:
            try:
                start_time = datetime.now()
                response = requests.get(api["endpoint"], timeout=5)
                response_time = (datetime.now() - start_time).total_seconds()

                expected = api["expected_status"]
                if isinstance(expected, list):
                    is_healthy = response.status_code in expected
                else:
                    is_healthy = response.status_code == expected

                health_status.append({
                    "name": api["name"],
                    "status": "healthy" if is_healthy else "unhealthy",
                    "response_time_ms": int(response_time * 1000),
                    "status_code": response.status_code
                })

                status_icon = "✅" if is_healthy else "❌"
                logger.info(f"   {status_icon} {api['name']}: {response.status_code} ({response_time*1000:.0f}ms)")

            except Exception as e:
                health_status.append({
                    "name": api["name"],
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"   ❌ {api['name']}: {str(e)}")

        return {
            "timestamp": datetime.now().isoformat(),
            "apis": health_status,
            "summary": {
                "total_apis": len(health_status),
                "healthy": len([a for a in health_status if a["status"] == "healthy"]),
                "unhealthy": len([a for a in health_status if a["status"] != "healthy"])
            }
        }

    def check_dependency_updates(self) -> List[Dict[str, str]]:
        """
        Check for available dependency updates.
        """
        logger.info("📦 Checking for dependency updates...")

        # This would use pip-outdated or similar
        # For demo, return mock data

        outdated = [
            {"package": "requests", "current": "2.31.0", "latest": "2.32.0"},
            {"package": "streamlit", "current": "1.28.0", "latest": "1.30.0"},
        ]

        return outdated


class OptimizationEngine:
    """
    Suggest optimizations and improvements.
    """

    def analyze_performance(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze performance metrics and suggest optimizations.
        """
        logger.info("⚡ Analyzing performance for optimization opportunities...")

        suggestions = []

        # Check cache hit rate
        if "cache_hit_rate" in metrics:
            if metrics["cache_hit_rate"] < 0.7:
                suggestions.append({
                    "type": "performance",
                    "priority": "high",
                    "issue": f"Low cache hit rate: {metrics['cache_hit_rate']:.1%}",
                    "recommendation": "Increase TTL for stable features or pre-warm cache",
                    "estimated_impact": "2-5x speedup"
                })

        # Check API response times
        if "avg_api_response_time" in metrics:
            if metrics["avg_api_response_time"] > 2000:  # 2 seconds
                suggestions.append({
                    "type": "performance",
                    "priority": "medium",
                    "issue": f"Slow API responses: {metrics['avg_api_response_time']}ms",
                    "recommendation": "Implement parallel API calls or add timeout limits",
                    "estimated_impact": "30-50% faster"
                })

        # Check feature count
        if "total_features" in metrics:
            if metrics["total_features"] > 300:
                suggestions.append({
                    "type": "optimization",
                    "priority": "low",
                    "issue": f"High feature count: {metrics['total_features']}",
                    "recommendation": "Use feature selection to reduce dimensionality",
                    "estimated_impact": "Better model performance"
                })

        return suggestions

    def suggest_code_improvements(self) -> List[Dict[str, Any]]:
        """
        Suggest code-level improvements.
        """
        improvements = [
            {
                "file": "full_enrichment.py",
                "type": "async",
                "suggestion": "Convert API calls to async/await for parallel execution",
                "estimated_speedup": "3-5x for multiple sources"
            },
            {
                "file": "enhanced_feature_engineering.py",
                "type": "vectorization",
                "suggestion": "Use numpy vectorization for score calculations",
                "estimated_speedup": "10-20x for batch processing"
            },
            {
                "file": "cache_manager.py",
                "type": "compression",
                "suggestion": "Add compression for cached results (gzip)",
                "estimated_savings": "60-70% memory reduction"
            }
        ]

        return improvements


# ========== CLI Interface ==========

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-Improvement System for Email Intelligence"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Discovery command
    discover_parser = subparsers.add_parser('discover', help='Discover new data sources')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze data patterns')
    analyze_parser.add_argument('--sample-size', type=int, default=100,
                               help='Number of samples to analyze')

    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')

    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Suggest optimizations')

    args = parser.parse_args()

    if args.command == 'discover':
        print("\n🔍 === SOURCE DISCOVERY === \n")
        discovery = SourceDiscovery()
        results = discovery.run_discovery()

        print(f"\n📊 Discovery Summary:")
        print(f"   GitHub Repos: {results['summary']['total_github_repos']}")
        print(f"   API Candidates: {results['summary']['total_api_candidates']}")
        print(f"   Free APIs: {results['summary']['free_apis']}")
        print(f"   Potential New Features: {results['summary']['potential_new_features']}")

        print(f"\n💡 Top API Candidates:")
        for api in results['api_candidates'][:5]:
            print(f"   • {api['name']} - {', '.join(api['features_potential'])}")

    elif args.command == 'analyze':
        print("\n📊 === DATA ANALYSIS ===\n")
        analyzer = FeatureAnalyzer()

        # In production, load actual enrichment results
        print("💡 Suggested New Features:")
        suggestions = analyzer._suggest_derived_features([])
        for suggestion in suggestions:
            print(f"   • {suggestion['name']}: {suggestion['description']}")

    elif args.command == 'health':
        print("\n🏥 === HEALTH CHECK ===\n")
        monitor = HealthMonitor()

        health = monitor.check_api_health()
        print(f"\n📊 Health Summary:")
        print(f"   Total APIs: {health['summary']['total_apis']}")
        print(f"   Healthy: {health['summary']['healthy']} ✅")
        print(f"   Unhealthy: {health['summary']['unhealthy']} ❌")

    elif args.command == 'optimize':
        print("\n⚡ === OPTIMIZATION SUGGESTIONS ===\n")
        optimizer = OptimizationEngine()

        # Mock metrics
        metrics = {
            "cache_hit_rate": 0.65,
            "avg_api_response_time": 2500,
            "total_features": 291
        }

        suggestions = optimizer.analyze_performance(metrics)
        print("📈 Performance Suggestions:")
        for s in suggestions:
            print(f"   [{s['priority'].upper()}] {s['issue']}")
            print(f"       → {s['recommendation']}")
            print(f"       Impact: {s['estimated_impact']}\n")

        improvements = optimizer.suggest_code_improvements()
        print("💻 Code Improvements:")
        for imp in improvements:
            print(f"   • {imp['file']}: {imp['suggestion']}")
            print(f"       Benefit: {imp.get('estimated_speedup', imp.get('estimated_savings'))}\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
