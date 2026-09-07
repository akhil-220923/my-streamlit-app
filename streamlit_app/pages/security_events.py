"""Security Events page — intrusion event management."""
import streamlit as st
import pandas as pd

from components.ui_components import (
    risk_badge, status_indicator, section_header, empty_state_html
)


def render(events):
    st.markdown(section_header(
        "Security Events",
        f"Intrusion event management — {len(events)} event{'s' if len(events) != 1 else ''} recorded"
    ), unsafe_allow_html=True)

    if not events:
        st.markdown(f"""
        <div class="ibvap-card">
            {empty_state_html("🚨", "No intrusion events detected",
            "Surveillance system is operating normally. No security events have been recorded.")}
        </div>
        """, unsafe_allow_html=True)
        return

    # Filters
    col_search, col_risk, col_status, col_sort = st.columns(4)

    with col_search:
        search = st.text_input("Search", placeholder="Event ID, track, timestamp...", key="evt-search")

    with col_risk:
        risk_options = ["ALL", "HIGH", "MEDIUM", "LOW"]
        risk_filter = st.selectbox("Risk", risk_options, key="evt-risk-filter")

    with col_status:
        status_options = ["ALL", "Confirmed", "Pending", "Resolved"]
        status_filter = st.selectbox("Status", status_options, key="evt-status-filter")

    with col_sort:
        sort_options = ["Frame (asc)", "Frame (desc)", "Timestamp (asc)", "Risk (desc)"]
        sort_choice = st.selectbox("Sort", sort_options, key="evt-sort")

    # Filter events
    filtered = events
    if search:
        q = search.lower()
        filtered = [e for e in filtered if q in e.event_id.lower() or q in e.event_type.lower()
                     or str(e.person_track_id) in q or q in e.timestamp]
    if risk_filter != "ALL":
        filtered = [e for e in filtered if e.risk == risk_filter]
    if status_filter != "ALL":
        filtered = [e for e in filtered if e.status == status_filter]

    risk_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    if sort_choice == "Frame (asc)":
        filtered.sort(key=lambda e: e.frame)
    elif sort_choice == "Frame (desc)":
        filtered.sort(key=lambda e: e.frame, reverse=True)
    elif sort_choice == "Timestamp (asc)":
        filtered.sort(key=lambda e: e.frame)
    elif sort_choice == "Risk (desc)":
        filtered.sort(key=lambda e: risk_order.get(e.risk, 0), reverse=True)

    # Table
    st.markdown("""
    <div class="ibvap-card" style="padding:0;overflow:hidden;">
    <table class="data-table">
        <thead><tr>
            <th>Event ID</th><th>Event Type</th><th>Track ID</th><th>Frame</th>
            <th>Timestamp</th><th>Risk</th><th>Evidence</th><th>Status</th><th>Action</th>
        </tr></thead>
    <tbody>
    """, unsafe_allow_html=True)

    for event in filtered:
        evidence_label = '<span style="color:#0d9488;font-weight:500;">Available</span>' if event.evidence_file else '<span style="color:#94a3b8;">N/A</span>'
        st.markdown(f"""
        <tr>
            <td style="font-family:monospace;font-weight:500;">{event.event_id}</td>
            <td>{event.event_type}</td>
            <td>Track {event.person_track_id}</td>
            <td style="font-family:monospace;">{event.frame}</td>
            <td style="font-family:monospace;">{event.timestamp}</td>
            <td>{risk_badge(event.risk)}</td>
            <td>{evidence_label}</td>
            <td><span style="color:#16a34a;font-weight:500;">{event.status}</span></td>
            <td></td>
        </tr>
        """, unsafe_allow_html=True)

    st.markdown("</tbody></table></div>", unsafe_allow_html=True)

    # Event detail buttons
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Event Details")
    st.markdown("Click a button below to view full event details:", unsafe_allow_html=True)

    def _select_event(eid):
        st.session_state.ibvap_selected_event = eid

    cols = st.columns(min(len(filtered), 3))
    for i, event in enumerate(filtered):
        with cols[i % 3]:
            st.button(
                f"View {event.event_id}",
                key=f"evt-detail-{event.event_id}",
                use_container_width=True,
                on_click=_select_event,
                args=(event.event_id,)
            )

    # Show modal for selected event
    selected_id = st.session_state.get("ibvap_selected_event")
    selected = next((e for e in events if e.event_id == selected_id), None)

    if selected:
        _render_event_modal(selected)


def _render_event_modal(event):
    st.markdown(f"""
    <div class="ibvap-modal-overlay">
        <div class="ibvap-modal">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="width:40px;height:40px;border-radius:10px;background:#fef2f2;
                    display:flex;align-items:center;justify-content:center;font-size:18px;">🛡️</div>
                    <div>
                        <h3 style="margin:0;font-size:16px;font-weight:700;color:#0f172a;">Security Event</h3>
                        <p style="margin:0;font-size:12px;color:#94a3b8;">{event.event_id}</p>
                    </div>
                </div>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;
            padding:12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:16px;">
                <span style="font-size:13px;color:#64748b;">Risk Level</span>
                {risk_badge(event.risk)}
            </div>
            <div style="space-y:8px;">
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#f8fafc;border-radius:8px;margin-bottom:6px;">
                    <span style="font-size:13px;color:#94a3b8;">🛡️ Event ID</span>
                    <span style="font-size:13px;font-family:monospace;font-weight:500;color:#1e293b;">{event.event_id}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#f8fafc;border-radius:8px;margin-bottom:6px;">
                    <span style="font-size:13px;color:#94a3b8;">⚠️ Event Type</span>
                    <span style="font-size:13px;font-weight:500;color:#1e293b;">{event.event_type}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#f8fafc;border-radius:8px;margin-bottom:6px;">
                    <span style="font-size:13px;color:#94a3b8;">🎯 Person Track</span>
                    <span style="font-size:13px;font-weight:500;color:#1e293b;">Track {event.person_track_id}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#f8fafc;border-radius:8px;margin-bottom:6px;">
                    <span style="font-size:13px;color:#94a3b8;">📄 Frame</span>
                    <span style="font-size:13px;font-family:monospace;font-weight:500;color:#1e293b;">{event.frame}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#f8fafc;border-radius:8px;margin-bottom:6px;">
                    <span style="font-size:13px;color:#94a3b8;">⏱️ Timestamp</span>
                    <span style="font-size:13px;font-family:monospace;font-weight:500;color:#1e293b;">{event.timestamp}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#f8fafc;border-radius:8px;margin-bottom:6px;">
                    <span style="font-size:13px;color:#94a3b8;">📍 Detection Method</span>
                    <span style="font-size:13px;font-weight:500;color:#1e293b;">{event.detection_method}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:#f8fafc;border-radius:8px;margin-bottom:16px;">
                    <span style="font-size:13px;color:#94a3b8;">📸 Evidence</span>
                    <span style="font-size:13px;font-weight:500;color:{"#0d9488" if event.evidence_file else "#94a3b8"};">
                    {"Available" if event.evidence_file else "N/A"}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    def _go_to_evidence(eid):
        st.session_state.ibvap_evidence_view = eid
        st.session_state.ibvap_page = "digital-evidence"

    def _go_to_surveillance():
        st.session_state.ibvap_page = "surveillance"

    def _close_modal():
        st.session_state.ibvap_selected_event = None

    col1, col2, col3 = st.columns(3)
    with col1:
        if event.evidence_file:
            st.button(
                "📸 View Evidence",
                key=f"modal-evidence-{event.event_id}",
                use_container_width=True,
                on_click=_go_to_evidence,
                args=(event.event_id,)
            )
    with col2:
        st.button(
            "📹 Open Video",
            key=f"modal-video-{event.event_id}",
            use_container_width=True,
            on_click=_go_to_surveillance
        )
    with col3:
        import json
        st.download_button(
            "📥 Download Event",
            data=json.dumps(event.to_dict(), indent=2),
            file_name=f"{event.event_id}_event.json",
            mime="application/json",
            key=f"modal-download-{event.event_id}",
            use_container_width=True
        )

    st.button("✕ Close", key="modal-close", use_container_width=True, on_click=_close_modal)
