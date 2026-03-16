#!/usr/bin/env python3
"""
Email Intelligence Dashboard
Interactive Streamlit dashboard for email enrichment and feature exploration

Run:
    streamlit run streamlit_app.py

Version: 4.2.0
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import time
from typing import Dict, Any, Optional
import plotly.express as px
import plotly.graph_objects as go

# Import enrichment pipeline
from full_enrichment import EmailEnrichmentPipeline
from enhanced_feature_engineering import EnhancedFeatureEngineer

# Page configuration
st.set_page_config(
    page_title="Email Intelligence Dashboard",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'enrichment_results' not in st.session_state:
        st.session_state.enrichment_results = {}
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = EmailEnrichmentPipeline()


def get_score_color(score: float) -> str:
    """Get color class based on score"""
    if score >= 0.7:
        return "score-high"
    elif score >= 0.4:
        return "score-medium"
    else:
        return "score-low"


def enrich_email(
    email: str,
    ip_address: Optional[str] = None,
    skip_commercial: bool = True
) -> Dict[str, Any]:
    """Enrich email and return results"""
    try:
        pipeline = st.session_state.pipeline

        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("🔍 Validating email format...")
        progress_bar.progress(10)
        time.sleep(0.3)

        status_text.text("📊 Collecting OSINT data...")
        progress_bar.progress(30)

        # Enrich email
        results = pipeline.enrich_email(
            email=email,
            ip_address=ip_address,
            skip_commercial=skip_commercial
        )

        status_text.text("🌐 Enriching with additional sources...")
        progress_bar.progress(60)
        time.sleep(0.3)

        status_text.text("🔬 Generating features...")
        progress_bar.progress(90)
        time.sleep(0.3)

        progress_bar.progress(100)
        status_text.text("✅ Enrichment completed!")
        time.sleep(0.5)

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

        # Add to history
        st.session_state.history.append({
            'email': email,
            'timestamp': datetime.now(),
            'trust_score': results['features']['all_features'].get('trust_score', 0)
        })

        return results

    except Exception as e:
        st.error(f"❌ Error enriching email: {str(e)}")
        return None


def render_summary_metrics(features: Dict[str, Any]):
    """Render summary metrics cards"""
    st.subheader("📊 Summary Scores")

    col1, col2, col3, col4 = st.columns(4)

    trust_score = features.get('trust_score', 0)
    identity_score = features.get('identity_strength_score', 0)
    security_risk = features.get('security_risk_score', 0)
    engagement_score = features.get('engagement_score', 0)

    with col1:
        st.metric(
            "Trust Score",
            f"{trust_score:.2f}",
            delta=None,
            help="Overall trustworthiness (0-1)"
        )
        st.markdown(f"<span class='{get_score_color(trust_score)}'>●</span>",
                   unsafe_allow_html=True)

    with col2:
        st.metric(
            "Identity Strength",
            f"{identity_score:.2f}",
            delta=None,
            help="Profile completeness (0-1)"
        )
        st.markdown(f"<span class='{get_score_color(identity_score)}'>●</span>",
                   unsafe_allow_html=True)

    with col3:
        st.metric(
            "Security Risk",
            f"{security_risk:.2f}",
            delta=None,
            help="Security risk level (0-1, lower is better)"
        )
        st.markdown(f"<span class='{get_score_color(1 - security_risk)}'>●</span>",
                   unsafe_allow_html=True)

    with col4:
        st.metric(
            "Engagement",
            f"{engagement_score:.2f}",
            delta=None,
            help="Activity engagement level (0-1)"
        )
        st.markdown(f"<span class='{get_score_color(engagement_score)}'>●</span>",
                   unsafe_allow_html=True)


def render_feature_breakdown(features: Dict[str, Any]):
    """Render feature breakdown by category"""
    st.subheader("🔍 Feature Breakdown")

    # Define feature categories
    categories = {
        'Identity & Validation': [
            'is_valid_format', 'is_free_provider', 'is_disposable',
            'is_corporate', 'has_name_in_email', 'is_professional_format'
        ],
        'Social & Professional': [
            'has_github', 'github_followers', 'github_repos',
            'has_gravatar', 'social_platforms_count'
        ],
        'Security & Quality': [
            'has_breaches', 'breach_count', 'deliverable',
            'spam_score', 'suspicious', 'blacklisted'
        ],
        'Technical & Geo': [
            'ip_country_code', 'ip_is_proxy', 'ip_is_vpn',
            'connection_type', 'locations_count'
        ]
    }

    tabs = st.tabs(list(categories.keys()))

    for tab, (category, feature_list) in zip(tabs, categories.items()):
        with tab:
            for feature in feature_list:
                if feature in features:
                    value = features[feature]

                    # Format value display
                    if isinstance(value, bool):
                        icon = "✅" if value else "❌"
                        st.write(f"{icon} **{feature.replace('_', ' ').title()}**: {value}")
                    elif isinstance(value, (int, float)):
                        st.write(f"**{feature.replace('_', ' ').title()}**: {value}")
                    else:
                        st.write(f"**{feature.replace('_', ' ').title()}**: {value}")


def render_radar_chart(features: Dict[str, Any]):
    """Render radar chart for key scores"""
    st.subheader("📈 Score Radar Chart")

    scores = {
        'Trust': features.get('trust_score', 0),
        'Identity': features.get('identity_strength_score', 0),
        'Social Proof': features.get('social_proof_score', 0),
        'Professional': features.get('professionalism_score', 0),
        'Developer': features.get('developer_score', 0),
        'Authenticity': features.get('authenticity_score', 0)
    }

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=list(scores.values()),
        theta=list(scores.keys()),
        fill='toself',
        name='Scores'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def render_github_stats(data_sources: Dict[str, Any]):
    """Render GitHub statistics"""
    if 'osint' not in data_sources:
        return

    github_data = data_sources['osint'].get('github', {})

    if not github_data.get('github_found'):
        st.info("ℹ️ No GitHub profile found")
        return

    st.subheader("💻 GitHub Profile")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Public Repos", github_data.get('public_repos', 0))
    with col2:
        st.metric("Followers", github_data.get('followers', 0))
    with col3:
        st.metric("Following", github_data.get('following', 0))
    with col4:
        account_age = github_data.get('account_age_days', 0)
        st.metric("Account Age", f"{account_age // 365}y {(account_age % 365) // 30}m")

    # GitHub activity chart
    if github_data.get('public_repos', 0) > 0:
        st.markdown(f"**Username**: [{github_data.get('username')}]({github_data.get('profile_url')})")
        if github_data.get('bio'):
            st.markdown(f"**Bio**: {github_data.get('bio')}")
        if github_data.get('location'):
            st.markdown(f"**Location**: {github_data.get('location')}")


def render_security_analysis(features: Dict[str, Any], data_sources: Dict[str, Any]):
    """Render security analysis section"""
    st.subheader("🔒 Security Analysis")

    # Security flags
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Email Security")

        is_disposable = features.get('is_disposable', False)
        has_breaches = features.get('has_breaches', False)
        suspicious = features.get('suspicious', False)

        if is_disposable:
            st.warning("⚠️ Disposable email detected")
        else:
            st.success("✅ Not a disposable email")

        if has_breaches:
            breach_count = features.get('breach_count', 0)
            st.error(f"🚨 Found in {breach_count} data breach(es)")
        else:
            st.success("✅ No known breaches")

        if suspicious:
            st.warning("⚠️ Suspicious patterns detected")
        else:
            st.success("✅ No suspicious patterns")

    with col2:
        st.markdown("#### IP Security")

        ip_is_proxy = features.get('ip_is_proxy', False)
        ip_is_vpn = features.get('ip_is_vpn', False)
        ip_is_tor = features.get('ip_is_tor', False)

        if ip_is_proxy:
            st.warning("⚠️ Proxy detected")
        if ip_is_vpn:
            st.info("ℹ️ VPN detected")
        if ip_is_tor:
            st.error("🚨 Tor network detected")

        if not any([ip_is_proxy, ip_is_vpn, ip_is_tor]):
            st.success("✅ Clean IP address")


def render_comparison_mode():
    """Render email comparison mode"""
    st.header("🔄 Compare Emails")

    col1, col2 = st.columns(2)

    with col1:
        email1 = st.text_input("Email 1", key="compare_email1")
        if st.button("Enrich Email 1", key="enrich1"):
            if email1:
                with st.spinner("Enriching..."):
                    results1 = enrich_email(email1, skip_commercial=True)
                    if results1:
                        st.session_state.compare_results_1 = results1

    with col2:
        email2 = st.text_input("Email 2", key="compare_email2")
        if st.button("Enrich Email 2", key="enrich2"):
            if email2:
                with st.spinner("Enriching..."):
                    results2 = enrich_email(email2, skip_commercial=True)
                    if results2:
                        st.session_state.compare_results_2 = results2

    # Show comparison if both enriched
    if 'compare_results_1' in st.session_state and 'compare_results_2' in st.session_state:
        st.subheader("📊 Comparison Results")

        features1 = st.session_state.compare_results_1['features']['all_features']
        features2 = st.session_state.compare_results_2['features']['all_features']

        # Compare key scores
        comparison_metrics = ['trust_score', 'identity_strength_score', 'security_risk_score']

        for metric in comparison_metrics:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{metric.replace('_', ' ').title()}**")
            with col2:
                st.write(f"{features1.get(metric, 0):.2f}")
            with col3:
                st.write(f"{features2.get(metric, 0):.2f}")


def main():
    """Main dashboard application"""
    init_session_state()

    # Header
    st.markdown("<div class='main-header'>📧 Email Intelligence Dashboard</div>",
                unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        mode = st.radio(
            "Mode",
            ["Single Email", "Batch Analysis", "Compare Emails", "History"],
            help="Choose analysis mode"
        )

        st.divider()

        skip_commercial = st.checkbox(
            "Skip Commercial APIs",
            value=True,
            help="Use only free data sources"
        )

        enable_cache = st.checkbox(
            "Enable Cache",
            value=True,
            help="Use Redis caching for faster results"
        )

        st.divider()

        # Stats
        st.metric("Emails Analyzed", len(st.session_state.history))

        if st.button("Clear History"):
            st.session_state.history = []
            st.session_state.enrichment_results = {}
            st.rerun()

    # Main content based on mode
    if mode == "Single Email":
        st.header("🔍 Single Email Analysis")

        col1, col2 = st.columns([3, 1])

        with col1:
            email = st.text_input(
                "Email Address",
                placeholder="user@example.com",
                help="Enter email address to analyze"
            )

        with col2:
            ip_address = st.text_input(
                "IP Address (optional)",
                placeholder="181.45.123.45"
            )

        if st.button("🚀 Analyze Email", type="primary"):
            if email:
                results = enrich_email(
                    email,
                    ip_address if ip_address else None,
                    skip_commercial
                )

                if results:
                    st.session_state.enrichment_results[email] = results

                    # Display results
                    st.success(f"✅ Successfully enriched: {email}")

                    features = results['features']['all_features']
                    data_sources = results['data_sources']

                    # Summary metrics
                    render_summary_metrics(features)

                    # Tabs for detailed analysis
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📊 Overview",
                        "🔍 Features",
                        "💻 GitHub",
                        "🔒 Security",
                        "📄 Raw Data"
                    ])

                    with tab1:
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            render_radar_chart(features)
                        with col2:
                            st.subheader("📋 Quick Facts")
                            st.write(f"**Email**: {email}")
                            st.write(f"**Provider**: {features.get('provider_type', 'Unknown')}")
                            st.write(f"**Valid Format**: {'✅' if features.get('is_valid_format') else '❌'}")
                            st.write(f"**Corporate**: {'✅' if features.get('is_corporate') else '❌'}")
                            st.write(f"**GitHub**: {'✅' if features.get('has_github') else '❌'}")
                            st.write(f"**Gravatar**: {'✅' if features.get('has_gravatar') else '❌'}")

                    with tab2:
                        render_feature_breakdown(features)

                    with tab3:
                        render_github_stats(data_sources)

                    with tab4:
                        render_security_analysis(features, data_sources)

                    with tab5:
                        st.json(results)

                        # Download button
                        json_str = json.dumps(results, indent=2, default=str)
                        st.download_button(
                            "📥 Download JSON",
                            json_str,
                            file_name=f"{email}_enrichment.json",
                            mime="application/json"
                        )
            else:
                st.warning("⚠️ Please enter an email address")

    elif mode == "Compare Emails":
        render_comparison_mode()

    elif mode == "History":
        st.header("📜 Enrichment History")

        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history)
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])

            st.dataframe(
                history_df.sort_values('timestamp', ascending=False),
                use_container_width=True
            )

            # Chart
            fig = px.line(
                history_df,
                x='timestamp',
                y='trust_score',
                markers=True,
                title='Trust Score Over Time'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ No enrichment history yet")

    elif mode == "Batch Analysis":
        st.header("📦 Batch Email Analysis")
        st.info("🚧 Batch mode coming soon! Use the streaming API for batch processing.")

        st.code("""
# Batch processing with streaming
python streaming.py worker --workers 4
python streaming.py submit email1@example.com email2@example.com email3@example.com
        """)


if __name__ == "__main__":
    main()
