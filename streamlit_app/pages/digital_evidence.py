"""Digital Evidence page — visual evidence gallery."""
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

from components.ui_components import (
    risk_badge, section_header, empty_state_html
)


def render(events):
    with_evidence = [e for e in events if e.evidence_file]

    st.markdown(section_header(
        "Digital Evidence",
        f"Visual evidence captured for intrusion events — {len(with_evidence)} item{'s' if len(with_evidence) != 1 else ''}"
    ), unsafe_allow_html=True)

    if not with_evidence:
        st.markdown(f"""
        <div class="ibvap-card">
            {empty_state_html("📸", "No Digital Evidence Available",
            "No evidence images have been captured. Evidence is generated when intrusion events are detected.")}
        </div>
        """, unsafe_allow_html=True)
        return

    # Evidence grid
    for i, event in enumerate(with_evidence):
        evidence_id = f"EV-{i+1:03d}"

        col_img, col_info = st.columns([3, 2])

        with col_img:
            try:
                st.image(event.evidence_file, caption=f"{evidence_id} — {event.event_id}", use_container_width=True)
            except Exception:
                st.markdown(f"""
                <div style="background:#0a1929;aspect-ratio:16/9;border-radius:12px;
                display:flex;align-items:center;justify-content:center;">
                    <span style="font-size:48px;">📸</span>
                </div>
                """, unsafe_allow_html=True)

        with col_info:
            st.markdown(f"""
            <div class="ibvap-card">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                    <span style="font-size:15px;font-weight:600;color:#1e293b;">{evidence_id}</span>
                    {risk_badge(event.risk)}
                </div>
                <div style="space-y:6px;">
                    <div style="display:flex;justify-content:space-between;padding:6px 0;">
                        <span style="font-size:13px;color:#94a3b8;">Event ID</span>
                        <span style="font-size:13px;font-family:monospace;color:#1e293b;">{event.event_id}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;">
                        <span style="font-size:13px;color:#94a3b8;">Event Type</span>
                        <span style="font-size:13px;color:#1e293b;">{event.event_type}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;">
                        <span style="font-size:13px;color:#94a3b8;">Person Track</span>
                        <span style="font-size:13px;color:#1e293b;">Track {event.person_track_id}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;">
                        <span style="font-size:13px;color:#94a3b8;">Frame</span>
                        <span style="font-size:13px;font-family:monospace;color:#1e293b;">{event.frame}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;">
                        <span style="font-size:13px;color:#94a3b8;">Timestamp</span>
                        <span style="font-size:13px;font-family:monospace;color:#1e293b;">{event.timestamp}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            def _zoom_evidence(eid):
                st.session_state.ibvap_evidence_view = eid

            def _go_to_event(eid):
                st.session_state.ibvap_selected_event = eid
                st.session_state.ibvap_page = "security-events"

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.button(
                    "🔍 Zoom",
                    key=f"zoom-{event.event_id}",
                    use_container_width=True,
                    on_click=_zoom_evidence,
                    args=(event.event_id,)
                )
            with col_b:
                st.markdown(f'<a href="{event.evidence_file}" target="_blank" download style="display:inline-block;width:100%;text-align:center;padding:8px;background:rgba(20,184,166,0.1);border:1px solid #14b8a6;border-radius:8px;color:#0d9488;text-decoration:none;font-weight:600;font-size:12px;">📥 Download</a>', unsafe_allow_html=True)
            with col_c:
                st.button(
                    "🔗 Event",
                    key=f"evt-link-{event.event_id}",
                    use_container_width=True,
                    on_click=_go_to_event,
                    args=(event.event_id,)
                )

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Full-size evidence viewer
    view_id = st.session_state.get("ibvap_evidence_view")
    if view_id:
        view_event = next((e for e in events if e.event_id == view_id), None)
        if view_event and view_event.evidence_file:
            def _close_evidence_view():
                st.session_state.ibvap_evidence_view = None

            st.markdown("---")
            st.markdown(f"#### Evidence Viewer — {view_event.event_id}")
            st.image(view_event.evidence_file, use_container_width=True)
            st.button("✕ Close Viewer", key="close-evidence-view", on_click=_close_evidence_view)
