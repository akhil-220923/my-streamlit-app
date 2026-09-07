"""Command Center page — executive security overview."""
import streamlit as st
import plotly.express as px
import pandas as pd

from components.ui_components import (
    metric_card_html, risk_badge, status_indicator,
    security_pipeline_html, section_header, info_card
)
from utils.data_service import get_system_status
@st.cache_data(ttl=60, show_spinner=False)
def _build_risk_chart(events_tuples):
    risk_counts = pd.DataFrame([{"Risk": r, "Count": 1} for _, r, _ in events_tuples]).groupby("Risk").sum().reset_index()
    fig = px.bar(risk_counts, x="Risk", y="Count", color="Risk",
                color_discrete_map={"HIGH": "#dc2626", "MEDIUM": "#d97706", "LOW": "#0d9488"},
                title="Risk Distribution")
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(size=12, color="#64748b"))
    return fig


@st.cache_data(ttl=60, show_spinner=False)
def _build_timeline_chart(events_tuples):
    timeline_df = pd.DataFrame([{"Frame": f, "Track": str(t), "Risk": r} for f, t, r in events_tuples])
    fig2 = px.scatter(timeline_df, x="Frame", y="Track", color="Risk", size_max=15,
                     color_discrete_map={"HIGH": "#dc2626", "MEDIUM": "#d97706", "LOW": "#0d9488"},
                     title="Intrusion Events Over Frames")
    fig2.update_traces(marker_size=12)
    fig2.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(size=12, color="#64748b"))
    return fig2


def render(events):
    st.markdown(section_header("Command Center", "Executive security overview"), unsafe_allow_html=True)

    unique_tracks = len(set(e.person_track_id for e in events))
    evidence_count = sum(1 for e in events if e.evidence_file)
    threat_level = "HIGH" if events else "NORMAL"

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card_html("Intrusion Events", str(len(events)), "🚨", "red"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card_html("Unique Person Tracks", str(unique_tracks), "🎯", "navy"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card_html("Threat Level", threat_level, "📊", "red" if threat_level == "HIGH" else "green"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card_html("Evidence Captured", str(evidence_count), "📸", "teal"), unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # Threat status + System health
    col_left, col_right = st.columns(2)

    with col_left:
        if events:
            st.markdown(f"""
            <div class="ibvap-card ibvap-card-threat">
                <div style="display:flex;align-items:flex-start;gap:14px;">
                    <div style="width:48px;height:48px;border-radius:10px;background:#fee2e2;
                    display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">⚠️</div>
                    <div>
                        <h3 style="color:#dc2626;font-size:15px;font-weight:700;margin:0;">
                            HIGH RISK ACTIVITY DETECTED</h3>
                        <p style="font-size:13px;color:#64748b;margin:4px 0 0 0;">
                            {len(events)} intrusion event{'s' if len(events) != 1 else ''} recorded.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ibvap-card ibvap-card-secure">
                <div style="display:flex;align-items:flex-start;gap:14px;">
                    <div style="width:48px;height:48px;border-radius:10px;background:#dcfce7;
                    display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">✅</div>
                    <div>
                        <h3 style="color:#16a34a;font-size:15px;font-weight:700;margin:0;">
                            SYSTEM SECURE</h3>
                        <p style="font-size:13px;color:#64748b;margin:4px 0 0 0;">No intrusion detected.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        status = get_system_status()
        modules = [
            ("🧠", "AI Detection", "YOLO11"),
            ("🎯", "Object Tracking", "ByteTrack"),
            ("📍", "Restricted Zone Monitoring", "Polygon zone"),
            ("📝", "Event Logger", "Structured log"),
            ("📸", "Evidence Capture", "Visual snapshot"),
            ("🛡️", "Audit System", "CSV audit trail"),
        ]
        items_html = ""
        for icon, label, sub in modules:
            items_html += f"""
            <div class="health-item">
                <div class="health-item-icon">{icon}</div>
                <div style="flex:1;min-width:0;">
                    <div class="health-item-label">{label}</div>
                    <div class="health-item-sub">{sub}</div>
                </div>
                {status_indicator(True, "ONLINE")}
            </div>"""
        st.markdown(f"""
        <div class="ibvap-card">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <h3 style="margin:0;">System Health</h3>
                <span style="font-size:12px;font-weight:500;color:#16a34a;">All Systems Online</span>
            </div>
            <div class="health-grid">{items_html}</div>
        </div>
        """, unsafe_allow_html=True)

    # Security pipeline
    st.markdown(f'<div class="pipeline-container">{security_pipeline_html()}</div>', unsafe_allow_html=True)

    # Risk distribution chart
    if events:
        events_tuples = tuple((e.frame, e.person_track_id, e.risk) for e in events)
        fig1 = _build_risk_chart(events_tuples)
        fig2 = _build_timeline_chart(events_tuples)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        with col_chart2:
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    # Recent events
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="ibvap-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <h3 style="margin:0;">Recent Security Events</h3>
        </div>
    """, unsafe_allow_html=True)

    if not events:
        st.markdown("""
        <p style="text-align:center;color:#94a3b8;padding:24px;">
        No intrusion events detected. Surveillance system is operating normally.</p>
        """, unsafe_allow_html=True)
    else:
        for event in events[:5]:
            st.markdown(f"""
            <div class="event-item">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="width:32px;height:32px;border-radius:8px;background:#fee2e2;
                    display:flex;align-items:center;justify-content:center;font-size:14px;">🚨</div>
                    <div>
                        <div style="font-size:13px;font-weight:500;color:#1e293b;">{event.event_type}</div>
                        <div style="font-size:11px;color:#94a3b8;">
                            Track {event.person_track_id} — Frame {event.frame} — {event.timestamp}
                        </div>
                    </div>
                </div>
                {risk_badge(event.risk)}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
