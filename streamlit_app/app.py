"""
IBVAP — Intelligent Border Video Analytics Platform
AI-Powered Border Surveillance, Intrusion Detection & Security Analytics

Main Streamlit application entry point.
SIH 2026 — Blockchain & Cybersecurity
"""
import streamlit as st
from datetime import datetime

from utils.data_service import fetch_events, get_system_status
from components.ui_components import (
    metric_card_html, risk_badge, status_indicator,
    security_pipeline_html, empty_state_html, section_header, info_card
)
from pages.command_center import render as render_command_center
from pages.surveillance import render as render_surveillance
from pages.security_events import render as render_security_events
from pages.digital_evidence import render as render_digital_evidence
from pages.audit_log import render as render_audit_log
from pages.system_page import render as render_system

st.set_page_config(
    page_title="IBVAP — Intelligent Border Video Analytics Platform",
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
/* Global */
.main .block-container { max-width: 1400px; padding-top: 1rem; padding-bottom: 2rem; }
.main > div { padding-top: 1rem; }

/* Hide Streamlit chrome */
#stMainMenu, footer { display: none; }
.stDeployButton { display: none; }

/* Header bar */
.ibvap-header {
    background: linear-gradient(135deg, #0a1929 0%, #102a43 100%);
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.ibvap-header h1 {
    color: #fff; font-size: 22px; font-weight: 700; margin: 0;
    letter-spacing: -0.5px;
}
.ibvap-header p {
    color: #94a3b8; font-size: 12px; margin: 2px 0 0 0;
}
.ibvap-status {
    display: flex; align-items: center; gap: 16px;
}
.ibvap-status-badge {
    background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3);
    border-radius: 8px; padding: 6px 14px;
    font-size: 12px; font-weight: 600; color: #4ade80;
    display: flex; align-items: center; gap: 6px;
}
.ibvap-clock { color: #94a3b8; font-size: 12px; font-family: monospace; }

/* Nav */
.ibvap-nav {
    display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;
}
.ibvap-nav button {
    background: var(--background-color); border: 1px solid var(--secondary-background-color); border-radius: 10px;
    padding: 10px 18px; font-size: 13px; font-weight: 500; color: var(--text-color);
    cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px;
}
.ibvap-nav button:hover { border-color: var(--primary-color); box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.ibvap-nav button.active {
    background: rgba(20, 184, 166, 0.1); border-color: #14b8a6; color: #0d9488;
    font-weight: 600;
}

/* Metric cards grid */
.metric-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px;
}
@media (max-width: 768px) { .metric-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .metric-grid { grid-template-columns: 1fr; } }

/* Cards */
.ibvap-card {
    background: var(--background-color); border: 1px solid var(--secondary-background-color); border-radius: 12px; padding: 20px;
    margin-bottom: 16px;
}
.ibvap-card h3 {
    font-size: 14px; font-weight: 600; color: var(--text-color); margin: 0 0 12px 0;
}
.ibvap-card-threat {
    background: rgba(254,242,242,0.1); border: 1px solid #fecaca;
}
.ibvap-card-secure {
    background: rgba(240,253,244,0.1); border: 1px solid #bbf7d0;
}

/* System health grid */
.health-grid {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;
}
.health-item {
    display: flex; align-items: center; gap: 10px; padding: 10px 12px;
    background: var(--secondary-background-color); border: 1px solid var(--secondary-background-color); border-radius: 8px;
}
.health-item-icon {
    width: 36px; height: 36px; border-radius: 8px; background: var(--background-color);
    border: 1px solid var(--secondary-background-color); display: flex; align-items: center;
    justify-content: center; font-size: 16px; flex-shrink: 0; color: var(--text-color);
}
.health-item-label { font-size: 13px; font-weight: 500; color: var(--text-color); }
.health-item-sub { font-size: 11px; opacity: 0.7; color: var(--text-color); }

/* Event list */
.event-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 14px; background: var(--secondary-background-color); border-radius: 8px;
    margin-bottom: 8px; transition: all 0.2s;
}
.event-item:hover { filter: brightness(0.95); }

/* Footer */
.ibvap-footer {
    border-top: 1px solid var(--secondary-background-color); padding: 16px 0; margin-top: 30px;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;
}
.ibvap-footer-text { font-size: 12px; opacity: 0.7; color: var(--text-color); }
.ibvap-footer-tech { font-size: 11px; opacity: 0.5; color: var(--text-color); }

/* Pipeline */
.pipeline-container {
    background: var(--background-color); border: 1px solid var(--secondary-background-color); border-radius: 12px; padding: 20px;
}

/* Mobile nav toggle */
.ibvap-mobile-nav {
    display: none;
}
@media (max-width: 768px) {
    .ibvap-mobile-nav {
        display: flex; gap: 8px; overflow-x: auto; padding-bottom: 12px;
        margin-bottom: 8px;
    }
    .ibvap-mobile-nav button {
        white-space: nowrap; background: var(--background-color); border: 1px solid var(--secondary-background-color);
        border-radius: 8px; padding: 8px 14px; font-size: 12px; font-weight: 500;
        color: var(--text-color); cursor: pointer;
    }
    .ibvap-mobile-nav button.active {
        background: rgba(20, 184, 166, 0.1); border-color: #14b8a6; color: #0d9488;
    }
}

/* Tables */
.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
    background: var(--secondary-background-color); border-bottom: 1px solid var(--border-color);
    padding: 10px 12px; text-align: left; font-size: 12px;
    font-weight: 600; opacity: 0.7; color: var(--text-color);
}
.data-table td {
    padding: 10px 12px; border-bottom: 1px solid var(--secondary-background-color);
    font-size: 13px; color: var(--text-color);
}
.data-table tr:hover td { filter: brightness(0.95); }

/* Modal */
.ibvap-modal-overlay {
    position: fixed; inset: 0; background: rgba(10,25,41,0.6);
    backdrop-filter: blur(4px); z-index: 200; display: flex;
    align-items: center; justify-content: center; padding: 20px;
}
.ibvap-modal {
    background: var(--background-color); border: 1px solid var(--secondary-background-color); border-radius: 12px; padding: 24px;
    max-width: 500px; width: 100%; max-height: 90vh; overflow-y: auto;
}

/* Evidence grid */
.evidence-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
}
@media (max-width: 768px) { .evidence-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .evidence-grid { grid-template-columns: 1fr; } }

.evidence-card {
    background: var(--background-color); border: 1px solid var(--secondary-background-color); border-radius: 12px;
    overflow: hidden; transition: all 0.2s;
}
.evidence-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.evidence-card img { width: 100%; aspect-ratio: 16/9; object-fit: cover; }
.evidence-card-body { padding: 14px; }

/* Zone visualization */
.zone-viz {
    background: #0a1929; border-radius: 8px; height: 160px;
    position: relative; overflow: hidden; margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# --- Session state for navigation ---
if "ibvap_page" not in st.session_state:
    st.session_state.ibvap_page = "command-center"
if "ibvap_selected_event" not in st.session_state:
    st.session_state.ibvap_selected_event = None
if "ibvap_evidence_view" not in st.session_state:
    st.session_state.ibvap_evidence_view = None

PAGES = [
    ("command-center", "Command Center", ":material/dashboard:"),
    ("surveillance", "Surveillance", ":material/videocam:"),
    ("security-events", "Security Events", ":material/warning:"),
    ("digital-evidence", "Digital Evidence", ":material/photo_camera:"),
    ("audit-log", "Audit Log", ":material/receipt_long:"),
    ("system", "System", ":material/settings:"),
]


def set_page(page_id: str):
    st.session_state.ibvap_page = page_id


def render_sidebar():
    current = st.session_state.ibvap_page
    with st.sidebar:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 22px; font-weight: 700; margin: 0; color: var(--text-color);">🛡️ IBVAP</h1>
            <p style="color: var(--text-color); opacity: 0.7; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin: 4px 0 0 0;">Border Video Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p style="color:var(--text-color);opacity:0.8;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;margin:0 0 10px 0;">Operations</p>', unsafe_allow_html=True)
        
        for pid, label, icon in PAGES:
            st.button(
                label, icon=icon, key=f"sidebtn-{pid}", use_container_width=True,
                type="primary" if current == pid else "secondary",
                on_click=set_page, args=(pid,)
            )
                
        # Status
        st.markdown('<div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid var(--secondary-background-color);">', unsafe_allow_html=True)
        st.markdown('<p style="color:var(--text-color);opacity:0.8;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 12px 0;font-weight:600;">System Status</p>', unsafe_allow_html=True)
        for label in ["AI Engine", "Tracking Engine", "Zone Monitor", "Audit Logger"]:
            st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;font-size:13px;color:var(--text-color);">{status_indicator(True)}<span>{label}</span></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display:flex;gap:12px;padding-top:16px;border-top:1px solid var(--secondary-background-color);margin-top:16px;">
            <span style="color:var(--text-color);opacity:0.6;font-size:11px;font-weight:500;">YOLO11</span>
            <span style="color:var(--text-color);opacity:0.6;font-size:11px;font-weight:500;">ByteTrack</span>
            <span style="color:var(--text-color);opacity:0.6;font-size:11px;font-weight:500;">OpenCV</span>
        </div>
        """, unsafe_allow_html=True)


def render_header():
    now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="ibvap-header">
        <div>
            <h1>IBVAP</h1>
            <p>Intelligent Border Video Analytics Platform</p>
            <p style="font-size:11px;color:#64748b;">AI-Powered Border Surveillance & Security Analytics</p>
        </div>
        <div class="ibvap-status">
            <span class="ibvap-clock">Last Updated {now}</span>
            <span class="ibvap-status-badge">{status_indicator(True)} SYSTEM OPERATIONAL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="ibvap-footer">
        <span class="ibvap-footer-text">
            <strong>IBVAP</strong> — Intelligent Border Video Analytics Platform
        </span>
        <span class="ibvap-footer-tech">
            YOLO11 • ByteTrack • OpenCV • SIH 2026 — Blockchain & Cybersecurity
        </span>
    </div>
    """, unsafe_allow_html=True)


# --- Main render ---
def main():
    if "ibvap_events" not in st.session_state or not st.session_state.ibvap_events:
        st.session_state.ibvap_events = fetch_events()
    events = st.session_state.ibvap_events

    render_sidebar()
    st.markdown('<div class="ibvap-main">', unsafe_allow_html=True)
    render_header()

    page = st.session_state.get("ibvap_page", "command-center")

    if page == "command-center":
        render_command_center(events)
    elif page == "surveillance":
        render_surveillance(events)
    elif page == "security-events":
        render_security_events(events)
    elif page == "digital-evidence":
        render_digital_evidence(events)
    elif page == "audit-log":
        render_audit_log(events)
    elif page == "system":
        render_system(events)

    render_footer()
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
