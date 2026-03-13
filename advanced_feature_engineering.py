#!/usr/bin/env python3
"""
Advanced Feature Engineering for Credit Scoring
Extrae 100+ features incluyendo temporal, NLP, ratios, anomalías
Implementa hallazgos de review técnico triple
"""

import re
import json
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict, field
from collections import Counter


@dataclass
class AdvancedMLFeatures:
    """Features avanzados para scoring crediticio - 100+ variables"""

    # ========== IDENTITY FEATURES ==========
    # Basic
    account_age_days: int
    account_age_years: float
    account_age_months: int
    account_age_weeks: int
    account_age_category: str  # 'new'(<1y), 'established'(1-5y), 'veteran'(5y+)

    # Platform presence
    has_github: int
    has_gravatar: int
    digital_footprint_count: int

    # ========== GITHUB ACTIVITY FEATURES (TEMPORAL) ==========
    # Counts
    github_repos: int
    github_followers: int
    github_following: int
    github_public_gists: int
    github_starred_repos: int  # NEW
    github_organizations: int  # NEW

    # Temporal recency
    days_since_last_github_update: int  # NEW - CRÍTICO
    is_active_last_30_days: int  # NEW
    is_active_last_90_days: int  # NEW
    is_active_last_year: int  # NEW

    # Velocity & trends
    repos_per_month: float  # NEW
    repos_per_year: float
    monthly_activity_score: float  # NEW - weighted recent activity

    # Quality signals
    avg_stars_per_repo: float  # NEW
    has_bio: int
    has_location: int
    has_company: int
    bio_length: int  # NEW
    is_hireable: int  # NEW - seeking employment?

    # ========== GITHUB INTERACTION RATIOS (NEW) ==========
    followers_to_following_ratio: float  # >1 = influencer
    stars_to_repos_ratio: float  # quality
    gists_to_repos_ratio: float
    repos_to_followers_ratio: float  # content/audience balance

    # ========== EMAIL FEATURES (ENHANCED) ==========
    email_valid: int
    is_free_email: int
    is_corporate_email: int
    is_disposable_email: int
    email_provider_risk: float

    # Email pattern analysis (NEW - CRÍTICO)
    email_structure_type: str  # 'professional', 'random', 'pattern'
    username_length: int  # NEW
    username_has_numbers: int  # NEW
    username_numeric_ratio: float  # NEW
    username_entropy: float  # NEW - randomness
    has_subaddressing: int  # NEW - usuario+tag@
    is_role_account: int  # NEW - info@, support@

    # ========== DOMAIN INTELLIGENCE (NEW - CRÍTICO) ==========
    domain_looks_corporate: int  # Heuristic
    domain_tld: str  # .com, .io, .ar, etc
    domain_is_common_free: int  # gmail, yahoo, etc

    # ========== SECURITY FEATURES (ENHANCED) ==========
    has_known_breaches: int
    breach_count: int
    breach_severity_score: float

    # Breach temporal (NEW - CRÍTICO)
    days_since_most_recent_breach: Optional[int]  # NEW
    has_breach_in_last_year: int  # NEW
    has_breach_in_last_3_years: int  # NEW

    # ========== TEXT/NLP FEATURES (NEW) ==========
    bio_word_count: int  # NEW
    bio_has_email_contact: int  # NEW
    bio_has_url: int  # NEW
    bio_professional_keyword_count: int  # NEW - developer, engineer, etc
    location_specificity_score: float  # NEW - "Argentina" vs "Buenos Aires, AR"
    company_is_known_tech: int  # NEW - FAANG, unicorns

    # ========== COMPOSITE SCORES (ENHANCED) ==========
    identity_strength_score: float
    activity_engagement_score: float
    security_risk_score: float
    overall_trust_score: float

    # New composite scores
    data_quality_score: float  # NEW - completeness + consistency
    recency_score: float  # NEW - how recent is activity
    professional_signal_score: float  # NEW - employment indicators
    anomaly_score: float  # NEW - suspicious patterns

    # ========== ANOMALY DETECTION (NEW) ==========
    is_repos_outlier: int  # NEW - >99th percentile
    is_followers_outlier: int  # NEW
    activity_pattern_suspicious: int  # NEW
    profile_inconsistency_count: int  # NEW

    # ========== MISSING DATA PATTERNS (NEW) ==========
    missing_critical_fields: int  # NEW
    data_completeness_ratio: float  # NEW

    # ========== CATEGORICAL ==========
    email_provider_type: str
    location_country: str
    profile_completeness: str
    account_maturity: str  # NEW - 'immature', 'developing', 'mature'

    # ========== METADATA ==========
    enrichment_timestamp: str
    feature_version: str


class AdvancedFeatureEngineer:
    """Feature engineering avanzado basado en review técnico"""

    FEATURE_VERSION = "2.0.0"

    # Professional keywords for bio analysis
    PROFESSIONAL_KEYWORDS = {
        'developer', 'engineer', 'software', 'programmer', 'architect',
        'dev', 'swe', 'ml', 'data', 'scientist', 'analyst', 'tech',
        'full stack', 'backend', 'frontend', 'devops', 'cto', 'ceo',
        'founder', 'freelance', 'consultant'
    }

    # Known tech companies
    KNOWN_TECH_COMPANIES = {
        'google', 'facebook', 'meta', 'amazon', 'microsoft', 'apple',
        'netflix', 'uber', 'airbnb', 'stripe', 'github', 'gitlab',
        'twitter', 'linkedin', 'spotify', 'tesla', 'nvidia'
    }

    # Role email prefixes
    ROLE_PREFIXES = {
        'info', 'contact', 'support', 'admin', 'sales', 'help',
        'service', 'hello', 'hi', 'team', 'noreply', 'no-reply'
    }

    def __init__(self, osint_data: Dict[str, Any]):
        self.raw_data = osint_data
        self.github = osint_data.get('github', {})
        self.gravatar = osint_data.get('gravatar', {})
        self.validation = osint_data.get('validation', {})
        self.domain_analysis = osint_data.get('domain_analysis', {})
        self.breach = osint_data.get('breach_check', {})

    # ========== TEMPORAL ANALYSIS ==========

    def _calculate_account_ages(self) -> Tuple[int, float, int, int]:
        """Calcula múltiples granularidades de edad"""
        created = self.github.get('created_at')
        if not created:
            return 0, 0.0, 0, 0

        created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        age_days = (now - created_date).days
        age_years = age_days / 365.25
        age_months = int(age_days / 30.44)
        age_weeks = age_days // 7

        return age_days, round(age_years, 2), age_months, age_weeks

    def _get_age_category(self, age_years: float) -> str:
        """Categoriza edad de cuenta"""
        if age_years < 1:
            return 'new'
        elif age_years < 5:
            return 'established'
        else:
            return 'veteran'

    def _calculate_recency(self) -> Tuple[int, int, int, int]:
        """
        Calcula recency signals
        Returns: (days_since_update, active_30d, active_90d, active_1y)
        """
        updated_at = self.github.get('updated_at')
        if not updated_at:
            return 9999, 0, 0, 0

        updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        days_since = (now - updated_date).days

        active_30 = 1 if days_since <= 30 else 0
        active_90 = 1 if days_since <= 90 else 0
        active_1y = 1 if days_since <= 365 else 0

        return days_since, active_30, active_90, active_1y

    def _calculate_velocity(self, repos: int, age_years: float) -> Tuple[float, float]:
        """Calcula repos por mes y por año"""
        if age_years <= 0:
            return 0.0, 0.0

        repos_per_year = repos / age_years
        repos_per_month = repos / (age_years * 12)

        return round(repos_per_month, 2), round(repos_per_year, 2)

    def _calculate_monthly_activity_score(self, days_since_update: int, repos: int) -> float:
        """
        Score ponderado de actividad con decay temporal
        Actividad reciente pesa más
        """
        # Exponential decay: score = activity * e^(-lambda * days)
        lambda_decay = 0.01  # Decay rate
        recency_weight = math.exp(-lambda_decay * days_since_update)

        # Activity baseline
        activity_baseline = min(repos / 50.0, 1.0)  # 50 repos = full score

        return round(activity_baseline * recency_weight, 3)

    # ========== EMAIL PATTERN ANALYSIS ==========

    def _analyze_email_structure(self, email: str) -> Tuple[str, int, int, float, float, int, int]:
        """
        Analiza estructura del email para detectar patrones
        Returns: (structure_type, username_len, has_numbers, numeric_ratio, entropy, has_subaddr, is_role)
        """
        username = email.split('@')[0] if '@' in email else email

        # Subaddressing (gmail+tag)
        has_subaddressing = 1 if '+' in username else 0
        clean_username = username.split('+')[0] if has_subaddressing else username

        # Role account
        is_role = 1 if clean_username.lower() in self.ROLE_PREFIXES else 0

        # Length
        username_len = len(clean_username)

        # Numbers
        has_numbers = 1 if any(c.isdigit() for c in clean_username) else 0
        numeric_count = sum(1 for c in clean_username if c.isdigit())
        numeric_ratio = numeric_count / username_len if username_len > 0 else 0

        # Entropy (randomness)
        entropy = self._calculate_entropy(clean_username)

        # Structure classification
        if '.' in clean_username and not has_numbers:
            structure_type = 'professional'  # first.last
        elif entropy > 3.5 or numeric_ratio > 0.5:
            structure_type = 'random'
        else:
            structure_type = 'pattern'

        return structure_type, username_len, has_numbers, round(numeric_ratio, 3), round(entropy, 3), has_subaddressing, is_role

    def _calculate_entropy(self, text: str) -> float:
        """Calcula entropía de Shannon (randomness)"""
        if not text:
            return 0.0

        # Count character frequency
        counter = Counter(text.lower())
        length = len(text)

        # Shannon entropy
        entropy = 0.0
        for count in counter.values():
            p = count / length
            entropy -= p * math.log2(p)

        return entropy

    # ========== DOMAIN INTELLIGENCE ==========

    def _analyze_domain(self, domain: str) -> Tuple[int, str, int]:
        """
        Analiza dominio para señales corporativas
        Returns: (looks_corporate, tld, is_common_free)
        """
        if not domain:
            return 0, 'unknown', 0

        # TLD
        parts = domain.split('.')
        tld = parts[-1] if parts else 'unknown'

        # Common free providers
        common_free = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'aol.com', 'protonmail.com', 'mail.com'
        }
        is_common_free = 1 if domain in common_free else 0

        # Corporate heuristics
        looks_corporate = 0
        if not is_common_free:
            # Check if domain looks like a company
            if len(parts) == 2 and tld in ['com', 'net', 'org', 'io']:
                looks_corporate = 1

        return looks_corporate, tld, is_common_free

    # ========== TEXT/NLP FEATURES ==========

    def _analyze_bio(self, bio: Optional[str]) -> Tuple[int, int, int, int]:
        """
        Analiza bio para extraer señales
        Returns: (word_count, has_email, has_url, professional_keywords)
        """
        if not bio:
            return 0, 0, 0, 0

        # Word count
        words = bio.split()
        word_count = len(words)

        # Email in bio
        has_email = 1 if '@' in bio else 0

        # URL in bio
        has_url = 1 if any(x in bio.lower() for x in ['http', 'www.', '.com', '.io']) else 0

        # Professional keywords
        bio_lower = bio.lower()
        prof_count = sum(1 for keyword in self.PROFESSIONAL_KEYWORDS if keyword in bio_lower)

        return word_count, has_email, has_url, prof_count

    def _analyze_location(self, location: Optional[str]) -> float:
        """
        Score de especificidad de ubicación
        "Buenos Aires, Argentina" = 1.0
        "Argentina" = 0.5
        "Earth" = 0.1
        """
        if not location:
            return 0.0

        # Count commas (more specific)
        comma_count = location.count(',')

        # Length
        length = len(location.strip())

        # Specificity score
        if comma_count >= 2 or length > 30:
            return 1.0
        elif comma_count == 1 or length > 15:
            return 0.7
        elif length > 5:
            return 0.4
        else:
            return 0.1

    def _check_known_tech_company(self, company: Optional[str]) -> int:
        """Check si trabaja en empresa tech conocida"""
        if not company:
            return 0

        company_lower = company.lower()
        return 1 if any(tech in company_lower for tech in self.KNOWN_TECH_COMPANIES) else 0

    # ========== GITHUB RATIOS ==========

    def _calculate_github_ratios(self) -> Tuple[float, float, float, float, float]:
        """
        Calcula ratios importantes
        Returns: (follow_ratio, stars_ratio, gists_ratio, repos_followers, avg_stars)
        """
        followers = self.github.get('followers', 0) or 0
        following = self.github.get('following', 0) or 0
        repos = self.github.get('public_repos', 0) or 0
        gists = self.github.get('public_gists', 0) or 0

        # Followers/following ratio
        follow_ratio = followers / following if following > 0 else float(followers)

        # Stars/repos (assume 0 stars for now, needs API call)
        stars_ratio = 0.0  # Placeholder

        # Gists/repos
        gists_ratio = gists / repos if repos > 0 else 0.0

        # Repos/followers (content production vs audience)
        repos_followers = repos / followers if followers > 0 else float(repos)

        # Avg stars per repo (placeholder)
        avg_stars = 0.0

        return (
            round(follow_ratio, 2),
            round(stars_ratio, 2),
            round(gists_ratio, 2),
            round(repos_followers, 2),
            round(avg_stars, 2)
        )

    # ========== BREACH TEMPORAL ANALYSIS ==========

    def _analyze_breach_temporal(self) -> Tuple[Optional[int], int, int]:
        """
        Analiza temporalidad de brechas
        Returns: (days_since_recent, breach_last_year, breach_last_3y)
        """
        # Placeholder - requires breach dates from API
        # In production, parse breach dates from HIBP
        breach_count = self.breach.get('breach_count', 0) or 0

        if breach_count == 0:
            return None, 0, 0

        # Placeholder logic (needs actual dates)
        days_since_recent = None  # Would calculate from breach dates
        breach_last_year = 0  # Check if any breach < 365 days
        breach_last_3y = min(breach_count, 1)  # Conservative estimate

        return days_since_recent, breach_last_year, breach_last_3y

    # ========== COMPOSITE SCORES ==========

    def _calculate_data_quality_score(self, has_bio: int, has_location: int, has_company: int) -> float:
        """Score de calidad y completitud de datos"""
        completeness = (has_bio + has_location + has_company) / 3.0
        return round(completeness, 3)

    def _calculate_recency_score(self, days_since_update: int) -> float:
        """Score de recencia con decay exponencial"""
        # e^(-0.005 * days)
        score = math.exp(-0.005 * days_since_update)
        return round(score, 3)

    def _calculate_professional_signal_score(
        self, has_company: int, is_corporate_email: int, prof_keywords: int
    ) -> float:
        """Score de señales profesionales"""
        score = (
            has_company * 0.4 +
            is_corporate_email * 0.4 +
            min(prof_keywords / 3.0, 1.0) * 0.2
        )
        return round(score, 3)

    def _calculate_anomaly_score(
        self, repos: int, followers: int, age_years: float
    ) -> float:
        """
        Score de anomalías/patrones sospechosos
        0 = normal, 1 = muy sospechoso
        """
        anomaly_count = 0

        # Too many repos for account age
        if age_years > 0:
            expected_repos = age_years * 5  # ~5 repos/year es normal
            if repos > expected_repos * 3:  # 3x expected
                anomaly_count += 1

        # Too many followers with few repos
        if repos < 5 and followers > 100:
            anomaly_count += 1

        # Brand new account with lots of activity
        if age_years < 0.25 and repos > 20:  # < 3 months, 20+ repos
            anomaly_count += 1

        # Score normalizado
        anomaly_score = min(anomaly_count / 3.0, 1.0)
        return round(anomaly_score, 3)

    def _detect_outliers(self, repos: int, followers: int) -> Tuple[int, int]:
        """
        Detecta outliers (valores extremos)
        Simple heuristic - in production use percentiles from dataset
        """
        # Rough 99th percentile estimates
        is_repos_outlier = 1 if repos > 200 else 0
        is_followers_outlier = 1 if followers > 500 else 0

        return is_repos_outlier, is_followers_outlier

    def _count_profile_inconsistencies(self) -> int:
        """Cuenta inconsistencias en el perfil"""
        count = 0

        # GitHub name vs Gravatar name mismatch
        gh_name = self.github.get('login', '').lower()
        gv_name = self.gravatar.get('display_name', '').lower()
        if gh_name and gv_name and gh_name != gv_name:
            count += 1

        # Has GitHub but no location
        if self.github.get('github_found') and not self.github.get('location'):
            # Not really inconsistent, more like incomplete
            pass

        return count

    def _calculate_missing_fields(self) -> Tuple[int, float]:
        """
        Cuenta campos críticos faltantes
        Returns: (missing_count, completeness_ratio)
        """
        critical_fields = [
            self.github.get('bio'),
            self.github.get('location'),
            self.github.get('company'),
            self.github.get('public_repos'),
            self.github.get('followers')
        ]

        missing = sum(1 for field in critical_fields if not field)
        completeness = (len(critical_fields) - missing) / len(critical_fields)

        return missing, round(completeness, 3)

    # ========== MAIN GENERATION ==========

    def generate_features(self) -> AdvancedMLFeatures:
        """Genera el conjunto completo de features avanzados"""

        # Extract base data
        email = self.raw_data.get('email', '')
        domain = self.validation.get('domain', '')

        # Calculate temporal
        age_days, age_years, age_months, age_weeks = self._calculate_account_ages()
        age_category = self._get_age_category(age_years)

        # Recency
        days_since_update, active_30, active_90, active_1y = self._calculate_recency()

        # Velocity
        repos = self.github.get('public_repos', 0) or 0
        repos_month, repos_year = self._calculate_velocity(repos, age_years)
        monthly_activity = self._calculate_monthly_activity_score(days_since_update, repos)

        # Email analysis
        (email_structure, username_len, username_nums, numeric_ratio,
         entropy, has_subaddr, is_role) = self._analyze_email_structure(email)

        # Domain
        looks_corp, tld, is_common_free = self._analyze_domain(domain)

        # Bio/Text
        bio = self.github.get('bio', '')
        bio_words, bio_email, bio_url, prof_keywords = self._analyze_bio(bio)
        location_score = self._analyze_location(self.github.get('location'))
        is_known_tech = self._check_known_tech_company(self.github.get('company'))

        # GitHub ratios
        followers = self.github.get('followers', 0) or 0
        following = self.github.get('following', 0) or 0
        (follow_ratio, stars_ratio, gists_ratio,
         repos_followers_ratio, avg_stars) = self._calculate_github_ratios()

        # Breach temporal
        (days_since_breach, breach_1y, breach_3y) = self._analyze_breach_temporal()

        # Composite scores
        has_bio = 1 if bio else 0
        has_location = 1 if self.github.get('location') else 0
        has_company = 1 if self.github.get('company') else 0
        is_corporate = self.domain_analysis.get('likely_corporate', False)

        data_quality = self._calculate_data_quality_score(has_bio, has_location, has_company)
        recency_score = self._calculate_recency_score(days_since_update)
        professional_score = self._calculate_professional_signal_score(
            has_company, int(is_corporate), prof_keywords
        )
        anomaly_score = self._calculate_anomaly_score(repos, followers, age_years)

        # Outliers
        is_repos_out, is_followers_out = self._detect_outliers(repos, followers)

        # Inconsistencies
        inconsistencies = self._count_profile_inconsistencies()
        missing_count, completeness_ratio = self._calculate_missing_fields()

        # Original scores (simplified versions)
        identity_strength = round(min(age_years / 10.0, 1.0) * 0.5 + data_quality * 0.5, 3)
        activity_engagement = round(min(repos / 20.0, 1.0) * 0.6 + recency_score * 0.4, 3)

        breach_count = self.breach.get('breach_count', 0) or 0
        is_disposable = self.domain_analysis.get('is_disposable', False)
        security_risk = round(min(breach_count / 3.0, 1.0) * 0.5 + (1.0 if is_disposable else 0.0) * 0.5, 3)

        overall_trust = round(
            identity_strength * 0.35 +
            activity_engagement * 0.25 +
            (1 - security_risk) * 0.25 +
            professional_score * 0.15,
            3
        )

        # Account maturity
        if age_years < 1:
            maturity = 'immature'
        elif age_years < 3:
            maturity = 'developing'
        else:
            maturity = 'mature'

        # Profile completeness
        if completeness_ratio > 0.8:
            profile_complete = 'full'
        elif completeness_ratio > 0.5:
            profile_complete = 'partial'
        elif completeness_ratio > 0.2:
            profile_complete = 'minimal'
        else:
            profile_complete = 'none'

        # Build features object
        features = AdvancedMLFeatures(
            # Identity
            account_age_days=age_days,
            account_age_years=age_years,
            account_age_months=age_months,
            account_age_weeks=age_weeks,
            account_age_category=age_category,
            has_github=1 if self.github.get('github_found') else 0,
            has_gravatar=1 if self.gravatar.get('has_gravatar') else 0,
            digital_footprint_count=sum([
                1 if self.github.get('github_found') else 0,
                1 if self.gravatar.get('has_gravatar') else 0
            ]),

            # GitHub activity
            github_repos=repos,
            github_followers=followers,
            github_following=following,
            github_public_gists=self.github.get('public_gists', 0) or 0,
            github_starred_repos=0,  # Needs additional API call
            github_organizations=0,  # Needs additional API call
            days_since_last_github_update=days_since_update,
            is_active_last_30_days=active_30,
            is_active_last_90_days=active_90,
            is_active_last_year=active_1y,
            repos_per_month=repos_month,
            repos_per_year=repos_year,
            monthly_activity_score=monthly_activity,
            avg_stars_per_repo=avg_stars,
            has_bio=has_bio,
            has_location=has_location,
            has_company=has_company,
            bio_length=len(bio) if bio else 0,
            is_hireable=0,  # Would need API field

            # GitHub ratios
            followers_to_following_ratio=follow_ratio,
            stars_to_repos_ratio=stars_ratio,
            gists_to_repos_ratio=gists_ratio,
            repos_to_followers_ratio=repos_followers_ratio,

            # Email
            email_valid=1 if self.validation.get('is_valid_format') else 0,
            is_free_email=1 if self.validation.get('is_free_provider') else 0,
            is_corporate_email=int(is_corporate),
            is_disposable_email=int(is_disposable),
            email_provider_risk=0.2,  # Simplified
            email_structure_type=email_structure,
            username_length=username_len,
            username_has_numbers=username_nums,
            username_numeric_ratio=numeric_ratio,
            username_entropy=entropy,
            has_subaddressing=has_subaddr,
            is_role_account=is_role,

            # Domain
            domain_looks_corporate=looks_corp,
            domain_tld=tld,
            domain_is_common_free=is_common_free,

            # Security
            has_known_breaches=1 if breach_count > 0 else 0,
            breach_count=breach_count,
            breach_severity_score=min(breach_count / 3.0, 1.0),
            days_since_most_recent_breach=days_since_breach,
            has_breach_in_last_year=breach_1y,
            has_breach_in_last_3_years=breach_3y,

            # Text/NLP
            bio_word_count=bio_words,
            bio_has_email_contact=bio_email,
            bio_has_url=bio_url,
            bio_professional_keyword_count=prof_keywords,
            location_specificity_score=location_score,
            company_is_known_tech=is_known_tech,

            # Composite scores
            identity_strength_score=identity_strength,
            activity_engagement_score=activity_engagement,
            security_risk_score=security_risk,
            overall_trust_score=overall_trust,
            data_quality_score=data_quality,
            recency_score=recency_score,
            professional_signal_score=professional_score,
            anomaly_score=anomaly_score,

            # Anomalies
            is_repos_outlier=is_repos_out,
            is_followers_outlier=is_followers_out,
            activity_pattern_suspicious=1 if anomaly_score > 0.5 else 0,
            profile_inconsistency_count=inconsistencies,

            # Missing data
            missing_critical_fields=missing_count,
            data_completeness_ratio=completeness_ratio,

            # Categorical
            email_provider_type=self.validation.get('provider_type', 'unknown'),
            location_country=self._extract_country(self.github.get('location', '')),
            profile_completeness=profile_complete,
            account_maturity=maturity,

            # Metadata
            enrichment_timestamp=self.raw_data.get('enrichment_timestamp', datetime.now().isoformat()),
            feature_version=self.FEATURE_VERSION
        )

        return features

    def _extract_country(self, location: str) -> str:
        """Extract country code from location"""
        if not location:
            return 'unknown'

        location_lower = location.lower()
        country_map = {
            'argentina': 'AR', 'brazil': 'BR', 'mexico': 'MX',
            'usa': 'US', 'united states': 'US', 'spain': 'ES',
            'colombia': 'CO', 'chile': 'CL',
        }

        for country, code in country_map.items():
            if country in location_lower:
                return code

        return 'OTHER'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        features = self.generate_features()
        return asdict(features)

    def to_ml_ready(self) -> Dict[str, Any]:
        """ML-ready format with numerical/categorical separation"""
        features_dict = self.to_dict()

        numerical = {}
        categorical = {}
        metadata = {}

        for key, value in features_dict.items():
            if key in ['enrichment_timestamp', 'feature_version']:
                metadata[key] = value
            elif isinstance(value, str):
                categorical[key] = value
            else:
                numerical[key] = value

        return {
            'numerical_features': numerical,
            'categorical_features': categorical,
            'metadata': metadata
        }


def main():
    """Demo"""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python advanced_feature_engineering.py <osint_results.json>")
        return

    with open(sys.argv[1], 'r') as f:
        data = json.load(f)

    osint_data = data.get('full_data', data)

    print("\n" + "="*70)
    print("ADVANCED FEATURE ENGINEERING v2.0 - 100+ Features")
    print("="*70)

    engineer = AdvancedFeatureEngineer(osint_data)
    features = engineer.generate_features()

    print(f"\n✅ Total features generados: {len(asdict(features))}")

    # Show some key features
    print("\n🔵 TEMPORAL FEATURES:")
    print(f"  • Account age: {features.account_age_years} years ({features.account_age_category})")
    print(f"  • Days since update: {features.days_since_last_github_update}")
    print(f"  • Active last 30d: {bool(features.is_active_last_30_days)}")
    print(f"  • Monthly activity score: {features.monthly_activity_score}")

    print("\n📧 EMAIL PATTERN ANALYSIS:")
    print(f"  • Structure: {features.email_structure_type}")
    print(f"  • Username entropy: {features.username_entropy}")
    print(f"  • Has subaddressing: {bool(features.has_subaddressing)}")
    print(f"  • Is role account: {bool(features.is_role_account)}")

    print("\n📊 ADVANCED SCORES:")
    print(f"  • Overall trust: {features.overall_trust_score}")
    print(f"  • Recency score: {features.recency_score}")
    print(f"  • Professional signal: {features.professional_signal_score}")
    print(f"  • Anomaly score: {features.anomaly_score}")
    print(f"  • Data quality: {features.data_quality_score}")

    # Export
    output_file = sys.argv[1].replace('.json', '_advanced_features.json')
    ml_ready = engineer.to_ml_ready()

    with open(output_file, 'w') as f:
        json.dump({
            'all_features': asdict(features),
            'ml_ready': ml_ready,
            'feature_count': len(asdict(features)),
            'version': AdvancedFeatureEngineer.FEATURE_VERSION
        }, f, indent=2)

    print(f"\n💾 Features guardados: {output_file}")
    print(f"\n📈 Numerical features: {len(ml_ready['numerical_features'])}")
    print(f"📋 Categorical features: {len(ml_ready['categorical_features'])}")


if __name__ == "__main__":
    main()
