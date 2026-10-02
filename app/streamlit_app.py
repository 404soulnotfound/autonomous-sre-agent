"""
Autonomous Incident RCA & Self-Healing SRE Agent Dashboard.
Redesigned with Option 4: Glassmorphic Tactical Dashboard (Futuristic Mission Control Dark).
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
    page_title="Tactical SRE // Autonomous Agent Command",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Option 4: Glassmorphic Tactical Dark Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', -apple-system, sans-serif;
    }
    
    /* Deep Navy Space Canvas */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0F172A 0%, #0A0F1D 100%);
        color: #F1F5F9;
    }
    
    /* Frosted Glass Card */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 16px;
    }
    
    /* Mission Control Header */
    .mission-header {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 16px;
        padding: 16px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.15);
    }
    
    /* Floating Status Pills */
    .pill-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.5);
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
    }
    
    .pill-operational {
        background: rgba(16, 185, 129, 0.15);
        color: #6EE7B7;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    
    /* Glowing Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(15, 23, 42, 0.5);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 14px;
        font-weight: 600;
        color: #94A3B8;
        border-radius: 8px;
        padding: 8px 18px;
        background: transparent;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(59, 130, 246, 0.3) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.25);
    }
    
    /* Frosted Metric Boxes */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }
    
    /* Code Diff Styling */
    .stCodeBlock {
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
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
    st.sidebar.markdown("### ⚡ **Mission Control // Chaos Lab**")
    st.sidebar.caption("Tactical Fault Injection & Sandbox")
    st.sidebar.markdown("---")
    
    fault_choice = st.sidebar.selectbox(
        "Inject Outage Scenario:",
        options=list(MockCloudEnvironment.FAULT_SCENARIOS.keys()),
        format_func=lambda x: MockCloudEnvironment.FAULT_SCENARIOS[x]["title"]
    )
    
    col_inj1, col_inj2 = st.sidebar.columns(2)
    with col_inj1:
        if st.button("⚡ Inject Outage", type="primary", use_container_width=True):
            env.inject_fault(fault_choice)
            st.sidebar.error(f"Injected: {fault_choice}")
            st.rerun()
    with col_inj2:
        if st.button("🔄 Restore Fleet", use_container_width=True):
            env.clear_fault()
            st.sidebar.success("All systems restored.")
            st.rerun()

    # Load Telemetry
    metrics_df = pd.read_csv(DATA_DIR / "prometheus_metrics.csv")
    logs_df = pd.read_csv(DATA_DIR / "opentelemetry_logs.csv")
    
    latest_metrics = metrics_df.groupby("service").last().reset_index()
    max_err = latest_metrics["error_rate_pct"].max()
    max_p99 = latest_metrics["latency_p99_ms"].max()
    is_incident_active = max_err > 10.0 or max_p99 > 1000

    # Top Status Ribbon
    if is_incident_active:
        badge_html = '<span class="pill-critical">● CRITICAL P0 INCIDENT DETECTED</span>'
    else:
        badge_html = '<span class="pill-operational">✓ FLEET HEALTHY // OPTIMAL</span>'

    st.markdown(f"""
    <div class="mission-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px;">
                TACTICAL COMMAND // <span style="color:#A78BFA;">SRE INCIDENT DEFENSE</span>
            </h2>
            <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                Real-Time Telemetry Correlator & Autonomous Remediation Engine
            </div>
        </div>
        <div>
            {badge_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 4 Tactical KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Fleet Status", "P0 CRITICAL" if is_incident_active else "OPERATIONAL", 
              delta="-Degraded" if is_incident_active else "Stable", delta_color="inverse")
    k2.metric("Peak P99 Latency", f"{max_p99:.0f} ms", delta=f"+{max_p99-70:.0f}ms" if max_p99 > 80 else None, delta_color="inverse")
    k3.metric("Peak Error Spike", f"{max_err:.1f}%", delta=f"+{max_err-0.1:.1f}%" if max_err > 1 else None, delta_color="inverse")
    k4.metric("Active Microservices", f"{len(latest_metrics)} Monitored")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Tabs
    tab_mission, tab_agent, tab_telemetry, tab_stream = st.tabs([
        "🛸 Tactical Service Matrix & Radar",
        "🧠 SRE Agent Autonomous RCA & Diff",
        "📈 Prometheus Telemetry Curves",
        "📜 OpenTelemetry Live Feed"
    ])

    # ==========================================
    # TAB 1: SERVICE MATRIX & RADAR
    # ==========================================
    with tab_mission:
        st.subheader("Microservice Fleet Status Grid")
        
        svc_cols = st.columns(len(latest_metrics))
        for idx, row in latest_metrics.iterrows():
            with svc_cols[idx]:
                is_deg = row["error_rate_pct"] > 5.0 or row["latency_p99_ms"] > 500
                st.markdown(f"""
                <div class="glass-card" style="padding: 14px; text-align: center; border-color: {'rgba(239, 68, 68, 0.4)' if is_deg else 'rgba(16, 185, 129, 0.3)'};">
                    <div style="font-size: 11px; text-transform: uppercase; color: #94A3B8;">{'🔴 DEGRADED' if is_deg else '🟢 NORMAL'}</div>
                    <div style="font-size: 15px; font-weight: 700; color: #F8FAFC; margin: 4px 0;">{row['service']}</div>
                    <div style="font-size: 12px; color: #CBD5E1;">CPU: <b>{row['cpu_usage_pct']}%</b></div>
                    <div style="font-size: 12px; color: #CBD5E1;">P99: <b>{row['latency_p99_ms']}ms</b></div>
                    <div style="font-size: 12px; color: {'#FCA5A5' if is_deg else '#CBD5E1'};">Err: <b>{row['error_rate_pct']}%</b></div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Latency Radar Map
        radar_categories = latest_metrics["service"].tolist()
        radar_values = latest_metrics["latency_p99_ms"].tolist()
        # close the polygon
        radar_categories += [radar_categories[0]]
        radar_values += [radar_values[0]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_values,
            theta=radar_categories,
            fill='toself',
            fillcolor='rgba(139, 92, 246, 0.25)',
            line=dict(color='#8B5CF6', width=2),
            name='Latency P99 (ms)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, max(1000, max_p99 * 1.1)], color="#94A3B8", gridcolor="rgba(255,255,255,0.08)"),
                angularaxis=dict(color="#CBD5E1", gridcolor="rgba(255,255,255,0.08)")
            ),
            showlegend=False,
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.markdown("#### Service Latency Topology Radar")
        st.plotly_chart(fig_radar, use_container_width=True)

    # ==========================================
    # TAB 2: AGENT AUTONOMOUS RCA & DIFF
    # ==========================================
    with tab_agent:
        st.subheader("Autonomous ReAct Root Cause Analysis Engine")
        st.markdown(
            "The SRE Agent executes an automated **ReAct diagnostic loop**: Correlates multi-service Prometheus spikes, "
            "inspects distributed trace exceptions, checks recent Git commits, executes sandbox commands, and synthesizes a production `git diff`."
        )
        
        if st.button("🚀 Trigger Autonomous Investigation & Sandbox Replay", type="primary"):
            with st.spinner("Agent running correlation across Prometheus, OpenTelemetry, and Git logs..."):
                investigation = agent.investigate_incident()
                st.session_state["sre_investigation"] = investigation
                
        if "sre_investigation" in st.session_state:
            res = st.session_state["sre_investigation"]
            
            st.success(f"**Root Cause Analysis Confirmed:** `{res['incident_title']}`")
            
            col_rca_l, col_rca_r = st.columns([3, 2])
            
            with col_rca_l:
                st.markdown(f"""
                <div class="glass-card">
                    <h3 style="margin-top:0; color:#F8FAFC;">Incident Post-Mortem</h3>
                    <p><b>Primary Culprit Microservice:</b> <span style="color:#A78BFA; font-family:'JetBrains Mono';">{res['culprit_service']}</span></p>
                    <p><b>Root Cause Hypothesis:</b><br>{res['root_cause']}</p>
                    <p><b>Remediation Action:</b><br><code>{res['remediation_action']}</code></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### Synthesized Remediation Diff (`git patch`)")
                st.code(res["patch_diff"], language="diff")
                
                st.markdown("#### Human-in-the-Loop Safe Deployment")
                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if st.button("✅ Approve & Auto-Deploy Patch", type="primary", use_container_width=True):
                        env.clear_fault()
                        st.success("Patch applied to container pods. Database pool recycled. Incident resolved!")
                with btn_c2:
                    if st.button("❌ Escalate to Human On-Call Lead", use_container_width=True):
                        st.warning("Incident escalated to Level 3 SRE Lead via PagerDuty.")

            with col_rca_r:
                st.markdown("### Agent Reasoning & Audit Trace")
                for step in res["reasoning_trace"]:
                    with st.expander(f"⚙️ {step['stage']}", expanded=True):
                        st.write(step["details"])

    # ==========================================
    # TAB 3: PROMETHEUS TELEMETRY
    # ==========================================
    with tab_telemetry:
        st.subheader("Prometheus High-Frequency Telemetry Curves")
        
        metric_choice = st.selectbox(
            "Select Telemetry Stream:",
            ["latency_p99_ms", "error_rate_pct", "cpu_usage_pct", "active_connections"]
        )
        
        fig_metric = px.line(
            metrics_df,
            x="timestamp",
            y=metric_choice,
            color="service",
            title=f"Telemetry: {metric_choice.replace('_', ' ').upper()}",
            color_discrete_sequence=["#8B5CF6", "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#EC4899"]
        )
        fig_metric.update_layout(
            height=420,
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)")
        )
        st.plotly_chart(fig_metric, use_container_width=True)

    # ==========================================
    # TAB 4: OPENTELEMETRY LIVE FEED
    # ==========================================
    with tab_stream:
        st.subheader("Distributed OpenTelemetry Log Pipeline")
        
        flt_c1, flt_c2 = st.columns(2)
        with flt_c1:
            lvl_filter = st.selectbox("Severity Level:", ["ALL", "FATAL", "ERROR", "WARN", "INFO"])
        with flt_c2:
            svc_filter = st.selectbox("Microservice:", ["ALL"] + MockCloudEnvironment.SERVICES)
            
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
