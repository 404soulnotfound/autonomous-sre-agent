"""
Autonomous SRE Agent — War Room Command Center.
Full-bleed single-screen layout with ZERO tabs and ZERO sidebar.
Zones: Header → Telemetry Sparklines → Service Grid + Radar → Chaos Controls → Agent RCA → Deep Dive.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from data.mock_environment.simulator import MockCloudEnvironment
from src.agent import AutonomousSREAgent


st.set_page_config(
    page_title="AutoSRE // War Room",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def hex_to_rgba(hex_color, alpha=0.1):
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{alpha})"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLASSMORPHIC WAR ROOM THEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', -apple-system, sans-serif;
    }

    /* ── Kill Sidebar ── */
    section[data-testid="stSidebar"] { display: none !important; }
    button[kind="header"] { display: none !important; }

    /* ── Deep Space Canvas ── */
    .stApp {
        background: linear-gradient(160deg, #080C18 0%, #0F172A 45%, #131B2E 100%);
        color: #E2E8F0;
    }
    header[data-testid="stHeader"] {
        background: rgba(8, 12, 24, 0.85) !important;
        backdrop-filter: blur(12px);
    }

    /* ── Glass Surface ── */
    .glass {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
    }

    /* ── Spark Card ── */
    .spark-card {
        background: rgba(30, 41, 59, 0.35);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 16px 20px 4px 20px;
    }

    /* ── Service Cards ── */
    .svc-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px;
        text-align: center;
    }
    .svc-card.degraded {
        background: rgba(239, 68, 68, 0.07);
        border: 1px solid rgba(239, 68, 68, 0.3);
        box-shadow: 0 0 35px rgba(239, 68, 68, 0.12);
    }
    .svc-card.nominal {
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    /* ── War Room Header ── */
    .warroom-hdr {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0 14px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 18px;
    }

    /* ── Status Pills ── */
    .pill-crit {
        background: rgba(239, 68, 68, 0.14);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 1.2px;
        animation: pulse-glow 2s ease-in-out infinite;
    }
    .pill-ok {
        background: rgba(16, 185, 129, 0.1);
        color: #6EE7B7;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 1.2px;
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 8px rgba(239,68,68,0.2); }
        50% { box-shadow: 0 0 28px rgba(239,68,68,0.45); }
    }

    /* ── Zone Labels ── */
    .zone-lbl {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        color: #475569;
        font-weight: 600;
        margin: 20px 0 14px 0;
        padding-left: 2px;
    }

    /* ── Metric boxes ── */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.35);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 14px;
        border-radius: 12px;
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="stMetricValue"] {
        color: #F1F5F9 !important;
        font-weight: 700 !important;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%) !important;
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        font-size: 13px;
    }
    .stButton > button {
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #CBD5E1 !important;
        background: rgba(30, 41, 59, 0.4) !important;
        font-weight: 600 !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] label { color: #94A3B8 !important; }

    /* ── Dividers ── */
    hr { border-color: rgba(255, 255, 255, 0.05) !important; margin: 6px 0 !important; }

    /* ── Expander ── */
    details summary { color: #CBD5E1 !important; }

    /* ── Dataframe ── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA LAYER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA_DIR = PROJECT_ROOT / "data" / "mock_environment"


@st.cache_resource
def get_environment():
    env = MockCloudEnvironment(DATA_DIR)
    if not (DATA_DIR / "prometheus_metrics.csv").exists():
        env.inject_fault("db_connection_leak")
    return env


def make_sparkline(values, color="#8B5CF6", height=55):
    """Tiny inline sparkline with gradient fill."""
    fill = hex_to_rgba(color, 0.12)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2, shape="spline"),
        fill="tozeroy", fillcolor=fill,
        hoverinfo="y"
    ))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    env = get_environment()
    agent = AutonomousSREAgent(DATA_DIR)

    metrics_df = pd.read_csv(DATA_DIR / "prometheus_metrics.csv")
    logs_df = pd.read_csv(DATA_DIR / "opentelemetry_logs.csv")

    latest = metrics_df.groupby("service").last().reset_index()
    max_err = latest["error_rate_pct"].max()
    max_p99 = latest["latency_p99_ms"].max()
    is_incident = max_err > 10.0 or max_p99 > 1000

    # ══════════════════════════════════════════════
    # ZONE 0 — WAR ROOM HEADER
    # ══════════════════════════════════════════════
    pill = '<span class="pill-crit">⦿ P0 INCIDENT ACTIVE</span>' if is_incident \
        else '<span class="pill-ok">✓ ALL SYSTEMS NOMINAL</span>'

    st.markdown(f"""
    <div class="warroom-hdr">
        <div>
            <div style="font-size: 28px; font-weight: 800; letter-spacing: -1px; color: #F8FAFC;">
                AUTO<span style="color:#8B5CF6;">SRE</span>
            </div>
            <div style="font-size: 11px; color: #475569; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px;">
                Autonomous Incident Response &bull; War Room Command
            </div>
        </div>
        <div>{pill}</div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # ZONE 1 — TELEMETRY SPARKLINE STRIP
    # ══════════════════════════════════════════════
    st.markdown('<div class="zone-lbl">▸ LIVE TELEMETRY FEED</div>', unsafe_allow_html=True)

    ts_agg = metrics_df.groupby("timestamp").agg({
        "cpu_usage_pct": "mean",
        "latency_p99_ms": "mean",
        "error_rate_pct": "mean",
        "active_connections": "mean"
    }).reset_index()

    cpu_vals = ts_agg["cpu_usage_pct"].values[-20:]
    lat_vals = ts_agg["latency_p99_ms"].values[-20:]
    err_vals = ts_agg["error_rate_pct"].values[-20:]
    conn_vals = ts_agg["active_connections"].values[-20:]

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown(f"""<div class="spark-card">
            <div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1.5px;">Fleet CPU</div>
            <div style="font-size:26px;font-weight:800;color:#E2E8F0;margin:4px 0 2px 0;">{cpu_vals[-1]:.1f}%</div>
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(make_sparkline(cpu_vals, "#8B5CF6"), use_container_width=True, config={"displayModeBar": False})

    with s2:
        lc = "#EF4444" if lat_vals[-1] > 500 else "#8B5CF6"
        st.markdown(f"""<div class="spark-card">
            <div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1.5px;">Avg P99 Latency</div>
            <div style="font-size:26px;font-weight:800;color:{lc};margin:4px 0 2px 0;">{lat_vals[-1]:.0f}ms</div>
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(make_sparkline(lat_vals, lc), use_container_width=True, config={"displayModeBar": False})

    with s3:
        ec = "#EF4444" if err_vals[-1] > 5 else "#10B981"
        st.markdown(f"""<div class="spark-card">
            <div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1.5px;">Avg Error Rate</div>
            <div style="font-size:26px;font-weight:800;color:{ec};margin:4px 0 2px 0;">{err_vals[-1]:.1f}%</div>
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(make_sparkline(err_vals, ec), use_container_width=True, config={"displayModeBar": False})

    with s4:
        st.markdown(f"""<div class="spark-card">
            <div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:1.5px;">Active Connections</div>
            <div style="font-size:26px;font-weight:800;color:#3B82F6;margin:4px 0 2px 0;">{conn_vals[-1]:.0f}</div>
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(make_sparkline(conn_vals, "#3B82F6"), use_container_width=True, config={"displayModeBar": False})

    # ══════════════════════════════════════════════
    # ZONE 2 — SERVICE FLEET GRID + RADAR
    # ══════════════════════════════════════════════
    st.markdown('<div class="zone-lbl">▸ MICROSERVICE FLEET STATUS</div>', unsafe_allow_html=True)

    grid_col, radar_col = st.columns([3, 2])

    with grid_col:
        services = latest.to_dict("records")
        rows = [services[i:i + 3] for i in range(0, len(services), 3)]

        for row_batch in rows:
            cols = st.columns(len(row_batch))
            for col, svc in zip(cols, row_batch):
                with col:
                    deg = svc["error_rate_pct"] > 5.0 or svc["latency_p99_ms"] > 500
                    cls = "svc-card degraded" if deg else "svc-card nominal"
                    dot_color = "#FCA5A5" if deg else "#6EE7B7"
                    dot_icon = "🔴" if deg else "🟢"
                    st_text = "DEGRADED" if deg else "NOMINAL"

                    st.markdown(f"""
                    <div class="{cls}">
                        <div style="font-size:10px;color:{dot_color};text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">
                            {dot_icon} {st_text}
                        </div>
                        <div style="font-size:15px;font-weight:700;color:#F8FAFC;margin-bottom:12px;">
                            {svc['service']}
                        </div>
                        <div style="display:flex;justify-content:space-around;font-size:12px;">
                            <div><div style="color:#475569;">CPU</div><div style="font-weight:700;color:#E2E8F0;">{svc['cpu_usage_pct']:.0f}%</div></div>
                            <div><div style="color:#475569;">P99</div><div style="font-weight:700;color:{'#FCA5A5' if svc['latency_p99_ms']>500 else '#E2E8F0'};">{svc['latency_p99_ms']:.0f}ms</div></div>
                            <div><div style="color:#475569;">ERR</div><div style="font-weight:700;color:{'#FCA5A5' if svc['error_rate_pct']>5 else '#E2E8F0'};">{svc['error_rate_pct']:.1f}%</div></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with radar_col:
        cats = latest["service"].tolist()
        r_vals = latest["latency_p99_ms"].tolist()
        cats += [cats[0]]
        r_vals += [r_vals[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=r_vals, theta=cats,
            fill="toself",
            fillcolor="rgba(139, 92, 246, 0.18)",
            line=dict(color="#8B5CF6", width=2.5),
            name="P99 Latency"
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, max(1000, max_p99 * 1.15)],
                                color="#475569", gridcolor="rgba(255,255,255,0.04)",
                                tickfont=dict(size=9, color="#475569")),
                angularaxis=dict(color="#94A3B8", gridcolor="rgba(255,255,255,0.04)",
                                 tickfont=dict(size=10, color="#94A3B8"))
            ),
            showlegend=False, height=380,
            margin=dict(l=50, r=50, t=40, b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.markdown("""<div style="text-align:center;font-size:13px;font-weight:700;color:#A78BFA;
                    letter-spacing:2px;text-transform:uppercase;margin-bottom:-8px;">
            Latency Topology Radar</div>""", unsafe_allow_html=True)
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ══════════════════════════════════════════════
    # ZONE 3 — CHAOS ENGINEERING CONTROLS
    # ══════════════════════════════════════════════
    st.markdown('<div class="zone-lbl">▸ CHAOS ENGINEERING LAB</div>', unsafe_allow_html=True)

    ch1, ch2, ch3 = st.columns([3, 1, 1])
    with ch1:
        fault_choice = st.selectbox(
            "Inject Scenario:",
            options=list(MockCloudEnvironment.FAULT_SCENARIOS.keys()),
            format_func=lambda x: f"⚡ {MockCloudEnvironment.FAULT_SCENARIOS[x]['title']}",
            label_visibility="collapsed"
        )
    with ch2:
        if st.button("⚡ INJECT FAULT", type="primary", use_container_width=True):
            env.inject_fault(fault_choice)
            st.rerun()
    with ch3:
        if st.button("🔄 RESTORE ALL", use_container_width=True):
            env.clear_fault()
            st.rerun()

    st.markdown("---")

    # ══════════════════════════════════════════════
    # ZONE 4 — AUTONOMOUS AGENT INVESTIGATION
    # ══════════════════════════════════════════════
    st.markdown('<div class="zone-lbl">▸ AUTONOMOUS AGENT INVESTIGATION</div>', unsafe_allow_html=True)

    if st.button("🚀 LAUNCH AUTONOMOUS ROOT CAUSE ANALYSIS", type="primary", use_container_width=True):
        with st.spinner("Agent correlating Prometheus ➜ OpenTelemetry ➜ Git history..."):
            investigation = agent.investigate_incident()
            st.session_state["sre_investigation"] = investigation

    if "sre_investigation" in st.session_state:
        res = st.session_state["sre_investigation"]

        rca_left, rca_right = st.columns([3, 2])

        with rca_left:
            st.markdown(f"""
            <div class="glass" style="border-left: 3px solid #8B5CF6;">
                <div style="font-size:10px;color:#64748B;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">
                    INCIDENT POST-MORTEM
                </div>
                <div style="font-size:20px;font-weight:700;color:#F8FAFC;margin-bottom:14px;">
                    {res['incident_title']}
                </div>
                <div style="margin-bottom:10px;">
                    <span style="color:#94A3B8;font-size:13px;">Culprit Service</span><br/>
                    <span style="color:#A78BFA;font-family:'JetBrains Mono';font-weight:600;font-size:15px;">{res['culprit_service']}</span>
                </div>
                <div style="margin-bottom:10px;">
                    <span style="color:#94A3B8;font-size:13px;">Root Cause</span><br/>
                    <span style="color:#E2E8F0;font-size:14px;">{res['root_cause']}</span>
                </div>
                <div>
                    <span style="color:#94A3B8;font-size:13px;">Remediation</span><br/>
                    <code style="background:rgba(139,92,246,0.12);color:#C4B5FD;padding:3px 8px;border-radius:6px;font-size:13px;">{res['remediation_action']}</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### Synthesized Remediation Patch")
            st.code(res["patch_diff"], language="diff")

            d1, d2 = st.columns(2)
            with d1:
                if st.button("✅ APPROVE & AUTO-DEPLOY", type="primary", use_container_width=True):
                    env.clear_fault()
                    st.success("Patch applied. Database pool recycled. Incident resolved.")
            with d2:
                if st.button("❌ ESCALATE TO ON-CALL LEAD", use_container_width=True):
                    st.warning("Escalated to L3 SRE Lead via PagerDuty.")

        with rca_right:
            st.markdown("""<div style="font-size:10px;color:#64748B;text-transform:uppercase;
                        letter-spacing:2px;margin-bottom:12px;">AGENT REASONING TRACE</div>""",
                        unsafe_allow_html=True)
            for step in res["reasoning_trace"]:
                with st.expander(f"⚙️ {step['stage']}", expanded=False):
                    st.write(step["details"])

    st.markdown("---")

    # ══════════════════════════════════════════════
    # ZONE 5 — TELEMETRY DEEP DIVE + LOG STREAM
    # ══════════════════════════════════════════════
    st.markdown('<div class="zone-lbl">▸ TELEMETRY DEEP DIVE & LOG STREAM</div>', unsafe_allow_html=True)

    tele_col, log_col = st.columns(2)

    with tele_col:
        metric_choice = st.selectbox(
            "Telemetry metric:",
            ["latency_p99_ms", "error_rate_pct", "cpu_usage_pct", "active_connections"],
            format_func=lambda x: x.replace("_", " ").upper()
        )
        fig_ts = go.Figure()
        for svc_name in metrics_df["service"].unique():
            svc_df = metrics_df[metrics_df["service"] == svc_name]
            fig_ts.add_trace(go.Scatter(
                x=svc_df["timestamp"], y=svc_df[metric_choice],
                mode="lines", name=svc_name, line=dict(width=2)
            ))
        fig_ts.update_layout(
            height=330, hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.03)", color="#94A3B8",
                       tickfont=dict(size=10, color="#64748B")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.03)", color="#94A3B8",
                       tickfont=dict(size=10, color="#64748B")),
            legend=dict(font=dict(color="#94A3B8", size=10), orientation="h",
                        yanchor="bottom", y=1.02, xanchor="right", x=1),
            colorway=["#8B5CF6", "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#EC4899"],
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_ts, use_container_width=True, config={"displayModeBar": False})

    with log_col:
        st.markdown("**OpenTelemetry Log Stream**")
        f1, f2 = st.columns(2)
        with f1:
            lvl = st.selectbox("Severity:", ["ALL", "FATAL", "ERROR", "WARN", "INFO"])
        with f2:
            svc_filter = st.selectbox("Service:", ["ALL"] + MockCloudEnvironment.SERVICES)

        display_logs = logs_df.copy()
        if lvl != "ALL":
            display_logs = display_logs[display_logs["level"] == lvl]
        if svc_filter != "ALL":
            display_logs = display_logs[display_logs["service"] == svc_filter]

        st.dataframe(display_logs.head(25), use_container_width=True, hide_index=True, height=300)


if __name__ == "__main__":
    main()
