"""
Interactive Incident War Room & Autonomous SRE Agent Dashboard.
Built with Streamlit & Plotly.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from data.mock_environment.simulator import MockCloudEnvironment
from src.agent import AutonomousSREAgent


st.set_page_config(
    page_title="Autonomous Incident RCA & SRE Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .trace-card {
        border-left: 4px solid #3b82f6;
        background-color: #1e293b;
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 4px;
    }
    .badge-p0 {
        background-color: #ef4444;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


DATA_DIR = PROJECT_ROOT / "data" / "mock_environment"


@st.cache_resource
def get_environment():
    env = MockCloudEnvironment(DATA_DIR)
    if not (DATA_DIR / "prometheus_metrics.csv").exists():
        env.inject_fault("db_connection_leak")
    return env


def main():
    env = get_environment()
    agent = AutonomousSREAgent(DATA_DIR)
    
    # Sidebar
    st.sidebar.title("🚨 SRE Incident War Room")
    st.sidebar.markdown("**Autonomous Self-Healing Agent**")
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### Chaos / Fault Injection Engine")
    fault_choice = st.sidebar.selectbox(
        "Select Chaos Scenario to Inject:",
        options=list(MockCloudEnvironment.FAULT_SCENARIOS.keys()),
        format_func=lambda x: MockCloudEnvironment.FAULT_SCENARIOS[x]["title"]
    )
    
    col_inj1, col_inj2 = st.sidebar.columns(2)
    with col_inj1:
        if st.button("⚡ Inject Fault", type="primary", use_container_width=True):
            env.inject_fault(fault_choice)
            st.sidebar.error(f"Injected: {fault_choice}")
            st.rerun()
    with col_inj2:
        if st.button("🔄 Clear System", use_container_width=True):
            env.clear_fault()
            st.sidebar.success("Environment reset to healthy.")
            st.rerun()

    # Load fresh telemetry
    metrics_df = pd.read_csv(DATA_DIR / "prometheus_metrics.csv")
    logs_df = pd.read_csv(DATA_DIR / "opentelemetry_logs.csv")
    
    # Dashboard Tabs
    tab_war_room, tab_agent, tab_metrics, tab_logs = st.tabs([
        "🚨 Incident War Room & Triage",
        "🧠 SRE Agent Autonomous RCA & Patch",
        "📈 Prometheus Telemetry Spikes",
        "📜 OpenTelemetry Live Stream"
    ])

    # ==========================================
    # TAB 1: WAR ROOM & TRIAGE
    # ==========================================
    with tab_war_room:
        st.subheader("Live System Health & Incident Status")
        
        # Calculate current fleet status
        latest_metrics = metrics_df.groupby("service").last().reset_index()
        max_err = latest_metrics["error_rate_pct"].max()
        max_p99 = latest_metrics["latency_p99_ms"].max()
        
        is_incident_active = max_err > 10.0 or max_p99 > 1000
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall Fleet Health", "CRITICAL P0 INCIDENT" if is_incident_active else "OPERATIONAL HEALTHY", 
                  delta="-Degraded" if is_incident_active else "Normal", delta_color="inverse")
        c2.metric("Peak P99 Latency", f"{max_p99:.0f} ms", delta=f"{max_p99-80:.0f} ms" if max_p99 > 80 else None, delta_color="inverse")
        c3.metric("Peak Error Rate", f"{max_err:.1f}%", delta=f"{max_err-0.1:.1f}%" if max_err > 1 else None, delta_color="inverse")
        c4.metric("Active Microservices", f"{len(latest_metrics)} Services")
        
        st.markdown("---")
        
        # Microservice Health Status Grid
        st.markdown("#### Microservice Health Matrix")
        grid_cols = st.columns(len(latest_metrics))
        for idx, row in latest_metrics.iterrows():
            with grid_cols[idx]:
                svc_status = "🔴 DEGRADED" if row["error_rate_pct"] > 5.0 or row["latency_p99_ms"] > 500 else "🟢 HEALTHY"
                st.markdown(f"**{row['service']}**")
                st.caption(f"Status: {svc_status}")
                st.caption(f"CPU: `{row['cpu_usage_pct']}%` | P99: `{row['latency_p99_ms']}ms`")
                st.caption(f"Errors: `{row['error_rate_pct']}%`")

        st.markdown("---")
        if is_incident_active:
            st.error("🚨 **Incident Detected:** High error rates and latency anomalies detected in production. Head to the **SRE Agent Autonomous RCA** tab to run automated diagnosis and patch generation.")

    # ==========================================
    # TAB 2: AGENT AUTONOMOUS RCA & PATCH
    # ==========================================
    with tab_agent:
        st.subheader("Autonomous SRE Root Cause Analysis & Automated Remediation")
        st.markdown(
            "The SRE Agent executes an autonomous **ReAct workflow**: Correlating Prometheus spikes, querying OpenTelemetry fatal logs, "
            "evaluating recent Git deployments, executing sandbox verification commands, and generating a verified patch diff."
        )
        
        if st.button("🚀 Trigger Autonomous Investigation", type="primary"):
            with st.spinner("Autonomous Agent actively querying telemetry, logs, and Git history..."):
                investigation = agent.investigate_incident()
                st.session_state["investigation"] = investigation
                
        if "investigation" in st.session_state:
            res = st.session_state["investigation"]
            
            st.success(f"**Incident RCA Complete:** `{res['incident_title']}`")
            
            col_rca_l, col_rca_r = st.columns([3, 2])
            
            with col_rca_l:
                st.markdown("### 📋 Executive Incident Post-Mortem")
                st.markdown(f"**Primary Culprit Service:** `{res['culprit_service']}`")
                st.markdown(f"**Root Cause Hypothesis:**\n\n{res['root_cause']}")
                st.markdown(f"**Recommended Action:**\n\n`{res['remediation_action']}`")
                
                st.markdown("### 🛠️ Proposed Automated Git Patch Diff")
                st.code(res["patch_diff"], language="diff")
                
                # Human in the Loop approval
                st.markdown("#### Human-in-the-Loop Safeguard")
                appr_col1, appr_col2 = st.columns(2)
                with appr_col1:
                    if st.button("✅ Approve & Deploy Remediation to Production", type="primary", use_container_width=True):
                        env.clear_fault()
                        st.success("Remediation deployed successfully! Active connections recycled. System recovered.")
                with appr_col2:
                    if st.button("❌ Reject Patch & Escalate to On-Call Human", use_container_width=True):
                        st.warning("Patch rejected. PagerDuty alert escalated to Principal On-Call.")

            with col_rca_r:
                st.markdown("### 🕵️ Agent Reasoning & Audit Trace")
                for step in res["reasoning_trace"]:
                    with st.expander(f"⚙️ {step['stage']}", expanded=True):
                        st.write(step["details"])

    # ==========================================
    # TAB 3: PROMETHEUS TELEMETRY
    # ==========================================
    with tab_metrics:
        st.subheader("Prometheus Real-Time Telemetry Spikes")
        
        metric_choice = st.selectbox(
            "Select Metric to Visualize:",
            ["latency_p99_ms", "error_rate_pct", "cpu_usage_pct", "active_connections"]
        )
        
        fig_metric = px.line(
            metrics_df,
            x="timestamp",
            y=metric_choice,
            color="service",
            title=f"Fleet-wide {metric_choice.replace('_', ' ').title()} Over Time",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_metric.update_layout(height=450, hovermode="x unified")
        st.plotly_chart(fig_metric, use_container_width=True)

    # ==========================================
    # TAB 4: OPENTELEMETRY LOG STREAM
    # ==========================================
    with tab_logs:
        st.subheader("OpenTelemetry Distributed Log Stream")
        
        col_flt1, col_flt2 = st.columns(2)
        with col_flt1:
            lvl_filter = st.selectbox("Log Severity Level:", ["ALL", "FATAL", "ERROR", "WARN", "INFO"])
        with col_flt2:
            svc_filter = st.selectbox("Filter Service:", ["ALL"] + MockCloudEnvironment.SERVICES)
            
        display_logs = logs_df.copy()
        if lvl_filter != "ALL":
            display_logs = display_logs[display_logs["level"] == lvl_filter]
        if svc_filter != "ALL":
            display_logs = display_logs[display_logs["service"] == svc_filter]
            
        st.dataframe(
            display_logs.head(40),
            use_container_width=True,
            hide_index=True
        )


if __name__ == "__main__":
    main()
