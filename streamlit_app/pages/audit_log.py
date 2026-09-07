"""Audit Log page — structured security audit trail."""
import streamlit as st

from components.ui_components import (
    risk_badge, status_indicator, section_header, empty_state_html
)
from utils.data_service import events_to_csv


def render(events):
    st.markdown(section_header(
        "Audit Log",
        f"Structured security audit trail — {len(events)} record{'s' if len(events) != 1 else ''}"
    ), unsafe_allow_html=True)

    # Info banner
    st.markdown("""
    <div class="ibvap-card" style="display:flex;align-items:flex-start;gap:12px;">
        <div style="width:36px;height:36px;border-radius:8px;background:#f0fdfa;
        display:flex;align-items:center;justify-content:center;flex-shrink:0;">🧾</div>
        <p style="font-size:13px;color:#475569;line-height:1.5;margin:0;">
        Each intrusion event is recorded with timestamp, tracked-person identifier, frame reference,
        risk level and associated evidence. The audit log can be exported as a structured CSV file
        for compliance and review.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not events:
        st.markdown(f"""
        <div class="ibvap-card">
            {empty_state_html("🧾", "Audit Log Unavailable",
            "No audit records found. Expected: output/intrusion_log.csv")}
        </div>
        """, unsafe_allow_html=True)
        return

    # Search + download
    col_search, col_download = st.columns([3, 1])
    with col_search:
        search = st.text_input("Search audit records...", key="audit-search")
    with col_download:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "📥 Download Security Audit Log",
            data=events_to_csv(events),
            file_name=f"ibvap_security_audit_log.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )

    # Filter
    filtered = events
    if search:
        q = search.lower()
        filtered = [e for e in events if q in e.event_id.lower() or q in e.event_type.lower()
                     or str(e.person_track_id) in q or q in e.timestamp.lower() or q in e.risk.lower()]

    # Table
    st.markdown("""
    <div class="ibvap-card" style="padding:0;overflow:hidden;">
    <table class="data-table">
        <thead><tr>
            <th>Event ID</th><th>Event Type</th><th>Track ID</th><th>Frame</th>
            <th>Timestamp</th><th>Risk</th><th>Evidence Ref</th><th>Status</th><th>Created At</th>
        </tr></thead>
    <tbody>
    """, unsafe_allow_html=True)

    for event in filtered:
        from datetime import datetime
        created = event.created_at[:19].replace("T", " ") if event.created_at else "N/A"
        evidence = "Available" if event.evidence_file else "N/A"
        st.markdown(f"""
        <tr>
            <td style="font-family:monospace;font-weight:500;">{event.event_id}</td>
            <td>{event.event_type}</td>
            <td>{event.person_track_id}</td>
            <td style="font-family:monospace;">{event.frame}</td>
            <td style="font-family:monospace;">{event.timestamp}</td>
            <td>{risk_badge(event.risk)}</td>
            <td>{evidence}</td>
            <td><span style="color:#16a34a;font-weight:500;">{event.status}</span></td>
            <td style="font-family:monospace;font-size:12px;color:#94a3b8;">{created}</td>
        </tr>
        """, unsafe_allow_html=True)

    st.markdown("</tbody></table></div>", unsafe_allow_html=True)

    # Cybersecurity architecture section
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Cybersecurity Architecture")

    col_current, col_future = st.columns(2)

    with col_current:
        items = ["AI-generated intrusion events", "Timestamped records", "Risk classification",
                 "Visual evidence", "CSV audit log"]
        items_html = "".join([
            f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;font-size:13px;color:#475569;">'
            f'<span style="color:#22c55e;">✓</span> {item}</div>'
            for item in items
        ])
        st.markdown(f"""
        <div class="ibvap-card">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <div style="width:32px;height:32px;border-radius:8px;background:#dcfce7;
                display:flex;align-items:center;justify-content:center;">🛡️</div>
                <div>
                    <h3 style="margin:0;">Current Implementation</h3>
                    <span style="font-size:10px;font-weight:600;color:#16a34a;">DEPLOYED</span>
                </div>
            </div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

    with col_future:
        steps = ["Event Record", "Cryptographic Hash", "Permissioned Blockchain", "Tamper-Evident Audit Trail"]
        steps_html = ""
        for i, step in enumerate(steps):
            steps_html += f"""
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;font-size:13px;color:#94a3b8;">
                <span style="width:20px;height:20px;border-radius:6px;background:#f1f5f9;
                display:flex;align-items:center;justify-content:center;font-size:10px;
                font-family:monospace;">{i+1}</span> {step}
            </div>"""
        st.markdown(f"""
        <div class="ibvap-card" style="border:2px dashed #cbd5e1;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <div style="width:32px;height:32px;border-radius:8px;background:#f1f5f9;
                display:flex;align-items:center;justify-content:center;">🔗</div>
                <div>
                    <h3 style="margin:0;">Future Blockchain Integration</h3>
                    <span style="font-size:10px;font-weight:600;color:#d97706;">FUTURE ENHANCEMENT</span>
                </div>
            </div>
            {steps_html}
            <p style="font-size:12px;color:#94a3b8;margin-top:12px;padding-top:12px;
            border-top:1px solid #f1f5f9;">
            Blockchain storage is future scope. Not yet implemented.</p>
        </div>
        """, unsafe_allow_html=True)
