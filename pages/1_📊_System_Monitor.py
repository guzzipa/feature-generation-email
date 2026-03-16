"""
System Monitor Page
Monitor Redis cache, streaming workers, and system health
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="System Monitor",
    page_icon="📊",
    layout="wide"
)

st.title("📊 System Monitor")
st.markdown("Monitor cache performance, streaming workers, and system health")

# Initialize
if 'monitoring_enabled' not in st.session_state:
    st.session_state.monitoring_enabled = False


def check_redis_connection():
    """Check if Redis is available"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        return True, client
    except:
        return False, None


def get_cache_stats(redis_client):
    """Get cache statistics"""
    try:
        info = redis_client.info()
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory_human': info.get('used_memory_human', 'N/A'),
            'total_keys': redis_client.dbsize(),
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0)
        }
    except Exception as e:
        st.error(f"Error getting cache stats: {e}")
        return None


def get_streaming_stats(redis_client):
    """Get streaming statistics"""
    try:
        metrics = redis_client.hgetall('email:enrichment:metrics')
        stream_length = redis_client.xlen('email:enrichment:stream')
        results_length = redis_client.xlen('email:enrichment:results')
        dlq_length = redis_client.xlen('email:enrichment:dlq')

        return {
            'jobs_submitted': int(metrics.get('jobs_submitted', 0)),
            'jobs_completed': int(metrics.get('jobs_completed', 0)),
            'jobs_failed': int(metrics.get('jobs_failed', 0)),
            'pending_jobs': stream_length,
            'results_stored': results_length,
            'failed_jobs_dlq': dlq_length
        }
    except Exception as e:
        return None


# Check Redis connection
redis_available, redis_client = check_redis_connection()

col1, col2 = st.columns([3, 1])

with col1:
    if redis_available:
        st.success("✅ Redis Connected")
    else:
        st.error("❌ Redis Not Available")
        st.info("Start Redis: `brew services start redis` or `redis-server`")

with col2:
    auto_refresh = st.checkbox("Auto Refresh (5s)", value=False)

if auto_refresh:
    time.sleep(5)
    st.rerun()

st.divider()

if redis_available:
    # Cache Statistics
    st.subheader("💾 Cache Statistics")

    cache_stats = get_cache_stats(redis_client)

    if cache_stats:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Keys", cache_stats['total_keys'])

        with col2:
            st.metric("Memory Used", cache_stats['used_memory_human'])

        with col3:
            hits = cache_stats['hits']
            misses = cache_stats['misses']
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            st.metric("Cache Hit Rate", f"{hit_rate:.1f}%")

        with col4:
            st.metric("Connected Clients", cache_stats['connected_clients'])

        # Cache efficiency chart
        if total > 0:
            st.subheader("📈 Cache Efficiency")
            cache_df = pd.DataFrame({
                'Type': ['Hits', 'Misses'],
                'Count': [hits, misses]
            })

            st.bar_chart(cache_df.set_index('Type'))

    st.divider()

    # Streaming Statistics
    st.subheader("🚀 Streaming Workers")

    streaming_stats = get_streaming_stats(redis_client)

    if streaming_stats:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Jobs Submitted",
                streaming_stats['jobs_submitted'],
                help="Total jobs submitted to stream"
            )
            st.metric(
                "Jobs Completed",
                streaming_stats['jobs_completed'],
                help="Successfully processed jobs"
            )

        with col2:
            st.metric(
                "Jobs Failed",
                streaming_stats['jobs_failed'],
                delta=f"-{streaming_stats['jobs_failed']}",
                delta_color="inverse",
                help="Failed jobs in DLQ"
            )
            st.metric(
                "Pending Jobs",
                streaming_stats['pending_jobs'],
                help="Jobs waiting in queue"
            )

        with col3:
            st.metric(
                "Results Stored",
                streaming_stats['results_stored'],
                help="Completed results in Redis"
            )

            # Success rate
            submitted = streaming_stats['jobs_submitted']
            completed = streaming_stats['jobs_completed']
            success_rate = (completed / submitted * 100) if submitted > 0 else 0
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%",
                help="Job completion rate"
            )

        # Worker health
        st.subheader("⚡ Worker Health")

        if streaming_stats['pending_jobs'] > 100:
            st.warning("⚠️ High queue backlog. Consider adding more workers.")
        elif streaming_stats['pending_jobs'] > 0:
            st.info(f"ℹ️ {streaming_stats['pending_jobs']} jobs in queue")
        else:
            st.success("✅ Queue is empty - all caught up!")

    st.divider()

    # Recent Cache Keys
    st.subheader("🔑 Recent Cache Keys")

    try:
        keys = redis_client.keys('result:*')[:10]  # Get first 10 result keys

        if keys:
            key_data = []
            for key in keys:
                ttl = redis_client.ttl(key)
                key_data.append({
                    'Key': key,
                    'TTL (seconds)': ttl if ttl > 0 else 'No expiry',
                    'Type': redis_client.type(key)
                })

            st.dataframe(pd.DataFrame(key_data), use_container_width=True)
        else:
            st.info("No cached results found")

    except Exception as e:
        st.error(f"Error fetching keys: {e}")

    st.divider()

    # Actions
    st.subheader("🔧 Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Clear All Cache"):
            if st.session_state.get('confirm_clear_cache'):
                redis_client.flushall()
                st.success("✅ Cache cleared!")
                st.session_state.confirm_clear_cache = False
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.confirm_clear_cache = True
                st.warning("⚠️ Click again to confirm")

    with col2:
        if st.button("📊 Export Metrics"):
            metrics_data = {
                'cache': cache_stats,
                'streaming': streaming_stats,
                'timestamp': datetime.now().isoformat()
            }
            st.download_button(
                "Download JSON",
                str(metrics_data),
                file_name=f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    with col3:
        if st.button("🔄 Refresh Now"):
            st.rerun()

else:
    st.info("""
    ### Redis is not running

    To enable caching and streaming:

    ```bash
    # Install Redis
    brew install redis  # macOS
    # or
    sudo apt install redis-server  # Linux

    # Start Redis
    brew services start redis  # macOS
    # or
    sudo systemctl start redis  # Linux
    ```
    """)

# System Information
st.divider()
st.subheader("💻 System Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Pipeline Version**: 4.2.0")
    st.markdown("**Total Features**: 291")
    st.markdown("**Deployment**: Streamlit Dashboard")

with col2:
    st.markdown(f"**Current Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"**Redis**: {'Connected' if redis_available else 'Disconnected'}")
